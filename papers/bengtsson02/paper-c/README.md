# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper C from the parent thesis [Clocks, DBMs and States in Timed Systems](../README.md).

It corresponds to thesis pages 67-92 and focuses on reducing memory usage in symbolic state-space exploration.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis lists this embedded paper as:

`Johan Bengtsson and Wang Yi. Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems. Technical Report 2001-009, Department of Information Technology, Uppsala University, 2001.`

## What to extract while reading

Focus on:

- packed symbolic-state representations
- compressed zone storage with cheap inclusion checks
- WAIT versus PASSED tradeoffs
- supertrace and hash-compaction ideas for timed systems

For this repository, the key reading question is:

"How should a timed-symbolic engine balance exactness, inclusion-check cost, and memory footprint once state-space size becomes the dominant constraint?"

## Where it maps into this repository

- Compact storage machinery: `UDBM/include/dbm/mingraph.h`
- Minimal-graph encoding implementation: `UDBM/src/mingraph_write.c`
- The wrapper-facing high-level API that ultimately sits on top of these native choices: `pyudbm/binding/udbm.py`

Concrete correspondences:

- it explains why state representation cost matters beyond a single DBM operation
- it gives context for memory-oriented reductions and compressed storage formats
- it clarifies why fast inclusion checks and compact state storage are often competing goals

## Why it matters for UDBM specifically

This paper is less about user-facing syntax and more about the cost model of a real verifier.

If you are trying to understand why UDBM contains compact-storage machinery and why verification engines care so much about representation shape, this is the relevant paper-level reference.

## How to read it

Read this after [paper-a/README.md](../paper-a/README.md) if your question is about memory footprint, compressed representations, or passed-list engineering.

If you are instead moving upward into UPPAAL engine semantics, continue with [paper-d/README.md](../paper-d/README.md) and [paper-e/README.md](../paper-e/README.md).
