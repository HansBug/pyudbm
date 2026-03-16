# Papers Guide

This directory collects the theory papers that are most useful for understanding why UDBM looks the way it does.

## Recommended reading order

1. `ta_tools`
   This is the semantic and DBM baseline. Read it first.
2. `llpy97`
   This adds minimal-graph storage and compact DBM representation.
3. `bblp04`
   This explains extrapolation and abstraction for termination.
4. `dhlp06`
   This explains why subtraction leaves the convex world and why federations are needed.
5. `behrmann03`
   This is the broad synthesis: unions of zones, CDDs, sharing, and the larger UPPAAL architecture.

If you want the shortest path to the part missing from `ta_tools`, jump from `ta_tools` directly to `dhlp06`, then come back to `llpy97` and `bblp04`.

## What each paper contributes

### `ta_tools`

Role:
foundation for timed automata semantics, zones, DBMs, and basic symbolic algorithms.

Main UDBM support:

- the meaning of a convex zone
- the canonical DBM view
- core operations such as delay, past, reset, and guard intersection

Repository anchors:

- `pyudbm/binding/udbm.py`
- `UDBM/include/dbm/dbm.h`
- `test/binding/test_api.py`

### `llpy97`

Role:
minimal graph and compact storage of DBMs.

Main UDBM support:

- why `mingraph` exists
- why canonical DBMs are not always the best stored form

Repository anchors:

- `UDBM/include/dbm/mingraph.h`
- `UDBM/src/mingraph_write.c`

Note:
this directory now includes a readable PDF recovered from the archived historical author-hosted copy.

### `bblp04`

Role:
lower/upper-bound abstractions for zone-based verification.

Main UDBM support:

- why extrapolation is sound
- why extrapolation can force termination
- why multiple extrapolation schemes exist

Repository anchors:

- `UDBM/include/dbm/dbm.h`
- `pyudbm/binding/udbm.py`

### `dhlp06`

Role:
DBM subtraction and the direct theoretical motivation for federations.

Main UDBM support:

- subtraction on zones
- non-convex results
- unions of DBMs as the result domain
- reduction after subtraction

Repository anchors:

- `UDBM/include/dbm/fed.h`
- `UDBM/src/fed.cpp`
- `pyudbm/binding/udbm.py`
- `srcpy2/udbm.py`

### `behrmann03`

Role:
system-level synthesis across symbolic data structures used around UPPAAL.

Main UDBM support:

- why unions of zones are important at the tool level
- why CDDs were explored as an alternative
- why sharing, storage layout, and priced extensions matter

Repository anchors:

- `UDBM/include/dbm/fed.h`
- `UDBM/include/dbm/pfed.h`
- `UDBM/include/dbm/partition.h`
- `UDBM/src/partition.cpp`

## How this maps to the Python wrapper work in this repository

The restored Python API in `pyudbm/binding/udbm.py` is not just wrapping raw matrix primitives. It is trying to reconstruct the historical `Context` / `Clock` / `Federation` model on top of UDBM.

That means:

- `ta_tools` explains the basic symbolic zone layer that the DSL manipulates
- `dhlp06` explains why `Federation` must remain a real union-based object instead of collapsing to one DBM
- `bblp04` explains why methods like `extrapolateMaxBounds` belong in the public surface
- `llpy97` explains the compressed-storage machinery already present in native UDBM
- `behrmann03` explains the broader architectural direction behind these choices

## Practical advice

If you are reading for implementation work in this repository:

- start with `ta_tools/GUIDE.md`
- then read `dhlp06/GUIDE.md`
- then read `bblp04/GUIDE.md`
- use `llpy97/GUIDE.md` when touching `mingraph`
- use `behrmann03/GUIDE.md` when you need the larger UPPAAL context
