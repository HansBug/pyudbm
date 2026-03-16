# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Clocks, DBMs and States in Timed Systems](../README.md) 中 Paper B 的拆分版本。

它对应 thesis 第 45-66 页，主题是带 clock-difference constraints 的 timed automata reachability analysis。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis 对这篇内嵌论文的说明是：

`Johan Bengtsson and Wang Yi. Reachability Analysis of Timed Automata Containing Constraints on Clock Differences. Submitted for publication.`

## 阅读时要抓住什么

建议重点关注：

- 旧的 normalization 方法为什么会在 difference constraints 下出错或失去正确性
- 为什么仅靠普通 maximal-clock normalization 不够
- 两个新 normalization 算法分别怎么做、代价有什么不同
- 论文为什么认为支持 difference constraints 不必带来无法接受的额外开销

对本仓库来说，关键问题是：

"一旦把 clock-difference guard 当成一等输入而不是边角特性，DBM 库到底要额外承担什么正确性责任？"

## 在本仓库中的对应位置

- DBM normalization 及相关操作：`UDBM/include/dbm/dbm.h`
- wrapper 暴露的高层语义：`pyudbm/binding/udbm.py`
- 面向兼容性的 zone 行为测试：`test/binding/test_api.py`

更具体地说：

- 它解释了为什么像 `x - y <= c` 这样的约束绝不是一个小小的 parser 细节
- 它给出了 normalization 逻辑必须和 difference constraints 对齐的理论理由
- 它也是解释为什么 extrapolation 一类行为不能忽略对角信息的最直接本地论文来源

## 为什么它对 UDBM 特别重要

如果你要声称一个 timed-automata 工具“支持 difference constraints”，这篇就是必须先读的 normalization 论文。

只要 wrapper 暴露了自然的时钟差比较语法，这篇论文就是那个公开表面背后正确性负担的主要本地依据。

## 如何阅读

如果你的任务涉及更强的时钟约束、对角约束或者 normalization 行为，建议在 [paper-a/README.md](../paper-a/README.md) 之后立刻读这篇。

如果你接下来更关心的是存储与内存成本，而不是 normalization 正确性，就继续看 [paper-c/README.md](../paper-c/README.md)。
