安装
====

``pyudbm`` 同时包含 Python 包装层以及原生 UDBM / UUtils 依赖。面向最终用户的目标分发方式是预构建 wheel，
而当前仓库开发阶段最稳妥的方式仍然是从源码构建。

通过 wheel 安装
---------------

如果目标平台已有发布好的 wheel，可以直接执行：

.. code-block:: bash

    pip install pyudbm

从源码构建
----------

本地开发建议从仓库 checkout 开始：

.. code-block:: bash

    git clone https://github.com/HansBug/pyudbm.git
    cd pyudbm
    git submodule update --init --recursive

然后创建虚拟环境并安装仓库依赖：

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate
    python -m pip install -U pip setuptools wheel
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-test.txt
    python -m pip install -r requirements-build.txt

接着构建 vendored 原生依赖以及 Python 扩展：

.. code-block:: bash

    make bin
    make build

最后执行绑定层测试：

.. code-block:: bash

    make unittest RANGE_DIR=binding

快速检查
--------

下面这段 shell 代码会验证包能够被正确导入：

.. literalinclude:: cli_check.demo.sh
    :language: bash
    :linenos:

示例输出：

.. literalinclude:: cli_check.demo.sh.txt
    :language: text
    :linenos:

下面的 Python 示例会实际构造一个 federation 并执行包含性检查：

.. literalinclude:: install_check.demo.py
    :language: python
    :linenos:

示例输出：

.. literalinclude:: install_check.demo.py.txt
    :language: text
    :linenos:

说明
----

当前仓库仍在持续开发中。对源码构建场景来说，仓库根目录的 ``make`` 流程是最稳妥的方式，因为它会同时维护
vendored 原生库、Python 扩展以及测试环境的一致性。
