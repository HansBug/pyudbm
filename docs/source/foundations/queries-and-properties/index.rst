Queries and Properties
======================

This page answers the next question after
:doc:`../timed-automata/index`: **once we have a timed model, what do we
usually ask about it?**

UPPAAL is not used only to draw timed automata. It is used to check
requirements against them. The verifier does this by on-the-fly exploration of
the symbolic state-space [UPP_VER]_.

The Core Intuition
------------------

Most beginner questions about a model are variants of one of these:

* can a good state be reached?
* can a bad state be reached?
* must some progress eventually happen?
* can the system get stuck?

UPPAAL's classic symbolic query language is built around exactly that kind of
question [LPY97_QP]_ [BY04_QP]_ [UPP_QSYN]_ [UPP_QSEM]_.

The Running State-Space Picture
-------------------------------

The easiest way to understand the common queries is to look at a small
state-space sketch:

.. graphviz:: state_space_queries.dot

Read the picture like this:

* ``Acked`` is a desirable target state
* ``Error`` is a bad state
* ``Stuck`` is a deadlock state
* ``Unreachable`` exists in the abstract graph, but no execution from the initial state ever gets there

This one picture already separates several common questions:

* ``E<> Acked`` asks whether *some* execution can reach ``Acked``
* ``A[] not Error`` asks whether *every reachable state* avoids ``Error``
* ``A<> Acked`` asks whether *every execution* is eventually forced to hit ``Acked``
* ``A[] not deadlock`` asks whether no reachable state is a deadlock

Those queries sound similar in English, but they are logically different.

From State Predicates To Queries
--------------------------------

UPPAAL queries are built from **state predicates**.

A state predicate is a boolean condition evaluated on one symbolic or concrete
state. Officially, it may mention locations, variables, logical combinations,
and clock constraints [UPP_QSYN]_ [UPP_QSEM]_.

Typical examples are:

* ``Controller.WaitAck`` meaning that process ``Controller`` is currently in location ``WaitAck``
* ``x <= 5`` meaning the current state satisfies that clock bound
* ``Controller.WaitAck and x < 5``
* ``deadlock``, which is a special built-in state predicate

The official syntax page summarizes the classic symbolic queries as:

.. math::

   \texttt{A[]}\; p,\qquad
   \texttt{E<>}\; p,\qquad
   \texttt{E[]}\; p,\qquad
   \texttt{A<>}\; p,\qquad
   p \; \texttt{-->} \; q

This page focuses on the first, second, fourth, and fifth forms, because they
cover most early modeling questions.

A Minimal Semantic Backbone
---------------------------

UPPAAL's official query semantics is phrased over a timed transition system

.. math::

   \mathcal{M} = (S, s_0, \to)

where:

* :math:`S` is the set of states
* :math:`s_0` is the initial state
* :math:`\to` is the transition relation induced by delay and discrete steps

If :math:`p` is a state predicate, write :math:`s \models p` when state
:math:`s` satisfies :math:`p`.

Also write

.. math::

   s_0 \to s_1 \to s_2 \to \cdots

for a path, and call a path **maximal** if it is infinite or cannot be
extended further.

Two details are worth making explicit before reading the formulas:

* :math:`\mathrm{Reach}(\mathcal{M})` means "the set of all states reachable from the initial state :math:`s_0` by some finite execution"
* so :math:`\forall s \in \mathrm{Reach}(\mathcal{M})` does not mean "for any abstract state one might imagine", but "for every state the system can actually get to"

In other words, reachability-style queries ask whether some execution can bring
the system somewhere, while ``A[]``-style queries ask whether every genuinely
reachable state satisfies a condition.

With that notation, the most useful beginner-level readings are:

.. math::

   \mathcal{M} \models E\langle\rangle p
   \iff
   \exists \text{ a path reaching some state } s \text{ with } s \models p

.. math::

   \mathcal{M} \models A[]\, p
   \iff
   \forall s \in \mathrm{Reach}(\mathcal{M}),\; s \models p

.. math::

   \mathcal{M} \models A\langle\rangle p
   \iff
   \forall \text{ maximal paths } \pi,\; \pi \text{ eventually reaches a state satisfying } p

.. math::

   \mathcal{M} \models E[]\, p
   \iff
   \exists \text{ a maximal path whose every state satisfies } p

Translated into plain language, these say:

* :math:`E\langle\rangle p`:
  there exists **some** execution that reaches a state satisfying :math:`p`.
  This is the right query when the question is "can this ever happen at all?"
* :math:`A[]\, p`:
  every **reachable state** must satisfy :math:`p`.
  This is easy to misread as "on every path, :math:`p` keeps holding forever".
  A more concrete reading is:
  **there is no reachable state that violates :math:`p`**.
* :math:`A\langle\rangle p`:
  every maximal execution must eventually enter a state satisfying :math:`p`.
  So this is not mere reachability. If even one execution can postpone :math:`p`
  forever, the property is false.
* :math:`E[]\, p`:
  there exists a maximal execution that stays inside :math:`p` all the way.
  This is useful when asking whether some behavior can persist indefinitely.

If :math:`A[]\, p` and :math:`A\langle\rangle p` still feel too close, force
the distinction like this:

* :math:`A[]\, p` talks about the truth of :math:`p` at every reachable state
* :math:`A\langle\rangle p` talks about whether every execution is eventually forced into :math:`p`

The first is a **state safety** view. The second is an **eventual progress**
view. They are not interchangeable.

For example:

* ``A[] not Error`` says "the system never enters ``Error``"
* ``A<> Acked`` says "no matter how the system runs, it will eventually enter ``Acked``"

A model may satisfy the first and still fail the second, for example if it can
loop forever in a non-error state without ever acknowledging anything.

These are slightly simplified tutorial-level readings, but they match the
official pseudo-formal semantics closely [UPP_QSEM]_.

Reading The Most Common Queries
-------------------------------

The four classic beginner queries can be read in plain language as follows.

Reachability: ``E<> p``
~~~~~~~~~~~~~~~~~~~~~~~

This is the "can this happen at all?" query.

For the picture above:

.. code-block:: text

   E<> Acked

is true, because there exists at least one path from ``Init`` to ``Acked``.

In UPPAAL models, a more realistic version usually looks like:

.. code-block:: text

   E<> Controller.Acked

or:

.. code-block:: text

   E<> Controller.WaitAck and x > 3

So ``E<>`` is the natural query when you want one witness execution.

Safety: ``A[] p``
~~~~~~~~~~~~~~~~~

This is the "is it always safe?" query.

For example:

.. code-block:: text

   A[] not Error

means that every reachable state must avoid ``Error``.

In the picture above this query is false, because ``Error`` is reachable.

This is why ``A[]`` is the natural way to express safety conditions such as:

* mutual exclusion
* buffer bounds
* "the bad location is never reachable"
* ``A[] not deadlock``

Universal Eventuality: ``A<> p``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is stronger than plain reachability.

.. code-block:: text

   A<> Acked

does **not** ask whether ``Acked`` is reachable on some path. It asks whether
every maximal execution is eventually forced to reach ``Acked``.

In the picture above the answer is false, because there are executions that go
to ``Error`` or ``Stuck`` instead.

That difference is fundamental:

* ``E<> Acked`` means "success is possible"
* ``A<> Acked`` means "success is unavoidable"

Potential Persistence: ``E[] p``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This query is not usually the first one people learn, but it is useful because
it explains the duality around ``A<>``.

.. code-block:: text

   E[] not Acked

asks whether there exists a maximal execution that can stay forever outside
``Acked``.

In the picture above the answer is yes: the path to ``Error`` already avoids
``Acked``, and the path to ``Stuck`` does too.

This is why UPPAAL documents the equivalence

.. math::

   A\langle\rangle p \equiv \neg E[]\, \neg p

and similarly

.. math::

   A[]\, p \equiv \neg E\langle\rangle \neg p

[UPP_QSEM]_.

Deadlock As A Property
----------------------

UPPAAL treats ``deadlock`` as a special state predicate.

Officially, a state :math:`(L, v)` satisfies ``deadlock`` iff

.. math::

   \forall d \ge 0,\; \text{there is no action successor of } (L, v + d)

[UPP_QSEM]_.

Read that carefully: a deadlock is not only "no discrete edge is enabled right
now". It also says that waiting longer will not help produce a legal action
successor either.

That is why

.. code-block:: text

   A[] not deadlock

is such a common sanity check in UPPAAL tutorials and models [BDL04_QP]_.

Leads-To Is Stronger Than Reachability
--------------------------------------

UPPAAL also supports the derived-style property

.. code-block:: text

   p --> q

meaning: whenever a state satisfying ``p`` occurs, a later state satisfying
``q`` must eventually follow on all continuations.

The official semantics states the equivalence

.. math::

   p \;\texttt{-->}\; q
   \equiv
   A[]\, (p \Rightarrow A\langle\rangle q)

[UPP_QSEM]_.

This is much stronger than saying merely that ``q`` is reachable somewhere.
Consider:

.. graphviz:: request_leadsto.dot

In this picture:

* ``E<> Acked`` is true, because there exists a path from ``Pending`` to ``Acked``
* but ``Pending --> Acked`` is false, because there is also a continuation that stays in ``RetryLoop`` forever

So leads-to is the right mental model for requirements such as:

* every request is eventually acknowledged
* every fault is eventually recovered
* every train that approaches the gate eventually crosses

Witnesses, Counterexamples, And Why Queries Feel Useful
-------------------------------------------------------

Queries are not only logical formulas. In practice, they are useful because the
tool can often show **why** they are true or false.

UPPAAL's symbolic verifier can produce witness and counterexample traces, and
those traces can be inspected in the symbolic simulator [UPP_QSEM]_ [UPP_VER]_.

That is the practical split:

* ``E<> p`` often comes with a witness path reaching ``p``
* ``A[] p`` often comes with a counterexample path reaching ``not p``
* ``A<> p`` and ``p --> q`` may fail because of an infinite postponing loop, not only because of an obvious bad state

This is one reason query formulation matters so much: two properties that sound
similar in prose may produce very different diagnostic traces.

Beyond Yes/No Queries
---------------------

The current symbolic query syntax in UPPAAL also includes forms such as
``sup``, ``inf``, and ``bounds`` for asking quantitative questions over clocks
or integer expressions [UPP_QSYN]_.

This page does not go into those yet. For now, the main lesson is simpler:

* first decide whether you are asking about existence, invariance, eventuality, or progress
* then choose the query form that matches that intent

Why This Matters For ``pyudbm``
-------------------------------

`pyudbm` does not yet expose UPPAAL's full query language, but the query view
already explains why clock constraints matter at all.

The verifier is checking properties over symbolic states represented by clock
constraints. That means:

* the meaning of a query ultimately depends on sets of valuations, not just one concrete valuation
* high-level clock predicates such as ``x <= 5`` are not decorations; they are the actual state properties verification talks about
* later pages on symbolic states, zones, DBMs, and federations are exactly the machinery that makes these queries tractable

What To Remember
----------------

If you keep five ideas from this page, keep these:

* ``E<> p`` asks whether ``p`` is reachable on some path
* ``A[] p`` asks whether ``p`` holds in every reachable state
* ``A<> p`` is stronger than reachability: it asks whether every path must eventually hit ``p``
* ``deadlock`` is a first-class state predicate in UPPAAL
* ``p --> q`` is a progress-style property, not just another reachability query

Next
----

The next natural page is ``symbolic-states/``: once the query viewpoint is in
place, the next question is why UPPAAL does not enumerate concrete timed states
one by one.

References
----------

.. [UPP_VER] UPPAAL official GUI documentation, ``Verifier``.
   Public link: `<https://docs.uppaal.org/gui-reference/verifier/>`_.
.. [UPP_QSYN] UPPAAL official documentation, ``Syntax of Symbolic Queries``.
   Public link: `<https://docs.uppaal.org/language-reference/query-syntax/symbolic_queries/>`_.
.. [UPP_QSEM] UPPAAL official documentation, ``Semantics of the Symbolic Queries``.
   Public link: `<https://docs.uppaal.org/language-reference/query-semantics/symb_queries/>`_.
.. [LPY97_QP] Kim Guldstrand Larsen, Paul Pettersson, and Wang Yi.
   ``UPPAAL in a Nutshell.``
   Public link: `<https://dblp.org/rec/journals/sttt/LarsenPY97>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/lpy97/README.md>`_.
.. [BDL04_QP] Gerd Behrmann, Alexandre David, and Kim Guldstrand Larsen.
   ``A Tutorial on UPPAAL.``
   Public link: `<https://dblp.org/rec/conf/sfm/BehrmannDL04>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/bdl04/README.md>`_.
.. [BY04_QP] Johan Bengtsson and Wang Yi.
   ``Timed Automata: Semantics, Algorithms and Tools``.
   Public link: `<https://uppaal.org/texts/by-lncs04.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README.md>`_.
