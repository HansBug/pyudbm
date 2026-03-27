import pytest

from pyudbm.binding import Expectation, ModelBuilder, Query, load_xml

from .utap_phase0_data import MINIMAL_XML_PATH


IMPORTED_QUERY_XTA = """clock x;
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
/* Comment: phase4 imported query */
/** Query end. */
"""

IMPORTED_PROCESS_XTA = """clock x;
process P()
{
    state
        Init;
    init Init;
}

P1 = P();
P2 = P();
system P1, P2;
"""

IMPORTED_TEMPLATE_PATCH_XTA = """clock x;
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
"""

IMPORTED_MODIFY_XTA = """clock y;
chan go;
process Worker(int bound)
{
    int count;
    state
        Init,
        Busy {(y <= bound)};
    urgent Busy;
    init Init;
    trans
        Init -> Busy {
            action SKIP;
            sync go?;
            assign (y = 0);
        };
}

W1 = Worker(7);
system W1;

/** Query begin: */
/* Formula: A[] not deadlock */
/* Comment: edited rich */
/** Query end. */
"""


def _rich_import_source_document():
    return (
        ModelBuilder()
        .clock("x")
        .chan("tick")
        .template("P", parameters="int limit", declaration="int visits;")
            .location("Init", initial=True)
            .location("Done", invariant="x <= limit", committed=True)
            .edge("Init", "Done", sync="tick?", update="x = 0")
            .end()
        .process("P1", "P", "5")
        .system("P1")
        .query("A[] not deadlock", comment="imported rich")
        .build()
    )


@pytest.mark.unittest
class TestUtapBuilderPhase4:
    def test_load_xml_roundtrip_via_from_document_keeps_exact_public_exports(self, text_aligner):
        source = load_xml(MINIMAL_XML_PATH)
        rebuilt = ModelBuilder.from_document(source).build()

        text_aligner.assert_equal(source.to_xta(), rebuilt.to_xta())
        text_aligner.assert_equal(source.dumps(), rebuilt.dumps())

    def test_from_document_preserves_rich_builder_surface_exactly(self, text_aligner):
        source = _rich_import_source_document()
        rebuilt = ModelBuilder.from_document(source).build()

        text_aligner.assert_equal(source.to_xta(), rebuilt.to_xta())
        text_aligner.assert_equal(source.dumps(), rebuilt.dumps())

    def test_from_document_can_append_query_with_exact_text_snapshot(self, text_aligner):
        document = (
            ModelBuilder.from_document(load_xml(MINIMAL_XML_PATH))
            .query("A[] not deadlock", comment="phase4 imported query")
            .build()
        )

        text_aligner.assert_equal(IMPORTED_QUERY_XTA, document.to_xta())
        assert document.queries == (
            Query(
                formula="A[] not deadlock",
                comment="phase4 imported query",
                options=(),
                expectation=Expectation("Symbolic", "True", "", ()),
                location="",
            ),
        )

    def test_from_document_can_append_process_and_patch_system_with_exact_text(self, text_aligner):
        document = (
            ModelBuilder.from_document(load_xml(MINIMAL_XML_PATH))
            .process("P2", "P")
            .system("P1", "P2")
            .build()
        )

        text_aligner.assert_equal(IMPORTED_PROCESS_XTA, document.to_xta())

    def test_from_document_can_patch_existing_template_structure_with_exact_text(self, text_aligner):
        builder = ModelBuilder.from_document(load_xml(MINIMAL_XML_PATH))
        with builder.edit_template("P") as template:
            template.location("Done")
            template.edge("Init", "Done", when="x >= 1")

        document = builder.build()

        text_aligner.assert_equal(IMPORTED_TEMPLATE_PATCH_XTA, document.to_xta())

    def test_from_document_can_modify_existing_content_with_exact_text(self, text_aligner):
        builder = ModelBuilder.from_document(_rich_import_source_document())
        builder.set_declarations("clock y;", "chan go;")
        builder.update_template("P", new_name="Worker", parameters="int bound")
        builder.update_process("P1", new_name="W1", template="Worker", arguments=("7",))
        builder.update_query(0, comment="edited rich")
        builder.system("W1")

        with builder.edit_template("Worker") as template:
            template.set_declarations("int count;")
            template.update_location("Done", new_name="Busy", invariant="y <= bound", committed=False, urgent=True)
            template.update_edge(0, target="Busy", sync="go?", update="y = 0")

        document = builder.build()

        text_aligner.assert_equal(IMPORTED_MODIFY_XTA, document.to_xta())

    def test_from_document_can_delete_existing_content_with_exact_text(self, text_aligner):
        source = (
            ModelBuilder()
            .clock("x")
            .template("P")
                .location("Init", initial=True)
                .location("Done")
                .edge("Init", "Done", when="x >= 1")
                .end()
            .template("Q")
                .location("Q0", initial=True)
                .end()
            .process("P1", "P")
            .process("Q1", "Q")
            .system("P1", "Q1")
            .query("A[] not deadlock", comment="remove me")
            .build()
        )
        builder = ModelBuilder.from_document(source)
        builder.remove_query(0)
        builder.remove_template("Q")

        with builder.edit_template("P") as template:
            template.remove_edge(0)
            template.remove_location("Done")

        document = builder.build()

        text_aligner.assert_equal(load_xml(MINIMAL_XML_PATH).to_xta(), document.to_xta())

    def test_imported_template_patch_error_paths_are_clear(self):
        builder = ModelBuilder.from_document(load_xml(MINIMAL_XML_PATH))

        with pytest.raises(ValueError, match=r"unknown template 'Missing'"):
            builder.edit_template("Missing")

        with pytest.raises(ValueError, match=r"template 'P' has duplicate location 'Init'"):
            builder.edit_template("P").location("Init")

    def test_imported_modify_delete_error_paths_are_clear(self):
        builder = ModelBuilder.from_document(
            ModelBuilder()
            .template("P")
                .location("Init", initial=True)
                .location("Done")
                .edge("Init", "Done")
                .end()
            .process("P1", "P")
            .system("P1")
            .query("A[] not deadlock")
            .build()
        )

        with pytest.raises(ValueError, match=r"unknown process 'Missing'"):
            builder.update_process("Missing", new_name="X")

        with pytest.raises(ValueError, match=r"unknown process 'Missing'"):
            builder.remove_process("Missing")

        with pytest.raises(ValueError, match=r"unknown template 'Missing'"):
            builder.update_template("Missing", new_name="Q")

        with pytest.raises(ValueError, match=r"unknown template 'Missing'"):
            builder.remove_template("Missing")

        with pytest.raises(IndexError, match=r"query index 2 is out of range"):
            builder.update_query(2, comment="x")

        with pytest.raises(IndexError, match=r"query index 2 is out of range"):
            builder.remove_query(2)

        with builder.edit_template("P") as template:
            with pytest.raises(ValueError, match=r"template 'P' has no location 'Missing'"):
                template.update_location("Missing", new_name="X")

            with pytest.raises(ValueError, match=r"template 'P' has no location 'Missing'"):
                template.remove_location("Missing")

            with pytest.raises(IndexError, match=r"edge index 5 is out of range"):
                template.update_edge(5, when="x >= 1")

            with pytest.raises(IndexError, match=r"edge index 5 is out of range"):
                template.remove_edge(5)
