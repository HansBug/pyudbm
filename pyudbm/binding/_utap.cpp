#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <utap/document.h>
#include <utap/utap.h>

#include <cstdio>
#include <filesystem>
#include <fstream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace py = pybind11;

namespace {

class ParseError : public std::runtime_error
{
public:
    explicit ParseError(const std::string& message): std::runtime_error(message) {}
};

class NativeDocument
{
public:
    explicit NativeDocument(std::shared_ptr<UTAP::Document> document): document_(std::move(document)) {}

    bool has_errors() const { return document_->has_errors(); }
    bool has_warnings() const { return document_->has_warnings(); }
    std::size_t error_count() const { return document_->get_errors().size(); }
    std::size_t warning_count() const { return document_->get_warnings().size(); }
    bool modified() const { return document_->is_modified(); }

    std::string repr() const
    {
        std::ostringstream oss;
        oss << "<_utap._NativeDocument errors=" << error_count() << " warnings=" << warning_count() << ">";
        return oss.str();
    }

private:
    std::shared_ptr<UTAP::Document> document_;
};

[[noreturn]] void throw_file_not_found(const std::filesystem::path& path)
{
    const auto message = "No such file or directory: " + path.string();
    PyErr_SetString(PyExc_FileNotFoundError, message.c_str());
    throw py::error_already_set();
}

std::string read_text_file(const std::filesystem::path& path)
{
    std::ifstream stream(path, std::ios::in | std::ios::binary);
    if (!stream) {
        throw_file_not_found(path);
    }

    std::ostringstream buffer;
    buffer << stream.rdbuf();
    return buffer.str();
}

std::string py_fspath(const py::object& path_object)
{
    return py::module::import("os").attr("fspath")(path_object).cast<std::string>();
}

std::vector<std::filesystem::path> py_libpaths(const py::iterable& libpaths_object)
{
    std::vector<std::filesystem::path> libpaths;
    for (const py::handle& item : libpaths_object) {
        libpaths.emplace_back(py_fspath(py::reinterpret_borrow<py::object>(item)));
    }
    return libpaths;
}

std::string first_error_message(const UTAP::Document& document)
{
    const auto& errors = document.get_errors();
    if (errors.empty()) {
        return {};
    }
    return errors.front().msg;
}

[[noreturn]] void raise_parse_error(const char* format_name, const UTAP::Document& document, int32_t return_code)
{
    if (document.has_errors()) {
        const auto message = std::string(format_name) + " parse failed: " + first_error_message(document);
        throw ParseError(message);
    }

    if (return_code != 0) {
        std::ostringstream oss;
        oss << format_name << " parse failed with code " << return_code;
        throw ParseError(oss.str());
    }

    throw ParseError(std::string(format_name) + " parse failed without UTAP diagnostics");
}

std::shared_ptr<NativeDocument> wrap_document(std::shared_ptr<UTAP::Document> document)
{
    return std::make_shared<NativeDocument>(std::move(document));
}

std::shared_ptr<NativeDocument> parse_xml_file(
    const std::filesystem::path& path,
    bool newxta,
    const std::vector<std::filesystem::path>& libpaths
)
{
    if (!std::filesystem::exists(path)) {
        throw_file_not_found(path);
    }

    auto document = std::make_shared<UTAP::Document>();
    const auto path_string = path.string();
    int32_t return_code = 0;
    try {
        py::gil_scoped_release release;
        return_code = parse_XML_file(path_string.c_str(), document.get(), newxta, libpaths);
    } catch (const std::exception& ex) {
        throw ParseError(std::string("XML parse failed: ") + ex.what());
    }

    if (return_code != 0 || document->has_errors()) {
        raise_parse_error("XML", *document, return_code);
    }

    return wrap_document(std::move(document));
}

std::shared_ptr<NativeDocument> parse_xml_buffer(
    const std::string& buffer,
    bool newxta,
    const std::vector<std::filesystem::path>& libpaths
)
{
    auto document = std::make_shared<UTAP::Document>();
    int32_t return_code = 0;
    try {
        py::gil_scoped_release release;
        return_code = parse_XML_buffer(buffer.c_str(), document.get(), newxta, libpaths);
    } catch (const std::exception& ex) {
        throw ParseError(std::string("XML parse failed: ") + ex.what());
    }

    if (return_code != 0 || document->has_errors()) {
        raise_parse_error("XML", *document, return_code);
    }

    return wrap_document(std::move(document));
}

std::shared_ptr<NativeDocument> parse_xta_buffer(const std::string& buffer, bool newxta)
{
    auto document = std::make_shared<UTAP::Document>();
    bool ok = false;
    try {
        py::gil_scoped_release release;
        ok = parse_XTA(buffer.c_str(), document.get(), newxta);
    } catch (const std::exception& ex) {
        throw ParseError(std::string("XTA parse failed: ") + ex.what());
    }

    if (!ok || document->has_errors()) {
        raise_parse_error("XTA", *document, 0);
    }

    return wrap_document(std::move(document));
}

std::shared_ptr<NativeDocument> parse_xta_file(const std::filesystem::path& path, bool newxta)
{
    return parse_xta_buffer(read_text_file(path), newxta);
}

}  // namespace

PYBIND11_MODULE(_utap, m)
{
    m.doc() = "Minimal native UTAP binding surface.";

    py::register_exception<ParseError>(m, "ParseError", PyExc_RuntimeError);

    py::class_<NativeDocument, std::shared_ptr<NativeDocument>>(m, "_NativeDocument")
        .def_property_readonly("has_errors", &NativeDocument::has_errors)
        .def_property_readonly("has_warnings", &NativeDocument::has_warnings)
        .def_property_readonly("error_count", &NativeDocument::error_count)
        .def_property_readonly("warning_count", &NativeDocument::warning_count)
        .def_property_readonly("modified", &NativeDocument::modified)
        .def("__repr__", &NativeDocument::repr);

    m.def(
        "load_xml",
        [](const py::object& path, bool newxta, const py::iterable& libpaths) {
            return parse_xml_file(std::filesystem::path{py_fspath(path)}, newxta, py_libpaths(libpaths));
        },
        py::arg("path"),
        py::arg("newxta") = true,
        py::arg("libpaths") = py::tuple()
    );
    m.def(
        "loads_xml",
        [](const std::string& buffer, bool newxta, const py::iterable& libpaths) {
            return parse_xml_buffer(buffer, newxta, py_libpaths(libpaths));
        },
        py::arg("buffer"),
        py::arg("newxta") = true,
        py::arg("libpaths") = py::tuple()
    );
    m.def(
        "load_xta",
        [](const py::object& path, bool newxta) {
            return parse_xta_file(std::filesystem::path{py_fspath(path)}, newxta);
        },
        py::arg("path"),
        py::arg("newxta") = true
    );
    m.def("loads_xta", &parse_xta_buffer, py::arg("buffer"), py::arg("newxta") = true);
    m.def("builtin_declarations", []() { return std::string(utap_builtin_declarations()); });
}
