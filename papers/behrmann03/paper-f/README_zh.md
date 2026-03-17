# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md) 中 Paper F 的拆分版本。

它对应根 PDF 第 163-193 页，主题是 priced zones，以及在线性价格 timed automata 上高效地做 cost-optimal reachability。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis summary 对这篇内嵌论文的标题说明是：

`As Cheap as Possible: Efficient Cost-Optimal Reachability for Priced Timed Automata`

thesis 中给出的发表历程是：

- 短版本发表于 `CAV'01`，收录于 `LNCS 2102`
- 当前 thesis 中嵌入的是这里采用的扩展 paper 版本

## 当前精修版本地阅读稿具体包含什么

本地的 [content.md](./content.md) 现在已经把整套 priced-zone 技术工具保留下来，而不是只给出“priced zones 存在”这个结论。它明确保留了：

- symbolic optimal reachability 的整体问题设定
- priced timed automata 的预备内容
- priced zone 作为主要符号对象的定义
- facets 以及 priced zones 上的运算，这正是论文真正的技术核心
- 实现与实验部分，以及 aircraft landing 的结果表

因此，这篇不只是告诉你“可以做 priced zones”，而是 thesis 里最直接解释“普通 zone machinery 怎么被抬升成带代价的 symbolic calculus”的那一篇。

## 阅读时要抓住什么

建议重点关注：

- priced zones 作为主要符号对象
- zone 的 facets，以及它们为什么是 priced-zone 操作所必需的
- 如何把普通基于 zone 的 timed reachability 机械提升到线性价格场景
- 如何从更偏理论的 priced regions，走到更偏实现友好的符号对象

对本仓库来说，核心问题是：

"经典的 zone 工具链到底要怎样扩展，才能让 optimal-cost reachability 变成一种自然的 symbolic operation，而不是额外叠加的一层理论？"

## 它和 `behrmann03` 其他子论文是什么关系

这篇是 priced 簇的终点。

- 如果你想补 region-theoretic 的前驱，先读 [paper-d/README_zh.md](../paper-d/README_zh.md)。
- 如果你想补从普通 DBM 机械通向 priced 搜索的实现桥梁，先读 [paper-e/README_zh.md](../paper-e/README_zh.md)。

## 在本仓库中的对应位置

- Federation 类型与操作：`UDBM/include/dbm/fed.h`
- Priced federation 类型：`UDBM/include/dbm/pfed.h`
- 面向 partition 的规约支持：`UDBM/include/dbm/partition.h`
- 高层 wrapper 表面：`pyudbm/binding/udbm.py`

更具体地说：

- 这是 thesis 里和 priced symbolic structure 最接近、同时又仍然贴着经典 zone machinery 的一篇
- 如果你想把 priced reachability 和 zone-like object 上的操作联系起来，而不是只停留在 region theory，这篇最好

## 为什么它对 UDBM 特别重要

在这六篇拆分论文里，这篇最像是 DBM / zone 风格工具链的 priced 扩展版本。

如果你碰的是 priced zones、priced federations，或者带代价标注的 symbolic state，这篇通常是整组里价值最高的一篇。

## 如何阅读

如果你想把 priced 这条线完整读下来，建议在 [paper-d/README_zh.md](../paper-d/README_zh.md) 和 [paper-e/README_zh.md](../paper-e/README_zh.md) 之后读它。

如果你只能从这篇 thesis 里选一篇 priced 论文来服务当前仓库工作，通常就选这一篇。
