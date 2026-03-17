# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md) 中 Paper B 的拆分版本。

它对应根 PDF 第 77-98 页，主题是层次化 `state/event` 系统、superstate reachability 的复用，以及把这种复用和组合式符号验证结合起来。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis summary 对这篇内嵌论文的标题说明是：

`Verification of Hierarchical State/Event Systems using Reusability and Compositionality`

thesis 中给出的发表历程是：

- 早期版本发表于 `TACAS'99`，收录于 `LNCS 1579`
- 完整版本发表于 `Formal Methods in System Design`，21 卷 2 期，2002 年 9 月

## 阅读时要抓住什么

建议重点关注：

- 如何复用更高层 superstate 的已有 reachability 结果
- reachability question 如何沿层次结构被拆解
- 如何在受限子系统上做 compositional backward step
- dependency closure 一类思路如何让分析只在必要时扩张

对本仓库来说，核心问题是：

"在进入 timed domain 之前，这篇 thesis 是如何从普通 symbolic compositionality 走到结构感知复用的？"

## 在本仓库中的对应位置

和 paper A 一样，这篇更偏背景，而不是 UDBM API 的直接来源。

它在这里最接近的价值是：

- 展示 thesis 如何把 symbolic reuse 当成一个工程问题来处理
- 解释后来 UPPAAL 为什么持续寻找能够避免重复全局探索的表示与算法

## 为什么它对 UDBM 特别重要

这篇不是关于 DBM、federation 或 priced zones 的论文。它的重要性主要在于：它补上了 thesis 更广义的 symbolic verification 发展轨迹。

如果你的任务严格面向 UDBM，可以快速浏览后继续往后看。

## 如何阅读

如果你想补完整的 pre-timed 背景，可以在 [paper-a/README.md](../paper-a/README.md) 之后继续读这篇。

如果你真正关心的是非凸 symbolic set，或者 timed / priced 结构，就直接跳到 [paper-c/README.md](../paper-c/README.md)。
