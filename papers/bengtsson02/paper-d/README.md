# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper D from the parent thesis [Clocks, DBMs and States in Timed Systems](../README.md).

It corresponds to thesis pages 93-114 and focuses on partial-order reduction for timed systems via a local-time semantics.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis lists this embedded paper as:

`Johan Bengtsson, Bengt Jonsson, Johan Lilius and Wang Yi. Partial Order Reductions for Timed Systems. In Proceedings, Ninth International Conference on Concurrency Theory, volume 1466 of Lecture Notes in Computer Science, Springer Verlag, 1998.`

## What to extract while reading

Focus on:

- the local-time semantics for networks of timed automata
- the resynchronization machinery needed when processes communicate
- how independence is recovered well enough to reuse standard partial-order ideas
- the DBM representation consequences of this changed semantics

For this repository, the key reading question is:

"What has to change in the underlying semantics before partial-order reasoning becomes useful again for timed systems?"

## Where it maps into this repository

- This paper is mainly UPPAAL-engine context rather than direct wrapper API
- It informs how to think about symbolic-state meaning, not just DBM operators
- It is useful background when reading later committed-location work and broader UPPAAL architecture papers

## Why it matters for UDBM specifically

This paper is not the first stop for the Python wrapper surface, but it explains an important part of the environment in which the UDBM-style state machinery was used.

Read it when you need the semantics behind local-time exploration, partial-order reduction claims, or later committed-location design choices.

## How to read it

Read this after [paper-a/README.md](../paper-a/README.md), [paper-b/README.md](../paper-b/README.md), and [paper-c/README.md](../paper-c/README.md) unless your task is specifically about UPPAAL semantics.

It pairs naturally with [paper-e/README.md](../paper-e/README.md), which turns the committed-location story into a concrete tool and case-study discussion.
