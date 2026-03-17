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

## What to extract while reading

Focus on:

- hierarchical reuse of earlier reachability checks
- how reachability questions get decomposed along the state hierarchy
- compositional backward steps over a restricted subsystem
- dependency-closure ideas used to expand the analysis only when necessary

For this repository, the key reading question is:

"How did the thesis move from plain symbolic compositionality to structure-aware reuse before it entered the timed domain?"

## Where it maps into this repository

Like paper A, this is mostly background rather than a direct UDBM API source.

Its closest relevance here is that it shows:

- how the thesis approaches symbolic reuse as an engineering problem
- why later UPPAAL work kept looking for representations and algorithms that avoid redoing global exploration work unnecessarily

## Why it matters for UDBM specifically

This paper is not about DBMs, federations, or priced zones. It matters mainly as part of the thesis' broader symbolic-verification trajectory.

If your task is strictly UDBM-facing, you can skim this and move on.

## How to read it

Read this after [paper-a/README.md](../paper-a/README.md) if you want the full pre-timed background.

If your actual target is non-convex symbolic sets or timed / priced structures, jump to [paper-c/README.md](../paper-c/README.md).
