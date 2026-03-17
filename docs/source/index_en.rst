Welcome to pyudbm
=================

Overview
--------

**pyudbm** is a Python wrapper around the UPPAAL UDBM library. The project is
focused on restoring the historical high-level Python binding while keeping the
modern wrapper thin, native-backed, and close to upstream semantics.

Key Features
~~~~~~~~~~~~~

* **Compatibility-minded API** centered on ``Context``, ``Clock``, and ``Federation``
* **Native federation operations** provided by the vendored UDBM library
* **Natural constraint syntax** for clock bounds and clock differences
* **Cross-platform packaging direction** for Linux, macOS, and Windows

Project Status
--------------

The repository is still under active development. Core federation construction,
valuation handling, and several high-level operations are already available,
but the package should still be treated as a work in progress rather than a
fully frozen public API.

Quick Start
-------------

.. code-block:: python

   from pyudbm import Context, IntValuation

   c = Context(["x", "y"], name="c")
   zone = (c.x < 10) & (c.x - c.y <= 1)

   valuation = IntValuation(c)
   valuation["x"] = 3
   valuation["y"] = 2

   assert zone.contains(valuation)

Architecture
-------------

The current package is organized around a small public surface:

* **Package root** (``pyudbm``): re-exports the high-level compatibility API
* **Binding layer** (``pyudbm.binding``): Python ergonomics over the native extension
* **Metadata layer** (``pyudbm.config``): package and upstream version metadata

Tutorials
---------

.. toctree::
    :maxdepth: 2
    :caption: Tutorials
    :hidden:

    tutorials/installation/index

* :doc:`tutorials/installation/index`

Concept Foundations
-------------------

.. toctree::
    :maxdepth: 2
    :caption: Foundations
    :hidden:

    foundations/reading-guide/index
    foundations/what-is-uppaal/index
    foundations/timed-automata/index
    foundations/queries-and-properties/index

* :doc:`foundations/reading-guide/index`
* :doc:`foundations/what-is-uppaal/index`
* :doc:`foundations/timed-automata/index`
* :doc:`foundations/queries-and-properties/index`

API Reference
-------------

.. include:: api_doc_en.rst

Upstream and Source
-------------------

* **GitHub Repository**: https://github.com/HansBug/pyudbm
* **UDBM Upstream**: https://github.com/UPPAALModelChecker/UDBM
* **UUtils Upstream**: https://github.com/UPPAALModelChecker/UUtils
