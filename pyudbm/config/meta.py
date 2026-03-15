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

#: Declared version of the vendored ``UDBM`` submodule.
__UDBM_VERSION__: str = "2.0.14"

#: Current commit hash of the vendored ``UDBM`` submodule.
__UDBM_COMMIT__: str = "d83b703126fb88b3565c71cca68e360227dfb192"
