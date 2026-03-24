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

from .udbm import DBM, Clock, Constraint, Context, Federation, FloatValuation, IntValuation, Valuation, VariableDifference
from .ucdd import BDDTraceSet, CDD, CDDContext, CDDExtraction, CDDBool, CDDClock, CDDLevelInfo
from .visual import PlotResult, plot_dbm, plot_federation

__all__ = [
    "DBM",
    "Clock",
    "Constraint",
    "CDDBool",
    "CDD",
    "CDDClock",
    "CDDContext",
    "CDDExtraction",
    "CDDLevelInfo",
    "Context",
    "Federation",
    "FloatValuation",
    "IntValuation",
    "PlotResult",
    "BDDTraceSet",
    "Valuation",
    "VariableDifference",
    "plot_dbm",
    "plot_federation",
]
