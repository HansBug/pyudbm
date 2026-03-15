# CLAUDE.md

## Project Identity

`pyudbm` is intended to become a Python wrapper around the UPPAAL DBM library, not a reimplementation of DBM algorithms.

Relevant upstream context:

- `UPPAALModelChecker` is the public GitHub organization for UPPAAL components and libraries.
- `UPPAALModelChecker/UDBM` is the upstream DBM library used here.
- `UDBM` depends on `UUtils`; this repository currently vendors `UUtils` as a submodule from `HansBug/UUtils`, while the original upstream utility library lives at `UPPAALModelChecker/UUtils`.

Current status:

- This repository is still unfinished.
- The Python wrapper layer is not complete yet and should be treated as work in progress.
- Do not assume the existing `pyudbm/` code is a finished or stable public API.

The job of this repository is to gradually expose, package, test, and document Python bindings for upstream functionality. Keep the wrapper thin and faithful to upstream behavior.

There is also a more specific product goal for this repository:

- Recreate the historical UDBM Python binding on top of modern Python tooling.
- Use the old binding as a behavioral reference first, then extend it.
- Modernize the implementation and packaging without casually changing the core model.

## Support Targets

This repository should be developed against the following support expectations:

- Target CPython versions: 3.7 through 3.14.
- Target platforms: Linux, macOS, and Windows.
- Cross-platform support is a core requirement, not an optional extra.
- CI, packaging metadata, and wheel-building configuration should reflect the supported Python range as closely as practical.

Windows compatibility requires extra discipline:

- Keep compatibility with older Windows versions in mind, including Windows 7 class environments where practical.
- Do not introduce unnecessary Win10+ or Win11-only assumptions in Python code, build scripts, or packaging logic.
- When a Windows limitation comes from upstream CPython rather than this repository, document that explicitly instead of misattributing it to `pyudbm`.

Important practical constraint:

- Official CPython support means Windows 7 compatibility is realistically relevant to Python 3.7 and 3.8.
- Newer CPython releases, including Python 3.14, require newer Windows versions upstream.
- Therefore, "support Python 3.7-3.14" and "keep old Windows compatibility" must be interpreted together, not as "every Python in that range runs on Windows 7".
- Avoid raising the Windows floor beyond what upstream Python already requires.

## Legacy Python Binding Reference

The historical upstream Python binding is an important reference for this repository.

Primary references:

- Wiki page: <https://github.com/UPPAALModelChecker/UDBM/wiki/Python-Binding>
- Legacy page: <https://homes.cs.aau.dk/~adavid/udbm/python.html>
- Legacy source package: <https://homes.cs.aau.dk/~adavid/UDBM/ureleases/python_dbm-0.1.tar.gz>

Key facts from that legacy binding:

- It targeted Python 2.x.
- It used SWIG, not pybind11.
- It was only documented and tested on Linux.
- The old install flow assumed a preinstalled UDBM library under `/usr/local/uppaal/include` and `/usr/local/uppaal/lib`.
- The release archive was named `python_dbm-0.1`.
- The package exposed a high-level Python API instead of only raw DBM helper functions.

Important legacy API concepts:

- `Context` created named clocks, for example `Context(["x", "y", "z"], name="c")`.
- `Clock` objects supported arithmetic and comparison operator overloading.
- `Clock` and clock differences built constraints such as `c.x < 10` or `c.x - c.y <= 1`.
- `Federation` represented unions of DBMs and supported set-style operators such as `&`, `|`, `+`, and `-`.
- `IntValuation` and `FloatValuation` were used for containment checks.
- The old package exported at least `Clock`, `Context`, and `Federation` from the package root.

Important legacy behaviors to preserve when practical:

- High-level modeling happened through `Context` / `Clock` / `Federation`, not only through raw matrix primitives.
- Natural expression syntax was a core feature, not a convenience detail.
- Many `Federation` transformation methods behaved as non-mutating operations by returning a modified copy.
- Legacy tests explicitly exercised behaviors such as `up`, `down`, `setZero`, `setInit`, `freeClock`, `predt`, `convexHull`, `reduce`, `updateValue`, `resetValue`, `contains`, `extrapolateMaxBounds`, `isZero`, `isEmpty`, and hashing.

For this repository, treat the legacy binding as the reference for high-level semantics, but not for implementation technology.

That means:

- Prefer Python 3, pybind11, modern packaging, and wheel-friendly builds.
- Do not preserve Python 2 or SWIG just for historical fidelity.
- It is fine to improve typing, packaging, module layout, and platform support.
- Avoid unnecessary semantic drift in the legacy `Context` / `Clock` / `Federation` programming model.
- When behavior is unclear, inspect the historical `udbm.py` and `test.py` before inventing a new API shape.

## Compatibility Direction

The current repository already contains low-level binding-oriented code under `pyudbm/`, but the historical reference point is a richer high-level Python DSL.

Therefore:

- Building low-level bindings is not enough by itself.
- A complete direction for this project should include a modern equivalent of the old high-level federation API.
- Legacy parity should be established before adding project-specific extensions, unless there is a strong reason to diverge.
- Extensions should preferably layer on top of, or coexist with, a compatibility-minded core API rather than replace it outright.

## Hard Boundary: Submodules

The `UDBM/` and `UUtils/` directories are git submodules.

Non-negotiable rule:

- Do not modify files inside `UDBM/` or `UUtils/`.
- The only allowed change involving those directories is updating the submodule version pointer.
- Do not apply "small local fixes" inside a submodule.
- Do not silently repoint submodule remotes or rewrite `.gitmodules` unless explicitly requested.

If a requested change requires altering upstream source code, do one of these instead:

1. Update the submodule to a version that already contains the needed fix.
2. Adapt this repository's wrapper, packaging, tests, or documentation around the current upstream behavior.
3. Document the upstream limitation clearly.

## Where Changes Belong

Safe places to work:

- `pyudbm/` for the in-progress Python API and binding-facing code.
- `pyudbm/core/*.cpp` for pybind11 bindings.
- `pyudbm/core/*.py` for Python-level wrappers.
- `pyudbm/config/meta.py` for package metadata.
- `test/` for Python tests.
- Root build and packaging glue such as `CMakeLists.txt`, `Makefile`, `setup.py`, `pyproject.toml`, and `.github/workflows/`.

Treat these as generated or local-only artifacts:

- `build/`
- `dist/`
- `wheelhouse/`
- `bin_install/`
- `UDBM_build/`
- `UUtils_build/`
- `.pytest_cache/`
- `__pycache__/`
- `venv/`

Do not commit generated binaries, coverage outputs, or environment-specific build products.

## Build and Test Workflow

Build order matters: `UUtils` -> `UDBM` -> `pyudbm`.

Typical local workflow:

1. Initialize submodules:
   `git submodule update --init --recursive`
2. Build and install the upstream C/C++ dependencies into the local prefix:
   `make bin`
3. Build the Python extension modules in place:
   `make build`
4. Run Python unit tests:
   `make unittest`
5. Clean generated outputs when needed:
   `make clean_x`

Packaging and wheel builds are driven by `pyproject.toml`, `setup.py`, and the GitHub Actions workflows. Keep local build logic aligned with CI.

## Engineering Expectations

- Preserve upstream terminology and semantics. Methods like `up`, `down`, `constrain`, and related DBM operations should stay close to UDBM.
- Prefer thin wrappers over opinionated abstractions.
- Since the wrapper is still incomplete, prefer extending coverage incrementally instead of pretending the API surface is already comprehensive.
- If you expose a new upstream capability, update the binding layer, the Python API, and tests together.
- Keep cross-platform build behavior in mind; this repository already carries Linux, macOS, and Windows wheel logic.
- Prefer fixing this repository's binding, packaging, or CI glue instead of patching upstream code in submodules.

## Decision Rules for Agents

- If the task is about Python ergonomics, packaging, build orchestration, CI, tests, or docs, solve it in this repository.
- If the task would require changing UDBM or UUtils source, stop at the wrapper boundary unless the user explicitly asks for a submodule version bump.
- When updating a submodule version, verify compatibility with the wrapper and adjust tests or build glue as needed.
- When in doubt, keep `pyudbm` aligned with upstream behavior rather than inventing repository-local semantics.

## Upstream References

- UPPAAL organization: <https://github.com/UPPAALModelChecker>
- UDBM upstream: <https://github.com/UPPAALModelChecker/UDBM>
- UUtils upstream: <https://github.com/UPPAALModelChecker/UUtils>
- Current vendored UUtils fork: <https://github.com/HansBug/UUtils>
