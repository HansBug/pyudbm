What Is UPPAAL Solving?
=======================

This page answers a basic question: what is UPPAAL for, and why does a
repository centered on the UDBM layer need to care about the broader UPPAAL
story at all?

The short answer is that UPPAAL is a tool chain for modeling and verifying
real-time systems. It is not only a bag of low-level matrix operations. It is a
workflow in which users build timed models, ask verification questions, and let
a symbolic engine explore large sets of clock valuations on their behalf
[LPY97]_ [BDL04]_ [BEH03]_.

The Running Example
-------------------

Consider a small request/response controller.

* A client sends a request.
* A server must acknowledge it within 5 time units.
* If no acknowledgement arrives before the deadline, the controller enters an
  error mode.

This is a good first example because it already contains the main ingredients
that make UPPAAL relevant:

* there is concurrency or interaction between components
* correctness depends on time, not only on ordering
* one bad run is enough to count as a bug

Even before any formal syntax appears, most readers already understand the key
question: can the system reach the error mode?

Why Testing Alone Is Not Always Enough
--------------------------------------

For ordinary software, testing and simulation are often the first tools we use.
They are still useful here, but they do not answer the same question as model
checking [LPY97]_ [BDL04]_.

Testing or simulation asks:
    "What happened in the runs that I tried?"

Model checking asks:
    "Is there *any* execution, among all executions allowed by the model, that
    violates the property?"

That distinction matters for timed systems. A request/response controller may
look fine in several simulated runs, yet still fail when one component delays
slightly longer than expected. Time creates infinitely many possible delays, so
the interesting bug may hide between two hand-picked test scenarios.

Why Time Makes Verification Harder
----------------------------------

In a timed model, the current control location is not enough. We also need the
current values of the clocks.

One standard way to write this is:

.. math::

   v : C \to \mathbb{R}_{\ge 0}

Here is the intended reading:

* :math:`C` is the set of clocks in the model.
* :math:`\mathbb{R}_{\ge 0}` is the set of non-negative real numbers.
* :math:`v` is a valuation, meaning that it assigns one current real-valued time
  reading to each clock.

The formula is short, but the idea behind it is important. It says that a clock
state is not just one integer counter or one Boolean flag. It is a whole map
from clock names to non-negative real values.

For the running example, if the request has just been sent, a clock
:math:`x` might start at :math:`0`. After 2.3 time units, the valuation might
map :math:`x` to :math:`2.3`. After 5.1 time units, the same run may already
have crossed the deadline and become erroneous.

That is why a concrete timed state is often written as:

.. math::

   (\ell, v)

This pair should be read carefully:

* :math:`\ell` is the current control location, such as ``WaitingForAck`` or
  ``Error``.
* :math:`v` is the current clock valuation defined above.

The intuition is that control flow alone is not enough. Two executions can both
be in ``WaitingForAck`` while still being very different, because one may have
waited :math:`1.2` time units and the other :math:`4.9`.

What UPPAAL Does At A High Level
--------------------------------

UPPAAL lets a user move through four high-level steps [LPY97]_ [BDL04]_ [BEH03]_:

* describe the system as a network of timed automata
* state a property or query about reachable behavior
* explore the model symbolically rather than one valuation at a time
* return either an answer or a diagnostic counterexample / witness

The whole workflow can be summarized like this:

.. graphviz::

   digraph uppaal_overview {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#f6f6f6", color="#666666"];
       model [label="Timed model"];
       query [label="Verification query"];
       engine [label="Symbolic exploration"];
       result [label="Answer or trace"];
       model -> query -> engine -> result;
   }

The key point is that the engine does not usually inspect one exact valuation at
a time. Later pages explain zones, DBMs, and federations in detail, but the
high-level reason already appears here: there are simply too many real-valued
clock states to enumerate naively [BEH03]_.

What Questions Users Usually Ask
--------------------------------

In practice, a user rarely asks "what is the exact set of all valuations?" as a
first question. They ask goal-shaped questions:

* Can the bad location be reached?
* Is a deadline always respected?
* Can the model deadlock?
* Is a recovery state still reachable after some fault?

For the running example, natural first questions are:

* Can ``Error`` be reached at all?
* Is every request eventually acknowledged before the 5-unit deadline?
* Can the model get stuck waiting forever?

The exact UPPAAL query language comes later. For now, the main intuition is
enough: the tool is built to answer behavioral questions about timed models, not
to expose raw DBM internals as the end-user experience.

Why Symbolic Exploration Enters The Story
-----------------------------------------

If time were discrete and tiny, we could try to enumerate states directly. But
timed systems are naturally described with real-valued clocks, so exact
enumeration quickly becomes hopeless.

That is why UPPAAL moves from concrete states :math:`(\ell, v)` to symbolic
states that stand for many valuations at once. A common later notation is
:math:`(\ell, Z)`, where :math:`Z` is a zone.

This page does not develop zones in detail yet, but the intuition matters now:

* a symbolic state represents many concrete timed states together
* symbolic exploration is what makes verification practical
* DBMs and federations are engineering devices in service of that larger goal

This is exactly where UDBM fits into the picture. UDBM does not tell the whole
UPPAAL story by itself, but it implements one of the most important symbolic
representation layers inside that story.

How This Connects To ``pyudbm``
-------------------------------

This repository currently wraps the UDBM layer rather than shipping a complete
UPPAAL model checker. Even so, the broader context still matters.

The reason is simple: historical UDBM Python bindings did not feel natural
because users wanted "a matrix library." They felt natural because they matched
the way UPPAAL users think:

* named clocks
* readable timing constraints
* symbolic sets of valuations
* operations that feel like model-level manipulations rather than raw table edits

That is why :mod:`pyudbm` restores ``Context``, ``Clock``, and ``Federation`` as
first-class objects. Those objects are most understandable when placed back into
the full user workflow that UPPAAL popularized.

What To Remember From This Page
-------------------------------

If you only keep four things in mind, keep these:

* UPPAAL is about verifying timed behavior, not only simulating it.
* Time makes state spaces much harder, because clocks range over real values.
* Symbolic exploration is the practical response to that difficulty.
* UDBM and this repository matter because they support one core layer of that
  symbolic workflow.

Further Reading
---------------

Then continue with the next concept page once it is added: ``timed-automata/``.

References
----------

.. [LPY97] Kim Guldstrand Larsen, Paul Pettersson, and Wang Yi.
   ``UPPAAL in a Nutshell.``
   Public link: `<https://dblp.org/rec/journals/sttt/LarsenPY97>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/lpy97/README.md>`_.
.. [BDL04] Gerd Behrmann, Alexandre David, and Kim Guldstrand Larsen.
   ``A Tutorial on UPPAAL.``
   Public link: `<https://dblp.org/rec/conf/sfm/BehrmannDL04>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/bdl04/README.md>`_.
.. [BEH03] Gerd Behrmann.
   ``Data Structures and Algorithms for the Analysis of Real Time Systems``.
   Public link: `<https://uppaal.org/texts/behrmann_phd.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/behrmann03/paper-intro/README.md>`_.
