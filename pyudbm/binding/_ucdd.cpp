#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cdd/cdd.h>
#include <cdd/kernel.h>

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace py = pybind11;

namespace
{
    void ensure_runtime_running()
    {
        cdd_ensure_running();
        if (!cdd_isrunning()) {
            throw std::runtime_error("Failed to initialize the UCDD runtime.");
        }
    }

    std::vector<raw_t> normalize_dbm(const std::vector<int32_t>& dbm, cindex_t dim)
    {
        const auto expected_size = static_cast<std::size_t>(dim) * static_cast<std::size_t>(dim);
        if (dbm.size() != expected_size) {
            throw std::invalid_argument(
                "DBM size does not match the supplied dimension. Expected dim * dim raw cells.");
        }

        auto result = std::vector<raw_t>{};
        result.reserve(dbm.size());
        for (const auto value : dbm) {
            result.push_back(static_cast<raw_t>(value));
        }
        return result;
    }

    void ensure_same_size(const std::vector<int32_t>& left, const std::vector<int32_t>& right, const char* message)
    {
        if (left.size() != right.size()) {
            throw std::invalid_argument(message);
        }
    }

    std::vector<std::vector<int32_t>> to_matrix_rows(
        const std::vector<int32_t>& data, int32_t row_count, int32_t column_count
    )
    {
        auto rows = std::vector<std::vector<int32_t>>{};
        if (row_count <= 0 || column_count <= 0) {
            return rows;
        }

        rows.reserve(static_cast<std::size_t>(row_count));
        for (int32_t row = 0; row < row_count; ++row) {
            const auto offset = static_cast<std::size_t>(row) * static_cast<std::size_t>(column_count);
            rows.emplace_back(
                data.begin() + static_cast<std::ptrdiff_t>(offset),
                data.begin() + static_cast<std::ptrdiff_t>(offset + column_count)
            );
        }
        return rows;
    }

    class NativeCDD;

    class NativeCDDLevelInfo
    {
    public:
        explicit NativeCDDLevelInfo(const LevelInfo& info): type_(info.type), clock1_(info.clock1), clock2_(info.clock2), diff_(info.diff) {}

        int32_t type() const { return type_; }
        int32_t clock1() const { return clock1_; }
        int32_t clock2() const { return clock2_; }
        int32_t diff() const { return diff_; }

    private:
        int32_t type_;
        int32_t clock1_;
        int32_t clock2_;
        int32_t diff_;
    };

    class NativeBDDTraceSet
    {
    public:
        explicit NativeBDDTraceSet(const bdd_arrays& arrays): num_traces_(arrays.numTraces), num_bools_(arrays.numBools)
        {
            const auto total_size = static_cast<std::size_t>(num_traces_ > 0 ? num_traces_ : 1) *
                static_cast<std::size_t>(num_bools_ > 0 ? num_bools_ : 1);

            if (arrays.vars != nullptr) {
                vars_.assign(arrays.vars, arrays.vars + static_cast<std::ptrdiff_t>(total_size));
                std::free(arrays.vars);
            }
            if (arrays.values != nullptr) {
                values_.assign(arrays.values, arrays.values + static_cast<std::ptrdiff_t>(total_size));
                std::free(arrays.values);
            }

            if (num_traces_ <= 0 || num_bools_ <= 0) {
                vars_.clear();
                values_.clear();
            }
        }

        int32_t num_traces() const { return num_traces_; }
        int32_t num_bools() const { return num_bools_; }

        std::vector<std::vector<int32_t>> vars_matrix() const
        {
            return to_matrix_rows(vars_, num_traces_, num_bools_);
        }

        std::vector<std::vector<int32_t>> values_matrix() const
        {
            return to_matrix_rows(values_, num_traces_, num_bools_);
        }

    private:
        int32_t num_traces_;
        int32_t num_bools_;
        std::vector<int32_t> vars_;
        std::vector<int32_t> values_;
    };

    class NativeCDDRuntime
    {
    public:
        static void init(int32_t maxsize, int32_t cache_size, std::size_t stack_size)
        {
            const auto code = cdd_init(maxsize, cache_size, stack_size);
            if (code != 0) {
                throw std::runtime_error("cdd_init failed with error code " + std::to_string(code) + ".");
            }
        }

        static void ensure_running()
        {
            ensure_runtime_running();
        }

        static void done();

        static bool is_running()
        {
            return cdd_isrunning() != 0;
        }

        static std::string version()
        {
            ensure_runtime_running();
            return std::string(cdd_versionstr());
        }

        static int32_t version_num()
        {
            ensure_runtime_running();
            return cdd_versionnum();
        }

        static void add_clocks(int32_t count)
        {
            ensure_runtime_running();
            cdd_add_clocks(count);
        }

        static int32_t add_bddvars(int32_t count)
        {
            ensure_runtime_running();
            return cdd_add_bddvar(count);
        }

        static int32_t getclocks()
        {
            ensure_runtime_running();
            return cdd_getclocks();
        }

        static int32_t get_level_count()
        {
            ensure_runtime_running();
            return cdd_get_level_count();
        }

        static int32_t get_bdd_level_count()
        {
            ensure_runtime_running();
            return cdd_get_bdd_level_count();
        }

        static NativeCDDLevelInfo get_level_info(int32_t level)
        {
            ensure_runtime_running();
            const auto* info = cdd_get_levelinfo(level);
            if (info == nullptr) {
                throw std::out_of_range("CDD level is out of range.");
            }
            return NativeCDDLevelInfo(*info);
        }
    };

    class NativeCDD
    {
    public:
        explicit NativeCDD(const cdd& value): cdd_(value)
        {
            ++live_count_;
        }

        NativeCDD(const NativeCDD& other): cdd_(other.cdd_)
        {
            ++live_count_;
        }

        NativeCDD(NativeCDD&& other) noexcept: cdd_(other.cdd_)
        {
            ++live_count_;
        }

        ~NativeCDD()
        {
            --live_count_;
        }

        NativeCDD& operator=(const NativeCDD& other)
        {
            cdd_ = other.cdd_;
            return *this;
        }

        NativeCDD& operator=(NativeCDD&& other) noexcept
        {
            cdd_ = other.cdd_;
            return *this;
        }

        static std::size_t live_count()
        {
            return live_count_;
        }

        static NativeCDD true_value()
        {
            ensure_runtime_running();
            return NativeCDD(cdd_true());
        }

        static NativeCDD false_value()
        {
            ensure_runtime_running();
            return NativeCDD(cdd_false());
        }

        static NativeCDD upper(int32_t i, int32_t j, int32_t bound)
        {
            ensure_runtime_running();
            return NativeCDD(cdd_upper(i, j, static_cast<raw_t>(bound)));
        }

        static NativeCDD lower(int32_t i, int32_t j, int32_t bound)
        {
            ensure_runtime_running();
            return NativeCDD(cdd_lower(i, j, static_cast<raw_t>(bound)));
        }

        static NativeCDD interval(int32_t i, int32_t j, int32_t low, int32_t up)
        {
            ensure_runtime_running();
            return NativeCDD(cdd_interval(i, j, static_cast<raw_t>(low), static_cast<raw_t>(up)));
        }

        static NativeCDD bddvar(int32_t level)
        {
            ensure_runtime_running();
            return NativeCDD(cdd_bddvar(level));
        }

        static NativeCDD bddnvar(int32_t level)
        {
            ensure_runtime_running();
            return NativeCDD(cdd_bddnvar(level));
        }

        static NativeCDD from_dbm(const std::vector<int32_t>& dbm, cindex_t dim)
        {
            ensure_runtime_running();
            const auto raw_dbm = normalize_dbm(dbm, dim);
            return NativeCDD(cdd(raw_dbm.data(), dim));
        }

        NativeCDD copy() const { return NativeCDD(cdd_); }

        NativeCDD and_op(const NativeCDD& other) const
        {
            return NativeCDD(cdd_ & other.cdd_);
        }

        NativeCDD or_op(const NativeCDD& other) const
        {
            return NativeCDD(cdd_ | other.cdd_);
        }

        NativeCDD minus_op(const NativeCDD& other) const
        {
            return NativeCDD(cdd_ - other.cdd_);
        }

        NativeCDD xor_op(const NativeCDD& other) const
        {
            return NativeCDD(cdd_ ^ other.cdd_);
        }

        NativeCDD invert() const
        {
            return NativeCDD(!cdd_);
        }

        NativeCDD ite(const NativeCDD& then_branch, const NativeCDD& else_branch) const
        {
            return NativeCDD(cdd_ite(cdd_, then_branch.cdd_, else_branch.cdd_));
        }

        NativeCDD apply(int32_t op, const NativeCDD& other) const
        {
            return NativeCDD(cdd_apply(cdd_, other.cdd_, op));
        }

        NativeCDD apply_reduce(int32_t op, const NativeCDD& other) const
        {
            return NativeCDD(cdd_apply_reduce(cdd_, other.cdd_, op));
        }

        NativeCDD reduce() const
        {
            return NativeCDD(cdd_reduce(cdd_));
        }

        NativeCDD reduce2() const
        {
            return NativeCDD(cdd_reduce2(cdd_));
        }

        bool equiv(const NativeCDD& other) const
        {
            return cdd_equiv(cdd_, other.cdd_);
        }

        int32_t nodecount() const
        {
            return cdd_nodecount(cdd_);
        }

        int32_t edgecount() const
        {
            return cdd_edgecount(cdd_.handle());
        }

        bool is_bdd() const
        {
            return cdd_isBDD(cdd_);
        }

        bool is_true() const
        {
            return cdd_.handle() == cddtrue;
        }

        bool is_false() const
        {
            return cdd_.handle() == cddfalse;
        }

        NativeCDD remove_negative() const
        {
            return NativeCDD(cdd_remove_negative(cdd_));
        }

        NativeCDD delay() const
        {
            return NativeCDD(cdd_delay(cdd_));
        }

        NativeCDD past() const
        {
            return NativeCDD(cdd_past(cdd_));
        }

        NativeCDD delay_invariant(const NativeCDD& invariant) const
        {
            return NativeCDD(cdd_delay_invariant(cdd_, invariant.cdd_));
        }

        NativeCDD predt(const NativeCDD& safe) const
        {
            return NativeCDD(cdd_predt(cdd_, safe.cdd_));
        }

        NativeCDD apply_reset(
            const std::vector<int32_t>& clock_resets,
            const std::vector<int32_t>& clock_values,
            const std::vector<int32_t>& bool_resets,
            const std::vector<int32_t>& bool_values
        ) const
        {
            ensure_same_size(clock_resets, clock_values, "Clock reset indices and values must have the same length.");
            ensure_same_size(bool_resets, bool_values, "Boolean reset levels and values must have the same length.");

            auto local_clock_resets = clock_resets;
            auto local_clock_values = clock_values;
            auto local_bool_resets = bool_resets;
            auto local_bool_values = bool_values;

            return NativeCDD(cdd_apply_reset(
                cdd_,
                local_clock_resets.empty() ? nullptr : local_clock_resets.data(),
                local_clock_values.empty() ? nullptr : local_clock_values.data(),
                static_cast<int32_t>(local_clock_resets.size()),
                local_bool_resets.empty() ? nullptr : local_bool_resets.data(),
                local_bool_values.empty() ? nullptr : local_bool_values.data(),
                static_cast<int32_t>(local_bool_resets.size())
            ));
        }

        NativeCDD transition(
            const NativeCDD& guard,
            const std::vector<int32_t>& clock_resets,
            const std::vector<int32_t>& clock_values,
            const std::vector<int32_t>& bool_resets,
            const std::vector<int32_t>& bool_values
        ) const
        {
            ensure_same_size(clock_resets, clock_values, "Clock reset indices and values must have the same length.");
            ensure_same_size(bool_resets, bool_values, "Boolean reset levels and values must have the same length.");

            auto local_clock_resets = clock_resets;
            auto local_clock_values = clock_values;
            auto local_bool_resets = bool_resets;
            auto local_bool_values = bool_values;

            return NativeCDD(cdd_transition(
                cdd_,
                guard.cdd_,
                local_clock_resets.empty() ? nullptr : local_clock_resets.data(),
                local_clock_values.empty() ? nullptr : local_clock_values.data(),
                static_cast<int32_t>(local_clock_resets.size()),
                local_bool_resets.empty() ? nullptr : local_bool_resets.data(),
                local_bool_values.empty() ? nullptr : local_bool_values.data(),
                static_cast<int32_t>(local_bool_resets.size())
            ));
        }

        NativeCDD transition_back(
            const NativeCDD& guard,
            const NativeCDD& update,
            const std::vector<int32_t>& clock_resets,
            const std::vector<int32_t>& bool_resets
        ) const
        {
            auto local_clock_resets = clock_resets;
            auto local_bool_resets = bool_resets;

            return NativeCDD(cdd_transition_back(
                cdd_,
                guard.cdd_,
                update.cdd_,
                local_clock_resets.empty() ? nullptr : local_clock_resets.data(),
                static_cast<int32_t>(local_clock_resets.size()),
                local_bool_resets.empty() ? nullptr : local_bool_resets.data(),
                static_cast<int32_t>(local_bool_resets.size())
            ));
        }

        NativeCDD transition_back_past(
            const NativeCDD& guard,
            const NativeCDD& update,
            const std::vector<int32_t>& clock_resets,
            const std::vector<int32_t>& bool_resets
        ) const
        {
            auto local_clock_resets = clock_resets;
            auto local_bool_resets = bool_resets;

            return NativeCDD(cdd_transition_back_past(
                cdd_,
                guard.cdd_,
                update.cdd_,
                local_clock_resets.empty() ? nullptr : local_clock_resets.data(),
                static_cast<int32_t>(local_clock_resets.size()),
                local_bool_resets.empty() ? nullptr : local_bool_resets.data(),
                static_cast<int32_t>(local_bool_resets.size())
            ));
        }

        bool contains_dbm(const std::vector<int32_t>& dbm, cindex_t dim) const
        {
            auto raw_dbm = normalize_dbm(dbm, dim);
            return cdd_contains(cdd_, raw_dbm.data(), dim);
        }

        py::tuple extract_dbm(cindex_t dim) const
        {
            auto dbm = std::vector<raw_t>(static_cast<std::size_t>(dim) * static_cast<std::size_t>(dim));
            const auto remainder = cdd_extract_dbm(cdd_, dbm.data(), dim);

            auto raw = std::vector<int32_t>{};
            raw.reserve(dbm.size());
            for (const auto value : dbm) {
                raw.push_back(static_cast<int32_t>(value));
            }

            return py::make_tuple(NativeCDD(remainder), raw);
        }

        NativeCDD extract_bdd(cindex_t dim) const
        {
            return NativeCDD(cdd_extract_bdd(cdd_, dim));
        }

        NativeBDDTraceSet bdd_to_array() const
        {
            return NativeBDDTraceSet(cdd_bdd_to_array(cdd_));
        }

        const cdd& value() const
        {
            return cdd_;
        }

    private:
        cdd cdd_;
        static std::size_t live_count_;
    };

    std::size_t NativeCDD::live_count_ = 0;

    void NativeCDDRuntime::done()
    {
        if (!cdd_isrunning()) {
            return;
        }
        if (NativeCDD::live_count() != 0) {
            throw std::runtime_error(
                "Cannot shut down the UCDD runtime while _NativeCDD objects are still alive."
            );
        }
        cdd_done();
    }

    class NativeCDDExtraction
    {
    public:
        explicit NativeCDDExtraction(const extraction_result& extraction):
            cdd_part_(extraction.CDD_part),
            bdd_part_(extraction.BDD_part)
        {
            if (extraction.dbm != nullptr) {
                const auto size = static_cast<std::size_t>(cdd_clocknum) * static_cast<std::size_t>(cdd_clocknum);
                dbm_.reserve(size);
                for (std::size_t index = 0; index < size; ++index) {
                    dbm_.push_back(static_cast<int32_t>(extraction.dbm[index]));
                }
                std::free(extraction.dbm);
            }
        }

        NativeCDD cdd_part() const { return cdd_part_; }
        NativeCDD bdd_part() const { return bdd_part_; }
        std::vector<int32_t> dbm() const { return dbm_; }

    private:
        NativeCDD cdd_part_;
        NativeCDD bdd_part_;
        std::vector<int32_t> dbm_;
    };
}  // namespace

PYBIND11_MODULE(_ucdd, m)
{
    m.doc() = "Thin pybind11 bindings for the native UCDD runtime and CDD objects.";

    m.attr("TYPE_CDD") = py::int_(TYPE_CDD);
    m.attr("TYPE_BDD") = py::int_(TYPE_BDD);
    m.attr("OP_AND") = py::int_(cddop_and);
    m.attr("OP_XOR") = py::int_(cddop_xor);

    py::class_<NativeCDDLevelInfo>(m, "_NativeCDDLevelInfo")
        .def_property_readonly("type", &NativeCDDLevelInfo::type)
        .def_property_readonly("clock1", &NativeCDDLevelInfo::clock1)
        .def_property_readonly("clock2", &NativeCDDLevelInfo::clock2)
        .def_property_readonly("diff", &NativeCDDLevelInfo::diff)
        .def("__repr__", [](const NativeCDDLevelInfo& info) {
            return "<_NativeCDDLevelInfo type=" + std::to_string(info.type()) +
                " clock1=" + std::to_string(info.clock1()) +
                " clock2=" + std::to_string(info.clock2()) +
                " diff=" + std::to_string(info.diff()) + ">";
        });

    py::class_<NativeBDDTraceSet>(m, "_NativeBDDTraceSet")
        .def_property_readonly("num_traces", &NativeBDDTraceSet::num_traces)
        .def_property_readonly("num_bools", &NativeBDDTraceSet::num_bools)
        .def("vars_matrix", &NativeBDDTraceSet::vars_matrix)
        .def("values_matrix", &NativeBDDTraceSet::values_matrix);

    py::class_<NativeCDDRuntime>(m, "_NativeCDDRuntime")
        .def_static("init", &NativeCDDRuntime::init, py::arg("maxsize"), py::arg("cache_size"), py::arg("stack_size"))
        .def_static("ensure_running", &NativeCDDRuntime::ensure_running)
        .def_static("done", &NativeCDDRuntime::done)
        .def_static("is_running", &NativeCDDRuntime::is_running)
        .def_static("version", &NativeCDDRuntime::version)
        .def_static("version_num", &NativeCDDRuntime::version_num)
        .def_static("add_clocks", &NativeCDDRuntime::add_clocks, py::arg("count"))
        .def_static("add_bddvars", &NativeCDDRuntime::add_bddvars, py::arg("count"))
        .def_static("getclocks", &NativeCDDRuntime::getclocks)
        .def_static("get_level_count", &NativeCDDRuntime::get_level_count)
        .def_static("get_bdd_level_count", &NativeCDDRuntime::get_bdd_level_count)
        .def_static("get_level_info", &NativeCDDRuntime::get_level_info, py::arg("level"));

    py::class_<NativeCDD>(m, "_NativeCDD")
        .def_static("true", &NativeCDD::true_value)
        .def_static("false", &NativeCDD::false_value)
        .def_static("upper", &NativeCDD::upper, py::arg("i"), py::arg("j"), py::arg("bound"))
        .def_static("lower", &NativeCDD::lower, py::arg("i"), py::arg("j"), py::arg("bound"))
        .def_static("interval", &NativeCDD::interval, py::arg("i"), py::arg("j"), py::arg("low"), py::arg("up"))
        .def_static("bddvar", &NativeCDD::bddvar, py::arg("level"))
        .def_static("bddnvar", &NativeCDD::bddnvar, py::arg("level"))
        .def_static("from_dbm", &NativeCDD::from_dbm, py::arg("dbm"), py::arg("dim"))
        .def_static("live_count", &NativeCDD::live_count)
        .def("copy", &NativeCDD::copy)
        .def("and_op", &NativeCDD::and_op, py::arg("other"))
        .def("or_op", &NativeCDD::or_op, py::arg("other"))
        .def("minus_op", &NativeCDD::minus_op, py::arg("other"))
        .def("xor_op", &NativeCDD::xor_op, py::arg("other"))
        .def("invert", &NativeCDD::invert)
        .def("ite", &NativeCDD::ite, py::arg("then_branch"), py::arg("else_branch"))
        .def("apply", &NativeCDD::apply, py::arg("op"), py::arg("other"))
        .def("apply_reduce", &NativeCDD::apply_reduce, py::arg("op"), py::arg("other"))
        .def("reduce", &NativeCDD::reduce)
        .def("reduce2", &NativeCDD::reduce2)
        .def("equiv", &NativeCDD::equiv, py::arg("other"))
        .def("nodecount", &NativeCDD::nodecount)
        .def("edgecount", &NativeCDD::edgecount)
        .def("is_bdd", &NativeCDD::is_bdd)
        .def("is_true", &NativeCDD::is_true)
        .def("is_false", &NativeCDD::is_false)
        .def("remove_negative", &NativeCDD::remove_negative)
        .def("delay", &NativeCDD::delay)
        .def("past", &NativeCDD::past)
        .def("delay_invariant", &NativeCDD::delay_invariant, py::arg("invariant"))
        .def("predt", &NativeCDD::predt, py::arg("safe"))
        .def("apply_reset", &NativeCDD::apply_reset, py::arg("clock_resets"), py::arg("clock_values"),
             py::arg("bool_resets"), py::arg("bool_values"))
        .def("transition", &NativeCDD::transition, py::arg("guard"), py::arg("clock_resets"),
             py::arg("clock_values"), py::arg("bool_resets"), py::arg("bool_values"))
        .def("transition_back", &NativeCDD::transition_back, py::arg("guard"), py::arg("update"),
             py::arg("clock_resets"), py::arg("bool_resets"))
        .def("transition_back_past", &NativeCDD::transition_back_past, py::arg("guard"), py::arg("update"),
             py::arg("clock_resets"), py::arg("bool_resets"))
        .def("contains_dbm", &NativeCDD::contains_dbm, py::arg("dbm"), py::arg("dim"))
        .def("extract_dbm", &NativeCDD::extract_dbm, py::arg("dim"))
        .def("extract_bdd", &NativeCDD::extract_bdd, py::arg("dim"))
        .def("extract_bdd_and_dbm", [](const NativeCDD& self) {
            return NativeCDDExtraction(cdd_extract_bdd_and_dbm(self.value()));
        })
        .def("bdd_to_array", &NativeCDD::bdd_to_array)
        .def("__and__", &NativeCDD::and_op, py::arg("other"))
        .def("__or__", &NativeCDD::or_op, py::arg("other"))
        .def("__sub__", &NativeCDD::minus_op, py::arg("other"))
        .def("__xor__", &NativeCDD::xor_op, py::arg("other"))
        .def("__invert__", &NativeCDD::invert)
        .def("__repr__", [](const NativeCDD& cdd_value) {
            return "<_NativeCDD nodes=" + std::to_string(cdd_value.nodecount()) + ">";
        });

    py::class_<NativeCDDExtraction>(m, "_NativeCDDExtraction")
        .def_property_readonly("cdd_part", &NativeCDDExtraction::cdd_part)
        .def_property_readonly("bdd_part", &NativeCDDExtraction::bdd_part)
        .def_property_readonly("dbm", &NativeCDDExtraction::dbm);
}
