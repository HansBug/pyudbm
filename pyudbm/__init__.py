"""
Public package interface for :mod:`pyudbm`.

The package now exposes the restored high-level compatibility API inspired by
the historical UDBM Python binding.
"""

from .config.meta import __VERSION__ as __version__

__all__ = ["__version__"]

try:
    from .binding import DBM, Clock, Constraint, Context, Federation, FloatValuation, IntValuation, Valuation, VariableDifference
except ModuleNotFoundError as err:
    if not err.name or not err.name.startswith("pyudbm.binding."):
        raise
else:
    __all__.extend(
        [
            "DBM",
            "Clock",
            "Constraint",
            "Context",
            "Federation",
            "FloatValuation",
            "IntValuation",
            "Valuation",
            "VariableDifference",
        ]
    )
