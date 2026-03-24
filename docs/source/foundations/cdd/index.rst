CDD Basics: How Shared Decision Graphs Compress Non-Convex Symbolic Sets
=========================================================================

.. currentmodule:: pyudbm.binding.ucdd

This page continues naturally from :doc:`../federations/index`.
Federations already show that finite unions of DBMs can represent non-convex
sets exactly. CDDs push on the next question: **once a verifier accumulates many
related non-convex pieces, can they be stored as one shared decision structure
instead of as a long flat DBM list?** [UPP_VER_CDD]_ [BEHR03_CDD_PAGE]_
[UCDD_REPO]_.

That is why the most direct way into CDDs is to start with the shared-graph
idea itself. CDDs reuse that idea, but apply it to clock-difference
constraints rather than only to boolean conditions.

This page connects four layers:

* how BDDs use shared graphs to represent condition structure
* how CDDs transfer that idea to clock-difference constraints
* why explicit DBM lists become a bottleneck in verification workflows
* what the current `UCDD` and :mod:`pyudbm.binding.ucdd` layers expose, and what those operations mean algorithmically

From BDDs To CDDs: Why Shared Graphs Matter
-------------------------------------------

BDD Intuition: Shared Decision Graphs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A binary decision diagram is best understood first as a structural idea.

Its core move is simple: represent a boolean function as a shared DAG rather
than as a fully expanded decision tree or truth table.

For example, consider

.. math::

   f(a,b,c) = (a \land c) \lor (\neg a \land b \land c).

Evaluating this function means answering a sequence of boolean questions:

* is :math:`a` true or false?
* then perhaps inspect :math:`b` or :math:`c`
* finally reach a ``True`` or ``False`` terminal

.. graphviz:: bdd_basics.dot

The most important thing to notice is the shared ``c`` node. Two different
paths reuse the same suffix instead of duplicating it. That is exactly what
makes the diagram useful as a data structure rather than just as a picture.

For this tutorial, the most useful BDD-level picture is just this:

* it represents a boolean function
* each inner node asks about one boolean variable
* edges typically mean ``0`` / ``1`` or ``False`` / ``True``
* the structure is a **shared graph**, not a tree with all suffixes copied

With that in mind, the move to CDDs becomes natural:

* BDD inner nodes test boolean variables
* CDD inner nodes test **which interval contains one clock difference**
* BDD edges are labeled by ``0`` / ``1``
* CDD edges are labeled by intervals

So a CDD reuses the same structural idea of ordered decisions, shared suffixes,
true/false terminals, and reduced graph maintenance, but swaps boolean-variable
tests for clock-difference interval tests.

Why Look Beyond Explicit Federations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With that BDD intuition in place, the motivation for CDDs becomes much less
abrupt.

In `WAIT` / `PASSED` style reachability, the real pressure point is not whether
one individual zone can be represented, but whether **all zones already seen at
one control location can be stored and queried as one compact symbolic
object**.

The CDD paper makes the relaxed stopping condition explicit [BEHR03_CDD_PAGE]_:

.. math::

   D \subseteq \bigcup \{\, D' \mid (l, D') \in \mathrm{PASSED} \,\}. \tag{1}

In words:

* :math:`D` is the newly generated zone
* the relevant question is whether location :math:`l` is already covered
  collectively by what is in ``PASSED``
* if yes, expanding :math:`D` again is unnecessary

An explicit federation still writes this as

.. math::

   F = D_1 \cup D_2 \cup \cdots \cup D_n,

which is semantically fine. But once non-convexity becomes strong, three costs
become visible:

* the number of DBM pieces may grow quickly
* structurally similar tails cannot be shared across pieces in a plain list
* the practically important question is often “is this new zone included in the
  whole non-convex object?”, not “is one DBM equal to another?”

That is where CDDs enter: **they bring the shared-graph intuition of BDDs into
the clock-constraint world, encoding finite unions of zones as a shared DAG
instead of a permanently flattened DBM list** [BEHR03_CDD_PAGE]_
[UCDD_CDD_H]_.

.. graphviz:: explicit_vs_shared.dot

Both sides of this diagram represent the **same non-convex set**:

.. math::

   F = D_1 \cup D_2 \cup D_3 \cup D_4,

where

.. math::

   \begin{aligned}
   D_1 &: 0 \leq x-y \leq 2,\; 0 \leq x \leq 1,\; 0 \leq y \leq 2, \\
   D_2 &: 0 \leq x-y \leq 2,\; 4 \leq x \leq 5,\; 0 \leq y \leq 2, \\
   D_3 &: 4 \leq x-y \leq 6,\; 0 \leq x \leq 1,\; 0 \leq y \leq 2, \\
   D_4 &: 4 \leq x-y \leq 6,\; 4 \leq x \leq 5,\; 0 \leq y \leq 2.
   \end{aligned}

The left side writes this as four explicit DBMs. The right side rewrites the
same constraints as a shared decision graph:

* first test whether :math:`x-y` lies in ``[0,2]`` or ``[4,6]``
* then test whether :math:`x` lies in ``[0,1]`` or ``[4,5]``
* finally enter the dashed shared-suffix box, where :math:`y \in [0,2]` is checked once

So the point is not just that “the right side has sharing”. It is that for the
same set, the explicit federation repeats the suffix condition
:math:`y \in [0,2]` inside all four DBMs, whereas the CDD keeps that suffix
once and lets multiple earlier branches point to it.

From the current Python wrapper perspective, this is not just historical
background. :mod:`pyudbm.binding.ucdd` now exposes :meth:`CDD.from_federation`,
:meth:`CDD.contains_dbm`, :meth:`CDD.extract_dbm`, and
:meth:`CDD.extract_bdd_and_dbm` directly [PYUDBM_UCDD_PY]_ [PYUDBM_UCDD_CPP]_.
That makes the “CDD <-> DBM / federation” bridge a real user-facing workflow.

The Core Definition: Nodes, Intervals, and Semantics
----------------------------------------------------

The paper-level definition can be compressed into one sentence: **a CDD is an
ordered reduced DAG whose inner nodes inspect one clock difference and whose
outgoing edges are labeled by intervals for that difference.**

Fix a type

.. math::

   t = (i, j), \qquad 1 \leq i < j \leq n

and let

.. math::

   I(i, j)

denote the constraint saying that :math:`X_i - X_j` lies in interval
:math:`I`.

Then an inner node does not ask a yes/no question about one boolean variable;
it asks: **which interval contains the current value of one clock difference?**

The semantics can be written as [BEHR03_CDD_PAGE]_:

.. math::

   \llbracket False \rrbracket = \emptyset,
   \qquad
   \llbracket True \rrbracket = \mathcal{V},

.. math::

   \llbracket n \rrbracket
   =
   \{\, v \in \mathcal{V}
   \mid
   \exists I, m.\;
   n \xrightarrow{I} m
   \land I(type(n))(v)
   \land v \in \llbracket m \rrbracket
   \,\}.

So evaluation is path-based:

* inspect the clock difference attached to the current node
* follow the unique interval edge matching the current valuation
* accept the valuation if the path ends in ``True``

This is also where the main difference from ROBDDs shows up. Clock-difference
constraints are **not independent**. Bounds on :math:`X`, :math:`Y`, and
:math:`X-Y` interact. That is why the paper emphasizes that CDDs do not gain a
simple canonical form just by fixing an order and applying sharing
[BEHR03_CDD_PAGE]_.

The definition therefore includes extra structural requirements:

* successor intervals of one node must be pairwise disjoint
* they must cover the real line
* the graph must respect the global order on types
* the reduced form uses maximal sharing and avoids trivial full-line edges

Later the paper introduces tightened and equally fine partitioned CDDs. The key
normal-form statement is [BEHR03_CDD_PAGE]_:

.. math::

   \llbracket C_1 \rrbracket = \llbracket C_2 \rrbracket
   \iff
   C_1 \cong C_2

but only under those extra hypotheses. For practical understanding, the
important takeaway is not “CDDs are automatically canonical”; it is:
**CDDs share aggressively, but equivalence and normal-form reasoning are more
subtle than in ROBDDs.**

From The Paper’s Continuous CDDs To Today’s Mixed Symbolic Graphs
-----------------------------------------------------------------

If one only follows the original 1999 paper narrative, it is natural to think
of a CDD mainly as “one shared structure compressing many continuous zones at
one location”. That is still true, but it is no longer the whole story for the
current `UCDD` and :mod:`pyudbm.binding.ucdd`.

In the actual UCDD codebase, BDD levels and clock-difference levels live inside
the same runtime and may appear in the same symbolic graph [UCDD_CDD_H]_
[PYUDBM_UCDD_CPP]_ [PYUDBM_UCDD_PY]_.

The public header says this quite explicitly:

* the module supports both ``BDD`` nodes and ``CDD`` nodes
* if only booleans are declared, it degenerates to a BDD library
* with both clocks and booleans, the total number of levels is
  :math:`O(n^2 + m)`:
  clock-difference levels from clock pairs, plus boolean-decision levels

The low-level API reflects exactly that split:

* ``TYPE_CDD = 0`` and ``TYPE_BDD = 1``
* ``LevelInfo`` exposes ``type``, ``clock1``, ``clock2``, and ``diff``
* ``cdd_add_bddvar(n)`` extends the global runtime with boolean levels
* ``cdd_add_clocks(n)`` extends it with clock-difference levels, whose space is
  :math:`O(c^2)`

.. graphviz:: runtime_layout.dot

At the Python layer, this mixed structure is user-facing rather than hidden:

* :class:`CDDContext` stores ``base_context``, ``clock_names``, ``bool_names``, and
  ``dimension`` together
* ``_ensure_runtime_layout`` calls native ``add_clocks`` / ``add_bddvars`` and
  caches the resulting ``bool_levels``
* each :class:`CDDBool` is tied to one native BDD level, and :meth:`CDDBool.as_cdd` becomes :meth:`CDD.bddvar`
* each :class:`CDDClock` / :class:`CDDVariableDifference` still uses the DBM-style DSL
  and then lifts the resulting zone through :meth:`CDD.from_federation`

So once you are in the Python DSL, booleans and zones are not two loose
side-by-side objects. They are woven into one symbolic object. For example,
starting from :class:`pyudbm.binding.udbm.Context` and
:meth:`pyudbm.binding.udbm.Context.to_cdd_context`:

.. code-block:: python

   from pyudbm import Context

   base = Context(["x", "y"], name="c")
   ctx = base.to_cdd_context(bools=["door_open", "alarm"])

   state = ((ctx.x <= 5) & ctx.door_open) | ((ctx.y <= 2) & ~ctx.door_open)

This ``state`` is not merely “a boolean formula plus a federation”. It is one
mixed graph. Along a root-to-terminal path you may encounter boolean levels and
clock-difference levels together, and the path as a whole defines one boolean
guard together with one zone fragment.

The same example can be written as

.. math::

   state = \bigl(door\_open \land 0 \leq x \leq 5\bigr)
   \;\lor\;
   \bigl(\neg door\_open \land 0 \leq y \leq 2\bigr).

If you sketch it as one mixed “boolean layer + continuous layer” object, the
shape looks roughly like this:

.. graphviz:: mixed_bool_zone.dot

This diagram does not claim that UCDD stores the graph in exactly this one
node layout. It visualizes the mixed path semantics of one :class:`CDD`:

* the root tests the boolean variable ``door_open``
* the true branch continues with the clock constraint :math:`x \in [0,5]`
* the false branch continues with :math:`y \in [0,2]`
* one graph therefore carries both discrete guards and continuous zone pieces

For the current implementation, the most faithful mental model is:

.. math::

   state \equiv \bigvee_k \bigl(B_k \land D_k\bigr),

where :math:`B_k` is the boolean guard extracted from one path and :math:`D_k`
is the associated DBM fragment. That formula is not a verbatim paper
definition. It is an implementation-level summary induced directly by the
current extraction API:

* :meth:`CDD.extract_bdd_and_dbm` returns one ``bdd_part``, one ``dbm``, and one
  ``remainder``
* :class:`CDDExtraction` keeps those three parts as high-level objects
* :meth:`CDD.to_federation` repeatedly extracts fragments and refuses conversion as
  soon as one extracted ``bdd_part`` is not ``True``

Together these behaviors almost spell out the runtime model:
**a mixed CDD represents many “boolean-guarded zone fragments”; a plain
federation can only carry the special case where those guards collapse to
truth.**

So in real UCDD, “zones and booleans coexist” is not a vague slogan. It means:

* boolean variables occupy BDD levels
* clock-difference constraints occupy CDD levels
* both share one global level order and one decision graph
* one extracted path becomes “guard + zone fragment”
* forward and backward discrete operators can accept both clock resets and
  boolean resets

Three practical boundaries are worth remembering:

* the UCDD runtime is process-global, and the wrapper enforces one compatible
  clock order plus one compatible boolean-prefix layout at a time
* boolean layouts can only grow compatibly by prefix; arbitrary renamings do
  not coexist in one live runtime
* native ``extract_*`` helpers require reduced CDDs, and the Python layer
  absorbs that precondition automatically [UCDD_CDD_H]_ [PYUDBM_UCDD_PY]_

That is also why CDDs matter here as more than historical background:

* they support a more unified Python-first symbolic workflow
* they keep the repository from ossifying at the level of explicit DBM
  federations alone

With that implementation picture in mind, the verification role of CDDs becomes
clearer.

What CDDs Are Doing Inside Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Placed back inside timed-automata symbolic semantics, CDDs take over three
jobs.

First, they turn “many zones at one location” into a first-class object. That
is the story behind formula (1) and behind the paper’s use of a CDD to compress
the continuous part of ``PASSED``.

Second, they aim to support DBM-like symbolic transforms. At the semantic
level, the two central operations are still [UPP_SEM_CDD]_ [BY04_CDD]_ [BEHR03_CDD_PAGE]_:

.. math::

   D^\uparrow = \{\, u + d \mid u \in D,\ d \in \mathbb{R}_{\ge 0} \,\},

.. math::

   r(D) = \{\, [r \mapsto 0]u \mid u \in D \,\}.

That is, time elapse and clock reset. The paper’s final section states
explicitly that, with tightened CDDs, these operations can be defined along the
same overall lines as for DBMs [BEHR03_CDD_PAGE]_.

Third, CDDs support whole-set boolean and inclusion-style reasoning:

* union, intersection, complement
* constructing a CDD from a constraint system / DBM
* checking whether one zone is included in one CDD

The asymmetric query

.. math::

   subset(D, C)

is especially important in reachability: one fresh zone :math:`D`, one
accumulated non-convex object :math:`C`.

Current API And Verification Meaning
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 21 18 24 37

   * - API
     - Category
     - Verification meaning
     - Notes
   * - ``from_dbm`` / ``from_federation``
     - Bridging
     - Move zones / federations into CDD form
     - Useful for connecting explicit DBM workflows to shared diagrams
   * - ``&`` / ``|`` / ``-`` / ``^`` / ``~``
     - Set / boolean algebra
     - intersection, union, difference, xor, complement
     - boolean literals and clock constraints live in one graph
   * - ``reduce`` / ``reduce2`` / ``equiv``
     - Representation maintenance
     - reduction and semantic equivalence
     - extraction-oriented helpers depend on reduced form
   * - ``contains_dbm``
     - Inclusion
     - ask whether a new zone is already covered
     - this matches the paper’s most important asymmetric query
   * - ``extract_dbm`` / ``extract_bdd`` / ``extract_bdd_and_dbm``
     - Decomposition
     - split one mixed graph into guard + DBM fragments
     - crucial for interop with DBM / federation code
   * - ``bdd_traces``
     - Boolean inspection
     - enumerate satisfying boolean assignments
     - especially useful for debugging mixed symbolic states
   * - ``delay`` / ``past`` / ``delay_invariant`` / ``predt``
     - Time operators
     - forward and backward time closure
     - align with timed-automata delay predecessor / successor reasoning
   * - ``apply_reset`` / ``transition``
     - Forward discrete-step operators
     - guard + clock/bool updates
     - ``transition`` is the edge-like high-level form
   * - ``transition_back`` / ``transition_back_past``
     - Backward discrete-step operators
     - symbolic predecessors of an edge
     - directly relevant to backward reachability
   * - ``to_federation``
     - Conversion back to explicit union form
     - only for pure-clock CDDs
     - mixed boolean guards are rejected explicitly

Understanding The Core Operations In Verification Terms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``contains_dbm()``: The Question Is Coverage, Not Similarity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For reachability, one of the most valuable questions is

.. math::

   D \subseteq F_{\mathrm{passed}} \; ?

meaning “is this new zone already covered by the accumulated symbolic object?”

This is not a symmetric equality test. It is an **incoming zone versus old
CDD** inclusion query. Section 4.2 of the paper treats exactly this as a key
operation, and the current Python API exposes it as ``CDD.contains_dbm(dbm)``
[BEHR03_CDD_PAGE]_ [PYUDBM_UCDD_PY]_.

.. image:: contains_cover.plot.py.svg
   :width: 96%
   :align: center
   :alt: Three-panel figure showing a passed-set union, a candidate DBM zone, and the final inclusion relation D subseteq F_passed.

The rightmost panel illustrates the practical meaning: if the candidate zone is
already inside the accumulated non-convex set, expanding it again usually adds
no new timing information.

``reduce()`` and ``extract_*()``: Splitting A Shared Graph Into Guards And DBMs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the current wrapper, a useful operational view is

.. math::

   C \equiv \bigvee_{k=1}^{m} \bigl(B_k \land D_k\bigr). \tag{2}

This is an inference from the current extraction API rather than a verbatim
paper definition: repeated ``extract_bdd_and_dbm()`` calls peel one boolean
guard :math:`B_k` plus one DBM fragment :math:`D_k` at a time until the
remainder is empty.

.. image:: mixed_extract.plot.py.svg
   :width: 96%
   :align: center
   :alt: Three-panel figure showing one mixed symbolic state and the two extracted guarded DBM fragments.

This matters because:

* it provides a clean bridge back into existing DBM / federation algorithms
* it exposes how boolean guards carve the continuous state space into pieces

It also clarifies a hard boundary: if a CDD still has a non-trivial boolean
guard, it cannot be converted directly to a plain federation.

``delay()`` and ``delay_invariant()``: Time-Successor Operators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Timed-automata forward time semantics are still

.. math::

   D^\uparrow = \{\, u + d \mid u \in D,\ d \in \mathbb{R}_{\ge 0} \,\}.

So ``delay()`` should be read as: **push the whole symbolic state forward in
time while staying in the same discrete control point.**

``delay_invariant(I)`` adds the requirement that the invariant :math:`I` remain
satisfied during that time passage. That makes it the more direct fit for
location-invariant reasoning.

.. image:: delay_reset.plot.py.svg
   :width: 96%
   :align: center
   :alt: Three-panel figure showing a source zone, its forward time successor, and the result of resetting x to zero.

The middle panel shows why this is a symbolic-state operator rather than a
single-state simulator step: a small bounded region can expand into a much
larger slanted band once all admissible time elapses are taken together.

``apply_reset()`` and ``transition()``: A Discrete Edge Is A Symbolic Transform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the symbolic level, a discrete edge has the shape

.. math::

   \mathrm{Post}_e(S)
   =
   \mathrm{reset}\bigl(S \cap g\bigr),

where :math:`g` is the guard. The current ``transition()`` method packages
exactly that pattern: intersect with a guard, then perform clock and boolean
updates [PYUDBM_UCDD_PY]_ [PYUDBM_UCDD_CPP]_.

In verification terms:

* ``guard`` filters valuations that can actually take the edge
* ``clock_resets`` implement clock updates on that edge
* ``bool_resets`` implement the discrete-side updates at the same step

This is also where the current wrapper goes beyond the paper’s original
continuous-only `PASSED` story: discrete guards and continuous constraints can
be combined in one graph first, then advanced together through one transition.

``past()``, ``predt()``, ``transition_back()``, ``transition_back_past()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Forward reachability is only one half of the story. Backward search, safe
predecessor reasoning, and some fixpoint algorithms need inverse-time and
inverse-edge operators as first-class tools.

``past()`` is the easiest one: it is the backward counterpart of ``delay()``.

``predt(safe)`` can be interpreted as

.. math::

   \mathrm{PredT}(T, S)
   =
   \{\, u \mid \exists d \ge 0.\ u + d \in T
   \land \forall e \in [0, d].\ u + e \in S \,\}. \tag{3}

This is an inference from the current naming, tests, and the way the operator
is combined with a safe region, rather than a literal wrapper comment. Under
that reading, ``predt`` asks which states can reach the target through time
while staying inside the safe region the whole way.

``transition_back()`` and ``transition_back_past()`` then push that idea across
discrete edges:

* ``transition_back`` computes symbolic predecessors of a discrete step
* ``transition_back_past`` also closes the result under inverse time elapse

.. image:: backward_ops.plot.py.svg
   :width: 96%
   :align: center
   :alt: Three-panel figure showing a post-state, the backward predecessor through one discrete transition, and the larger predecessor after adding backward time closure.

The third panel being larger than the second is exactly the point: first invert
the edge, then add earlier time-predecessor states as well.

Important Takeaways
-------------------

If this page leaves you with seven core points, they should be these:

* **Federations answer exact non-convex representation; CDDs answer sharing, compression, and whole-set querying.**
* **The basic decision unit of a CDD is an interval over one clock difference, not a single boolean bit.**
* **CDD structure is BDD-like, but it should not be explained as if it were automatically a simple ROBDD-style canonical form.**
* **The most important paper-level query is whether one incoming zone is already covered by the accumulated `PASSED` CDD.**
* **The current `pyudbm.binding.ucdd` layer already supports mixed boolean + clock symbolic graphs.**
* **Operators such as `delay`, `reset`, `predt`, and `transition_back_past` make sense as timed-automata symbolic semantics, not just as isolated data-structure tricks.**
* **A CDD with a non-trivial boolean guard cannot be flattened back into a plain federation directly.**

Next
~~~~

After CDDs, the next natural topic cluster is search, storage, extrapolation,
and termination: now that zones, federations, and CDDs are all on the table,
the next question is how they participate in real `WAIT` / `PASSED` loops.

References
~~~~~~~~~~

.. [UPP_VER_CDD] UPPAAL GUI documentation, ``Verifier``.
   Public link: `<https://docs.uppaal.org/gui-reference/verifier/>`_.
.. [UPP_SEM_CDD] UPPAAL documentation, ``Semantics``.
   Public link: `<https://docs.uppaal.org/language-reference/system-description/semantics/>`_.
.. [BY04_CDD] Johan Bengtsson and Wang Yi.
   ``Timed Automata: Semantics, Algorithms and Tools``.
   Public link: `<https://uppaal.org/texts/by-lncs04.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README.md>`_.
.. [BEHR03_CDD_PAGE] Gerd Behrmann.
   ``Efficient Timed Reachability Analysis using Clock Difference Diagrams``.
   Public link: `<https://www.brics.dk/RS/98/47/BRICS-RS-98-47.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/behrmann03/paper-c/README.md>`_.
.. [UCDD_REPO] UPPAALModelChecker.
   ``UCDD``.
   Public link: `<https://github.com/UPPAALModelChecker/UCDD>`_.
.. [UCDD_CDD_H] UPPAALModelChecker.
   ``UCDD/include/cdd/cdd.h``.
   Public link: `<https://github.com/UPPAALModelChecker/UCDD/blob/master/include/cdd/cdd.h>`_.
.. [PYUDBM_UCDD_PY] HansBug.
   ``pyudbm/binding/ucdd.py``.
   Public link: `<https://github.com/HansBug/pyudbm/blob/main/pyudbm/binding/ucdd.py>`_.
.. [PYUDBM_UCDD_CPP] HansBug.
   ``pyudbm/binding/_ucdd.cpp``.
   Public link: `<https://github.com/HansBug/pyudbm/blob/main/pyudbm/binding/_ucdd.cpp>`_.
