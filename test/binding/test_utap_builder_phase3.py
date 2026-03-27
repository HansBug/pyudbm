import pytest

from pyudbm.binding import (
    EdgeSpec,
    Expectation,
    LocationSpec,
    ModelBuilder,
    ModelSpec,
    Query,
    QuerySpec,
    TemplateSpec,
    build_model,
)


MINIMAL_SPEC_XTA = """process P()
{
    state
        Init;
    init Init;
}

P1 = P();
system P1;
"""

MINIMAL_SPEC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nta PUBLIC "-//Uppaal Team//DTD Flat System 1.1//EN" "http://www.it.uu.se/research/group/darts/uppaal/flat-1_1.dtd"><nta>
  <declaration></declaration>
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

RICH_SPEC_XTA = """const int limit = 5;
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

RICH_SPEC_XML = """<?xml version="1.0" encoding="UTF-8"?>
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


def _build_rich_builder():
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
    )


def _rich_spec():
    return ModelSpec(
        declarations=("clock x;", "int[0,3] count = 1;", "const int limit = 5;", "chan start;", "chan done;"),
        templates=(
            TemplateSpec(
                name="Worker",
                declarations=("int visits;",),
                locations=(
                    LocationSpec("Idle", initial=True),
                    LocationSpec("Busy", invariant="x <= limit"),
                ),
                edges=(
                    EdgeSpec("Idle", "Busy", sync="start?", update="x = 0, visits = visits + 1"),
                    EdgeSpec("Busy", "Idle", guard="x >= count", sync="done!"),
                ),
            ),
        ),
        processes=(("W1", "Worker", ()),),
        system_process_names=("W1",),
        queries=(QuerySpec("A[] not deadlock", comment="phase23 query"),),
    )


@pytest.mark.unittest
class TestUtapBuilderPhase3:
    def test_build_model_from_minimal_spec_has_exact_public_exports(self, text_aligner):
        document = build_model(
            ModelSpec(
                templates=(TemplateSpec("P", locations=(LocationSpec("Init", initial=True),)),),
                processes=(("P1", "P", ()),),
                system_process_names=("P1",),
            )
        )

        text_aligner.assert_equal(MINIMAL_SPEC_XTA, document.to_xta())
        text_aligner.assert_equal(MINIMAL_SPEC_XML, document.dumps())

    def test_builder_to_spec_exports_exact_public_model_spec(self):
        expected = ModelSpec(
            declarations=("clock x;", "int[0,3] count = 1;", "const int limit = 5;", "chan start;", "chan done;"),
            templates=(
                TemplateSpec(
                    name="Worker",
                    declarations=("int visits;",),
                    locations=(
                        LocationSpec("Idle", initial=True),
                        LocationSpec("Busy", invariant="x <= limit"),
                    ),
                    edges=(
                        EdgeSpec("Idle", "Busy", sync="start?", update="x = 0, visits = visits + 1"),
                        EdgeSpec("Busy", "Idle", guard="x >= count", sync="done!"),
                    ),
                ),
            ),
            processes=(("W1", "Worker", ()),),
            system_process_names=("W1",),
            queries=(
                QuerySpec(
                    formula="A[] not deadlock",
                    comment="phase23 query",
                    options=(),
                    expectation=Expectation("Symbolic", "True", "", ()),
                    location="",
                ),
            ),
        )

        assert _build_rich_builder().to_spec() == expected

    def test_builder_and_spec_builds_are_exactly_equivalent(self, text_aligner):
        builder_document = _build_rich_builder().build()
        spec_document = build_model(_rich_spec())

        text_aligner.assert_equal(RICH_SPEC_XTA, builder_document.to_xta())
        text_aligner.assert_equal(RICH_SPEC_XML, builder_document.dumps())
        text_aligner.assert_equal(RICH_SPEC_XTA, spec_document.to_xta())
        text_aligner.assert_equal(RICH_SPEC_XML, spec_document.dumps())
        assert spec_document.queries == (
            Query(
                formula="A[] not deadlock",
                comment="phase23 query",
                options=(),
                expectation=Expectation("Symbolic", "True", "", ()),
                location="",
            ),
        )

    def test_build_model_rejects_invalid_public_spec_inputs(self):
        with pytest.raises(TypeError, match=r"spec must be a ModelSpec instance"):
            build_model(object())

        with pytest.raises(ValueError, match=r"system_process_names must not be empty"):
            build_model(
                ModelSpec(
                    templates=(TemplateSpec("P", locations=(LocationSpec("Init", initial=True),)),),
                    processes=(("P1", "P", ()),),
                )
            )

        with pytest.raises(TypeError, match=r"process arguments must be an iterable of argument expressions, not a string"):
            build_model(
                ModelSpec(
                    templates=(TemplateSpec("P", parameters="int limit", locations=(LocationSpec("Init", initial=True),)),),
                    processes=(("P1", "P", "10"),),
                    system_process_names=("P1",),
                )
            )

        with pytest.raises(ValueError, match=r"process 'P1' references unknown template 'Missing'"):
            build_model(ModelSpec(processes=(("P1", "Missing", ()),), system_process_names=("P1",)))

    def test_query_spec_defaults_map_to_public_query_defaults(self):
        document = build_model(
            ModelSpec(
                templates=(TemplateSpec("P", locations=(LocationSpec("Init", initial=True),)),),
                processes=(("P1", "P", ()),),
                system_process_names=("P1",),
                queries=(QuerySpec("A[] not deadlock"),),
            )
        )

        assert document.queries == (
            Query(
                formula="A[] not deadlock",
                comment="",
                options=(),
                expectation=Expectation("Symbolic", "True", "", ()),
                location="",
            ),
        )
