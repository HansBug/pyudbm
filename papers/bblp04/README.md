# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This is the paper to read when you want to understand why UDBM exposes extrapolation operations at all, and why they come in `max-bounds`, `LU-bounds`, and diagonal variants.

It is the cleanest theory source in this set for abstraction-based termination in zone exploration.

## What to extract while reading

Focus on:

- why plain zone exploration may not terminate
- why abstraction by lower and upper bounds preserves the verification objective
- how the abstraction is parameterized by per-clock constants
- why different extrapolation schemes trade precision for convergence

For UDBM, the key question is:

"What exactly is being forgotten by extrapolation, and why is that safe?"

## Where it maps into this repository

- Low-level extrapolation functions: `UDBM/include/dbm/dbm.h`
- High-level Python wrapper: `pyudbm/binding/udbm.py`
- Tests exercising the restored legacy behavior: `test/binding/test_api.py`

Concrete correspondences:

- `dbm_extrapolateMaxBounds(...)`
- `dbm_diagonalExtrapolateMaxBounds(...)`
- `dbm_extrapolateLUBounds(...)`
- `dbm_diagonalExtrapolateLUBounds(...)`
- `Federation.extrapolateMaxBounds(...)`

## Why it matters for UDBM specifically

Without this paper, extrapolation methods look like opaque performance switches. With this paper, they become semantic abstractions with a correctness story.

That matters because UDBM is not only a container of DBM operations; it is part of the symbolic-state termination machinery used by UPPAAL-style verification.

## How to read it

Read this paper after `by04`. If your immediate concern is the Python API, read the abstraction definitions first, then compare them with the wrapper method `Federation.extrapolateMaxBounds(...)` and the native declarations in `dbm.h`.
