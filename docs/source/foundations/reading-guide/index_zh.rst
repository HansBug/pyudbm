入口导读
========

\ **这一部分是**\ :doc:`/tutorials/installation/index_zh`\ **的概念层补充。**
它主要不是用来讲安装步骤或命令流程，而是用来解释 UPPAAL 里的核心概念到底是什么意思、为什么需要它们，
以及这些概念和 :mod:`pyudbm` 未来的 Python 侧方向有什么关系。

如何使用这一部分
----------------

当你在问下面这些问题时，应该优先看这里：

* UPPAAL 到底想解决什么问题？
* 为什么带时间的系统比普通有限状态验证更难？
* 为什么会出现 symbolic states、zones、DBMs 和 federations？
* 在什么概念准备好之后，`pyudbm` 的高层 Python API 才会显得自然？

如果你现在只想安装包、从源码构建，或者先跑一个快速检查，应该先看
:doc:`/tutorials/installation/index_zh`。

阅读分流
--------

\ **这个入口页不是普通目录，而是一个阅读路由页。**\ 不同背景的读者，起点不应该一样。

如果你对 formal verification / model checking 都不熟悉：
    \ **从**\ :doc:`../what-is-uppaal/index_zh`\ **开始。**

如果你知道 model checking 是什么，但 timed automata 还不熟：
    \ **先读**\ :doc:`../what-is-uppaal/index_zh`\ **，**\ 再继续读后续会补上的 ``timed-automata/`` 页面。

如果你已经知道 timed automata，但 symbolic state 和 zone 还比较抽象：
    先用 :doc:`../what-is-uppaal/index_zh` 建立整体图景，然后继续读后续会补上的
    ``symbolic-states/`` 和 ``dbm-basics/`` 页面。

如果你已经知道 zone 和 DBM，但还不理解为什么会出现非凸符号集合：
    可以先快速读一遍 :doc:`../what-is-uppaal/index_zh`，再去看后续会补上的
    ``federations/`` 和 ``cdd/`` 页面。

如果你最关心的是这个仓库未来的 Python API 会怎样映射这些概念：
    也建议\ **先读**\ :doc:`../what-is-uppaal/index_zh`，因为它解释了被恢复的
    ``Context`` / ``Clock`` / ``Federation`` 这套接口到底在服务怎样的验证工作流。

当前内容
--------

.. toctree::
    :maxdepth: 2

    ../what-is-uppaal/index_zh

规划中的主题顺序
----------------

当前的概念路线大致是：

* ``what-is-uppaal/``
* ``timed-automata/``
* ``queries-and-properties/``
* ``symbolic-states/``
* ``dbm-basics/``
* ``federations/``
* ``cdd/``
* 搜索 / extrapolation / storage 相关主题
* reduction 相关主题
* priced timed automata 与 API 重建路线相关主题

和其他文档区域的关系
--------------------

\ **这三个文档区域的职责不同：**

* :doc:`/tutorials/installation/index_zh`\ **回答**\ “怎么安装、怎么构建、怎么开始用”
* ``foundations/``\ **回答**\ “这些概念到底是什么意思”
* 仓库里的 ``papers/``\ **回答**\ “这些讲法主要依托哪些论文和阅读指南”

对当前仓库来说，这个分层尤其重要。`pyudbm` 现在还不是完整的 UPPAAL 克隆，
但它确实在尝试围绕 UDBM 基础层恢复一层足够薄、又足够自然的高层 Python 接口；
而这层接口只有放回完整的 UPPAAL 语境里才容易讲清楚。
