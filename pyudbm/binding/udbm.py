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
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from ._binding import _NativeConstraint, _NativeDBM, _NativeFederation

__all__ = [
    "DBM",
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
_DBM_INFINITY_RAW = ((2 ** 31 - 1) >> 1) << 1


def _is_exact_int(value: Any) -> bool:
    """Return whether ``value`` is a plain ``int`` and not a subclass such as ``bool``."""

    return type(value) is int


def _is_exact_int_or_float(value: Any) -> bool:
    """Return whether ``value`` is a plain ``int`` or ``float``."""

    value_type = type(value)
    return value_type is int or value_type is float


def _format_dbm_raw(raw_value: int) -> str:
    """Return one human-readable DBM cell."""

    if raw_value == _DBM_INFINITY_RAW:
        return "<inf"
    return "{0}{1}".format("<" if (raw_value & 1) == 0 else "<=", raw_value >> 1)


def _tuple_from_dbm_raw(raw_value: int) -> Tuple[str, Union[int, float]]:
    """Return one decoded DBM cell as ``(operator, bound)``."""

    if raw_value == _DBM_INFINITY_RAW:
        return "<", float("inf")
    return ("<" if (raw_value & 1) == 0 else "<=", raw_value >> 1)


class DBM:
    """
    Immutable read-only DBM snapshot.

    A :class:`DBM` represents one convex zone extracted from a federation. It
    provides DBM-level rendering, direct matrix-cell inspection, matrix export,
    and minimal-graph export while staying detached from future mutations of
    the source federation.

    In UDBM terms, this object is one closed DBM over the clocks of a single
    :class:`Context`. The first matrix row and column always correspond to the
    implicit reference clock ``0``. User clocks therefore start at matrix index
    ``1`` even though they are exposed by name at the Python level.

    :param context: Context whose clock names apply to this DBM.
    :type context: Context
    :param native: Native DBM snapshot.
    :type native: _NativeDBM
    :ivar context: Context whose clock names label the DBM matrix.

    Example::

        >>> from pyudbm import Context
        >>> context = Context(["x", "y"], name="c")
        >>> federation = (context.x <= 10) & (context.y <= 7) & (context.x - context.y < 3)
        >>> dbm = federation.to_dbm_list()[0]
        >>> dbm.dimension
        3
        >>> dbm.clock_names
        ('0', 'c.x', 'c.y')
        >>> str(dbm)
        '(c.x-c.y<3 & c.y<=7)'
    """

    def __init__(self, context: "Context", native: _NativeDBM):
        """
        Initialize one read-only DBM snapshot.

        Instances are normally created internally by
        :meth:`Federation.to_dbm_list` rather than directly by user code.

        :param context: Context whose clock names apply to this DBM.
        :type context: Context
        :param native: Native DBM snapshot.
        :type native: _NativeDBM
        :return: ``None``.
        :rtype: None
        """
        self.context = context
        self._dbm = native

    def _clock_names(self) -> List[str]:
        return ["0"] + [clock.get_full_name() for clock in self.context.clocks]

    def _raw_matrix(self) -> tuple:
        return tuple(int(value) for value in self._dbm.raw_matrix())

    def _available_index_names(self) -> List[str]:
        names = ["0"] + [clock.name for clock in self.context.clocks]
        if self.context.name:
            names.extend(clock.get_full_name() for clock in self.context.clocks)
        return names

    def _resolve_index(self, value: Union[int, str], position: str) -> int:
        if isinstance(value, int):
            if value < 0 or value >= self.dimension:
                raise IndexError(
                    "DBM {0} index {1!r} is out of range. Valid integer indices are 0 through {2}.".format(
                        position, value, self.dimension - 1
                    )
                )
            return value

        if not isinstance(value, str):
            raise TypeError(
                "DBM {0} index must be an integer or a clock name string, got {1}.".format(
                    position, type(value).__name__
                )
            )

        if value == "0":
            return 0

        short_name_to_index = {clock.name: clock.dbm_index for clock in self.context.clocks}
        if value in short_name_to_index:
            return short_name_to_index[value]

        if "." in value:
            prefix, suffix = value.split(".", 1)
            if not self.context.name:
                raise ValueError(
                    "DBM {0} index {1!r} uses a qualified clock name, but this DBM context is unnamed. "
                    "Available names: {2}.".format(position, value, ", ".join(repr(name) for name in self._available_index_names()))
                )
            if prefix != self.context.name:
                raise ValueError(
                    "DBM {0} index {1!r} uses context prefix {2!r}, but this DBM belongs to context {3!r}. "
                    "Available names: {4}.".format(
                        position, value, prefix, self.context.name, ", ".join(repr(name) for name in self._available_index_names())
                    )
                )
            if suffix in short_name_to_index:
                return short_name_to_index[suffix]
            raise ValueError(
                "DBM {0} index {1!r} uses the correct context prefix {2!r}, but {3!r} is not a clock in this context. "
                "Available names: {4}.".format(
                    position, value, self.context.name, suffix, ", ".join(repr(name) for name in self._available_index_names())
                )
            )

        raise ValueError(
            "DBM {0} index {1!r} is not a valid clock name for this context. Available names: {2}.".format(
                position, value, ", ".join(repr(name) for name in self._available_index_names())
            )
        )

    def _normalize_indices(self, i: Union[int, str], j: Union[int, str]) -> Tuple[int, int]:
        i = self._resolve_index(i, "row (i)")
        j = self._resolve_index(j, "column (j)")
        return i, j

    @property
    def dimension(self) -> int:
        """
        Return the DBM dimension including the reference clock.

        For a context with ``n`` user clocks, the DBM dimension is ``n + 1``
        because index ``0`` is reserved for the reference clock.

        :return: Matrix dimension.
        :rtype: int

        Example::

            >>> from pyudbm import Context
            >>> dbm = (Context(["x", "y"]).x <= 1).to_dbm_list()[0]
            >>> dbm.dimension
            3
        """

        return self._dbm.get_dimension()

    @property
    def shape(self) -> tuple:
        """
        Return ``(dimension, dimension)`` for the DBM matrix.

        :return: Matrix shape tuple.
        :rtype: tuple

        Example::

            >>> from pyudbm import Context
            >>> dbm = (Context(["x"]).x <= 1).to_dbm_list()[0]
            >>> dbm.shape
            (2, 2)
        """

        return self.dimension, self.dimension

    @property
    def clock_names(self) -> tuple:
        """
        Return the matrix headers including the reference clock ``0``.

        :return: Tuple of matrix row and column names.
        :rtype: tuple

        Example::

            >>> from pyudbm import Context
            >>> dbm = (Context(["x"], name="c").x <= 1).to_dbm_list()[0]
            >>> dbm.clock_names
            ('0', 'c.x')
        """

        return tuple(self._clock_names())

    def to_string(self, full: bool = False) -> str:
        """
        Return a textual representation of the DBM.

        With ``full=False`` the output uses UDBM's minimal-constraint
        rendering. With ``full=True`` all finite non-diagonal constraints of
        the closed matrix are printed explicitly.

        :param full: Whether to print all finite non-diagonal constraints
            instead of the minimal constraint set.
        :type full: bool
        :return: Human-readable DBM expression.
        :rtype: str

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"], name="c")
            >>> dbm = ((context.x <= 10) & (context.y <= 7) & (context.x - context.y < 3)).to_dbm_list()[0]
            >>> dbm.to_string()
            '(c.x-c.y<3 & c.y<=7)'
            >>> dbm.to_string(full=True)
            '(0<=c.x & 0<=c.y & c.x<10 & c.x-c.y<3 & c.y<=7 & c.y-c.x<=7)'
        """

        return self._dbm.to_string(self._clock_names(), full).replace(" && ", " & ")

    def raw(self, i: Union[int, str], j: Union[int, str]) -> int:
        """
        Return the raw UDBM matrix cell at ``(i, j)``.

        The returned integer is UDBM's encoded ``raw_t`` value. Use
        :meth:`bound`, :meth:`is_strict`, and :meth:`is_infinity` when you
        need decoded semantics.

        ``i`` and ``j`` may be either integer matrix indices or clock-name
        strings. String indices accept the reference clock ``"0"``, bare
        clock names such as ``"x"``, and context-qualified names such as
        ``"c.x"`` when this DBM belongs to the context ``c``.

        :param i: Row index or clock name.
        :type i: int or str
        :param j: Column index or clock name.
        :type j: int or str
        :return: Raw encoded DBM value.
        :rtype: int
        :raises TypeError: If either index is neither an integer nor a string.
        :raises IndexError: If an integer index is out of range.
        :raises ValueError: If a string index does not identify a clock in
            this DBM context.

        Example::

            >>> from pyudbm import Context
            >>> dbm = (Context(["x"], name="c").x <= 1).to_dbm_list()[0]
            >>> dbm.raw("c.x", "0")
            3
        """

        i, j = self._normalize_indices(i, j)
        values = self._raw_matrix()
        return values[i * self.dimension + j]

    def bound(self, i: Union[int, str], j: Union[int, str]) -> int:
        """
        Return the decoded integer bound at ``(i, j)``.

        This is the integer part of UDBM's ``raw_t`` encoding. For finite
        cells it matches the bound printed by :meth:`to_string` and
        :meth:`format_matrix`.

        :param i: Row index or clock name.
        :type i: int or str
        :param j: Column index or clock name.
        :type j: int or str
        :return: Decoded integer bound.
        :rtype: int

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"], name="c")
            >>> dbm = (context.x - context.y <= 1).to_dbm_list()[0]
            >>> dbm.bound("c.x", "y")
            1
        """

        return self.raw(i, j) >> 1

    def is_strict(self, i: Union[int, str], j: Union[int, str]) -> bool:
        """
        Return whether the DBM cell at ``(i, j)`` is strict.

        :param i: Row index or clock name.
        :type i: int or str
        :param j: Column index or clock name.
        :type j: int or str
        :return: ``True`` when the encoded inequality is strict.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"], name="c")
            >>> dbm = (context.x - context.y < 3).to_dbm_list()[0]
            >>> dbm.is_strict("x", "c.y")
            True
        """

        return (self.raw(i, j) & 1) == 0

    def is_infinity(self, i: Union[int, str], j: Union[int, str]) -> bool:
        """
        Return whether the DBM cell at ``(i, j)`` equals ``< inf``.

        :param i: Row index or clock name.
        :type i: int or str
        :param j: Column index or clock name.
        :type j: int or str
        :return: ``True`` if the matrix cell is the infinity sentinel.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> dbm = (Context(["x", "y"], name="c").x <= 1).to_dbm_list()[0]
            >>> dbm.is_infinity("c.y", "x")
            True
        """

        return self.raw(i, j) == _DBM_INFINITY_RAW

    def to_matrix(self, mode: str = "tuple") -> List[List[Union[int, str, Tuple[str, Union[int, float]]]]]:
        """
        Export the DBM matrix as a nested Python list.

        The matrix is returned in row-major order and includes the reference
        clock row and column at index ``0``.

        ``mode="tuple"`` is the default and returns decoded tuples of the
        form ``('<', 3)`` or ``('<=', 7)``; the infinity sentinel becomes
        ``('<', float('inf'))``. ``mode="raw"`` returns native encoded
        integers. ``mode="string"``
        returns presentation-oriented strings such as ``<=0`` or ``<inf``.

        :param mode: Output mode. Supported values are ``"raw"``,
            ``"string"``, and ``"tuple"``.
        :type mode: str
        :return: Nested row-major matrix.
        :rtype: List[List[Union[int, str, Tuple[str, Union[int, float]]]]]
        :raises TypeError: If ``mode`` is not a string.
        :raises ValueError: If ``mode`` is not one of the supported modes.

        Example::

            >>> from pyudbm import Context
            >>> dbm = (Context(["x"]).x <= 1).to_dbm_list()[0]
            >>> dbm.to_matrix()
            [[('<=', 0), ('<=', 0)], [('<=', 1), ('<=', 0)]]
            >>> dbm.to_matrix(mode="string")
            [['<=0', '<=0'], ['<=1', '<=0']]
        """

        if not isinstance(mode, str):
            raise TypeError("Matrix export mode must be a string.")
        if mode not in {"raw", "string", "tuple"}:
            raise ValueError("Unsupported matrix export mode: {0!r}.".format(mode))

        rows = []  # type: List[List[Union[int, str, Tuple[str, Union[int, float]]]]]
        for i in range(self.dimension):
            row = []
            for j in range(self.dimension):
                raw_value = self.raw(i, j)
                if mode == "raw":
                    cell = raw_value
                elif mode == "string":
                    cell = _format_dbm_raw(raw_value)
                else:
                    cell = _tuple_from_dbm_raw(raw_value)
                row.append(cell)
            rows.append(row)
        return rows

    def format_matrix(self) -> str:
        """
        Return a human-readable table view of the DBM matrix.

        The formatted view includes row and column headers, including the
        reference clock ``0``.

        :return: Pretty-printed matrix with row and column headers.
        :rtype: str

        Example::

            >>> from pyudbm import Context
            >>> dbm = (Context(["x"]).x <= 1).to_dbm_list()[0]
            >>> print(dbm.format_matrix())
                 0   x
              0 <=0 <=0
              x <=1 <=0
        """

        headers = [""] + list(self.clock_names)
        rows = []
        for i, row_name in enumerate(self.clock_names):
            rows.append([row_name] + [_format_dbm_raw(self.raw(i, j)) for j in range(self.dimension)])

        widths = [len(str(cell)) for cell in headers]
        for row in rows:
            for index, cell in enumerate(row):
                widths[index] = max(widths[index], len(str(cell)))

        rendered = ["  ".join(str(cell).rjust(widths[index]) for index, cell in enumerate(headers))]
        rendered.extend("  ".join(str(cell).rjust(widths[index]) for index, cell in enumerate(row)) for row in rows)
        return "\n".join(rendered)

    def to_min_dbm(self, minimize_graph: bool = True, try_constraints_16: bool = True) -> tuple:
        """
        Export the DBM as packed UDBM minimal-DBM words.

        The returned tuple is the raw packed minimal-graph representation
        produced by UDBM. It is intended for inspection, persistence, or
        interoperability rather than direct hand-editing.

        :param minimize_graph: Whether to request graph minimization.
        :type minimize_graph: bool
        :param try_constraints_16: Whether UDBM may compress finite
            constraints to 16-bit storage when possible.
        :type try_constraints_16: bool
        :return: Packed minimal-DBM words.
        :rtype: tuple

        Example::

            >>> from pyudbm import Context
            >>> dbm = (Context(["x"]).x <= 1).to_dbm_list()[0]
            >>> isinstance(dbm.to_min_dbm(), tuple)
            True
        """

        return tuple(self._dbm.to_min_dbm(minimize_graph, try_constraints_16))

    def __str__(self) -> str:
        """
        Return the default minimal textual rendering of the DBM.

        :return: Minimal DBM expression.
        :rtype: str

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"], name="c")
            >>> dbm = ((context.x <= 10) & (context.y <= 7) & (context.x - context.y < 3)).to_dbm_list()[0]
            >>> str(dbm)
            '(c.x-c.y<3 & c.y<=7)'
        """
        return self.to_string()

    def __repr__(self) -> str:
        """
        Return a debugging representation including the DBM clock names.

        :return: Debugging representation.
        :rtype: str

        Example::

            >>> from pyudbm import Context
            >>> dbm = (Context(["x"], name="c").x <= 1).to_dbm_list()[0]
            >>> repr(dbm)
            "DBM(clock_names=('0', 'c.x'))"
        """
        return "DBM(clock_names={0})".format(self.clock_names)


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
        """
        Initialize one clock object inside a context.

        The constructor is normally called by :class:`Context` while it creates
        the declared clock set. ``index`` is the user-clock position, while the
        derived :attr:`dbm_index` is shifted by one because UDBM reserves DBM
        index ``0`` for the reference clock.

        :param context: Owning context.
        :type context: Context
        :param name: User-visible clock name.
        :type name: str
        :param index: Zero-based user-clock index.
        :type index: int
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> context.x.index
            0
            >>> context.x.dbm_index
            1
        """
        self.context = context
        self.index = index
        self.name = name
        self.dbm_index = index + 1

    def __repr__(self) -> str:
        """
        Return a debugging representation of the clock.

        :return: Representation containing the fully-qualified name.
        :rtype: str

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"], name="c")
            >>> repr(context.x)
            '<Clock c.x>'
        """
        return "<Clock {0}>".format(self.get_full_name())

    def __sub__(self, other: Any) -> "VariableDifference":
        """
        Build a symbolic difference between two clocks.

        The result is a :class:`VariableDifference`, not a numeric value. Both
        clocks must belong to the same context because UDBM diagonal
        constraints are context-local.

        :param other: Right-hand clock.
        :type other: Any
        :return: Symbolic clock difference.
        :rtype: VariableDifference
        :raises ValueError: If the clocks come from different contexts.

        Example::

            >>> from pyudbm import Context, VariableDifference
            >>> context = Context(["x", "y"])
            >>> isinstance(context.x - context.y, VariableDifference)
            True
        """
        if not isinstance(other, Clock):
            return NotImplemented
        if other.context is not self.context:
            raise ValueError("Clock subtraction requires clocks from the same context.")
        return VariableDifference([self, other])

    def __le__(self, bound: Any) -> Any:
        """
        Build the non-strict upper-bound constraint ``clock <= bound``.

        :param bound: Integer upper bound.
        :type bound: Any
        :return: Federation representing the constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> str(context.x <= 2)
            '(x<=2)'
        """
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self, None, bound, False))

    def __ge__(self, bound: Any) -> Any:
        """
        Build the non-strict lower-bound constraint ``clock >= bound``.

        :param bound: Integer lower bound.
        :type bound: Any
        :return: Federation representing the constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> str(context.x >= 2)
            '(2<=x)'
        """
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(None, self, -bound, False))

    def __lt__(self, bound: Any) -> Any:
        """
        Build the strict upper-bound constraint ``clock < bound``.

        :param bound: Integer upper bound.
        :type bound: Any
        :return: Federation representing the strict constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> str(context.x < 2)
            '(x<2)'
        """
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self, None, bound, True))

    def __gt__(self, bound: Any) -> Any:
        """
        Build the strict lower-bound constraint ``clock > bound``.

        :param bound: Integer lower bound.
        :type bound: Any
        :return: Federation representing the strict constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> str(context.x > 2)
            '(2<x)'
        """
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(None, self, -bound, True))

    def __eq__(self, bound: Any) -> Any:
        """
        Build equality to a constant, or compare clock identity otherwise.

        With an integer operand this returns the zone ``clock == bound``. With
        any non-integer operand it falls back to normal Python object identity.

        :param bound: Integer bound or arbitrary object.
        :type bound: Any
        :return: Constraint federation or boolean identity result.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> str(context.x == 2)
            '(x==2)'
            >>> context.x == context["x"]
            True
        """
        if _is_exact_int(bound):
            return Federation(Constraint(self, None, bound, False)) & Federation(Constraint(None, self, -bound, False))
        return self is bound

    def __ne__(self, bound: Any) -> Any:
        """
        Build disequality to a constant, or compare identity otherwise.

        With an integer operand the result is the union ``clock < bound`` or
        ``clock > bound``. With non-integer operands this is the negation of
        :meth:`__eq__`.

        :param bound: Integer bound or arbitrary object.
        :type bound: Any
        :return: Constraint federation or boolean identity result.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> str(context.x != 2)
            '(2<x) | (x<2)'
            >>> context.x != context["x"]
            False
        """
        if _is_exact_int(bound):
            return Federation(Constraint(self, None, bound, True)) | Federation(Constraint(None, self, -bound, True))
        return not self.__eq__(bound)

    def __hash__(self) -> int:
        """
        Return the hash derived from the fully-qualified clock name.

        :return: Hash value.
        :rtype: int

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"], name="c")
            >>> hash(context.x) == hash(context.x.get_full_name())
            True
        """
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
        """
        Initialize an empty valuation for one context.

        :param context: Owning context.
        :type context: Context
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context, Valuation
            >>> valuation = Valuation(Context(["x"]))
            >>> len(valuation)
            0
        """
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
        """
        Store a value using either a clock name or a :class:`Clock` key.

        :param key: Clock name or clock object.
        :type key: str or Clock
        :param value: Concrete clock value.
        :type value: Any
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context, Valuation
            >>> context = Context(["x", "y"])
            >>> valuation = Valuation(context)
            >>> valuation["x"] = 1
            >>> valuation[context.y] = 2
            >>> valuation[context.x], valuation[context.y]
            (1, 2)
        """
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
        """
        Store one integer-valued clock assignment.

        :param key: Clock name or clock object.
        :type key: str or Clock
        :param value: Integer value to assign.
        :type value: Any
        :return: ``None``.
        :rtype: None
        :raises TypeError: If ``value`` is not a plain integer.

        Example::

            >>> from pyudbm import Context, IntValuation
            >>> valuation = IntValuation(Context(["x"]))
            >>> valuation["x"] = 3
            >>> valuation[valuation.context.x]
            3
        """
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
        """
        Store one real-valued clock assignment.

        :param key: Clock name or clock object.
        :type key: str or Clock
        :param value: Integer or floating-point value.
        :type value: Any
        :return: ``None``.
        :rtype: None
        :raises TypeError: If ``value`` is neither ``int`` nor ``float``.

        Example::

            >>> from pyudbm import Context, FloatValuation
            >>> valuation = FloatValuation(Context(["x"]))
            >>> valuation["x"] = 1.5
            >>> valuation[valuation.context.x]
            1.5
        """
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
        >>> str(diagonal == 1)
        '(1<=x & x-y==1)'
        >>> (diagonal == 1) == ((context.x - context.y) == 1)
        True
    """

    def __init__(self, variables: List[Clock]):
        """
        Initialize a symbolic difference ``left - right``.

        :param variables: Exactly two clocks from the same context.
        :type variables: List[Clock]
        :return: ``None``.
        :rtype: None
        :raises ValueError: If the input does not contain exactly two
            compatible clocks.

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> difference = context.x - context.y
            >>> [clock.name for clock in difference.vars]
            ['x', 'y']
        """
        if len(variables) != 2:
            raise ValueError("VariableDifference requires exactly two clocks.")
        if variables[0].context is not variables[1].context:
            raise ValueError("VariableDifference requires clocks from the same context.")

        self.vars = variables
        self.context = variables[0].context

    def __le__(self, bound: Any) -> Any:
        """
        Build the diagonal constraint ``left - right <= bound``.

        :param bound: Integer upper bound.
        :type bound: Any
        :return: Federation representing the diagonal constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> str(context.x - context.y <= 2)
            '(x-y<=2)'
        """
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self.vars[0], self.vars[1], bound, False))

    def __ge__(self, bound: Any) -> Any:
        """
        Build the diagonal constraint ``left - right >= bound``.

        :param bound: Integer lower bound.
        :type bound: Any
        :return: Federation representing the diagonal constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> str(context.x - context.y >= 2)
            '(y-x<=-2)'
        """
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self.vars[1], self.vars[0], -bound, False))

    def __lt__(self, bound: Any) -> Any:
        """
        Build the strict diagonal constraint ``left - right < bound``.

        :param bound: Integer upper bound.
        :type bound: Any
        :return: Federation representing the diagonal constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> str(context.x - context.y < 2)
            '(x-y<2)'
        """
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self.vars[0], self.vars[1], bound, True))

    def __gt__(self, bound: Any) -> Any:
        """
        Build the strict diagonal constraint ``left - right > bound``.

        :param bound: Integer lower bound.
        :type bound: Any
        :return: Federation representing the diagonal constraint.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> str(context.x - context.y > 2)
            '(y-x<-2)'
        """
        if not _is_exact_int(bound):
            return NotImplemented
        return Federation(Constraint(self.vars[1], self.vars[0], -bound, True))

    def __eq__(self, bound: Any) -> Any:
        """
        Build the equality zone ``left - right == bound``.

        :param bound: Integer difference value.
        :type bound: Any
        :return: Federation representing the equality, or ``False`` for
            non-integer operands.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> str(context.x - context.y == 2)
            '(2<=x & x-y==2)'
        """
        if not _is_exact_int(bound):
            return False
        return Federation(Constraint(self.vars[0], self.vars[1], bound, False)) & Federation(
            Constraint(self.vars[1], self.vars[0], -bound, False)
        )

    def __ne__(self, bound: Any) -> Any:
        """
        Build the disequality zone ``left - right != bound``.

        :param bound: Integer difference value.
        :type bound: Any
        :return: Federation representing the disequality, or ``True`` for
            non-integer operands.
        :rtype: Any

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> str(context.x - context.y != 2)
            '(y-x<-2) | (x-y<2)'
        """
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
        """
        Initialize one symbolic DBM constraint wrapper.

        :param arg1: Left clock operand, or ``None`` for the reference clock.
        :type arg1: Clock or None
        :param arg2: Right clock operand, or ``None`` for the reference clock.
        :type arg2: Clock or None
        :param val: Integer bound.
        :type val: int
        :param is_strict: Whether the bound is strict.
        :type is_strict: bool
        :return: ``None``.
        :rtype: None
        :raises TypeError: If operands or the bound have invalid types.
        :raises ValueError: If no operand is given or the clocks belong to
            different contexts.

        Example::

            >>> from pyudbm import Constraint, Context
            >>> context = Context(["x", "y"])
            >>> constraint = Constraint(context.x, context.y, 3, False)
            >>> constraint.context is context
            True
        """
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
        """
        Initialize a federation from a context or one constraint.

        Passing a :class:`Context` creates that context's zero federation.
        Passing a :class:`Constraint` creates a one-DBM federation containing
        the corresponding symbolic zone.

        :param arg: Context or constraint source.
        :type arg: Context or Constraint
        :return: ``None``.
        :rtype: None
        :raises TypeError: If ``arg`` is neither a context nor a constraint.

        Example::

            >>> from pyudbm import Constraint, Context, Federation
            >>> context = Context(["x"])
            >>> Federation(context).is_zero()
            True
            >>> Federation(Constraint(context.x, None, 2, False)) == (context.x <= 2)
            True
        """
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
        """
        Return UDBM-style textual rendering of the federation.

        :return: Human-readable symbolic zone expression.
        :rtype: str

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> str(context.x < 2)
            '(x<2)'
        """
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

    def to_dbm_list(self) -> List[DBM]:
        """
        Export the federation as a list of read-only DBM snapshots.

        Each returned :class:`DBM` is a detached snapshot of one native DBM in
        the federation. This is important because federations are mutable while
        DBM snapshots returned here are intentionally read-only.

        :return: List of DBMs in native federation order.
        :rtype: List[DBM]

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"], name="c")
            >>> dbms = ((context.x <= 1) | (context.x >= 3)).to_dbm_list()
            >>> len(dbms)
            2
            >>> [str(dbm) for dbm in dbms]
            ['(c.x<=1)', '(3<=c.x)']
        """

        return [DBM(self.context, native) for native in self._fed.to_dbm_list()]

    def __and__(self, other: "Federation") -> "Federation":
        """
        Return the exact intersection of two federations.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: Intersection result.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> left = context.x >= 1
            >>> right = context.x <= 3
            >>> (left & right) == ((context.x >= 1) & (context.x <= 3))
            True
        """
        self._require_compatible(other)
        return Federation._from_native(self.context, self._fed.and_op(other._fed))

    def __iand__(self, other: "Federation") -> "Federation":
        """
        Intersect this federation with another one in place.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: ``self`` after intersection.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> zone = context.x >= 1
            >>> zone &= (context.x <= 3)
            >>> zone == ((context.x >= 1) & (context.x <= 3))
            True
        """
        self._require_compatible(other)
        self._fed.iand(other._fed)
        return self

    def __or__(self, other: "Federation") -> "Federation":
        """
        Return the set-theoretic union of two federations.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: Union result.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> union = (context.x == 0) | (context.x == 1)
            >>> union.get_size()
            2
        """
        self._require_compatible(other)
        return Federation._from_native(self.context, self._fed.or_op(other._fed))

    def __ior__(self, other: "Federation") -> "Federation":
        """
        Union this federation with another one in place.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: ``self`` after union.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> zone = context.x == 0
            >>> zone |= (context.x == 1)
            >>> zone.get_size()
            2
        """
        self._require_compatible(other)
        self._fed.ior(other._fed)
        return self

    def __add__(self, other: "Federation") -> "Federation":
        """
        Return the convex union of two federations.

        Unlike :meth:`__or__`, this computes UDBM's convex-hull style addition
        and may introduce new valuations between the operands.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: Convex union result.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> hull = (context.x == 0) + (context.x == 2)
            >>> hull == ((context.x >= 0) & (context.x <= 2))
            True
        """
        self._require_compatible(other)
        return Federation._from_native(self.context, self._fed.add_op(other._fed))

    def __iadd__(self, other: "Federation") -> "Federation":
        """
        Replace this federation by its convex union with another one.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: ``self`` after convex union.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> zone = context.x == 0
            >>> zone += (context.x == 2)
            >>> zone == ((context.x >= 0) & (context.x <= 2))
            True
        """
        self._require_compatible(other)
        self._fed.iadd(other._fed)
        return self

    def __sub__(self, other: "Federation") -> "Federation":
        """
        Return the set difference ``self \\ other``.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: Difference result.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context, IntValuation
            >>> context = Context(["x"])
            >>> zone = ((context.x >= 0) & (context.x <= 2)) - (context.x == 1)
            >>> kept = IntValuation(context)
            >>> kept["x"] = 0
            >>> removed = IntValuation(context)
            >>> removed["x"] = 1
            >>> zone.contains(kept), zone.contains(removed)
            (True, False)
        """
        self._require_compatible(other)
        return Federation._from_native(self.context, self._fed.minus_op(other._fed))

    def __isub__(self, other: "Federation") -> "Federation":
        """
        Subtract another federation from this one in place.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: ``self`` after subtraction.
        :rtype: Federation

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> zone = (context.x >= 0) & (context.x <= 2)
            >>> zone -= (context.x == 1)
            >>> zone == (((context.x >= 0) & (context.x < 1)) | ((context.x > 1) & (context.x <= 2)))
            True
        """
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
        """
        Return whether two federations denote the same symbolic set.

        :param other: Object to compare with.
        :type other: Any
        :return: ``True`` if both federations are equal.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> (context.x == 1) == ((context.x <= 1) & (context.x >= 1))
            True
        """
        if not isinstance(other, Federation):
            return False
        self._require_compatible(other)
        return self._fed.eq(other._fed)

    def __ne__(self, other: Any) -> bool:
        """
        Return whether two federations denote different symbolic sets.

        :param other: Object to compare with.
        :type other: Any
        :return: ``True`` if the federations differ.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> (context.x == 1) != (context.x == 2)
            True
        """
        return not self == other

    def __le__(self, other: "Federation") -> bool:
        """
        Return whether ``self`` is a subset of ``other``.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: ``True`` if inclusion holds.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> (context.x == 1) <= (context.x <= 1)
            True
        """
        self._require_compatible(other)
        return self._fed.le(other._fed)

    def __ge__(self, other: "Federation") -> bool:
        """
        Return whether ``self`` is a superset of ``other``.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: ``True`` if reverse inclusion holds.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> (context.x <= 1) >= (context.x == 1)
            True
        """
        self._require_compatible(other)
        return self._fed.ge(other._fed)

    def __lt__(self, other: "Federation") -> bool:
        """
        Return whether ``self`` is a strict subset of ``other``.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: ``True`` if strict inclusion holds.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> (context.x == 1) < (context.x <= 1)
            True
        """
        self._require_compatible(other)
        return self._fed.lt(other._fed)

    def __gt__(self, other: "Federation") -> bool:
        """
        Return whether ``self`` is a strict superset of ``other``.

        :param other: Other federation in the same context.
        :type other: Federation
        :return: ``True`` if strict reverse inclusion holds.
        :rtype: bool

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x"])
            >>> (context.x <= 1) > (context.x == 1)
            True
        """
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
        """
        Return the native order-insensitive federation hash.

        :return: Hash value.
        :rtype: int

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> left = (context.x == 1) | (context.y == 1)
            >>> right = (context.y == 1) | (context.x == 1)
            >>> hash(left) == hash(right)
            True
        """
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
        """
        Initialize a context and create all declared clocks.

        :param clock_names: Names of clocks to create.
        :type clock_names: Iterable[str]
        :param name: Optional display prefix.
        :type name: str or None
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"], name="c")
            >>> [clock.name for clock in context.clocks]
            ['x', 'y']
            >>> context.name
            'c'
        """
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
        """
        Return one clock by its declared name.

        :param arg: Clock name.
        :type arg: str
        :return: Matching clock object.
        :rtype: Clock
        :raises KeyError: If no unique clock with that name exists.

        Example::

            >>> from pyudbm import Context
            >>> context = Context(["x", "y"])
            >>> context["x"] is context.x
            True
        """
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
