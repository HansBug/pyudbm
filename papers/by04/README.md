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

## What the local refined content now gives you

The local `content.md` for this paper is no longer just a rough excerpt. It now gives you a fairly complete, GitHub-readable version of the chapter with most of the material that is directly useful for this repository:

- Section 2 covers the timed-automata baseline: syntax, operational semantics, and verification problems such as reachability, language questions, and bisimulation
- Section 3 covers symbolic semantics in detail, including regions, zone graphs, infinite zone graphs, and why normalization is required to recover finiteness
- the normalization story is split the same way as the chapter itself: first automata without difference constraints, then automata with them
- Section 4 is the dense DBM part: DBM basics, graph interpretations, canonical closure, minimal forms, property checking, transformations, normalization, and memory layout
- Section 5 keeps the UPPAAL context instead of dropping it, so you also get the modeling view, product-automaton intuition, query forms, and the architecture pipeline
- the appendix pseudo-code has been preserved, which makes this one of the most implementation-relevant local reading artifacts in the whole `papers/` tree

If you are reading with wrapper work in mind, the appendix is especially valuable because it names the operation vocabulary almost one-to-one with the public surface that a compatibility-minded Python layer tends to need.

## Suggested reading route inside the paper

If you do not want to read the whole chapter linearly, a good repository-oriented route is:

1. read Section 3 first to re-establish the symbolic-state viewpoint
2. then read Section 4 for the actual DBM machinery and operations
3. then skim Section 5 so you do not lose the tool-level perspective
4. finally return to the appendix algorithms when you need implementation-level detail

This route mirrors how the wrapper itself is layered: symbolic semantics first, DBM operations second, tool-facing API expectations third.

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

It is also unusually useful because it does not stop at the abstract semantics level. It connects the semantic side, the algorithm side, and the data-structure side in one continuous text, which is exactly the combination a wrapper project needs when it tries to stay thin without becoming semantically blind.

## How to read it

Read it first if you want the clearest single paper on what UDBM is supposed to manipulate.

If you only have time for one "practical theory" refresher before touching UDBM code, this is a strong candidate.
