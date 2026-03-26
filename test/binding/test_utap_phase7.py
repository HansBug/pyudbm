from pathlib import Path

import pytest

from pyudbm.binding import (
    Expectation,
    Option,
    Query,
    Resource,
    builtin_declarations,
    load_query,
    loads_query,
    loads_xml,
    loads_xta,
    parse_query,
)

from .utap_phase7_data import (
    BUILTIN_DECLARATION_TOKENS,
    PHASE7_MINIMAL_XTA,
    PHASE7_PARSED_QUERY_EXPECTATION_CASES,
    PHASE7_SERIALIZED_EXPECTATION_CASES,
)


def _load_minimal_document():
    return loads_xta(PHASE7_MINIMAL_XTA)


def _dump_parsed_expectation(expectation):
    return {
        "result_kind": expectation.result_kind,
        "status": expectation.status,
        "value": expectation.value,
        "time_ms": expectation.time_ms,
        "mem_kib": expectation.mem_kib,
    }


@pytest.mark.unittest
class TestUtapPhase7:
    def test_builtin_declarations_are_available_via_public_api(self):
        declarations = builtin_declarations()

        assert type(declarations) is str
        assert declarations
        for token in BUILTIN_DECLARATION_TOKENS:
            assert token in declarations

    @pytest.mark.parametrize(
        ("name", "query_text", "expected"),
        PHASE7_PARSED_QUERY_EXPECTATION_CASES,
        ids=[name for name, _, _ in PHASE7_PARSED_QUERY_EXPECTATION_CASES],
    )
    def test_public_query_entrypoints_preserve_parsed_expectations(self, name, query_text, expected, tmp_path):
        document = _load_minimal_document()
        query_path = tmp_path / f"{name}.q"
        query_path.write_text(query_text, encoding="utf-8")

        from_module_load = load_query(query_path, document, builder="property")
        from_module_loads = loads_query(query_text, document, builder="property")
        from_module_parse = parse_query(query_text, document, builder="property")
        from_method_load = document.load_query(query_path, builder="property")
        from_method_loads = document.loads_query(query_text, builder="property")
        from_method_parse = document.parse_query(query_text, builder="property")

        expected_payload = [expected]
        assert [_dump_parsed_expectation(item.expectation) for item in from_module_load] == expected_payload
        assert [_dump_parsed_expectation(item.expectation) for item in from_module_loads] == expected_payload
        assert [_dump_parsed_expectation(item.expectation) for item in from_module_parse] == expected_payload
        assert [_dump_parsed_expectation(item.expectation) for item in from_method_load] == expected_payload
        assert [_dump_parsed_expectation(item.expectation) for item in from_method_loads] == expected_payload
        assert [_dump_parsed_expectation(item.expectation) for item in from_method_parse] == expected_payload

    @pytest.mark.parametrize(
        ("name", "case"),
        PHASE7_SERIALIZED_EXPECTATION_CASES,
        ids=[name for name, _ in PHASE7_SERIALIZED_EXPECTATION_CASES],
    )
    def test_public_document_serialization_covers_expectation_shapes(self, name, case, tmp_path):
        document = _load_minimal_document()
        document.options = tuple(Option(key, value) for key, value in case["document_options"])
        document.queries = (
            Query(
                formula=case["formula"],
                comment=case["comment"],
                options=tuple(Option(key, value) for key, value in case["query_options"]),
                expectation=Expectation(
                    value_type=case["expectation"]["value_type"],
                    status=case["expectation"]["status"],
                    value=case["expectation"]["value"],
                    resources=tuple(
                        Resource(resource_name, resource_value, resource_unit)
                        for resource_name, resource_value, resource_unit in case["expectation"]["resources"]
                    ),
                ),
                location="",
            ),
        )

        xml_text = document.dumps()
        dump_path = tmp_path / f"{name}.xml"
        document.dump(dump_path)

        assert dump_path.read_text(encoding="utf-8") == xml_text
        for fragment in case["xml_fragments"]:
            assert fragment in xml_text

        if case["reloaded_expectation"] is not None:
            reloaded = loads_xml(xml_text)
            expectation = reloaded.queries[0].expectation
            assert expectation.value_type == case["reloaded_expectation"]["value_type"]
            assert expectation.status == case["reloaded_expectation"]["status"]
            assert expectation.value == case["reloaded_expectation"]["value"]
