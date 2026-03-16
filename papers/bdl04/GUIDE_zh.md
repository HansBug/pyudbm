# 导读

## 在整套论文中的位置

这是偏工具用户视角的一篇成熟 `UPPAAL` 教程。它不是最适合先读来理解 DBM 内部机制的论文，但当你想理解 symbolic engine 究竟在服务什么样的建模方式时，它非常有用。

和 `lpy97` 相比，这篇对建模特性的覆盖更完整，对实际建模 pattern 的总结也更丰富。

## 阅读时要抓住什么

建议重点关注：

- `UPPAAL` 所采用的 timed automata 方言
- invariants、urgency、committed locations、synchronization channels
- 以 reachability 为中心的查询语言
- 让验证更可行的建模模式

对本仓库来说，最关键的问题是：

"一个高层 UDBM wrapper，应该让什么样的用户建模体验变得自然？"

## 在本仓库中的对应位置

- 历史风格的高层 API：`pyudbm/binding/udbm.py`
- 历史兼容参考实现：`srcpy2/udbm.py`
- 工具层模型背后的原生 symbolic 操作：`UDBM/include/dbm/dbm.h`、`UDBM/include/dbm/fed.h`

更具体地说：

- 自然的 clock 表达式对应 `Context`、`Clock`、`Constraint`
- symbolic zone 更新对应 `Federation.up()`、`Federation.down()`、`Federation.updateValue(...)`、`Federation.freeClock(...)`
- 非凸 symbolic set 对应 `Federation`，而不是单个 DBM

## 为什么它对 UDBM 特别重要

这篇论文对产品方向很有提醒作用。最终用户思考的不是原始矩阵，而是 clocks、guards、resets、urgency 和可达的 symbolic states。

这也正是为什么本仓库应该继续重建历史上的 `Context` / `Clock` / `Federation` 编程模型，而不是停留在低层绑定。

## 如何阅读

建议放在 `lpy97` 或 `by04` 之后读。当你在做 Python ergonomics、示例设计，或者判断什么才算 “自然的高层 API” 时，它尤其有参考价值。

不要把它当作 DBM 算法主文献；那部分应优先看 `by04` 和 `bengtsson02`。
