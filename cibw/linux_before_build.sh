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

install_packages() {
    if command -v dnf >/dev/null 2>&1; then
        dnf install -y "$@"
    elif command -v yum >/dev/null 2>&1; then
        yum install -y "$@"
    elif command -v microdnf >/dev/null 2>&1; then
        microdnf install -y "$@"
    elif command -v apt-get >/dev/null 2>&1; then
        apt-get update
        apt-get install -y "$@"
    elif command -v apk >/dev/null 2>&1; then
        apk add --no-cache "$@"
    else
        printf 'No supported package manager found to install: %s\n' "$*" >&2
        return 1
    fi
}

download_file() {
    local url="$1"
    local output="$2"

    python - "$url" "$output" <<'PY'
import sys
import urllib.request
from pathlib import Path

url, output = sys.argv[1], Path(sys.argv[2])
output.parent.mkdir(parents=True, exist_ok=True)

with urllib.request.urlopen(url) as resp, output.open('wb') as f:
    while True:
        chunk = resp.read(1024 * 1024)
        if not chunk:
            break
        f.write(chunk)
PY
}

build_autotools_tool() {
    local name="$1"
    local version="$2"
    local url="$3"
    local source_dir="$TOOLS_SRC_DIR/${name}-${version}"
    local archive="$TOOLS_SRC_DIR/${name}-${version}.tar.gz"
    shift 3

    if [[ -x "$TOOLS_PREFIX/bin/$name" ]]; then
        return 0
    fi

    download_file "$url" "$archive"
    rm -rf "$source_dir"
    mkdir -p "$TOOLS_SRC_DIR"
    tar -xzf "$archive" -C "$TOOLS_SRC_DIR"

    (
        cd "$source_dir"
        ./configure --prefix="$TOOLS_PREFIX" "$@"
        make -j"$BUILD_JOBS"
        make install
    )
}

PROJECT_ROOT="${1:-$PWD}"
PROJECT_ROOT="$(resolve_path "$PROJECT_ROOT")"

cd "$PROJECT_ROOT"

export CC=gcc
export CXX=g++
export CMAKE_GENERATOR=Ninja

echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "CC=$CC CXX=$CXX"
BUILD_JOBS="$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)"
TOOLS_SRC_DIR="$(resolve_path .cibw-native-src)"
TOOLS_PREFIX="$(resolve_path .cibw-native-tools)"

if ! command -v m4 >/dev/null 2>&1; then
    install_packages m4
fi

build_autotools_tool \
    flex \
    2.6.4 \
    https://github.com/westes/flex/releases/download/v2.6.4/flex-2.6.4.tar.gz \
    --disable-dependency-tracking

build_autotools_tool \
    bison \
    3.8.2 \
    https://ftp.gnu.org/gnu/bison/bison-3.8.2.tar.gz \
    --disable-dependency-tracking \
    --disable-nls

export PATH="$TOOLS_PREFIX/bin:$PATH"
git config --global --add url."https://github.com/".insteadOf git@github.com:
git config --global --add url."https://github.com/".insteadOf ssh://git@github.com/
python -m pip install -U ninja
python -m pip install pybind11[global]
python -m pip install -U "cmake<4"

BIN_INSTALL="$(resolve_path bin_install)"
FLEX_EXECUTABLE="$(command -v flex)"
BISON_EXECUTABLE="$(command -v bison)"
COMMON_FLAGS=(
    -G "$CMAKE_GENERATOR"
    -DCMAKE_C_COMPILER="$CC"
    -DCMAKE_CXX_COMPILER="$CXX"
    -DCMAKE_BUILD_TYPE=Release
)

cmake -S UUtils -B UUtils_build "${COMMON_FLAGS[@]}"
cmake --build UUtils_build --config Release
ctest --test-dir UUtils_build --output-on-failure -C Release
cmake --install UUtils_build --prefix bin_install --config Release

UUTILS_DIR="$(resolve_glob 'bin_install/lib*/cmake/UUtils')"
cmake -S UDBM -B UDBM_build "${COMMON_FLAGS[@]}" \
    -DUUtils_DIR="$UUTILS_DIR"
cmake --build UDBM_build --config Release
ctest --test-dir UDBM_build --output-on-failure -C Release
cmake --install UDBM_build --prefix bin_install --config Release

UDBM_DIR="$(resolve_glob 'bin_install/lib*/cmake/UDBM')"
cmake -S UCDD -B UCDD_build "${COMMON_FLAGS[@]}" \
    -DCMAKE_PREFIX_PATH="$BIN_INSTALL" \
    -DUUtils_DIR="$UUTILS_DIR" \
    -DUDBM_DIR="$UDBM_DIR" \
    -DFIND_FATAL=OFF
cmake --build UCDD_build --config Release
ctest --test-dir UCDD_build --output-on-failure -C Release
cmake --install UCDD_build --prefix bin_install --config Release

cmake -S UTAP -B UTAP_build "${COMMON_FLAGS[@]}" \
    -DCMAKE_PREFIX_PATH="$BIN_INSTALL" \
    -DFLEX_EXECUTABLE="$FLEX_EXECUTABLE" \
    -DBISON_EXECUTABLE="$BISON_EXECUTABLE"
cmake --build UTAP_build --config Release
ctest --test-dir UTAP_build --output-on-failure -C Release
cmake --install UTAP_build --prefix bin_install --config Release
