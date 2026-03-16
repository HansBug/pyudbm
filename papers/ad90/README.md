# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This is one of the original timed automata papers. It matters less as a direct DBM paper than as the source of the clock / guard / reset model that later zone- and DBM-based work builds on.

If `by04` answers "how do we do symbolic algorithms on zones?", this paper helps answer "what are clocks and timed automata supposed to mean in the first place?"

## What to extract while reading

Focus on:

- real-valued clocks as part of the automaton state
- guards and resets as the basic timing mechanism
- timed traces and language-theoretic reasoning
- the decidability boundary: some timed-language questions remain hard or undecidable

For UDBM, the key reading question is:

"What is the underlying timed-automaton object that later zone and DBM algorithms are trying to represent?"

## Where it maps into this repository

- Clock-centric high-level DSL: `pyudbm/binding/udbm.py`
- Native clock-constraint operations: `UDBM/include/dbm/dbm.h`
- Compatibility-oriented API tests: `test/binding/test_api.py`

Concrete correspondences:

- `Clock` and `Constraint` preserve the clock / guard viewpoint
- reset-like operations map to `Federation.updateValue(...)`, `Federation.resetValue(...)`, `Federation.setZero()`, and `Federation.setInit()`
- conjunctions of clock bounds map to the symbolic objects wrapped by `Federation`

## Why it matters for UDBM specifically

UDBM does not implement timed automata as syntax trees. It implements the symbolic clock-constraint layer underneath them. This paper explains why the wrapper should stay clock-oriented instead of collapsing into anonymous matrix helpers.

It is also a useful reminder that the later zone literature is a semantic optimization layer on top of the timed-automaton model, not a replacement for it.

## How to read it

Read it before `by04` if you want the historical origin first, or after `by04` if you want to backfill the formal roots of the model.

Availability note:
the local `paper.pdf` in this directory is now a 14-page scanned copy of the full chapter, and `content.md` is a manually refined Markdown transcription based on that scan.

Practical caveat:
this is still a scan of an old proceedings chapter rather than a born-digital PDF, so keeping the diagram crops alongside the refined transcription is important for checking notation and automaton structure against the source pages.
