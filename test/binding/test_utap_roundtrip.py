import json
import xml.etree.ElementTree as ET

import pytest

from pyudbm.binding import ModelDocument, load_xml, loads_xml

from .utap_phase6_data import DIRECT_WRITE_ROOT_TAGS, PHASE6_ROUNDTRIP_CASES


def _root_tags(xml_text):
    return [child.tag for child in ET.fromstring(xml_text)]


@pytest.mark.unittest
class TestUtapRoundTrip:
    @pytest.mark.parametrize(
        ("model_path", "expected"),
        PHASE6_ROUNDTRIP_CASES,
        ids=[model_path.name for model_path, _ in PHASE6_ROUNDTRIP_CASES],
    )
    def test_dump_and_dumps_roundtrip_preserve_semantic_structure(self, model_path, expected, tmp_path):
        document = load_xml(model_path)
        dump_text = document.dumps()
        dump_path = tmp_path / f"{model_path.stem}.dump.xml"
        document.dump(dump_path)
        from_buffer = loads_xml(dump_text)
        from_file = load_xml(dump_path)

        assert type(document) is ModelDocument
        assert document.to_xml() == dump_text
        assert dump_path.read_text(encoding="utf-8") == dump_text
        assert _root_tags(dump_text) == expected["dump_root_tags"]

        for reloaded in (from_buffer, from_file):
            assert tuple(template.name for template in reloaded.templates) == expected["template_names"]
            assert tuple(process.name for process in reloaded.processes) == expected["process_names"]
            assert tuple(query.formula for query in reloaded.queries) == expected["query_formulas"]
            assert tuple(location.invariant.text for location in reloaded.templates[0].locations) == expected["location_invariants"]
            assert reloaded.global_declarations == expected["global_declarations"]
            assert reloaded.global_clock_names == expected["global_clock_names"]
            assert reloaded.template_clock_names == expected["template_clock_names"]
            assert reloaded.feature_summary() == expected["feature_summary"]
            assert reloaded.capability_summary() == expected["capability_summary"]
            assert reloaded.pretty() == json.dumps(expected["pretty_payload"], indent=2, sort_keys=True)

        assert from_buffer.queries == document.queries
        assert from_file.queries == document.queries
        assert from_buffer.features == document.features
        assert from_file.features == document.features

    def test_write_xml_uses_direct_upstream_writer_without_query_injection(self, tmp_path):
        document = load_xml(PHASE6_ROUNDTRIP_CASES[1][0])
        output_path = tmp_path / "direct.xml"

        document.write_xml(output_path)

        assert _root_tags(output_path.read_text(encoding="utf-8")) == DIRECT_WRITE_ROOT_TAGS

    def test_public_introspection_helpers_return_exact_values(self):
        minimal_document = load_xml(PHASE6_ROUNDTRIP_CASES[0][0])
        simple_document = load_xml(PHASE6_ROUNDTRIP_CASES[1][0])

        assert minimal_document.global_declarations == PHASE6_ROUNDTRIP_CASES[0][1]["global_declarations"]
        assert minimal_document.before_update_text == ""
        assert minimal_document.after_update_text == ""
        assert minimal_document.channel_priority_texts == ()
        assert minimal_document.global_clock_names == PHASE6_ROUNDTRIP_CASES[0][1]["global_clock_names"]
        assert minimal_document.template_clock_names == PHASE6_ROUNDTRIP_CASES[0][1]["template_clock_names"]
        assert minimal_document.feature_summary() == PHASE6_ROUNDTRIP_CASES[0][1]["feature_summary"]
        assert minimal_document.capability_summary() == PHASE6_ROUNDTRIP_CASES[0][1]["capability_summary"]

        assert simple_document.global_declarations == PHASE6_ROUNDTRIP_CASES[1][1]["global_declarations"]
        assert simple_document.before_update_text == ""
        assert simple_document.after_update_text == ""
        assert simple_document.channel_priority_texts == ()
        assert simple_document.global_clock_names == PHASE6_ROUNDTRIP_CASES[1][1]["global_clock_names"]
        assert simple_document.template_clock_names == PHASE6_ROUNDTRIP_CASES[1][1]["template_clock_names"]
        assert simple_document.feature_summary() == PHASE6_ROUNDTRIP_CASES[1][1]["feature_summary"]
        assert simple_document.capability_summary() == PHASE6_ROUNDTRIP_CASES[1][1]["capability_summary"]
