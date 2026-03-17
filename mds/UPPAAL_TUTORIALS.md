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
- 多使用几何直觉图、执行过程图、状态空间图
- 证明味道太重的内容放到读者已经有直觉之后再讲

### 3. 每篇都要兼顾直觉、图和少量数学

每一页比较合适的默认配置是：

- 1 张主图
- 必要时再加 1 张补图
- 2 到 4 个关键公式
- 1 个贯穿整页的小例子
- 结尾有一小节解释“这和 UPPAAL / Python 重建方向有什么关系”

文档不能变成纯公式，也不能变成只有口头描述的科普稿。

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

## 素材来源与主要依托

这份教程规划主要建立在下面这些本地 paper guide 的基础上：

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

粗略地说：

- `ad90` 和 `by04` 提供 timed automata 与 symbolic semantics 的基础主线
- `dhlp06` 解释 federation、减法和非凸性
- `bblp04` 解释 extrapolation、抽象和终止
- `llpy97` 与 `bengtsson02` 解释存储、压缩和引擎成本压力
- `lpy97` 与 `bdl04` 提供工具视角与建模视角
- `behrmann03` 把视角扩展到 CDD、系统架构和 priced symbolic structures

## 总体策略：主线篇 + 进阶篇

更合适的公开结构不是一条长长的线性教程，而是两层：

- 主线篇：给初学者建立完整直觉
- 进阶篇：给开始关心实现、算法和 Python 重建路径的人

这样既不会把门槛抬得太高，也不会把真正重要的工程问题都省掉。

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

## 图与公式的使用建议

### 图的建议

- 每篇至少应该有一张真正承担解释任务的主图
- zone、DBM、federation、extrapolation 这类主题非常适合几何图
- 性质、搜索、引擎结构这类主题更适合流程图或状态空间图
- DBM / federation / CDD / priced structure 的差异最好通过对比图来讲

### 公式的建议

- 不要一上来就堆完整形式系统
- 先用自然语言说明直觉，再给公式
- 第一次介绍一个概念时，宁可只给一个代表性公式
- 太密的形式细节更适合放到后续页面、附注或旁栏

## 双语组织建议

未来 `docs/source/tutorials/` 下的 theory 部分建议继续沿用仓库已有的中英配对结构。

一个可能的目录形状是：

```text
docs/source/tutorials/theory/
|- index.rst
|- index_zh.rst
|- 01-what-is-uppaal.rst
|- 01-what-is-uppaal_zh.rst
|- 02-timed-automata-basics.rst
|- 02-timed-automata-basics_zh.rst
|- ...
```

具体文件名可以再调整，但“成对页面”这个原则不建议改。

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
