# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md) 中 introduction 部分的拆分版本。

它对应根 PDF 第 15-54 页。它不属于六篇内嵌论文本身，但对仓库工作依然很有价值，因为这里包含了：

- motivation 章节
- modeling formalism 与 data structure 的总览
- `The Making of Uppaal` 这一节
- papers A-F 的 thesis summary

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 为什么要单独拆这一段

虽然 thesis 形式上说自己是六篇论文的合集，但 introduction 部分本身异常有用。很多 thesis 级别的信息，在单篇 paper 的拆分目录里反而看不到。

对本仓库来说，这段 introduction 最有价值的地方在于：

- 它把 thesis 如何从 `visualSTATE` / ROBDD 走到 CDD 和 priced timed automata 解释清楚了
- 它给出了作者自己对主要 modeling formalism 和 symbolic data structure 的总览
- 它还包含 `Uppaal` 架构的系统级讨论，把算法和真实工具设计连在了一起

## 阅读时要抓住什么

建议重点关注：

- thesis 如何把 reachability analysis 放到多个 formalisms 里统一讨论
- explicit、symbolic、DBM、CDD、priced representation 之间的比较关系
- `The Making of Uppaal` 这一节，尤其是 layered architecture、symbolic state manipulation，以及 passed / waiting list 设计
- thesis summary 这一节，因为它用最短的篇幅给 papers A-F 补上了发表与定位信息

对本仓库来说，核心问题是：

"从 thesis 层面看，federation、CDD、priced structure 和 UPPAAL engine design 为什么会被放进同一条架构故事里？"

## 在本仓库中的对应位置

- Federation 类型与操作：`UDBM/include/dbm/fed.h`
- Priced federation 类型：`UDBM/include/dbm/pfed.h`
- Partition 支持：`UDBM/include/dbm/partition.h`
- Python 高层 wrapper：`pyudbm/binding/udbm.py`

更具体地说：

- data-structure overview 解释了为什么 thesis 会把 DBM、minimal constraints、CDD 和 priced structures 看成不同的工程选择
- `The Making of Uppaal` 是本地最直接的架构性文字，能帮助理解 symbolic-state representation 如何嵌进真实工具流水线
- thesis summary 则是进入 papers A-F 之前最快的定向入口

## 为什么它对 UDBM 特别重要

如果拆出来的各篇论文回答的是“某个算法或数据结构是什么”，那么这段 introduction 回答的是“为什么这些主题会一起组成同一篇 thesis”。

当你需要的是架构层 framing，而不是某个孤立结果时，它就是最好的本地入口。

## 如何阅读

如果你想先拿到 thesis 级别的地图，再进入各篇拆分论文，就先读这篇。

然后再按主题继续：

- [paper-c/README.md](../paper-c/README.md)：CDD 与非凸 symbolic set
- [paper-d/README.md](../paper-d/README.md)、[paper-e/README.md](../paper-e/README.md)、[paper-f/README.md](../paper-f/README.md)：priced timed automata
- [paper-a/README.md](../paper-a/README.md) 和 [paper-b/README.md](../paper-b/README.md)：更早期的 `visualSTATE` 背景
