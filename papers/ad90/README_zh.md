# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这是 timed automata 最早的一批原始论文之一。它对 UDBM 的价值，不在于直接讲 DBM，而在于给出了后来 zone / DBM 工作所依赖的 `clock + guard + reset` 基本模型。

如果说 `by04` 回答的是“怎样对 zone 做符号算法”，那这篇更偏向回答“clock 和 timed automata 这个对象本身到底是什么”。

## 阅读时要抓住什么

建议重点关注：

- 作为自动机状态组成部分的实值 clocks
- guard 和 reset 这套基本时间机制
- timed traces 与语言论视角
- 可判定与不可判定的边界

对 UDBM 来说，最关键的问题是：

"后来的 zone 和 DBM 算法，究竟是在表示一个什么样的 timed automaton 对象？"

## 在本仓库中的对应位置

- 以 clock 为中心的高层 DSL：`pyudbm/binding/udbm.py`
- 原生 clock-constraint 操作：`UDBM/include/dbm/dbm.h`
- 面向兼容性的 API 测试：`test/binding/test_api.py`

更具体地说：

- `Clock` 和 `Constraint` 保留了论文里的 clock / guard 视角
- reset 风格操作对应 `Federation.updateValue(...)`、`Federation.resetValue(...)`、`Federation.setZero()`、`Federation.setInit()`
- 多个 clock bound 的合取，最终对应由 `Federation` 包装的符号约束对象

## 为什么它对 UDBM 特别重要

UDBM 并不直接实现 timed automata 的语法树，而是在实现其下层的 symbolic clock-constraint 层。这篇论文解释了为什么 wrapper 应该保持以 clock 为中心，而不是退化成匿名矩阵 helper。

它也提醒我们：后来的 zone 文献，本质上是在 timed automaton 模型之上做符号化优化，而不是把原模型替换掉。

## 如何阅读

如果你想先看历史源头，可以放在 `by04` 之前读；如果你已经先读了 `by04`，那它适合作为回填 formal roots 的一篇。

可获取性说明：
本目录里的 `paper.pdf` 是 Springer 章节落地页当前可获取的预览 PDF：

- https://page-one.springer.com/pdf/preview/10.1007/BFb0032042

它不是完整章节全文。针对这篇 ICALP 1990 chapter，在收集阶段没有找到合法公开的完整 PDF。
