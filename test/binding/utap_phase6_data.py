from .utap_phase0_data import MINIMAL_XML_PATH, UTAP_SIMPLE_SYSTEM_PATH


MINIMAL_FEATURE_SUMMARY = {
    "has_priority_declaration": False,
    "has_strict_invariants": False,
    "has_stop_watch": False,
    "has_strict_lower_bound_on_controllable_edges": False,
    "has_clock_guard_recv_broadcast": False,
    "has_urgent_transition": False,
    "has_dynamic_templates": False,
    "all_broadcast": True,
    "sync_used": 0,
    "supports_symbolic": True,
    "supports_stochastic": True,
    "supports_concrete": True,
}

SIMPLE_FEATURE_SUMMARY = {
    "has_priority_declaration": False,
    "has_strict_invariants": True,
    "has_stop_watch": False,
    "has_strict_lower_bound_on_controllable_edges": True,
    "has_clock_guard_recv_broadcast": False,
    "has_urgent_transition": False,
    "has_dynamic_templates": False,
    "all_broadcast": True,
    "sync_used": 0,
    "supports_symbolic": True,
    "supports_stochastic": True,
    "supports_concrete": True,
}

COMMON_CAPABILITY_SUMMARY = {
    "supports_symbolic": True,
    "supports_stochastic": True,
    "supports_concrete": True,
}

MINIMAL_PRETTY_PAYLOAD = {
    "after_update": "",
    "before_update": "",
    "capabilities": COMMON_CAPABILITY_SUMMARY,
    "channel_priorities": [],
    "features": MINIMAL_FEATURE_SUMMARY,
    "global_clock_names": ["x"],
    "global_declarations": "// variables\nclock x;\n",
    "processes": [
        {
            "arguments": "",
            "mapping": "",
            "name": "P1",
            "parameters": "",
            "template_name": "P",
        }
    ],
    "queries": [],
    "template_clock_names": {"P": []},
    "templates": [
        {
            "branchpoint_count": 0,
            "dynamic": False,
            "edge_count": 0,
            "init_name": "Init",
            "is_defined": False,
            "is_instantiated": True,
            "is_ta": True,
            "location_count": 1,
            "mode": "",
            "name": "P",
            "type": "",
        }
    ],
}

SIMPLE_PRETTY_PAYLOAD = {
    "after_update": "",
    "before_update": "",
    "capabilities": COMMON_CAPABILITY_SUMMARY,
    "channel_priorities": [],
    "features": SIMPLE_FEATURE_SUMMARY,
    "global_clock_names": ["c"],
    "global_declarations": "// variables\nclock c;\n",
    "processes": [
        {
            "arguments": "",
            "mapping": "",
            "name": "Process",
            "parameters": "",
            "template_name": "Template",
        },
        {
            "arguments": "",
            "mapping": "",
            "name": "Process2",
            "parameters": "",
            "template_name": "Template",
        },
    ],
    "queries": [
        {
            "comment": "",
            "formula": "",
            "location": "/nta/queries/query[1]/formula",
            "options": [],
        }
    ],
    "template_clock_names": {"Template": []},
    "templates": [
        {
            "branchpoint_count": 0,
            "dynamic": False,
            "edge_count": 3,
            "init_name": "First",
            "is_defined": False,
            "is_instantiated": True,
            "is_ta": True,
            "location_count": 3,
            "mode": "",
            "name": "Template",
            "type": "",
        }
    ],
}

PHASE6_ROUNDTRIP_CASES = (
    (
        MINIMAL_XML_PATH,
        {
            "template_names": ("P",),
            "process_names": ("P1",),
            "query_formulas": (),
            "location_invariants": ("",),
            "global_declarations": "// variables\nclock x;\n",
            "global_clock_names": ("x",),
            "template_clock_names": {"P": ()},
            "feature_summary": MINIMAL_FEATURE_SUMMARY,
            "capability_summary": COMMON_CAPABILITY_SUMMARY,
            "pretty_payload": MINIMAL_PRETTY_PAYLOAD,
            "dump_root_tags": ["declaration", "template", "system"],
        },
    ),
    (
        UTAP_SIMPLE_SYSTEM_PATH,
        {
            "template_names": ("Template",),
            "process_names": ("Process", "Process2"),
            "query_formulas": ("",),
            "location_invariants": ("", "", "1 && c < 2"),
            "global_declarations": "// variables\nclock c;\n",
            "global_clock_names": ("c",),
            "template_clock_names": {"Template": ()},
            "feature_summary": SIMPLE_FEATURE_SUMMARY,
            "capability_summary": COMMON_CAPABILITY_SUMMARY,
            "pretty_payload": SIMPLE_PRETTY_PAYLOAD,
            "dump_root_tags": ["declaration", "template", "system", "queries"],
        },
    ),
)

DIRECT_WRITE_ROOT_TAGS = ["declaration", "template", "system"]
