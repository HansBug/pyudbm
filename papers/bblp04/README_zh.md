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

## 本地精修稿现在能直接提供什么

这篇论文的本地 `content.md` 现在已经不是粗糙抽取稿，而是一份可以直接阅读的精修版；其中已经保留了对这个仓库最有用的那部分内容：

- 引言里围绕 Fig. 1 的动机例子已经整理完整，这是这篇论文里最紧凑也最直接的说明：为什么 lower / upper bounds 要分开看
- 预备章节已经把 TA syntax、具体语义、符号语义、abstraction 的基本定义，以及后续 extrapolation 需要的 DBM 回顾都补在一起
- 语义层面的核心内容已经能直接读：classical maximal-bound abstraction、LU-preorder 和 `a_{≺LU}` 都保留了下来，包括从 bisimulation 走向 simulation-based reachability exactness 的关键转折
- extrapolation 章节不是只留下最后结论，而是四种 operator 都在：`Extra_M`、`Extra_M^+`、`Extra_LU`、`Extra_LU^+`，对应的小几何示意图和 Fig. 3 的包含关系图也都在
- successor computation acceleration 那一节已经完整可读，包括 LU-form DBM、各步操作成本拆解，以及在 LU 形状下用 `LU-Canonize` 替代完整 cubic closure 的算法
- 实现与实验部分已经保留，Table 1 不只是有图片资源，还额外做了可读的 Markdown 转写，因此性能结论不是一句话概述，而是能直接查对原表
- 结尾关于 asymmetric DBM storage 的讨论也保住了；如果你在思考 LU 信息是不是只影响分析、还是也会影响表示与存储设计，这一段很有价值

如果你读这篇论文的目的更偏向 wrapper design 而不是纯理论，那么第 4 节和第 5 节是收益最高的两段，因为它们把语义抽象、具体 DBM 改写和实现代价直接连起来了。

## 论文内部建议阅读路线

如果你不想严格按顺序从头读到尾，一个更贴近仓库工作的路线是：

1. 先读第 1 节后半段和 Fig. 1 相关讨论，把 LU bounds 的动机先吃透
2. 第 2 节只需读到足够重新建立 symbolic semantics 与 DBM 语境
3. 第 3 节要认真读，因为 semantic abstraction 的核心陈述就在这里
4. 然后把第 4 节完整读掉；这一节和 UDBM 里的实际 extrapolation operators 对应得最直接
5. 在看实验前，先把第 5 节读完，因为 `LU-Canonize` 和 LU-form DBM 才真正说明这篇论文为什么不只是 correctness paper，而是 implementation paper

如果你真正想回答的问题不是“timed automaton 是什么”，而是“DBM 库里为什么会有这些具体的外推算子，它们到底换来了什么”，这个阅读顺序会更高效。

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

另外，这篇论文在本地材料里也很特殊：它不是停在“LU abstraction 是正确的”这里，而是进一步解释了 LU 信息为什么会改变 successor computation 本身的代价结构。

## 如何阅读

建议放在 `by04` 之后读。如果你当前最关心的是 Python API，那么可以先读 abstraction 的定义，再回头对照 `Federation.extrapolateMaxBounds(...)` 和 `dbm.h` 里的原生声明。

如果你当前更关心实现细节而不是 API 形状，那么建议从第 4 节直接跳到第 5 节里的 `LU-Canonize` 部分，再回头看实验。
