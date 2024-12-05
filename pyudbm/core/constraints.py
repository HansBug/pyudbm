from typing import Protocol, Any

# noinspection PyUnresolvedReferences,PyProtectedMember
from .._core._c_udbm_constraints import (
    _c_dbm_bound2raw, _c_dbm_boundbool2raw, _c_dbm_raw2bound,
    _c_dbm_weakRaw, _c_dbm_strictRaw, _c_dbm_raw2strict,
    _c_dbm_rawIsStrict, _c_dbm_rawIsWeak, _c_dbm_negRaw,
    _c_dbm_weakNegRaw, _c_dbm_isValidRaw, _c_dbm_addRawRaw,
    _c_dbm_addRawFinite, _c_dbm_addFiniteRaw, _c_dbm_addFiniteFinite,
    _c_dbm_addFiniteWeak, _c_dbm_rawInc, _c_dbm_rawDec,
    _c_dbm_constraint, _c_dbm_constraint2, _c_dbm_negConstraint,
    _c_dbm_areConstraintsEqual, _CStrictness, _CConstraint,
    DBM_INFINITY, DBM_OVERFLOW,
    DBM_LE_ZERO, DBM_LS_INFINITY, DBM_LE_OVERFLOW,
)
from ..utils import EnumProtocol

__all__ = [
    'Strictness',
    'Constraint',
    'dbm_bound2raw',
    'dbm_boundbool2raw',
    'dbm_raw2bound',
    'dbm_weak_raw',
    'dbm_strict_raw',
    'dbm_raw2strict',
    'dbm_raw_is_strict',
    'dbm_raw_is_weak',
    'dbm_neg_raw',
    'dbm_weak_neg_raw',
    'dbm_is_valid_raw',
    'dbm_add_raw_raw',
    'dbm_add_raw_finite',
    'dbm_add_finite_raw',
    'dbm_add_finite_finite',
    'dbm_add_finite_weak',
    'dbm_raw_inc',
    'dbm_raw_dec',
    'dbm_constraint',
    'dbm_constraint2',
    'dbm_neg_constraint',
    'dbm_are_constraints_equal',
    'DBM_INFINITY',
    'DBM_OVERFLOW',
    'DBM_LE_ZERO',
    'DBM_LS_INFINITY',
    'DBM_LE_OVERFLOW',
]


class _StrictnessProtocol(EnumProtocol['_StrictnessTyping']):
    STRICT: '_StrictnessProtocol'
    WEAK: '_StrictnessProtocol'


class _ConstraintProtocol(Protocol):
    """
    Represents a time constraint between two clock variables in a Difference Bound Matrix (DBM).

    Fields:
        i (int): Index of the first clock variable
        j (int): Index of the second clock variable
        value (int): The bound value of the constraint

    The constraint represents a relation of the form x_i - x_j <= value
    """

    i: int
    j: int
    value: int

    def __call__(self, i: int, j: int, value: int):
        """Create an empty constraint"""
        ...  # pragma: no cover

    def __eq__(self, other: Any) -> bool:
        """Check if two constraints are equal"""
        ...  # pragma: no cover

    def __neg__(self: '_ConstraintProtocol') -> '_ConstraintProtocol':
        """Negate the constraint"""
        ...  # pragma: no cover

    def __repr__(self) -> str:
        """String representation of the constraint"""
        ...  # pragma: no cover


Strictness: _StrictnessProtocol = _CStrictness
Constraint: _ConstraintProtocol = _CConstraint


def dbm_bound2raw(bound: int, strict: Strictness) -> int:
    """
    Encode bound into raw representation.

    :param bound: The bound to encode.
    :type bound: int
    :param strict: The strictness of the bound.
    :type strict: Strictness
    :return: Encoded raw representation.
    :rtype: int
    """
    return _c_dbm_bound2raw(bound, strict)


def dbm_boundbool2raw(bound: int, is_strict: bool) -> int:
    """
    Encode bound into raw representation based on a boolean.

    :param bound: The bound to encode.
    :type bound: int
    :param is_strict: True if the bound is strict.
    :type is_strict: bool
    :return: Encoded raw representation.
    :rtype: int
    """
    return _c_dbm_boundbool2raw(bound, is_strict)


def dbm_raw2bound(raw: int) -> int:
    """
    Decode raw representation to get the bound value.

    :param raw: The encoded constraint.
    :type raw: int
    :return: The decoded bound value.
    :rtype: int
    """
    return _c_dbm_raw2bound(raw)


def dbm_weak_raw(raw: int) -> int:
    """
    Make an encoded constraint weak.

    :param raw: The raw constraint.
    :type raw: int
    :return: Weak raw constraint.
    :rtype: int
    """
    return _c_dbm_weakRaw(raw)


def dbm_strict_raw(raw: int) -> int:
    """
    Make an encoded constraint strict.

    :param raw: The raw constraint.
    :type raw: int
    :return: Strict raw constraint.
    :rtype: int
    """
    return _c_dbm_strictRaw(raw)


def dbm_raw2strict(raw: int) -> Strictness:
    """
    Decode raw representation to get strictness.

    :param raw: The encoded constraint.
    :type raw: int
    :return: The decoded strictness.
    :rtype: Strictness
    """
    return _c_dbm_raw2strict(raw)


def dbm_raw_is_strict(raw: int) -> bool:
    """
    Check if the constraint is strict.

    :param raw: The encoded constraint.
    :type raw: int
    :return: True if the constraint is strict.
    :rtype: bool
    """
    return _c_dbm_rawIsStrict(raw)


def dbm_raw_is_weak(raw: int) -> bool:
    """
    Check if the constraint is weak.

    :param raw: The encoded constraint.
    :type raw: int
    :return: True if the constraint is weak.
    :rtype: bool
    """
    return _c_dbm_rawIsWeak(raw)


def dbm_neg_raw(c: int) -> int:
    """
    Negate a constraint.

    :param c: The raw constraint.
    :type c: int
    :return: Negated raw constraint.
    :rtype: int
    """
    return _c_dbm_negRaw(c)


def dbm_weak_neg_raw(c: int) -> int:
    """
    Weak negate a constraint.

    :param c: The raw constraint.
    :type c: int
    :return: Weak negated raw constraint.
    :rtype: int
    """
    return _c_dbm_weakNegRaw(c)


def dbm_is_valid_raw(x: int) -> bool:
    """
    Check if a raw bound is valid.

    :param x: The encoded constraint.
    :type x: int
    :return: True if valid.
    :rtype: bool
    """
    return _c_dbm_isValidRaw(x)


def dbm_add_raw_raw(x: int, y: int) -> int:
    """
    Add two raw constraints.

    :param x: The first raw constraint.
    :type x: int
    :param y: The second raw constraint.
    :type y: int
    :return: The result of addition.
    :rtype: int
    """
    return _c_dbm_addRawRaw(x, y)


def dbm_add_raw_finite(x: int, y: int) -> int:
    """
    Add a raw constraint and a finite constraint.

    :param x: The raw constraint.
    :type x: int
    :param y: The finite constraint.
    :type y: int
    :return: The result of addition.
    :rtype: int
    """
    return _c_dbm_addRawFinite(x, y)


def dbm_add_finite_raw(x: int, y: int) -> int:
    """
    Add a finite constraint and a raw constraint.

    :param x: The finite constraint.
    :type x: int
    :param y: The raw constraint.
    :type y: int
    :return: The result of addition.
    :rtype: int
    """
    return _c_dbm_addFiniteRaw(x, y)


def dbm_add_finite_finite(x: int, y: int) -> int:
    """
    Add two finite constraints.

    :param x: The first finite constraint.
    :type x: int
    :param y: The second finite constraint.
    :type y: int
    :return: The result of addition.
    :rtype: int
    """
    return _c_dbm_addFiniteFinite(x, y)


def dbm_add_finite_weak(x: int, y: int) -> int:
    """
    Specialized addition of finite constraints.

    :param x: The first finite constraint.
    :type x: int
    :param y: The second finite constraint.
    :type y: int
    :return: The result of addition.
    :rtype: int
    """
    return _c_dbm_addFiniteWeak(x, y)


def dbm_raw_inc(c: int, i: int) -> int:
    """
    Increment a raw constraint.

    :param c: The raw constraint.
    :type c: int
    :param i: The increment value.
    :type i: int
    :return: The incremented raw constraint.
    :rtype: int
    """
    return _c_dbm_rawInc(c, i)


def dbm_raw_dec(c: int, d: int) -> int:
    """
    Decrement a raw constraint.

    :param c: The raw constraint.
    :type c: int
    :param d: The decrement value.
    :type d: int
    :return: The decremented raw constraint.
    :rtype: int
    """
    return _c_dbm_rawDec(c, d)


def dbm_constraint(i: int, j: int, bound: int, strictness: Strictness) -> Constraint:
    """
    Create a constraint.

    :param i: The first index.
    :type i: int
    :param j: The second index.
    :type j: int
    :param bound: The bound value.
    :type bound: int
    :param strictness: The strictness of the constraint.
    :type strictness: Strictness
    :return: The created constraint.
    :rtype: Constraint
    """
    return _c_dbm_constraint(i, j, bound, strictness)


def dbm_constraint2(i: int, j: int, bound: int, is_strict: bool) -> Constraint:
    """
    Create a constraint with strictness flag.

    :param i: The first index.
    :type i: int
    :param j: The second index.
    :type j: int
    :param bound: The bound value.
    :type bound: int
    :param is_strict: True if the constraint is strict.
    :type is_strict: bool
    :return: The created constraint.
    :rtype: Constraint
    """
    return _c_dbm_constraint2(i, j, bound, is_strict)


def dbm_neg_constraint(c: Constraint) -> Constraint:
    """
    Negate a constraint.

    :param c: The constraint to negate.
    :type c: Constraint
    :return: The negated constraint.
    :rtype: Constraint
    """
    return _c_dbm_negConstraint(c)


def dbm_are_constraints_equal(c1: Constraint, c2: Constraint) -> bool:
    """
    Check if two constraints are equal.

    :param c1: The first constraint.
    :type c1: Constraint
    :param c2: The second constraint.
    :type c2: Constraint
    :return: True if equal.
    :rtype: bool
    """
    return _c_dbm_areConstraintsEqual(c1, c2)
