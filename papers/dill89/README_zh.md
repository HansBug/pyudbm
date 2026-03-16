# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这篇是后续 timed automata 与 zone 文献之前的重要历史前驱。它还不是后来 `UPPAAL` 意义上的 DBM 论文，但它非常关键，因为它展示了验证工作如何从 untimed state graph 走向 dense-time symbolic timing constraints。

它在这条发展线里，比 `ta_tools`、`ad90` 和后来的 zone 论文都更早。

## 阅读时要抓住什么

建议重点关注：

- 带上下界 delay 的连续时间验证
- 附着在自动机状态上的 symbolic timer-state 表示
- 作为验证对象的凸 timing regions
- 从 speed-independent verification 走向 timing-aware verification 的转变

对 UDBM 来说，最关键的问题是：

"在后来的 DBM 术语稳定下来之前，symbolic timing constraints 是怎样先成为一等验证对象的？"

## 在本仓库中的对应位置

- 对 symbolic timing constraints 的核心 DBM 操作：`UDBM/include/dbm/dbm.h`
- Federation / symbolic set 扩展层：`UDBM/include/dbm/fed.h`
- 对 symbolic zones 做高层操作的 Python wrapper：`pyudbm/binding/udbm.py`

更具体地说：

- timer-state 推理是现代 zone 操作的历史祖先
- timing constraints 上的状态空间操作，对应后来的 `up`、`down` 和 reset 风格更新
- containment 与 emptiness 检查，则延续了同一套 symbolic verification 视角，只是表示法更现代

## 为什么它对 UDBM 特别重要

如果不读这类论文，DBM 很容易看起来像某种纯技术性的矩阵技巧。这篇能帮助你看到更深的一层：实时验证需要一种能表示“可能 clock valuation 集合”的符号对象。

因此，它很适合作为一种历史上的纠偏，提醒我们 UDBM 不是“单纯的矩阵库”。

## 如何阅读

建议把它当成历史动机材料来读，而不是当成当前 UDBM API 设计说明书。

如果你是为了实现工作来读，最好和 `ta_tools` 或 `by04` 搭配，这样可以把它较早期的 timer-region 叙述翻译到后来的 zone / DBM 语言里。
