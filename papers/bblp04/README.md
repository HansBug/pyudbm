# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This is the paper to read when you want to understand why UDBM exposes extrapolation operations at all, and why they come in `max-bounds`, `LU-bounds`, and diagonal variants.

It is the cleanest theory source in this set for abstraction-based termination in zone exploration.

## What to extract while reading

Focus on:

- why plain zone exploration may not terminate
- why abstraction by lower and upper bounds preserves the verification objective
- how the abstraction is parameterized by per-clock constants
- why different extrapolation schemes trade precision for convergence

For UDBM, the key question is:

"What exactly is being forgotten by extrapolation, and why is that safe?"

## What the local refined content now gives you

The local `content.md` for this paper is now a proper reading artifact rather than a rough extraction. It gives you most of the parts that matter directly for UDBM and the wrapper work in this repository:

- the introductory motivation built around Fig. 1, which is the clearest compact example in this paper for why lower and upper bounds should be separated in the first place
- the preliminaries chapter with TA syntax, concrete semantics, symbolic semantics, abstraction definitions, and the DBM recap that the extrapolation constructions depend on
- the semantic side of the paper in a readable form: classical maximal-bound abstraction, the LU-preorder, and the abstraction `a_{≺LU}`, including the key move from bisimulation arguments to simulation-based exactness for reachability
- the full extrapolation chapter, not just the headline result: `Extra_M`, `Extra_M^+`, `Extra_LU`, and `Extra_LU^+` are all preserved, together with the small geometric illustrations and the inclusion diagram in Fig. 3
- the successor-computation acceleration section, including LU-form DBMs, the operation-cost breakdown, and the `LU-Canonize` algorithm that replaces the full cubic closure step in the LU-shaped case
- the implementation and experiment section with Table 1 preserved as both an image and a readable Markdown transcription, so the performance story is not reduced to a vague summary
- the conclusion on asymmetric DBM storage, which is especially useful when thinking about whether LU information belongs only to analysis or also to representation design

If you are reading this paper for wrapper design rather than for pure theory, Section 4 and Section 5 are the highest-yield parts because they connect semantic abstraction, concrete DBM rewrites, and implementation cost in one continuous line.

## Suggested reading route inside the paper

If you do not want to read the paper strictly front to back, a repository-oriented route is:

1. read the end of Section 1 and the Fig. 1 discussion to internalize the motivation for LU bounds
2. skim Section 2 only enough to refresh the symbolic-semantics and DBM setup
3. read Section 3 carefully because that is where the semantic abstraction story is stated in its cleanest form
4. then read Section 4 in full, since this is the section that most directly maps to actual UDBM extrapolation operators
5. finish with Section 5 before the experiments, because `LU-Canonize` and LU-form DBMs explain why the paper matters for implementation and not only for correctness proofs

This route works well if your real question is not "What is a timed automaton?" but rather "Why do these particular extrapolation operators exist in a DBM library, and what do they buy us?"

## Where it maps into this repository

- Low-level extrapolation functions: `UDBM/include/dbm/dbm.h`
- High-level Python wrapper: `pyudbm/binding/udbm.py`
- Tests exercising the restored legacy behavior: `test/binding/test_api.py`

Concrete correspondences:

- `dbm_extrapolateMaxBounds(...)`
- `dbm_diagonalExtrapolateMaxBounds(...)`
- `dbm_extrapolateLUBounds(...)`
- `dbm_diagonalExtrapolateLUBounds(...)`
- `Federation.extrapolateMaxBounds(...)`

## Why it matters for UDBM specifically

Without this paper, extrapolation methods look like opaque performance switches. With this paper, they become semantic abstractions with a correctness story.

That matters because UDBM is not only a container of DBM operations; it is part of the symbolic-state termination machinery used by UPPAAL-style verification.

It also matters because this paper is one of the rare local references that does not stop at saying LU-based abstraction is correct. It goes on to explain why LU information can change the cost structure of successor computation itself.

## How to read it

Read this paper after `by04`. If your immediate concern is the Python API, read the abstraction definitions first, then compare them with the wrapper method `Federation.extrapolateMaxBounds(...)` and the native declarations in `dbm.h`.

If your immediate concern is implementation detail rather than API shape, jump from Section 4 directly into the `LU-Canonize` part of Section 5 before reading the experiment section.
