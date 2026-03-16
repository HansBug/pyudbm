# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Clocks, DBMs and States in Timed Systems](../README.md) 中 Paper A 的拆分版本。

它对应 thesis 第 23-44 页，主题就是 DBM 包本身：数据结构、基础操作、normalization，以及内存布局选择。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis 对这篇内嵌论文的说明是：

`Johan Bengtsson. DBM: Structures, Operations and Implementation. Submitted for publication.`

## 阅读时要抓住什么

建议重点关注：

- canonical DBM 与 minimal constraint system
- symbolic exploration 需要的基础检查与变换操作
- DBM 上的 normalization 操作
- dense / sparse zone 的实际存储布局

对本仓库来说，核心问题是：

"UDBM 里的哪些 DBM 操作属于基础算法原语，它们又依赖什么样的表示假设？"

## 在本仓库中的对应位置

- 核心 DBM 操作：`UDBM/include/dbm/dbm.h`
- 紧凑与约简表示：`UDBM/include/dbm/mingraph.h`
- Python 层暴露的历史操作：`pyudbm/binding/udbm.py`

更具体地说：

- `up`、`down`、emptiness check、update 等操作，都直接落在本文的核心操作集合里
- 对 minimal constraints 的讨论，有助于理解为什么“约简存储”与“canonical 操作”是两个不同问题
- 对内存布局的讨论，有助于理解 UDBM 为什么会关心 DBM 的底层存储形状

## 为什么它对 UDBM 特别重要

这是最直接解释 UDBM 里 DBM 层到底应该提供什么能力的一篇论文。

如果你要论证某个 DBM API 是否合理、分析 canonical 假设、或者判断某个能力应该留在 native 层而不是 Python 层，优先读这篇。

## 如何阅读

如果你当前关注的是 DBM 语义、基础操作或者底层表示选择，这篇应该是五篇二级论文里最先读的。

如果你接下来关心的是 difference constraints，就继续看 [paper-b/README.md](../paper-b/README.md)。如果你更关心紧凑存储和 passed list 成本，就继续看 [paper-c/README.md](../paper-c/README.md)。
