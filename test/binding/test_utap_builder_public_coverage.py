from dataclasses import replace
import pytest

from pyudbm.binding import (
    EdgeSpec,
    Expectation,
    LocationSpec,
    ModelBuilder,
    ModelDocument,
    ModelSpec,
    Option,
    Process,
    Query,
    QuerySpec,
    TemplateSpec,
    build_model,
    load_xml,
)

from .utap_phase0_data import MINIMAL_XML_PATH

FAKE_BASE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<nta>
  <declaration></declaration>
  <template>
    <name>P</name>
    <parameter></parameter>
    <declaration></declaration>
    <location id="id0" x="0" y="0">
      <name x="0" y="0">Init</name>
    </location>
    <location id="id1" x="0" y="0">
      <name x="0" y="0">Done</name>
    </location>
    <init ref="id0"/>
  </template>
  <system>P1 = P();
system P1; </system>
</nta>
"""

RENAME_SOURCE_XTA = """int n;
broadcast chan tick;
process P()
{
    int i;
    state
        Start,
        Done;
    init Start;
    trans
        Start -> Done {
            action SKIP;
        };
}

P1 = P();
system P1;
"""

UPDATE_INITIAL_XTA = """int n;
broadcast chan tick;
process P()
{
    int i;
    state
        Init,
        Done;
    init Done;
    trans
        Init -> Done {
            action SKIP;
        };
}

P1 = P();
system P1;
"""

UPDATE_EDGE_GUARD_XTA = """int n;
broadcast chan tick;
process P()
{
    int i;
    state
        Init,
        Done;
    init Init;
    trans
        Init -> Done {
            action SKIP;
            guard (n >= 2);
        };
}

P1 = P();
system P1;
"""


class ImportedDocument(ModelDocument):
    def __init__(
        self,
        xml_text,
        *,
        processes=(),
        queries=(),
        options=(),
        before_update_text="",
        after_update_text="",
        channel_priority_texts=(),
    ):
        self.templates = ()
        self.processes = processes
        self.queries = queries
        self.options = options
        self.errors = ()
        self.warnings = ()
        self.modified = False
        self.features = None
        self._xml_text = xml_text
        self._before_update_text = before_update_text
        self._after_update_text = after_update_text
        self._channel_priority_texts = tuple(channel_priority_texts)

    def dumps(self):
        return self._xml_text

    @property
    def before_update_text(self):
        return self._before_update_text

    @property
    def after_update_text(self):
        return self._after_update_text

    @property
    def channel_priority_texts(self):
        return self._channel_priority_texts


def _minimal_process_document(arguments=""):
    source = load_xml(MINIMAL_XML_PATH)
    process = replace(source.processes[0], arguments=arguments)
    source.processes = (process,)
    return source


def _custom_import_document(template_xml, **kwargs):
    return ImportedDocument(
        """<?xml version="1.0" encoding="UTF-8"?>
<nta>
  <declaration></declaration>
  <template>
%s
  </template>
  <system>P1 = P();
system P1; </system>
</nta>
"""
        % template_xml,
        **kwargs
    )


@pytest.mark.unittest
class TestUtapBuilderPublicCoverage:
    def test_public_scalar_validations_reject_invalid_inputs(self):
        with pytest.raises(TypeError, match=r"text must be a string"):
            ModelBuilder().declaration(None)

        with pytest.raises(ValueError, match=r"text must not be empty"):
            ModelBuilder().declaration("   ")

        with pytest.raises(TypeError, match=r"parameters must be a string"):
            (
                ModelBuilder()
                .template("P")
                    .location("Init", initial=True)
                    .end()
                .update_template("P", parameters=None)
            )

        with pytest.raises(ValueError, match=r"lower must not be empty"):
            ModelBuilder().integer("count", lower=" ", upper=1)

        with pytest.raises(ValueError, match=r"clock requires at least one name"):
            ModelBuilder().clock()

        with pytest.raises(ValueError, match=r"channel names must be unique within one call"):
            ModelBuilder().chan("tick", "tick")

        with pytest.raises(TypeError, match=r"query options must be Option instances or \(name, value\) pairs"):
            ModelBuilder().query("A[] not deadlock", options=(object(),))

        with pytest.raises(TypeError, match=r"expectation must be an Expectation instance or None"):
            ModelBuilder().query("A[] not deadlock", expectation="bad")

    def test_public_option_reset_and_argument_validations_cover_extra_branches(self):
        document = (
            ModelBuilder()
            .declaration("int x; int y;")
            .template("P")
                .location("Init", initial=True)
                .location("Done")
                .edge("Init", "Done", reset=[("x", 0), ("y", 1)])
                .end()
            .process("P1", "P")
            .system("P1")
            .query("A[] not deadlock", options=(("trace", "short"),))
            .build()
        )

        assert document.queries[0].options == (Option("trace", "short"),)

        with pytest.raises(TypeError, match=r"reset must be a mapping or an iterable of \(name, value\) pairs"):
            (
                ModelBuilder()
                .template("P")
                    .location("Init", initial=True)
                    .location("Done")
                    .edge("Init", "Done", reset="x = 0")
            )

        with pytest.raises(TypeError, match=r"reset must contain \(name, value\) pairs"):
            (
                ModelBuilder()
                .template("P")
                    .location("Init", initial=True)
                    .location("Done")
                    .edge("Init", "Done", reset=[("x", 0), object()])
            )

        with pytest.raises(ValueError, match=r"edge sync is ambiguous: use either 'sync' or 'send'/'recv'"):
            (
                ModelBuilder()
                .template("P")
                    .location("Init", initial=True)
                    .location("Done")
                    .edge("Init", "Done", sync="tick\\?", send="tick")
            )

        with pytest.raises(TypeError, match=r"process arguments must be an iterable of argument expressions"):
            build_model(
                ModelSpec(
                    templates=(TemplateSpec("P", locations=(LocationSpec("Init", initial=True),)),),
                    processes=(("P1", "P", 1),),
                    system_process_names=("P1",),
                )
            )

    def test_public_spec_validation_covers_extra_modelspec_paths(self):
        minimal = ModelSpec(
            templates=(TemplateSpec("P", locations=(LocationSpec("Init", initial=True),)),),
            processes=(("P1", "P"),),
            system_process_names=("P1",),
        )
        assert build_model(minimal).templates[0].name == "P"

        with pytest.raises(TypeError, match=r"process specs must be tuples"):
            build_model(ModelSpec(templates=minimal.templates, processes=(["P1", "P"],), system_process_names=("P1",)))

        with pytest.raises(ValueError, match=r"process specs must have the shape"):
            build_model(ModelSpec(templates=minimal.templates, processes=(("P1", "P", (), "x"),), system_process_names=("P1",)))

        with pytest.raises(TypeError, match=r"template locations must be LocationSpec instances"):
            build_model(ModelSpec(templates=(TemplateSpec("P", locations=(object(),)),), processes=(("P1", "P"),), system_process_names=("P1",)))

        with pytest.raises(TypeError, match=r"template edges must be EdgeSpec instances"):
            build_model(
                ModelSpec(
                    templates=(TemplateSpec("P", locations=(LocationSpec("Init", initial=True),), edges=(object(),)),),
                    processes=(("P1", "P"),),
                    system_process_names=("P1",),
                )
            )

        with pytest.raises(TypeError, match=r"model queries must be QuerySpec instances"):
            build_model(ModelSpec(templates=minimal.templates, processes=(("P1", "P"),), system_process_names=("P1",), queries=(object(),)))

        with pytest.raises(TypeError, match=r"model templates must be TemplateSpec instances"):
            build_model(ModelSpec(templates=(object(),), processes=(("P1", "P"),), system_process_names=("P1",)))

        with pytest.raises(ValueError, match=r"duplicate template 'P'"):
            build_model(
                ModelSpec(
                    templates=(
                        TemplateSpec("P", locations=(LocationSpec("Init", initial=True),)),
                        TemplateSpec("P", locations=(LocationSpec("Init", initial=True),)),
                    ),
                    processes=(("P1", "P"),),
                    system_process_names=("P1",),
                )
            )

        with pytest.raises(ValueError, match=r"template 'P' has duplicate location 'Init'"):
            build_model(
                ModelSpec(
                    templates=(TemplateSpec("P", locations=(LocationSpec("Init", initial=True), LocationSpec("Init"))),),
                    processes=(("P1", "P"),),
                    system_process_names=("P1",),
                )
            )

        with pytest.raises(ValueError, match=r"template 'P' has multiple initial locations"):
            build_model(
                ModelSpec(
                    templates=(TemplateSpec("P", locations=(LocationSpec("Init", initial=True), LocationSpec("Done", initial=True))),),
                    processes=(("P1", "P"),),
                    system_process_names=("P1",),
                )
            )

        with pytest.raises(ValueError, match=r"duplicate process 'P1'"):
            build_model(
                ModelSpec(
                    templates=minimal.templates,
                    processes=(("P1", "P"), ("P1", "P")),
                    system_process_names=("P1",),
                )
            )

    def test_public_from_document_guards_cover_document_options_and_update_sections(self):
        with pytest.raises(TypeError, match=r"document must be a ModelDocument instance"):
            ModelBuilder.from_document(object())

        source = load_xml(MINIMAL_XML_PATH)
        source.options = (Option("trace", "short"),)
        with pytest.raises(ValueError, match=r"from_document\(\) does not support document-level options"):
            ModelBuilder.from_document(source)

        with pytest.raises(ValueError, match=r"from_document\(\) does not support before_update declarations"):
            ModelBuilder.from_document(ImportedDocument(FAKE_BASE_XML, before_update_text="before"))

        with pytest.raises(ValueError, match=r"from_document\(\) does not support after_update declarations"):
            ModelBuilder.from_document(ImportedDocument(FAKE_BASE_XML, after_update_text="after"))

        with pytest.raises(ValueError, match=r"from_document\(\) does not support channel priority declarations"):
            ModelBuilder.from_document(ImportedDocument(FAKE_BASE_XML, channel_priority_texts=("default < tick",)))

        source = load_xml(MINIMAL_XML_PATH)
        source.queries = (Query("", "comment", (), Expectation("Symbolic", "True", "", ()), ""),)
        with pytest.raises(ValueError, match=r"from_document\(\) does not support empty imported query formulas with metadata"):
            ModelBuilder.from_document(source)

    def test_public_from_document_skips_empty_queries_without_metadata(self):
        source = load_xml(MINIMAL_XML_PATH)
        source.queries = (
            Query("", "", (), Expectation("Symbolic", "True", "", ()), ""),
            Query("A[] not deadlock", "", (), Expectation("Symbolic", "True", "", ()), ""),
        )

        builder = ModelBuilder.from_document(source)

        assert builder.to_spec().queries == (
            QuerySpec("A[] not deadlock", "", (), Expectation("Symbolic", "True", "", ()), ""),
        )

    def test_public_from_document_process_argument_parsing_covers_nested_and_error_paths(self):
        document = _minimal_process_document('"a,\\"b\\"", [1,2], {3,4}, (5,6), \'u,v\'')
        builder = ModelBuilder.from_document(document)

        assert builder.to_spec().processes == (
            ("P1", "P", ('"a,\\"b\\""', "[1,2]", "{3,4}", "(5,6)", "'u,v'")),
        )

        with pytest.raises(ValueError, match=r"process argument text must not contain empty entries"):
            ModelBuilder.from_document(_minimal_process_document("1,,2"))

        with pytest.raises(ValueError, match=r"process argument text is not balanced"):
            ModelBuilder.from_document(_minimal_process_document("("))

        with pytest.raises(ValueError, match=r"process argument text must not contain empty entries"):
            ModelBuilder.from_document(_minimal_process_document("1,"))

    def test_public_from_document_xml_limitations_cover_remaining_template_branches(self):
        with pytest.raises(ValueError, match=r"from_document\(\) does not support branchpoints in template 'P'"):
            ModelBuilder.from_document(
                _custom_import_document(
                    """
    <name>P</name>
    <parameter></parameter>
    <declaration></declaration>
    <location id="id0" x="0" y="0"><name x="0" y="0">Init</name></location>
    <branchpoint id="bp0" x="0" y="0"/>
    <init ref="id0"/>
                    """
                )
            )

        with pytest.raises(ValueError, match=r"from_document\(\) could not resolve initial location in template 'P'"):
            ModelBuilder.from_document(
                _custom_import_document(
                    """
    <name>P</name>
    <parameter></parameter>
    <declaration></declaration>
    <location id="id0" x="0" y="0"><name x="0" y="0">Init</name></location>
    <init ref="missing"/>
                    """
                )
            )

        with pytest.raises(ValueError, match=r"from_document\(\) requires transitions with both source and target references"):
            ModelBuilder.from_document(
                _custom_import_document(
                    """
    <name>P</name>
    <parameter></parameter>
    <declaration></declaration>
    <location id="id0" x="0" y="0"><name x="0" y="0">Init</name></location>
    <init ref="id0"/>
    <transition><target ref="id0"/></transition>
                    """
                )
            )

        with pytest.raises(ValueError, match=r"from_document\(\) does not support branchpoint transitions in template 'P'"):
            ModelBuilder.from_document(
                _custom_import_document(
                    """
    <name>P</name>
    <parameter></parameter>
    <declaration></declaration>
    <location id="id0" x="0" y="0"><name x="0" y="0">Init</name></location>
    <init ref="id0"/>
    <transition><source ref="bp0"/><target ref="id0"/></transition>
                    """
                )
            )

        with pytest.raises(ValueError, match=r"from_document\(\) does not support edge select clauses in template 'P'"):
            ModelBuilder.from_document(
                _custom_import_document(
                    """
    <name>P</name>
    <parameter></parameter>
    <declaration></declaration>
    <location id="id0" x="0" y="0"><name x="0" y="0">Init</name></location>
    <location id="id1" x="0" y="0"><name x="0" y="0">Done</name></location>
    <init ref="id0"/>
    <transition><source ref="id0"/><target ref="id1"/><label kind="select" x="0" y="0">i:int[0,1]</label></transition>
                    """
                )
            )

        with pytest.raises(ValueError, match=r"from_document\(\) does not support edge probability labels in template 'P'"):
            ModelBuilder.from_document(
                _custom_import_document(
                    """
    <name>P</name>
    <parameter></parameter>
    <declaration></declaration>
    <location id="id0" x="0" y="0"><name x="0" y="0">Init</name></location>
    <location id="id1" x="0" y="0"><name x="0" y="0">Done</name></location>
    <init ref="id0"/>
    <transition><source ref="id0"/><target ref="id1"/><label kind="probability" x="0" y="0">10</label></transition>
                    """
                )
            )

        with pytest.raises(ValueError, match=r"from_document\(\) does not support edge comments in template 'P'"):
            ModelBuilder.from_document(
                _custom_import_document(
                    """
    <name>P</name>
    <parameter></parameter>
    <declaration></declaration>
    <location id="id0" x="0" y="0"><name x="0" y="0">Init</name></location>
    <location id="id1" x="0" y="0"><name x="0" y="0">Done</name></location>
    <init ref="id0"/>
    <transition><source ref="id0"/><target ref="id1"/><label kind="comments" x="0" y="0">note</label></transition>
                    """
                )
            )

    def test_public_builder_editing_paths_cover_remaining_mutation_branches(self, text_aligner):
        document = (
            ModelBuilder()
            .declaration("int n;")
            .chan("tick", broadcast=True)
            .template("P")
                .declaration("int i;")
                .location("Init", initial=True)
                .location("Done")
                .edge("Init", "Done")
                .end()
            .process("P1", "P")
            .system("P1")
            .build()
        )

        assert "broadcast chan tick;" in document.to_xta()
        assert "int n;" in document.to_xta()
        assert "int i;" in document.to_xta()

        builder = ModelBuilder.from_document(
            ModelBuilder()
            .template("P")
                .location("Init", initial=True)
                .end()
            .template("Q")
                .location("Start", initial=True)
                .end()
            .process("P1", "P")
            .process("Q1", "Q")
            .system("P1", "Q1")
            .build()
        )
        with pytest.raises(ValueError, match=r"duplicate template 'P'"):
            builder.update_template("Q", new_name="P")

        with pytest.raises(ValueError, match=r"duplicate process 'P1'"):
            builder.process("P1", "P")

        builder.process("P2", "P").system("P1", "P2")
        with pytest.raises(ValueError, match=r"duplicate process 'P2'"):
            builder.update_process("P1", new_name="P2")

        builder.remove_process("P2")
        assert builder.to_spec().system_process_names == ("P1",)

        rename_builder = ModelBuilder.from_document(document)
        with rename_builder.edit_template("P") as template:
            template.update_location("Init", new_name="Start")
        text_aligner.assert_equal(RENAME_SOURCE_XTA, rename_builder.build().to_xta())

        initial_builder = ModelBuilder.from_document(document)
        with initial_builder.edit_template("P") as template:
            template.update_location("Done", initial=True)
        text_aligner.assert_equal(UPDATE_INITIAL_XTA, initial_builder.build().to_xta())

        guard_builder = ModelBuilder.from_document(document)
        with guard_builder.edit_template("P") as template:
            template.update_edge(0, when="n >= 2")
        text_aligner.assert_equal(UPDATE_EDGE_GUARD_XTA, guard_builder.build().to_xta())

        remove_initial_builder = ModelBuilder.from_document(document)
        with remove_initial_builder.edit_template("P") as template:
            template.remove_location("Init")
        with pytest.raises(ValueError, match=r"template 'P' must define one initial location"):
            remove_initial_builder.build()

        clear_initial_builder = ModelBuilder.from_document(document)
        with clear_initial_builder.edit_template("P") as template:
            template.update_location("Init", initial=False)
        with pytest.raises(ValueError, match=r"template 'P' must define one initial location"):
            clear_initial_builder.build()

    def test_public_builder_editing_errors_cover_closed_and_index_type_paths(self):
        template = ModelBuilder().template("P")
        template.end()

        with pytest.raises(RuntimeError, match=r"template builder is already closed"):
            template.declaration("int i;")

        builder = (
            ModelBuilder()
            .template("P")
                .location("Init", initial=True)
                .location("Done")
                .edge("Init", "Done")
                .end()
            .process("P1", "P")
            .system("P1")
            .query("A[] not deadlock")
        )

        with pytest.raises(TypeError, match=r"query index must be an integer"):
            builder.update_query("0", comment="bad")

        with pytest.raises(TypeError, match=r"edge index must be an integer"):
            builder.edit_template("P").update_edge("0", when="x >= 1")

        with pytest.raises(ValueError, match=r"template 'P' has duplicate location 'Done'"):
            builder.edit_template("P").update_location("Init", new_name="Done")
