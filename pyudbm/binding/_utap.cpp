#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <utap/builder.h>
#include <utap/common.h>
#include <utap/document.h>
#include <utap/prettyprinter.h>
#include <utap/property.h>
#include <utap/utap.h>

#include <cstdint>
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

std::string normalize_newlines(const std::string& input)
{
    std::string normalized;
    normalized.reserve(input.size());

    for (std::size_t index = 0; index < input.size(); ++index) {
        if (input[index] != '\r') {
            normalized.push_back(input[index]);
            continue;
        }

        if ((index + 1) < input.size() && input[index + 1] == '\n') {
            ++index;
        }
        normalized.push_back('\n');
    }

    return normalized;
}

const std::string& normalized_text_view(const std::string& input, std::string& storage)
{
    if (input.find('\r') == std::string::npos) {
        return input;
    }

    storage = normalize_newlines(input);
    return storage;
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

[[noreturn]] void raise_text_render_error(const char* format_name, int32_t return_code)
{
    std::ostringstream oss;
    oss << format_name << " text rendering failed with code " << return_code;
    throw ParseError(oss.str());
}

std::string pretty_print_xta_part(const std::string& buffer, bool newxta, UTAP::xta_part_t part, const char* format_name)
{
    std::ostringstream stream;
    UTAP::PrettyPrinter pretty_printer(stream);
    std::string normalized_buffer;
    const auto& parse_buffer = normalized_text_view(buffer, normalized_buffer);
    int32_t return_code = 0;
    try {
        py::gil_scoped_release release;
        return_code = parse_XTA(parse_buffer.c_str(), &pretty_printer, newxta, part, "");
    } catch (const std::exception& ex) {
        throw ParseError(std::string(format_name) + " text rendering failed: " + ex.what());
    }

    if (return_code < 0) {
        raise_text_render_error(format_name, return_code);
    }

    return stream.str();
}

std::string textual_builtin_preamble(bool newxta)
{
    if (!newxta) {
        return {};
    }
    return pretty_print_xta_part(utap_builtin_declarations(), true, UTAP::S_DECLARATION, "builtin preamble");
}

std::string strip_exact_prefix(const std::string& text, const std::string& prefix)
{
    if (!prefix.empty() && text.size() >= prefix.size() && text.compare(0, prefix.size(), prefix) == 0) {
        return text.substr(prefix.size());
    }
    return text;
}

bool is_known_position(const UTAP::position_t& position)
{
    return position.start != UTAP::position_t::unknown_pos && position.end != UTAP::position_t::unknown_pos;
}

py::object path_to_object(const std::shared_ptr<std::string>& path)
{
    if (!path) {
        return py::none();
    }
    return py::str(*path);
}

py::dict make_unknown_position_dict()
{
    py::dict result;
    result["start"] = UTAP::position_t::unknown_pos;
    result["end"] = UTAP::position_t::unknown_pos;
    result["line"] = py::none();
    result["column"] = py::none();
    result["end_line"] = py::none();
    result["end_column"] = py::none();
    result["path"] = py::none();
    return result;
}

py::dict make_position_dict(const UTAP::Document& document, const UTAP::position_t& position)
{
    py::dict result = make_unknown_position_dict();
    result["start"] = position.start;
    result["end"] = position.end;

    if (!is_known_position(position)) {
        return result;
    }

    const auto& start_line = document.find_position(position.start);
    const auto& end_line = document.find_position(position.end);
    result["line"] = start_line.line;
    result["column"] = (position.start - start_line.position) + 1;
    result["end_line"] = end_line.line;
    result["end_column"] = (position.end - end_line.position) + 1;
    result["path"] = path_to_object(start_line.path);
    return result;
}

py::dict make_diagnostic_position_dict(const UTAP::error_t& diagnostic)
{
    py::dict result;
    result["start"] = diagnostic.position.start;
    result["end"] = diagnostic.position.end;
    result["line"] = diagnostic.start.line;
    result["column"] = (diagnostic.position.start - diagnostic.start.position) + 1;
    result["end_line"] = diagnostic.end.line;
    result["end_column"] = (diagnostic.position.end - diagnostic.end.position) + 1;
    result["path"] = path_to_object(diagnostic.start.path);
    return result;
}

py::dict option_to_dict(const UTAP::option_t& option)
{
    py::dict result;
    result["name"] = option.name;
    result["value"] = option.value;
    return result;
}

py::list options_to_list(const UTAP::options_t& options)
{
    py::list result;
    for (const auto& option : options) {
        result.append(option_to_dict(option));
    }
    return result;
}

py::dict resource_to_dict(const UTAP::resource_t& resource)
{
    py::dict result;
    result["name"] = resource.name;
    result["value"] = resource.value;
    if (resource.unit.has_value()) {
        result["unit"] = resource.unit.value();
    } else {
        result["unit"] = py::none();
    }
    return result;
}

py::list resources_to_list(const UTAP::resources_t& resources)
{
    py::list result;
    for (const auto& resource : resources) {
        result.append(resource_to_dict(resource));
    }
    return result;
}

std::string expectation_type_name(UTAP::expectation_type type)
{
    switch (type) {
    case UTAP::expectation_type::Symbolic: return "Symbolic";
    case UTAP::expectation_type::Probability: return "Probability";
    case UTAP::expectation_type::NumericValue: return "NumericValue";
    case UTAP::expectation_type::_ErrorValue: return "ErrorValue";
    }
    return "Unknown";
}

std::string query_status_name(UTAP::query_status_t status)
{
    switch (status) {
    case UTAP::query_status_t::True: return "True";
    case UTAP::query_status_t::False: return "False";
    case UTAP::query_status_t::MaybeTrue: return "MaybeTrue";
    case UTAP::query_status_t::MaybeFalse: return "MaybeFalse";
    case UTAP::query_status_t::Unknown: return "Unknown";
    }
    return "Unknown";
}

std::string quantifier_name(UTAP::quant_t quantifier)
{
    switch (quantifier) {
    case UTAP::quant_t::empty: return "empty";
    case UTAP::quant_t::AG: return "AG";
    case UTAP::quant_t::EE: return "EE";
    case UTAP::quant_t::EG: return "EG";
    case UTAP::quant_t::AE: return "AE";
    case UTAP::quant_t::leads_to: return "leads_to";
    case UTAP::quant_t::probaMinBox: return "probaMinBox";
    case UTAP::quant_t::probaMinDiamond: return "probaMinDiamond";
    case UTAP::quant_t::probaBox: return "probaBox";
    case UTAP::quant_t::probaDiamond: return "probaDiamond";
    case UTAP::quant_t::probaCompare: return "probaCompare";
    case UTAP::quant_t::probaExpected: return "probaExpected";
    case UTAP::quant_t::probaSimulate: return "probaSimulate";
    case UTAP::quant_t::probaSimulateReach: return "probaSimulateReach";
    case UTAP::quant_t::Mitl: return "Mitl";
    case UTAP::quant_t::control_AF: return "control_AF";
    case UTAP::quant_t::control_AUntil: return "control_AUntil";
    case UTAP::quant_t::control_AG: return "control_AG";
    case UTAP::quant_t::control_AWeakUntil: return "control_AWeakUntil";
    case UTAP::quant_t::control_AB: return "control_AB";
    case UTAP::quant_t::control_ABuchi: return "control_ABuchi";
    case UTAP::quant_t::EF_control_AF: return "EF_control_AF";
    case UTAP::quant_t::EF_control_AUntil: return "EF_control_AUntil";
    case UTAP::quant_t::EF_control_AG: return "EF_control_AG";
    case UTAP::quant_t::EF_control_AWeakUntil: return "EF_control_AWeakUntil";
    case UTAP::quant_t::control_opt_AF: return "control_opt_AF";
    case UTAP::quant_t::control_opt_AUntil: return "control_opt_AUntil";
    case UTAP::quant_t::control_opt_Def1_AF: return "control_opt_Def1_AF";
    case UTAP::quant_t::control_opt_Def1_AUntil: return "control_opt_Def1_AUntil";
    case UTAP::quant_t::control_opt_Def2_AF: return "control_opt_Def2_AF";
    case UTAP::quant_t::control_opt_Def2_AUntil: return "control_opt_Def2_AUntil";
    case UTAP::quant_t::PO_control_AF: return "PO_control_AF";
    case UTAP::quant_t::PO_control_AUntil: return "PO_control_AUntil";
    case UTAP::quant_t::PO_control_AG: return "PO_control_AG";
    case UTAP::quant_t::PO_control_AWeakUntil: return "PO_control_AWeakUntil";
    case UTAP::quant_t::control_SMC_AUntil: return "control_SMC_AUntil";
    case UTAP::quant_t::control_SMC_AF: return "control_SMC_AF";
    case UTAP::quant_t::control_MinExp: return "control_MinExp";
    case UTAP::quant_t::control_MaxExp: return "control_MaxExp";
    case UTAP::quant_t::strategy_load: return "strategy_load";
    case UTAP::quant_t::strategy_save: return "strategy_save";
    case UTAP::quant_t::supremum: return "supremum";
    case UTAP::quant_t::infimum: return "infimum";
    case UTAP::quant_t::bounds: return "bounds";
    case UTAP::quant_t::PMax: return "PMax";
    case UTAP::quant_t::scenario: return "scenario";
    }
    return "unknown";
}

std::string strategy_type_name(UTAP::StrategyType strategy_type)
{
    switch (strategy_type) {
    case UTAP::StrategyType::None: return "None";
    case UTAP::StrategyType::ZoneStrategy: return "ZoneStrategy";
    case UTAP::StrategyType::NonZoneStrategy: return "NonZoneStrategy";
    }
    return "Unknown";
}

std::string property_status_name(UTAP::status_t status)
{
    switch (status) {
    case UTAP::status_t::WAITING: return "WAITING";
    case UTAP::status_t::RUNNING: return "RUNNING";
    case UTAP::status_t::DONE_TRUE: return "DONE_TRUE";
    case UTAP::status_t::DONE_FALSE: return "DONE_FALSE";
    case UTAP::status_t::DONE_MAYBE_TRUE: return "DONE_MAYBE_TRUE";
    case UTAP::status_t::DONE_MAYBE_FALSE: return "DONE_MAYBE_FALSE";
    case UTAP::status_t::DONE_ERROR: return "DONE_ERROR";
    }
    return "UNKNOWN";
}

bool quantifier_is_smc(UTAP::quant_t quantifier)
{
    switch (quantifier) {
    case UTAP::quant_t::probaMinBox:
    case UTAP::quant_t::probaMinDiamond:
    case UTAP::quant_t::probaBox:
    case UTAP::quant_t::probaDiamond:
    case UTAP::quant_t::probaCompare:
    case UTAP::quant_t::probaExpected:
    case UTAP::quant_t::probaSimulate:
    case UTAP::quant_t::probaSimulateReach:
    case UTAP::quant_t::Mitl:
    case UTAP::quant_t::control_SMC_AUntil:
    case UTAP::quant_t::control_SMC_AF:
    case UTAP::quant_t::control_MinExp:
    case UTAP::quant_t::control_MaxExp: return true;
    default: return false;
    }
}

py::dict expectation_to_dict(const UTAP::expectation_t& expectation)
{
    py::dict result;
    result["value_type"] = expectation_type_name(expectation.value_type);
    result["status"] = query_status_name(expectation.status);
    result["value"] = expectation.value;
    result["resources"] = resources_to_list(expectation.resources);
    return result;
}

py::dict type_to_dict(const UTAP::Document& document, const UTAP::type_t& type);
py::dict expression_to_dict(const UTAP::Document& document, const UTAP::expression_t& expression);

template <typename Fn>
std::string safe_stringify(Fn&& fn)
{
    try {
        return fn();
    } catch (const std::exception&) {
        return {};
    }
}

std::string expression_text_or_empty(const UTAP::expression_t& expression)
{
    return expression.empty() ? std::string{} : safe_stringify([&expression]() { return expression.str(); });
}

std::string type_name_or_empty(const UTAP::type_t& type)
{
    if (type.unknown()) {
        return {};
    }
    if (type.is_integer()) {
        return "int";
    }
    if (type.isBoolean()) {
        return "bool";
    }
    if (type.is_clock()) {
        return "clock";
    }
    if (type.is_process()) {
        return "process";
    }
    if (type.is_process_set()) {
        return "process_set";
    }
    if (type.is_location()) {
        return "location";
    }
    if (type.is_location_expr()) {
        return "location_expr";
    }
    if (type.is_instance_line()) {
        return "instance_line";
    }
    if (type.is_branchpoint()) {
        return "branchpoint";
    }
    if (type.is_channel()) {
        return "channel";
    }
    if (type.is_array()) {
        return "array";
    }
    if (type.is_scalar()) {
        return "scalar";
    }
    if (type.is_record()) {
        return "record";
    }
    if (type.is_diff()) {
        return "diff";
    }
    if (type.is_void()) {
        return "void";
    }
    if (type.is_cost()) {
        return "cost";
    }
    if (type.is_double()) {
        return "double";
    }
    if (type.is_string()) {
        return "string";
    }
    if (type.is_function()) {
        return "function";
    }
    if (type.is_function_external()) {
        return "function_external";
    }
    if (type.is_range()) {
        return "range";
    }
    return {};
}

std::string type_text_or_empty(const UTAP::type_t& type)
{
    return type_name_or_empty(type);
}

std::string type_declaration_or_empty(const UTAP::type_t& type)
{
    return type_name_or_empty(type);
}

std::string declarations_text_or_empty(const UTAP::declarations_t& declarations, bool global)
{
    return safe_stringify([&declarations, global]() { return declarations.str(global); });
}

const std::set<std::string>& builtin_global_names()
{
    static const std::set<std::string> names = {
        "INT8_MIN",
        "INT8_MAX",
        "UINT8_MAX",
        "INT16_MIN",
        "INT16_MAX",
        "UINT16_MAX",
        "INT32_MIN",
        "INT32_MAX",
        "FLT_MIN",
        "FLT_MAX",
        "DBL_MIN",
        "DBL_MAX",
        "M_PI",
        "M_PI_2",
        "M_PI_4",
        "M_E",
        "M_LOG2E",
        "M_LOG10E",
        "M_LN2",
        "M_LN10",
        "M_1_PI",
        "M_2_PI",
        "M_2_SQRTPI",
        "M_SQRT2",
        "M_SQRT1_2",
        "int8_t",
        "uint8_t",
        "int16_t",
        "uint16_t",
        "int32_t",
    };
    return names;
}

bool is_builtin_global_name(const std::string& name)
{
    return builtin_global_names().find(name) != builtin_global_names().end();
}

std::string user_declarations_text(const UTAP::declarations_t& declarations, bool global)
{
    std::vector<std::string> sections;

    std::ostringstream constants;
    bool wrote_constants = false;
    for (const auto& variable : declarations.variables) {
        if (variable.uid.get_type().get_kind() == UTAP::Constants::CONSTANT && !is_builtin_global_name(variable.uid.get_name())) {
            if (!wrote_constants) {
                constants << "// constants\n";
                wrote_constants = true;
            }
            variable.print(constants) << ";\n";
        }
    }
    if (wrote_constants) {
        sections.push_back(constants.str());
    }

    std::ostringstream typedefs;
    bool wrote_typedefs = false;
    for (const auto& symbol : declarations.frame) {
        if (symbol.get_type().get_kind() == UTAP::Constants::TYPEDEF && !is_builtin_global_name(symbol.get_name())) {
            if (!wrote_typedefs) {
                typedefs << "// type definitions\n";
                wrote_typedefs = true;
            }
            symbol.get_type().print_declaration(typedefs) << ";\n";
        }
    }
    if (wrote_typedefs) {
        sections.push_back(typedefs.str());
    }

    std::ostringstream variables;
    bool wrote_variables = false;
    for (const auto& variable : declarations.variables) {
        if (variable.uid.get_type().get_kind() != UTAP::Constants::CONSTANT) {
            if (!wrote_variables) {
                variables << "// variables\n";
                wrote_variables = true;
            }
            variable.print(variables) << ";\n";
        }
    }
    if (wrote_variables) {
        sections.push_back(variables.str());
    }

    if (!declarations.functions.empty()) {
        std::ostringstream functions;
        functions << "// functions\n";
        for (const auto& function : declarations.functions) {
            function.print(functions) << "\n\n";
        }
        sections.push_back(functions.str());
    }

    std::ostringstream result;
    bool first = true;
    for (const auto& section : sections) {
        if (!first) {
            result << "\n";
        }
        first = false;
        result << section;
    }
    return result.str();
}

std::string expression_summary_or_empty(const UTAP::expression_t& expression)
{
    return expression.empty() ? std::string{} : safe_stringify([&expression]() { return expression.str(); });
}

std::string chan_priority_text_or_empty(const UTAP::chan_priority_t& priority)
{
    return safe_stringify([&priority]() { return priority.str(); });
}

bool is_clock_like_type(const UTAP::type_t& type)
{
    if (type.unknown()) {
        return false;
    }
    if (type.is_clock()) {
        return true;
    }
    if (type.is_array()) {
        return type.strip_array().is_clock();
    }
    return type.strip().is_clock();
}

void append_clock_name_if_needed(std::vector<std::string>& names, std::set<std::string>& seen, const std::string& name)
{
    if (seen.insert(name).second) {
        names.push_back(name);
    }
}

std::vector<std::string> declarations_clock_names(const UTAP::declarations_t& declarations)
{
    std::vector<std::string> names;
    std::set<std::string> seen;
    for (const auto& variable : declarations.variables) {
        if (is_clock_like_type(variable.uid.get_type())) {
            append_clock_name_if_needed(names, seen, variable.uid.get_name());
        }
    }
    return names;
}

std::vector<std::string> frame_clock_names(const UTAP::frame_t& frame)
{
    std::vector<std::string> names;
    std::set<std::string> seen;
    for (const auto& symbol : frame) {
        if (is_clock_like_type(symbol.get_type())) {
            append_clock_name_if_needed(names, seen, symbol.get_name());
        }
    }
    return names;
}

py::list string_vector_to_list(const std::vector<std::string>& values)
{
    py::list result;
    for (const auto& value : values) {
        result.append(value);
    }
    return result;
}

std::string join_strings(const std::vector<std::string>& parts, const char* separator)
{
    std::ostringstream oss;
    bool first = true;
    for (const auto& part : parts) {
        if (!first) {
            oss << separator;
        }
        first = false;
        oss << part;
    }
    return oss.str();
}

std::string parameters_to_string(const UTAP::frame_t& parameters)
{
    std::vector<std::string> parts;
    parts.reserve(parameters.get_size());
    for (const auto& symbol : parameters) {
        std::ostringstream item;
        const auto type = symbol.get_type();
        if (!type.unknown()) {
            item << type_declaration_or_empty(type);
            if (!symbol.get_name().empty()) {
                item << ' ';
            }
        }
        item << symbol.get_name();
        parts.push_back(item.str());
    }
    return join_strings(parts, ", ");
}

std::string arguments_to_string(const UTAP::instance_t& instance)
{
    std::vector<std::string> parts;
    parts.reserve(instance.parameters.get_size());
    for (const auto& symbol : instance.parameters) {
        const auto it = instance.mapping.find(symbol);
        parts.push_back(it == instance.mapping.end() ? std::string{} : expression_text_or_empty(it->second));
    }
    return join_strings(parts, ", ");
}

std::string mapping_to_string(const UTAP::instance_t& instance)
{
    std::vector<std::string> parts;
    parts.reserve(instance.mapping.size());
    for (const auto& entry : instance.mapping) {
        std::ostringstream item;
        item << entry.first.get_name() << " = " << expression_text_or_empty(entry.second);
        parts.push_back(item.str());
    }
    return join_strings(parts, "\n");
}

py::dict symbol_to_dict(const UTAP::Document& document, const UTAP::symbol_t& symbol)
{
    py::dict result;
    result["name"] = symbol.get_name();
    result["type"] = type_to_dict(document, symbol.get_type());
    result["position"] = make_position_dict(document, symbol.get_position());
    return result;
}

py::dict type_to_dict(const UTAP::Document& document, const UTAP::type_t& type)
{
    py::dict result;
    const bool is_unknown = type.unknown();
    result["kind"] = static_cast<int>(type.get_kind());
    try {
        result["position"] = is_unknown ? make_unknown_position_dict() : make_position_dict(document, type.get_position());
    } catch (const std::exception&) {
        result["position"] = make_unknown_position_dict();
    }
    try {
        result["size"] = is_unknown ? 0U : type.size();
    } catch (const std::exception&) {
        result["size"] = 0U;
    }
    result["text"] = type_text_or_empty(type);
    result["declaration"] = type_declaration_or_empty(type);
    result["is_unknown"] = is_unknown;
    result["is_range"] = type.is_range();
    result["is_integer"] = type.is_integer();
    result["is_boolean"] = type.isBoolean();
    result["is_function"] = type.is_function();
    result["is_function_external"] = type.is_function_external();
    result["is_clock"] = type.is_clock();
    result["is_process"] = type.is_process();
    result["is_process_set"] = type.is_process_set();
    result["is_location"] = type.is_location();
    result["is_location_expr"] = type.is_location_expr();
    result["is_instance_line"] = type.is_instance_line();
    result["is_branchpoint"] = type.is_branchpoint();
    result["is_channel"] = type.is_channel();
    result["is_record"] = type.is_record();
    result["is_array"] = type.is_array();
    result["is_scalar"] = type.is_scalar();
    result["is_diff"] = type.is_diff();
    result["is_void"] = type.is_void();
    result["is_cost"] = type.is_cost();
    result["is_integral"] = type.is_integral();
    result["is_invariant"] = type.is_invariant();
    result["is_probability"] = type.is_probability();
    result["is_guard"] = type.is_guard();
    result["is_constraint"] = type.is_constraint();
    result["is_formula"] = type.is_formula();
    result["is_double"] = type.is_double();
    result["is_string"] = type.is_string();
    return result;
}

py::dict expression_to_dict(const UTAP::Document& document, const UTAP::expression_t& expression)
{
    py::dict result;
    const bool is_empty = expression.empty();
    result["text"] = is_empty ? std::string{} : expression_text_or_empty(expression);
    try {
        result["kind"] = is_empty ? -1 : static_cast<int>(expression.get_kind());
    } catch (const std::exception&) {
        result["kind"] = -1;
    }
    try {
        result["position"] = is_empty ? make_unknown_position_dict() : make_position_dict(document, expression.get_position());
    } catch (const std::exception&) {
        result["position"] = make_unknown_position_dict();
    }
    try {
        result["type"] = type_to_dict(document, is_empty ? UTAP::type_t{} : expression.get_type());
    } catch (const std::exception&) {
        result["type"] = type_to_dict(document, UTAP::type_t{});
    }
    std::size_t child_count = 0;
    try {
        child_count = is_empty ? 0U : expression.get_size();
    } catch (const std::exception&) {
        child_count = 0U;
    }
    result["size"] = child_count;
    result["is_empty"] = is_empty;

    py::list children;
    if (!is_empty) {
        for (std::size_t index = 0; index < child_count; ++index) {
            try {
                children.append(expression_to_dict(document, expression.get(index)));
            } catch (const std::exception&) {
                children.append(expression_to_dict(document, UTAP::expression_t{}));
            }
        }
    }
    result["children"] = children;
    return result;
}

std::string frame_to_string(const UTAP::frame_t& frame)
{
    std::ostringstream oss;
    oss << frame;
    return oss.str();
}

py::list frame_symbols_to_list(const UTAP::Document& document, const UTAP::frame_t& frame)
{
    py::list result;
    for (const auto& symbol : frame) {
        result.append(symbol_to_dict(document, symbol));
    }
    return result;
}

py::list symbol_set_to_list(const UTAP::Document& document, const std::set<UTAP::symbol_t>& symbols)
{
    py::list result;
    for (const auto& symbol : symbols) {
        result.append(symbol_to_dict(document, symbol));
    }
    return result;
}

py::dict branchpoint_to_dict(const UTAP::Document& document, const UTAP::branchpoint_t& branchpoint)
{
    py::dict result;
    result["name"] = branchpoint.uid.get_name();
    result["index"] = branchpoint.bpNr;
    result["position"] = make_position_dict(document, branchpoint.uid.get_position());
    result["symbol"] = symbol_to_dict(document, branchpoint.uid);
    return result;
}

py::dict location_to_dict(const UTAP::Document& document, const UTAP::location_t& location)
{
    py::dict result;
    result["name"] = location.uid.get_name();
    result["index"] = location.nr;
    result["position"] = make_position_dict(document, location.uid.get_position());
    result["symbol"] = symbol_to_dict(document, location.uid);
    result["name_expression"] = expression_to_dict(document, location.name);
    result["invariant"] = expression_to_dict(document, location.invariant);
    result["exp_rate"] = expression_to_dict(document, location.exp_rate);
    result["cost_rate"] = expression_to_dict(document, location.cost_rate);
    result["is_urgent"] = location.uid.get_type().is(UTAP::Constants::URGENT);
    result["is_committed"] = location.uid.get_type().is(UTAP::Constants::COMMITTED);
    return result;
}

std::string edge_endpoint_name(const UTAP::edge_t& edge, bool source)
{
    const auto* location = source ? edge.src : edge.dst;
    const auto* branchpoint = source ? edge.srcb : edge.dstb;
    if (location != nullptr) {
        return location->uid.get_name();
    }
    if (branchpoint != nullptr) {
        return branchpoint->uid.get_name();
    }
    return {};
}

std::string edge_endpoint_kind(const UTAP::edge_t& edge, bool source)
{
    if ((source ? edge.src : edge.dst) != nullptr) {
        return "location";
    }
    if ((source ? edge.srcb : edge.dstb) != nullptr) {
        return "branchpoint";
    }
    return "unknown";
}

py::dict edge_to_dict(const UTAP::Document& document, const UTAP::edge_t& edge)
{
    py::dict result;
    result["index"] = edge.nr;
    result["control"] = edge.control;
    result["action_name"] = edge.actname;
    result["source_name"] = edge_endpoint_name(edge, true);
    result["source_kind"] = edge_endpoint_kind(edge, true);
    result["target_name"] = edge_endpoint_name(edge, false);
    result["target_kind"] = edge_endpoint_kind(edge, false);
    result["guard"] = expression_to_dict(document, edge.guard);
    result["assign"] = expression_to_dict(document, edge.assign);
    result["sync"] = expression_to_dict(document, edge.sync);
    result["prob"] = expression_to_dict(document, edge.prob);
    result["select_text"] = frame_to_string(edge.select);
    result["select_symbols"] = frame_symbols_to_list(document, edge.select);
    py::list select_values;
    for (const auto value : edge.selectValues) {
        select_values.append(value);
    }
    result["select_values"] = select_values;
    return result;
}

py::dict query_to_dict(const UTAP::query_t& query)
{
    py::dict result;
    result["formula"] = query.formula;
    result["comment"] = query.comment;
    result["options"] = options_to_list(query.options);
    result["expectation"] = expectation_to_dict(query.expectation);
    result["location"] = query.location;
    return result;
}

py::dict instance_to_dict(const UTAP::Document& document, const UTAP::instance_t& instance, std::size_t index)
{
    py::dict result;
    result["name"] = instance.uid.get_name();
    result["index"] = index;
    result["position"] = make_position_dict(document, instance.uid.get_position());
    result["template_name"] = instance.templ != nullptr ? instance.templ->uid.get_name() : std::string{};
    result["parameters"] = parameters_to_string(instance.parameters);
    result["arguments"] = arguments_to_string(instance);
    result["mapping"] = mapping_to_string(instance);
    result["argument_count"] = instance.arguments;
    result["unbound_count"] = instance.unbound;
    result["restricted_symbols"] = symbol_set_to_list(document, instance.restricted);
    return result;
}

py::dict template_to_dict(const UTAP::Document& document, const UTAP::template_t& templ, std::size_t index)
{
    py::dict result;
    result["name"] = templ.uid.get_name();
    result["index"] = index;
    result["position"] = make_position_dict(document, templ.uid.get_position());
    result["parameter"] = parameters_to_string(templ.parameters);
    result["declaration"] = std::string{};
    result["init_name"] = templ.init == UTAP::symbol_t{} ? std::string{} : templ.init.get_name();
    result["type"] = templ.type;
    result["mode"] = templ.mode;
    result["is_ta"] = templ.is_TA;
    result["is_instantiated"] = templ.is_instantiated;
    result["dynamic"] = templ.dynamic;
    result["is_defined"] = templ.is_defined;

    py::list locations;
    for (const auto& location : templ.locations) {
        locations.append(location_to_dict(document, location));
    }
    result["locations"] = locations;

    py::list branchpoints;
    for (const auto& branchpoint : templ.branchpoints) {
        branchpoints.append(branchpoint_to_dict(document, branchpoint));
    }
    result["branchpoints"] = branchpoints;

    py::list edges;
    for (const auto& edge : templ.edges) {
        edges.append(edge_to_dict(document, edge));
    }
    result["edges"] = edges;

    return result;
}

py::dict diagnostic_to_dict(const UTAP::error_t& diagnostic)
{
    py::dict result;
    const auto position = make_diagnostic_position_dict(diagnostic);
    result["message"] = diagnostic.msg;
    result["context"] = diagnostic.context;
    result["position"] = position;
    result["line"] = position["line"];
    result["column"] = position["column"];
    result["end_line"] = position["end_line"];
    result["end_column"] = position["end_column"];
    result["path"] = position["path"];
    return result;
}

py::list diagnostics_to_list(const std::vector<UTAP::error_t>& diagnostics)
{
    py::list result;
    for (const auto& diagnostic : diagnostics) {
        result.append(diagnostic_to_dict(diagnostic));
    }
    return result;
}

void restore_diagnostics(UTAP::Document& document, const std::vector<UTAP::error_t>& errors, const std::vector<UTAP::error_t>& warnings)
{
    document.clear_errors();
    document.clear_warnings();
    for (const auto& error : errors) {
        document.add_error(error.position, error.msg, error.context);
    }
    for (const auto& warning : warnings) {
        document.add_warning(warning.position, warning.msg, warning.context);
    }
}

py::dict features_to_dict(const UTAP::Document& document)
{
    py::dict result;
    const auto& supported = document.get_supported_methods();
    result["has_priority_declaration"] = document.has_priority_declaration();
    result["has_strict_invariants"] = document.has_strict_invariants();
    result["has_stop_watch"] = document.has_stop_watch();
    result["has_strict_lower_bound_on_controllable_edges"] =
        document.has_strict_lower_bound_on_controllable_edges();
    result["has_clock_guard_recv_broadcast"] = document.has_clock_guard_recv_broadcast();
    result["has_urgent_transition"] = document.has_urgent_transition();
    result["has_dynamic_templates"] = document.has_dynamic_templates();
    result["all_broadcast"] = document.all_broadcast();
    result["sync_used"] = document.get_sync_used();
    result["supports_symbolic"] = supported.symbolic;
    result["supports_stochastic"] = supported.stochastic;
    result["supports_concrete"] = supported.concrete;
    return result;
}

class NativeDocument
{
public:
    explicit NativeDocument(std::shared_ptr<UTAP::Document> document): document_(std::move(document)) {}

    bool has_errors() const { return document_->has_errors(); }
    bool has_warnings() const { return document_->has_warnings(); }
    std::size_t error_count() const { return document_->get_errors().size(); }
    std::size_t warning_count() const { return document_->get_warnings().size(); }
    bool modified() const { return document_->is_modified(); }

    py::dict snapshot() const
    {
        py::dict result;

        py::list templates;
        std::size_t template_index = 0;
        for (const auto& templ : document_->get_templates()) {
            templates.append(template_to_dict(*document_, templ, template_index));
            ++template_index;
        }
        result["templates"] = templates;

        py::list processes;
        std::size_t process_index = 0;
        for (const auto& process : document_->get_processes()) {
            processes.append(instance_to_dict(*document_, process, process_index));
            ++process_index;
        }
        result["processes"] = processes;

        py::list queries;
        for (const auto& query : document_->get_queries()) {
            queries.append(query_to_dict(query));
        }
        result["queries"] = queries;

        result["options"] = options_to_list(document_->get_options());
        result["features"] = features_to_dict(*document_);
        result["errors"] = diagnostics_to_list(document_->get_errors());
        result["warnings"] = diagnostics_to_list(document_->get_warnings());
        result["modified"] = document_->is_modified();
        return result;
    }

    void write_xml(const std::filesystem::path& path) const
    {
        const auto path_string = path.string();
        int32_t return_code = 0;
        try {
            py::gil_scoped_release release;
            return_code = write_XML_file(path_string.c_str(), document_.get());
        } catch (const std::exception& ex) {
            throw ParseError(std::string("XML write failed: ") + ex.what());
        }

        if (return_code != 0) {
            std::ostringstream oss;
            oss << "XML write failed with code " << return_code;
            throw ParseError(oss.str());
        }
    }

    std::string global_declarations() const { return user_declarations_text(document_->get_globals(), true); }

    std::string before_update_text() const { return expression_summary_or_empty(document_->get_before_update()); }

    std::string after_update_text() const { return expression_summary_or_empty(document_->get_after_update()); }

    py::list channel_priority_texts() const
    {
        py::list result;
        for (const auto& priority : document_->get_chan_priorities()) {
            result.append(chan_priority_text_or_empty(priority));
        }
        return result;
    }

    py::list global_clock_names() const { return string_vector_to_list(declarations_clock_names(document_->get_globals())); }

    py::dict template_clock_names() const
    {
        py::dict result;
        for (const auto& templ : document_->get_templates()) {
            std::vector<std::string> names = declarations_clock_names(templ);
            auto parameter_names = frame_clock_names(templ.parameters);
            std::set<std::string> seen(names.begin(), names.end());
            for (const auto& name : parameter_names) {
                append_clock_name_if_needed(names, seen, name);
            }
            result[py::str(templ.uid.get_name())] = string_vector_to_list(names);
        }
        return result;
    }

    std::string repr() const
    {
        std::ostringstream oss;
        oss << "<_utap._NativeDocument errors=" << error_count() << " warnings=" << warning_count() << ">";
        return oss.str();
    }

    UTAP::Document& document() const { return *document_; }

private:
    std::shared_ptr<UTAP::Document> document_;
};

std::shared_ptr<NativeDocument> wrap_document(std::shared_ptr<UTAP::Document> document)
{
    return std::make_shared<NativeDocument>(std::move(document));
}

std::shared_ptr<NativeDocument> parse_xml_file(
    const std::filesystem::path& path,
    bool newxta,
    bool strict,
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
        if (!strict && (document->has_errors() || document->has_warnings())) {
            return wrap_document(std::move(document));
        }
        throw ParseError(std::string("XML parse failed: ") + ex.what());
    }

    if (strict && (return_code != 0 || document->has_errors())) {
        raise_parse_error("XML", *document, return_code);
    }

    if (!strict) {
        return wrap_document(std::move(document));
    }

    if (return_code != 0) {
        raise_parse_error("XML", *document, return_code);
    }

    return wrap_document(std::move(document));
}

std::shared_ptr<NativeDocument> parse_xml_buffer(
    const std::string& buffer,
    bool newxta,
    bool strict,
    const std::vector<std::filesystem::path>& libpaths
)
{
    auto document = std::make_shared<UTAP::Document>();
    int32_t return_code = 0;
    try {
        py::gil_scoped_release release;
        return_code = parse_XML_buffer(buffer.c_str(), document.get(), newxta, libpaths);
    } catch (const std::exception& ex) {
        if (!strict && (document->has_errors() || document->has_warnings())) {
            return wrap_document(std::move(document));
        }
        throw ParseError(std::string("XML parse failed: ") + ex.what());
    }

    if (strict && (return_code != 0 || document->has_errors())) {
        raise_parse_error("XML", *document, return_code);
    }

    if (!strict) {
        return wrap_document(std::move(document));
    }

    if (return_code != 0) {
        raise_parse_error("XML", *document, return_code);
    }

    return wrap_document(std::move(document));
}

std::shared_ptr<NativeDocument> parse_xta_buffer(const std::string& buffer, bool newxta, bool strict)
{
    auto document = std::make_shared<UTAP::Document>();
    std::string normalized_buffer;
    const auto& parse_buffer = normalized_text_view(buffer, normalized_buffer);
    bool ok = false;
    try {
        py::gil_scoped_release release;
        ok = parse_XTA(parse_buffer.c_str(), document.get(), newxta);
    } catch (const std::exception& ex) {
        if (!strict && (document->has_errors() || document->has_warnings())) {
            return wrap_document(std::move(document));
        }
        throw ParseError(std::string("XTA parse failed: ") + ex.what());
    }

    if (strict && (!ok || document->has_errors())) {
        raise_parse_error("XTA", *document, 0);
    }

    if (!strict) {
        return wrap_document(std::move(document));
    }

    if (!ok) {
        raise_parse_error("XTA", *document, 0);
    }

    return wrap_document(std::move(document));
}

std::shared_ptr<NativeDocument> parse_xta_file(const std::filesystem::path& path, bool newxta, bool strict)
{
    return parse_xta_buffer(read_text_file(path), newxta, strict);
}

std::string xml_to_text(const std::string& buffer, bool newxta, bool include_builtin_preamble)
{
    std::ostringstream stream;
    UTAP::PrettyPrinter pretty_printer(stream);
    std::string normalized_buffer;
    const auto& parse_buffer = normalized_text_view(buffer, normalized_buffer);
    int32_t return_code = 0;
    try {
        py::gil_scoped_release release;
        return_code = parse_XML_buffer(parse_buffer.c_str(), &pretty_printer, newxta);
    } catch (const std::exception& ex) {
        throw ParseError(std::string(newxta ? "XTA" : "TA") + " pretty print failed: " + ex.what());
    }

    if (return_code < 0) {
        raise_text_render_error(newxta ? "XTA" : "TA", return_code);
    }

    const auto text = stream.str();
    if (include_builtin_preamble || !newxta) {
        return text;
    }
    return strip_exact_prefix(text, textual_builtin_preamble(true));
}

py::object property_expectation_to_object(const UTAP::expectation* expectation)
{
    if (expectation == nullptr) {
        return py::none();
    }

    py::dict result;
    if (std::holds_alternative<UTAP::status_t>(expectation->result)) {
        result["result_kind"] = "status";
        result["status"] = property_status_name(std::get<UTAP::status_t>(expectation->result));
        result["value"] = py::none();
    } else {
        result["result_kind"] = "numeric";
        result["status"] = py::none();
        result["value"] = std::get<double>(expectation->result);
    }
    result["time_ms"] = expectation->time_ms;
    result["mem_kib"] = expectation->mem_kib;
    return result;
}

py::dict prop_info_to_dict(
    const UTAP::Document& document,
    const UTAP::PropInfo& property,
    const std::string& builder_name
)
{
    py::dict result;
    auto expression_payload = expression_to_dict(document, property.intermediate);
    const auto fallback_text = expression_payload["text"].cast<std::string>().empty() ? quantifier_name(property.type) : "";
    result["line"] = property.line;
    result["no"] = property.no;
    result["builder"] = builder_name;
    result["text"] = fallback_text.empty() ? expression_payload["text"] : py::str(fallback_text);
    result["quantifier"] = quantifier_name(property.type);
    result["options"] = options_to_list(property.options);
    if (!fallback_text.empty()) {
        expression_payload["text"] = py::str(fallback_text);
    }
    result["expression"] = expression_payload;
    result["is_smc"] = quantifier_is_smc(property.type);
    result["declaration"] = property.declaration;
    result["result_type"] = strategy_type_name(property.result_type);
    result["expectation"] = property.expect ? property_expectation_to_object(property.expect.get()) : py::none();
    return result;
}

template <typename Builder>
struct QueryParseAttempt
{
    bool ok{false};
    py::list properties;
    std::string message;
};

template <typename Builder>
QueryParseAttempt<Builder> parse_query_with_builder(
    UTAP::Document& document,
    const std::string& buffer,
    const std::string& builder_name
)
{
    QueryParseAttempt<Builder> attempt;
    const auto original_errors = document.get_errors();
    const auto original_warnings = document.get_warnings();
    document.clear_errors();
    document.clear_warnings();

    try {
        Builder builder(document);
        std::unique_ptr<FILE, decltype(&std::fclose)> file(std::tmpfile(), &std::fclose);
        if (!file) {
            throw std::runtime_error("Unable to create temporary query file");
        }
        if (!buffer.empty()) {
            const auto written = std::fwrite(buffer.data(), 1, buffer.size(), file.get());
            if (written != buffer.size()) {
                throw std::runtime_error("Unable to write temporary query file");
            }
        }
        std::rewind(file.get());
        builder.parse(file.get());
        if (document.has_errors()) {
            attempt.message = first_error_message(document);
        } else {
            for (const auto& property : builder.getProperties()) {
                attempt.properties.append(prop_info_to_dict(document, property, builder_name));
            }
            attempt.ok = true;
        }
    } catch (const std::exception& ex) {
        attempt.message = ex.what();
    }

    if (attempt.message.empty() && !attempt.ok) {
        attempt.message = "query parse failed";
    }

    restore_diagnostics(document, original_errors, original_warnings);
    return attempt;
}

py::list parse_query_buffer(const std::shared_ptr<NativeDocument>& native_document, const std::string& buffer, const std::string& builder)
{
    auto& document = native_document->document();
    std::string normalized_buffer;
    const auto& parse_buffer = normalized_text_view(buffer, normalized_buffer);
    if (builder == "property") {
        const auto attempt = parse_query_with_builder<UTAP::PropertyBuilder>(document, parse_buffer, "property");
        if (!attempt.ok) {
            throw ParseError("query parse failed with property builder: " + attempt.message);
        }
        return attempt.properties;
    }
    if (builder == "tiga") {
        const auto attempt = parse_query_with_builder<UTAP::TigaPropertyBuilder>(document, parse_buffer, "tiga");
        if (!attempt.ok) {
            throw ParseError("query parse failed with tiga builder: " + attempt.message);
        }
        return attempt.properties;
    }
    if (builder != "auto") {
        throw py::value_error("Unknown query builder: " + builder);
    }

    const auto property_attempt = parse_query_with_builder<UTAP::PropertyBuilder>(document, parse_buffer, "property");
    if (property_attempt.ok) {
        return property_attempt.properties;
    }

    const auto tiga_attempt = parse_query_with_builder<UTAP::TigaPropertyBuilder>(document, parse_buffer, "tiga");
    if (tiga_attempt.ok) {
        return tiga_attempt.properties;
    }

    throw ParseError(
        "query parse failed with auto builder: property=" + property_attempt.message + "; tiga=" + tiga_attempt.message
    );
}

py::list parse_query_file(
    const std::shared_ptr<NativeDocument>& native_document,
    const std::filesystem::path& path,
    const std::string& builder
)
{
    return parse_query_buffer(native_document, read_text_file(path), builder);
}

}  // namespace

PYBIND11_MODULE(_utap, m)
{
    m.doc() = "Native UTAP binding surface.";

    py::register_exception<ParseError>(m, "ParseError", PyExc_RuntimeError);

    py::class_<NativeDocument, std::shared_ptr<NativeDocument>>(m, "_NativeDocument")
        .def_property_readonly("has_errors", &NativeDocument::has_errors)
        .def_property_readonly("has_warnings", &NativeDocument::has_warnings)
        .def_property_readonly("error_count", &NativeDocument::error_count)
        .def_property_readonly("warning_count", &NativeDocument::warning_count)
        .def_property_readonly("modified", &NativeDocument::modified)
        .def("snapshot", &NativeDocument::snapshot)
        .def("write_xml", [](const NativeDocument& document, const py::object& path) {
            document.write_xml(std::filesystem::path{py_fspath(path)});
        })
        .def("global_declarations", &NativeDocument::global_declarations)
        .def("before_update_text", &NativeDocument::before_update_text)
        .def("after_update_text", &NativeDocument::after_update_text)
        .def("channel_priority_texts", &NativeDocument::channel_priority_texts)
        .def("global_clock_names", &NativeDocument::global_clock_names)
        .def("template_clock_names", &NativeDocument::template_clock_names)
        .def("__repr__", &NativeDocument::repr);

    m.def(
        "load_xml",
        [](const py::object& path, bool newxta, bool strict, const py::iterable& libpaths) {
            return parse_xml_file(std::filesystem::path{py_fspath(path)}, newxta, strict, py_libpaths(libpaths));
        },
        py::arg("path"),
        py::arg("newxta") = true,
        py::arg("strict") = true,
        py::arg("libpaths") = py::tuple()
    );
    m.def(
        "loads_xml",
        [](const std::string& buffer, bool newxta, bool strict, const py::iterable& libpaths) {
            return parse_xml_buffer(buffer, newxta, strict, py_libpaths(libpaths));
        },
        py::arg("buffer"),
        py::arg("newxta") = true,
        py::arg("strict") = true,
        py::arg("libpaths") = py::tuple()
    );
    m.def(
        "_xml_to_text",
        &xml_to_text,
        py::arg("buffer"),
        py::arg("newxta") = true,
        py::arg("include_builtin_preamble") = false
    );
    m.def("textual_builtin_preamble", &textual_builtin_preamble, py::arg("newxta") = true);
    m.def(
        "load_xta",
        [](const py::object& path, bool newxta, bool strict) {
            return parse_xta_file(std::filesystem::path{py_fspath(path)}, newxta, strict);
        },
        py::arg("path"),
        py::arg("newxta") = true,
        py::arg("strict") = true
    );
    m.def("loads_xta", &parse_xta_buffer, py::arg("buffer"), py::arg("newxta") = true, py::arg("strict") = true);
    m.def(
        "load_query",
        [](const py::object& path, const std::shared_ptr<NativeDocument>& document, const std::string& builder) {
            return parse_query_file(document, std::filesystem::path{py_fspath(path)}, builder);
        },
        py::arg("path"),
        py::arg("document"),
        py::arg("builder") = "auto"
    );
    m.def(
        "loads_query",
        [](const std::string& buffer, const std::shared_ptr<NativeDocument>& document, const std::string& builder) {
            return parse_query_buffer(document, buffer, builder);
        },
        py::arg("buffer"),
        py::arg("document"),
        py::arg("builder") = "auto"
    );
    m.def(
        "parse_query",
        [](const std::string& buffer, const std::shared_ptr<NativeDocument>& document, const std::string& builder) {
            return parse_query_buffer(document, buffer, builder);
        },
        py::arg("buffer"),
        py::arg("document"),
        py::arg("builder") = "auto"
    );
    m.def("builtin_declarations", []() { return std::string(utap_builtin_declarations()); });
}
