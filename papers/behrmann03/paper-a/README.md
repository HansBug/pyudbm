# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper A from the parent thesis [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md).

It corresponds to root PDF pages 55-76 and focuses on compositional symbolic model checking of large `state/event` systems using dependency analysis and backwards reachability.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis summary describes this paper as:

`Verification of Large State/Event Systems using Compositionality and Dependency Analysis`

Publication history noted in the thesis:

- early version at `TACAS'98` in `LNCS 1385`
- full version published in `Formal Methods in System Design`, volume 18, number 1, January 2001

## What the refined local reading version now contains

The local [content.md](./content.md) now preserves the paper as a coherent technical note rather than a thin extraction. In particular, it keeps:

- the full state/event-systems presentation, not only the headline algorithm
- the reduction from visualSTATE consistency checks to reachability and local-deadlock questions
- the ROBDD encoding section, including transition-relation construction and partitioned-transition discussion
- the compositional backwards-reachability section with the core `B_I` operator, dependency-closed sets, and the main algorithm figures
- the local-deadlock section, which matters because the paper is not only about reachability
- the experimental section together with both tables and the dependency / usage figures for large examples

For repository reading, this means the paper now exposes both the symbolic-search method and the surrounding tool-engineering problem that motivated it.

## What to extract while reading

Focus on:

- compositional backwards reachability
- dependency analysis as a way to delay bringing more components into the search
- symbolic reuse across incrementally enlarged analyses
- the distinction between the mathematical fixed-point story and the ROBDD implementation story
- how industrial examples are used to justify the dependency-oriented search style

For this repository, the key reading question is:

"What symbolic-search design habits from the author's finite-state work later reappear in the timed and priced parts of the thesis?"

## How it connects to the rest of `behrmann03`

This is the first step in the pre-timed cluster.

- Read [paper-b/README.md](../paper-b/README.md) next if you want to see how this compositionality story gets extended to hierarchical reuse.
- Skip ahead to [paper-c/README.md](../paper-c/README.md) if you only need the first paper in the thesis that becomes directly relevant to UDBM-style non-convex symbolic-state questions.

## Where it maps into this repository

This paper is mostly historical background rather than a direct source for current UDBM APIs.

Its closest value in this repository is conceptual:

- it explains why UPPAAL-family tooling kept investing in symbolic pruning and structured exploration
- it shows the author's older dependence on partitioning, reuse, and delayed inclusion of more behavior
- it helps explain the engineering mindset behind later non-convex and priced symbolic-state work

## Why it matters for UDBM specifically

This is not a DBM or federation paper. Its value is that it shows the symbolic-model-checking style the thesis is coming from before it moves into timed systems.

If you only care about UDBM-facing data structures, you can safely treat this as optional background. If you care about the author's long-term verification-engine habits, it is useful context.

## How to read it

Read this if you want the full thesis chronology or the pre-timed symbolic-verification context.

If your real target is non-convex symbolic sets, CDDs, or priced structures, move on quickly to [paper-c/README.md](../paper-c/README.md).
