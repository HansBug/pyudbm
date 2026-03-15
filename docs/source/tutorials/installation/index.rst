Installation
============

``pyudbm`` combines a Python package with native UDBM and UUtils
dependencies. The intended end-user path is prebuilt wheels, while repository
development is currently most reliable from a source checkout.

Install from a wheel
--------------------

If a published wheel is available for your platform, install it with:

.. code-block:: bash

    pip install pyudbm

Build from source
-----------------

For local development, start from a repository checkout:

.. code-block:: bash

    git clone https://github.com/HansBug/pyudbm.git
    cd pyudbm
    git submodule update --init --recursive

Create an isolated Python environment and install the repository requirements:

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate
    python -m pip install -U pip setuptools wheel
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-test.txt
    python -m pip install -r requirements-build.txt

Build the vendored native dependencies and then the Python extension:

.. code-block:: bash

    make bin
    make build

Run the binding-focused unit tests:

.. code-block:: bash

    make unittest RANGE_DIR=binding

Smoke Check
-----------

The shell snippet below verifies that the package imports correctly:

.. literalinclude:: cli_check.demo.sh
    :language: bash
    :linenos:

Example output:

.. literalinclude:: cli_check.demo.sh.txt
    :language: text
    :linenos:

The Python snippet below exercises the restored high-level API:

.. literalinclude:: install_check.demo.py
    :language: python
    :linenos:

Example output:

.. literalinclude:: install_check.demo.py.txt
    :language: text
    :linenos:

Notes
-----

The repository is still unfinished. For source builds, the repository-level
``make`` flow remains the most reliable path because it keeps the vendored
native libraries, Python extension, and test environment aligned.
