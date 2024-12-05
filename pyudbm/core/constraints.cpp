#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <dbm/constraints.h>

namespace py = pybind11;

PYBIND11_MODULE(_c_udbm_constraints, m) {
    m.doc() = "Python bindings for constraints.h";

    m.attr("DBM_INFINITY") = static_cast<int>(dbm_INFINITY);
    m.attr("DBM_OVERFLOW") = static_cast<int>(dbm_OVERFLOW);

    m.attr("DBM_LE_ZERO") = static_cast<int>(dbm_LE_ZERO);
    m.attr("DBM_LS_INFINITY") = static_cast<int>(dbm_LS_INFINITY);
    m.attr("DBM_LE_OVERFLOW") = static_cast<int>(dbm_LE_OVERFLOW);

    // Enum for strictness
    py::enum_<strictness_t>(m, "_CStrictness",
        "An enumeration representing the strictness of time constraints in a Difference Bound Matrix (DBM).")
        .value("STRICT", dbm_STRICT, "Indicates a strict inequality constraint (e.g., x < y)")
        .value("WEAK", dbm_WEAK, "Indicates a non-strict inequality constraint (e.g., x <= y)")
        .export_values();

    // Struct for constraint
    py::class_<constraint_t>(m, "_CConstraint",
        "Represents a time constraint between two clock variables in a Difference Bound Matrix (DBM).\n\n"
        "Fields:\n"
        "    i (int): Index of the first clock variable\n"
        "    j (int): Index of the second clock variable\n"
        "    value (int): The bound value of the constraint\n\n"
        "The constraint represents a relation of the form x_i - x_j <= value")
        .def(py::init<cindex_t, cindex_t, int>(), py::arg("i"), py::arg("j"), py::arg("value"),
             "Create a constraint with specified i, j indices and bound value")
        .def_readwrite("i", &constraint_t::i, "Index of the first clock variable")
        .def_readwrite("j", &constraint_t::j, "Index of the second clock variable")
        .def_readwrite("value", &constraint_t::value, "Bound value of the constraint")
        .def("__eq__", &dbm_areConstraintsEqual, "Check if two constraints are equal")
        .def("__neg__", &dbm_negConstraint, "Negate the constraint")
        .def("__repr__", [](const constraint_t &c) {
            return "<Constraint: i=" + std::to_string(c.i) +
                   ", j=" + std::to_string(c.j) +
                   ", value=" + std::to_string(c.value) + ">";
        }, "String representation of the constraint");

    // Functions
    m.def("_c_dbm_bound2raw", &dbm_bound2raw, py::arg("bound"), py::arg("strict"),
          "Encode bound into raw representation.");

    m.def("_c_dbm_boundbool2raw", &dbm_boundbool2raw, py::arg("bound"), py::arg("isStrict"),
          "Encode bound into raw representation based on a boolean.");

    m.def("_c_dbm_raw2bound", &dbm_raw2bound, py::arg("raw"),
          "Decode raw representation to get the bound value.");

    m.def("_c_dbm_weakRaw", &dbm_weakRaw, py::arg("raw"),
          "Make an encoded constraint weak.");

    m.def("_c_dbm_strictRaw", &dbm_strictRaw, py::arg("raw"),
          "Make an encoded constraint strict.");

    m.def("_c_dbm_raw2strict", &dbm_raw2strict, py::arg("raw"),
          "Decode raw representation to get strictness.");

    m.def("_c_dbm_rawIsStrict", &dbm_rawIsStrict, py::arg("raw"),
          "Check if the constraint is strict.");

    m.def("_c_dbm_rawIsWeak", &dbm_rawIsWeak, py::arg("raw"),
          "Check if the constraint is weak.");

    m.def("_c_dbm_negRaw", &dbm_negRaw, py::arg("c"),
          "Negate a constraint.");

    m.def("_c_dbm_weakNegRaw", &dbm_weakNegRaw, py::arg("c"),
          "Weak negate a constraint.");

    m.def("_c_dbm_isValidRaw", &dbm_isValidRaw, py::arg("x"),
          "Check if a raw bound is valid.");

    m.def("_c_dbm_addRawRaw", &dbm_addRawRaw, py::arg("x"), py::arg("y"),
          "Add two raw constraints.");

    m.def("_c_dbm_addRawFinite", &dbm_addRawFinite, py::arg("x"), py::arg("y"),
          "Add a raw constraint and a finite constraint.");

    m.def("_c_dbm_addFiniteRaw", &dbm_addFiniteRaw, py::arg("x"), py::arg("y"),
          "Add a finite constraint and a raw constraint.");

    m.def("_c_dbm_addFiniteFinite", &dbm_addFiniteFinite, py::arg("x"), py::arg("y"),
          "Add two finite constraints.");

    m.def("_c_dbm_addFiniteWeak", &dbm_addFiniteWeak, py::arg("x"), py::arg("y"),
          "Specialized addition of finite constraints.");

    m.def("_c_dbm_rawInc", &dbm_rawInc, py::arg("c"), py::arg("i"),
          "Increment a raw constraint.");

    m.def("_c_dbm_rawDec", &dbm_rawDec, py::arg("c"), py::arg("d"),
          "Decrement a raw constraint.");

    m.def("_c_dbm_constraint", [](int i, int j, int bound, strictness_t strictness) {
        return dbm_constraint(static_cast<cindex_t>(i), static_cast<cindex_t>(j), bound, strictness);
    }, py::arg("i"), py::arg("j"), py::arg("bound"), py::arg("strictness"),
          "Create a constraint.");

    m.def("_c_dbm_constraint2", [](int i, int j, int bound, bool isStrict) {
        return dbm_constraint2(static_cast<cindex_t>(i), static_cast<cindex_t>(j), bound, isStrict);
    }, py::arg("i"), py::arg("j"), py::arg("bound"), py::arg("isStrict"),
          "Create a constraint with strictness flag.");

    m.def("_c_dbm_negConstraint", &dbm_negConstraint, py::arg("c"),
          "Negate a constraint.");

    m.def("_c_dbm_areConstraintsEqual", &dbm_areConstraintsEqual, py::arg("c1"), py::arg("c2"),
          "Check if two constraints are equal.");
}
