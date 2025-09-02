from typing import List, Tuple

import numpy as np

# noinspection PyUnresolvedReferences
from .._core._c_udbm_dbm import (
    _c_dbm_init, _c_dbm_zero, _c_dbm_isEqualToInit, _c_dbm_hasZero,
    _c_dbm_isEqualToZero, _c_dbm_convexUnion, _c_dbm_intersection,
    _c_dbm_relaxedIntersection, _c_dbm_haveIntersection, _c_dbm_constrain,
    _c_dbm_constrainN, _c_dbm_constrainIndexedN,
    _c_dbm_constrain1, _c_dbm_constrainC, _c_dbm_up, _c_dbm_up_stop,
    _c_dbm_downFrom, _c_dbm_down, _c_dbm_down_stop, _c_dbm_updateValue,
    _c_dbm_freeClock, _c_dbm_freeUp, _c_dbm_freeAllUp, _c_dbm_isFreedAllUp,
    _c_dbm_testFreeAllDown, _c_dbm_freeDown, _c_dbm_freeAllDown,
    _c_dbm_updateClock, _c_dbm_updateIncrement, _c_dbm_update,
    _c_dbm_constrainClock, _c_dbm_satisfies, _c_dbm_isEmpty, _c_dbm_close,
    _c_dbm_isClosed, _c_dbm_closex, _c_dbm_close1, _c_dbm_closeij,
    _c_dbm_tighten, _c_dbm_isUnbounded, _c_dbm_relation, _c_dbm_isSubsetEq,
    _c_dbm_isSupersetEq, _c_dbm_relaxUpClock, _c_dbm_relaxDownClock,
    _c_dbm_relaxAll, _c_dbm_relaxUp, _c_dbm_relaxDown, _c_dbm_tightenDown,
    _c_dbm_tightenUp, _c_dbm_copy, _c_dbm_areEqual, _c_dbm_hash,
    _c_dbm_isPointIncluded, _c_dbm_isRealPointIncluded,
    _c_dbm_extrapolateMaxBounds, _c_dbm_diagonalExtrapolateMaxBounds,
    _c_dbm_extrapolateLUBounds, _c_dbm_diagonalExtrapolateLUBounds,
    _c_dbm_shrinkExpand, _c_dbm_updateDBM, _c_dbm_swapClocks,
    _c_dbm_isDiagonalOK, _c_dbm_isValid, _c_dbm_relation2string,
    _c_dbm_getMaxRange
)

__all__ = ['DBM']


class DBM:
    def __init__(self, dim: int):
        self.dim = dim
        self.dbm = np.zeros((dim, dim), dtype=np.int32)
        _c_dbm_init(self.dbm, dim)

    def zero(self):
        _c_dbm_zero(self.dbm, self.dim)
        return self

    def is_equal_to_init(self) -> bool:
        return _c_dbm_isEqualToInit(self.dbm, self.dim)

    def has_zero(self) -> bool:
        return _c_dbm_hasZero(self.dbm, self.dim)

    def is_equal_to_zero(self) -> bool:
        return _c_dbm_isEqualToZero(self.dbm, self.dim)

    def convex_union(self, other: 'DBM'):
        _c_dbm_convexUnion(self.dbm, other.dbm, self.dim)

    def intersection(self, other: 'DBM') -> bool:
        return _c_dbm_intersection(self.dbm, other.dbm, self.dim)

    def relaxed_intersection(self, other1: 'DBM', other2: 'DBM') -> bool:
        return _c_dbm_relaxedIntersection(self.dbm, other1.dbm, other2.dbm, self.dim)

    def have_intersection(self, other: 'DBM') -> bool:
        return _c_dbm_haveIntersection(self.dbm, other.dbm, self.dim)

    def constrain(self, i: int, j: int, constraint: int, touched: np.ndarray) -> bool:
        return _c_dbm_constrain(self.dbm, self.dim, i, j, constraint, touched)

    def constrain_n(self, constraints: List[Tuple[int, int, int]]) -> bool:
        constraints_array = np.array(constraints, dtype=[('i', np.int32), ('j', np.int32), ('value', np.int32)])
        return _c_dbm_constrainN(self.dbm, self.dim, constraints_array, len(constraints))

    def constrain_indexed_n(self, index_table: np.ndarray, constraints: List[Tuple[int, int, int]]) -> bool:
        constraints_array = np.array(constraints, dtype=[('i', np.int32), ('j', np.int32), ('value', np.int32)])
        return _c_dbm_constrainIndexedN(self.dbm, self.dim, index_table, constraints_array, len(constraints))

    def constrain1(self, i: int, j: int, constraint: int) -> bool:
        return _c_dbm_constrain1(self.dbm, self.dim, i, j, constraint)

    def constrain_c(self, constraint: Tuple[int, int, int]) -> bool:
        i, j, value = constraint
        return _c_dbm_constrainC(self.dbm, self.dim, (i, j, value))

    def up(self):
        _c_dbm_up(self.dbm, self.dim)
        return self

    def up_stop(self, stopped: np.ndarray):
        _c_dbm_up_stop(self.dbm, self.dim, stopped)
        return self

    def down_from(self, j0: int):
        _c_dbm_downFrom(self.dbm, self.dim, j0)
        return self

    def down(self):
        _c_dbm_down(self.dbm, self.dim)
        return self

    def down_stop(self, stopped: np.ndarray):
        _c_dbm_down_stop(self.dbm, self.dim, stopped)
        return self

    def update_value(self, index: int, value: int):
        _c_dbm_updateValue(self.dbm, self.dim, index, value)
        return self

    def free_clock(self, index: int):
        _c_dbm_freeClock(self.dbm, self.dim, index)
        return self

    def free_up(self, index: int):
        _c_dbm_freeUp(self.dbm, self.dim, index)
        return self

    def free_all_up(self):
        _c_dbm_freeAllUp(self.dbm, self.dim)
        return self

    def is_freed_all_up(self) -> bool:
        return _c_dbm_isFreedAllUp(self.dbm, self.dim)

    def test_free_all_down(self) -> int:
        return _c_dbm_testFreeAllDown(self.dbm, self.dim)

    def free_down(self, index: int):
        _c_dbm_freeDown(self.dbm, self.dim, index)
        return self

    def free_all_down(self):
        _c_dbm_freeAllDown(self.dbm, self.dim)
        return self

    def update_clock(self, i: int, j: int):
        _c_dbm_updateClock(self.dbm, self.dim, i, j)
        return self

    def update_increment(self, i: int, value: int):
        _c_dbm_updateIncrement(self.dbm, self.dim, i, value)
        return self

    def update(self, i: int, j: int, value: int):
        _c_dbm_update(self.dbm, self.dim, i, j, value)
        return self

    def constrain_clock(self, clock: int, value: int) -> bool:
        return _c_dbm_constrainClock(self.dbm, self.dim, clock, value)

    def satisfies(self, i: int, j: int, constraint: int) -> bool:
        return _c_dbm_satisfies(self.dbm, self.dim, i, j, constraint)

    def is_empty(self) -> bool:
        return _c_dbm_isEmpty(self.dbm, self.dim)

    def close(self) -> bool:
        return _c_dbm_close(self.dbm, self.dim)

    def is_closed(self) -> bool:
        return _c_dbm_isClosed(self.dbm, self.dim)

    def closex(self, touched: np.ndarray) -> bool:
        return _c_dbm_closex(self.dbm, self.dim, touched)

    def close1(self, k: int) -> bool:
        return _c_dbm_close1(self.dbm, self.dim, k)

    def closeij(self, i: int, j: int):
        _c_dbm_closeij(self.dbm, self.dim, i, j)
        return self

    def tighten(self, i: int, j: int, c: int):
        _c_dbm_tighten(self.dbm, self.dim, i, j, c)
        return self

    def is_unbounded(self) -> bool:
        return _c_dbm_isUnbounded(self.dbm, self.dim)

    def relation(self, other: 'DBM') -> int:
        return _c_dbm_relation(self.dbm, other.dbm, self.dim)

    def is_subset_eq(self, other: 'DBM') -> bool:
        return _c_dbm_isSubsetEq(self.dbm, other.dbm, self.dim)

    def is_superset_eq(self, other: 'DBM') -> bool:
        return _c_dbm_isSupersetEq(self.dbm, other.dbm, self.dim)

    def relax_up_clock(self, clock: int):
        _c_dbm_relaxUpClock(self.dbm, self.dim, clock)
        return self

    def relax_down_clock(self, clock: int):
        _c_dbm_relaxDownClock(self.dbm, self.dim, clock)
        return self

    def relax_all(self):
        _c_dbm_relaxAll(self.dbm, self.dim)
        return self

    def relax_up(self):
        _c_dbm_relaxUp(self.dbm, self.dim)
        return self

    def relax_down(self):
        _c_dbm_relaxDown(self.dbm, self.dim)
        return self

    def tighten_down(self) -> bool:
        return _c_dbm_tightenDown(self.dbm, self.dim)

    def tighten_up(self) -> bool:
        return _c_dbm_tightenUp(self.dbm, self.dim)

    def copy(self, other: 'DBM'):
        _c_dbm_copy(self.dbm, other.dbm, self.dim)
        return self

    def are_equal(self, other: 'DBM') -> bool:
        return _c_dbm_areEqual(self.dbm, other.dbm, self.dim)

    def hash(self) -> int:
        return _c_dbm_hash(self.dbm, self.dim)

    def is_point_included(self, pt: np.ndarray) -> bool:
        return _c_dbm_isPointIncluded(pt, self.dbm, self.dim)

    def is_real_point_included(self, pt: np.ndarray) -> bool:
        return _c_dbm_isRealPointIncluded(pt, self.dbm, self.dim)

    def extrapolate_max_bounds(self, max_bounds: np.ndarray):
        _c_dbm_extrapolateMaxBounds(self.dbm, self.dim, max_bounds)
        return self

    def diagonal_extrapolate_max_bounds(self, max_bounds: np.ndarray):
        _c_dbm_diagonalExtrapolateMaxBounds(self.dbm, self.dim, max_bounds)
        return self

    def extrapolate_lu_bounds(self, lower: np.ndarray, upper: np.ndarray):
        _c_dbm_extrapolateLUBounds(self.dbm, self.dim, lower, upper)
        return self

    def diagonal_extrapolate_lu_bounds(self, lower: np.ndarray, upper: np.ndarray):
        _c_dbm_diagonalExtrapolateLUBounds(self.dbm, self.dim, lower, upper)
        return self

    def shrink_expand(self, other: 'DBM', bit_src: np.ndarray, bit_dst: np.ndarray, table: np.ndarray) -> int:
        return _c_dbm_shrinkExpand(self.dbm, other.dbm, self.dim, bit_src, bit_dst, len(bit_src), table)

    def update_dbm(self, other: 'DBM', cols: np.ndarray):
        _c_dbm_updateDBM(self.dbm, other.dbm, self.dim, other.dim, cols)
        return self

    def swap_clocks(self, x: int, y: int):
        _c_dbm_swapClocks(self.dbm, self.dim, x, y)
        return self

    def is_diagonal_ok(self) -> bool:
        return _c_dbm_isDiagonalOK(self.dbm, self.dim)

    def is_valid(self) -> bool:
        return _c_dbm_isValid(self.dbm, self.dim)

    @staticmethod
    def relation_to_string(rel: int) -> str:
        return _c_dbm_relation2string(rel)

    def get_max_range(self) -> int:
        return _c_dbm_getMaxRange(self.dbm, self.dim)

    def __hash__(self):
        return self.hash()

    def __eq__(self, other):
        return isinstance(other, DBM) and self.are_equal(other)
