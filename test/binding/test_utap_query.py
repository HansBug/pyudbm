import json

import pytest

from pyudbm.binding import (
    ModelDocument,
    ParsedQuery,
    load_query,
    load_xml,
    load_xta,
    loads_query,
    parse_query,
)

from .utap_phase4_data import (
    LINE_ENDING_SENSITIVE_PROPERTY_CONTEXT,
    LINE_ENDING_SENSITIVE_PROPERTY_QUERY,
    OFFICIAL_QUERY_CASES,
    OFFICIAL_QUERY_EXPECTATIONS_PATH,
    REPRESENTATIVE_MIXED_CONTEXT,
    REPRESENTATIVE_MIXED_QUERY,
    REPRESENTATIVE_PROPERTY_CONTEXT,
    REPRESENTATIVE_PROPERTY_QUERY,
    REPRESENTATIVE_TIGA_CONTEXT,
    REPRESENTATIVE_TIGA_QUERY,
    query_expectation,
    resolve_official_path,
)


def _rewrite_newlines(text, newline):
    return text.replace("\n", newline)


def _write_text_file(path, text):
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(text)


def _load_context_document(context_relative_path, newxta):
    context_path = resolve_official_path(context_relative_path)
    if context_path.suffix == ".xml":
        return load_xml(context_path, newxta=True if newxta is None else newxta)
    return load_xta(context_path, newxta=True if newxta is None else newxta)


def _simplify_query(query):
    return {
        "line": query.line,
        "no": query.no,
        "builder": query.builder,
        "quantifier": query.quantifier,
        "text": query.text,
        "expression_kind": query.expression.kind,
        "expression_size": query.expression.size,
        "expression_line": query.expression.position.line,
        "expression_column": query.expression.position.column,
        "is_smc": query.is_smc,
        "declaration": query.declaration,
        "result_type": query.result_type,
        "options": [{"name": option.name, "value": option.value} for option in query.options],
        "expectation": None
        if query.expectation is None
        else {
            "result_kind": query.expectation.result_kind,
            "status": query.expectation.status,
            "value": query.expectation.value,
            "time_ms": query.expectation.time_ms,
            "mem_kib": query.expectation.mem_kib,
        },
    }


@pytest.mark.unittest
class TestUtapQueryApi:
    def test_query_expectation_fixture_is_present(self):
        payload = json.loads(OFFICIAL_QUERY_EXPECTATIONS_PATH.read_text(encoding="utf-8"))

        assert OFFICIAL_QUERY_EXPECTATIONS_PATH.is_file()
        assert payload["version"] == 1
        assert len(payload["files"]) == 47

    @pytest.mark.parametrize(
        ("query_relative_path", "context_relative_path", "context_newxta"),
        OFFICIAL_QUERY_CASES,
        ids=[query_relative_path for query_relative_path, _, _ in OFFICIAL_QUERY_CASES],
    )
    def test_official_query_files_parse_via_public_api(self, query_relative_path, context_relative_path, context_newxta):
        expected = query_expectation(query_relative_path)
        context_document = _load_context_document(context_relative_path, context_newxta)
        from_module = load_query(resolve_official_path(query_relative_path), context_document)
        from_method = context_document.load_query(resolve_official_path(query_relative_path))

        assert type(context_document) is ModelDocument
        assert len(from_module) == len(expected["queries"])
        assert len(from_method) == len(expected["queries"])
        assert all(type(item) is ParsedQuery for item in from_module)
        assert all(type(item) is ParsedQuery for item in from_method)
        assert [_simplify_query(item) for item in from_module] == expected["queries"]
        assert [_simplify_query(item) for item in from_method] == expected["queries"]

    def test_property_query_supports_auto_property_and_tiga_builder_paths(self):
        expected = query_expectation(REPRESENTATIVE_PROPERTY_QUERY)["queries"]
        context_document = _load_context_document(REPRESENTATIVE_PROPERTY_CONTEXT, True)
        auto_queries = load_query(resolve_official_path(REPRESENTATIVE_PROPERTY_QUERY), context_document, builder="auto")
        property_queries = load_query(resolve_official_path(REPRESENTATIVE_PROPERTY_QUERY), context_document, builder="property")
        tiga_queries = load_query(resolve_official_path(REPRESENTATIVE_PROPERTY_QUERY), context_document, builder="tiga")
        expected_tiga = [{**item, "builder": "tiga"} for item in expected]

        assert [_simplify_query(item) for item in auto_queries] == expected
        assert [_simplify_query(item) for item in property_queries] == expected
        assert [_simplify_query(item) for item in tiga_queries] == expected_tiga

    def test_tiga_query_requires_tiga_builder_or_auto(self):
        expected = query_expectation(REPRESENTATIVE_TIGA_QUERY)["queries"]
        context_document = _load_context_document(REPRESENTATIVE_TIGA_CONTEXT, True)
        auto_queries = load_query(resolve_official_path(REPRESENTATIVE_TIGA_QUERY), context_document, builder="auto")
        tiga_queries = load_query(resolve_official_path(REPRESENTATIVE_TIGA_QUERY), context_document, builder="tiga")

        assert [_simplify_query(item) for item in auto_queries] == expected
        assert [_simplify_query(item) for item in tiga_queries] == expected

        with pytest.raises(RuntimeError) as property_error:
            load_query(resolve_official_path(REPRESENTATIVE_TIGA_QUERY), context_document, builder="property")

        assert property_error.value.args == ("query parse failed with property builder: $Invalid_property_type",)

    def test_mixed_query_file_routes_auto_to_tiga_and_rejects_property_builder(self):
        expected = query_expectation(REPRESENTATIVE_MIXED_QUERY)["queries"]
        context_document = _load_context_document(REPRESENTATIVE_MIXED_CONTEXT, True)
        auto_queries = load_query(resolve_official_path(REPRESENTATIVE_MIXED_QUERY), context_document, builder="auto")
        tiga_queries = load_query(resolve_official_path(REPRESENTATIVE_MIXED_QUERY), context_document, builder="tiga")

        assert [_simplify_query(item) for item in auto_queries] == expected
        assert [_simplify_query(item) for item in tiga_queries] == expected

        with pytest.raises(RuntimeError) as property_error:
            load_query(resolve_official_path(REPRESENTATIVE_MIXED_QUERY), context_document, builder="property")

        assert property_error.value.args == ("query parse failed with property builder: $Invalid_property_type",)

    def test_query_text_entrypoints_support_property_and_tiga_text_inputs(self):
        property_context = _load_context_document(REPRESENTATIVE_PROPERTY_CONTEXT, True)
        tiga_context = _load_context_document(REPRESENTATIVE_TIGA_CONTEXT, True)

        property_from_loads = loads_query("A[] not deadlock", property_context, builder="property")
        property_from_parse = parse_query("A[] not deadlock", property_context, builder="property")
        property_from_method = property_context.loads_query("A[] not deadlock", builder="property")
        tiga_from_loads = loads_query("control: A<> Main.goal", tiga_context, builder="tiga")
        tiga_from_parse = parse_query("control: A<> Main.goal", tiga_context, builder="tiga")
        tiga_from_method = tiga_context.parse_query("control: A<> Main.goal", builder="tiga")

        assert [_simplify_query(item) for item in property_from_loads] == [
            {
                "line": 1,
                "no": 0,
                "builder": "property",
                "quantifier": "AG",
                "text": "A[] !deadlock",
                "expression_kind": 103,
                "expression_size": 1,
                "expression_line": 1,
                "expression_column": 1,
                "is_smc": False,
                "declaration": "",
                "result_type": "None",
                "options": [],
                "expectation": None,
            }
        ]
        assert [_simplify_query(item) for item in property_from_parse] == [_simplify_query(item) for item in property_from_loads]
        assert [_simplify_query(item) for item in property_from_method] == [_simplify_query(item) for item in property_from_loads]
        assert [_simplify_query(item) for item in tiga_from_loads] == [
            {
                "line": 1,
                "no": 0,
                "builder": "tiga",
                "quantifier": "control_AF",
                "text": "A<> Main.goal",
                "expression_kind": 102,
                "expression_size": 1,
                "expression_line": 1,
                "expression_column": 10,
                "is_smc": False,
                "declaration": "",
                "result_type": "ZoneStrategy",
                "options": [],
                "expectation": None,
            }
        ]
        assert [_simplify_query(item) for item in tiga_from_parse] == [_simplify_query(item) for item in tiga_from_loads]
        assert [_simplify_query(item) for item in tiga_from_method] == [_simplify_query(item) for item in tiga_from_loads]

    @pytest.mark.parametrize(
        ("newline_name", "newline"),
        (("crlf", "\r\n"), ("cr", "\r")),
    )
    def test_query_entrypoints_normalize_non_lf_newlines_for_buffer_and_file_inputs(self, tmp_path, newline_name, newline):
        expected = query_expectation(LINE_ENDING_SENSITIVE_PROPERTY_QUERY)["queries"]
        context_document = _load_context_document(LINE_ENDING_SENSITIVE_PROPERTY_CONTEXT, False)
        query_text = resolve_official_path(LINE_ENDING_SENSITIVE_PROPERTY_QUERY).read_text(encoding="utf-8")
        variant_text = _rewrite_newlines(query_text, newline)
        variant_path = tmp_path / f"line_endings_{newline_name}.q"

        _write_text_file(variant_path, variant_text)

        assert [_simplify_query(item) for item in loads_query(variant_text, context_document, builder="property")] == expected
        assert [_simplify_query(item) for item in parse_query(variant_text, context_document, builder="property")] == expected
        assert [_simplify_query(item) for item in context_document.loads_query(variant_text, builder="property")] == expected
        assert [_simplify_query(item) for item in context_document.parse_query(variant_text, builder="property")] == expected
        assert [_simplify_query(item) for item in load_query(variant_path, context_document, builder="property")] == expected
        assert [_simplify_query(item) for item in context_document.load_query(variant_path, builder="property")] == expected

    def test_query_entrypoints_reject_invalid_builder_and_invalid_document_type(self):
        context_document = _load_context_document(REPRESENTATIVE_PROPERTY_CONTEXT, True)

        with pytest.raises(ValueError) as invalid_builder:
            load_query(resolve_official_path(REPRESENTATIVE_PROPERTY_QUERY), context_document, builder="missing")
        with pytest.raises(TypeError) as invalid_document:
            parse_query("A[] not deadlock", object(), builder="property")

        assert invalid_builder.value.args == ("Unknown query builder: missing",)
        assert invalid_document.value.args == ("document must be a ModelDocument",)

    def test_query_objects_expose_public_dataclass_fields(self):
        context_document = _load_context_document(REPRESENTATIVE_PROPERTY_CONTEXT, True)
        query = parse_query("A[] not deadlock", context_document, builder="property")[0]

        assert type(query) is ParsedQuery
        assert query.line == 1
        assert query.no == 0
        assert query.builder == "property"
        assert query.quantifier == "AG"
        assert query.text == "A[] !deadlock"
        assert query.expression.text == "A[] !deadlock"
        assert query.expression.kind == 103
        assert query.expression.size == 1
        assert query.expression.position.line == 1
        assert query.expression.position.column == 1
        assert query.is_smc is False
        assert query.declaration == ""
        assert query.result_type == "None"
        assert query.options == ()
        assert query.expectation is None
