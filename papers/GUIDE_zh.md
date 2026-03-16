# 论文总导读

这个目录收集的是理解 UDBM 以及本仓库 wrapper 为什么会长成现在这个样子时，最值得读的一组理论论文、工具论文和历史背景文献。

## 建议阅读路径

### 面向本仓库实现工作的主线

1. `ta_tools`
   先建立 timed automata、zones、DBMs 和基本 symbolic 算法的基线。
2. `by04`
   然后补 regions、zones、DBMs 和验证算法的最佳紧凑教程。
3. `dhlp06`
   接着补 federation 与 subtraction 的理论动机。
4. `bblp04`
   再补外推、抽象与终止性的理论。
5. `llpy97`
   动 `mingraph` 和紧凑存储时读它。
6. `bengtsson02`
   需要更深入的 DBM / normalization / 存储实现视角时读它。

### 面向工具语境的补充路径

- `lpw95`
  早期 `UPPAAL` 的 symbolic / compositional verification 基础。
- `lpy97`
  `UPPAAL` toolbox 与设计准则的短综述。
- `bdl04`
  更成熟的 `UPPAAL` 教程，偏建模模式与实际使用。
- `behrmann03`
  federation、CDD、共享、priced extension 等更大系统视角。

### 面向历史根源的补线路径

- `dill89`
  更早的 dense-time symbolic verification 前驱。
- `ad90`
  原始 timed automata 源头论文。
- `rokicki93`
  normalization 文献线上的历史引用点；本地没有可读全文。

如果你只想走最短路径，直接读：
`ta_tools -> by04 -> dhlp06 -> bblp04 -> llpy97`。

## 每篇论文分别起什么作用

### `ta_tools`

作用：
提供 timed automata 语义、zones、DBMs 和基本 symbolic 算法的基础。

它为 UDBM 提供的主要理论支撑：

- 凸 zone 的语义
- canonical DBM 的视角
- `delay`、`past`、`reset`、`guard intersection` 这些基本操作

### `by04`

作用：
给出 timed automata 语义、regions、zones、DBMs 与验证算法的紧凑型总教程。

它为 UDBM 提供的主要理论支撑：

- 为什么实践里要从 regions 转向 zones
- canonical DBM 如何编码 zone
- 验证工具反复需要哪些 symbolic 操作
- 为什么 normalization / bounded abstraction 重要

### `dhlp06`

作用：
给出 DBM subtraction 以及 federation 最直接的理论动机。

它为 UDBM 提供的主要理论支撑：

- zone subtraction
- 非凸结果
- 用 DBM 的并来表示结果
- subtraction 后的规约与简化

### `bblp04`

作用：
给出 zone-based verification 里的 lower / upper bound abstraction。

它为 UDBM 提供的主要理论支撑：

- 为什么 extrapolation 是安全的
- 为什么 extrapolation 能帮助保证终止
- 为什么会存在多种外推方案

### `llpy97`

作用：
解释 minimal graph 和 DBM 的紧凑存储。

它为 UDBM 提供的主要理论支撑：

- 为什么会有 `mingraph`
- 为什么 canonical DBM 虽然适合运算，但不一定是最佳存储形式

### `bengtsson02`

作用：
从实现视角深入讨论 clocks、DBMs、states、normalization 与存储。

它为 UDBM 提供的主要理论支撑：

- symbolic exploration 背后的完整 DBM 操作集
- 带 difference constraints 的 normalization
- 存储、压缩与 hashing 的动机

### `lpw95`

作用：
早期 `UPPAAL` 的 symbolic 与 compositional model checking 基础论文。

它为 UDBM 提供的主要理论支撑：

- 为什么求解 clock-constraint systems 是核心
- 为什么实践里 symbolic state exploration 优于显式 region 处理
- 为什么 UDBM 处在 model-checking stack 的下层而不是整套工具本身

### `lpy97`

作用：
简明介绍 `UPPAAL` toolbox 与其面向用户的设计。

它为 UDBM 提供的主要理论支撑：

- 为什么 constraint solving 与 on-the-fly reachability 是引擎重心
- 为什么可用性和可读的 symbolic 建模表达同样重要

### `bdl04`

作用：
面向实际建模、查询和模式的 `UPPAAL` 教程。

它为 UDBM 提供的主要理论支撑：

- symbolic engine 所服务的用户侧 timed-automata 方言
- 为什么高层 clock-oriented API 比原始矩阵 helper 更重要

### `behrmann03`

作用：
从更高层次综合说明 UPPAAL 周边所使用的符号数据结构。

它为 UDBM 提供的主要理论支撑：

- 为什么 unions of zones 在工具层面重要
- 为什么 CDD 曾被作为替代方案探索
- 为什么共享、存储布局和 priced 扩展重要

### `dill89`

作用：
从 timing assumptions 走向 symbolic dense-time verification 的历史前驱。

它为 UDBM 提供的主要理论支撑：

- 早期 symbolic timing-state 表示的思路
- 为什么要把 clock valuation 的集合当作符号对象来表示

### `ad90`

作用：
timed automata 的原始语言论源头。

它为 UDBM 提供的主要理论支撑：

- 后来各种 symbolic technique 底下的 `clock / guard / reset` 模型
- zone 与 DBM 方法后来实际编码的 formal timed-automaton 对象

### `rokicki93`

作用：
normalization 文献线里的历史引用点。

它为 UDBM 提供的主要理论支撑：

- 主要体现在后来被 `by04` 与 `bengtsson02` 继续引用的 normalization 背景

说明：
`rokicki93` 在最初收集阶段和本次补充尝试中，都没有找到合法公开可下载的全文 PDF。

## 这些论文与本仓库 Python wrapper 的关系

本仓库恢复中的 Python API `pyudbm/binding/udbm.py`，并不是在包一层原始矩阵函数而已。它试图在现代绑定层之上重建历史上的 `Context` / `Clock` / `Federation` 编程模型。

因此：

- `ad90` 和 `dill89` 解释了以 clock 为中心的 symbolic reasoning 的更早语义根源
- `ta_tools` 和 `by04` 解释了这个 DSL 所操作的单个 zone / DBM 层
- `dhlp06` 说明为什么 `Federation` 必须保持为真正的 union 对象，而不能退化成单个 DBM
- `bblp04` 说明为什么 `extrapolateMaxBounds` 这类方法应该存在于公开接口里
- `llpy97` 和 `bengtsson02` 说明原生 UDBM 中已经存在的压缩存储与实现机制背后的理论
- `lpw95`、`lpy97`、`bdl04` 和 `behrmann03` 说明这个引擎所在的更大 `UPPAAL` 工具语境，以及用户侧对它的期待

## 实用建议

如果你是为了本仓库的实现工作来读这些论文，建议这样用：

- 先看 `ta_tools/GUIDE_zh.md`
- 然后看 `by04/GUIDE_zh.md`
- 再看 `dhlp06/GUIDE_zh.md`
- 之后看 `bblp04/GUIDE_zh.md`
- 当你碰 `mingraph`、存储或更底层 DBM 机制时，去看 `llpy97/GUIDE_zh.md` 和 `bengtsson02/GUIDE_zh.md`
- 当你在想高层 API 的易用性和建模风格时，看 `lpy97/GUIDE_zh.md` 与 `bdl04/GUIDE_zh.md`
- 当你需要更大的 `UPPAAL` 架构语境时，看 `behrmann03/GUIDE_zh.md`
