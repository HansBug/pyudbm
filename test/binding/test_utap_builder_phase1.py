import pytest

from pyudbm.binding import Expectation, ModelBuilder, ModelDocument, Option, Query, load_xml, load_xta, loads_xta


MINIMAL_BUILDER_XTA = """clock x;
process P()
{
    state
        Init;
    init Init;
}

P1 = P();
system P1;
"""

MINIMAL_BUILDER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nta PUBLIC "-//Uppaal Team//DTD Flat System 1.1//EN" "http://www.it.uu.se/research/group/darts/uppaal/flat-1_1.dtd"><nta>
  <declaration>// variables
clock x;
</declaration>
  <template>
    <name>P</name>
    <parameter></parameter>
    <declaration>


</declaration>
    <location id="id0" x="0" y="0">
      <name x="8" y="8">Init</name>
    </location>
    <init ref="id0"/>
  </template>
  <system>P1 = P();
system P1; </system>
</nta>
"""

RICH_BUILDER_XTA = """clock x;
urgent chan tick;
process Worker(int limit)
{
    int visits;
    state
        Idle,
        Busy {(x <= limit)};
    commit Busy;
    urgent Idle;
    init Idle;
    trans
        Idle -> Busy {
            action SKIP;
            sync tick?;
            assign (x = 0), (visits = (visits + 1));
        },
        Busy -> Idle {
            action SKIP;
            guard (x >= 3);
        };
}

W1 = Worker(5);
system W1;

/** Query begin: */
/* Formula: A[] not deadlock */
/* Comment: phase1 builder query */
/** Query end. */
"""

RICH_BUILDER_TA = """clock x;
urgent chan tick;
process Worker(int &limit)
{
    int visits;
    state
        Idle,
        Busy {(x <= limit)};
    commit Busy;
    urgent Idle;
    init Idle;
    trans
        Idle -> Busy {
            action SKIP;
            sync tick?;
            assign (x = 0), (visits = (visits + 1));
        },
        Busy -> Idle {
            action SKIP;
            guard (x >= 3);
        };
}

W1 = Worker(5);
system W1;

/** Query begin: */
/* Formula: A[] not deadlock */
/* Comment: phase1 builder query */
/** Query end. */
"""

WITH_OPTIONS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nta PUBLIC "-//Uppaal Team//DTD Flat System 1.1//EN" "http://www.it.uu.se/research/group/darts/uppaal/flat-1_1.dtd"><nta>
  <declaration>// variables
clock x;
</declaration>
  <template>
    <name>P</name>
    <parameter></parameter>
    <declaration>


</declaration>
    <location id="id0" x="0" y="0">
      <name x="8" y="8">Init</name>
    </location>
    <init ref="id0"/>
  </template>
  <system>P1 = P();
system P1; </system>
  <queries>
    <query>
      <formula>A[] not deadlock</formula>
      <comment>with options</comment>
      <option key="trace" value="short"/>
      <expect outcome="success" type="probability" value="0.95"/>
    </query>
  </queries>
</nta>
"""


def _document_snapshot(document):
    return {
        "templates": tuple(item.name for item in document.templates),
        "processes": tuple(item.name for item in document.processes),
        "global_declarations": document.global_declarations,
        "location_names": tuple(item.name for item in document.templates[0].locations),
        "queries": tuple((item.formula, item.comment) for item in document.queries),
    }


@pytest.mark.unittest
class TestUtapBuilderPhase1:
    def test_minimal_builder_roundtrip_and_exact_exports(self, tmp_path, text_aligner):
        document = (
            ModelBuilder()
            .clock("x")
            .template("P")
                .location("Init", initial=True)
                .end()
            .process("P1", "P")
            .system("P1")
            .build()
        )

        xml_path = tmp_path / "builder.xml"
        xta_path = tmp_path / "builder.xta"
        ta_path = tmp_path / "builder.ta"

        document.dump(xml_path)
        document.dump_xta(xta_path)
        document.dump_ta(ta_path)

        xml_roundtrip = load_xml(xml_path)
        xta_roundtrip = loads_xta(document.to_xta())
        xta_file_roundtrip = load_xta(xta_path)
        ta_roundtrip = loads_xta(document.to_ta(), newxta=False)
        ta_file_roundtrip = load_xta(ta_path, newxta=False)

        assert type(document) is ModelDocument
        text_aligner.assert_equal(MINIMAL_BUILDER_XTA, document.to_xta())
        text_aligner.assert_equal(MINIMAL_BUILDER_XTA, document.to_ta())
        text_aligner.assert_equal(MINIMAL_BUILDER_XML, document.dumps())
        text_aligner.assert_equal(MINIMAL_BUILDER_XML, xml_path.read_text(encoding="utf-8"))
        text_aligner.assert_equal(MINIMAL_BUILDER_XTA, xta_path.read_text(encoding="utf-8"))
        text_aligner.assert_equal(MINIMAL_BUILDER_XTA, ta_path.read_text(encoding="utf-8"))
        assert _document_snapshot(xml_roundtrip) == _document_snapshot(document)
        assert _document_snapshot(xta_roundtrip) == _document_snapshot(document)
        assert _document_snapshot(xta_file_roundtrip) == _document_snapshot(document)
        assert _document_snapshot(ta_roundtrip) == _document_snapshot(document)
        assert _document_snapshot(ta_file_roundtrip) == _document_snapshot(document)

    def test_context_manager_template_builder_has_exact_text_exports(self, text_aligner):
        builder = ModelBuilder().clock("x").chan("tick", urgent=True)
        with builder.template("Worker", parameters="int limit", declaration="int visits;") as template:
            template.location("Idle", initial=True, urgent=True)
            template.location("Busy", invariant="x <= limit", committed=True)
            template.edge("Idle", "Busy", sync="tick?", update="x = 0, visits = visits + 1")
            template.edge("Busy", "Idle", when="x >= 3")

        document = builder.process("W1", "Worker", "5").system("W1").query(
            "A[] not deadlock",
            comment="phase1 builder query",
        ).build()

        text_aligner.assert_equal(RICH_BUILDER_XTA, document.to_xta())
        text_aligner.assert_equal(RICH_BUILDER_TA, document.to_ta())
        assert document.queries == (
            Query(
                formula="A[] not deadlock",
                comment="phase1 builder query",
                options=(),
                expectation=Expectation("Symbolic", "True", "", ()),
                location="",
            ),
        )

    def test_query_options_and_expectation_keep_exact_xml_dump(self, text_aligner):
        document = (
            ModelBuilder()
            .clock("x")
            .template("P")
                .location("Init", initial=True)
                .end()
            .process("P1", "P")
            .system("P1")
            .query(
                "A[] not deadlock",
                comment="with options",
                options=(Option("trace", "short"),),
                expectation=Expectation("Probability", "True", "0.95", ()),
            )
            .build()
        )

        text_aligner.assert_equal(WITH_OPTIONS_XML, document.dumps())
        assert document.queries == (
            Query(
                formula="A[] not deadlock",
                comment="with options",
                options=(Option("trace", "short"),),
                expectation=Expectation("Probability", "True", "0.95", ()),
                location="",
            ),
        )

    def test_duplicate_location_is_rejected(self):
        template = ModelBuilder().template("P")
        template.location("Init", initial=True)

        with pytest.raises(ValueError, match=r"template 'P' has duplicate location 'Init'"):
            template.location("Init")

    def test_missing_initial_location_is_rejected(self):
        with pytest.raises(ValueError, match=r"template 'P' must define one initial location"):
            (
                ModelBuilder()
                .template("P")
                    .location("Init")
                    .end()
                .process("P1", "P")
                .system("P1")
                .build()
            )

    def test_unknown_edge_target_is_rejected(self):
        with pytest.raises(ValueError, match=r"template 'P' edge target 'Done' does not exist"):
            (
                ModelBuilder()
                .template("P")
                    .location("Init", initial=True)
                    .edge("Init", "Done")
                    .end()
                .process("P1", "P")
                .system("P1")
                .build()
            )

    def test_unknown_template_process_is_rejected(self):
        with pytest.raises(ValueError, match=r"process 'P1' references unknown template 'Missing'"):
            ModelBuilder().process("P1", "Missing").system("P1").build()

    def test_unknown_system_process_is_rejected(self):
        with pytest.raises(ValueError, match=r"system references unknown process 'P1'"):
            (
                ModelBuilder()
                .template("P")
                    .location("Init", initial=True)
                    .end()
                .system("P1")
                .build()
            )
