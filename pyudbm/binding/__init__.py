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
from .utap import (
    Branchpoint,
    Diagnostic,
    Edge,
    Expectation,
    Expression,
    FeatureFlags,
    Location,
    MAPPED_FIELDS,
    MAPPED_FIELD_NOTES,
    ModelDocument,
    Option,
    ParsedQuery,
    ParsedQueryExpectation,
    Position,
    Process,
    Query,
    Resource,
    Symbol,
    Template,
    TypeInfo,
    UNMAPPED_FIELDS,
    UNMAPPED_FIELD_REASONS,
    builtin_declarations,
    load_query,
    load_xml,
    load_xta,
    loads_query,
    loads_xml,
    loads_xta,
    parse_query,
)
from .visual import PlotResult, plot_dbm, plot_federation

__all__ = [
    "Diagnostic",
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
    "Branchpoint",
    "Edge",
    "Expectation",
    "Expression",
    "FeatureFlags",
    "Federation",
    "FloatValuation",
    "IntValuation",
    "Location",
    "MAPPED_FIELDS",
    "MAPPED_FIELD_NOTES",
    "ModelDocument",
    "Option",
    "ParsedQuery",
    "ParsedQueryExpectation",
    "PlotResult",
    "Position",
    "Process",
    "Query",
    "BDDTraceSet",
    "Resource",
    "Symbol",
    "Template",
    "TypeInfo",
    "UNMAPPED_FIELDS",
    "UNMAPPED_FIELD_REASONS",
    "Valuation",
    "VariableDifference",
    "builtin_declarations",
    "load_query",
    "load_xml",
    "load_xta",
    "loads_query",
    "loads_xml",
    "loads_xta",
    "parse_query",
    "plot_dbm",
    "plot_federation",
]
