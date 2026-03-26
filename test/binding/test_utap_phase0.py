import json

import pytest

from .utap_phase0_data import OFFICIAL_CATALOG_PATH, PHASE0_FIELD_COVERAGE, PHASE0_SAMPLE_LAYERS, REPO_ROOT


@pytest.mark.unittest
class TestUtapPhase0:
    def test_official_catalog_entries_are_structurally_valid(self):
        catalog = json.loads(OFFICIAL_CATALOG_PATH.read_text(encoding="utf-8"))
        files = catalog["files"]
        resolved_paths = tuple((OFFICIAL_CATALOG_PATH.parent / item["path"]).resolve() for item in files)
        statuses = tuple(item["status"] for item in files)

        assert OFFICIAL_CATALOG_PATH.is_file()
        assert catalog["base_dir"] == "."
        assert catalog["generated_from"] == "manifest.json"
        assert catalog["version"] == 1
        assert tuple(catalog["parse_kind_enum"]) == ("XML_MODEL_FILE", "TEXTUAL_MODEL_FILE", "QUERY_PROPERTY_FILE")
        assert all(path.is_file() for path in resolved_paths)
        assert statuses == ("ok",) * len(files)

    def test_query_entries_have_resolvable_context_paths(self):
        catalog = json.loads(OFFICIAL_CATALOG_PATH.read_text(encoding="utf-8"))
        query_entries = tuple(item for item in catalog["files"] if item["parse_kind"] == "QUERY_PROPERTY_FILE")
        context_paths = tuple(item["context_path"] for item in query_entries)
        resolved_contexts = tuple((OFFICIAL_CATALOG_PATH.parent / relpath).resolve() for relpath in context_paths)

        assert len(query_entries) == 47
        assert all(context_paths)
        assert all(path.is_file() for path in resolved_contexts)

    @pytest.mark.parametrize(
        ("object_name", "fields"),
        tuple(PHASE0_FIELD_COVERAGE.items()),
    )
    def test_phase0_field_coverage_map_is_present(self, object_name, fields):
        assert object_name in PHASE0_FIELD_COVERAGE
        assert PHASE0_FIELD_COVERAGE[object_name] == fields
        assert len(fields) >= 3

    @pytest.mark.parametrize(
        ("layer_name", "relative_paths"),
        tuple(PHASE0_SAMPLE_LAYERS.items()),
    )
    def test_phase0_sample_layers_are_resolved(self, layer_name, relative_paths):
        resolved_paths = tuple((REPO_ROOT / relative_path).resolve() for relative_path in relative_paths)

        assert PHASE0_SAMPLE_LAYERS[layer_name] == relative_paths
        assert all(path.exists() for path in resolved_paths)
