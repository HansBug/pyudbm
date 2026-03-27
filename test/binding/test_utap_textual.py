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
\tstate
\t\tInit;
\tinit Init;
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
\tstate
\t\tL3,
\t\tL2,
\t\tFirst {(c < 2)};
\tinit First;
\ttrans
\t\tL3 -> First {
\t\t\taction SKIP;
\t\t},
\t\tL2 -> L3 {
\t\t\taction SKIP;
\t\t},
\t\tFirst -> L2 {
\t\t\taction SKIP;
\t\t\tguard (c > 1);
\t\t};
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

    def test_to_xta_can_keep_official_builtin_preamble(self, text_aligner):
        document = load_xml(MINIMAL_XML_PATH)

        text_aligner.assert_equal(
            textual_builtin_preamble() + MINIMAL_TEXTUAL_EXPORT,
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
