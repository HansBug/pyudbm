# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper C from the parent thesis [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md).

It corresponds to root PDF pages 99-114 and focuses on Clock Difference Diagrams (CDDs) as a compact representation of finite unions of zones.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis summary describes this paper as:

`Efficient Timed Reachability Analysis using Clock Difference Diagrams`

Publication history noted in the thesis:

- appears as `BRICS Report Series RS-98-47`, December 1998
- presented at `CAV'99` and published in `LNCS 1633`

## What to extract while reading

Focus on:

- the CDD data structure itself
- boolean set operations on CDDs
- encoding zones as CDDs and checking inclusion of a zone in a CDD
- using CDDs to compress the passed set during timed reachability analysis
- the paper's fully symbolic direction beyond a DBM-only passed list

For this repository, the key reading question is:

"What does a first-class representation for finite unions of zones buy us beyond keeping a list of DBMs?"

## Where it maps into this repository

- Federation type and operations: `UDBM/include/dbm/fed.h`
- Federation implementation: `UDBM/src/fed.cpp`
- Priced federation type: `UDBM/include/dbm/pfed.h`
- High-level Python `Federation` wrapper: `pyudbm/binding/udbm.py`

Concrete correspondences:

- the paper gives the best local explanation here for why non-convex symbolic sets are worth representing explicitly
- it offers a CDD-based alternative to DBM lists, which is important architectural context even though current UDBM uses federation-based machinery instead
- it directly connects symbolic-state storage pressure to representation choice

## Why it matters for UDBM specifically

This is the first paper in the thesis that becomes directly relevant to UDBM-style data-structure questions.

If you need a repository-local paper explaining why "one DBM per symbolic state" is often not enough, start here.

## How to read it

Read this first among the six extracted papers if your question is about non-convex symbolic sets, CDDs, federation-like objects, or symbolic-state compaction.

If your next concern is cost-optimal reachability, continue with [paper-d/README.md](../paper-d/README.md).
