# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper E from the parent thesis [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md).

It corresponds to root PDF pages 139-162 and focuses on efficient minimum-cost search in UPPAAL for uniformly priced timed automata.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis summary describes this paper as:

`Efficient Guiding Towards Cost-Optimality in Uppaal`

Publication history noted in the thesis:

- short version presented at `TACAS'01` and published in `LNCS 2031`
- full version published as `BRICS Report Series RS-01-4`

## What to extract while reading

Focus on:

- symbolic cost states for uniformly priced timed automata
- the DBM-based representation using an extra cost clock
- minimum-cost (`MC`) and `MC+` search orders
- bounding and heuristic guidance in a practical UPPAAL implementation

For this repository, the key reading question is:

"How can standard zone / DBM machinery be reused to get practical cost-guided exploration before moving to full priced zones?"

## Where it maps into this repository

- Core DBM API: `UDBM/include/dbm/dbm.h`
- Priced federation type: `UDBM/include/dbm/pfed.h`
- High-level wrapper surface: `pyudbm/binding/udbm.py`

Concrete correspondences:

- this paper is the strongest local bridge from ordinary DBM operations to cost-guided search
- it shows that search order and pruning are part of the symbolic-state story, not only the data structure itself

## Why it matters for UDBM specifically

This is the most implementation-facing priced paper in the thesis if your baseline is ordinary DBM / zone machinery.

It is especially useful when you need to reason about practical priced-state exploration rather than only the abstract problem statement.

## How to read it

Read this after [paper-d/README.md](../paper-d/README.md) if you want the priced line in order.

If your main target is the more general priced-zone machinery for linear prices, continue with [paper-f/README.md](../paper-f/README.md).
