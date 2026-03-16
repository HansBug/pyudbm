# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这篇 thesis 是最贴近 UDBM 本体的长篇参考之一。它不只讲抽象的 timed automata 理论，而是深入到 DBM 的数据结构、操作、normalization、存储以及实现取舍。

如果说 `by04` 是最好的紧凑型教程，那么这篇就是更偏实现导向的深挖版。

## 阅读时要抓住什么

不建议把整本 thesis 等权来读。对 UDBM 工作来说，建议重点关注：

- DBM 数据结构和 canonical representation
- symbolic exploration 需要的完整 DBM 操作集
- normalization，特别是带 clock-difference constraints 的情形
- 压缩和状态存储技术

对本仓库来说，最关键的问题是：

"UDBM 里的哪些实现选择，其实是有理论支持的算法决定，而不是随手写出来的库工程细节？"

## 在本仓库中的对应位置

- 核心 DBM API：`UDBM/include/dbm/dbm.h`
- Federation 与更高层 symbolic set 支持：`UDBM/include/dbm/fed.h`
- 紧凑存储机制：`UDBM/include/dbm/mingraph.h`、`UDBM/src/mingraph_write.c`
- 暴露历史操作的高层包装：`pyudbm/binding/udbm.py`
- 恢复历史行为的测试：`test/binding/test_api.py`

更具体地说：

- thesis 里的 DBM 操作，和 `up`、`down`、`updateValue`、`freeClock`、emptiness / containment 检查直接对应
- normalization 的讨论，有助于理解 `dbm.h` 与 wrapper 里的 extrapolation 风格公开操作
- 压缩相关内容，有助于理解 UDBM 已经存在的 `mingraph`、hashing 与存储优化代码

## 为什么它对 UDBM 特别重要

这篇 thesis 和 UDBM 真实的工程形态非常接近：它面对的是验证工具约束下的生产级 symbolic timing library。

当你需要解释为什么库里会暴露某种操作、为什么要保持 canonical closure、或者为什么会有看上去像“内部优化杂项”的存储与压缩机制时，它尤其有用。

## 如何阅读

建议选择性阅读。先读 DBM 与 normalization 相关章节；如果你在动 `mingraph`、hashing 或表示层问题，再继续读存储 / 压缩部分。

后面关于 partial-order reduction 和 committed locations 的部分，对理解 `UPPAAL` 背景仍然有价值，但和本仓库 wrapper 表层 API 的直接关系相对更弱。
