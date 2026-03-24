import importlib.util
import re
from pathlib import Path

import pytest


_META_PATH = Path(__file__).resolve().parents[2] / 'pyudbm' / 'config' / 'meta.py'
_META_SPEC = importlib.util.spec_from_file_location('pyudbm_config_meta', _META_PATH)
_META_MODULE = importlib.util.module_from_spec(_META_SPEC)
assert _META_SPEC.loader is not None
_META_SPEC.loader.exec_module(_META_MODULE)
_COMMIT_TIME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}$')


@pytest.mark.unittest
class TestConfigMeta:
    def test_title(self):
        assert _META_MODULE.__TITLE__ == 'pyudbm'

    def test_upstream_metadata_present(self):
        assert _META_MODULE.__UUTILS_VERSION__
        assert _META_MODULE.__UUTILS_COMMIT__
        assert _META_MODULE.__UUTILS_COMMIT_TIME__
        assert _COMMIT_TIME_PATTERN.fullmatch(_META_MODULE.__UUTILS_COMMIT_TIME__)
        assert _META_MODULE.__UDBM_VERSION__
        assert _META_MODULE.__UDBM_COMMIT__
        assert _META_MODULE.__UDBM_COMMIT_TIME__
        assert _COMMIT_TIME_PATTERN.fullmatch(_META_MODULE.__UDBM_COMMIT_TIME__)
        assert _META_MODULE.__UCDD_VERSION__
        assert _META_MODULE.__UCDD_COMMIT__
        assert _META_MODULE.__UCDD_COMMIT_TIME__
        assert _COMMIT_TIME_PATTERN.fullmatch(_META_MODULE.__UCDD_COMMIT_TIME__)
