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
]
