# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper F from the parent thesis [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md).

It corresponds to root PDF pages 163-193 and focuses on priced zones and efficient cost-optimal reachability for linearly priced timed automata.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis summary describes this paper as:

`As Cheap as Possible: Efficient Cost-Optimal Reachability for Priced Timed Automata`

Publication history noted in the thesis:

- short version presented at `CAV'01` and published in `LNCS 2102`
- the thesis embeds the extended paper-level version used here

## What to extract while reading

Focus on:

- priced zones as the main symbolic object
- facets of zones and why they are needed for operations on priced zones
- lifting ordinary zone-based timed reachability machinery to the linear-price setting
- the practical algorithmic step from theory-heavy priced regions to implementation-friendlier symbolic objects

For this repository, the key reading question is:

"How does the classic zone toolchain get extended so that optimal-cost reachability becomes a natural symbolic operation rather than a separate theory layer?"

## Where it maps into this repository

- Federation type and operations: `UDBM/include/dbm/fed.h`
- Priced federation type: `UDBM/include/dbm/pfed.h`
- Partition-oriented reduction support: `UDBM/include/dbm/partition.h`
- High-level wrapper surface: `pyudbm/binding/udbm.py`

Concrete correspondences:

- this is the strongest thesis-local paper for priced symbolic structures that still feel close to classic zone machinery
- it is the best local paper here when you need to connect priced reachability to operations on zone-like objects rather than to pure region theory

## Why it matters for UDBM specifically

Among the six extracted papers, this is the one that feels closest to a priced extension of the DBM / zone style of tooling.

If you are touching priced zones, priced federations, or cost-annotated symbolic states, this is usually the highest-value paper in the set.

## How to read it

Read this after [paper-d/README.md](../paper-d/README.md) and [paper-e/README.md](../paper-e/README.md) if you want the priced line in full.

If you only have time for one priced paper from this thesis for repository purposes, this is usually the best choice.
