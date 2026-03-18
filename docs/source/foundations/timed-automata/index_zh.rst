时间自动机
==========

这一页回答的是紧接着
:doc:`../what-is-uppaal/index_zh`
之后最自然的问题：\ **系统究竟是靠什么模型随时间演化的？**

对 UPPAAL 来说，基本建模对象是时间自动机网络(network of timed automata)。单个自动机看起来像一个有限状态机，
但它被进一步扩展了：

* 实值时钟(clocks)
* 时钟约束(clock constraints)
* 重置(reset)
* 位置不变量(location invariants)

这些元素一起决定了“时间什么时候可以流逝、离散跳转什么时候可以发生” [UPP_LOC_ZH]_ [UPP_EDGE_ZH]_ [UPP_SEM_ZH]_。

基本对象与状态
--------------

运行中的小例子
~~~~~~~~~~~~~~

先看一个非常小的请求-响应控制器，它只有一个时钟 ``x``：

* 在 ``Idle`` 中，系统可以发送请求，并把 ``x`` 重置为 `0`
* 在 ``WaitAck`` 中，系统等待确认，同时要求 ``x <= 5``
* 如果确认及时到达，就回到 ``Idle``
* 如果时间到达截止时间(deadline)，就可以走超时边进入 ``Error``

.. graphviz:: request_response.dot

这个图已经是一张真正的时间自动机图，而不只是控制流程草图：

* ``send`` 和 ``ack`` 是动作标签：``send`` 表示“发出请求”，``ack`` 表示“收到确认”
* 在 UPPAAL 风格的记号里，``!`` 表示在某个 channel 上发送，``?`` 表示在某个 channel 上接收
* ``send! / x := 0`` 表示“把请求发出去，并把 ``x`` 重置为 `0`”
* ``ack?`` 表示“接收到确认”
* ``timeout!`` 表示“发出一个超时事件”
* ``inv: x <= 5`` 表示在 ``WaitAck`` 里最多只能停留到 `x = 5`
* ``x >= 5 / timeout!`` 表示一旦到达边界，超时边就会变得可用

基本形式定义
~~~~~~~~~~~~

一个常见的写法是把时间自动机记作

.. math::

   A = (L, \ell_0, C, \Sigma, E, \mathrm{Inv})

这组符号可以这样读：

* :math:`L` 是有限个位置(location)的集合
* :math:`\ell_0 \in L` 是初始位置
* :math:`C` 是有限个时钟的集合
* :math:`\Sigma` 是动作标签集合
* :math:`E \subseteq L \times \Sigma \times G(C) \times 2^C \times L` 是边关系
* :math:`\mathrm{Inv}` 给每个位置指定一个不变量

这里 :math:`G(C)` 表示时钟约束的集合。一个够用而且很典型的语法是：

.. math::

   g ::= x \bowtie c \mid x - y \bowtie c \mid g \land g

其中 :math:`x, y \in C`，:math:`c \in \mathbb{Z}`，
:math:`\bowtie \in \{<, \le, =, \ge, >\}`。

这不是随便写出来的一套符号。后面区域(zone) / 差分约束矩阵(DBM) 能成立，关键就在于守卫条件(guard)和不变量
都是由这类简单时钟约束做合取得到的，而不是任意实数公式 [AD90_ZH]_ [BY04_ZH]_。

\ **这一点很重要，最好现在就记住。**\ 后面的章节还会反复用到它：不只是区域 / 差分约束矩阵这种表示，
而是整个 UPPAAL 对时间自动机的绝大多数符号化验证(symbolic verification)做法，几乎都是建立在这种
“约束是简单差值/界约束的合取”这一性质上的。你后面看到的区域划分(region)、区域、差分约束矩阵、联邦、
规范化(normalization)、外推(extrapolation)，本质上都在吃这条结构性前提带来的红利。

回到上面的运行中的小例子，这个元组(tuple) 可以具体展开成：

.. math::

   A = (L, \ell_0, C, \Sigma, E, \mathrm{Inv})

其中：

* :math:`L = \{\mathrm{Idle}, \mathrm{WaitAck}, \mathrm{Error}\}`，
  也就是图里的三个位置
* :math:`\ell_0 = \mathrm{Idle}`，
  因为系统一开始还没有发请求
* :math:`C = \{x\}`，
  因为这个例子里只有一个时钟 ``x``
* :math:`\Sigma = \{\mathrm{send}, \mathrm{ack}, \mathrm{timeout}\}`，
  它们分别表示“发出请求”“收到确认”“发生超时”这三类离散动作
* :math:`E` 是图里的三条边组成的集合，可以写成：

  .. math::

     E = \{
     (\mathrm{Idle}, \mathrm{send}, \mathrm{true}, \{x\}, \mathrm{WaitAck}),
     (\mathrm{WaitAck}, \mathrm{ack}, \mathrm{true}, \emptyset, \mathrm{Idle}),
     (\mathrm{WaitAck}, \mathrm{timeout}, x \ge 5, \emptyset, \mathrm{Error})
     \}

  第一条边表示“发送请求并重置 ``x``”，第二条边表示“收到确认后回到 ``Idle``”，
  第三条边表示“当 :math:`x \ge 5` 时可以发生超时并进入 ``Error``”
* :math:`\mathrm{Inv}` 则给每个位置一个不变量：

  .. math::

     \mathrm{Inv}(\mathrm{Idle}) = \mathrm{true}, \qquad
     \mathrm{Inv}(\mathrm{WaitAck}) = (x \le 5), \qquad
     \mathrm{Inv}(\mathrm{Error}) = \mathrm{true}

  也就是说，真正限制时间停留长度的是 ``WaitAck``；而 ``Idle`` 和 ``Error`` 在这个玩具例子里没有额外时间上界

如果你把图上的 ``send!``、``ack?``、``timeout!`` 也一起考虑进去，那么它们是在
UPPAAL 网络语义里对动作方向做的补充标记：这里的自动机会发送 ``send`` 和 ``timeout``，
并接收 ``ack``。但就上面的数学元组而言，先把这些动作名记成
:math:`\mathrm{send}`、:math:`\mathrm{ack}`、:math:`\mathrm{timeout}` 就够了。

为什么状态里必须有赋值
~~~~~~~~~~~~~~~~~~~~~~

普通有限自动机里，经常只靠控制位置就能描述状态。

但时间自动机里不行。\ **时钟赋值(valuation)本身就是状态的一部分。**

标准写法是：

.. math::

   v : C \to \mathbb{R}_{\ge 0}

这里每个符号都可以直接读成：

* :math:`v` 是一个赋值，也就是“当前每个时钟各自取多少值”
* :math:`C` 是时钟集合；在运行中的小例子里就是 :math:`C = \{x\}`
* :math:`\to` 表示“从一个集合映射到另一个集合”
* :math:`\mathbb{R}_{\ge 0}` 表示非负实数集合，也就是 `0`、`0.3`、`2.7`、`5` 这类值

所以 :math:`v : C \to \mathbb{R}_{\ge 0}` 的意思其实很朴素：
\ **赋值 :math:`v` 会给每个时钟分配一个非负实数值。**

在这个例子里，因为只有一个时钟 ``x``，所以一个赋值基本上就是在说：

.. math::

   v(x) = 0
   \qquad \text{或} \qquad
   v(x) = 3.2
   \qquad \text{或} \qquad
   v(x) = 5

因此一个具体带时间状态(timed state) 会写成 :math:`(\ell, v)`，其中：

* :math:`\ell` 是当前位置
* :math:`v` 是当前所有时钟的取值

例如 :math:`(\mathrm{WaitAck}, v)` 且 :math:`v(x) = 4.9`，表示系统现在位于 ``WaitAck``，
并且距离超时边界已经非常近了。

有两个辅助记号经常一起出现：

.. math::

   (v + d)(x) = v(x) + d
   \qquad\qquad
   v[R := 0](x) =
   \begin{cases}
   0 & \text{if } x \in R, \\
   v(x) & \text{otherwise.}
   \end{cases}

这些符号也值得逐个拆开：

* :math:`d` 是流逝的时间长度，例如 `1`、`2.5`
* :math:`(v + d)` 表示“在赋值 :math:`v` 的基础上，让所有时钟一起增加 :math:`d`”
* :math:`(v + d)(x)` 表示“增加完之后，时钟 :math:`x` 的值是多少”
* :math:`R` 是要被重置的时钟集合
* :math:`v[R := 0]` 表示“从 :math:`v` 出发，把 :math:`R` 里的时钟全部改成 `0` 后得到的新赋值”
* :math:`v[R := 0](x)` 表示重置之后时钟 :math:`x` 的值

前者表示“让时间流逝 :math:`d`”；后者表示“把集合 :math:`R` 里的时钟重置为 `0`”。

在运行中的小例子里，因为只有一个时钟 ``x``：

* 如果当前 :math:`v(x) = 1`，再等 `2` 个时间单位，那么 :math:`(v + 2)(x) = 3`
* 如果当前 :math:`v(x) = 4`，并且发生某个把 ``x`` 重置的动作，那么对 :math:`R = \{x\}` 有
  :math:`v[R := 0](x) = 0`

回到前面的例子里，``(WaitAck, x = 1)`` 和 ``(WaitAck, x = 4.9)`` 虽然都在同一个位置，
但它们显然不是同一个状态。前者离超时还远，后者几乎马上就必须做出离散选择。

运行语义与组合
--------------

两类迁移语义
~~~~~~~~~~~~

时间自动机之所以和普通自动机不同，本质上就是因为它有两种完全不同的演化方式：

* **时间流逝迁移(delay transition)**：时间过去，所有时钟一起增长
* **离散迁移(discrete transition)**：走一条可用边，并可能重置部分时钟

时间流逝的语义规则可以写成：

.. math::

   (\ell, v) \xrightarrow{d} (\ell, v + d)
   \quad \text{if } d \in \mathbb{R}_{\ge 0}
   \text{ and } \forall \delta \in [0, d],\; v + \delta \models \mathrm{Inv}(\ell)

这里也可以把符号读成：

* :math:`(\ell, v)` 是当前状态
* :math:`\xrightarrow{d}` 表示“经过 :math:`d` 个时间单位的流逝”
* :math:`\forall \delta \in [0, d]` 表示“对从 `0` 到 :math:`d` 的每一个中间时刻都成立”
* :math:`\models` 表示“满足”；例如 :math:`v \models x \le 5` 意味着在赋值 :math:`v` 下约束 :math:`x \le 5` 为真
* :math:`\mathrm{Inv}(\ell)` 表示位置 :math:`\ell` 的不变量

这里最关键的是对 :math:`\delta` 的全称条件。它表示不变量必须在整段等待区间里都成立，
而不是只要求“开始时成立”或“结束时成立”。

对一条离散边 :math:`e = (\ell, a, g, R, \ell')`，规则可以写成：

.. math::

   (\ell, v) \xrightarrow{a} (\ell', v[R := 0])
   \quad \text{if } v \models g
   \text{ and } v[R := 0] \models \mathrm{Inv}(\ell')

这里的符号则可以读成：

* :math:`a` 是离散动作标签
* :math:`g` 是守卫条件
* :math:`R` 是重置集合
* :math:`\ell'` 是目标位置

这就把几种角色分清楚了：

* **守卫条件** 决定这条边什么时候可用
* **重置集合** 决定哪些时钟会跳回 `0`
* **目标不变量** 决定跳过去之后能不能合法停在目标位置

下面把前面的例子改画成“具体带时间状态的演化”：

.. graphviz:: state_evolution.dot

这张图想强调的语义点很简单但很重要：系统可以从 ``x = 0`` 一直拖到 ``x = 5``，但不能再继续等。
一旦到达这个边界，接下来就必须发生离散跳转；否则运行会被不变量卡死。

从单个自动机到自动机网络
~~~~~~~~~~~~~~~~~~~~~~~~

UPPAAL 实际上通常处理的是\ **时间自动机网络**，而不是单个自动机单独运行。此时一个全局状态可以写成：

.. math::

   ((\ell_1, \ldots, \ell_n), v)

其中每个 :math:`\ell_i` 是一个进程当前所在的位置，:math:`v` 是共享的时钟赋值。

直觉上可以这样理解：

* 时间流逝是全局的，所以所有时钟一起增长
* 离散步可以是某一个自动机自己走，也可以是多个自动机通过通道(channel)同步一起走
* 验证器(verifier) 并不会一个赋值一个赋值地枚举这个无限状态空间，而是后面会用符号状态来打包处理

这一页刻意先停留在单个自动机上，因为时钟、守卫条件、重置、不变量的基本语义，
在这个最小场景里就已经完整出现了。

最容易混淆的三个点
~~~~~~~~~~~~~~~~~~

时间自动机刚入门时，最容易把下面三件事混在一起：

* \ **位置不是完整状态。** 赋值也是状态的一部分。
* \ **不变量不是普通守卫条件。** 守卫条件管的是“能不能走某条边”；不变量管的是“还能不能继续待在这里”。
* \ **到达边界往往会逼出一个离散选择。** 如果再等已经不合法了，那下一步不是走边，就是死锁(deadlock)。

收束与定位
----------

这和 ``pyudbm`` 有什么关系
~~~~~~~~~~~~~~~~~~~~~~~~~~

这个仓库现在还没有把完整的 UPPAAL 语言和网络语义都恢复出来，但时间自动机这套视角已经足够解释：
为什么 Python 接口(API) 必须是以时钟为中心，而不是只暴露匿名矩阵操作。

可以直接把对应关系看成：

* ``Context`` 固定时钟集合 :math:`C`
* ``Clock`` 用来构造守卫条件、不变量和时钟差约束(clock-difference constraints)
* ``Federation`` 表示满足这些约束的一批赋值

所以 `pyudbm` 暴露的并不是“某种偶然的数据结构”，而是在暴露守卫条件、不变量和可达带时间状态
背后的符号约束层。

这一页最该记住什么
~~~~~~~~~~~~~~~~~~

如果这一页最后只记住五件事，那应该是：

* 时间自动机 = 有限控制图 + 时钟
* 一个具体状态是 ``(位置, 赋值)``
* 时间流逝和离散跳转是两类不同的迁移
* 不变量决定一个位置最多还能停多久
* 这些时钟约束正是后面区域和差分约束矩阵的语义来源

下一步
~~~~~~

下一篇最自然的内容是 :doc:`../queries-and-properties/index_zh`：模型长什么样讲清楚以后，接下来就是用户通常会问它什么性质。

.. [UPP_LOC_ZH] UPPAAL 官方文档，``Locations``。
   公开链接：`<https://docs.uppaal.org/language-reference/system-description/templates/locations/>`_。
.. [UPP_EDGE_ZH] UPPAAL 官方文档，``Edges``。
   公开链接：`<https://docs.uppaal.org/language-reference/system-description/templates/edges/>`_。
.. [UPP_SEM_ZH] UPPAAL 官方文档，``Semantics``。
   公开链接：`<https://docs.uppaal.org/language-reference/system-description/semantics/>`_。
.. [AD90_ZH] Rajeev Alur, David L. Dill。
   ``Automata for Modeling Real-Time Systems``。
   公开链接：`<https://dblp.org/rec/conf/icalp/AlurD90>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/ad90/README_zh.md>`_。
.. [BY04_ZH] Johan Bengtsson, Wang Yi。
   ``Timed Automata: Semantics, Algorithms and Tools``。
   公开链接：`<https://uppaal.org/texts/by-lncs04.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README_zh.md>`_。
