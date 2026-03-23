欢迎来到 pyudbm 的文档
======================

概述
----

\ **pyudbm**\ 是对 UPPAAL UDBM 原生库的 Python 封装。这个项目的重点是在现代
``pybind11 + CMake + setuptools`` 构建栈上恢复历史高层 Python 绑定，同时尽量保持封装足够薄，并贴近上游语义。

核心特性
~~~~~~~~~~~~~

* **兼容历史风格的 API**，核心对象是 ``Context``、``Clock`` 和 ``Federation``
* **原生 federation 运算**，底层能力直接来自 vendored UDBM
* **自然的约束表达式语法**，可以直接描述时钟界和时钟差
* **面向跨平台分发的包装方向**，目标平台覆盖 Linux、macOS 和 Windows

项目状态
~~~~~~~~

当前仓库仍处于持续开发中。核心 federation 构造、valuation 处理以及一批高层操作已经可用，
但整个包仍应被视为兼容导向的进行中实现，而不是完全冻结的最终 API。

快速开始
~~~~~~~~

.. code-block:: python

   from pyudbm import Context, IntValuation

   c = Context(["x", "y"], name="c")
   zone = (c.x < 10) & (c.x - c.y <= 1)

   valuation = IntValuation(c)
   valuation["x"] = 3
   valuation["y"] = 2

   assert zone.contains(valuation)

架构
~~~~

当前公开结构可以概括为：

* **包根** (``pyudbm``)：对外重导出高层兼容 API
* **绑定层** (``pyudbm.binding``)：在原生扩展之上提供 Python 侧易用接口
* **元数据层** (``pyudbm.config``)：暴露包版本和上游版本信息

上游与源码
~~~~~~~~~~

* **GitHub 仓库**：https://github.com/HansBug/pyudbm
* **UDBM 上游**：https://github.com/UPPAALModelChecker/UDBM
* **UUtils 上游**：https://github.com/UPPAALModelChecker/UUtils

教程
----

.. toctree::
    :maxdepth: 2
    :caption: 教程
    :hidden:

    tutorials/installation/index_zh

* :doc:`tutorials/installation/index_zh`

概念基础
--------

.. toctree::
    :maxdepth: 2
    :caption: 概念基础
    :hidden:

    foundations/reading-guide/index_zh
    foundations/what-is-uppaal/index_zh
    foundations/timed-automata/index_zh
    foundations/queries-and-properties/index_zh
    foundations/symbolic-states/index_zh
    foundations/dbm-basics/index_zh
    foundations/federations/index_zh

* :doc:`foundations/reading-guide/index_zh`
* :doc:`foundations/what-is-uppaal/index_zh`
* :doc:`foundations/timed-automata/index_zh`
* :doc:`foundations/queries-and-properties/index_zh`
* :doc:`foundations/symbolic-states/index_zh`
* :doc:`foundations/dbm-basics/index_zh`
* :doc:`foundations/federations/index_zh`

.. include:: api_doc_zh.rst
