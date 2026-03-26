import importlib

import pytest

import pyudbm.binding as binding_module
import pyudbm.binding.utap as utap_module
from pyudbm.binding import (
    Branchpoint,
    Diagnostic,
    MAPPED_FIELDS,
    MAPPED_FIELD_NOTES,
    ModelDocument,
    ParsedQuery,
    ParsedQueryExpectation,
    UNMAPPED_FIELDS,
    UNMAPPED_FIELD_REASONS,
    load_query,
    load_xml,
    load_xta,
    loads_query,
    loads_xml,
    loads_xta,
    parse_query,
)

from .utap_phase0_data import (
    DUPLICATE_LOCATION_ID_WARNING_XML,
    INVALID_XTA_UNKNOWN_PROCESS,
    MINIMAL_XML_PATH,
    MINIMAL_XTA_PATH,
    OFFICIAL_TEXTUAL_MODEL_CASES,
    OFFICIAL_XML_MODEL_CASES,
    UTAP_SIMPLE_SYSTEM_PATH,
)


def _rewrite_newlines(text, newline):
    return text.replace("\n", newline)


def _write_text_file(path, text):
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(text)


def _minimal_textual_snapshot(document):
    template = document.templates[0]
    process = document.processes[0]
    location = template.locations[0]
    return {
        "errors": tuple(item.message for item in document.errors),
        "warnings": tuple(item.message for item in document.warnings),
        "templates": tuple(item.name for item in document.templates),
        "processes": tuple(item.name for item in document.processes),
        "template_name": template.name,
        "template_parameter": template.parameter,
        "template_declaration": template.declaration,
        "template_init_name": template.init_name,
        "template_is_ta": template.is_ta,
        "template_is_instantiated": template.is_instantiated,
        "template_dynamic": template.dynamic,
        "template_is_defined": template.is_defined,
        "process_template_name": process.template_name,
        "process_parameters": process.parameters,
        "process_arguments": process.arguments,
        "process_mapping": process.mapping,
        "process_argument_count": process.argument_count,
        "process_unbound_count": process.unbound_count,
        "location_names": tuple(item.name for item in template.locations),
        "edge_count": len(template.edges),
        "location_path": location.position.path,
        "location_line": location.position.line,
        "location_column": location.position.column,
    }


@pytest.mark.unittest
class TestUtapApi:
    def test_binding_exports_public_utap_surface(self):
        loaded_module = importlib.import_module("pyudbm.binding.utap")

        assert loaded_module is utap_module
        assert binding_module.ModelDocument is ModelDocument
        assert binding_module.load_xml is load_xml
        assert binding_module.loads_xml is loads_xml
        assert binding_module.load_xta is load_xta
        assert binding_module.loads_xta is loads_xta
        assert binding_module.load_query is load_query
        assert binding_module.loads_query is loads_query
        assert binding_module.parse_query is parse_query
        assert binding_module.Branchpoint is Branchpoint
        assert binding_module.ParsedQuery is ParsedQuery
        assert binding_module.ParsedQueryExpectation is ParsedQueryExpectation
        assert binding_module.MAPPED_FIELDS is MAPPED_FIELDS
        assert binding_module.MAPPED_FIELD_NOTES is MAPPED_FIELD_NOTES
        assert binding_module.UNMAPPED_FIELDS is UNMAPPED_FIELDS
        assert binding_module.UNMAPPED_FIELD_REASONS is UNMAPPED_FIELD_REASONS

    def test_model_document_flat_read_only_helpers_are_properties(self):
        assert type(ModelDocument.__dict__["global_declarations"]) is property
        assert type(ModelDocument.__dict__["before_update_text"]) is property
        assert type(ModelDocument.__dict__["after_update_text"]) is property
        assert type(ModelDocument.__dict__["channel_priority_texts"]) is property
        assert type(ModelDocument.__dict__["global_clock_names"]) is property
        assert type(ModelDocument.__dict__["template_clock_names"]) is property

    def test_model_document_derived_helpers_remain_methods(self):
        assert type(ModelDocument.__dict__["dumps"]) is not property
        assert type(ModelDocument.__dict__["to_xml"]) is not property
        assert type(ModelDocument.__dict__["feature_summary"]) is not property
        assert type(ModelDocument.__dict__["capability_summary"]) is not property
        assert type(ModelDocument.__dict__["pretty"]) is not property

    @pytest.mark.parametrize(
        ("model_path", "newxta"),
        OFFICIAL_XML_MODEL_CASES,
        ids=[str(path) for path, _ in OFFICIAL_XML_MODEL_CASES],
    )
    def test_official_xml_models_parse_via_public_api(self, model_path, newxta):
        document = load_xml(model_path, newxta=newxta if newxta is not None else True)

        assert type(document) is ModelDocument
        assert document.errors == ()
        assert type(document.warnings) is tuple
        assert all(type(item) is Diagnostic for item in document.warnings)

    @pytest.mark.parametrize(
        ("model_path", "newxta"),
        OFFICIAL_TEXTUAL_MODEL_CASES,
        ids=[str(path) for path, _ in OFFICIAL_TEXTUAL_MODEL_CASES],
    )
    def test_official_textual_models_parse_via_public_api(self, model_path, newxta):
        document = load_xta(model_path, newxta=newxta if newxta is not None else True)

        assert type(document) is ModelDocument
        assert document.errors == ()
        assert type(document.warnings) is tuple
        assert all(type(item) is Diagnostic for item in document.warnings)

    def test_minimal_xml_document_structure(self):
        document = load_xml(MINIMAL_XML_PATH)
        template = document.templates[0]
        location = template.locations[0]

        assert repr(document) == "<ModelDocument templates=1 processes=1 queries=0 errors=0 warnings=0>"
        assert len(document.templates) == 1
        assert len(document.processes) == 1
        assert len(document.queries) == 0
        assert tuple(item.name for item in document.templates) == ("P",)
        assert tuple(item.name for item in document.processes) == ("P1",)
        assert tuple(item.name for item in template.locations) == ("Init",)
        assert len(template.edges) == 0
        assert template.parameter == ""
        assert template.declaration == ""
        assert template.init_name == "Init"
        assert template.is_ta is True
        assert template.is_instantiated is True
        assert template.dynamic is False
        assert template.is_defined is False
        assert location.index == 0
        assert location.is_urgent is False
        assert location.is_committed is False
        assert location.invariant.is_empty is True
        assert location.exp_rate.is_empty is True
        assert location.cost_rate.is_empty is True
        assert document.features.has_priority_declaration is False
        assert document.features.has_strict_invariants is False
        assert document.features.has_stop_watch is False
        assert document.features.has_strict_lower_bound_on_controllable_edges is False
        assert document.features.has_clock_guard_recv_broadcast is False
        assert document.features.has_urgent_transition is False
        assert document.features.has_dynamic_templates is False
        assert document.features.all_broadcast is True
        assert document.features.sync_used == 0
        assert document.features.supports_symbolic is True
        assert document.features.supports_stochastic is True
        assert document.features.supports_concrete is True

    def test_minimal_textual_document_structure(self):
        document = load_xta(MINIMAL_XTA_PATH)
        template = document.templates[0]
        location = template.locations[0]
        process = document.processes[0]

        assert repr(document) == "<ModelDocument templates=1 processes=1 queries=0 errors=0 warnings=0>"
        assert len(document.templates) == 1
        assert len(document.processes) == 1
        assert tuple(item.name for item in document.templates) == ("P",)
        assert tuple(item.name for item in document.processes) == ("P1",)
        assert process.template_name == "P"
        assert process.parameters == ""
        assert process.arguments == ""
        assert process.mapping == ""
        assert process.argument_count == 0
        assert process.unbound_count == 0
        assert tuple(item.name for item in template.locations) == ("S",)
        assert len(template.edges) == 0
        assert location.position.path == ""
        assert location.position.line == 3
        assert location.position.column == 7

    @pytest.mark.parametrize(
        ("newline_name", "newline"),
        (("crlf", "\r\n"), ("cr", "\r")),
    )
    def test_textual_entrypoints_normalize_non_lf_newlines_for_buffer_and_file_inputs(self, tmp_path, newline_name, newline):
        baseline = _minimal_textual_snapshot(load_xta(MINIMAL_XTA_PATH))
        xta_text = MINIMAL_XTA_PATH.read_text(encoding="utf-8")
        variant_text = _rewrite_newlines(xta_text, newline)
        variant_path = tmp_path / f"line_endings_{newline_name}.xta"

        _write_text_file(variant_path, variant_text)

        assert _minimal_textual_snapshot(loads_xta(variant_text)) == baseline
        assert _minimal_textual_snapshot(load_xta(variant_path)) == baseline

    def test_simple_system_exposes_model_structure_expression_type_and_symbol_fields(self):
        document = load_xml(UTAP_SIMPLE_SYSTEM_PATH)
        template = document.templates[0]
        invariant_location = template.locations[2]
        invariant = invariant_location.invariant
        comparison = invariant.children[1]
        first_child = comparison.children[0]
        second_child = comparison.children[1]

        assert len(document.templates) == 1
        assert len(document.processes) == 2
        assert len(document.queries) == 1
        assert tuple(item.name for item in document.processes) == ("Process", "Process2")
        assert tuple(item.name for item in template.locations) == ("L3", "L2", "First")
        assert tuple((edge.source_name, edge.target_name) for edge in template.edges) == (
            ("L3", "First"),
            ("L2", "L3"),
            ("First", "L2"),
        )
        assert tuple(query.formula for query in document.queries) == ("",)
        assert template.init_name == "First"
        assert invariant.text == "1 && c < 2"
        assert invariant.kind == 10
        assert invariant.size == 2
        assert invariant.is_empty is False
        assert comparison.text == "c < 2"
        assert comparison.kind == 18
        assert comparison.size == 2
        assert first_child.text == "c"
        assert first_child.size == 0
        assert first_child.is_empty is False
        assert first_child.type.is_clock is True
        assert first_child.type.text == "clock"
        assert second_child.text == "2"
        assert second_child.size == 0
        assert second_child.type.is_integer is True
        assert second_child.type.text == "int"
        assert invariant_location.symbol.name == "First"
        assert invariant_location.symbol.type.text == "location"
        assert invariant_location.position.path == "/nta/template[1]/location[3]"
        assert invariant_location.position.line == 1
        assert invariant_location.position.column == 1
        assert template.edges[2].guard.text == "c > 1"
        assert template.edges[2].guard.kind == 23
        assert template.edges[2].sync.is_empty is True
        assert template.edges[2].assign.text == "1"
        assert template.edges[2].assign.kind == 137
        assert template.edges[2].assign.is_empty is False
        assert template.edges[2].prob.text == "1"
        assert template.edges[2].prob.kind == 137
        assert template.edges[2].prob.is_empty is False
        assert template.edges[2].select_text == "{}"
        assert template.edges[2].select_symbols == ()

    def test_diagnostics_are_exposed_structurally_for_errors(self):
        document = loads_xta(INVALID_XTA_UNKNOWN_PROCESS, strict=False)
        error = document.errors[0]

        assert len(document.errors) == 1
        assert len(document.warnings) == 0
        assert error.message == "$No_such_process: Missing"
        assert error.context == ""
        assert error.path == ""
        assert error.line == 6
        assert error.column == 8
        assert error.end_line == 6
        assert error.end_column == 15
        assert error.position.line == 6
        assert error.position.column == 8
        assert error.position.end_line == 6
        assert error.position.end_column == 15
        assert error.position.path == ""

    def test_diagnostics_are_exposed_structurally_for_warnings(self):
        document = loads_xml(DUPLICATE_LOCATION_ID_WARNING_XML)
        warning = document.warnings[0]

        assert len(document.errors) == 0
        assert len(document.warnings) == 1
        assert warning.message == "$Non-unique_id_attribute_value: dup"
        assert warning.context == ""
        assert warning.path == "/nta/template[1]/location[2]/name"
        assert warning.line == 1
        assert warning.column == 1
        assert warning.end_line == 1
        assert warning.end_column == 3
        assert warning.position.path == "/nta/template[1]/location[2]/name"

    def test_field_mapping_manifests_are_exposed(self):
        assert MAPPED_FIELDS["Document"] == (
            "templates",
            "processes",
            "queries",
            "options",
            "features",
            "errors",
            "warnings",
            "modified",
        )
        assert MAPPED_FIELDS["Template"] == (
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
        )
        assert MAPPED_FIELDS["Branchpoint"] == ("name", "index", "position", "symbol")
        assert MAPPED_FIELDS["expression_t"] == ("text", "kind", "position", "type", "size", "children", "is_empty")
        assert UNMAPPED_FIELDS["Document"] == ("globals", "before_update", "after_update", "chan_priorities", "strings")
        assert UNMAPPED_FIELDS["Edge"] == ()
        assert MAPPED_FIELD_NOTES["Template"]["declaration"] == (
            "Conservative first-phase field. The current binding keeps this empty instead of calling unstable "
            "upstream pretty-printers on every template."
        )
        assert UNMAPPED_FIELD_REASONS["type_t"]["children"] == (
            "Deferred until recursive type-shape wrappers are stabilized for records, arrays, and process fields."
        )
