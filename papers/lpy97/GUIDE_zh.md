# 导读

## 在整套论文中的位置

这篇是早期 `UPPAAL` 的简明工具总览。它更偏向解释整个 toolbox、设计准则和使用流程，而不是去证明新的 DBM 定理。

如果你想理解 UDBM 的 symbolic operations 原本是处在怎样的用户工具环境里，这篇很合适。

## 阅读时要抓住什么

建议重点关注：

- `efficiency` 与 `ease of use` 这两个设计准则
- description language、simulator、model checker 的分工
- 基于 constraints 的 reachability-oriented symbolic verification
- diagnostic traces 和交互式建模支持

对本仓库来说，最关键的问题是：

"如果一个高层 wrapper 想贴近历史上的 UDBM / UPPAAL 世界，它应该支撑什么样的工具使用模式？"

## 在本仓库中的对应位置

- 高层 Python DSL 与历史风格用户接口：`pyudbm/binding/udbm.py`
- 包根级兼容导出：`pyudbm/__init__.py`
- 工具叙事背后的原生 symbolic engine：`UDBM/include/dbm/dbm.h`、`UDBM/include/dbm/fed.h`
- 恢复公开行为的测试：`test/binding/test_api.py`

更具体地说：

- 论文对 user-oriented modeling 的强调，有助于解释为什么 `Context`、`Clock`、`Federation` 应该作为 Python 一等对象存在
- 基于 constraint-solving 的 reachability 叙事，说明了为什么被包装出来的 API 会以 symbolic operations 为主
- diagnostic 与 simulator 的需求，则解释了为什么即使底层引擎很低层，高层表达式仍然必须可读

## 为什么它对 UDBM 特别重要

这篇论文的价值在于提醒我们：UDBM 所处的是一个有人类建模工作流的工具生态，而不只是算法内核。

对本仓库尤其重要的一点是：恢复历史 binding，不只是把 native calls 暴露出来，还要尽量恢复正确的可用性层。

## 如何阅读

如果你想先快速建立 `UPPAAL` 工具全景，再去读 `bdl04`，这篇很适合作为短导读。

它不是理解 DBM 内部机制的主文献；更适合用来把握 surrounding tool design 和期望的交互风格。
