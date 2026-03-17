# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This thesis is one of the most directly useful long-form references for UDBM itself. It goes past the abstract timed-automata story and into DBM structures, operations, normalization, storage, and implementation tradeoffs.

If `by04` is the best compact tutorial, this thesis is the deeper implementation-oriented follow-up.

## Embedded paper layout

This entry now has two layers:

- thesis-level material in the root of `papers/bengtsson02/`, including the full [paper.pdf](./paper.pdf), the thesis-level guides, and the refined [content.md](./content.md)
- extracted second-level paper directories under `paper-a/` through `paper-e/`

The root thesis PDF remains the canonical full-text record in this repository. The child directories are convenience splits of the five embedded papers listed in the thesis itself. Each child directory now has a paper-level reading guide pair and a refined local reading artifact:

- `paper.pdf`
- `README.md`
- `README_zh.md`
- `content.md`
- `content_assets/` when figures or tables are needed

Current second-level mapping:

- [paper-a/README.md](./paper-a/README.md): `DBM: Structures, Operations and Implementation` (thesis pages 23-44)
- [paper-b/README.md](./paper-b/README.md): `Reachability Analysis of Timed Automata Containing Constraints on Clock Differences` (thesis pages 45-66)
- [paper-c/README.md](./paper-c/README.md): `Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems` (thesis pages 67-92)
- [paper-d/README.md](./paper-d/README.md): `Partial Order Reductions for Timed Systems` (thesis pages 93-114)
- [paper-e/README.md](./paper-e/README.md): `Automated Verification of an Audio-Control Protocol using UPPAAL` (thesis pages 115-143)

Use the root thesis when you need the introduction, the thesis-wide framing across all five papers, or the unified bibliography. Use the child directories when you want to read or reference one embedded paper in isolation.

## How The Five Embedded Papers Fit Together

The five embedded papers are not interchangeable. They form a fairly clear progression from DBM internals into broader state-space engineering and, finally, UPPAAL engine context.

- [paper-a/README.md](./paper-a/README.md) is the DBM-core entry point.
  It is the closest single embedded paper to `dbm.h` / `dbm.c`: representation, closure-oriented operations, primitive transformations, and implementation choices around raw DBMs.
- [paper-b/README.md](./paper-b/README.md) is the normalization follow-up.
  It explains what changes once symbolic reachability must preserve constraints on clock differences instead of only simpler upper-bound style constraints.
- [paper-c/README.md](./paper-c/README.md) is the memory and storage paper.
  It moves from single-DBM manipulation into passed-list growth, compact storage, and reduction strategies that later show up in `mingraph`-style machinery.
- [paper-d/README.md](./paper-d/README.md) is the local-time / partial-order paper.
  It is less about wrapper-surface DBM methods directly, and more about how symbolic timing structures behave inside a more aggressive exploration algorithm.
- [paper-e/README.md](./paper-e/README.md) is the committed-location / case-study paper.
  It shows how the modeling and exploration changes from paper-d pay off in a realistic UPPAAL verification setting rather than only in a synthetic algorithm discussion.

If you want the shortest implementation-facing path through the five embedded papers, read:

1. [paper-a/README.md](./paper-a/README.md)
2. [paper-b/README.md](./paper-b/README.md)
3. [paper-c/README.md](./paper-c/README.md)
4. [paper-d/README.md](./paper-d/README.md)
5. [paper-e/README.md](./paper-e/README.md)

That order starts with the DBM object itself, then adds normalization, then storage, and only afterwards moves up to search-order reduction and industrial tool context.

## What Each Embedded Paper Adds

### Paper A

Title:
`DBM: Structures, Operations and Implementation`

Repository value:

- best paper-level source here for the raw DBM operation vocabulary behind `up`, `down`, reset-like updates, closure, and relation checks
- especially useful when reading native DBM code and wanting an implementation-minded narrative instead of only a generic timed-automata explanation

### Paper B

Title:
`Reachability Analysis of Timed Automata Containing Constraints on Clock Differences`

Repository value:

- the most direct local explanation of why normalization becomes subtler once guards and invariants contain clock-difference constraints
- useful when reasoning about which symbolic simplifications remain sound and which require more care

### Paper C

Title:
`Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems`

Repository value:

- strongest embedded-paper link to compact storage, passed-list pressure, and `mingraph`-adjacent design
- useful when the question is not "how do we operate on one DBM?" but "how do we keep many symbolic states around efficiently?"

### Paper D

Title:
`Partial Order Reductions for Timed Systems`

Repository value:

- explains the local-time semantics and symbolic restructuring needed before partial-order reduction becomes practical for timed systems
- useful when you need to understand why reduction-friendly exploration can require changing the underlying symbolic view, not just adding a search heuristic on top

### Paper E

Title:
`Automated Verification of an Audio-Control Protocol using UPPAAL`

Repository value:

- shows committed locations and related exploration choices paying off on a real protocol instead of a minimal academic toy
- useful when you need a concrete UPPAAL case study explaining why modeling atomicity and avoiding unnecessary interleavings mattered in practice

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

Another practical rule of thumb:

- use papers A-C when the question is mainly "what does native UDBM do, and why?"
- use papers D-E when the question is mainly "what kind of model-checking engine pressures shaped those data structures and APIs?"
