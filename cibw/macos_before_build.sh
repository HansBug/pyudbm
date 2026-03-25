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

select_clang() {
    local tool="$1"
    local resolved

    if command -v xcrun >/dev/null 2>&1; then
        resolved="$(xcrun --find "$tool" 2>/dev/null || true)"
        if [[ -n "$resolved" && -x "$resolved" ]]; then
            printf '%s\n' "$resolved"
            return 0
        fi
    fi

    if command -v "$tool" >/dev/null 2>&1; then
        command -v "$tool"
        return 0
    fi

    return 1
}

PROJECT_ROOT="${1:-$PWD}"
PROJECT_ROOT="$(resolve_path "$PROJECT_ROOT")"

cd "$PROJECT_ROOT"

export CC="$(select_clang clang)"
export CXX="$(select_clang clang++)"
export CMAKE_GENERATOR=Ninja

"$PROJECT_ROOT/macos_kill_cmake.sh"

brew install flex bison doctest
export PATH="$(brew --prefix flex)/bin:$(brew --prefix bison)/bin:$PATH"
export FLEX_EXECUTABLE="$(brew --prefix flex)/bin/flex"
export BISON_EXECUTABLE="$(brew --prefix bison)/bin/bison"
DOCTEST_PREFIX="$(brew --prefix doctest)"
git config --global --add url."https://github.com/".insteadOf git@github.com:
git config --global --add url."https://github.com/".insteadOf ssh://git@github.com/

python -m pip install -U ninja
python -m pip install pybind11[global]
python -m pip install -U "cmake<4"

uname -m
echo "$CIBW_ARCHS"
if [[ "$CIBW_ARCHS" = "arm64" ]]; then
    echo "detected arm64"
    MACOS_ARCH=arm64
    MACOS_DEPLOYMENT=11.0
else
    echo "detected x86_64"
    MACOS_ARCH=x86_64
    MACOS_DEPLOYMENT=11.0
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

cmake -G "$CMAKE_GENERATOR" -S UTAP -B UTAP_build \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DCMAKE_PREFIX_PATH="$BIN_INSTALL;$DOCTEST_PREFIX" \
    -DCMAKE_OSX_ARCHITECTURES="$MACOS_ARCH" \
    -DCMAKE_SYSTEM_PROCESSOR="$MACOS_ARCH" \
    -DCMAKE_OSX_DEPLOYMENT_TARGET="$MACOS_DEPLOYMENT" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TRY_COMPILE_OSX_ARCHITECTURES="$MACOS_ARCH" \
    -DFLEX_EXECUTABLE="$FLEX_EXECUTABLE" \
    -DBISON_EXECUTABLE="$BISON_EXECUTABLE"
cmake --build UTAP_build --config Release
ctest --test-dir UTAP_build --output-on-failure -C Release
cmake --install UTAP_build --prefix bin_install --config Release
