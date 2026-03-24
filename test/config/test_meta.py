import re

import pytest

from pyudbm.config.meta import (
    __TITLE__,
    __UCDD_COMMIT__,
    __UCDD_COMMIT_TIME__,
    __UCDD_VERSION__,
    __UDBM_COMMIT__,
    __UDBM_COMMIT_TIME__,
    __UDBM_VERSION__,
    __UUTILS_COMMIT__,
    __UUTILS_COMMIT_TIME__,
    __UUTILS_VERSION__,
)

_VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+(?:[A-Za-z0-9.+_-]+)?$')
_COMMIT_PATTERN = re.compile(r'^[0-9a-f]{40}$')
_COMMIT_TIME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}$')


@pytest.mark.unittest
class TestConfigMeta:
    def test_title(self):
        assert __TITLE__ == 'pyudbm'

    def test_upstream_metadata_present(self):
        assert _VERSION_PATTERN.fullmatch(__UUTILS_VERSION__)
        assert _COMMIT_PATTERN.fullmatch(__UUTILS_COMMIT__)
        assert _COMMIT_TIME_PATTERN.fullmatch(__UUTILS_COMMIT_TIME__)
        assert _VERSION_PATTERN.fullmatch(__UDBM_VERSION__)
        assert _COMMIT_PATTERN.fullmatch(__UDBM_COMMIT__)
        assert _COMMIT_TIME_PATTERN.fullmatch(__UDBM_COMMIT_TIME__)
        assert _VERSION_PATTERN.fullmatch(__UCDD_VERSION__)
        assert _COMMIT_PATTERN.fullmatch(__UCDD_COMMIT__)
        assert _COMMIT_TIME_PATTERN.fullmatch(__UCDD_COMMIT_TIME__)
