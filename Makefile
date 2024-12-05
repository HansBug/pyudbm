.PHONY: docs test unittest build clean benchmark zip bin_test bin_build bin_clean bin bin_install

PYTHON := $(shell which python)
CC     ?= $(shell which gcc)
CXX    ?= $(shell which g++)

PS     ?= $(shell ${PYTHON} -c "import os; print(os.pathsep)")

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

RANGE_DIR       ?= .
RANGE_TEST_DIR  := ${TEST_DIR}/${RANGE_DIR}
RANGE_BENCH_DIR := ${BENCHMARK_DIR}/${RANGE_DIR}
RANGE_SRC_DIR   := ${SRC_DIR}/${RANGE_DIR}

BINSTALL_LIB_DIR     ?= $(shell readlink -f ${BINSTALL_DIR}/lib*)
BINSTALL_INCLUDE_DIR ?= $(shell readlink -f ${BINSTALL_DIR}/include*)

CMAKE_EP ?= -DCMAKE_PREFIX_PATH="$(shell readlink -f ${BINSTALL_DIR})${PS}${CMAKE_PREFIX_PATH}"
CMAKE_EL ?= -DCMAKE_LIBRARY_PATH="${BINSTALL_LIB_DIR}${PS}${CMAKE_LIBRARY_PATH}"
CMAKE_EI ?= -DCMAKE_INCLUDE_PATH="${BINSTALL_INCLUDE_DIR}${PS}${CMAKE_INCLUDE_PATH}"
CMAKE_E  ?= ${CMAKE_EP} ${CMAKE_EL} ${CMAKE_EI}

CTEST_CFG ?= Release

COV_TYPES ?= xml term-missing

build:
	BINSTALL_DIR="${BINSTALL_DIR}" $(PYTHON) setup.py build_ext --inplace
clean:
	rm -rf $(shell find ${SRC_DIR} -name '*.so')
	rm -rf ${DIST_DIR} ${WHEELHOUSE_DIR}
	rm -rf ${BUILD_DIR}/temp.*
clean_x:
	rm -rf ${DIST_DIR} ${WHEELHOUSE_DIR} ${BUILD_DIR} ${BINSTALL_DIR}

package:
	BINSTALL_DIR="${BINSTALL_DIR}" $(PYTHON) -m build --sdist --wheel --outdir ${DIST_DIR}
zip:
	BINSTALL_DIR="${BINSTALL_DIR}" $(PYTHON) -m build --sdist --outdir ${DIST_DIR}

unittest:
	$(PYTHON) -m pytest "${RANGE_TEST_DIR}" \
		-sv -m unittest \
		$(shell for type in ${COV_TYPES}; do echo "--cov-report=$$type"; done) \
		--cov="${RANGE_SRC_DIR}" \
		$(if ${MIN_COVERAGE},--cov-fail-under=${MIN_COVERAGE},) \
		$(if ${WORKERS},-n ${WORKERS},)

uutils_build:
	cmake -S ${UUTILS_DIR} -B "${UUTILS_BUILD_DIR}" $(if ${CTEST_CFG},-DCMAKE_BUILD_TYPE=${CTEST_CFG},)
	cmake --build "${UUTILS_BUILD_DIR}" $(if ${CTEST_CFG},--config ${CTEST_CFG},)
uutils_test:
	ctest --test-dir "${UUTILS_BUILD_DIR}" --output-on-failure $(if ${CTEST_CFG},-C ${CTEST_CFG},)
uutils_install:
	cmake --install "${UUTILS_BUILD_DIR}" --prefix "${BINSTALL_DIR}" $(if ${CTEST_CFG},--config ${CTEST_CFG},)
uutils_clean:
	rm -rf "${UUTILS_BUILD_DIR}"
uutils: uutils_build uutils_test uutils_install
uutils_notest: uutils_build uutils_install

udbm_build:
	cmake -S ${UDBM_DIR} -B "${UDBM_BUILD_DIR}" $(if ${CTEST_CFG},-DCMAKE_BUILD_TYPE=${CTEST_CFG},) \
		-DUUtils_DIR="$(shell readlink -f ${BINSTALL_DIR}/lib*/cmake/UUtils)"
	cmake --build "${UDBM_BUILD_DIR}" $(if ${CTEST_CFG},--config ${CTEST_CFG},)
udbm_test:
	ctest --test-dir "${UDBM_BUILD_DIR}" --output-on-failure $(if ${CTEST_CFG},-C ${CTEST_CFG},)
udbm_install:
	cmake --install "${UDBM_BUILD_DIR}" --prefix "${BINSTALL_DIR}" $(if ${CTEST_CFG},--config ${CTEST_CFG},)
udbm_clean:
	rm -rf "${UDBM_BUILD_DIR}"
udbm: udbm_build udbm_test udbm_install
udbm_notest: udbm_build udbm_install

bin_clean: uutils_clean udbm_clean
	rm -rf "${BINSTALL_DIR}"
bin: uutils udbm
bin_notest: uutils_notest udbm_notest

docs:
	$(MAKE) -C "${DOC_DIR}" build
pdocs:
	$(MAKE) -C "${DOC_DIR}" prod

info:
	echo "PS: ${PS}"
	echo "CMAKE_E: ${CMAKE_E}"