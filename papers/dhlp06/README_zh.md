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

## 如何阅读

建议在 `by04` 之后读。如果你最关心的是历史 Python API，那就把论文内容和 `pyudbm/binding/udbm.py` 里 `Federation` 暴露出来的方法直接对照着看。
