What Is UPPAAL?
===============

This page is a beginner-friendly introduction. It answers one simple question:
**what problem is UPPAAL trying to solve?**

**UPPAAL is a tool environment for modeling, simulating, and verifying
real-time systems.** The official web site describes it as an integrated
environment for networks of timed automata with data types, and the official
documentation describes it as a tool for non-deterministic processes with
finite control structure and real-valued clocks [UPP_HOME]_ [UPP_HELP]_.

For this repository, the big picture matters because `pyudbm` wraps one layer
of that world. UDBM is not the whole UPPAAL story, but it supports one of the
most important symbolic representations inside it.

A Tiny Example
--------------

Consider a small request/response controller:

* a client sends a request
* a server should acknowledge it within 5 time units
* if no acknowledgement arrives in time, the system enters ``Error``

Even if you know nothing else yet, the core question already makes sense:
**can the system reach the error state?**

Here is a simple control sketch:

.. graphviz::

   digraph control_loop {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#f8f8f8", color="#666666"];
       client [label="Client\nsend request"];
       controller [label="Controller\nstart clock x"];
       server [label="Server\nsend ack"];
       error [label="Error if x > 5\nbefore ack", fillcolor="#fff1f1", color="#aa5555"];
       client -> controller [label="request"];
       controller -> server [label="dispatch"];
       server -> controller [label="ack"];
       controller -> error [label="deadline miss"];
   }

This is not yet a timed-automaton diagram. It is only here to make the story
concrete before we introduce more terminology.

Why Not Just Test It?
---------------------

Testing and simulation are still useful, but they answer a different question.

Testing asks:
    "What happened in the executions that I tried?"

Model checking asks:
    "Is there *any* execution allowed by the model that violates the property?"

That difference matters a lot for timed systems. A few sample runs may look
fine, but the bad run might be the one where a component waits just a little
too long. Time introduces many possible delays, so bugs can hide between the
runs you happened to test [LPY97]_ [BDL04]_.

Why Time Makes Things Harder
----------------------------

In an untimed model, a state is often described mainly by control flow:
"where am I in the program or automaton?"

In a timed model, that is not enough. **We also need the current clock
values.**

One standard notation is:

.. math::

   v : C \to \mathbb{R}_{\ge 0}

Read it like this:

* :math:`C` is the set of clocks
* :math:`v` gives each clock a non-negative real value

That means two runs can be in the same control location and still be very
different, because one may have waited `1.2` time units and the other `4.9`.

For the running example, that difference is exactly what separates "still safe"
from "deadline already missed".

What Does UPPAAL Actually Do?
-----------------------------

At a high level, UPPAAL supports a simple workflow:

* build a timed model
* simulate possible behavior
* ask a verification query
* get either an answer or a diagnostic trace

That workflow looks like this:

.. graphviz::

   digraph uppaal_overview {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#f6f6f6", color="#666666"];
       model [label="Timed model"];
       sim [label="Simulation"];
       query [label="Query"];
       engine [label="Symbolic exploration"];
       result [label="Answer or trace"];
       model -> sim;
       model -> query;
       sim -> query;
       query -> engine -> result;
   }

The official documentation also makes clear that UPPAAL is not only a language,
but a tool environment with a GUI, a verifier, simulators, and command-line
use [UPP_HELP]_ [UPP_FEATURES]_.

Why Symbolic States Appear
--------------------------

If clocks are real-valued, then there are too many exact timed states to list
one by one. That is why UPPAAL does not work only with single concrete states.
It groups many valuations together into **symbolic states**.

You do not need the details yet. For now, the key idea is simple:

* exact timed states are too numerous
* symbolic states group many of them together
* this is what makes verification practical

Later pages explain zones, DBMs, and federations. This page only needs to give
you the reason they appear at all.

Why This Matters For ``pyudbm``
-------------------------------

`pyudbm` does not currently implement the whole UPPAAL tool chain. It wraps the
UDBM layer. But that layer makes much more sense when you remember the larger
workflow.

**Users do not think in raw matrices first.** They think in clocks,
constraints, reachable behavior, and error conditions. That is why this
repository restores high-level objects such as ``Context``, ``Clock``, and
``Federation``.

What To Remember
----------------

If you only keep five ideas from this page, keep these:

* **UPPAAL is for timed systems.**
* **It helps users model, simulate, and verify them.**
* **Testing a few runs is not the same as checking all possible runs.**
* **Real-valued clocks make timed verification harder.**
* **Symbolic states are the practical answer to that difficulty.**

Next
----

The next concept page is :doc:`../timed-automata/index`. That is where the
actual model shape gets introduced.

References
----------

.. [UPP_HOME] UPPAAL official web site.
   Public link: `<https://uppaal.org/>`_.
.. [UPP_HELP] UPPAAL official documentation overview.
   Public link: `<https://docs.uppaal.org/>`_.
.. [UPP_FEATURES] UPPAAL official features page.
   Public link: `<https://uppaal.org/features/>`_.
.. [LPY97] Kim Guldstrand Larsen, Paul Pettersson, and Wang Yi.
   ``UPPAAL in a Nutshell.``
   Public link: `<https://dblp.org/rec/journals/sttt/LarsenPY97>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/lpy97/README.md>`_.
.. [BDL04] Gerd Behrmann, Alexandre David, and Kim Guldstrand Larsen.
   ``A Tutorial on UPPAAL.``
   Public link: `<https://dblp.org/rec/conf/sfm/BehrmannDL04>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/bdl04/README.md>`_.
