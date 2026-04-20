搜索、外推与存储：为什么 UPPAAL 不只是“几种数据结构的堆叠”
==================================================================

.. currentmodule:: pyudbm.binding.udbm

这一页紧接着 :doc:`../cdd/index_zh` 往下走。
如果说前几页已经把\ **符号状态(symbolic state)、区域(zone)、差分约束矩阵(DBM)、联邦(federation) 与 CDD**\ 这些对象分别介绍清楚了，
那么这一页要回答的就是更偏工程、但同样核心的问题：
\ **这些对象在真实验证器里到底怎样被串成一条可执行的状态空间搜索流水线？**

换句话说，真正的 UPPAAL 风格引擎并不是“先随手挑一种表示，再把若干集合操作拼起来”。
它同时面临三种压力：

* \ **搜索压力**：符号后继要不断生成，``WAIT`` / ``PASSED`` 循环要持续跑下去
* \ **终止压力**：如果不做抽象，精确 zone graph 往往会无限增长
* \ **内存压力**：即使单个 DBM 操作够快，海量符号状态的保存、去重与包含检查仍然会吞掉大部分代价

因此，这一页会把下面五层明确连起来：

* 真实 reachability 主循环里，``WAIT`` 与 ``PASSED`` 到底在做什么
* 为什么“只做精确后继”通常不够，必须引入外推(extrapolation)
* 为什么后继计算(successor computation)的成本并不只来自集合运算本身
* 为什么最小约束、紧凑存储和早期包含检查会直接影响工具是否能跑完
* 这些想法在当前 `UDBM` / :mod:`pyudbm.binding.udbm` 里已经落到了哪些 API 和代码入口

从一条最小但真实的搜索主线开始
--------------------------------

前几页已经反复出现过一个基本对象：\ **符号状态**\ ，也就是“控制位置 + 一个约束区域”。
对 reachability 来说，真正不断循环的对象就是它，而不是孤立的 DBM 操作。

先把 WAIT 和 PASSED 说清楚
~~~~~~~~~~~~~~~~~~~~~~~~~~

很多读者第一次看搜索算法时，最容易卡住的其实不是 ``up``、``reset`` 或 DBM，
而是：\ **验证器手里到底维护了哪两堆状态，它们分别拿来干什么？**

先用最口语的方式说，可以把它理解成“待办清单 + 已处理记录”：

* ``WAIT``：已经发现、确认可达，但还没有展开后继的符号状态
* ``PASSED``：已经展开过，并且以后可以拿来挡掉重复探索的符号状态

再稍微精确一点说：

* ``WAIT`` 是当前搜索前沿(frontier)；它可以实现成栈、队列或别的工作表，但共同点都是“还没展开”
* ``PASSED`` 不是简单的“visited 节点集合”，而是一个\ **覆盖集(cover set)**\ ：它保存那些已经足以代表后续探索的符号状态

于是，最典型的搜索主循环其实就是：

1. 把初始符号状态放进 ``WAIT``。
2. 从 ``WAIT`` 里取出一个候选状态 :math:`(l, Z)`。
3. 如果同一控制位置下，``PASSED`` 里已经有状态能覆盖它，就直接跳过。
4. 否则把它加入 ``PASSED``，再生成它的后继并放回 ``WAIT``。
5. 一旦碰到目标位置，就得到“可达”。

下面这张图把这五步压成一张总流程图：节点里同时保留 :math:`S = (l, Z)`、:math:`Z \subseteq Z'`、
:math:`Post_e(S)` 这类符号，以及每一步到底在做什么的自然语言说明。

.. graphviz:: search_loop_overview_zh.dot

这里最容易误解的一点是：``PASSED`` 不是普通图搜索里那种“我来过这个节点一次”的打卡记录。
在 timed automata 的符号搜索里，一个状态不是单个节点 id，而是“位置 + 一整片时钟区域”。
所以 ``PASSED`` 真正承担的是覆盖作用：如果新来的 :math:`(l, Z)` 已经被某个更大的
:math:`(l, Z')` 包住了，那么再展开它，通常也不会带来新的可达信息。

把这两个角色先分清楚之后，后面的公式其实就只是在把这条主循环写精确。

如果这里只是把两条后继公式直接甩出来，读者很容易只记住“有个 ``up``、有个 ``reset``”，
却仍然不知道验证器到底在操作什么对象。所以先把最小但足够真实的一组记号摆平。

先把记号摆平
~~~~~~~~~~~~

设时钟集合为 :math:`C`，所有非负实值赋值构成的空间记作：

.. math::

   V = \mathbb{R}_{\ge 0}^{C}

一个符号状态写成：

.. math::

   S = (l, Z)

它代表的一批具体状态是：

.. math::

   \llbracket S \rrbracket
   =
   \left\{ (l, v) \mid v \in Z,\; v \models I(l) \right\}

这里每个符号都要逐个读：

* :math:`l` 是当前控制位置(location)
* :math:`v` 是一个具体时钟赋值(valuation)，会给每个时钟 :math:`x \in C` 指定一个非负实数 :math:`v(x)`
* :math:`Z` 是一个约束区域，也就是一批赋值的集合
* :math:`I(l)` 是位置 :math:`l` 的不变量(invariant)
* :math:`v \models I(l)` 表示赋值 :math:`v` 满足这个不变量
* :math:`\llbracket S \rrbracket` 表示符号状态 :math:`S` 所代表的全部具体带时间状态

时间流逝、守卫过滤和重置在集合层分别可以写成：

.. math::

   Z^{\uparrow}
   =
   \left\{ v + d \mid v \in Z,\; d \in \mathbb{R}_{\ge 0} \right\}

.. math::

   Z \cap g
   =
   \left\{ v \in Z \mid v \models g \right\}

.. math::

   reset_r(Z)
   =
   \left\{ v[r := 0] \mid v \in Z \right\}

其中：

.. math::

   (v + d)(x) = v(x) + d
   \qquad
   \text{对每个 } x \in C

.. math::

   v[r := 0](x)
   =
   \begin{cases}
      0, & x \in r \\
      v(x), & x \notin r
   \end{cases}

如果 ``WAIT`` 里保存的是对当前位置已经做过时间闭包的稳定符号状态(stable symbolic states)，
那么对一条边 :math:`e = (l, g, r, l')`，常见的前向后继写法可以压成：

.. math::

   \mathrm{Post}_{e}(l, Z)
   =
   \left(
      l',
      \left(reset_r(Z \cap g)\right)^{\uparrow} \cap I(l')
   \right)

这个式子正好把验证器里最重要的四个动作串在一起：

* 先用守卫 :math:`g` 过滤当前区域
* 再把 :math:`r` 里的时钟重置
* 然后让目标位置里的时间继续流逝
* 最后再用目标位置不变量 :math:`I(l')` 把结果截回合法区域

不同实现会把 ``up`` 放在边前还是边后，这取决于 ``WAIT`` 里到底保存“进入位置后立即的状态”还是“已经对该位置做过时间闭包的稳定状态”。
但无论工程分层怎么放，真正被重复组合的都是这几种集合操作。

一个真实的微型验证例子
~~~~~~~~~~~~~~~~~~~~~~

下面看一个只有一个时钟 :math:`x` 的极小自动机。它足够小，小到可以把每一步搜索都算出来；
但它又已经完整包含了守卫、重置、目标不变量和 ``WAIT`` / ``PASSED`` 的主循环。

.. graphviz:: verification_search_example_zh.dot

我们要问的性质是：

.. math::

   E \Diamond Goal

也就是“是否存在一条执行，最终到达位置 :math:`Goal`”。

这台自动机的三组位置不变量分别是：

.. math::

   I(L_0): x \le 5

.. math::

   I(L_1): x \le 3

.. math::

   I(Goal): x \le 1

两条边则是：

.. math::

   e_0 = (L_0,\; x \ge 2,\; \{x\},\; L_1)

.. math::

   e_1 = (L_1,\; x \ge 1,\; \{x\},\; Goal)

如果验证器把 ``WAIT`` 里的状态保存成稳定符号状态，那么初始位置上的第一个候选状态不是单点 :math:`x = 0`，
而是先对 :math:`L_0` 做过时间闭包后的：

.. math::

   Z_0 = \left\{ v \mid 0 \le v(x) \le 5 \right\}

.. math::

   S_0 = (L_0, Z_0)

这时候，沿着第一条边 :math:`e_0` 的后继会一步一步变成：

.. math::

   Z_0 \cap g_0
   =
   \left\{ v \mid 2 \le v(x) \le 5 \right\}

.. math::

   reset_{\{x\}}(Z_0 \cap g_0)
   =
   \left\{ v \mid v(x) = 0 \right\}

.. math::

   Z_1
   =
   \left(reset_{\{x\}}(Z_0 \cap g_0)\right)^{\uparrow} \cap I(L_1)
   =
   \left\{ v \mid 0 \le v(x) \le 3 \right\}

同样地，沿着第二条边 :math:`e_1`：

.. math::

   Z_1 \cap g_1
   =
   \left\{ v \mid 1 \le v(x) \le 3 \right\}

.. math::

   reset_{\{x\}}(Z_1 \cap g_1)
   =
   \left\{ v \mid v(x) = 0 \right\}

.. math::

   Z_2
   =
   \left(reset_{\{x\}}(Z_1 \cap g_1)\right)^{\uparrow} \cap I(Goal)
   =
   \left\{ v \mid 0 \le v(x) \le 1 \right\}

也就是说，验证器并不是在追踪某个单独时刻 :math:`x = 2` 或 :math:`x = 3.4`。
它在追踪的是：

* :math:`L_0` 中的整段可行时间窗口 :math:`0 \le x \le 5`
* 穿过第一条边后在 :math:`L_1` 中的整段窗口 :math:`0 \le x \le 3`
* 再穿过第二条边后在 :math:`Goal` 中的整段窗口 :math:`0 \le x \le 1`

下面这张图把这一串区域变化直接画成一维区间：

.. image:: worked_search_intervals.plot.py.svg
   :width: 98%
   :align: center
   :alt: 六联图，依次展示稳定初始区域、守卫过滤、重置、到达下一位置后的稳定区域、第二次守卫过滤与最终目标区域。

如果把主循环里的关键变量都显式写出来，并采用和上面总流程图一致的顺序
“取出 ``current`` :math:`\to` 先看目标 :math:`\to` 再看覆盖 :math:`\to` 再展开”，
同一件事可以写成下面这张更工程化的状态快照表。
这里用方括号表示当前 ``WAIT`` 工作表里的内容，不强调它到底实现成队列还是栈，只关心此时手上有哪些候选状态。

.. list-table::
   :header-rows: 1
   :widths: 10 18 21 21 18 32

   * - 轮次
     - 当前候选 ``current``
     - ``WAIT`` 快照
     - ``PASSED`` 快照
     - ``succ`` / ``result``
     - 备注
   * - 初始化
     - :math:`current = \bot`
     - 开始前：:math:`[]`
       稳定初始态入队后：:math:`[S_0]`
     - :math:`\emptyset`
     - :math:`succ = \emptyset`
     - 这里把 :math:`S_0 = (L_0, Z_0)` 看成已经对初始位置做过时间闭包后的稳定初始状态。
   * - 0
     - :math:`current = S_0 = (L_0, Z_0)`
     - 取出前：:math:`[S_0]`
       本轮结束后：:math:`[S_1]`
     - 本轮前：:math:`\emptyset`
       本轮后：:math:`\{S_0\}`
     - :math:`succ = \{S_1\}`
     - :math:`current` 不是目标，且还没有被覆盖，所以沿 :math:`e_0` 展开，得到 :math:`S_1 = (L_1, Z_1)`。
   * - 1
     - :math:`current = S_1 = (L_1, Z_1)`
     - 取出前：:math:`[S_1]`
       本轮结束后：:math:`[S_2]`
     - 本轮前：:math:`\{S_0\}`
       本轮后：:math:`\{S_0, S_1\}`
     - :math:`succ = \{S_2\}`
     - :math:`current` 仍然不是目标，也没有被覆盖，所以继续沿 :math:`e_1` 展开，得到 :math:`S_2 = (Goal, Z_2)`。
   * - 2
     - :math:`current = S_2 = (Goal, Z_2)`
     - 取出前：:math:`[S_2]`
       终止时：:math:`[]`
     - 本轮前：:math:`\{S_0, S_1\}`
       本轮后：:math:`\{S_0, S_1\}`
     - :math:`result = reachable`
     - 一取出就命中目标，所以这里直接终止；在这个写法里不会再继续做覆盖判断，也不会再生成新后继。

这一小段例子已经包含了真实验证里的三个关键事实：

* ``WAIT`` 里存的不是一个时刻，而是一个区域
* 单条边后继本质上是“守卫过滤 + 重置 + 时间闭包 + 目标不变量”
* 一旦某个候选状态到达目标位置，就可以终止这次 reachability 搜索

WAIT / PASSED 的覆盖判断到底在跳过什么
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Behrmann 的 thesis introduction 与 Bengtsson 的内存论文都把 reachability 主循环写得很直白：
维护两个集合 ``WAIT`` 和 ``PASSED``，不断从 ``WAIT`` 里取状态，如果它还没有被 ``PASSED`` 覆盖，就把它加入 ``PASSED`` 并生成后继
[BEHR03_INTRO_ZH]_ [BENG02_MEM_ZH]_。

把它压成一句数学化的判断，就是：

.. math::

   \text{skip } (l, Z)
   \quad \text{if} \quad
   \exists (l, Z') \in \mathrm{PASSED} : Z \subseteq Z'.

这个判断之所以成立，是因为在同一控制位置下：

.. math::

   Z \subseteq Z'
   \quad \Rightarrow \quad
   \llbracket (l, Z) \rrbracket \subseteq \llbracket (l, Z') \rrbracket

也就是说，``PASSED`` 里真正存的不是“访问过的原始节点 id”，而是\ **同一控制位置下，已经足以覆盖后续探索的符号集合代表**\。

.. graphviz:: forward_search_loop_zh.dot

这张图没有去画位置语义、trace 记录或具体容器实现，而是把搜索主线压成了最值得盯住的几个环节：

* ``WAIT`` 负责“可达但还没展开”
* ``PASSED`` 负责“已经展开过，并且足以做覆盖判断”
* 真正昂贵的部分不是“取状态”本身，而是后面的\ **离散后继、时间后继、规范化 / 外推、包含判断**
* 搜索循环真正不断复用的对象，是\ **带位置的区域**\ ，不是某个单独 DBM 原语

这也是为什么 :mod:`pyudbm.binding.udbm` 的高层 API 看起来会围绕这些动词组织：

* :meth:`Federation.up`
* :meth:`Federation.down`
* :meth:`Federation.predt`
* :meth:`Federation.contains`
* :meth:`Federation.extrapolate_max_bounds`
* :meth:`Federation.reduce`

它们不是零散 helper，而是在对应搜索流水线里的真实环节 [BY04_SEARCH_ZH]_ [UDBM_DBM_H_SEARCH_ZH]_ [UDBM_FED_H_SEARCH_ZH]_ [PYUDBM_UDBM_PY_SEARCH_ZH]_。

为什么“只做精确后继”通常不够
--------------------------------

把 reachability 写成上面的样子并不困难；真正困难的是：\ **如果每次都坚持保存完全精确的 zone 后继，这个图常常根本不会停。**

最经典的压力来自这样一种情形：

* 某个循环不断让一个时钟差增长
* 模型的真实行为只关心它是否超过某个常数，而不关心它之后到底是 ``3``、``30`` 还是 ``3000``
* 但如果我们仍然把这些值全部精确记住，就会得到一串不断向外扩张、彼此不同的符号状态

`bblp04` 的动机例子讲的正是这件事：对于 reachability 来说，只要时钟已经越过模型真正用到的最大常数，继续保留更精确的数值常常不会带来新的可观测行为，
却会让状态空间继续膨胀 [BBLP04_LU_ZH]_。

下面这张图把这种“精确族无限长、外推后塌缩”的直觉画成了最小玩具例子：

.. image:: exact_family_collapse.plot.py.svg
   :width: 98%
   :align: center
   :alt: 三联图，分别展示一串精确对角线区域、外推后得到的较大覆盖区域，以及一个新候选区域已被该覆盖区域包含。

左图里，每条细长的对角线片段都对应一个精确区域 :math:`Z_k`；
如果搜索一直沿着循环往前走，:math:`k` 可以继续增加，于是 ``WAIT`` / ``PASSED`` 里就会不断冒出新状态。

右边两幅图展示了外推真正做的事：

* 它\ **不是**\ 在说“这些区域本来就相等”
* 它是在说“对 reachability 而言，我们可以安全地把一整个精确族压成更粗的代表”
* 一旦 ``PASSED`` 里已经有了这个更粗的代表，后面落在它内部的新候选区域就可以直接跳过

对当前仓库来说，这一点不是抽象理论，而是当前实现就已经暴露的行为。上图里的绿色覆盖区域就是直接调用
:meth:`Federation.extrapolate_max_bounds` 算出来的，而不是手画出来的。

如果把当前 `UDBM/include/dbm/dbm.h` 里的 maximal-bound 外推想法压到最小，
最核心的规则其实只有两条 [UDBM_DBM_H_SEARCH_ZH]_：

.. math::

   c_{i,j} > M(x_i) \;\Longrightarrow\; c'_{i,j} = \infty

.. math::

   -c_{i,j} > M(x_j) \;\Longrightarrow\; c'_{i,j} = (-M(x_j), <)

直觉上可以这样读：

* 如果某个上界已经大到超出时钟 :math:`x_i` 的最大相关常数，就把它忘掉
* 如果某个下界已经低到超出时钟 :math:`x_j` 的最大相关常数，就把它截断到“只保留是否越界”这一层

这就是为什么外推不是普通的 closure。closure 维持\ **精确语义**\；而外推是为了\ **有限抽象与搜索终止**\，
有意识地把若干精确状态并到一起 [BY04_SEARCH_ZH]_ [BBLP04_LU_ZH]_。

这里还有一个很重要、但容易被忽略的现实边界：

* 当前 Python 高层 API 暴露了 :meth:`Federation.extrapolate_max_bounds`
* 上游原生 `dbm.h` / `fed.h` 里其实还同时有 diagonal maximal-bound、LU-bound 和 diagonal-LU-bound 变体

也就是说，\ **“外推”在 UDBM 里不是单一按钮，而是一整族针对精度 / 终止 / 代价折中的操作。**
当前 Python 层先恢复了历史兼容面里最核心的 maximal-bound 入口，但更宽的设计空间并没有消失
[BBLP04_LU_ZH]_ [UDBM_DBM_H_SEARCH_ZH]_ [UDBM_FED_H_SEARCH_ZH]_。

为什么后继计算本身也会变贵
--------------------------------

即使已经接受“需要外推”，问题也还没有结束。
真正的后继计算并不是只有一个 ``up()`` 或一个 ``&``，而是一串操作的组合。

`bblp04` 在分析 LU 外推时，把 UPPAAL 风格的一个后继计算拆成了下面六步 [BBLP04_LU_ZH]_：

1. 守卫相交并检查是否为空
2. reset 被重置的时钟
3. 做 delay / elapse
4. 再与目标不变量相交
5. 应用 extrapolation
6. 把 DBM 拉回 normal form

这六步里，最扎眼的不是集合运算本身，而是最后的 normal form / canonize。
如果直接用普通 Floyd-Warshall 风格 closure，它天然带着 :math:`O(n^3)` 的代价。

这也是 `bblp04` 真正重要的地方：它不是只说“LU 外推能让状态图更小”，还进一步说明：
\ **一旦外推把 DBM 变成 LU-form，后续 normalisation 的代价结构本身也会变化。**

.. image:: successor_costs.plot.py.svg
   :width: 92%
   :align: center
   :alt: 左右两幅柱状图，分别示意稠密 canonical 流水线与 LU-aware 流水线中各步骤的相对代价，其中 close 在前者里更突出。

这张图不是 benchmark，而是把 `bblp04` 的复杂度拆解画成一张\ **示意图**\：

* 左边表示普通稠密 canonical 流水线里，``close`` 往往是最重的阶段
* 右边表示一旦能利用 LU 结构，最后一步的压力会显著下降

论文里给出的 LU-aware 复杂度写法是 [BBLP04_LU_ZH]_：

.. math::

   O(|Low| \cdot |Up| \cdot |Low \cap Up|)

它和普通的 :math:`O(n^3)` closure 对比，真正强调的不是某个常数优化，而是：
\ **如果 lower-bounded clocks 和 upper-bounded clocks 的分布本来就稀疏，那么“规范化”这个步骤的有效工作集会比完整矩阵小很多。**

换句话说：

* 外推决定\ **状态图规模**
* LU-form 决定\ **后继计算成本形状**
* 这两件事在工程上是连着的，不该被拆成“理论正确性”和“后端优化”两张互不相干的皮

这也是为什么 thesis introduction 里会把 reachability checker 画成一串过滤器和缓冲区，而不是一个黑箱大循环
[BEHR03_INTRO_ZH]_：

.. graphviz:: engine_pipeline_zh.dot

这张图强调三件事：

* 工具里真正的 reachability checker 是\ **状态操作 + 状态空间表示**\ 的组合，而不是单个函数
* delay、normalisation、active clock reduction、trace storage 等步骤都可能是可替换组件
* 一旦你开始关心速度和内存，问题的核心就不再是“有没有 DBM”，而是“哪些步骤共享了什么结构、哪些步骤可以被绕开”

为什么 WAIT / PASSED 的表示形状会决定内存上限
------------------------------------------------

只让图有限还不够。对真实工具来说，更常见的崩点是：
\ **图虽然理论上有限，但 ``WAIT`` / ``PASSED`` 里的对象太大、太多，内存先撑爆了。**

`llpy97` 和 Bengtsson thesis 的 Paper C 从两个互补方向回答了这个问题：

* \ **局部压缩(local reduction)**：让每一个保存下来的符号状态更小
* \ **全局压缩(global reduction)**：让真正需要保存下来的符号状态更少

前者的核心结论是：闭包后的 canonical DBM 虽然适合做精确运算，但它通常并不是最省空间的保存形式。
很多约束只是三角不等式推出来的冗余边，可以删掉，只保留一组最小约束 [LLPY97_STORAGE_ZH]_。

后者的核心结论是：为了保证终止，并不一定非得把每一个探索过的符号状态都存进 ``PASSED``；
对动态循环(dynamic loop)来说，只保存足够覆盖这些循环的状态就已经够了 [LLPY97_STORAGE_ZH]_。

而 Bengtsson 的内存论文又把这个思路往前推了一步：
不仅 ``PASSED`` 要省，连 ``WAIT`` 里也应该尽早做包含判断，避免把明知迟早会被丢掉的候选状态白白塞进去
[BENG02_MEM_ZH]_。

这时候，单个符号状态在存储路径里的“外形”就很关键了：

.. graphviz:: storage_stack_zh.dot

这张图想表达的不是某个唯一实现，而是这一层真实的工程分工：

* 搜索时真正操作的是\ **闭包后的 DBM / 联邦**
* 为了节省空间，可以把它压成\ **最小约束 / minDBM**
* 再往下才是适合放进哈希表、缓存或 PWList 的紧凑编码
* Python 侧虽然不直接暴露完整 PWList，但已经能看到其中一部分边界，例如 :meth:`DBM.to_min_dbm`

当前仓库里，和这条存储线最直接对应的入口有：

* `UDBM/include/dbm/mingraph.h`：最小图 / minDBM C API
* `UDBM/src/mingraph_write.c`：最小约束分析与写出
* :meth:`DBM.to_min_dbm`：Python 侧拿到 packed minimal DBM words 的入口

它们和 :meth:`Federation.contains`、:math:`\le` 这类覆盖判断 API 放在一起看，才更容易理解：
\ **UDBM 不只是“会操作 DBM”，它也在为“怎样保存很多个符号状态”服务。**

下面这个小例子能把这层关系看得更具体：

.. code-block:: python

   from pyudbm import Context

   c = Context(["x", "y"])
   x = c.x
   y = c.y

   zone = ((x >= 0) & (x <= 2) & (y >= 0) & (y <= 2))
   dbm = zone.to_dbm_list()[0]
   packed = dbm.to_min_dbm()

   assert isinstance(packed, tuple)

这里的 ``packed`` 并不是“另一种语义对象”，而是\ **同一个 zone 的更紧凑存储形态**\。
如果后续要做哈希、缓存、压缩保存或 passed-list 级别的状态管理，这种形态通常比完整闭包矩阵更合适
[LLPY97_STORAGE_ZH]_ [UDBM_MINGRAPH_H_ZH]_ [UDBM_MINGRAPH_WRITE_ZH]_ [PYUDBM_UDBM_PY_SEARCH_ZH]_。

当前 `pyudbm` / `UDBM` 里已经能看到什么
---------------------------------------

为了避免这一页只停在论文叙事，下面把“搜索 / 外推 / 存储”这一页最相关的代码入口一次对齐，
同时明确对到当前 Python 包装层、原生绑定层和公开测试 [PYUDBM_UDBM_PY_SEARCH_ZH]_
[PYUDBM_UDBM_CPP_SEARCH_ZH]_ [PYUDBM_TEST_UDBM_ZH]_。

.. list-table::
   :header-rows: 1
   :widths: 18 20 20 42

   * - 主题
     - 当前 Python 入口
     - 当前原生入口
     - 为什么它重要
   * - 时间后继
     - :meth:`Federation.up`
     - ``dbm_up`` / ``fed_t::up``
     - 对应 delay successor，是 reachability 主循环的基本动作。
   * - 时间前驱
     - :meth:`Federation.down`、:meth:`Federation.predt`
     - ``dbm_down`` / ``fed_t::predt``
     - 对应 backward-style 分析与“避开 bad 的前驱”计算。
   * - 覆盖 / 包含判断
     - :meth:`Federation.contains`、:math:`\le`、:math:`\ge`
     - ``fed_t::contains``、relation / inclusion checks
     - 决定 ``PASSED`` 是否足以挡住一个新候选状态。
   * - 最大常数外推
     - :meth:`Federation.extrapolate_max_bounds`
     - ``dbm_extrapolateMaxBounds`` / ``fed_t::extrapolateMaxBounds``
     - 决定精确 zone graph 如何塌缩成有限抽象。
   * - LU / diagonal 外推
     - 当前高层暂未直接公开
     - ``dbm_extrapolateLUBounds``、``dbm_diagonalExtrapolateLUBounds``
     - 说明上游本来就把外推看成一族操作，而不是单个“优化开关”。
   * - 表示维护
     - :meth:`Federation.reduce`、:meth:`Federation.intern`
     - ``fed_t::mergeReduce``、``fed_t::intern``
     - 几何语义不变，但内部表示可更紧，适合长期保存。
   * - 最小约束导出
     - :meth:`DBM.to_min_dbm`
     - ``dbm_analyzeForMinDBM``、``dbm_writeToMinDBMWithOffset``
     - 对应单个符号状态的局部压缩，是存储层而不是语义层能力。

从这个表可以看出当前仓库的一个很明确的现实状态：

* 和 reachability 主循环最接近的\ **基础语义动作**\ 已经不少
* 但\ **真正的引擎级组合件**\ 还没有在 Python 层变成一等对象
* 也就是说，仓库已经不只是“几个低层 DBM helper”，但离完整的 Python-first verification workflow 还有一段距离

这恰好解释了为什么这篇必须存在。
如果没有它，读者很容易把前几页理解成“先学几个表示法，再各自记一点 API”；
而真正的 UPPAAL 视角恰恰是相反的：\ **这些表示法存在的意义，就是为了让搜索循环在正确性、终止性和内存压力之间达成可运行的平衡。**

这和 UPPAAL / Python 重建方向有什么关系
-----------------------------------------

对这个仓库来说，这一页有三个直接后果。

第一，未来的 Python-first API 不应该只暴露“能操作一个 DBM 的函数”，而应该逐步把\ **符号搜索工作流**\ 里的关键对象抬出来。
哪怕一开始不把完整验证器搬到 Python，也至少要让用户能够自然组合：

* 后继计算
* 覆盖判断
* 外推策略
* 表示维护
* 状态快照 / 压缩导出

第二，外推与存储不该被误解成“后端优化细节”。
从 `bblp04` 到 `llpy97` 再到 `bengtsson02`，它们讨论的都不是可有可无的加速小技巧，而是\ **状态空间何时有限、单步成本有多高、总内存能否承受**\ 这三个根问题
[BBLP04_LU_ZH]_ [LLPY97_STORAGE_ZH]_ [BENG02_MEM_ZH]_。

第三，`pyudbm` 当前已经有足够多的入口，可以把这条工程主线重新搭起来。
例如只靠现有公开面，就已经能向用户解释：

* 为什么 :meth:`Federation.up` / :meth:`Federation.down` 是核心操作
* 为什么 :meth:`Federation.extrapolate_max_bounds` 会决定搜索是否收敛
* 为什么 :meth:`DBM.to_min_dbm` 代表的是状态保存层，而不是另一种语义层

也就是说，\ **恢复历史绑定并不是终点；把这些对象重新放回一条真实的 symbolic verification story 里，才是这条路线真正的中段。**

延伸阅读与参考文献
------------------

如果你要继续顺着这条线往下读，最自然的后续主题是：

* reduction 相关主题：当问题从“如何保存状态”转向“如何少生成无谓交错”时
* priced timed automata 相关主题：当问题从“能否到达”转向“怎样最优到达”时

对这一页本身来说，最值得配套阅读的本地 guide 是：

* `papers/by04/README_zh.md`
* `papers/bblp04/README_zh.md`
* `papers/llpy97/README_zh.md`
* `papers/bengtsson02/paper-c/README_zh.md`
* `papers/behrmann03/paper-intro/README_zh.md`

参考文献
~~~~~~~~

.. [BY04_SEARCH_ZH] Johan Bengtsson, Wang Yi.
   ``Timed Automata: Semantics, Algorithms and Tools``。
   公开链接：`<https://uppaal.org/texts/by-lncs04.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README_zh.md>`_。
.. [BBLP04_LU_ZH] Gerd Behrmann, Patricia Bouyer, Kim G. Larsen, Radek Pelánek。
   ``Lower and Upper Bounds in Zone Based Abstractions of Timed Automata``。
   公开链接：`<https://www.researchgate.net/profile/Radek-Pelanek/publication/221224338_Lower_and_Upper_Bounds_in_Zone-Based_Abstractions_of_Timed_Automata/links/0912f50be648eae2d0000000/Lower-and-Upper-Bounds-in-Zone-Based-Abstractions-of-Timed-Automata.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/bblp04/README_zh.md>`_。
.. [LLPY97_STORAGE_ZH] Kim G. Larsen, Fredrik Larsson, Paul Pettersson, Wang Yi。
   ``Efficient Verification of Real-Time Systems: Compact Data Structure and State-Space Reduction``。
   公开链接：`<https://web.archive.org/web/20240919204934if_/https://www2.it.uu.se/research/group/darts/papers/texts/llpw-rtss97.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/llpy97/README_zh.md>`_。
.. [BENG02_MEM_ZH] Johan Bengtsson, Wang Yi。
   ``Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems``。
   公开链接：`<https://github.com/HansBug/pyudbm/blob/main/papers/bengtsson02/paper-c/paper.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/bengtsson02/paper-c/README_zh.md>`_。
.. [BEHR03_INTRO_ZH] Gerd Behrmann。
   ``Data Structures and Algorithms for the Analysis of Real Time Systems``，introduction 部分。
   公开链接：`<https://github.com/HansBug/pyudbm/blob/main/papers/behrmann03/paper-intro/paper.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/behrmann03/paper-intro/README_zh.md>`_。
.. [UDBM_DBM_H_SEARCH_ZH] UPPAALModelChecker。
   ``UDBM/include/dbm/dbm.h``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/dbm.h>`_。
.. [UDBM_FED_H_SEARCH_ZH] UPPAALModelChecker。
   ``UDBM/include/dbm/fed.h``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/fed.h>`_。
.. [UDBM_MINGRAPH_H_ZH] UPPAALModelChecker。
   ``UDBM/include/dbm/mingraph.h``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/mingraph.h>`_。
.. [UDBM_MINGRAPH_WRITE_ZH] UPPAALModelChecker。
   ``UDBM/src/mingraph_write.c``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/src/mingraph_write.c>`_。
.. [PYUDBM_UDBM_PY_SEARCH_ZH] HansBug。
   ``pyudbm/binding/udbm.py``。
   公开链接：`<https://github.com/HansBug/pyudbm/blob/main/pyudbm/binding/udbm.py>`_。
.. [PYUDBM_UDBM_CPP_SEARCH_ZH] HansBug。
   ``pyudbm/binding/_udbm.cpp``。
   公开链接：`<https://github.com/HansBug/pyudbm/blob/main/pyudbm/binding/_udbm.cpp>`_。
.. [PYUDBM_TEST_UDBM_ZH] HansBug。
   ``test/binding/test_udbm.py``。
   公开链接：`<https://github.com/HansBug/pyudbm/blob/main/test/binding/test_udbm.py>`_。
