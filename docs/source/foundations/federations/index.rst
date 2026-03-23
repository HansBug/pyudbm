Federations: Exact Unions Of DBM Zones
======================================

This page answers the next question after
:doc:`../dbm-basics/index`: **if one DBM already represents one convex zone
exactly, what should we do when symbolic manipulation produces a non-convex
set?**

For UDBM, the answer is a **federation**: a finite union of DBMs. That is the
next exact representation layer above one canonical DBM, and it is the reason
why the high-level Python API is centered on :class:`pyudbm.Federation`
rather than on bare matrices alone [DHLP06_FED]_ [BEHR03_CDD]_ [UDBM_FED_H]_
[UDBM_FED_CPP]_.

This page is still a tutorial page first. So it does not start as a reference
sheet. It first explains why federations become necessary at all, then why
they matter for UDBM and :mod:`pyudbm`, and only after that does it inventory
the current Federation surface in a more systematic way.

The goal is to make the connection between:

* the theory reason for federations,
* the native UDBM federation layer in ``fed.h`` / ``fed.cpp``, and
* the current :mod:`pyudbm` API

explicit and easy to scan.

Why One DBM Stops Being Enough
------------------------------

The key limitation to remember from the previous page is simple:

* one DBM represents one convex zone
* symbolic algorithms do not stay inside the convex world forever

Subtraction is the cleanest place to see the break.

Take one outer zone :math:`Z` and subtract one inner zone :math:`H`:

.. math::

   Z = \{(x,y) \mid 1 \leq x \leq 5,\; 1 \leq y \leq 5\}

.. math::

   H = \{(x,y) \mid 2 \leq x \leq 4,\; 2 \leq y \leq 4\}

.. math::

   R = Z \setminus H

The result is not convex anymore. It is one rectangular shell with a hole in
the middle:

.. image:: subtract_nonconvex.plot.py.svg
   :width: 94%
   :align: center
   :alt: Three-panel figure showing an outer zone, an inner hole, and the non-convex subtraction result.

This is exactly the pressure described in the subtraction paper by David,
Larsen, Lime, and Poulsen [DHLP06_FED]_: once subtraction leaves the convex
world, a single DBM is no longer a sufficient exact target.

In UDBM, the exact result therefore becomes a union of DBMs rather than one new
matrix. In the current Python binding, the same example can be written
directly:

.. code-block:: python

   from pyudbm import Context, IntValuation

   c = Context(["x", "y"])
   x = c.x
   y = c.y

   outer = (x >= 1) & (x <= 5) & (y >= 1) & (y <= 5)
   hole = (x >= 2) & (x <= 4) & (y >= 2) & (y <= 4)
   ring = outer - hole

   assert ring.get_size() == 4

   inside = IntValuation(c)
   inside["x"] = 1
   inside["y"] = 1

   removed = IntValuation(c)
   removed["x"] = 3
   removed["y"] = 3

   assert ring.contains(inside)
   assert not ring.contains(removed)

Mathematically, that means

.. math::

   R = D_1 \cup D_2 \cup D_3 \cup D_4

with each :math:`D_i` still an ordinary convex DBM zone.

What A Federation Means In UDBM
-------------------------------

A federation is not a mysterious new constraint language. It is a finite union
of ordinary DBM zones:

.. math::

   F = D_1 \cup D_2 \cup \cdots \cup D_n

where every :math:`D_i` is still one convex DBM.

That design choice matters for two reasons.

First, it preserves the DBM machinery instead of replacing it. The algorithms
for closure, relation checks, delay, reset, and containment still operate at
the DBM level; the federation layer lifts them to finite unions [UDBM_FED_H]_
[UDBM_FED_CPP]_.

Second, it keeps non-convex symbolic states exact. In the native code, this is
the job of ``fed_t`` in ``fed.h`` / ``fed.cpp``. The implementation is not a
diagram structure like a CDD. It is an explicit federation layer with set
operations, subtraction, reduction, predecessor-style operators, and relation
checks on unions of DBMs [DHLP06_FED]_ [BEHR03_CDD]_.

What Federations Can Do
-----------------------

The current Federation operations and properties can be grouped like this:

This table focuses on the **semantics-facing Federation surface** currently
exposed by the Python binding. It intentionally excludes object-infrastructure
helpers such as ``copy()``, ``plot()``, textual rendering, and hashing.

.. list-table::
   :header-rows: 1
   :widths: 18 16 14 18 34

   * - API
     - Kind
     - Semantics
     - Mutation Style
     - Jump To Details
   * - ``to_dbm_list()``
     - Representation
     - Exact
     - Returns snapshots
     - :ref:`fed-to-dbm-list`
   * - ``get_size()``
     - Representation
     - Exact
     - Query only
     - :ref:`fed-get-size`
   * - ``&``
     - Set operation
     - Exact
     - Returns new federation
     - :ref:`fed-and`
   * - ``|``
     - Set operation
     - Exact
     - Returns new federation
     - :ref:`fed-or`
   * - ``+``
     - Set operation
     - Convex over-approximation
     - Returns new federation
     - :ref:`fed-add`
   * - ``-``
     - Set operation
     - Exact
     - Returns new federation
     - :ref:`fed-sub`
   * - ``up()``
     - Time transform
     - Exact
     - Returns new federation
     - :ref:`fed-up`
   * - ``down()``
     - Time transform
     - Exact
     - Returns new federation
     - :ref:`fed-down`
   * - ``free_clock()``
     - Clock transform
     - Exact
     - Returns new federation
     - :ref:`fed-free-clock`
   * - ``set_zero()``
     - Re-initialization
     - Exact
     - Mutates ``self``
     - :ref:`fed-set-zero`
   * - ``has_zero()``
     - Property
     - Exact
     - Query only
     - :ref:`fed-has-zero`
   * - ``set_init()``
     - Re-initialization
     - Exact
     - Mutates ``self``
     - :ref:`fed-set-init`
   * - ``convex_hull()``
     - Shape transform
     - Convex over-approximation
     - Returns new federation
     - :ref:`fed-convex-hull`
   * - ``==`` / ``!=``
     - Relation
     - Exact
     - Query only
     - :ref:`fed-relations`
   * - ``<=`` / ``>=`` / ``<`` / ``>``
     - Relation
     - Exact
     - Query only
     - :ref:`fed-relations`
   * - ``intern()``
     - Representation maintenance
     - Geometry-preserving
     - Mutates internal sharing state
     - :ref:`fed-intern`
   * - ``predt()``
     - Temporal transform
     - Exact
     - Returns new federation
     - :ref:`fed-predt`
   * - ``contains()``
     - Membership
     - Exact
     - Query only
     - :ref:`fed-contains`
   * - ``update_value()``
     - Clock assignment
     - Exact
     - Returns new federation
     - :ref:`fed-update-value`
   * - ``reset_value()``
     - Clock assignment
     - Exact
     - Returns new federation
     - :ref:`fed-reset-value`
   * - ``reduce()``
     - Representation maintenance
     - Geometry-preserving
     - Mutates ``self``
     - :ref:`fed-reduce`
   * - ``extrapolate_max_bounds()``
     - Abstraction
     - Over-approximation
     - Returns new federation
     - :ref:`fed-extrapolate-max-bounds`
   * - ``is_zero()``
     - Property
     - Exact
     - Query only
     - :ref:`fed-is-zero`
   * - ``is_empty()``
     - Property
     - Exact
     - Query only
     - :ref:`fed-is-empty`

Representation And Structural Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _fed-to-dbm-list:

Decomposing A Federation With ``to_dbm_list()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most direct way to see what a federation is internally is to export its
DBM pieces:

.. image:: decompose.plot.py.svg
   :width: 54%
   :align: center
   :alt: A federation drawn as two convex DBM pieces.

.. code-block:: python

   from pyudbm import Context

   c = Context(["x", "y"])
   x = c.x
   y = c.y

   fed = ((x >= 1) & (x <= 2) & (y >= 1) & (y <= 3)) | ((x >= 4) & (x <= 5) & (y >= 2) & (y <= 4))
   pieces = fed.to_dbm_list()

   assert len(pieces) == 2

This is exact representation inspection, not approximation. It is especially
useful when subtraction or exact union has produced several convex pieces.

.. _fed-get-size:

Counting Pieces With ``get_size()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same decomposition figure also explains ``get_size()``:

.. code-block:: python

   assert fed.get_size() == 2

``get_size()`` counts native DBMs, not visible edges, constraints, or vertices.
So its meaning is representational: how many convex components are currently
stored in the federation.

.. _fed-reduce:
.. _fed-intern:

Representation Quality: ``reduce()`` And ``intern()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Federations are not only about set semantics. Once many DBMs accumulate, their
representation quality starts to matter too:

.. image:: fed_reduce_intern.plot.py.svg
   :width: 88%
   :align: center
   :alt: Three-panel figure showing a federation before reduction, after reduction, and after intern.

``reduce()`` tries to clean up the DBM list while preserving the represented
set. In the figure, the left federation is represented by two overlapping DBMs,
while the middle panel shows the same set after reduction:

.. code-block:: python

   reduced = fed.copy().reduce()
   assert reduced == fed

``intern()`` is different. It is not a geometric or semantic transformation at
all. It asks UDBM to share equal canonical DBMs internally through its hash
tables:

.. code-block:: python

   before = fed.copy()
   fed.intern()
   assert fed == before

So the right mental split is:

* ``reduce()`` tries to improve the visible DBM list
* ``intern()`` tries to improve internal sharing and equality costs
* neither is supposed to change the symbolic set

Set Operations
~~~~~~~~~~~~~~

.. _fed-and:

Exact Intersection ``&``
~~~~~~~~~~~~~~~~~~~~~~~~

Intersection stays inside the exact symbolic world:

.. image:: fed_and.plot.py.svg
   :width: 92%
   :align: center
   :alt: Three-panel figure showing two zones and their exact intersection.

.. code-block:: python

   left = (x >= 1) & (x <= 4) & (y >= 1) & (y <= 4)
   right = (x >= 3) & (x <= 5) & (y >= 2) & (y <= 5)
   exact_intersection = left & right

The result is exact and usually still convex enough to fit into one DBM.

.. _fed-or:

Exact Union ``|``
~~~~~~~~~~~~~~~~~

Exact union keeps all pieces and keeps all gaps:

.. image:: union_vs_hull.plot.py.svg
   :width: 88%
   :align: center
   :alt: Two-panel figure showing exact union and convex hull.

In the left panel, the federation really is two separated regions:

.. code-block:: python

   exact = a | b

This is the natural federation-building operation when symbolic branching or
subtraction has produced multiple exact components.

.. _fed-add:

Convex Union ``+``
~~~~~~~~~~~~~~~~~~

``+`` is **not** the same as ``|``. It computes UDBM's convex-union style
addition:

.. code-block:: python

   hull_like = a + b

For the separated example in the figure, that fills the gap and introduces new
valuations. So ``+`` is already an over-approximation-style operation, not a
plain exact set union.

This distinction between ``|`` and ``+`` is exactly where the geometric
difference between **exact union** and **convex hull-like combination** belongs:
the left panel keeps the gap, the right panel fills it. Federation support is
therefore not just "store several DBMs in one object"; different operators
really do have different symbolic meanings.

.. _fed-sub:

Exact Difference ``-``
~~~~~~~~~~~~~~~~~~~~~~

Subtraction is the cleanest place where one DBM stops being enough, which is
why it already appeared in the tutorial motivation above. At the API level the
same idea is simply:

.. code-block:: python

   ring = outer - hole

Transformations On Federations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _fed-up:

Delay Successor ``up()``
~~~~~~~~~~~~~~~~~~~~~~~~

``up()`` lifts the usual DBM delay successor to every DBM in the federation:

.. image:: fed_up.plot.py.svg
   :width: 88%
   :align: center
   :alt: Before and after figure for federation up.

.. code-block:: python

   delayed = fed.up()

Semantically, upper bounds against the zero clock are relaxed so time can
elapse.

.. _fed-down:

Inverse Delay ``down()``
~~~~~~~~~~~~~~~~~~~~~~~~

``down()`` is the temporal predecessor counterpart:

.. image:: fed_down.plot.py.svg
   :width: 88%
   :align: center
   :alt: Before and after figure for federation down.

.. code-block:: python

   predecessor = fed.down()

This relaxes lower bounds so that delaying can lead into the current
federation.

.. _fed-free-clock:

Forgetting One Clock With ``free_clock()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Freeing a clock removes the informative constraints involving it:

.. image:: fed_free.plot.py.svg
   :width: 88%
   :align: center
   :alt: Before and after figure for freeClock.

.. code-block:: python

   freed = fed.free_clock(y)

Geometrically, this often turns a bounded shape into a strip or half-space.

.. _fed-set-zero:

Re-initializing To The Origin With ``set_zero()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``set_zero()`` mutates the federation into the single origin valuation:

.. image:: fed_set_zero.plot.py.svg
   :width: 88%
   :align: center
   :alt: Before and after figure for setZero.

.. code-block:: python

   zone.set_zero()
   assert zone.has_zero()

This is exact, not symbolic shorthand.

.. _fed-set-init:

Re-initializing To The Positive Initial Zone With ``set_init()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``set_init()`` replaces the current federation by the standard non-negative
initial zone:

.. image:: fed_set_init.plot.py.svg
   :width: 88%
   :align: center
   :alt: Before and after figure for setInit.

.. code-block:: python

   zone.set_init()
   assert str(zone) == "true"

This is the UDBM-style "all clocks are non-negative, otherwise unconstrained"
initial symbolic state.

.. _fed-convex-hull:

Convex Hull With ``convex_hull()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``convex_hull()`` works on one federation and computes one convex
over-approximation:

.. image:: union_vs_hull.plot.py.svg
   :width: 88%
   :align: center
   :alt: Exact union versus convex hull.

.. code-block:: python

   hull = exact.convex_hull()

This differs from ``+`` only in arity and use style:

* ``a + b`` combines two arguments by convex union
* ``f.convex_hull()`` hulls all DBMs already inside one federation

.. _fed-predt:

Temporal Predecessor ``predt()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``predt()`` computes states that may delay into a good region while avoiding a
bad one:

.. image:: fed_predt.plot.py.svg
   :width: 88%
   :align: center
   :alt: Figure showing good and bad zones and the predecessor region.

.. code-block:: python

   pred = good.predt(bad)

This is one of the places where the federation layer clearly behaves like a
symbolic-state engine rather than only a container of matrices.

.. _fed-update-value:
.. _fed-reset-value:

Updating And Resetting Clocks: ``update_value()`` And ``reset_value()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both operations assign one clock a concrete value:

.. image:: fed_update.plot.py.svg
   :width: 94%
   :align: center
   :alt: Three-panel figure showing a base zone, updateValue to x=2, and resetValue to x=0.

.. code-block:: python

   updated = fed.update_value(x, 2)
   reset = fed.reset_value(x)

``reset_value(clock)`` is just the ``0``-specialized case of
``update_value(clock, value)``.

.. _fed-extrapolate-max-bounds:

Max-Bound Extrapolation ``extrapolate_max_bounds()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extrapolation is where the tutorial leaves exact symbolic semantics and enters
abstraction for termination:

.. image:: fed_extrapolate.plot.py.svg
   :width: 88%
   :align: center
   :alt: Before and after figure for maximal-bound extrapolation.

.. code-block:: python

   abstracted = fed.extrapolate_max_bounds({"x": 100, "y": 100})

The point is not to preserve the exact original federation. The point is to
drop constraints that exceed the maximal constants and keep the analysis
finite [UDBM_FED_H]_.

Queries And Properties
~~~~~~~~~~~~~~~~~~~~~~

.. _fed-contains:

Containment ``contains()``
~~~~~~~~~~~~~~~~~~~~~~~~~~

The properties figure contains a direct membership picture:

.. image:: fed_properties.plot.py.svg
   :width: 94%
   :align: center
   :alt: Property gallery showing decomposition, subset relation, contains, hasZero, isZero, and isEmpty.

In the ``contains`` panel, one point lies inside the federation and one lies in
the gap:

.. code-block:: python

   assert fed.contains(inside_point)
   assert not fed.contains(outside_point)

This is valuation membership in the most literal sense.

.. _fed-has-zero:
.. _fed-is-zero:

Zero-Point Queries: ``has_zero()`` And ``is_zero()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same figure distinguishes two related but different questions:

* ``has_zero()`` asks whether the origin belongs to the federation at all
* ``is_zero()`` asks whether the whole federation is exactly the origin zone

That is why the ``hasZero`` panel still shows a nontrivial region, while the
``isZero`` panel collapses to the single point :math:`(0,0)`.

.. _fed-is-empty:

Empty Federations With ``is_empty()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The last panel of the properties figure illustrates the empty case. This is the
result of contradictory constraints, for example:

.. code-block:: python

   empty = (x == 1) & (x != 1)
   assert empty.is_empty()

.. _fed-relations:

Relations: ``==``, ``!=``, ``<=``, ``>=``, ``<``, ``>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The subset panel in the properties figure is the geometric model for all six
comparison operators:

* ``A == B`` means same symbolic set
* ``A != B`` means different symbolic sets
* ``A <= B`` means subset
* ``A >= B`` means superset
* ``A < B`` means strict subset
* ``A > B`` means strict superset

In other words, the comparison operators on federations are **set-theoretic**,
not lexical or object-identity based.

Important Takeaways
-------------------

Several distinctions matter a lot in practice:

* **A federation is still built from DBMs.** It does not replace DBMs; it sits one layer above them.
* **Subtraction is where federations stop looking optional.** Non-convex results are a semantic fact, not a UI choice.
* **Exact union and convex union are different operations.** They should not be explained as if one were just a faster version of the other.
* **Reduction and interning are about representation quality.** They matter because federation size and internal sharing affect later symbolic work.
* **Extrapolation is not an exact transform.** It is an intentional abstraction step.
* **The public Python surface follows the native semantic layer closely.** This is why the restored API has to center on ``Federation`` rather than only on one DBM at a time.

Next
~~~~

The next natural topic after federations is the planned ``cdd/`` page: once
finite unions of zones become first-class, the next question is whether an
explicit list of DBMs is always the best representation, or whether shared
diagram structures sometimes compress the same symbolic set better.

References
~~~~~~~~~~

.. [DHLP06_FED] Alexandre David, Kim G. Larsen, Didier Lime, and Brian H. Poulsen.
   ``Subtracting Clock Zones``.
   Public link: `<https://homes.cs.aau.dk/~adavid/dhlp06-zones.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/dhlp06/README.md>`_.
.. [BEHR03_CDD] Gerd Behrmann.
   ``Efficient Timed Reachability Analysis using Clock Difference Diagrams``.
   Public link: `<https://www.brics.dk/RS/98/47/BRICS-RS-98-47.pdf>`_.
   Repository guide: `<https://github.com/HansBug/pyudbm/blob/main/papers/behrmann03/paper-c/README.md>`_.
.. [UDBM_FED_H] UPPAALModelChecker.
   ``UDBM/include/dbm/fed.h``.
   Public link: `<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/fed.h>`_.
.. [UDBM_FED_CPP] UPPAALModelChecker.
   ``UDBM/src/fed.cpp``.
   Public link: `<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/src/fed.cpp>`_.
