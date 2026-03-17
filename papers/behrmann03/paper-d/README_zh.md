# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md) 中 Paper D 的拆分版本。

它对应根 PDF 第 115-138 页，主题是在线性价格 timed automata 上，利用 priced regions 做 minimum-cost reachability。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis summary 对这篇内嵌论文的标题说明是：

`Minimum-Cost Reachability for Priced Timed Automata`

thesis 中给出的发表历程是：

- 短版本发表于 `HSCC'01`，收录于 `LNCS 2034`
- 完整版本作为 `BRICS Report Series RS-01-3`

## 阅读时要抓住什么

建议重点关注：

- linearly priced timed automata 的形式化模型
- priced regions 作为 thesis 里第一个面向 minimum-cost reachability 的符号对象
- branch-and-bound 风格的探索算法
- 为什么这个问题可判定，但 region-based 机械还不够实现友好

对本仓库来说，核心问题是：

"在引入 priced zones 之前，cost-optimal timed reachability 的理论型符号基础到底是什么？"

## 在本仓库中的对应位置

- Priced federation 类型：`UDBM/include/dbm/pfed.h`
- 高层 symbolic set 暴露：`pyudbm/binding/udbm.py`

更具体地说：

- 这篇解释了为什么 priced symbolic state 需要自己的对象，而不能只是普通 reachability 之后再做一层后处理
- 它更像概念前驱，而不是直接的 API 蓝图

## 为什么它对 UDBM 特别重要

这篇是 thesis 里 priced 理论线的起点。

虽然它的实现感不如 E-F 两篇强，但如果你想先搞清楚“priced reachability 到底在求什么”，它是本地最清晰的一篇。

## 如何阅读

如果你想在读 [paper-f/README.md](../paper-f/README.md) 之前先把 priced-zone 工作的理论动机补齐，就先读这篇。

如果你更想先看通向实际 UPPAAL / DBM 机械的桥梁，就继续看 [paper-e/README.md](../paper-e/README.md)。
