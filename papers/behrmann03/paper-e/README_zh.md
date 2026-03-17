# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md) 中 Paper E 的拆分版本。

它对应根 PDF 第 139-162 页，主题是在 uniformly priced timed automata 上，如何在 UPPAAL 中高效地做 minimum-cost 搜索。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis summary 对这篇内嵌论文的标题说明是：

`Efficient Guiding Towards Cost-Optimality in Uppaal`

thesis 中给出的发表历程是：

- 短版本发表于 `TACAS'01`，收录于 `LNCS 2031`
- 完整版本作为 `BRICS Report Series RS-01-4`

## 当前精修版本地阅读稿具体包含什么

本地的 [content.md](./content.md) 现在已经把整篇论文保留成一篇真正的实现导向算法论文，而不只是“有一种 priced search order”。它明确保留了：

- uniformly priced timed automata 的设定，以及它和更一般 linearly priced 模型的关系
- cost function machinery 与 symbolic semantics
- 用额外 cost clock 实现的 DBM 表示
- `MC` 与 `MC+` 搜索顺序，以及 estimates / heuristics / bounding 的讨论
- bridge problem、job shop scheduling、Sidmar steel plant、biphase mark protocol 这些实验小节
- 全部五张表，因为这篇论文的重要性很大程度上就在于搜索策略与实测效果

因此，这篇现在已经是一座非常直接的桥：把“普通 DBM 风格 symbolic state”与“真实 UPPAAL 实现里的 cost-guided search”连了起来。

## 阅读时要抓住什么

建议重点关注：

- uniformly priced timed automata 的 symbolic cost state
- 利用额外 cost clock 的 DBM 表示
- `MC` 和 `MC+` 搜索顺序
- 在实际 UPPAAL 实现里，bounding 和 heuristic guidance 如何工作
- 语义上的 optimality 与搜索引导质量之间的区别

对本仓库来说，核心问题是：

"在走向完整 priced zones 之前，标准 zone / DBM 机械如何被复用来得到可实践的代价引导探索？"

## 它和 `behrmann03` 其他子论文是什么关系

这篇是 priced 簇里的实现桥梁。

- 如果你想先补理论起点，先读 [paper-d/README_zh.md](../paper-d/README_zh.md)。
- 如果你想再往前走到一般线性价格下的 priced-zone symbolic object，下一篇读 [paper-f/README_zh.md](../paper-f/README_zh.md)。

## 在本仓库中的对应位置

- 核心 DBM API：`UDBM/include/dbm/dbm.h`
- Priced federation 类型：`UDBM/include/dbm/pfed.h`
- 高层 wrapper 表面：`pyudbm/binding/udbm.py`

更具体地说：

- 这篇是本地最强的一座桥，把普通 DBM 操作和代价引导搜索连了起来
- 它表明搜索顺序与剪枝也是 symbolic-state story 的一部分，不只是数据结构本身

## 为什么它对 UDBM 特别重要

如果你的出发点是普通 DBM / zone 机械，那么这是 thesis 里最偏实现的一篇 priced 论文。

当你关心的是“实际怎么跑 priced-state exploration”，而不只是抽象问题定义时，这篇尤其有用。

## 如何阅读

如果你想按 priced 这条线顺着读，建议在 [paper-d/README_zh.md](../paper-d/README_zh.md) 之后读它。

如果你真正想看的是一般线性价格情形下更完整的 priced-zone 机械，就继续看 [paper-f/README_zh.md](../paper-f/README_zh.md)。
