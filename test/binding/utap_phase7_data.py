PHASE7_MINIMAL_XTA = """clock x;
process P() {
state S;
init S;
}
P1 = P();
system P1;
"""


BUILTIN_DECLARATION_TOKENS = (
    "const int INT32_MAX",
    "typedef int[INT32_MIN,INT32_MAX] int32_t;",
)


PHASE7_PARSED_QUERY_EXPECTATION_CASES = (
    (
        "status",
        "A[] not deadlock\n/* EXPECT:T,10MS,5KB */\n",
        {
            "result_kind": "status",
            "status": "DONE_TRUE",
            "value": None,
            "time_ms": 10,
            "mem_kib": 5,
        },
    ),
    (
        "numeric",
        "A[] not deadlock\n/* EXPECT:1.5,2S,3MB */\n",
        {
            "result_kind": "numeric",
            "status": None,
            "value": 1.5,
            "time_ms": 2000,
            "mem_kib": 3072,
        },
    ),
)


PHASE7_SERIALIZED_EXPECTATION_CASES = (
    (
        "resources",
        {
            "document_options": (("trace", "short"),),
            "query_options": (("--discretization", "0.5"),),
            "formula": "A[] not deadlock",
            "comment": "resource expectation",
            "expectation": {
                "value_type": "Probability",
                "status": "True",
                "value": "0.95",
                "resources": (
                    ("time", "100", "ms"),
                    ("memory", "2048", None),
                ),
            },
            "xml_fragments": (
                '<option key="trace" value="short"/>',
                '<option key="--discretization" value="0.5"/>',
                '<expect outcome="success" type="probability" value="0.95">',
                '<resource type="time" value="100" unit="ms"/>',
                '<resource type="memory" value="2048"/>',
                "</expect>",
            ),
            "reloaded_expectation": {
                "value_type": "Probability",
                "status": "True",
                "value": "0.95",
            },
        },
    ),
    (
        "attributes_only",
        {
            "document_options": (),
            "query_options": (),
            "formula": "A[] not deadlock",
            "comment": "attribute expectation",
            "expectation": {
                "value_type": "NumericValue",
                "status": "False",
                "value": "42",
                "resources": (),
            },
            "xml_fragments": (
                '<expect outcome="failure" type="value" value="42"/>',
            ),
            "reloaded_expectation": None,
        },
    ),
    (
        "empty_expect",
        {
            "document_options": (),
            "query_options": (),
            "formula": "A[] not deadlock",
            "comment": "empty expectation",
            "expectation": {
                "value_type": "CustomValue",
                "status": "Unknownish",
                "value": "",
                "resources": (),
            },
            "xml_fragments": (
                "<expect/>",
            ),
            "reloaded_expectation": None,
        },
    ),
)
