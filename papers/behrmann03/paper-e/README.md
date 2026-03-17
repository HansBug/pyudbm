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

## What the refined local reading version now contains

The local [content.md](./content.md) now preserves the paper as a practical algorithm paper rather than only a priced-search slogan. In particular, it keeps:

- the uniformly priced timed-automata setup and its relation to the more general linearly priced model
- the cost-function machinery and the symbolic semantics used in the search
- the DBM-based representation with an additional cost clock
- the `MC` and `MC+` search orders, together with the estimates / heuristics / bounding discussion
- the experiment sections on the bridge problem, job-shop scheduling, the Sidmar steel plant, and the biphase-mark protocol
- all five tables, which matter because much of the paper's value is empirical and search-strategy-oriented

This makes the paper a direct local bridge between "ordinary DBM-style symbolic states" and "practical cost-guided search in a real UPPAAL implementation".

## What to extract while reading

Focus on:

- symbolic cost states for uniformly priced timed automata
- the DBM-based representation using an extra cost clock
- minimum-cost (`MC`) and `MC+` search orders
- bounding and heuristic guidance in a practical UPPAAL implementation
- the difference between semantic optimality and search guidance quality

For this repository, the key reading question is:

"How can standard zone / DBM machinery be reused to get practical cost-guided exploration before moving to full priced zones?"

## How it connects to the rest of `behrmann03`

This is the implementation bridge inside the priced cluster.

- Read [paper-d/README.md](../paper-d/README.md) first if you want the theory-first priced-regions motivation.
- Read [paper-f/README.md](../paper-f/README.md) next if you want the more general priced-zone symbolic object for linear prices.

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
