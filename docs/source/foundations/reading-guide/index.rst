Reading Guide
=============

**This section is the concept-oriented companion to**
:doc:`/tutorials/installation/index`. **It is not mainly about installation
steps or command sequences.** Its job is to explain what the core UPPAAL
concepts mean, why they are needed, and how they connect to the Python-facing
direction of :mod:`pyudbm`.

How To Use This Section
-----------------------

Use this section when you are asking questions such as:

* What problem is UPPAAL trying to solve?
* Why is time harder than ordinary finite-state verification?
* Why do symbolic states, zones, DBMs, and federations appear at all?
* Which concepts do I need before the high-level Python API starts to feel natural?

If you only want to install the package or run a quick smoke check, start with
:doc:`/tutorials/installation/index` instead.

Reading Routes
--------------

**This entry page is meant to be a reading router rather than a flat
directory.** Different readers should start in different places.

If you are new to formal verification or model checking:
    **Start with** :doc:`../what-is-uppaal/index`.

If you already know what model checking is, but timed automata still feel unfamiliar:
    **Start with** :doc:`../what-is-uppaal/index`, then continue to
    :doc:`../timed-automata/index`.

If you already know timed automata, but symbolic states and zones still feel abstract:
    Read :doc:`../what-is-uppaal/index` for the big-picture workflow first, then
    continue to the planned ``symbolic-states/`` and ``dbm-basics/`` pages.

If you already know zones and DBMs, but do not yet see why non-convex symbolic sets matter:
    Skim :doc:`../what-is-uppaal/index`, then continue to the planned
    ``federations/`` and ``cdd/`` pages.

If your main concern is the future Python-facing architecture of this repository:
    **Read** :doc:`../what-is-uppaal/index` **first**, because it explains the
    user-facing verification workflow that the restored ``Context`` /
    ``Clock`` / ``Federation`` model is trying to serve.

Current Coverage
----------------

.. toctree::
    :maxdepth: 2

    ../what-is-uppaal/index
    ../timed-automata/index

Planned Sequence
----------------

The current concept roadmap is:

* ``what-is-uppaal/``
* ``timed-automata/``
* ``queries-and-properties/``
* ``symbolic-states/``
* ``dbm-basics/``
* ``federations/``
* ``cdd/``
* search / extrapolation / storage topics
* reduction-oriented topics
* priced timed automata and API reconstruction topics

How This Relates To Other Doc Areas
-----------------------------------

**The three documentation areas serve different jobs:**

* :doc:`/tutorials/installation/index` **answers** "How do I install or build it?"
* ``foundations/`` **answers** "What do these concepts mean?"
* ``papers/`` in the repository **answers** "Which papers and reading guides are these explanations based on?"

For this repository in particular, that separation matters. ``pyudbm`` is not
trying to be a complete UPPAAL clone today, but it is trying to rebuild a thin,
high-level Python surface on top of the UDBM layer in a way that still makes
sense inside the larger UPPAAL story.
