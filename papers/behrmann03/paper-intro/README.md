# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted introduction part of the parent thesis [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md).

It corresponds to root PDF pages 15-54 and contains material that is not one of the six embedded papers, but is still highly valuable for repository work:

- the motivation chapter
- the modeling-formalism and data-structure overviews
- the `The Making of Uppaal` section
- the thesis summary of papers A-F

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Why this split exists

Although the thesis formally describes itself as a collection of six papers, the introduction is unusually useful on its own. It gives the high-level map that the individual paper splits do not provide.

For repository purposes, this introduction is the best place to find:

- one compact explanation of how the thesis moves from `visualSTATE` and ROBDD work to CDDs and priced timed automata
- the author's own overview of the major modeling formalisms and symbolic data structures
- the system-level `Uppaal` architecture discussion that links algorithms to actual tool design

## What to extract while reading

Focus on:

- how the thesis positions reachability analysis across several formalisms
- the comparison between explicit, symbolic, DBM-based, CDD-based, and priced representations
- the `The Making of Uppaal` section, especially its discussion of layered architecture, symbolic state manipulation, and passed / waiting list design
- the thesis summary section, which gives concise publication-level context for papers A-F

For this repository, the key reading question is:

"What thesis-level architectural story ties together federations, CDDs, priced structures, and UPPAAL's engine design?"

## Where it maps into this repository

- Federation type and operations: `UDBM/include/dbm/fed.h`
- Priced federation type: `UDBM/include/dbm/pfed.h`
- Partition support: `UDBM/include/dbm/partition.h`
- High-level Python wrapper: `pyudbm/binding/udbm.py`

Concrete correspondences:

- the data-structure overview explains why the thesis treats DBMs, minimal constraints, CDDs, and priced structures as separate engineering choices
- the `The Making of Uppaal` section is the most directly architectural local text for understanding how symbolic-state representations fit into a real tool pipeline
- the thesis summary is the shortest way to orient yourself before diving into papers A-F individually

## Why it matters for UDBM specifically

If the split papers answer "what was the algorithm or data structure?", this introduction answers "why did these topics belong together in one thesis at all?"

It is the best local entry when you need architectural framing rather than one isolated result.

## How to read it

Read this before the paper splits if you want the thesis-level map first.

Then continue selectively:

- [paper-c/README.md](../paper-c/README.md) for CDDs and non-convex symbolic sets
- [paper-d/README.md](../paper-d/README.md), [paper-e/README.md](../paper-e/README.md), and [paper-f/README.md](../paper-f/README.md) for priced timed automata
- [paper-a/README.md](../paper-a/README.md) and [paper-b/README.md](../paper-b/README.md) for the earlier `visualSTATE` background
