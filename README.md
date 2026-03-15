# pyudbm (Python Wrapper for UPPAAL UDBM)

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/pyudbm)](https://pypi.org/project/pyudbm/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyudbm)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/pyudbm)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pyudbm)

![Loc](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/95404278cd0d7b2dd8128e17a4ffcf0b/raw/loc.json)
![Comments](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/95404278cd0d7b2dd8128e17a4ffcf0b/raw/comments.json)
[![codecov](https://codecov.io/gh/HansBug/pyudbm/graph/badge.svg)](https://codecov.io/gh/HansBug/pyudbm)
[![Documentation Status](https://readthedocs.org/projects/pyudbm/badge/?version=latest)](https://pyudbm.readthedocs.io/en/latest/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/HansBug/pyudbm)

[![Code Test](https://github.com/HansBug/pyudbm/workflows/Code%20Test/badge.svg)](https://github.com/HansBug/pyudbm/actions?query=workflow%3A%22Code+Test%22)
[![Badge Creation](https://github.com/HansBug/pyudbm/workflows/Badge%20Creation/badge.svg)](https://github.com/HansBug/pyudbm/actions?query=workflow%3A%22Badge+Creation%22)
[![Release Test](https://github.com/HansBug/pyudbm/workflows/Release%20Test/badge.svg)](https://github.com/HansBug/pyudbm/actions?query=workflow%3A%22Release+Test%22)
[![Release](https://github.com/HansBug/pyudbm/workflows/Release/badge.svg)](https://github.com/HansBug/pyudbm/actions?query=workflow%3A%22Release%22)

[![GitHub stars](https://img.shields.io/github/stars/HansBug/pyudbm)](https://github.com/HansBug/pyudbm/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/HansBug/pyudbm)](https://github.com/HansBug/pyudbm/network)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/HansBug/pyudbm)
[![GitHub issues](https://img.shields.io/github/issues/HansBug/pyudbm)](https://github.com/HansBug/pyudbm/issues)
[![GitHub pulls](https://img.shields.io/github/issues-pr/HansBug/pyudbm)](https://github.com/HansBug/pyudbm/pulls)
[![Contributors](https://img.shields.io/github/contributors/HansBug/pyudbm)](https://github.com/HansBug/pyudbm/graphs/contributors)
[![GitHub license](https://img.shields.io/github/license/HansBug/pyudbm)](https://github.com/HansBug/pyudbm/blob/main/LICENSE)

</div>

---

**pyudbm** is a compatibility-minded Python wrapper around the UPPAAL
**UDBM** library. The project is rebuilding the historical high-level Python
binding around **Context / Clock / Federation** on top of a modern
**pybind11 + CMake + setuptools** stack, while keeping the core semantics in
the upstream native library instead of reimplementing DBM algorithms in pure
Python.

The current repository already exposes a restored high-level API, native-backed
federation operations, and valuation-based containment checks. At the same
time, the project is still **work in progress** and should not yet be treated
as a finalized, frozen public API.

## Table of Contents

- [Core Features](#core-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Build From Source](#build-from-source)
- [Project Status](#project-status)
- [Documentation](#documentation)
- [Upstream and References](#upstream-and-references)
- [License](#license)

## Core Features

pyudbm aims to restore the old UDBM Python experience without drifting away
from upstream behavior. The current repository direction focuses on the
following:

| Feature | Description | Why it matters |
|:--|:--|:--|
| **Historical-style API** | Rebuilds the classic `Context`, `Clock`, and `Federation` programming model. | Keeps old modeling style recognizable and ergonomic. |
| **Natural constraint syntax** | Uses Python operators such as `c.x < 10` and `c.x - c.y <= 1` to construct zones. | Makes timed constraints concise and readable. |
| **Native federation operations** | Delegates DBM and federation behavior to vendored upstream `UDBM` and `UUtils`. | Keeps semantics thin and close to upstream instead of inventing a Python-only reimplementation. |
| **Valuation support** | Supports `IntValuation` and `FloatValuation` for containment checks. | Covers a key part of the historical binding workflow. |
| **Compatibility-oriented semantics** | Restores methods such as `up`, `down`, `setZero`, `setInit`, `freeClock`, `predt`, `convexHull`, and `reduce`. | Preserves familiar high-level operations expected by older users. |
| **Cross-platform packaging direction** | Targets CPython 3.7 through 3.14 on Linux, macOS, and Windows. | Aligns the wrapper with practical end-user distribution via wheels. |

## Installation

### Basic Installation

If a wheel is available for your platform, install `pyudbm` from PyPI:

```shell
pip install pyudbm
```

You can verify the installation with:

```shell
python -c "import pyudbm; print(pyudbm.__version__)"
```

### Install the Latest Main Branch

If you want the newest repository state before the next release:

```shell
pip install -U git+https://github.com/HansBug/pyudbm@main
```

### Development Installation

For repository development, start from a full checkout with submodules:

```shell
git clone https://github.com/HansBug/pyudbm.git
cd pyudbm
git submodule update --init --recursive

python -m venv venv
source venv/bin/activate

python -m pip install -U pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -r requirements-test.txt
python -m pip install -r requirements-build.txt
```

## Quick Start

### 1. Build Zones with the High-Level API

```python
from pyudbm import Context

c = Context(["x", "y"], name="c")

zone = (c.x < 10) & (c.x - c.y <= 1)
other = (c.x <= 20)

assert zone <= other
print(zone)
```

### 2. Check Containment with Valuations

```python
from pyudbm import Context, IntValuation

c = Context(["x", "y"], name="c")
zone = (c.x < 10) & (c.x - c.y <= 1)

valuation = IntValuation(c)
valuation["x"] = 3
valuation["y"] = 2

assert zone.contains(valuation)
```

### 3. Apply Common Federation Operations

```python
from pyudbm import Context

c = Context(["x", "y"], name="c")
zone = (c.x >= 1) & (c.x <= 2) & (c.y >= 1) & (c.y <= 2)

future_zone = zone.up()
past_zone = zone.down()
reset_zone = zone.resetValue(c.x)
free_y_zone = zone.freeClock(c.y)
```

The package root re-exports the restored high-level API, so users can import
directly from `pyudbm` without going through lower-level helper modules.

## Build From Source

For local source builds, the repository-level `make` flow is currently the most
reliable path because it keeps `UUtils`, `UDBM`, and the Python extension in
sync:

```shell
make bin
make build
make unittest RANGE_DIR=binding
```

If you changed native-integration logic, a fuller rebuild is safer:

```shell
make bin_clean
make bin
make build
make unittest
```

## Project Status

The project is intentionally described as **unfinished**:

- The wrapper is restoring legacy semantics incrementally rather than declaring
  a fully complete API up front.
- The historical Python binding preserved under `srcpy2/` is still an important
  behavior reference.
- The current direction is to keep the wrapper thin and faithful to upstream
  `UDBM`, not to turn this repository into a separate DBM implementation.

What is already in place:

- A public high-level API exported from `pyudbm`
- Native-backed federation construction and set operations
- Integer and floating-point valuations
- Cross-platform build and wheel workflows
- Read the Docs based documentation build integration

## Documentation

- Documentation site: https://pyudbm.readthedocs.io/en/latest/
- Installation guide: https://pyudbm.readthedocs.io/en/latest/tutorials/installation/index.html
- API reference: https://pyudbm.readthedocs.io/en/latest/

## Upstream and References

- Repository: https://github.com/HansBug/pyudbm
- UDBM upstream: https://github.com/UPPAALModelChecker/UDBM
- UUtils upstream: https://github.com/UPPAALModelChecker/UUtils
- Historical UDBM Python binding notes: https://github.com/UPPAALModelChecker/UDBM/wiki/Python-Binding

## License

This repository is distributed under the GPL-3.0 license. See
[LICENSE](LICENSE) for details.
