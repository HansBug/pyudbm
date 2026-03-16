# DBM: Structures, Operations and Implementation

Johan Bengtsson

> Note: the local `paper.pdf` is the extracted Paper A from the thesis *Clocks, DBMs and States in Timed Systems*. The Markdown below is a manually refined reading version against that local PDF. All numbered figures are kept as local assets from `paper-a/paper.pdf`, and the unnumbered example DBM matrix shown in the paper is also preserved as an asset.

## Abstract

A key issue when building a verification tool for timed systems is how to handle timing constraints arising in state-space exploration. Difference Bound Matrices (DBMs) are a well-studied technique for representing and manipulating timing constraints. The goal of this paper is to provide a cook-book and a software package for the development of verification tools using DBMs. We present all operations on DBMs needed in symbolic state-space exploration for timed automata, as well as data structures and techniques for efficient implementation.

## 1 Introduction

During the last ten years, timed automata [AD90, AD94] have evolved as a common model for timed systems, and one of the reasons behind their success is the availability of verification tools such as UPPAAL [LPY97, ABB 01] and Kronos [DOTY95, Yov97], which can verify industrial-size applications modelled as timed automata. The major problem in automatic verification is the large number of states induced by state explosion. For timed systems this problem has an even larger impact, since both the number of states and the size of a single state are significantly larger than in the untimed case due to timing constraints. This makes data structures for states and timing constraints one of the key challenges in developing verification tools for timed systems.

This paper describes a software package for representing timing constraints arising from state-space exploration of timed systems as difference bound matrices [Dil89]. The package is based on the DBM implementation of [BL96], but it has been significantly improved using implementation experience gained from developing the current version of UPPAAL. The paper is intended as a cook-book for developers of verification tools and aims to provide a basis for the implementation of state-of-the-art verification tools.

The paper is organised as follows. Section 2 introduces the DBM structure and its canonical form, and also describes how to find the minimal number of constraints needed to represent the same set of clock assignments as a given DBM. Section 3 lists the DBM operations needed to implement a verification tool such as UPPAAL together with efficient algorithms for these operations. Section 4 discusses how to store the structures in memory, and Section 5 concludes the paper.

## 2 DBM Basics

The key objects for representing timing information in symbolic state-space exploration for timed systems are a special class of constraint systems referred to as difference-bound constraint systems, or more commonly, zones. Since zones are frequently used objects, their representation is a major issue when building a verification tool for timed automata.

To have a unified form for clock constraints, the paper introduces a reference clock with constant value `0`. Let

$$
C_0 = C \cup \{0\}.
$$

Then any zone `D` can be rewritten as a conjunction of constraints of the form

$$
x - y \preceq n
\qquad
\text{for } x, y \in C_0,\; \preceq \in \{\le, <\},\; n \in \mathbb{Z}.
$$

Naturally, if the rewritten zone has two constraints on the same pair of variables, only the tightest of them is significant. Thus a zone can be represented using at most `(n + 1)^2` atomic constraints of the form `x_i - x_j \preceq n`, such that each pair of clocks is mentioned only once. We can then store zones as matrices in which each element corresponds to an atomic constraint. Since each matrix element represents a bound on the difference between two clocks, these matrices are called *Difference Bound Matrices* (DBMs). In the following, `D_{ij}` denotes element `(i, j)` in the DBM representing zone `D`.

To compute the DBM representation for a zone, we number all clocks in `C_0` to assign one row and one column in the matrix to each clock. The row is used for storing lower bounds on the difference between the clock and all other clocks, while the column is used for upper bounds. The elements are then computed in three steps:

1. For each bound `x_i - x_j \preceq n` in `D`, let `D_{ij} = (n, \preceq)`.
2. For each clock difference `x_i - x_j` that is unbounded in `D`, let `D_{ij} = \infty`.
3. Add the implicit constraints that all clocks are positive, that is, `0 - x_i \le 0`, and that the difference between a clock and itself is always `0`, that is, `x_i - x_i \le 0`.

The paper illustrates this construction with a small three-clock example and its matrix representation:

![](content_assets/other-1-example-dbm-matrix.png)

*Unnumbered example DBM matrix shown in Paper A after the introductory construction.*

To manipulate DBMs efficiently, we need two operations on bounds: comparison and addition. Bounds are compared lexicographically by integer value and strictness, and addition is defined in the natural way, with `\infty + b = b + \infty = \infty`.

### 2.1 Canonical DBMs

Usually there are infinitely many zones sharing the same solution set. However, for each family of zones with the same solution set there is a unique constraint system in which no atomic constraint can be strengthened without losing solutions. Such a zone is said to be *closed under entailment*, or simply *closed*. Since there is a unique closed zone for each solution set, closed zones are used as the canonical representation of entire families of zones.

To compute the closed representative of a given zone, we need the tightest constraint on each clock difference. The paper solves this using a graph interpretation of zones: clocks are nodes, atomic constraints are weighted edges, and deriving tighter bounds corresponds to adding weights along paths in the graph. In this interpretation DBMs are exactly adjacency matrices.

As a running example, the paper considers the zone

$$
x - 0 < 20 \wedge y - 0 < 20 \wedge x - y \le -10 \wedge y - z \le 5.
$$

Combining the atomic constraints yields a stronger bound on `x - z`, and the graph interpretation makes that strengthening visible as a shortest-path computation.

![](content_assets/figure-1.png)

*Figure 1. Graph interpretation of the example zone and its closed form.*

Thus, deriving the tightest constraint on a pair of clocks in a zone is equivalent to finding the shortest path between their nodes in the graph interpretation of the zone. The conclusion is that a canonical, that is, closed, version of a zone can be computed using a shortest-path algorithm. Many timed-automata verifiers use the Floyd-Warshall algorithm [Flo62] for this purpose:

**Algorithm 1. Floyd's algorithm for computing shortest paths**

```text
for k := 0 to n do
  for i := 0 to n do
    for j := 0 to n do
      Dij := min(Dij, Dik + Dkj)
    end for
  end for
end for
```

Since Floyd-Warshall is cubic in the number of clocks, it is desirable to make frequently used operations preserve canonical form, so that canonicalisation does not have to be recomputed from scratch after every step.

### 2.2 Minimal Constraint Systems

A zone may contain redundant constraints. Removing such constraints is desirable if we want to store only the minimal number of constraints. The paper reviews the line of work from [LLPY97, Pet99, Lar00] showing that each zone has a minimal constraint system with the same solution set, and that sparse storage of such minimal systems may reduce memory usage during state-space exploration.

The problem is stated in graph terms. Closing a DBM corresponds to computing all shortest paths, so the task is to find a minimal set of bounds having a given shortest-path closure. A cycle whose weights sum to `0` is called a *zero cycle*. An edge `x_i -> x_j` is called *redundant* if there is another path from `x_i` to `x_j` whose total weight is no larger than the direct edge.

In graphs without zero cycles, all redundant edges can be removed without affecting the shortest-path closure [Pet99]. If the input graph is already in shortest-path form, all redundant edges can be located by considering alternative paths of length two.

![](content_assets/figure-2.png)

*Figure 2. A zero cycle free graph and its minimal form.*

This yields the following reduction procedure:

**Algorithm 2. Reduction of a zero-cycle-free graph `G` with `n` nodes**

```text
for i := 1 to n do
  for j := 1 to n do
    for k := 1 to n do
      if Gik + Gkj <= Gij then
        mark edge i -> j as redundant
      end if
    end for
  end for
end for
remove all edges marked as redundant
```

However, this algorithm does not work in the presence of zero cycles, because the set of redundant edges is then no longer unique. The paper's solution is to partition nodes according to zero cycles and build a super-graph whose nodes are the partitions.

![](content_assets/figure-3.png)

*Figure 3. A graph with a zero-cycle and its minimal form.*

The reduction then proceeds by reducing the zero-cycle-free super-graph and reconnecting the reduced partitions:

**Algorithm 3. Reduction of a negative-cycle-free graph `G` with `n` nodes**

```text
for i := 1 to n do
  if Nodei is not in a partition then
    Eqi := empty
    for j := i to n do
      if Gij + Gji = 0 then
        Eqi := Eqi union {Nodej}
      end if
    end for
  end if
end for

let G' be a graph without nodes
for each Eqi do
  pick one representative Nodei in Eqi
  add Nodei to G'
  connect Nodei to all nodes in G' using weights from G
end for
reduce G'
for each Eqi do
  add one zero cycle containing all nodes in Eqi to G'
end for
```

With this, the paper obtains an algorithm for computing the minimum number of edges needed to represent a shortest-path closure, and therefore the minimum number of constraints needed to represent a given zone.

## 3 Operations on DBMs

This section presents the DBM operations needed in symbolic state-space exploration of timed automata, both for forward and backward analysis. Even if a verification tool only explores the state space in one direction, these operations are still useful for other purposes, such as generating diagnostic traces.

The paper assumes that clocks in `C_0` are numbered `0, ..., n` with the index for the reference clock equal to `0`, and that input zones are consistent and already in canonical form. The operations are divided into three classes:

1. *Property checking*: consistency, inclusion, and satisfaction of a given atomic constraint.
2. *Transformation*: guard application, delay, and reset-like operations.
3. *Normalisation*: operations used to obtain a finite zone graph.

### 3.1 Checking Properties of DBMs

#### `consistent(D)`

The most basic operation on a DBM is to check whether it is consistent, that is, whether its solution set is non-empty. In state-space exploration this is used to remove inconsistent states from exploration.

For a zone to be inconsistent, there must be at least one pair of clocks whose upper bound is smaller than the corresponding lower bound. In graph terms this means the graph contains a negative-cost cycle. In a canonical DBM this can be detected locally by marking inconsistency through a negative diagonal entry, so it is enough to check whether `D_{00}` is negative.

#### `relation(D, D')`

Another key operation is inclusion checking. For canonical DBMs, the condition

$$
D_{ij} \le D'_{ij}
\qquad
\text{for all } i, j
$$

is necessary and sufficient to conclude that `D \subseteq D'`. The opposite comparison yields `D' \subseteq D`. The paper therefore implements a combined inclusion test returning both answers at once.

#### `satisfied(D, x_i - x_j \preceq m)`

Sometimes it is desirable to check non-destructively whether a zone satisfies an extra constraint, that is, whether

$$
D \wedge (x_i - x_j \preceq m)
$$

is consistent without altering `D`. Since consistency is equivalent to the absence of negative cycles, this check can also be performed locally on canonical DBMs: we only need to test whether `(m, \preceq) + D_{ji}` is negative.

### 3.2 Transformations

#### `up(D)`

The `up` operation computes the strongest postcondition of a zone with respect to delay:

$$
\operatorname{up}(D) = \{u + d \mid u \in D,\; d \in \mathbb{R}_{\ge 0}\}.
$$

Algorithmically, `up` is computed by removing the upper bounds on all individual clocks, that is, by setting every `D_{i0}` to `\infty`. This says that any time assignment in the zone may delay by an arbitrary amount of time. Since all clocks proceed at the same speed, constraints on clock differences are unchanged. The operation preserves canonical form.

#### `down(D)`

The `down` operation computes the weakest precondition of a zone with respect to delay:

$$
\operatorname{down}(D) = \{u \mid u + d \in D,\; d \in \mathbb{R}_{\ge 0}\}.
$$

Intuitively, it is the set of clock valuations that can reach `D` by delaying. A naive implementation would set the lower bound on each individual clock to `(0, \le)`, but difference constraints may then force tighter bounds and destroy canonicity.

![](content_assets/figure-4.png)

*Figure 4. Applying down to a zone.*

To compute the new lower bound for a clock `x`, the paper assumes that all other clocks are `0` and examines all difference constraints `y_i - x`, taking the minimum bound found in the DBM. The resulting bound on `0 - x` gives the correct canonical value.

#### `and(D, x_i - x_j \preceq b)`

The most useful operation in state-space exploration is conjunction, that is, adding a constraint to a zone. The basic step is to check whether `(b, \preceq) < D_{ij}` and, if so, set `D_{ij}` to `(b, \preceq)`. If the bound changes, the DBM must be put back into canonical form. Instead of running a full shortest-path recomputation, the paper derives a specialised `O(n^2)` re-canonicalisation algorithm that takes advantage of the fact that only one bound changed.

#### `free(D, x)`

The `free` operation removes all constraints on a given clock:

$$
\operatorname{free}(D, x) = \{u[x = d] \mid u \in D,\; d \in \mathbb{R}_{\ge 0}\}.
$$

In state-space exploration this is used together with conjunction to implement resets, especially in backward exploration. Simply removing all bounds on `x` and setting `D_{0x} = (0, \le)` does not preserve canonical form. The paper instead derives the new difference constraints on `x` from constraints on the other clocks.

#### `reset(D, x := m)`

In forward exploration, `reset` sets a clock to a specific value:

$$
\operatorname{reset}(D, x := m) = \{u[x = m] \mid u \in D\}.
$$

Without a canonicity requirement, this could be implemented by assigning `D_{x0} = (m, \le)`, `D_{0x} = (-m, \le)`, and deleting other bounds on `x`. The paper instead derives a canonical implementation by reusing the same idea as in `free`.

#### `copy(D, x := y)`

This copies the value of one clock to another:

$$
\operatorname{copy}(D, x := y) = \{u[x = u(y)] \mid u \in D\}.
$$

As with `reset`, a straightforward implementation would delete all bounds on `x` and re-canonicalise. A more efficient implementation sets the equality bounds between `x` and `y` and then copies the remaining bounds on `x` from `y`.

#### `shift(D, x := x + m)`

The last reset-like operation shifts a clock by an integer amount:

$$
\operatorname{shift}(D, x := x + m) = \{u[x = u(x) + m] \mid u \in D\}.
$$

This can be viewed as substituting `x - m` for `x` in the zone. Therefore `m` is added to upper bounds on `x`, while `m` is subtracted from lower bounds, which are represented through constraints on differences of the form `y - x`.

### 3.3 Normalisation Operations

To obtain a finite zone graph, verifiers apply normalisation operations to zones. The paper describes the classical `k`-normalisation with respect to the maximum constant each clock is compared to in the automaton.

#### `norm_k(D)`

Operationally, `k`-normalisation removes all upper bounds larger than the maximal constants and lowers all lower bounds larger than the maximal constants down to those constants. On a canonical DBM this consists of two steps:

1. remove all bounds `x_i - x_j \preceq m` such that `(m, \preceq) > (k_i, \le)`;
2. set all bounds `x_i - x_j \preceq m` such that `(m, \preceq) < (-k_j, <)` to `(-k_j, <)`.

This corresponds to forgetting exact values once they exceed the maximal relevant constants. The operation does not preserve canonical form, so the resulting DBM is closed again using Floyd-Warshall.

The paper closes the section with a visual summary of the operations:

![](content_assets/figure-5.png)

*Figure 5. All DBM operations applied to the same zone.*

## 4 Zones in Memory

This section discusses several techniques for storing zones in computer memory. It starts with the encoding of individual DBM elements, continues with two layouts for storing two-dimensional DBMs in linear memory, and ends with sparse representations.

### 4.1 Storing DBM Elements

To store a DBM element in memory, we need both the integer bound and the information about whether the bound is strict. Since the integer range is typically far below the full range of a machine word, and strictness needs only one bit, the paper proposes storing both in a single machine word.

The least significant bit (LSB) stores strictness. Since strict bounds are smaller than non-strict ones, a set bit (`1`) denotes a non-strict bound, while an unset bit (`0`) denotes a strict bound. The remaining bits store the integer bound itself. The value `\infty` is encoded using the largest positive machine integer, denoted `MAX_INT`.

For good performance, addition on encoded bounds must also be efficient:

**Algorithm 4. Adding encoded bounds**

```text
if b1 = MAX_INT or b2 = MAX_INT then
  return MAX_INT
else
  return b1 + b2 - ((b1 & 1) | (b2 & 1))
end if
```

### 4.2 Placing DBMs in Memory

Another implementation issue is how to place two-dimensional DBMs in linear memory. The natural layout stores matrix elements row-wise (or symmetrically, column-wise), so that each row is consecutive in memory. Its main advantage is performance, because the location function is simple:

$$
\operatorname{loc}(x, y) = x \cdot (n + 1) + y.
$$

The second layout is a layered model in which each layer consists of the bounds between a clock and the clocks with lower index in the DBM. This makes local clocks cheap to implement, since all information about them is concentrated at the end of the DBM, but the index mapping becomes more complicated:

$$
\operatorname{loc}(x, y) =
\begin{cases}
y \cdot (y + 1) + x & \text{if } x \le y, \\
x \cdot x + y & \text{otherwise.}
\end{cases}
$$

The layered mapping adds at least one comparison and one conditional branch, and it also tends to behave worse in the cache.

![](content_assets/figure-6.png)

*Figure 6. Different layouts of DBMs in memory.*

The paper's conclusion is pragmatic: unless the verifier supports dynamically adding and removing clocks, the row-wise mapping should be used. If the tool supports local clocks, the layered mapping may be preferable because no reordering of the DBM is then needed when entering or leaving a clock scope.

### 4.3 Storing Sparse Zones

In most verification tools, the majority of zones are stored in the set of already visited states, where they are used to guarantee termination by preventing repeated exploration. For these states it may be beneficial to store only the minimal number of constraints using a sparse representation.

A straightforward implementation stores a sparse zone as a vector of constraints of the form `(x, y, b)`. Additional memory can be saved by omitting implicit constraints such as `0 - x \le 0`. A drawback is that each stored constraint must now explicitly store clock indices, so unless at least half of the constraints in a full DBM are redundant, sparse storage does not actually save space.

One attractive feature of sparse representations is that checking whether a full DBM `D_f` is included in a sparse zone `D_s` does not require reconstruction of the full DBM for `D_s`: it is enough to check that every constraint stored in `D_s` is at least as loose as the corresponding bound in `D_f`. The reverse inclusion test still requires reconstructing the full DBM for the sparse zone.

## 5 Conclusions

The paper reviews Difference Bound Matrices as a data structure for timing constraints. It presents the basic representation, the primitive DBM operations needed in symbolic state-space exploration of timed automata, algorithms for canonicalisation and reduction, and several implementation choices for storing both dense and sparse zones efficiently in memory.

## References

`[ABB 01]` Tobias Amnell, Gerd Behrmann, Johan Bengtsson, Pedro R. D'Argenio, Alexandre David, Ansgar Fehnker, Thomas Hune, Bertrand Jeannet, Kim G. Larsen, M. Oliver Moller, Paul Pettersson, Carsten Weise, and Wang Yi. *UPPAAL - Now, Next, and Future*. In *Modelling and Verification of Parallel Processes*, volume 2067 of Lecture Notes in Computer Science, pages 100-125. Springer-Verlag, 2001.

`[AD90]` Rajeev Alur and David L. Dill. *Automata for modeling real-time systems*. In *Proceedings, Seventeenth International Colloquium on Automata, Languages and Programming*, volume 443 of Lecture Notes in Computer Science, pages 322-335. Springer-Verlag, 1990.

`[AD94]` Rajeev Alur and David L. Dill. *A theory of timed automata*. *Theoretical Computer Science*, 126(2):183-235, 1994.

`[BL96]` Johan Bengtsson and Fredrik Larsson. *UPPAAL a tool for automatic verification of real-time systems*. Technical Report 96/67, Department of Computer Systems, Uppsala University, 1996.

`[BY01]` Johan Bentsson and Wang Yi. *Reachability analysis of timed automata containing constraints on clock differences*. Submitted for publication, 2001.

`[Dil89]` David L. Dill. *Timing assumptions and verification of finite-state concurrent systems*. In *Proceedings, Automatic Verification Methods for Finite State Systems*, volume 407 of Lecture Notes in Computer Science, pages 197-212. Springer-Verlag, 1989.

`[DOTY95]` Conrado Daws, Alfredo Olivero, Stavros Tripakis, and Sergio Yovine. *The tool Kronos*. In *Proceedings, Hybrid Systems III: Verification and Control*, volume 1066 of Lecture Notes in Computer Science. Springer-Verlag, 1995.

`[Flo62]` Robert W. Floyd. *Acm algorithm 97: Shortest path*. *Communications of the ACM*, 5(6):345, June 1962.

`[Lar00]` Fredrik Larsson. *Efficient implementation of model-checkers for networks of timed automata*. Licentiate Thesis 2000-003, Department of Information Technology, Uppsala University, 2000.

`[LLPY97]` Kim G. Larsen, Fredrik Larsson, Paul Pettersson, and Wang Yi. *Efficient verification of real-time systems: Compact data structure and state space reduction*. In *Proceedings, 18th IEEE Real-Time Systems Symposium*, pages 14-24. IEEE Computer Society Press, 1997.

`[LPY97]` Kim G. Larsen, Paul Petterson, and Wang Yi. *UPPAAL in a nutshell*. *Journal on Software Tools for Technology Transfer*, 1997.

`[Pet99]` Paul Pettersson. *Modelling and Verification of Real-Time Systems Using Timed Automata: Theory and Practice*. PhD thesis, Uppsala University, 1999.

`[Yov97]` Sergio Yovine. *Kronos: a verification tool for real-time systems*. *Journal on Software Tools for Technology Transfer*, 1, October 1997.

## Appendix: Pseudo-Code

### Algorithm 5 `relation(D, D')`

```text
fDsubsetD' := true
fDsupsetD' := true
for i := 0 to n do
  for j := 0 to n do
    fDsubsetD' := fDsubsetD' and (Dij <= D'ij)
    fDsupsetD' := fDsupsetD' and (Dij >= D'ij)
  end for
end for
return <fDsubsetD', fDsupsetD'>
```

### Algorithm 6 `up(D)`

```text
for i := 1 to n do
  Di0 := infinity
end for
```

### Algorithm 7 `down(D)`

```text
for i := 1 to n do
  D0i := (0, <=)
  for j := 1 to n do
    if Dji < D0i then
      D0i := Dji
    end if
  end for
end for
```

### Algorithm 8 `and(D, g)`

```text
if Dyx + (m, <=) < 0 then
  D00 := (-1, <=)
else if (m, <=) < Dxy then
  Dxy := (m, <=)
  for i := 0 to n do
    for j := 0 to n do
      if Dix + Dxj < Dij then
        Dij := Dix + Dxj
      end if
      if Diy + Dyj < Dij then
        Dij := Diy + Dyj
      end if
    end for
  end for
end if
```

### Algorithm 9 `free(D, x)`

```text
for i := 0 to n do
  if i != x then
    Dxi := infinity
    Dix := Di0
  end if
end for
```

### Algorithm 10 `reset(D, x := m)`

```text
for i := 0 to n do
  Dxi := (m, <=) + D0i
  Dix := Di0 + (-m, <=)
end for
```

### Algorithm 11 `copy(D, x := y)`

```text
for i := 0 to n do
  if i != x then
    Dxi := Dyi
    Dix := Diy
  end if
end for
Dxy := (0, <=)
Dyx := (0, <=)
```

### Algorithm 12 `shift(D, x := x + m)`

```text
for i := 0 to n do
  if i != x then
    Dxi := Dxi + (m, <=)
    Dix := Dix + (-m, <=)
  end if
end for
D0x := max(D0x, (0, <=))
Dx0 := min(Dx0, (0, <=))
```

### Algorithm 13 `norm_k(D)`

```text
for i := 0 to n do
  for j := 0 to n do
    if Dij != infinity and Dij > (ki, <=) then
      Dij := infinity
    else if Dij != infinity and Dij < (-kj, <) then
      Dij := (-kj, <)
    end if
  end for
end for
close(D)
```
