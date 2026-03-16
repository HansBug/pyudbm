# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This is the most direct theory paper for the part of UDBM that `by04` does not really explain: subtraction on DBMs and the resulting need for federations.

If your question is "why does UDBM have `fed_t` and `Federation.__sub__` at all?", start here.

## What to extract while reading

Focus on:

- subtraction of one convex zone from another can be non-convex
- therefore a single DBM is not enough as a target representation
- a federation is a finite union of DBMs used to represent that result
- a useful subtraction algorithm should try to keep the result small and preferably disjoint

For UDBM, the key question is:

"How do we stay inside DBM-based technology after subtraction leaves the convex world?"

## Where it maps into this repository

- Federation interface: `UDBM/include/dbm/fed.h`
- Federation algorithms: `UDBM/src/fed.cpp`
- High-level Python API: `pyudbm/binding/udbm.py`
- Legacy compatibility API: `srcpy2/udbm.py`
- Tests of federation-level operations: `test/binding/test_api.py`

Concrete correspondences:

- `fed_t::operator-=`
- `fed_t::subtractDown(...)`
- `fed_t::reduce()`
- `fed_t::expensiveReduce()`
- `fed_t::mergeReduce(...)`
- `fed_t::convexReduce()`
- `Federation.__sub__`
- `Federation.reduce(...)`
- `Federation.predt(...)`

## Why it matters for UDBM specifically

This paper is the missing link between "DBMs represent convex zones" and "UDBM manipulates non-convex sets using unions of DBMs".

It is the strongest single paper-level justification for:

- the existence of `fed_t`
- subtraction as a federation-only operation
- post-subtraction simplification and reduction heuristics

## How to read it

Read this after `by04`. If your main interest is the historical Python API, compare the paper directly with the methods exposed on `Federation` in `pyudbm/binding/udbm.py`.
