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

## What the local refined content now gives you

The local `content.md` already captures substantially more than the headline claim "subtraction may be non-convex":

- the introduction keeps the concrete priority example that shows exactly how non-convexity appears in reachable sets
- the preliminaries restate clock constraints, DBMs, zone operations, and the naive subtraction construction in a form that is easy to map onto code
- the timed-automata-with-priorities section preserves both the concrete and symbolic semantics, so the paper does not float free from the model-checking use case
- the subtraction chapter includes the basic algorithm, minimal-constraint improvement, disjoint subtraction, and the simple early-stop cases
- the heuristic chapter keeps both the efficient heuristic and the more expensive facet-aware one
- the experimental section is present as well, including the Fischer example and the timed-game / job-shop tables, so you can see why the subtraction details matter for performance and reduction rather than only for theory

That combination makes the local reading version especially useful when you need to explain not just why federations exist, but why different reduction and subtraction strategies exist inside them.

## Suggested reading route inside the paper

For repository work, a practical reading order is:

1. read the introduction and the running priority example first
2. then read Section 4 directly for the subtraction mechanics
3. continue into Section 5 to understand why ordering heuristics and reduction quality matter
4. only then return to Section 3 if you need to reconnect the subtraction machinery to the full symbolic-semantics story

This order works well when your real target is federation behavior in code rather than the formal presentation order of the paper.

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

It is also where the theoretical story starts to look recognizably like concrete API design pressure. Once you read the paper's subtraction cases and heuristics together with the experiments, methods such as subtraction, reduction, expensive reduction, and merge-style cleanup stop looking like optional convenience features and start looking like part of the semantic cost of representing non-convex results faithfully.

## How to read it

Read this after `by04`. If your main interest is the historical Python API, compare the paper directly with the methods exposed on `Federation` in `pyudbm/binding/udbm.py`.
