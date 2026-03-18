符号状态与约束区域
==================

这一页回答的是紧接着
:doc:`../queries-and-properties/index_zh`
之后最自然的问题：\ **为什么 UPPAAL 不去一个一个枚举具体带时间状态？**

简短答案是：时钟的取值来自非负实数域，所以哪怕一个很小的时间自动机，也已经拥有无限多个具体状态。
因此，UPPAAL 会用\ **由约束表示的符号状态(symbolic states)**\ 来探索状态空间，而不是只处理单个赋值
[UPP_VER_SS_ZH]_ [UPP_TRACE_SS_ZH]_。

从具体状态到符号状态
--------------------

运行中的压力点
~~~~~~~~~~~~~~

回到前几页里的那个小请求-响应自动机。在位置 ``WaitAck`` 中，时钟 ``x`` 满足：

.. math::

   0 \leq x \leq 5

光是这一个约束窗口，就已经会产生无限多个具体状态：

* ``(WaitAck, x = 0)``
* ``(WaitAck, x = 0.2)``
* ``(WaitAck, x = 1.7)``
* ``(WaitAck, x = 4.999)``
* 以及中间无限多个别的取值

这就是最核心的压力来源。甚至在你还没有引入第二个进程、第二个时钟之前，连续时间本身就已经把“显式枚举”
这条路堵死了。

.. graphviz:: explicit_vs_symbolic_zh.dot

这张图故意画得很简单：同一个控制位置下的大量具体带时间状态，可以被一个符号描述打包起来。

为什么具体带时间状态会爆炸
~~~~~~~~~~~~~~~~~~~~~~~~~~

UPPAAL 官方语义把系统行为写成一个带时间迁移系统，其中状态形状是

.. math::

   (L, v)

这里 :math:`L` 是位置向量(location vector)，:math:`v` 是满足当前位置不变量的赋值(valuation)
[UPP_SEM_SS_ZH]_。

这个记号很紧凑，但它背后的含义很大：

* :math:`L` 固定当前各个进程所在的位置
* :math:`v` 固定当前所有时钟和变量的值
* 如果时钟是实值的，那么就算 :math:`L` 固定不变，也仍然会对应无限多个不同的具体状态

一旦你有两个时钟，情况就更明显了。如果模型允许 ``x`` 和 ``y`` 连续变化，那么验证器面对的就不再是一串长长的
状态列表，而是一块几何意义上的赋值空间。

为什么符号状态有用
~~~~~~~~~~~~~~~~~~

UPPAAL 官方文档其实把这个直觉说得很直接：验证器探索的是符号状态，符号模拟器展示的是符号轨迹(symbolic trace)，
而不是单条具体轨迹 [UPP_VER_SS_ZH]_ [UPP_TRACE_SS_ZH]_。

对教程来说，最核心的点是：

* 一个符号状态会固定当前活跃位置(active locations)
* 它会固定离散变量(discrete variables) 的取值
* 它会让时钟在一整个由约束描述的赋值集合里变化

因此，我们存的不是一个赋值，而是一\ **批**\ 赋值：

.. math::

   Z = \{\, v \mid v \models g_1 \land \cdots \land g_k \,\}

这里最好逐个读：

* :math:`Z` 是符号状态里负责时钟部分的那个 zone 风格对象
* :math:`v` 在所有可能赋值上取值
* :math:`v \models g_i` 表示赋值 :math:`v` 满足约束 :math:`g_i`
* 合取 :math:`g_1 \land \cdots \land g_k` 表示这些时钟约束必须同时成立

对 ``WaitAck`` 这个位置，最简单的例子就是：

.. math::

   Z_{\mathrm{wait}} = \{\, v \mid 0 \leq v(x) \leq 5 \,\}

这一个集合，就代表了所有“控制位置是 ``WaitAck`` 且时钟值仍在 deadline 窗口内”的具体状态。

Region 与 Zone 以及符号后继
---------------------------

Region 与 Zone 不是一回事
~~~~~~~~~~~~~~~~~~~~~~~~~

这里最容易混淆的，是两个都很重要、但职责不同的概念：

* **区域(region)**：给 timed automata 提供有限等价划分，是理论上解释可判定性的重要对象
* **区域(zone)**：由时钟约束定义出来的一类较大赋值集合，是工具真正直接操作的对象

region 的视角很重要，因为它解释了为什么 timed automata 验证在理论上能够被有限化。
但 UPPAAL 这一类工具在日常工作里，并不是围绕显式 region 对象展开的，而是围绕 zone 风格的约束集合展开。
原因很直接：时间后继、守卫条件求交、重置、包含关系检查这些操作，在 zone 表示下会自然得多
[BY04_SS_ZH]_ [LPW95_SS_ZH]_。

一个单时钟的具体例子
^^^^^^^^^^^^^^^^^^^^

假设现在只有一个时钟 ``x``，而模型里出现过的最大常数是 `2`。

那么在 **region** 的视角下，``x`` 轴会被切成一组固定的有限划分，例如：

* ``x = 0``
* ``0 < x < 1``
* ``x = 1``
* ``1 < x < 2``
* ``x = 2``
* ``x > 2``

这套划分是 timed automata 理论预先决定的，不是验证过程中临时按需要去挑的。

再看一个 **zone**：

.. math::

   Z = \{\, v \mid 0 \leq v(x) < 2 \,\}

这个 zone 一次就包含了很多具体赋值：

* :math:`v(x) = 0`
* :math:`v(x) = 0.2`
* :math:`v(x) = 0.8`
* :math:`v(x) = 1`
* :math:`v(x) = 1.7`

更关键的是，它其实同时覆盖了 **多个不同的 region**：

* ``x = 0``
* ``0 < x < 1``
* ``x = 1``
* ``1 < x < 2``

这就是两者最实用的区别：

* **region** 是固定理论划分里的一个小格子
* **zone** 是工具按约束构造并操作的一块赋值集合

所以当我们说 zone 比 region 更“粗”时，意思就是：一个 zone 往往会把好几个 region 一起打包进去。

.. graphviz:: regions_vs_zone_zh.dot

这张图想表达的不是“一个 zone 永远刚好包含九个 region”，而是：
\ **zone 往往比底层 region 划分更粗，因此更适合作为工程上的符号对象。**

这里的权衡要记清楚：

* region 提供理论上的有限商(finite quotient)直觉
* zone 提供实践里的符号表示
* 朴素 zone graph 仍然可能是无限的，所以后面还需要 normalization 和 extrapolation

符号后继大致长什么样
~~~~~~~~~~~~~~~~~~~~

一旦把赋值打包成 zone，下一步就是把原本定义在单个赋值上的迁移，提升到“赋值集合”上。

对时间流逝来说，符号后继的形状是：

.. math::

   \mathrm{Post}_{\mathrm{delay}}(Z)
   =
   \{\, v + d \mid v \in Z,\; d \in \mathbb{R}_{\geq 0} \,\}

对一条守卫条件为 :math:`g`、重置集合为 :math:`R` 的离散边来说，形状是：

.. math::

   \mathrm{Post}_{e}(Z)
   =
   \{\, v[R := 0] \mid v \in Z,\; v \models g \,\}

这些式子可以直接按操作来读：

* :math:`v \in Z` 表示我们从当前符号状态所覆盖的一批赋值里出发
* :math:`d \in \mathbb{R}_{\geq 0}` 表示允许非负时间流逝
* :math:`v + d` 表示所有时钟一起增加 :math:`d`
* :math:`v \models g` 表示该赋值满足这条边的守卫条件
* :math:`v[R := 0]` 表示把 :math:`R` 里的时钟都重置为 `0`

真正的 UPPAAL 后继计算里，还会继续受当前位置不变量和目标位置不变量约束。但即便只看这个简化版，
你也已经能看出：后面为什么会自然出现 ``up``、守卫条件求交、reset 和包含检查这类操作。

三个最容易误解的点
~~~~~~~~~~~~~~~~~~

这里最常见的混淆有三个：

* \ **符号状态不只是一个 zone。** 它还固定控制位置和离散数据部分。
* \ **zone 不是任意形状的集合。** 在基础 DBM 故事里，它是由时钟约束定义出来的凸集合。
* \ **符号轨迹里看到的每个点，不代表都一定会走向同一个后继。** UPPAAL 官方关于 symbolic trace 的说明明确提醒：模拟器里的轨迹是 backward stable 的，但不一定 forward stable [UPP_TRACE_SS_ZH]_。

收束与定位
----------

这和 ``pyudbm`` 有什么关系
~~~~~~~~~~~~~~~~~~~~~~~~~~

这一页其实正好能把 `pyudbm` 的角色讲清楚。

`pyudbm` 本身\ **并不表示完整的 UPPAAL 符号状态**。它表示的是符号状态下面那一层时钟约束技术：

* ``Context`` 固定时钟空间
* ``Clock`` 对象负责构造简单界约束和时钟差约束
* ``Federation`` 保存一个或多个关于这些时钟的符号赋值集合

所以，这个仓库在恢复高层 Python DSL 时，本质上是在重建“让符号状态变得可操作”的约束层，
而不是直接重做整个 verifier。

这一页最该记住什么
~~~~~~~~~~~~~~~~~~

如果这一页最后只记住五件事，那应该是：

* 具体带时间状态会无限增长，因为时钟取值来自实数域
* 一个符号状态会固定位置和离散数据，但把很多赋值合并处理
* zone 是 UPPAAL 风格工具真正直接操作的约束表示
* region 负责解释理论上的有限性，zone 负责解释工程上的可操作性
* 后面的 DBM 层之所以存在，就是为了把这些 zone 操作高效落到具体数据结构上

下一步
~~~~~~

下一篇最自然的内容是 :doc:`../dbm-basics/index_zh`：当 zone 视角建立起来以后，接下来就该问，
为什么一个矩阵能够高效表示这样一组时钟约束。

.. [UPP_SEM_SS_ZH] UPPAAL 官方文档，``Semantics``。
   公开链接：`<https://docs.uppaal.org/language-reference/system-description/semantics/>`_。
.. [UPP_VER_SS_ZH] UPPAAL 官方图形界面文档，``Verifier``。
   公开链接：`<https://docs.uppaal.org/gui-reference/verifier/>`_。
.. [UPP_TRACE_SS_ZH] UPPAAL 官方图形界面文档，``Symbolic Traces``。
   公开链接：`<https://docs.uppaal.org/gui-reference/symbolic-simulator/symbolic-traces/>`_。
.. [BY04_SS_ZH] Johan Bengtsson, Wang Yi.
   ``Timed Automata: Semantics, Algorithms and Tools``。
   公开链接：`<https://uppaal.org/texts/by-lncs04.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README_zh.md>`_。
.. [LPW95_SS_ZH] Kim Guldstrand Larsen, Paul Pettersson, Wang Yi.
   ``Compositional and Symbolic Model-Checking of Real-Time Systems``。
   公开链接：`<https://dblp.org/rec/conf/rtss/LarsenPW95>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/lpw95/README_zh.md>`_。
