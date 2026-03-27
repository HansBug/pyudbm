#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "pyudbm/binding/_utap_bindings.hpp"

#include <utap/DocumentBuilder.hpp>
#include <utap/featurechecker.h>
#include <utap/typechecker.h>
#include <utap/utap.h>

#include <cstdint>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace py = pybind11;

namespace {

using pyudbm::binding::utap_native::ParseError;

struct LocationPayload
{
    std::string name;
    std::string invariant;
    bool urgent;
    bool committed;
};

struct EdgePayload
{
    std::string source;
    std::string target;
    std::string guard;
    std::string sync;
    std::string update;
};

struct TemplatePayload
{
    std::string name;
    std::string parameters;
    std::vector<std::string> declarations;
    std::vector<LocationPayload> locations;
    std::vector<EdgePayload> edges;
    std::string initial_location;
};

struct ProcessPayload
{
    std::string name;
    std::string template_name;
    std::vector<std::string> arguments;
};

struct ResourcePayload
{
    std::string name;
    std::string value;
    std::optional<std::string> unit;
};

struct ExpectationPayload
{
    std::string value_type;
    std::string status;
    std::string value;
    std::vector<ResourcePayload> resources;
};

struct OptionPayload
{
    std::string name;
    std::string value;
};

struct QueryPayload
{
    std::string formula;
    std::string comment;
    std::vector<OptionPayload> options;
    ExpectationPayload expectation;
    std::string location;
};

std::string last_error_message(const UTAP::Document& document)
{
    const auto& errors = document.get_errors();
    if (errors.empty()) {
        return {};
    }
    return errors.back().msg;
}

[[noreturn]] void raise_build_error(const std::string& context, const UTAP::Document& document, int32_t return_code)
{
    if (document.has_errors()) {
        throw ParseError("UTAP native build failed while " + context + ": " + last_error_message(document));
    }

    if (return_code < 0) {
        std::ostringstream oss;
        oss << "UTAP native build failed while " << context << " with code " << return_code;
        throw ParseError(oss.str());
    }

    throw ParseError("UTAP native build failed while " + context);
}

void parse_xta_part_or_throw(
    const std::string& text,
    UTAP::DocumentBuilder& builder,
    UTAP::Document& document,
    UTAP::xta_part_t part,
    const std::string& context
)
{
    if (text.empty()) {
        return;
    }

    int32_t return_code = 0;
    try {
        py::gil_scoped_release release;
        return_code = parse_XTA(text.c_str(), &builder, true, part, "");
    } catch (const std::exception& ex) {
        throw ParseError("UTAP native build failed while " + context + ": " + ex.what());
    }

    if (return_code < 0 || document.has_errors()) {
        raise_build_error(context, document, return_code);
    }
}

std::string join_with_separator(const std::vector<std::string>& items, const char* separator)
{
    std::ostringstream oss;
    for (std::size_t index = 0; index < items.size(); ++index) {
        if (index != 0) {
            oss << separator;
        }
        oss << items[index];
    }
    return oss.str();
}

std::vector<std::string> to_string_vector(const py::handle& object)
{
    std::vector<std::string> result;
    for (const py::handle& item : py::reinterpret_borrow<py::sequence>(object)) {
        result.push_back(py::cast<std::string>(item));
    }
    return result;
}

LocationPayload parse_location_payload(const py::dict& payload)
{
    return LocationPayload{
        py::cast<std::string>(payload["name"]),
        py::cast<std::string>(payload["invariant"]),
        py::cast<bool>(payload["urgent"]),
        py::cast<bool>(payload["committed"]),
    };
}

EdgePayload parse_edge_payload(const py::dict& payload)
{
    return EdgePayload{
        py::cast<std::string>(payload["source"]),
        py::cast<std::string>(payload["target"]),
        py::cast<std::string>(payload["guard"]),
        py::cast<std::string>(payload["sync"]),
        py::cast<std::string>(payload["update"]),
    };
}

TemplatePayload parse_template_payload(const py::dict& payload)
{
    TemplatePayload result;
    result.name = py::cast<std::string>(payload["name"]);
    result.parameters = py::cast<std::string>(payload["parameters"]);
    result.declarations = to_string_vector(payload["declarations"]);
    result.initial_location = py::cast<std::string>(payload["initial_location"]);

    for (const py::handle& item : py::reinterpret_borrow<py::sequence>(payload["locations"])) {
        result.locations.push_back(parse_location_payload(py::reinterpret_borrow<py::dict>(item)));
    }
    for (const py::handle& item : py::reinterpret_borrow<py::sequence>(payload["edges"])) {
        result.edges.push_back(parse_edge_payload(py::reinterpret_borrow<py::dict>(item)));
    }
    return result;
}

ProcessPayload parse_process_payload(const py::dict& payload)
{
    ProcessPayload result;
    result.name = py::cast<std::string>(payload["name"]);
    result.template_name = py::cast<std::string>(payload["template_name"]);
    result.arguments = to_string_vector(payload["arguments"]);
    return result;
}

ResourcePayload parse_resource_payload(const py::dict& payload)
{
    ResourcePayload result;
    result.name = py::cast<std::string>(payload["name"]);
    result.value = py::cast<std::string>(payload["value"]);
    if (!payload["unit"].is_none()) {
        result.unit = py::cast<std::string>(payload["unit"]);
    }
    return result;
}

ExpectationPayload parse_expectation_payload(const py::dict& payload)
{
    ExpectationPayload result;
    result.value_type = py::cast<std::string>(payload["value_type"]);
    result.status = py::cast<std::string>(payload["status"]);
    result.value = py::cast<std::string>(payload["value"]);
    for (const py::handle& item : py::reinterpret_borrow<py::sequence>(payload["resources"])) {
        result.resources.push_back(parse_resource_payload(py::reinterpret_borrow<py::dict>(item)));
    }
    return result;
}

OptionPayload parse_option_payload(const py::dict& payload)
{
    return OptionPayload{
        py::cast<std::string>(payload["name"]),
        py::cast<std::string>(payload["value"]),
    };
}

QueryPayload parse_query_payload(const py::dict& payload)
{
    QueryPayload result;
    result.formula = py::cast<std::string>(payload["formula"]);
    result.comment = py::cast<std::string>(payload["comment"]);
    result.expectation = parse_expectation_payload(py::reinterpret_borrow<py::dict>(payload["expectation"]));
    result.location = py::cast<std::string>(payload["location"]);
    for (const py::handle& item : py::reinterpret_borrow<py::sequence>(payload["options"])) {
        result.options.push_back(parse_option_payload(py::reinterpret_borrow<py::dict>(item)));
    }
    return result;
}

UTAP::expectation_type expectation_type_from_string(const std::string& value_type)
{
    if (value_type.empty() || value_type == "Symbolic") {
        return UTAP::expectation_type::Symbolic;
    }
    if (value_type == "Probability") {
        return UTAP::expectation_type::Probability;
    }
    if (value_type == "NumericValue") {
        return UTAP::expectation_type::NumericValue;
    }
    return UTAP::expectation_type::_ErrorValue;
}

UTAP::query_status_t expectation_status_from_string(const std::string& status)
{
    if (status.empty() || status == "True") {
        return UTAP::query_status_t::True;
    }
    if (status == "False") {
        return UTAP::query_status_t::False;
    }
    if (status == "MaybeTrue") {
        return UTAP::query_status_t::MaybeTrue;
    }
    if (status == "MaybeFalse") {
        return UTAP::query_status_t::MaybeFalse;
    }
    return UTAP::query_status_t::Unknown;
}

std::string build_system_block(const std::vector<ProcessPayload>& processes, const std::vector<std::string>& system_names)
{
    std::ostringstream oss;
    for (const auto& process : processes) {
        oss << process.name << " = " << process.template_name << "(" << join_with_separator(process.arguments, ", ")
            << ");\n";
    }
    oss << "system " << join_with_separator(system_names, ", ") << ";";
    return oss.str();
}

void build_templates(UTAP::DocumentBuilder& builder, UTAP::Document& document, const std::vector<TemplatePayload>& templates)
{
    for (const auto& templ : templates) {
        parse_xta_part_or_throw(templ.parameters, builder, document, UTAP::S_PARAMETERS, "parsing template parameters");
        builder.proc_begin(templ.name.c_str(), true, "", "");

        for (const auto& declaration : templ.declarations) {
            parse_xta_part_or_throw(declaration, builder, document, UTAP::S_LOCAL_DECL, "parsing template declarations");
        }

        for (const auto& location : templ.locations) {
            if (!location.invariant.empty()) {
                parse_xta_part_or_throw(location.invariant, builder, document, UTAP::S_INVARIANT, "parsing invariant");
                builder.proc_location(location.name.c_str(), true, false);
            } else {
                builder.proc_location(location.name.c_str(), false, false);
            }

            if (document.has_errors()) {
                raise_build_error("adding location", document, 1);
            }

            if (location.urgent) {
                builder.proc_location_urgent(location.name.c_str());
            }
            if (location.committed) {
                builder.proc_location_commit(location.name.c_str());
            }
            if (document.has_errors()) {
                raise_build_error("configuring location", document, 1);
            }
        }

        builder.proc_location_init(templ.initial_location.c_str());
        if (document.has_errors()) {
            raise_build_error("setting initial location", document, 1);
        }

        for (const auto& edge : templ.edges) {
            builder.proc_edge_begin(edge.source.c_str(), edge.target.c_str(), false, "");
            if (document.has_errors()) {
                raise_build_error("starting edge", document, 1);
            }

            parse_xta_part_or_throw(edge.guard, builder, document, UTAP::S_GUARD, "parsing edge guard");
            parse_xta_part_or_throw(edge.sync, builder, document, UTAP::S_SYNC, "parsing edge synchronisation");
            parse_xta_part_or_throw(edge.update, builder, document, UTAP::S_ASSIGN, "parsing edge update");
            builder.proc_edge_end(edge.source.c_str(), edge.target.c_str());
        }

        builder.proc_end();
    }
}

void build_queries(UTAP::Document& document, const std::vector<QueryPayload>& queries)
{
    for (const auto& item : queries) {
        UTAP::query_t query;
        query.formula = item.formula;
        query.comment = item.comment;
        query.location = item.location;
        query.expectation.value_type = expectation_type_from_string(item.expectation.value_type);
        query.expectation.status = expectation_status_from_string(item.expectation.status);
        query.expectation.value = item.expectation.value;

        for (const auto& option : item.options) {
            query.options.emplace_back(option.name, option.value);
        }
        for (const auto& resource : item.expectation.resources) {
            query.expectation.resources.push_back(UTAP::resource_t{resource.name, resource.value, resource.unit});
        }

        document.add_query(std::move(query));
    }
}

py::object build_model(const py::dict& payload)
{
    auto document = std::make_shared<UTAP::Document>();
    UTAP::DocumentBuilder builder(*document);

    parse_xta_part_or_throw(
        std::string(utap_builtin_declarations()),
        builder,
        *document,
        UTAP::S_DECLARATION,
        "loading builtin declarations"
    );

    for (const py::handle& item : py::reinterpret_borrow<py::sequence>(payload["declarations"])) {
        parse_xta_part_or_throw(py::cast<std::string>(item), builder, *document, UTAP::S_DECLARATION, "parsing declarations");
    }

    std::vector<TemplatePayload> templates;
    for (const py::handle& item : py::reinterpret_borrow<py::sequence>(payload["templates"])) {
        templates.push_back(parse_template_payload(py::reinterpret_borrow<py::dict>(item)));
    }
    build_templates(builder, *document, templates);

    std::vector<ProcessPayload> processes;
    for (const py::handle& item : py::reinterpret_borrow<py::sequence>(payload["processes"])) {
        processes.push_back(parse_process_payload(py::reinterpret_borrow<py::dict>(item)));
    }
    const auto system_names = to_string_vector(payload["system_process_names"]);
    parse_xta_part_or_throw(build_system_block(processes, system_names), builder, *document, UTAP::S_SYSTEM, "parsing system");

    std::vector<QueryPayload> queries;
    for (const py::handle& item : py::reinterpret_borrow<py::sequence>(payload["queries"])) {
        queries.push_back(parse_query_payload(py::reinterpret_borrow<py::dict>(item)));
    }
    build_queries(*document, queries);

    if (document->has_errors()) {
        raise_build_error("finishing document", *document, 1);
    }

    try {
        py::gil_scoped_release release;
        UTAP::TypeChecker checker(*document);
        document->accept(checker);
        if (!document->has_errors()) {
            UTAP::FeatureChecker feature_checker(*document);
            document->set_supported_methods(feature_checker.get_supported_methods());
        }
    } catch (const std::exception& ex) {
        throw ParseError(std::string("UTAP native build failed during type checking: ") + ex.what());
    }

    if (document->has_errors()) {
        raise_build_error("type checking", *document, 1);
    }

    return pyudbm::binding::utap_native::wrap_document_object(std::move(document));
}

}  // namespace

namespace pyudbm { namespace binding { namespace utap_native {

void bind_utap_builder(py::module& m)
{
    m.def("_build_model", &build_model, py::arg("payload"));
}

}}}  // namespace pyudbm::binding::utap_native
