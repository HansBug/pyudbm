cmake_minimum_required(VERSION 3.15)
project(uutils_hash)

set(CMAKE_CXX_STANDARD 17)
include(FetchContent)

execute_process(
    COMMAND pwd
    OUTPUT_VARIABLE CURRENT_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Current working directory: ${CURRENT_DIR}")

# Check if LINETRACE environment variable is set
if(DEFINED ENV{LINETRACE})
    # Add coverage flags only when LINETRACE is not empty
    if(NOT "$ENV{LINETRACE}" STREQUAL "")
        message(STATUS "Coverage analysis enabled via LINETRACE")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fprofile-arcs -ftest-coverage")
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fprofile-arcs -ftest-coverage")
    endif()
endif()

# read from env BINSTALL_DIR, otherwise use bin_install
if(DEFINED ENV{BINSTALL_DIR})
    set(CUSTOM_INSTALL_PREFIX $ENV{BINSTALL_DIR} CACHE PATH "Custom installation prefix")
    message(STATUS "BINSTALL_DIR: ${CUSTOM_INSTALL_PREFIX}")
else()
    set(CUSTOM_INSTALL_PREFIX "./bin_install" CACHE PATH "Custom installation prefix")
    message(WARNING "Environment variable BINSTALL_DIR not set, using default path: ${CUSTOM_INSTALL_PREFIX}")
endif()

list(APPEND CMAKE_PREFIX_PATH "${CUSTOM_INSTALL_PREFIX}")
list(APPEND CMAKE_LIBRARY_PATH "${CUSTOM_INSTALL_PREFIX}/lib")
list(APPEND CMAKE_INCLUDE_PATH "${CUSTOM_INSTALL_PREFIX}/include")

find_package(pybind11 REQUIRED)

# find all libraries from uutils library
file(GLOB STATIC_LIBS "${CUSTOM_INSTALL_PREFIX}/lib*/*.a" "${CUSTOM_INSTALL_PREFIX}/lib*/*.lib")
if(NOT STATIC_LIBS)
    message(FATAL_ERROR "No static libraries (*.a or *.lib) found in ${CUSTOM_INSTALL_PREFIX}/lib* directories")
endif()
message(STATUS "STATIC_LIBS: ${STATIC_LIBS}")

include(UDBM/cmake/xxhash.cmake)
include(UDBM/cmake/sanitizer.cmake)
include(UDBM/cmake/UUtils.cmake)

list(APPEND PYBIND_MODULES
    "_c_udbm_constraints|pyudbm/core/constraints.cpp"
    "_c_udbm_dbm|pyudbm/core/dbm.cpp"
)

foreach(MODULE_PAIR IN LISTS PYBIND_MODULES)
    message(STATUS "Current Pair: ${MODULE_PAIR}")
    string(FIND "${MODULE_PAIR}" "|" SEMICOLON_POS)
    if(SEMICOLON_POS GREATER -1)
        string(SUBSTRING "${MODULE_PAIR}" 0 ${SEMICOLON_POS} MODULE_NAME)
        math(EXPR SOURCE_START "${SEMICOLON_POS} + 1")
        string(SUBSTRING "${MODULE_PAIR}" ${SOURCE_START} -1 SOURCE_FILE)
        message(STATUS "Module: ${MODULE_NAME}, Source file: ${SOURCE_FILE}")

        pybind11_add_module(${MODULE_NAME} ${SOURCE_FILE})
        target_link_libraries(${MODULE_NAME} PRIVATE xxHash ${STATIC_LIBS})
        target_include_directories(${MODULE_NAME} PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}
            ${CUSTOM_INSTALL_PREFIX}/include
        )

        get_filename_component(INSTALL_DIR "${SOURCE_FILE}" PATH)
        install(TARGETS ${MODULE_NAME} DESTINATION ${INSTALL_DIR})
    else()
        message(FATAL_ERROR "Invalid module pair format: ${MODULE_PAIR}")
    endif()
endforeach()
