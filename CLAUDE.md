# CLAUDE.md

`AGENTS.md` and `CLAUDE.md` are the same file via symlink. Edit only one of them and avoid duplicate changes.

## Project Identity

`pyudbm` is intended to become a Python wrapper around the UPPAAL DBM library, not a reimplementation of DBM algorithms inside this repository.

Relevant upstream context:

- `UPPAALModelChecker` is the public GitHub organization for UPPAAL components and libraries.
- `UPPAALModelChecker/UDBM` is the upstream DBM library used here.
- `UDBM` depends on `UUtils`.
- This repository currently vendors `UUtils/` as a submodule from `HansBug/UUtils`, while the original upstream utility library lives at `UPPAALModelChecker/UUtils`.

Current status:

- This repository is still unfinished.
- The Python wrapper layer is still work in progress.
- Do not assume the existing `pyudbm/` code is a complete, stable, final public API.

The core job of this repository is to gradually expose, package, test, and document Python bindings for upstream functionality while keeping the wrapper thin and faithful to upstream behavior.

There is also a more specific product direction:

- Recreate the historical UDBM Python binding on top of the current technology stack.
- Use the old binding as the behavioral reference first, then extend it.
- Modernize the implementation and packaging without casually changing the core model.

Short-term repository direction:

- Recreate the core high-level functionality preserved in `srcpy2/`.
- Restore the historical `Context` / `Clock` / `Federation` programming model on top of the current stack.
- Prioritize natural expression syntax, core federation operations, valuations, and containment semantics.
- Do not treat “low-level DBM helper bindings only” as an acceptable end state.

## Current Repository Reality

As the repository currently stands:

- The binding stack is `pybind11 + CMake + setuptools`, not SWIG.
- The root `CMakeLists.txt` builds one pybind11 extension module from:
  - `pyudbm/binding/_binding.cpp`
- The currently visible Python-side code mostly lives in:
  - `pyudbm/binding/udbm.py`
  - `pyudbm/binding/__init__.py`
  - `pyudbm/config/meta.py`
- The package root re-exports the high-level binding API from `pyudbm.binding`.
- Test coverage is currently centered on:
  - `test/binding/test_api.py`
  - `test/config/test_meta.py`

That means the repository has already moved back to a compatibility-oriented high-level API, but the wrapper is still unfinished and should continue to follow the long-term legacy-parity direction instead of ossifying around temporary implementation details.

## Support Targets

This repository should be developed against the following support expectations:

- Target CPython versions: `3.7` through `3.14`
- Target platforms: `Linux`, `macOS`, and `Windows`
- Cross-platform support is a core requirement, not an optional extra
- CI, packaging metadata, and wheel-building configuration should reflect the supported Python range as closely as practical

Windows compatibility requires extra discipline:

- Keep older Windows environments in mind, including Windows 7 class environments where practical.
- Do not introduce unnecessary Win10+ or Win11-only assumptions in Python code, build scripts, or packaging logic.
- When a Windows limitation comes from upstream CPython rather than this repository, document that explicitly instead of misattributing it to `pyudbm`.

Important practical constraint:

- Official CPython support means Windows 7 compatibility is realistically relevant mainly to Python `3.7` and `3.8`.
- Newer CPython releases, including Python `3.14`, require newer Windows versions upstream.
- Therefore, “support Python 3.7-3.14” and “keep old Windows compatibility in mind” must be interpreted together, not as “every Python in that range runs on Windows 7”.
- Do not raise the Windows floor beyond what upstream Python already requires.

Release constraint:

- The intended distribution model is prebuilt packages for end users.
- End users should not need to compile UDBM locally in order to install `pyudbm`.
- That means development choices must avoid runtime designs that rely on the user having a local native build toolchain.

Current CI / wheel facts that matter:

- The repository uses `cibuildwheel`.
- `PyPy` is skipped.
- Free-threaded CPython `3.13t` / `3.14t` wheels are skipped.
- Current workflows cover mainstream Linux / Windows / macOS combinations.
- Windows is currently validated primarily on `AMD64`.
- Win32 still has known failures, so do not assume 32-bit Windows is already solved.
- On macOS arm64, do not assume every older Python release is available; for example, Python `3.7` has upstream installer availability constraints.

## Legacy Python Binding Reference

The historical upstream Python binding is an important reference point for this repository.

Primary references:

- Wiki page: <https://github.com/UPPAALModelChecker/UDBM/wiki/Python-Binding>
- Legacy page: <https://homes.cs.aau.dk/~adavid/udbm/python.html>
- Legacy source package: <https://homes.cs.aau.dk/~adavid/UDBM/ureleases/python_dbm-0.1.tar.gz>

Local repository copy:

- `srcpy2/` contains an extracted local copy of the official legacy `python_dbm-0.1` source package.

Reference snapshot rules for `srcpy2/`:

- `srcpy2/` exists to preserve the historical Python 2 binding as an archaeological reference snapshot.
- Start with `srcpy2/README.md` for provenance, usage reconstruction, and historical context.
- Then inspect the following when recovering legacy semantics or build assumptions:
  - `srcpy2/udbm.py`
  - `srcpy2/test.py`
  - `srcpy2/setup.py`
  - `srcpy2/udbm_int.i`
  - `srcpy2/udbm_int.h`
- Unless the user explicitly requests it, do not treat `srcpy2/` as an implementation target for feature work, cleanup, modernization, or bug fixing.
- Unless the user explicitly requests it, do not modify any file under `srcpy2/` except `srcpy2/README.md`.
- In particular, do not edit these by default:
  - `srcpy2/README`
  - `srcpy2/PKG-INFO`
  - `srcpy2/__init__.py`
  - `srcpy2/setup.py`
  - `srcpy2/test.py`
  - `srcpy2/udbm.py`
  - `srcpy2/udbm_int.h`
  - `srcpy2/udbm_int.i`

Key facts from that legacy binding:

- It targeted Python 2.x.
- It used SWIG, not pybind11.
- It was documented and tested mainly on Linux.
- The old install flow assumed a preinstalled UDBM library under `/usr/local/uppaal/include` and `/usr/local/uppaal/lib`.
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
- Legacy tests explicitly exercised behaviors such as:
  - `up`
  - `down`
  - `setZero`
  - `setInit`
  - `freeClock`
  - `predt`
  - `convexHull`
  - `reduce`
  - `updateValue`
  - `resetValue`
  - `contains`
  - `extrapolateMaxBounds`
  - `isZero`
  - `isEmpty`
  - hashing

When behavior is unclear, inspect `srcpy2/udbm.py` and `srcpy2/test.py` before inventing a new API shape.

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
- Do not apply “small local fixes” inside a submodule.
- Do not silently repoint submodule remotes or rewrite `.gitmodules` unless explicitly requested.

If a requested change requires altering upstream source code, do one of these instead:

1. Update the submodule to a version that already contains the needed fix.
2. Adapt this repository’s wrapper, packaging, tests, or documentation around the current upstream behavior.
3. Document the upstream limitation clearly.

## Where Changes Belong

Safe places to work:

- `pyudbm/` for the in-progress Python API and binding-facing code.
- `tools/` for repository maintenance utilities such as metadata sync scripts.
- `papers/` for paper metadata, reading guides, and manually refined paper content.
- `pyudbm/binding/*.cpp` for pybind11 bindings.
- `pyudbm/binding/*.py` for Python-level wrappers.
- `pyudbm/config/meta.py` for package metadata.
- `test/` for Python tests.
- `srcpy2/README.md` for archaeology notes about the vendored legacy Python 2 reference snapshot.
- Root build and packaging glue such as:
  - `CMakeLists.txt`
  - `Makefile`
  - `setup.py`
  - `pyproject.toml`
  - `.github/workflows/*`

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
- `.coverage`
- `coverage.xml`
- `pyudbm/binding/*.so`
- `pyudbm/binding/*.pyd`

Do not commit generated binaries, coverage outputs, or environment-specific build products.

## Papers Workflow

The `papers/` tree is a curated documentation and reference area with its own maintenance rules.

Before doing any work under `papers/`, you must first read:

- `papers/README.md`

Treat `papers/README.md` as the source of truth for:

- the standard structure of each paper directory
- top-level maintenance rules for paper entries
- the expected relationship between `README.md` and `README_zh.md`
- the content-refinement workflow for `content.md` and `content_assets/`

Important rules for `papers/` work:

- Do not start editing, generating, renaming, or refining files under `papers/` before reading `papers/README.md`.
- If a task changes top-level `papers/README.md`, keep `papers/README_zh.md` synchronized unless the user explicitly asks for English-only changes.
- If a task involves refining `content.md`, follow the workflow in `papers/README.md` exactly.
- In particular, for paper-content refinement, only the initial export step should rely on `python -m tools.papers_to_content`; the later refinement steps must be driven by the LLM's own text understanding and page-level visual reading ability rather than rough automatic cleanup tools.

## Tutorial Docs Workflow

The `docs/source/foundations/` area has its own structure and citation rules.

Directory and navigation rules:

- Do not create or keep unnecessary `docs/source/foundations/index.rst` or `index_zh.rst` section-index pages.
- Treat each actual foundations page as its own topic directory with `index.rst` / `index_zh.rst`.
- `reading-guide/` is a normal topic page, not a parent page above the other topics.
- Every completed foundations page should also be linked directly from:
  - `docs/source/index_en.rst`
  - `docs/source/index_zh.rst`

Source selection rules:

- For introductory or tool-facing UPPAAL pages, do not rely on papers alone.
- Also consult official UPPAAL sources such as:
  - `https://uppaal.org/`
  - `https://uppaal.org/features/`
  - `https://docs.uppaal.org/`
- Use papers and local `papers/*/README*.md` guides as deeper or historical support, not as the only source for official tool behavior.

Reference style rules:

- When a tutorial page extends to specific papers or official docs, use paper-style references in the body, such as `[LPY97]_` or `[UPP_HELP]_`.
- End the page with a `References` / `参考文献` section.
- Each reference entry should include:
  - author or source name
  - title
  - a public link
  - when applicable, a link to the repository-local reading guide
- For English pages, prefer linking to `README.md`.
- For Chinese pages, prefer linking to `README_zh.md`.

Writing expectations:

- Introductory tutorial pages should not be text-only walls.
- Prefer adding explanatory diagrams, especially:
  - system or control-loop sketches
  - workflow diagrams
- symbolic-vs-concrete intuition diagrams
- If a page is conceptually central, it should usually contain more than one figure.
- When showing a DBM as a LaTeX matrix in tutorial pages, include explicit row and column clock headers in the matrix itself, such as `x_0`, `x`, `y`, rather than showing an unlabeled bare matrix. This applies to both English and Chinese pages.
- For geometric DBM / zone figures, prefer checked-in `.plot.py` generators that produce `.plot.py.svg` outputs through the existing docs build chain rather than hand-drawn screenshots.
- Prefer keeping DBM / zone plot figures language-neutral when practical, so the same SVG can usually be reused by English and Chinese pages; put most explanatory prose in the surrounding `.rst` text instead of inside the plot.
- For operation-oriented geometric figures, prefer before/after side-by-side comparisons so readers can see how a DBM operation changes the represented zone.
- Do not open too many high-level sections on a single tutorial page when they are really explaining one continuous topic. Group related material under a limited number of top-level sections, and use lower-level subsections inside them.
- Before setting section boundaries, identify the page's main narrative spine and make the top-level table-of-contents view reflect that spine clearly. A reader scanning the section list should see a few coherent stages, not a flat pile of near-duplicate topics.

Chinese terminology rule:

- In Chinese `.rst` tutorial pages, use Chinese terminology as the default prose language.
- On first mention within a page, you may introduce the English term or abbreviation in parentheses, for example `时间自动机(timed automata)` or `符号状态(symbolic state)`.
- After that first introduction, continue using the Chinese term in normal prose instead of switching back and forth between Chinese and English.
- Apply the same rule to explanatory text inside Chinese-facing diagrams, especially Graphviz labels, cluster titles, node descriptions, and edge labels; keep English only for code literals, page slugs, official names, and unavoidable acronyms.
- Exceptions are limited to code literals, file paths, page slugs, official document titles, and unavoidable proper-name acronyms.
- Before finalizing Chinese docs edits, do a pass specifically to remove leftover English-term drift in the prose.

## Repository Structure

The current repository layout can be understood like this:

```text
.
|- AGENTS.md -> CLAUDE.md
|- CLAUDE.md
|- CMakeLists.txt                # Root CMake for pybind11 extension builds
|- Makefile                      # Unified local build / test / package entrypoint
|- tools/                        # Repository maintenance helper scripts
|  |- __init__.py
|  `- udbm_version.py            # Sync UDBM version/commit into pyudbm metadata
|- pyproject.toml                # Build-system metadata and cibuildwheel config
|- setup.py                      # setuptools + CMake bridge
|- requirements*.txt             # runtime / build / test / docs dependencies
|- papers/                       # curated paper references, guides, and refined content
|- pyudbm/                       # Current Python package
|  |- __init__.py
|  |- binding/
|  |  |- __init__.py             # public binding namespace
|  |  |- _binding.cpp            # pybind11 binding implementation
|  |  `- udbm.py                 # historical high-level Python DSL
|  |- config/
|  |  `- meta.py                 # package metadata
|- test/
|  |- binding/
|  |  `- test_api.py
|  |- config/
|  |  `- test_meta.py
|- srcpy2/                       # historical Python 2 binding snapshot
|- UUtils/                       # upstream submodule, do not patch directly
|- UDBM/                         # upstream submodule, do not patch directly
|- UUtils_build/                 # local UUtils build directory
|- UDBM_build/                   # local UDBM build directory
|- bin_install/                  # local install prefix
|- build/                        # Python extension temporary build directory
`- .github/workflows/            # CI / wheel / release workflows
```

Additional notes:

- `pyudbm/binding/` contains both hand-written source files and the in-place built extension output.
- Do not edit compiled extension artifacts that appear under `pyudbm/binding/`.
- The repository currently has no root `docs/` directory, so `make docs` / `make pdocs` should not be treated as a working documentation flow yet.
- `Makefile` still exposes variables for benchmark paths, but the repository does not currently contain a real benchmark tree.

## Local Development Environment

### Required Tooling

To run the repository end-to-end locally, you need at least:

- `git`
- `bash`
- `make`
- `cmake`
- a working C/C++ compiler toolchain
- a working `python` and `pip`

Based on the current repository:

- `CMake < 4` is expected
- a `C++17` capable toolchain is required
- `pybind11[global]` is required for local extension builds
- `setuptools`, `wheel`, and `build` are part of the local build toolchain

Python dependency layers in this repository:

- Runtime: `requirements.txt`
- Build: `requirements-build.txt`
- Test: `requirements-test.txt`
- Docs: `requirements-doc.txt`

Concrete dependency notes from the current files:

- `requirements.txt` is currently empty because the restored high-level binding does not need extra runtime Python dependencies.
- `requirements-build.txt` currently contains:
  - `pybind11[global]`
  - `build>=0.7.0`
  - `auditwheel>=4`
  - `cmake<4`
  - `wheel`
- `requirements-test.txt` currently includes:
  - `coverage`
  - `mock`
  - `flake8`
  - `testfixtures`
  - `pytest`
  - `pytest-cov`
  - `pytest-timeout`
  - `easydict`
  - `testtools`
  - `where`
  - `responses`
  - `natsort`

### Platform Guidance

Linux:

- Prepare `gcc/g++` or another compatible toolchain.
- Prepare `make`.
- Prepare `cmake`.

macOS:

- Prepare Xcode Command Line Tools.
- Prepare `make`.
- Prepare a recent `cmake`.
- The repository includes `macos_kill_cmake.sh`, which is a sign that old system CMake versions have been a real issue.

Windows:

- Prefer running repository-level `make` commands from `Git Bash` or another environment with `bash`.
- The current `Makefile` uses `readlink -f`, shell expansion, and quoted environment-variable passing. Do not assume a pure `cmd.exe` workflow will work cleanly.
- Current CI validates `windows-2022` with `bash`, `make`, and `cmake`.
- Do not assume Win32 is already working.

## Local Setup

Recommended local bootstrap flow:

```bash
git submodule update --init --recursive

python -m venv venv
source venv/bin/activate
# Windows (Git Bash): source venv/Scripts/activate

python -m pip install -U pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -r requirements-test.txt
python -m pip install -r requirements-build.txt
```

If you want to inspect the current path and CMake environment expansion before building, run:

```bash
make info
```

That prints values such as:

- `PS`
- `CMAKE_E`

This is useful when debugging local prefix and CMake lookup issues.

## Full Local Bring-Up Flow

If you want to run the repository end-to-end locally once, the correct order is:

1. Initialize submodules.
2. Run `make bin`.
3. Run `make build`.
4. Run `make unittest`.

If you skip `make bin`, `make build` will likely fail because the root `CMakeLists.txt` expects to find installed UUtils / UDBM libraries and headers under the local prefix, by default `bin_install/`.

### Step 1: Initialize Submodules

```bash
git submodule update --init --recursive
```

Without this, `UDBM/` and `UUtils/` may be incomplete.

### Step 2: Build, Test, and Install Native Dependencies

```bash
make bin
```

`make bin` expands to:

1. `make uutils`
2. `make udbm`

And those expand to:

- `make uutils` = `uutils_build` + `uutils_test` + `uutils_install`
- `make udbm` = `udbm_build` + `udbm_test` + `udbm_install`

So `make bin` is not just “compile native code”. It actually:

- configures and builds `UUtils`
- runs `ctest` for `UUtils`
- installs `UUtils` into the local prefix `bin_install/`
- configures and builds `UDBM`
- runs `ctest` for `UDBM`
- installs `UDBM` into the local prefix `bin_install/`

This is the native prerequisite chain for Python extension builds.

### Step 3: Build the Python Bindings

```bash
make build
```

This runs:

```bash
BINSTALL_DIR="${BINSTALL_DIR}" python setup.py build_ext --inplace
```

In practice this means:

- enter `setup.py`
- invoke the custom `CMakeBuild`
- build the pybind11 extensions through the root `CMakeLists.txt`
- place the built module in `pyudbm/binding/`

At the moment the root build produces one extension module:

- `_binding`

### Step 4: Run Python Unit Tests

```bash
make unittest
```

This runs pytest against the Python test tree and is not a replacement for the upstream native `ctest` runs already covered by `make bin`.

## Recommended Local Validation Commands

Typical full local smoke flow:

```bash
git submodule update --init --recursive
python -m pip install -r requirements.txt
python -m pip install -r requirements-test.txt
python -m pip install -r requirements-build.txt
make uversion
make bin
make build
make unittest
```

If you want something closer to the current CI flow:

```bash
CC=gcc CXX=g++ CTEST_CFG=Release make bin
make build
make clean_x
make unittest
```

Important detail:

- `make clean_x` removes `build/`, `dist/`, `wheelhouse/`, and `bin_install/`
- it does not remove the in-place built extension modules already copied into `pyudbm/binding/`
- that is why CI can run `make build`, then `make clean_x`, then still run `make unittest`

By contrast, `make clean` removes the in-place extension `.so` files under `pyudbm/`, so after `make clean` you must rebuild with `make build`.

## Make Target Reference

### Python Package Targets

`make build`

- Build Python extension modules in place.
- Requires the native dependencies to already exist in the local prefix.

`make package`

- Build both sdist and wheel into `dist/`.
- Still depends on the native build chain being resolvable.

`make zip`

- Build only the sdist.

`make clean`

- Remove built extension `.so` files under `pyudbm/`
- Remove `dist/` and `wheelhouse/`
- Remove `build/temp.*`

`make clean_x`

- Remove a wider set of local build outputs:
  - `dist/`
  - `wheelhouse/`
  - `build/`
  - `bin_install/`

`make uversion`

- Update `pyudbm/config/meta.py` with the declared version from
  `UDBM/CMakeLists.txt` and the current `UDBM` submodule commit hash.
- Runs `python -m tools.udbm_version -i UDBM -o pyudbm/config/meta.py`.

### Python Test Targets

`make test`

- Alias for `make unittest`

`make unittest`

- Run pytest
- Default path is `test/${RANGE_DIR}`
- Default marker is `unittest`
- Default coverage reports are `xml term-missing`

Useful variables:

- `RANGE_DIR=<dir>` limits the test scope
- `COV_TYPES='xml term-missing'` controls coverage report types
- `MIN_COVERAGE=<n>` sets a minimum coverage threshold
- `WORKERS=<n>` enables pytest-xdist parallel workers

Examples:

```bash
make unittest
make unittest RANGE_DIR=binding
make unittest COV_TYPES="xml term-missing"
make unittest MIN_COVERAGE=80
make unittest WORKERS=4
```

### UUtils Targets

`make uutils_build`

- Configure and build `UUtils`

`make uutils_test`

- Run `ctest` inside `UUtils_build/`

`make uutils_install`

- Install `UUtils` into `bin_install/`

`make uutils_clean`

- Remove `UUtils_build/`

`make uutils`

- `uutils_build` + `uutils_test` + `uutils_install`

`make uutils_notest`

- `uutils_build` + `uutils_install`

### UDBM Targets

`make udbm_build`

- Configure and build `UDBM`
- Requires `UUtils` to have already been installed into the local prefix

`make udbm_test`

- Run `ctest` inside `UDBM_build/`

`make udbm_install`

- Install `UDBM` into `bin_install/`

`make udbm_clean`

- Remove `UDBM_build/`

`make udbm`

- `udbm_build` + `udbm_test` + `udbm_install`

`make udbm_notest`

- `udbm_build` + `udbm_install`

### Combined Native Dependency Pipeline

`make bin`

- `uutils` + `udbm`
- Full build + test + install pipeline for native dependencies

`make bin_notest`

- `uutils_notest` + `udbm_notest`

`make bin_clean`

- Remove:
  - `UUtils_build/`
  - `UDBM_build/`
  - `bin_install/`

### Documentation Targets

`make docs`

- Intended to build docs
- Currently not usable as a real workflow because the repository does not have a root `docs/` tree

`make pdocs`

- Same caveat as above

### Diagnostic Targets

`make info`

- Print current path-separator and CMake-related environment values
- Useful when debugging local prefix / lookup issues

## Important Build Details

### Local Install Prefix

By default, native dependencies are installed into:

- `bin_install/`

Relevant variables:

- `BINSTALL_DIR`
- `BINSTALL_LIB_DIR`
- `BINSTALL_INCLUDE_DIR`

If you need a custom prefix:

```bash
BINSTALL_DIR=/custom/prefix make bin
BINSTALL_DIR=/custom/prefix make build
```

Important rule:

- `make build` must use the same prefix that was used for `make bin`
- otherwise the Python extension build may fail to locate UUtils / UDBM

### CMake Build Configuration

Default build configuration:

- `CTEST_CFG=Release`

You can override it explicitly:

```bash
CTEST_CFG=Release make bin
CTEST_CFG=Debug make build
```

### Coverage Instrumentation

The root `CMakeLists.txt` adds coverage flags for C++ builds when the `LINETRACE` environment variable is non-empty:

```bash
LINETRACE=1 make build
```

Current CI also uses this mechanism.

## Packaging and Release

Current packaging stack:

- `pyproject.toml`
- `setup.py`
- `setuptools`
- `build`
- `pybind11`
- `cibuildwheel`

Release principles:

- This is a Python package with native extensions.
- Prebuilt wheels are the intended end-user distribution path.
- Do not design around “the user will build UDBM locally” as the normal installation story.
- Every added dependency should be evaluated for:
  - cross-platform build stability
  - Python `3.7-3.14` compatibility
  - wheel-building complexity on Windows / macOS / Linux

## Engineering Expectations

### Semantics and Architecture

- Preserve upstream terminology and semantics. Methods like `up`, `down`, `constrain`, and related DBM operations should stay close to UDBM.
- Prefer thin wrappers over opinionated abstractions.
- If upstream already provides the capability, prefer exposing it faithfully instead of re-inventing it in repository-local form.
- High-level API design should follow the historical binding where practical, not the accidental shape of the current incomplete low-level wrapper.
- Low-level bindings alone are not enough. The product direction includes a high-level Python DSL.

### Change Scope

- If you expose a new upstream capability, update the binding layer, the Python API, and tests together.
- Since the wrapper is still incomplete, prefer extending coverage incrementally instead of pretending the API surface is already comprehensive.

### Platform Awareness

- Do not write code that assumes Linux-only paths or behaviors.
- Do not assume a case-sensitive filesystem.
- Do not assume `/usr/local/...` style install paths exist.
- Do not assume symlinks, `fork`, or GNU-specific tool behavior everywhere.
- Think about Windows compatibility from the start instead of treating it as a later cleanup task.

## Python Code Style

This section is adapted from the Python style guidance in `~/oo-projects/pyfcstm/CLAUDE.md`, but adjusted to fit this repository.

### Core Principles

- Code must remain compatible with Python `3.7-3.14`.
- Prefer clarity, stability, and portability over fashionable syntax.
- Public APIs should have type annotations.
- Public Python APIs should have docstrings.
- New behavior should come with tests.
- Python-side semantics should stay aligned with upstream UDBM and the historical binding.

### Python 3.7 Compatibility Rules

Because support starts at Python `3.7`, do not default to newer-only syntax or stdlib features such as:

- `list[str]`, `dict[str, int]`, and other PEP 585 built-in generic syntax
- `str | None` and other PEP 604 union syntax
- `match/case`
- `typing.Self`
- `tomllib`
- newer typing features with no compatibility path

Prefer:

- `List`, `Dict`, `Tuple`, `Set`
- `Optional`
- `Union`
- compatibility imports when needed for `Protocol`, `TypedDict`, and similar features

Example:

```python
from typing import List, Optional, Tuple, Union
```

instead of:

```python
def f(items: list[str] | None) -> dict[str, int]:
    ...
```

### Dependency and Portability Rules

- Do not add third-party dependencies casually.
- Before adding a dependency, evaluate:
  - Python 3.7 support
  - Windows / Linux / macOS support
  - wheel build impact
- If the standard library is sufficient, prefer it.
- Use `os.path` or `pathlib` for paths.
- Be explicit about subprocess behavior, path handling, and encodings instead of relying on platform defaults.

### API Semantics Rules

- If a historical method was non-mutating, do not casually make it mutating.
- If the historical API exposed high-level expression syntax, do not regress to “call low-level helper functions only”.
- Prefer names and semantics aligned with UDBM and the legacy binding.
- When adding high-level APIs, inspect `srcpy2/udbm.py` and `srcpy2/test.py` first.

### Testing Rules

- New or changed behavior must have pytest coverage.
- For high-level compatibility work, tests should express the intended historical behavior.
- If behavior is inherited from upstream UDBM rather than invented locally, reflect that clearly in tests, comments, or commit messages.
- Extend the structured `test/` tree instead of adding ad hoc validation scripts and calling them “tests”.

### Test Organization

- Put tests under `test/` and mark unit tests with `@pytest.mark.unittest`.
- Binding-facing tests belong under `test/binding/`.
- If shared fixtures or helpers become necessary, place them in a dedicated `test/testings/` area instead of scattering them across feature directories.
- Keep test runtime within the timeout configured by `pytest.ini` for this repository.

## Commit Message Style

Follow the dominant repository convention from recent history.

- For normal commits, prefer `type(scope): imperative summary`, such as
  `feat(binding): add federation containment helpers` or
  `test(binding): strengthen legacy compatibility coverage`.
- Use short lowercase types such as `feat`, `fix`, `docs`, `test`, `refactor`, `chore`; keep the scope lowercase when present
  (`binding`, `config`, `tests`, `cmake`, `packaging`, `ci`, etc.). Omit the scope only when the change genuinely spans the whole repository.
- Write the summary as a concise imperative phrase starting with a lowercase verb (`add`, `update`, `improve`, `align`, `restore`,
  `clean up`); do not add a trailing period.
- For non-trivial changes, add a blank line and then a body. Match the common repository pattern:
  a short overview sentence or paragraph first, followed by `-` bullet points for concrete changes, tests, compatibility notes,
  docs updates, or behavior clarifications.
- When a bullet needs to wrap, continue it on the next line with indentation rather than starting a new bullet.
- Preserve standard trailers when applicable, especially `Co-Authored-By: Name <email>`.
- Merge commits should keep the generated style used in history, such as `Merge branch 'main' into dev/...` or
  `Merge pull request #52 from HansBug/dev/fixed`.

## reST Documentation and Docstring Style Guide

Use **reStructuredText (reST)** conventions for both public Python docstrings and repository `.rst` documentation
pages. For docstrings, follow PEP 257 and Sphinx conventions. For `.rst` pages, apply the same inline markup
discipline and prefer source-only edits rather than touching generated outputs.

### Core Requirements

1. Use reST only, not Google or NumPy style.
2. Public modules, classes, functions, and methods should have docstrings.
3. Non-trivial APIs should have more than a one-line summary.
4. Document parameters with `:param:` and `:type:`.
5. Document return values with `:return:` and `:rtype:`.
6. Document exceptions with `:raises:`.
7. User-facing public APIs should ideally have at least a minimal example.

### Module Template

```python
"""
Brief one-line description.

Longer description of the module purpose and how it fits into :mod:`pyudbm`.

The module contains:
* :class:`SomeClass` - Brief summary
* :func:`some_function` - Brief summary

Example::

    >>> from pyudbm.some_module import some_function
    >>> some_function()
    expected_result
"""
```

### Class Template

```python
class SomeClass:
    """
    Brief one-line description.

    Longer explanation of responsibilities and expected usage.

    :param dim: Dimension of the DBM.
    :type dim: int
    :ivar dim: Stored DBM dimension.
    :vartype dim: int

    Example::

        >>> obj = SomeClass(3)
        >>> obj.dim
        3
    """
```

### Function or Method Template

```python
def some_function(value: int, strict: bool = False) -> int:
    """
    Brief one-line description.

    Longer explanation of behavior or important semantic notes.

    :param value: Input value to encode.
    :type value: int
    :param strict: Whether strict semantics should be used, defaults to ``False``.
    :type strict: bool, optional
    :return: Encoded raw DBM bound.
    :rtype: int
    :raises ValueError: If ``value`` is outside the accepted range.

    Example::

        >>> some_function(5, strict=True)
        10
    """
```

### Parameter, Return, and Exception Patterns

```python
:param name: Description
:type name: int
:param strict: Description, defaults to ``False``
:type strict: bool, optional
:return: Encoded value
:rtype: int
:return: ``None``.
:rtype: None
:raises ValueError: If the input is invalid.
```

### Documentation Editing

When working on documentation trees:

- edit source `.rst` and `.md` files only
- do not edit generated HTML, copied index files, or other generated artifacts directly
- if a documentation workflow generates derived files, regenerate them from source instead of patching the outputs

### Cross-References and Inline Markup

Prefer reST roles:

- `:class:\`ClassName\``
- `:func:\`function_name\``
- `:meth:\`Class.method_name\``
- `:mod:\`pyudbm.core.constraints\``
- `:exc:\`ValueError\``
- `:data:\`DBM_INFINITY\``
- `:attr:\`instance.attr\``

Inline code should always use double backticks:

- Correct: ``dbm_bound2raw(5, Strictness.STRICT)``
- Incorrect: `dbm_bound2raw(5, Strictness.STRICT)`

### reST Inline Markup Boundary Rules

For `.rst` content, check both the left boundary of the opening marker and the right boundary of the closing marker
for inline strong emphasis (`**text**`) and inline literals (``code``).

Problematic patterns:

- `prefix**text**`
- `**text**suffix`
- `建模**层次状态机**。`
- `前文``code``后文`
- ``literal``（explanation）

Safe patterns:

- `prefix **text** suffix`
- `前文\ **强调**\ 后文`
- `prefix ``code`` suffix`
- `前文\ ``code``\ 后文`
- ``literal``\ （explanation）

Practical rule:

- Do not leave closing `**` or ```` directly attached to full-width Chinese punctuation such as `（`.
- In tight prose, especially around Chinese text, `\ ` is the safest default separator.
- If you do not want visible spaces in rendered Chinese text, prefer `\ ` on both sides as the default safe pattern.

Do not trust full-width Chinese punctuation as a safe boundary. Real broken patterns include:

- `**普通详细级别**（默认）`
- `**1. pip 安装**（推荐）：`
- `1. **本地事件**（``::``）：...`
- `**场景 1：初始进入**（``HierarchyDemo -> Parent -> ChildA``）`
- ``A.enter``（未定义）
- `执行 ``A.enter``（未定义）`
- `检查转换：``A -> B :: Go``（事件匹配！）`
- `**整数：** ``123``、``0xFF``（十六进制）、``0b1010``（二进制）`
- `- ``variable_display_mode`` ... ``'hide'``（默认：``'legend'``）`

Safe forms for those cases:

- `**普通详细级别**\ （默认）`
- `**1. pip 安装**\ （推荐）：`
- `1. **本地事件**\ （``::``）：...`
- `**场景 1：初始进入**\ （``HierarchyDemo -> Parent -> ChildA``）`
- ``A.enter``\ （未定义）
- `执行 ``A.enter``\ （未定义）`
- `检查转换：``A -> B :: Go``\ （事件匹配！）`
- `**整数：** ``123``、``0xFF``\ （十六进制）、``0b1010``\ （二进制）`
- `- ``variable_display_mode`` ... ``'hide'``\ （默认：``'legend'``）`

Do not use single backticks for inline code in reST. Use double backticks only: ``code``.

### reST Verification Workflow

When fixing inline markup at scale in a Sphinx documentation tree:

- rebuild rendered output instead of relying only on source scans
- search the rendered HTML for `problematic` spans or leftover raw `**...**` text
- use rendered output as the final authority for whether `**` / ```` issues are actually fixed

### Docstring Checklist

- One-line summary at the top
- Longer explanation for non-trivial APIs
- All params documented with `:param:` and `:type:`
- Return value documented with `:return:` and `:rtype:`
- Exceptions documented with `:raises:`
- Examples for public APIs where helpful
- Cross-references use reST roles
- Inline code uses double backticks
- Inline markup boundaries are valid in multilingual prose for both docstrings and `.rst` pages

### Anti-Patterns

Do not:

- use Google-style docstrings
- use NumPy-style docstrings
- omit `:type:` when writing `:param:`
- omit `:rtype:` when writing `:return:`
- use single backticks for inline code
- assume full-width Chinese punctuation is a safe boundary for closing `**` or ````
- write vague descriptions like “Does something”
- forget to update docstrings when code changes

## C++ / pybind11 Binding Guidance

- Keep the pybind11 binding layer thin.
- Do not invent new business semantics in the C++ binding layer unless there is a strong reason.
- Prefer exposing upstream UDBM capabilities directly.
- Place higher-level Python ergonomics in the Python layer unless performance or boundary concerns clearly require C++.
- Keep naming close to upstream terminology.
- If a change is only about making Python usage nicer, first ask whether it belongs in `pyudbm/binding/*.py` instead of the C++ binding.

## Agent Decision Rules

- If the task is about Python ergonomics, packaging, build orchestration, CI, tests, or docs, solve it in this repository.
- If the task would require changing UDBM or UUtils source, stop at the wrapper boundary unless the user explicitly asks for a submodule version bump.
- If a task mentions `srcpy2/`, default to reading it as historical reference material. Modify only `srcpy2/README.md` unless the user explicitly asks for a refresh or direct edit of the vendored snapshot.
- When in doubt, keep `pyudbm` aligned with upstream behavior rather than inventing repository-local semantics.
- If behavior is unclear, inspect the historical binding first, then decide how the modern wrapper should expose it.

## Common Workflows

### If You Only Changed the Python Wrapper Layer

Typical flow:

```bash
make build
make unittest RANGE_DIR=binding
```

This assumes you have already run `make bin` at least once before.

### If You Changed UDBM / UUtils Integration Logic

Recommended flow:

```bash
make bin_clean
make bin
make build
make unittest
```

### If You Changed Packaging Logic

Also run:

```bash
make package
```

Then verify:

- the artifacts in `dist/` look correct
- no local-only paths or debug-only binaries leaked into the package

## Upstream References

- UPPAAL organization: <https://github.com/UPPAALModelChecker>
- UDBM upstream: <https://github.com/UPPAALModelChecker/UDBM>
- UUtils upstream: <https://github.com/UPPAALModelChecker/UUtils>
- Current vendored UUtils fork: <https://github.com/HansBug/UUtils>
