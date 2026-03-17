Timed Automata
==============

This page answers the next natural question after
:doc:`../what-is-uppaal/index`: **what is the actual model that evolves over
time?**

For UPPAAL, the basic modeling object is a network of timed automata. Each
automaton looks like a finite-state machine, but it is extended with
real-valued clocks, clock constraints, resets, and location invariants
[UPP_LOC]_ [UPP_EDGE]_ [UPP_SEM]_.

The Running Example
-------------------

Consider a tiny request/response controller with one clock ``x``:

* in ``Idle``, the system may send a request and reset ``x`` to zero
* in ``WaitAck``, it waits for an acknowledgement while ``x <= 5``
* if an acknowledgement arrives in time, the system returns to ``Idle``
* if time reaches the deadline, the system can take a timeout transition to ``Error``

.. graphviz:: request_response.dot

This is already a timed automaton, not just a control sketch:

* ``send`` and ``ack`` are action labels: ``send`` means "a request is sent", and ``ack`` means "an acknowledgement is received"
* in UPPAAL-style notation, ``!`` means sending on a channel and ``?`` means receiving from a channel
* the edge label ``send! / x := 0`` means "send the request and reset ``x`` to zero"
* the edge label ``ack?`` means "receive the acknowledgement"
* the edge label ``timeout!`` means "emit a timeout event"
* the invariant ``x <= 5`` restricts how long the automaton may remain in ``WaitAck``
* the guard ``x >= 5`` enables the timeout edge exactly at the deadline

The Basic Definition
--------------------

One standard definition writes a timed automaton as

.. math::

   A = (L, \ell_0, C, \Sigma, E, \mathrm{Inv})

Read the tuple like this:

* :math:`L` is a finite set of locations
* :math:`\ell_0 \in L` is the initial location
* :math:`C` is a finite set of clocks
* :math:`\Sigma` is a set of action labels
* :math:`E \subseteq L \times \Sigma \times G(C) \times 2^C \times L` is the edge relation
* :math:`\mathrm{Inv}` assigns an invariant to each location

The set :math:`G(C)` contains the clock constraints used as guards and
invariants. A convenient syntax is:

.. math::

   g ::= x \bowtie c \mid x - y \bowtie c \mid g \land g

where :math:`x, y \in C`, :math:`c \in \mathbb{Z}`, and
:math:`\bowtie \in \{<, \le, =, \ge, >\}`.

This notation is not accidental. The whole later zone / DBM story depends on
the fact that guards and invariants are conjunctions of simple clock
constraints rather than arbitrary real arithmetic [AD90]_ [BY04]_.

Returning to the running example above, the tuple can be unpacked concretely as:

.. math::

   A = (L, \ell_0, C, \Sigma, E, \mathrm{Inv})

with:

* :math:`L = \{\mathrm{Idle}, \mathrm{WaitAck}, \mathrm{Error}\}`,
  the three locations shown in the figure
* :math:`\ell_0 = \mathrm{Idle}`,
  because the system starts before any request has been sent
* :math:`C = \{x\}`,
  because the example uses only one clock
* :math:`\Sigma = \{\mathrm{send}, \mathrm{ack}, \mathrm{timeout}\}`,
  representing the three discrete actions "send a request", "receive an acknowledgement", and "timeout occurs"
* :math:`E`, the set of edges in the figure:

  .. math::

     E = \{
     (\mathrm{Idle}, \mathrm{send}, \mathrm{true}, \{x\}, \mathrm{WaitAck}),
     (\mathrm{WaitAck}, \mathrm{ack}, \mathrm{true}, \emptyset, \mathrm{Idle}),
     (\mathrm{WaitAck}, \mathrm{timeout}, x \ge 5, \emptyset, \mathrm{Error})
     \}

  The first edge means "send the request and reset ``x``", the second means
  "receive the acknowledgement and return to ``Idle``", and the third means
  "once :math:`x \ge 5`, a timeout may move the system to ``Error``"
* :math:`\mathrm{Inv}`, which assigns an invariant to each location:

  .. math::

     \mathrm{Inv}(\mathrm{Idle}) = \mathrm{true}, \qquad
     \mathrm{Inv}(\mathrm{WaitAck}) = (x \le 5), \qquad
     \mathrm{Inv}(\mathrm{Error}) = \mathrm{true}

  So ``WaitAck`` is the only location with an actual time bound in this toy example, while ``Idle`` and ``Error`` impose no additional delay limit

If you also keep the diagram labels ``send!``, ``ack?``, and ``timeout!`` in
mind, those are UPPAAL-style direction markers used in network semantics: this
automaton sends ``send`` and ``timeout``, and receives ``ack``. For the
mathematical tuple above, it is enough to record the action names as
:math:`\mathrm{send}`, :math:`\mathrm{ack}`, and :math:`\mathrm{timeout}`.

Why A State Needs A Valuation
-----------------------------

In an ordinary finite automaton, a control location is often enough to describe
the current state. In a timed automaton, it is not.

We also need a **clock valuation**:

.. math::

   v : C \to \mathbb{R}_{\ge 0}

Each symbol here has a concrete meaning:

* :math:`v` is a valuation, meaning "the current value assigned to each clock"
* :math:`C` is the clock set; in the running example, :math:`C = \{x\}`
* :math:`\to` means "maps from one set to another"
* :math:`\mathbb{R}_{\ge 0}` is the set of non-negative real numbers, such as `0`, `0.3`, `2.7`, and `5`

So :math:`v : C \to \mathbb{R}_{\ge 0}` simply means:
**the valuation :math:`v` assigns a non-negative real value to every clock.**

In the running example there is only one clock, so a valuation is basically
telling us something like:

.. math::

   v(x) = 0
   \qquad \text{or} \qquad
   v(x) = 3.2
   \qquad \text{or} \qquad
   v(x) = 5

So a concrete timed state is written as :math:`(\ell, v)`, where:

* :math:`\ell` is the current location
* :math:`v` gives the current clock values

For example, :math:`(\mathrm{WaitAck}, v)` with :math:`v(x) = 4.9` means the
system is in ``WaitAck`` and already very close to the timeout boundary.

Two helper notations are standard:

.. math::

   (v + d)(x) = v(x) + d
   \qquad\qquad
   v[R := 0](x) =
   \begin{cases}
   0 & \text{if } x \in R, \\
   v(x) & \text{otherwise.}
   \end{cases}

These symbols are worth unpacking too:

* :math:`d` is the amount of elapsed time, such as `1` or `2.5`
* :math:`(v + d)` means "start from valuation :math:`v` and let all clocks increase by :math:`d`"
* :math:`(v + d)(x)` asks for the value of clock :math:`x` after that delay
* :math:`R` is the set of clocks that will be reset
* :math:`v[R := 0]` means "start from :math:`v` and replace every clock in :math:`R` by `0`"
* :math:`v[R := 0](x)` asks for the value of clock :math:`x` after the reset

The first means "let time elapse by :math:`d`". The second means "reset all
clocks in :math:`R` to zero".

In the running example, because there is only one clock ``x``:

* if :math:`v(x) = 1` and we wait `2` time units, then :math:`(v + 2)(x) = 3`
* if :math:`v(x) = 4` and some action resets ``x``, then for :math:`R = \{x\}` we get :math:`v[R := 0](x) = 0`

For the running example, ``(WaitAck, x = 1)`` and ``(WaitAck, x = 4.9)`` are
different states even though the control location is the same. One is still far
from the timeout boundary; the other is almost forced to leave immediately.

Two Kinds Of Transition
-----------------------

Timed automata evolve in two fundamentally different ways:

* **delay transitions**, where time passes and all clocks grow together
* **discrete transitions**, where an enabled edge is taken and some clocks may be reset

For delay, the semantic rule is:

.. math::

   (\ell, v) \xrightarrow{d} (\ell, v + d)
   \quad \text{if } d \in \mathbb{R}_{\ge 0}
   \text{ and } \forall \delta \in [0, d],\; v + \delta \models \mathrm{Inv}(\ell)

Here the notation means:

* :math:`(\ell, v)` is the current state
* :math:`\xrightarrow{d}` means "evolves by delaying :math:`d` time units"
* :math:`\forall \delta \in [0, d]` means "for every intermediate time point between `0` and :math:`d`"
* :math:`\models` means "satisfies"; for example, :math:`v \models x \le 5` means the valuation :math:`v` makes the constraint :math:`x \le 5` true
* :math:`\mathrm{Inv}(\ell)` is the invariant attached to location :math:`\ell`

The important part is the universal condition over :math:`\delta`. It says the
invariant must stay true during the *entire* waiting interval, not only at the
end.

For a discrete edge :math:`e = (\ell, a, g, R, \ell')`, the rule is:

.. math::

   (\ell, v) \xrightarrow{a} (\ell', v[R := 0])
   \quad \text{if } v \models g
   \text{ and } v[R := 0] \models \mathrm{Inv}(\ell')

Here:

* :math:`a` is the discrete action label
* :math:`g` is the guard
* :math:`R` is the reset set
* :math:`\ell'` is the target location

This separates the roles cleanly:

* the **guard** says when the edge is enabled
* the **reset set** says which clocks jump back to zero
* the **target invariant** says whether the destination may be entered legally

Here is the same running example viewed as concrete timed states:

.. graphviz:: state_evolution.dot

The key semantic point is that the automaton may delay from ``x = 0`` to
``x = 5``, but not beyond. Once the boundary is reached, a discrete choice has
to happen.

From One Automaton To A Network
-------------------------------

UPPAAL usually works with **networks** of timed automata rather than only one
automaton in isolation. A global state then has the shape

.. math::

   ((\ell_1, \ldots, \ell_n), v)

where each :math:`\ell_i` is the current location of one process and
:math:`v` is the shared clock valuation.

The intuition is:

* time delay is global, so all clocks advance together
* discrete steps may belong to one process alone, or to several processes synchronized by channels
* the verifier explores this infinite timed state space symbolically rather than valuation by valuation

This page stays with a single automaton because that is the smallest setting in
which clocks, guards, resets, and invariants already make semantic sense.

Common Intuition Traps
----------------------

Three confusions are especially common when timed automata are new:

* **A location is not a full state.** The valuation is part of the state too.
* **An invariant is not just another guard.** A guard controls an edge; an invariant controls how long time may remain in a location.
* **Reaching a boundary often forces a choice.** If no more delay is legal, the next move must be discrete or the run deadlocks.

Why This Matters For ``pyudbm``
-------------------------------

This repository does not yet expose the whole UPPAAL language or full network
semantics. But the timed-automata viewpoint already explains why the Python API
needs clock-oriented objects:

* ``Context`` fixes the clock set :math:`C`
* ``Clock`` objects build guards and clock-difference constraints
* ``Federation`` represents sets of valuations satisfying those constraints

So when `pyudbm` wraps clock constraints, it is not exposing random matrix
plumbing. It is exposing the symbolic layer underneath guards, invariants, and
reachable timed states.

What To Remember
----------------

If you keep five ideas from this page, keep these:

* a timed automaton is a finite control graph plus clocks
* a concrete state is ``(location, valuation)``
* time elapse and discrete edges are separate transition kinds
* invariants bound how long time may stay in one location
* these clock constraints are exactly what later become zones and DBMs

Next
----

The next natural page is ``queries-and-properties/``: once the model is clear,
the next question is what users usually ask about it.

References
----------

.. [UPP_LOC] UPPAAL official documentation, ``Locations``.
   Public link: `<https://docs.uppaal.org/language-reference/system-description/templates/locations/>`_.
.. [UPP_EDGE] UPPAAL official documentation, ``Edges``.
   Public link: `<https://docs.uppaal.org/language-reference/system-description/templates/edges/>`_.
.. [UPP_SEM] UPPAAL official documentation, ``Semantics``.
   Public link: `<https://docs.uppaal.org/language-reference/system-description/semantics/>`_.
.. [AD90] Rajeev Alur and David L. Dill.
   ``Automata for Modeling Real-Time Systems``.
   Public link: `<https://dblp.org/rec/conf/icalp/AlurD90>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/ad90/README.md>`_.
.. [BY04] Johan Bengtsson and Wang Yi.
   ``Timed Automata: Semantics, Algorithms and Tools``.
   Public link: `<https://uppaal.org/texts/by-lncs04.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README.md>`_.
