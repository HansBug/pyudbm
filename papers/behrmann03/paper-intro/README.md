# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted introduction part of the parent thesis [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md).

It corresponds to root PDF pages 15-54. It is not one of the six embedded papers, but for repository work it is often the most efficient place to start because it gives the thesis-level framing that the split papers assume.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Why this split exists

Although the thesis presents itself as a collection of six papers, the introduction is unusually useful on its own. It gives:

- the motivation for the thesis as a whole
- one compact map from `visualSTATE` / ROBDD work to CDDs and priced timed automata
- the author's own survey of modeling formalisms and symbolic data structures
- the `The Making of Uppaal` material, which is much more architecture-oriented than the embedded papers
- the thesis summary of papers A-F, which is the shortest publication-level orientation inside the package

## What the refined local reading version now contains

The local [content.md](./content.md) is now a substantial reading artifact rather than a raw extraction. In particular, it preserves:

- the motivation and reachability-analysis setup that frames the rest of the thesis
- the modeling-formalism overview across state/event machines, hierarchical state/event machines, timed automata, and priced timed automata
- the data-structure overview across ROBDDs, DBMs, CDDs, priced zones, and minimal-constraint form
- the `The Making of Uppaal` section, including goals, architecture, the Umbrella work, distributed UPPAAL, stopwatches, and priced timed automata in UPPAAL
- the thesis-summary section for papers A-F, including the author-level "contributions" framing for each embedded paper

This means the introduction now works as a repository-local architecture note, not just as preface material.

## What to extract while reading

Focus on:

- how the thesis positions reachability analysis across several formalisms
- how the author compares explicit, symbolic, DBM-based, CDD-based, and priced representations
- the system architecture in `The Making of Uppaal`, especially symbolic-state manipulation and passed / waiting list design
- the thesis summary, which tells you how the author thinks papers A-F fit together

For this repository, the key reading question is:

"What thesis-level architectural story ties together federations, CDDs, priced structures, and UPPAAL's engine design?"

## How it connects to the rest of `behrmann03`

This introduction is the hub of the split package.

- Read [paper-a/README.md](../paper-a/README.md) and [paper-b/README.md](../paper-b/README.md) after it if you want the pre-timed `visualSTATE` / ROBDD background.
- Read [paper-c/README.md](../paper-c/README.md) after it if your next concern is non-convex symbolic sets, CDDs, or alternatives to plain DBM lists.
- Read [paper-d/README.md](../paper-d/README.md), [paper-e/README.md](../paper-e/README.md), and [paper-f/README.md](../paper-f/README.md) after it if your next concern is cost-optimal reachability and priced symbolic states.

## Where it maps into this repository

- Federation type and operations: `UDBM/include/dbm/fed.h`
- Priced federation type: `UDBM/include/dbm/pfed.h`
- Partition support: `UDBM/include/dbm/partition.h`
- High-level Python wrapper: `pyudbm/binding/udbm.py`

Concrete correspondences:

- the data-structure overview explains why the thesis treats DBMs, minimal constraints, CDDs, and priced structures as different engineering choices rather than one interchangeable abstraction
- `The Making of Uppaal` is the strongest local architecture text for understanding how symbolic-state representations sit inside a real verification pipeline
- the summary of papers A-F is the shortest reliable index for deciding which split paper to read next

## Why it matters for UDBM specifically

If the split papers answer "what was the algorithm or data structure?", this introduction answers "why did these topics belong together in one thesis at all?"

It is the best local entry when you need system-level framing rather than one isolated result.

## How to read it

Read this first if you want a thesis-level map before entering the split papers.

Then continue selectively:

- use [paper-c/README.md](../paper-c/README.md) for CDDs and non-convex symbolic sets
- use [paper-d/README.md](../paper-d/README.md), [paper-e/README.md](../paper-e/README.md), and [paper-f/README.md](../paper-f/README.md) for priced timed automata
- use [paper-a/README.md](../paper-a/README.md) and [paper-b/README.md](../paper-b/README.md) for the earlier `visualSTATE` symbolic-model-checking background
