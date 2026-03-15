"""
Legacy-style high-level UDBM API.

This module restores the historical Python DSL built around
:class:`Context`, :class:`Clock`, and :class:`Federation`, while using the
modern pybind11 binding layer underneath.

Example::

    >>> from pyudbm import Context
    >>> c = Context(["x", "y"], name="c")
    >>> zone = (c.x < 10) & (c.x - c.y > 1)
    >>> other = (c.x < 20)
    >>> zone <= other
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


class Clock:
    """
    Symbolic clock inside a :class:`Context`.

    Clock instances drive the high-level DSL by overloading arithmetic and
    comparison operators to build :class:`Federation` objects instead of plain
    booleans.

    :param context: Owning clock context.
    :type context: Context
    :param name: Clock name inside the context.
    :type name: str
    :param index: Zero-based clock index inside the context.
    :type index: int
    """

    def __init__(self, context: "Context", name: str, index: int):
        self.context = context
        self.index = index
        self.name = name
        self.dbm_index = index + 1

    def __repr__(self) -> str:
        return "<Clock {0}>".format(self.getFullName())

    def __sub__(self, other: Any) -> "VariableDifference":
        if not isinstance(other, Clock):
            return NotImplemented
        if other.context is not self.context:
            raise ValueError("Clock subtraction requires clocks from the same context.")
        return VariableDifference([self, other])

    def __le__(self, bound: Any) -> Any:
        if not isinstance(bound, int):
            return NotImplemented
        return Federation(Constraint(self, None, bound, False))

    def __ge__(self, bound: Any) -> Any:
        if not isinstance(bound, int):
            return NotImplemented
        return Federation(Constraint(None, self, -bound, False))

    def __lt__(self, bound: Any) -> Any:
        if not isinstance(bound, int):
            return NotImplemented
        return Federation(Constraint(self, None, bound, True))

    def __gt__(self, bound: Any) -> Any:
        if not isinstance(bound, int):
            return NotImplemented
        return Federation(Constraint(None, self, -bound, True))

    def __eq__(self, bound: Any) -> Any:
        if isinstance(bound, int):
            return Federation(Constraint(self, None, bound, False)) & Federation(Constraint(None, self, -bound, False))
        return self is bound

    def __ne__(self, bound: Any) -> Any:
        if isinstance(bound, int):
            return Federation(Constraint(self, None, bound, True)) | Federation(Constraint(None, self, -bound, True))
        return not self.__eq__(bound)

    def __hash__(self) -> int:
        return hash(self.getFullName())

    def getFullName(self) -> str:
        """
        Return the fully-qualified clock name.

        :return: Context-qualified clock name when a context name is present.
        :rtype: str
        """

        if self.context.name:
            return "{0}.{1}".format(self.context.name, self.name)
        return self.name


class Valuation(dict):
    """
    Clock valuation base class.

    Values are stored by :class:`Clock` instance, but assignment by clock name
    is also accepted for convenience.

    :param context: Owning clock context.
    :type context: Context
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

        Missing clocks are logged for compatibility with the historical
        implementation.

        :return: ``None``.
        :rtype: None
        """

        for clock in self.context.clocks:
            if clock not in self:
                LOGGER.error("Clock %s is not present in the clock valuation.", clock.name)


class IntValuation(Valuation):
    """
    Integer clock valuation.

    :param context: Owning clock context.
    :type context: Context
    """

    def __setitem__(self, key: Union[str, Clock], value: Any) -> None:
        if not isinstance(value, int):
            raise TypeError("Integer valuations require integer values.")
        super().__setitem__(key, value)


class FloatValuation(Valuation):
    """
    Floating-point clock valuation.

    :param context: Owning clock context.
    :type context: Context
    """

    def __setitem__(self, key: Union[str, Clock], value: Any) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Float valuations require int or float values.")
        super().__setitem__(key, value)


class VariableDifference:
    """
    Symbolic difference between two clocks.

    :param variables: Two clocks from the same context.
    :type variables: list[Clock]
    """

    def __init__(self, variables: List[Clock]):
        if len(variables) != 2:
            raise ValueError("VariableDifference requires exactly two clocks.")
        if variables[0].context is not variables[1].context:
            raise ValueError("VariableDifference requires clocks from the same context.")

        self.vars = variables
        self.context = variables[0].context

    def __le__(self, bound: Any) -> Any:
        if not isinstance(bound, int):
            return NotImplemented
        return Federation(Constraint(self.vars[0], self.vars[1], bound, False))

    def __ge__(self, bound: Any) -> Any:
        if not isinstance(bound, int):
            return NotImplemented
        return Federation(Constraint(self.vars[1], self.vars[0], -bound, False))

    def __lt__(self, bound: Any) -> Any:
        if not isinstance(bound, int):
            return NotImplemented
        return Federation(Constraint(self.vars[0], self.vars[1], bound, True))

    def __gt__(self, bound: Any) -> Any:
        if not isinstance(bound, int):
            return NotImplemented
        return Federation(Constraint(self.vars[1], self.vars[0], -bound, True))

    def __eq__(self, bound: Any) -> Any:
        if not isinstance(bound, int):
            return False
        return Federation(Constraint(self.vars[0], self.vars[1], bound, False)) & Federation(
            Constraint(self.vars[1], self.vars[0], -bound, False)
        )

    def __ne__(self, bound: Any) -> Any:
        if not isinstance(bound, int):
            return True
        return Federation(Constraint(self.vars[0], self.vars[1], bound, True)) | Federation(
            Constraint(self.vars[1], self.vars[0], -bound, True)
        )


class Constraint:
    """
    Internal symbolic constraint wrapper.

    :param arg1: Left clock operand, or ``None`` for the reference clock.
    :type arg1: Clock or None
    :param arg2: Right clock operand, or ``None`` for the reference clock.
    :type arg2: Clock or None
    :param val: Integer bound.
    :type val: int
    :param isStrict: Whether the bound is strict.
    :type isStrict: bool
    """

    def __init__(self, arg1: Optional[Clock], arg2: Optional[Clock], val: int, isStrict: bool):
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
        self._constraint = _NativeConstraint(i, j, val, isStrict)


class Federation:
    """
    Union of DBMs within a single :class:`Context`.

    The constructor mirrors the historical binding: creating from a
    :class:`Context` yields the zero federation, while creating from a
    :class:`Constraint` yields the initial federation constrained by that
    symbolic expression.

    :param arg: Context or symbolic constraint source.
    :type arg: Context or Constraint
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
        return ["0"] + [clock.getFullName() for clock in self.context.clocks]

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

        :return: A copy sharing the same context.
        :rtype: Federation
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
        ret = self.copy()
        ret._fed.up()
        return ret

    def down(self) -> "Federation":
        ret = self.copy()
        ret._fed.down()
        return ret

    def reduce(self, level: int = 0) -> "Federation":
        """
        Merge-reduce the federation in place.

        :param level: Historical expensive-try level passed to UDBM.
        :type level: int
        :return: ``self``.
        :rtype: Federation
        """

        self._fed.merge_reduce(0, level)
        return self

    def freeClock(self, clock: Clock) -> "Federation":
        ret = self.copy()
        ret._fed.free_clock(clock.dbm_index)
        return ret

    def setZero(self) -> "Federation":
        self._fed.set_zero()
        return self

    def hasZero(self) -> bool:
        return self._fed.has_zero()

    def setInit(self) -> "Federation":
        self._fed.set_init()
        return self

    def convexHull(self) -> "Federation":
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
        self._fed.intern()

    def predt(self, other: "Federation") -> "Federation":
        self._require_compatible(other)
        ret = self.copy()
        ret._fed.predt(other._fed)
        return ret

    def contains(self, valuation: Valuation) -> bool:
        valuation.check()
        values = self._valuation_vector(valuation)
        if isinstance(valuation, IntValuation):
            return self._fed.contains_int(values)
        if isinstance(valuation, FloatValuation):
            return self._fed.contains_float(values)
        raise TypeError("Unknown valuation type.")

    def updateValue(self, clock: Clock, value: int) -> "Federation":
        if clock.context is not self.context:
            raise ValueError("Clock update requires the same context.")
        ret = self.copy()
        ret._fed.update_value(clock.dbm_index, value)
        return ret

    def resetValue(self, clock: Clock) -> "Federation":
        return self.updateValue(clock, 0)

    def getSize(self) -> int:
        return self._fed.size()

    def extrapolateMaxBounds(self, bounds: Mapping[Clock, int]) -> "Federation":
        if len(bounds) != len(self.context.clocks):
            LOGGER.error("extrapolateMaxBounds called without bounds for every clock.")

        ret = self.copy()
        vector = [0] * (len(self.context.clocks) + 1)
        for key, value in bounds.items():
            if isinstance(key, str):
                clock = self.context[key]
            elif isinstance(key, Clock):
                clock = key
            else:
                raise TypeError("Bounds keys must be clock names or Clock objects.")

            if clock.context is not self.context:
                raise ValueError("Bounds clocks must belong to the same context.")
            vector[clock.dbm_index] = int(value)

        ret._fed.extrapolate_max_bounds(vector)
        return ret

    def isZero(self) -> bool:
        return self == self.context.getZeroFederation()

    def isEmpty(self) -> bool:
        return self._fed.is_empty()

    def __hash__(self) -> int:
        return self._fed.hash()

    def hash(self) -> int:
        return hash(self)


class Context:
    """
    Named clock context.

    :param clock_names: Clock names to create.
    :type clock_names: iterable[str]
    :param name: Optional context prefix used in string rendering.
    :type name: str or None
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

    def setName(self, name: Optional[str]) -> None:
        """
        Set the context display name.

        :param name: New context name.
        :type name: str or None
        :return: ``None``.
        :rtype: None
        """

        self.name = name

    def __getitem__(self, arg: str) -> Clock:
        names = [clock for clock in self.clocks if clock.name == arg]
        if not names:
            raise KeyError(arg)
        if len(names) != 1:
            raise KeyError("Ambiguous clock name: {0}".format(arg))
        return names[0]

    def getZeroFederation(self) -> Federation:
        """
        Return the zero federation for this context.

        :return: Zero federation.
        :rtype: Federation
        """

        return Federation(self)
