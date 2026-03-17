查询与性质
==========

这一页回答的是紧接着
:doc:`../timed-automata/index_zh`
之后的下一个问题：\ **模型已经有了，用户通常到底在问它什么？**

UPPAAL 不是只用来画时间自动机的。它真正重要的用途，是拿这些模型去检查需求(requirements)。
官方文档对 verifier 的描述很直接：它会通过对符号状态空间(symbolic state-space)的 on-the-fly
探索来检查 safety 和 liveness 一类性质 [UPP_VER_ZH]_。

核心直觉
--------

初学者最常见的问题，大致都会落进下面几类：

* 某个“好状态”能不能到达？
* 某个“坏状态”会不会发生？
* 某种进展最终会不会一定发生？
* 系统会不会卡死？

UPPAAL 经典的 symbolic query 语言，本质上就是围绕这些问题组织起来的
[LPY97_QP_ZH]_ [BY04_QP_ZH]_ [UPP_QSYN_ZH]_ [UPP_QSEM_ZH]_。

运行中的状态空间图
------------------

理解这些查询，最直接的办法是先看一张很小的状态空间示意图：

.. graphviz:: state_space_queries.dot

可以这样读这张图：

* ``Acked`` 是一个希望达到的目标状态
* ``Error`` 是一个坏状态
* ``Stuck`` 是一个死锁状态
* ``Unreachable`` 虽然画在图里，但从初始状态出发永远到不了

光是这一张图，就足够区分几类经常被混淆的问题：

* ``E<> Acked`` 在问：是否\ **存在某条执行**\ 能到达 ``Acked``
* ``A[] not Error`` 在问：是否\ **每个可达状态**\ 都避开 ``Error``
* ``A<> Acked`` 在问：是否\ **每条执行**\ 最终都会被迫到达 ``Acked``
* ``A[] not deadlock`` 在问：是否不存在可达死锁

这些查询在中文口语里听起来很接近，但逻辑强度完全不同。

从状态谓词到查询
----------------

UPPAAL 查询是由\ **状态谓词(state predicates)**\ 组合出来的。

状态谓词就是“在某个状态上取真或取假的布尔条件”。按照官方文档，它可以引用
location、变量、逻辑组合以及时钟约束 [UPP_QSYN_ZH]_ [UPP_QSEM_ZH]_。

典型例子包括：

* ``Controller.WaitAck``：进程 ``Controller`` 当前位于 location ``WaitAck``
* ``x <= 5``：当前状态满足这个时钟约束
* ``Controller.WaitAck and x < 5``
* ``deadlock``：这是一个内置的特殊状态谓词

官方 syntax 页面把经典 symbolic queries 概括为：

.. math::

   \texttt{A[]}\; p,\qquad
   \texttt{E<>}\; p,\qquad
   \texttt{E[]}\; p,\qquad
   \texttt{A<>}\; p,\qquad
   p \; \texttt{-->} \; q

这一页主要聚焦前四类里最常见的三类，加上 ``p --> q`` 这种 progress 风格性质，
因为它们已经覆盖了大部分入门阶段的问题。

最小语义骨架
------------

UPPAAL 官方对 query 的语义，是放在一个 timed transition system 上来写的：

.. math::

   \mathcal{M} = (S, s_0, \to)

其中：

* :math:`S` 是状态集合
* :math:`s_0` 是初始状态
* :math:`\to` 是由时间流逝和离散跳转共同诱导出来的迁移关系

如果 :math:`p` 是一个状态谓词，记 :math:`s \models p` 表示“状态 :math:`s` 满足谓词 :math:`p`”。

再记

.. math::

   s_0 \to s_1 \to s_2 \to \cdots

是一条执行路径；如果一条路径要么无限长、要么已经不能继续扩展，就把它叫做一条
\ **maximal path**。

这里有两个点值得先说透：

* :math:`\mathrm{Reach}(\mathcal{M})` 表示“从初始状态 :math:`s_0` 出发，经过有限步执行后所有能够到达的状态集合”
* 所以 :math:`\forall s \in \mathrm{Reach}(\mathcal{M})` 的意思不是“随便拿一个抽象状态集合里的元素”，而是“对系统真正可能跑到的每个状态都要检查”

也就是说，reachability 语义关注的是“有没有某条执行能把系统带到某处”，而
``A[]`` 这类语义关注的是“所有真正可达的状态是不是都满足某个条件”。

在这个记号下，最适合入门者把握的几条读法是：

.. math::

   \mathcal{M} \models E\langle\rangle p
   \iff
   \exists \text{ 一条路径到达某个满足 } p \text{ 的状态}

.. math::

   \mathcal{M} \models A[]\, p
   \iff
   \forall s \in \mathrm{Reach}(\mathcal{M}),\; s \models p

.. math::

   \mathcal{M} \models A\langle\rangle p
   \iff
   \forall \text{ maximal paths } \pi,\; \pi \text{ 最终到达某个满足 } p \text{ 的状态}

.. math::

   \mathcal{M} \models E[]\, p
   \iff
   \exists \text{ 一条 maximal path，其上每个状态都满足 } p

逐条把它们翻成人话，可以这样理解：

* :math:`E\langle\rangle p`：
  只要存在\ **一条**\ 执行，能把系统带到某个满足 :math:`p` 的状态，这个 query 就为真。
  这里强调的是“存在性”，所以它适合问“这种情况能不能发生一次”。
* :math:`A[]\, p`：
  对所有\ **可达状态**\ ，性质 :math:`p` 都必须成立。
  这一条特别容易被误读成“每条路径上都一直有 :math:`p`”。严格来说，它等价于：
  不管你沿着哪条执行走，只要那个状态是可达的，它就必须满足 :math:`p`。
  也可以反过来理解成：\ **不存在任何可达状态违反 :math:`p`**。
* :math:`A\langle\rangle p`：
  不只是说 :math:`p` 可达，而是说每一条 maximal path 迟早都会进入某个满足 :math:`p` 的状态。
  如果存在哪怕一条执行能永远拖着不进入 :math:`p`，那它就是假的。
* :math:`E[]\, p`：
  存在一条 maximal path，可以一直待在满足 :math:`p` 的状态里。
  这条通常用来表达“是否存在一种运行方式，能永远保持在某种区域里”。

如果你觉得第二条 :math:`A[]\, p` 和第三条 :math:`A\langle\rangle p` 很像，可以这样强行分开：

* :math:`A[]\, p` 检查的是“所有可达状态本身是不是都满足 :math:`p`”
* :math:`A\langle\rangle p` 检查的是“所有执行未来最终会不会走到 :math:`p`”

前者是\ **状态安全性**\ ，后者是\ **路径上的最终进展**\ 。这两者的逻辑强度和直觉对象并不一样。

例如：

* ``A[] not Error`` 是在说“任何时候都不能落进 ``Error``”
* ``A<> Acked`` 是在说“无论系统怎么跑，最终总会进入 ``Acked``”

一个系统完全可能满足前者、但不满足后者。比如它永远在一个“既不报错、也不确认”的循环里打转；
这时它始终安全，但没有保证最终完成。

这几条写法对教学做了轻度简化，但和官方给出的 pseudo-formal semantics 是一致方向的
[UPP_QSEM_ZH]_。

四类最常见查询怎么读
--------------------

下面把最常见的几类查询逐个拆开说。

可达性：``E<> p``
~~~~~~~~~~~~~~~~~

这是“这件事\ **能不能发生**\ ”的查询。

对上面的图来说：

.. code-block:: text

   E<> Acked

是真的，因为至少存在一条从 ``Init`` 到 ``Acked`` 的路径。

在实际 UPPAAL 模型里，更常见的写法往往像这样：

.. code-block:: text

   E<> Controller.Acked

或者：

.. code-block:: text

   E<> Controller.WaitAck and x > 3

所以当你想找“一条见证执行(witness trace)”时，``E<>`` 往往是最自然的起点。

安全性：``A[] p``
~~~~~~~~~~~~~~~~~

这是“是不是一直都安全”的查询。

例如：

.. code-block:: text

   A[] not Error

意思是：所有可达状态都必须避开 ``Error``。

在上面的图里，这个查询是假的，因为 ``Error`` 明显可达。

这也是为什么 ``A[]`` 很适合表达：

* 互斥(mutual exclusion)
* 缓冲区上界
* “坏位置永远不可达”
* ``A[] not deadlock``

最终必达：``A<> p``
~~~~~~~~~~~~~~~~~~~

这个查询比单纯可达性强得多。

.. code-block:: text

   A<> Acked

它问的不是“是否存在某条执行到达 ``Acked``”，而是“是否每一条 maximal execution 最终都会到达 ``Acked``”。

在上面的图里，这个查询是假的，因为有些路径会去 ``Error``，也有些路径会去 ``Stuck``，
因此并不是所有路径都通向 ``Acked``。

这个区别非常关键：

* ``E<> Acked`` 表示“成功是可能的”
* ``A<> Acked`` 表示“成功是不可避免的”

潜在保持：``E[] p``
~~~~~~~~~~~~~~~~~~~

这通常不是初学者第一眼会用的查询，但它能帮助你真正理解 ``A<>`` 的对偶关系。

.. code-block:: text

   E[] not Acked

它问的是：是否存在一条 maximal execution，能一直待在 ``Acked`` 之外。

在上面的图里，答案是肯定的：去 ``Error`` 的路径就从头到尾没有经过 ``Acked``，
去 ``Stuck`` 的路径也一样。

这也解释了为什么 UPPAAL 官方会给出下面这个等价式：

.. math::

   A\langle\rangle p \equiv \neg E[]\, \neg p

同理还有：

.. math::

   A[]\, p \equiv \neg E\langle\rangle \neg p

[UPP_QSEM_ZH]_。

死锁也是一种性质
----------------

在 UPPAAL 里，``deadlock`` 不是普通英文单词，而是一个有明确定义的状态谓词。

官方给出的定义是：状态 :math:`(L, v)` 满足 ``deadlock``，当且仅当

.. math::

   \forall d \ge 0,\; \text{不存在 } (L, v + d) \text{ 的 action successor}

[UPP_QSEM_ZH]_。

这一定义要仔细体会。它不是在说“此刻没有立即可走的离散边”这么简单，而是在说：
\ **不管再等多久，都不会出现一个合法的动作后继。**

这也是为什么

.. code-block:: text

   A[] not deadlock

会成为 UPPAAL 教程和示例里最常见的 sanity check 之一 [BDL04_QP_ZH]_。

``p --> q`` 比可达性更强
------------------------

UPPAAL 还支持一种 progress 风格的性质：

.. code-block:: text

   p --> q

它的意思是：只要某个状态满足 ``p``，那么之后在所有继续执行里，最终都必须出现满足 ``q`` 的状态。

官方给出的等价式是：

.. math::

   p \;\texttt{-->}\; q
   \equiv
   A[]\, (p \Rightarrow A\langle\rangle q)

[UPP_QSEM_ZH]_。

这比“`q` 在某处可达”强得多。看下面这张图：

.. graphviz:: request_leadsto.dot

在这张图里：

* ``E<> Acked`` 为真，因为确实存在一条从 ``Pending`` 到 ``Acked`` 的路径
* 但 ``Pending --> Acked`` 为假，因为也存在一条继续执行会永远困在 ``RetryLoop`` 里

所以 ``p --> q`` 更适合表达这类需求：

* 每个请求最终都会收到确认
* 每个故障最终都会恢复
* 每列接近道口的火车最终都会通过

为什么 query 会显得这么有用
----------------------------

query 的价值不只是“逻辑上可判定”，还在于工具通常能告诉你\ **为什么**\ 它真或假。

UPPAAL 的 symbolic verifier 可以生成 witness 或 counterexample trace，这些轨迹还能在
symbolic simulator 里继续检查 [UPP_QSEM_ZH]_ [UPP_VER_ZH]_。

实践上大致可以这样理解：

* ``E<> p`` 往往会附带一条到达 ``p`` 的 witness path
* ``A[] p`` 往往会附带一条到达 ``not p`` 的 counterexample
* ``A<> p`` 和 ``p --> q`` 的失败原因，很多时候不是“显式坏状态”，而是“某个无限拖延的循环”

这也是为什么 query 的措辞非常重要：两个用自然语言说起来差不多的需求，可能会对应完全不同的诊断轨迹。

超出 yes/no 之后
----------------

当前 UPPAAL 的 symbolic query syntax 还包括 ``sup``、``inf``、``bounds`` 这类定量查询形式，
可以对时钟或整数表达式提问 [UPP_QSYN_ZH]_。

这一页先不展开它们。当前最重要的事情更基础：

* 先分清你问的是 existence、invariance、eventuality 还是 progress
* 再选与之匹配的 query 形式

这和 ``pyudbm`` 有什么关系
---------------------------

`pyudbm` 现在还没有暴露完整的 UPPAAL query 语言，但 query 的视角已经足够解释：
为什么 clocks 和 clock constraints 根本不是“附属细节”。

因为 verifier 检查的是建基于符号状态之上的性质，所以：

* query 的真实语义最终落在“满足某些约束的一批 valuation”上，而不是单个 valuation 上
* 高层谓词如 ``x <= 5`` 并不是装饰语法，而是验证真正谈论的对象
* 后面 symbolic states、zones、DBMs、federations 这些页面，讲的正是让这些 query 变得可做的底层表示

这一页最该记住什么
------------------

如果这一页最后只记住五件事，那应该是：

* ``E<> p`` 问的是 ``p`` 在某条路径上是否可达
* ``A[] p`` 问的是 ``p`` 是否在所有可达状态里都成立
* ``A<> p`` 比 reachability 强，它问的是每条路径最终是否都必须到达 ``p``
* ``deadlock`` 在 UPPAAL 里是一个一等状态谓词
* ``p --> q`` 是 progress 风格性质，不只是另一种 reachability

下一步
------

下一篇最自然的内容是 ``symbolic-states/``：当 query 视角建立起来以后，下一个问题就是，
为什么 UPPAAL 不去一个一个枚举具体 timed states。

.. [UPP_VER_ZH] UPPAAL 官方图形界面文档，``Verifier``。
   公开链接：`<https://docs.uppaal.org/gui-reference/verifier/>`_。
.. [UPP_QSYN_ZH] UPPAAL 官方文档，``Syntax of Symbolic Queries``。
   公开链接：`<https://docs.uppaal.org/language-reference/query-syntax/symbolic_queries/>`_。
.. [UPP_QSEM_ZH] UPPAAL 官方文档，``Semantics of the Symbolic Queries``。
   公开链接：`<https://docs.uppaal.org/language-reference/query-semantics/symb_queries/>`_。
.. [LPY97_QP_ZH] Kim Guldstrand Larsen, Paul Pettersson, Wang Yi.
   ``UPPAAL in a Nutshell``。
   公开链接：`<https://dblp.org/rec/journals/sttt/LarsenPY97>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/lpy97/README_zh.md>`_。
.. [BDL04_QP_ZH] Gerd Behrmann, Alexandre David, Kim Guldstrand Larsen.
   ``A Tutorial on UPPAAL``。
   公开链接：`<https://dblp.org/rec/conf/sfm/BehrmannDL04>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/bdl04/README_zh.md>`_。
.. [BY04_QP_ZH] Johan Bengtsson, Wang Yi.
   ``Timed Automata: Semantics, Algorithms and Tools``。
   公开链接：`<https://uppaal.org/texts/by-lncs04.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README_zh.md>`_。
