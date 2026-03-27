import pytest

from pyudbm.binding import Expectation, ModelBuilder, Query


PHASE6_IMPORT_INSPECT_PATCH_XTA = """clock x;
process P()
{
    state
        Init,
        Done;
    init Init;
    trans
        Init -> Done {
            action SKIP;
            guard (x >= 1);
        };
}

P1 = P();
system P1;

/** Query begin: */
/* Formula: A[] not deadlock */
/* Comment: phase6 inspect patch */
/** Query end. */
"""


def _phase6_source_builder():
    return (
        ModelBuilder()
        .clock("x")
        .chan("go", "tick")
        .template("P")
            .location("Init", initial=True)
            .location("Busy")
            .location("Done")
            .edge("Init", "Busy", sync="go?")
            .edge("Init", "Done")
            .end()
        .process("P1", "P")
        .system("P1")
        .query("A[] not deadlock", comment="q0")
        .query("E<> Busy", comment="q1")
    )


@pytest.mark.unittest
class TestUtapBuilderPhase6:
    def test_selector_patch_paths_keep_index_fallback_compatibility(self):
        builder = _phase6_source_builder()
        builder.update_query(where={"formula": "E<> Busy"}, comment="patched q1")
        builder.remove_query(0)

        with builder.edit_template("P") as template:
            template.update_edge(where={"source": "Init", "target": "Busy"}, sync="tick?")
            template.remove_edge(1)

        document = builder.build()

        assert document.queries == (
            Query(
                formula="E<> Busy",
                comment="patched q1",
                options=(),
                expectation=Expectation("Symbolic", "True", "", ()),
                location="",
            ),
        )
        assert "sync tick?" in document.to_xta()

    def test_selector_ambiguity_errors_expose_candidate_indexes(self):
        builder = (
            ModelBuilder()
            .template("P")
                .location("Init", initial=True)
                .location("Done")
                .edge("Init", "Done")
                .edge("Init", "Done")
                .end()
            .process("P1", "P")
            .system("P1")
            .query("A[] not deadlock")
            .query("A[] not deadlock")
        )

        with pytest.raises(ValueError, match=r"query selector .* is ambiguous: matched 2 queries: .*index=0.*index=1"):
            builder.remove_query(where={"formula": "A[] not deadlock"})

        with builder.edit_template("P") as template:
            with pytest.raises(ValueError, match=r"edge selector .* is ambiguous: matched 2 edges: .*index=0.*index=1"):
                template.update_edge(where={"source": "Init"}, sync="go?")

    def test_selector_validation_errors_are_clear(self):
        builder = _phase6_source_builder()

        with pytest.raises(ValueError, match=r"query selection requires either 'index' or 'where'"):
            builder.update_query(comment="bad")

        with pytest.raises(ValueError, match=r"query selection is ambiguous: use either 'index' or 'where'"):
            builder.update_query(0, where={"formula": "A[] not deadlock"}, comment="bad")

        with pytest.raises(TypeError, match=r"query selector must be a mapping"):
            builder.remove_query(where="A[] not deadlock")

        with pytest.raises(ValueError, match=r"query selector field 'options' is not supported"):
            builder.update_query(where={"options": "x"}, comment="bad")

        with pytest.raises(ValueError, match=r"query selector .* matched no query"):
            builder.remove_query(where={"formula": "A[] deadlock"})

        with builder.edit_template("P") as template:
            with pytest.raises(ValueError, match=r"edge selection requires either 'index' or 'where'"):
                template.update_edge(sync="tick?")

            with pytest.raises(ValueError, match=r"edge selection is ambiguous: use either 'index' or 'where'"):
                template.remove_edge(0, where={"source": "Init", "target": "Busy"})

            with pytest.raises(TypeError, match=r"edge selector must be a mapping"):
                template.remove_edge(where="Init -> Busy")

            with pytest.raises(ValueError, match=r"edge selector field 'action' is not supported"):
                template.update_edge(where={"action": "SKIP"}, sync="x?")

            with pytest.raises(ValueError, match=r"edge selector .* matched no edge"):
                template.remove_edge(where={"source": "Busy", "target": "Init"})

    def test_list_and_inspect_helpers_expose_index_and_semantic_fields(self):
        builder = _phase6_source_builder()

        assert builder.list_templates() == (
            {
                "index": 0,
                "name": "P",
                "parameters": "",
                "declarations": (),
                "initial_location": "Init",
                "location_count": 3,
                "edge_count": 2,
            },
        )
        assert builder.list_processes() == (
            {
                "index": 0,
                "name": "P1",
                "template_name": "P",
                "arguments": (),
                "in_system": True,
                "system_index": 0,
            },
        )
        assert builder.list_queries()[0]["index"] == 0
        assert builder.list_queries()[0]["formula"] == "A[] not deadlock"
        assert builder.list_locations("P") == (
            {
                "index": 0,
                "name": "Init",
                "initial": True,
                "invariant": "",
                "urgent": False,
                "committed": False,
            },
            {
                "index": 1,
                "name": "Busy",
                "initial": False,
                "invariant": "",
                "urgent": False,
                "committed": False,
            },
            {
                "index": 2,
                "name": "Done",
                "initial": False,
                "invariant": "",
                "urgent": False,
                "committed": False,
            },
        )
        assert builder.list_edges("P") == (
            {
                "index": 0,
                "source": "Init",
                "target": "Busy",
                "guard": "",
                "sync": "go?",
                "update": "",
            },
            {
                "index": 1,
                "source": "Init",
                "target": "Done",
                "guard": "",
                "sync": "",
                "update": "",
            },
        )

        snapshot = builder.inspect()
        assert snapshot["declarations"] == ("clock x;", "chan go, tick;")
        assert snapshot["system_process_names"] == ("P1",)
        assert snapshot["templates"][0]["index"] == 0
        assert snapshot["templates"][0]["locations"][0]["index"] == 0
        assert snapshot["templates"][0]["edges"][0]["index"] == 0
        assert snapshot["queries"][1]["formula"] == "E<> Busy"

    def test_import_inspect_patch_roundtrip_has_exact_text(self, text_aligner):
        source = (
            ModelBuilder()
            .clock("x")
            .template("P")
                .location("Init", initial=True)
                .location("Done")
                .edge("Init", "Done")
                .end()
            .process("P1", "P")
            .system("P1")
            .query("A[] not deadlock", comment="imported")
            .build()
        )
        builder = ModelBuilder.from_document(source)
        assert builder.inspect()["queries"][0]["comment"] == "imported"

        builder.update_query(where={"formula": "A[] not deadlock"}, comment="phase6 inspect patch")
        with builder.edit_template("P") as template:
            template.update_edge(where={"source": "Init", "target": "Done"}, when="x >= 1")

        text_aligner.assert_equal(PHASE6_IMPORT_INSPECT_PATCH_XTA, builder.build().to_xta())
