"""
Package metadata for :mod:`pyudbm`.

This module stores package-level constants consumed by packaging glue and
lightweight runtime introspection.
"""

#: Project title, expected to be ``pyudbm``.
__TITLE__ = "pyudbm"

#: Project version.
__VERSION__ = "0.0.1"

#: Short description included in ``setup.py``.
__DESCRIPTION__ = 'Python wrapper for Uppaal UDBM.'

#: Project author.
__AUTHOR__ = "HansBug"

#: Project author email address.
__AUTHOR_EMAIL__ = "hansbug@buaa.edu.cn"

#: Declared version of the vendored ``UUtils`` submodule.
__UUTILS_VERSION__: str = "2.0.6"

#: Current commit hash of the vendored ``UUtils`` submodule.
__UUTILS_COMMIT__: str = "636dcbb83d8568e8fb006ac9af493c88985d132d"

#: Current commit time of the vendored ``UUtils`` submodule.
__UUTILS_COMMIT_TIME__: str = "2024-12-03 11:25:12 +0100"

#: Declared version of the vendored ``UDBM`` submodule.
__UDBM_VERSION__: str = "2.0.14"

#: Current commit hash of the vendored ``UDBM`` submodule.
__UDBM_COMMIT__: str = "d83b703126fb88b3565c71cca68e360227dfb192"

#: Current commit time of the vendored ``UDBM`` submodule.
__UDBM_COMMIT_TIME__: str = "2023-09-15 10:08:41 +0200"

#: Declared version of the vendored ``UCDD`` submodule.
__UCDD_VERSION__: str = "0.2.1"

#: Current commit hash of the vendored ``UCDD`` submodule.
__UCDD_COMMIT__: str = "b2f12c0f29eda0395d4a4bf2c1ba395d0732e95e"

#: Current commit time of the vendored ``UCDD`` submodule.
__UCDD_COMMIT_TIME__: str = "2023-09-15 10:15:16 +0200"
