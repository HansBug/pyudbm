# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This thesis is broader than the rest of the papers in this set. It is not the best first paper if you only want one narrow result, but it is extremely useful once you want the larger UPPAAL data-structure picture around federations, CDDs, storage, sharing, and priced zones.

Think of it as the system-level bridge between individual algorithms and tool architecture.

## What to extract while reading

Do not read the thesis cover to cover unless you want the full historical arc. For UDBM-related work, focus on:

- the chapters and papers on CDDs
- the discussion of unions of zones, symbolic-state storage, and coverage
- the engineering motivation for sharing and compact symbolic representations

The most useful conceptual point is that finite unions of zones are a real semantic and algorithmic object in UPPAAL-style verification, not an accidental wrapper artifact.

## Where it maps into this repository

- Federation type and operations: `UDBM/include/dbm/fed.h`
- Federation implementation: `UDBM/src/fed.cpp`
- Priced federation type: `UDBM/include/dbm/pfed.h`
- Partitioning support for federation reduction: `UDBM/include/dbm/partition.h`, `UDBM/src/partition.cpp`
- High-level Python `Federation` wrapper: `pyudbm/binding/udbm.py`

Concrete correspondences:

- the thesis discussion of unions of zones helps explain why `fed_t` is a separate type
- the storage and sharing discussion helps explain `intern()`, hashing, and compact representations
- the broader symbolic-state perspective helps explain why UDBM contains both explicit federation support and compressed DBM support

## Why it matters for UDBM specifically

This thesis is not the direct source for every concrete API, but it gives the architectural reason why UDBM grew beyond "just DBM helper functions".

It is especially helpful if you want to understand:

- why non-convex symbolic sets keep showing up
- why CDDs were explored as an alternative to DBM lists
- why priced extensions exist alongside ordinary federations

## How to read it

Use this thesis as a selective deep reference, not as the first document in the chain. It works best after `by04` and after you already know that `fed_t`, `mingraph`, and extrapolation exist.
