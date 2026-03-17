# UPPAAL Tutorials Planning Notes

## Purpose

This document records the current planning discussion for a future bilingual
UPPAAL-oriented theory/tutorial section under `docs/`.

The goal is not merely to document `UDBM` in isolation. The larger intended
direction is to gradually reconstruct the broader UPPAAL stack in Python, with
`UDBM` as one important foundational layer among several others.

Accordingly, the tutorial plan here treats the following as first-class topics:

- timed automata and their semantics
- verification properties and query intuition
- symbolic states, zones, and DBMs
- federations and non-convex symbolic sets
- CDDs as an alternative symbolic representation
- core exploration algorithms and termination machinery
- storage, compression, and passed/waiting engineering
- reduction techniques and modeling-oriented optimization
- priced timed automata and cost-optimal reachability
- the eventual mapping from theory to a Python-facing UPPAAL-oriented API

## Planning Principles

### 1. Do not structure the docs by paper order

The `papers/` tree is source material, not the public-facing tutorial
structure.

For newcomers, the tutorial should follow a learning curve:

1. what problem UPPAAL solves
2. what kind of model it uses
3. what properties users ask
4. why symbolic states are needed
5. which symbolic representations exist
6. how the verification engine runs
7. why extra optimizations and extensions appear

This is more suitable than mirroring the citation order or writing one
"paper digest" per entry.

### 2. The writing should stay friendly

The target audience includes readers who are not already familiar with timed
automata or formal verification.

That implies:

- start from examples and problems before formal definitions
- use formulas, but sparingly
- always explain formulas in plain language
- introduce one or two running examples early and reuse them
- prefer diagrams that show geometric or execution intuition
- delay proof-heavy material until the reader already has a mental model

### 3. Each page should mix intuition, diagrams, and a small amount of math

A good default for each tutorial page is:

- 1 main figure
- optionally 1 supporting figure
- 2 to 4 key formulas at most
- 1 running example used throughout the page
- a short "why this matters for UPPAAL/Python" ending section

The docs should not collapse into pure formulas or pure handwaving.

### 4. Treat the UPPAAL stack as larger than UDBM

The original narrow UDBM-centered view is not sufficient for the current
project ambition.

`UDBM` is central, but not enough by itself. A broader UPPAAL-oriented
tutorial plan must also account for:

- query/property thinking
- engine architecture
- federation-level semantics
- CDDs and symbolic-representation alternatives
- passed/waiting lists and state storage pressure
- extrapolation and normalization
- partial-order and modeling-sensitive reductions
- priced symbolic structures and optimality

### 5. Keep the bilingual structure explicit

The repository already uses paired English/Chinese documentation pages, for
example:

- `docs/source/index_en.rst`
- `docs/source/index_zh.rst`
- `docs/source/tutorials/installation/index.rst`
- `docs/source/tutorials/installation/index_zh.rst`

The future theory/tutorial section should follow the same paired structure
instead of trying to mix both languages into a single page.

## Source-Material Orientation

The tutorial plan below is based primarily on the following local paper guides:

- `papers/ad90/README.md`
- `papers/by04/README.md`
- `papers/dhlp06/README.md`
- `papers/bblp04/README.md`
- `papers/lpw95/README.md`
- `papers/lpy97/README.md`
- `papers/bdl04/README.md`
- `papers/llpy97/README.md`
- `papers/bengtsson02/README.md`
- `papers/behrmann03/README.md`
- `papers/behrmann03/paper-intro/README.md`

Roughly speaking:

- `ad90` and `by04` provide the core model and symbolic-semantics baseline
- `dhlp06` explains federation subtraction and non-convexity
- `bblp04` explains extrapolation and termination-oriented abstraction
- `llpy97` and `bengtsson02` explain compact storage and engine cost pressure
- `lpy97` and `bdl04` contribute the tool-user and modeling perspective
- `behrmann03` broadens the picture toward CDDs, system architecture, and
  priced symbolic structures

## Two-Track Tutorial Strategy

The recommended public structure is:

- a **main track** for newcomers
- an **advanced track** for implementation-aware readers

This keeps the entry barrier low without hiding the broader UPPAAL design
space.

## Main Track

The main track should be readable by someone who is new to timed automata and
model checking.

### 1. What Problem Does UPPAAL Solve?

Suggested focus:

- what formal verification is, at a high level
- how it differs from testing and simulation
- why timing constraints make concurrent systems harder
- the big-picture structure: model, properties, symbolic engine, answer

Best source anchors:

- `papers/lpy97/README.md`
- `papers/bdl04/README.md`
- `papers/behrmann03/paper-intro/README.md`

Suggested diagram:

- one overview pipeline from model to symbolic exploration to counterexample

Formula load:

- minimal; this page is mainly conceptual

### 2. Timed Automata: How Systems Evolve with Time

Suggested focus:

- locations, clocks, guards, resets, invariants
- time-delay transitions versus discrete transitions
- valuations as part of the state
- a small request/response or timeout example

Best source anchors:

- `papers/ad90/README.md`
- `papers/by04/README.md`

Suggested diagrams:

- one small timed automaton
- one figure showing time elapse versus jump

Formula load:

- only the most basic semantic rules

### 3. What Kinds of Properties Does UPPAAL Check?

Suggested focus:

- reachability and safety intuition
- deadlock-style questions
- "can something happen?" versus "must something always hold?"
- a beginner-friendly view of query intent before full logical syntax
- a light foreshadowing of cost/optimality

Best source anchors:

- `papers/bdl04/README.md`
- `papers/lpy97/README.md`
- `papers/by04/README.md`

Suggested diagram:

- good states, bad states, and target states in a state-space picture

Formula load:

- light; prefer examples over logic-heavy presentation

### 4. Why Symbolic States Are Needed: From Explicit States to Zones

Suggested focus:

- why continuous time breaks naive explicit enumeration
- why regions matter theoretically
- why zones matter practically
- how symbolic state sets replace single valuations

Best source anchors:

- `papers/by04/README.md`
- `papers/lpw95/README.md`

Suggested diagrams:

- region partition versus a larger zone
- a 2D `(x, y)` clock-space picture

Formula load:

- the reader only needs the idea of conjunctions of clock constraints

### 5. DBM: Why a Matrix Can Represent a Zone

Suggested focus:

- constraints of the form `xi - xj <= c`
- the role of the zero clock
- DBM layout and intuition
- canonical closure as the core invariant
- why UDBM is the implementation-facing realization of this layer

Best source anchors:

- `papers/by04/README.md`
- `papers/bengtsson02/README.md`

Suggested diagrams:

- a geometric zone next to its DBM table

Formula load:

- moderate; keep to the essential representation equations

### 6. Why One DBM Is Not Enough: Federations and Non-Convex Sets

Suggested focus:

- subtraction of convex zones can yield a non-convex set
- why a federation is a finite union of DBMs
- why union, subtraction, and reduction are semantically necessary
- why this is not just an API convenience

Best source anchors:

- `papers/dhlp06/README.md`
- `papers/behrmann03/paper-c/README.md`

Suggested diagrams:

- a convex region with a middle part removed, producing multiple components

Formula load:

- light to moderate; the pictures matter more

### 7. Why CDDs Exist: Another Way to Represent Non-Convex Symbolic Sets

Suggested focus:

- federations and CDDs as two different answers to non-convex symbolic sets
- the intuition behind sharing and decomposition
- when a list of DBMs is natural
- when a decision-diagram-style representation becomes attractive
- the idea that UPPAAL's design space is broader than "one DBM type"

Best source anchors:

- `papers/behrmann03/README.md`
- `papers/behrmann03/paper-intro/README.md`
- `papers/behrmann03/paper-c/README.md`

Suggested diagrams:

- non-convex set as separate pieces versus diagram-based shared structure

Formula load:

- low; this page should establish the design-space intuition first

### 8. Search and Optimization: Why UPPAAL Is Not Just a Bag of Data Structures

Suggested focus:

- the core forward symbolic reachability loop
- waiting versus passed
- inclusion checks
- normalization and extrapolation for termination
- compact storage, hashing, and memory pressure
- why algorithmic structure and data structure shape influence each other

Best source anchors:

- `papers/bblp04/README.md`
- `papers/llpy97/README.md`
- `papers/bengtsson02/README.md`
- `papers/behrmann03/paper-intro/README.md`

Suggested diagrams:

- search loop flowchart
- extrapolation before/after picture
- compact-storage or passed-list pressure sketch

Formula load:

- moderate; short pseudocode may be better than dense formulas here

## Advanced Track

The advanced track should serve readers who want the broader UPPAAL research
and implementation story, including future Python reconstruction questions.

### 9. Modeling Choices and Reduction: Urgent, Committed, and Partial Order

Suggested focus:

- why some modeling constructs reduce unnecessary interleavings
- urgent and committed intuition
- why partial-order reduction is harder in timed systems
- local-time style thinking and exploration restructuring

Best source anchors:

- `papers/bdl04/README.md`
- `papers/bengtsson02/README.md`

### 10. Beyond Reachability: Priced Timed Automata and Cost-Optimal Search

Suggested focus:

- from "is the target reachable?" to "what is the cheapest way to reach it?"
- cost/price in the model
- priced regions, priced zones, and cost-guided search
- why UPPAAL's research line naturally expanded toward optimality

Best source anchors:

- `papers/behrmann03/README.md`
- `papers/behrmann03/paper-d/README.md`
- `papers/behrmann03/paper-e/README.md`
- `papers/behrmann03/paper-f/README.md`

### 11. The Symbolic Data-Structure Family Tree

Suggested focus:

- explicit states
- zones
- DBMs
- federations
- CDDs
- priced zones
- minimal constraints and compressed forms
- what each representation optimizes for

Best source anchors:

- `papers/behrmann03/paper-intro/README.md`
- `papers/bengtsson02/README.md`
- `papers/llpy97/README.md`

This page is especially useful as a bridge from theory tutorial to codebase
reading and future design work.

### 12. From Theory to Python API: What a Python-Side UPPAAL Reconstruction Should Expose

Suggested focus:

- which concepts should be first-class Python objects
- which pieces belong to public API versus engine internals
- which layers should likely be restored first
- how to keep historical compatibility while still leaving room for broader
  UPPAAL-level reconstruction

This page is more project-direction-oriented than paper-oriented, but it
should synthesize the preceding tutorial line.

## Recommended Release Batches

To keep the writing manageable, publish in three rounds:

### Batch 1

- pages 1 through 6

This gives readers a coherent first understanding of:

- what UPPAAL is for
- what timed automata are
- what properties are being checked
- why symbolic zones are needed
- what DBMs are
- why federations appear

### Batch 2

- pages 7 and 8

This is where the docs widen from "basic zone reasoning" into:

- alternative non-convex representations such as CDDs
- engine-level search and optimization structure

### Batch 3

- pages 9 through 12

This batch brings in:

- reduction-aware modeling and partial-order concerns
- priced timed automata
- a unified symbolic-representation map
- the connection to future Python API design

## Stable Internal Page Template

Each tutorial page should ideally follow a stable internal pattern:

1. What question this page answers
2. A small intuitive example
3. The core concept
4. One main figure
5. A few key formulas or short pseudocode
6. Why this matters for UPPAAL and for the Python reconstruction direction
7. Suggested further reading in `papers/`

This pattern is friendly for newcomers and easy to maintain in bilingual form.

## Diagram and Formula Guidance

### Diagram guidance

- each page should have one clear primary diagram
- geometric clock-space diagrams are especially useful for zones, DBMs,
  federations, and extrapolation
- state-space flow diagrams are especially useful for properties, search, and
  engine architecture
- comparison diagrams are especially useful for DBM versus federation versus
  CDD versus priced structures

### Formula guidance

- do not flood the page with formalism
- give the intuition in plain language before the formula
- prefer one representative formula over full formal systems on first
  introduction
- move dense formal details to later pages or side boxes

## Bilingual Organization Recommendation

The future theory section under `docs/source/tutorials/` should follow the
same bilingual pairing style already used by the repository.

One likely shape is:

```text
docs/source/tutorials/theory/
|- index.rst
|- index_zh.rst
|- 01-what-is-uppaal.rst
|- 01-what-is-uppaal_zh.rst
|- 02-timed-automata-basics.rst
|- 02-timed-automata-basics_zh.rst
|- ...
```

The exact filenames can be adjusted, but the pairing principle should remain.

## What Changed Relative to the Initial Narrower Plan

An earlier draft of the discussion was too UDBM-centered.

That earlier version did capture several useful points:

- the docs should be friendly
- the docs should not be organized by paper order
- diagrams and formulas should be balanced
- `by04`, `dhlp06`, and `bblp04` are central foundations

However, that narrower draft underemphasized the fact that the broader project
direction is not "document UDBM nicely" but rather "help rebuild the larger
UPPAAL stack in Python."

The revised plan therefore expands the writing scope to explicitly include:

- property/query thinking
- CDDs
- engine architecture
- storage and search-pressure concerns
- reduction-oriented modeling constructs
- priced symbolic structures
- eventual Python-side UPPAAL API design

## Topic-to-Page Quick Map

If a future writer wants the shortest answer to "where should this topic go?",
the current answer is:

- `fed`: page 6
- `CDD`: page 7
- search loop / waiting / passed / inclusion / extrapolation: page 8
- urgent / committed / partial order: page 9
- priced timed automata / cost optimality: page 10
- representation comparison and family tree: page 11
- Python-side reconstruction strategy: page 12
- basic properties and query intuition: page 3

## Final Editorial Summary

The key editorial decision is:

Do not write "theory notes for UDBM internals only."

Write a beginner-friendly but technically honest tutorial line for the broader
UPPAAL symbolic-verification ecosystem, with UDBM placed inside that ecosystem
as the DBM/federation foundation rather than treated as the whole story.
