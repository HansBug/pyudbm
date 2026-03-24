CDD 基础：共享图结构如何压缩非凸符号集合
===========================================

.. currentmodule:: pyudbm.binding.ucdd

这一页紧接着 :doc:`../federations/index_zh` 往前走一步。
联邦(federation)已经告诉我们：有限个有界差矩阵(DBM, difference bound matrix) 的精确并，足以表示非凸集合。
而 CDD 想继续解决的问题是：**当验证器手里已经有很多彼此相近的非凸片段时，能不能不要总把它们摊平成一长串显式 DBM，而是像共享决策图那样把公共结构压到一起。**

因此，这一页最自然的讲法不是先从联邦的工程压力说起，而是先把共享决策图的基本直觉讲清楚。CDD 借鉴的正是这条思路，只不过它处理的对象不再是纯布尔条件，而是时钟差约束 [UPP_VER_CDD_ZH]_ [BEHR03_CDD_PAGE_ZH]_ [UCDD_REPO_ZH]_。

这页会依次回答四件事：

* 先看布尔决策图(BDD, binary decision diagram)是怎样用共享图表示条件结构的
* 再看 CDD 如何把这套思路搬到时钟差约束上
* 然后说明为什么显式 DBM 列表在验证器里会逐渐变成瓶颈
* 最后落到当前 `UCDD` 与 :mod:`pyudbm.binding.ucdd` 真正提供了哪些能力，以及这些操作在时间自动机(timed automata)验证里各自有什么算法意义

从 BDD 到 CDD：为什么需要共享图
-------------------------------

BDD 的共享决策图直觉
~~~~~~~~~~~~~~~~~~~~

先从布尔决策图(BDD, binary decision diagram)开始，会更容易理解 CDD 借来的到底是哪一种结构思想。

BDD 最核心的想法很直接：**用一张可以共享后缀的有向无环图(DAG, directed acyclic graph)表示布尔函数，而不是把所有输入组合展开成一棵完全重复的判定树。**

如果一个布尔函数写成

.. math::

   f(a,b,c) = (a \land c) \lor (\neg a \land b \land c),

那么判定某个输入是否满足它时，你可以把过程理解成不断回答一串布尔问题：

* 先看 :math:`a` 是真还是假
* 再看 :math:`b` 或 :math:`c`
* 最后落到 ``True`` 或 ``False`` 终端

.. graphviz:: bdd_basics_zh.dot

这张图里最该注意的是蓝色的 ``c`` 节点。它被两条不同路径共同指向，这正是“决策图”而不是“决策树”的关键：

* 终端只有“真 / 假”两个
* 内部节点只测试布尔变量
* 如果两个分支后面剩下的判别结构完全一样，就可以共享同一段后缀，而不必复制两份

因此，对这一页来说，BDD 最值得先记住的是下面四件事：

* 它表示的是布尔函数
* 每个内部节点问的是“某个布尔变量是真是假”
* 两条边通常对应 ``0`` / ``1`` 或 ``False`` / ``True``
* 它是一张\ **共享图**\ ，不是一棵把所有后缀都重复展开的树

有了这层直觉，再来看 CDD 就自然了：

* BDD 的内部节点测试的是布尔变量
* CDD 的内部节点测试的是\ **某一对时钟的差值落在哪个区间里**
* BDD 的边标记是 ``0`` / ``1``
* CDD 的边标记则变成区间

也就是说，CDD 借用的是 BDD 的\ **有序决策、共享后缀、真/假终端、约简维护**\ 这套结构思想，只不过把判别对象从布尔变量换成了时钟差约束。

为什么在联邦之后还要继续引入 CDD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

现在有了上面这层 BDD 直觉，再回头看 CDD 的引入动机，就不会显得突然。

从 ``WAIT`` / ``PASSED`` 风格的可达性分析算法看，真正令人头疼的不是“单个约束区域能否表示”，而是
\ **同一个控制位置下，已经探索过的许多区域能否像 BDD 那样被整体压缩和整体查询**\。

这件事在现实里并不抽象。想象一个带超时、重传和条件分支的模型：

* 一次前向展开后，你得到一个区域
* 再走一轮重试边和时间流逝，又得到一个相邻但不完全相同的区域
* 再考虑不同离散条件，区域会继续分裂

如果这些结果都只是塞进一个显式列表，那么验证器后面反复做的事情就会变成：

* 把一个新区域逐个拿去和旧区域比包含关系
* 把大量“前半段不同、后半段很像”的结构重复存很多次
* 在 ``PASSED`` 越来越大时，为同一个控制位置维护越来越长的非凸区域列表

也就是说，问题已经不再是“数学上能不能表示”，而是“工程上这样表示会不会越来越笨重”。

Behrmann 这篇 CDD 论文把更宽松的停止条件写得很直接 [BEHR03_CDD_PAGE_ZH]_：

.. math::

   D \subseteq \bigcup \{\, D' \mid (l, D') \in \mathrm{PASSED} \,\}. \tag{1}

这里要逐个读：

* :math:`D` 是当前候选符号状态里的那个新区域
* ``PASSED`` 里不再只是一个个独立区域的“历史记录”，而是控制位置 :math:`l` 下已经探索过的整体覆盖
* 只要 :math:`D` 已经被整体覆盖，就没有必要再把它展开探索一遍

这条式子看起来只是把“某个旧区域覆盖新区域”改成了“许多旧区域的并覆盖新区域”，
但数据结构压力其实一下子就上来了。

显式联邦的写法是：

.. math::

   F = D_1 \cup D_2 \cup \cdots \cup D_n.

它在语义上完全正确，但如果非凸性越来越强，问题也会越来越具体：

* 需要维护的 DBM 数量可能迅速增加
* 不同 DBM 之间常常有可共享的后缀结构，但显式列表看不见这些共享
* 对算法来说，我们真正想问的经常不是“某个 DBM 是否等于另一个 DBM”，而是“一个新区域是否已包含在整个非凸集合里”

这正是 CDD 的切入点：**把 BDD 式的共享图直觉搬到时钟约束世界里，用共享有向无环图来表示有限个区域的并，而不是把这些区域永远摊平成一个显式 DBM 列表**
[BEHR03_CDD_PAGE_ZH]_ [UCDD_CDD_H_ZH]_。

.. graphviz:: explicit_vs_shared_zh.dot

这张图两边表示的是\ **同一个非凸集合**\ ，只是写法不同：

.. math::

   F = D_1 \cup D_2 \cup D_3 \cup D_4,

其中

.. math::

   \begin{aligned}
   D_1 &: 0 \leq x-y \leq 2,\; 0 \leq x \leq 1,\; 0 \leq y \leq 2, \\
   D_2 &: 0 \leq x-y \leq 2,\; 4 \leq x \leq 5,\; 0 \leq y \leq 2, \\
   D_3 &: 4 \leq x-y \leq 6,\; 0 \leq x \leq 1,\; 0 \leq y \leq 2, \\
   D_4 &: 4 \leq x-y \leq 6,\; 4 \leq x \leq 5,\; 0 \leq y \leq 2.
   \end{aligned}

左边把这个集合显式写成四个 DBM 的并；右边则把同一组约束改写成共享决策结构：

* 先看 :math:`x-y` 是否落在 ``[0,2]`` 或 ``[4,6]``
* 再看 :math:`x` 是否落在 ``[0,1]`` 或 ``[4,5]``
* 最后进入虚线框里的共享后缀，只检查一次 :math:`y \in [0,2]`

因此，这张图想强调的不再只是“右边有共享”这个口号，而是：
\ **对于同一个集合，显式联邦会把 :math:`y \in [0,2]` 这段后缀条件在四个 DBM 里各写一遍；CDD 则可以把这一段判别结构只保留一份，再让前面的不同分支共同指向它。**

从当前 Python 包装的角度看，这个动机并不是只停留在历史论文里。当前 :mod:`pyudbm.binding.ucdd`
已经直接暴露了 :meth:`CDD.from_federation`、:meth:`CDD.contains_dbm`、
:meth:`CDD.extract_dbm` 和 :meth:`CDD.extract_bdd_and_dbm`
这组桥接接口 [PYUDBM_UCDD_PY_ZH]_ [PYUDBM_UCDD_CPP_ZH]_。
这说明仓库已经在把“CDD 与 DBM / 联邦相互转换”当作真实工作流的一部分，而不是只把 CDD 当成论文注脚。

CDD 的定义：节点、区间与语义
----------------------------

论文里的 CDD 定义可以压缩成一句话：**它是一张有序、约简后的有向无环图；内部节点测试某个时钟差，边上标的是该时钟差允许落入的区间。**

先固定两样东西 [BEHR03_CDD_PAGE_ZH]_：

.. math::

   t = (i, j), \qquad 1 \leq i < j \leq n

表示一个\ **type**\ ，也就是“要观察哪一对时钟的差”；而对一个区间 :math:`I`，记

.. math::

   I(i, j)

为“时钟差 :math:`X_i - X_j` 落在区间 :math:`I` 内”的约束。

于是，一个内部节点不再像布尔决策图那样问“这个布尔变量是真是假”，而是问：
\ **当前赋值下，时钟差 :math:`X_i - X_j` 落在哪个区间里？**

论文给出的语义定义可以写成：

.. math::

   \llbracket False \rrbracket = \emptyset,
   \qquad
   \llbracket True \rrbracket = \mathcal{V},

.. math::

   \llbracket n \rrbracket
   =
   \{\, v \in \mathcal{V}
   \mid
   \exists I, m.\;
   n \xrightarrow{I} m
   \land I(type(n))(v)
   \land v \in \llbracket m \rrbracket
   \,\}.

也就是说，对一个赋值 :math:`v`，你从根节点一路往下走：

* 在每个节点先看对应时钟差的实际值
* 选择那个包含该值的区间边
* 如果最后到达 ``True``，这个赋值就属于当前 CDD 所表示的集合

这个定义和布尔决策图很像，但差别也正好在这里开始变得关键：
\ **不同时钟差之间并不独立。**

如果你已经知道

.. math::

   1 \leq X \leq 3
   \qquad\text{且}\qquad
   X = Y,

那么 :math:`Y` 的界实际上已经被间接约束住了。这也是论文特别强调的一点：CDD 不像普通约简布尔决策图那样，光靠固定变量顺序和共享就自然得到一个简单规范形 [BEHR03_CDD_PAGE_ZH]_。

因此，CDD 定义里除了“像决策图一样分支”之外，还有几条很重要的结构要求：

* 同一节点的后继区间必须两两不相交
* 这些区间要覆盖整个实数轴
* 图必须按 type 顺序排列
* 约简后图要做最大共享，且避免无意义的 ``R`` 全域边

论文后面又引入了 tightened 和 equally fine partitioned 这两层，用来逼近更强的正规形态。
其中最重要的结果是 [BEHR03_CDD_PAGE_ZH]_：

.. math::

   \llbracket C_1 \rrbracket = \llbracket C_2 \rrbracket
   \iff
   C_1 \cong C_2

不过这条等价需要额外前提：:math:`C_1` 和 :math:`C_2` 都得是 tightened 且 equally fine partitioned。
所以对教程来说，最重要的结论不是“CDD 天生有简单规范形”，而是：
\ **CDD 有很强的共享能力，但等价性和正规形态处理比普通约简布尔决策图更微妙。**

从论文里的连续 CDD，到当前 UCDD 的混合符号图
----------------------------------------------

如果只按 1999 年论文的主叙事来读，CDD 最容易被理解成：
\ **把一个控制位置下很多连续约束区域压成一张共享图。**
这个理解没有错，但放到当前仓库里的 `UCDD` 与 :mod:`pyudbm.binding.ucdd` 上，已经不够了。

真正的 UCDD 不是“纯连续层”和“纯布尔层”分开的两套对象，而是\ **把 BDD 层和时钟差层放进同一个运行时层级体系里，允许它们出现在同一张符号图中**\ [UCDD_CDD_H_ZH]_ [PYUDBM_UCDD_CPP_ZH]_ [PYUDBM_UCDD_PY_ZH]_。

`UCDD/include/cdd/cdd.h` 在总览注释里就把这件事说得很直白：

* 模块同时支持 ``BDD`` 节点和 ``CDD`` 节点
* 若只声明布尔变量，它就退化成一个 BDD 库
* 若同时声明布尔变量和时钟，则总层级数是 :math:`O(n^2 + m)`：
  时钟差层来自所有时钟对，布尔层来自布尔变量本身

头文件里的底层约定也完全对应这个说法：

* ``TYPE_CDD = 0``，``TYPE_BDD = 1``
* ``LevelInfo`` 里公开 ``type``、``clock1``、``clock2``、``diff``
* ``cdd_add_bddvar(n)`` 先向全局运行时加入布尔层
* ``cdd_add_clocks(n)`` 再加入时钟差层；由于考虑时钟差，所以层级规模是 :math:`O(c^2)`

.. graphviz:: runtime_layout_zh.dot

到了当前 Python 包装层，这种“混合图”不是隐含能力，而是直接暴露成了用户接口：

* :class:`CDDContext` 在一个对象里同时维护 ``base_context``、``clock_names``、``bool_names`` 和 ``dimension``
* ``_ensure_runtime_layout`` 会向原生运行时依次调用 ``add_clocks``、``add_bddvars``，并缓存 ``bool_levels``
* 每个 :class:`CDDBool` 都绑定一个原生 ``level``，其 :meth:`CDDBool.as_cdd` 最终会落到 :meth:`CDD.bddvar`
* 每个 :class:`CDDClock` / :class:`CDDVariableDifference` 仍然沿用 DBM 风格 DSL，把约束先转成区域，再送入 :meth:`CDD.from_federation`

这意味着真正进入 Python DSL 之后，布尔条件和连续区域不是“并排摆着的两个参数”，而是直接交织进同一个符号对象里。例如，先从 :class:`pyudbm.binding.udbm.Context`
通过 :meth:`pyudbm.binding.udbm.Context.to_cdd_context` 建一个混合上下文：

.. code-block:: python

   from pyudbm import Context

   base = Context(["x", "y"], name="c")
   ctx = base.to_cdd_context(bools=["door_open", "alarm"])

   state = ((ctx.x <= 5) & ctx.door_open) | ((ctx.y <= 2) & ~ctx.door_open)

这里的 ``state`` 不是“一个布尔公式 + 一个联邦”的松散配对，而是一张混合图。沿着一条根到终端的路径往下走时，你可能先经过布尔判定层，也可能经过时钟差层；最后这条路径共同定义出一个\ **布尔守卫 + 一个区域片段**\ 。

上面这个例子可以写成

.. math::

   state = \bigl(door\_open \land 0 \leq x \leq 5\bigr)
   \;\lor\;
   \bigl(\neg door\_open \land 0 \leq y \leq 2\bigr).

如果把它画成一张“布尔层 + 连续层”混合在一起的概念图，形状大致会像下面这样：

.. graphviz:: mixed_bool_zone_zh.dot

这张图不是在声称 UCDD 内部一定就按这一个节点布局存储，而是想把当前 :class:`CDD` 对象的\ **混合路径语义**\ 画出来：

* 根节点先判断布尔变量 ``door_open``
* 真分支继续检查时钟 :math:`x` 是否落在 ``[0,5]``
* 假分支继续检查时钟 :math:`y` 是否落在 ``[0,2]``
* 因而整张图同时携带了离散守卫和连续区域条件

对当前实现，更贴切的理解是：

.. math::

   state \equiv \bigvee_k \bigl(B_k \land D_k\bigr),

其中 :math:`B_k` 是某条路径抽出的布尔守卫，:math:`D_k` 是对应的 DBM 片段。这个式子不是论文里逐字给出的定义，而是\ **根据当前 :meth:`CDD.extract_bdd_and_dbm`、:class:`CDDExtraction` 和 :meth:`CDD.to_federation` 的行为，对现有实现做出的直接归纳**\：

* :meth:`CDD.extract_bdd_and_dbm` 会一次抽出 ``bdd_part``、``dbm`` 和 ``remainder``
* :class:`CDDExtraction` 在 Python 层把它们包装成高层对象
* :meth:`CDD.to_federation` 会反复抽取；一旦发现 ``bdd_part`` 不是 ``True``，就拒绝退回普通联邦

这三件事合起来，几乎已经把当前实现的工作模型写出来了：
\ **混合 CDD 可以表示很多“布尔守卫约束下的区域片段”；普通联邦只能承载其中布尔守卫已经退化为真值的那部分。**

因此，在真正的 UCDD 里，“zone 和 bool 同时存在”不是一句泛泛的口号，而是有非常具体的运行时布局和提取语义：

* 布尔变量占用 BDD levels
* 时钟差约束占用 CDD levels
* 二者共享同一个全局层级顺序和同一张决策图
* 一条路径最终会落成“守卫 + 区域片段”
* 前向 / 后向离散操作还能同时接收时钟重置和布尔重置

还有三个很值得先记住的现实边界：

* `UCDD` 的运行时(runtime)在当前实现里是\ **进程级全局对象**\ 。``ucdd.py`` 的 ``_ensure_runtime_layout`` 会强制新上下文复用兼容的时钟顺序与布尔前缀，否则直接报错。
* 布尔布局只能按前缀兼容方式增长；不是任意名字集合都能在同一个进程里随意拼起来。
* 原生 ``cdd_extract_dbm`` / ``cdd_extract_bdd`` / ``cdd_extract_bdd_and_dbm`` 都要求先做 ``reduce``。Python 包装把这个前置条件吸收进了高层方法里，因此 ``extract_*`` 调用前不需要用户自己手动记忆这个约束 [UCDD_CDD_H_ZH]_ [PYUDBM_UCDD_PY_ZH]_。

也正因为如此，对当前仓库来说，CDD 的意义已经不只是“为历史论文补背景”：

* 它给未来更完整的 Python-first 符号工作流提供了统一对象层
* 它让仓库的语义视角不至于只停在“DBM 显式联邦”这一层

带着这个实现视角，再看验证算法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

把 CDD 放回时间自动机的符号语义里，它其实是在接手三类任务。

第一类是\ **把许多区域的并收成一个对象**\ 。这对应刚才的公式 (1)，也对应论文里把 ``PASSED`` 的连续部分压成一个 CDD 的主叙事。

第二类是\ **继续支持和 DBM 一样的符号变换**\ 。对符号语义来说，最核心的两个操作本来就是 [UPP_SEM_CDD_ZH]_ [BY04_CDD_ZH]_ [BEHR03_CDD_PAGE_ZH]_：

.. math::

   D^\uparrow = \{\, u + d \mid u \in D,\ d \in \mathbb{R}_{\ge 0} \,\},

.. math::

   r(D) = \{\, [r \mapsto 0]u \mid u \in D \,\}.

也就是时间流逝和时钟重置。论文第 6 节明确说，若使用 tightened CDD，那么时间前进和重置可以沿着 DBM 风格的思路继续定义 [BEHR03_CDD_PAGE_ZH]_。

第三类是\ **在整个非凸对象上做包含、空性和布尔运算**\ 。论文第 4 节重点讨论的正是：

* 并、交、补
* 从约束系统或 DBM 生成 CDD
* 某个区域是否包含于某个 CDD

尤其是那种非对称查询：

.. math::

   subset(D, C)

其中左边是一个区域，右边是一个 CDD。对可达性分析来说，这恰好是最重要的场景之一：新来的单个区域，是否已经落在累计的 ``PASSED`` CDD 里面。

当前 API 与验证语义
--------------------

下面这张表只列当前绑定已经显式暴露、并且对符号化验证(symbolic verification)语义真正相关的那部分接口。

.. list-table::
   :header-rows: 1
   :widths: 21 18 24 37

   * - API
     - 类别
     - 验证里的意义
     - 说明
   * - :meth:`CDD.from_dbm` / :meth:`CDD.from_federation`
     - 桥接
     - 把现有区域 / 联邦送入 CDD
     - 方便把显式 DBM 工作流接到共享图表示上
   * - ``&`` / ``|`` / ``-`` / ``^`` / ``~``
     - 集合 / 布尔运算
     - 交、并、差、异或、补
     - 时钟约束和布尔守卫都可以放在同一张图里
   * - :meth:`CDD.reduce` / :meth:`CDD.reduce2` / :meth:`CDD.equiv`
     - 表示维护
     - 归约与等价检查
     - 提取和若干原生运算依赖 reduced 形态
   * - :meth:`CDD.contains_dbm`
     - 包含检查
     - 判断新区域是否已被累计 CDD 覆盖
     - 直接对应论文里最重要的非对称包含场景
   * - :meth:`CDD.extract_dbm` / :meth:`CDD.extract_bdd` / :meth:`CDD.extract_bdd_and_dbm`
     - 分解
     - 把共享图拆回布尔守卫 + 区域片段
     - 便于和现有 DBM / 联邦算法互操作
   * - :meth:`CDD.bdd_traces`
     - 布尔观察
     - 枚举当前布尔决策图部分的布尔赋值
     - 对调试混合符号状态很有用
   * - :meth:`CDD.delay` / :meth:`CDD.past` / :meth:`CDD.delay_invariant` / :meth:`CDD.predt`
     - 时间算子
     - 前向 / 后向时间闭包
     - 对应时间自动机里的时间前驱 / 后继
   * - :meth:`CDD.apply_reset` / :meth:`CDD.transition`
     - 前向离散边
     - 守卫求交后再做时钟 / 布尔更新
     - ``transition`` 是更接近边语义的高层入口
   * - :meth:`CDD.transition_back` / :meth:`CDD.transition_back_past`
     - 后向离散边
     - 反推一条边的前驱
     - 对后向可达性分析很直接
   * - :meth:`CDD.to_federation`
     - 回退到显式联邦
     - 仅适用于纯时钟 CDD
     - 如果还有非平凡布尔守卫，会显式拒绝转换

把几类核心操作放回验证任务里理解
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:meth:`CDD.contains_dbm`：问的不是“两个对象相不像”，而是“新来的区域用不用再展开”
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

对可达性分析而言，最值钱的问题之一就是：

.. math::

   D \subseteq F_{\mathrm{passed}} \; ?

也就是“当前候选区域 :math:`D` 是否已经被累计的已探索集合覆盖”。

这不是一个对称的相等检查，而是一个\ **新区域对旧 CDD**\ 的包含查询。论文第 4.2 节把它作为关键操作单独拿出来，
当前 Python API 则把这个问题落成了 :meth:`CDD.contains_dbm` [BEHR03_CDD_PAGE_ZH]_ [PYUDBM_UCDD_PY_ZH]_。

.. image:: contains_cover.plot.py.svg
   :width: 96%
   :align: center
   :alt: 三联图，分别展示 passed 集合、候选区域，以及候选区域被 passed 集合整体覆盖的关系。

图里右侧表达的正是“一个小区域已经完全包含在累计非凸集合里”，因此继续把它放回 ``WAIT`` 展开通常不会再带来新的时钟信息。

:meth:`CDD.reduce` 与 ``extract_*``：把共享图拆成“布尔守卫 + DBM 片段”
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

当前包装里，一个非常实用的视角是把混合 CDD 理解成：

.. math::

   C \equiv \bigvee_{k=1}^{m} \bigl(B_k \land D_k\bigr). \tag{2}

这不是论文里逐字给出的定义，而是\ **根据当前 :meth:`CDD.extract_bdd_and_dbm` 的行为，对现有实现做出的直接归纳**\：
每次提取都会拿出一个布尔部分 :math:`B_k` 和一个 DBM 片段 :math:`D_k`，反复执行直到 remainder 为空。

.. image:: mixed_extract.plot.py.svg
   :width: 96%
   :align: center
   :alt: 三联图，先展示一个混合 CDD 的两块受不同布尔守卫约束的几何片段，再分别展示两个提取出的 DBM 片段。

这件事在验证任务里有两个直接意义：

* 当你需要把混合符号状态交回现有 DBM / 联邦管线时，提取接口提供了一条明确桥梁。
* 当你想观察“离散条件到底是怎样把连续区域分片的”时，:meth:`CDD.bdd_traces` 和 :meth:`CDD.extract_bdd_and_dbm` 可以直接把图结构拆开看。

同时也要记住边界：如果一个 CDD 仍然带有非平凡布尔守卫，:meth:`CDD.to_federation` 会拒绝，因为普通联邦没法承载这层守卫。

:meth:`CDD.delay` 与 :meth:`CDD.delay_invariant`：时间流逝后的后继区域
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

时间自动机的前向时间语义本来就是

.. math::

   D^\uparrow = \{\, u + d \mid u \in D,\ d \in \mathbb{R}_{\ge 0} \,\}.

因此从验证任务视角看，:meth:`CDD.delay` 做的就是：
\ **在离散控制位置不变时，把当前符号状态沿时间方向向前推出去。**

而 :meth:`CDD.delay_invariant` 则是在此基础上再要求沿途保持不变量 :math:`I`。这很接近 UPPAAL 真正做 location-invariant 过滤时的语义形状。

.. image:: delay_reset.plot.py.svg
   :width: 96%
   :align: center
   :alt: 三联图，分别展示原始区域、时间前进后的区域，以及把 x 重置为 0 之后的结果。

图中中间面板的绿色区域说明：即使原始集合是一个有上下界的小矩形，时间流逝后也往往会变成更大的斜带区域。
这和单点仿真很不一样，因为它同时在推进\ **整批赋值**\ ，而不是推进一个具体状态。

:meth:`CDD.apply_reset` 与 :meth:`CDD.transition`：离散边不是“普通赋值”，而是符号状态变换
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

一条时间自动机边最核心的结构是：

.. math::

   \mathrm{Post}_e(S)
   =
   \mathrm{reset}\bigl(S \cap g\bigr),

其中 :math:`g` 是守卫，``reset`` 则把被重置的时钟设到指定值。当前 :meth:`CDD.transition`
正是把“先求交守卫，再做时钟 / 布尔更新”这件事封成了一个高层算子 [PYUDBM_UCDD_PY_ZH]_ [PYUDBM_UCDD_CPP_ZH]_。

对时间自动机验证来说，它的意义非常直接：

* ``guard`` 负责筛掉当前不能走这条边的赋值
* ``clock_resets`` 负责实现离散跳转上的时钟重置
* ``bool_resets`` 则把离散布尔条件一并更新

这也是当前混合 CDD 比“纯连续 CDD 只管 ``PASSED`` 压缩”的论文原始故事更进一步的地方：
**离散守卫和连续约束可以先在一张图里合流，再一起做一步 :meth:`CDD.transition`。**

:meth:`CDD.past`、:meth:`CDD.predt`、:meth:`CDD.transition_back`、:meth:`CDD.transition_back_past`：后向验证时最重要的一组算子
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

只做前向可达性分析当然是一条主线，但 UPPAAL 风格的验证工作流并不只需要前向算子。后向搜索、安全前驱(safe predecessor)、
以及某些不动点(fixpoint)风格算法都很依赖反向时间与反向迁移。

其中 :meth:`CDD.past` 最容易理解：它就是前向 :meth:`CDD.delay` 的后向版，给出“哪些更早的赋值经过纯时间流逝能到这里”。

:meth:`CDD.predt` 则可以这样理解：

.. math::

   \mathrm{PredT}(T, S)
   =
   \{\, u \mid \exists d \ge 0.\ u + d \in T
   \land \forall e \in [0, d].\ u + e \in S \,\}. \tag{3}

这个式子不是包装源码里逐字写出的定义；它是\ **根据 :meth:`CDD.predt` 的命名、UDBM/UCDD 测试以及它和 ``safe`` 区的组合方式，对当前实现所做的合理解释**\。
按这个理解，:meth:`CDD.predt` 问的是：哪些状态可以\ **沿着一直保持安全的时间演化**\ 最终进入目标集。

而 :meth:`CDD.transition_back` / :meth:`CDD.transition_back_past` 则把这种思路再推进一层：

* :meth:`CDD.transition_back` 反推一条离散边之前的前驱
* :meth:`CDD.transition_back_past` 还会把离散边之前允许的逆向时间流逝一起并进来

.. image:: backward_ops.plot.py.svg
   :width: 96%
   :align: center
   :alt: 三联图，分别展示后继状态、transition_back 得到的前驱，以及 transition_back_past 再加入后向时间闭包后的结果。

右侧面板比中间面板更大，正对应“先反推离散边，再把更早的时间前驱一并纳入”的语义。
这在后向可达性分析、最坏情况分析和某些控制 / 安全算法里都很常见。

这一页最该记住什么
------------------

如果这一页最后只记住七件事，那应该是：

* **联邦解决的是“能不能精确表示非凸集合”，CDD 进一步解决的是“能不能共享、压缩并整体查询这些非凸集合”。**
* **CDD 的基本判别单位不是单个布尔变量，而是某一对时钟的差值落在哪个区间里。**
* **CDD 很像 BDD，但不该想当然地把它当成天然具有简单规范形的约简布尔决策图。**
* **论文里最重要的场景是“一个新区域是否已包含在累计的 ``PASSED`` CDD 里”。**
* **当前 :mod:`pyudbm.binding.ucdd` 已经支持布尔 + 时钟的混合符号图，而不只是纯连续 CDD。**
* **:meth:`CDD.delay`、:meth:`CDD.apply_reset`、:meth:`CDD.predt`、:meth:`CDD.transition_back_past` 这些 API 都应该按时间自动机符号语义来理解，而不是当成孤立数据结构操作。**
* **如果一个 CDD 仍然带有非平凡布尔守卫，就不能直接退回普通联邦。**

下一步
~~~~~~

在 CDD 之后，最自然的下一批主题就是搜索、存储、外推(extrapolation)与终止机制：既然现在已经有了
约束区域、联邦和 CDD，这些符号对象究竟怎样进入真实的 ``WAIT`` / ``PASSED`` 算法循环，就成了下一层问题。

参考文献
~~~~~~~~

.. [UPP_VER_CDD_ZH] UPPAAL 官方图形界面文档，``Verifier``。
   公开链接：`<https://docs.uppaal.org/gui-reference/verifier/>`_。
.. [UPP_SEM_CDD_ZH] UPPAAL 官方文档，``Semantics``。
   公开链接：`<https://docs.uppaal.org/language-reference/system-description/semantics/>`_。
.. [BY04_CDD_ZH] Johan Bengtsson, Wang Yi.
   ``Timed Automata: Semantics, Algorithms and Tools``。
   公开链接：`<https://uppaal.org/texts/by-lncs04.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README_zh.md>`_。
.. [BEHR03_CDD_PAGE_ZH] Gerd Behrmann.
   ``Efficient Timed Reachability Analysis using Clock Difference Diagrams``。
   公开链接：`<https://www.brics.dk/RS/98/47/BRICS-RS-98-47.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/behrmann03/paper-c/README_zh.md>`_。
.. [UCDD_REPO_ZH] UPPAALModelChecker。
   ``UCDD``。
   公开链接：`<https://github.com/UPPAALModelChecker/UCDD>`_。
.. [UCDD_CDD_H_ZH] UPPAALModelChecker。
   ``UCDD/include/cdd/cdd.h``。
   公开链接：`<https://github.com/UPPAALModelChecker/UCDD/blob/master/include/cdd/cdd.h>`_。
.. [PYUDBM_UCDD_PY_ZH] HansBug。
   ``pyudbm/binding/ucdd.py``。
   公开链接：`<https://github.com/HansBug/pyudbm/blob/main/pyudbm/binding/ucdd.py>`_。
.. [PYUDBM_UCDD_CPP_ZH] HansBug。
   ``pyudbm/binding/_ucdd.cpp``。
   公开链接：`<https://github.com/HansBug/pyudbm/blob/main/pyudbm/binding/_ucdd.cpp>`_。
