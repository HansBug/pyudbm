UPPAAL 在解决什么问题？
========================

这一页回答一个基础问题：UPPAAL 到底是干什么的？以及，为什么一个围绕 UDBM 层展开的仓库，
仍然必须关心更完整的 UPPAAL 背景？

短答案是：UPPAAL 是一套面向实时系统建模与验证的工具链。它不是一堆低层矩阵操作的集合，
而是一条工作流：用户建立带时间的模型、提出验证问题，再由符号引擎替用户探索大量时钟赋值组成的状态空间。
[LPY97_ZH]_ [BDL04_ZH]_ [BEH03_ZH]_

贯穿全文的小例子
----------------

考虑一个很小的请求-响应控制器：

* 客户端发出一个请求
* 服务端必须在 5 个时间单位内返回确认
* 如果超过截止时间还没有确认，控制器就进入错误状态

这个例子很适合作为起点，因为它已经包含了 UPPAAL 最关心的几个因素：

* 系统里存在并发或组件交互
* 正确性依赖于时间，而不只是事件顺序
* 只要存在一条坏执行，就已经算 bug

哪怕现在还没有形式语法，大多数读者也已经能理解核心问题：

错误状态到底能不能到达？

为什么不能只靠测试
------------------

对普通软件来说，测试和仿真通常是第一反应。在这里它们仍然有价值，但它们回答的问题和 model checking 并不一样
[LPY97_ZH]_ [BDL04_ZH]_。

测试或仿真更像是在问：
    “我试过的那些执行里，发生了什么？”

model checking 更像是在问：
    “在模型允许的所有执行里，是否存在任意一条执行会违反性质？”

对带时间的系统来说，这个区别尤其重要。一个请求-响应控制器在几次仿真里看起来都没问题，
并不代表它真的安全；只要某个部件比预期稍微多延迟一点，就可能踩到截止时间。

时间会带来无限多种可能的延迟，因此真正有意思的 bug 往往藏在两次手工挑选的测试场景之间。

为什么时间会让问题更难
----------------------

在带时间的模型里，只知道当前控制位置还不够，我们还需要知道当前各个时钟的取值。

一个常见写法是：

.. math::

   v : C \to \mathbb{R}_{\ge 0}

这条公式要这样读：

* :math:`C` 表示模型里的时钟集合
* :math:`\mathbb{R}_{\ge 0}` 表示非负实数集合
* :math:`v` 表示一个 valuation，也就是“给每个时钟分配一个当前实数时间值”的映射

这条公式虽然很短，但背后的含义非常关键。它说明时钟状态不是一个简单的整数计数器，
也不是一个布尔标志，而是一个从时钟名到非负实数的整体映射。

放回到前面的例子里，如果请求刚刚发出，时钟 :math:`x` 可以从 :math:`0` 开始计时。
过了 2.3 个时间单位后，valuation 可能把 :math:`x` 映射到 :math:`2.3`。
再过到 5.1 个时间单位时，这条执行就已经可能越过截止时间并进入错误。

因此，一个具体的带时间状态常常写成：

.. math::

   (\ell, v)

这对符号也需要拆开理解：

* :math:`\ell` 是当前控制位置，例如 ``WaitingForAck`` 或 ``Error``
* :math:`v` 是上面定义的当前时钟赋值

直观上，这意味着“只看控制流位置”是不够的。两条执行都在 ``WaitingForAck``，
但其中一条只等了 :math:`1.2` 个时间单位，另一条已经等了 :math:`4.9` 个时间单位，
它们的风险程度显然完全不同。

从高层看，UPPAAL 在做什么
--------------------------

从用户视角看，UPPAAL 大致包含四步 [LPY97_ZH]_ [BDL04_ZH]_ [BEH03_ZH]_：

* 把系统描述成一个 timed automata 网络
* 写出一个关于可达行为的性质或查询
* 用符号方式探索模型，而不是一次只看一个精确 valuation
* 给出答案，或者给出一条诊断性 counterexample / witness

整个流程可以概括成这样：

.. graphviz::

   digraph uppaal_overview_zh {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#f6f6f6", color="#666666"];
       model [label="带时间模型"];
       query [label="验证查询"];
       engine [label="符号探索"];
       result [label="答案或轨迹"];
       model -> query -> engine -> result;
   }

这里最关键的一点是：引擎通常不会一次只检查一个精确的时钟赋值。后面的页面会详细讲 zone、
DBM 和 federation，但在这里先记住高层原因就够了：带实值时钟的状态空间实在太大，无法朴素枚举。
[BEH03_ZH]_

用户通常在问什么问题
--------------------

在真实使用里，用户一开始很少会问“所有 valuation 的精确集合是什么”。他们更常问的是目标导向的问题：

* 坏状态能不能到达？
* 截止时间是否总能满足？
* 模型会不会 deadlock？
* 出现某种故障后，恢复状态是否仍然可达？

回到这个请求-响应例子，最自然的几个问题就是：

* ``Error`` 状态能不能到达？
* 每个请求是否都能在 5 个时间单位内被确认？
* 模型会不会一直等下去，最后卡死？

具体的 UPPAAL query 语法后面再讲。当前只需要把握住直觉：

这个工具首先是为了回答带时间模型的行为问题，而不是把 DBM 内部结构直接当成最终用户接口。

为什么会进入符号探索
--------------------

如果时间是离散而且范围很小，也许我们还能直接枚举状态。但带时间系统通常用实值时钟来描述，
所以“逐个精确状态枚举”很快就会变得不可行。

这正是 UPPAAL 要从具体状态 :math:`(\ell, v)` 走向符号状态的原因。后面常见的一种写法是
:math:`(\ell, Z)`，其中 :math:`Z` 表示一个 zone。

这一页先不展开 zone 的细节，但现在就应该建立下面几个直觉：

* 一个符号状态代表的是很多个具体 timed states
* 符号探索是让验证真正可做的关键工程手段
* DBM 和 federation 不是孤立的数据结构，而是服务于这条大工作流的表示层

这也正是 UDBM 在整个故事里的位置。UDBM 并不能单独讲完全部 UPPAAL，
但它实现了其中最关键的一层符号表示能力。

这和 ``pyudbm`` 有什么关系
---------------------------

当前仓库封装的是 UDBM 层，而不是完整的 UPPAAL model checker。即便如此，更大的背景依然重要。

原因很简单：历史上的 UDBM Python 绑定之所以自然，并不是因为用户想直接操作“矩阵库”，
而是因为它贴合了 UPPAAL 用户真正的思考方式：

* 有名字的 clocks
* 可读的时间约束表达式
* 表示 valuation 集合的符号对象
* 看起来像“模型层操作”而不是“表格底层操作”的接口

这就是为什么 :mod:`pyudbm` 要恢复 ``Context``、``Clock`` 和 ``Federation`` 作为一等对象。
只有把它们放回完整的用户工作流里，这套接口才最容易理解。

这一页最该记住什么
------------------

如果这一页最后只记住四件事，那应该是：

* UPPAAL 关心的是带时间行为的验证，不只是仿真
* 时间让状态空间变难，是因为时钟取值来自实数域
* 符号探索是应对这件事的核心工程办法
* UDBM 和这个仓库之所以重要，是因为它们支撑了这条符号工作流中的关键表示层

延伸阅读
--------

读完这一页之后，下一步应该继续进入后续会补上的 ``timed-automata/`` 页面。

参考文献
--------

.. [LPY97_ZH] Kim Guldstrand Larsen, Paul Pettersson, Wang Yi.
   ``UPPAAL in a Nutshell``。
   公开链接：`<https://dblp.org/rec/journals/sttt/LarsenPY97>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/lpy97/README_zh.md>`_。
.. [BDL04_ZH] Gerd Behrmann, Alexandre David, Kim Guldstrand Larsen.
   ``A Tutorial on UPPAAL``。
   公开链接：`<https://dblp.org/rec/conf/sfm/BehrmannDL04>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/bdl04/README_zh.md>`_。
.. [BEH03_ZH] Gerd Behrmann.
   ``Data Structures and Algorithms for the Analysis of Real Time Systems``。
   公开链接：`<https://uppaal.org/texts/behrmann_phd.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/behrmann03/paper-intro/README_zh.md>`_。
