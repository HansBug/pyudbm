# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md) 中 Paper C 的拆分版本。

它对应根 PDF 第 99-114 页，主题是把 Clock Difference Diagrams (CDDs) 作为有限个 zone 并集的紧凑表示。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis summary 对这篇内嵌论文的标题说明是：

`Efficient Timed Reachability Analysis using Clock Difference Diagrams`

thesis 中给出的发表历程是：

- 作为 `BRICS Report Series RS-98-47` 发表，时间为 1998 年 12 月
- 在 `CAV'99` 上报告，并收录于 `LNCS 1633`

## 阅读时要抓住什么

建议重点关注：

- CDD 数据结构本身
- CDD 上的布尔集合操作
- 如何把 zone 编码成 CDD，以及如何判断一个 zone 是否包含于某个 CDD
- 如何用 CDD 压缩 timed reachability analysis 里的 passed set
- 论文往 fully symbolic 方向推进，而不仅是“用 DBM 存 passed list”

对本仓库来说，核心问题是：

"把有限个 zone 的并做成一等表示，和单纯维护一个 DBM 列表相比，到底多带来了什么？"

## 在本仓库中的对应位置

- Federation 类型与操作：`UDBM/include/dbm/fed.h`
- Federation 实现：`UDBM/src/fed.cpp`
- Priced federation 类型：`UDBM/include/dbm/pfed.h`
- Python 高层 `Federation` 包装：`pyudbm/binding/udbm.py`

更具体地说：

- 这篇是本地最适合解释“为什么非凸 symbolic set 值得显式表示”的论文
- 它给出了一个 CDD 路线的替代方案；虽然当前 UDBM 主要走 federation 路线，但这个架构背景依然重要
- 它把 symbolic-state 的存储压力直接和表示选择联系了起来

## 为什么它对 UDBM 特别重要

这是 thesis 里第一篇真正进入 UDBM 风格数据结构问题的论文。

如果你想找一篇仓库内本地论文来说明“每个 symbolic state 只放一个 DBM 往往不够”，优先从这篇开始。

## 如何阅读

如果你的问题是非凸 symbolic set、CDD、federation 一类对象，或者 symbolic-state compaction，六篇里应先读这篇。

如果你接下来更关心的是最优代价可达性，就继续看 [paper-d/README.md](../paper-d/README.md)。
