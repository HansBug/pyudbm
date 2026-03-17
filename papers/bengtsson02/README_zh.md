# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这篇 thesis 是最贴近 UDBM 本体的长篇参考之一。它不只讲抽象的 timed automata 理论，而是深入到 DBM 的数据结构、操作、normalization、存储以及实现取舍。

如果说 `by04` 是最好的紧凑型教程，那么这篇就是更偏实现导向的深挖版。

## 内嵌子论文架构

这个条目现在分成两层：

- `papers/bengtsson02/` 根目录下的 thesis 级材料，包括完整的 [paper.pdf](./paper.pdf)、thesis 级 README，以及整理后的 [content.md](./content.md)
- `paper-a/` 到 `paper-e/` 这五个二级子目录，对应 thesis 里内嵌的五篇子论文

仓库里仍然把根目录下的 thesis PDF 视为这篇条目的规范完整版本。新增的五个子目录只是把 thesis 中已经包含的五篇论文分别拆开，便于单独阅读和引用。现在每个子目录都已经有 paper 级导读和本地精修阅读版本：

- `paper.pdf`
- `README.md`
- `README_zh.md`
- `content.md`
- 当需要图表资源时还会有 `content_assets/`

当前二级结构对应关系如下：

- [paper-a/README.md](./paper-a/README.md)：`DBM: Structures, Operations and Implementation`（thesis 第 23-44 页）
- [paper-b/README.md](./paper-b/README.md)：`Reachability Analysis of Timed Automata Containing Constraints on Clock Differences`（thesis 第 45-66 页）
- [paper-c/README.md](./paper-c/README.md)：`Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems`（thesis 第 67-92 页）
- [paper-d/README.md](./paper-d/README.md)：`Partial Order Reductions for Timed Systems`（thesis 第 93-114 页）
- [paper-e/README.md](./paper-e/README.md)：`Automated Verification of an Audio-Control Protocol using UPPAAL`（thesis 第 115-143 页）

如果你需要读 thesis 自己的导论、作者对五篇文章的统一定位、或者完整参考文献，请留在根目录阅读。若你只是想单独跟某一篇子论文，直接进入对应的 `paper-a` 到 `paper-e` 子目录更合适。

## 这五篇子论文之间是什么关系

这五篇并不是并列、可随便替换的材料。它们整体上形成了一条比较清晰的路线：先从 DBM 本体出发，再走到 normalization、状态存储，最后上升到 UPPAAL 的搜索策略和工业案例语境。

- [paper-a/README.md](./paper-a/README.md) 是 DBM 本体入口。
  它和 `dbm.h` / `dbm.c` 的距离最近，重点是表示、closure 导向的操作、原始 DBM 变换，以及底层实现取舍。
- [paper-b/README.md](./paper-b/README.md) 是 normalization 的后续。
  它解释了当 symbolic reachability 需要保留 clock-difference constraints 时，事情为什么会比简单上界约束复杂得多。
- [paper-c/README.md](./paper-c/README.md) 是内存与存储那篇。
  它把视角从“如何操作单个 DBM”推进到 passed list 增长、紧凑存储，以及后来会在 `mingraph` 一类机制里出现的 reduction 思路。
- [paper-d/README.md](./paper-d/README.md) 是 local-time / partial-order 那篇。
  它和 wrapper 表层 DBM 方法的直接关系没那么强，但对理解 timed symbolic structures 在更激进的 exploration algorithm 里如何运作很重要。
- [paper-e/README.md](./paper-e/README.md) 是 committed locations / 工业案例那篇。
  它展示了 paper-d 那类建模与搜索改造在真实 UPPAAL 验证场景里如何落地，而不只是停留在算法层面的讨论。

如果你要按“最贴近实现”的路径读这五篇，建议顺序是：

1. [paper-a/README.md](./paper-a/README.md)
2. [paper-b/README.md](./paper-b/README.md)
3. [paper-c/README.md](./paper-c/README.md)
4. [paper-d/README.md](./paper-d/README.md)
5. [paper-e/README.md](./paper-e/README.md)

这个顺序的好处是：先把 DBM 对象本身读清楚，再补 normalization，然后再看存储；等这些都稳了，再进入搜索顺序约简和工业工具背景。

## 五篇子论文各自补什么

### Paper A

标题：
`DBM: Structures, Operations and Implementation`

对仓库的价值：

- 这是本地最直接解释原生 DBM 操作词汇的一篇：`up`、`down`、reset 类更新、closure、relation checks 等都能在这里找到实现导向的语境
- 当你在读 native DBM 代码，而又不想只看泛泛的 timed automata 理论介绍时，它尤其有用

### Paper B

标题：
`Reachability Analysis of Timed Automata Containing Constraints on Clock Differences`

对仓库的价值：

- 它最直接解释了：一旦 guard / invariant 里含有 clock-difference constraints，normalization 为什么会明显变难
- 当你要判断某种 symbolic 简化是否仍然 sound、还是需要额外条件时，这篇很关键

### Paper C

标题：
`Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems`

对仓库的价值：

- 这是五篇里和紧凑存储、passed list 压力、`mingraph` 相关设计最接近的一篇
- 当问题不再是“单个 DBM 怎么操作”，而是“很多 symbolic states 怎么高效保存”时，它最有帮助

### Paper D

标题：
`Partial Order Reductions for Timed Systems`

对仓库的价值：

- 它解释了在 timed systems 里让 partial-order reduction 真正可用之前，为什么要先改造 local-time semantics 和 symbolic view
- 当你需要理解“约简友好的探索”为什么不是简单叠一个搜索启发式，而是要改 underlying symbolic model 时，这篇很重要

### Paper E

标题：
`Automated Verification of an Audio-Control Protocol using UPPAAL`

对仓库的价值：

- 它展示了 committed locations 和相关 exploration 选择在真实协议上如何产生收益，而不是只在教科书级小例子里成立
- 当你需要一个具体的 UPPAAL 工业案例来解释“建模原子性”和“避免无谓 interleavings”为什么真的重要时，这篇最好用

## 阅读时要抓住什么

不建议把整本 thesis 等权来读。对 UDBM 工作来说，建议重点关注：

- DBM 数据结构和 canonical representation
- symbolic exploration 需要的完整 DBM 操作集
- normalization，特别是带 clock-difference constraints 的情形
- 压缩和状态存储技术

对本仓库来说，最关键的问题是：

"UDBM 里的哪些实现选择，其实是有理论支持的算法决定，而不是随手写出来的库工程细节？"

## 在本仓库中的对应位置

- 核心 DBM API：`UDBM/include/dbm/dbm.h`
- Federation 与更高层 symbolic set 支持：`UDBM/include/dbm/fed.h`
- 紧凑存储机制：`UDBM/include/dbm/mingraph.h`、`UDBM/src/mingraph_write.c`
- 暴露历史操作的高层包装：`pyudbm/binding/udbm.py`
- 恢复历史行为的测试：`test/binding/test_api.py`

更具体地说：

- thesis 里的 DBM 操作，和 `up`、`down`、`updateValue`、`freeClock`、emptiness / containment 检查直接对应
- normalization 的讨论，有助于理解 `dbm.h` 与 wrapper 里的 extrapolation 风格公开操作
- 压缩相关内容，有助于理解 UDBM 已经存在的 `mingraph`、hashing 与存储优化代码

## 为什么它对 UDBM 特别重要

这篇 thesis 和 UDBM 真实的工程形态非常接近：它面对的是验证工具约束下的生产级 symbolic timing library。

当你需要解释为什么库里会暴露某种操作、为什么要保持 canonical closure、或者为什么会有看上去像“内部优化杂项”的存储与压缩机制时，它尤其有用。

## 如何阅读

建议选择性阅读。如果你需要作者在 thesis 层面对全局贡献的总结，就先看根目录下的导论；如果你已经知道自己关心的主题，直接进入拆分后的二级子论文更高效。

对本仓库最实用的一条路径是：

- [paper-a/README.md](./paper-a/README.md)：先看 DBM 数据结构和基础操作
- [paper-b/README.md](./paper-b/README.md)：再看带 clock-difference constraints 的 normalization
- [paper-c/README.md](./paper-c/README.md)：然后看压缩、WAIT / PASSED 与内存优化

后两篇依然值得看，但更偏 UPPAAL 引擎背景，而不是 wrapper 表层 API：

- [paper-d/README.md](./paper-d/README.md)：local-time semantics 与 partial-order reduction
- [paper-e/README.md](./paper-e/README.md)：committed locations 与工业音频协议案例

还可以记一个更实用的分界：

- 如果你的问题主要是“原生 UDBM 到底做了什么、为什么这样做”，优先看 A-C
- 如果你的问题主要是“这些数据结构和 API 是在什么样的 model-checking engine 压力下形成的”，再补 D-E
