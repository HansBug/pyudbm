from pathlib import Path

from pyudbm.binding import (
    Branchpoint,
    Edge,
    Expression,
    FeatureFlags,
    Location,
    Position,
    Process,
    Symbol,
    Template,
    TypeInfo,
)


REPO_ROOT = Path(__file__).resolve().parents[2]

MINIMAL_XML_PATH = REPO_ROOT / "test/testfile/utap/minimal_ok.xml"
MINIMAL_XTA_PATH = REPO_ROOT / "test/testfile/utap/minimal_ok.xta"
SIMPLE_SYSTEM_XML_PATH = REPO_ROOT / "test/testfile/utap/simple_system.xml"
SAMPLESMC_XML_PATH = REPO_ROOT / "test/testfile/official/linked/uppaal.org/casestudies/smc/samplesmc.xml"
LMAC6_XML_PATH = REPO_ROOT / "test/testfile/official/linked/uppaal.org/casestudies/smc/lmac6.xml"
HDDI_INPUT_02_TA_PATH = (
    REPO_ROOT / "test/testfile/official/linked/www.it.uu.se/research/group/darts/uppaal/benchmarks/hddi/hddi_input_02.ta"
)

PHASE5_FIELD_MATRIX = {
    "Document": {
        "mapped": ("templates", "processes", "queries", "options", "features", "errors", "warnings", "modified"),
        "unmapped": ("globals", "before_update", "after_update", "chan_priorities", "strings"),
    },
    "Template": {
        "mapped": (
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
        "unmapped": ("messages", "updates", "conditions", "dynamic_evals"),
    },
    "Process": {
        "mapped": (
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
        "unmapped": ("restricted",),
    },
    "Branchpoint": {
        "mapped": ("name", "index", "position", "symbol"),
        "unmapped": (),
    },
    "Location": {
        "mapped": (
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
        "unmapped": (),
    },
    "Edge": {
        "mapped": (
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
        "unmapped": (),
    },
    "Query": {
        "mapped": ("formula", "comment", "options", "expectation", "location"),
        "unmapped": ("results",),
    },
    "Option": {
        "mapped": ("name", "value"),
        "unmapped": (),
    },
    "FeatureFlags": {
        "mapped": (
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
        "unmapped": (),
    },
    "expectation_t": {
        "mapped": ("result_kind", "status", "value", "time_ms", "mem_kib"),
        "unmapped": (),
    },
    "ParsedQuery": {
        "mapped": (
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
        "unmapped": ("subjections", "imitation"),
    },
    "expression_t": {
        "mapped": ("text", "kind", "position", "type", "size", "children", "is_empty"),
        "unmapped": ("value", "double_value", "sync", "record_label_index", "string_value", "symbol"),
    },
    "type_t": {
        "mapped": (
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
        "unmapped": ("children", "range", "labels"),
    },
    "symbol_t": {
        "mapped": ("name", "type", "position"),
        "unmapped": ("frame", "user_data"),
    },
    "position_t": {
        "mapped": ("start", "end", "line", "column", "end_line", "end_column", "path"),
        "unmapped": (),
    },
    "diagnostic_t": {
        "mapped": ("message", "context", "position", "line", "column", "end_line", "end_column", "path"),
        "unmapped": (),
    },
}

PHASE5_MAPPED_FIELD_NOTES = {
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

PHASE5_UNMAPPED_FIELD_REASONS = {
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

EMPTY_POSITION = Position(
    start=2147483647,
    end=2147483647,
    line=None,
    column=None,
    end_line=None,
    end_column=None,
    path=None,
)


def _make_type(kind, text, declaration, position=EMPTY_POSITION, size=0, **flags):
    bool_flags = {
        "is_unknown": False,
        "is_range": False,
        "is_integer": False,
        "is_boolean": False,
        "is_function": False,
        "is_function_external": False,
        "is_clock": False,
        "is_process": False,
        "is_process_set": False,
        "is_location": False,
        "is_location_expr": False,
        "is_instance_line": False,
        "is_branchpoint": False,
        "is_channel": False,
        "is_record": False,
        "is_array": False,
        "is_scalar": False,
        "is_diff": False,
        "is_void": False,
        "is_cost": False,
        "is_integral": False,
        "is_invariant": False,
        "is_probability": False,
        "is_guard": False,
        "is_constraint": False,
        "is_formula": False,
        "is_double": False,
        "is_string": False,
    }
    bool_flags.update(flags)
    return TypeInfo(
        kind=kind,
        position=position,
        size=size,
        text=text,
        declaration=declaration,
        **bool_flags,
    )


def _make_expr(text, kind, position, type_info, size, children=(), is_empty=False):
    return Expression(
        text=text,
        kind=kind,
        position=position,
        type=type_info,
        size=size,
        children=children,
        is_empty=is_empty,
    )


UNKNOWN_TYPE = _make_type(152, "", "", is_unknown=True)
INT_TYPE = _make_type(
    155,
    "int",
    "int",
    is_integer=True,
    is_integral=True,
    is_invariant=True,
    is_probability=True,
    is_guard=True,
    is_constraint=True,
    is_formula=True,
)
LOCATION_TYPE = _make_type(
    160,
    "location",
    "location",
    is_location=True,
    is_integral=True,
    is_invariant=True,
    is_guard=True,
    is_constraint=True,
    is_formula=True,
)
BRANCHPOINT_TYPE = _make_type(170, "branchpoint", "branchpoint", is_branchpoint=True)
INVARIANT_TYPE = _make_type(164, "", "", is_invariant=True, is_guard=True, is_constraint=True, is_formula=True)
RANGED_INT_TYPE = _make_type(
    137,
    "int",
    "int",
    size=1,
    is_range=True,
    is_integer=True,
    is_integral=True,
    is_invariant=True,
    is_probability=True,
    is_guard=True,
    is_constraint=True,
    is_formula=True,
)

SIMPLE_SYSTEM_CLOCK_TYPE = _make_type(
    154,
    "clock",
    "clock",
    position=Position(start=1885, end=1890, line=1, column=1, end_line=1, end_column=6, path="/nta/declaration"),
    is_clock=True,
    is_probability=True,
)
SAMPLESMC_CLOCK_TYPE = _make_type(
    154,
    "clock",
    "clock",
    position=Position(
        start=2065,
        end=2070,
        line=2,
        column=1,
        end_line=2,
        end_column=6,
        path="/nta/template[1]/declaration",
    ),
    is_clock=True,
    is_probability=True,
)

EMPTY_EXPRESSION = _make_expr("", -1, EMPTY_POSITION, UNKNOWN_TYPE, 0, (), True)

DEFAULT_FEATURE_FLAGS = FeatureFlags(
    has_priority_declaration=False,
    has_strict_invariants=False,
    has_stop_watch=False,
    has_strict_lower_bound_on_controllable_edges=False,
    has_clock_guard_recv_broadcast=False,
    has_urgent_transition=False,
    has_dynamic_templates=False,
    all_broadcast=True,
    sync_used=0,
    supports_symbolic=True,
    supports_stochastic=True,
    supports_concrete=True,
)

MINIMAL_XML_LOCATION = Location(
    name="Init",
    index=0,
    position=Position(
        start=1903,
        end=1904,
        line=1,
        column=1,
        end_line=1,
        end_column=2,
        path="/nta/template[1]/location[1]",
    ),
    symbol=Symbol(
        name="Init",
        type=LOCATION_TYPE,
        position=Position(
            start=1903,
            end=1904,
            line=1,
            column=1,
            end_line=1,
            end_column=2,
            path="/nta/template[1]/location[1]",
        ),
    ),
    name_expression=EMPTY_EXPRESSION,
    invariant=EMPTY_EXPRESSION,
    exp_rate=EMPTY_EXPRESSION,
    cost_rate=EMPTY_EXPRESSION,
    is_urgent=False,
    is_committed=False,
)

MINIMAL_XML_TEMPLATE = Template(
    name="P",
    index=0,
    position=Position(
        start=1896,
        end=1897,
        line=1,
        column=1,
        end_line=1,
        end_column=2,
        path="/nta/template[1]",
    ),
    parameter="",
    declaration="",
    init_name="Init",
    type="",
    mode="",
    is_ta=True,
    is_instantiated=True,
    dynamic=False,
    is_defined=False,
    locations=(MINIMAL_XML_LOCATION,),
    branchpoints=(),
    edges=(),
)

MINIMAL_XML_PROCESS = Process(
    name="P1",
    index=0,
    position=Position(
        start=1926,
        end=1928,
        line=2,
        column=8,
        end_line=2,
        end_column=10,
        path="/nta/system",
    ),
    template_name="P",
    parameters="",
    arguments="",
    mapping="",
    argument_count=0,
    unbound_count=0,
    restricted_symbols=(),
)

MINIMAL_XML_DOCUMENT_PUBLIC = {
    "templates": (MINIMAL_XML_TEMPLATE,),
    "processes": (MINIMAL_XML_PROCESS,),
    "queries": (),
    "options": (),
    "features": DEFAULT_FEATURE_FLAGS,
    "errors": (),
    "warnings": (),
    "modified": False,
}

MINIMAL_XTA_LOCATION = Location(
    name="S",
    index=0,
    position=Position(start=3843, end=3844, line=3, column=7, end_line=3, end_column=8, path=""),
    symbol=Symbol(
        name="S",
        type=LOCATION_TYPE,
        position=Position(start=3843, end=3844, line=3, column=7, end_line=3, end_column=8, path=""),
    ),
    name_expression=EMPTY_EXPRESSION,
    invariant=EMPTY_EXPRESSION,
    exp_rate=EMPTY_EXPRESSION,
    cost_rate=EMPTY_EXPRESSION,
    is_urgent=False,
    is_committed=False,
)

MINIMAL_XTA_TEMPLATE = Template(
    name="P",
    index=0,
    position=Position(start=3823, end=3836, line=2, column=1, end_line=2, end_column=14, path=""),
    parameter="",
    declaration="",
    init_name="S",
    type="",
    mode="",
    is_ta=True,
    is_instantiated=True,
    dynamic=False,
    is_defined=False,
    locations=(MINIMAL_XTA_LOCATION,),
    branchpoints=(),
    edges=(),
)

MINIMAL_XTA_PROCESS = Process(
    name="P1",
    index=0,
    position=Position(start=3873, end=3875, line=7, column=8, end_line=7, end_column=10, path=""),
    template_name="P",
    parameters="",
    arguments="",
    mapping="",
    argument_count=0,
    unbound_count=0,
    restricted_symbols=(),
)

MINIMAL_XTA_DOCUMENT_PUBLIC = {
    "templates": (MINIMAL_XTA_TEMPLATE,),
    "processes": (MINIMAL_XTA_PROCESS,),
    "queries": (),
    "options": (),
    "features": DEFAULT_FEATURE_FLAGS,
    "errors": (),
    "warnings": (),
    "modified": False,
}

SIMPLE_SYSTEM_PROCESS = Process(
    name="Process",
    index=0,
    position=Position(
        start=2069,
        end=2076,
        line=4,
        column=8,
        end_line=4,
        end_column=15,
        path="/nta/system",
    ),
    template_name="Template",
    parameters="",
    arguments="",
    mapping="",
    argument_count=0,
    unbound_count=0,
    restricted_symbols=(),
)

SIMPLE_SYSTEM_LOCATION = Location(
    name="First",
    index=2,
    position=Position(
        start=1967,
        end=1968,
        line=1,
        column=1,
        end_line=1,
        end_column=2,
        path="/nta/template[1]/location[3]",
    ),
    symbol=Symbol(
        name="First",
        type=LOCATION_TYPE,
        position=Position(
            start=1967,
            end=1968,
            line=1,
            column=1,
            end_line=1,
            end_column=2,
            path="/nta/template[1]/location[3]",
        ),
    ),
    name_expression=EMPTY_EXPRESSION,
    invariant=_make_expr(
        "1 && c < 2",
        10,
        Position(
            start=1959,
            end=1964,
            line=1,
            column=1,
            end_line=1,
            end_column=6,
            path="/nta/template[1]/location[3]/label[1]",
        ),
        INVARIANT_TYPE,
        2,
        children=(
            _make_expr("1", 137, EMPTY_POSITION, INT_TYPE, 0),
            _make_expr(
                "c < 2",
                18,
                Position(
                    start=1959,
                    end=1964,
                    line=1,
                    column=1,
                    end_line=1,
                    end_column=6,
                    path="/nta/template[1]/location[3]/label[1]",
                ),
                INVARIANT_TYPE,
                2,
                children=(
                    _make_expr(
                        "c",
                        136,
                        Position(
                            start=1959,
                            end=1960,
                            line=1,
                            column=1,
                            end_line=1,
                            end_column=2,
                            path="/nta/template[1]/location[3]/label[1]",
                        ),
                        SIMPLE_SYSTEM_CLOCK_TYPE,
                        0,
                    ),
                    _make_expr(
                        "2",
                        137,
                        Position(
                            start=1963,
                            end=1964,
                            line=1,
                            column=5,
                            end_line=1,
                            end_column=6,
                            path="/nta/template[1]/location[3]/label[1]",
                        ),
                        INT_TYPE,
                        0,
                    ),
                ),
            ),
        ),
    ),
    exp_rate=_make_expr(
        "1",
        137,
        Position(
            start=1965,
            end=1966,
            line=1,
            column=1,
            end_line=1,
            end_column=2,
            path="/nta/template[1]/location[3]/label[2]",
        ),
        INT_TYPE,
        0,
    ),
    cost_rate=EMPTY_EXPRESSION,
    is_urgent=False,
    is_committed=False,
)

SIMPLE_SYSTEM_EDGE = Edge(
    index=2,
    control=True,
    action_name="SKIP",
    source_name="First",
    source_kind="location",
    target_name="L2",
    target_kind="location",
    guard=_make_expr(
        "c > 1",
        23,
        Position(
            start=1971,
            end=1976,
            line=1,
            column=1,
            end_line=1,
            end_column=6,
            path="/nta/template[1]/transition[3]/label[1]",
        ),
        INVARIANT_TYPE,
        2,
        children=(
            _make_expr(
                "c",
                136,
                Position(
                    start=1971,
                    end=1972,
                    line=1,
                    column=1,
                    end_line=1,
                    end_column=2,
                    path="/nta/template[1]/transition[3]/label[1]",
                ),
                SIMPLE_SYSTEM_CLOCK_TYPE,
                0,
            ),
            _make_expr(
                "1",
                137,
                Position(
                    start=1975,
                    end=1976,
                    line=1,
                    column=5,
                    end_line=1,
                    end_column=6,
                    path="/nta/template[1]/transition[3]/label[1]",
                ),
                INT_TYPE,
                0,
            ),
        ),
    ),
    assign=_make_expr(
        "1",
        137,
        Position(start=1969, end=1970, line=1, column=1, end_line=1, end_column=2, path="/nta/template[1]"),
        INT_TYPE,
        0,
    ),
    sync=EMPTY_EXPRESSION,
    prob=_make_expr(
        "1",
        137,
        Position(start=1969, end=1970, line=1, column=1, end_line=1, end_column=2, path="/nta/template[1]"),
        INT_TYPE,
        0,
    ),
    select_text="{}",
    select_symbols=(),
    select_values=(),
)

SAMPLESMC_BRANCHPOINT = Branchpoint(
    name="_id5",
    index=0,
    position=Position(
        start=4193,
        end=4194,
        line=1,
        column=1,
        end_line=1,
        end_column=2,
        path="/nta/template[1]/branchpoint[1]",
    ),
    symbol=Symbol(
        name="_id5",
        type=BRANCHPOINT_TYPE,
        position=Position(
            start=4193,
            end=4194,
            line=1,
            column=1,
            end_line=1,
            end_column=2,
            path="/nta/template[1]/branchpoint[1]",
        ),
    ),
)

SAMPLESMC_BRANCH_EDGE = Edge(
    index=6,
    control=True,
    action_name="SKIP",
    source_name="_id5",
    source_kind="branchpoint",
    target_name="NOK",
    target_kind="location",
    guard=_make_expr(
        "1",
        137,
        Position(
            start=2156,
            end=2159,
            line=1,
            column=1,
            end_line=1,
            end_column=4,
            path="/nta/template[1]/transition[6]/label[2]",
        ),
        INT_TYPE,
        0,
    ),
    assign=_make_expr(
        "x = 0",
        89,
        Position(
            start=2160,
            end=2163,
            line=1,
            column=1,
            end_line=1,
            end_column=4,
            path="/nta/template[1]/transition[7]/label[1]",
        ),
        SAMPLESMC_CLOCK_TYPE,
        2,
        children=(
            _make_expr(
                "x",
                136,
                Position(
                    start=2160,
                    end=2161,
                    line=1,
                    column=1,
                    end_line=1,
                    end_column=2,
                    path="/nta/template[1]/transition[7]/label[1]",
                ),
                SAMPLESMC_CLOCK_TYPE,
                0,
            ),
            _make_expr(
                "0",
                137,
                Position(
                    start=2162,
                    end=2163,
                    line=1,
                    column=3,
                    end_line=1,
                    end_column=4,
                    path="/nta/template[1]/transition[7]/label[1]",
                ),
                INT_TYPE,
                0,
            ),
        ),
    ),
    sync=EMPTY_EXPRESSION,
    prob=_make_expr(
        "58",
        137,
        Position(
            start=2164,
            end=2166,
            line=1,
            column=1,
            end_line=1,
            end_column=3,
            path="/nta/template[1]/transition[7]/label[2]",
        ),
        INT_TYPE,
        0,
    ),
    select_text="{}",
    select_symbols=(),
    select_values=(),
)

LMAC6_SELECT_SYMBOL = Symbol(
    name="slot",
    type=RANGED_INT_TYPE,
    position=Position(
        start=9367,
        end=9387,
        line=1,
        column=1,
        end_line=1,
        end_column=21,
        path="/nta/template[1]/transition[13]/label[1]",
    ),
)

LMAC6_SELECT_EDGE_SIGNATURE = {
    "index": 12,
    "control": True,
    "action_name": "SKIP",
    "source_name": "choice",
    "source_kind": "location",
    "target_name": "normal",
    "target_kind": "location",
    "guard_text": "!aux_vec[slot] && aux_vec != zero_vec",
    "guard_kind": 10,
    "guard_size": 2,
    "assign_text": "slot_no[id] = slot, aux_vec = zero_vec",
    "assign_kind": 147,
    "assign_size": 2,
    "sync_text": "",
    "sync_kind": -1,
    "sync_size": 0,
    "prob_text": "1",
    "prob_kind": 137,
    "prob_size": 0,
    "select_text": '{(const (range (int) "0" "frame - 1")) slot}',
    "select_symbols": (LMAC6_SELECT_SYMBOL,),
    "select_values": (),
}

HDDI_INPUT_02_PROCESS = Process(
    name="RING",
    index=0,
    position=Position(start=2200, end=2204, line=62, column=8, end_line=62, end_column=12, path=""),
    template_name="RING",
    parameters="",
    arguments="",
    mapping="",
    argument_count=0,
    unbound_count=0,
    restricted_symbols=(),
)
