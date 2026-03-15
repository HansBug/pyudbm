# Historical UDBM Python 2 Binding Snapshot

This directory contains a local reference copy of the official legacy `python_dbm-0.1` source package described on the UDBM wiki. It is not the active implementation of this repository, and it should not be treated as a maintained Python 3 package. This folder exists so the modern `pyudbm` work can reconstruct the historical API shape and behavior from original materials rather than from memory.

The analysis below is based on static source inspection only. This repository has not built or executed this legacy Python 2 package as part of preparing this note.

## Primary Upstream References

- Main wiki page: <https://github.com/UPPAALModelChecker/UDBM/wiki/Python-Binding>
- Wiki history page: <https://github.com/UPPAALModelChecker/UDBM/wiki/Python-Binding/_history>
- Historical HTML page: <https://homes.cs.aau.dk/~adavid/udbm/python.html>
- Stable source release: <https://homes.cs.aau.dk/~adavid/UDBM/ureleases/python_dbm-0.1.tar.gz>
- Launchpad code repository referenced by the wiki: <https://launchpad.net/pydbm>
- Launchpad development branch page: <https://launchpad.net/~shiyee/pydbm/pydbm>

## Dating and Timeline

Several distinct dates matter here:

- The GitHub wiki page `Python Binding` currently shows its last public edit on June 14, 2021, by Kenneth Yrke Jorgensen. The page currently shows `1 revision`.
- The `python_dbm-0.1.tar.gz` archive copied into this directory carries archive metadata dated March 21, 2011.
- The wiki page points to Launchpad as the "up-to-date source code". The current Launchpad branch page for `lp:pydbm` reports `date_last_modified` as April 8, 2013.

Taken together, the most likely historical picture is:

1. the packaged `0.1` release dates from 2011
2. some later development activity was mirrored on Launchpad by 2013
3. the GitHub wiki page describing the old binding was still edited in 2021

That means the documentation surface was touched more recently than the actual Python 2 code snapshot stored here.

## What Is In This Directory

This snapshot is small, but it is complete enough to reconstruct the original binding layout:

- `README`: the original upstream one-line README pointing to the historical documentation page.
- `README.md`: this explanatory document added in this repository.
- `setup.py`: a `distutils` build script for a SWIG-based native extension.
- `__init__.py`: package entry point exporting `Clock`, `Context`, and `Federation`.
- `udbm.py`: the high-level Python DSL and object model.
- `udbm_int.i`: the SWIG interface definition.
- `udbm_int.h`: a handwritten C++ adapter layer wrapping UDBM types for SWIG exposure.
- `test.py`: the legacy Python test suite and best local semantic reference.
- `PKG-INFO`: sparse distribution metadata from the original source package.

One additional build-time detail is worth noting: the snapshot does not contain a checked-in `udbm_int.py`, but that is consistent with SWIG-era workflows. A likely historical build output was:

- `_udbm_int` as the compiled extension module
- `udbm_int.py` as a SWIG-generated Python shim importing `_udbm_int`

That missing generated layer helps explain why this source tree is incomplete as a runnable package unless it is first built.

## Overall Structure

The codebase appears to be organized in three layers:

1. Python user-facing DSL in `udbm.py`.
   This layer defines `Context`, `Clock`, `VariableDifference`, `Constraint`, `Federation`, `IntValuation`, and `FloatValuation`.
2. SWIG extension boundary through `udbm_int.i`.
   This layer describes the native types and methods to export to Python.
3. C++ adapter layer in `udbm_int.h`, linked against the upstream UDBM library.
   This layer includes UDBM headers such as `dbm/fed.h`, `dbm/gen.h`, `dbm/mingraph.h`, `dbm/ClockAccessor.h`, and hash utilities, then wraps them into SWIG-friendlier classes.

In compact form, the architecture looks like this:

`Python API in udbm.py` -> `SWIG wrapper` -> `C++ glue in udbm_int.h` -> `native UDBM library`

## Likely Technical Stack

From the source layout, wiki instructions, and build script, this legacy package was most likely built with the following stack:

- Python 2.x
- `distutils`
- SWIG for Python/C++ binding generation
- C++
- GCC on Linux
- an already installed UDBM native library

The wiki says the binding was tested on Linux only and mentions GCC `4.4.5`. It also says SWIG `1.3.40` was used. The build assumptions in `setup.py` are explicit:

- headers are searched under `/usr/local/uppaal/include`
- libraries are searched under `/usr/local/uppaal/lib`
- the extension links against `udbm`

That strongly suggests a pre-wheel, pre-PEP-517, manually installed native dependency workflow centered on Linux rather than portable packaging.

## How It Was Expected To Be Used Back Then

The historical workflow can be reconstructed from the wiki, `setup.py`, `__init__.py`, and `test.py`.

### 1. System-level prerequisites first

The wiki expected the user to install the native UDBM library before touching the Python package. It also expected SWIG to already exist on the machine. The old instructions assumed this native installation layout:

- `/usr/local/uppaal/include` for headers
- `/usr/local/uppaal/lib` for libraries

The wiki also mentions that on 64-bit systems the user might need to add `-fPIC` to the UDBM Makefile.

### 2. Build and install using Python 2 tooling

The documented build flow was:

```bash
python ./setup.py build
sudo python ./setup.py install
python ./setup.py install --user
```

This is a classic `distutils` source-install workflow rather than a modern isolated build.

One small archaeology note: the current GitHub wiki rendering shows the third command as `python ./setup install --user` without `.py`. Given the presence of `setup.py` and the surrounding commands, that line is very likely just a documentation typo on the wiki page rather than evidence of some different tool.

### 3. Import style depended on whether the code was installed or run from source

There is an interesting split between the wiki and the test suite:

- The wiki shows installed usage via `from python_dbm import Context`.
- The local `test.py` imports `udbm` directly.

The most likely interpretation is:

- after installation, the package name exposed to users was `python_dbm`
- during source-tree development, the high-level module `udbm.py` was imported directly as `udbm`

This makes sense given `setup.py` uses `packages = ['python_dbm']` while `__init__.py` re-exports objects from `udbm.py` using Python 2 implicit relative import behavior.

## Historical Usage Examples

The wiki presents the binding as a natural Python DSL for zones and federations. Its documented example looked like this:

```python
from python_dbm import Context

c = Context(["x", "y", "z"], "c")

a = (c.x < 10) & (c.x - c.y > 1)
b = (c.x < 20)

print a <= b
print a >= b
print a.up() | b
print a | b
```

That is very revealing. The intended user experience was not "call a low-level C function". It was "write zone expressions that look like math".

The source-tree test suite suggests additional expected usage patterns. For example, it tests valuation-based containment:

```python
import udbm

c = udbm.Context(["x", "y", "z"], name="c")
v = udbm.IntValuation(c)
v["x"] = 1
v["y"] = 1
v["z"] = 1

print ((c.x == 1) & (c.y == 1) & (c.z == 1)).contains(v)
```

It also tests difference constraints and non-mutating federation transformations:

```python
import udbm

c = udbm.Context(["x", "y"])
d1 = (c.x >= 1) & (c.x <= 2) & (c.y >= 1) & (c.y <= 2)

print d1.up()
print d1.down()
print d1.freeClock(c.x)
print d1.convexHull()
```

And it uses set-style federation algebra:

```python
import udbm

c = udbm.Context(["x", "y", "z"], name="c")
d1 = (c.x == 1) & (c.y == 1)
d2 = (c.z == 1)

print d1 | d2
print d1 & d2
print d1 + d2
print d1 - d2
```

None of these examples have been executed in this repository as part of this note. They are shown here as historical reconstruction from the original docs and source.

## Inferred Architecture and Design Intent

The old binding was not trying to expose only raw DBM primitives. Instead, it built a high-level modeling DSL on top of a small native bridge:

- `Context` owns named clocks and exposes them by attribute access such as `c.x` and by keyed access such as `c["x"]`.
- `Clock` overloads comparison operators so expressions like `c.x < 10` create symbolic constraints rather than booleans.
- `Clock - Clock` produces a `VariableDifference`, enabling expressions such as `c.x - c.y <= 1`.
- `Federation` is the main semantic object representing unions of DBMs or zones.
- Native operations are wrapped in a Python style that prefers readable algebraic expressions over explicit low-level matrix manipulation.

This is the most important architectural conclusion from the archaeology work: the historical binding was already designed as a user-facing timed-constraint DSL, not merely as a thin debugging shell around a C++ library.

## Reconstructed Functional Scope

Based on `udbm.py`, `udbm_int.h`, `udbm_int.i`, and `test.py`, this package appears to support at least the following behaviors:

- named clock contexts
- symbolic clock constraints with overloaded operators
- difference constraints between clocks
- federation set operations:
  intersection `&`, union `|`, convex union-like `+`, and subtraction `-`
- order and equality relations between federations
- non-mutating transformation methods returning copies for operations such as `up`, `down`, `freeClock`, `convexHull`, `predt`, `updateValue`, `resetValue`, and `extrapolateMaxBounds`
- mutating operations for selected methods such as `setZero`, `setInit`, `reduce`, and in-place set operators
- integer and floating-point valuations for containment checks
- zero-zone and initial-zone helpers
- hashing, emptiness checks, string rendering, and size queries

The test suite also strongly suggests intended semantics such as:

- expression equivalence for overloaded operators
- copy-oriented federation transformations
- a distinction between exact equality, inclusion, and strict inclusion
- support for both integer and floating-point valuations
- a stable hash notion for federations
- emptiness checks over unions of contradictory constraints

## What This Old Code Probably Does Well

Even without executing it, several strengths are visible:

- The user-facing syntax is concise and expressive.
- High-level timed-zone reasoning is clearly the main goal.
- The tests encode semantic expectations that are still useful as a compatibility target.
- The native layer is relatively small, leaving most of the domain-specific ergonomics in Python.
- The package root intentionally exported `Clock`, `Context`, and `Federation`, showing a clear public API focus.

## What Looks Dated or Fragile

Again based on source inspection, the main weaknesses are typical for its era:

- Python 2-only assumptions, including implicit relative imports and `has_key`
- heavy reliance on `assert` for API validation
- hard-coded include and library paths
- `distutils` and SWIG era build flow
- sparse packaging metadata
- no obvious cross-platform packaging strategy
- Linux-only documented installation path
- some package/import behavior that depends on historical Python 2 import rules

## Suggestions For A Modern Recreation

If this binding is recreated with modern tooling, the safest direction is to preserve the semantic model while replacing the implementation technology:

- Keep the high-level `Context` / `Clock` / `Federation` DSL as the compatibility-oriented surface.
- Rebuild the low-level native boundary with `pybind11` rather than SWIG.
- Keep the native layer thin and move Python ergonomics into normal Python modules.
- Use modern packaging such as `pyproject.toml` plus CMake-backed build tooling.
- Remove hard-coded `/usr/local/uppaal` paths and make dependency discovery configurable and cross-platform.
- Port the legacy tests in `test.py` into the repository's Python 3 test suite, using them as semantic regression tests.
- Replace assertion-driven API checks with explicit Python exceptions.
- Preserve non-mutating behavior where the historical API appears copy-oriented.
- Preserve the historical import ergonomics at the top level, even if the internal module structure changes.
- Add type hints and clearer docs, but avoid semantic drift unless there is a strong reason.

In short: modernize the binding technology, not the mathematical model.

## Provenance and Rights

This local snapshot comes from the historical upstream materials referenced by the UDBM project:

- UDBM wiki page: <https://github.com/UPPAALModelChecker/UDBM/wiki/Python-Binding>
- UDBM wiki history page: <https://github.com/UPPAALModelChecker/UDBM/wiki/Python-Binding/_history>
- historical documentation page: <https://homes.cs.aau.dk/~adavid/udbm/python.html>
- historical release archive: <https://homes.cs.aau.dk/~adavid/UDBM/ureleases/python_dbm-0.1.tar.gz>
- Launchpad project page: <https://launchpad.net/pydbm>

The source headers in `udbm.py`, `udbm_int.h`, and `udbm_int.i` attribute the Python binding code to Peter Bulychev and state:

- `Copyright 2011 Peter Bulychev`
- distribution under the GNU General Public License, version 3 or later

This repository does not claim authorship of the historical `srcpy2/` code. It is stored here as an upstream reference snapshot for compatibility and reconstruction work. Rights to the original work remain with the original authors and licensors. Please consult the original source headers and upstream project materials for the authoritative copyright and licensing terms.
