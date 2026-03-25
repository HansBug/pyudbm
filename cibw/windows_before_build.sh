#!/usr/bin/env bash

set -euo pipefail

to_posix_path() {
    local path="$1"
    if command -v cygpath >/dev/null 2>&1 && [[ "$path" =~ ^[A-Za-z]:\\ ]]; then
        cygpath -u "$path"
    else
        printf '%s\n' "$path"
    fi
}

to_mixed_path() {
    local path="$1"
    if command -v cygpath >/dev/null 2>&1 && [[ "$path" =~ ^[A-Za-z]:\\ ]]; then
        cygpath -m "$path"
    else
        printf '%s\n' "$path"
    fi
}

PROJECT_ROOT_INPUT="${1:-$PWD}"
PROJECT_ROOT="$(to_posix_path "$PROJECT_ROOT_INPUT")"
PROJECT_ROOT_MIXED="$(to_mixed_path "$PROJECT_ROOT_INPUT")"

cd "$PROJECT_ROOT"

choco install mingw winflexbison3 -y

MINGW_BIN_WIN="$(python -m tools.windows_mingw --bin-dir)"
MINGW_BIN="$(to_posix_path "$MINGW_BIN_WIN")"
WIN_FLEX_WIN="$(where.exe win_flex | head -n1 | tr -d '\r')"
WIN_BISON_WIN="$(where.exe win_bison | head -n1 | tr -d '\r')"
FLEX_EXECUTABLE="$(to_posix_path "$WIN_FLEX_WIN")"
BISON_EXECUTABLE="$(to_posix_path "$WIN_BISON_WIN")"

export MINGW_BIN
export PATH="$MINGW_BIN:$PATH"
export CC="$MINGW_BIN/gcc.exe"
export CXX="$MINGW_BIN/g++.exe"
export CMAKE_GENERATOR=Ninja
git config --global --add url."https://github.com/".insteadOf git@github.com:
git config --global --add url."https://github.com/".insteadOf ssh://git@github.com/

echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "MINGW_BIN=$MINGW_BIN"
"$CC" --version
"$CXX" --version
python -m pip install -U ninja
python -m pip install pybind11[global]
python -m pip install -U "cmake<4"
ls -al
whoami
pwd
bash --version

COMMON_FLAGS=(
    -G "$CMAKE_GENERATOR"
    -DCMAKE_C_COMPILER="$CC"
    -DCMAKE_CXX_COMPILER="$CXX"
    -DCMAKE_C_FLAGS="-static-libgcc"
    -DCMAKE_CXX_FLAGS="-static-libgcc -static-libstdc++"
    -DCMAKE_EXE_LINKER_FLAGS="-static-libgcc -static-libstdc++"
    -DCMAKE_SHARED_LINKER_FLAGS="-static-libgcc -static-libstdc++"
    -DCMAKE_BUILD_TYPE=Release
)

cmake -S UUtils -B UUtils_build "${COMMON_FLAGS[@]}"
cmake --build UUtils_build --config Release
ctest --test-dir UUtils_build --output-on-failure -C Release
cmake --install UUtils_build --prefix bin_install --config Release

cmake -S UDBM -B UDBM_build "${COMMON_FLAGS[@]}" \
    -DUUtils_DIR="$PROJECT_ROOT_MIXED/bin_install/lib/cmake/UUtils"
cmake --build UDBM_build --config Release
ctest --test-dir UDBM_build --output-on-failure -C Release
cmake --install UDBM_build --prefix bin_install --config Release

cmake -S UCDD -B UCDD_build "${COMMON_FLAGS[@]}" \
    -DCMAKE_PREFIX_PATH="$PROJECT_ROOT_MIXED/bin_install" \
    -DUUtils_DIR="$PROJECT_ROOT_MIXED/bin_install/lib/cmake/UUtils" \
    -DUDBM_DIR="$PROJECT_ROOT_MIXED/bin_install/lib/cmake/UDBM" \
    -DFIND_FATAL=OFF
cmake --build UCDD_build --config Release
ctest --test-dir UCDD_build --output-on-failure -C Release
cmake --install UCDD_build --prefix bin_install --config Release

cmake -S UTAP -B UTAP_build "${COMMON_FLAGS[@]}" \
    -DCMAKE_PREFIX_PATH="$PROJECT_ROOT_MIXED/bin_install" \
    -DFLEX_EXECUTABLE="$FLEX_EXECUTABLE" \
    -DBISON_EXECUTABLE="$BISON_EXECUTABLE"
cmake --build UTAP_build --config Release
ctest --test-dir UTAP_build --output-on-failure -C Release
cmake --install UTAP_build --prefix bin_install --config Release
