"""
Windows MinGW discovery helpers.

This module centralizes how the repository locates the GNU toolchain on
Windows so workflow glue, packaging, and local scripts do not each hardcode
their own install paths.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _is_gnu_compiler(path: Path) -> bool:
    try:
        output = subprocess.check_output(
            [str(path), "-v"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return "gcc version" in output.lower()


def _iter_where_paths(name: str):
    where_exe = shutil.which("where.exe")
    if not where_exe:
        return

    try:
        output = subprocess.check_output(
            [where_exe, name],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return

    for line in output.splitlines():
        candidate = line.strip()
        if candidate:
            yield Path(candidate)


def _candidate_bin_dirs():
    seen = set()

    def _yield(directory: Path):
        directory = directory.resolve()
        key = os.path.normcase(str(directory))
        if key in seen:
            return
        seen.add(key)
        yield directory

    mingw_bin = os.environ.get("MINGW_BIN")
    if mingw_bin:
        yield from _yield(Path(mingw_bin))

    for executable in ("gcc.exe", "g++.exe", "gcc", "g++"):
        resolved = shutil.which(executable)
        if resolved:
            yield from _yield(Path(resolved).parent)

    for executable in ("gcc.exe", "g++.exe"):
        for resolved in _iter_where_paths(executable) or ():
            yield from _yield(resolved.parent)

    choco_root = os.environ.get("ChocolateyInstall")
    if choco_root:
        lib_root = Path(choco_root) / "lib"
        if lib_root.is_dir():
            for resolved in sorted(lib_root.glob("**/bin/gcc.exe")):
                yield from _yield(resolved.parent)


def find_mingw_bin() -> str:
    if platform.system() != "Windows":
        raise RuntimeError("MinGW discovery is only supported on Windows")

    for directory in _candidate_bin_dirs():
        gcc = directory / "gcc.exe"
        gxx = directory / "g++.exe"
        if gcc.is_file() and gxx.is_file() and _is_gnu_compiler(gcc):
            return str(directory)

    raise RuntimeError("Unable to locate a usable MinGW bin directory")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bin-dir",
        action="store_true",
        help="Print the discovered MinGW bin directory.",
    )
    args = parser.parse_args(argv)

    if args.bin_dir:
        print(find_mingw_bin())
        return 0

    parser.error("No action requested")
    return 2


if __name__ == "__main__":
    sys.exit(main())
