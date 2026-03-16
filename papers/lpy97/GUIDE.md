# Reading Guide

## Position in the stack

This is the short tool-overview paper for early UPPAAL. It is less about proving new DBM theorems and more about explaining the overall toolbox, its design criteria, and the workflow it supports.

Read it when you want to understand the user-facing environment in which UDBM's symbolic operations were meant to live.

## What to extract while reading

Focus on:

- the design criteria of efficiency and ease of use
- the split between description language, simulator, and model checker
- reachability-oriented symbolic verification based on constraints
- diagnostic traces and interactive modeling support

For this repository, the key reading question is:

"What sort of tool usage pattern should a high-level wrapper support if it wants to feel native to the historical UDBM / UPPAAL world?"

## Where it maps into this repository

- High-level Python DSL and legacy-style user surface: `pyudbm/binding/udbm.py`
- Package-root compatibility exports: `pyudbm/__init__.py`
- Native symbolic engine underneath the tooling story: `UDBM/include/dbm/dbm.h`, `UDBM/include/dbm/fed.h`
- Restored public behavior tests: `test/binding/test_api.py`

Concrete correspondences:

- the paper's emphasis on user-oriented modeling helps justify `Context`, `Clock`, and `Federation` as first-class Python objects
- the constraint-solving reachability story explains why symbolic operations dominate the wrapped API surface
- diagnostic and simulator concerns explain why readable high-level expressions matter even when the core engine is low-level

## Why it matters for UDBM specifically

This paper is useful because it keeps the wrapper effort honest: UDBM exists in a tool ecosystem shaped by human modeling workflows, not only by internal algorithms.

That matters for this repository because recreating the historical binding is partly about restoring the right usability layer, not only the native calls.

## How to read it

Read this as a concise orientation before `bdl04` if you want the short version of the UPPAAL toolbox story.

It is not the main paper for DBM internals; use it to understand the surrounding tool design and the intended style of interaction.
