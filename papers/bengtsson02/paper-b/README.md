# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper B from the parent thesis [Clocks, DBMs and States in Timed Systems](../README.md).

It corresponds to thesis pages 45-66 and focuses on reachability analysis when timed automata contain constraints on clock differences.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis lists this embedded paper as:

`Johan Bengtsson and Wang Yi. Reachability Analysis of Timed Automata Containing Constraints on Clock Differences. Submitted for publication.`

## What to extract while reading

Focus on:

- why older normalization schemes break or become unsound with difference constraints
- the refinement needed beyond ordinary maximal-clock normalization
- the two new normalization algorithms and their tradeoffs
- the implementation claim that support for difference constraints need not be prohibitively expensive

For this repository, the key reading question is:

"What must a DBM library do differently once clock-difference guards are treated as first-class input rather than as an unsupported corner case?"

## Where it maps into this repository

- DBM normalization and related operations: `UDBM/include/dbm/dbm.h`
- High-level semantics exposed through the wrapper: `pyudbm/binding/udbm.py`
- Compatibility-driven tests for zone behavior: `test/binding/test_api.py`

Concrete correspondences:

- it explains why support for constraints such as `x - y <= c` is not a small parser detail
- it gives the theory reason that normalization logic must stay aligned with difference constraints
- it is the closest paper-level explanation for why extrapolation-like behavior cannot ignore diagonal information

## Why it matters for UDBM specifically

This is the normalization paper to read before making any claim that a timed-automata tool "supports difference constraints."

If a wrapper or binding exposes expressive clock comparisons, this paper is the main local source for the correctness burden behind that surface.

## How to read it

Read this after [paper-a/README.md](../paper-a/README.md) if your task involves expressive clock guards, diagonal constraints, or normalization behavior.

If your next concern is storage and memory cost rather than correctness of normalization, continue with [paper-c/README.md](../paper-c/README.md).
