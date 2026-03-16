# Reading Guide

## Position in the stack

This is a mature UPPAAL tutorial from the tool-user side. It is not the paper to read for DBM internals first, but it is very useful once you want to understand what kind of modeling style the symbolic engine is serving.

Compared with `lpy97`, this paper is broader on modeling features and much richer on practical modeling patterns.

## What to extract while reading

Focus on:

- the specific timed-automata dialect used by UPPAAL
- invariants, urgency, committed locations, and synchronization channels
- the reachability-oriented query language
- the modeling patterns that keep verification practical

For this repository, the key reading question is:

"What kind of user-facing modeling experience should a high-level UDBM wrapper make natural?"

## Where it maps into this repository

- Legacy-style high-level API: `pyudbm/binding/udbm.py`
- Historical compatibility reference: `srcpy2/udbm.py`
- Native symbolic operations underneath the tool-facing model: `UDBM/include/dbm/dbm.h`, `UDBM/include/dbm/fed.h`

Concrete correspondences:

- natural clock expressions map to `Context`, `Clock`, and `Constraint`
- symbolic zone updates map to `Federation.up()`, `Federation.down()`, `Federation.updateValue(...)`, and `Federation.freeClock(...)`
- non-convex symbolic sets map to `Federation` instead of a single DBM

## Why it matters for UDBM specifically

This paper is useful as a product-direction reminder. End users do not think in terms of raw matrices. They think in terms of clocks, guards, resets, urgency, and reachable symbolic states.

That is exactly why this repository should keep rebuilding the historical `Context` / `Clock` / `Federation` programming model rather than stopping at low-level bindings.

## How to read it

Read this after `lpy97` or `by04`. Use it when you are making decisions about Python ergonomics, examples, or what should count as a natural high-level API for UDBM-backed modeling.

Do not use it as the main source for DBM algorithms. For that, read `by04` and `bengtsson02`.
