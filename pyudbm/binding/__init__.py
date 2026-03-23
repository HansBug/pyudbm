"""
Binding namespace for :mod:`pyudbm`.

This subpackage exposes the restored high-level API so users may import either
from :mod:`pyudbm` or directly from :mod:`pyudbm.binding`.

The actual semantics live in :mod:`pyudbm.binding.udbm`; this module simply
re-exports the public Python binding surface so that both of the following
import styles stay valid.

Example::

    >>> import pyudbm
    >>> import pyudbm.binding
    >>> pyudbm.Context is pyudbm.binding.Context
    True
    >>> pyudbm.Federation is pyudbm.binding.Federation
    True
"""

import os
import sys


_WINDOWS_DLL_DIR_HANDLES = []


def _prepare_windows_dll_search_paths():
    if sys.platform != "win32" or not hasattr(os, "add_dll_directory"):
        return

    candidate_dirs = []
    package_dir = os.path.dirname(__file__)
    candidate_dirs.append(package_dir)

    mingw_bin = os.environ.get("MINGW_BIN")
    if mingw_bin:
        candidate_dirs.append(mingw_bin)

    candidate_dirs.extend([
        r"C:\ProgramData\mingw64\mingw64\bin",
        r"C:\mingw64\bin",
    ])

    seen = set()
    for path in candidate_dirs:
        if not path:
            continue
        norm = os.path.normcase(os.path.abspath(path))
        if norm in seen or not os.path.isdir(path):
            continue
        seen.add(norm)
        _WINDOWS_DLL_DIR_HANDLES.append(os.add_dll_directory(path))


_prepare_windows_dll_search_paths()

from .udbm import DBM, Clock, Constraint, Context, Federation, FloatValuation, IntValuation, Valuation, VariableDifference
from .visual import PlotResult, plot_dbm, plot_federation

__all__ = [
    "DBM",
    "Clock",
    "Constraint",
    "Context",
    "Federation",
    "FloatValuation",
    "IntValuation",
    "PlotResult",
    "Valuation",
    "VariableDifference",
    "plot_dbm",
    "plot_federation",
]
