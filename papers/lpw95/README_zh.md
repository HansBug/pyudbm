# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这篇是早期 `UPPAAL` 的直接基础论文之一。它讨论的是实时模型检测里的两个实际爆炸问题，并用 symbolic constraints 与 compositional 技术去解决。

在这组论文链条里，它是 timed-automata 理论走向真实验证工具架构的桥。

## 阅读时要抓住什么

建议重点关注：

- 为什么 region-based verification 在实践里过细、过大
- 如何通过求解简单的 clock-constraint systems 来做 symbolic verification
- on-the-fly exploration 的作用
- compositional quotienting 的角色，即使这部分并不直接在本仓库里实现

对 UDBM 来说，最关键的问题是：

"为什么高效操作 clock-constraint systems，会成为整条工程路线的核心？"

## 在本仓库中的对应位置

- 核心 clock-constraint 机制：`UDBM/include/dbm/dbm.h`
- symbolic set 操作的 federation 支持：`UDBM/include/dbm/fed.h`
- 对库角色的公开描述：`UDBM/README.md`
- 建立在 symbolic 操作之上的高层兼容 wrapper：`pyudbm/binding/udbm.py`

更具体地说：

- 论文中的 symbolic clock constraints，是 UDBM 后来 DBM 风格操作的概念前身
- on-the-fly symbolic state exploration 解释了为什么 `up`、`down`、intersection、update 这些操作如此核心
- 它作为 `UPPAAL` 基础论文的身份，也解释了为什么 UDBM 是一个可复用的 symbolic engine，而不是一个一体化 model checker

## 为什么它对 UDBM 特别重要

这篇论文有助于解释：为什么库会围绕高效 symbolic-state primitives 来设计，而不是围绕显式 region 对象，或者完整的一站式验证工作流。

它也有助于把两层责任分清：
UDBM 提供 constraint technology，更大的 model-checking algorithm 则在其上层。

## 如何阅读

建议放在 `ta_tools` 之后读，看看理论是如何进入早期 symbolic tool design 的。

如果你只关心最贴近 UDBM 的部分，优先看 symbolic constraint solving 相关章节，quotienting 部分可以放后。
