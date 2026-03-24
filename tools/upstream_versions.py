"""
Synchronize vendored upstream metadata into :mod:`pyudbm.config.meta`.

The tool reads the declared versions from the vendored ``UUtils``, ``UDBM``,
and ``UCDD`` submodules' ``CMakeLists.txt`` files, resolves their current
submodule commits from Git, and updates the corresponding metadata fields in
``pyudbm/config/meta.py``.

Example::

    python -m tools.upstream_versions --uutils-input UUtils --udbm-input UDBM --ucdd-input UCDD -o pyudbm/config/meta.py
    python tools/upstream_versions.py --uutils-input UUtils --udbm-input UDBM --ucdd-input UCDD -o pyudbm/config/meta.py
"""

import argparse
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Match, Optional, Pattern, Sequence


@dataclass(frozen=True)
class UpstreamComponent:
    project_name: str
    default_dirname: str
    version_field: str
    commit_field: str
    commit_time_field: str


_COMPONENTS = (
    UpstreamComponent(
        project_name="UUtils",
        default_dirname="UUtils",
        version_field="__UUTILS_VERSION__",
        commit_field="__UUTILS_COMMIT__",
        commit_time_field="__UUTILS_COMMIT_TIME__",
    ),
    UpstreamComponent(
        project_name="UDBM",
        default_dirname="UDBM",
        version_field="__UDBM_VERSION__",
        commit_field="__UDBM_COMMIT__",
        commit_time_field="__UDBM_COMMIT_TIME__",
    ),
    UpstreamComponent(
        project_name="UCDD",
        default_dirname="UCDD",
        version_field="__UCDD_VERSION__",
        commit_field="__UCDD_COMMIT__",
        commit_time_field="__UCDD_COMMIT_TIME__",
    ),
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


def _build_project_version_pattern(project_name: str) -> Pattern[str]:
    return re.compile(
        r"project\s*\(\s*{name}\s+VERSION\s+(?P<version>[^\s\)]+)".format(
            name=re.escape(project_name)
        ),
        re.IGNORECASE,
    )


def _build_field_pattern(field_name: str) -> Pattern[str]:
    return re.compile(
        r"^(?P<prefix>{field}(?:\s*:\s*str)?\s*=\s*)(?P<quote>['\"])(?P<value>.*?)(?P=quote)(?P<suffix>\s*)$".format(
            field=re.escape(field_name)
        ),
        re.MULTILINE,
    )


def resolve_project_version(component: UpstreamComponent, source_dir: str) -> str:
    """
    Resolve the declared upstream version from the vendored source tree.

    :param component: Description of the upstream component to inspect.
    :type component: UpstreamComponent
    :param source_dir: Path to the local submodule checkout.
    :type source_dir: str
    :return: The version declared in ``CMakeLists.txt``.
    :rtype: str
    :raises FileNotFoundError: If ``CMakeLists.txt`` cannot be found.
    :raises ValueError: If the version cannot be parsed from ``CMakeLists.txt``.
    """

    cmake_path = os.path.join(source_dir, "CMakeLists.txt")
    content = _read_text(cmake_path)
    match = _build_project_version_pattern(component.project_name).search(content)
    if match is None:
        raise ValueError(
            "Unable to find the {name} project version declaration in {path!r}.".format(
                name=component.project_name,
                path=cmake_path,
            )
        )
    return match.group("version")


def resolve_project_commit(component: UpstreamComponent, source_dir: str) -> str:
    """
    Resolve the current upstream submodule commit hash.

    :param component: Description of the upstream component to inspect.
    :type component: UpstreamComponent
    :param source_dir: Path to the local submodule checkout.
    :type source_dir: str
    :return: The full Git commit hash for the submodule HEAD.
    :rtype: str
    :raises RuntimeError: If Git cannot resolve the commit hash.
    """

    try:
        completed = subprocess.run(
            ["git", "-C", source_dir, "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        message = getattr(error, "stderr", None)
        detail = message.strip() if message else str(error)
        raise RuntimeError(
            "Unable to determine the {name} commit from {path!r}: {detail}".format(
                name=component.project_name,
                path=source_dir,
                detail=detail,
            )
        )
    return completed.stdout.strip()


def resolve_project_commit_time(component: UpstreamComponent, source_dir: str) -> str:
    """
    Resolve the current upstream submodule commit time.

    The returned timestamp keeps the commit's own timezone offset and uses the
    ``YYYY-mm-dd HH:MM:SS +ZZZZ`` format.

    :param component: Description of the upstream component to inspect.
    :type component: UpstreamComponent
    :param source_dir: Path to the local submodule checkout.
    :type source_dir: str
    :return: The formatted commit timestamp for the submodule HEAD.
    :rtype: str
    :raises RuntimeError: If Git cannot resolve the commit timestamp.
    """

    try:
        completed = subprocess.run(
            [
                "git",
                "-C",
                source_dir,
                "log",
                "-1",
                "--date=format:%Y-%m-%d %H:%M:%S %z",
                "--format=%cd",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        message = getattr(error, "stderr", None)
        detail = message.strip() if message else str(error)
        raise RuntimeError(
            "Unable to determine the {name} commit time from {path!r}: {detail}".format(
                name=component.project_name,
                path=source_dir,
                detail=detail,
            )
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


def update_meta_file(
    meta_path: str,
    uutils_version: str,
    uutils_commit: str,
    uutils_commit_time: str,
    udbm_version: str,
    udbm_commit: str,
    udbm_commit_time: str,
    ucdd_version: str,
    ucdd_commit: str,
    ucdd_commit_time: str,
) -> bool:
    """
    Update the vendored upstream metadata fields in ``meta.py``.

    Only the upstream version and commit fields are modified. All other
    content is preserved byte-for-byte except for the replaced literal values.

    :param meta_path: Path to the metadata module to update.
    :type meta_path: str
    :param uutils_version: The UUtils version string to write.
    :type uutils_version: str
    :param uutils_commit: The UUtils commit hash to write.
    :type uutils_commit: str
    :param uutils_commit_time: The UUtils commit time string to write.
    :type uutils_commit_time: str
    :param udbm_version: The UDBM version string to write.
    :type udbm_version: str
    :param udbm_commit: The UDBM commit hash to write.
    :type udbm_commit: str
    :param udbm_commit_time: The UDBM commit time string to write.
    :type udbm_commit_time: str
    :param ucdd_version: The UCDD version string to write.
    :type ucdd_version: str
    :param ucdd_commit: The UCDD commit hash to write.
    :type ucdd_commit: str
    :param ucdd_commit_time: The UCDD commit time string to write.
    :type ucdd_commit_time: str
    :return: ``True`` if the file changed, otherwise ``False``.
    :rtype: bool
    :raises ValueError: If either target field cannot be located.
    """

    original_content = _read_text(meta_path)
    component_values = (
        (_COMPONENTS[0].version_field, uutils_version),
        (_COMPONENTS[0].commit_field, uutils_commit),
        (_COMPONENTS[0].commit_time_field, uutils_commit_time),
        (_COMPONENTS[1].version_field, udbm_version),
        (_COMPONENTS[1].commit_field, udbm_commit),
        (_COMPONENTS[1].commit_time_field, udbm_commit_time),
        (_COMPONENTS[2].version_field, ucdd_version),
        (_COMPONENTS[2].commit_field, ucdd_commit),
        (_COMPONENTS[2].commit_time_field, ucdd_commit_time),
    )
    updated_content = original_content
    for field_name, field_value in component_values:
        updated_content = _replace_field(
            _build_field_pattern(field_name),
            field_name,
            updated_content,
            field_value,
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
        description="Update pyudbm/config/meta.py with version metadata from the vendored UUtils, UDBM, and UCDD submodules."
    )
    parser.add_argument(
        "--uutils-input",
        default=os.path.join(repo_root, _COMPONENTS[0].default_dirname),
        help="Path to the UUtils submodule checkout. Defaults to the repository's UUtils directory.",
    )
    parser.add_argument(
        "--udbm-input",
        default=os.path.join(repo_root, _COMPONENTS[1].default_dirname),
        help="Path to the UDBM submodule checkout. Defaults to the repository's UDBM directory.",
    )
    parser.add_argument(
        "--ucdd-input",
        default=os.path.join(repo_root, _COMPONENTS[2].default_dirname),
        help="Path to the UCDD submodule checkout. Defaults to the repository's UCDD directory.",
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

    uutils_component, udbm_component, ucdd_component = _COMPONENTS
    uutils_version = resolve_project_version(uutils_component, args.uutils_input)
    uutils_commit = resolve_project_commit(uutils_component, args.uutils_input)
    uutils_commit_time = resolve_project_commit_time(uutils_component, args.uutils_input)
    udbm_version = resolve_project_version(udbm_component, args.udbm_input)
    udbm_commit = resolve_project_commit(udbm_component, args.udbm_input)
    udbm_commit_time = resolve_project_commit_time(udbm_component, args.udbm_input)
    ucdd_version = resolve_project_version(ucdd_component, args.ucdd_input)
    ucdd_commit = resolve_project_commit(ucdd_component, args.ucdd_input)
    ucdd_commit_time = resolve_project_commit_time(ucdd_component, args.ucdd_input)
    changed = update_meta_file(
        args.output,
        uutils_version,
        uutils_commit,
        uutils_commit_time,
        udbm_version,
        udbm_commit,
        udbm_commit_time,
        ucdd_version,
        ucdd_commit,
        ucdd_commit_time,
    )

    status = "updated" if changed else "already up to date"
    print(
        (
            "{output}: {status}\n"
            "UUtils {uutils_version}, commit {uutils_commit}, time {uutils_commit_time}\n"
            "UDBM {udbm_version}, commit {udbm_commit}, time {udbm_commit_time}\n"
            "UCDD {ucdd_version}, commit {ucdd_commit}, time {ucdd_commit_time}"
        ).format(
            output=args.output,
            status=status,
            uutils_version=uutils_version,
            uutils_commit=uutils_commit,
            uutils_commit_time=uutils_commit_time,
            udbm_version=udbm_version,
            udbm_commit=udbm_commit,
            udbm_commit_time=udbm_commit_time,
            ucdd_version=ucdd_version,
            ucdd_commit=ucdd_commit,
            ucdd_commit_time=ucdd_commit_time,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
