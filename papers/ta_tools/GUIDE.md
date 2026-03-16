# Reading Guide

## Position in the stack

This paper is the entry point for the whole set. It gives the semantic and algorithmic baseline for timed automata, zones, and DBMs. Read it first if you want a clean model of what UDBM is supposed to manipulate.

What it covers well:

- timed automata semantics
- symbolic semantics via zones
- convex zones represented by DBMs
- core operations on zones and DBMs
- normalization for termination

What it does not cover deeply enough for UDBM:

- federations as a first-class non-convex representation
- DBM subtraction as a main algorithmic topic
- minimal graph compression as a standalone data structure topic
- LU-bound abstractions as a focused theory

## What to extract while reading

Focus on Sections 2 to 4. The key result is not a single theorem, but the modeling shift:

- a symbolic state is represented by a location plus a zone
- a convex zone can be stored canonically as a DBM
- verification algorithms are built from `up`, `down`, reset, guard intersection, and normalization

That is the exact conceptual layer underneath UDBM's basic DBM operations.

## Where it maps into this repository

- High-level Python DSL for clocks, constraints, and federations: `pyudbm/binding/udbm.py`
- Native DBM operations and extrapolation hooks: `UDBM/include/dbm/dbm.h`
- Legacy compatibility surface: `srcpy2/udbm.py`
- Binding-level behavior checks: `test/binding/test_api.py`

Concrete correspondences:

- clock constraints and clock differences map to `Clock`, `VariableDifference`, and `Constraint`
- symbolic zone operations map to `Federation.up()`, `Federation.down()`, `Federation.updateValue()`, `Federation.freeClock()`, `Federation.setZero()`, and `Federation.setInit()`
- convex approximation maps to `Federation.convexHull()`

## How to read it for UDBM work

Read this paper as the answer to: "What is a single DBM supposed to mean?"

Do not read it as the answer to:

- why `fed_t` exists
- why subtraction returns unions
- why `mergeReduce` and `expensiveReduce` matter
- why minimal graph storage exists

Those questions are answered by the later papers.
