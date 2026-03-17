# UPPAAL 教程规划笔记

## 目的

这份文档用于记录未来 `docs/` 下双语 UPPAAL 理论 / 教程部分的写作规划。

这里的目标不是只把 `UDBM` 单独讲清楚，而是把更完整的 UPPAAL 技术栈逐步在 Python 侧重建出来，而 `UDBM` 只是其中一个非常核心、但并不等于全部的基础层。

因此，这份规划把下面这些内容都视为一等主题：

- timed automata 及其语义
- 验证性质与查询直觉
- symbolic state、zone 和 DBM
- federation 与非凸符号集合
- CDD 作为另一类符号表示
- 核心搜索算法与终止机制
- 存储、压缩、passed / waiting 等工程问题
- reduction 技术与面向建模的优化
- priced timed automata 与最优代价可达性
- 最终如何映射到 Python 侧的 UPPAAL 风格 API

## 规划原则

### 1. 不按论文顺序写

`papers/` 是素材库，不应该直接成为面向读者的教程结构。

对初学者更合适的顺序应该是学习曲线顺序，而不是引文顺序：

1. UPPAAL 在解决什么问题
2. 它用什么模型描述系统
3. 用户通常在问什么性质
4. 为什么需要 symbolic states
5. symbolic representation 有哪些
6. 验证引擎是怎么跑起来的
7. 为什么后面还会出现各种优化和扩展

这比把每篇论文写成一篇读书笔记更适合公开教程。

### 2. 写法要尽量亲民

目标读者应包括之前并不熟悉 timed automata 和 formal verification 的人。

因此写法上要坚持：

- 先讲问题和例子，再讲形式定义
- 可以有公式，但不能被公式淹没
- 每次上公式之前先用人话解释
- 尽量尽早引入一到两个 running example，并在后文反复复用
- 不要只给抽象定义；每个核心概念都尽量给出一个足够具体、能把事情讲明白的直观例子
- 同一个概念最好同时准备“玩具例子”和“接近真实建模的例子”两种尺度
- 读者第一次看到新术语时，优先先看到例子里的行为，再看到术语定义
- 多使用几何直觉图、执行过程图、状态空间图
- 证明味道太重的内容放到读者已经有直觉之后再讲

这里要避免一个误区：

- 并不是每个例子都必须是“最小可运行示例”
- 对很多理论概念来说，更重要的是例子是否具体、是否把语义和直觉讲清楚
- 只要能让读者真正看到对象、约束、状态变化或几何关系，这个例子就是合格的

### 3. 每篇都要兼顾直觉、图和少量数学

每一页比较合适的默认配置是：

- 1 张主图
- 必要时再加 1 张补图
- 2 到 4 个关键公式
- 1 个贯穿整页的小例子
- 再补 1 到 2 个局部小例子，用来拆开最容易误解的点
- 结尾有一小节解释“这和 UPPAAL / Python 重建方向有什么关系”

文档不能变成纯公式，也不能变成只有口头描述的科普稿。

这里要特别强调：

- 例子不是点缀，而是正文主体的一部分
- 对 timed automata、query、zone、DBM、federation 这类主题，最好都能给出具体约束或具体状态空间片段
- 如果一段解释里连续几段都没有例子、图或具体对象，通常说明这一段已经开始“飘”
- 允许使用公式，尤其是关键定义、核心不变量、关键语义规则和最重要的表示式
- 但公式绝不能裸放；每一个公式都必须紧跟详细解读和直观说明

### 4. 要明确把 UPPAAL 看作大于 UDBM 的整体

如果只从 UDBM 出发，视角会过窄，不足以支撑当前项目目标。

`UDBM` 很重要，但并不够。更完整的 UPPAAL 教程规划必须显式覆盖：

- query / property 视角
- 引擎整体架构
- federation 层面的语义对象
- CDD 这类替代性 symbolic representation
- passed / waiting 以及状态存储压力
- extrapolation 与 normalization
- partial-order 与建模相关的 reduction
- priced symbolic structure 与 optimality

### 5. 双语结构要显式成对

仓库当前文档已经有比较明确的中英配对结构，例如：

- `docs/source/index_en.rst`
- `docs/source/index_zh.rst`
- `docs/source/tutorials/installation/index.rst`
- `docs/source/tutorials/installation/index_zh.rst`

未来的 theory / tutorial 部分也应该继续采用这种成对页面结构，而不是把中英混写在同一页。

### 6. 不直接把这组内容塞进 `tutorials/`

`docs/source/tutorials/` 更适合作为安装、快速开始、面向任务的线性教程区。

而这份规划里的内容，本质上更像是围绕 UPPAAL 核心概念展开的“概念基础库”，读者往往会按自己的知识缺口跳着读，而不是从头到尾顺着读完。

因此更合适的做法是：

- 保留 `tutorials/` 作为操作型教程入口
- 另开一个与 `tutorials/` 同级的路径来承载概念型内容
- 每个主题单独占一个子目录，目录内只保留中英两个入口页和资源文件
- 在入口页里做阅读分流，而不是只给一棵平铺目录树

这也意味着：`mds/UPPAAL_TUTORIALS.md` 对应的未来内容，不应被简单理解为“再往 `tutorials/` 下堆一串 rst 页面”。

### 7. 顶层首页也要直接列出每一篇内容

除了在 `foundations/` 内部组织主题页之外，仓库根级的双语首页也应该直接把这些概念页列出来，而不只是挂一个总入口。

也就是说，在：

- `docs/source/index_en.rst`
- `docs/source/index_zh.rst`

里，后续每新增一篇概念页，都应直接加入对应语言首页的“Concept Foundations / 概念基础”部分，与入口导读处于同一级别。

这样做的目的有两个：

- 让读者在最顶层首页就能看到当前已经写了哪些主题，而不是必须先点进二级入口
- 避免 `foundations/` 退化成一个“真正内容都藏在里面”的黑箱目录

### 8. 入口导读本身也是一个同级主题页

“入口导读”应该被视为 `foundations/` 下的一个普通主题页，而不是所有主题的上位正文页。

更合适的结构是：

- `foundations/reading-guide/index.rst` / `index_zh.rst` 承担入口导读职责
- `foundations/what-is-uppaal/index.rst` / `index_zh.rst` 与 `reading-guide/` 平级

后续其他主题也应继续遵守这个规则，而不是重新把“导读页”写成所有页面的正文上位页。

这里进一步明确：

- `foundations/index*.rst` 这类“本地区域索引页”没有必要保留
- 顶层首页应直接列出 `reading-guide/` 与所有已完成主题页
- `reading-guide/` 负责分流，但不是 `what-is-uppaal/` 等正文页的父页面

## 素材来源与主要依托

这份教程规划主要建立在两类材料上。

第一类是本地 paper guide：

- `papers/ad90/README.md`
- `papers/by04/README.md`
- `papers/dhlp06/README.md`
- `papers/bblp04/README.md`
- `papers/lpw95/README.md`
- `papers/lpy97/README.md`
- `papers/bdl04/README.md`
- `papers/llpy97/README.md`
- `papers/bengtsson02/README.md`
- `papers/behrmann03/README.md`
- `papers/behrmann03/paper-intro/README.md`

第二类是官方 UPPAAL 材料，尤其适合用来写工具定位、工作流、GUI / simulator / verifier 行为这类页面：

- `https://uppaal.org/`
- `https://uppaal.org/features/`
- `https://docs.uppaal.org/`
- `https://docs.uppaal.org/gui-reference/...`
- `https://docs.uppaal.org/language-reference/...`

粗略地说：

- `ad90` 和 `by04` 提供 timed automata 与 symbolic semantics 的基础主线
- `dhlp06` 解释 federation、减法和非凸性
- `bblp04` 解释 extrapolation、抽象和终止
- `llpy97` 与 `bengtsson02` 解释存储、压缩和引擎成本压力
- `lpy97` 与 `bdl04` 提供工具视角与建模视角
- `behrmann03` 把视角扩展到 CDD、系统架构和 priced symbolic structures

实际写作时应注意：

- 讲理论骨架时，paper guide 往往更系统
- 讲“官方工具到底怎么描述自己、有哪些组成部分、GUI / simulator / verifier 怎么配合”时，官方网站和官方文档优先级更高

## 总体策略：操作教程 + 概念基础页 + 进阶专题

更合适的公开结构不是把所有内容揉成一条长长的教程线，而是拆成三层：

- `tutorials/`：安装、快速开始、面向任务的操作教程
- `foundations/`：面向概念理解的基础页与主题页
- 进阶专题：在 `foundations/` 体系内逐步覆盖实现层、算法层和 Python 重建路径

其中 `foundations/` 这个名字只是当前建议，用意是强调“概念地基”而不是“按任务操作”。这个目录和 `tutorials/` 同级，负责承接 timed automata、query、zone、DBM、federation、CDD、搜索、priced extension 等主题。

这样拆开以后：

- 初学者可以先走 `tutorials/` 的安装与使用入口，再按不熟悉的概念跳到 `foundations/`
- 读者不会把理论内容误解成必须线性读完的长教程
- 每个概念页可以自己带图、例子、资源，而不必挤在一大堆并列 rst 文件里
- 入口页也更容易做“你现在应该读哪里”的分流

## 主线篇规划

主线篇面向第一次接触 timed automata / model checking 的读者。

### 1. UPPAAL 在解决什么问题

建议重点：

- 什么是形式化验证
- 它和测试、仿真的区别是什么
- 为什么带时间约束的并发系统更难处理
- UPPAAL 的整体结构：模型、性质、symbolic engine、输出结果

主要素材来源：

- `papers/lpy97/README.md`
- `papers/bdl04/README.md`
- `papers/behrmann03/paper-intro/README.md`

建议配图：

- 一张从建模到 symbolic exploration 再到 counterexample / answer 的总流程图

公式密度：

- 尽量低，这一篇主要负责建立世界观

### 2. Timed Automata：系统如何随着时间演化

建议重点：

- location、clock、guard、reset、invariant
- 时间流逝迁移和离散迁移
- valuation 为什么是状态的一部分
- 一个小型请求-响应或超时重传例子

主要素材来源：

- `papers/ad90/README.md`
- `papers/by04/README.md`

建议配图：

- 一张小型 timed automaton
- 一张展示时间流逝和离散跳转的示意图

公式密度：

- 只保留最基本的语义规则

### 3. UPPAAL 一般在验证什么性质

建议重点：

- reachability 和 safety 的直觉
- deadlock 一类的问题
- “某件事能不能发生”与“某个条件是否总成立”之间的区别
- 在不一开始灌完整逻辑语法的前提下，先建立 query 的直觉
- 轻度埋下 cost / optimality 的伏笔

主要素材来源：

- `papers/bdl04/README.md`
- `papers/lpy97/README.md`
- `papers/by04/README.md`

建议配图：

- 一个状态空间里目标状态、坏状态、不可达状态的示意图

公式密度：

- 低，优先用例子解释

### 4. 为什么需要 Symbolic States：从显式状态到 Zone

建议重点：

- 为什么连续时间让显式枚举直接失效
- region 的理论意义
- zone 的工程意义
- 为什么 symbolic state 会替代单个 valuation

主要素材来源：

- `papers/by04/README.md`
- `papers/lpw95/README.md`

建议配图：

- region 划分和一个更大 zone 的对比图
- 二维 `(x, y)` 时钟空间示意图

公式密度：

- 只需要让读者理解“若干时钟约束的合取”这个层面

### 5. DBM：为什么一个矩阵可以表示一个 Zone

建议重点：

- `xi - xj <= c` 这种差值约束
- 零时钟的作用
- DBM 的基本形状与直觉
- canonical closure 为什么是核心不变量
- 为什么 UDBM 是这一层最直接的实现承载

主要素材来源：

- `papers/by04/README.md`
- `papers/bengtsson02/README.md`

建议配图：

- 一个几何上的 zone 和对应 DBM 表格的对照图

公式密度：

- 中等，只讲最关键的表示式

### 6. 为什么单个 DBM 不够：Federation 与非凸集合

建议重点：

- 凸 zone 做减法为什么可能产生非凸结果
- federation 为什么是“多个 DBM 的并”
- 并、减法、规约为什么是语义上必须的，不是 API 装饰
- 为什么 UPPAAL 风格工具不可能只靠单个 DBM 走到底

主要素材来源：

- `papers/dhlp06/README.md`
- `papers/behrmann03/paper-c/README.md`

建议配图：

- 一个凸区域挖掉中间一块后变成多块的几何图

公式密度：

- 低到中等，图比式子更重要

### 7. 为什么还会有 CDD：非凸符号集合的另一种表示方式

建议重点：

- federation 和 CDD 都在回答“如何表示非凸 symbolic set”
- 共享与分解的基本直觉
- 什么时候 list-of-DBMs 很自然
- 什么时候图结构式表示更合适
- 强调 UPPAAL 的设计空间并不只有“一种 DBM 容器”

主要素材来源：

- `papers/behrmann03/README.md`
- `papers/behrmann03/paper-intro/README.md`
- `papers/behrmann03/paper-c/README.md`

建议配图：

- 同一个非凸集合分别用多块区域和 diagram-based shared structure 表示的对比图

公式密度：

- 低，这一篇先讲设计空间，不急着压公式

### 8. 搜索与优化：为什么 UPPAAL 不是一堆数据结构的简单堆叠

建议重点：

- forward symbolic reachability 的主循环
- waiting 与 passed
- inclusion check
- normalization 和 extrapolation 如何帮助终止
- 压缩存储、hashing、内存压力
- 为什么算法结构和数据结构形状会相互塑造

主要素材来源：

- `papers/bblp04/README.md`
- `papers/llpy97/README.md`
- `papers/bengtsson02/README.md`
- `papers/behrmann03/paper-intro/README.md`

建议配图：

- 搜索主循环框图
- extrapolation 前后对比图
- compact storage / passed-list pressure 示意图

公式密度：

- 中等，这里很多时候短伪代码比堆公式更有用

## 进阶篇规划

进阶篇面向已经接受了主线框架、开始关心实现层和扩展层的读者。

### 9. 建模与 Reduction：Urgent、Committed 与 Partial Order 在做什么

建议重点：

- 为什么某些建模构造本身就能减少无意义交错
- urgent 和 committed 的直觉
- 为什么 timed systems 上的 partial-order reduction 更难
- local-time 一类思路和探索重构

主要素材来源：

- `papers/bdl04/README.md`
- `papers/bengtsson02/README.md`

### 10. 超越 Reachability：Priced Timed Automata 与最优代价搜索

建议重点：

- 从“能否到达”转向“以最小代价到达”
- 成本 / price 如何进入模型
- priced regions、priced zones 和 cost-guided search
- 为什么 UPPAAL 的研究路线自然会延伸到 optimality

主要素材来源：

- `papers/behrmann03/README.md`
- `papers/behrmann03/paper-d/README.md`
- `papers/behrmann03/paper-e/README.md`
- `papers/behrmann03/paper-f/README.md`

### 11. 符号数据结构谱系图

建议重点：

- explicit states
- zones
- DBMs
- federations
- CDDs
- priced zones
- minimal constraints 与 compressed forms
- 各自到底在优化什么、牺牲什么

主要素材来源：

- `papers/behrmann03/paper-intro/README.md`
- `papers/bengtsson02/README.md`
- `papers/llpy97/README.md`

这篇很适合拿来连接理论教程、代码阅读和未来设计讨论。

### 12. 从理论走向 Python API：未来的 Python 侧 UPPAAL 重建应该暴露哪些层

建议重点：

- 哪些概念应该成为一等 Python 对象
- 哪些东西适合进入 public API，哪些更适合留在引擎内部
- 哪些层次应该优先恢复
- 如何在保持历史兼容的同时，给更完整的 UPPAAL Python 重建留出空间

这一篇更偏项目路线总结，不是单篇论文导向，但它应当把前面所有内容收束起来。

## 推荐的分批发布方式

为了让写作和维护压力可控，比较合适的方式是三批发布。

### 第一批

- 第 1 篇到第 6 篇

这一批解决的是读者第一次真正理解下面这些事情：

- UPPAAL 是干什么的
- timed automata 是什么
- 常见性质在问什么
- 为什么要用 symbolic zones
- DBM 是什么
- federation 为什么会出现

### 第二批

- 第 7 篇到第 8 篇

这一批开始把读者从基础 zone 直觉带到更真实的引擎层：

- CDD 这样的替代表示
- 搜索过程、终止机制和存储压力

### 第三批

- 第 9 篇到第 12 篇

这一批则进入：

- reduction-aware 的建模与算法
- priced timed automata
- symbolic representation 全景图
- Python 侧整体重建路线

## 每篇内部推荐模板

每篇教程最好维持一个相对稳定的内部结构：

1. 这篇要回答什么问题
2. 一个直观的小例子
3. 核心概念
4. 一张主图
5. 少量关键公式或短伪代码
6. 这和 UPPAAL 以及 Python 重建方向有什么关系
7. 延伸阅读：对应 `papers/` 下哪些材料

这种模板既适合新手，也便于中英文成对维护。

为了避免页面写成“概念堆叠”，每篇还应当额外自查：

- 开头的小例子是否足够具体，而不是一句抽象场景描述就带过
- 主图是否真的在解释例子，而不是只装饰概念
- 关键公式是否都能回指到前面的例子
- 结尾是否把例子和 Python / UPPAAL 语义对象重新连起来

## `foundations/` 目录形状建议

如果采用和 `tutorials/` 同级的新路径，当前更推荐的名字是：

- `docs/source/foundations/`

推荐目录形状：

```text
docs/source/foundations/
|- reading-guide/
|  |- index.rst
|  |- index_zh.rst
|  `- ... resources ...
|- what-is-uppaal/
|  |- index.rst
|  |- index_zh.rst
|  `- ... resources ...
|- timed-automata/
|  |- index.rst
|  |- index_zh.rst
|  `- ... resources ...
|- queries-and-properties/
|  |- index.rst
|  |- index_zh.rst
|  `- ... resources ...
|- symbolic-states/
|  |- index.rst
|  |- index_zh.rst
|  `- ... resources ...
|- dbm-basics/
|  |- index.rst
|  |- index_zh.rst
|  `- ... resources ...
|- federations/
|  |- index.rst
|  |- index_zh.rst
|  `- ... resources ...
`- ...
```

这里有几个约束需要明确写死：

- 每个主题子目录都只放 `index.rst`、`index_zh.rst` 和资源文件
- `reading-guide/` 也是普通主题子目录，和其他主题平级
- 主题子目录里不要再继续拆出别的 `*.rst` 页面
- 附图、示意图、演示代码、数据文件都作为该主题目录下的资源文件管理
- 如果某个主题很大，也优先通过同一对 `index` 页面内部组织小节，而不是继续横向增殖 rst 文件

这样做的好处是：

- 页面入口稳定，Sphinx 路径也更整齐
- 中英版本天然成对，不容易漏同步
- 每个主题的图、示例和页面文本会自然聚在一起
- 以后就算补资源，也不会把目录结构越长越散

## 图与公式的使用建议

### 图的建议

- 每篇至少应该有一张真正承担解释任务的主图
- 对入口导论页和体系性页面，最好不止一张图
- zone、DBM、federation、extrapolation 这类主题非常适合几何图
- 性质、搜索、引擎结构这类主题更适合流程图或状态空间图
- DBM / federation / CDD / priced structure 的差异最好通过对比图来讲
- `what-is-uppaal` 这类页面尤其应该补：
  - 一个简化控制系统 / 组件交互示意图
  - 一个工具工作流图
  - 一个 concrete vs symbolic 的直观对比图

### 公式的建议

- 不要一上来就堆完整形式系统
- 先用自然语言说明直觉，再给公式
- 第一次介绍一个概念时，宁可只给一个代表性公式
- 太密的形式细节更适合放到后续页面、附注或旁栏
- 关键公式和关键定义允许完整写出，但写出来就必须负责把它讲透

这里的“讲透”至少应包含下面几层：

- 公式整体在回答什么问题
- 公式里每个符号分别代表什么
- 这个约束、定义或规则在语义上到底限制了什么
- 读者应该从几何、状态变化、搜索过程或建模行为上如何直观理解它
- 这个公式和前后文例子之间是什么对应关系

如果某个公式很重要，推荐紧跟一个固定解读模板：

1. 先用一句人话说这条公式想表达什么
2. 再逐项解释符号、变量、约束方向和边界
3. 再说明它在图上、在状态里或在算法里分别意味着什么
4. 最后把它重新连回当前例子

也就是说，后续撰写时允许而且鼓励写出重要公式，但不接受下面这种写法：

- 直接抛出定义，不解释符号
- 公式写完以后只说“由此可见”
- 用论文原式替代自己的教学性解读
- 把真正关键的理解工作留给读者自己补

### LaTeX / reStructuredText 书写约定

涉及数学公式时，统一使用 LaTeX 形式书写，但不要使用 Markdown 风格的 `$...$` 或 `$$...$$`。

在 `rst` / Sphinx 页面里，统一采用下面两种写法：

- 行内公式使用 `:math:`
- 块级公式使用 `.. math::`

推荐写法示例：

```rst
一个 zone 可以看作若干差值约束的合取，例如
:math:`x - y \leq 3` 和 :math:`y \leq 5`。
```

```rst
.. math::

   x_i - x_j \leq c
```

如果需要写多行推导、分段讨论或带编号的展示公式，也继续放在 `.. math::` 块里完成，而不是额外发明别的记号风格。

这条约定的原因有两层：

- Sphinx 官方对 reStructuredText 数学内容的推荐入口就是 `:math:` 与 `.. math::`
- 本仓库当前 `docs/source/conf.py` 已经启用了 `sphinx.ext.mathjax`，因此这套写法和现有文档构建配置是匹配的

因此后续撰写时建议明确禁止：

- 直接写 `$x < 3$`
- 直接写 `$$x - y \leq 1$$`
- 把公式截图当成正文公式的主要承载方式

只有在确实需要展示手写推导、几何示意或论文原图时，才把图片当作公式的补充，而不是替代。

除了“写对格式”，还要满足一条内容规则：

- 每个公式都要配套详细文字解读
- 每个关键定义都要配套直观解释
- 如果公式无法被用自然语言讲清楚，通常说明作者自己也还没有把它吃透

## 入口导航建议

真正重要的不只是目录存在，还要在入口导读页里明确告诉用户“如果你现在卡在什么概念上，应该先读哪里”。

因此 `docs/source/foundations/reading-guide/index.rst` 与
`docs/source/foundations/reading-guide/index_zh.rst` 不应该只是一个普通 toctree，而应该承担“阅读分流页”的作用。

比较合适的入口结构是：

1. 先给一句话说明：这里不是安装教程，而是 UPPAAL 概念基础页
2. 然后给一组“我现在更像哪类读者”的分流入口
3. 再给完整主题目录
4. 最后给和 `papers/`、`tutorials/` 的关系说明

入口处分流建议至少覆盖下面几类读者：

- 如果你对 formal verification / model checking 都不熟悉：
  先读 `what-is-uppaal/`、`timed-automata/`、`queries-and-properties/`
- 如果你知道 timed automata，但不熟悉 symbolic state / zone：
  先读 `symbolic-states/`，再读 `dbm-basics/`
- 如果你已经知道 zone 和 DBM，但不清楚为什么会出现非凸表示：
  先读 `federations/`，再读 `cdd/`
- 如果你已经熟悉基础 symbolic semantics，想看引擎为什么能跑得动：
  先读搜索 / extrapolation / storage 相关主题
- 如果你主要关心这个仓库未来的 Python API 会怎么映射这些概念：
  在基础页里补一条明确导航，指向 API 重建路线相关页面

入口页还应该明确告诉读者：

- `tutorials/` 解决“怎么装、怎么跑、怎么开始用”
- `foundations/` 解决“这些概念到底是什么意思”
- `papers/` 解决“这些讲法主要来自哪些论文与材料”

换句话说，入口页不是简单列目录，而是要像一个“阅读路由器”。

## 双语组织建议

无论最终先写哪些主题，`foundations/` 体系都应继续沿用仓库已有的中英配对方式。

也就是说：

- 每个主题页都成对：`<topic>/index.rst` / `<topic>/index_zh.rst`
- 资源文件可共享，但正文页面始终保持中英分离

这一点不建议为了省事而退化成“一个英文页 + 一份中文补丁”或者“中英混写”。

## 中文术语写法建议

中文教程页不应长期处于“大量中英文混用”的状态。

更合适的规则是：

- 中文页默认使用中文术语作为正文主述
- 某个术语在一篇页面里第一次出现时，可以写成“中文术语(English term)”的形式
- 如果还需要缩写，可以在第一次出现时一起给出，例如“状态机(state machine, 简称 STM)”
- 在同一篇页面的后续内容里，优先继续使用中文术语，不要反复切回英文

例如：

- 时间自动机(timed automata)
- 模型检查(model checking)
- 形式化验证(formal verification)
- 符号状态(symbolic states)
- 区域(zone)
- 差分约束矩阵(DBM)
- 联邦(federation)

不推荐的写法是：

- 一段话里连续切换中英文术语
- 前面已经给过括注，后面仍然频繁直接写英文
- 中文句子主体已经成立，却仍然把大量英文名词直接塞进正文

这条规则的目标不是排斥英文，而是：

- 保持中文教程的阅读连续性
- 让首次出现时的英文术语仍然可检索、可对照论文与官方文档
- 让读者在后文更容易把握概念，而不是反复被术语切换打断

## 内容加粗规则

教程页可以使用加粗来帮助快速扫读，但必须克制使用。

更适合加粗的内容包括：

- 页面开头的定位句
- 一个章节里最关键的结论句
- 对比关系里的核心判断
- 读者最应该记住的一句话
- 分流页里“先读哪里”的关键指引

不适合加粗的内容包括：

- 大段整段文字
- 普通铺垫句
- 只是列事实但不承担结论作用的句子
- 几乎每段都加粗，导致页面重新失去层次

实践上可以把它理解为：

- 加粗是为了让读者“扫一眼就抓住主干”
- 不是为了把整页涂黑

## 论文引用与参考文献写法建议

当某一页的内容需要明确延伸到相关论文出处时，不要只在末尾随手列几个文件路径，也不要把出处信息混在正文里一带而过。

更合适的写法是采用接近论文参考文献的风格：

- 在正文需要给出处的地方使用类似 `[LPY97]_`、`[BDL04]_`、`[BEH03]_` 这样的引用
- 对官方 UPPAAL 文档或官方网站，也使用同样风格的引用，例如 `[UPP_HELP]_`、`[UPP_FEATURES]_`
- 在页面末尾单独设一个 `References` / `参考文献` 小节
- 每条文献项至少包含：
  - 作者
  - 题名
  - 一个公开可访问的文献链接
  - 一个指向本仓库对应语言 `README.md` 或 `README_zh.md` 的链接

对于官方文档来源，文献项至少应包含：

- 来源名或页面标题
- 官方公开链接
- 如果它只是用来支持工具行为或界面描述，可以没有仓库内 README 链接

对双语页面来说，这里还要额外注意：

- 英文页优先链接到仓库里的 `README.md`
- 中文页优先链接到仓库里的 `README_zh.md`
- 如果某篇论文在仓库里只有单语阅读指南，需要在页面里明确说明，而不是静默缺失

这样做的目的不是把教程写成论文，而是：

- 让读者知道每个关键说法主要来自哪里
- 让读者能顺着公开资料继续查文献
- 让读者能顺着仓库内阅读指南继续深入
- 让“官方工具行为”和“论文理论来源”在引用上都可追踪

## Phase 划分与 Checklist

为了让这份规划能够真正落地，后续工作建议按 phase 推进；每个 phase 完成前，都至少过一遍对应 checklist。

### Phase 0：文档结构与写作规范定稿

* [x] 确认 `tutorials/` 与 `foundations/` 的职责边界
* [x] 确认 `foundations/` 根目录与主题子目录的目录规则
* [x] 确认中英成对页面规则
* [x] 确认“主题子目录只放 `index.rst` / `index_zh.rst` + 资源文件”的约束
* [x] 确认入口页要承担阅读分流功能，而不是普通目录页
* [x] 确认每篇页面都必须以例子驱动，而不是定义驱动
* [x] 确认公式统一使用 LaTeX，并在 `rst` 中采用 `:math:` 与 `.. math::`
* [x] 确认不要使用 `$...$` / `$$...$$` 这类 Markdown 数学写法

### Phase 1：根入口与阅读分流页

* [x] 删除不必要的 `foundations/index*.rst`
* [x] 把入口导读作为 `foundations/reading-guide/` 的同级主题页落地
* [x] 在入口页写清楚 `tutorials/`、`foundations/`、`papers/` 三者的分工
* [x] 在入口页加入“如果你不熟悉 X，应先读 Y”的阅读分流
* [x] 在入口页加入完整主题目录
* [x] 在入口页说明这些页面和未来 Python API 重建路线的关系
* [x] 把入口导读和已完成主题页都同步加入顶层 `index_en.rst` / `index_zh.rst`
* [x] 检查中英入口页的结构是否对齐

### Phase 2：主线基础主题第一批

范围建议：

- 第 1 篇到第 6 篇

* [ ] `what-is-uppaal/` 页面完成中英双语骨架
* [ ] `timed-automata/` 页面完成中英双语骨架
* [ ] `queries-and-properties/` 页面完成中英双语骨架
* [ ] `symbolic-states/` 页面完成中英双语骨架
* [ ] `dbm-basics/` 页面完成中英双语骨架
* [ ] `federations/` 页面完成中英双语骨架
* [ ] 每个主题页都至少有 1 个贯穿页面的主例子
* [ ] 每个主题页都至少有 1 张真正承担解释任务的主图
* [ ] 每个主题页都至少有 1 处用 `:math:` 的行内公式
* [ ] 每个需要展示公式的主题页都使用 `.. math::` 编写块级公式
* [ ] 每个主题页结尾都补上“这和 UPPAAL / Python 重建方向有什么关系”
* [ ] 每个主题页都补上延伸阅读到 `papers/`
* [ ] 每个主题页都在正文里使用统一的论文式引用
* [ ] 每个主题页末尾都补上公开文献链接和仓库内对应语言阅读指南链接
* [ ] 每个主题页都在正文里使用统一的论文式引用
* [ ] 每个主题页末尾都补上公开文献链接和仓库内对应语言阅读指南链接

### Phase 3：引擎与表示进阶主题第二批

范围建议：

- 第 7 篇到第 8 篇

* [ ] `cdd/` 主题页完成中英双语骨架
* [ ] 搜索 / extrapolation / storage 主题页完成中英双语骨架
* [ ] 每页都明确说明它在回答什么工程问题
* [ ] 每页都至少给出 1 个“为什么基础表示不够”的具体例子
* [ ] 每页都至少给出 1 个算法流程图、状态流图或结构对比图
* [ ] 每页公式都保持“少而关键”，避免直接抄论文大段定义
* [ ] 每页都明确和前面基础主题的衔接关系

### Phase 4：扩展与项目路线第三批

范围建议：

- 第 9 篇到第 12 篇

* [ ] reduction 相关主题页完成中英双语骨架
* [ ] priced timed automata 相关主题页完成中英双语骨架
* [ ] symbolic representation family tree 主题页完成中英双语骨架
* [ ] Python API 重建路线主题页完成中英双语骨架
* [ ] 每页都明确“新增了什么视角，而不是重复前文”
* [ ] 每页都至少给出 1 个和真实工具设计有关的例子
* [ ] API 路线页明确区分 public API、内部语义对象和实现细节
* [ ] 主题之间的链接关系补齐

### Phase 5：统一润色与发布前自查

* [ ] 全部主题页都检查一次中英结构对齐情况
* [ ] 全部主题页都检查一次例子数量是否足够
* [ ] 全部主题页都检查一次公式是否统一使用 LaTeX + `:math:` / `.. math::`
* [ ] 全部主题页都检查一次是否混入 `$...$` / `$$...$$`
* [ ] 全部主题页都检查一次图是否真的承担解释任务
* [ ] 全部主题页都检查一次与 `papers/` 的延伸阅读链接
* [ ] 全部主题页都检查一次与 `tutorials/` / API 文档的入口连接
* [ ] 按读者视角试走一遍阅读路径，确认入口分流是否自然
* [ ] 选 1 到 2 个新手读者路径做通读，检查是否存在“先讲公式后给例子”的倒挂问题

## 相比最初窄版本规划，这里做了什么修正

最初的讨论版本偏 UDBM 中心，这里面有一些判断其实仍然是对的：

- 不按论文顺序写
- 风格要友好
- 图和公式要平衡
- `by04`、`dhlp06`、`bblp04` 是极核心的理论骨架

但那个版本低估了当前项目的真正方向：目标不是“把 UDBM 讲明白”，而是“帮助整个 UPPAAL 技术栈逐步在 Python 上复出来”。

因此修正后的规划明确把下面这些内容补进来了：

- property / query 视角
- CDD
- 整体引擎架构
- 存储与搜索压力
- reduction-oriented 建模构造
- priced symbolic structures
- 未来 Python 侧的整体 API 设计
- 与 `tutorials/` 同级的 `foundations/` 概念页目录
- 在入口页按读者背景做阅读分流

## 主题与篇目的快速对照

如果后面要快速决定“某个主题应该放哪一篇”，当前建议是：

- `fed`：第 6 篇
- `CDD`：第 7 篇
- 搜索主循环 / waiting / passed / inclusion / extrapolation：第 8 篇
- urgent / committed / partial order：第 9 篇
- priced timed automata / cost optimality：第 10 篇
- symbolic representation family tree：第 11 篇
- Python 侧整体重建策略：第 12 篇
- 基础性质与 query 直觉：第 3 篇

## 最后的编辑结论

这套文档不应该被写成“只面向 UDBM 内核的理论笔记”。

更合适的定位是：

围绕整个 UPPAAL 符号验证生态写一条对新手友好、但技术上足够诚实的教程主线，把 UDBM 放在其中的 DBM / federation 基础层位置上，而不是把它误当成全部故事。
