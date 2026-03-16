# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Clocks, DBMs and States in Timed Systems](../README.md) 中 Paper E 的拆分版本。

它对应 thesis 第 115-143 页，主题是 committed locations 以及一个基于 UPPAAL 的工业音频控制协议案例。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis 对这篇内嵌论文的说明是：

`Johan Bengtsson, W. O. David Griffioen, Kare J. Kristoffersen, Kim G. Larsen, Fredrik Larsson, Paul Pettersson and Wang Yi. Automated Verification of an Audio-Control Protocol using UPPAAL. Accepted for publication in Journal on Logic and Algebraic Programming.`

## 阅读时要抓住什么

建议重点关注：

- committed locations 机制本身，以及它为什么同时影响建模方式和验证成本
- 为了利用 committed locations，model-checking algorithm 需要做哪些调整
- 带 bus collision 的音频控制协议如何作为真实案例验证这套方法
- 新版 UPPAAL 实现和旧行为之间的性能对比

对本仓库来说，关键问题是：

"为什么 committed locations 在工程实践里重要到足以同时改变建模风格和状态空间探索算法？"

## 在本仓库中的对应位置

- 这篇主要提供的是 UPPAAL 工具背景，而不是直接的 UDBM API 设计
- 当你要理解更高层建模 ergonomics，以及状态空间约简为什么在实践中重要时，它很有价值
- 它和 `papers/` 中已经收录的 `lpy97`、`bdl04` 等 UPPAAL 使用论文自然连在一起

## 为什么它对 UDBM 特别重要

这篇用一个非平凡工业案例展示了 DBM 与状态空间优化究竟在什么样的使用环境中产生真实收益。

如果你需要一个具体例子来说明 committed locations、状态空间约简和高效 symbolic manipulation 并不只是理论上的小修小补，这篇很合适。

## 如何阅读

如果你想看 committed locations 和 reduction 思路在真实 UPPAAL 案例里怎样落地，建议在 [paper-d/README.md](../paper-d/README.md) 之后读这篇。

对 wrapper 直接开发来说，它更像补充背景而不是第一优先论文；但当你需要工业级例子而不是纯算法论证时，这篇很有价值。
