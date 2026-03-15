import os

import pytest

from pyudbm.config.meta import __TITLE__, __UDBM_COMMIT__, __UDBM_VERSION__
from tools.udbm_version import resolve_udbm_commit, resolve_udbm_version


_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
_UDBM_DIR = os.path.join(_PROJECT_ROOT, "UDBM")


@pytest.mark.unittest
class TestConfigMeta:
    def test_title(self):
        assert __TITLE__ == 'pyudbm'

    def test_udbm_version(self):
        assert isinstance(__UDBM_VERSION__, str)
        assert __UDBM_VERSION__ == resolve_udbm_version(_UDBM_DIR)

    def test_udbm_commit(self):
        assert isinstance(__UDBM_COMMIT__, str)
        assert __UDBM_COMMIT__ == resolve_udbm_commit(_UDBM_DIR)
