# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper A from the parent thesis [Clocks, DBMs and States in Timed Systems](../README.md).

It corresponds to thesis pages 23-44 and focuses on the DBM package itself: data structures, primitive operations, normalization, and in-memory layout decisions.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis lists this embedded paper as:

`Johan Bengtsson. DBM: Structures, Operations and Implementation. Submitted for publication.`

## What to extract while reading

Focus on:

- canonical DBMs and minimal constraint systems
- the primitive checks and transformations needed in symbolic exploration
- normalization operations on DBMs
- practical layout choices for storing dense and sparse zones

For this repository, the core reading question is:

"Which DBM operations in UDBM are fundamental algorithmic primitives, and what representation assumptions do they rely on?"

## Where it maps into this repository

- Core DBM operations: `UDBM/include/dbm/dbm.h`
- Compact and reduced representations: `UDBM/include/dbm/mingraph.h`
- Python exposure of legacy operations: `pyudbm/binding/udbm.py`

Concrete correspondences:

- operations such as `up`, `down`, emptiness checks, and updates sit directly in the paper's main operation set
- minimal-constraint discussion helps explain why reduced storage is a separate concern from canonical manipulation
- memory-layout discussion helps explain why UDBM cares about low-level DBM storage shape

## Why it matters for UDBM specifically

This is the most direct paper-level explanation of what the DBM layer in UDBM is actually supposed to provide.

If you need to justify a DBM-facing API, reason about canonical assumptions, or understand why certain low-level operations belong in the native library rather than in the Python layer, start here.

## How to read it

Read this before the other extracted papers if your task is primarily about DBM semantics, primitive operations, or low-level representation choices.

If your question is specifically about difference constraints, continue with [paper-b/README.md](../paper-b/README.md). If your question is about compact storage and passed-list cost, continue with [paper-c/README.md](../paper-c/README.md).
