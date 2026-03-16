# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This is the primary entry point for the whole set and one of the best single tutorial references if you want semantics, symbolic algorithms, and DBM mechanics in one place.

It gives the semantic and symbolic-zone baseline for this repository while also serving as the compact bridge to the deeper implementation-oriented treatment in `bengtsson02`.

## What to extract while reading

Focus on:

- the concrete and abstract semantics of timed automata
- the transition from regions to zones
- canonical DBM representation and core DBM operations
- normalization for termination
- the appendix-level algorithm descriptions

For UDBM, the key reading question is:

"What exact symbolic operations on zones does a timed-automata tool need, and how are they realized with DBMs?"

## Where it maps into this repository

- Native DBM operations: `UDBM/include/dbm/dbm.h`
- Federation-level symbolic operations: `UDBM/include/dbm/fed.h`
- High-level Python compatibility layer: `pyudbm/binding/udbm.py`
- Tests covering restored legacy semantics: `test/binding/test_api.py`

Concrete correspondences:

- canonical closure of zones explains why DBM operations maintain a normalized internal form
- symbolic operations correspond to `up`, `down`, `updateValue`, `freeClock`, `contains`, and emptiness tests
- normalization discussion explains why extrapolation / bounded abstraction operations exist in the public surface

## Why it matters for UDBM specifically

This chapter is close to the center of gravity of the library. It explains not only what a DBM is, but what a verification tool repeatedly needs to do with DBMs in practice.

That makes it a particularly good paper to read when you are deciding whether a wrapper method belongs in the public API or whether an operation is only an internal helper.

## How to read it

Read it first if you want the clearest single paper on what UDBM is supposed to manipulate.

If you only have time for one "practical theory" refresher before touching UDBM code, this is a strong candidate.
