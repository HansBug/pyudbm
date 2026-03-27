#pragma once

#include <pybind11/pybind11.h>

#include <utap/document.h>

#include <memory>
#include <stdexcept>
#include <string>

namespace pyudbm { namespace binding { namespace utap_native {

class ParseError : public std::runtime_error
{
public:
    explicit ParseError(const std::string& message): std::runtime_error(message) {}
};

pybind11::object wrap_document_object(std::shared_ptr<UTAP::Document> document);

void bind_utap_builder(pybind11::module& m);

}}}  // namespace pyudbm::binding::utap_native
