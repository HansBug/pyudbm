# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这篇论文是对 `by04` 没真正讲开的那部分最直接的理论补充：DBM subtraction，以及 subtraction 为什么会迫使我们引入 federation。

如果你的问题是“UDBM 为什么会有 `fed_t` 和 `Federation.__sub__`”，那就应该先读这篇。

## 阅读时要抓住什么

建议重点关注：

- 一个凸 zone 减去另一个凸 zone，结果可能变成非凸
- 因而单个 DBM 不再足够表达结果
- federation 就是用有限个 DBM 的并来表示这种结果
- 一个好用的 subtraction 算法应尽量让结果小、最好还是互不重叠

对 UDBM 来说，最关键的问题是：

"当 subtraction 把我们带出凸世界之后，怎样还能继续停留在 DBM 技术栈里？"

## 本地精修版现在具体给了什么

本地 `content.md` 现在已经远不止一句“subtraction 可能导出非凸结果”的摘要，而是把这篇对仓库最关键的部分基本都保住了：

- 引言里那个 priorities 例子还在，而且它很具体地展示了非凸可达集是怎样在真实建模语境里出现的
- 预备知识部分已经重新铺好 clock constraints、DBM、zone operations 和 naive subtraction 构造，比较容易直接映射到代码
- timed automata with priorities 那一节也保住了 concrete / symbolic semantics，因此 subtraction 并不是脱离 model-checking 语境孤立讨论的
- subtraction 主体章节已经包括 basic algorithm、minimal constraints 改进、disjoint subtraction，以及几个简单但很实用的 early-stop 情况
- heuristic 章节的两个版本都在：一个是更实用的 efficient heuristic，一个是更昂贵的 facet-aware heuristic
- 实验部分也已经在本地稿里，包括 Fischer 例子以及 timed game / jobshop 的表格，因此你能直接看到 subtraction 细节为什么会影响性能和 reduction，而不只是停在理论层

这套内容放在一起读时，最大的价值在于：它不只是解释 federation 为什么存在，也解释了 federation 里面为什么会继续长出不同的 subtraction / reduction 策略。

## 这篇内部建议怎么读

如果你是为了仓库实现而读，一个很实用的顺序是：

1. 先看引言和那个持续贯穿的 priorities 示例
2. 再直接看 Section 4，把 subtraction 机制本身读透
3. 接着看 Section 5，理解为什么 split 顺序和 reduction 质量会直接影响结果
4. 最后如果你需要把 subtraction 放回完整 model-checking 语境，再回到 Section 3 看 symbolic semantics

这个顺序比按论文原始顺序从头线性往下读，更适合“我现在就是要理解 federation 在代码里为什么这么设计”的场景。

## 在本仓库中的对应位置

- Federation 接口：`UDBM/include/dbm/fed.h`
- Federation 算法实现：`UDBM/src/fed.cpp`
- Python 高层 API：`pyudbm/binding/udbm.py`
- 历史兼容 API：`srcpy2/udbm.py`
- federation 层操作测试：`test/binding/test_api.py`

更具体地说，直接对应的是：

- `fed_t::operator-=`
- `fed_t::subtractDown(...)`
- `fed_t::reduce()`
- `fed_t::expensiveReduce()`
- `fed_t::mergeReduce(...)`
- `fed_t::convexReduce()`
- `Federation.__sub__`
- `Federation.reduce(...)`
- `Federation.predt(...)`

## 为什么它对 UDBM 特别重要

这篇论文正好补上了“DBM 只能表示凸 zone”和“UDBM 实际上在操作 DBM 的并”之间的缺口。

它是下面这些设计最强的一篇论文级依据：

- `fed_t` 为什么存在
- 为什么 subtraction 是 federation 级操作
- 为什么 subtraction 之后还要做简化、规约和合并

它还有一个很重要的价值：当你把论文里的 subtraction 情况、heuristic 和实验放在一起看时，高层 API 里的 subtraction、reduction、`expensiveReduce` 以及 merge 风格清理，就不再像是“顺手加的方便方法”，而会显得更像是 faithfully 表达非凸结果时不可回避的语义成本。

## 如何阅读

建议在 `by04` 之后读。如果你最关心的是历史 Python API，那就把论文内容和 `pyudbm/binding/udbm.py` 里 `Federation` 暴露出来的方法直接对照着看。
