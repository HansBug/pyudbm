import pytest

from pyudbm.binding import Expectation, ModelBuilder, Query


PHASE2_BUILDER_XTA = """const int limit = 5;
clock x;
int[0,3] count = 1;
chan start;
chan done;
process Worker()
{
    int visits;
    state
        Idle,
        Busy {(x <= limit)};
    init Idle;
    trans
        Idle -> Busy {
            action SKIP;
            sync start?;
            assign (x = 0), (visits = (visits + 1));
        },
        Busy -> Idle {
            action SKIP;
            guard (x >= count);
            sync done!;
        };
}

W1 = Worker();
system W1;

/** Query begin: */
/* Formula: A[] not deadlock */
/* Comment: phase23 query */
/** Query end. */
"""

PHASE2_BUILDER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nta PUBLIC "-//Uppaal Team//DTD Flat System 1.1//EN" "http://www.it.uu.se/research/group/darts/uppaal/flat-1_1.dtd"><nta>
  <declaration>// constants
const int limit = 5;

// variables
clock x;
int[0,3] count = 1;
chan start;
chan done;
</declaration>
  <template>
    <name>Worker</name>
    <parameter></parameter>
    <declaration>

// variables
int visits;

</declaration>
    <location id="id0" x="0" y="0">
      <name x="8" y="8">Idle</name>
    </location>
    <location id="id1" x="120" y="120">
      <name x="128" y="128">Busy</name>
      <label kind="invariant" x="128" y="144">x &lt;= limit</label>
    </location>
    <init ref="id0"/>
    <transition>
      <source ref="id0"/>
      <target ref="id1"/>
      <label kind="synchronisation" x="0" y="120">start?</label>
      <label kind="assignment" x="0" y="136">x = 0, visits = visits + 1</label>
      <nail x="0" y="120"/>
    </transition>
    <transition>
      <source ref="id1"/>
      <target ref="id0"/>
      <label kind="guard" x="120" y="-16">x &gt;= count</label>
      <label kind="synchronisation" x="120" y="0">done!</label>
      <nail x="120" y="0"/>
    </transition>
  </template>
  <system>W1 = Worker();
system W1; </system>
  <queries>
    <query>
      <formula>A[] not deadlock</formula>
      <comment>phase23 query</comment>
    </query>
  </queries>
</nta>
"""


def _build_phase2_document():
    builder = (
        ModelBuilder()
        .clock("x")
        .integer("count", lower=0, upper=3, init=1)
        .integer("limit", init=5, const=True)
        .chan("start")
        .chan("done")
    )
    with builder.template("Worker", declaration="int visits;") as template:
        template.location("Idle", initial=True)
        template.location("Busy", invariant="x <= limit")
        template.edge("Idle", "Busy", recv="start", reset={"x": 0, "visits": "visits + 1"})
        template.edge("Busy", "Idle", when="x >= count", send="done")

    return builder.process("W1", "Worker").system("W1").query(
        "A[] not deadlock",
        comment="phase23 query",
    ).build()


@pytest.mark.unittest
class TestUtapBuilderPhase2:
    def test_builder_sugar_and_integer_helpers_have_exact_public_exports(self, text_aligner):
        document = _build_phase2_document()

        text_aligner.assert_equal(PHASE2_BUILDER_XTA, document.to_xta())
        text_aligner.assert_equal(PHASE2_BUILDER_XML, document.dumps())
        assert document.queries == (
            Query(
                formula="A[] not deadlock",
                comment="phase23 query",
                options=(),
                expectation=Expectation("Symbolic", "True", "", ()),
                location="",
            ),
        )

    def test_duplicate_template_name_is_rejected(self):
        builder = ModelBuilder().template("P").location("Init", initial=True).end()

        with pytest.raises(ValueError, match=r"duplicate template 'P'"):
            builder.template("P")

    def test_multiple_initial_locations_are_rejected(self):
        template = ModelBuilder().template("P")
        template.location("Init", initial=True)

        with pytest.raises(ValueError, match=r"template 'P' already has an initial location"):
            template.location("Done", initial=True)

    def test_unknown_edge_source_is_rejected(self):
        with pytest.raises(ValueError, match=r"template 'P' edge source 'Missing' does not exist"):
            (
                ModelBuilder()
                .template("P")
                    .location("Init", initial=True)
                    .edge("Missing", "Init")
                    .end()
                .process("P1", "P")
                .system("P1")
                .build()
            )

    def test_integer_validation_errors_are_clear(self):
        with pytest.raises(ValueError, match=r"integer bounds require both 'lower' and 'upper'"):
            ModelBuilder().integer("count", lower=0)

        with pytest.raises(ValueError, match=r"const integer 'limit' requires an initializer"):
            ModelBuilder().integer("limit", const=True)

    def test_edge_argument_ambiguity_errors_are_clear(self):
        template = ModelBuilder().template("P").location("Init", initial=True).location("Done")

        with pytest.raises(ValueError, match=r"edge guard is ambiguous: use either 'guard' or 'when'"):
            template.edge("Init", "Done", guard="x > 0", when="x > 1")

        with pytest.raises(ValueError, match=r"edge sync is ambiguous: use only one of 'send' or 'recv'"):
            template.edge("Init", "Done", send="tick", recv="tick")

        with pytest.raises(ValueError, match=r"edge update is ambiguous: use either 'update' or 'reset'"):
            template.edge("Init", "Done", update="x = 1", reset={"x": 0})
