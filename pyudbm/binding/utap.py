"""
High-level read-only UTAP API.

This module layers immutable Python snapshot objects on top of the native
``pyudbm.binding._utap`` bindings. It is the public high-level inspection
layer for parsed UPPAAL models and queries.

The surface is intentionally read-only in this phase:

* model parsing returns a :class:`ModelDocument`;
* nested model objects are frozen dataclass snapshots;
* query parsing returns immutable :class:`ParsedQuery` values;
* the owning :class:`ModelDocument` retains the native document for XML
  round-tripping helpers.

Compared with :mod:`pyudbm.binding._utap`, this module focuses on a stable
Python-facing object model for templates, processes, locations, edges,
queries, diagnostics, and selected document-level declarations.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Tuple
from xml.sax.saxutils import escape, quoteattr

from ._utap import (
    _NativeDocument,
    builtin_declarations as _builtin_declarations,
    load_query as _load_query,
    load_xml as _load_xml,
    load_xta as _load_xta,
    loads_query as _loads_query,
    loads_xml as _loads_xml,
    loads_xta as _loads_xta,
    textual_builtin_preamble as _textual_builtin_preamble,
    _xml_to_text as _xml_to_text,
    parse_query as _parse_query,
)

__all__ = [
    "Branchpoint",
    "Diagnostic",
    "Edge",
    "Expectation",
    "Expression",
    "FeatureFlags",
    "Location",
    "MAPPED_FIELDS",
    "MAPPED_FIELD_NOTES",
    "ModelDocument",
    "Option",
    "ParsedQuery",
    "ParsedQueryExpectation",
    "Position",
    "Process",
    "Query",
    "Resource",
    "Symbol",
    "Template",
    "TypeInfo",
    "UNMAPPED_FIELDS",
    "UNMAPPED_FIELD_REASONS",
    "builtin_declarations",
    "load_query",
    "load_xml",
    "load_xta",
    "loads_query",
    "loads_xml",
    "loads_xta",
    "parse_query",
    "textual_builtin_preamble",
]


#: Public snapshot fields currently exposed for each native UTAP payload type.
#:
#: This mapping documents the first-phase Python-facing surface that
#: :class:`ModelDocument` and related value objects guarantee to populate.
MAPPED_FIELDS = {
    "Document": ("templates", "processes", "queries", "options", "features", "errors", "warnings", "modified"),
    "Template": (
        "name",
        "index",
        "position",
        "parameter",
        "declaration",
        "init_name",
        "type",
        "mode",
        "is_ta",
        "is_instantiated",
        "dynamic",
        "is_defined",
        "locations",
        "branchpoints",
        "edges",
    ),
    "Process": (
        "name",
        "index",
        "position",
        "template_name",
        "parameters",
        "arguments",
        "mapping",
        "argument_count",
        "unbound_count",
        "restricted_symbols",
    ),
    "Branchpoint": ("name", "index", "position", "symbol"),
    "Location": (
        "name",
        "index",
        "position",
        "symbol",
        "name_expression",
        "invariant",
        "exp_rate",
        "cost_rate",
        "is_urgent",
        "is_committed",
    ),
    "Edge": (
        "index",
        "control",
        "action_name",
        "source_name",
        "source_kind",
        "target_name",
        "target_kind",
        "guard",
        "assign",
        "sync",
        "prob",
        "select_text",
        "select_symbols",
        "select_values",
    ),
    "Query": ("formula", "comment", "options", "expectation", "location"),
    "Option": ("name", "value"),
    "FeatureFlags": (
        "has_priority_declaration",
        "has_strict_invariants",
        "has_stop_watch",
        "has_strict_lower_bound_on_controllable_edges",
        "has_clock_guard_recv_broadcast",
        "has_urgent_transition",
        "has_dynamic_templates",
        "all_broadcast",
        "sync_used",
        "supports_symbolic",
        "supports_stochastic",
        "supports_concrete",
    ),
    "expectation_t": ("result_kind", "status", "value", "time_ms", "mem_kib"),
    "ParsedQuery": (
        "line",
        "no",
        "builder",
        "text",
        "quantifier",
        "options",
        "expression",
        "is_smc",
        "declaration",
        "result_type",
        "expectation",
    ),
    "expression_t": ("text", "kind", "position", "type", "size", "children", "is_empty"),
    "type_t": (
        "kind",
        "position",
        "size",
        "text",
        "declaration",
        "is_unknown",
        "is_range",
        "is_integer",
        "is_boolean",
        "is_function",
        "is_function_external",
        "is_clock",
        "is_process",
        "is_process_set",
        "is_location",
        "is_location_expr",
        "is_instance_line",
        "is_branchpoint",
        "is_channel",
        "is_record",
        "is_array",
        "is_scalar",
        "is_diff",
        "is_void",
        "is_cost",
        "is_integral",
        "is_invariant",
        "is_probability",
        "is_guard",
        "is_constraint",
        "is_formula",
        "is_double",
        "is_string",
    ),
    "symbol_t": ("name", "type", "position"),
    "position_t": ("start", "end", "line", "column", "end_line", "end_column", "path"),
    "diagnostic_t": ("message", "context", "position", "line", "column", "end_line", "end_column", "path"),
}

#: Additional compatibility notes for selected mapped fields.
#:
#: These notes explain conservative wrappers and intentionally restricted
#: representations where the Python layer avoids exposing unstable native
#: pretty-printer or parser internals directly.
MAPPED_FIELD_NOTES = {
    "Template": {
        "declaration": "Conservative first-phase field. The current binding keeps this empty instead of calling unstable upstream pretty-printers on every template.",
    },
    "type_t": {
        "text": "Safe pretty-printer wrapper. Returns a stable fallback when upstream stringification throws.",
        "declaration": "Safe declaration wrapper. Returns a stable fallback when upstream pretty-printers throw.",
    },
    "expression_t": {
        "text": "Safe pretty-printer wrapper. Some upstream expressions still fall back to synthesized text when direct stringification is unstable.",
    },
}

#: Native UTAP fields that are currently not promoted to the public snapshot
#: layer.
UNMAPPED_FIELDS = {
    "Document": ("globals", "before_update", "after_update", "chan_priorities", "strings"),
    "Template": ("messages", "updates", "conditions", "dynamic_evals"),
    "Process": ("restricted",),
    "Branchpoint": (),
    "Location": (),
    "Edge": (),
    "Query": ("results",),
    "Option": (),
    "FeatureFlags": (),
    "expectation_t": (),
    "ParsedQuery": ("subjections", "imitation"),
    "expression_t": ("value", "double_value", "sync", "record_label_index", "string_value", "symbol"),
    "type_t": ("children", "range", "labels"),
    "symbol_t": ("frame", "user_data"),
    "position_t": (),
    "diagnostic_t": (),
}

#: Explanations for why entries in :data:`UNMAPPED_FIELDS` are not yet exposed
#: directly in the high-level Python API.
UNMAPPED_FIELD_REASONS = {
    "Document": {
        "globals": "Exposed via the global_declarations property instead of re-exporting raw declarations_t as a first-phase value object.",
        "before_update": "Exposed via the before_update_text property instead of re-exporting raw expression_t on the first-phase document snapshot.",
        "after_update": "Exposed via the after_update_text property instead of re-exporting raw expression_t on the first-phase document snapshot.",
        "chan_priorities": "Exposed via the channel_priority_texts property instead of re-exporting raw chan_priority_t objects.",
        "strings": "Internal interned-string table is not a stable user-facing semantic object.",
    },
    "Template": {
        "messages": "LSC-specific structures need dedicated wrappers instead of string summaries.",
        "updates": "LSC-specific structures need dedicated wrappers instead of string summaries.",
        "conditions": "LSC-specific structures need dedicated wrappers instead of string summaries.",
        "dynamic_evals": "Deferred until dynamic-template introspection gets a stable public shape.",
    },
    "Process": {
        "restricted": "The raw restricted-variable set is exposed indirectly via restricted_symbols; the original native container itself is not re-exported.",
    },
    "Query": {
        "results": "Upstream query_t does not currently preserve structured result entries in the live document object.",
    },
    "ParsedQuery": {
        "subjections": "Not yet promoted to a stable first-phase Python value object.",
        "imitation": "Not yet promoted to a stable first-phase Python value object.",
    },
    "expression_t": {
        "value": "Literal-value extraction needs a typed Python value layer instead of ad hoc unions.",
        "double_value": "Literal-value extraction needs a typed Python value layer instead of ad hoc unions.",
        "sync": "Sync-kind internals are better exposed together with higher-level synchronization helpers.",
        "record_label_index": "Record-label internals need a dedicated typed accessor instead of leaking parser internals.",
        "string_value": "Literal-value extraction needs a typed Python value layer instead of ad hoc unions.",
        "symbol": "Expression-bound symbol references need a dedicated stable wrapper contract.",
    },
    "type_t": {
        "children": "Deferred until recursive type-shape wrappers are stabilized for records, arrays, and process fields.",
        "range": "Deferred until recursive type-shape wrappers are stabilized for ranged and dependent types.",
        "labels": "Deferred until recursive type-shape wrappers are stabilized for record/process field labels.",
    },
    "symbol_t": {
        "frame": "Raw frame_t is an implementation-level scope object without a stable first-phase Python API.",
        "user_data": "Raw user_data pointers are native implementation details and not a safe Python-facing field.",
    },
}

_EXPECTATION_STATUS_TO_XML = {
    "True": "success",
    "False": "failure",
    "MaybeTrue": "maybe_true",
    "MaybeFalse": "maybe_false",
}

_EXPECTATION_TYPE_TO_XML = {
    "Probability": "probability",
    "Symbolic": "symbolic",
    "NumericValue": "value",
}


@dataclass(frozen=True)
class Position:
    """
    Source span of one parsed UTAP object.

    Positions are immutable snapshots produced from UTAP source metadata.
    Line, column, and path information may be absent for synthesized nodes
    that do not correspond to a concrete file-backed location.

    :param start: Start offset in the normalized source buffer.
    :type start: int
    :param end: End offset in the normalized source buffer.
    :type end: int
    :param line: One-based starting line number, if available.
    :type line: int or None
    :param column: One-based starting column number, if available.
    :type column: int or None
    :param end_line: One-based ending line number, if available.
    :type end_line: int or None
    :param end_column: One-based ending column number, if available.
    :type end_column: int or None
    :param path: Source path associated with the position, if available.
    :type path: str or None

    Example::

        >>> from pyudbm.binding.utap import Position
        >>> position = Position(0, 4, 1, 1, 1, 5, "model.xta")
        >>> position.line
        1
    """

    start: int
    end: int
    line: Optional[int]
    column: Optional[int]
    end_line: Optional[int]
    end_column: Optional[int]
    path: Optional[str]


@dataclass(frozen=True)
class Option:
    """
    One XML or query option expressed as a key/value pair.

    :param name: Option name.
    :type name: str
    :param value: Option value as text.
    :type value: str

    Example::

        >>> from pyudbm.binding.utap import Option
        >>> Option("trace", "short").name
        'trace'
    """

    name: str
    value: str


@dataclass(frozen=True)
class Resource:
    """
    One resource measurement attached to a query expectation.

    :param name: Resource kind, for example time or memory.
    :type name: str
    :param value: Resource value as text.
    :type value: str
    :param unit: Optional unit associated with the value.
    :type unit: str or None

    Example::

        >>> from pyudbm.binding.utap import Resource
        >>> Resource("time", "100", "ms").unit
        'ms'
    """

    name: str
    value: str
    unit: Optional[str]


@dataclass(frozen=True)
class Expectation:
    """
    Expected verification outcome stored with a model query.

    ``value_type`` and ``status`` mirror UTAP's expectation metadata, while
    ``resources`` stores optional time or memory budgets.

    :param value_type: Expectation category such as ``"Symbolic"`` or
        ``"Probability"``.
    :type value_type: str
    :param status: Expected outcome status.
    :type status: str
    :param value: Expected scalar value rendered as text, when present.
    :type value: str
    :param resources: Optional resource constraints or measurements.
    :type resources: Tuple[Resource, ...]

    Example::

        >>> from pyudbm.binding.utap import Expectation, Resource
        >>> expectation = Expectation("Probability", "True", "0.95", (Resource("time", "100", "ms"),))
        >>> expectation.value
        '0.95'
    """

    value_type: str
    status: str
    value: str
    resources: Tuple[Resource, ...]


@dataclass(frozen=True)
class TypeInfo:
    """
    Immutable snapshot of one UTAP ``type_t`` descriptor.

    The boolean flags mirror native predicate helpers so callers can inspect
    semantic categories without depending on unstable native internals.

    :param kind: Native ``type_t`` kind code.
    :type kind: int
    :param position: Source position of the type node.
    :type position: Position
    :param size: Native size or arity field.
    :type size: int
    :param text: Safe pretty-printed type text.
    :type text: str
    :param declaration: Safe pretty-printed declaration text.
    :type declaration: str
    :param is_unknown: Whether the type is unresolved.
    :type is_unknown: bool
    :param is_range: Whether the type is a ranged integer type.
    :type is_range: bool
    :param is_integer: Whether the type is an integer type.
    :type is_integer: bool
    :param is_boolean: Whether the type is a boolean type.
    :type is_boolean: bool
    :param is_function: Whether the type denotes a function.
    :type is_function: bool
    :param is_function_external: Whether the function type is external.
    :type is_function_external: bool
    :param is_clock: Whether the type denotes a clock.
    :type is_clock: bool
    :param is_process: Whether the type denotes a process.
    :type is_process: bool
    :param is_process_set: Whether the type denotes a process set.
    :type is_process_set: bool
    :param is_location: Whether the type denotes a location.
    :type is_location: bool
    :param is_location_expr: Whether the type denotes a location expression.
    :type is_location_expr: bool
    :param is_instance_line: Whether the type denotes an instance line.
    :type is_instance_line: bool
    :param is_branchpoint: Whether the type denotes a branchpoint.
    :type is_branchpoint: bool
    :param is_channel: Whether the type denotes a channel.
    :type is_channel: bool
    :param is_record: Whether the type denotes a record.
    :type is_record: bool
    :param is_array: Whether the type denotes an array.
    :type is_array: bool
    :param is_scalar: Whether the type denotes a scalar set.
    :type is_scalar: bool
    :param is_diff: Whether the type denotes a clock-difference form.
    :type is_diff: bool
    :param is_void: Whether the type denotes ``void``.
    :type is_void: bool
    :param is_cost: Whether the type denotes a cost quantity.
    :type is_cost: bool
    :param is_integral: Whether the type is integral.
    :type is_integral: bool
    :param is_invariant: Whether the type denotes an invariant expression.
    :type is_invariant: bool
    :param is_probability: Whether the type denotes a probability.
    :type is_probability: bool
    :param is_guard: Whether the type denotes a guard expression.
    :type is_guard: bool
    :param is_constraint: Whether the type denotes a constraint.
    :type is_constraint: bool
    :param is_formula: Whether the type denotes a formula.
    :type is_formula: bool
    :param is_double: Whether the type denotes a floating-point value.
    :type is_double: bool
    :param is_string: Whether the type denotes a string.
    :type is_string: bool

    Example::

        >>> from pyudbm.binding.utap import Position, TypeInfo
        >>> position = Position(0, 0, None, None, None, None, None)
        >>> type_info = TypeInfo(
        ...     kind=0,
        ...     position=position,
        ...     size=1,
        ...     text="int",
        ...     declaration="int",
        ...     is_unknown=False,
        ...     is_range=False,
        ...     is_integer=True,
        ...     is_boolean=False,
        ...     is_function=False,
        ...     is_function_external=False,
        ...     is_clock=False,
        ...     is_process=False,
        ...     is_process_set=False,
        ...     is_location=False,
        ...     is_location_expr=False,
        ...     is_instance_line=False,
        ...     is_branchpoint=False,
        ...     is_channel=False,
        ...     is_record=False,
        ...     is_array=False,
        ...     is_scalar=False,
        ...     is_diff=False,
        ...     is_void=False,
        ...     is_cost=False,
        ...     is_integral=True,
        ...     is_invariant=False,
        ...     is_probability=False,
        ...     is_guard=False,
        ...     is_constraint=False,
        ...     is_formula=False,
        ...     is_double=False,
        ...     is_string=False,
        ... )
        >>> type_info.is_integer
        True
    """

    kind: int
    position: Position
    size: int
    text: str
    declaration: str
    is_unknown: bool
    is_range: bool
    is_integer: bool
    is_boolean: bool
    is_function: bool
    is_function_external: bool
    is_clock: bool
    is_process: bool
    is_process_set: bool
    is_location: bool
    is_location_expr: bool
    is_instance_line: bool
    is_branchpoint: bool
    is_channel: bool
    is_record: bool
    is_array: bool
    is_scalar: bool
    is_diff: bool
    is_void: bool
    is_cost: bool
    is_integral: bool
    is_invariant: bool
    is_probability: bool
    is_guard: bool
    is_constraint: bool
    is_formula: bool
    is_double: bool
    is_string: bool


@dataclass(frozen=True)
class Symbol:
    """
    Immutable snapshot of one UTAP symbol reference.

    :param name: Symbol name.
    :type name: str
    :param type: Symbol type information.
    :type type: TypeInfo
    :param position: Source position of the symbol declaration or reference.
    :type position: Position

    Example::

        >>> from pyudbm.binding.utap import Position, Symbol, TypeInfo
        >>> position = Position(0, 0, None, None, None, None, None)
        >>> type_info = TypeInfo(
        ...     0,
        ...     position,
        ...     1,
        ...     "clock",
        ...     "clock",
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     True,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ... )
        >>> Symbol("x", type_info, position).name
        'x'
    """

    name: str
    type: TypeInfo
    position: Position


@dataclass(frozen=True)
class Expression:
    """
    Immutable snapshot of one parsed expression tree node.

    ``children`` contains recursively converted expression nodes and
    ``is_empty`` marks optional fields that UTAP reports as structurally empty.

    :param text: Safe pretty-printed expression text.
    :type text: str
    :param kind: Native ``expression_t`` kind code.
    :type kind: int
    :param position: Source position of the expression node.
    :type position: Position
    :param type: Static type information for the expression.
    :type type: TypeInfo
    :param size: Native size or child-count field.
    :type size: int
    :param children: Child expressions in native order.
    :type children: Tuple[Expression, ...]
    :param is_empty: Whether the expression is structurally empty.
    :type is_empty: bool

    Example::

        >>> from pyudbm.binding.utap import Expression, Position, TypeInfo
        >>> position = Position(0, 0, None, None, None, None, None)
        >>> type_info = TypeInfo(
        ...     0,
        ...     position,
        ...     1,
        ...     "int",
        ...     "int",
        ...     False,
        ...     False,
        ...     True,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     True,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ...     False,
        ... )
        >>> expression = Expression("0", 0, position, type_info, 0, (), False)
        >>> expression.text
        '0'
    """

    text: str
    kind: int
    position: Position
    type: TypeInfo
    size: int
    children: Tuple["Expression", ...]
    is_empty: bool


@dataclass(frozen=True)
class Diagnostic:
    """
    One parser or semantic diagnostic emitted by UTAP.

    :param message: Primary diagnostic message.
    :type message: str
    :param context: Additional context text from UTAP.
    :type context: str
    :param position: Structured source span for the diagnostic.
    :type position: Position
    :param line: One-based starting line number, if available.
    :type line: int or None
    :param column: One-based starting column number, if available.
    :type column: int or None
    :param end_line: One-based ending line number, if available.
    :type end_line: int or None
    :param end_column: One-based ending column number, if available.
    :type end_column: int or None
    :param path: Source path associated with the diagnostic, if available.
    :type path: str or None

    Example::

        >>> from pyudbm.binding.utap import Diagnostic, Position
        >>> position = Position(0, 5, 1, 1, 1, 6, "model.xml")
        >>> diagnostic = Diagnostic("error", "context", position, 1, 1, 1, 6, "model.xml")
        >>> diagnostic.message
        'error'
    """

    message: str
    context: str
    position: Position
    line: Optional[int]
    column: Optional[int]
    end_line: Optional[int]
    end_column: Optional[int]
    path: Optional[str]


@dataclass(frozen=True)
class FeatureFlags:
    """
    Supported-language and capability flags detected for a document.

    These fields summarize whether the parsed document uses or supports major
    UTAP feature families such as priorities, stochastic constructs, or
    symbolic verification.

    :param has_priority_declaration: Whether channel priorities are declared.
    :type has_priority_declaration: bool
    :param has_strict_invariants: Whether strict invariants are used.
    :type has_strict_invariants: bool
    :param has_stop_watch: Whether stop-watch clocks are used.
    :type has_stop_watch: bool
    :param has_strict_lower_bound_on_controllable_edges: Whether strict lower
        bounds on controllable edges are used.
    :type has_strict_lower_bound_on_controllable_edges: bool
    :param has_clock_guard_recv_broadcast: Whether receive-broadcast guards use
        clock constraints.
    :type has_clock_guard_recv_broadcast: bool
    :param has_urgent_transition: Whether urgent transitions are present.
    :type has_urgent_transition: bool
    :param has_dynamic_templates: Whether dynamic templates are present.
    :type has_dynamic_templates: bool
    :param all_broadcast: Whether synchronization is broadcast-only.
    :type all_broadcast: bool
    :param sync_used: Native synchronization-usage summary code.
    :type sync_used: int
    :param supports_symbolic: Whether the document is suitable for symbolic
        analysis.
    :type supports_symbolic: bool
    :param supports_stochastic: Whether the document is suitable for
        stochastic analysis.
    :type supports_stochastic: bool
    :param supports_concrete: Whether the document is suitable for concrete
        simulation.
    :type supports_concrete: bool

    Example::

        >>> from pyudbm.binding.utap import FeatureFlags
        >>> flags = FeatureFlags(False, False, False, False, False, False, False, True, 0, True, True, True)
        >>> flags.supports_symbolic
        True
    """

    has_priority_declaration: bool
    has_strict_invariants: bool
    has_stop_watch: bool
    has_strict_lower_bound_on_controllable_edges: bool
    has_clock_guard_recv_broadcast: bool
    has_urgent_transition: bool
    has_dynamic_templates: bool
    all_broadcast: bool
    sync_used: int
    supports_symbolic: bool
    supports_stochastic: bool
    supports_concrete: bool


@dataclass(frozen=True)
class Branchpoint:
    """
    Immutable snapshot of one branchpoint declared inside a template.

    :param name: Branchpoint name.
    :type name: str
    :param index: Native branchpoint index within the template.
    :type index: int
    :param position: Source position of the branchpoint.
    :type position: Position
    :param symbol: Symbol information for the branchpoint.
    :type symbol: Symbol

    Example::

        >>> from pyudbm.binding.utap import Branchpoint, loads_xta
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> document = loads_xta(xta)
        >>> symbol = document.templates[0].locations[0].symbol
        >>> Branchpoint("B", 0, symbol.position, symbol).name
        'B'
    """

    name: str
    index: int
    position: Position
    symbol: Symbol


@dataclass(frozen=True)
class Location:
    """
    Immutable snapshot of one template location.

    Expression fields such as ``invariant`` and ``cost_rate`` are already
    converted to Python expression snapshots.

    :param name: Location name.
    :type name: str
    :param index: Native location index within the template.
    :type index: int
    :param position: Source position of the location.
    :type position: Position
    :param symbol: Symbol information for the location.
    :type symbol: Symbol
    :param name_expression: Optional name expression payload.
    :type name_expression: Expression
    :param invariant: Invariant expression.
    :type invariant: Expression
    :param exp_rate: Exponential-rate expression.
    :type exp_rate: Expression
    :param cost_rate: Cost-rate expression.
    :type cost_rate: Expression
    :param is_urgent: Whether the location is urgent.
    :type is_urgent: bool
    :param is_committed: Whether the location is committed.
    :type is_committed: bool

    Example::

        >>> from pyudbm.binding.utap import loads_xta
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> document = loads_xta(xta)
        >>> document.templates[0].locations[0].name
        'S'
    """

    name: str
    index: int
    position: Position
    symbol: Symbol
    name_expression: Expression
    invariant: Expression
    exp_rate: Expression
    cost_rate: Expression
    is_urgent: bool
    is_committed: bool


@dataclass(frozen=True)
class Edge:
    """
    Immutable snapshot of one template edge.

    Guard, assignment, synchronization, probability, and select metadata are
    exposed through converted expression and symbol snapshots.

    :param index: Native edge index within the template.
    :type index: int
    :param control: Whether the edge is controllable.
    :type control: bool
    :param action_name: Edge action name.
    :type action_name: str
    :param source_name: Source node name.
    :type source_name: str
    :param source_kind: Source node kind.
    :type source_kind: str
    :param target_name: Target node name.
    :type target_name: str
    :param target_kind: Target node kind.
    :type target_kind: str
    :param guard: Guard expression.
    :type guard: Expression
    :param assign: Assignment expression.
    :type assign: Expression
    :param sync: Synchronization expression.
    :type sync: Expression
    :param prob: Probability expression.
    :type prob: Expression
    :param select_text: Raw select clause text.
    :type select_text: str
    :param select_symbols: Symbols introduced by the select clause.
    :type select_symbols: Tuple[Symbol, ...]
    :param select_values: Native select values associated with the symbols.
    :type select_values: Tuple[int, ...]

    Example::

        >>> from pyudbm.binding.utap import Edge, loads_xta
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> document = loads_xta(xta)
        >>> location = document.templates[0].locations[0]
        >>> edge = Edge(
        ...     0,
        ...     False,
        ...     "",
        ...     "S",
        ...     "location",
        ...     "S",
        ...     "location",
        ...     location.invariant,
        ...     location.invariant,
        ...     location.invariant,
        ...     location.invariant,
        ...     "",
        ...     (),
        ...     (),
        ... )
        >>> edge.source_name
        'S'
    """

    index: int
    control: bool
    action_name: str
    source_name: str
    source_kind: str
    target_name: str
    target_kind: str
    guard: Expression
    assign: Expression
    sync: Expression
    prob: Expression
    select_text: str
    select_symbols: Tuple[Symbol, ...]
    select_values: Tuple[int, ...]


@dataclass(frozen=True)
class Query:
    """
    One query entry stored in the parsed document.

    :param formula: Query formula text.
    :type formula: str
    :param comment: Query comment text.
    :type comment: str
    :param options: Query-local option entries.
    :type options: Tuple[Option, ...]
    :param expectation: Stored expectation metadata.
    :type expectation: Expectation
    :param location: Query source-location text.
    :type location: str

    Example::

        >>> from pyudbm.binding.utap import Expectation, Option, Query
        >>> query = Query("A[] !deadlock", "safety", (Option("trace", "short"),), Expectation("Symbolic", "True", "", ()), "")
        >>> query.formula
        'A[] !deadlock'
    """

    formula: str
    comment: str
    options: Tuple[Option, ...]
    expectation: Expectation
    location: str


@dataclass(frozen=True)
class ParsedQueryExpectation:
    """
    Structured expectation metadata produced by query parsing helpers.

    :param result_kind: Parsed result kind.
    :type result_kind: str
    :param status: Parsed expectation status, if present.
    :type status: str or None
    :param value: Parsed expectation numeric value, if present.
    :type value: float or None
    :param time_ms: Expected time budget or measurement in milliseconds.
    :type time_ms: int
    :param mem_kib: Expected memory budget or measurement in KiB.
    :type mem_kib: int

    Example::

        >>> from pyudbm.binding.utap import ParsedQueryExpectation
        >>> expectation = ParsedQueryExpectation("Symbolic", "True", None, 10, 32)
        >>> expectation.time_ms
        10
    """

    result_kind: str
    status: Optional[str]
    value: Optional[float]
    time_ms: int
    mem_kib: int


@dataclass(frozen=True)
class ParsedQuery:
    """
    Immutable snapshot of one query parsed against a document context.

    The parsed expression tree, detected builder, and optional expectation
    metadata are all detached from the native parsing result.

    :param line: One-based source line of the query.
    :type line: int
    :param no: Query number reported by UTAP.
    :type no: int
    :param builder: Selected query builder name.
    :type builder: str
    :param text: Original query text.
    :type text: str
    :param quantifier: Top-level query quantifier.
    :type quantifier: str
    :param options: Parsed query options.
    :type options: Tuple[Option, ...]
    :param expression: Parsed query expression tree.
    :type expression: Expression
    :param is_smc: Whether the query is an SMC query.
    :type is_smc: bool
    :param declaration: Query-local declaration block.
    :type declaration: str
    :param result_type: Parsed query result type.
    :type result_type: str
    :param expectation: Structured expectation metadata, if present.
    :type expectation: ParsedQueryExpectation or None

    Example::

        >>> from pyudbm.binding.utap import loads_xta, parse_query
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> document = loads_xta(xta)
        >>> query = parse_query("A[] not deadlock", document, builder="property")[0]
        >>> query.quantifier
        'AG'
    """

    line: int
    no: int
    builder: str
    text: str
    quantifier: str
    options: Tuple[Option, ...]
    expression: Expression
    is_smc: bool
    declaration: str
    result_type: str
    expectation: Optional[ParsedQueryExpectation]


@dataclass(frozen=True)
class Process:
    """
    Immutable snapshot of one instantiated process in the system section.

    :param name: Process instance name.
    :type name: str
    :param index: Native process index.
    :type index: int
    :param position: Source position of the process declaration.
    :type position: Position
    :param template_name: Name of the referenced template.
    :type template_name: str
    :param parameters: Template parameter text.
    :type parameters: str
    :param arguments: Instantiation argument text.
    :type arguments: str
    :param mapping: Native process mapping text.
    :type mapping: str
    :param argument_count: Number of supplied arguments.
    :type argument_count: int
    :param unbound_count: Number of unresolved parameters.
    :type unbound_count: int
    :param restricted_symbols: Restricted symbols associated with the process.
    :type restricted_symbols: Tuple[Symbol, ...]

    Example::

        >>> from pyudbm.binding.utap import loads_xta
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> document = loads_xta(xta)
        >>> document.processes[0].name
        'P1'
    """

    name: str
    index: int
    position: Position
    template_name: str
    parameters: str
    arguments: str
    mapping: str
    argument_count: int
    unbound_count: int
    restricted_symbols: Tuple[Symbol, ...]


@dataclass(frozen=True)
class Template:
    """
    Immutable snapshot of one UTAP template.

    Locations, branchpoints, and edges are eagerly converted into immutable
    nested snapshots.

    :param name: Template name.
    :type name: str
    :param index: Native template index.
    :type index: int
    :param position: Source position of the template.
    :type position: Position
    :param parameter: Template parameter declaration text.
    :type parameter: str
    :param declaration: Template declaration text currently exposed by the
        high-level wrapper.
    :type declaration: str
    :param init_name: Name of the initial location.
    :type init_name: str
    :param type: Template type name.
    :type type: str
    :param mode: Template mode string.
    :type mode: str
    :param is_ta: Whether the template is a timed automaton.
    :type is_ta: bool
    :param is_instantiated: Whether the template is instantiated in the
        system section.
    :type is_instantiated: bool
    :param dynamic: Whether the template is dynamic.
    :type dynamic: bool
    :param is_defined: Whether the template is fully defined.
    :type is_defined: bool
    :param locations: Template locations.
    :type locations: Tuple[Location, ...]
    :param branchpoints: Template branchpoints.
    :type branchpoints: Tuple[Branchpoint, ...]
    :param edges: Template edges.
    :type edges: Tuple[Edge, ...]

    Example::

        >>> from pyudbm.binding.utap import loads_xta
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> document = loads_xta(xta)
        >>> document.templates[0].name
        'P'
    """

    name: str
    index: int
    position: Position
    parameter: str
    declaration: str
    init_name: str
    type: str
    mode: str
    is_ta: bool
    is_instantiated: bool
    dynamic: bool
    is_defined: bool
    locations: Tuple[Location, ...]
    branchpoints: Tuple[Branchpoint, ...]
    edges: Tuple[Edge, ...]


def _to_position(payload: Mapping[str, Any]) -> Position:
    return Position(
        start=payload["start"],
        end=payload["end"],
        line=payload["line"],
        column=payload["column"],
        end_line=payload["end_line"],
        end_column=payload["end_column"],
        path=payload["path"],
    )


def _to_option(payload: Mapping[str, Any]) -> Option:
    return Option(name=payload["name"], value=payload["value"])


def _to_resource(payload: Mapping[str, Any]) -> Resource:
    return Resource(name=payload["name"], value=payload["value"], unit=payload["unit"])


def _to_expectation(payload: Mapping[str, Any]) -> Expectation:
    return Expectation(
        value_type=payload["value_type"],
        status=payload["status"],
        value=payload["value"],
        resources=tuple(_to_resource(item) for item in payload["resources"]),
    )


def _to_type(payload: Mapping[str, Any]) -> TypeInfo:
    return TypeInfo(
        kind=payload["kind"],
        position=_to_position(payload["position"]),
        size=payload["size"],
        text=payload["text"],
        declaration=payload["declaration"],
        is_unknown=payload["is_unknown"],
        is_range=payload["is_range"],
        is_integer=payload["is_integer"],
        is_boolean=payload["is_boolean"],
        is_function=payload["is_function"],
        is_function_external=payload["is_function_external"],
        is_clock=payload["is_clock"],
        is_process=payload["is_process"],
        is_process_set=payload["is_process_set"],
        is_location=payload["is_location"],
        is_location_expr=payload["is_location_expr"],
        is_instance_line=payload["is_instance_line"],
        is_branchpoint=payload["is_branchpoint"],
        is_channel=payload["is_channel"],
        is_record=payload["is_record"],
        is_array=payload["is_array"],
        is_scalar=payload["is_scalar"],
        is_diff=payload["is_diff"],
        is_void=payload["is_void"],
        is_cost=payload["is_cost"],
        is_integral=payload["is_integral"],
        is_invariant=payload["is_invariant"],
        is_probability=payload["is_probability"],
        is_guard=payload["is_guard"],
        is_constraint=payload["is_constraint"],
        is_formula=payload["is_formula"],
        is_double=payload["is_double"],
        is_string=payload["is_string"],
    )


def _to_symbol(payload: Mapping[str, Any]) -> Symbol:
    return Symbol(
        name=payload["name"],
        type=_to_type(payload["type"]),
        position=_to_position(payload["position"]),
    )


def _to_expression(payload: Mapping[str, Any]) -> Expression:
    return Expression(
        text=payload["text"],
        kind=payload["kind"],
        position=_to_position(payload["position"]),
        type=_to_type(payload["type"]),
        size=payload["size"],
        children=tuple(_to_expression(item) for item in payload["children"]),
        is_empty=payload["is_empty"],
    )


def _to_diagnostic(payload: Mapping[str, Any]) -> Diagnostic:
    return Diagnostic(
        message=payload["message"],
        context=payload["context"],
        position=_to_position(payload["position"]),
        line=payload["line"],
        column=payload["column"],
        end_line=payload["end_line"],
        end_column=payload["end_column"],
        path=payload["path"],
    )


def _to_features(payload: Mapping[str, Any]) -> FeatureFlags:
    return FeatureFlags(
        has_priority_declaration=payload["has_priority_declaration"],
        has_strict_invariants=payload["has_strict_invariants"],
        has_stop_watch=payload["has_stop_watch"],
        has_strict_lower_bound_on_controllable_edges=payload["has_strict_lower_bound_on_controllable_edges"],
        has_clock_guard_recv_broadcast=payload["has_clock_guard_recv_broadcast"],
        has_urgent_transition=payload["has_urgent_transition"],
        has_dynamic_templates=payload["has_dynamic_templates"],
        all_broadcast=payload["all_broadcast"],
        sync_used=payload["sync_used"],
        supports_symbolic=payload["supports_symbolic"],
        supports_stochastic=payload["supports_stochastic"],
        supports_concrete=payload["supports_concrete"],
    )


def _to_branchpoint(payload: Mapping[str, Any]) -> Branchpoint:
    return Branchpoint(
        name=payload["name"],
        index=payload["index"],
        position=_to_position(payload["position"]),
        symbol=_to_symbol(payload["symbol"]),
    )


def _to_location(payload: Mapping[str, Any]) -> Location:
    return Location(
        name=payload["name"],
        index=payload["index"],
        position=_to_position(payload["position"]),
        symbol=_to_symbol(payload["symbol"]),
        name_expression=_to_expression(payload["name_expression"]),
        invariant=_to_expression(payload["invariant"]),
        exp_rate=_to_expression(payload["exp_rate"]),
        cost_rate=_to_expression(payload["cost_rate"]),
        is_urgent=payload["is_urgent"],
        is_committed=payload["is_committed"],
    )


def _to_edge(payload: Mapping[str, Any]) -> Edge:
    return Edge(
        index=payload["index"],
        control=payload["control"],
        action_name=payload["action_name"],
        source_name=payload["source_name"],
        source_kind=payload["source_kind"],
        target_name=payload["target_name"],
        target_kind=payload["target_kind"],
        guard=_to_expression(payload["guard"]),
        assign=_to_expression(payload["assign"]),
        sync=_to_expression(payload["sync"]),
        prob=_to_expression(payload["prob"]),
        select_text=payload["select_text"],
        select_symbols=tuple(_to_symbol(item) for item in payload["select_symbols"]),
        select_values=tuple(payload["select_values"]),
    )


def _to_query(payload: Mapping[str, Any]) -> Query:
    return Query(
        formula=payload["formula"],
        comment=payload["comment"],
        options=tuple(_to_option(item) for item in payload["options"]),
        expectation=_to_expectation(payload["expectation"]),
        location=payload["location"],
    )


def _to_parsed_query_expectation(payload: Optional[Mapping[str, Any]]) -> Optional[ParsedQueryExpectation]:
    if payload is None:
        return None
    return ParsedQueryExpectation(
        result_kind=payload["result_kind"],
        status=payload["status"],
        value=payload["value"],
        time_ms=payload["time_ms"],
        mem_kib=payload["mem_kib"],
    )


def _to_parsed_query(payload: Mapping[str, Any]) -> ParsedQuery:
    return ParsedQuery(
        line=payload["line"],
        no=payload["no"],
        builder=payload["builder"],
        text=payload["text"],
        quantifier=payload["quantifier"],
        options=tuple(_to_option(item) for item in payload["options"]),
        expression=_to_expression(payload["expression"]),
        is_smc=payload["is_smc"],
        declaration=payload["declaration"],
        result_type=payload["result_type"],
        expectation=_to_parsed_query_expectation(payload["expectation"]),
    )


def _to_process(payload: Mapping[str, Any]) -> Process:
    return Process(
        name=payload["name"],
        index=payload["index"],
        position=_to_position(payload["position"]),
        template_name=payload["template_name"],
        parameters=payload["parameters"],
        arguments=payload["arguments"],
        mapping=payload["mapping"],
        argument_count=payload["argument_count"],
        unbound_count=payload["unbound_count"],
        restricted_symbols=tuple(_to_symbol(item) for item in payload["restricted_symbols"]),
    )


def _to_template(payload: Mapping[str, Any]) -> Template:
    return Template(
        name=payload["name"],
        index=payload["index"],
        position=_to_position(payload["position"]),
        parameter=payload["parameter"],
        declaration=payload["declaration"],
        init_name=payload["init_name"],
        type=payload["type"],
        mode=payload["mode"],
        is_ta=payload["is_ta"],
        is_instantiated=payload["is_instantiated"],
        dynamic=payload["dynamic"],
        is_defined=payload["is_defined"],
        locations=tuple(_to_location(item) for item in payload["locations"]),
        branchpoints=tuple(_to_branchpoint(item) for item in payload["branchpoints"]),
        edges=tuple(_to_edge(item) for item in payload["edges"]),
    )


class ModelDocument:
    """
    Immutable Python snapshot of one parsed UTAP document.

    Child objects are detached immutable snapshots created eagerly from the
    native document payload. The owning native document is still retained on
    this object for later phases, but nested wrappers do not depend on it for
    field access.

    The public attributes ``templates``, ``processes``, ``queries``,
    ``options``, ``features``, ``errors``, ``warnings``, and ``modified`` are
    populated eagerly during initialization.

    :ivar templates: Parsed template snapshots.
    :ivar processes: Parsed process snapshots.
    :ivar queries: Stored model queries.
    :ivar options: Top-level query option entries.
    :ivar features: Document feature and capability summary.
    :ivar errors: Parser or semantic errors reported by UTAP.
    :ivar warnings: Parser or semantic warnings reported by UTAP.
    :ivar modified: Whether UTAP reports the document as modified.

    Example::

        >>> from pyudbm.binding.utap import ModelDocument, loads_xta
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> document = loads_xta(xta)
        >>> isinstance(document, ModelDocument)
        True
    """

    def __init__(self, native_document: _NativeDocument):
        """
        Initialize one immutable document snapshot from a native UTAP document.

        :param native_document: Parsed native document returned by
            :mod:`pyudbm.binding._utap`.
        :type native_document: _NativeDocument
        :return: ``None``.
        :rtype: None

        Example::

            >>> from pyudbm.binding._utap import loads_xta as native_loads_xta
            >>> from pyudbm.binding.utap import ModelDocument
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> document = ModelDocument(native_loads_xta(xta))
            >>> document.templates[0].name
            'P'
        """
        self._native = native_document
        payload = native_document.snapshot()
        self.templates = tuple(_to_template(item) for item in payload["templates"])
        self.processes = tuple(_to_process(item) for item in payload["processes"])
        self.queries = tuple(_to_query(item) for item in payload["queries"])
        self.options = tuple(_to_option(item) for item in payload["options"])
        self.features = _to_features(payload["features"])
        self.errors = tuple(_to_diagnostic(item) for item in payload["errors"])
        self.warnings = tuple(_to_diagnostic(item) for item in payload["warnings"])
        self.modified = payload["modified"]

    def __repr__(self) -> str:
        return "<ModelDocument templates={0} processes={1} queries={2} errors={3} warnings={4}>".format(
            len(self.templates), len(self.processes), len(self.queries), len(self.errors), len(self.warnings)
        )

    def write_xml(self, path: Any) -> None:
        """
        Write the native XML serialization to ``path``.

        This delegates directly to the underlying native document writer,
        before Python-side query reinjection performed by :meth:`dumps`.

        :param path: Output path accepted by the native binding.
        :type path: Any
        :return: ``None``.
        :rtype: None

        Example::

            >>> import os
            >>> import tempfile
            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> document = loads_xta(xta)
            >>> with tempfile.TemporaryDirectory() as tempdir:
            ...     path = os.path.join(tempdir, "model.xml")
            ...     document.write_xml(path)
            ...     os.path.isfile(path)
            True
        """

        self._native.write_xml(path)

    def dumps(self) -> str:
        """
        Serialize the document to one XML string.

        The native UTAP writer is used as the structural base. Global
        declarations and query blocks are then patched back into the emitted
        XML so the round-tripped text matches the higher-level Python view.

        :return: XML serialization of the current snapshot.
        :rtype: str
        :raises RuntimeError: If the native XML output does not contain the
            expected ``<declaration>`` or ``</nta>`` structure.

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> document = loads_xta(xta)
            >>> document.dumps().startswith("<?xml")
            True
        """

        with tempfile.TemporaryDirectory(prefix="pyudbm-utap-") as tempdir:
            temp_path = os.path.join(tempdir, "document.xml")
            self.write_xml(temp_path)
            with open(temp_path, "r", encoding="utf-8") as file:
                xml_text = file.read()
        xml_text = _replace_global_declaration_block(xml_text, self.global_declarations)
        return _inject_queries_block(xml_text, self.options, self.queries)

    def to_xml(self) -> str:
        """
        Return the XML serialization of the document.

        This is a convenience alias for :meth:`dumps`.

        :return: XML serialization of the current snapshot.
        :rtype: str

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> document = loads_xta(xta)
            >>> document.to_xml() == document.dumps()
            True
        """

        return self.dumps()

    def dump(self, path: Any) -> None:
        """
        Write the XML serialization of the document to ``path``.

        :param path: Output path.
        :type path: Any
        :return: ``None``.
        :rtype: None

        Example::

            >>> import os
            >>> import tempfile
            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> document = loads_xta(xta)
            >>> with tempfile.TemporaryDirectory() as tempdir:
            ...     path = os.path.join(tempdir, "dump.xml")
            ...     document.dump(path)
            ...     os.path.isfile(path)
            True
        """

        with open(os.fspath(path), "w", encoding="utf-8", newline="\n") as file:
            file.write(self.dumps())

    def to_xta(self, *, include_builtin_preamble: bool = False) -> str:
        """
        Render the document as textual XTA using the upstream UTAP pretty printer.

        This path goes through :meth:`dumps` first and then reparses the
        resulting XML through the official UTAP :class:`PrettyPrinter`.
        It therefore follows the current high-level XML semantics of this
        wrapper rather than the raw native writer.

        By default the built-in declaration preamble injected by the official
        UTAP XML parser in new-syntax mode is removed again before returning
        the result. Set ``include_builtin_preamble=True`` to keep that official
        preamble in the returned text.

        Important limitation:
        upstream pretty-printing focuses on the model text itself. Query
        formulas and comments may be emitted as comments, while XML-only query
        metadata such as query options and expectations are not preserved as a
        machine-readable textual round-trip format.

        :param include_builtin_preamble: Whether to keep the official UTAP
            built-in declaration preamble in the returned XTA text.
        :type include_builtin_preamble: bool
        :return: Textual XTA rendering of the current document.
        :rtype: str

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> "process P()" in loads_xta(xta).to_xta()
            True
        """

        return _xml_to_text(self.dumps(), True, include_builtin_preamble)

    def dump_xta(self, path: Any, *, include_builtin_preamble: bool = False) -> None:
        """
        Write the upstream-pretty-printed XTA rendering to ``path``.

        :param path: Output path.
        :type path: Any
        :param include_builtin_preamble: Whether to keep the official UTAP
            built-in declaration preamble in the written XTA text.
        :type include_builtin_preamble: bool
        :return: ``None``.
        :rtype: None
        """

        with open(os.fspath(path), "w", encoding="utf-8", newline="\n") as file:
            file.write(self.to_xta(include_builtin_preamble=include_builtin_preamble))

    def to_ta(self) -> str:
        """
        Render the document using the upstream pretty printer in old-syntax mode.

        This is the same official pretty-printing path as :meth:`to_xta`, but
        with ``newxta=False`` when feeding XML back into UTAP.

        :return: Textual TA rendering of the current document.
        :rtype: str

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> "process P()" in loads_xta(xta).to_ta()
            True
        """

        return _xml_to_text(self.dumps(), False, False)

    def dump_ta(self, path: Any) -> None:
        """
        Write the old-syntax upstream-pretty-printed rendering to ``path``.

        :param path: Output path.
        :type path: Any
        :return: ``None``.
        :rtype: None
        """

        with open(os.fspath(path), "w", encoding="utf-8", newline="\n") as file:
            file.write(self.to_ta())

    @property
    def global_declarations(self) -> str:
        """
        Return the global declaration block as plain text.

        :return: Global declarations.
        :rtype: str

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> document = loads_xta(xta)
            >>> "clock x;" in document.global_declarations
            True
        """

        return self._native.global_declarations()

    @property
    def before_update_text(self) -> str:
        """
        Return the ``before_update`` declaration text, if present.

        :return: ``before_update`` declaration text.
        :rtype: str

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> loads_xta(xta).before_update_text
            ''
        """

        return self._native.before_update_text()

    @property
    def after_update_text(self) -> str:
        """
        Return the ``after_update`` declaration text, if present.

        :return: ``after_update`` declaration text.
        :rtype: str

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> loads_xta(xta).after_update_text
            ''
        """

        return self._native.after_update_text()

    @property
    def channel_priority_texts(self) -> Tuple[str, ...]:
        """
        Return channel-priority declarations.

        :return: Channel-priority declaration texts.
        :rtype: Tuple[str, ...]

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> loads_xta(xta).channel_priority_texts
            ()
        """

        return tuple(self._native.channel_priority_texts())

    @property
    def global_clock_names(self) -> Tuple[str, ...]:
        """
        Return the global clock names reported by the native document.

        :return: Global clock names.
        :rtype: Tuple[str, ...]

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> loads_xta(xta).global_clock_names
            ('x',)
        """

        return tuple(self._native.global_clock_names())

    @property
    def template_clock_names(self) -> Mapping[str, Tuple[str, ...]]:
        """
        Return per-template clock names.

        :return: Mapping ``{template_name: (clock_names...)}``.
        :rtype: Mapping[str, Tuple[str, ...]]

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> loads_xta(xta).template_clock_names
            {'P': ()}
        """

        return {name: tuple(values) for name, values in self._native.template_clock_names().items()}

    def feature_summary(self) -> Mapping[str, Any]:
        """
        Return feature flags as a plain mapping.

        Keys follow :data:`MAPPED_FIELDS["FeatureFlags"]`.

        :return: Feature-flag mapping.
        :rtype: Mapping[str, Any]

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> loads_xta(xta).feature_summary()["supports_symbolic"]
            True
        """

        return {name: getattr(self.features, name) for name in MAPPED_FIELDS["FeatureFlags"]}

    def capability_summary(self) -> Mapping[str, bool]:
        """
        Return the coarse-grained capability summary.

        :return: Mapping with ``supports_symbolic``,
            ``supports_stochastic``, and ``supports_concrete`` entries.
        :rtype: Mapping[str, bool]

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> loads_xta(xta).capability_summary()["supports_concrete"]
            True
        """

        return {
            "supports_symbolic": self.features.supports_symbolic,
            "supports_stochastic": self.features.supports_stochastic,
            "supports_concrete": self.features.supports_concrete,
        }

    def pretty(self) -> str:
        """
        Return a JSON-formatted summary of the document.

        This helper is intended for debugging, snapshots, and human inspection,
        not as a stable machine-readable interchange contract.

        :return: Pretty-printed JSON summary.
        :rtype: str

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> '"templates"' in loads_xta(xta).pretty()
            True
        """

        payload = {
            "global_declarations": self.global_declarations,
            "before_update": self.before_update_text,
            "after_update": self.after_update_text,
            "channel_priorities": list(self.channel_priority_texts),
            "global_clock_names": list(self.global_clock_names),
            "template_clock_names": {name: list(values) for name, values in self.template_clock_names.items()},
            "features": self.feature_summary(),
            "capabilities": self.capability_summary(),
            "templates": [
                {
                    "name": template.name,
                    "init_name": template.init_name,
                    "type": template.type,
                    "mode": template.mode,
                    "is_ta": template.is_ta,
                    "is_instantiated": template.is_instantiated,
                    "dynamic": template.dynamic,
                    "is_defined": template.is_defined,
                    "location_count": len(template.locations),
                    "branchpoint_count": len(template.branchpoints),
                    "edge_count": len(template.edges),
                }
                for template in self.templates
            ],
            "processes": [
                {
                    "name": process.name,
                    "template_name": process.template_name,
                    "parameters": process.parameters,
                    "arguments": process.arguments,
                    "mapping": process.mapping,
                }
                for process in self.processes
            ],
            "queries": [
                {
                    "formula": query.formula,
                    "comment": query.comment,
                    "options": [{"name": option.name, "value": option.value} for option in query.options],
                    "location": query.location,
                }
                for query in self.queries
            ],
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    def load_query(self, path: Any, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
        """
        Parse queries from ``path`` against this document.

        :param path: Query-file path accepted by the native binding.
        :type path: Any
        :param builder: Query parser selection such as ``"auto"`` or a
            concrete builder name.
        :type builder: str
        :return: Parsed query snapshots.
        :rtype: Tuple[ParsedQuery, ...]
        :raises FileNotFoundError: If ``path`` does not exist.
        :raises pyudbm.binding._utap.ParseError: If UTAP fails to parse the
            query file.

        Example::

            >>> import os
            >>> import tempfile
            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> document = loads_xta(xta)
            >>> with tempfile.TemporaryDirectory() as tempdir:
            ...     path = os.path.join(tempdir, "model.q")
            ...     with open(path, "w", encoding="utf-8") as file:
            ...         _ = file.write("A[] not deadlock")
            ...     document.load_query(path, builder="property")[0].quantifier
            'AG'
        """

        return tuple(_to_parsed_query(item) for item in _load_query(path, self._native, builder=builder))

    def loads_query(self, buffer: str, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
        """
        Parse queries from an in-memory string against this document.

        :param buffer: Query text buffer.
        :type buffer: str
        :param builder: Query parser selection such as ``"auto"`` or a
            concrete builder name.
        :type builder: str
        :return: Parsed query snapshots.
        :rtype: Tuple[ParsedQuery, ...]
        :raises pyudbm.binding._utap.ParseError: If UTAP fails to parse the
            query text.

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> document = loads_xta(xta)
            >>> document.loads_query("A[] not deadlock", builder="property")[0].builder
            'property'
        """

        return tuple(_to_parsed_query(item) for item in _loads_query(buffer, self._native, builder=builder))

    def parse_query(self, buffer: str, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
        """
        Parse inline query text against this document.

        This is a convenience alias over the native inline query parser.

        :param buffer: Query text buffer.
        :type buffer: str
        :param builder: Query parser selection such as ``"auto"`` or a
            concrete builder name.
        :type builder: str
        :return: Parsed query snapshots.
        :rtype: Tuple[ParsedQuery, ...]
        :raises pyudbm.binding._utap.ParseError: If UTAP fails to parse the
            query text.

        Example::

            >>> from pyudbm.binding.utap import loads_xta
            >>> xta = '''clock x;
            ... process P() {
            ... state S;
            ... init S;
            ... }
            ... P1 = P();
            ... system P1;
            ... '''
            >>> document = loads_xta(xta)
            >>> document.parse_query("A[] not deadlock", builder="property")[0].text
            'A[] !deadlock'
        """

        return tuple(_to_parsed_query(item) for item in _parse_query(buffer, self._native, builder=builder))


def builtin_declarations() -> str:
    """
    Return the built-in declaration block injected by the UTAP parser.

    :return: Built-in declarations understood by the parser.
    :rtype: str

    Example::

        >>> from pyudbm.binding.utap import builtin_declarations
        >>> "INT32_MAX" in builtin_declarations()
        True
    """

    return _builtin_declarations()


def textual_builtin_preamble(*, newxta: bool = True) -> str:
    """
    Return the official textual built-in preamble emitted by UTAP.

    This uses the upstream UTAP declaration parser together with the official
    :class:`PrettyPrinter`, so the returned string matches the exact preamble
    that ``parse_XML_*`` injects in new-syntax mode before user declarations.

    :param newxta: Whether to request the new-syntax textual preamble. Old
        syntax does not prepend built-in declarations and therefore returns an
        empty string.
    :type newxta: bool
    :return: Official textual built-in preamble.
    :rtype: str

    Example::

        >>> from pyudbm.binding.utap import textual_builtin_preamble
        >>> textual_builtin_preamble().startswith("const int INT8_MIN")
        True
        >>> textual_builtin_preamble(newxta=False)
        ''
    """

    return _textual_builtin_preamble(newxta)


def _expectation_is_implicit_default(expectation: Expectation) -> bool:
    return (
        expectation.value_type == "Symbolic"
        and expectation.status == "True"
        and expectation.value == ""
        and expectation.resources == ()
    )


def _serialize_options_xml(options: Tuple[Option, ...], indent: str) -> Tuple[str, ...]:
    return tuple(
        f"{indent}<option key={quoteattr(option.name)} value={quoteattr(option.value)}/>" for option in options
    )


def _serialize_expectation_xml(expectation: Expectation, indent: str) -> Tuple[str, ...]:
    if _expectation_is_implicit_default(expectation):
        return ()

    attributes = []
    outcome = _EXPECTATION_STATUS_TO_XML.get(expectation.status)
    if outcome is not None:
        attributes.append(f'outcome={quoteattr(outcome)}')

    expectation_type = _EXPECTATION_TYPE_TO_XML.get(expectation.value_type)
    if expectation_type is not None:
        attributes.append(f'type={quoteattr(expectation_type)}')

    if expectation.value != "":
        attributes.append(f'value={quoteattr(expectation.value)}')

    if expectation.resources:
        lines = [f"{indent}<expect {' '.join(attributes)}>".rstrip()]
        for resource in expectation.resources:
            resource_attributes = [f'type={quoteattr(resource.name)}', f'value={quoteattr(resource.value)}']
            if resource.unit is not None:
                resource_attributes.append(f'unit={quoteattr(resource.unit)}')
            lines.append(f"{indent}  <resource {' '.join(resource_attributes)}/>")
        lines.append(f"{indent}</expect>")
        return tuple(lines)

    if attributes:
        return (f"{indent}<expect {' '.join(attributes)}/>",)

    return (f"{indent}<expect/>",)


def _serialize_query_xml(query: Query, indent: str) -> Tuple[str, ...]:
    lines = [f"{indent}<query>"]
    lines.append(f"{indent}  <formula>{escape(query.formula)}</formula>")
    lines.append(f"{indent}  <comment>{escape(query.comment)}</comment>")
    lines.extend(_serialize_options_xml(query.options, indent + "  "))
    lines.extend(_serialize_expectation_xml(query.expectation, indent + "  "))
    lines.append(f"{indent}</query>")
    return tuple(lines)


def _serialize_queries_block(options: Tuple[Option, ...], queries: Tuple[Query, ...]) -> str:
    if not options and not queries:
        return ""

    lines = ["  <queries>"]
    lines.extend(_serialize_options_xml(options, "    "))
    for query in queries:
        lines.extend(_serialize_query_xml(query, "    "))
    lines.append("  </queries>")
    return "\n".join(lines) + "\n"


def _inject_queries_block(xml_text: str, options: Tuple[Option, ...], queries: Tuple[Query, ...]) -> str:
    queries_block = _serialize_queries_block(options, queries)
    if not queries_block:
        return xml_text

    marker = "</nta>"
    marker_index = xml_text.rfind(marker)
    if marker_index < 0:
        raise RuntimeError("UTAP XML writer returned content without </nta> root terminator")

    prefix = xml_text[:marker_index]
    suffix = xml_text[marker_index:]
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    return prefix + queries_block + suffix


def _replace_global_declaration_block(xml_text: str, declaration_text: str) -> str:
    start_tag = "<declaration>"
    end_tag = "</declaration>"
    start_index = xml_text.find(start_tag)
    if start_index < 0:
        raise RuntimeError("UTAP XML writer returned content without <declaration> tag")
    end_index = xml_text.find(end_tag, start_index)
    if end_index < 0:
        raise RuntimeError("UTAP XML writer returned content without </declaration> terminator")
    content_start = start_index + len(start_tag)
    return xml_text[:content_start] + escape(declaration_text) + xml_text[end_index:]


def _native_document(document: ModelDocument) -> _NativeDocument:
    if type(document) is not ModelDocument:
        raise TypeError("document must be a ModelDocument")
    return document._native


def load_query(path: Any, document: ModelDocument, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
    """
    Parse queries from ``path`` against a parsed model document.

    :param path: Query-file path accepted by the native binding.
    :type path: Any
    :param document: Parsed model document that provides the declaration
        context.
    :type document: ModelDocument
    :param builder: Query parser selection such as ``"auto"`` or a concrete
        builder name.
    :type builder: str
    :return: Parsed query snapshots.
    :rtype: Tuple[ParsedQuery, ...]
    :raises FileNotFoundError: If ``path`` does not exist.
    :raises TypeError: If ``document`` is not a :class:`ModelDocument`.
    :raises pyudbm.binding._utap.ParseError: If UTAP fails to parse the query
        file.

    Example::

        >>> import os
        >>> import tempfile
        >>> from pyudbm.binding.utap import load_query, loads_xta
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> document = loads_xta(xta)
        >>> with tempfile.TemporaryDirectory() as tempdir:
        ...     path = os.path.join(tempdir, "model.q")
        ...     with open(path, "w", encoding="utf-8") as file:
        ...         _ = file.write("A[] not deadlock")
        ...     load_query(path, document, builder="property")[0].quantifier
        'AG'
    """

    return tuple(_to_parsed_query(item) for item in _load_query(path, _native_document(document), builder=builder))


def loads_query(buffer: str, document: ModelDocument, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
    """
    Parse queries from an in-memory string against a parsed model document.

    :param buffer: Query text buffer.
    :type buffer: str
    :param document: Parsed model document that provides the declaration
        context.
    :type document: ModelDocument
    :param builder: Query parser selection such as ``"auto"`` or a concrete
        builder name.
    :type builder: str
    :return: Parsed query snapshots.
    :rtype: Tuple[ParsedQuery, ...]
    :raises TypeError: If ``document`` is not a :class:`ModelDocument`.
    :raises pyudbm.binding._utap.ParseError: If UTAP fails to parse the query
        text.

    Example::

        >>> from pyudbm.binding.utap import loads_query, loads_xta
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> document = loads_xta(xta)
        >>> loads_query("A[] not deadlock", document, builder="property")[0].builder
        'property'
    """

    return tuple(
        _to_parsed_query(item) for item in _loads_query(buffer, _native_document(document), builder=builder)
    )


def parse_query(buffer: str, document: ModelDocument, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
    """
    Parse inline query text against a parsed model document.

    :param buffer: Query text buffer.
    :type buffer: str
    :param document: Parsed model document that provides the declaration
        context.
    :type document: ModelDocument
    :param builder: Query parser selection such as ``"auto"`` or a concrete
        builder name.
    :type builder: str
    :return: Parsed query snapshots.
    :rtype: Tuple[ParsedQuery, ...]
    :raises TypeError: If ``document`` is not a :class:`ModelDocument`.
    :raises pyudbm.binding._utap.ParseError: If UTAP fails to parse the query
        text.

    Example::

        >>> from pyudbm.binding.utap import loads_xta, parse_query
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> document = loads_xta(xta)
        >>> parse_query("A[] not deadlock", document, builder="property")[0].text
        'A[] !deadlock'
    """

    return tuple(
        _to_parsed_query(item) for item in _parse_query(buffer, _native_document(document), builder=builder)
    )


def load_xml(path: Any, newxta: bool = True, strict: bool = True, libpaths: Iterable[Any] = ()) -> ModelDocument:
    """
    Parse one XML model file into a :class:`ModelDocument`.

    :param path: XML model path.
    :type path: Any
    :param newxta: Whether to enable the ``newxta`` parser mode.
    :type newxta: bool
    :param strict: Whether to request strict parsing.
    :type strict: bool
    :param libpaths: Additional include-library search paths.
    :type libpaths: Iterable[Any]
    :return: Parsed immutable document snapshot.
    :rtype: ModelDocument
    :raises FileNotFoundError: If ``path`` does not exist.
    :raises pyudbm.binding._utap.ParseError: If UTAP fails to parse the XML
        model.

    Example::

        >>> import os
        >>> import tempfile
        >>> from pyudbm.binding.utap import load_xml
        >>> xml_text = '''<?xml version="1.0" encoding="utf-8"?>
        ... <!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
        ... <nta>
        ...   <declaration>clock x;</declaration>
        ...   <template>
        ...     <name x="0" y="0">P</name>
        ...     <location id="id0" x="0" y="0">
        ...       <name x="0" y="0">Init</name>
        ...     </location>
        ...     <init ref="id0"/>
        ...   </template>
        ...   <system>P1 = P();
        ... system P1;</system>
        ... </nta>
        ... '''
        >>> with tempfile.TemporaryDirectory() as tempdir:
        ...     path = os.path.join(tempdir, "model.xml")
        ...     with open(path, "w", encoding="utf-8") as file:
        ...         _ = file.write(xml_text)
        ...     load_xml(path).templates[0].name
        'P'
    """

    return ModelDocument(_load_xml(path, newxta=newxta, strict=strict, libpaths=tuple(libpaths)))


def loads_xml(buffer: str, newxta: bool = True, strict: bool = True, libpaths: Iterable[Any] = ()) -> ModelDocument:
    """
    Parse one XML model string into a :class:`ModelDocument`.

    :param buffer: XML model text.
    :type buffer: str
    :param newxta: Whether to enable the ``newxta`` parser mode.
    :type newxta: bool
    :param strict: Whether to request strict parsing.
    :type strict: bool
    :param libpaths: Additional include-library search paths.
    :type libpaths: Iterable[Any]
    :return: Parsed immutable document snapshot.
    :rtype: ModelDocument
    :raises pyudbm.binding._utap.ParseError: If UTAP fails to parse the XML
        model.

    Example::

        >>> from pyudbm.binding.utap import loads_xml
        >>> xml_text = '''<?xml version="1.0" encoding="utf-8"?>
        ... <!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
        ... <nta>
        ...   <declaration>clock x;</declaration>
        ...   <template>
        ...     <name x="0" y="0">P</name>
        ...     <location id="id0" x="0" y="0">
        ...       <name x="0" y="0">Init</name>
        ...     </location>
        ...     <init ref="id0"/>
        ...   </template>
        ...   <system>P1 = P();
        ... system P1;</system>
        ... </nta>
        ... '''
        >>> loads_xml(xml_text).processes[0].name
        'P1'
    """

    return ModelDocument(_loads_xml(buffer, newxta=newxta, strict=strict, libpaths=tuple(libpaths)))


def load_xta(path: Any, newxta: bool = True, strict: bool = True) -> ModelDocument:
    """
    Parse one textual XTA model file into a :class:`ModelDocument`.

    :param path: XTA model path.
    :type path: Any
    :param newxta: Whether to enable the ``newxta`` parser mode.
    :type newxta: bool
    :param strict: Whether to request strict parsing.
    :type strict: bool
    :return: Parsed immutable document snapshot.
    :rtype: ModelDocument
    :raises FileNotFoundError: If ``path`` does not exist.
    :raises pyudbm.binding._utap.ParseError: If UTAP fails to parse the XTA
        model.

    Example::

        >>> import os
        >>> import tempfile
        >>> from pyudbm.binding.utap import load_xta
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> with tempfile.TemporaryDirectory() as tempdir:
        ...     path = os.path.join(tempdir, "model.xta")
        ...     with open(path, "w", encoding="utf-8") as file:
        ...         _ = file.write(xta)
        ...     load_xta(path).templates[0].name
        'P'
    """

    return ModelDocument(_load_xta(path, newxta=newxta, strict=strict))


def loads_xta(buffer: str, newxta: bool = True, strict: bool = True) -> ModelDocument:
    """
    Parse one textual XTA model string into a :class:`ModelDocument`.

    :param buffer: XTA model text.
    :type buffer: str
    :param newxta: Whether to enable the ``newxta`` parser mode.
    :type newxta: bool
    :param strict: Whether to request strict parsing.
    :type strict: bool
    :return: Parsed immutable document snapshot.
    :rtype: ModelDocument
    :raises pyudbm.binding._utap.ParseError: If UTAP fails to parse the XTA
        model.

    Example::

        >>> from pyudbm.binding.utap import loads_xta
        >>> xta = '''clock x;
        ... process P() {
        ... state S;
        ... init S;
        ... }
        ... P1 = P();
        ... system P1;
        ... '''
        >>> loads_xta(xta).processes[0].name
        'P1'
    """

    return ModelDocument(_loads_xta(buffer, newxta=newxta, strict=strict))
