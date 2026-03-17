# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper D from the parent thesis [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md).

It corresponds to root PDF pages 115-138 and focuses on minimum-cost reachability for linearly priced timed automata using priced regions.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis summary describes this paper as:

`Minimum-Cost Reachability for Priced Timed Automata`

Publication history noted in the thesis:

- shorter version presented at `HSCC'01` and published in `LNCS 2034`
- full version appears as `BRICS Report Series RS-01-3`

## What to extract while reading

Focus on:

- the formal model of linearly priced timed automata
- priced regions as the first symbolic object in this thesis for minimum-cost reachability
- the branch-and-bound style exploration algorithm
- why the problem is decidable but region-based machinery is not yet implementation-friendly

For this repository, the key reading question is:

"What was the theory-first symbolic basis for cost-optimal timed reachability before priced zones were introduced?"

## Where it maps into this repository

- Priced federation type: `UDBM/include/dbm/pfed.h`
- High-level symbolic-set exposure: `pyudbm/binding/udbm.py`

Concrete correspondences:

- this paper explains why priced symbolic states need their own objects, not just a post-processing layer on ordinary reachability
- it is more of a conceptual precursor than a direct API blueprint

## Why it matters for UDBM specifically

This paper is the priced-theory starting point in the thesis.

It is less implementation-aligned than papers E-F, but it gives the cleanest local explanation of what the priced reachability problem is supposed to compute in the first place.

## How to read it

Read this before [paper-f/README.md](../paper-f/README.md) if you want the priced-zone work with its theoretical motivation in place.

If you mainly want the practical DBM-based bridge to UPPAAL, continue with [paper-e/README.md](../paper-e/README.md).
