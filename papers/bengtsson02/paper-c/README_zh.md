# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Clocks, DBMs and States in Timed Systems](../README.md) 中 Paper C 的拆分版本。

它对应 thesis 第 67-92 页，主题是如何降低 symbolic state-space exploration 的内存消耗。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis 对这篇内嵌论文的说明是：

`Johan Bengtsson and Wang Yi. Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems. Technical Report 2001-009, Department of Information Technology, Uppsala University, 2001.`

## 阅读时要抓住什么

建议重点关注：

- packed symbolic state 的表示
- 既压缩 zone 又保持便宜 inclusion check 的方法
- WAIT 与 PASSED 之间的取舍
- timed systems 上的 supertrace 与 hash compaction 思路

对本仓库来说，关键问题是：

"当 state-space 大小本身成为主要瓶颈时，一个 timed-symbolic 引擎应该如何在精确性、包含判断成本和内存占用之间折中？"

## 在本仓库中的对应位置

- 紧凑存储机制：`UDBM/include/dbm/mingraph.h`
- minimal graph 编码实现：`UDBM/src/mingraph_write.c`
- 最终建立在这些 native 选择之上的高层 wrapper API：`pyudbm/binding/udbm.py`

更具体地说：

- 它说明了为什么状态表示成本不只是“单个 DBM 操作快不快”的问题
- 它为内存导向的约简与压缩存储格式提供了背景
- 它也解释了为什么“快速 inclusion check”和“紧凑状态存储”经常是互相拉扯的目标

## 为什么它对 UDBM 特别重要

这篇论文关注的不是用户侧语法，而是真实验证器背后的成本模型。

如果你想理解 UDBM 为什么会有紧凑存储机制，以及验证引擎为什么会如此在意表示形状，这篇就是最相关的论文级参考。

## 如何阅读

如果你的问题集中在内存占用、压缩表示或者 passed list 工程实现上，建议在 [paper-a/README.md](../paper-a/README.md) 之后读这篇。

如果你准备继续往 UPPAAL 引擎语义和更高层工具背景走，再看 [paper-d/README.md](../paper-d/README.md) 和 [paper-e/README.md](../paper-e/README.md)。
