#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <dbm/dbm.h>

namespace py = pybind11;

PYBIND11_MODULE(_c_udbm_dbm, m) {
    m.doc() = "Python bindings for DBM operations";

    m.attr("CLOCKS_POSITIVE") = &CLOCKS_POSITIVE;

    m.def("_c_dbm_init", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf = dbm.request();
        dbm_init(static_cast<raw_t*>(buf.ptr), dim);
    }, "Initialize a DBM");

    m.def("_c_dbm_zero", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf = dbm.request();
        dbm_zero(static_cast<raw_t*>(buf.ptr), dim);
    }, "Set the DBM to zero");

    m.def("_c_dbm_isEqualToInit", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf = dbm.request();
        return dbm_isEqualToInit(static_cast<const raw_t*>(buf.ptr), dim);
    }, "Test if DBM is equal to initial state");

    m.def("_c_dbm_hasZero", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf = dbm.request();
        return dbm_hasZero(static_cast<const raw_t*>(buf.ptr), dim);
    }, "Test if DBM contains zero point");

    m.def("_c_dbm_isEqualToZero", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf = dbm.request();
        return dbm_isEqualToZero(static_cast<const raw_t*>(buf.ptr), dim);
    }, "Test if DBM is equal to zero");

    m.def("_c_dbm_convexUnion", [](py::array_t<raw_t> dbm1, py::array_t<raw_t> dbm2, cindex_t dim) {
        auto buf1 = dbm1.request();
        auto buf2 = dbm2.request();
        dbm_convexUnion(static_cast<raw_t*>(buf1.ptr), static_cast<const raw_t*>(buf2.ptr), dim);
    }, "Compute convex union of two DBMs");

    m.def("_c_dbm_intersection", [](py::array_t<raw_t> dbm1, py::array_t<raw_t> dbm2, cindex_t dim) {
        auto buf1 = dbm1.request();
        auto buf2 = dbm2.request();
        return dbm_intersection(static_cast<raw_t*>(buf1.ptr), static_cast<const raw_t*>(buf2.ptr), dim);
    }, "Compute intersection of two DBMs");

    m.def("_c_dbm_relaxedIntersection", [](py::array_t<raw_t> dst, py::array_t<raw_t> dbm1, py::array_t<raw_t> dbm2, cindex_t dim) {
        auto buf_dst = dst.request();
        auto buf1 = dbm1.request();
        auto buf2 = dbm2.request();
        return dbm_relaxedIntersection(static_cast<raw_t*>(buf_dst.ptr), static_cast<const raw_t*>(buf1.ptr), static_cast<const raw_t*>(buf2.ptr), dim);
    }, "Compute relaxed intersection of two DBMs");

    m.def("_c_dbm_haveIntersection", [](py::array_t<raw_t> dbm1, py::array_t<raw_t> dbm2, cindex_t dim) {
        auto buf1 = dbm1.request();
        auto buf2 = dbm2.request();
        return dbm_haveIntersection(static_cast<const raw_t*>(buf1.ptr), static_cast<const raw_t*>(buf2.ptr), dim);
    }, "Test if two DBMs have intersection");

    m.def("_c_dbm_constrain", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t i, cindex_t j, raw_t constraint, py::array_t<uint32_t> touched) {
        auto buf_dbm = dbm.request();
        auto buf_touched = touched.request();
        return dbm_constrain(static_cast<raw_t*>(buf_dbm.ptr), dim, i, j, constraint, static_cast<uint32_t*>(buf_touched.ptr));
    }, "Constrain a DBM with a constraint");

    m.def("_c_dbm_constrainN", [](py::array_t<raw_t> dbm, cindex_t dim, py::array_t<constraint_t> constraints, size_t n) {
        auto buf_dbm = dbm.request();
        auto buf_constraints = constraints.request();
        return dbm_constrainN(static_cast<raw_t*>(buf_dbm.ptr), dim, static_cast<const constraint_t*>(buf_constraints.ptr), n);
    }, "Constrain a DBM with several constraints");

    m.def("_c_dbm_constrainIndexedN", [](py::array_t<raw_t> dbm, cindex_t dim, py::array_t<cindex_t> indexTable, py::array_t<constraint_t> constraints, size_t n) {
        auto buf_dbm = dbm.request();
        auto buf_indexTable = indexTable.request();
        auto buf_constraints = constraints.request();
        return dbm_constrainIndexedN(static_cast<raw_t*>(buf_dbm.ptr), dim, static_cast<const cindex_t*>(buf_indexTable.ptr), static_cast<const constraint_t*>(buf_constraints.ptr), n);
    }, "Constrain a DBM with several constraints using an index table");

    m.def("_c_dbm_constrain1", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t i, cindex_t j, raw_t constraint) {
        auto buf_dbm = dbm.request();
        return dbm_constrain1(static_cast<raw_t*>(buf_dbm.ptr), dim, i, j, constraint);
    }, "Constrain a DBM with one constraint");

    m.def("_c_dbm_constrainC", [](py::array_t<raw_t> dbm, cindex_t dim, constraint_t c) {
        auto buf_dbm = dbm.request();
        return dbm_constrainC(static_cast<raw_t*>(buf_dbm.ptr), dim, c);
    }, "Wrapper for constrain1");

    m.def("_c_dbm_up", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        dbm_up(static_cast<raw_t*>(buf_dbm.ptr), dim);
    }, "Delay operation");

    m.def("_c_dbm_up_stop", [](py::array_t<raw_t> dbm, cindex_t dim, py::array_t<uint32_t> stopped) {
        auto buf_dbm = dbm.request();
        auto buf_stopped = stopped.request();
        dbm_up_stop(static_cast<raw_t*>(buf_dbm.ptr), dim, static_cast<const uint32_t*>(buf_stopped.ptr));
    }, "Delay operation with stopped clocks");

    m.def("_c_dbm_downFrom", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t j0) {
        auto buf_dbm = dbm.request();
        dbm_downFrom(static_cast<raw_t*>(buf_dbm.ptr), dim, j0);
    }, "Internal dbm_down, don't use directly");

    m.def("_c_dbm_down", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        dbm_down(static_cast<raw_t*>(buf_dbm.ptr), dim);
    }, "Inverse delay operation");

    m.def("_c_dbm_down_stop", [](py::array_t<raw_t> dbm, cindex_t dim, py::array_t<uint32_t> stopped) {
        auto buf_dbm = dbm.request();
        auto buf_stopped = stopped.request();
        dbm_down_stop(static_cast<raw_t*>(buf_dbm.ptr), dim, static_cast<const uint32_t*>(buf_stopped.ptr));
    }, "Inverse delay operation with stopped clocks");

    m.def("_c_dbm_updateValue", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t index, int32_t value) {
        auto buf_dbm = dbm.request();
        dbm_updateValue(static_cast<raw_t*>(buf_dbm.ptr), dim, index, value);
    }, "Update operation");

    m.def("_c_dbm_freeClock", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t index) {
        auto buf_dbm = dbm.request();
        dbm_freeClock(static_cast<raw_t*>(buf_dbm.ptr), dim, index);
    }, "Free operation");

    m.def("_c_dbm_freeUp", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t index) {
        auto buf_dbm = dbm.request();
        dbm_freeUp(static_cast<raw_t*>(buf_dbm.ptr), dim, index);
    }, "Free all upper bounds for a given clock");

    m.def("_c_dbm_freeAllUp", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        dbm_freeAllUp(static_cast<raw_t*>(buf_dbm.ptr), dim);
    }, "Free all upper bounds for all clocks");

    m.def("_c_dbm_isFreedAllUp", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_isFreedAllUp(static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Test if dbm_freeAllUp has no effect on dbm");

    m.def("_c_dbm_testFreeAllDown", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_testFreeAllDown(static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Test if dbm_freeAllDown has no effect on dbm");

    m.def("_c_dbm_freeDown", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t index) {
        auto buf_dbm = dbm.request();
        dbm_freeDown(static_cast<raw_t*>(buf_dbm.ptr), dim, index);
    }, "Free all lower bounds for a given clock");

    m.def("_c_dbm_freeAllDown", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        dbm_freeAllDown(static_cast<raw_t*>(buf_dbm.ptr), dim);
    }, "Free all lower bounds for all clocks");

    m.def("_c_dbm_updateClock", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t i, cindex_t j) {
        auto buf_dbm = dbm.request();
        dbm_updateClock(static_cast<raw_t*>(buf_dbm.ptr), dim, i, j);
    }, "Clock copy operation");

    m.def("_c_dbm_updateIncrement", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t i, int32_t value) {
        auto buf_dbm = dbm.request();
        dbm_updateIncrement(static_cast<raw_t*>(buf_dbm.ptr), dim, i, value);
    }, "Increment operation");

    m.def("_c_dbm_update", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t i, cindex_t j, int32_t value) {
        auto buf_dbm = dbm.request();
        dbm_update(static_cast<raw_t*>(buf_dbm.ptr), dim, i, j, value);
    }, "General update operation");

    m.def("_c_dbm_constrainClock", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t clock, int32_t value) {
        auto buf_dbm = dbm.request();
        return dbm_constrainClock(static_cast<raw_t*>(buf_dbm.ptr), dim, clock, value);
    }, "Constrain clock to a value");

    m.def("_c_dbm_satisfies", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t i, cindex_t j, raw_t constraint) {
        auto buf_dbm = dbm.request();
        return dbm_satisfies(static_cast<const raw_t*>(buf_dbm.ptr), dim, i, j, constraint);
    }, "Check if DBM satisfies a constraint");

    m.def("_c_dbm_isEmpty", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_isEmpty(static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Check if DBM is empty");

    m.def("_c_dbm_close", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_close(static_cast<raw_t*>(buf_dbm.ptr), dim);
    }, "Close operation");

    m.def("_c_dbm_isClosed", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_isClosed(static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Check if DBM is closed");

    m.def("_c_dbm_closex", [](py::array_t<raw_t> dbm, cindex_t dim, py::array_t<uint32_t> touched) {
        auto buf_dbm = dbm.request();
        auto buf_touched = touched.request();
        return dbm_closex(static_cast<raw_t*>(buf_dbm.ptr), dim, static_cast<const uint32_t*>(buf_touched.ptr));
    }, "Close operation with touched clocks");

    m.def("_c_dbm_close1", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t k) {
        auto buf_dbm = dbm.request();
        return dbm_close1(static_cast<raw_t*>(buf_dbm.ptr), dim, k);
    }, "Close operation for 1 clock");

    m.def("_c_dbm_closeij", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t i, cindex_t j) {
        auto buf_dbm = dbm.request();
        dbm_closeij(static_cast<raw_t*>(buf_dbm.ptr), dim, i, j);
    }, "Specialized close operation for one constraint");

    m.def("_c_dbm_tighten", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t i, cindex_t j, raw_t c) {
        auto buf_dbm = dbm.request();
        dbm_tighten(static_cast<raw_t*>(buf_dbm.ptr), dim, i, j, c);
    }, "Tighten with a constraint and maintain closed form");

    m.def("_c_dbm_isUnbounded", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_isUnbounded(static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Check if DBM is unbounded");

    m.def("_c_dbm_relation", [](py::array_t<raw_t> dbm1, py::array_t<raw_t> dbm2, cindex_t dim) {
        auto buf_dbm1 = dbm1.request();
        auto buf_dbm2 = dbm2.request();
        return dbm_relation(static_cast<const raw_t*>(buf_dbm1.ptr), static_cast<const raw_t*>(buf_dbm2.ptr), dim);
    }, "Relation between 2 DBMs");

    m.def("_c_dbm_isSubsetEq", [](py::array_t<raw_t> dbm1, py::array_t<raw_t> dbm2, cindex_t dim) {
        auto buf_dbm1 = dbm1.request();
        auto buf_dbm2 = dbm2.request();
        return dbm_isSubsetEq(static_cast<const raw_t*>(buf_dbm1.ptr), static_cast<const raw_t*>(buf_dbm2.ptr), dim);
    }, "Test if dbm1 <= dbm2");

    m.def("_c_dbm_isSupersetEq", [](py::array_t<raw_t> dbm1, py::array_t<raw_t> dbm2, cindex_t dim) {
        auto buf_dbm1 = dbm1.request();
        auto buf_dbm2 = dbm2.request();
        return dbm_isSupersetEq(static_cast<const raw_t*>(buf_dbm1.ptr), static_cast<const raw_t*>(buf_dbm2.ptr), dim);
    }, "Test if dbm1 >= dbm2");

    m.def("_c_dbm_relaxUpClock", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t clock) {
        auto buf_dbm = dbm.request();
        dbm_relaxUpClock(static_cast<raw_t*>(buf_dbm.ptr), dim, clock);
    }, "Relax upper bounds of a given clock");

    m.def("_c_dbm_relaxDownClock", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t clock) {
        auto buf_dbm = dbm.request();
        dbm_relaxDownClock(static_cast<raw_t*>(buf_dbm.ptr), dim, clock);
    }, "Relax lower bounds of a given clock");

    m.def("_c_dbm_relaxAll", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        dbm_relaxAll(static_cast<raw_t*>(buf_dbm.ptr), dim);
    }, "Relax all bounds");

    m.def("_c_dbm_relaxUp", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        dbm_relaxUp(static_cast<raw_t*>(buf_dbm.ptr), dim);
    }, "Smallest possible delay");

    m.def("_c_dbm_relaxDown", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        dbm_relaxDown(static_cast<raw_t*>(buf_dbm.ptr), dim);
    }, "Smallest possible inverse delay");

    m.def("_c_dbm_tightenDown", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_tightenDown(static_cast<raw_t*>(buf_dbm.ptr), dim);
    }, "Constrain all lower bounds to be strict");

    m.def("_c_dbm_tightenUp", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_tightenUp(static_cast<raw_t*>(buf_dbm.ptr), dim);
    }, "Constrain all upper bounds to be strict");

    m.def("_c_dbm_copy", [](py::array_t<raw_t> dst, py::array_t<raw_t> src, cindex_t dim) {
        auto buf_dst = dst.request();
        auto buf_src = src.request();
        dbm_copy(static_cast<raw_t*>(buf_dst.ptr), static_cast<const raw_t*>(buf_src.ptr), dim);
    }, "Copy DBMs");

    m.def("_c_dbm_areEqual", [](py::array_t<raw_t> dbm1, py::array_t<raw_t> dbm2, cindex_t dim) {
        auto buf_dbm1 = dbm1.request();
        auto buf_dbm2 = dbm2.request();
        return dbm_areEqual(static_cast<const raw_t*>(buf_dbm1.ptr), static_cast<const raw_t*>(buf_dbm2.ptr), dim);
    }, "Test equality of DBMs");

    m.def("_c_dbm_hash", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_hash(static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Compute hash value for a DBM");

    m.def("_c_dbm_isPointIncluded", [](py::array_t<int32_t> pt, py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_pt = pt.request();
        auto buf_dbm = dbm.request();
        return dbm_isPointIncluded(static_cast<const int32_t*>(buf_pt.ptr), static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Test if a discrete point is included in the zone");

    m.def("_c_dbm_isRealPointIncluded", [](py::array_t<double> pt, py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_pt = pt.request();
        auto buf_dbm = dbm.request();
        return dbm_isRealPointIncluded(static_cast<const double*>(buf_pt.ptr), static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Test if a real point is included in the zone");

    m.def("_c_dbm_extrapolateMaxBounds", [](py::array_t<raw_t> dbm, cindex_t dim, py::array_t<int32_t> max) {
        auto buf_dbm = dbm.request();
        auto buf_max = max.request();
        dbm_extrapolateMaxBounds(static_cast<raw_t*>(buf_dbm.ptr), dim, static_cast<const int32_t*>(buf_max.ptr));
    }, "Classical extrapolation based on maximal bounds");

    m.def("_c_dbm_diagonalExtrapolateMaxBounds", [](py::array_t<raw_t> dbm, cindex_t dim, py::array_t<int32_t> max) {
        auto buf_dbm = dbm.request();
        auto buf_max = max.request();
        dbm_diagonalExtrapolateMaxBounds(static_cast<raw_t*>(buf_dbm.ptr), dim, static_cast<const int32_t*>(buf_max.ptr));
    }, "Diagonal extrapolation based on maximal bounds");

    m.def("_c_dbm_extrapolateLUBounds", [](py::array_t<raw_t> dbm, cindex_t dim, py::array_t<int32_t> lower, py::array_t<int32_t> upper) {
        auto buf_dbm = dbm.request();
        auto buf_lower = lower.request();
        auto buf_upper = upper.request();
        dbm_extrapolateLUBounds(static_cast<raw_t*>(buf_dbm.ptr), dim, static_cast<const int32_t*>(buf_lower.ptr), static_cast<const int32_t*>(buf_upper.ptr));
    }, "Extrapolation based on lower-upper bounds");

    m.def("_c_dbm_diagonalExtrapolateLUBounds", [](py::array_t<raw_t> dbm, cindex_t dim, py::array_t<int32_t> lower, py::array_t<int32_t> upper) {
        auto buf_dbm = dbm.request();
        auto buf_lower = lower.request();
        auto buf_upper = upper.request();
        dbm_diagonalExtrapolateLUBounds(static_cast<raw_t*>(buf_dbm.ptr), dim, static_cast<const int32_t*>(buf_lower.ptr), static_cast<const int32_t*>(buf_upper.ptr));
    }, "Diagonal extrapolation based on lower-upper bounds");

    m.def("_c_dbm_shrinkExpand", [](py::array_t<raw_t> dbmSrc, py::array_t<raw_t> dbmDst, cindex_t dimSrc, py::array_t<uint32_t> bitSrc, py::array_t<uint32_t> bitDst, size_t bitSize, py::array_t<cindex_t> table) {
        auto buf_dbmSrc = dbmSrc.request();
        auto buf_dbmDst = dbmDst.request();
        auto buf_bitSrc = bitSrc.request();
        auto buf_bitDst = bitDst.request();
        auto buf_table = table.request();
        return dbm_shrinkExpand(static_cast<const raw_t*>(buf_dbmSrc.ptr), static_cast<raw_t*>(buf_dbmDst.ptr), dimSrc, static_cast<const uint32_t*>(buf_bitSrc.ptr), static_cast<const uint32_t*>(buf_bitDst.ptr), bitSize, static_cast<cindex_t*>(buf_table.ptr));
    }, "Shrink and expand a DBM");

    m.def("_c_dbm_updateDBM", [](py::array_t<raw_t> dbmDst, py::array_t<raw_t> dbmSrc, cindex_t dimDst, cindex_t dimSrc, py::array_t<cindex_t> cols) {
        auto buf_dbmDst = dbmDst.request();
        auto buf_dbmSrc = dbmSrc.request();
        auto buf_cols = cols.request();
        dbm_updateDBM(static_cast<raw_t*>(buf_dbmDst.ptr), static_cast<const raw_t*>(buf_dbmSrc.ptr), dimDst, dimSrc, static_cast<const cindex_t*>(buf_cols.ptr));
    }, "Update DBM using indirection table");

    m.def("_c_dbm_swapClocks", [](py::array_t<raw_t> dbm, cindex_t dim, cindex_t x, cindex_t y) {
        auto buf_dbm = dbm.request();
        dbm_swapClocks(static_cast<raw_t*>(buf_dbm.ptr), dim, x, y);
    }, "Swap clocks");

    m.def("_c_dbm_isDiagonalOK", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_isDiagonalOK(static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Test if the diagonal is correct");

    m.def("_c_dbm_isValid", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_isValid(static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Test if DBM is valid");

    m.def("_c_dbm_relation2string", &dbm_relation2string, "Convert relation code to string");

    m.def("_c_dbm_getMaxRange", [](py::array_t<raw_t> dbm, cindex_t dim) {
        auto buf_dbm = dbm.request();
        return dbm_getMaxRange(static_cast<const raw_t*>(buf_dbm.ptr), dim);
    }, "Compute max range of DBM constraints");
}
