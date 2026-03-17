# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这个目录保存的是母论文 [Data Structures and Algorithms for the Analysis of Real Time Systems](../README.md) 中 Paper B 的拆分版本。

它对应根 PDF 第 77-98 页，主题是层次化 `state/event` 系统、superstate reachability 的复用，以及把这种复用和组合式符号验证结合起来。

本目录下的 [paper.pdf](./paper.pdf) 是从上级 [../paper.pdf](../paper.pdf) 中拆出来的版本；规范完整记录仍然以上级 thesis 条目为准。

## 发表状态

thesis summary 对这篇内嵌论文的标题说明是：

`Verification of Hierarchical State/Event Systems using Reusability and Compositionality`

thesis 中给出的发表历程是：

- 早期版本发表于 `TACAS'99`，收录于 `LNCS 1579`
- 完整版本发表于 `Formal Methods in System Design`，21 卷 2 期，2002 年 9 月

## 当前精修版本地阅读稿具体包含什么

本地的 [content.md](./content.md) 现在已经把整篇论文的层次化论证链条保住了。它明确保留了：

- Fig. 1 的 toy train 示例以及与 flattening 的直接对照
- Fig. 2 那个 simple / complex substates 动机例子
- HSEM 的完整形式化模型，包括 configurations、activity semantics、guards 和 operational rules
- reusable reachability 的主体，包括 `Init`、Algorithm 1 和相关引理
- compositional extension，包括 sorts、`CB_I`、dependency closure 和 Algorithm 2
- `Init` / `Dep` 的 syntactic approximation
- 实验部分，包括 hierarchical cell benchmark family、运行时间曲线以及最后的 reachability-distribution 表

因此，这篇论文现在呈现出来的不只是“复用旧的 reachability 结果”，而是一条从 flat compositional search 走向 hierarchy-aware symbolic reasoning 的完整桥梁。

## 阅读时要抓住什么

建议重点关注：

- 如何复用更高层 superstate 的已有 reachability 结果
- reachability question 如何沿层次结构被拆解
- 如何在受限子系统上做 compositional backward step
- `Init`、`lowest(X)`、sort 与 dependency closure 如何共同把搜索限制在小范围内
- benchmark 设计本身，因为它说明作者预期哪类 hierarchy 会真正带来收益

对本仓库来说，核心问题是：

"在进入 timed domain 之前，这篇 thesis 是如何从普通 symbolic compositionality 走到结构感知复用的？"

## 它和 `behrmann03` 其他子论文是什么关系

这篇补完了 pre-timed 的 `visualSTATE` 双篇结构。

- 如果你想看 flat system 的 compositional 背景，先读 [paper-a/README_zh.md](../paper-a/README_zh.md)。
- 如果你真正关心的是非凸 symbolic set 和更贴近 UDBM 的数据结构问题，下一篇看 [paper-c/README_zh.md](../paper-c/README_zh.md)。

## 在本仓库中的对应位置

和 paper A 一样，这篇更偏背景，而不是 UDBM API 的直接来源。

它在这里最接近的价值是：

- 展示 thesis 如何把 symbolic reuse 当成一个工程问题来处理
- 解释后来 UPPAAL 为什么持续寻找能够避免重复全局探索的表示与算法
- 展示结构分解与行为依赖是如何被放进同一条实现导向的验证叙述里

## 为什么它对 UDBM 特别重要

这篇不是关于 DBM、federation 或 priced zones 的论文。它的重要性主要在于：它补上了 thesis 更广义的 symbolic verification 发展轨迹。

它对 UDBM 的价值是间接的，但并不弱，因为它展示了作者在进入 timed systems 前就已经偏好“可复用、结构感知”的 symbolic exploration。

## 如何阅读

如果你想补完整的 pre-timed 背景，可以在 [paper-a/README_zh.md](../paper-a/README_zh.md) 之后继续读这篇。

如果你的实际目标是非凸 symbolic set 或 timed / priced 结构，就直接跳到 [paper-c/README_zh.md](../paper-c/README_zh.md)。
