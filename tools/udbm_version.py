"""
Synchronize UDBM metadata into :mod:`pyudbm.config.meta`.

The tool reads the declared UDBM version from the vendored ``UDBM``
submodule's ``CMakeLists.txt`` file and the current submodule commit from
Git, then updates only ``__UDBM_VERSION__`` and ``__UDBM_COMMIT__`` in the
target metadata module.

Example::

    python -m tools.udbm_version -i UDBM -o pyudbm/config/meta.py
    python tools/udbm_version.py -i UDBM -o pyudbm/config/meta.py
"""

import argparse
import os
import re
import subprocess
import tempfile
from typing import Match, Optional, Pattern, Sequence


_PROJECT_VERSION_PATTERN = re.compile(
    r"project\s*\(\s*UDBM\s+VERSION\s+(?P<version>[^\s\)]+)",
    re.IGNORECASE,
)
_UDBM_VERSION_FIELD_PATTERN = re.compile(
    r"^(?P<prefix>__UDBM_VERSION__(?:\s*:\s*str)?\s*=\s*)(?P<quote>['\"])(?P<value>.*?)(?P=quote)(?P<suffix>\s*)$",
    re.MULTILINE,
)
_UDBM_COMMIT_FIELD_PATTERN = re.compile(
    r"^(?P<prefix>__UDBM_COMMIT__(?:\s*:\s*str)?\s*=\s*)(?P<quote>['\"])(?P<value>.*?)(?P=quote)(?P<suffix>\s*)$",
    re.MULTILINE,
)


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", newline="") as file:
        return file.read()


def _write_text(path: str, content: str) -> None:
    directory = os.path.dirname(path) or "."
    file_descriptor, temporary_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="") as file:
            file.write(content)
        os.replace(temporary_path, path)
    except Exception:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)
        raise


def resolve_udbm_version(udbm_dir: str) -> str:
    """
    Resolve the declared UDBM version from the vendored source tree.

    :param udbm_dir: Path to the local UDBM submodule checkout.
    :type udbm_dir: str
    :return: The version declared in ``UDBM/CMakeLists.txt``.
    :rtype: str
    :raises FileNotFoundError: If ``CMakeLists.txt`` cannot be found.
    :raises ValueError: If the version cannot be parsed from ``CMakeLists.txt``.
    """

    cmake_path = os.path.join(udbm_dir, "CMakeLists.txt")
    content = _read_text(cmake_path)
    match = _PROJECT_VERSION_PATTERN.search(content)
    if match is None:
        raise ValueError(
            "Unable to find the UDBM project version declaration in {!r}.".format(cmake_path)
        )
    return match.group("version")


def resolve_udbm_commit(udbm_dir: str) -> str:
    """
    Resolve the current UDBM submodule commit hash.

    :param udbm_dir: Path to the local UDBM submodule checkout.
    :type udbm_dir: str
    :return: The full Git commit hash for the submodule HEAD.
    :rtype: str
    :raises RuntimeError: If Git cannot resolve the commit hash.
    """

    try:
        completed = subprocess.run(
            ["git", "-C", udbm_dir, "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        message = getattr(error, "stderr", None)
        detail = message.strip() if message else str(error)
        raise RuntimeError(
            "Unable to determine the UDBM commit from {!r}: {}".format(udbm_dir, detail)
        )
    return completed.stdout.strip()


def _replace_field(
    pattern: Pattern[str], field_name: str, content: str, value: str
) -> str:
    def _replacement(match: Match[str]) -> str:
        return "{prefix}{quote}{value}{quote}{suffix}".format(
            prefix=match.group("prefix"),
            quote=match.group("quote"),
            value=value,
            suffix=match.group("suffix"),
        )

    updated_content, count = pattern.subn(_replacement, content, count=1)
    if count != 1:
        raise ValueError(
            "Field {!r} was not found exactly once in the target metadata file.".format(
                field_name
            )
        )
    return updated_content


def update_meta_file(meta_path: str, udbm_version: str, udbm_commit: str) -> bool:
    """
    Update the UDBM metadata fields in ``meta.py``.

    Only ``__UDBM_VERSION__`` and ``__UDBM_COMMIT__`` are modified. All other
    content is preserved byte-for-byte except for the replaced literal values.

    :param meta_path: Path to the metadata module to update.
    :type meta_path: str
    :param udbm_version: The UDBM version string to write.
    :type udbm_version: str
    :param udbm_commit: The UDBM commit hash to write.
    :type udbm_commit: str
    :return: ``True`` if the file changed, otherwise ``False``.
    :rtype: bool
    :raises ValueError: If either target field cannot be located.
    """

    original_content = _read_text(meta_path)
    updated_content = _replace_field(
        _UDBM_VERSION_FIELD_PATTERN, "__UDBM_VERSION__", original_content, udbm_version
    )
    updated_content = _replace_field(
        _UDBM_COMMIT_FIELD_PATTERN, "__UDBM_COMMIT__", updated_content, udbm_commit
    )

    if updated_content == original_content:
        return False

    _write_text(meta_path, updated_content)
    return True


def build_argument_parser() -> argparse.ArgumentParser:
    """
    Build the command line parser for this tool.

    :return: A configured argument parser.
    :rtype: argparse.ArgumentParser
    """

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(
        description="Update pyudbm/config/meta.py with version metadata from the vendored UDBM submodule."
    )
    parser.add_argument(
        "-i",
        "--input",
        default=os.path.join(repo_root, "UDBM"),
        help="Path to the UDBM submodule checkout. Defaults to the repository's UDBM directory.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=os.path.join(repo_root, "pyudbm", "config", "meta.py"),
        help="Path to the target meta.py file. Defaults to pyudbm/config/meta.py in this repository.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Run the command line entrypoint.

    :param argv: Optional command line arguments without the executable name.
    :type argv: Sequence[str] or None
    :return: Process exit code.
    :rtype: int
    """

    parser = build_argument_parser()
    args = parser.parse_args(argv)

    udbm_version = resolve_udbm_version(args.input)
    udbm_commit = resolve_udbm_commit(args.input)
    changed = update_meta_file(args.output, udbm_version, udbm_commit)

    status = "updated" if changed else "already up to date"
    print(
        "{output}: {status} (UDBM {version}, commit {commit})".format(
            output=args.output,
            status=status,
            version=udbm_version,
            commit=udbm_commit,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
