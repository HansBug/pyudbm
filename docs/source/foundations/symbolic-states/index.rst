Symbolic States and Zones
=========================

This page answers the next question after
:doc:`../queries-and-properties/index`: **why does UPPAAL not enumerate
concrete timed states one by one?**

The short answer is that clocks range over the non-negative reals, so even a
very small timed automaton already has infinitely many concrete states. UPPAAL
therefore explores the state-space using **symbolic states represented by
constraints** rather than by single valuations [UPP_VER_SS]_ [UPP_TRACE_SS]_.

The Running Pressure
--------------------

Return to the small request/response automaton from the previous pages. Inside
location ``WaitAck``, the clock ``x`` may satisfy:

.. math::

   0 \leq x \leq 5

These five symbols are already enough to create an infinite family of concrete
states:

* ``(WaitAck, x = 0)``
* ``(WaitAck, x = 0.2)``
* ``(WaitAck, x = 1.7)``
* ``(WaitAck, x = 4.999)``
* and infinitely many more in between

That is the core pressure point. Even before adding more processes or more
clocks, continuous time has already destroyed any hope of plain explicit
enumeration.

.. graphviz:: explicit_vs_symbolic.dot

The picture is intentionally simple: many concrete timed states in the same
control location can be summarized by one symbolic description.

Why Explicit Timed States Explode
---------------------------------

UPPAAL's semantics is defined over a timed transition system whose states have
the form

.. math::

   (L, v)

where :math:`L` is a location vector and :math:`v` is a valuation satisfying
the current invariants [UPP_SEM_SS]_.

This notation is compact, but the implication is large:

* :math:`L` fixes the current control locations
* :math:`v` fixes the current values of clocks and variables
* if clocks are real-valued, then even one fixed :math:`L` can correspond to infinitely many different concrete states

With two clocks the space is even richer. If a model allows both ``x`` and
``y`` to vary continuously, then the verifier is no longer facing a long list
of states, but a geometric space of possible valuations.

Why Symbolic States Help
------------------------

The official UPPAAL documentation gives the operational intuition very clearly:
the verifier explores symbolic states, and the symbolic simulator shows
symbolic traces rather than single concrete traces [UPP_VER_SS]_ [UPP_TRACE_SS]_.

For tutorial purposes, the key idea is:

* a symbolic state keeps the active locations fixed
* it keeps the discrete-variable values fixed
* it lets the clocks range over a whole set of valuations described by constraints

So instead of storing one valuation, we store a **set** of valuations:

.. math::

   Z = \{\, v \mid v \models g_1 \land \cdots \land g_k \,\}

Read this carefully:

* :math:`Z` is the zone-like clock part of the symbolic state
* :math:`v` ranges over valuations
* :math:`v \models g_i` means valuation :math:`v` satisfies constraint :math:`g_i`
* the conjunction :math:`g_1 \land \cdots \land g_k` says all listed clock constraints must hold together

For the running location ``WaitAck``, the simplest example is:

.. math::

   Z_{\mathrm{wait}} = \{\, v \mid 0 \leq v(x) \leq 5 \,\}

This single set stands for every concrete state whose control location is
``WaitAck`` and whose clock value stays inside the deadline window.

Regions And Zones Are Not The Same
----------------------------------

Two symbolic ideas are easy to mix up:

* **regions** provide a finite equivalence partition used in the theory of timed automata
* **zones** are larger constraint-defined sets of valuations that tools manipulate directly

The region viewpoint matters because it explains why timed-automata verification
can be made finite in principle. But UPPAAL-style tools are not built around
explicit region objects in day-to-day verification work. They are built around
zone-style constraints because delay, guard intersection, reset, and inclusion
tests become much more natural there [BY04_SS]_ [LPW95_SS]_.

A Concrete One-Clock Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose there is only one clock ``x`` and the largest constant mentioned by the
model is `2`.

Then the **region** viewpoint cuts the ``x``-axis into a fixed finite partition
such as:

* ``x = 0``
* ``0 < x < 1``
* ``x = 1``
* ``1 < x < 2``
* ``x = 2``
* ``x > 2``

That partition is fixed by the timed-automata theory. You do not choose it
dynamically during exploration.

Now compare that with the **zone**

.. math::

   Z = \{\, v \mid 0 \leq v(x) < 2 \,\}

This one zone contains many concrete valuations at once:

* :math:`v(x) = 0`
* :math:`v(x) = 0.2`
* :math:`v(x) = 0.8`
* :math:`v(x) = 1`
* :math:`v(x) = 1.7`

More importantly, it also contains **several different regions at once**:

* ``x = 0``
* ``0 < x < 1``
* ``x = 1``
* ``1 < x < 2``

That is the practical distinction:

* a **region** is one small cell in a fixed theoretical partition
* a **zone** is a constraint-defined set that the tool forms and manipulates as needed

So when people say zones are coarser than regions, this is exactly what they
mean: one zone often covers many region cells at once.

.. graphviz:: regions_vs_zone.dot

The point of the picture is not that one zone always contains exactly nine
regions. The point is that a zone is usually **coarser** than the underlying
region partition and therefore much more practical as an engineering object.

The tradeoff is important:

* regions give the clean finite quotient intuition
* zones give the practical symbolic representation
* naive zone graphs may still be infinite, which is why later pages need normalization and extrapolation

What Symbolic Successors Look Like
----------------------------------

Once valuations are grouped into a zone, the next step is to lift ordinary
timed-automata transitions from single valuations to sets of valuations.

For delay, the symbolic successor shape is:

.. math::

   \mathrm{Post}_{\mathrm{delay}}(Z)
   =
   \{\, v + d \mid v \in Z,\; d \in \mathbb{R}_{\geq 0} \,\}

For a discrete edge with guard :math:`g` and reset set :math:`R`, the shape is:

.. math::

   \mathrm{Post}_{e}(Z)
   =
   \{\, v[R := 0] \mid v \in Z,\; v \models g \,\}

These formulas should be read operationally:

* :math:`v \in Z` means we start from a valuation already represented by the current symbolic state
* :math:`d \in \mathbb{R}_{\geq 0}` means we allow non-negative delay
* :math:`v + d` means all clocks advance together by :math:`d`
* :math:`v \models g` means the valuation enables the chosen edge
* :math:`v[R := 0]` means all clocks in :math:`R` are reset to zero

In a real UPPAAL successor computation, invariants and target invariants also
restrict these sets. But even this simplified view already shows why the core
operation vocabulary later looks like ``up``, guard intersection, reset, and
containment tests.

Common Intuition Traps
----------------------

Three confusions are especially common here:

* **A symbolic state is not only a zone.** It also fixes the control locations and the discrete data part.
* **A zone is not an arbitrary shape.** It is a constraint-defined set of valuations, and in the basic DBM story it is convex.
* **A symbolic trace is not a promise about every point you see in it.** UPPAAL's symbolic-trace documentation explicitly warns that simulator traces are backward stable, but not necessarily forward stable [UPP_TRACE_SS]_.

Why This Matters For ``pyudbm``
-------------------------------

This page is exactly where the role of `pyudbm` becomes easier to explain.

`pyudbm` does **not** represent the whole UPPAAL symbolic state by itself. It
represents the clock-constraint layer underneath it:

* ``Context`` fixes the clock space
* ``Clock`` objects build the simple bounds and difference constraints
* ``Federation`` stores one or more symbolic valuation sets over those clocks

So when this repository restores a high-level Python DSL, it is rebuilding the
constraint technology that makes symbolic states workable, not trying to replace
the whole verifier.

What To Remember
----------------

If you keep five ideas from this page, keep these:

* concrete timed states are infinite because clocks range over real values
* a symbolic state keeps locations and discrete data fixed, but groups many valuations together
* zones are the practical constraint-based representation used by UPPAAL-style tools
* regions explain finiteness in theory, while zones explain tool efficiency in practice
* the later DBM layer exists because these zone operations need an efficient concrete representation

Next
----

The next natural page is :doc:`../dbm-basics/index`: once the zone view is
clear, the next question is why one matrix can encode such a set of clock
constraints efficiently.

.. [UPP_SEM_SS] UPPAAL official documentation, ``Semantics``.
   Public link: `<https://docs.uppaal.org/language-reference/system-description/semantics/>`_.
.. [UPP_VER_SS] UPPAAL official GUI documentation, ``Verifier``.
   Public link: `<https://docs.uppaal.org/gui-reference/verifier/>`_.
.. [UPP_TRACE_SS] UPPAAL official GUI documentation, ``Symbolic Traces``.
   Public link: `<https://docs.uppaal.org/gui-reference/symbolic-simulator/symbolic-traces/>`_.
.. [BY04_SS] Johan Bengtsson and Wang Yi.
   ``Timed Automata: Semantics, Algorithms and Tools``.
   Public link: `<https://uppaal.org/texts/by-lncs04.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README.md>`_.
.. [LPW95_SS] Kim Guldstrand Larsen, Paul Pettersson, and Wang Yi.
   ``Compositional and Symbolic Model-Checking of Real-Time Systems``.
   Public link: `<https://dblp.org/rec/conf/rtss/LarsenPW95>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/lpw95/README.md>`_.
