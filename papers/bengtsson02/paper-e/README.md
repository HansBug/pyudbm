# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This directory contains the extracted copy of Paper E from the parent thesis [Clocks, DBMs and States in Timed Systems](../README.md).

It corresponds to thesis pages 115-143 and covers committed locations together with an industrial audio-control protocol case study in UPPAAL.

The local [paper.pdf](./paper.pdf) is an extraction of the parent [../paper.pdf](../paper.pdf). The thesis-level entry remains the canonical full record.

## Publication status

The thesis lists this embedded paper as:

`Johan Bengtsson, W. O. David Griffioen, Kare J. Kristoffersen, Kim G. Larsen, Fredrik Larsson, Paul Pettersson and Wang Yi. Automated Verification of an Audio-Control Protocol using UPPAAL. Accepted for publication in Journal on Logic and Algebraic Programming.`

## What to extract while reading

Focus on:

- the committed-location mechanism and why it affects both modeling and verification cost
- the model-checking algorithm changes needed to exploit committed locations
- the audio-control protocol with bus collision as a realistic validation case
- the performance comparison between the newer UPPAAL implementation and older behavior

For this repository, the key reading question is:

"Why did committed locations matter enough in practice to change both the modeling style and the exploration algorithm?"

## Where it maps into this repository

- This paper is mostly UPPAAL tool context rather than direct UDBM API design
- It is useful when reasoning about higher-level modeling ergonomics and why symbolic-state reduction matters in practice
- It connects naturally to `lpy97`, `bdl04`, and other UPPAAL usage papers already collected in `papers/`

## Why it matters for UDBM specifically

This paper shows the operational environment in which DBM and state-space optimizations paid off on a nontrivial case study.

Read it when you need a concrete explanation of why committed locations, state-space reduction, and efficient symbolic manipulation were not merely theoretical refinements.

## How to read it

Read this after [paper-d/README.md](../paper-d/README.md) if you want the concrete UPPAAL case-study that follows the committed-location and reduction ideas into practice.

For wrapper-facing work it is supporting context rather than the first paper to read, but it is useful when you need an industrial example instead of a purely algorithmic argument.
