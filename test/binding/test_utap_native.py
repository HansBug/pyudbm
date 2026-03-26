import importlib

import pytest
from pyudbm.binding._utap import ParseError, _NativeDocument

from pyudbm.binding import _utap as utap_module
from .utap_phase0_data import (
    EXPECTED_BUILTIN_DECLARATIONS,
    INVALID_XML_MISSING_REF,
    INVALID_XTA_UNKNOWN_PROCESS,
    MINIMAL_XML_PATH,
    MINIMAL_XTA_PATH,
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
