Search, Extrapolation, and Storage: Why UPPAAL Is More Than “A Few Data Structures”
====================================================================================

.. currentmodule:: pyudbm.binding.udbm

This page continues naturally from :doc:`../cdd/index`.
The previous pages introduced symbolic states, zones, DBMs, federations, and
CDDs one by one. The next engineering question is the one that really matters
for a verifier:
**how are those objects wired together into one actual state-space exploration
pipeline?**

A realistic UPPAAL-style engine is not just “pick one symbolic representation
and then add a few set operations”. It is simultaneously constrained by three
pressures:

* **search pressure**: symbolic successors must keep flowing through a
  `WAIT` / `PASSED` loop
* **termination pressure**: exact zone graphs are often infinite unless we
  abstract
* **memory pressure**: even when one DBM operation is cheap, storing and
  comparing many symbolic states can dominate the total cost

This page therefore connects five layers:

* what `WAIT` and `PASSED` mean in an actual reachability loop
* why exact successors alone are rarely enough, and why extrapolation exists
* why successor computation cost is not reducible to one or two DBM operators
* why minimal constraints, compact storage, and early inclusion checks matter
* where these ideas already surface in today's `UDBM` and
  :mod:`pyudbm.binding.udbm`

Start With A Small But Real Search Loop
---------------------------------------

The fundamental object of timed symbolic search is the symbolic state: a
control location together with one clock region.

If we show only two short successor formulas here, the notation looks cleaner
than the real algorithm. So first fix the smallest useful set of symbols.

Fix The Notation First
~~~~~~~~~~~~~~~~~~~~~~

Let :math:`C` be the set of clocks and let the space of non-negative
valuations be:

.. math::

   V = \mathbb{R}_{\ge 0}^{C}

One symbolic state is written as:

.. math::

   S = (l, Z)

Its concrete meaning is:

.. math::

   \llbracket S \rrbracket
   =
   \left\{ (l, v) \mid v \in Z,\; v \models I(l) \right\}

Each symbol matters:

* :math:`l` is the current control location
* :math:`v` is one concrete valuation that assigns a non-negative real to each
  clock :math:`x \in C`
* :math:`Z` is one zone, meaning a set of valuations
* :math:`I(l)` is the invariant of location :math:`l`
* :math:`v \models I(l)` means that :math:`v` satisfies that invariant
* :math:`\llbracket S \rrbracket` is the set of all concrete timed states
  represented by :math:`S`

Time elapse, guard filtering, and reset can then be written as:

.. math::

   Z^{\uparrow}
   =
   \left\{ v + d \mid v \in Z,\; d \in \mathbb{R}_{\ge 0} \right\}

.. math::

   Z \cap g
   =
   \left\{ v \in Z \mid v \models g \right\}

.. math::

   reset_r(Z)
   =
   \left\{ v[r := 0] \mid v \in Z \right\}

with:

.. math::

   (v + d)(x) = v(x) + d
   \qquad
   \text{for every } x \in C

.. math::

   v[r := 0](x)
   =
   \begin{cases}
      0, & x \in r \\
      v(x), & x \notin r
   \end{cases}

If `WAIT` stores stable symbolic states that are already time-closed at the
current location, then a common forward successor shape for one edge
:math:`e = (l, g, r, l')` is:

.. math::

   \mathrm{Post}_{e}(l, Z)
   =
   \left(
      l',
      \left(reset_r(Z \cap g)\right)^{\uparrow} \cap I(l')
   \right)

This one formula already connects the four actions that keep coming back in a
real verifier:

* filter the current zone with the guard :math:`g`
* reset the clocks in :math:`r`
* let time elapse again in the target location
* clip the result with the target invariant :math:`I(l')`

Different engines place `up` before or after edge firing depending on whether
`WAIT` stores “just-entered” states or already time-closed stable states.
But the repeated building blocks are still the same set operations.

A Tiny But Real Verification Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now consider a tiny automaton with only one clock `x`.
It is small enough that we can calculate each search step explicitly, but it
already contains guards, resets, target invariants, and a real `WAIT` /
`PASSED` loop.

.. graphviz:: verification_search_example.dot

The query is:

.. math::

   E \Diamond Goal

meaning “is there an execution that eventually reaches `Goal`?”

The three location invariants are:

.. math::

   I(L_0): x \le 5

.. math::

   I(L_1): x \le 3

.. math::

   I(Goal): x \le 1

The two edges are:

.. math::

   e_0 = (L_0,\; x \ge 2,\; \{x\},\; L_1)

.. math::

   e_1 = (L_1,\; x \ge 1,\; \{x\},\; Goal)

If the verifier stores stable symbolic states in `WAIT`, then the first state
at `L_0` is not the point :math:`x = 0`, but the time-closed zone:

.. math::

   Z_0 = \left\{ v \mid 0 \le v(x) \le 5 \right\}

.. math::

   S_0 = (L_0, Z_0)

Along the first edge :math:`e_0`, the successor is computed step by step as:

.. math::

   Z_0 \cap g_0
   =
   \left\{ v \mid 2 \le v(x) \le 5 \right\}

.. math::

   reset_{\{x\}}(Z_0 \cap g_0)
   =
   \left\{ v \mid v(x) = 0 \right\}

.. math::

   Z_1
   =
   \left(reset_{\{x\}}(Z_0 \cap g_0)\right)^{\uparrow} \cap I(L_1)
   =
   \left\{ v \mid 0 \le v(x) \le 3 \right\}

Along the second edge :math:`e_1`:

.. math::

   Z_1 \cap g_1
   =
   \left\{ v \mid 1 \le v(x) \le 3 \right\}

.. math::

   reset_{\{x\}}(Z_1 \cap g_1)
   =
   \left\{ v \mid v(x) = 0 \right\}

.. math::

   Z_2
   =
   \left(reset_{\{x\}}(Z_1 \cap g_1)\right)^{\uparrow} \cap I(Goal)
   =
   \left\{ v \mid 0 \le v(x) \le 1 \right\}

So the verifier is not following one time point such as `x = 2` or `x = 3.4`.
It is following:

* the full feasible interval :math:`0 \le x \le 5` in `L_0`
* then the full interval :math:`0 \le x \le 3` in `L_1`
* then the full interval :math:`0 \le x \le 1` in `Goal`

The next figure turns that same story into a one-dimensional zone evolution:

.. image:: worked_search_intervals.plot.py.svg
   :width: 98%
   :align: center
   :alt: Six-panel interval figure showing the stable initial zone, guard filtering, reset, the next stable zone, the second guard filter, and the final goal zone.

From the search-loop point of view, the same run can be summarized as:

.. list-table::
   :header-rows: 1
   :widths: 12 26 28 34

   * - Round
     - state popped from `WAIT`
     - `PASSED` update
     - newly generated successors
   * - 0
     - :math:`(L_0, Z_0)`
     - add it to :math:`PASSED(L_0)`
     - generate :math:`(L_1, Z_1)` and enqueue it
   * - 1
     - :math:`(L_1, Z_1)`
     - add it to :math:`PASSED(L_1)`
     - generate :math:`(Goal, Z_2)` and enqueue it
   * - 2
     - :math:`(Goal, Z_2)`
     - goal hit
     - return “reachable” and optionally reconstruct a diagnostic trace

This tiny example already contains three facts that matter in a real verifier:

* `WAIT` stores a zone, not one time instant
* one edge successor is really “guard filter + reset + time closure + target invariant”
* once one candidate state reaches the target location, reachability can stop

What The Cover Check Is Really Skipping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both Behrmann's thesis introduction and Bengtsson's memory paper write the core
reachability loop in exactly this spirit: keep a `WAIT` set and a `PASSED`
set, repeatedly remove one symbolic state from `WAIT`, and only expand it if it
is not already covered by something in `PASSED` [BEHR03_INTRO]_ [BENG02_MEM]_.

The key skip condition can be written as:

.. math::

   \text{skip } (l, Z)
   \quad \text{if} \quad
   \exists (l, Z') \in \mathrm{PASSED} : Z \subseteq Z'.

This is sound because, at the same control location:

.. math::

   Z \subseteq Z'
   \quad \Rightarrow \quad
   \llbracket (l, Z) \rrbracket \subseteq \llbracket (l, Z') \rrbracket

So `PASSED` is not storing “visited node ids”. It stores **symbolic
representatives that are already sufficient to cover later exploration at the
same control location**.

.. graphviz:: forward_search_loop.dot

This figure does not try to show concrete containers, trace recording, or every
semantic side-condition. It compresses the main exploration spine into the
steps that matter most:

* `WAIT` means “reachable but not explored yet”
* `PASSED` means “already explored, useful as a cover set”
* the expensive work starts after dequeueing: edge successors, delay
  successors, normalisation / extrapolation, and inclusion checks
* the object being reused all the time is **a zone attached to a control
  location**, not one isolated DBM primitive

This is also why the high-level Python API is organized around verbs such as:

* :meth:`Federation.up`
* :meth:`Federation.down`
* :meth:`Federation.predt`
* :meth:`Federation.contains`
* :meth:`Federation.extrapolate_max_bounds`
* :meth:`Federation.reduce`

These are not accidental helpers. They correspond to real phases of symbolic
search [BY04_SEARCH]_ [UDBM_DBM_H_SEARCH]_ [UDBM_FED_H_SEARCH]_ [PYUDBM_UDBM_PY_SEARCH]_.

Why Exact Successors Alone Are Usually Not Enough
-------------------------------------------------

Writing the search loop is not the hard part.
The hard part is that **if we insist on storing fully exact successors, the
symbolic graph often never stabilizes**.

The canonical pressure point is a loop where:

* one clock difference keeps growing
* the model only cares whether that value is above some constant
* but exact symbolic states still distinguish `3`, `30`, and `3000`

That is the core motivation in `bblp04`: for reachability, once a clock is far
beyond every relevant constant of the model, keeping the exact larger value may
contribute no new behaviour, while still forcing the symbolic state space to
grow [BBLP04_LU]_.

The next figure turns that idea into the smallest possible geometric toy
example:

.. image:: exact_family_collapse.plot.py.svg
   :width: 98%
   :align: center
   :alt: Three-panel figure showing a family of exact diagonal zones, a larger extrapolated cover zone, and a later candidate already included in that cover.

Each thin diagonal slice on the left is one exact zone :math:`Z_k`.
If exploration keeps iterating the loop, :math:`k` keeps increasing, and
`WAIT` / `PASSED` keep seeing new symbolic states.

The two right panels show what extrapolation actually does:

* it is **not** claiming that these exact zones were equal all along
* it is claiming that, for reachability, a coarser representative is enough
* once that coarser representative is in `PASSED`, later exact candidates
  inside it can be skipped

In this repository, that is not just paper-level intuition. The green cover
region in the figure is produced directly by
:meth:`Federation.extrapolate_max_bounds` on the current implementation.

If we compress the maximal-bound idea from `UDBM/include/dbm/dbm.h` down to its
most important rules, the heart of the transformation is [UDBM_DBM_H_SEARCH]_:

.. math::

   c_{i,j} > M(x_i) \;\Longrightarrow\; c'_{i,j} = \infty

.. math::

   -c_{i,j} > M(x_j) \;\Longrightarrow\; c'_{i,j} = (-M(x_j), <)

The intuition is:

* if an upper bound is already beyond the largest relevant constant for
  :math:`x_i`, forget it
* if a lower bound is already far below the largest relevant constant for
  :math:`x_j`, clamp it to the “already beyond relevance” threshold

That is why extrapolation is not ordinary closure. Closure preserves **exact
zone semantics**. Extrapolation deliberately trades exactness for **finite
abstraction and search termination** [BY04_SEARCH]_ [BBLP04_LU]_.

There is also a practical boundary worth making explicit:

* the current Python layer exposes :meth:`Federation.extrapolate_max_bounds`
* the native `dbm.h` and `fed.h` layers already provide diagonal maximal-bound,
  LU-bound, and diagonal-LU-bound variants

So in UDBM, **“extrapolation” is already a family of choices**, not one opaque
performance switch [BBLP04_LU]_ [UDBM_DBM_H_SEARCH]_ [UDBM_FED_H_SEARCH]_.

Why Successor Computation Itself Also Becomes Expensive
-------------------------------------------------------

Even after accepting the need for abstraction, the cost story is not over.
A real successor computation is not just one `up()` call or one set
intersection. It is a pipeline.

`bblp04` breaks a typical UPPAAL-style successor computation into six phases
[BBLP04_LU]_:

1. intersect with the guard and check emptiness
2. reset the modified clocks
3. compute delay / elapse
4. intersect with the target invariant
5. apply extrapolation
6. bring the DBM back to normal form

The striking point is that the real hotspot is often not the set operation
itself, but the final normalisation / canonisation step.
If this step is handled with a dense Floyd-Warshall-style closure, it comes
with the familiar :math:`O(n^3)` shape.

This is where `bblp04` becomes more than an abstraction paper.
It does not just say “LU extrapolation gives a smaller state graph”.
It also explains that **once extrapolation pushes the DBM into LU-form, the
cost structure of later normalisation changes as well**.

.. image:: successor_costs.plot.py.svg
   :width: 92%
   :align: center
   :alt: Two schematic bar charts comparing a dense canonical successor pipeline with an LU-aware one, where close is less dominant in the latter.

This figure is schematic rather than empirical.
Its job is to make the asymmetry easy to see:

* in the dense canonical pipeline, `close` is the obvious heavy phase
* in an LU-aware pipeline, the final normalisation can become much cheaper

The LU-aware complexity highlighted in the paper is [BBLP04_LU]_:

.. math::

   O(|Low| \cdot |Up| \cdot |Low \cap Up|)

The point is not just a better constant factor.
The point is that when lower-bounded and upper-bounded clocks are sparse,
the effective working set of normalisation is much smaller than the full DBM.

So:

* extrapolation shapes the **size of the search graph**
* LU-form shapes the **cost of computing one successor**
* these are engineering-coupled, not separate topics called “theory” and
  “backend optimisation”

This is also why the thesis introduction presents the reachability checker as a
composition of filters and buffers rather than as one monolithic loop
[BEHR03_INTRO]_:

.. graphviz:: engine_pipeline.dot

Three things matter here:

* a realistic checker is a composition of **state manipulation** and
  **state-space representation**
* delay, normalisation, active clock reduction, and trace storage can all be
  replaceable stages
* as soon as speed and memory matter, the real question is no longer “do we
  have DBMs?” but “which stages share which structure, and which stages can be
  bypassed or compressed?”

Why The Shape Of WAIT / PASSED Determines The Memory Ceiling
------------------------------------------------------------

Making the graph finite is still not enough.
In real tools, the more common failure mode is:
**the graph is finite in principle, but the objects inside `WAIT` and `PASSED`
are too large and too numerous**.

`llpy97` and Bengtsson's thesis Paper C attack this from two complementary
directions:

* **local reduction**: make each saved symbolic state smaller
* **global reduction**: make fewer symbolic states need to be saved at all

The local result is that a closed canonical DBM is excellent for exact
manipulation, but often wasteful as a stored form.
Many constraints are redundant consequences of the triangular inequality, so a
much smaller minimal-constraint representation is possible [LLPY97_STORAGE]_.

The global result is that termination does not necessarily require saving every
explored symbolic state in `PASSED`.
For dynamic loops, it can be enough to save states that cover the relevant
loop structure [LLPY97_STORAGE]_.

Bengtsson's memory paper pushes the idea further:
it argues that inclusion checks should happen as early as possible, even in the
waiting structure, to avoid filling `WAIT` with states that will eventually be
discarded anyway [BENG02_MEM]_.

At that point, the storage shape of one symbolic state starts to matter a lot:

.. graphviz:: storage_stack.dot

This figure is not claiming one unique implementation. It is showing the real
layering pressure:

* search manipulates **closed DBMs / federations**
* storage wants **minimal constraints / minDBM**
* hash tables and PWList-style buffers want an even more compact encoded form
* the Python layer already exposes a visible boundary of this stack through
  :meth:`DBM.to_min_dbm`

In the current repository, the most direct hooks are:

* `UDBM/include/dbm/mingraph.h`: the minimal-graph / minDBM C API
* `UDBM/src/mingraph_write.c`: the analysis and encoding path
* :meth:`DBM.to_min_dbm`: the Python-level export of packed minimal-DBM words

Seen together with :meth:`Federation.contains` and inclusion comparisons, this
makes the point clearer:
**UDBM is not just about manipulating DBMs; it is also about storing many
symbolic states under search pressure.**

The relationship becomes concrete even from today's public surface:

.. code-block:: python

   from pyudbm import Context

   c = Context(["x", "y"])
   x = c.x
   y = c.y

   zone = ((x >= 0) & (x <= 2) & (y >= 0) & (y <= 2))
   dbm = zone.to_dbm_list()[0]
   packed = dbm.to_min_dbm()

   assert isinstance(packed, tuple)

Here, `packed` is not a new semantic object.
It is the **same zone in a more storage-oriented representation**.
That representation is a better fit for hashing, caching, compact saving, or
passed-list management than a full closed matrix
[LLPY97_STORAGE]_ [UDBM_MINGRAPH_H]_ [UDBM_MINGRAPH_WRITE]_ [PYUDBM_UDBM_PY_SEARCH]_.

What Is Already Visible In Today’s pyudbm / UDBM Stack
------------------------------------------------------

To keep this page from drifting into paper-only narrative, the following table
aligns the most relevant code-level entry points for search, extrapolation, and
storage against the current Python wrapper, native binding layer, and public
tests [PYUDBM_UDBM_PY_SEARCH]_ [PYUDBM_UDBM_CPP_SEARCH]_ [PYUDBM_TEST_UDBM]_.

.. list-table::
   :header-rows: 1
   :widths: 18 20 20 42

   * - Topic
     - Current Python surface
     - Current native surface
     - Why it matters
   * - Delay successor
     - :meth:`Federation.up`
     - ``dbm_up`` / ``fed_t::up``
     - This is the core time-elapse action in symbolic reachability.
   * - Time predecessor
     - :meth:`Federation.down`, :meth:`Federation.predt`
     - ``dbm_down`` / ``fed_t::predt``
     - This covers backward-style reasoning and predecessor computation while avoiding bad zones.
   * - Cover / inclusion test
     - :meth:`Federation.contains`, ``<=``, ``>=``
     - ``fed_t::contains``, relation / inclusion checks
     - These decide whether `PASSED` is already strong enough to block a new candidate.
   * - Max-bound extrapolation
     - :meth:`Federation.extrapolate_max_bounds`
     - ``dbm_extrapolateMaxBounds`` / ``fed_t::extrapolateMaxBounds``
     - This is where infinite exact zone families collapse into finite abstractions.
   * - LU / diagonal extrapolation
     - not yet exposed directly at high level
     - ``dbm_extrapolateLUBounds``, ``dbm_diagonalExtrapolateLUBounds``
     - These show that upstream already treats extrapolation as a family of strategies.
   * - Representation maintenance
     - :meth:`Federation.reduce`, :meth:`Federation.intern`
     - ``fed_t::mergeReduce``, ``fed_t::intern``
     - Geometry may stay the same while the stored representation becomes cheaper.
   * - Minimal-constraint export
     - :meth:`DBM.to_min_dbm`
     - ``dbm_analyzeForMinDBM``, ``dbm_writeToMinDBMWithOffset``
     - This is a storage-layer capability, not a new semantic domain.

The current repository state is therefore already fairly specific:

* many of the **semantic search actions** are present today
* but the **engine-level composites** are not yet first-class Python objects
* so the project is already well beyond “a few low-level DBM helpers”, yet
  still short of a complete Python-first verification workflow

That is exactly why this page matters.
Without it, it is too easy to read the previous pages as “learn a few
representations and memorize some APIs”.
The actual UPPAAL perspective is the reverse:
**the reason these representations exist is that the search loop needs them to
balance correctness, termination, and memory pressure.**

What This Means For The UPPAAL / Python Reconstruction Direction
----------------------------------------------------------------

For this repository, three consequences follow directly.

First, the future Python-first API should not stop at exposing “functions that
operate on one DBM”.
Even before a full verifier exists in Python, users should eventually be able
to combine:

* successor computation
* cover checking
* extrapolation choices
* representation maintenance
* state snapshot / compact export

Second, extrapolation and storage should not be dismissed as “mere backend
optimisations”.
From `bblp04` to `llpy97` to Bengtsson's thesis, the real questions are always:
**when is the search space finite, how expensive is one step, and can the
global memory footprint survive the run?** [BBLP04_LU]_ [LLPY97_STORAGE]_
[BENG02_MEM]_.

Third, `pyudbm` already exposes enough hooks to retell that engineering story
coherently today.
Even now, the public surface is already enough to explain:

* why :meth:`Federation.up` and :meth:`Federation.down` are not optional API sugar
* why :meth:`Federation.extrapolate_max_bounds` decides whether search can
  stabilise
* why :meth:`DBM.to_min_dbm` belongs to the state-storage layer rather than a
  new semantic layer

So **restoring the historical binding is not the endpoint**.
Putting those restored objects back into a real symbolic-verification story is
the more important middle step.

Further Reading And References
------------------------------

The most natural follow-on topics from here are:

* reduction-related pages: when the question becomes “how do we generate fewer
  useless interleavings?”
* priced timed automata pages: when the question shifts from “can we reach?”
  to “how do we reach optimally?”

For this page itself, the most relevant local reading guides are:

* `papers/by04/README.md`
* `papers/bblp04/README.md`
* `papers/llpy97/README.md`
* `papers/bengtsson02/paper-c/README.md`
* `papers/behrmann03/paper-intro/README.md`

References
~~~~~~~~~~

.. [BY04_SEARCH] Johan Bengtsson and Wang Yi.
   ``Timed Automata: Semantics, Algorithms and Tools``.
   Public link: `<https://uppaal.org/texts/by-lncs04.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README.md>`_.
.. [BBLP04_LU] Gerd Behrmann, Patricia Bouyer, Kim G. Larsen, and Radek Pelánek.
   ``Lower and Upper Bounds in Zone Based Abstractions of Timed Automata``.
   Public link: `<https://www.researchgate.net/profile/Radek-Pelanek/publication/221224338_Lower_and_Upper_Bounds_in_Zone-Based_Abstractions_of_Timed_Automata/links/0912f50be648eae2d0000000/Lower-and-Upper-Bounds-in-Zone-Based-Abstractions-of-Timed-Automata.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/bblp04/README.md>`_.
.. [LLPY97_STORAGE] Kim G. Larsen, Fredrik Larsson, Paul Pettersson, and Wang Yi.
   ``Efficient Verification of Real-Time Systems: Compact Data Structure and State-Space Reduction``.
   Public link: `<https://web.archive.org/web/20240919204934if_/https://www2.it.uu.se/research/group/darts/papers/texts/llpw-rtss97.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/llpy97/README.md>`_.
.. [BENG02_MEM] Johan Bengtsson and Wang Yi.
   ``Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems``.
   Public link: `<https://github.com/HansBug/pyudbm/blob/main/papers/bengtsson02/paper-c/paper.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/bengtsson02/paper-c/README.md>`_.
.. [BEHR03_INTRO] Gerd Behrmann.
   ``Data Structures and Algorithms for the Analysis of Real Time Systems``, introduction section.
   Public link: `<https://github.com/HansBug/pyudbm/blob/main/papers/behrmann03/paper-intro/paper.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/behrmann03/paper-intro/README.md>`_.
.. [UDBM_DBM_H_SEARCH] UPPAALModelChecker.
   ``UDBM/include/dbm/dbm.h``.
   Public link: `<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/dbm.h>`_.
.. [UDBM_FED_H_SEARCH] UPPAALModelChecker.
   ``UDBM/include/dbm/fed.h``.
   Public link: `<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/fed.h>`_.
.. [UDBM_MINGRAPH_H] UPPAALModelChecker.
   ``UDBM/include/dbm/mingraph.h``.
   Public link: `<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/mingraph.h>`_.
.. [UDBM_MINGRAPH_WRITE] UPPAALModelChecker.
   ``UDBM/src/mingraph_write.c``.
   Public link: `<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/src/mingraph_write.c>`_.
.. [PYUDBM_UDBM_PY_SEARCH] HansBug.
   ``pyudbm/binding/udbm.py``.
   Public link: `<https://github.com/HansBug/pyudbm/blob/main/pyudbm/binding/udbm.py>`_.
.. [PYUDBM_UDBM_CPP_SEARCH] HansBug.
   ``pyudbm/binding/_udbm.cpp``.
   Public link: `<https://github.com/HansBug/pyudbm/blob/main/pyudbm/binding/_udbm.cpp>`_.
.. [PYUDBM_TEST_UDBM] HansBug.
   ``test/binding/test_udbm.py``.
   Public link: `<https://github.com/HansBug/pyudbm/blob/main/test/binding/test_udbm.py>`_.
