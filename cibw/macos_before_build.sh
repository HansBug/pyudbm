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

select_gcc() {
    local kind="$1"
    local cmd
    for cmd in "${kind}-9" "${kind}-10" "${kind}-11" "${kind}-12" "${kind}-13" "${kind}-14" "$kind"; do
        if command -v "$cmd" >/dev/null 2>&1 && "$cmd" -v 2>&1 | grep -qi "gcc version"; then
            printf '%s\n' "$cmd"
            return 0
        fi
    done
    return 1
}

PROJECT_ROOT="${1:-$PWD}"
PROJECT_ROOT="$(resolve_path "$PROJECT_ROOT")"

cd "$PROJECT_ROOT"

brew list gcc@11 >/dev/null 2>&1 || brew install gcc@11 || brew install gcc@12 || brew install gcc

export CC="$(select_gcc gcc)"
export CXX="$(select_gcc g++)"
export CMAKE_GENERATOR=Ninja

"$PROJECT_ROOT/macos_kill_cmake.sh"

pip install -U ninja
pip install pybind11[global]
pip install -U "cmake<4"

uname -m
echo "$CIBW_ARCHS"
if [[ "$CIBW_ARCHS" = "arm64" ]]; then
    echo "detected arm64"
    MACOS_ARCH=arm64
    MACOS_DEPLOYMENT=11.0
else
    echo "detected x86_64"
    MACOS_ARCH=x86_64
    MACOS_DEPLOYMENT=10.9
fi

echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "CC=$CC CXX=$CXX"

BIN_INSTALL="$(resolve_path bin_install)"

cmake -G "$CMAKE_GENERATOR" -S UUtils -B UUtils_build \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DCMAKE_OSX_ARCHITECTURES="$MACOS_ARCH" \
    -DCMAKE_SYSTEM_PROCESSOR="$MACOS_ARCH" \
    -DCMAKE_OSX_DEPLOYMENT_TARGET="$MACOS_DEPLOYMENT" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TRY_COMPILE_OSX_ARCHITECTURES="$MACOS_ARCH"
cmake --build UUtils_build --config Release
ctest --test-dir UUtils_build --output-on-failure -C Release
cmake --install UUtils_build --prefix bin_install --config Release

UUTILS_DIR="$(resolve_glob 'bin_install/lib*/cmake/UUtils')"
cmake -G "$CMAKE_GENERATOR" -S UDBM -B UDBM_build \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DUUtils_DIR="$UUTILS_DIR" \
    -DCMAKE_OSX_ARCHITECTURES="$MACOS_ARCH" \
    -DCMAKE_SYSTEM_PROCESSOR="$MACOS_ARCH" \
    -DCMAKE_OSX_DEPLOYMENT_TARGET="$MACOS_DEPLOYMENT" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TRY_COMPILE_OSX_ARCHITECTURES="$MACOS_ARCH"
cmake --build UDBM_build --config Release
ctest --test-dir UDBM_build --output-on-failure -C Release
cmake --install UDBM_build --prefix bin_install --config Release

UDBM_DIR="$(resolve_glob 'bin_install/lib*/cmake/UDBM')"
cmake -G "$CMAKE_GENERATOR" -S UCDD -B UCDD_build \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DCMAKE_PREFIX_PATH="$BIN_INSTALL" \
    -DUUtils_DIR="$UUTILS_DIR" \
    -DUDBM_DIR="$UDBM_DIR" \
    -DCMAKE_OSX_ARCHITECTURES="$MACOS_ARCH" \
    -DCMAKE_SYSTEM_PROCESSOR="$MACOS_ARCH" \
    -DCMAKE_OSX_DEPLOYMENT_TARGET="$MACOS_DEPLOYMENT" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TRY_COMPILE_OSX_ARCHITECTURES="$MACOS_ARCH" \
    -DFIND_FATAL=OFF
cmake --build UCDD_build --config Release
ctest --test-dir UCDD_build --output-on-failure -C Release
cmake --install UCDD_build --prefix bin_install --config Release
