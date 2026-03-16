# UDBM Code Guide

## Scope and Goal

This document is a source-reading guide for the native `UDBM/` submodule, not for the Python wrapper in `pyudbm/`.

The goal is to answer four questions:

1. What is the overall structure of UDBM as a project?
2. What does each major module do?
3. Which local papers in [`papers/`](../papers/README.md) explain the theory behind each module?
4. Which substantial parts of the current codebase are not really covered by the current local paper set?

The intended audience is someone reading the native code and wanting a paper-backed mental model of the implementation.

## What UDBM Is

UDBM is the symbolic zone-manipulation library that sits below UPPAAL-style timed verification.

It is not a full model checker. It does not contain the complete timed-automata reachability engine, parser, query language, or product construction. Instead, it implements the symbolic data structures and operations that the model checker needs:

- difference-bound matrices (DBMs) for convex zones
- federations, meaning finite unions of DBMs
- minimal-graph compression of DBMs
- priced DBMs and priced federations
- helper structures for valuations, printing, random generation, and reduction support

At build time, the native library is assembled from the sources listed in `UDBM/src/CMakeLists.txt`. Conceptually, those sources fall into five layers:

1. Raw DBM kernel in C
2. C++ ownership, interning, and federation layer
3. Minimal-graph compression layer
4. Priced-zone extension
5. Support and utility modules

## Architectural Overview

### Core mathematical model

The basic semantic object is a **zone** over clocks `x0, x1, ..., xn`, where `x0` is the reference clock. A DBM is a square matrix of encoded constraints of the form:

`xi - xj < c` or `xi - xj <= c`

Internally:

- bounds are stored as encoded `raw_t` values
- canonical closed DBMs are the central invariant
- emptiness, inclusion, delay, reset, intersection, extrapolation, and normalization are expressed as DBM operations

Above that:

- a `dbm_t` is an owning C++ wrapper around one canonical DBM
- a `fed_t` is a finite union of DBMs
- a `mingraph_t` is a compact representation of a DBM using only the non-redundant constraints
- a `PDBM` is a priced DBM, meaning a zone plus an affine cost function
- a `pfed_t` is a union of priced DBMs

### Practical code split

The public headers in `UDBM/include/dbm/` define the conceptual API boundaries. The files in `UDBM/src/` contain the implementations.

The split is fairly consistent:

- `constraints.h`, `dbm.h`, `priced.h`, `mingraph.h` define the low-level mathematical kernels
- `fed.h`, `pfed.h`, `partition.h`, `valuation.h` define higher-level C++ objects
- `inline_fed.h` and `DBMAllocator.*` hold the internal ownership model behind `dbm_t` and `fed_t`
- `print.*` and `gen.*` are support code for debugging, experiments, and tests

## Best Paper Set for Reading the Code

If the goal is to understand the native UDBM implementation itself, the best reading path in this repository is:

1. [`by04`](../papers/by04/README.md)
2. [`bengtsson02`](../papers/bengtsson02/README.md)
3. [`dhlp06`](../papers/dhlp06/README.md)
4. [`bblp04`](../papers/bblp04/README.md)
5. [`llpy97`](../papers/llpy97/README.md)
6. [`behrmann03`](../papers/behrmann03/README.md) for priced and broader system-level structures

In practice:

- `by04` gives the cleanest semantic baseline and the appendix algorithms that look most like the code.
- `bengtsson02` is the closest long-form match to the implementation shape of raw DBMs, normalization, storage, and hashing.
- `dhlp06` explains why federation subtraction and reduction matter.
- `bblp04` explains extrapolation and why there are several extrapolation operators.
- `llpy97` explains why `mingraph` exists at all.
- `behrmann03` gives the broader architecture around bound matrices, priced zones, minimal forms, and tool-level design.

## Module Map

| Module | Main Files | Main Responsibility | Best Paper Anchors |
| --- | --- | --- | --- |
| Constraint encoding and raw DBM views | `constraints.h`, `dbm_raw.hpp` | Encoded bounds, raw matrix access, basic representation conventions | `by04` §4.1, `bengtsson02` Paper A §2 |
| Raw DBM kernel | `dbm.h`, `dbm.c` | Closure, intersection, relation, delay, reset, free, point inclusion, extrapolation, dimension-changing operations | `by04` §4.1-§4.4 and Appendix, `bengtsson02` Paper A §3-§4, Paper B §3-§4, `bblp04` §3-§5 |
| C++ DBM and federation API | `fed.h`, `fed_dbm.cpp`, `fed.cpp` | `dbm_t`, `fed_t`, set operations, reductions, exact relations, predecessor/successor-style operations, valuation extraction | `by04`, `dhlp06` §4-§5, `bengtsson02` Paper A, partial support from `behrmann03` |
| Internal ownership and interning | `inline_fed.h`, `DBMAllocator.h`, `DBMAllocator.cpp` | Copy-on-write, reference counting, internalized DBMs, hash-consing, custom allocators | Only indirect background in current papers |
| Minimal graph and compression | `mingraph.h`, `mingraph.c`, `mingraph_read.c`, `mingraph_write.c`, `mingraph_relation.c`, `mingraph_equal.c`, `mingraph_cache.*` | Sparse/minimal constraint sets, compact encodings, comparison against compressed DBMs | `llpy97`, `by04` §4.4 and Appendix Algorithms 3-4, `bengtsson02` Paper A §2.2 and §4.3, Paper C §3 |
| Priced DBMs | `priced.h`, `priced.cpp`, `infimum.h`, `infimum.cpp` | Zones with affine cost functions, cost infimum, facets, zero cycles, normal form, priced extrapolation | `behrmann03` §3.4, §4.4, §4.5, Paper D §4, Paper E §2.3-§2.4, Paper F §4-§5 |
| Priced federations | `pfed.h`, `pfed.cpp` | Unions of priced DBMs, cost-aware delay and update splitting along facets | Mostly `behrmann03` Papers D-F, but only partial coverage of the exact code structure |
| Partition support | `partition.h`, `partition.cpp` | Partitioned handling of federations during reduction | Only very indirect support in current papers |
| Valuations and names | `valuation.h`, `valuation.cpp`, `ClockAccessor.h` | Clock valuations, delay extraction between points, name-aware rendering | Background only; papers assume valuations semantically but do not focus on these classes |
| Printing and generation | `print.h`, `print.cpp`, `gen.h`, `gen.c` | Debug printing and random DBM/point generation | Support code, not a major paper-driven area |

## Detailed Module Guide

### 1. Constraint Encoding and Raw Access Layer

#### Files

- `UDBM/include/dbm/constraints.h`
- `UDBM/include/dbm/dbm_raw.hpp`

#### What this layer does

This is the foundation that everything else builds on.

`constraints.h` defines:

- `raw_t` as the encoded bound type
- the bound encoding scheme for strict and weak inequalities
- `constraint_t`
- helpers such as `dbm_bound2raw`, `dbm_raw2bound`, `dbm_addRawRaw`, `dbm_negRaw`, and strictness manipulation helpers

`dbm_raw.hpp` adds small non-owning C++ wrappers:

- `dbm::reader`
- `dbm::writer`

These wrappers do not add new DBM semantics. They exist to make C++ code more readable and safer when passing raw DBM matrices around.

#### Why it matters

If you do not understand the encoded bound convention, the rest of the code is hard to read. Nearly every algorithm in `dbm.c`, `mingraph_*`, `priced.cpp`, and `infimum.cpp` manipulates `raw_t` values directly.

#### Best paper mapping

Read these parts first:

- [`by04`](../papers/by04/README.md): §4.1 "DBM Basics"
- [`bengtsson02`](../papers/bengtsson02/README.md): Paper A §2 "DBM basics"

Those sections explain:

- how constraints are stored in matrix form
- why canonical DBMs represent convex zones
- how graph-style shortest-path reasoning maps to DBM closure

#### Coverage quality

This layer is conceptually covered well by the papers. The exact bit-level encoding helpers are implementation detail, but they are straightforward consequences of the standard DBM representation.

### 2. Raw DBM Kernel

#### Files

- `UDBM/include/dbm/dbm.h`
- `UDBM/src/dbm.c`

#### What this layer does

This is the mathematical engine of ordinary DBMs. It is the single most important module in UDBM.

The public API contains the standard zone operations:

- initialization and zero DBMs
- convex union and intersection
- constraint addition
- delay and inverse delay: `dbm_up`, `dbm_down`
- stopped-clock variants: `dbm_up_stop`, `dbm_down_stop`
- resets and updates: `dbm_updateValue`, `dbm_updateClock`, `dbm_updateIncrement`, `dbm_update`
- clock elimination and relaxation: `dbm_freeClock`, `dbm_freeUp`, `dbm_freeDown`, `dbm_relax*`
- closure and incremental closure: `dbm_close`, `dbm_closex`, `dbm_close1`, `dbm_closeij`
- property checks: emptiness, closure, unboundedness, relation, subset
- point membership for integer and real valuations
- extrapolation: `Extra_M`, diagonal `Extra_M`, `Extra_LU`, diagonal `Extra_LU`
- dimension-changing helpers such as shrink/expand and clock swapping
- validation and hashing

#### How to think about the implementation

This file is where the standard symbolic-zone calculus is encoded as low-level algorithms over raw matrices.

The key invariants are:

- DBMs are expected to be canonical or brought back to canonical form after updates
- emptiness is detected via diagonal inconsistency
- closure is the central repair step after many local modifications
- a DBM is both a matrix object and a shortest-path graph object

The raw kernel is intentionally C-like because it is meant to be reusable, efficient, and easy to wrap.

#### Best paper mapping

This module maps very directly to the literature.

Primary references:

- [`by04`](../papers/by04/README.md)
  - §3.1-§3.4 for the symbolic semantics around zones
  - §4.1 "DBM Basics"
  - §4.2 "Basic Operations on DBMs"
  - §4.3 "Zone-Normalization"
  - §4.4 "Zones in Memory"
  - Appendix Algorithms 2-17, especially `close`, `relation`, `up`, `down`, `and`, `free`, `reset`, `copy`, `shift`, and normalization
- [`bengtsson02`](../papers/bengtsson02/README.md)
  - Paper A §2.1-§2.2 on canonical DBMs and minimal constraint systems
  - Paper A §3.1-§3.3 on property checking, transformations, and normalization
  - Paper A §4 on zone storage
  - Paper B §3-§4 on normalization with clock-difference constraints
- [`bblp04`](../papers/bblp04/README.md)
  - §3 "Maximum Bound Abstractions"
  - §4 "Extrapolation Using Zones"
  - §5 "Acceleration of Successor Computation"

#### What is especially well covered

The papers cover the heart of this module extremely well:

- canonical closure
- relation and inclusion
- delay and inverse delay
- guard intersection
- reset/copy/shift/free
- normalization
- extrapolation

#### What is only weakly covered here

Two parts of `dbm.c` are noticeably less well covered by the local papers:

- the stopped-clock operations `dbm_up_stop` and `dbm_down_stop`
- the exact floating-point behavior of `dbm_isRealPointIncluded`

The first is a real semantic extension, not just a minor implementation trick. The second matters because the actual code runs on machine doubles, while papers usually present exact dense-time semantics.

### 3. C++ DBM and Federation Layer

#### Files

- `UDBM/include/dbm/fed.h`
- `UDBM/include/dbm/inline_fed.h`
- `UDBM/src/fed_dbm.cpp`
- `UDBM/src/fed.cpp`
- `UDBM/src/DBMAllocator.h`
- `UDBM/src/DBMAllocator.cpp`

#### What this layer does

This is the main object-oriented layer of ordinary UDBM.

It introduces:

- `dbm_t`: owning C++ wrapper for one DBM
- `fed_t`: finite union of DBMs
- internal objects such as `idbm_t`, `ifed_t`, `fdbm_t`, `dbmlist_t`

The public behavior includes:

- copy-on-write DBMs and federations
- direct set-style operations on federations
- `relation()` and `exactRelation()`
- reduction operations: `reduce`, `mergeReduce`, `convexReduce`, `partitionReduce`
- delay and inverse delay lifted to federations
- subtraction and non-convex result handling
- predecessor and successor style operators such as `predt` and `succt`
- extraction of one satisfying valuation
- pointwise delay queries such as `getMinDelay` and `getMaxDelay`

#### Internal design ideas

This layer is not only a convenience wrapper. It is where UDBM becomes a practical symbolic-state engine rather than just a matrix toolkit.

The important design points are:

- reference-counted ownership
- copy-on-write mutation
- interning identical canonical DBMs in a hash table
- cheap equality and sharing when DBMs are interned
- federations as explicit lists of DBMs, not as some opaque symbolic structure

`inline_fed.h` and `DBMAllocator.*` are especially important because they define the actual runtime object model:

- `idbm_t` stores the internal DBM object
- `DBMTable` is the hash table for internalized DBMs
- `DBMAllocator` and the item allocators manage custom memory pools
- mutable vs immutable behavior is driven by reference count and hashed state

#### Best paper mapping

This layer has mixed paper coverage: some parts map very directly, while some are mostly engineering.

Strong coverage:

- [`by04`](../papers/by04/README.md)
  - the DBM-level semantics that `dbm_t` wraps
- [`dhlp06`](../papers/dhlp06/README.md)
  - §4 "DBM Subtraction"
  - §5 "Reducing DBM Subtractions"
  - this is the main theoretical background for federation subtraction and reduction heuristics
- [`bengtsson02`](../papers/bengtsson02/README.md)
  - Paper A for DBM operations and storage assumptions
  - Paper C for memory-conscious representation and hashing-oriented implementation concerns

Partial or indirect coverage:

- [`behrmann03`](../papers/behrmann03/README.md)
  - §4.2 "Bound Matrices"
  - §5.1-§5.2 on tool architecture and surrounding symbolic data structures

#### What each paper explains here

`by04` explains why `dbm_t` has the operations it has.

`dhlp06` explains why `fed_t` is necessary at all, especially for:

- subtraction
- non-convex symbolic states
- heuristic reduction after subtraction

`bengtsson02` helps most with:

- canonical DBM assumptions
- minimal constraint thinking
- memory-conscious storage
- packed-state and hashing motivation

#### Coverage quality

The semantic side of `dbm_t` and `fed_t` is covered reasonably well.

The implementation side is not:

- interning
- hash-consing
- custom allocation
- mutable/unhashed vs immutable/hashed transitions
- cached minimal graphs attached to internal DBMs

Those are central content blocks of the actual codebase, but the current local paper set only gives background motivation, not a direct explanation of the concrete implementation.

#### Important content only partly covered

Even inside `fed_t`, several substantial features are only partly represented in the local papers:

- `exactRelation()` versus approximate `relation()`
- `predt`, `succt`, `toLowerBounds`, `toUpperBounds`, `lower2upper`
- pointwise delay-query APIs such as `getMinDelay` and `getMaxDelay`

These are not small helper tricks. They are meaningful operations or service layers on top of federations.

### 4. Minimal Graph and Compression Layer

#### Files

- `UDBM/include/dbm/mingraph.h`
- `UDBM/src/mingraph.c`
- `UDBM/src/mingraph_read.c`
- `UDBM/src/mingraph_write.c`
- `UDBM/src/mingraph_relation.c`
- `UDBM/src/mingraph_equal.c`
- `UDBM/src/mingraph_cache.h`
- `UDBM/src/mingraph_cache.cpp`
- `UDBM/src/mingraph_coding.h`

#### What this layer does

This layer exists to store DBMs more compactly than a full dense matrix when possible.

The main ideas are:

- analyze which DBM constraints are actually necessary
- keep only a minimal or near-minimal constraint set
- choose one of several compact encodings
- support reading, writing, equality, inclusion, and convex union directly against compressed data

This is why the module is larger than a simple serializer. It is not just file-format code. It is a compact symbolic representation layer.

The important operations are:

- `dbm_analyzeForMinDBM`
- `dbm_writeToMinDBMWithOffset`
- `dbm_readFromMinDBM`
- `dbm_relationWithMinDBM`
- `dbm_approxRelationWithMinDBM`
- equality and convex union against a minimal graph

The implementation supports several internal encodings:

- full copy-like layouts
- bit-matrix guided layouts
- encoded `(i, j)` pair layouts
- 16-bit and 32-bit storage variants

There is also a small cache for minimal-graph analysis results in `mingraph_cache.cpp`.

#### Why this layer matters

Canonical DBMs are mathematically convenient, but they are often storage-heavy because many constraints are redundant. UDBM therefore separates:

- the best format for **doing operations**
- the best format for **storing or comparing results**

That separation is one of the most important design ideas in the codebase.

#### Best paper mapping

This module has very strong paper support.

Primary references:

- [`llpy97`](../papers/llpy97/README.md)
  - the main repository-local reference for minimal graphs, redundant constraints, and compact storage
- [`by04`](../papers/by04/README.md)
  - §4.4 "Zones in Memory"
  - Appendix Algorithm 3 and Algorithm 4 on graph reduction
- [`bengtsson02`](../papers/bengtsson02/README.md)
  - Paper A §2.2 "Minimal Constraint Systems"
  - Paper A §4.3 "Storing Sparse Zones"
  - Paper C §3 on packed states and cheap inclusion checks

#### What is especially well covered

The current papers explain the motivation for this layer very well:

- why canonical DBMs contain redundant constraints
- why minimal constraint systems are useful
- why compressed forms matter for memory and inclusion checking

#### What is not fully covered

The exact concrete encoding families in `mingraph_*` are implementation-specific. The papers explain the data-structure idea, but not every individual storage code path used by this implementation. That is expected and not a major gap.

### 5. Priced DBM Layer

#### Files

- `UDBM/include/dbm/priced.h`
- `UDBM/src/priced.cpp`
- `UDBM/src/infimum.h`
- `UDBM/src/infimum.cpp`

#### What this layer does

This module extends plain zones to **priced zones**.

A priced DBM consists of:

- an ordinary DBM zone
- an affine cost plane over that zone
- a cost at the offset point
- per-clock rates

The public API supports:

- priced DBM allocation and reference counting
- constraint application and relation checking
- cost infimum queries
- point containment
- delay and reset-like updates with cost semantics
- priced extrapolation
- facet extraction
- zero-cycle detection
- rate access and normal-form operations
- minimal-graph read/write for priced DBMs

#### Key concepts in the implementation

This code is not merely "ordinary DBMs plus one extra number". It has its own mathematical layer.

Important concepts include:

- cost offsets and rate vectors
- infimum computation over a zone
- zero cycles and rate transfer across equivalent clocks
- facet-based updates
- normal forms for priced zones

The most algorithmically distinct file here is `infimum.cpp`, which computes the cost infimum using a network-simplex-style algorithm on a dual network-flow formulation.

#### Best paper mapping

This module is mainly explained by [`behrmann03`](../papers/behrmann03/README.md).

Most relevant parts:

- thesis §3.4 "Priced Timed Automata"
- thesis §4.4 "Priced Zones"
- thesis §4.5 "Minimal Constraint Form"
- thesis section "Stopwatches in Uppaal" for broader context
- Paper D §4 "Symbolic Semantics and Algorithm"
- Paper E §2.3-§2.4 on symbolic semantics and cost-function representation
- Paper F §4 "Priced Zones"
- Paper F §5 "Facets & Operations on Priced Zones"

Secondary support:

- [`bblp04`](../papers/bblp04/README.md) helps for extrapolation structure, though it is not a priced-zones paper
- `by04` remains useful as the ordinary DBM baseline underneath the priced extension

#### What is especially well covered

The local paper set covers these ideas reasonably well:

- what priced zones are
- why facets matter
- how symbolic cost-optimal reachability is organized
- why minimal forms and compact representations remain important

#### What is only partially covered

The exact algorithmic internals in the current implementation go beyond what the local papers directly explain:

- the detailed network-simplex-style solver in `infimum.cpp`
- the concrete `pdbm_findZeroCycle` and `dbm_findZeroCycles` machinery
- the exact normal-form implementation in `pdbm_normalise`
- the full set of rate-transfer details used during extrapolation and reset-like operations

These are substantial pieces of code, not merely local micro-optimizations.

### 6. Priced Federation Layer

#### Files

- `UDBM/include/dbm/pfed.h`
- `UDBM/src/pfed.cpp`

#### What this layer does

`pfed_t` is the priced analogue of `fed_t`: a union of priced DBMs.

Its implementation is much smaller than ordinary `fed_t`, but conceptually it is important because priced operations often split a zone along facets and therefore naturally produce unions.

Examples in the code:

- `pfed_t::up(int32_t rate)` may split a zone along lower or upper facets depending on the relation between the old and new delay rates
- `pfed_t::updateValue(clock, value)` may likewise split along relative facets depending on the sign of the relevant rate

#### Best paper mapping

The best available local source is again [`behrmann03`](../papers/behrmann03/README.md), especially Papers D-F.

Most relevant ideas:

- priced symbolic semantics
- priced zones
- facets
- cost-preserving symbolic transformations

#### Coverage quality

The **conceptual reason** for priced federations is covered.

The **exact shape of this code** is not. In particular:

- the exact high-level API and algebra of `pfed_t`
- the specific union-building control flow used in `pfed.cpp`
- the gaps where operations are not implemented

are not directly explained by the current local papers.

### 7. Partition Layer

#### Files

- `UDBM/include/dbm/partition.h`
- `UDBM/src/partition.cpp`

#### What this layer does

`partition_t` stores a partition of federations indexed by IDs and keeps the stored federations disjoint.

In the broader codebase, it is used as a structural aid for reduction:

- instead of reducing one large federation monolithically
- split it into disjoint subproblems
- reduce partitions separately
- then combine the results

This is not just a small helper. It is a deliberate data-structure choice for scaling reduction behavior.

#### Best paper mapping

Current local papers only support this module indirectly.

Closest background:

- [`dhlp06`](../papers/dhlp06/README.md) for subtraction and reduction pressure in federations
- [`behrmann03`](../papers/behrmann03/README.md) for the broader tool-architecture mindset

#### Coverage quality

This module is one of the clearest examples of code content that the current local papers do **not** directly cover.

The papers motivate non-convex unions and reductions, but they do not explain this explicit partition data structure and its concrete algorithmic role in the implementation.

### 8. Valuation, Naming, Printing, and Generation Support

#### Files

- `UDBM/include/dbm/valuation.h`
- `UDBM/src/valuation.cpp`
- `UDBM/include/dbm/ClockAccessor.h`
- `UDBM/include/dbm/print.h`
- `UDBM/src/print.cpp`
- `UDBM/include/dbm/gen.h`
- `UDBM/src/gen.c`

#### What these modules do

These are support layers around the main symbolic structures.

`valuation.h` and `valuation.cpp` provide:

- integer and floating-point clock valuations
- simple operations such as uniform delay shifts
- rendering through `ClockAccessor`
- helper logic like `get_delay_to`

`ClockAccessor.h` provides an abstract naming interface for clocks.

`print.*` provides:

- readable DBM pretty-printing
- diff printing
- constraint and bound rendering
- C and C++ printing front-ends

`gen.*` provides random generation of:

- DBMs
- subsets and supersets
- argument DBMs for intersection/subtraction testing
- integer and real points inside zones

#### Best paper mapping

These modules are not major theory modules. They are mostly engineering support.

The papers support them only indirectly:

- the semantics of valuations obviously come from the DBM theory
- printing reflects DBM constraints
- generation code is mainly for testing and experimentation

#### Coverage quality

It is normal that the local paper set does not discuss these files in much detail.

## Source Reading Order

If you want to read the code in a dependency-aware order, this sequence works well:

1. `constraints.h`
   Understand the raw bound encoding first.
2. `dbm.h` and `dbm.c`
   Read these with `by04` §4 and `bengtsson02` Paper A open.
3. `fed.h`, `fed_dbm.cpp`, `fed.cpp`
   Read these with `dhlp06` open once the raw DBM operations are familiar.
4. `mingraph.h` and `mingraph_*`
   Read these with `llpy97` and the storage sections of `bengtsson02`.
5. `priced.h`, `priced.cpp`, `infimum.cpp`
   Read these with `behrmann03` Papers D-F.
6. `pfed.h`, `pfed.cpp`
   Read after you understand priced DBMs and facets.
7. `partition.h`, `partition.cpp`
   Read after the federation reductions in `fed.cpp` make sense.
8. `valuation.*`, `print.*`, `gen.*`
   Read last as support code.

## Coverage Audit: What the Current Local Papers Cover Well

The current `papers/` set covers the main UDBM theory backbone well:

- ordinary DBM semantics and canonical closure
- basic DBM operations such as `up`, `down`, `free`, `reset`, `copy`, and relation checking
- normalization and extrapolation
- federation subtraction and heuristic reduction
- minimal-graph representations and compact storage
- priced zones, facets, and cost-optimal symbolic reasoning at a high level

That means the conceptual core of UDBM is well anchored in the local papers.

## Coverage Audit: What the Current Local Papers Do Not Really Cover

The important remaining gaps are not just tiny local tricks. They are substantial code-content areas.

### A. Largely uncovered content

#### 1. Concrete ownership, interning, and allocator architecture

This includes:

- `idbm_t`
- `DBMTable`
- `DBMAllocator`
- copy-on-write transitions
- hashed versus mutable DBMs
- allocator-backed internal federation objects
- mingraph caching attached to internal DBMs

Why this is a real gap:

- it is a major part of how UDBM behaves as a library
- it determines memory sharing, mutation cost, and equality behavior
- the current local papers mostly provide motivation, not the concrete design

#### 2. Stopped-clock semantics

This includes:

- `dbm_up_stop`
- `dbm_down_stop`
- `dbm_t::upStop`
- `dbm_t::downStop`
- `fed_t::upStop`
- `fed_t::downStop`

Why this is a real gap:

- this is a semantic feature, not just a local optimization
- the current local paper set does not directly explain the corresponding algorithms in the code

#### 3. Pointwise delay-query APIs

This includes:

- `dbm_t::getMinDelay`
- `dbm_t::getMaxDelay`
- `fed_t::getMinDelay`
- `fed_t::getMaxDelay`
- valuation extraction behavior beyond plain containment tests

Why this is a real gap:

- these APIs are service-level operations over zones and federations
- the current papers discuss symbolic transformers, but not this concrete query layer over a fixed valuation

#### 4. Partition-based federation reduction

This includes:

- `partition_t`
- `partition.cpp`
- `fed_t::partitionReduce()`

Why this is a real gap:

- the current papers explain why reduction matters
- they do not explain this explicit partition data structure or its algorithmic workflow

#### 5. Machine numeric semantics for real-point operations

This includes:

- `dbm_isRealPointIncluded`
- floating-point point membership
- double-based delay queries
- real-point tests and edge handling

Why this is a real gap:

- papers usually present exact dense-time semantics
- the code must commit to finite-precision `double` behavior and boundary handling
- this can affect observed behavior in real runs

### B. Only partially covered content

#### 1. Exact versus approximate set relations on federations

The split between:

- approximate `relation()`
- subtraction-backed `exactRelation()`

is important in the API and implementation. The underlying set-theoretic issue is standard, but this specific dual-API design is not really explained by the local papers.

#### 2. `predt`, `succt`, and bound-transform families

This includes:

- `predt`
- `succt`
- `toLowerBounds`
- `toUpperBounds`
- `lower2upper`

These are related to federation subtraction and backward reasoning, but the current local papers do not directly explain the current implementation family in `fed.cpp`.

#### 3. The exact infimum solver in `infimum.cpp`

The priced-zone papers explain symbolic cost reasoning, but the current local papers do not really walk through the specific network-simplex-style solver used here.

#### 4. Full `pfed_t` algebra as code

The local papers explain priced zones and why unions can appear. They do not fully explain the exact structure of the current priced-federation implementation, especially where the implementation is partial or unfinished.

## Practical Conclusion

If your goal is to understand **most** of UDBM, the existing local papers are already strong enough:

- `by04`
- `bengtsson02`
- `dhlp06`
- `bblp04`
- `llpy97`
- `behrmann03`

If your goal is to understand **all major content blocks in the current source tree**, you will still need to read some parts of the code directly without expecting a one-to-one paper explanation, especially for:

- runtime ownership and interning
- stopped clocks
- pointwise delay queries
- partition-based reduction
- floating-point behavior
- the exact priced infimum solver

That is the main source-reading reality of the current codebase.
