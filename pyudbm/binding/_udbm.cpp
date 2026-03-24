#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <base/c_allocator.h>
#include <dbm/ClockAccessor.h>
#include <dbm/constraints.h>
#include <dbm/fed.h>

#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace py = pybind11;

namespace
{
    class IndexedClockAccessor final : public dbm::ClockAccessor
    {
    public:
        explicit IndexedClockAccessor(std::vector<std::string> names): names_(std::move(names)) {}

        const std::string& getClockName(cindex_t index) const override
        {
            if (static_cast<std::size_t>(index) >= names_.size()) {
                throw std::out_of_range("Clock index is out of range.");
            }
            return names_[static_cast<std::size_t>(index)];
        }

    private:
        std::vector<std::string> names_;
    };

    class NativeConstraint
    {
    public:
        NativeConstraint(cindex_t i, cindex_t j, int32_t bound, bool is_strict):
            constraint_(dbm_constraint2(i, j, bound, is_strict))
        {}

        cindex_t i() const { return constraint_.i; }
        cindex_t j() const { return constraint_.j; }
        raw_t value() const { return constraint_.value; }

        const constraint_t& get() const { return constraint_; }

    private:
        constraint_t constraint_;
    };

    class NativeDBM
    {
    public:
        explicit NativeDBM(const dbm::dbm_t& dbm): dbm_(dbm) {}

        NativeDBM copy() const { return NativeDBM(dbm_); }

        cindex_t get_dimension() const { return dbm_.getDimension(); }

        std::string to_string(const std::vector<std::string>& names, bool full = false) const
        {
            ensure_name_count(names.size());
            return dbm_.str(IndexedClockAccessor(names), full);
        }

        std::vector<int32_t> raw_matrix() const
        {
            const auto dim = static_cast<std::size_t>(dbm_.getDimension());
            if (dbm_.isEmpty()) {
                return {};
            }

            const raw_t* matrix = dbm_();
            return std::vector<int32_t>(matrix, matrix + (dim * dim));
        }

        std::vector<int32_t> to_min_dbm(bool minimize_graph = true, bool try_constraints_16 = true) const
        {
            if (dbm_.isEmpty()) {
                return {};
            }

            int32_t* memory = dbm_.writeToMinDBMWithOffset(minimize_graph, try_constraints_16, base_mallocator, 0);
            if (memory == nullptr) {
                return {};
            }

            const auto size = dbm_getSizeOfMinDBM(memory);
            auto result = std::vector<int32_t>(memory, memory + size);
            base_mallocator.deallocFunction(memory, size, base_mallocator.allocData);
            return result;
        }

    private:
        void ensure_name_count(std::size_t count) const
        {
            if (count != static_cast<std::size_t>(dbm_.getDimension())) {
                throw std::invalid_argument("Clock name count does not match DBM dimension.");
            }
        }

        dbm::dbm_t dbm_;
    };

    class NativeFederation
    {
    public:
        explicit NativeFederation(cindex_t dim): fed_(dim) {}

        NativeFederation(cindex_t dim, const NativeConstraint& constraint): fed_(dim)
        {
            fed_.setInit();
            fed_ &= constraint.get();
        }

        NativeFederation(const NativeFederation&) = default;
        NativeFederation& operator=(const NativeFederation&) = default;

        NativeFederation copy() const { return NativeFederation(fed_); }

        cindex_t get_dimension() const { return fed_.getDimension(); }
        std::size_t size() const { return fed_.size(); }
        bool is_empty() const { return fed_.isEmpty(); }
        bool has_zero() const { return fed_.hasZero(); }
        std::uint32_t hash() const { return fed_.hash(); }

        std::string to_string(const std::vector<std::string>& names, bool full = false) const
        {
            ensure_name_count(names.size());
            return fed_.str(IndexedClockAccessor(names), full);
        }

        std::vector<NativeDBM> to_dbm_list() const
        {
            auto result = std::vector<NativeDBM>{};
            result.reserve(fed_.size());
            for (const auto& dbm : fed_) {
                result.emplace_back(dbm);
            }
            return result;
        }

        NativeFederation and_op(const NativeFederation& other) const
        {
            ensure_same_dimension(other);
            dbm::fed_t result(fed_);
            result &= other.fed_;
            return NativeFederation(result);
        }

        NativeFederation or_op(const NativeFederation& other) const
        {
            ensure_same_dimension(other);
            dbm::fed_t result(fed_);
            result |= other.fed_;
            return NativeFederation(result);
        }

        NativeFederation add_op(const NativeFederation& other) const
        {
            ensure_same_dimension(other);
            dbm::fed_t result(fed_);
            result += other.fed_;
            return NativeFederation(result);
        }

        NativeFederation minus_op(const NativeFederation& other) const
        {
            ensure_same_dimension(other);
            dbm::fed_t result(fed_);
            result -= other.fed_;
            return NativeFederation(result);
        }

        void iand(const NativeFederation& other)
        {
            ensure_same_dimension(other);
            fed_ &= other.fed_;
        }

        void ior(const NativeFederation& other)
        {
            ensure_same_dimension(other);
            fed_ |= other.fed_;
        }

        void iadd(const NativeFederation& other)
        {
            ensure_same_dimension(other);
            fed_ += other.fed_;
        }

        void isub(const NativeFederation& other)
        {
            ensure_same_dimension(other);
            fed_ -= other.fed_;
        }

        void up() { fed_.up(); }
        void down() { fed_.down(); }
        void merge_reduce(std::size_t skip, int expensive_try) { fed_.mergeReduce(skip, expensive_try); }
        void free_clock(cindex_t clock) { fed_.freeClock(clock); }
        void set_zero() { fed_.setZero(); }
        void set_init() { fed_.setInit(); }
        void convex_hull() { fed_.convexHull(); }
        void predt(const NativeFederation& other)
        {
            ensure_same_dimension(other);
            fed_.predt(other.fed_);
        }
        void intern() { fed_.intern(); }
        void update_value(cindex_t clock, int32_t value) { fed_.updateValue(clock, value); }

        bool eq(const NativeFederation& other) const
        {
            ensure_same_dimension(other);
            return fed_.eq(other.fed_);
        }

        bool lt(const NativeFederation& other) const
        {
            ensure_same_dimension(other);
            return fed_.lt(other.fed_);
        }

        bool gt(const NativeFederation& other) const
        {
            ensure_same_dimension(other);
            return fed_.gt(other.fed_);
        }

        bool le(const NativeFederation& other) const
        {
            ensure_same_dimension(other);
            return fed_.le(other.fed_);
        }

        bool ge(const NativeFederation& other) const
        {
            ensure_same_dimension(other);
            return fed_.ge(other.fed_);
        }

        bool contains_int(const std::vector<int32_t>& point) const
        {
            ensure_point_count(point.size());
            return fed_.contains(point);
        }

        bool contains_float(const std::vector<double>& point) const
        {
            ensure_point_count(point.size());
            return fed_.contains(point);
        }

        void extrapolate_max_bounds(const std::vector<int32_t>& max_bounds)
        {
            ensure_point_count(max_bounds.size());
            fed_.extrapolateMaxBounds(max_bounds.data());
        }

    private:
        explicit NativeFederation(const dbm::fed_t& fed): fed_(fed) {}

        void ensure_same_dimension(const NativeFederation& other) const
        {
            if (fed_.getDimension() != other.fed_.getDimension()) {
                throw std::invalid_argument("Federation dimensions do not match.");
            }
        }

        void ensure_name_count(std::size_t count) const
        {
            if (count != static_cast<std::size_t>(fed_.getDimension())) {
                throw std::invalid_argument("Clock name count does not match federation dimension.");
            }
        }

        void ensure_point_count(std::size_t count) const
        {
            if (count != static_cast<std::size_t>(fed_.getDimension())) {
                throw std::invalid_argument("Point dimension does not match federation dimension.");
            }
        }

        dbm::fed_t fed_;
    };
}  // namespace

PYBIND11_MODULE(_udbm, m)
{
    m.doc() = "Thin pybind11 bindings for the legacy-style pyudbm federation API.";

    py::class_<NativeConstraint>(m, "_NativeConstraint")
        .def(py::init<cindex_t, cindex_t, int32_t, bool>(), py::arg("i"), py::arg("j"), py::arg("bound"),
             py::arg("is_strict"))
        .def_property_readonly("i", &NativeConstraint::i)
        .def_property_readonly("j", &NativeConstraint::j)
        .def_property_readonly("value", &NativeConstraint::value)
        .def("__repr__", [](const NativeConstraint& constraint) {
            return "<_NativeConstraint i=" + std::to_string(constraint.i()) + " j=" + std::to_string(constraint.j()) +
                   " value=" + std::to_string(constraint.value()) + ">";
        });

    py::class_<NativeDBM>(m, "_NativeDBM")
        .def("copy", &NativeDBM::copy)
        .def("get_dimension", &NativeDBM::get_dimension)
        .def("to_string", &NativeDBM::to_string, py::arg("names"), py::arg("full") = false)
        .def("raw_matrix", &NativeDBM::raw_matrix)
        .def("to_min_dbm", &NativeDBM::to_min_dbm, py::arg("minimize_graph") = true,
             py::arg("try_constraints_16") = true);

    py::class_<NativeFederation>(m, "_NativeFederation")
        .def(py::init<cindex_t>(), py::arg("dim"))
        .def(py::init<cindex_t, const NativeConstraint&>(), py::arg("dim"), py::arg("constraint"))
        .def("copy", &NativeFederation::copy)
        .def("get_dimension", &NativeFederation::get_dimension)
        .def("size", &NativeFederation::size)
        .def("is_empty", &NativeFederation::is_empty)
        .def("has_zero", &NativeFederation::has_zero)
        .def("hash", &NativeFederation::hash)
        .def("to_string", &NativeFederation::to_string, py::arg("names"), py::arg("full") = false)
        .def("to_dbm_list", &NativeFederation::to_dbm_list)
        .def("and_op", &NativeFederation::and_op, py::arg("other"))
        .def("or_op", &NativeFederation::or_op, py::arg("other"))
        .def("add_op", &NativeFederation::add_op, py::arg("other"))
        .def("minus_op", &NativeFederation::minus_op, py::arg("other"))
        .def("iand", &NativeFederation::iand, py::arg("other"))
        .def("ior", &NativeFederation::ior, py::arg("other"))
        .def("iadd", &NativeFederation::iadd, py::arg("other"))
        .def("isub", &NativeFederation::isub, py::arg("other"))
        .def("up", &NativeFederation::up)
        .def("down", &NativeFederation::down)
        .def("merge_reduce", &NativeFederation::merge_reduce, py::arg("skip") = 0, py::arg("expensive_try") = 0)
        .def("free_clock", &NativeFederation::free_clock, py::arg("clock"))
        .def("set_zero", &NativeFederation::set_zero)
        .def("set_init", &NativeFederation::set_init)
        .def("convex_hull", &NativeFederation::convex_hull)
        .def("predt", &NativeFederation::predt, py::arg("other"))
        .def("intern", &NativeFederation::intern)
        .def("update_value", &NativeFederation::update_value, py::arg("clock"), py::arg("value"))
        .def("eq", &NativeFederation::eq, py::arg("other"))
        .def("lt", &NativeFederation::lt, py::arg("other"))
        .def("gt", &NativeFederation::gt, py::arg("other"))
        .def("le", &NativeFederation::le, py::arg("other"))
        .def("ge", &NativeFederation::ge, py::arg("other"))
        .def("contains_int", &NativeFederation::contains_int, py::arg("point"))
        .def("contains_float", &NativeFederation::contains_float, py::arg("point"))
        .def("extrapolate_max_bounds", &NativeFederation::extrapolate_max_bounds, py::arg("max_bounds"));
}
