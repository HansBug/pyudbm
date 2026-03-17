UPPAAL 是做什么的？
====================

这一页是一篇真正面向新手的导论。它只回答一个简单问题：
\ **UPPAAL 到底想解决什么问题？**

\ **UPPAAL 是一套面向实时系统的建模、仿真与验证工具环境。** 官方首页把它描述为一个
针对“带数据类型扩展的时间自动机(timed automata)网络”的集成式工具环境；官方文档则把它定位为
适用于“具有有限控制结构、实值时钟、通过通道(channel)或共享数据(shared data)通信的非确定性进程集合”
的工具 [UPP_HOME_ZH]_ [UPP_HELP_ZH]_。

对这个仓库来说，理解这个大背景很重要。`pyudbm` 封装的是 UDBM 层，而 UDBM 只是整个 UPPAAL 故事里的
一层符号表示能力，不是全部。

一个很小的例子
--------------

考虑一个很简单的请求-响应控制器：

* 客户端发出请求
* 服务端应该在 5 个时间单位内返回确认
* 如果超时还没有确认，系统就进入 ``Error`` 状态

哪怕现在你什么术语都还没学，核心问题也已经很直观了：
\ **错误状态到底能不能到达？**

先用一个很简单的控制系统图把事情说具体：

.. graphviz::

   digraph control_loop_zh {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#f8f8f8", color="#666666"];
       client [label="客户端\n发送请求"];
       controller [label="控制器\n启动时钟 x"];
       server [label="服务端\n返回确认"];
       error [label="若 x > 5 且\n还未确认则 Error", fillcolor="#fff1f1", color="#aa5555"];
       client -> controller [label="request"];
       controller -> server [label="dispatch"];
       server -> controller [label="ack"];
       controller -> error [label="超时"];
   }

这个图现在还不是时间自动机图。它只是先把故事讲具体：有请求、有确认、有截止时间(deadline)、有错误状态。

为什么不能只靠测试
------------------

测试和仿真当然仍然有用，但它们回答的问题不一样。

测试或仿真更像是在问：
    “我试过的那些执行里，发生了什么？”

模型检查(model checking)更像是在问：
    “在模型允许的所有执行里，是否存在任意一条执行会违反性质？”

这个差别对带时间系统尤其重要。你手上跑过的几条执行可能都没问题，但真正出错的那条执行，
也许只是某个部件“刚好多等了一点点”。时间会带来大量可能的延迟，因此 bug 往往藏在你没有试到的地方
[LPY97_ZH]_ [BDL04_ZH]_。

为什么时间会让问题更难
----------------------

在无时间模型里，一个状态通常主要靠“当前在什么控制位置”来描述。

但在带时间模型里，这还不够。\ **我们还必须知道当前时钟的取值。**

一个常见写法是：

.. math::

   v : C \to \mathbb{R}_{\ge 0}

可以把它读成：

* :math:`C` 是时钟集合
* :math:`v` 给每个时钟一个非负实数值

这意味着：两条执行就算都在同一个控制位置，也可能完全不同，因为其中一条已经等了 `1.2` 个时间单位，
另一条可能已经等了 `4.9` 个时间单位。

回到前面的例子里，这个差别就可能直接决定“还安全”还是“已经超时”。

UPPAAL 实际在做什么
--------------------

从高层看，UPPAAL 支持一条很简单的工作流：

* 建立带时间模型
* 用仿真观察可能行为
* 提出验证查询(query)
* 得到答案或诊断性轨迹(trace)

它的整体工作流可以简单画成这样：

.. graphviz::

   digraph uppaal_overview_zh {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#f6f6f6", color="#666666"];
       model [label="带时间模型"];
       sim [label="仿真"];
       query [label="查询"];
       engine [label="符号探索"];
       result [label="答案或轨迹"];
       model -> sim;
       model -> query;
       sim -> query;
       query -> engine -> result;
   }

官方文档也明确表明，UPPAAL 不只是一个语言，还包括图形界面、验证器(verifier)、仿真器(simulator)
和命令行使用方式 [UPP_HELP_ZH]_ [UPP_FEATURES_ZH]_。

为什么会出现“符号状态”
----------------------

如果时钟取值来自实数域，那么精确的带时间状态会多到没法一个一个枚举。

这就是为什么 UPPAAL 不会只处理单个具体状态，而要把很多赋值(valuation)打包成
\ **符号状态(symbolic states)**。

你现在还不需要掌握细节。只要先记住这三个直觉就够了：

* 精确带时间状态太多了
* 符号状态会把很多状态合在一起表示
* 这正是让验证真正可做的关键工程办法

后面的页面会继续解释区域(zone)、差分约束矩阵(DBM)和联邦(federation)；这一页只需要先让你知道
它们为什么会出现。

这和 ``pyudbm`` 有什么关系
---------------------------

`pyudbm` 现在并没有实现完整的 UPPAAL 工具链，它主要封装 UDBM 层。但如果你忘了整个大背景，
就很容易误以为 UDBM 只是一个“矩阵工具”。

\ **真实用户首先想到的并不是原始矩阵，而是时钟、约束、可达行为和错误状态。**
这也是为什么这个仓库要恢复 ``Context``、``Clock`` 和 ``Federation`` 这样的高层对象。

这一页最该记住什么
------------------

如果这一页最后只记住五件事，那应该是：

* \ **UPPAAL 处理的是带时间系统。**
* \ **它帮助用户建模、仿真和验证。**
* \ **测试几条执行，不等于检查所有可能执行。**
* \ **实值时钟会让验证变难。**
* \ **符号状态是解决这个问题的关键办法。**

下一步
------

下一篇最自然的内容是 :doc:`../timed-automata/index_zh`，也就是正式介绍模型长什么样。

.. [UPP_HOME_ZH] UPPAAL 官方首页。
   公开链接：`<https://uppaal.org/>`_。
.. [UPP_HELP_ZH] UPPAAL 官方文档总入口。
   公开链接：`<https://docs.uppaal.org/>`_。
.. [UPP_FEATURES_ZH] UPPAAL 官方功能页面。
   公开链接：`<https://uppaal.org/features/>`_。
.. [LPY97_ZH] Kim Guldstrand Larsen, Paul Pettersson, Wang Yi.
   ``UPPAAL in a Nutshell``。
   公开链接：`<https://dblp.org/rec/journals/sttt/LarsenPY97>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/lpy97/README_zh.md>`_。
.. [BDL04_ZH] Gerd Behrmann, Alexandre David, Kim Guldstrand Larsen.
   ``A Tutorial on UPPAAL``。
   公开链接：`<https://dblp.org/rec/conf/sfm/BehrmannDL04>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/bdl04/README_zh.md>`_。
