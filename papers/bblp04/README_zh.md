# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

如果你想理解 UDBM 为什么要暴露各种外推操作，以及为什么会有 `max-bounds`、`LU-bounds` 和 diagonal 变体，这篇论文就是最直接的理论来源。

在这组论文里，它是关于 zone abstraction 与终止性最干净的一篇。

## 阅读时要抓住什么

建议重点关注：

- 为什么直接做 zone exploration 可能不终止
- 为什么基于 lower / upper bounds 的 abstraction 仍然保持验证目标
- 这种 abstraction 是如何由每个 clock 的常数参数化的
- 不同外推方案如何在精度与收敛性之间折中

对 UDBM 来说，最关键的问题是：

"外推到底忘掉了什么信息，为什么这样做还是安全的？"

## 在本仓库中的对应位置

- 底层外推函数：`UDBM/include/dbm/dbm.h`
- Python 高层包装：`pyudbm/binding/udbm.py`
- 对历史行为的测试覆盖：`test/binding/test_api.py`

更具体地说，对应的是：

- `dbm_extrapolateMaxBounds(...)`
- `dbm_diagonalExtrapolateMaxBounds(...)`
- `dbm_extrapolateLUBounds(...)`
- `dbm_diagonalExtrapolateLUBounds(...)`
- `Federation.extrapolateMaxBounds(...)`

## 为什么它对 UDBM 特别重要

如果不读这篇论文，外推方法看起来很像一些“黑盒性能开关”。读完以后，你会知道它们其实是带有正确性语义的抽象操作。

这很重要，因为 UDBM 不只是 DBM 操作容器，它还是 UPPAAL 风格符号验证中保证状态空间探索终止的那套机制的一部分。

## 如何阅读

建议放在 `by04` 之后读。如果你当前最关心的是 Python API，那么可以先读 abstraction 的定义，再回头对照 `Federation.extrapolateMaxBounds(...)` 和 `dbm.h` 里的原生声明。
