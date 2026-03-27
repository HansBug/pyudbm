from pathlib import Path

import pytest

from pyudbm.binding import Expectation, Query, loads_xta

from .utap_phase7_data import PHASE7_MINIMAL_XTA
from .utap_phase8_data import PHASE8_MALFORMED_DUMP_CASES, PHASE8_NO_NEWLINE_XML


def _load_minimal_document():
    return loads_xta(PHASE7_MINIMAL_XTA)


def _override_write_xml(document, xml_text):
    document.write_xml = lambda path: Path(path).write_text(xml_text, encoding="utf-8")


@pytest.mark.unittest
class TestUtapPhase8:
    def test_dumps_inserts_newline_before_queries_block_when_public_writer_omits_it(self):
        document = _load_minimal_document()
        document.queries = (
            Query(
                formula="A[] not deadlock",
                comment="newline normalization",
                options=(),
                expectation=Expectation("Symbolic", "True", "", ()),
                location="",
            ),
        )
        _override_write_xml(document, PHASE8_NO_NEWLINE_XML)

        xml_text = document.dumps()

        assert "</declaration>\n  <queries>\n" in xml_text
        assert xml_text.endswith("</nta>")

    @pytest.mark.parametrize(
        ("name", "xml_text", "needs_queries", "message"),
        PHASE8_MALFORMED_DUMP_CASES,
        ids=[name for name, _, _, _ in PHASE8_MALFORMED_DUMP_CASES],
    )
    def test_dumps_reports_public_writer_shape_errors(self, name, xml_text, needs_queries, message):
        document = _load_minimal_document()
        if needs_queries:
            document.queries = (
                Query(
                    formula="A[] not deadlock",
                    comment=name,
                    options=(),
                    expectation=Expectation("Symbolic", "True", "", ()),
                    location="",
                ),
            )
        _override_write_xml(document, xml_text)

        with pytest.raises(RuntimeError) as error:
            document.dumps()

        assert error.value.args == (message,)
