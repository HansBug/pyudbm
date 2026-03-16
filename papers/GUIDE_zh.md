# 论文总导读

这个目录收集的是理解 UDBM 为什么会长成现在这个样子时，最值得读的几篇理论论文。

## 建议阅读顺序

1. `ta_tools`
   这是 timed automata 语义和 DBM 的基础入口，先读它。
2. `llpy97`
   这一篇补 minimal graph 存储与紧凑 DBM 表示。
3. `bblp04`
   这一篇补外推与抽象为什么能保证终止。
4. `dhlp06`
   这一篇解释 subtraction 为什么会离开凸世界，以及为什么必须要 federation。
5. `behrmann03`
   这是更大的综合视角：unions of zones、CDD、共享和更完整的 UPPAAL 架构。

如果你只想最短路径补上 `ta_tools` 缺的那一块，那么可以从 `ta_tools` 直接跳到 `dhlp06`，再回头读 `llpy97` 和 `bblp04`。

## 每篇论文分别起什么作用

### `ta_tools`

作用：
给出 timed automata 语义、zones、DBMs 和基本符号算法的基础。

它为 UDBM 提供的主要理论支撑：

- 凸 zone 的语义
- canonical DBM 的视角
- `delay`、`past`、`reset`、`guard intersection` 这些基本操作

仓库里的对应位置：

- `pyudbm/binding/udbm.py`
- `UDBM/include/dbm/dbm.h`
- `test/binding/test_api.py`

### `llpy97`

作用：
解释 minimal graph 和 DBM 的紧凑存储。

它为 UDBM 提供的主要理论支撑：

- 为什么会有 `mingraph`
- 为什么 canonical DBM 虽然适合运算，但不一定是最佳存储形式

仓库里的对应位置：

- `UDBM/include/dbm/mingraph.h`
- `UDBM/src/mingraph_write.c`

说明：
这个目录目前只有 metadata 和来源说明，还没有拿到 primary-source PDF。

### `bblp04`

作用：
给出 zone-based verification 里的 lower / upper bound abstraction。

它为 UDBM 提供的主要理论支撑：

- 为什么 extrapolation 是安全的
- 为什么 extrapolation 能帮助保证终止
- 为什么会存在多种外推方案

仓库里的对应位置：

- `UDBM/include/dbm/dbm.h`
- `pyudbm/binding/udbm.py`

### `dhlp06`

作用：
给出 DBM subtraction 以及 federation 最直接的理论动机。

它为 UDBM 提供的主要理论支撑：

- zone subtraction
- 非凸结果
- 用 DBM 的并来表示结果
- subtraction 后的规约与简化

仓库里的对应位置：

- `UDBM/include/dbm/fed.h`
- `UDBM/src/fed.cpp`
- `pyudbm/binding/udbm.py`
- `srcpy2/udbm.py`

### `behrmann03`

作用：
从更高层次综合说明 UPPAAL 周边所使用的符号数据结构。

它为 UDBM 提供的主要理论支撑：

- 为什么 unions of zones 在工具层面重要
- 为什么 CDD 曾被作为替代方案探索
- 为什么共享、存储布局和 priced 扩展重要

仓库里的对应位置：

- `UDBM/include/dbm/fed.h`
- `UDBM/include/dbm/pfed.h`
- `UDBM/include/dbm/partition.h`
- `UDBM/src/partition.cpp`

## 这些论文与本仓库 Python wrapper 的关系

本仓库恢复中的 Python API `pyudbm/binding/udbm.py`，并不是在包一层原始矩阵函数而已。它试图在现代绑定层之上重建历史上的 `Context` / `Clock` / `Federation` 编程模型。

因此：

- `ta_tools` 说明这个 DSL 在操作的基础 symbolic zone 层是什么
- `dhlp06` 说明为什么 `Federation` 必须保持为真正的 union 对象，而不能退化成单个 DBM
- `bblp04` 说明为什么 `extrapolateMaxBounds` 这类方法应该存在于公开接口里
- `llpy97` 说明原生 UDBM 中已经存在的压缩存储机制背后的理论
- `behrmann03` 说明这些设计背后的更大架构方向

## 实用建议

如果你是为了本仓库的实现工作来读这些论文，建议这样用：

- 先看 `ta_tools/GUIDE_zh.md`
- 然后看 `dhlp06/GUIDE_zh.md`
- 再看 `bblp04/GUIDE_zh.md`
- 当你碰 `mingraph` 相关代码时看 `llpy97/GUIDE_zh.md`
- 当你需要更大的 UPPAAL 语境时看 `behrmann03/GUIDE_zh.md`
