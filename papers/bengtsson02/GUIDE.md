# Reading Guide

## Position in the stack

This thesis is one of the most directly useful long-form references for UDBM itself. It goes past the abstract timed-automata story and into DBM structures, operations, normalization, storage, and implementation tradeoffs.

If `by04` is the best compact tutorial, this thesis is the deeper implementation-oriented follow-up.

## What to extract while reading

Do not treat the whole thesis as equally relevant. For UDBM work, focus on:

- the DBM data structure and canonical representation
- the full set of DBM operations needed in symbolic exploration
- normalization algorithms, especially for automata with clock-difference constraints
- compression and state-storage techniques

For this repository, the key reading question is:

"Which implementation choices in UDBM are theory-backed algorithmic decisions rather than arbitrary library engineering?"

## Where it maps into this repository

- Core DBM API: `UDBM/include/dbm/dbm.h`
- Federation and higher-level symbolic set support: `UDBM/include/dbm/fed.h`
- Compact storage machinery: `UDBM/include/dbm/mingraph.h`, `UDBM/src/mingraph_write.c`
- High-level wrapper exposing legacy operations: `pyudbm/binding/udbm.py`
- Restored legacy behavior tests: `test/binding/test_api.py`

Concrete correspondences:

- DBM operations in the thesis line up with `up`, `down`, `updateValue`, `freeClock`, and emptiness / containment checks
- normalization work helps explain extrapolation-style public operations in `dbm.h` and the wrapper
- compression work helps explain `mingraph`, hashing, and storage-oriented code paths already present in UDBM

## Why it matters for UDBM specifically

This thesis is unusually close to what UDBM actually is: a production-oriented symbolic timing library shaped by verification-tool constraints.

It is especially useful when you need to defend why the library exposes a certain operation, keeps canonical closure, or contains storage and compression machinery that might otherwise look like internal optimization clutter.

## How to read it

Read it selectively. Start with the DBM and normalization chapters, then read the storage / compression parts if you are touching `mingraph`, hashing, or representation issues.

The later sections on partial-order reduction and committed locations are valuable UPPAAL context, but they are less directly about the wrapper surface in this repository.
