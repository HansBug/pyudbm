from dataclasses import fields, is_dataclass

import pytest

from pyudbm.binding import (
    Branchpoint,
    Diagnostic,
    Edge,
    Expression,
    FeatureFlags,
    Location,
    MAPPED_FIELDS,
    MAPPED_FIELD_NOTES,
    ModelDocument,
    ParsedQuery,
    ParsedQueryExpectation,
    Position,
    Process,
    Query,
    Symbol,
    Template,
    TypeInfo,
    UNMAPPED_FIELDS,
    UNMAPPED_FIELD_REASONS,
    load_xml,
    load_xta,
    Option,
)

from .utap_phase5_data import (
    HDDI_INPUT_02_PROCESS,
    HDDI_INPUT_02_TA_PATH,
    LMAC6_SELECT_EDGE_SIGNATURE,
    LMAC6_SELECT_SYMBOL,
    LMAC6_XML_PATH,
    MINIMAL_XML_DOCUMENT_PUBLIC,
    MINIMAL_XML_PATH,
    MINIMAL_XTA_DOCUMENT_PUBLIC,
    MINIMAL_XTA_PATH,
    PHASE5_FIELD_MATRIX,
    PHASE5_MAPPED_FIELD_NOTES,
    PHASE5_UNMAPPED_FIELD_REASONS,
    SAMPLESMC_BRANCHPOINT,
    SAMPLESMC_BRANCH_EDGE,
    SAMPLESMC_XML_PATH,
    SIMPLE_SYSTEM_EDGE,
    SIMPLE_SYSTEM_LOCATION,
    SIMPLE_SYSTEM_PROCESS,
    SIMPLE_SYSTEM_XML_PATH,
)


def _document_public_projection(document):
    return {name: getattr(document, name) for name in MAPPED_FIELDS["Document"]}


def _normalize_value(value):
    # UTAP absolute offsets are not stable across repeated parses in the same process,
    # so golden values use only the stable user-facing coordinates.
    if isinstance(value, Position):
        return {
            "line": value.line,
            "column": value.column,
            "end_line": value.end_line,
            "end_column": value.end_column,
            "path": value.path,
        }
    if is_dataclass(value):
        return {field.name: _normalize_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple):
        return tuple(_normalize_value(item) for item in value)
    if isinstance(value, dict):
        return {key: _normalize_value(item) for key, item in value.items()}
    return value


@pytest.mark.unittest
class TestUtapFieldMatrix:
    @pytest.mark.parametrize(
        ("matrix_key", "cls"),
        (
            ("position_t", Position),
            ("type_t", TypeInfo),
            ("symbol_t", Symbol),
            ("expression_t", Expression),
            ("FeatureFlags", FeatureFlags),
            ("Branchpoint", Branchpoint),
            ("Location", Location),
            ("Edge", Edge),
            ("Query", Query),
            ("Option", Option),
            ("expectation_t", ParsedQueryExpectation),
            ("ParsedQuery", ParsedQuery),
            ("Process", Process),
            ("Template", Template),
            ("diagnostic_t", Diagnostic),
        ),
    )
    def test_public_dataclass_field_order_matches_phase5_matrix(self, matrix_key, cls):
        assert tuple(field.name for field in fields(cls)) == PHASE5_FIELD_MATRIX[matrix_key]["mapped"]

    def test_phase5_field_manifests_match_expected_matrix(self):
        assert MAPPED_FIELDS == {name: item["mapped"] for name, item in PHASE5_FIELD_MATRIX.items()}
        assert UNMAPPED_FIELDS == {name: item["unmapped"] for name, item in PHASE5_FIELD_MATRIX.items()}

    def test_phase5_notes_and_unmapped_reasons_are_explicit(self):
        assert MAPPED_FIELD_NOTES == PHASE5_MAPPED_FIELD_NOTES
        assert UNMAPPED_FIELD_REASONS == PHASE5_UNMAPPED_FIELD_REASONS

    @pytest.mark.parametrize(("path", "loader", "expected"), ((MINIMAL_XML_PATH, load_xml, MINIMAL_XML_DOCUMENT_PUBLIC),))
    def test_minimal_xml_document_public_projection_is_exact(self, path, loader, expected):
        document = loader(path)

        assert type(document) is ModelDocument
        assert tuple(name for name in document.__dict__ if not name.startswith("_")) == PHASE5_FIELD_MATRIX["Document"]["mapped"]
        assert _normalize_value(_document_public_projection(document)) == _normalize_value(expected)

    def test_minimal_xta_document_public_projection_is_exact(self):
        document = load_xta(MINIMAL_XTA_PATH)

        assert type(document) is ModelDocument
        assert tuple(name for name in document.__dict__ if not name.startswith("_")) == PHASE5_FIELD_MATRIX["Document"]["mapped"]
        assert _normalize_value(_document_public_projection(document)) == _normalize_value(MINIMAL_XTA_DOCUMENT_PUBLIC)

    def test_simple_system_process_is_exact(self):
        document = load_xml(SIMPLE_SYSTEM_XML_PATH)

        assert _normalize_value(document.processes[0]) == _normalize_value(SIMPLE_SYSTEM_PROCESS)

    def test_simple_system_location_is_exact(self):
        document = load_xml(SIMPLE_SYSTEM_XML_PATH)

        assert _normalize_value(document.templates[0].locations[2]) == _normalize_value(SIMPLE_SYSTEM_LOCATION)

    def test_simple_system_edge_is_exact(self):
        document = load_xml(SIMPLE_SYSTEM_XML_PATH)

        assert _normalize_value(document.templates[0].edges[2]) == _normalize_value(SIMPLE_SYSTEM_EDGE)

    def test_simple_system_representative_typeinfo_values_are_exact(self):
        document = load_xml(SIMPLE_SYSTEM_XML_PATH)
        location = document.templates[0].locations[2]

        assert _normalize_value(location.invariant.children[1].children[0].type) == _normalize_value(
            SIMPLE_SYSTEM_LOCATION.invariant.children[1].children[0].type
        )
        assert _normalize_value(location.invariant.children[1].children[1].type) == _normalize_value(
            SIMPLE_SYSTEM_LOCATION.invariant.children[1].children[1].type
        )
        assert _normalize_value(location.symbol.type) == _normalize_value(SIMPLE_SYSTEM_LOCATION.symbol.type)

    def test_samplesmc_branchpoint_is_exact(self):
        document = load_xml(SAMPLESMC_XML_PATH)

        assert _normalize_value(document.templates[0].branchpoints[0]) == _normalize_value(SAMPLESMC_BRANCHPOINT)

    def test_samplesmc_branch_edge_is_exact(self):
        document = load_xml(SAMPLESMC_XML_PATH)
        branch_edge = next(edge for edge in document.templates[0].edges if edge.source_kind == "branchpoint")

        assert _normalize_value(branch_edge) == _normalize_value(SAMPLESMC_BRANCH_EDGE)

    def test_lmac6_select_symbol_and_edge_signature_are_exact(self):
        document = load_xml(LMAC6_XML_PATH)
        select_edge = next(edge for template in document.templates for edge in template.edges if edge.select_symbols)

        assert _normalize_value(select_edge.select_symbols[0]) == _normalize_value(LMAC6_SELECT_SYMBOL)
        assert _normalize_value(
            {
            "index": select_edge.index,
            "control": select_edge.control,
            "action_name": select_edge.action_name,
            "source_name": select_edge.source_name,
            "source_kind": select_edge.source_kind,
            "target_name": select_edge.target_name,
            "target_kind": select_edge.target_kind,
            "guard_text": select_edge.guard.text,
            "guard_kind": select_edge.guard.kind,
            "guard_size": select_edge.guard.size,
            "assign_text": select_edge.assign.text,
            "assign_kind": select_edge.assign.kind,
            "assign_size": select_edge.assign.size,
            "sync_text": select_edge.sync.text,
            "sync_kind": select_edge.sync.kind,
            "sync_size": select_edge.sync.size,
            "prob_text": select_edge.prob.text,
            "prob_kind": select_edge.prob.kind,
            "prob_size": select_edge.prob.size,
            "select_text": select_edge.select_text,
            "select_symbols": select_edge.select_symbols,
            "select_values": select_edge.select_values,
            }
        ) == _normalize_value(LMAC6_SELECT_EDGE_SIGNATURE)

    def test_hddi_legacy_text_process_is_exact(self):
        document = load_xta(HDDI_INPUT_02_TA_PATH, newxta=False)

        assert _normalize_value(document.processes[0]) == _normalize_value(HDDI_INPUT_02_PROCESS)
