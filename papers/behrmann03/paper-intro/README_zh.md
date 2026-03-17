# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md) 中 introduction 部分的拆分版本。

它对应根 PDF 第 15-54 页。它不属于六篇内嵌论文本身，但对仓库工作往往是最高效的起点，因为它补上了各篇拆分论文默认省略掉的 thesis 级 framing。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 为什么要单独拆这一段

虽然 thesis 形式上是六篇论文的合集，但 introduction 本身异常有用。它同时给出：

- thesis 整体动机
- 从 `visualSTATE` / ROBDD 走到 CDD 与 priced timed automata 的总路线图
- 作者自己对 modeling formalism 和 symbolic data structure 的总览
- `The Making of Uppaal` 这类明显偏架构、偏工具工程的内容
- papers A-F 的 thesis 级 summary，能最快说明各篇论文为什么会被放在一起

## 当前精修版本地阅读稿具体包含什么

本地的 [content.md](./content.md) 现在已经是一份可直接阅读的整理稿，而不是粗抽取结果。它明确保留了：

- motivation 与 reachability analysis 的 thesis 级铺垫
- state/event machines、hierarchical state/event machines、timed automata、priced timed automata 的形式化总览
- ROBDD、DBM、CDD、priced zones、minimal constraint form 的数据结构总览
- `The Making of Uppaal`，包括 goals、architecture、Umbrella、distributed UPPAAL、stopwatches、priced timed automata in UPPAAL 等内容
- papers A-F 的 thesis summary，以及作者自己给出的 contribution 视角

因此，这份 introduction 现在已经可以当作仓库内的体系结构导论来用，而不只是前言。

## 阅读时要抓住什么

建议重点关注：

- thesis 如何把 reachability analysis 放到多个 formalisms 里统一讨论
- 作者如何比较 explicit、symbolic、DBM、CDD、priced representation
- `The Making of Uppaal` 里的 symbolic-state manipulation 与 passed / waiting list 设计
- papers A-F summary，因为它是进入各个拆分子论文之前最快的定向入口

对本仓库来说，核心问题是：

"从 thesis 层面看，federation、CDD、priced structure 和 UPPAAL engine design 为什么会被放进同一条架构故事里？"

## 它和 `behrmann03` 其他子论文是什么关系

这篇 introduction 是整套拆分材料的中枢。

- 如果你想补 `visualSTATE` / ROBDD 的 pre-timed 背景，后面继续读 [paper-a/README_zh.md](../paper-a/README_zh.md) 和 [paper-b/README_zh.md](../paper-b/README_zh.md)。
- 如果你接下来关心的是非凸 symbolic set、CDD、或 plain DBM list 的替代表示，后面继续读 [paper-c/README_zh.md](../paper-c/README_zh.md)。
- 如果你接下来关心的是 cost-optimal reachability 与 priced symbolic states，后面继续读 [paper-d/README_zh.md](../paper-d/README_zh.md)、[paper-e/README_zh.md](../paper-e/README_zh.md)、[paper-f/README_zh.md](../paper-f/README_zh.md)。

## 在本仓库中的对应位置

- Federation 类型与操作：`UDBM/include/dbm/fed.h`
- Priced federation 类型：`UDBM/include/dbm/pfed.h`
- Partition 支持：`UDBM/include/dbm/partition.h`
- Python 高层 wrapper：`pyudbm/binding/udbm.py`

更具体地说：

- data-structure overview 解释了为什么 thesis 会把 DBM、minimal constraints、CDD 和 priced structures 看成不同的工程选择，而不是同一对象的不同表皮
- `The Making of Uppaal` 是本地最强的一段架构性文字，能帮助理解 symbolic-state representation 如何嵌进真实工具流水线
- papers A-F summary 则是决定“下一篇该读哪篇”的最快索引

## 为什么它对 UDBM 特别重要

如果拆出来的各篇论文回答的是“某个算法或数据结构是什么”，那么这段 introduction 回答的是“为什么这些主题会一起组成同一篇 thesis”。

当你需要的是系统级 framing，而不是某个孤立结果时，它就是最好的本地入口。

## 如何阅读

如果你想先拿到 thesis 级别的地图，再进入各篇拆分论文，就先读这篇。

然后再按主题继续：

- 用 [paper-c/README_zh.md](../paper-c/README_zh.md) 跟 CDD 与非凸 symbolic set
- 用 [paper-d/README_zh.md](../paper-d/README_zh.md)、[paper-e/README_zh.md](../paper-e/README_zh.md)、[paper-f/README_zh.md](../paper-f/README_zh.md) 跟 priced timed automata
- 用 [paper-a/README_zh.md](../paper-a/README_zh.md) 和 [paper-b/README_zh.md](../paper-b/README_zh.md) 补 `visualSTATE` 背景
