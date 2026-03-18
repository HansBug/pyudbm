DBM 基础：矩阵如何表示约束区域
==============================

这一页回答的是紧接着
:doc:`../symbolic-states/index_zh`
之后的下一个问题：\ **如果 zone 是一批赋值的集合，为什么一个矩阵就能表示它？**

对 UPPAAL 风格的符号验证来说，答案非常具体：
\ **差分约束矩阵(DBM, difference bound matrix)**\ 保存的是各对时钟差值的上界。
而 timed automata 里的 guard / invariant 语言，恰好就是围绕这类约束组织起来的；因此 DBM 既足以精确表示
单个凸区域，又足以支撑 UDBM 实际暴露出来的那一整组符号操作 [UPP_VER_DBM_ZH]_ [BY04_DBM_ZH]_ [BENG02_DBM_ZH]_ [UDBM_REPO_ZH]_。

运行中的区域
------------

先看一个关于 ``x`` 和 ``y`` 的具体凸区域(zone)：

.. math::

   0 \leq y \leq 3,\qquad
   0 \leq x \leq 5,\qquad
   x - y \leq 2

这时它还只是一个几何对象：满足若干约束的赋值集合。

DBM 的关键一步，是把\ **零时钟(zero clock)**\ :math:`x_0` 加进来，并规定它永远等于 `0`。
这样一来，普通上下界也都能改写成差值约束：

* :math:`x \leq 5` 改写成 :math:`x - x_0 \leq 5`
* :math:`x \geq 0` 改写成 :math:`x_0 - x \leq 0`
* :math:`y \leq 3` 改写成 :math:`y - x_0 \leq 3`
* :math:`y \geq 0` 改写成 :math:`x_0 - y \leq 0`
* :math:`x - y \leq 2` 本来就是正确形状

一旦所有约束都变成“某个时钟减另一个时钟的值有上界”，矩阵就自然成为最合适的容器。

如果把时钟顺序固定成 :math:`(x_0, x, y)`，那么这个运行中例子对应的 DBM 可以直接写成：

.. math::

   D_{\text{zone}} =
   \left[
   \begin{array}{c|ccc}
        & x_0 & x & y \\
      \hline
      x_0 & (\leq, 0) & (\leq, 0) & (\leq, 0) \\
      x   & (\leq, 5) & (\leq, 0) & (\leq, 2) \\
      y   & (\leq, 3) & (\leq, 3) & (\leq, 0)
   \end{array}
   \right]

这里每个格子都还是同一种二元对写法。例如：

* 第二行第三列 :math:`(\leq, 2)` 表示 :math:`x - y \leq 2`
* 第三行第二列 :math:`(\leq, 3)` 表示 :math:`y - x \leq 3`
* 第二行第一列 :math:`(\leq, 5)` 表示 :math:`x - x_0 \leq 5`

核心编码思想
------------

对时钟 :math:`x_0, x_1, \ldots, x_n`，一个 DBM 会保存条目

.. math::

   D_{ij} = (\triangleleft_{ij}, c_{ij})

它的意思是，当前区域要求

.. math::

   x_i - x_j \triangleleft_{ij} c_{ij}

这里每个部分都要读清楚：

* :math:`\triangleleft_{ij}` 是 :math:`<` 或 :math:`\leq`
* :math:`c_{ij}` 是一个整数上界
* 所以这个二元组同时记录了“数值是多少”和“边界是否严格”

在教程层面，也可以先把 :math:`D_{ij}` 简单理解成：
\ **当前对 :math:`x_i - x_j` 这件事知道的最紧上界。**

用上面的运行中例子来读，最值得先盯住的三个条目是：

* :math:`D_{x,x_0} = (\leq, 5)`，表示 :math:`x - x_0 \leq 5`，也就是 :math:`x \leq 5`
* :math:`D_{x_0,y} = (\leq, 0)`，表示 :math:`x_0 - y \leq 0`，也就是 :math:`y \geq 0`
* :math:`D_{x,y} = (\leq, 2)`，表示 :math:`x - y \leq 2`

所以 DBM 不是“随便一个方阵”。它的每一行、每一列都对应一个时钟，而每个格子都在表达一个差值约束。

沿用上面的运行中例子，把它按矩阵完整展开，就是：

.. math::

   D_{\text{zone}} =
   \left[
   \begin{array}{c|ccc}
        & x_0 & x & y \\
      \hline
      x_0 & (\leq, 0) & (\leq, 0) & (\leq, 0) \\
      x   & (\leq, 5) & (\leq, 0) & (\leq, 2) \\
      y   & (\leq, 3) & (\leq, 3) & (\leq, 0)
   \end{array}
   \right]

也就是说，你看到的不是“一个数字表”，而是“按时钟索引组织起来的一组差值约束”。

UDBM 代码里一格到底存的是什么
------------------------------

在数学层面上，把 :math:`D_{ij}` 讲成二元组 :math:`(c_{ij}, \triangleleft_{ij})` 很方便。
但在 UDBM 的实际代码里，一个 DBM 单元格存的并不是显式 pair，而是一个 ``raw_t`` 类型的整数
[UDBM_CONSTRAINTS_ZH]_。

`constraints.h` 里的打包规则是：

.. math::

   \mathrm{raw} = 2 \cdot \mathrm{bound} \;|\; \mathrm{strictness}

其中：

* ``dbm_STRICT = 0`` 表示 :math:`<`
* ``dbm_WEAK = 1`` 表示 :math:`\leq`

也就是说，最低位负责存“严格还是非严格”，其余位用来存整数 bound。
两个非常小的例子就能把这件事讲死：

* ``dbm_bound2raw(5, dbm_STRICT) = 10``，编码的是 :math:`< 5`
* ``dbm_bound2raw(5, dbm_WEAK) = 11``，编码的是 :math:`\leq 5`

反向读取时，则用配套函数：

* ``dbm_raw2bound(raw)`` 去掉最低位，取回整数 bound
* ``dbm_rawIsStrict(raw)`` 判断编码出来的是不是 :math:`<`
* ``dbm_rawIsWeak(raw)`` 判断是不是 :math:`\leq`

这也正是为什么 UDBM 可以直接用整数运算做大量 DBM 操作，而不必在每个格子里维护一个显式 struct pair。
`dbm_raw.hpp` 里的轻量封装也是按这个视角写的：它提供 ``at``、``bound``、``is_strict``、``is_weak`` 这类读取接口
[UDBM_RAW_HPP_ZH]_。

真实矩阵里 ``inf`` 是常态，不是例外
-----------------------------------

真实的 DBM 里，并不是每个格子都装着一个小的有限整数。很多条目表达的是：
\ **当前根本没有有限上界。**

因此 UDBM 把 infinity 当成第一等编码情况来处理：

* ``dbm_INFINITY`` 是解码后的整数侧哨兵值
* ``dbm_LS_INFINITY`` 是 raw 侧用于表示 :math:`< \infty` 的特殊值

这里有个实现细节很重要。UDBM 并不把 :math:`\leq \infty` 当作普通 DBM 条目来用。
实际上，``dbm_weakRaw`` 还会显式拒绝把 infinity 变成 weak，因为库内部采用的规范形式就是 ``<INF``，
而不是 ``<=INF`` [UDBM_CONSTRAINTS_ZH]_。

所以一个真实 DBM 更常见的样子，其实更像下面这样，而不是前面那张全是有限数字的示意图：

.. math::

   D_{\text{init}} =
   \left[
   \begin{array}{c|ccc}
        & x_0 & x & y \\
      \hline
      x_0 & (\leq, 0) & (\leq, 0) & (\leq, 0) \\
      x   & (<, \infty) & (\leq, 0) & (<, \infty) \\
      y   & (<, \infty) & (<, \infty) & (\leq, 0)
   \end{array}
   \right]

这基本就是 ``CLOCKS_POSITIVE`` 打开时，``dbm_init`` 产生的初始矩阵形状：
第一行和对角线是 ``<= 0``，其余条目大量是 ``<INF`` [UDBM_DBM_H_CODE_ZH]_ [UDBM_DBM_C_CODE_ZH]_。

同样的特殊值在普通操作里也会一再出现：

* ``dbm_up`` 通过把 ``DBM(i, 0)`` 设成 ``dbm_LS_INFINITY`` 来移除上界
* ``dbm_freeClock`` 通过把被释放时钟那一行的大部分条目改成 infinity 风格值来忘掉信息
* 调整维度、外推(extrapolation)和紧凑存储相关代码也都会反复处理这个哨兵值

所以，如果一份 DBM 说明完全不谈 ``inf``，那它其实漏掉了 UDBM 实际行为里非常关键的一层。

为什么零时钟这么重要
--------------------

零时钟的作用，是把原本看起来分裂的两类约束强行统一。

如果没有 :math:`x_0 = 0`，你会同时面对两种语法世界：

* 普通边界，例如 :math:`x \leq 5`
* 时钟差边界，例如 :math:`x - y \leq 2`

引入零时钟以后，两者就都能写成同一种格式：

.. math::

   x \leq 5
   \iff
   x - x_0 \leq 5
   \qquad\qquad
   x \geq 1
   \iff
   x_0 - x \leq -1

这层统一性正是 DBM 好用的根源：

* 同一种存储格式同时覆盖下界、上界和时钟差
* 同一套算法就能更新它们
* 同一种图论视角就能解释闭包、空性和关系检查

图视角与规范闭包(canonical closure)
---------------------------------------------

每个 DBM 还可以被读成一张带权有向图：

* 顶点是各个时钟
* 边 :math:`i \to j` 保存当前对 :math:`x_i - x_j` 的上界

在这个视角下，做过\ **规范闭包**\ 的 DBM，指的是每个条目都已经收紧到“由所有路径共同推出的最紧上界”的那种形式。
这正对应于三角不等式条件：

.. math::

   D_{ij} \leq D_{ik} + D_{kj}
   \qquad
   \text{对所有 } i,j,k

这里只是把严格 / 非严格边界也一并按配对规则处理进去 [BY04_DBM_ZH]_ [BENG02_DBM_ZH]_。

.. graphviz:: dbm_closure_graph_zh.dot

图里的虚线边不是用户额外写进来的新约束，而是规范闭包把所有路径的最短推出关系都显式算出来之后得到的。

这也就是为什么规范闭包不是一个可有可无的“整理步骤”，而是核心不变量：

* 它会把不同写法但语义相同的 DBM 收敛到同一个规范形式
* 它让关系检查和更新操作都更容易讲清楚
* 它使得每个条目都能被当作真正可靠的最紧摘要，而不只是一个粗糙提示

结合 UDBM 源码怎么理解规范闭包
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

如果只看概念图，规范闭包很容易被误解成“把矩阵整理漂亮一点”。但 UDBM 的源码把它写得非常明确：
它就是\ **Floyd 最短路算法在 DBM 图上的直接实现**。

`dbm.h` 里对 ``dbm_close`` 的说明写得很直白：复杂度是三次方，算法就是对每个中介时钟 :math:`k`，
检查是否有

.. math::

   D_{ij} > D_{ik} + D_{kj}

如果有，就把 :math:`D_{ij}` 收紧成这个更小的值 [UDBM_DBM_H_CODE_ZH]_。

而在 `dbm.c` 里的 ``dbm_close`` 实现里，这件事几乎是一字不差地展开出来的：

* 最外层循环枚举中介点 ``k``
* 中间循环枚举行 ``i``
* 最内层循环枚举列 ``j``
* 只有当 ``dbm[i,k]`` 和 ``dbm[k,j]`` 都不是 ``dbm_LS_INFINITY`` 时，才真正尝试更新
* 如果 ``dbm[i,j]`` 比 ``dbm[i,k] + dbm[k,j]`` 更松，就把它收紧

这几点都很值得注意：

* 它不是“拍脑袋传播约束”，而是非常标准的最短路闭包
* 它会显式跳过 ``INF`` 路径，因为“没有有限上界”当然不能参与推出更紧有限约束
* 它不会无脑扫完再说，而是在每轮内部就检查对角线是否跌破 ``dbm_LE_ZERO``

最后这一点尤其重要。源码里如果发现 ``dbm[i,i] < dbm_LE_ZERO``，就会立刻返回空。
直觉上，这表示图已经推出了某种
:math:`x_i - x_i < 0`
式的矛盾，因此区域为空。

所以这里最该抓住的核心只有一条：
\ **规范闭包本质上就是基于类 Floyd 的最短路式传播，把所有间接可推出的更紧约束系统地收进矩阵。**

规范形式和最小约束集不是一回事
--------------------------------

这里特别容易混淆：

* **规范形式** 意味着所有最短路径推出的上界都已经显式写进去了
* **最小约束集** 意味着为了存储或压缩，把冗余约束删掉了

所以规范闭包往往会让矩阵\ **更密**\ ，而不是更小。这不是矛盾，而是两个目标本来就不同：
规范形式适合做精确符号操作；紧凑存储则是后面的另一层问题 [BY04_DBM_ZH]_ [BENG02_DBM_ZH]_。

举一个具体例子会更清楚。考虑两个普通时钟 :math:`x,y`，以及参考时钟
:math:`x_0 = 0`。假设我们想表示的 zone 其实只是这个简单长方形：

.. math::

   0 \leq x \leq 5,
   \qquad
   0 \leq y \leq 3

先看一种\ **非规范**\ 的写法。我们可能只显式写入这些约束：

* :math:`x - x_0 \leq 5`
* :math:`x_0 - x \leq 0`
* :math:`y - x_0 \leq 3`
* :math:`x_0 - y \leq 0`
* 甚至还额外写了一个偏松的约束 :math:`x - y \leq 10`

这时候矩阵已经描述了正确的区域，但它还不是规范形式：

* 由 :math:`x \leq 5` 和 :math:`y \geq 0`，其实可以推出更紧的
  :math:`x - y \leq 5`
* 原来显式写进去的 :math:`x - y \leq 10` 明显太松
* 由 :math:`y \leq 3` 和 :math:`x \geq 0`，还可以推出
  :math:`y - x \leq 3`
* 即使我们一开始根本没写 :math:`y - x` 那个条目，规范闭包之后它也会变成显式约束

如果把时钟顺序固定成 :math:`(x_0, x, y)`，并约定矩阵第 :math:`(i,j)` 个元素写成
:math:`(\triangleleft, c)`，表示约束
:math:`x_i - x_j \triangleleft c`，那么一个可能的\ **非规范起点**\ 可以写成

.. math::

   D_{\text{start}} =
   \left[
   \begin{array}{c|ccc}
        & x_0 & x & y \\
      \hline
      x_0 & (\leq, 0) & (\leq, 0) & (\leq, 0) \\
      x   & (\leq, 5) & (\leq, 0) & (\leq, 10) \\
      y   & (\leq, 3) & (<, \infty) & (\leq, 0)
   \end{array}
   \right]

这里最后一行第二列的 :math:`(<, \infty)` 表示我们一开始根本没有给出
:math:`y - x` 的有限上界；第二行第三列的 :math:`(\leq, 10)` 则是那个故意写得偏松的
:math:`x - y \leq 10`。

做完\ **规范闭包**\ 之后，这个 DBM 会变成“所有可推出最紧上界都已写明”的形式。对这个例子来说，关键差异是：

* :math:`x - y \leq 10` 会被收紧成 :math:`x - y \leq 5`
* 原本没显式给出的 :math:`y - x \leq 3` 也会被补出来
* 对角线和其他能由路径推出的最紧条目都会被统一收紧到规范内容

对这个矩阵做完\ **规范闭包**\ 之后，得到的规范形式会是

.. math::

   D_{\text{canon}} =
   \left[
   \begin{array}{c|ccc}
        & x_0 & x & y \\
      \hline
      x_0 & (\leq, 0) & (\leq, 0) & (\leq, 0) \\
      x   & (\leq, 5) & (\leq, 0) & (\leq, 5) \\
      y   & (\leq, 3) & (\leq, 3) & (\leq, 0)
   \end{array}
   \right]

这个矩阵里的每个条目都正好对应最紧可推出上界：

* :math:`D_{10} = (\leq, 5)` 表示 :math:`x - x_0 \leq 5`
* :math:`D_{01} = (\leq, 0)` 表示 :math:`x_0 - x \leq 0`，也就是 :math:`x \geq 0`
* :math:`D_{12} = (\leq, 5)` 表示 :math:`x - y \leq 5`
* :math:`D_{21} = (\leq, 3)` 表示 :math:`y - x \leq 3`

这个例子里所有最紧界都是非严格的，所以规范矩阵里的有限条目都带 ``\leq``。
如果原始 zone 中有严格约束，例如 :math:`x < 5` 或 :math:`x - y < 2`，那相应条目就会变成
:math:`(<, 5)` 或 :math:`(<, 2)` 这种形式。

但如果我们转而问：“\ **为了表示同一个 zone，最少需要保留哪些约束？**\ ”答案就不一样了。
这个例子里的\ **最小约束集**\ 完全可以只保留：

* :math:`0 \leq x \leq 5`
* :math:`0 \leq y \leq 3`

因为：

* :math:`x - y \leq 5` 虽然在规范形式里会显式出现，但它已经能由上面四个 box 约束推出
* :math:`y - x \leq 3` 也同样是可推导冗余项
* 那条原先写进去的 :math:`x - y \leq 10` 不但不是最小约束集的一部分，连规范形式里都不会保留原值

所以三者的关系可以概括成：

* **原始表示** 可能缺少某些可推出约束，也可能把某些条目写得过松
* **规范形式** 会把所有可推出的最紧约束都显式写出来，因此通常更完整、更密
* **最小约束集** 则会反过来删掉那些虽然可推出、但没必要单独存储的冗余约束，因此通常更稀疏

这也就是为什么“规范化”与“最小化”不是同一个方向的操作：
前者是在补全语义上的最紧信息，后者是在删去表示上的冗余信息。

DBM 上的核心操作
----------------

DBM 真正有价值的地方，不只是“它能存一个 zone”，而是：
\ **它正好支持验证器反复需要的那组符号操作。**

求交与加约束
~~~~~~~~~~~~

如果现在再加一个 guard，例如要求 :math:`y \geq 1`，那就等价于往矩阵里加入

.. math::

   x_0 - y \leq -1

这一步在 DBM 上的直观过程是：

* 先把对应条目收紧
* 再重新做 closure
* 让这个新约束对其他时钟差的影响一并传播出来

语义上，它就是把旧区域和新约束做求交。

在 UDBM 的 C API 里，这件事会直接落到 ``dbm_constrain``、``dbm_constrain1`` 这类函数上：
它们接收 raw 编码后的约束，先收紧受影响条目，再配合 closure 把影响传播完
[UDBM_DBM_H_CODE_ZH]_ [UDBM_DBM_C_CODE_ZH]_。

空性检查
~~~~~~~~

矛盾最终会在 closure 之后表现成“不可能的自环上界”。

例如，若同时要求 :math:`x \leq 1` 和 :math:`x \geq 3`，就等价于

.. math::

   x - x_0 \leq 1,
   \qquad
   x_0 - x \leq -3

两者合起来就会推出一个负对角约束。直觉上，这张图会在对角线上宣称
:math:`x - x < 0`，而这显然不可能。因此 DBM 的空性检查会变得很结构化、很便宜 [BY04_DBM_ZH]_。

时间后继：``up``
~~~~~~~~~~~~~~~~

未来操作(future) 让时间流逝，同时保留那些在“所有时钟一起增长”之后仍然有效的关系。

几何上可以写成：

.. math::

   \mathrm{up}(Z) = \{\, v + d \mid v \in Z,\; d \geq 0 \,\}

在 DBM 上，这会产生一个很有辨识度的效果：

* 像 :math:`x \leq 5` 这样的绝对上界可能会消失
* 像 :math:`x - y \leq 2` 这样的相对差值约束则仍可能保留下来

所以 ``up`` 不是“把所有约束都忘掉”，而是“只忘掉那些在统一时间流逝之后不再能维持的约束”。

这一点在 UDBM 实现里非常直接：``dbm_up`` 就是对每个非参考时钟执行
``DBM(i, 0) = dbm_LS_INFINITY``。代码层面的意思正是“把
:math:`x_i - x_0 \leq c` 这种上界删掉” [UDBM_DBM_C_CODE_ZH]_。

过去操作：``down``
~~~~~~~~~~~~~~~~~~

``down`` 则是在问：哪些更早的赋值，只要再等一段时间，就能进入当前区域？

几何上写成：

.. math::

   \mathrm{down}(Z) = \{\, v \mid \exists d \geq 0:\; v + d \in Z \,\}

如果说 ``up`` 是把区域往未来扩出去，那么 ``down`` 就是在向更早的赋值回溯。
它是 backward reasoning 和 predecessor 风格算法里很自然的对偶操作。

重置与更新
~~~~~~~~~~

时间自动机边上的 reset，在 DBM 里对应的是“按零时钟和其他时钟的关系，重写某个时钟的行和列”。

以最常见的 :math:`x := 0` 为例，新区域必须满足：

.. math::

   x - x_0 \leq 0
   \qquad\text{并且}\qquad
   x_0 - x \leq 0

与此同时，所有涉及 :math:`x` 的混合约束也都需要被一致地重算。

更一般的 :math:`x := c` 或 value-copy 风格更新，本质上都是同一路数：
先替换这个时钟和其他时钟的关系，再重新闭包。

而在 ``dbm.c`` 里，``dbm_updateValue`` 的写法也非常“DBM 本色”：
它先把 ``DBM(k, 0)`` 和 ``DBM(0, k)`` 设成关于 :math:`x_k = c` 的 weak 编码边界，
然后用 ``dbm_addFiniteRaw`` / ``dbm_addRawFinite`` 把整行整列重新算出来
[UDBM_DBM_C_CODE_ZH]_ [UDBM_CONSTRAINTS_ZH]_。

释放时钟
~~~~~~~~

有些算法步骤需要几乎彻底“忘掉”一个时钟。

这就是 ``free`` 或 ``freeClock`` 一类操作在做的事：

* 把这个时钟参与的大多数信息性约束去掉
* 只保留它和自己、和零时钟之间维持一致性的那些平凡关系

语义上，这是一种受控抽象：新的区域表达的是“只要剩下的约束还成立，这个被释放的时钟取什么都行”。

对应到代码，``dbm_freeClock`` 会把被释放时钟那一行的大部分条目改成 ``dbm_LS_INFINITY``，
而列方向则根据 ``CLOCKS_POSITIVE`` 的值决定是保留与零时钟一致的下界信息，还是一并放掉
[UDBM_DBM_C_CODE_ZH]_。

包含关系与相等性
~~~~~~~~~~~~~~~~

一旦 DBM 处于规范形式，矩阵级别的关系检查就有了明确语义。

如果一个规范形式的 DBM 的所有条目都比另一个更紧，那么它表示的区域就更小。这样就能支持：

* 区域包含关系检查
* 语义相等意义下的相等判断
* 基于规范内容而不是偶然写法的 hashing / sharing

点包含
~~~~~~

一个具体赋值是否落在某个 DBM 区域里，本质上就是问：
它是否满足 DBM 里保存的所有差值约束。

因此点包含在概念上很直接：

* 把这个赋值代入每个差值约束
* 检查所有不等式是否都成立

这正是 valuation membership 这类 API 背后的基本想法。

几个必须分清的性质
------------------

下面这些区分在实践里非常重要：

* **一个 DBM 只表示一个凸 zone。** 如果集合是非凸的，单个 DBM 就不够了。
* **严格 / 非严格边界是数据本身的一部分。** :math:`x < 5` 和 :math:`x \leq 5` 在 DBM 里不是同一个条目。
* **规范闭包不是文书整理。** 它决定了矩阵能否被当成语义可靠的规范对象。
* **规范形式不等于最省空间。** 压缩存储是后续独立主题。
* **normalization / extrapolation 不等于普通 closure。** closure 保持精确区域；外推是为了终止性而有意做的过近似。

为什么 UDBM 正好在这一层
------------------------

这正是 UDBM 最自然的层级位置。

UDBM 上游项目自己就把 DBM 描述成 clock constraints 的核心数据结构，并明确列出 ``up``、``down``、update、
extrapolation、DBM / federation 关系检查等操作 [UDBM_REPO_ZH]_。

因此，这个仓库当前的分层其实非常顺：

* timed automata 语义给出 zone 的需求
* DBM 给 zone 一个高效而精确的表示
* UDBM 在这个表示上实现基础操作
* `pyudbm` 则在其上恢复更自然的 Python 侧接口

这一页最该记住什么
------------------

如果这一页最后只记住五件事，那应该是：

* DBM 保存的是各对时钟差值 :math:`x_i - x_j` 的上界
* 零时钟让普通上下界和时钟差约束统一到同一种表示
* 规范闭包表示每个条目都已经被收紧到最紧推出上界
* DBM 的价值在于它支撑了核心符号操作，而不只是“存了一个 zone”
* 单个 DBM 仍然只表示一个凸 zone，因此下一页自然会走到 federation

下一步
------

下一篇最自然的内容是后续规划中的 ``federations/``：既然单个凸区域已经能被精确表示，那么下一步就是，
当减法或分支产生非凸符号集合时该怎么办。

.. [UPP_VER_DBM_ZH] UPPAAL 官方图形界面文档，``Verifier``。
   公开链接：`<https://docs.uppaal.org/gui-reference/verifier/>`_。
.. [UDBM_REPO_ZH] UPPAALModelChecker。
   ``UDBM: UPPAAL DBM Library``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM>`_。
.. [UDBM_CONSTRAINTS_ZH] UPPAALModelChecker。
   ``UDBM/include/dbm/constraints.h``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/constraints.h>`_。
.. [UDBM_RAW_HPP_ZH] UPPAALModelChecker。
   ``UDBM/include/dbm/dbm_raw.hpp``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/dbm_raw.hpp>`_。
.. [UDBM_DBM_H_CODE_ZH] UPPAALModelChecker。
   ``UDBM/include/dbm/dbm.h``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/include/dbm/dbm.h>`_。
.. [UDBM_DBM_C_CODE_ZH] UPPAALModelChecker。
   ``UDBM/src/dbm.c``。
   公开链接：`<https://github.com/UPPAALModelChecker/UDBM/blob/d83b703126fb88b3565c71cca68e360227dfb192/src/dbm.c>`_。
.. [BY04_DBM_ZH] Johan Bengtsson, Wang Yi.
   ``Timed Automata: Semantics, Algorithms and Tools``。
   公开链接：`<https://uppaal.org/texts/by-lncs04.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/by04/README_zh.md>`_。
.. [BENG02_DBM_ZH] Johan Bengtsson.
   ``Clocks, DBMs and States in Timed Systems``。
   公开链接：`<https://www.cmi.ac.in/~madhavan/courses/acts2010/bengtsson-thesis-full.pdf>`_。
   仓库阅读指南：`<https://github.com/HansBug/pyudbm/blob/main/papers/bengtsson02/README_zh.md>`_。
   内嵌论文导读：`<https://github.com/HansBug/pyudbm/blob/main/papers/bengtsson02/paper-a/README_zh.md>`_。
