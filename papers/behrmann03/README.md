# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This thesis is broader than a single algorithm paper. It spans three fairly different layers of work around the UPPAAL ecosystem:

- symbolic verification of large finite-state `visualSTATE` models
- alternative symbolic data structures for timed systems, most notably CDDs
- cost-optimal reachability for priced timed automata

For UDBM-related work, the most valuable parts are the CDD paper and the three priced timed-automata papers. Those are the parts that best explain why UPPAAL-family tooling cared about non-convex symbolic sets, sharing, and priced symbolic state representations.

## Embedded paper layout

This entry now has two layers:

- thesis-level material in the root of `papers/behrmann03/`, including the full [paper.pdf](./paper.pdf), the thesis-level guides, and the refined [content.md](./content.md)
- extracted second-level directories under `paper-intro/` and `paper-a/` through `paper-f/`

The root thesis PDF remains the canonical full-text record in this repository. The child directories are convenience splits of the thesis introduction and the six embedded papers listed by the thesis itself. Each child directory now has:

- `paper.pdf`
- `README.md`
- `README_zh.md`

Current second-level mapping:

- [paper-intro/README.md](./paper-intro/README.md): thesis introduction, motivation, data-structure overview, UPPAAL architecture, and thesis summary (root PDF pages 15-54)
- [paper-a/README.md](./paper-a/README.md): `Verification of Large State/Event Systems using Compositionality and Dependency Analysis` (root PDF pages 55-76)
- [paper-b/README.md](./paper-b/README.md): `Verification of Hierarchical State/Event Systems using Reusability and Compositionality` (root PDF pages 77-98)
- [paper-c/README.md](./paper-c/README.md): `Efficient Timed Reachability Analysis using Clock Difference Diagrams` (root PDF pages 99-114)
- [paper-d/README.md](./paper-d/README.md): `Minimum-Cost Reachability for Priced Timed Automata` (root PDF pages 115-138)
- [paper-e/README.md](./paper-e/README.md): `Efficient Guiding Towards Cost-Optimality in Uppaal` (root PDF pages 139-162)
- [paper-f/README.md](./paper-f/README.md): `As Cheap as Possible: Efficient Cost-Optimal Reachability for Priced Timed Automata` (root PDF pages 163-193)

Use the root thesis when you need the unified bibliography or the complete dissertation context. Use [paper-intro/README.md](./paper-intro/README.md) when you want the introduction material in isolation, and use the remaining child directories when you want one embedded paper in isolation.

## How The Six Embedded Papers Fit Together

The six embedded papers are not one single linear story. Together with the extracted introduction, the structure breaks into four practical layers.

- [paper-intro/README.md](./paper-intro/README.md) is the thesis-level framing layer.
  It contains the motivation, the modeling-formalism overview, the data-structure overview, the "Making of Uppaal" section, and the thesis summary of papers A-F.

- [paper-a/README.md](./paper-a/README.md) and [paper-b/README.md](./paper-b/README.md) are the `visualSTATE` / ROBDD cluster.
  They are mostly pre-UDBM background: large finite-state symbolic verification, then hierarchical reuse on top of that.
- [paper-c/README.md](./paper-c/README.md) is the CDD bridge paper.
  It is the first paper here that becomes directly relevant to UDBM-style questions about non-convex symbolic sets, unions of zones, storage, and symbolic-state compaction.
- [paper-d/README.md](./paper-d/README.md), [paper-e/README.md](./paper-e/README.md), and [paper-f/README.md](./paper-f/README.md) are the priced timed-automata cluster.
  They move from decidability via priced regions, to DBM-based optimal search in uniformly priced systems, to priced zones for the more general linear-price setting.

If you want the shortest UDBM-facing path through this thesis, read:

1. [paper-intro/README.md](./paper-intro/README.md)
2. [paper-c/README.md](./paper-c/README.md)
3. [paper-d/README.md](./paper-d/README.md)
4. [paper-e/README.md](./paper-e/README.md)
5. [paper-f/README.md](./paper-f/README.md)

Use papers A-B mainly as historical background for the author's symbolic-model-checking perspective and tool-engineering style.

## What Each Embedded Paper Adds

### Paper A

Title:
`Verification of Large State/Event Systems using Compositionality and Dependency Analysis`

Repository value:

- historical background for compositional symbolic search before the thesis moves into timed systems
- useful when tracing how dependency analysis and symbolic reuse shaped later verification-engine thinking

### Paper B

Title:
`Verification of Hierarchical State/Event Systems using Reusability and Compositionality`

Repository value:

- adds hierarchy-aware reuse on top of the paper-A style symbolic verification story
- useful as background for tool architecture and structured state-space decomposition, but not a direct UDBM paper

### Paper C

Title:
`Efficient Timed Reachability Analysis using Clock Difference Diagrams`

Repository value:

- the most direct local paper here on CDDs, unions of zones, and compact representation of non-convex symbolic sets
- useful when you need to explain why finite unions of zones are a real algorithmic object rather than just a convenience wrapper

### Paper D

Title:
`Minimum-Cost Reachability for Priced Timed Automata`

Repository value:

- establishes the first priced timed-automata minimum-cost reachability story in this thesis via priced regions
- useful as the theory-first precursor to the later priced-zone work, even though it is less implementation-aligned than papers E-F

### Paper E

Title:
`Efficient Guiding Towards Cost-Optimality in Uppaal`

Repository value:

- the most direct bridge from ordinary DBM machinery to practical cost-guided search in UPPAAL
- useful when the question is how zone-based symbolic states, search order, and branch-and-bound style heuristics interact in an actual engine

### Paper F

Title:
`As Cheap as Possible: Efficient Cost-Optimal Reachability for Priced Timed Automata`

Repository value:

- the strongest thesis-local link to priced zones, facets, and lifting ordinary zone machinery to general linear-price optimal reachability
- useful when you want the paper here that feels closest to a priced extension of the classic DBM / zone toolchain

## What to extract while reading

Do not treat the whole thesis as equally relevant. For UDBM work, focus on:

- the CDD treatment of finite unions of zones
- the storage and sharing motivation behind symbolic-state representations
- the progression from priced regions to DBM-based priced search to priced zones
- the distinction between theory-first symbolic objects and implementation-friendly symbolic objects

For this repository, the key reading question is:

"Which non-convex and priced symbolic structures did the UPPAAL line consider important enough to turn into first-class data structures?"

## Where it maps into this repository

- Federation type and operations: `UDBM/include/dbm/fed.h`
- Federation implementation: `UDBM/src/fed.cpp`
- Priced federation type: `UDBM/include/dbm/pfed.h`
- Partition-oriented reduction support: `UDBM/include/dbm/partition.h`, `UDBM/src/partition.cpp`
- High-level Python `Federation` wrapper: `pyudbm/binding/udbm.py`

Concrete correspondences:

- paper C gives the clearest local discussion of non-convex symbolic sets as something richer than a single DBM
- papers D-F explain why priced symbolic state representations exist beside ordinary zone operations
- the thesis-wide discussion of storage and sharing helps explain hashing, interning-style thinking, and compact symbolic representations in the broader UPPAAL line

## Why it matters for UDBM specifically

This thesis is not the direct source for every UDBM API, but it gives the architectural reason why the UPPAAL ecosystem grew beyond "one DBM at a time".

It is especially helpful if you want to understand:

- why finite unions of zones keep reappearing
- why CDDs were explored alongside DBM-based approaches
- why priced extensions sit naturally next to ordinary federation support

## How to read it

Use this thesis selectively.

- Read [paper-intro/README.md](./paper-intro/README.md) first if you want the thesis-level explanation of why these six papers belong together and how they fit into UPPAAL.
- Read [paper-c/README.md](./paper-c/README.md) first if your question is about non-convex symbolic sets, CDDs, or alternatives to plain DBM lists.
- Read [paper-d/README.md](./paper-d/README.md), [paper-e/README.md](./paper-e/README.md), and [paper-f/README.md](./paper-f/README.md) if your question is about optimal-cost reachability and priced extensions.
- Read [paper-a/README.md](./paper-a/README.md) and [paper-b/README.md](./paper-b/README.md) mainly when you want the broader pre-timed symbolic-model-checking background behind the thesis.
