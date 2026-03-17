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

## What to extract while reading

Focus on:

- compositional backwards reachability
- dependency analysis as a way to delay bringing more components into the search
- symbolic reuse across incrementally enlarged analyses
- industrial-scale symbolic verification under limited resources

For this repository, the key reading question is:

"What symbolic-search design habits from the author's finite-state work later reappear in the timed and priced parts of the thesis?"

## Where it maps into this repository

This paper is mostly historical background rather than a direct source for current UDBM APIs.

Its closest value in this repository is conceptual:

- it gives background for why UPPAAL-family tooling kept investing in symbolic pruning and structured exploration
- it helps explain the engineering mindset behind later non-convex and priced symbolic-state work

## Why it matters for UDBM specifically

This is not a DBM or federation paper. Its value is that it shows the symbolic-model-checking style the thesis is coming from before it moves into timed systems.

If you only care about UDBM-facing data structures, you can safely treat this as optional background.

## How to read it

Read this if you want the full thesis chronology or the pre-timed symbolic-verification context.

If you want the first paper here that becomes directly relevant to UDBM-style questions, continue with [paper-c/README.md](../paper-c/README.md).
