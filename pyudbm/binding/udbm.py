"""
Legacy-style high-level UDBM API.

This module exposes the main Python modeling layer of :mod:`pyudbm`. It keeps
the historical ``Context`` / ``Clock`` / ``Federation`` programming model
while delegating the actual Difference Bound Matrix (DBM) algorithms to the
native UDBM library.

Conceptually, the binding mirrors the standard timed-automata representation
used by UDBM:

* a DBM represents one convex zone, that is, one conjunction of constraints of
  the form ``x_i - x_j <= c``;
* a federation is a finite union of DBMs, used for non-convex symbolic states;
* clock ``0`` is the implicit reference clock ``x0 = 0`` used by UDBM, while
  user-visible clocks start at DBM index ``1``;
* the Python DSL turns natural expressions such as ``c.x < 5`` or
  ``c.x - c.y <= 2`` into native UDBM constraints.

The Python layer intentionally stays thin: methods like :meth:`Federation.up`,
:meth:`Federation.down`, :meth:`Federation.predt`, and
:meth:`Federation.extrapolate_max_bounds` are direct high-level wrappers around
the corresponding UDBM operations. The documentation below therefore explains
both the Python API and the underlying DBM semantics.

Example::

    >>> from pyudbm import Context, IntValuation
    >>> context = Context(["x", "y"], name="c")
    >>> zone = (context.x < 10) & (context.x - context.y > 1)
    >>> relaxed = zone.up()
    >>> valuation = IntValuation(context)
    >>> valuation["x"] = 5
    >>> valuation["y"] = 3
    >>> zone.contains(valuation)
    True
    >>> relaxed >= zone
    True
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, List, Mapping, Optional, Union

from ._binding import _NativeConstraint, _NativeFederation

__all__ = [
    "Clock",
    "Constraint",
    "Context",
    "Federation",
    "FloatValuation",
    "IntValuation",
    "Valuation",
    "VariableDifference",
]

LOGGER = logging.getLogger("pyudbm")


def _is_exact_int(value: Any) -> bool:
    """Return whether ``value`` is a plain ``int`` and not a subclass such as ``bool``."""

    return type(value) is int


def _is_exact_int_or_float(value: Any) -> bool:
    """Return whether ``value`` is a plain ``int`` or ``float``."""

    value_type = type(value)
    return value_type is int or value_type is float


class Clock:
    """
    Symbolic clock inside a :class:`Context`.

    A :class:`Clock` is the Python name-bearing handle for one user-visible
    UDBM clock. The underlying DBM still works with integer indices and keeps
    index ``0`` reserved for the reference clock ``x0 = 0``. The public
    attribute :attr:`dbm_index` therefore starts at ``1``.

    Clock instances are the entry point to the DSL. Comparing a clock with an
    integer does not produce a boolean; instead it builds a
    :class:`Federation` containing the corresponding zone:

    * ``clock <= n`` means ``clock - x0 <= n``
    * ``clock >= n`` means ``x0 - clock <= -n``
    * ``clock == n`` is the intersection of both bounds
    * ``clock1 - clock2`` produces a :class:`VariableDifference`

    The binding intentionally accepts only plain integers for symbolic bounds.
    This matches the native DBM interface used here and avoids the accidental
    acceptance of ``bool`` values.

    :param context: Owning clock context.
    :type context: Context
    :param name: Clock name inside the context.
    :type name: str
    :param index: Zero-based clock index inside the context.
    :type index: int
    :ivar context: The owning context.
    :ivar index: Zero-based user index inside :attr:`Context.clocks`.
    :ivar name: User-visible clock name.
    :ivar dbm_index: Native DBM index, shifted by one because UDBM keeps
        index ``0`` for the reference clock.

    Example::

        >>> from pyudbm import Context
        >>> context = Context(["x", "y"], name="c")
        >>> context.x.get_full_name()
        'c.x'
        >>> str(context.x < 10)
        '(c.x<10)'
        >>> (context.x == 3) <= (context.x <= 3)
        True
        >>> (context.x - context.y <= 2) == (context.y - context.x >= -2)
        True
    """

    def __init__(self, context: "Context", name: str, index: int):
        self.context = context
        self.index = index
        self.name = name
        self.dbm_index = index + 1

    def __repr__(self) -> str:
        return "<Clock {0}>".format(self.get_full_name())

    def __sub__(self, other: Any) -> "VariableDifference":
        if not isinstance(other, Clock):
            return NotImplemented
        if other.context is not self.context:
            raise ValueError("Clock subtraction requires clocks from the same context.")
        return VariableDifference([self, other])

    def __le__(self, bound: Any) -> Any:
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self, None, bound, False))

    def __ge__(self, bound: Any) -> Any:
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(None, self, -bound, False))

    def __lt__(self, bound: Any) -> Any:
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self, None, bound, True))

    def __gt__(self, bound: Any) -> Any:
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(None, self, -bound, True))

    def __eq__(self, bound: Any) -> Any:
        if _is_exact_int(bound):
            return Federation(Constraint(self, None, bound, False)) & Federation(Constraint(None, self, -bound, False))
        return self is bound

    def __ne__(self, bound: Any) -> Any:
        if _is_exact_int(bound):
            return Federation(Constraint(self, None, bound, True)) | Federation(Constraint(None, self, -bound, True))
        return not self.__eq__(bound)

    def __hash__(self) -> int:
        return hash(self.get_full_name())

    def get_full_name(self) -> str:
        """
        Return the fully-qualified clock name.

        If the parent context has a display name, the result uses the
        ``context.clock`` form that UDBM string rendering expects. Otherwise
        the raw clock name is returned unchanged.

        :return: Context-qualified clock name when a context name is present.
        :rtype: str

        Example::

            >>> from pyudbm import Context
            >>> named = Context(["x"], name="sys")
            >>> anonymous = Context(["x"])
            >>> named.x.get_full_name()
            'sys.x'
            >>> anonymous.x.get_full_name()
            'x'
        """

        if self.context.name:
            return "{0}.{1}".format(self.context.name, self.name)
        return self.name


class Valuation(dict):
    """
    Clock valuation base class.

    UDBM membership tests are performed against concrete valuations. This class
    stores such valuations as a mapping from :class:`Clock` objects to concrete
    numeric values, while also accepting clock names on assignment for
    convenience.

    The base class only normalizes keys and tracks context consistency; it does
    not restrict the value type. For membership checks through
    :meth:`Federation.contains`, use :class:`IntValuation` or
    :class:`FloatValuation`, which match the two native containment entry
    points.

    :param context: Owning clock context.
    :type context: Context
    :ivar context: The context that defines the allowed clock keys.

    Example::

        >>> from pyudbm import Context, Valuation
        >>> context = Context(["x", "y"])
        >>> valuation = Valuation(context)
        >>> valuation["x"] = 1
        >>> valuation[context.y] = 2
        >>> valuation[context.x]
        1
        >>> valuation[context.y]
        2
    """

    def __init__(self, context: "Context"):
        super().__init__()
        self.context = context

    def _normalize_key(self, key: Union[str, Clock]) -> Clock:
        if isinstance(key, Clock):
            if key.context is not self.context:
                raise ValueError("Clock valuation keys must belong to the same context.")
            return key

        if not isinstance(key, str):
            raise TypeError("Valuation keys must be clock names or Clock objects.")
        return self.context[key]

    def __setitem__(self, key: Union[str, Clock], value: Any) -> None:
        super().__setitem__(self._normalize_key(key), value)

    def check(self) -> None:
        """
        Check whether all clocks of the context have assigned values.

        The method does not raise. For historical compatibility, missing
        entries are reported through the ``pyudbm`` logger instead. This is
        primarily useful before calling :meth:`Federation.contains`, where a
        partial valuation would otherwise fail later when translated into a
        native point vector.

        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context, Valuation
            >>> context = Context(["x", "y"])
            >>> valuation = Valuation(context)
            >>> valuation["x"] = 1
            >>> valuation["y"] = 2
            >>> valuation.check() is None
            True
        """

        for clock in self.context.clocks:
            if clock not in self:
                LOGGER.error("Clock %s is not present in the clock valuation.", clock.name)


class IntValuation(Valuation):
    """
    Integer clock valuation.

    This specialization matches UDBM's integer containment check. It accepts
    only plain :class:`int` values and rejects ``bool`` for the same reason as
    the symbolic constraint layer.

    :param context: Owning clock context.
    :type context: Context

    Example::

        >>> from pyudbm import Context, IntValuation
        >>> context = Context(["x", "y"])
        >>> valuation = IntValuation(context)
        >>> valuation["x"] = 3
        >>> valuation["y"] = 1
        >>> ((context.x == 3) & (context.y == 1)).contains(valuation)
        True
    """

    def __setitem__(self, key: Union[str, Clock], value: Any) -> None:
        if not _is_exact_int(value):
            raise TypeError("Integer valuations require integer values.")
        super().__setitem__(key, value)


class FloatValuation(Valuation):
    """
    Floating-point clock valuation.

    This specialization targets UDBM's real-valued point inclusion test. It
    accepts both integers and floating-point numbers and is the right choice
    when strict inequalities make the difference between integer and real
    membership observable.

    :param context: Owning clock context.
    :type context: Context

    Example::

        >>> from pyudbm import Context, FloatValuation
        >>> context = Context(["x"])
        >>> valuation = FloatValuation(context)
        >>> valuation["x"] = 1.5
        >>> (context.x > 1).contains(valuation)
        True
        >>> (context.x == 1).contains(valuation)
        False
    """

    def __setitem__(self, key: Union[str, Clock], value: Any) -> None:
        if not _is_exact_int_or_float(value):
            raise TypeError("Float valuations require int or float values.")
        super().__setitem__(key, value)


class VariableDifference:
    """
    Symbolic difference between two clocks.

    This lightweight helper represents the symbolic expression ``x - y`` for
    two clocks in the same context. Comparing the difference with an integer
    creates a :class:`Federation` whose DBM contains the corresponding
    diagonal constraint ``x - y <= c`` or its strict / reversed variants.

    In timed-automata terms, this is how diagonal constraints are expressed in
    the Python DSL.

    :param variables: Two clocks from the same context.
    :type variables: list[Clock]
    :ivar vars: The two clocks in ``[left, right]`` order.
    :ivar context: Shared context of both clocks.

    Example::

        >>> from pyudbm import Context
        >>> context = Context(["x", "y"])
        >>> diagonal = context.x - context.y
        >>> (diagonal <= 3) == (context.y - context.x >= -3)
        True
        >>> (diagonal == 1) == ((context.x == 2) & (context.y == 1))
        True
    """

    def __init__(self, variables: List[Clock]):
        if len(variables) != 2:
            raise ValueError("VariableDifference requires exactly two clocks.")
        if variables[0].context is not variables[1].context:
            raise ValueError("VariableDifference requires clocks from the same context.")

        self.vars = variables
        self.context = variables[0].context

    def __le__(self, bound: Any) -> Any:
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self.vars[0], self.vars[1], bound, False))

    def __ge__(self, bound: Any) -> Any:
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self.vars[1], self.vars[0], -bound, False))

    def __lt__(self, bound: Any) -> Any:
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self.vars[0], self.vars[1], bound, True))

    def __gt__(self, bound: Any) -> Any:
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self.vars[1], self.vars[0], -bound, True))

    def __eq__(self, bound: Any) -> Any:
        if not _is_exact_int(bound):
            return False
        return Federation(Constraint(self.vars[0], self.vars[1], bound, False)) & Federation(
            Constraint(self.vars[1], self.vars[0], -bound, False)
        )

    def __ne__(self, bound: Any) -> Any:
        if not _is_exact_int(bound):
            return True
        return Federation(Constraint(self.vars[0], self.vars[1], bound, True)) | Federation(
            Constraint(self.vars[1], self.vars[0], -bound, True)
        )


class Constraint:
    """
    Internal symbolic constraint wrapper.

    This class is the immediate bridge between the Python DSL and the native
    UDBM ``constraint_t`` representation. It stores one encoded difference
    constraint of the form ``arg1 - arg2 <= val`` together with strictness.

    End users usually create :class:`Constraint` objects implicitly through
    :class:`Clock` and :class:`VariableDifference` expressions, but the class
    remains public because it is part of the historical high-level surface and
    is used directly by :class:`Federation`.

    :param arg1: Left clock operand, or ``None`` for the reference clock.
    :type arg1: Clock or None
    :param arg2: Right clock operand, or ``None`` for the reference clock.
    :type arg2: Clock or None
    :param val: Integer bound.
    :type val: int
    :param is_strict: Whether the bound is strict.
    :type is_strict: bool
    :ivar arg1: Left clock operand, or ``None`` for the reference clock.
    :ivar arg2: Right clock operand, or ``None`` for the reference clock.
    :ivar context: Context owning the participating clocks.

    Example::

        >>> from pyudbm import Constraint, Context, Federation
        >>> context = Context(["x", "y"])
        >>> constraint = Constraint(context.x, context.y, 3, False)
        >>> zone = Federation(constraint)
        >>> zone == (context.x - context.y <= 3)
        True
    """

    def __init__(self, arg1: Optional[Clock], arg2: Optional[Clock], val: int, is_strict: bool):
        if not isinstance(val, int):
            raise TypeError("Constraint bounds must be integers.")
        if arg1 is None and arg2 is None:
            raise ValueError("At least one clock operand must be present.")
        if arg1 is not None and not isinstance(arg1, Clock):
            raise TypeError("Constraint operands must be Clock objects or None.")
        if arg2 is not None and not isinstance(arg2, Clock):
            raise TypeError("Constraint operands must be Clock objects or None.")
        if arg1 is not None and arg2 is not None and arg1.context is not arg2.context:
            raise ValueError("Constraint operands must belong to the same context.")

        self.arg1 = arg1
        self.arg2 = arg2
        self.context = arg1.context if arg1 is not None else arg2.context

        i = arg1.dbm_index if arg1 is not None else 0
        j = arg2.dbm_index if arg2 is not None else 0
        self._constraint = _NativeConstraint(i, j, val, is_strict)


class Federation:
    """
    Union of DBMs within a single :class:`Context`.

    A federation is the core symbolic set object of UDBM. Each element of the
    union is one DBM, that is, one convex zone over the clocks of the context.
    Federations are therefore the natural representation for non-convex timed
    states.

    This Python wrapper keeps the algebra close to the underlying library:

    * ``&`` is exact intersection;
    * ``|`` is set union;
    * ``+`` is convex union, meaning pairwise DBM hull construction rather
      than plain set union;
    * ``-`` is set subtraction;
    * comparisons implement set inclusion semantics.

    Mutability follows the historical binding rather than a pure in-place API:

    * :meth:`reduce`, :meth:`set_zero`, :meth:`set_init`, and :meth:`intern`
      mutate the object and return ``self`` (or ``None`` for ``intern``);
    * methods such as :meth:`up`, :meth:`down`, :meth:`free_clock`,
      :meth:`convex_hull`, :meth:`predt`, :meth:`update_value`,
      :meth:`reset_value`, and :meth:`extrapolate_max_bounds` return a modified
      copy and leave the original federation untouched.

    The constructor mirrors the historical binding: creating from a
    :class:`Context` yields the zero federation, while creating from a
    :class:`Constraint` yields the initial federation constrained by that
    symbolic expression.

    :param arg: Context or symbolic constraint source.
    :type arg: Context or Constraint
    :ivar context: Context shared by every DBM in the federation.

    Example::

        >>> from pyudbm import Context
        >>> context = Context(["x", "y"], name="c")
        >>> d1 = (context.x >= 1) & (context.x <= 2)
        >>> d2 = (context.y >= 3) & (context.y <= 4)
        >>> union = d1 | d2
        >>> hull = d1 + d2
        >>> union.get_size()
        2
        >>> hull >= d1
        True
        >>> hull >= d2
        True
    """

    def __init__(self, arg: Union["Context", Constraint]):
        if isinstance(arg, Constraint):
            self._fed = _NativeFederation(len(arg.context.clocks) + 1, arg._constraint)
            self.context = arg.context
        elif isinstance(arg, Context):
            self._fed = _NativeFederation(len(arg.clocks) + 1)
            self._fed.set_zero()
            self.context = arg
        else:
            raise TypeError("Federation expects a Context or Constraint.")

    @classmethod
    def _from_native(cls, context: "Context", native: _NativeFederation) -> "Federation":
        result = cls.__new__(cls)
        result.context = context
        result._fed = native
        return result

    def _require_compatible(self, other: "Federation") -> None:
        if not isinstance(other, Federation):
            raise TypeError("Federation operations require another Federation.")
        if other.context is not self.context:
            raise ValueError("Federation operations require the same context.")

    def _clock_names(self) -> List[str]:
        return ["0"] + [clock.get_full_name() for clock in self.context.clocks]

    def _valuation_vector(self, valuation: Valuation) -> List[Union[int, float]]:
        values = [0]
        for clock in self.context.clocks:
            values.append(valuation[clock])
        return values

    def __str__(self) -> str:
        return self._fed.to_string(self._clock_names()).replace(" && ", " & ").replace(" || ", " | ")

    def copy(self) -> "Federation":
        """
        Return a copy of the federation.

        The copy shares the same :class:`Context` but owns an independent
        native federation value.

        :return: A copy sharing the same context.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> original = (context.x == 1)
            >>> copied = original.copy()
            >>> copied |= (context.y == 2)
            >>> original != copied
            True
            >>> original == (context.x == 1)
            True
        """

        return Federation._from_native(self.context, self._fed.copy())

    def __and__(self, other: "Federation") -> "Federation":
        self._require_compatible(other)
        return Federation._from_native(self.context, self._fed.and_op(other._fed))

    def __iand__(self, other: "Federation") -> "Federation":
        self._require_compatible(other)
        self._fed.iand(other._fed)
        return self

    def __or__(self, other: "Federation") -> "Federation":
        self._require_compatible(other)
        return Federation._from_native(self.context, self._fed.or_op(other._fed))

    def __ior__(self, other: "Federation") -> "Federation":
        self._require_compatible(other)
        self._fed.ior(other._fed)
        return self

    def __add__(self, other: "Federation") -> "Federation":
        self._require_compatible(other)
        return Federation._from_native(self.context, self._fed.add_op(other._fed))

    def __iadd__(self, other: "Federation") -> "Federation":
        self._require_compatible(other)
        self._fed.iadd(other._fed)
        return self

    def __sub__(self, other: "Federation") -> "Federation":
        self._require_compatible(other)
        return Federation._from_native(self.context, self._fed.minus_op(other._fed))

    def __isub__(self, other: "Federation") -> "Federation":
        self._require_compatible(other)
        self._fed.isub(other._fed)
        return self

    def up(self) -> "Federation":
        """
        Compute the delay successor of the federation.

        In DBM terms this removes upper bounds of the form ``x_i - x0 <= c``
        from every DBM, which is the standard strongest post-condition for time
        elapse.

        :return: A delayed copy of the federation.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> zone = (context.x >= 1) & (context.x <= 2) & (context.y >= 1) & (context.y <= 2)
            >>> expected = (context.x - context.y <= 1) & (context.y - context.x <= 1) & (context.x >= 1) & (context.y >= 1)
            >>> zone.up() == expected
            True
            >>> zone != expected
            True
        """
        ret = self.copy()
        ret._fed.up()
        return ret

    def down(self) -> "Federation":
        """
        Compute the inverse delay predecessor of the federation.

        This is the standard weakest pre-condition for time elapse: lower
        bounds are relaxed so that delaying can lead into the current zone.

        :return: A predecessor copy of the federation.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> zone = (context.x >= 1) & (context.x <= 2) & (context.y >= 1) & (context.y <= 2)
            >>> expected = (context.x - context.y <= 1) & (context.y - context.x <= 1) & (context.x <= 2) & (context.y <= 2)
            >>> zone.down() == expected
            True
        """
        ret = self.copy()
        ret._fed.down()
        return ret

    def reduce(self, level: int = 0) -> "Federation":
        """
        Merge-reduce the federation in place.

        The historical Python API exposes this operation as ``reduce``. In the
        current pybind11 implementation it is backed by UDBM's
        ``mergeReduce(skip=0, level=level)`` heuristic, which tries to replace
        several DBMs by fewer equivalent or safely merged DBMs.

        :param level: Historical expensive-try level passed to UDBM.
        :type level: int
        :return: ``self``.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> federation = (context.x >= 1) | (context.x <= 1)
            >>> federation.get_size()
            2
            >>> federation.reduce().get_size()
            1
        """

        self._fed.merge_reduce(0, level)
        return self

    def free_clock(self, clock: Clock) -> "Federation":
        """
        Return a copy where one clock has been unconstrained.

        UDBM's ``freeClock`` removes both upper and lower bounds involving the
        given clock, while still preserving the ambient positivity convention
        inherited from the reference clock.

        :param clock: Clock to unconstrain.
        :type clock: Clock
        :return: A modified copy with the clock freed.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> zone = (context.x >= 10) & (context.y >= 10)
            >>> zone.free_clock(context.x) == (context.y >= 10)
            True
            >>> zone == ((context.x >= 10) & (context.y >= 10))
            True
        """
        if not isinstance(clock, Clock):
            raise TypeError("free_clock expects a Clock instance.")
        if clock.context is not self.context:
            raise ValueError("free_clock requires a clock from the same context.")
        ret = self.copy()
        ret._fed.free_clock(clock.dbm_index)
        return ret

    def set_zero(self) -> "Federation":
        """
        Reset the federation to the single origin point.

        The resulting federation contains exactly the valuation where every
        clock is ``0``.

        :return: ``self``.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> zone = (context.x == 1) & (context.y == 2)
            >>> zone.set_zero() == ((context.x == 0) & (context.y == 0))
            True
            >>> zone.has_zero()
            True
        """
        self._fed.set_zero()
        return self

    def has_zero(self) -> bool:
        """
        Return whether the federation contains the origin.

        The origin is the valuation where every user clock is ``0``. This is a
        cheap and common query in timed-automata algorithms.

        :return: ``True`` if the origin is included.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> (context.x < 1).has_zero()
            True
            >>> (context.x > 1).has_zero()
            False
        """
        return self._fed.has_zero()

    def set_init(self) -> "Federation":
        """
        Reset the federation to the initial non-negative zone.

        This corresponds to UDBM's ``setInit`` operation: all user clocks are
        constrained only by the standard positivity convention ``x >= 0``.

        :return: ``self``.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> zone = (context.x == 1) & (context.y == 2)
            >>> zone.set_init() == ((context.x >= 0) & (context.y >= 0))
            True
        """
        self._fed.set_init()
        return self

    def convex_hull(self) -> "Federation":
        """
        Return the convex hull of the federation.

        UDBM computes the convex union of all DBMs in the federation, yielding
        one convex over-approximation zone.

        :return: A convex-hull copy.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> d1 = (context.x >= 1) & (context.x <= 2) & (context.y >= 1) & (context.y <= 2)
            >>> d2 = (context.x >= 3) & (context.x <= 4) & (context.y >= 3) & (context.y <= 4)
            >>> hull = (context.x - context.y <= 1) & (context.y - context.x <= 1)
            >>> hull &= (context.x >= 1) & (context.y >= 1) & (context.x <= 4) & (context.y <= 4)
            >>> (d1 | d2).convex_hull() == hull
            True
        """
        ret = self.copy()
        ret._fed.convex_hull()
        return ret

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Federation):
            return False
        self._require_compatible(other)
        return self._fed.eq(other._fed)

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __le__(self, other: "Federation") -> bool:
        self._require_compatible(other)
        return self._fed.le(other._fed)

    def __ge__(self, other: "Federation") -> bool:
        self._require_compatible(other)
        return self._fed.ge(other._fed)

    def __lt__(self, other: "Federation") -> bool:
        self._require_compatible(other)
        return self._fed.lt(other._fed)

    def __gt__(self, other: "Federation") -> bool:
        self._require_compatible(other)
        return self._fed.gt(other._fed)

    def intern(self) -> None:
        """
        Intern the native DBMs backing this federation.

        UDBM can canonicalize identical DBMs through internal hash tables.
        Calling :meth:`intern` is therefore a memory and equality-optimization
        hint rather than a semantic transformation.

        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> federation = context.x - context.y <= 1
            >>> before = federation.copy()
            >>> federation.intern() is None
            True
            >>> federation == before
            True
        """
        self._fed.intern()

    def predt(self, other: "Federation") -> "Federation":
        """
        Compute the temporal predecessor of ``self`` while avoiding ``other``.

        This is UDBM's ``predt(good, bad)`` operation with ``self`` playing the
        role of ``good`` and ``other`` playing the role of ``bad``. The result
        contains states that may delay, remain outside ``other``, and
        eventually enter ``self``.

        :param other: Forbidden region to avoid during delay.
        :type other: Federation
        :return: A predecessor copy.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> good = (context.x >= 2) & (context.x <= 4)
            >>> bad = (context.x == 1) & (context.x != 1)
            >>> good.predt(bad) == good.down()
            True
        """
        self._require_compatible(other)
        ret = self.copy()
        ret._fed.predt(other._fed)
        return ret

    def contains(self, valuation: Valuation) -> bool:
        """
        Test whether a concrete valuation belongs to the federation.

        The valuation must cover every clock of the context. Integer and
        floating-point valuations are dispatched to the corresponding native
        UDBM containment check.

        :param valuation: Concrete clock values.
        :type valuation: Valuation
        :return: ``True`` if the valuation is contained in at least one DBM.
        :rtype: bool

        Example::

            >>> from pyudbm import Context, IntValuation
            >>> context = Context(["x", "y"])
            >>> zone = (context.x == 2) & (context.y == 1)
            >>> valuation = IntValuation(context)
            >>> valuation["x"] = 2
            >>> valuation["y"] = 1
            >>> zone.contains(valuation)
            True
        """
        valuation.check()
        values = self._valuation_vector(valuation)
        if isinstance(valuation, IntValuation):
            return self._fed.contains_int(values)
        if isinstance(valuation, FloatValuation):
            return self._fed.contains_float(values)
        raise TypeError("Unknown valuation type.")

    def update_value(self, clock: Clock, value: int) -> "Federation":
        """
        Return a copy where one clock has been updated to a constant value.

        This wraps UDBM's ``updateValue`` operation, historically also called a
        reset when the target value is ``0``.

        :param clock: Clock to update.
        :type clock: Clock
        :param value: New integer value.
        :type value: int
        :return: Updated copy of the federation.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "z"])
            >>> zone = (context.x == 1) | (context.z == 2)
            >>> zone.update_value(context.x, 2) == (context.x == 2)
            True
        """
        if clock.context is not self.context:
            raise ValueError("Clock update requires the same context.")
        ret = self.copy()
        ret._fed.update_value(clock.dbm_index, value)
        return ret

    def reset_value(self, clock: Clock) -> "Federation":
        """
        Return a copy where one clock has been reset to ``0``.

        This is a convenience wrapper around :meth:`update_value`.

        :param clock: Clock to reset.
        :type clock: Clock
        :return: Updated copy of the federation.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "z"])
            >>> zone = (context.x == 1) & (context.z == 2)
            >>> zone.reset_value(context.x) == ((context.x == 0) & (context.z == 2))
            True
        """
        return self.update_value(clock, 0)

    def get_size(self) -> int:
        """
        Return the number of DBMs currently stored in the federation.

        This is the exact native federation size, not the number of visible
        clock constraints.

        :return: Number of DBMs.
        :rtype: int

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> federation = (context.x == 0) | (context.x == 1)
            >>> federation.get_size()
            2
        """
        return self._fed.size()

    def extrapolate_max_bounds(self, bounds: Mapping[Union[str, Clock], int]) -> "Federation":
        """
        Return a maximal-bound extrapolation of the federation.

        This is the classical DBM ``k``-normalization described in UDBM as
        ``extrapolateMaxBounds``. For each DBM, constraints above the maximal
        constant of their source clock are dropped to infinity, while very low
        lower bounds are clamped to the negated maximal constant of the target
        clock. The operation preserves closure but may over-approximate the
        original zone.

        The Python wrapper accepts a mapping keyed either by :class:`Clock`
        objects or by clock names. Bounds must be provided for every clock in
        the context.

        :param bounds: Maximal constants for every user clock.
        :type bounds: Mapping[str or Clock, int]
        :return: Extrapolated copy of the federation.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y", "z"])
            >>> federation = (context.x - context.y <= 1) & (context.x < 150)
            >>> federation &= (context.z < 150) & (context.x - context.z <= 1000)
            >>> bounds = {context.x: 100, context.y: 300, context.z: 400}
            >>> federation.extrapolate_max_bounds(bounds) == ((context.x - context.y <= 1) & (context.z < 150))
            True
        """
        normalized_bounds = {}
        for key, value in bounds.items():
            if isinstance(key, str):
                clock = self.context[key]
            elif isinstance(key, Clock):
                clock = key
            else:
                raise TypeError("Bounds keys must be clock names or Clock objects.")

            if clock.context is not self.context:
                raise ValueError("Bounds clocks must belong to the same context.")
            if clock in normalized_bounds:
                raise ValueError("Duplicate bounds provided for clock: {0}".format(clock.name))
            normalized_bounds[clock] = int(value)

        missing_clocks = [clock for clock in self.context.clocks if clock not in normalized_bounds]
        if missing_clocks:
            raise ValueError("extrapolate_max_bounds requires bounds for every clock.")

        ret = self.copy()
        vector = [0] * (len(self.context.clocks) + 1)
        for clock in self.context.clocks:
            vector[clock.dbm_index] = normalized_bounds[clock]

        ret._fed.extrapolate_max_bounds(vector)
        return ret

    def is_zero(self) -> bool:
        """
        Return whether the federation is exactly the origin zone.

        This is stronger than :meth:`has_zero`: the whole federation must equal
        the zero federation of its context.

        :return: ``True`` if the federation equals the origin zone.
        :rtype: bool

        Example::

            >>> from pyudbm import Context, Federation
            >>> context = Context(["x"])
            >>> Federation(context).is_zero()
            True
            >>> (context.x == 1).is_zero()
            False
        """
        return self == self.context.get_zero_federation()

    def is_empty(self) -> bool:
        """
        Return whether the federation contains no valuations.

        :return: ``True`` if the federation is empty.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> ((context.x == 1) & (context.x != 1)).is_empty()
            True
            >>> (context.x == 1).is_empty()
            False
        """
        return self._fed.is_empty()

    def __hash__(self) -> int:
        return self._fed.hash()

    def hash(self) -> int:
        """
        Return the Python hash of the federation.

        The underlying native hash is designed to be insensitive to DBM order.
        The Python wrapper exposes it through :func:`hash` and this convenience
        method.

        :return: Hash value.
        :rtype: int

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> left = (context.x == 1) | (context.y == 1)
            >>> right = (context.y == 1) | (context.x == 1)
            >>> left.hash() == right.hash()
            True
        """
        return hash(self)


class Context:
    """
    Named clock context.

    A context owns the finite set of clocks manipulated together by UDBM. All
    :class:`Clock`, :class:`Valuation`, :class:`VariableDifference`, and
    :class:`Federation` objects are context-specific, and almost every binary
    operation requires the same context on both sides.

    Each declared clock is available in two ways:

    * as an attribute, for example ``context.x``;
    * through name lookup, for example ``context["x"]``.

    Attribute access is convenient for normal modeling code, while indexed
    lookup keeps working even when a clock name would shadow an existing
    attribute.

    :param clock_names: Clock names to create.
    :type clock_names: iterable[str]
    :param name: Optional context prefix used in string rendering.
    :type name: str or None
    :ivar clocks: List of clocks in declaration order.
    :ivar name: Optional display prefix used by :meth:`Clock.get_full_name`.

    Example::

        >>> from pyudbm import Context
        >>> context = Context(["x", "y"], name="c")
        >>> context.x is context["x"]
        True
        >>> context.y.get_full_name()
        'c.y'
        >>> context.get_zero_federation().is_zero()
        True
    """

    def __init__(self, clock_names: Iterable[str], name: Optional[str] = None):
        self.clocks = []  # type: List[Clock]
        self.name = name

        for index, clock_name in enumerate(clock_names):
            clock = Clock(self, clock_name, index)
            self.clocks.append(clock)
            if hasattr(self, clock_name):
                LOGGER.warning("Class %s already has attribute %s.", self.__class__.__name__, clock_name)
            else:
                setattr(self, clock_name, clock)

    def set_name(self, name: Optional[str]) -> None:
        """
        Set the context display name.

        The display name affects only string rendering and derived clock full
        names. It does not change DBM identities or context compatibility.

        :param name: New context name.
        :type name: str or None
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> context.set_name("renamed")
            >>> context.x.get_full_name()
            'renamed.x'
        """

        self.name = name

    def __getitem__(self, arg: str) -> Clock:
        names = [clock for clock in self.clocks if clock.name == arg]
        if not names:
            raise KeyError(arg)
        if len(names) != 1:
            raise KeyError("Ambiguous clock name: {0}".format(arg))
        return names[0]

    def get_zero_federation(self) -> Federation:
        """
        Return the zero federation for this context.

        The zero federation contains exactly the origin valuation where all
        clocks are equal to ``0``.

        :return: Zero federation.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> zero = context.get_zero_federation()
            >>> zero.is_zero()
            True
            >>> zero.has_zero()
            True
        """

        return Federation(self)
