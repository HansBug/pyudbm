"""
High-level Python API for UCDD integration.

This module layers a Python-friendly symbolic API on top of the thin native
``_ucdd`` bindings. The design mirrors the existing :mod:`pyudbm.binding.udbm`
compatibility layer:

* :class:`CDDContext` provides named clock and boolean variables;
* :class:`CDD` is the main symbolic set object;
* pure clock zones can move between :class:`~pyudbm.binding.udbm.Federation`
  and :class:`CDD`;
* extracted DBM fragments are wrapped back into the existing :class:`DBM`
  class rather than introducing a second DBM wrapper hierarchy.

The UCDD runtime is global, so this module keeps one process-level runtime
layout. Reusing the same clock layout and boolean prefix is supported. Trying
to combine incompatible runtime layouts raises a descriptive error instead of
silently corrupting level mappings.

Example::

    >>> from pyudbm import Context
    >>> from pyudbm.binding.ucdd import CDDContext
    >>> base = Context(["x", "y"], name="c")
    >>> ctx = CDDContext.from_context(base, bools=["door_open"])
    >>> state = ((ctx.x <= 5) & ctx.door_open) | ((ctx.y <= 2) & ~ctx.door_open)
    >>> isinstance(state.reduce().bdd_traces().to_dicts(), list)
    True
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple, Union

from ._ucdd import OP_AND, OP_XOR, TYPE_BDD, TYPE_CDD, _NativeCDD, _NativeCDDRuntime
from ._udbm import _NativeDBM, _NativeFederation
from .udbm import DBM, Clock, Context, Federation, VariableDifference

__all__ = [
    "BDDTraceSet",
    "CDD",
    "CDDContext",
    "CDDExtraction",
    "CDDBool",
    "CDDClock",
    "CDDLevelInfo",
    "OP_AND",
    "OP_XOR",
    "TYPE_BDD",
    "TYPE_CDD",
]


@dataclass(frozen=True)
class CDDLevelInfo:
    """
    Immutable snapshot of one UCDD level descriptor.

    :param level: Level index inside the global UCDD runtime.
    :type level: int
    :param type: Native level type constant such as :data:`TYPE_CDD`.
    :type type: int
    :param clock1: Positive clock index used by CDD levels.
    :type clock1: int
    :param clock2: Negative clock index used by CDD levels.
    :type clock2: int
    :param diff: Encoded clock-difference identifier from the native runtime.
    :type diff: int
    """

    level: int
    type: int
    clock1: int
    clock2: int
    diff: int


@dataclass(frozen=True)
class _RuntimeLayout:
    clock_count: int
    bool_names: Tuple[str, ...]
    bool_levels: Tuple[int, ...]


_RUNTIME_LAYOUT: Optional[_RuntimeLayout] = None


def _clock_name_tuple(context: Context) -> Tuple[str, ...]:
    return tuple(clock.name for clock in context.clocks)


def _compatible_clock_layout(left: Context, right: Context) -> bool:
    return _clock_name_tuple(left) == _clock_name_tuple(right)


def _get_bdd_levels() -> Tuple[int, ...]:
    levels = []
    for level in range(_NativeCDDRuntime.get_level_count()):
        if _NativeCDDRuntime.get_level_info(level).type == TYPE_BDD:
            levels.append(level)
    return tuple(levels)


def _restart_runtime_if_idle() -> bool:
    """
    Restart the UCDD runtime when it is still running but no live CDD handles
    remain.

    This keeps the Python layer usable across independent test cases and
    sequential workflows that intentionally switch to a different global UCDD
    layout after all previous symbolic objects are gone.
    """

    global _RUNTIME_LAYOUT

    if not _NativeCDDRuntime.is_running():  # pragma: no cover
        return False
    if _NativeCDD.live_count() != 0:
        return False

    _NativeCDDRuntime.done()
    _RUNTIME_LAYOUT = None
    return True


def _ensure_runtime_layout(clock_count: int, bool_names: Sequence[str]) -> _RuntimeLayout:
    """
    Ensure that the global UCDD runtime matches the requested symbolic layout.

    The runtime can only grow monotonically, so this helper permits repeated
    requests for the same clock count and for boolean-name prefixes. Any other
    shape mismatch is rejected with a clear error message.
    """

    global _RUNTIME_LAYOUT

    requested_bool_names = tuple(bool_names)
    _NativeCDDRuntime.ensure_running()

    current_clock_count = _NativeCDDRuntime.getclocks()
    current_bool_count = _NativeCDDRuntime.get_bdd_level_count()
    if _RUNTIME_LAYOUT is not None and current_clock_count == 0 and current_bool_count == 0:  # pragma: no cover
        _RUNTIME_LAYOUT = None

    if current_clock_count == 0:
        _NativeCDDRuntime.add_clocks(clock_count)
        current_clock_count = _NativeCDDRuntime.getclocks()
    if current_clock_count != clock_count:
        if _restart_runtime_if_idle():
            return _ensure_runtime_layout(clock_count, requested_bool_names)
        raise RuntimeError(
            "UCDD runtime already uses {0} clocks, but this CDDContext requires {1}.".format(
                current_clock_count, clock_count
            )
        )

    if _RUNTIME_LAYOUT is None:
        if current_bool_count < len(requested_bool_names):
            _NativeCDDRuntime.add_bddvars(len(requested_bool_names) - current_bool_count)
            current_bool_count = _NativeCDDRuntime.get_bdd_level_count()
        if current_bool_count != len(requested_bool_names):
            if _restart_runtime_if_idle():
                return _ensure_runtime_layout(clock_count, requested_bool_names)
            raise RuntimeError(
                "UCDD runtime already uses {0} boolean levels, but this CDDContext requires {1}. "
                "Restart the process or reuse the same boolean layout.".format(
                    current_bool_count, len(requested_bool_names)
                )
            )

        levels = _get_bdd_levels()
        if len(levels) != len(requested_bool_names):  # pragma: no cover
            raise RuntimeError("Failed to resolve the expected boolean levels from the UCDD runtime.")

        _RUNTIME_LAYOUT = _RuntimeLayout(clock_count, requested_bool_names, levels)
        return _RUNTIME_LAYOUT

    if _RUNTIME_LAYOUT.clock_count != clock_count:  # pragma: no cover
        if _restart_runtime_if_idle():
            return _ensure_runtime_layout(clock_count, requested_bool_names)
        raise RuntimeError(
            "UCDD runtime already uses {0} clocks, but this CDDContext requires {1}.".format(
                _RUNTIME_LAYOUT.clock_count, clock_count
            )
        )

    existing_names = _RUNTIME_LAYOUT.bool_names
    if existing_names[: len(requested_bool_names)] == requested_bool_names:
        return _RUNTIME_LAYOUT

    if requested_bool_names[: len(existing_names)] == existing_names:
        _NativeCDDRuntime.add_bddvars(len(requested_bool_names) - len(existing_names))
        levels = _get_bdd_levels()
        _RUNTIME_LAYOUT = _RuntimeLayout(clock_count, requested_bool_names, levels)
        return _RUNTIME_LAYOUT

    if _restart_runtime_if_idle():
        return _ensure_runtime_layout(clock_count, requested_bool_names)

    raise RuntimeError(
        "UCDD runtime already uses boolean names {0}, which are incompatible with requested names {1}.".format(
            list(existing_names), list(requested_bool_names)
        )
    )


def _coerce_cdd_context(value: Union["CDDContext", Context]) -> "CDDContext":
    if isinstance(value, CDDContext):
        return value
    if isinstance(value, Context):
        return CDDContext.from_context(value)
    raise TypeError("Expected a CDDContext or Context instance.")


class CDDClock:
    """
    Clock variable inside a :class:`CDDContext`.

    The DSL mirrors :class:`~pyudbm.binding.udbm.Clock`, but comparisons return
    :class:`CDD` objects instead of :class:`Federation` objects.

    The public behavior intentionally stays close to the restored UDBM API:

    * ``clock <= n`` builds a pure-clock CDD constraint;
    * ``clock1 - clock2`` produces a :class:`CDDVariableDifference`;
    * non-integer comparisons are rejected instead of being silently coerced.

    :param context: Owning mixed symbolic context.
    :type context: CDDContext
    :param base_clock: Underlying clock from the wrapped
        :class:`~pyudbm.binding.udbm.Context`.
    :type base_clock: Clock
    :ivar context: Owning mixed symbolic context.
    :ivar name: Declared clock name.
    :ivar dbm_index: Native DBM / CDD clock index.

    Example::

        >>> from pyudbm import Context
        >>> from pyudbm.binding.ucdd import CDDContext
        >>> ctx = CDDContext.from_context(Context(["x", "y"], name="c"))
        >>> str(ctx.x.get_full_name())
        'c.x'
        >>> (ctx.x <= 3).to_federation() == (ctx.base_context.x <= 3)
        True
    """

    def __init__(self, context: "CDDContext", base_clock: Clock):
        """
        Initialize one mixed-context clock wrapper.

        Instances are normally created by :class:`CDDContext`, not directly by
        user code.

        :param context: Owning mixed symbolic context.
        :type context: CDDContext
        :param base_clock: Underlying wrapped UDBM clock.
        :type base_clock: Clock
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> ctx.x.name
            'x'
        """
        self.context = context
        self._base_clock = base_clock
        self.index = base_clock.index
        self.name = base_clock.name
        self.dbm_index = base_clock.dbm_index

    def __repr__(self) -> str:
        """
        Return a debugging representation of the clock.

        :return: Representation containing the fully-qualified clock name.
        :rtype: str

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"], name="c").to_cdd_context()
            >>> repr(ctx.x)
            '<CDDClock c.x>'
        """
        return "<CDDClock {0}>".format(self.get_full_name())

    def get_full_name(self) -> str:
        """
        Return the context-qualified clock name used in string rendering.

        :return: Qualified or plain clock name.
        :rtype: str
        """
        return self._base_clock.get_full_name()

    def __hash__(self) -> int:
        """
        Return a stable hash derived from context identity and clock name.

        :return: Hash value.
        :rtype: int

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> isinstance(hash(ctx.x), int)
            True
        """
        return hash((self.context, self.name))

    def __sub__(self, other: Any) -> "CDDVariableDifference":
        """
        Build a symbolic clock difference.

        :param other: Right-hand clock.
        :type other: Any
        :return: Symbolic clock-difference helper.
        :rtype: CDDVariableDifference
        :raises ValueError: If the clocks belong to different contexts.

        Example::

            >>> from pyudbm import Context
            >>> from pyudbm.binding.ucdd import CDDVariableDifference
            >>> ctx = Context(["x", "y"]).to_cdd_context()
            >>> isinstance(ctx.x - ctx.y, CDDVariableDifference)
            True
        """
        if not isinstance(other, CDDClock):
            return NotImplemented
        if other.context is not self.context:
            raise ValueError("Clock subtraction requires clocks from the same CDDContext.")
        return CDDVariableDifference([self, other])

    def __le__(self, bound: Any) -> Any:
        """
        Build the non-strict upper-bound constraint ``clock <= bound``.

        :param bound: Integer upper bound.
        :type bound: Any
        :return: Equivalent pure-clock CDD.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> (ctx.x <= 3).to_federation() == (ctx.base_context.x <= 3)
            True
        """
        if type(bound) is not int:
            return NotImplemented
        return CDD.from_federation(self._base_clock <= bound, cdd_context=self.context)

    def __ge__(self, bound: Any) -> Any:
        """
        Build the non-strict lower-bound constraint ``clock >= bound``.

        :param bound: Integer lower bound.
        :type bound: Any
        :return: Equivalent pure-clock CDD.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> (ctx.x >= 2).to_federation() == (ctx.base_context.x >= 2)
            True
        """
        if type(bound) is not int:
            return NotImplemented
        return CDD.from_federation(self._base_clock >= bound, cdd_context=self.context)

    def __lt__(self, bound: Any) -> Any:
        """
        Build the strict upper-bound constraint ``clock < bound``.

        :param bound: Integer upper bound.
        :type bound: Any
        :return: Equivalent pure-clock CDD.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> (ctx.x < 4).to_federation() == (ctx.base_context.x < 4)
            True
        """
        if type(bound) is not int:
            return NotImplemented
        return CDD.from_federation(self._base_clock < bound, cdd_context=self.context)

    def __gt__(self, bound: Any) -> Any:
        """
        Build the strict lower-bound constraint ``clock > bound``.

        :param bound: Integer lower bound.
        :type bound: Any
        :return: Equivalent pure-clock CDD.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> (ctx.x > 1).to_federation() == (ctx.base_context.x > 1)
            True
        """
        if type(bound) is not int:
            return NotImplemented
        return CDD.from_federation(self._base_clock > bound, cdd_context=self.context)

    def __eq__(self, other: Any) -> Any:
        """
        Build equality to a constant, or compare identity otherwise.

        :param other: Integer bound or arbitrary object.
        :type other: Any
        :return: CDD equality constraint for integers, otherwise identity
            comparison result.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> (ctx.x == 2).to_federation() == (ctx.base_context.x == 2)
            True
        """
        if type(other) is int:
            return CDD.from_federation(self._base_clock == other, cdd_context=self.context)
        return self is other

    def __ne__(self, other: Any) -> Any:
        """
        Build disequality to a constant, or compare identity otherwise.

        :param other: Integer bound or arbitrary object.
        :type other: Any
        :return: CDD disequality constraint for integers, otherwise identity
            comparison result.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> (ctx.x != 2).to_federation() == (ctx.base_context.x != 2)
            True
        """
        if type(other) is int:
            return CDD.from_federation(self._base_clock != other, cdd_context=self.context)
        return not self.__eq__(other)


class CDDVariableDifference:
    """
    Symbolic difference between two :class:`CDDClock` variables.

    This helper mirrors :class:`~pyudbm.binding.udbm.VariableDifference`, but
    every comparison returns a :class:`CDD`.

    :param variables: Two clocks from the same :class:`CDDContext`.
    :type variables: list[CDDClock]
    :ivar context: Shared owning context.
    :ivar vars: Ordered ``[left, right]`` clock pair.

    Example::

        >>> from pyudbm import Context
        >>> ctx = Context(["x", "y"]).to_cdd_context()
        >>> ((ctx.x - ctx.y) <= 1).to_federation() == (ctx.base_context.x - ctx.base_context.y <= 1)
        True
    """

    def __init__(self, variables: List[CDDClock]):
        """
        Initialize one symbolic clock-difference helper.

        :param variables: Exactly two clocks from the same context.
        :type variables: List[CDDClock]
        :return: ``None``.
        :rtype: None
        :raises ValueError: If the input does not contain exactly two
            compatible clocks.

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x", "y"]).to_cdd_context()
            >>> diff = CDDVariableDifference([ctx.x, ctx.y])
            >>> len(diff.vars)
            2
        """
        if len(variables) != 2:
            raise ValueError("CDDVariableDifference requires exactly two clocks.")
        if variables[0].context is not variables[1].context:
            raise ValueError("CDDVariableDifference requires clocks from the same CDDContext.")
        self.context = variables[0].context
        self.vars = variables

    def __le__(self, bound: Any) -> Any:
        """
        Build ``left - right <= bound``.

        :param bound: Integer upper bound.
        :type bound: Any
        :return: Equivalent CDD constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x", "y"]).to_cdd_context()
            >>> ((ctx.x - ctx.y) <= 1).to_federation() == (ctx.base_context.x - ctx.base_context.y <= 1)
            True
        """
        if type(bound) is not int:
            return NotImplemented
        return CDD.from_federation(
            self.vars[0]._base_clock - self.vars[1]._base_clock <= bound, cdd_context=self.context
        )

    def __ge__(self, bound: Any) -> Any:
        """
        Build ``left - right >= bound``.

        :param bound: Integer lower bound.
        :type bound: Any
        :return: Equivalent CDD constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x", "y"]).to_cdd_context()
            >>> ((ctx.x - ctx.y) >= 1).to_federation() == (ctx.base_context.x - ctx.base_context.y >= 1)
            True
        """
        if type(bound) is not int:
            return NotImplemented
        return CDD.from_federation(
            self.vars[0]._base_clock - self.vars[1]._base_clock >= bound, cdd_context=self.context
        )

    def __lt__(self, bound: Any) -> Any:
        """
        Build ``left - right < bound``.

        :param bound: Integer upper bound.
        :type bound: Any
        :return: Equivalent CDD constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x", "y"]).to_cdd_context()
            >>> ((ctx.x - ctx.y) < 1).to_federation() == (ctx.base_context.x - ctx.base_context.y < 1)
            True
        """
        if type(bound) is not int:
            return NotImplemented
        return CDD.from_federation(
            self.vars[0]._base_clock - self.vars[1]._base_clock < bound, cdd_context=self.context
        )

    def __gt__(self, bound: Any) -> Any:
        """
        Build ``left - right > bound``.

        :param bound: Integer lower bound.
        :type bound: Any
        :return: Equivalent CDD constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x", "y"]).to_cdd_context()
            >>> ((ctx.x - ctx.y) > 1).to_federation() == (ctx.base_context.x - ctx.base_context.y > 1)
            True
        """
        if type(bound) is not int:
            return NotImplemented
        return CDD.from_federation(
            self.vars[0]._base_clock - self.vars[1]._base_clock > bound, cdd_context=self.context
        )

    def __eq__(self, bound: Any) -> Any:
        """
        Build ``left - right == bound`` for integer operands.

        :param bound: Integer difference value or arbitrary object.
        :type bound: Any
        :return: CDD equality constraint for integers, otherwise ``False``.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x", "y"]).to_cdd_context()
            >>> ((ctx.x - ctx.y) == 0).to_federation() == (ctx.base_context.x - ctx.base_context.y == 0)
            True
        """
        if type(bound) is not int:
            return False
        return CDD.from_federation(
            self.vars[0]._base_clock - self.vars[1]._base_clock == bound, cdd_context=self.context
        )

    def __ne__(self, bound: Any) -> Any:
        """
        Build ``left - right != bound`` for integer operands.

        :param bound: Integer difference value or arbitrary object.
        :type bound: Any
        :return: CDD disequality constraint for integers, otherwise ``True``.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x", "y"]).to_cdd_context()
            >>> ((ctx.x - ctx.y) != 0).to_federation() == (ctx.base_context.x - ctx.base_context.y != 0)
            True
        """
        if type(bound) is not int:
            return True
        return CDD.from_federation(
            self.vars[0]._base_clock - self.vars[1]._base_clock != bound, cdd_context=self.context
        )


class CDDBool:
    """
    Boolean variable inside a :class:`CDDContext`.

    The variable object is intentionally lightweight. Using it in symbolic
    expressions transparently produces :class:`CDD` objects.

    :param context: Owning mixed symbolic context.
    :type context: CDDContext
    :param name: Declared boolean name.
    :type name: str
    :param level: Native BDD level in the global UCDD runtime.
    :type level: int
    :ivar context: Owning mixed symbolic context.
    :ivar name: User-visible boolean name.
    :ivar level: Native BDD level.

    Example::

        >>> from pyudbm import Context
        >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
        >>> (ctx.flag & (ctx.x <= 2)).extract_bdd_and_dbm().dbm.to_cdd().to_federation() == (ctx.base_context.x <= 2)
        True
    """

    def __init__(self, context: "CDDContext", name: str, level: int):
        """
        Initialize one boolean variable wrapper.

        Instances are normally created by :class:`CDDContext`.

        :param context: Owning mixed symbolic context.
        :type context: CDDContext
        :param name: Declared boolean name.
        :type name: str
        :param level: Native BDD level.
        :type level: int
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> ctx.flag.name
            'flag'
        """
        self.context = context
        self.name = name
        self.level = level

    def __repr__(self) -> str:
        """
        Return a debugging representation of the boolean variable.

        :return: Representation containing the fully-qualified name.
        :rtype: str

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"], name="c").to_cdd_context(bools=["flag"])
            >>> repr(ctx.flag)
            '<CDDBool c.flag>'
        """
        return "<CDDBool {0}>".format(self.get_full_name())

    def __hash__(self) -> int:
        """
        Return a stable hash derived from context, name, and level.

        :return: Hash value.
        :rtype: int

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> isinstance(hash(ctx.flag), int)
            True
        """
        return hash((self.context, self.name, self.level))

    def get_full_name(self) -> str:
        """
        Return the context-qualified boolean name.

        :return: Qualified or plain boolean name.
        :rtype: str
        """
        if self.context.name:
            return "{0}.{1}".format(self.context.name, self.name)
        return self.name

    def as_cdd(self) -> "CDD":
        """
        Return this boolean variable as a one-node symbolic CDD.

        :return: Positive boolean literal.
        :rtype: CDD
        """
        return CDD.bddvar(self.context, self.level)

    def __invert__(self) -> "CDD":
        """
        Return the negated boolean literal.

        :return: Negative boolean literal.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> (~ctx.flag).equiv(CDD.bddnvar(ctx, "flag"))
            True
        """
        return CDD.bddnvar(self.context, self.level)

    def __and__(self, other: Any) -> "CDD":
        """
        Return the conjunction with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Conjoined symbolic set.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> (ctx.flag & (ctx.x <= 2)).extract_bdd_and_dbm().has_bdd_part()
            True
        """
        return self.as_cdd() & other

    def __rand__(self, other: Any) -> "CDD":
        """
        Return the reflected conjunction with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Conjoined symbolic set.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> ((ctx.x <= 2) & ctx.flag).equiv(ctx.flag & (ctx.x <= 2))
            True
        """
        return CDD._coerce_symbolic(other, self.context) & self.as_cdd()

    def __or__(self, other: Any) -> "CDD":
        """
        Return the disjunction with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Union of the two symbolic sets.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> (ctx.flag | ~ctx.flag).is_true()
            True
        """
        return self.as_cdd() | other

    def __ror__(self, other: Any) -> "CDD":
        """
        Return the reflected disjunction with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Union of the two symbolic sets.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> ((ctx.x <= 2) | ctx.flag).equiv(ctx.flag | (ctx.x <= 2))
            True
        """
        return CDD._coerce_symbolic(other, self.context) | self.as_cdd()

    def __xor__(self, other: Any) -> "CDD":
        """
        Return the exclusive-or with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Exclusive-or symbolic set.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> (ctx.flag ^ ctx.flag).is_false()
            True
        """
        return self.as_cdd() ^ other

    def __rxor__(self, other: Any) -> "CDD":
        """
        Return the reflected exclusive-or with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Exclusive-or symbolic set.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> ((ctx.x <= 2) ^ ctx.flag).equiv(ctx.flag ^ (ctx.x <= 2))
            True
        """
        return CDD._coerce_symbolic(other, self.context) ^ self.as_cdd()

    def __sub__(self, other: Any) -> "CDD":
        """
        Return the set difference with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Symbolic set difference.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> (ctx.flag - ctx.flag).is_false()
            True
        """
        return self.as_cdd() - other

    def __rsub__(self, other: Any) -> "CDD":
        """
        Return the reflected set difference with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Symbolic set difference ``other - self``.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> (((ctx.x <= 2) | ctx.flag) - ctx.flag).contains_dbm((ctx.base_context.x <= 2).to_dbm_list()[0])
            True
        """
        return CDD._coerce_symbolic(other, self.context) - self.as_cdd()

    def __eq__(self, other: Any) -> Any:
        """
        Compare the boolean variable with a concrete boolean.

        :param other: Boolean literal or arbitrary object.
        :type other: Any
        :return: Positive or negative literal for booleans, otherwise identity
            comparison result.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> (ctx.flag == True).equiv(ctx.flag.as_cdd())
            True
        """
        if type(other) is bool:
            return self.as_cdd() if other else ~self.as_cdd()
        return self is other

    def __ne__(self, other: Any) -> Any:
        """
        Compare the boolean variable for disequality with a concrete boolean.

        :param other: Boolean literal or arbitrary object.
        :type other: Any
        :return: Negative or positive literal for booleans, otherwise identity
            comparison result.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> (ctx.flag != True).equiv(~ctx.flag.as_cdd())
            True
        """
        if type(other) is bool:
            return ~self.as_cdd() if other else self.as_cdd()
        return not self.__eq__(other)


class CDDContext:
    """
    Mixed clock/boolean symbolic context for UCDD.

    A :class:`CDDContext` wraps one clock layout together with an ordered set
    of boolean variables. Clock naming reuses the existing
    :class:`~pyudbm.binding.udbm.Context` semantics so that federation and CDD
    conversions stay dimension-stable.

    :param clocks: Clock names when creating a fresh compatibility context.
    :type clocks: iterable[str]
    :param bools: Boolean variable names.
    :type bools: iterable[str]
    :param name: Optional context display name.
    :type name: str or None
    :ivar base_context: Wrapped clock-only :class:`Context`.
    :ivar clocks: List of :class:`CDDClock` objects in declaration order.
    :ivar bools: List of :class:`CDDBool` objects in declaration order.
    :ivar dimension: DBM / CDD dimension including the reference clock.

    Example::

        >>> from pyudbm import Context
        >>> ctx = Context(["x", "y"], name="c").to_cdd_context(bools=["door_open"])
        >>> ctx["x"] is ctx.x
        True
        >>> ctx["door_open"] is ctx.door_open
        True
        >>> ctx.dimension
        3
    """

    def __init__(self, clocks: Iterable[str], bools: Iterable[str] = (), name: Optional[str] = None):
        """
        Initialize a mixed clock/boolean symbolic context.

        :param clocks: Clock names to declare.
        :type clocks: Iterable[str]
        :param bools: Boolean variable names to declare.
        :type bools: Iterable[str]
        :param name: Optional display prefix used for rendering.
        :type name: str or None
        :return: ``None``.
        :rtype: None
        :raises ValueError: If boolean names are duplicated or collide with
            clock names.

        Example::

            >>> ctx = CDDContext(["x", "y"], bools=["flag"], name="c")
            >>> ctx.bool_names
            ('flag',)
        """
        self._base_context = Context(list(clocks), name=name)
        self._initialize(tuple(bools))

    @classmethod
    def from_context(
        cls, context: Context, bools: Iterable[str] = (), name: Optional[str] = None
    ) -> "CDDContext":
        """
        Build a :class:`CDDContext` from an existing :class:`Context`.

        The resulting object preserves the existing clock order so that
        :class:`Federation` and :class:`DBM` objects from the source context can
        be converted without dimension remapping.

        :param context: Existing clock-only context.
        :type context: Context
        :param bools: Boolean variable names to add.
        :type bools: Iterable[str]
        :param name: Optional display-name override.
        :type name: str or None
        :return: New mixed symbolic context.
        :rtype: CDDContext

        Example::

            >>> from pyudbm import Context
            >>> base = Context(["x"], name="c")
            >>> mixed = CDDContext.from_context(base, bools=["flag"])
            >>> mixed.base_context is base
            True
        """

        result = cls.__new__(cls)
        result._base_context = context if name is None or name == context.name else Context(_clock_name_tuple(context), name=name)
        result._initialize(tuple(bools))
        return result

    def _initialize(self, bool_names: Tuple[str, ...]) -> None:
        if len(set(bool_names)) != len(bool_names):
            raise ValueError("CDDContext boolean names must be unique.")
        if set(bool_names) & set(_clock_name_tuple(self._base_context)):
            overlap = sorted(set(bool_names) & set(_clock_name_tuple(self._base_context)))
            raise ValueError("CDDContext boolean names cannot collide with clock names: {0}".format(", ".join(overlap)))

        layout = _ensure_runtime_layout(len(self._base_context.clocks) + 1, bool_names)

        self.name = self._base_context.name
        self.clock_names = tuple(clock.name for clock in self._base_context.clocks)
        self.bool_names = bool_names
        self.dimension = len(self._base_context.clocks) + 1

        self.clocks = []  # type: List[CDDClock]
        self._clock_by_name = {}  # type: Dict[str, CDDClock]
        for base_clock in self._base_context.clocks:
            clock = CDDClock(self, base_clock)
            self.clocks.append(clock)
            self._clock_by_name[clock.name] = clock
            if not hasattr(self, clock.name):
                setattr(self, clock.name, clock)

        self.bools = []  # type: List[CDDBool]
        self._bool_by_name = {}  # type: Dict[str, CDDBool]
        self._bool_by_level = {}  # type: Dict[int, CDDBool]
        for name, level in zip(bool_names, layout.bool_levels):
            bool_var = CDDBool(self, name, level)
            self.bools.append(bool_var)
            self._bool_by_name[name] = bool_var
            self._bool_by_level[level] = bool_var
            if not hasattr(self, name):
                setattr(self, name, bool_var)

    @property
    def base_context(self) -> Context:
        """
        Return the underlying clock-only :class:`Context`.

        :return: Wrapped clock-only context.
        :rtype: Context
        """

        return self._base_context

    def __getitem__(self, name: str) -> Union[CDDClock, CDDBool]:
        """
        Return one declared clock or boolean variable by name.

        :param name: Clock or boolean variable name.
        :type name: str
        :return: Matching symbolic variable.
        :rtype: CDDClock or CDDBool
        :raises KeyError: If the name is unknown.

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"], name="c").to_cdd_context(bools=["flag"])
            >>> ctx["x"] is ctx.x
            True
        """
        if name in self._clock_by_name:
            return self._clock_by_name[name]
        if name in self._bool_by_name:
            return self._bool_by_name[name]
        raise KeyError(name)

    def __hash__(self) -> int:
        """
        Return a stable hash derived from clock names, boolean names, and the
        display name.

        :return: Hash value.
        :rtype: int

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> isinstance(hash(ctx), int)
            True
        """
        return hash((self.clock_names, self.bool_names, self.name))

    def clock(self, name: str) -> CDDClock:
        """
        Return one clock variable by name.

        :param name: Declared clock name.
        :type name: str
        :return: Matching clock variable.
        :rtype: CDDClock
        """

        return self._clock_by_name[name]

    def bool(self, name: str) -> CDDBool:
        """
        Return one boolean variable by name.

        :param name: Declared boolean name.
        :type name: str
        :return: Matching boolean variable.
        :rtype: CDDBool
        """

        return self._bool_by_name[name]

    def level_info(self, level: int) -> CDDLevelInfo:
        """
        Return one decoded runtime level descriptor.

        :param level: Runtime level index.
        :type level: int
        :return: Immutable level-info snapshot.
        :rtype: CDDLevelInfo
        """

        info = _NativeCDDRuntime.get_level_info(level)
        return CDDLevelInfo(level=level, type=info.type, clock1=info.clock1, clock2=info.clock2, diff=info.diff)

    def all_level_info(self) -> List[CDDLevelInfo]:
        """
        Return all currently visible runtime level descriptors.

        :return: Level descriptors in runtime order.
        :rtype: List[CDDLevelInfo]
        """

        return [self.level_info(level) for level in range(_NativeCDDRuntime.get_level_count())]

    def bool_name_for_level(self, level: int) -> str:
        """
        Return the declared boolean name for one runtime level.

        :param level: Runtime BDD level.
        :type level: int
        :return: Declared boolean name.
        :rtype: str
        """

        return self._bool_by_level[level].name

    def true(self) -> "CDD":
        """
        Return the tautological CDD for this context.

        :return: Symbolic tautology in this context.
        :rtype: CDD
        """

        return CDD.true(self)

    def false(self) -> "CDD":
        """
        Return the empty CDD for this context.

        :return: Empty symbolic set in this context.
        :rtype: CDD
        """

        return CDD.false(self)


class BDDTraceSet:
    """
    Iterable wrapper around the native ``bdd_arrays`` structure.

    The underlying native object stores one collection of BDD traces extracted
    from a symbolic CDD. The Python wrapper turns that low-level array-shaped
    data into normal Python iteration helpers.

    Iteration yields sparse dictionaries mapping boolean names to truth values.
    This is useful when a CDD is logically a pure BDD, or when only the
    boolean portion of a mixed symbolic state is relevant.

    :param context: Owning symbolic context whose boolean names label the
        extracted traces.
    :type context: CDDContext
    :param native: Native ``bdd_arrays`` wrapper returned by the thin UCDD
        binding.
    :type native: Any
    :ivar context: Owning symbolic context.

    Example::

        >>> from pyudbm import Context
        >>> ctx = Context(["x"]).to_cdd_context(bools=["door_open", "alarm"])
        >>> traces = (ctx.door_open | ctx.alarm).bdd_traces()
        >>> isinstance(traces.to_dicts(), list)
        True
    """

    def __init__(self, context: CDDContext, native: Any):
        """
        Initialize one boolean-trace wrapper.

        Instances are usually created by :meth:`CDD.bdd_traces`.

        :param context: Owning symbolic context.
        :type context: CDDContext
        :param native: Native ``bdd_arrays`` object.
        :type native: Any
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> traces = ctx.flag.bdd_traces()
            >>> isinstance(traces, BDDTraceSet)
            True
        """
        self.context = context
        self._native = native

    def __len__(self) -> int:
        """
        Return the number of extracted boolean traces.

        :return: Trace count.
        :rtype: int

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> len(ctx.flag.bdd_traces()) >= 1
            True
        """
        return self._native.num_traces

    def _iter_rows(self) -> Iterator[Tuple[Tuple[str, bool], ...]]:
        for vars_row, values_row in zip(self._native.vars_matrix(), self._native.values_matrix()):
            row = []
            for level, value in zip(vars_row, values_row):
                if level < 0 or value < 0:
                    continue
                row.append((self.context.bool_name_for_level(level), bool(value)))
            yield tuple(row)

    def __iter__(self) -> Iterator[Dict[str, bool]]:
        """
        Iterate over sparse boolean assignments.

        Each yielded mapping contains only the boolean variables that were
        explicitly present on the corresponding BDD path.

        :return: Iterator over sparse boolean assignments.
        :rtype: Iterator[Dict[str, bool]]

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> next(iter(ctx.flag.bdd_traces()))["flag"]
            True
        """
        for row in self._iter_rows():
            yield dict(row)

    def to_rows(self) -> List[Tuple[Tuple[str, bool], ...]]:
        """
        Return each trace as an ordered tuple of ``(bool_name, value)`` pairs.

        This preserves the native row order and is useful when a deterministic
        positional representation is more convenient than dictionaries.

        :return: Ordered boolean assignments.
        :rtype: List[Tuple[Tuple[str, bool], ...]]
        """

        return list(self._iter_rows())

    def to_dicts(self, sparse: bool = True) -> List[Dict[str, Optional[bool]]]:
        """
        Return traces as dictionaries keyed by boolean name.

        :param sparse: When ``True``, omit unspecified booleans. When
            ``False``, include every boolean name and use ``None`` for
            unspecified values.
        :type sparse: bool
        :return: Boolean assignments keyed by variable name.
        :rtype: List[Dict[str, Optional[bool]]]

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> rows = ctx.flag.bdd_traces().to_dicts(sparse=False)
            >>> rows[0]["flag"]
            True
        """

        rows = []
        for row in self._iter_rows():
            mapping = dict(row)
            if not sparse:
                complete = {name: mapping.get(name) for name in self.context.bool_names}
                rows.append(complete)
            else:
                rows.append(mapping)
        return rows


class CDDExtraction:
    """
    High-level wrapper for one ``extract_bdd_and_dbm`` result.

    A mixed CDD path can be seen as a boolean guard together with one extracted
    DBM zone. This wrapper keeps those parts in public high-level objects so
    callers can continue working with familiar :class:`CDD` and :class:`DBM`
    values.

    :param context: Owning symbolic context.
    :type context: CDDContext
    :param native: Native extraction result object returned by the thin UCDD
        binding.
    :type native: Any
    :ivar remainder: Remaining symbolic graph after one DBM extraction.
    :ivar bdd_part: Boolean guard associated with the extracted DBM.
    :ivar dbm: Extracted DBM wrapped through the existing :class:`DBM` class.

    Example::

        >>> from pyudbm import Context
        >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
        >>> extraction = (ctx.flag & (ctx.x <= 3)).extract_bdd_and_dbm()
        >>> extraction.has_bdd_part()
        True
    """

    def __init__(self, context: CDDContext, native: Any):
        """
        Initialize one extracted mixed symbolic fragment.

        :param context: Owning symbolic context.
        :type context: CDDContext
        :param native: Native extraction result.
        :type native: Any
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> extraction = (ctx.flag & (ctx.x <= 2)).extract_bdd_and_dbm()
            >>> isinstance(extraction, CDDExtraction)
            True
        """
        self.context = context
        self.remainder = CDD._from_native(context, native.cdd_part)
        self.bdd_part = CDD._from_native(context, native.bdd_part)
        self.dbm = DBM._from_raw_matrix(context.base_context, native.dbm)

    def to_federation(self, require_pure: bool = True) -> Federation:
        """
        Convert the extracted DBM to a one-zone federation when its boolean
        guard is trivial.

        :param require_pure: Whether to reject non-trivial boolean guards with
            :class:`ValueError`. When ``False``, mixed guarded conversion still
            raises :class:`NotImplementedError` because this wrapper does not
            yet materialize guarded federation fragments.
        :type require_pure: bool
        :return: One-zone federation equivalent to :attr:`dbm`.
        :rtype: Federation
        :raises ValueError: If the extraction still carries a boolean guard and
            ``require_pure`` is ``True``.
        :raises NotImplementedError: If guarded federation conversion is
            requested with ``require_pure=False``.
        """

        if not self.bdd_part.is_true():
            if require_pure:
                raise ValueError("Cannot convert an extracted DBM with a non-trivial boolean guard to Federation.")
            raise NotImplementedError("Splitting mixed CDD fragments into guarded federations is not implemented.")

        native = _NativeFederation.from_dbm_list([list(self.dbm._raw_matrix())], self.context.dimension)
        return Federation._from_native(self.context.base_context, native)

    def has_bdd_part(self) -> bool:
        """
        Return whether the extraction carried a non-trivial boolean guard.

        :return: ``True`` if :attr:`bdd_part` is not the tautology.
        :rtype: bool
        """

        return not self.bdd_part.is_true()


class CDD:
    """
    High-level symbolic Clock Difference Diagram wrapper.

    Instances behave like symbolic sets. Boolean variables and clock
    constraints can be combined through the normal Python operators ``&``,
    ``|``, ``^``, ``-``, and ``~``.

    Conceptually this class is the mixed-symbolic counterpart to
    :class:`~pyudbm.binding.udbm.Federation`:

    * pure clock states can move between :class:`Federation` and :class:`CDD`;
    * boolean literals can be combined with clock constraints in one symbolic
      graph;
    * extraction helpers expose individual DBM fragments and their associated
      boolean guards.

    Unless stated otherwise, operations return new symbolic objects and do not
    mutate the original CDD.

    :param context: Owning mixed symbolic context.
    :type context: CDDContext
    :param native: Native UCDD handle.
    :type native: _NativeCDD
    :ivar context: Owning mixed symbolic context.

    Example::

        >>> from pyudbm import Context
        >>> ctx = Context(["x", "y"], name="c").to_cdd_context(bools=["door_open"])
        >>> state = ((ctx.x <= 5) & ctx.door_open) | ((ctx.y <= 2) & ~ctx.door_open)
        >>> isinstance(state.reduce(), CDD)
        True
    """

    def __init__(self, context: CDDContext, native: _NativeCDD):
        """
        Initialize one high-level symbolic CDD wrapper.

        Instances are normally created through the class constructors such as
        :meth:`true`, :meth:`from_federation`, or boolean / clock DSL
        expressions.

        :param context: Owning mixed symbolic context.
        :type context: CDDContext
        :param native: Native UCDD handle.
        :type native: _NativeCDD
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> state = CDD.true(ctx)
            >>> isinstance(state, CDD)
            True
        """
        self.context = context
        self._cdd = native

    @classmethod
    def _from_native(cls, context: CDDContext, native: _NativeCDD) -> "CDD":
        return cls(context, native)

    @staticmethod
    def _coerce_symbolic(value: Any, context: CDDContext) -> "CDD":
        if isinstance(value, CDD):
            if value.context is not context:
                raise ValueError("CDD operations require the same CDDContext.")
            return value
        if isinstance(value, CDDBool):
            if value.context is not context:
                raise ValueError("CDD operations require the same CDDContext.")
            return value.as_cdd()
        if isinstance(value, Federation):
            return CDD.from_federation(value, cdd_context=context)
        if isinstance(value, DBM):
            return CDD.from_dbm(value, cdd_context=context)
        raise TypeError("Unsupported symbolic operand type: {0}.".format(type(value).__name__))

    @classmethod
    def true(cls, context: Union[CDDContext, Context]) -> "CDD":
        """
        Return the tautological symbolic set for one context.

        :param context: Target mixed context, or a plain clock
            :class:`Context` that will be promoted automatically.
        :type context: CDDContext or Context
        :return: Tautological symbolic set.
        :rtype: CDD
        """
        cdd_context = _coerce_cdd_context(context)
        return cls._from_native(cdd_context, _NativeCDD.true())

    @classmethod
    def false(cls, context: Union[CDDContext, Context]) -> "CDD":
        """
        Return the empty symbolic set for one context.

        :param context: Target mixed context, or a plain clock
            :class:`Context` that will be promoted automatically.
        :type context: CDDContext or Context
        :return: Empty symbolic set.
        :rtype: CDD
        """
        cdd_context = _coerce_cdd_context(context)
        return cls._from_native(cdd_context, _NativeCDD.false())

    @classmethod
    def upper(cls, context: Union[CDDContext, Context], i: int, j: int, bound: int) -> "CDD":
        """
        Build the raw clock-difference constraint ``x_i - x_j <= bound``.

        This is the low-level indexed constructor mirroring the native UCDD
        API. Most user code should prefer the clock DSL such as
        ``ctx.x - ctx.y <= 3``.

        :param context: Target mixed context, or a plain clock context.
        :type context: CDDContext or Context
        :param i: Left DBM clock index.
        :type i: int
        :param j: Right DBM clock index.
        :type j: int
        :param bound: Upper bound.
        :type bound: int
        :return: Equivalent pure-clock CDD.
        :rtype: CDD
        """
        cdd_context = _coerce_cdd_context(context)
        return cls._from_native(cdd_context, _NativeCDD.upper(i, j, bound))

    @classmethod
    def lower(cls, context: Union[CDDContext, Context], i: int, j: int, bound: int) -> "CDD":
        """
        Build the raw clock-difference constraint ``x_i - x_j >= bound``.

        :param context: Target mixed context, or a plain clock context.
        :type context: CDDContext or Context
        :param i: Left DBM clock index.
        :type i: int
        :param j: Right DBM clock index.
        :type j: int
        :param bound: Lower bound.
        :type bound: int
        :return: Equivalent pure-clock CDD.
        :rtype: CDD
        """
        cdd_context = _coerce_cdd_context(context)
        return cls._from_native(cdd_context, _NativeCDD.lower(i, j, bound))

    @classmethod
    def interval(cls, context: Union[CDDContext, Context], i: int, j: int, low: int, up: int) -> "CDD":
        """
        Build the raw interval constraint ``low <= x_i - x_j <= up``.

        :param context: Target mixed context, or a plain clock context.
        :type context: CDDContext or Context
        :param i: Left DBM clock index.
        :type i: int
        :param j: Right DBM clock index.
        :type j: int
        :param low: Inclusive lower bound.
        :type low: int
        :param up: Inclusive upper bound.
        :type up: int
        :return: Equivalent pure-clock CDD.
        :rtype: CDD
        """
        cdd_context = _coerce_cdd_context(context)
        return cls._from_native(cdd_context, _NativeCDD.interval(i, j, low, up))

    @classmethod
    def bddvar(cls, context: Union[CDDContext, Context], level_or_name: Union[int, str]) -> "CDD":
        """
        Build the positive literal of one boolean variable.

        :param context: Target mixed context, or a plain clock context that
            has already been promoted to a compatible boolean layout.
        :type context: CDDContext or Context
        :param level_or_name: Boolean runtime level or declared variable name.
        :type level_or_name: int or str
        :return: Positive boolean literal.
        :rtype: CDD
        """
        cdd_context = _coerce_cdd_context(context)
        if isinstance(level_or_name, str):
            level = cdd_context.bool(level_or_name).level
        else:
            level = int(level_or_name)
        return cls._from_native(cdd_context, _NativeCDD.bddvar(level))

    @classmethod
    def bddnvar(cls, context: Union[CDDContext, Context], level_or_name: Union[int, str]) -> "CDD":
        """
        Build the negative literal of one boolean variable.

        :param context: Target mixed context, or a plain clock context that
            has already been promoted to a compatible boolean layout.
        :type context: CDDContext or Context
        :param level_or_name: Boolean runtime level or declared variable name.
        :type level_or_name: int or str
        :return: Negative boolean literal.
        :rtype: CDD
        """
        cdd_context = _coerce_cdd_context(context)
        if isinstance(level_or_name, str):
            level = cdd_context.bool(level_or_name).level
        else:
            level = int(level_or_name)
        return cls._from_native(cdd_context, _NativeCDD.bddnvar(level))

    @classmethod
    def from_dbm(cls, dbm: DBM, cdd_context: Optional[CDDContext] = None) -> "CDD":
        """
        Build a pure clock CDD from one :class:`DBM` snapshot.

        :param dbm: Source DBM snapshot.
        :type dbm: DBM
        :param cdd_context: Optional target mixed context. When omitted, a
            compatible clock-only :class:`CDDContext` is built automatically
            from ``dbm.context``.
        :type cdd_context: CDDContext or None
        :return: Equivalent pure-clock symbolic set.
        :rtype: CDD
        :raises TypeError: If ``dbm`` is not a :class:`DBM`.
        :raises ValueError: If the target context has an incompatible clock
            layout.

        Example::

            >>> from pyudbm import Context
            >>> base = Context(["x"], name="c")
            >>> dbm = (base.x <= 3).to_dbm_list()[0]
            >>> CDD.from_dbm(dbm).to_federation() == (base.x <= 3)
            True
        """

        if not isinstance(dbm, DBM):
            raise TypeError("CDD.from_dbm expects a DBM instance.")

        context = cdd_context or CDDContext.from_context(dbm.context)
        if not _compatible_clock_layout(context.base_context, dbm.context):
            raise ValueError("CDDContext clock layout is incompatible with the DBM context.")

        native = _NativeCDD.from_dbm(list(dbm._raw_matrix()), dbm.dimension)
        return cls._from_native(context, native)

    @classmethod
    def from_federation(cls, federation: Federation, cdd_context: Optional[CDDContext] = None) -> "CDD":
        """
        Build a pure clock CDD from a :class:`Federation`.

        :param federation: Source federation.
        :type federation: Federation
        :param cdd_context: Optional target mixed context. When omitted, a
            compatible clock-only :class:`CDDContext` is built automatically
            from ``federation.context``.
        :type cdd_context: CDDContext or None
        :return: Equivalent pure-clock symbolic set.
        :rtype: CDD
        :raises TypeError: If ``federation`` is not a :class:`Federation`.
        :raises ValueError: If the target context has an incompatible clock
            layout.
        """

        if not isinstance(federation, Federation):
            raise TypeError("CDD.from_federation expects a Federation instance.")

        context = cdd_context or CDDContext.from_context(federation.context)
        if not _compatible_clock_layout(context.base_context, federation.context):
            raise ValueError("CDDContext clock layout is incompatible with the Federation context.")

        result = cls.false(context)
        for dbm in federation.to_dbm_list():
            result |= cls.from_dbm(dbm, cdd_context=context)
        return result.reduce()

    def copy(self) -> "CDD":
        """
        Return a copied symbolic handle for the same symbolic set.

        :return: Semantically equivalent copied CDD.
        :rtype: CDD
        """
        return CDD._from_native(self.context, self._cdd.copy())

    def __repr__(self) -> str:
        """
        Return a compact debugging representation.

        :return: Representation containing node count and context name.
        :rtype: str

        Example::

            >>> from pyudbm import Context
            >>> state = (Context(["x"], name="c").to_cdd_context().x <= 3)
            >>> repr(state).startswith("<CDD nodes=")
            True
        """
        return "<CDD nodes={0} context={1!r}>".format(self.nodecount(), self.context.name)

    def __and__(self, other: Any) -> "CDD":
        """
        Return the conjunction / symbolic intersection with another operand.

        :param other: Another :class:`CDD`, :class:`CDDBool`,
            :class:`Federation`, or :class:`DBM` from the same clock layout.
        :type other: Any
        :return: Conjoined symbolic set.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> ((ctx.x <= 3) & ctx.flag).extract_bdd_and_dbm().has_bdd_part()
            True
        """
        other_cdd = self._coerce_symbolic(other, self.context)
        return CDD._from_native(self.context, self._cdd.and_op(other_cdd._cdd))

    def __rand__(self, other: Any) -> "CDD":
        """
        Return the reflected conjunction with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Conjoined symbolic set.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> ((ctx.x <= 3) & ctx.flag).equiv(ctx.flag & (ctx.x <= 3))
            True
        """
        return self._coerce_symbolic(other, self.context) & self

    def __or__(self, other: Any) -> "CDD":
        """
        Return the symbolic union with another operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Union of the two symbolic sets.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> ((ctx.x <= 2) | (ctx.x >= 5)).to_federation() == ((ctx.base_context.x <= 2) | (ctx.base_context.x >= 5))
            True
        """
        other_cdd = self._coerce_symbolic(other, self.context)
        return CDD._from_native(self.context, self._cdd.or_op(other_cdd._cdd))

    def __ror__(self, other: Any) -> "CDD":
        """
        Return the reflected union with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Union of the two symbolic sets.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> ((ctx.x <= 2) | ctx.flag).equiv(ctx.flag | (ctx.x <= 2))
            True
        """
        return self._coerce_symbolic(other, self.context) | self

    def __sub__(self, other: Any) -> "CDD":
        """
        Return the symbolic set difference ``self - other``.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Symbolic set difference.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> (((ctx.x <= 5) - (ctx.x <= 2)).to_federation() == ((ctx.base_context.x <= 5) - (ctx.base_context.x <= 2)))
            True
        """
        other_cdd = self._coerce_symbolic(other, self.context)
        return CDD._from_native(self.context, self._cdd.minus_op(other_cdd._cdd))

    def __rsub__(self, other: Any) -> "CDD":
        """
        Return the reflected symbolic set difference ``other - self``.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Symbolic set difference ``other - self``.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> (((ctx.x <= 3) | ctx.flag) - ctx.flag).contains_dbm((ctx.base_context.x <= 3).to_dbm_list()[0])
            True
        """
        return self._coerce_symbolic(other, self.context) - self

    def __xor__(self, other: Any) -> "CDD":
        """
        Return the symbolic exclusive-or with another operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Exclusive-or symbolic set.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> (ctx.flag ^ ctx.flag).is_false()
            True
        """
        other_cdd = self._coerce_symbolic(other, self.context)
        return CDD._from_native(self.context, self._cdd.xor_op(other_cdd._cdd))

    def __rxor__(self, other: Any) -> "CDD":
        """
        Return the reflected exclusive-or with another symbolic operand.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Exclusive-or symbolic set.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> ((ctx.x <= 2) ^ ctx.flag).equiv(ctx.flag ^ (ctx.x <= 2))
            True
        """
        return self._coerce_symbolic(other, self.context) ^ self

    def __invert__(self) -> "CDD":
        """
        Return the symbolic complement.

        :return: Complement of this symbolic set.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> ((~(ctx.x <= 2)) | (ctx.x <= 2)).is_true()
            True
        """
        return CDD._from_native(self.context, self._cdd.invert())

    def __eq__(self, other: Any) -> bool:
        """
        Compare two CDDs by symbolic equivalence.

        Unlike plain handle identity, this checks semantic equivalence inside
        the same :class:`CDDContext`.

        :param other: Object to compare with.
        :type other: Any
        :return: Whether both CDDs denote the same symbolic set.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> (ctx.x <= 3) == CDD.from_federation(ctx.base_context.x <= 3, cdd_context=ctx)
            True
        """
        if not isinstance(other, CDD):
            return False
        if other.context is not self.context:
            return False
        return self._cdd.equiv(other._cdd)

    def __ne__(self, other: Any) -> bool:
        """
        Return whether another object is not semantically equivalent.

        :param other: Object to compare with.
        :type other: Any
        :return: Negation of :meth:`__eq__`.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context()
            >>> (ctx.x <= 3) != (ctx.x <= 2)
            True
        """
        return not self == other

    def ite(self, then_branch: Any, else_branch: Any) -> "CDD":
        """
        Build the symbolic if-then-else ``self ? then_branch : else_branch``.

        :param then_branch: Symbolic branch chosen where ``self`` holds.
        :type then_branch: Any
        :param else_branch: Symbolic branch chosen where ``self`` does not
            hold.
        :type else_branch: Any
        :return: Resulting symbolic combination.
        :rtype: CDD
        """
        then_cdd = self._coerce_symbolic(then_branch, self.context)
        else_cdd = self._coerce_symbolic(else_branch, self.context)
        return CDD._from_native(self.context, self._cdd.ite(then_cdd._cdd, else_cdd._cdd))

    def apply(self, op: int, other: Any) -> "CDD":
        """
        Apply one native binary operator code to another symbolic operand.

        The public constants :data:`OP_AND` and :data:`OP_XOR` expose the
        currently supported operator codes at the Python layer.

        :param op: Native operation code.
        :type op: int
        :param other: Another symbolic operand.
        :type other: Any
        :return: Result of the native binary operation.
        :rtype: CDD
        """
        other_cdd = self._coerce_symbolic(other, self.context)
        return CDD._from_native(self.context, self._cdd.apply(op, other_cdd._cdd))

    def apply_reduce(self, op: int, other: Any) -> "CDD":
        """
        Apply one native binary operator code and reduce the result.

        :param op: Native operation code.
        :type op: int
        :param other: Another symbolic operand.
        :type other: Any
        :return: Reduced result of the native binary operation.
        :rtype: CDD
        """
        other_cdd = self._coerce_symbolic(other, self.context)
        return CDD._from_native(self.context, self._cdd.apply_reduce(op, other_cdd._cdd))

    def reduce(self) -> "CDD":
        """
        Return a reduced symbolic graph.

        Reduction is a common prerequisite for extraction-oriented native UCDD
        operations. High-level helpers such as :meth:`extract_bdd_and_dbm`
        already call it automatically.

        :return: Reduced symbolic graph.
        :rtype: CDD
        """
        return CDD._from_native(self.context, self._cdd.reduce())

    def reduce2(self) -> "CDD":
        """
        Return the alternative reduced form provided by native UCDD.

        :return: Reduced symbolic graph.
        :rtype: CDD
        """
        return CDD._from_native(self.context, self._cdd.reduce2())

    def equiv(self, other: Any) -> bool:
        """
        Return whether another symbolic operand is semantically equivalent.

        :param other: Another symbolic operand.
        :type other: Any
        :return: Whether both denote the same symbolic set.
        :rtype: bool
        """
        other_cdd = self._coerce_symbolic(other, self.context)
        return self._cdd.equiv(other_cdd._cdd)

    def nodecount(self) -> int:
        """
        Return the native node count reported for this symbolic graph.

        :return: Native node count.
        :rtype: int
        """
        return self._cdd.nodecount()

    def edgecount(self) -> int:
        """
        Return the native edge count reported for this symbolic graph.

        :return: Native edge count.
        :rtype: int
        """
        return self._cdd.edgecount()

    def is_bdd(self) -> bool:
        """
        Return whether this symbolic graph is purely boolean.

        :return: ``True`` if the graph contains only BDD structure.
        :rtype: bool
        """
        return self._cdd.is_bdd()

    def is_true(self) -> bool:
        """
        Return whether this symbolic set is the tautology.

        :return: ``True`` if the symbolic set is universally true.
        :rtype: bool
        """
        return self._cdd.is_true()

    def is_false(self) -> bool:
        """
        Return whether this symbolic set is empty.

        :return: ``True`` if the symbolic set is empty.
        :rtype: bool
        """
        return self._cdd.is_false()

    def remove_negative(self) -> "CDD":
        """
        Remove negative constraints through the native UCDD helper.

        :return: Transformed symbolic set.
        :rtype: CDD
        """
        return CDD._from_native(self.context, self._cdd.remove_negative())

    def delay(self) -> "CDD":
        """
        Apply forward time elapse to the symbolic state.

        This is the mixed-symbolic counterpart to federation ``up``-style
        behavior.

        :return: Time-successor symbolic set.
        :rtype: CDD
        """
        return CDD._from_native(self.context, self._cdd.delay())

    def past(self) -> "CDD":
        """
        Apply inverse time elapse to the symbolic state.

        :return: Past-closed symbolic set.
        :rtype: CDD
        """
        return CDD._from_native(self.context, self._cdd.past())

    def delay_invariant(self, invariant: Any) -> "CDD":
        """
        Apply forward time elapse constrained by an invariant.

        :param invariant: Invariant symbolic set that must remain satisfied
            during time passage.
        :type invariant: Any
        :return: Time-successor symbolic set respecting the invariant.
        :rtype: CDD
        """
        invariant_cdd = self._coerce_symbolic(invariant, self.context)
        return CDD._from_native(self.context, self._cdd.delay_invariant(invariant_cdd._cdd))

    def predt(self, safe: Any) -> "CDD":
        """
        Compute the time predecessor relative to a safe region.

        :param safe: Symbolic set that must remain satisfied during backward
            time propagation.
        :type safe: Any
        :return: Symbolic predecessor set.
        :rtype: CDD
        """
        safe_cdd = self._coerce_symbolic(safe, self.context)
        return CDD._from_native(self.context, self._cdd.predt(safe_cdd._cdd))

    def contains_dbm(self, dbm: DBM) -> bool:
        """
        Return whether one DBM zone is contained in this CDD.

        :param dbm: Candidate DBM zone.
        :type dbm: DBM
        :return: Whether the DBM is contained.
        :rtype: bool
        :raises TypeError: If ``dbm`` is not a :class:`DBM`.
        :raises ValueError: If the DBM context has an incompatible clock
            layout.
        """
        if not isinstance(dbm, DBM):
            raise TypeError("contains_dbm expects a DBM instance.")
        if not _compatible_clock_layout(self.context.base_context, dbm.context):
            raise ValueError("DBM context is incompatible with this CDDContext.")
        return self._cdd.contains_dbm(list(dbm._raw_matrix()), dbm.dimension)

    def extract_dbm(self) -> Tuple["CDD", DBM]:
        """
        Extract one DBM from the reduced CDD and return ``(remainder, dbm)``.

        This helper is convenient for pure-clock iteration where the boolean
        guard is known to be trivial and only the next DBM fragment matters.

        :return: ``(remainder, dbm)`` pair.
        :rtype: tuple[CDD, DBM]
        """

        reduced = self.reduce()
        remainder, raw_dbm = reduced._cdd.extract_dbm(self.context.dimension)
        return CDD._from_native(self.context, remainder), DBM._from_raw_matrix(self.context.base_context, raw_dbm)

    def extract_bdd(self) -> "CDD":
        """
        Extract the bottom BDD of the first reduced DBM path.

        :return: Extracted boolean guard as a CDD.
        :rtype: CDD
        """

        return CDD._from_native(self.context, self.reduce()._cdd.extract_bdd(self.context.dimension))

    def extract_bdd_and_dbm(self) -> CDDExtraction:
        """
        Extract one DBM together with its boolean guard.

        The native operation expects a reduced CDD. The Python wrapper performs
        that reduction automatically so callers do not have to remember the
        precondition.

        :return: High-level extraction bundle containing remainder, BDD guard,
            and DBM fragment.
        :rtype: CDDExtraction
        """

        return CDDExtraction(self.context, self.reduce()._cdd.extract_bdd_and_dbm())

    def bdd_traces(self) -> BDDTraceSet:
        """
        Return the boolean traces of this CDD interpreted as a BDD.

        The result is most meaningful for pure-boolean or BDD-shaped CDDs, but
        the native helper is exposed as-is.

        :return: Iterable boolean-trace wrapper.
        :rtype: BDDTraceSet
        """

        return BDDTraceSet(self.context, self._cdd.bdd_to_array())

    @staticmethod
    def _normalize_clock_reset_mapping(
        context: CDDContext, resets: Optional[Union[Mapping[Union[str, Clock, CDDClock], int], Iterable[Tuple[Union[str, Clock, CDDClock], int]]]]
    ) -> Tuple[List[int], List[int]]:
        if resets is None:
            return [], []

        items = resets.items() if isinstance(resets, Mapping) else list(resets)
        indices = []
        values = []
        for key, value in items:
            if type(value) is not int:
                raise TypeError("Clock reset values must be plain integers.")
            if isinstance(key, str):
                clock = context.clock(key)
            elif isinstance(key, CDDClock):
                clock = key
            elif isinstance(key, Clock):
                if not _compatible_clock_layout(context.base_context, key.context):
                    raise ValueError("Clock reset uses a clock from an incompatible context.")
                clock = context.clock(key.name)
            else:
                raise TypeError("Clock reset keys must be names, Clock objects, or CDDClock objects.")
            if clock.context is not context:
                raise ValueError("Clock reset keys must belong to the same CDDContext.")
            indices.append(clock.dbm_index)
            values.append(value)
        return indices, values

    @staticmethod
    def _normalize_bool_reset_mapping(
        context: CDDContext, resets: Optional[Union[Mapping[Union[str, CDDBool], bool], Iterable[Tuple[Union[str, CDDBool], bool]]]]
    ) -> Tuple[List[int], List[int]]:
        if resets is None:
            return [], []

        items = resets.items() if isinstance(resets, Mapping) else list(resets)
        levels = []
        values = []
        for key, value in items:
            if type(value) is not bool:
                raise TypeError("Boolean reset values must be bool.")
            if isinstance(key, str):
                bool_var = context.bool(key)
            elif isinstance(key, CDDBool):
                bool_var = key
            else:
                raise TypeError("Boolean reset keys must be names or CDDBool objects.")
            if bool_var.context is not context:
                raise ValueError("Boolean reset keys must belong to the same CDDContext.")
            levels.append(bool_var.level)
            values.append(1 if value else 0)
        return levels, values

    @staticmethod
    def _normalize_reset_list(
        context: CDDContext, resets: Optional[Iterable[Union[str, Clock, CDDClock, CDDBool]]], *, bools: bool
    ) -> List[int]:
        if resets is None:
            return []

        result = []
        for item in resets:
            if bools:
                if isinstance(item, str):
                    bool_var = context.bool(item)
                elif isinstance(item, CDDBool):
                    bool_var = item
                else:
                    raise TypeError("Boolean reset lists must contain names or CDDBool objects.")
                if bool_var.context is not context:
                    raise ValueError("Boolean reset lists must use the same CDDContext.")
                result.append(bool_var.level)
            else:
                if isinstance(item, str):
                    clock = context.clock(item)
                elif isinstance(item, CDDClock):
                    clock = item
                elif isinstance(item, Clock):
                    if not _compatible_clock_layout(context.base_context, item.context):
                        raise ValueError("Clock reset list uses a clock from an incompatible context.")
                    clock = context.clock(item.name)
                else:
                    raise TypeError("Clock reset lists must contain names, Clock objects, or CDDClock objects.")
                if clock.context is not context:
                    raise ValueError("Clock reset lists must use the same CDDContext.")
                result.append(clock.dbm_index)
        return result

    def apply_reset(
        self,
        clock_resets: Optional[Union[Mapping[Union[str, Clock, CDDClock], int], Iterable[Tuple[Union[str, Clock, CDDClock], int]]]] = None,
        bool_resets: Optional[Union[Mapping[Union[str, CDDBool], bool], Iterable[Tuple[Union[str, CDDBool], bool]]]] = None,
    ) -> "CDD":
        """
        Apply Python-friendly clock and boolean reset mappings.

        Clock resets use integer assignments, while boolean resets use Python
        ``bool`` values. Keys may be variable names or the corresponding public
        clock / boolean objects.

        :param clock_resets: Mapping or iterable of ``(clock, value)`` pairs.
        :type clock_resets: mapping or iterable or None
        :param bool_resets: Mapping or iterable of ``(bool_var, value)`` pairs.
        :type bool_resets: mapping or iterable or None
        :return: Reset symbolic set.
        :rtype: CDD

        Example::

            >>> from pyudbm import Context
            >>> ctx = Context(["x"]).to_cdd_context(bools=["flag"])
            >>> state = (ctx.x <= 3) & ctx.flag
            >>> isinstance(state.apply_reset({"x": 0}, {"flag": False}), CDD)
            True
        """

        clock_indices, clock_values = self._normalize_clock_reset_mapping(self.context, clock_resets)
        bool_levels, bool_values = self._normalize_bool_reset_mapping(self.context, bool_resets)
        return CDD._from_native(
            self.context, self._cdd.apply_reset(clock_indices, clock_values, bool_levels, bool_values)
        )

    def transition(
        self,
        guard: Any,
        clock_resets: Optional[Union[Mapping[Union[str, Clock, CDDClock], int], Iterable[Tuple[Union[str, Clock, CDDClock], int]]]] = None,
        bool_resets: Optional[Union[Mapping[Union[str, CDDBool], bool], Iterable[Tuple[Union[str, CDDBool], bool]]]] = None,
    ) -> "CDD":
        """
        Apply a guard and then perform clock/boolean resets.

        This corresponds to the common forward symbolic transition pattern:
        intersect with the transition guard, then apply discrete updates.

        :param guard: Transition guard.
        :type guard: Any
        :param clock_resets: Clock reset assignments.
        :type clock_resets: mapping or iterable or None
        :param bool_resets: Boolean reset assignments.
        :type bool_resets: mapping or iterable or None
        :return: Forward transition successor.
        :rtype: CDD
        """

        guard_cdd = self._coerce_symbolic(guard, self.context)
        clock_indices, clock_values = self._normalize_clock_reset_mapping(self.context, clock_resets)
        bool_levels, bool_values = self._normalize_bool_reset_mapping(self.context, bool_resets)
        return CDD._from_native(
            self.context, self._cdd.transition(guard_cdd._cdd, clock_indices, clock_values, bool_levels, bool_values)
        )

    def transition_back(
        self,
        guard: Any,
        update: Any,
        clock_resets: Optional[Iterable[Union[str, Clock, CDDClock]]] = None,
        bool_resets: Optional[Iterable[Union[str, CDDBool]]] = None,
    ) -> "CDD":
        """
        Compute the symbolic backward transition predecessor.

        ``guard`` is the transition guard and ``update`` is the updated post-
        transition symbolic relation used by the native backward operator.

        :param guard: Transition guard.
        :type guard: Any
        :param update: Updated symbolic target.
        :type update: Any
        :param clock_resets: Clocks reset by the transition.
        :type clock_resets: iterable or None
        :param bool_resets: Boolean variables reset by the transition.
        :type bool_resets: iterable or None
        :return: Backward predecessor.
        :rtype: CDD
        """

        guard_cdd = self._coerce_symbolic(guard, self.context)
        update_cdd = self._coerce_symbolic(update, self.context)
        clock_indices = self._normalize_reset_list(self.context, clock_resets, bools=False)
        bool_levels = self._normalize_reset_list(self.context, bool_resets, bools=True)
        return CDD._from_native(
            self.context, self._cdd.transition_back(guard_cdd._cdd, update_cdd._cdd, clock_indices, bool_levels)
        )

    def transition_back_past(
        self,
        guard: Any,
        update: Any,
        clock_resets: Optional[Iterable[Union[str, Clock, CDDClock]]] = None,
        bool_resets: Optional[Iterable[Union[str, CDDBool]]] = None,
    ) -> "CDD":
        """
        Compute the backward predecessor and include inverse time elapse.

        :param guard: Transition guard.
        :type guard: Any
        :param update: Updated symbolic target.
        :type update: Any
        :param clock_resets: Clocks reset by the transition.
        :type clock_resets: iterable or None
        :param bool_resets: Boolean variables reset by the transition.
        :type bool_resets: iterable or None
        :return: Backward predecessor closed under inverse time elapse.
        :rtype: CDD
        """

        guard_cdd = self._coerce_symbolic(guard, self.context)
        update_cdd = self._coerce_symbolic(update, self.context)
        clock_indices = self._normalize_reset_list(self.context, clock_resets, bools=False)
        bool_levels = self._normalize_reset_list(self.context, bool_resets, bools=True)
        return CDD._from_native(
            self.context, self._cdd.transition_back_past(guard_cdd._cdd, update_cdd._cdd, clock_indices, bool_levels)
        )

    def to_federation(self, require_pure: bool = True) -> Federation:
        """
        Convert a pure clock CDD back into a :class:`Federation`.

        A non-trivial boolean guard cannot be represented as a plain
        federation, so mixed CDDs raise by default.

        :param require_pure: Whether to reject mixed CDDs with
            :class:`ValueError`. When ``False``, mixed conversion still raises
            :class:`NotImplementedError` because guarded federation output is
            not materialized by this wrapper.
        :type require_pure: bool
        :return: Equivalent pure-clock federation.
        :rtype: Federation
        :raises ValueError: If this CDD contains non-trivial boolean guards and
            ``require_pure`` is ``True``.
        :raises NotImplementedError: If guarded federation conversion is
            requested with ``require_pure=False``.

        Example::

            >>> from pyudbm import Context
            >>> base = Context(["x"])
            >>> pure = (base.x <= 3).to_cdd()
            >>> pure.to_federation() == (base.x <= 3)
            True
        """

        pending = self.reduce()
        dbms = []
        while not pending.is_false():
            extracted = pending.extract_bdd_and_dbm()
            if not extracted.bdd_part.is_true():
                if require_pure:
                    raise ValueError("Cannot convert a mixed bool/clock CDD to Federation.")
                raise NotImplementedError("Splitting mixed CDDs into guarded federations is not implemented.")
            dbms.append(list(extracted.dbm._raw_matrix()))
            pending = extracted.remainder

        native = _NativeFederation.from_dbm_list(dbms, self.context.dimension)
        return Federation._from_native(self.context.base_context, native)
