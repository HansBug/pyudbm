联邦(federation)基础：多个 DBM 如何精确表示非凸集合
====================================================

这一页回答的是紧接着
:doc:`../dbm-basics/index_zh`
之后的下一个问题：**如果一个 DBM 已经能精确表示一个凸区域，那么当符号操作产生非凸集合时该怎么办？**

对 UDBM 来说，答案是 **联邦**：它是有限个 DBM 的并。这就是单个规范 DBM 之上的下一层精确表示，
也是为什么当前高层 Python 接口不是停在裸矩阵上，而是以 :class:`pyudbm.Federation` 为核心对象
[DHLP06_FED_ZH]_ [BEHR03_CDD_ZH]_ [UDBM_FED_H_ZH]_ [UDBM_FED_CPP_ZH]_。

这一页首先仍然是一篇教程，而不是速查表。因此它不会一上来只列 API，而是会先把
“为什么需要联邦”这条叙事主线讲清楚，再回过头去系统梳理当前 Python 绑定里
``联邦`` 对象到底支持哪些操作与性质。

目标是把下面三层明确连起来：

* 论文里为什么需要联邦
* UDBM 原生 ``fed_t`` 这一层到底在做什么
* 当前 :mod:`pyudbm` 已经恢复出来的联邦 API 能力边界

为什么单个 DBM 终究不够
------------------------------------------------------------

从上一页延续下来，最关键的限制其实很简单：

* 一个 DBM 只表示一个凸区域
* 真实的符号算法不会永远停留在凸世界里

最容易把这件事看穿的地方，就是减法。

先取一个外层区域 :math:`Z`，再减去一个内层区域 :math:`H`：

.. math::

   Z = \{(x,y) \mid 1 \leq x \leq 5,\; 1 \leq y \leq 5\}

.. math::

   H = \{(x,y) \mid 2 \leq x \leq 4,\; 2 \leq y \leq 4\}

.. math::

   R = Z \setminus H

结果已经不再是凸的。它会变成一个中间挖空的矩形壳：

.. image:: subtract_nonconvex.plot.py.svg
   :width: 94%
   :align: center
   :alt: 三联图，展示一个外层区域、一个被减去的内层区域，以及得到的非凸减法结果。

这正是 subtraction 论文强调的核心压力 [DHLP06_FED_ZH]_：一旦减法把我们带出凸世界，单个 DBM 就不再是足够精确的结果容器。

因此，在 UDBM 里，精确结果会变成多个 DBM 的并，而不是“再造一个更复杂的单矩阵”。在当前 Python 绑定里，同一个例子可以直接写成：

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

从数学上说，这意味着

.. math::

   R = D_1 \cup D_2 \cup D_3 \cup D_4

其中每个 :math:`D_i` 仍然只是普通的凸 DBM 区域。

UDBM 里的联邦到底是什么
------------------------------------------------------------

联邦并不是一种全新的约束语言。它的语义其实非常朴素：**一个联邦就是有限个普通 DBM 区域的并**。
如果时钟集合是 :math:`C`，那么一个联邦 :math:`F` 可以写成

.. math::

   F = D_1 \cup D_2 \cup \cdots \cup D_n,

其中每个 :math:`D_i \subseteq \mathbb{R}_{\ge 0}^{|C|}` 都仍然是由差分约束定义出来的凸区域，也就是一个普通 DBM。
因此，对任意赋值 :math:`v`，联邦成员关系只是

.. math::

   v \in F \iff \exists i \in \{1,\dots,n\},\; v \in D_i.

换句话说，单个 DBM 对应的是“一个凸块”；联邦对应的是“若干个凸块的精确并”。论文里经常把这一层直接视为
非凸符号状态的最直接精确表示 [DHLP06_FED_ZH]_ [BEHR03_CDD_ZH]_。

这件事的重要性，不只是“它能装下非凸集合”这么一句话。更准确地说，它保住了两层结构：

* 底层仍然是 DBM，因此单块区域上的规范化、最小约束、包含检查、延时、重置这些成熟算法都还成立。
* 上层只负责把这些单块操作提升到有限并上，而不是重新发明另一套针对时钟差约束的基础算法 [UDBM_FED_H_ZH]_ [UDBM_FED_CPP_ZH]_。

因此，如果某个操作 :math:`\Phi` 在单个 DBM 上已经有明确定义，那么联邦层最自然的精确提升通常就是

.. math::

   \Phi(F) = \bigcup_{i=1}^{n} \Phi(D_i).

例如时间后继可以理解成

.. math::

   \mathrm{up}(F) = \bigcup_{i=1}^{n} \mathrm{up}(D_i),

而忘掉某个时钟也可以理解成

.. math::

   \mathrm{free}_x(F) = \bigcup_{i=1}^{n} \mathrm{free}_x(D_i).

集合运算同样如此。若 :math:`F = \bigcup_i D_i`、:math:`G = \bigcup_j E_j`，那么

.. math::

   F \cap G = \bigcup_{i,j} (D_i \cap E_j).

这就是为什么高层 API 看起来像是在操作一个对象，实际上语义上一直是在操作“若干个 DBM 的并”。

减法论文把这个动机讲得更直接。给两个 DBM :math:`D` 和 :math:`E`，减法定义为

.. math::

   D - E = D \land \neg E.

问题就在这里：:math:`\neg E` 一般不是一个区域，所以结果也一般不再是单个凸 DBM。论文进一步把它展开成
“由 :math:`E` 的若干被取反约束切出来的一组 DBM 之并” [DHLP06_FED_ZH]_：

.. math::

   D - E = \bigcup_k \bigl(D \land \neg e_k\bigr),

其中 :math:`e_k` 是 :math:`E` 的约束。也就是说，联邦并不是后来人为补出来的“容器层”；它几乎是从减法
这个运算本身自然长出来的表示层。

不过，联邦也因此有一个和单个规范 DBM 很不一样的地方：**它不是天然规范的**。同一个集合，可能既能写成
:math:`D_1 \cup D_2`，也能写成 :math:`D'_1 \cup D'_2 \cup D'_3`，甚至这些 DBM 之间还可能有重叠。因此在 ``fed_t``
这一层，除了集合运算本身，还必须有 ``reduce()``、``intern()``、包含式合并和共享这类表示维护动作
[UDBM_FED_H_ZH]_ [UDBM_FED_CPP_ZH]_。这也是为什么联邦 API 里会出现“几何语义不变，但内部表示会变化”的操作：
它们不是多余的优化接口，而是显式 DBM-list 表示法的现实成本。

从源码角度看，UDBM 里的这一层对应 ``fed_t``。``fed.h`` 里直接把联邦层的核心语义列得很清楚：
``|`` 是精确并，``-`` 是精确减法，``+`` 是凸并，此外还有 ``freeClock``、``reduce``、
``predt``、``setZero``、``setInit`` 等操作 [UDBM_FED_H_ZH]_。这说明在 UDBM 里，联邦并不是“几个 DBM 顺手放在一起”，
而是一层明确的一等数据结构。

也正因为如此，Behrmann 的 CDD 论文才会把“显式 DBM 列表形式的联邦”当成一个需要继续改进的基线来讨论。
论文明确指出，有限个区域的并当然可以用 DBM 列表来表示；但当非凸性变强时，需要的 DBM 数量会迅速增长，
而包含检查也会变贵 [BEHR03_CDD_ZH]_。CDD 想解决的正是这个问题：**如何比显式联邦更紧凑地表示和共享非凸集合**。

所以，这一页讨论的“联邦”可以理解成一个非常具体的位置：

* 它比单个 DBM 更强，因为它能精确承载非凸结果。
* 它比 CDD 更朴素，因为它仍然坚持“结果就是若干个 DBM 的并”。
* 它也是 UDBM 当前高层接口的主力对象，因为这正是很多时间自动机符号操作从凸世界跨到非凸世界时，
  最自然也最忠实的一层表示。

联邦能做什么
------------------------------------------------------------

下面这张表按“表示 / 集合运算 / 变换 / 查询性质”四类，把当前绑定暴露出来的联邦语义面一次列全。

它只关心当前 Python 绑定里 **语义相关的联邦接口**。像 ``copy()``、``plot()``、字符串化和哈希这类对象基础设施接口，
这里先不放进来。

.. list-table::
   :header-rows: 1
   :widths: 18 16 14 18 34

   * - API
     - 类型
     - 语义
     - 修改方式
     - 跳转到详解
   * - ``to_dbm_list()``
     - 表示查看
     - 精确
     - 返回快照
     - :ref:`fed-zh-to-dbm-list`
   * - ``get_size()``
     - 表示查看
     - 精确
     - 只读查询
     - :ref:`fed-zh-get-size`
   * - ``&``
     - 集合运算
     - 精确
     - 返回新联邦
     - :ref:`fed-zh-and`
   * - ``|``
     - 集合运算
     - 精确
     - 返回新联邦
     - :ref:`fed-zh-or`
   * - ``+``
     - 集合运算
     - 凸过近似
     - 返回新联邦
     - :ref:`fed-zh-add`
   * - ``-``
     - 集合运算
     - 精确
     - 返回新联邦
     - :ref:`fed-zh-sub`
   * - ``up()``
     - 时间变换
     - 精确
     - 返回新联邦
     - :ref:`fed-zh-up`
   * - ``down()``
     - 时间变换
     - 精确
     - 返回新联邦
     - :ref:`fed-zh-down`
   * - ``free_clock()``
     - 时钟变换
     - 精确
     - 返回新联邦
     - :ref:`fed-zh-free-clock`
   * - ``set_zero()``
     - 重新初始化
     - 精确
     - 原地修改 ``self``
     - :ref:`fed-zh-set-zero`
   * - ``has_zero()``
     - 性质
     - 精确
     - 只读查询
     - :ref:`fed-zh-has-zero`
   * - ``set_init()``
     - 重新初始化
     - 精确
     - 原地修改 ``self``
     - :ref:`fed-zh-set-init`
   * - ``convex_hull()``
     - 形状变换
     - 凸过近似
     - 返回新联邦
     - :ref:`fed-zh-convex-hull`
   * - ``==`` / ``!=``
     - 关系判断
     - 精确
     - 只读查询
     - :ref:`fed-zh-relations`
   * - ``<=`` / ``>=`` / ``<`` / ``>``
     - 关系判断
     - 精确
     - 只读查询
     - :ref:`fed-zh-relations`
   * - ``intern()``
     - 表示维护
     - 几何不变
     - 修改内部共享状态
     - :ref:`fed-zh-intern`
   * - ``predt()``
     - 时序变换
     - 精确
     - 返回新联邦
     - :ref:`fed-zh-predt`
   * - ``contains()``
     - 成员判断
     - 精确
     - 只读查询
     - :ref:`fed-zh-contains`
   * - ``update_value()``
     - 时钟赋值
     - 精确
     - 返回新联邦
     - :ref:`fed-zh-update-value`
   * - ``reset_value()``
     - 时钟赋值
     - 精确
     - 返回新联邦
     - :ref:`fed-zh-reset-value`
   * - ``reduce()``
     - 表示维护
     - 几何不变
     - 原地修改 ``self``
     - :ref:`fed-zh-reduce`
   * - ``extrapolate_max_bounds()``
     - 抽象
     - 过近似
     - 返回新联邦
     - :ref:`fed-zh-extrapolate-max-bounds`
   * - ``is_zero()``
     - 性质
     - 精确
     - 只读查询
     - :ref:`fed-zh-is-zero`
   * - ``is_empty()``
     - 性质
     - 精确
     - 只读查询
     - :ref:`fed-zh-is-empty`

这里面最关键的统一直觉是：

.. math::

   F = D_1 \cup D_2 \cup \cdots \cup D_n

每个 :math:`D_i` 仍然只是一个普通的凸 DBM 区域。联邦层并没有取代 DBM，而是在其之上给“有限个 DBM 的并”一个精确对象。

表示与结构查询
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _fed-zh-to-dbm-list:

``to_dbm_list()``：把联邦拆成凸片段
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

最直接理解联邦的方法，就是把它拆成组成它的 DBM 片段：

.. image:: decompose.plot.py.svg
   :width: 54%
   :align: center
   :alt: 一个由两个凸 DBM 片段组成的联邦。

.. code-block:: python

   from pyudbm import Context

   c = Context(["x", "y"])
   x = c.x
   y = c.y

   fed = ((x >= 1) & (x <= 2) & (y >= 1) & (y <= 3)) | ((x >= 4) & (x <= 5) & (y >= 2) & (y <= 4))
   pieces = fed.to_dbm_list()
   piece_texts = sorted(dbm.to_string() for dbm in pieces)

   assert len(pieces) == 2
   assert piece_texts == [
       "(1<=x & 1<=y & x<=2 & y<=3)",  # D1
       "(4<=x & 2<=y & x<=5 & y<=4)",  # D2
   ]

这里得到的是一个 **精确表示快照**，不是近似，不是采样，也不是重新求凸包。
这个例子里，字符串已经把两个片段各自的约束写清楚了：``D1`` 是左边矩形，``D2`` 是右边矩形。
之所以先排序，只是为了让示例不依赖底层返回顺序。

.. _fed-zh-get-size:

``get_size()``：当前到底有多少个 DBM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

同一张分解图也解释了 ``get_size()`` 的含义：

.. code-block:: python

   assert fed.get_size() == 2

``get_size()`` 数的是原生联邦内部当前持有的 DBM 个数，而不是边数、顶点数、约束个数或坐标轴切片数。
因此它是一个 **表示层面的大小指标**。

.. _fed-zh-reduce:
.. _fed-zh-intern:

``reduce()`` 与 ``intern()``：表示维护，而不是集合语义
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

联邦不只是一个集合语义对象，也是一个可能越长越复杂的表示容器。因此还会有表示维护类操作：

.. image:: fed_reduce_intern.plot.py.svg
   :width: 88%
   :align: center
   :alt: 三联图，展示 reduce 前、reduce 后，以及 intern 后的联邦表示。

``reduce()`` 的典型价值，就是把一个表示上别扭的联邦压缩得更简单，但几何区域不变。这里用一个很短的例子：
``x <= 1 | x >= 1`` 在左图里还是两个 DBM，中图里则被规约成了一个更简单的表示：

.. code-block:: python

   complex_fed = (x <= 1) | (x >= 1)
   assert complex_fed.get_size() == 2

   complex_fed.reduce()
   assert complex_fed.get_size() == 1
   assert complex_fed == (x >= 0)

``intern()`` 则更进一步，它根本不是几何变换，也不是集合变换。它只是请求 UDBM 在内部对相同的规范 DBM 做共享，
所以右图几何上看起来不会再变化：

.. code-block:: python

   complex_fed.intern()
   assert complex_fed.get_size() == 1
   assert complex_fed == (x >= 0)

因此更好的理解方式是：

* ``reduce()`` 尝试改善 **可见的 DBM 列表**
* ``intern()`` 尝试改善 **内部共享与相等判断成本**
* 二者都不应该改变所表示的符号集合

集合运算
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _fed-zh-and:

``&``：精确交
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

交运算仍然完全留在精确符号语义内：

.. image:: fed_and.plot.py.svg
   :width: 92%
   :align: center
   :alt: 三联图，展示两个区域以及它们的精确交。

.. code-block:: python

   left = (x >= 1) & (x <= 4) & (y >= 1) & (y <= 4)
   right = (x >= 3) & (x <= 5) & (y >= 2) & (y <= 5)
   exact_intersection = left & right

前两个面板里已经把另一个操作数的轮廓叠了进去，因此在看结果之前就能直观看到重叠区域。
最后一个面板再把原本的 ``A``、``B`` 作为虚线参考叠在结果上，填充部分才是精确的 ``A & B``。

它的结果通常仍然足够凸，因此常常能落回一个 DBM。

.. _fed-zh-or:

``|``：精确并
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

精确并会保留所有片段，也保留所有空隙：

.. image:: fed_or.plot.py.svg
   :width: 92%
   :align: center
   :alt: 三联图，展示两个凸片段以及它们的精确并。

.. code-block:: python

   exact = a | b

结果面板里两块区域仍然是分开的，中间的空隙没有被补上，这正是联邦层在表达上的关键价值。

这正是联邦层最自然的构造方式：分支、减法或路径分裂之后，把多个精确凸片段用并连接起来。

.. _fed-zh-add:

``+``：凸并
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``+`` 不是 ``|`` 的快一点版本。它表示的是 UDBM 风格的 **凸并**：

.. image:: fed_add.plot.py.svg
   :width: 88%
   :align: center
   :alt: 双联图，展示保留空隙的精确并，以及由凸并填满空隙后的结果。

.. code-block:: python

   hull_like = a + b

这里必须再分清一件事：**精确并不等于凸包，也不等于凸并。**

在这张图里，左边的精确并保留了中间空隙；右边的凸并把空隙填满，因此会引入新的赋值。
也就是说，``+`` 从语义上就已经不是精确并，而是凸过近似风格操作。

这也是为什么联邦支持绝不是“把几个 DBM 装进一个对象”这么简单。像 ``|`` 和 ``+`` 这样的操作，看起来都在“合并区域”，
但它们对应的符号语义并不一样。

.. _fed-zh-sub:

``-``：精确减法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

减法正是前面教程动机部分里最核心的例子。到了 API 层，它对应的写法其实很直接：

.. image:: subtract_nonconvex.plot.py.svg
   :width: 94%
   :align: center
   :alt: 三联图，展示一个外层区域、一个被减去的内层区域，以及得到的非凸减法结果。

.. code-block:: python

   ring = outer - hole

联邦上的变换
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _fed-zh-up:

``up()``：时间后继
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``up()`` 把普通 DBM 的 delay successor 提升到联邦层：

.. image:: fed_up.plot.py.svg
   :width: 88%
   :align: center
   :alt: 联邦 up 操作的前后对比图。

.. code-block:: python

   delayed = fed.up()

语义上，它会放松针对零时钟的上界，让时间得以流逝。

.. _fed-zh-down:

``down()``：时间前驱
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``down()`` 是相对的时间前驱：

.. image:: fed_down.plot.py.svg
   :width: 88%
   :align: center
   :alt: 联邦 down 操作的前后对比图。

.. code-block:: python

   predecessor = fed.down()

它会放松下界，使“再延迟一会儿就能进入当前联邦”的状态也被纳入。

.. _fed-zh-free-clock:

``free_clock()``：忘掉一个时钟
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

释放一个时钟，会把与该时钟相关的大部分信息性约束拿掉：

.. image:: fed_free.plot.py.svg
   :width: 88%
   :align: center
   :alt: freeClock 操作的前后对比图。

.. code-block:: python

   freed = fed.free_clock(y)

几何上，它经常会把一个有界形状变成条带或半无限区域。

.. _fed-zh-set-zero:

``set_zero()``：重置为原点区
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``set_zero()`` 会原地把当前联邦变成单个原点赋值：

.. image:: fed_set_zero.plot.py.svg
   :width: 88%
   :align: center
   :alt: setZero 操作的前后对比图。

.. code-block:: python

   zone.set_zero()
   assert zone.has_zero()

这不是语义简写，而是一个精确重置。

.. _fed-zh-set-init:

``set_init()``：重置为标准初始区
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``set_init()`` 会把当前联邦替换成标准的非负初始区：

.. image:: fed_set_init.plot.py.svg
   :width: 88%
   :align: center
   :alt: setInit 操作的前后对比图。

.. code-block:: python

   zone.set_init()
   assert str(zone) == "true"

这里的意思是：所有时钟只受“非负”这一环境约束。

.. _fed-zh-convex-hull:

``convex_hull()``：联邦整体求凸包
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``convex_hull()`` 是对一个已有联邦求整体凸包：

.. image:: union_vs_hull.plot.py.svg
   :width: 88%
   :align: center
   :alt: 精确并与凸包的对比图。

.. code-block:: python

   hull = exact.convex_hull()

它和 ``+`` 的区别在于用法层：

* ``a + b`` 是二元凸并
* ``f.convex_hull()`` 是对一个已有联邦内部全部 DBM 统一求凸包

.. _fed-zh-predt:

``predt()``：避开 bad 的时间前驱
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``predt()`` 计算的是：哪些状态可以在 **一直避开 bad** 的同时，经过时间流逝进入 good：

.. image:: fed_predt.plot.py.svg
   :width: 88%
   :align: center
   :alt: 展示 good、bad 与 predt 结果的图。

.. code-block:: python

   pred = good.predt(bad)

这正是联邦层开始显得像“符号状态引擎”而不只是“DBM 容器”的地方之一。

.. _fed-zh-update-value:
.. _fed-zh-reset-value:

``update_value()`` 与 ``reset_value()``：时钟赋值
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

这两个操作都会把某个时钟赋成具体值：

.. image:: fed_update.plot.py.svg
   :width: 94%
   :align: center
   :alt: 三联图，展示基础区域、updateValue 到 x=2、以及 resetValue 到 x=0。

.. code-block:: python

   updated = fed.update_value(x, 2)
   reset = fed.reset_value(x)

其中 ``reset_value(clock)`` 只是 ``update_value(clock, 0)`` 的便捷形式。

.. _fed-zh-extrapolate-max-bounds:

``extrapolate_max_bounds()``：最大界外推
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

外推是教程从“精确符号语义”走向“为了终止性而做抽象”的分界点：

.. image:: fed_extrapolate.plot.py.svg
   :width: 88%
   :align: center
   :alt: maximal-bound extrapolation 的前后对比图。

.. code-block:: python

   abstracted = fed.extrapolate_max_bounds({"x": 100, "y": 100})

这里的重点不是精确保留原区域，而是丢掉超出最大常数的信息，从而让分析过程保持有限 [UDBM_FED_H_ZH]_。

查询与性质
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _fed-zh-contains:

``contains()``：点成员判断
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

性质总览图里有一个最直接的成员判断画面：

.. image:: fed_properties.plot.py.svg
   :width: 94%
   :align: center
   :alt: 性质总览图，展示 decomposition、subset、contains、hasZero、isZero 和 isEmpty。

其中 ``contains`` 面板里，一个点落在联邦内部，另一个点落在中间空隙中：

.. code-block:: python

   assert fed.contains(inside_point)
   assert not fed.contains(outside_point)

这就是 valuation membership 最字面的几何意义。

.. _fed-zh-has-zero:
.. _fed-zh-is-zero:

``has_zero()`` 与 ``is_zero()``：原点相关查询
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

同一张性质图里，这两个问题其实非常不同：

* ``has_zero()`` 问的是：原点是否属于当前联邦
* ``is_zero()`` 问的是：整个联邦是否恰好就是原点区

因此 ``hasZero`` 面板里仍然是一个非平凡区域，而 ``isZero`` 面板则真正收缩成单点 :math:`(0,0)`。

.. _fed-zh-is-empty:

``is_empty()``：空联邦
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

性质图最后一个面板展示的是空联邦。它来自矛盾约束，例如：

.. code-block:: python

   empty = (x == 1) & (x != 1)
   assert empty.is_empty()

.. _fed-zh-relations:

``==``、``!=``、``<=``、``>=``、``<``、``>``：集合关系
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

这六个比较运算最好直接分开看：

.. image:: fed_relations.plot.py.svg
   :width: 94%
   :align: center
   :alt: 一个 2 行 3 列的关系图，分别展示 ==、!=、<=、>=、<、> 的代表性集合关系。

图里每个面板都给了一个代表性例子。对于非严格关系 ``<=`` 和 ``>=``，相等当然也算成立，
这里只是故意画成了真包含，这样几何上更直观。

* ``A == B`` 表示两个联邦是同一个符号集合
* ``A != B`` 表示两个联邦不是同一个符号集合
* ``A <= B`` 表示子集
* ``A >= B`` 表示超集
* ``A < B`` 表示真子集
* ``A > B`` 表示真超集

也就是说，联邦比较运算是 **集合论意义上的比较**，而不是对象身份比较，也不是字符串比较。

这一页最该记住什么
------------------------------------------------------------

下面这些区分在实践里尤其重要：

* **联邦仍然是由 DBM 组成的。** 它不是把 DBM 废掉，而是在其上加一层。
* **减法让联邦从“可选设计”变成“语义必需”。** 非凸结果不是 API 装饰，而是集合语义本身。
* **精确并和凸并不是一个操作的快慢两种实现。** 它们表达的是不同的符号意义。
* **reduce 和 intern 关心的是表示质量。** 联邦大小和内部共享会影响后续符号计算成本。
* **外推不是精确变换。** 它是为了终止性而有意做的抽象。
* **公开 Python 接口之所以必须围绕联邦展开，是因为单个 DBM 从语义上根本不够。**

下一步
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在联邦之后，最自然的下一页就是规划中的 ``cdd/``：既然“有限个 zone 的并”已经成为一等对象，
那么下一个问题就是，显式维护一个 DBM 列表是否总是最好的表示，还是说共享图结构有时能把同一个符号集合压得更紧。

参考文献
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. [DHLP06_FED_ZH] Alexandre David, Kim G. Larsen, Didier Lime, Brian H. Poulsen.
   ``Subtracting Clock Zones``。
   公开链接：`<https://homes.cs.aau.dk/~adavid/dhlp06-zones.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/dhlp06/README_zh.md>`_。
.. [BEHR03_CDD_ZH] Gerd Behrmann.
   ``Efficient Timed Reachability Analysis using Clock Difference Diagrams``。
   公开链接：`<https://www.brics.dk/RS/98/47/BRICS-RS-98-47.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/behrmann03/paper-c/README_zh.md>`_。
.. [UDBM_FED_H_ZH] UPPAALModelChecker。
   ``UDBM/include/dbm/fed.h``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/fed.h>`_。
.. [UDBM_FED_CPP_ZH] UPPAALModelChecker。
   ``UDBM/src/fed.cpp``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/src/fed.cpp>`_。
