.PHONY: help info build clean clean_x package zip test unittest \
	uutils_build uutils_test uutils_install uutils_clean uutils uutils_notest \
	udbm_build udbm_test udbm_install udbm_clean udbm udbm_notest \
	ucdd_build ucdd_test ucdd_install ucdd_clean ucdd ucdd_notest \
	bin_clean bin bin_notest docs docs_en docs_zh pdocs rst_auto sync_versions uversion

PYTHON := $(shell which python)
UNAME_S := $(shell uname -s 2>/dev/null || echo unknown)

GNU_GCC_CANDIDATES := gcc-9 gcc-10 gcc-11 gcc-12 gcc-13 gcc-14 gcc
GNU_GXX_CANDIDATES := g++-9 g++-10 g++-11 g++-12 g++-13 g++-14 g++
DETECTED_GCC       := $(shell bash -lc 'for cmd in $(GNU_GCC_CANDIDATES); do if command -v $$cmd >/dev/null 2>&1 && $$cmd -v 2>&1 | grep -qi "gcc version"; then echo $$cmd; exit 0; fi; done')
DETECTED_GXX       := $(shell bash -lc 'for cmd in $(GNU_GXX_CANDIDATES); do if command -v $$cmd >/dev/null 2>&1 && $$cmd -v 2>&1 | grep -qi "gcc version"; then echo $$cmd; exit 0; fi; done')
DETECTED_CLANG     := $(shell bash -lc 'if command -v xcrun >/dev/null 2>&1; then xcrun --find clang 2>/dev/null && exit 0; fi; command -v clang 2>/dev/null')
DETECTED_CLANGXX   := $(shell bash -lc 'if command -v xcrun >/dev/null 2>&1; then xcrun --find clang++ 2>/dev/null && exit 0; fi; command -v clang++ 2>/dev/null')

ifeq ($(UNAME_S),Darwin)
DEFAULT_CC := $(if $(DETECTED_CLANG),$(DETECTED_CLANG),clang)
DEFAULT_CXX := $(if $(DETECTED_CLANGXX),$(DETECTED_CLANGXX),clang++)
else
DEFAULT_CC := $(if $(DETECTED_GCC),$(DETECTED_GCC),gcc)
DEFAULT_CXX := $(if $(DETECTED_GXX),$(DETECTED_GXX),g++)
endif

ifeq ($(origin CC), default)
CC := $(DEFAULT_CC)
else ifeq ($(origin CC), undefined)
CC := $(DEFAULT_CC)
endif

ifeq ($(origin CXX), default)
CXX := $(DEFAULT_CXX)
else ifeq ($(origin CXX), undefined)
CXX := $(DEFAULT_CXX)
endif

ifeq ($(OS),Windows_NT)
IS_WINDOWS := 1
else ifneq ($(filter MINGW% MSYS% CYGWIN%,$(UNAME_S)),)
IS_WINDOWS := 1
else
IS_WINDOWS := 0
endif

PS     ?= $(shell ${PYTHON} -c "import os; print(os.pathsep)")
CC_BINDIR := $(shell bash -lc 'p=$$(command -v "$(CC)" 2>/dev/null); if [ -n "$$p" ]; then dirname "$$p"; fi')

PROJ_DIR       := .
DOC_DIR        := ${PROJ_DIR}/docs
DIST_DIR       := ${PROJ_DIR}/dist
WHEELHOUSE_DIR := ${PROJ_DIR}/wheelhouse
TEST_DIR       := ${PROJ_DIR}/test
BENCHMARK_DIR  := ${PROJ_DIR}/benchmark
SRC_DIR        := ${PROJ_DIR}/pyudbm
RUNS_DIR       := ${PROJ_DIR}/runs
BUILD_DIR      := ${PROJ_DIR}/build
BINSTALL_DIR   := ${PROJ_DIR}/bin_install

UUTILS_DIR       := ${PROJ_DIR}/UUtils
UUTILS_BUILD_DIR := ${PROJ_DIR}/UUtils_build
UDBM_DIR         := ${PROJ_DIR}/UDBM
UDBM_BUILD_DIR   := ${PROJ_DIR}/UDBM_build
UCDD_DIR         := ${PROJ_DIR}/UCDD
UCDD_BUILD_DIR   := ${PROJ_DIR}/UCDD_build

RANGE_DIR       ?= .
RANGE_TEST_DIR  := ${TEST_DIR}/${RANGE_DIR}
RANGE_BENCH_DIR := ${BENCHMARK_DIR}/${RANGE_DIR}
RANGE_SRC_DIR   := ${SRC_DIR}/${RANGE_DIR}

PYTHON_CODE_DIR   := ${SRC_DIR}
RST_DOC_DIR       := ${DOC_DIR}/source/api_doc
PYTHON_CODE_FILES := $(shell find ${PYTHON_CODE_DIR} -name "*.py" ! -path "*/__pycache__/*" ! -name "__*.py" 2>/dev/null)
RST_DOC_FILES     := $(patsubst ${PYTHON_CODE_DIR}/%.py,${RST_DOC_DIR}/%.rst,${PYTHON_CODE_FILES})
PYTHON_NONM_FILES := $(shell find ${PYTHON_CODE_DIR} -name "__init__.py" ! -path "*/__pycache__/*" 2>/dev/null)
RST_NONM_FILES    := $(foreach file,${PYTHON_NONM_FILES},$(patsubst %/__init__.py,%/index.rst,$(patsubst ${PYTHON_CODE_DIR}/%,${RST_DOC_DIR}/%,$(patsubst ${PYTHON_CODE_DIR}/__init__.py,${RST_DOC_DIR}/index.rst,${file}))))

BINSTALL_LIB_DIR     ?= $(shell readlink -f ${BINSTALL_DIR}/lib*)
BINSTALL_INCLUDE_DIR ?= $(shell readlink -f ${BINSTALL_DIR}/include*)

CMAKE_EP ?= -DCMAKE_PREFIX_PATH="$(shell readlink -f ${BINSTALL_DIR})${PS}${CMAKE_PREFIX_PATH}"
CMAKE_EL ?= -DCMAKE_LIBRARY_PATH="${BINSTALL_LIB_DIR}${PS}${CMAKE_LIBRARY_PATH}"
CMAKE_EI ?= -DCMAKE_INCLUDE_PATH="${BINSTALL_INCLUDE_DIR}${PS}${CMAKE_INCLUDE_PATH}"
CMAKE_E  ?= ${CMAKE_EP} ${CMAKE_EL} ${CMAKE_EI}

CTEST_CFG ?= Release
CMAKE_GENERATOR ?= Ninja
CMAKE_GNU_RUNTIME_ARGS :=
ifeq ($(IS_WINDOWS),1)
CMAKE_GNU_RUNTIME_ARGS += -DCMAKE_C_FLAGS="-static-libgcc"
CMAKE_GNU_RUNTIME_ARGS += -DCMAKE_CXX_FLAGS="-static-libgcc -static-libstdc++"
CMAKE_GNU_RUNTIME_ARGS += -DCMAKE_EXE_LINKER_FLAGS="-static-libgcc -static-libstdc++"
CMAKE_GNU_RUNTIME_ARGS += -DCMAKE_SHARED_LINKER_FLAGS="-static-libgcc -static-libstdc++"
endif
CMAKE_TOOLCHAIN_ARGS := -G "${CMAKE_GENERATOR}" -DCMAKE_C_COMPILER="${CC}" -DCMAKE_CXX_COMPILER="${CXX}" ${CMAKE_GNU_RUNTIME_ARGS}
CTEST_ENV := $(if $(CC_BINDIR),PATH="$(CC_BINDIR)${PS}$$PATH",)

COV_TYPES ?= xml term-missing

.DEFAULT_GOAL := help

help:
	@echo "pyudbm Build System"
	@echo "==================="
	@echo ""
	@echo "Python Package:"
	@echo "  make build        - Build Python extension modules in place"
	@echo "  make package      - Build Python source and wheel packages"
	@echo "  make zip          - Build Python source package only"
	@echo "  make sync_versions - Sync UUtils/UDBM/UCDD version, commit, and commit time metadata into pyudbm/config/meta.py"
	@echo "  make clean        - Remove Python extension and package artifacts"
	@echo "  make clean_x      - Remove all local build outputs, including local prefix"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run tests (alias for unittest)"
	@echo "  make unittest     - Run pytest unit tests"
	@echo "                      Options: RANGE_DIR=<dir> COV_TYPES='xml term-missing'"
	@echo "                               MIN_COVERAGE=<percent> WORKERS=<n>"
	@echo ""
	@echo "Upstream Dependencies:"
	@echo "  make uutils_build   - Configure and build UUtils"
	@echo "  make uutils_test    - Run UUtils tests"
	@echo "  make uutils_install - Install UUtils into the local prefix"
	@echo "  make uutils_clean   - Remove the UUtils build directory"
	@echo "  make uutils         - Build, test, and install UUtils"
	@echo "  make uutils_notest  - Build and install UUtils without running tests"
	@echo ""
	@echo "  make udbm_build     - Configure and build UDBM"
	@echo "  make udbm_test      - Run UDBM tests"
	@echo "  make udbm_install   - Install UDBM into the local prefix"
	@echo "  make udbm_clean     - Remove the UDBM build directory"
	@echo "  make udbm           - Build, test, and install UDBM"
	@echo "  make udbm_notest    - Build and install UDBM without running tests"
	@echo ""
	@echo "  make ucdd_build     - Configure and build UCDD"
	@echo "  make ucdd_test      - Run UCDD tests"
	@echo "  make ucdd_install   - Install UCDD into the local prefix"
	@echo "  make ucdd_clean     - Remove the UCDD build directory"
	@echo "  make ucdd           - Build, test, and install UCDD"
	@echo "  make ucdd_notest    - Build and install UCDD without running tests"
	@echo ""
	@echo "Combined Dependency Pipeline:"
	@echo "  make bin          - Build, test, and install UUtils, UDBM, and UCDD"
	@echo "  make bin_notest   - Build and install UUtils, UDBM, and UCDD without tests"
	@echo "  make bin_clean    - Remove UUtils, UDBM, UCDD, and local prefix build outputs"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs         - Build documentation (auto-detects language)"
	@echo "  make docs_en      - Build English documentation"
	@echo "  make docs_zh      - Build Chinese documentation"
	@echo "  make pdocs        - Build production documentation"
	@echo "  make rst_auto     - Generate RST documentation from Python source"
	@echo ""
	@echo "Diagnostics:"
	@echo "  make info         - Print current path and CMake environment values"
	@echo ""
	@echo "Common Variables:"
	@echo "  BINSTALL_DIR=<dir> - Local install prefix for UUtils/UDBM/UCDD"
	@echo "  CMAKE_GENERATOR    - CMake generator (default: Ninja)"
	@echo "  CTEST_CFG=<cfg>    - CMake/CTest build configuration (default: Release)"
	@echo "  RANGE_DIR=<dir>    - Limit pytest coverage and test scope (default: .)"
	@echo "  COV_TYPES=<types>  - Coverage report types (default: xml term-missing)"
	@echo "  MIN_COVERAGE=<n>   - Minimum required coverage percentage"
	@echo "  WORKERS=<n>        - Number of parallel pytest workers"
	@echo ""

build:
	$(if $(CC_BINDIR),PATH="${CC_BINDIR}${PS}$$PATH",) CC="${CC}" CXX="${CXX}" CMAKE_GENERATOR="${CMAKE_GENERATOR}" BINSTALL_DIR="${BINSTALL_DIR}" $(PYTHON) setup.py build_ext --inplace
sync_versions:
	$(PYTHON) -m tools.upstream_versions --uutils-input "${UUTILS_DIR}" --udbm-input "${UDBM_DIR}" --ucdd-input "${UCDD_DIR}" -o "${SRC_DIR}/config/meta.py"
uversion: sync_versions
clean:
	rm -rf $(shell find ${SRC_DIR} \( -name '*.so' -o -name '*.pyd' -o -name '*.dll' -o -name '*.dylib' \))
	rm -rf ${DIST_DIR} ${WHEELHOUSE_DIR}
	rm -rf ${BUILD_DIR}/temp.*
clean_x:
	rm -rf ${DIST_DIR} ${WHEELHOUSE_DIR} ${BUILD_DIR} ${BINSTALL_DIR}

package:
	BINSTALL_DIR="${BINSTALL_DIR}" $(PYTHON) -m build --sdist --wheel --outdir ${DIST_DIR}
zip:
	BINSTALL_DIR="${BINSTALL_DIR}" $(PYTHON) -m build --sdist --outdir ${DIST_DIR}

test: unittest

unittest:
	$(PYTHON) -m pytest "${RANGE_TEST_DIR}" \
		-sv -m unittest \
		$(shell for type in ${COV_TYPES}; do echo "--cov-report=$$type"; done) \
		--cov="${RANGE_SRC_DIR}" \
		$(if ${MIN_COVERAGE},--cov-fail-under=${MIN_COVERAGE},) \
		$(if ${WORKERS},-n ${WORKERS},)

uutils_build:
	cmake -S ${UUTILS_DIR} -B "${UUTILS_BUILD_DIR}" ${CMAKE_TOOLCHAIN_ARGS} $(if ${CTEST_CFG},-DCMAKE_BUILD_TYPE=${CTEST_CFG},)
	cmake --build "${UUTILS_BUILD_DIR}" $(if ${CTEST_CFG},--config ${CTEST_CFG},)
uutils_test:
	${CTEST_ENV} ctest --test-dir "${UUTILS_BUILD_DIR}" --output-on-failure $(if ${CTEST_CFG},-C ${CTEST_CFG},)
uutils_install:
	cmake --install "${UUTILS_BUILD_DIR}" --prefix "${BINSTALL_DIR}" $(if ${CTEST_CFG},--config ${CTEST_CFG},)
uutils_clean:
	rm -rf "${UUTILS_BUILD_DIR}"
uutils: uutils_build uutils_test uutils_install
uutils_notest: uutils_build uutils_install

udbm_build:
	cmake -S ${UDBM_DIR} -B "${UDBM_BUILD_DIR}" ${CMAKE_TOOLCHAIN_ARGS} $(if ${CTEST_CFG},-DCMAKE_BUILD_TYPE=${CTEST_CFG},) \
		-DUUtils_DIR="$(shell readlink -f ${BINSTALL_DIR}/lib*/cmake/UUtils)"
	cmake --build "${UDBM_BUILD_DIR}" $(if ${CTEST_CFG},--config ${CTEST_CFG},)
udbm_test:
	${CTEST_ENV} ctest --test-dir "${UDBM_BUILD_DIR}" --output-on-failure $(if ${CTEST_CFG},-C ${CTEST_CFG},)
udbm_install:
	cmake --install "${UDBM_BUILD_DIR}" --prefix "${BINSTALL_DIR}" $(if ${CTEST_CFG},--config ${CTEST_CFG},)
udbm_clean:
	rm -rf "${UDBM_BUILD_DIR}"
udbm: udbm_build udbm_test udbm_install
udbm_notest: udbm_build udbm_install

ucdd_build:
	cmake -S ${UCDD_DIR} -B "${UCDD_BUILD_DIR}" ${CMAKE_TOOLCHAIN_ARGS} $(if ${CTEST_CFG},-DCMAKE_BUILD_TYPE=${CTEST_CFG},) \
		-DCMAKE_PREFIX_PATH="$(shell readlink -f ${BINSTALL_DIR})" \
		-DUUtils_DIR="$(shell readlink -f ${BINSTALL_DIR}/lib*/cmake/UUtils)" \
		-DUDBM_DIR="$(shell readlink -f ${BINSTALL_DIR}/lib*/cmake/UDBM)" \
		-DFIND_FATAL=OFF
	cmake --build "${UCDD_BUILD_DIR}" $(if ${CTEST_CFG},--config ${CTEST_CFG},)
ucdd_test:
	${CTEST_ENV} ctest --test-dir "${UCDD_BUILD_DIR}" --output-on-failure $(if ${CTEST_CFG},-C ${CTEST_CFG},)
ucdd_install:
	cmake --install "${UCDD_BUILD_DIR}" --prefix "${BINSTALL_DIR}" $(if ${CTEST_CFG},--config ${CTEST_CFG},)
ucdd_clean:
	rm -rf "${UCDD_BUILD_DIR}"
ucdd: udbm ucdd_build ucdd_test ucdd_install
ucdd_notest: udbm_notest ucdd_build ucdd_install

bin_clean: uutils_clean udbm_clean ucdd_clean
	rm -rf "${BINSTALL_DIR}"
bin: uutils udbm ucdd
bin_notest: uutils_notest udbm_notest ucdd_notest

docs: bin_notest build
	$(MAKE) -C "${DOC_DIR}" build
docs_en: bin_notest build
	READTHEDOCS_LANGUAGE=en $(MAKE) -C "${DOC_DIR}" build
docs_zh: bin_notest build
	READTHEDOCS_LANGUAGE=zh-cn $(MAKE) -C "${DOC_DIR}" build
pdocs: bin_notest build
	$(MAKE) -C "${DOC_DIR}" prod

rst_auto: ${RST_DOC_FILES} ${RST_NONM_FILES} auto_rst_top_index.py
	$(PYTHON) auto_rst_top_index.py -i "${PYTHON_CODE_DIR}" -o "${DOC_DIR}/source"

${RST_DOC_DIR}/%.rst: ${PYTHON_CODE_DIR}/%.py auto_rst.py Makefile
	@mkdir -p "$(dir $@)"
	$(PYTHON) auto_rst.py -i "$<" -o "$@"

${RST_DOC_DIR}/%/index.rst: ${PYTHON_CODE_DIR}/%/__init__.py auto_rst.py Makefile
	@mkdir -p "$(dir $@)"
	$(PYTHON) auto_rst.py -i "$<" -o "$@"

${RST_DOC_DIR}/index.rst: ${PYTHON_CODE_DIR}/__init__.py auto_rst.py Makefile
	@mkdir -p "$(dir $@)"
	$(PYTHON) auto_rst.py -i "$<" -o "$@"

info:
	echo "PS: ${PS}"
	echo "CC: ${CC}"
	echo "CXX: ${CXX}"
	echo "CC_BINDIR: ${CC_BINDIR}"
	echo "IS_WINDOWS: ${IS_WINDOWS}"
	echo "CMAKE_GENERATOR: ${CMAKE_GENERATOR}"
	echo "CMAKE_E: ${CMAKE_E}"
