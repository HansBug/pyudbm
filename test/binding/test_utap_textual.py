import pytest

from pyudbm.binding import (
    Expectation,
    ModelDocument,
    Query,
    load_xml,
    load_xta,
    loads_xta,
    textual_builtin_preamble,
)

from .utap_phase0_data import MINIMAL_XML_PATH, UTAP_SIMPLE_SYSTEM_PATH


MINIMAL_TEXTUAL_EXPORT = """clock x;
process P()
{
    state
        Init;
    init Init;
}

P1 = P();
system P1;
"""

MINIMAL_TEXTUAL_EXPORT_TABS = """clock x;
process P()
{
\tstate
\t\tInit;
\tinit Init;
}

P1 = P();
system P1;
"""

MINIMAL_TEXTUAL_EXPORT_WITH_QUERY = """clock x;
process P()
{
    state
        Init;
    init Init;
}

P1 = P();
system P1;

/** Query begin: */
/* Formula: A[] not deadlock */
/* Comment: text export query */
/** Query end. */
"""

SIMPLE_SYSTEM_TEXTUAL_EXPORT = """clock c;
process Template()
{
    state
        L3,
        L2,
        First {(c < 2)};
    init First;
    trans
        L3 -> First {
            action SKIP;
        },
        L2 -> L3 {
            action SKIP;
        },
        First -> L2 {
            action SKIP;
            guard (c > 1);
        };
}

Process = Template();
Process2 = Template();
system Process, Process2;

/** Query begin: */
/** Query end. */
"""


def _textual_snapshot(document):
    return {
        "templates": tuple(item.name for item in document.templates),
        "processes": tuple(item.name for item in document.processes),
        "global_declarations": document.global_declarations,
        "location_names": tuple(item.name for item in document.templates[0].locations),
    }


@pytest.mark.unittest
class TestUtapTextualExport:
    def test_to_xta_and_dump_xta_roundtrip_via_public_api(self, tmp_path, text_aligner):
        document = load_xml(MINIMAL_XML_PATH)
        output_text = document.to_xta()
        output_path = tmp_path / "model.xta"

        document.dump_xta(output_path)

        from_buffer = loads_xta(output_text)
        from_file = load_xta(output_path)

        assert type(document) is ModelDocument
        text_aligner.assert_equal(MINIMAL_TEXTUAL_EXPORT, output_text)
        text_aligner.assert_equal(MINIMAL_TEXTUAL_EXPORT, output_path.read_text(encoding="utf-8"))
        assert _textual_snapshot(from_buffer) == _textual_snapshot(document)
        assert _textual_snapshot(from_file) == _textual_snapshot(document)

    def test_to_xta_none_indent_preserves_official_tabs(self, text_aligner):
        document = load_xml(MINIMAL_XML_PATH)

        text_aligner.assert_equal(MINIMAL_TEXTUAL_EXPORT_TABS, document.to_xta(indent=None))

    def test_to_xta_custom_indent_replaces_tabs_with_spaces(self, tmp_path, text_aligner):
        document = load_xml(MINIMAL_XML_PATH)
        output_path = tmp_path / "model_spaces2.xta"
        expected = MINIMAL_TEXTUAL_EXPORT_TABS.replace("\t", "  ")

        output_text = document.to_xta(indent=2)
        document.dump_xta(output_path, indent=2)

        text_aligner.assert_equal(expected, output_text)
        text_aligner.assert_equal(expected, output_path.read_text(encoding="utf-8"))

    def test_to_xta_can_keep_official_builtin_preamble(self, text_aligner):
        document = load_xml(MINIMAL_XML_PATH)

        text_aligner.assert_equal(
            textual_builtin_preamble().replace("\t", "    ") + MINIMAL_TEXTUAL_EXPORT,
            document.to_xta(include_builtin_preamble=True),
        )

    def test_to_ta_and_dump_ta_roundtrip_via_public_api(self, tmp_path, text_aligner):
        document = load_xml(MINIMAL_XML_PATH)
        output_text = document.to_ta()
        output_path = tmp_path / "model.ta"

        document.dump_ta(output_path)

        from_buffer = loads_xta(output_text, newxta=False)
        from_file = load_xta(output_path, newxta=False)

        text_aligner.assert_equal(MINIMAL_TEXTUAL_EXPORT, output_text)
        text_aligner.assert_equal(MINIMAL_TEXTUAL_EXPORT, output_path.read_text(encoding="utf-8"))
        assert _textual_snapshot(from_buffer) == _textual_snapshot(document)
        assert _textual_snapshot(from_file) == _textual_snapshot(document)

    def test_to_ta_none_indent_preserves_official_tabs(self, text_aligner):
        document = load_xml(MINIMAL_XML_PATH)

        text_aligner.assert_equal(MINIMAL_TEXTUAL_EXPORT_TABS, document.to_ta(indent=None))

    def test_to_ta_custom_indent_replaces_tabs_with_spaces(self, tmp_path, text_aligner):
        document = load_xml(MINIMAL_XML_PATH)
        output_path = tmp_path / "model_spaces2.ta"
        expected = MINIMAL_TEXTUAL_EXPORT_TABS.replace("\t", "  ")

        output_text = document.to_ta(indent=2)
        document.dump_ta(output_path, indent=2)

        text_aligner.assert_equal(expected, output_text)
        text_aligner.assert_equal(expected, output_path.read_text(encoding="utf-8"))

    @pytest.mark.parametrize("method_name", ["to_xta", "to_ta"])
    def test_textual_export_rejects_negative_indent(self, method_name):
        document = load_xml(MINIMAL_XML_PATH)

        with pytest.raises(ValueError, match=r"indent must be >= 0 or None"):
            getattr(document, method_name)(indent=-1)

    def test_textual_export_uses_high_level_xml_semantics_for_python_side_queries(self, text_aligner):
        document = load_xml(MINIMAL_XML_PATH)
        document.queries = (
            Query(
                formula="A[] not deadlock",
                comment="text export query",
                options=(),
                expectation=Expectation("Symbolic", "True", "", ()),
                location="",
            ),
        )

        output_text = document.to_xta()

        text_aligner.assert_equal(MINIMAL_TEXTUAL_EXPORT_WITH_QUERY, output_text)

    def test_textual_export_uses_official_prettyprinter_query_boundary_on_xml_models(self, text_aligner):
        document = load_xml(UTAP_SIMPLE_SYSTEM_PATH)

        output_text = document.to_xta()

        text_aligner.assert_equal(SIMPLE_SYSTEM_TEXTUAL_EXPORT, output_text)
