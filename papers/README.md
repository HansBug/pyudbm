# Papers Guide

This directory collects the theory, tool, and historical-background papers that are most useful for understanding why UDBM and this wrapper project look the way they do.

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Directory structure

The default structure for one paper subdirectory under `papers/` is:

- `bibtex.bib`
  The canonical citation metadata for the paper.
- `paper.pdf`
  A locally vendored copy of the paper when a lawful public full text is available or otherwise intentionally included.
- `README.md`
  The English reading guide for the paper.
- `README_zh.md`
  The Chinese reading guide for the paper.

Some directories may also contain a small number of additional reference files when there is a concrete need, but the four files above are the standard maintenance target.

## Maintenance rules

When adding or updating a paper entry in this directory:

- create or keep one subdirectory named by a stable citation key such as `by04` or `dhlp06`
- always include `bibtex.bib`
- include `paper.pdf` only when there is a lawful source worth vendoring; if no public full text is available, say that explicitly in `README.md` and `README_zh.md` instead of adding a placeholder PDF
- keep `README.md` and `README_zh.md` paired, cross-linked, and structurally aligned
- keep the paper-level guides focused on repository-relevant reading advice: position in the stack, what to extract, where it maps into the codebase, and why it matters for UDBM
- update this top-level `papers/README.md` and `papers/README_zh.md` whenever new papers are added or the reading paths change

## Recommended reading paths

### Fast path for work in this repository

1. `ta_tools`
   Start here for the semantic and symbolic-zone baseline.
2. `by04`
   Read this next for the best compact tutorial on regions, zones, DBMs, and algorithms.
3. `dhlp06`
   Read this when you need the theory reason for federations and subtraction.
4. `bblp04`
   Read this for extrapolation, abstraction, and termination.
5. `llpy97`
   Read this when touching `mingraph` or compact DBM storage.
6. `bengtsson02`
   Read this for the deeper implementation-oriented DBM and normalization story.

### Tool-context path

- `lpw95`
  Early symbolic / compositional verification foundation for UPPAAL.
- `lpy97`
  Short overview of the UPPAAL toolbox and its design criteria.
- `bdl04`
  Mature UPPAAL tutorial with modeling patterns and practical usage.
- `behrmann03`
  Broader system-level architecture around federations, CDDs, sharing, and priced extensions.

### Historical-root path

- `dill89`
  Early dense-time symbolic verification precursor.
- `ad90`
  Original timed-automata source paper.
- `rokicki93`
  Historical citation point in the normalization line; full text is not locally available here.

If you want the shortest path to the parts most directly visible in today's Python wrapper, use:
`ta_tools -> by04 -> dhlp06 -> bblp04 -> llpy97`.

## What each paper contributes

### `ta_tools`

Role:
foundation for timed automata semantics, zones, DBMs, and basic symbolic algorithms.

Main UDBM support:

- the meaning of a convex zone
- the canonical DBM view
- core operations such as delay, past, reset, and guard intersection

### `by04`

Role:
best compact tutorial on timed automata semantics, regions, zones, DBMs, and verification algorithms.

Main UDBM support:

- why zones replace regions in practice
- how canonical DBMs encode zones
- what symbolic operations a verification tool repeatedly needs
- why normalization / bounded abstraction matters

### `dhlp06`

Role:
DBM subtraction and the direct theoretical motivation for federations.

Main UDBM support:

- subtraction on zones
- non-convex results
- unions of DBMs as the result domain
- reduction after subtraction

### `bblp04`

Role:
lower/upper-bound abstractions for zone-based verification.

Main UDBM support:

- why extrapolation is sound
- why extrapolation can force termination
- why multiple extrapolation schemes exist

### `llpy97`

Role:
minimal graph and compact storage of DBMs.

Main UDBM support:

- why `mingraph` exists
- why canonical DBMs are not always the best stored form

### `bengtsson02`

Role:
deep implementation-oriented thesis on clocks, DBMs, states, normalization, and storage in timed verification.

Main UDBM support:

- the full DBM operation set behind symbolic exploration
- normalization with difference constraints
- storage, compression, and hashing motivations

### `lpw95`

Role:
early UPPAAL foundation paper on symbolic and compositional model checking.

Main UDBM support:

- why solving clock-constraint systems is central
- why symbolic state exploration beats explicit region handling in practice
- why UDBM sits below, not inside, the whole model-checking stack

### `lpy97`

Role:
short overview of the UPPAAL toolbox and its user-facing design.

Main UDBM support:

- why constraint solving and on-the-fly reachability dominate the engine design
- why usability and readable symbolic modeling matter

### `bdl04`

Role:
practical UPPAAL tutorial for modeling language, queries, and patterns.

Main UDBM support:

- the user-side timed-automata dialect served by the symbolic engine
- why high-level clock-oriented APIs matter more than raw matrix helpers

### `behrmann03`

Role:
system-level synthesis across symbolic data structures used around UPPAAL.

Main UDBM support:

- why unions of zones are important at the tool level
- why CDDs were explored as an alternative
- why sharing, storage layout, and priced extensions matter

### `dill89`

Role:
historical precursor from timing assumptions to symbolic dense-time verification.

Main UDBM support:

- the early move toward symbolic timing-state representations
- the deeper motivation for representing sets of clock valuations symbolically

### `ad90`

Role:
original timed-automata language-theoretic source.

Main UDBM support:

- the clock / guard / reset model underneath later symbolic techniques
- the formal timed-automaton object that zone and DBM methods later encode

### `rokicki93`

Role:
historical reference point in the normalization literature.

Main UDBM support:

- mainly provenance for the normalization line later cited by `by04` and `bengtsson02`

Note:
no lawful public full-text PDF was found for `rokicki93` during collection or during the follow-up retrieval attempt for this update.

## How this maps to the Python wrapper work in this repository

The restored Python API in `pyudbm/binding/udbm.py` is not just wrapping raw matrix primitives. It is trying to reconstruct the historical `Context` / `Clock` / `Federation` model on top of UDBM.

That means:

- `ad90` and `dill89` explain the older semantic roots of clock-based symbolic reasoning
- `ta_tools` and `by04` explain the single-zone / DBM layer that the DSL manipulates
- `dhlp06` explains why `Federation` must remain a real union-based object instead of collapsing to one DBM
- `bblp04` explains why methods like `extrapolateMaxBounds` belong in the public surface
- `llpy97` and `bengtsson02` explain the compressed-storage and implementation machinery already present in native UDBM
- `lpw95`, `lpy97`, `bdl04`, and `behrmann03` explain the larger UPPAAL tool context and user-facing expectations around that engine

## Practical advice

If you are reading for implementation work in this repository:

- start with `ta_tools/README.md`
- then read `by04/README.md`
- then read `dhlp06/README.md`
- then read `bblp04/README.md`
- use `llpy97/README.md` and `bengtsson02/README.md` when touching `mingraph`, storage, or lower-level DBM machinery
- use `lpy97/README.md` and `bdl04/README.md` when thinking about high-level API ergonomics
- use `behrmann03/README.md` when you need the larger UPPAAL architecture
