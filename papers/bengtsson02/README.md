# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This thesis is one of the most directly useful long-form references for UDBM itself. It goes past the abstract timed-automata story and into DBM structures, operations, normalization, storage, and implementation tradeoffs.

If `by04` is the best compact tutorial, this thesis is the deeper implementation-oriented follow-up.

## Embedded paper layout

This entry now has two layers:

- thesis-level material in the root of `papers/bengtsson02/`, including the full [paper.pdf](./paper.pdf), the thesis-level guides, and the refined [content.md](./content.md)
- extracted second-level paper directories under `paper-a/` through `paper-e/`

The root thesis PDF remains the canonical full-text record in this repository. The child directories are convenience splits of the five embedded papers listed in the thesis itself. Each child directory currently contains:

- `paper.pdf`
- `README.md`
- `README_zh.md`

Current second-level mapping:

- [paper-a/README.md](./paper-a/README.md): `DBM: Structures, Operations and Implementation` (thesis pages 23-44)
- [paper-b/README.md](./paper-b/README.md): `Reachability Analysis of Timed Automata Containing Constraints on Clock Differences` (thesis pages 45-66)
- [paper-c/README.md](./paper-c/README.md): `Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems` (thesis pages 67-92)
- [paper-d/README.md](./paper-d/README.md): `Partial Order Reductions for Timed Systems` (thesis pages 93-114)
- [paper-e/README.md](./paper-e/README.md): `Automated Verification of an Audio-Control Protocol using UPPAAL` (thesis pages 115-143)

Use the root thesis when you need the introduction, the thesis-wide framing across all five papers, or the unified bibliography. Use the child directories when you want to read or reference one embedded paper in isolation.

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

Read it selectively. Start with the thesis introduction if you need the author-level framing, then move into the extracted papers according to topic.

A practical repository-oriented path is:

- [paper-a/README.md](./paper-a/README.md) for DBM data structures and primitive operations
- [paper-b/README.md](./paper-b/README.md) for normalization with clock-difference constraints
- [paper-c/README.md](./paper-c/README.md) for compression, WAIT / PASSED tradeoffs, and memory reduction

The later papers are still useful, but they are more UPPAAL-engine context than direct wrapper surface:

- [paper-d/README.md](./paper-d/README.md) for local-time semantics and partial-order reduction
- [paper-e/README.md](./paper-e/README.md) for committed locations and the industrial audio-control case study
