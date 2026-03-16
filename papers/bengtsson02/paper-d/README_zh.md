# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Clocks, DBMs and States in Timed Systems](../README.md) 中 Paper D 的拆分版本。

它对应 thesis 第 93-114 页，主题是通过 local-time semantics 在 timed systems 上做 partial-order reduction。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis 对这篇内嵌论文的说明是：

`Johan Bengtsson, Bengt Jonsson, Johan Lilius and Wang Yi. Partial Order Reductions for Timed Systems. In Proceedings, Ninth International Conference on Concurrency Theory, volume 1466 of Lecture Notes in Computer Science, Springer Verlag, 1998.`

## 阅读时要抓住什么

建议重点关注：

- timed automata network 的 local-time semantics
- 进程通信时需要的 resynchronization 机制
- 如何重新恢复足够的 independence，从而复用标准 partial-order 思路
- 这种语义变化对 DBM 表示带来的后果

对本仓库来说，关键问题是：

"要让 partial-order reasoning 在 timed systems 上重新变得有用，底层语义到底必须改动到什么程度？"

## 在本仓库中的对应位置

- 这篇更偏 UPPAAL 引擎背景，而不是直接对应 wrapper API
- 它帮助理解的是 symbolic state 的语义，而不只是某个 DBM 操作
- 在阅读后续 committed-location 工作和更广义的 UPPAAL 架构论文时，这篇是重要背景

## 为什么它对 UDBM 特别重要

这篇不是 Python wrapper 表层 API 的第一优先参考，但它解释了 UDBM 一类状态表示机制所处的工具语境。

如果你需要理解 local-time exploration 的语义依据、partial-order reduction 的论证，或者后续 committed locations 的设计背景，就应该读这篇。

## 如何阅读

除非你的任务本来就直接指向 UPPAAL 语义，否则建议先读完 [paper-a/README.md](../paper-a/README.md)、[paper-b/README.md](../paper-b/README.md) 和 [paper-c/README.md](../paper-c/README.md)，再来看这篇。

它和 [paper-e/README.md](../paper-e/README.md) 是自然衔接的，后者会把 committed locations 的故事推进到具体工具与案例层面。
