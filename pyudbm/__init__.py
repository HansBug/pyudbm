"""
Public package interface for :mod:`pyudbm`.

The package now exposes the restored high-level compatibility API inspired by
the historical UDBM Python binding.
"""

from .config.meta import __VERSION__ as __version__
from .binding import DBM, Clock, Constraint, Context, Federation, FloatValuation, IntValuation, Valuation, VariableDifference

__all__ = [
    "DBM",
    "Clock",
    "Constraint",
    "Context",
    "Federation",
    "FloatValuation",
    "IntValuation",
    "Valuation",
    "VariableDifference",
    "__version__",
]
