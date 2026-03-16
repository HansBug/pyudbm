# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这篇 thesis 的范围比这组里的其他论文都更大。若你只想抓一个狭义结果，它不是最好的第一篇；但当你想把 UPPAAL 在 federation、CDD、存储、共享、priced zones 这些方向上的整体图景串起来时，它非常有价值。

可以把它看成“单个算法论文”和“工具整体架构”之间的桥。

## 阅读时要抓住什么

不建议一开始从头到尾通读整本 thesis。对 UDBM 相关工作，建议重点看：

- 关于 CDD 的章节与所收录论文
- 关于 zone 的并、symbolic-state 存储和 coverage 的讨论
- 关于共享和紧凑表示的工程动机

这里最有价值的一点在于：有限个 zone 的并，在 UPPAAL 风格验证里是一个真实的语义与算法对象，而不是某种偶然包装层。

## 在本仓库中的对应位置

- Federation 类型与操作：`UDBM/include/dbm/fed.h`
- Federation 实现：`UDBM/src/fed.cpp`
- Priced federation 类型：`UDBM/include/dbm/pfed.h`
- Federation 规约的 partition 支持：`UDBM/include/dbm/partition.h`、`UDBM/src/partition.cpp`
- Python 高层 `Federation` 包装：`pyudbm/binding/udbm.py`

更具体地说：

- thesis 对 unions of zones 的讨论，解释了为什么 `fed_t` 会是一个独立类型
- 对存储和共享的讨论，帮助理解 `intern()`、hashing 以及紧凑表示
- 更大的 symbolic-state 视角，解释了为什么 UDBM 同时包含显式 federation 支持和压缩 DBM 支持

## 为什么它对 UDBM 特别重要

它不一定是每个具体 API 的直接来源，但它给出了 UDBM 为什么会超出“纯 DBM helper functions”这一层的架构性原因。

如果你想理解下面这些问题，它会很有帮助：

- 为什么非凸 symbolic set 会反复出现
- 为什么 CDD 曾被作为 DBM list 的替代方案来探索
- 为什么 priced 扩展会和普通 federation 并存

## 如何阅读

把它当成选择性深挖的参考，而不是链条里的第一篇。它最适合放在 `by04` 之后，并且是在你已经知道 `fed_t`、`mingraph` 和 extrapolation 这些部件存在之后再读。
