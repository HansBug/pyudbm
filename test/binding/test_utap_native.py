import importlib
import xml.etree.ElementTree as ET

import pytest
from pyudbm.binding._utap import ParseError, _NativeDocument

from pyudbm.binding import _utap as utap_module
from .utap_phase0_data import (
    EXPECTED_BUILTIN_DECLARATIONS,
    INVALID_XML_MISSING_REF,
    INVALID_XTA_UNKNOWN_PROCESS,
    MINIMAL_XML_PATH,
    MINIMAL_XTA_PATH,
    UTAP_SIMPLE_SYSTEM_PATH,
)
from .utap_phase4_data import (
    REPRESENTATIVE_MIXED_CONTEXT,
    REPRESENTATIVE_MIXED_QUERY,
    REPRESENTATIVE_PROPERTY_CONTEXT,
    REPRESENTATIVE_PROPERTY_QUERY,
    REPRESENTATIVE_TIGA_CONTEXT,
    REPRESENTATIVE_TIGA_QUERY,
    query_expectation,
    resolve_official_path,
)


@pytest.mark.unittest
class TestUtapNative:
    def test_native_module_is_importable(self):
        loaded_module = importlib.import_module("pyudbm.binding._utap")

        assert loaded_module is utap_module
        assert utap_module._NativeDocument is _NativeDocument
        assert utap_module.ParseError is ParseError
        assert callable(utap_module.load_xml)
        assert callable(utap_module.loads_xml)
        assert callable(utap_module.load_xta)
        assert callable(utap_module.loads_xta)
        assert callable(utap_module.load_query)
        assert callable(utap_module.loads_query)
        assert callable(utap_module.parse_query)
        assert callable(utap_module.builtin_declarations)

    def test_builtin_declarations_snapshot(self):
        assert utap_module.builtin_declarations() == EXPECTED_BUILTIN_DECLARATIONS

    def test_xml_entrypoints_return_native_document(self):
        xml_text = MINIMAL_XML_PATH.read_text(encoding="utf-8")
        from_file = utap_module.load_xml(MINIMAL_XML_PATH)
        from_buffer = utap_module.loads_xml(xml_text)

        assert type(from_file) is _NativeDocument
        assert type(from_buffer) is _NativeDocument
        assert from_file.has_errors is False
        assert from_file.has_warnings is False
        assert from_file.error_count == 0
        assert from_file.warning_count == 0
        assert from_file.modified is False
        assert repr(from_file) == "<_utap._NativeDocument errors=0 warnings=0>"
        assert from_buffer.has_errors is False
        assert from_buffer.has_warnings is False
        assert from_buffer.error_count == 0
        assert from_buffer.warning_count == 0
        assert from_buffer.modified is False
        assert repr(from_buffer) == "<_utap._NativeDocument errors=0 warnings=0>"

    def test_textual_entrypoints_return_native_document(self):
        xta_text = MINIMAL_XTA_PATH.read_text(encoding="utf-8")
        from_file = utap_module.load_xta(MINIMAL_XTA_PATH)
        from_buffer = utap_module.loads_xta(xta_text)

        assert type(from_file) is _NativeDocument
        assert type(from_buffer) is _NativeDocument
        assert from_file.has_errors is False
        assert from_file.has_warnings is False
        assert from_file.error_count == 0
        assert from_file.warning_count == 0
        assert from_file.modified is False
        assert repr(from_file) == "<_utap._NativeDocument errors=0 warnings=0>"
        assert from_buffer.has_errors is False
        assert from_buffer.has_warnings is False
        assert from_buffer.error_count == 0
        assert from_buffer.warning_count == 0
        assert from_buffer.modified is False
        assert repr(from_buffer) == "<_utap._NativeDocument errors=0 warnings=0>"

    def test_native_document_exposes_write_and_introspection_helpers(self, tmp_path):
        document = utap_module.load_xml(MINIMAL_XML_PATH)
        output_path = tmp_path / "native.xml"

        document.write_xml(output_path)

        assert output_path.is_file()
        assert document.global_declarations() == "// variables\nclock x;\n"
        assert document.before_update_text() == ""
        assert document.after_update_text() == ""
        assert document.channel_priority_texts() == []
        assert document.global_clock_names() == ["x"]
        assert document.template_clock_names() == {"P": []}

    def test_native_write_xml_keeps_upstream_structure_without_queries_injection(self, tmp_path):
        document = utap_module.load_xml(UTAP_SIMPLE_SYSTEM_PATH)
        output_path = tmp_path / "native_simple.xml"

        document.write_xml(output_path)

        assert [child.tag for child in ET.fromstring(output_path.read_text(encoding="utf-8"))] == [
            "declaration",
            "template",
            "system",
        ]

    def test_missing_xml_path_raises_file_not_found(self):
        missing_path = MINIMAL_XML_PATH.parent / "missing.xml"

        with pytest.raises(FileNotFoundError) as exc_info:
            utap_module.load_xml(missing_path)

        assert type(exc_info.value) is FileNotFoundError
        assert exc_info.value.args == (f"No such file or directory: {missing_path}",)

    def test_invalid_xml_inputs_raise_parse_error(self):
        invalid_file = MINIMAL_XML_PATH.parent / "invalid_missing_ref.xml"

        invalid_file.write_text(INVALID_XML_MISSING_REF, encoding="utf-8")
        try:
            with pytest.raises(ParseError) as file_exc_info:
                utap_module.load_xml(invalid_file)
            with pytest.raises(ParseError) as buffer_exc_info:
                utap_module.loads_xml(INVALID_XML_MISSING_REF)
        finally:
            invalid_file.unlink()

        assert type(file_exc_info.value) is ParseError
        assert type(buffer_exc_info.value) is ParseError
        assert file_exc_info.value.args == ("XML parse failed: Missing reference",)
        assert buffer_exc_info.value.args == ("XML parse failed: Missing reference",)

    def test_invalid_textual_inputs_raise_parse_error(self):
        invalid_file = MINIMAL_XTA_PATH.parent / "invalid_unknown_process.xta"

        invalid_file.write_text(INVALID_XTA_UNKNOWN_PROCESS, encoding="utf-8")
        try:
            with pytest.raises(ParseError) as file_exc_info:
                utap_module.load_xta(invalid_file)
            with pytest.raises(ParseError) as buffer_exc_info:
                utap_module.loads_xta(INVALID_XTA_UNKNOWN_PROCESS)
        finally:
            invalid_file.unlink()

        assert type(file_exc_info.value) is ParseError
        assert type(buffer_exc_info.value) is ParseError
        assert file_exc_info.value.args == ("XTA parse failed: $No_such_process: Missing",)
        assert buffer_exc_info.value.args == ("XTA parse failed: $No_such_process: Missing",)

    def test_native_query_entrypoints_parse_property_and_tiga_queries(self):
        property_document = utap_module.load_xml(resolve_official_path(REPRESENTATIVE_PROPERTY_CONTEXT))
        tiga_document = utap_module.load_xml(resolve_official_path(REPRESENTATIVE_TIGA_CONTEXT))
        property_queries = utap_module.load_query(resolve_official_path(REPRESENTATIVE_PROPERTY_QUERY), property_document)
        tiga_queries = utap_module.load_query(resolve_official_path(REPRESENTATIVE_TIGA_QUERY), tiga_document)

        assert type(property_queries) is list
        assert type(tiga_queries) is list
        assert len(property_queries) == len(query_expectation(REPRESENTATIVE_PROPERTY_QUERY)["queries"])
        assert len(tiga_queries) == len(query_expectation(REPRESENTATIVE_TIGA_QUERY)["queries"])
        assert property_queries[0]["builder"] == "property"
        assert property_queries[0]["quantifier"] == "AG"
        assert property_queries[0]["text"] == "A[] !deadlock"
        assert property_queries[0]["expression"]["kind"] == 103
        assert property_queries[0]["expression"]["size"] == 1
        assert property_queries[0]["options"] == []
        assert property_queries[0]["expectation"] is None
        assert tiga_queries[0]["builder"] == "tiga"
        assert tiga_queries[0]["quantifier"] == "control_AF"
        assert tiga_queries[0]["text"] == "A<> Main.goal"
        assert tiga_queries[0]["expression"]["kind"] == 102
        assert tiga_queries[0]["expression"]["size"] == 1
        assert tiga_queries[0]["options"] == []
        assert tiga_queries[0]["expectation"] is None

    def test_native_query_entrypoints_support_buffer_and_explicit_builder_paths(self):
        mixed_document = utap_module.load_xml(resolve_official_path(REPRESENTATIVE_MIXED_CONTEXT))
        mixed_query_text = resolve_official_path(REPRESENTATIVE_MIXED_QUERY).read_text(encoding="utf-8")
        explicit_tiga = utap_module.load_query(resolve_official_path(REPRESENTATIVE_MIXED_QUERY), mixed_document, builder="tiga")
        from_buffer = utap_module.loads_query(mixed_query_text, mixed_document, builder="tiga")
        from_alias = utap_module.parse_query(mixed_query_text, mixed_document, builder="tiga")

        assert len(explicit_tiga) == 6
        assert [item["builder"] for item in explicit_tiga] == ["tiga"] * 6
        assert [item["quantifier"] for item in explicit_tiga] == [
            "control_AF",
            "probaDiamond",
            "probaExpected",
            "probaExpected",
            "AE",
            "AE",
        ]
        assert [item["text"] for item in explicit_tiga] == [item["text"] for item in from_buffer]
        assert [item["text"] for item in explicit_tiga] == [item["text"] for item in from_alias]

    def test_native_query_entrypoints_report_invalid_builder_and_builder_mismatch(self):
        tiga_document = utap_module.load_xml(resolve_official_path(REPRESENTATIVE_TIGA_CONTEXT))

        with pytest.raises(ValueError) as invalid_builder:
            utap_module.load_query(resolve_official_path(REPRESENTATIVE_TIGA_QUERY), tiga_document, builder="missing")
        with pytest.raises(ParseError) as property_builder_error:
            utap_module.load_query(resolve_official_path(REPRESENTATIVE_TIGA_QUERY), tiga_document, builder="property")

        assert type(invalid_builder.value) is ValueError
        assert invalid_builder.value.args == ("Unknown query builder: missing",)
        assert type(property_builder_error.value) is ParseError
        assert property_builder_error.value.args == ("query parse failed with property builder: $Invalid_property_type",)
