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
find_package(UCDD CONFIG REQUIRED)
find_package(UTAP CONFIG REQUIRED)

function(pyudbm_enable_origin_rpath target_name)
    if(APPLE)
        set_target_properties(${target_name} PROPERTIES
            BUILD_RPATH "@loader_path;${PYUDBM_INSTALL_PREFIX}/lib"
            INSTALL_RPATH "@loader_path"
        )
    elseif(UNIX)
        set_target_properties(${target_name} PROPERTIES
            BUILD_RPATH "\$ORIGIN;${PYUDBM_INSTALL_PREFIX}/lib"
            INSTALL_RPATH "\$ORIGIN"
        )
    endif()
endfunction()

pybind11_add_module(_udbm pyudbm/binding/_udbm.cpp)
target_link_libraries(_udbm PRIVATE UDBM)
target_include_directories(_udbm PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

pybind11_add_module(_ucdd pyudbm/binding/_ucdd.cpp)
target_link_libraries(_ucdd PRIVATE UCDD)
target_include_directories(_ucdd PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

pybind11_add_module(_utap pyudbm/binding/_utap.cpp)
target_link_libraries(_utap PRIVATE UTAP)
target_include_directories(_utap PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
pyudbm_enable_origin_rpath(_utap)
