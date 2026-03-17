# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper B from the parent thesis [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md).

It corresponds to root PDF pages 77-98 and focuses on hierarchical `state/event` systems, reusing superstate reachability checks, and combining that reuse with compositional symbolic verification.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis summary describes this paper as:

`Verification of Hierarchical State/Event Systems using Reusability and Compositionality`

Publication history noted in the thesis:

- early version at `TACAS'99` in `LNCS 1579`
- full version published in `Formal Methods in System Design`, volume 21, number 2, September 2002

## What the refined local reading version now contains

The local [content.md](./content.md) now preserves the paper's full hierarchy-aware argument. In particular, it includes:

- the toy-train running example and the explicit flattening contrast in Fig. 1
- the schematic "simple vs. complex substates" example that motivates reuse in Fig. 2
- the formal HSEM model, including configurations, activity semantics, guards, and operational rules
- the reusable-reachability development, with the `Init` construction, Algorithm 1, and the main lemmas
- the compositional extension with sorts, `CB_I`, dependency closure, and Algorithm 2
- the syntactic approximations of `Init` and `Dep`
- the experimental section, including the generated hierarchical-cell benchmark family, the runtime plots, and the final reachability-distribution table

This matters because the paper is much more than "reuse an old reachability result"; it is a carefully layered bridge from flat compositional search to hierarchy-aware symbolic reasoning.

## What to extract while reading

Focus on:

- hierarchical reuse of earlier reachability checks
- how reachability questions get decomposed along the state hierarchy
- compositional backward steps over a restricted subsystem
- the role of `Init`, `lowest(X)`, sorts, and dependency closure in keeping the search small
- the benchmark design, because it explains what kind of hierarchy the authors expect to help in practice

For this repository, the key reading question is:

"How did the thesis move from plain symbolic compositionality to structure-aware reuse before it entered the timed domain?"

## How it connects to the rest of `behrmann03`

This paper completes the pre-timed `visualSTATE` pair.

- Read [paper-a/README.md](../paper-a/README.md) first if you want the flat-system compositional background.
- Read [paper-c/README.md](../paper-c/README.md) next if you want the first paper in the thesis that becomes directly relevant to non-convex symbolic sets and UDBM-adjacent data structures.

## Where it maps into this repository

Like paper A, this is mostly background rather than a direct UDBM API source.

Its closest relevance here is that it shows:

- how the thesis approaches symbolic reuse as an engineering problem
- why later UPPAAL work kept looking for representations and algorithms that avoid redoing global exploration work unnecessarily
- how structural decomposition and behavioral dependency get coupled in an implementation-oriented verification story

## Why it matters for UDBM specifically

This paper is not about DBMs, federations, or priced zones. It matters mainly as part of the thesis' broader symbolic-verification trajectory.

Its value is indirect but real: it shows the author's preference for making symbolic exploration reuse-aware and structure-aware before the thesis even moves into timed systems.

## How to read it

Read this after [paper-a/README.md](../paper-a/README.md) if you want the full pre-timed background.

If your actual target is non-convex symbolic sets or timed / priced structures, jump to [paper-c/README.md](../paper-c/README.md).
