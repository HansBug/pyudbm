#!/usr/bin/env bash

set -euo pipefail

resolve_path() {
    python - "$1" <<'PY'
import sys
from pathlib import Path

print(Path(sys.argv[1]).resolve())
PY
}

resolve_glob() {
    python - "$1" <<'PY'
import glob
import sys
from pathlib import Path

matches = sorted(glob.glob(sys.argv[1]))
if not matches:
    raise SystemExit(f'No path matched: {sys.argv[1]}')
print(Path(matches[0]).resolve())
PY
}

PROJECT_ROOT="${1:-$PWD}"
PROJECT_ROOT="$(resolve_path "$PROJECT_ROOT")"

cd "$PROJECT_ROOT"

export CC=gcc
export CXX=g++
export CMAKE_GENERATOR=Ninja

echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "CC=$CC CXX=$CXX"
python -m pip install -U ninja
python -m pip install pybind11[global]
python -m pip install -U "cmake<4"

BIN_INSTALL="$(resolve_path bin_install)"

cmake -G "$CMAKE_GENERATOR" -S UUtils -B UUtils_build \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DCMAKE_BUILD_TYPE=Release
cmake --build UUtils_build --config Release
ctest --test-dir UUtils_build --output-on-failure -C Release
cmake --install UUtils_build --prefix bin_install --config Release

UUTILS_DIR="$(resolve_glob 'bin_install/lib*/cmake/UUtils')"
cmake -G "$CMAKE_GENERATOR" -S UDBM -B UDBM_build \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DCMAKE_BUILD_TYPE=Release \
    -DUUtils_DIR="$UUTILS_DIR"
cmake --build UDBM_build --config Release
ctest --test-dir UDBM_build --output-on-failure -C Release
cmake --install UDBM_build --prefix bin_install --config Release

UDBM_DIR="$(resolve_glob 'bin_install/lib*/cmake/UDBM')"
cmake -G "$CMAKE_GENERATOR" -S UCDD -B UCDD_build \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH="$BIN_INSTALL" \
    -DUUtils_DIR="$UUTILS_DIR" \
    -DUDBM_DIR="$UDBM_DIR" \
    -DFIND_FATAL=OFF
cmake --build UCDD_build --config Release
ctest --test-dir UCDD_build --output-on-failure -C Release
cmake --install UCDD_build --prefix bin_install --config Release
