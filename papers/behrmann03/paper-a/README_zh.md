# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md) 中 Paper A 的拆分版本。

它对应根 PDF 第 55-76 页，主题是利用 dependency analysis 和 backwards reachability 对大型 `state/event` 系统做组合式符号模型检测。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis summary 对这篇内嵌论文的标题说明是：

`Verification of Large State/Event Systems using Compositionality and Dependency Analysis`

thesis 中给出的发表历程是：

- 早期版本发表于 `TACAS'98`，收录于 `LNCS 1385`
- 完整版本发表于 `Formal Methods in System Design`，18 卷 1 期，2001 年 1 月

## 当前精修版本地阅读稿具体包含什么

本地的 [content.md](./content.md) 现在已经把整篇论文整理成一份连贯技术稿，而不是只保留核心口号。它明确保留了：

- state/event systems 的形式化定义，而不只是算法摘要
- visualSTATE consistency checks 如何被归约成 reachability 与 local deadlock 问题
- ROBDD 编码与 transition relation 构造，包括 partitioned transition relation 的讨论
- compositional backwards reachability 的主体，包括 `B_I`、dependency-closed set 和核心算法图
- local deadlock detection 这一半内容，因为这篇论文并不只是在讲 reachability
- 实验部分以及两张表和多张 dependency / usage 图

对仓库阅读来说，这意味着现在可以同时看到“符号搜索方法本身”以及“它为什么会被这样工程化”。

## 阅读时要抓住什么

建议重点关注：

- compositional backwards reachability
- dependency analysis 如何推迟把更多组件拉进搜索
- 分析范围逐步扩大时的 symbolic reuse
- 数学上的 fixed point 叙述和 ROBDD 实现叙述之间的关系
- 工业示例是如何被用来支撑这种 dependency-oriented 搜索风格的

对本仓库来说，核心问题是：

"作者在有限状态系统里形成的哪些符号搜索习惯，后来又出现在 thesis 的 timed 和 priced 部分？"

## 它和 `behrmann03` 其他子论文是什么关系

这篇是 pre-timed 簇的第一步。

- 如果你想继续看这套 compositionality 如何被扩展到层次化复用，下一篇读 [paper-b/README_zh.md](../paper-b/README_zh.md)。
- 如果你只关心真正开始进入 UDBM 风格问题的部分，可以直接跳到 [paper-c/README_zh.md](../paper-c/README_zh.md)。

## 在本仓库中的对应位置

这篇主要是历史背景，而不是当前 UDBM API 的直接来源。

它在本仓库里的价值更偏概念层面：

- 它解释了为什么 UPPAAL 这条技术线一直重视 symbolic pruning 和结构化探索
- 它展示了作者早期就依赖 partitioning、reuse 和 delayed inclusion 的工程偏好
- 它有助于理解后面非凸与 priced symbolic-state 工作背后的验证引擎思路

## 为什么它对 UDBM 特别重要

这不是一篇 DBM 或 federation 论文。它的重要性在于：它展示了 thesis 在进入 timed systems 之前，作者已经形成了怎样的 symbolic model checking 风格。

如果你只关心 UDBM 直接相关的数据结构，可以把它视为可选背景材料；如果你关心作者长期的验证引擎方法论，它就很有价值。

## 如何阅读

如果你想补完整的 thesis 时间线或者 pre-timed 的符号验证背景，就读这篇。

如果你真正关心的是非凸 symbolic set、CDD 或 priced 结构，就尽快继续看 [paper-c/README_zh.md](../paper-c/README_zh.md)。
