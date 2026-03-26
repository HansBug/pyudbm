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

import json
import os
import tempfile
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Tuple
from xml.sax.saxutils import escape, quoteattr

from . import _utap

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
]


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

UNMAPPED_FIELD_REASONS = {
    "Document": {
        "globals": "Exposed via global_declarations() instead of re-exporting raw declarations_t as a first-phase value object.",
        "before_update": "Exposed via before_update_text() instead of re-exporting raw expression_t on the first-phase document snapshot.",
        "after_update": "Exposed via after_update_text() instead of re-exporting raw expression_t on the first-phase document snapshot.",
        "chan_priorities": "Exposed via channel_priority_texts() instead of re-exporting raw chan_priority_t objects.",
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
class Branchpoint:
    name: str
    index: int
    position: Position
    symbol: Symbol


@dataclass(frozen=True)
class Location:
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
    formula: str
    comment: str
    options: Tuple[Option, ...]
    expectation: Expectation
    location: str


@dataclass(frozen=True)
class ParsedQueryExpectation:
    result_kind: str
    status: Optional[str]
    value: Optional[float]
    time_ms: int
    mem_kib: int


@dataclass(frozen=True)
class ParsedQuery:
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
        self.modified = payload["modified"]

    def __repr__(self) -> str:
        return "<ModelDocument templates={0} processes={1} queries={2} errors={3} warnings={4}>".format(
            len(self.templates), len(self.processes), len(self.queries), len(self.errors), len(self.warnings)
        )

    def write_xml(self, path: Any) -> None:
        self._native.write_xml(path)

    def dumps(self) -> str:
        with tempfile.TemporaryDirectory(prefix="pyudbm-utap-") as tempdir:
            temp_path = os.path.join(tempdir, "document.xml")
            self.write_xml(temp_path)
            with open(temp_path, "r", encoding="utf-8") as file:
                xml_text = file.read()
        xml_text = _replace_global_declaration_block(xml_text, self.global_declarations())
        return _inject_queries_block(xml_text, self.options, self.queries)

    def to_xml(self) -> str:
        return self.dumps()

    def dump(self, path: Any) -> None:
        with open(os.fspath(path), "w", encoding="utf-8", newline="\n") as file:
            file.write(self.dumps())

    def global_declarations(self) -> str:
        return self._native.global_declarations()

    def before_update_text(self) -> str:
        return self._native.before_update_text()

    def after_update_text(self) -> str:
        return self._native.after_update_text()

    def channel_priority_texts(self) -> Tuple[str, ...]:
        return tuple(self._native.channel_priority_texts())

    def global_clock_names(self) -> Tuple[str, ...]:
        return tuple(self._native.global_clock_names())

    def template_clock_names(self) -> Mapping[str, Tuple[str, ...]]:
        return {name: tuple(values) for name, values in self._native.template_clock_names().items()}

    def feature_summary(self) -> Mapping[str, Any]:
        return {name: getattr(self.features, name) for name in MAPPED_FIELDS["FeatureFlags"]}

    def capability_summary(self) -> Mapping[str, bool]:
        return {
            "supports_symbolic": self.features.supports_symbolic,
            "supports_stochastic": self.features.supports_stochastic,
            "supports_concrete": self.features.supports_concrete,
        }

    def pretty(self) -> str:
        payload = {
            "global_declarations": self.global_declarations(),
            "before_update": self.before_update_text(),
            "after_update": self.after_update_text(),
            "channel_priorities": list(self.channel_priority_texts()),
            "global_clock_names": list(self.global_clock_names()),
            "template_clock_names": {name: list(values) for name, values in self.template_clock_names().items()},
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
        return tuple(_to_parsed_query(item) for item in _utap.load_query(path, self._native, builder=builder))

    def loads_query(self, buffer: str, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
        return tuple(_to_parsed_query(item) for item in _utap.loads_query(buffer, self._native, builder=builder))

    def parse_query(self, buffer: str, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
        return tuple(_to_parsed_query(item) for item in _utap.parse_query(buffer, self._native, builder=builder))


def builtin_declarations() -> str:
    return _utap.builtin_declarations()


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


def _native_document(document: ModelDocument) -> _utap._NativeDocument:
    if type(document) is not ModelDocument:
        raise TypeError("document must be a ModelDocument")
    return document._native


def load_query(path: Any, document: ModelDocument, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
    return tuple(_to_parsed_query(item) for item in _utap.load_query(path, _native_document(document), builder=builder))


def loads_query(buffer: str, document: ModelDocument, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
    return tuple(_to_parsed_query(item) for item in _utap.loads_query(buffer, _native_document(document), builder=builder))


def parse_query(buffer: str, document: ModelDocument, *, builder: str = "auto") -> Tuple[ParsedQuery, ...]:
    return tuple(_to_parsed_query(item) for item in _utap.parse_query(buffer, _native_document(document), builder=builder))


def load_xml(path: Any, newxta: bool = True, strict: bool = True, libpaths: Iterable[Any] = ()) -> ModelDocument:
    return ModelDocument(_utap.load_xml(path, newxta=newxta, strict=strict, libpaths=tuple(libpaths)))


def loads_xml(buffer: str, newxta: bool = True, strict: bool = True, libpaths: Iterable[Any] = ()) -> ModelDocument:
    return ModelDocument(_utap.loads_xml(buffer, newxta=newxta, strict=strict, libpaths=tuple(libpaths)))


def load_xta(path: Any, newxta: bool = True, strict: bool = True) -> ModelDocument:
    return ModelDocument(_utap.load_xta(path, newxta=newxta, strict=strict))


def loads_xta(buffer: str, newxta: bool = True, strict: bool = True) -> ModelDocument:
    return ModelDocument(_utap.loads_xta(buffer, newxta=newxta, strict=strict))
