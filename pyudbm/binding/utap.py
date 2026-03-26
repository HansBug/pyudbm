"""
High-level read-only UTAP API.

This module layers immutable Python snapshots on top of the native
``pyudbm.binding._utap`` module. The public API intentionally stays read-only
for now:

* parsing returns a :class:`ModelDocument`;
* nested model objects are immutable dataclass snapshots;
* the owning :class:`ModelDocument` still keeps the native document alive for
  future phases such as XML round-trip helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Tuple

from . import _utap

__all__ = [
    "Diagnostic",
    "Edge",
    "Expectation",
    "Expression",
    "FeatureFlags",
    "Location",
    "MAPPED_FIELDS",
    "ModelDocument",
    "Option",
    "Position",
    "Process",
    "Query",
    "Resource",
    "Symbol",
    "Template",
    "TypeInfo",
    "UNMAPPED_FIELDS",
    "builtin_declarations",
    "load_xml",
    "load_xta",
    "loads_xml",
    "loads_xta",
]


MAPPED_FIELDS = {
    "Document": ("templates", "processes", "queries", "options", "features", "errors", "warnings"),
    "Template": ("name", "index", "position", "parameter", "declaration", "init_name", "locations", "edges"),
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
    ),
    "Location": ("name", "index", "position", "symbol", "invariant", "exp_rate", "cost_rate", "is_urgent", "is_committed"),
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
    ),
    "Query": ("formula", "comment", "options", "expectation", "location"),
    "expression_t": ("text", "kind", "position", "type", "size", "children", "is_empty"),
    "type_t": (
        "kind",
        "position",
        "size",
        "text",
        "declaration",
        "is_unknown",
        "is_integer",
        "is_boolean",
        "is_clock",
        "is_process",
        "is_record",
        "is_array",
        "is_integral",
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

UNMAPPED_FIELDS = {
    "Document": ("globals", "before_update", "after_update", "chan_priorities", "strings"),
    "Template": ("branchpoints", "messages", "updates", "conditions", "dynamic_evals"),
    "Process": ("restricted",),
    "Location": ("name_expression",),
    "Edge": ("select_values",),
    "Query": ("results",),
    "expression_t": ("value", "double_value", "sync", "record_label_index", "string_value", "symbol"),
    "type_t": ("children", "range", "labels"),
    "symbol_t": ("frame", "user_data"),
}


@dataclass(frozen=True)
class Position:
    start: int
    end: int
    line: Optional[int]
    column: Optional[int]
    end_line: Optional[int]
    end_column: Optional[int]
    path: Optional[str]


@dataclass(frozen=True)
class Option:
    name: str
    value: str


@dataclass(frozen=True)
class Resource:
    name: str
    value: str
    unit: Optional[str]


@dataclass(frozen=True)
class Expectation:
    value_type: str
    status: str
    value: str
    resources: Tuple[Resource, ...]


@dataclass(frozen=True)
class TypeInfo:
    kind: int
    position: Position
    size: int
    text: str
    declaration: str
    is_unknown: bool
    is_integer: bool
    is_boolean: bool
    is_clock: bool
    is_process: bool
    is_record: bool
    is_array: bool
    is_integral: bool
    is_guard: bool
    is_constraint: bool
    is_formula: bool
    is_double: bool
    is_string: bool


@dataclass(frozen=True)
class Symbol:
    name: str
    type: TypeInfo
    position: Position


@dataclass(frozen=True)
class Expression:
    text: str
    kind: int
    position: Position
    type: TypeInfo
    size: int
    children: Tuple["Expression", ...]
    is_empty: bool


@dataclass(frozen=True)
class Diagnostic:
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
class Location:
    name: str
    index: int
    position: Position
    symbol: Symbol
    invariant: Expression
    exp_rate: Expression
    cost_rate: Expression
    is_urgent: bool
    is_committed: bool


@dataclass(frozen=True)
class Edge:
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


@dataclass(frozen=True)
class Query:
    formula: str
    comment: str
    options: Tuple[Option, ...]
    expectation: Expectation
    location: str


@dataclass(frozen=True)
class Process:
    name: str
    index: int
    position: Position
    template_name: str
    parameters: str
    arguments: str
    mapping: str
    argument_count: int
    unbound_count: int


@dataclass(frozen=True)
class Template:
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
        is_integer=payload["is_integer"],
        is_boolean=payload["is_boolean"],
        is_clock=payload["is_clock"],
        is_process=payload["is_process"],
        is_record=payload["is_record"],
        is_array=payload["is_array"],
        is_integral=payload["is_integral"],
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


def _to_location(payload: Mapping[str, Any]) -> Location:
    return Location(
        name=payload["name"],
        index=payload["index"],
        position=_to_position(payload["position"]),
        symbol=_to_symbol(payload["symbol"]),
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
    )


def _to_query(payload: Mapping[str, Any]) -> Query:
    return Query(
        formula=payload["formula"],
        comment=payload["comment"],
        options=tuple(_to_option(item) for item in payload["options"]),
        expectation=_to_expectation(payload["expectation"]),
        location=payload["location"],
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
        edges=tuple(_to_edge(item) for item in payload["edges"]),
    )


class ModelDocument:
    """
    Immutable Python snapshot of one parsed UTAP document.

    Child objects are detached immutable snapshots created eagerly from the
    native document payload. The owning native document is still retained on
    this object for later phases, but nested wrappers do not depend on it for
    field access.
    """

    def __init__(self, native_document: _utap._NativeDocument):
        self._native = native_document
        payload = native_document.snapshot()
        self.templates = tuple(_to_template(item) for item in payload["templates"])
        self.processes = tuple(_to_process(item) for item in payload["processes"])
        self.queries = tuple(_to_query(item) for item in payload["queries"])
        self.options = tuple(_to_option(item) for item in payload["options"])
        self.features = _to_features(payload["features"])
        self.errors = tuple(_to_diagnostic(item) for item in payload["errors"])
        self.warnings = tuple(_to_diagnostic(item) for item in payload["warnings"])

    def __repr__(self) -> str:
        return "<ModelDocument templates={0} processes={1} queries={2} errors={3} warnings={4}>".format(
            len(self.templates), len(self.processes), len(self.queries), len(self.errors), len(self.warnings)
        )


def builtin_declarations() -> str:
    return _utap.builtin_declarations()


def load_xml(path: Any, newxta: bool = True, strict: bool = True, libpaths: Iterable[Any] = ()) -> ModelDocument:
    return ModelDocument(_utap.load_xml(path, newxta=newxta, strict=strict, libpaths=tuple(libpaths)))


def loads_xml(buffer: str, newxta: bool = True, strict: bool = True, libpaths: Iterable[Any] = ()) -> ModelDocument:
    return ModelDocument(_utap.loads_xml(buffer, newxta=newxta, strict=strict, libpaths=tuple(libpaths)))


def load_xta(path: Any, newxta: bool = True, strict: bool = True) -> ModelDocument:
    return ModelDocument(_utap.load_xta(path, newxta=newxta, strict=strict))


def loads_xta(buffer: str, newxta: bool = True, strict: bool = True) -> ModelDocument:
    return ModelDocument(_utap.loads_xta(buffer, newxta=newxta, strict=strict))
