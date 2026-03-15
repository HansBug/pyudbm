cmake_minimum_required(VERSION 3.15)
project(pyudbm LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(DEFINED ENV{LINETRACE} AND NOT "$ENV{LINETRACE}" STREQUAL "")
    message(STATUS "Coverage analysis enabled via LINETRACE")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fprofile-arcs -ftest-coverage")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fprofile-arcs -ftest-coverage")
endif()

if(DEFINED ENV{BINSTALL_DIR} AND NOT "$ENV{BINSTALL_DIR}" STREQUAL "")
    set(PYUDBM_INSTALL_PREFIX "$ENV{BINSTALL_DIR}")
else()
    set(PYUDBM_INSTALL_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/bin_install")
endif()
get_filename_component(PYUDBM_INSTALL_PREFIX "${PYUDBM_INSTALL_PREFIX}" ABSOLUTE)
message(STATUS "Using dependency prefix: ${PYUDBM_INSTALL_PREFIX}")

list(PREPEND CMAKE_PREFIX_PATH "${PYUDBM_INSTALL_PREFIX}")

find_package(pybind11 REQUIRED)
find_package(UUtils CONFIG REQUIRED)
find_package(UDBM CONFIG REQUIRED)

pybind11_add_module(_binding pyudbm/_binding.cpp)
target_link_libraries(_binding PRIVATE UDBM)
target_include_directories(_binding PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
