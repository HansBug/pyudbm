# 导读

## 在整套论文中的位置

这篇论文是整组材料的入口。它提供了 timed automata、zone 和 DBM 的语义与算法基线。如果你想先搞清楚 UDBM 究竟在操作什么对象，应当先读它。

它讲得比较充分的内容：

- timed automata 的语义
- 用 zone 做符号语义
- 用 DBM 表示凸 zone
- zone / DBM 的核心操作
- 为保证终止性的 normalization

它对 UDBM 来说讲得还不够的内容：

- 作为一等对象的 federation，也就是非凸集合表示
- DBM subtraction 作为核心算法
- minimal graph 压缩作为独立的数据结构主题
- LU-bound abstraction 的专门理论

## 阅读时要抓住什么

建议重点读第 2 到第 4 节。这里最重要的不是某一个单独定理，而是它建立了一个统一视角：

- 一个 symbolic state 可以看成 “location + zone”
- 一个凸 zone 可以被 canonical DBM 表示
- 验证算法是由 `up`、`down`、reset、guard intersection 和 normalization 这些操作拼出来的

这正是 UDBM 基础 DBM 操作所在的概念层。

## 在本仓库中的对应位置

- Python 高层 DSL：`pyudbm/binding/udbm.py`
- 原生 DBM 操作与外推接口：`UDBM/include/dbm/dbm.h`
- 历史兼容 API：`srcpy2/udbm.py`
- 绑定层行为测试：`test/binding/test_api.py`

更具体地说：

- clock constraint 和 clock difference 对应 `Clock`、`VariableDifference`、`Constraint`
- symbolic zone 操作对应 `Federation.up()`、`Federation.down()`、`Federation.updateValue()`、`Federation.freeClock()`、`Federation.setZero()`、`Federation.setInit()`
- 凸近似对应 `Federation.convexHull()`

## 读它时要带着什么问题

把这篇论文当成对这个问题的回答：

"单个 DBM 在语义上到底表示什么？"

不要指望它回答下面这些问题：

- 为什么需要 `fed_t`
- 为什么 subtraction 会返回 union
- 为什么 `mergeReduce`、`expensiveReduce` 会重要
- 为什么要做 minimal graph 存储

这些问题要靠后面的论文来补齐。
