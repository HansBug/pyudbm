import pytest

from pyudbm.core.constraints import *


@pytest.mark.unittest
class TestConstraints:

    def test_dbm_bound2raw(self):
        assert dbm_bound2raw(5, Strictness.STRICT) == 10
        assert dbm_bound2raw(5, Strictness.WEAK) == 11

    def test_dbm_boundbool2raw(self):
        assert dbm_boundbool2raw(5, True) == 10
        assert dbm_boundbool2raw(5, False) == 11

    def test_dbm_raw2bound(self):
        assert dbm_raw2bound(10) == 5
        assert dbm_raw2bound(11) == 5

    def test_dbm_weak_raw(self):
        assert dbm_weak_raw(10) == 11

    def test_dbm_strict_raw(self):
        assert dbm_strict_raw(11) == 10

    def test_dbm_raw2strict(self):
        assert dbm_raw2strict(10) == Strictness.STRICT
        assert dbm_raw2strict(11) == Strictness.WEAK

    def test_dbm_raw_is_strict(self):
        assert dbm_raw_is_strict(10) == True
        assert dbm_raw_is_strict(11) == False

    def test_dbm_raw_is_weak(self):
        assert dbm_raw_is_weak(10) == False
        assert dbm_raw_is_weak(11) == True

    def test_dbm_neg_raw(self):
        assert dbm_neg_raw(10) == -9
        assert dbm_neg_raw(11) == -10

    def test_dbm_weak_neg_raw(self):
        assert dbm_weak_neg_raw(11) == -9

    def test_dbm_is_valid_raw(self):
        assert dbm_is_valid_raw(10) == True
        assert dbm_is_valid_raw(DBM_LS_INFINITY) == True
        assert dbm_is_valid_raw(DBM_LE_OVERFLOW) == False

    def test_dbm_add_raw_raw(self):
        assert dbm_add_raw_raw(10, 11) == 20
        assert dbm_add_raw_raw(10, DBM_LS_INFINITY) == DBM_LS_INFINITY

    def test_dbm_add_raw_finite(self):
        assert dbm_add_raw_finite(10, 11) == 20
        assert dbm_add_raw_finite(DBM_LS_INFINITY, 11) == DBM_LS_INFINITY

    def test_dbm_add_finite_finite(self):
        assert dbm_add_finite_finite(10, 11) == 20

    def test_dbm_add_finite_weak(self):
        assert dbm_add_finite_weak(11, 11) == 21

    def test_dbm_raw_inc(self):
        assert dbm_raw_inc(10, 5) == 15
        assert dbm_raw_inc(DBM_LS_INFINITY, 5) == DBM_LS_INFINITY

    def test_dbm_raw_dec(self):
        assert dbm_raw_dec(15, 5) == 10
        assert dbm_raw_dec(DBM_LS_INFINITY, 5) == DBM_LS_INFINITY

    def test_dbm_constraint(self):
        c = dbm_constraint(1, 2, 5, Strictness.STRICT)
        assert c.i == 1
        assert c.j == 2
        assert c.value == 10

    def test_dbm_constraint2(self):
        c = dbm_constraint2(1, 2, 5, True)
        assert c.i == 1
        assert c.j == 2
        assert c.value == 10

    def test_dbm_neg_constraint(self):
        c = dbm_constraint(1, 2, 5, Strictness.STRICT)
        neg_c = dbm_neg_constraint(c)
        assert neg_c.i == 2
        assert neg_c.j == 1
        assert neg_c.value == -9

    def test_dbm_are_constraints_equal(self):
        c1 = dbm_constraint(1, 2, 5, Strictness.STRICT)
        c2 = dbm_constraint(1, 2, 5, Strictness.STRICT)
        c3 = dbm_constraint(1, 2, 5, Strictness.WEAK)
        assert dbm_are_constraints_equal(c1, c2) == True
        assert dbm_are_constraints_equal(c1, c3) == False

    def test_constraint_equality(self):
        c1 = dbm_constraint(1, 2, 5, Strictness.STRICT)
        c2 = dbm_constraint(1, 2, 5, Strictness.STRICT)
        c3 = dbm_constraint(1, 2, 5, Strictness.WEAK)
        assert c1 == c2
        assert c1 != c3

    def test_constraint_negation(self):
        c = dbm_constraint(1, 2, 5, Strictness.STRICT)
        neg_c = -c
        assert neg_c.i == 2
        assert neg_c.j == 1
        assert neg_c.value == -9

    def test_constants(self):
        assert DBM_INFINITY > 0
        assert DBM_OVERFLOW > 0
        assert DBM_LE_ZERO == 1
        assert DBM_LS_INFINITY > DBM_INFINITY
        assert DBM_LS_INFINITY == DBM_INFINITY * 2
        assert DBM_LE_OVERFLOW > DBM_OVERFLOW
        assert DBM_LE_OVERFLOW == DBM_LS_INFINITY // 2

    def test_dbm_add_finite_raw_cases(self):
        assert dbm_add_finite_raw(10, DBM_LS_INFINITY) == DBM_LS_INFINITY
        assert dbm_add_raw_finite(DBM_LS_INFINITY, 10) == DBM_LS_INFINITY
        # dont use dbm_add_finite_raw(DBM_LS_INFINITY, 10), that is unexpected behaviour
        assert dbm_add_raw_raw(DBM_LS_INFINITY, DBM_LS_INFINITY) == DBM_LS_INFINITY

    def test_dbm_add_raw_extreme_cases(self):
        assert dbm_add_raw_raw(DBM_LE_ZERO, 10) == 10
        assert dbm_add_raw_raw(10, DBM_LE_ZERO) == 10

        assert dbm_add_raw_raw(DBM_LS_INFINITY, 10) == DBM_LS_INFINITY
        assert dbm_add_raw_raw(10, DBM_LS_INFINITY) == DBM_LS_INFINITY

    def test_dbm_raw_arithmetic_with_infinity(self):
        assert dbm_raw_inc(DBM_LS_INFINITY, 10) == DBM_LS_INFINITY
        assert dbm_raw_dec(DBM_LS_INFINITY, 10) == DBM_LS_INFINITY

        assert dbm_raw_inc(DBM_LS_INFINITY, 10) == DBM_LS_INFINITY
        assert dbm_raw_dec(DBM_LS_INFINITY, 10) == DBM_LS_INFINITY

    def test_dbm_raw_comparison_with_infinity(self):
        assert dbm_is_valid_raw(DBM_LS_INFINITY)
        assert dbm_is_valid_raw(DBM_LS_INFINITY)
        assert not dbm_is_valid_raw(DBM_LE_OVERFLOW)
