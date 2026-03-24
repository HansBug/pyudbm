# UCDD Python Binding 与现有 DBM Binding 联动接入方案

## PR 关联

本方案对应的 GitHub Pull Request：

- PR #8: <https://github.com/HansBug/pyudbm/pull/8>

## 说明

这份文档是 `pyudbm` 仓库内关于 UCDD 接入方案的设计文档。

本文档已经按仓库约定完成 PR 编号回填：

- 首次提交使用不含 PR 编号的临时描述性文件名
- PR 创建后，已将真实 PR 编号回填到文件名前缀
- PR 链接也已回填进本文档，并应与 PR 描述中的文档链接保持双向关联

## 背景与目标

当前仓库已经具备一条以 UDBM 为核心的高层 Python 封装链路：

- 当前 native pybind11 入口位于 `pyudbm/binding/_binding.cpp`
- 本方案建议后续将其重命名为 `pyudbm/binding/_udbm.cpp`，并同步调整扩展模块命名、导入路径和构建配置
- Python 高层 DSL 位于 `pyudbm/binding/udbm.py`
- 公开模型以 `Context` / `Clock` / `Federation` / `DBM` 为主

这条链路已经恢复了历史 binding 的主要使用习惯，但仍然主要停留在：

- 纯 clock-zone 语义
- DBM 与 Federation 语义
- 不包含布尔变量的统一符号图表达

而 UCDD 提供的是另一条更强的符号表示能力：

- BDD
- CDD
- BDD 与 CDD 的混合图
- 面向 timed symbolic analysis 的 delay / past / predt / transition 一类操作

因此，UCDD 的接入目标不能只是“再暴露一个低层 native 模块”，而必须同时解决下面四件事：

1. 盘点 UCDD 对外真正有意义的数据结构与操作边界。
2. 区分哪些对象适合直接暴露到 pybinding，哪些应保持为内部结构。
3. 设计 UCDD 与现有 `DBM` / `Federation` / `Context` 之间的联动方案。
4. 给出一个不会把 `pyudbm` API 撕裂成两套平行体系的渐进式落地计划。

本文档的目标不是立即改代码，而是先把后续接入工作的技术边界、对象模型和阶段计划讲清楚。

## 概念澄清：CDD、DBM、Federation 分别是什么

在进入对象设计和接口分层之前，需要先把一个容易混淆的问题说清楚：

- `CDD` 不是 `Federation` 的别名
- 但在纯 clock 场景下，二者经常可以表达相同的语义集合
- 一旦把 bool 变量纳入同一个符号对象，`CDD` 的表达范围就明显超过 `Federation`

### 一、先看现有 `DBM` / `Federation` 语义

当前仓库中的高层 UDBM API 可以先理解成两层：

- `DBM`：一个凸的 clock zone
- `Federation`：有限个 `DBM` 的并集

例如：

```python
from pyudbm import Context

c = Context(["x", "y"], name="c")

z1 = (c.x <= 3) & (c.y <= 2)
z2 = (c.x >= 8) & (c.x - c.y < 4)
fed = z1 | z2
```

这里可以直观理解为：

- `z1` 是时钟空间里的一块凸区域
- `z2` 是另一块凸区域
- `fed` 是这两块区域的并集

因此，`Federation` 擅长表达的是：

- 纯时钟约束
- 非凸 zone
- zone 的并、交、差、`up`、`down`、`predt` 等操作

但它的语义边界也很明确：

- 它表达的是 clock valuation 的集合
- 它不直接表达布尔变量赋值
- 它也不直接表达“离散条件 + zone”统一混合后的符号图

### 二、CDD 不是“另一种 Federation”，而是“统一决策图表示”

相比之下，UCDD 中的 `cdd`/`CDD` 更适合从“统一决策图对象”来理解，而不是“多个 DBM 的另一种容器”。

可以先用一个不太严格但直观的比喻理解：

- `DBM` 像一块凸多边形
- `Federation` 像若干块凸多边形的并集
- `CDD` 像一张压缩后的判定图，沿着图上的判断分支决定某个状态是否属于该集合

这张图中的判断节点既可以是：

- 布尔变量判断
- clock-difference 约束判断

因此 `CDD` 的核心不是“显式列出若干 DBM”，而是：

- 用图结构共享公共子结构
- 用统一节点体系同时表示纯 BDD、纯 CDD、以及混合 BCDD
- 面向后续 symbolic analysis 继续做 `delay`、`past`、`predt`、`transition` 等运算

### 三、纯 clock 场景下，CDD 与 Federation 的关系

在不引入 bool 变量时，可以把关系理解成：

- `Federation` 更接近“显式的 zone 并集”
- `CDD` 更接近“用决策图压缩组织出来的 zone 表示”

所以在纯 clock 场景下：

- 两者经常可以表示相同的语义集合
- 两者应当可以互转
- 但它们的内部结构和适合承载的后续分析流程并不相同

例如：

```python
from pyudbm import Context

c = Context(["x", "y"], name="c")
fed = ((c.x <= 10) & (c.x - c.y < 3)) | ((c.y <= 2) & (c.x >= 8))
```

这个 `fed` 表示的是纯时钟语义下的非凸状态集合。

按本文档推荐方向，后续应允许：

```python
cdd = CDD.from_federation(fed)
fed2 = cdd.to_federation(require_pure=True)
```

这体现的不是“`CDD` 和 `Federation` 完全一样”，而是：

- 对纯 clock 集合来说，二者应能在语义上对齐
- `CDD` 可以作为 `Federation` 的增强表示层继续承接后续符号运算

### 四、为什么一引入 bool，CDD 就不再等价于 Federation

关键差别在于：`Federation` 只覆盖时钟空间，而 `CDD` 目标是覆盖“离散条件 + 时钟条件”的统一符号状态。

例如，考虑下面这个状态集合：

```text
(door_open ∧ x <= 5) ∨ (!door_open ∧ x <= 2)
```

它的直观含义是：

- 门开着时，允许 `x <= 5`
- 门关着时，只允许 `x <= 2`

在 Python 高层理想接口里，这会更像：

```python
safe = (ctx.door_open & (ctx.x <= 5)) | (~ctx.door_open & (ctx.x <= 2))
```

这里包含了两类信息：

- 布尔离散状态：`door_open`
- 连续时间状态：`x <= 5`、`x <= 2`

这时：

- `Federation` 无法原生表达 `door_open`
- `CDD` 则可以把它作为同一张图中的一类判断节点

因此，一旦进入 mixed bool/clock 场景，`CDD` 就不是“换一种写法的 Federation”，而是语义域真正扩大了。

### 五、项目设计上为什么必须把这层关系讲清楚

这直接决定后续 Python API 应该怎么设计。

如果把 `CDD` 误解成“另一个 Federation 容器”，就容易走到错误方向：

- 只做一个新的 native helper 层
- 继续只覆盖 pure zone 语义
- 忽略 bool 与 clock 的统一建模价值
- 最终把 API 变成两套彼此平行、但都不完整的体系

而本文档所采取的方向是：

- 保留 `Federation` 作为纯 zone 工作流的一等对象
- 让 `CDD` 成为更强的统一符号图对象
- 在纯 clock 场景下支持 `Federation <-> CDD` 互转
- 在 mixed bool/clock 场景下，让 `CDD` 承接 `Federation` 无法直接覆盖的语义能力

## 与经典时间自动机文献的对应关系

上面关于“统一符号状态”的理解，并不是凭空发明出来的，而是和 timed automata
文献中的经典 symbolic semantics 可以对齐。

### 一、经典写法通常是 `(l, Z)` 或 `(l, ν, Z)`

在经典 timed automata / UPPAAL 语境下，一个符号状态通常不会只写成一个 zone，
而更常被理解成：

- `(l, Z)`：离散位置 `l` 加一个 zone `Z`
- `(l, ν, Z)`：若再引入离散变量赋值，则是离散位置 `l`、离散赋值 `ν` 与 zone `Z`

这也是为什么“只讨论 DBM / Federation 的 zone 部分”在形式上不够完整：

- `Z` 只覆盖时钟约束
- `l` 与 `ν` 仍然需要被表示

相关经典出处包括：

- UPPAAL / SPIN 相关论文 *Unification & Sharing in Timed Automata Verification*：
  其中直接把 `(l, Z)` 描述为 symbolic states
  - <https://uppaal.org/texts/spin03.pdf>
- UPPAAL 教程与综述材料中常见的 `<l, z>` 写法：
  其中 `z` 是 zone，通常以 DBM 表示
  - <https://uppaal.org/texts/mm-master.pdf>
- UPPAAL 官方文档关于 symbolic traces 的说明：
  其中也明确 symbolic state 里，active locations 和 discrete variables
  对该状态中的 concrete states 是一致的
  - <https://docs.uppaal.org/gui-reference/symbolic-simulator/symbolic-traces/>

换句话说，经典文献本来就在说：

- 真正的 symbolic state 不是“只有 zone”
- 而是“离散控制部分 + 时间约束部分”

### 二、脚本示例里的 bool 编码，是对经典语义的工程映射

需要明确一点：

- 经典文献通常直接写 `(l, Z)` 或 `(l, ν, Z)`
- 不会逐字写成“用若干 bool 变量来编码 location”

而本项目在 Python / UCDD 层采用的方式是：

- 用 BDD 部分承载 `l` 和 `ν` 这类离散信息
- 用 CDD / DBM 部分承载 `Z` 这类时钟约束

因此，像下面这样的写法：

```python
state = location_open & (ctx.x <= 5)
```

本质上是在做一个工程映射：

- `location_open` 对应经典语义里的 `l`
- `(ctx.x <= 5)` 对应经典语义里的 `Z`

所以应当把它理解成：

- 不是“论文原句就这么写”
- 而是“把经典 timed automata symbolic state 映射到 UCDD 混合 BDD/CDD 表示”

这层映射之所以成立，是因为 UCDD 的实际实现本来就支持：

- 纯 BDD
- 纯 CDD
- 混合 BCDD
- `delay` / `past` / `predt`
- `transition` / `transition_back` / `transition_back_past`

### 三、有了 CDD 后，离时间自动机形式化验证还差多远

这个问题需要分层回答。

#### 1. 若只问“核心 symbolic engine 是否基本具备”

答案是：**已经非常接近。**

只要具备下面这些能力，就已经足以搭出一个时间自动机 reachability /
safety checking 的原型引擎：

- 统一表示 symbolic state：离散部分 + zone
- 时间推进：`delay` / `delay_invariant` / `past`
- 离散迁移：`transition`
- 反向算子：`transition_back` / `transition_back_past` / `predt`
- 片段抽取：`extract_bdd_and_dbm`

从这个意义上说，有了 CDD 之后，确实已经拿到了“时间自动机符号验证器的
核心状态表示与主要算子底座”。

#### 2. 若问“是否已经等于完整 model checker”

答案是：**还没有。**

在一个完整的 timed automata 形式化验证工具里，除了 CDD 这种统一符号状态
表示与算子层之外，通常还需要：

- 自动机/网络层数据结构
- 多模板并发组合与同步语义
- urgent / committed / broadcast / priority 等系统语义
- zone abstraction / extrapolation / subsumption
- passed / waiting 探索框架
- 查询语言，例如 `A[]`、`E<>`
- 诊断轨迹与反例生成
- 更完整的离散数据变量语义

所以更准确的判断应当是：

- 有了 `CDD`，已经基本拿到了“形式化验证器的核心 symbolic engine”
- 但还没有自动得到“完整的时间自动机 model checker”

### 四、这对本项目的直接含义

这也解释了为什么本项目引入 UCDD 后，下一阶段工作重点不应只是“再补几个
native helper”。

更合理的演进路径应该是：

1. 先把 `CDD` 作为统一 symbolic state 对象打磨稳定
2. 在纯 clock 场景下与现有 `Federation` 做好语义对照
3. 在 mixed bool/clock 场景下，把 location / discrete control / zone
   的统一建模方式讲清楚
4. 在此基础上，再往“自动机语义层”和“验证算法层”推进

这也是为什么根目录示例脚本更适合写成“时间自动机控制器”的原因：

- 它能直接展示 `CDD` 不只是另一个 zone 表示
- 它更接近 timed automata symbolic state 的真实使用方式
- 也更接近后续可达性分析、前驱分析、模型检查等工作的真实落地方向

## 现有仓库基线

### 已有 DBM binding 能力

当前仓库已经通过 `pybind11 + CMake + setuptools` 暴露了 UDBM 的一部分高层能力：

- `_NativeConstraint`
- `_NativeDBM`
- `_NativeFederation`

以及建立在其上的高层对象：

- `Clock`
- `Constraint`
- `Context`
- `DBM`
- `Federation`
- `IntValuation`
- `FloatValuation`

这意味着仓库现在已经有三项非常关键的资产：

- 一套稳定的 Python 命名与上下文模型
- 一套已经在测试中使用的 zone/federation 高层语义
- 一套可被复用的 DBM 快照和联邦对象包装方式

所以，UCDD 接入时最重要的原则之一就是：

**不要重新发明另一套完全平行的 clock 命名、DBM 表示、zone 抽取与打印体系。**

### UCDD 在本仓库中的现实定位

根据 `UCDD/include/cdd/cdd.h`、`UCDD/include/cdd/kernel.h`、`UCDD/src/cppext.cpp` 与 `UCDD/test/test_cdd.cpp` 的实际接口和测试覆盖，UCDD 对外并不是“一个纯 CDD 库”，而是：

- 一个统一的决策图系统
- 同时支持 BDD 节点和 CDD 节点
- 支持纯 BDD、纯 CDD、混合 BCDD
- 支持 DBM 和 DD 之间的来回转换与抽取

这点直接影响 Python API 设计：

- 不应把 Python 侧建模成两个完全平行、互不相干的顶级类 `BDD` 与 `CDD`
- 更合适的一等公民是统一的图对象
- 其中“是否纯 BDD”“是否纯 CDD”“是否包含混合底部 BDD”是对象状态，而不是先验类层次

## UCDD 主要数据结构盘点

下面按“概念层数据结构”和“内核实现结构”两类分别盘点。

### 一、建议作为公开概念看待的数据结构

#### 1. 统一 DD 图对象 `cdd`

这是 UCDD C++ 接口里的核心值对象。

它包装了一个 `ddNode*` 根句柄，并负责引用计数维护。这个对象可以代表：

- 纯 BDD
- 纯 CDD
- 混合 BCDD
- `true` / `false` 终端

这也是为什么在 Python 侧更适合先设计统一 `CDD` 类，而不是平行 `BDD`/`CDD` 两套主类。

应暴露级别：

- 必须暴露
- 应作为 UCDD Python 层的核心对象

#### 2. `LevelInfo`

`LevelInfo` 是对每个 decision-diagram level 的解释信息，包含：

- level 对应的是 `TYPE_BDD` 还是 `TYPE_CDD`
- 若是 clock-difference level，其 `clock1` / `clock2` / `diff` 是什么

这个结构对 Python 侧非常重要，因为它是把“内部 level 编号”还原成“用户看得懂的变量语义”的关键桥梁。

应暴露级别：

- 应暴露为只读元数据对象
- 适合做调试、诊断、图结构解释与文档输出

#### 3. `extraction_result`

`extraction_result` 表示从一个 CDD 中抽出首个 DBM 分量后的结果，包含：

- `CDD_part`：剩余图
- `BDD_part`：所抽取 DBM 底部附着的 BDD 条件
- `dbm`：被抽取出的一个 DBM

这个结构对 Python API 很有价值，因为它天然就是 UCDD 与现有 DBM/Federation API 的连接点。

应暴露级别：

- 应暴露
- 但不应原样暴露裸指针
- 应包装成 Python 友好的结果对象

#### 4. `bdd_arrays`

`bdd_arrays` 是把纯 BDD 转成“布尔赋值轨迹数组”后的结果，包含：

- `vars`
- `values`
- `numTraces`
- `numBools`

这实际上是 BDD 的一种扁平枚举表示。

应暴露级别：

- 应暴露
- 但不应在 Python 层停留在裸数组协议
- 应进一步包装为更易理解的 trace / assignment 结构

#### 5. `CddGbcStat` / `CddRehashStat`

这两个结构是运行时统计信息：

- garbage collection 统计
- rehash 统计

它们属于“诊断与实现观测”而不是“核心符号语义”。

应暴露级别：

- 可以暴露
- 但应放在专家/调试层
- 不宜进入首批高层主 API

### 二、只应视为内部实现的数据结构

#### 1. `ddNode`

这是统一节点基类句柄。

它是所有图对象的内部根指针类型，但它并不适合成为 Python 公开类，因为：

- 生命周期依赖 UCDD 自身引用计数体系
- 语义信息不足
- 公开后会诱导用户做错误的节点级操作

结论：

- 不应直接暴露

#### 2. `cddnode_`

这是 CDD 节点的内部结构，包含：

- 公共 node header
- 一个变长 `Elem[]` 数组

它体现了 CDD 多分支区间边的底层布局，但它不是 Python 层应该直接操作的结构。

结论：

- 不应暴露为 Python 对象
- 它的语义应通过 interval/constraint 构造与图打印能力体现

#### 3. `bddnode_`

这是 BDD 节点的内部结构，包含：

- `low`
- `high`

同样只适合留在内部。

结论：

- 不应直接暴露

#### 4. `elem_`

这是 CDD 边元素，包含：

- `child`
- `bnd`

它完全属于内部存储布局。

结论：

- 不应暴露

#### 5. `xtermnode_`

这是在 `MULTI_TERMINAL` 条件编译下使用的额外 terminal 节点。

它在库里有意义，但是否要进入 Python 首批 API，要看仓库是否准备对 multi-terminal 语义做长期承诺。

结论：

- 首版不建议作为公开 API 承诺
- 只在 pybinding 设计时预留空间

#### 6. `chunk_` / `subtable_` / `nodemanager_`

这些结构用于：

- 节点分块分配
- hash subtable
- node manager

它们完全是内存管理实现细节。

结论：

- 明确不暴露

## UCDD 公开语义对象应如何建模

### 结论：Python 层应以“统一 `CDD` 图对象”为中心

推荐的高层对象模型不是：

- `BDD`
- `CDD`
- `MixedCDD`

而是：

- `CDD`
- `CDDContext`
- 若干只读结果与元数据对象

原因如下：

- UCDD 底层本身就是统一 DD 系统
- 许多运算天然对纯 BDD、纯 CDD、混合图都适用
- 同一个对象经过运算后可能从纯 BDD 变成混合图，或从混合图退化成纯 BDD
- 如果 Python 层一开始就把 `BDD` 和 `CDD` 分成两个顶级类，会引入大量不必要的类型转换和语义边界问题

### 建议的公开对象

建议未来在 Python 层形成如下对象集：

- `CDDContext`
- `CDD`
- `CDDLevelInfo`
- `CDDExtraction`
- `BDDTraceSet`

可选的专家级对象：

- `CDDRuntime`
- `CddGbcStat`
- `CddRehashStat`

## 各对象需要支持哪些操作

下面按对象列出建议暴露的操作范围。

### 一、`CDDRuntime` 或等价 runtime 管理层

这层负责包住 UCDD 的全局运行时状态。

必须注意的是，UCDD 当前运行时带有明显的全局性：

- `cdd_clocknum`
- `cdd_varnum`
- `bdd_start_level`
- `cdd_levelinfo`

这意味着它并不是一个天然“无全局状态”的纯值库。Python 接入时必须显式面对这一点，而不是假装它和普通独立对象系统一样。

建议支持的操作：

- `init(maxsize, cache_size, stack_size)`
- `done()`
- `ensure_running()`
- `is_running()`
- `version()`
- `add_clocks(n)`
- `add_bddvars(n)`
- `getclocks()`
- `get_level_count()`
- `get_bdd_level_count()`
- `get_level_info(level)`

放入首批高层 API 的建议：

- 不建议直接暴露给普通用户
- 应由 `CDDContext` 负责管理
- 但 pybinding 层必须保留

### 二、`CDDContext`

`CDDContext` 负责把 UCDD runtime 的全局 level/clock/bool 声明，映射成 Python 可理解的上下文对象。

建议它承担这些职责：

- 记录 clock names
- 记录 bool names
- 建立 `clock name -> clock index` 映射
- 建立 `bool name -> level` 映射
- 生成变量对象
- 提供 level 解释与调试信息

建议支持的操作：

- 构造：`CDDContext(clocks=[...], bools=[...], name=None)`
- `from_context(context, bools=[...])`
- `clock(name)` / `bool(name)`
- 属性式访问时钟与布尔变量
- `level_info(level)`
- `all_level_info()`
- `true()`
- `false()`

### 三、`CDD`

这是最核心的公开对象。

它需要支持四大类操作：

- 基础图代数
- 时钟/时间语义操作
- 转换与抽取操作
- 调试与诊断操作

#### 1. 基础构造操作

建议支持：

- `CDD.true()`
- `CDD.false()`
- `CDD.upper(i, j, bound)`
- `CDD.lower(i, j, bound)`
- `CDD.interval(i, j, low, high)`
- `CDD.bddvar(level_or_name)`
- `CDD.bddnvar(level_or_name)`
- `CDD.from_dbm(dbm)`
- `CDD.from_federation(federation)`

其中 `from_federation` 是和现有 binding 联动的关键能力，后文会详细展开。

#### 2. 基础图代数操作

这些操作应进入 pybinding，也应大多进入高层 API：

- `&` / `and`
- `|` / `or`
- `-` / `minus`
- `^` / `xor`
- `~` / `not`
- `ite`
- `apply(op)`
- `apply_reduce(op)`
- `reduce()`
- `reduce2()`
- `equiv(other)`
- `nodecount()`
- `edgecount()`

API 层建议：

- Python 运算符优先提供
- `apply(op)` 与 `apply_reduce(op)` 保留为专家接口
- `==` 应定义为语义等价，不应复用底层指针相等

#### 3. 量化与替换操作

这些操作是完整符号分析能力的重要组成部分。

建议支持：

- `exist(bools=..., clocks=...)`
- `replace(from_levels, to_levels)`

API 层建议：

- 高层接口用名字、变量对象或索引都可接受
- Python 层负责排序、校验和去重

#### 4. 时间/时钟语义操作

这些是 UCDD 相比现有纯 UDBM binding 最有增量价值的一组能力。

建议支持：

- `remove_negative()`
- `delay()`
- `past()`
- `delay_invariant(invariant)`
- `predt(safe)`

其中：

- `delay()` 对应时间后继
- `past()` 对应逆时间流动
- `delay_invariant()` 在 delay 后与 invariant 相交
- `predt()` 则是更强的 timed predecessor 语义

这些操作应全部进入高层 API。

#### 5. reset 与 transition 相关操作

这是 UCDD 在模型检查工作流中的关键能力。

建议支持：

- `apply_reset(clock_resets=..., clock_values=..., bool_resets=..., bool_values=...)`
- `transition(guard, ...)`
- `transition_back(guard, update, ...)`
- `transition_back_past(guard, update, ...)`

这些也应进入高层 API，但 Python 层需要在接口设计上做一层更友好的包装，例如：

- 时钟更新允许用 `{clock: value}` 映射
- 布尔更新允许用 `{boolvar: True/False}` 映射
- `update` 图对象可由高级帮助函数构造

#### 6. 转换与抽取操作

这是 UCDD 与现有 DBM binding 联动的核心区域。

建议支持：

- `contains_dbm(dbm)`
- `extract_dbm()`
- `extract_bdd(dim=None)`
- `extract_bdd_and_dbm()`
- `bdd_to_array()`
- `to_federation(require_pure=True)`
- `to_dbm()` 或 `extract_first_dbm()`

其中最重要的是：

- `from_federation`
- `to_federation`
- `extract_bdd_and_dbm`

这三者决定了新旧两套能力是否能真正联动。

#### 7. 检查与调试操作

建议支持：

- `is_bdd()`
- `is_true()`
- `is_false()`
- `to_dot(push_negate=False)`
- `to_code_graph(...)`
- `to_graph_text(...)`

其中：

- `to_dot()` 应进入高层 API
- 其余打印型接口可先放专家层

### 四、`CDDExtraction`

这是对 `extraction_result` 的 Python 包装。

建议包含字段：

- `remainder`
- `bdd_part`
- `dbm`

这里的 `dbm` 不应只是裸矩阵，而应优先直接复用现有 `DBM` 包装对象。

建议支持的操作：

- 只读属性访问
- `to_federation()`，将抽取出的 DBM 转成单 DBM `Federation`
- `has_bdd_part()`

### 五、`BDDTraceSet`

这是对 `bdd_arrays` 的 Python 包装。

建议提供的能力：

- 迭代所有 trace
- 每条 trace 输出为 `{bool_name: bool}` 风格字典
- 可选输出稀疏格式，只列出实际涉及的变量
- 可选输出完整格式，对未指定变量用 `None`

建议支持的操作：

- `__len__`
- `__iter__`
- `to_dicts(sparse=True)`
- `to_rows()`

## 哪些操作应该暴露到 pybinding，哪些应该提升到高层 API

### pybinding 必须有，但高层可晚一点包装的

- runtime 初始化与 level 元信息
- `apply(op)` / `apply_reduce(op)`
- `replace`
- `reduce2`
- `nodecount` / `edgecount`
- `to_code_graph`
- `bdd_to_array`
- `extract_bdd_and_dbm`
- GC / rehash 统计与 hook

这些接口对完整性很重要，但并不一定都应该在第一版高层 API 上直接给最终用户当主入口。

### 高层 API 第一批就应该提供的

- 统一 `CDD` 对象
- `true` / `false`
- 基础集合运算 `& | - ^ ~`
- `equiv`
- `delay`
- `past`
- `delay_invariant`
- `predt`
- `apply_reset`
- `transition`
- `transition_back`
- `transition_back_past`
- `extract_bdd_and_dbm`
- `to_dot`
- `from_federation`
- `to_federation`

原因很简单：

- 这些才是用户真正会拿来做符号分析和联动验证的能力
- 如果只做低层节点和数组接口，最后会变成“又多了一个 native helper 层”，但并没有形成可用的 Python 模型

## 与现有 DBM binding 联动的核心设计

这部分是本文档的重点。

### 原则：UCDD 接入不能与现有 `Context` / `DBM` / `Federation` 割裂

如果 UCDD 接入后出现以下局面，这个方案就是失败的：

- UDBM 用户继续使用 `Context` / `Federation`
- UCDD 用户必须重新使用另一套完全不同的 clock context
- 两边无法互转
- zone 相关可视化、打印、调试逻辑重复维护

所以，联动设计必须优先于“单独把 UCDD 包起来”。

### 设计原则一：复用现有 clock 命名与 DBM 维度约定

现有 Python API 已经确定了以下事实：

- DBM 维度包含隐式参考时钟 `0`
- 用户时钟从索引 `1` 开始
- `Context` 负责时钟命名
- `DBM` 已经是现成的只读快照包装

因此，UCDD 接入时应遵守同样的约定：

- 对时钟的编号体系与现有 `Context` 对齐
- 从 CDD 抽出的 DBM 应直接能包装成现有 `DBM`
- 从 `Federation` 构造纯 CDD 时，不应重新洗牌 clock index

### 设计原则二：UCDD 高层上下文应建立在现有 `Context` 之上，而不是替代它

建议不要发明一套完全独立的 `CDDClock` 体系。

更好的方案是：

- `CDDContext` 内部持有一个现有 `Context` 或兼容其语义
- 对 clock 部分直接复用现有 `Clock` 命名和 index 约定
- 在此之上额外增加 bool 变量表

更具体地说，推荐提供：

- `CDDContext.from_context(context, bools=[...])`

这样带来的好处是：

- 现有 clock DSL 语义不需要重做
- 文档上更容易解释
- UCDD 与现有 Federation 转换时语义最稳定

### 设计原则三：从 CDD 抽出的 DBM 应直接复用现有 `DBM` 包装

`extract_dbm` / `extract_bdd_and_dbm` 抽出的 zone，不应该再创建一套新的 `CDDDBM` 类。

推荐做法：

- pybinding 层拿到原始 DBM 后
- 直接构造现有 `DBM` Python 包装对象

这样后续可以立刻复用现有能力：

- `DBM.to_string()`
- `DBM.raw()`
- `DBM.bound()`
- `DBM.to_matrix()`
- 可视化接口

这会显著减少代码重复。

### 设计原则四：从 `Federation` 到 `CDD` 的桥接必须是首批能力

建议首批直接支持：

- `CDD.from_federation(fed)`

其语义应为：

- 遍历 `fed.to_dbm_list()`
- 把每个 DBM 转成纯 clock CDD
- 对各个 DBM 对应 CDD 做并集

如果后续在 native 层愿意加更直接的桥接，这个接口仍可保留，只是实现路径变快。

这样做的价值是：

- 现有 Federation 用户可无缝进入 UCDD 语义
- 纯 clock 场景可先用 UDBM 建模、后续再升级到混合 symbolic graph
- 有利于写对照测试

这里还需要进一步明确一条实现原则：

- `Federation -> CDD` 的语义转换应优先复用 UCDD 自己的建模方式
- 能通过 UCDD 现有 `cdd` / `cppext.cpp` 思路完成的，不要在 Python 层重新发明一套等价转换
- 如果确实需要桥接辅助逻辑，也应尽量围绕 `dbm::fed_t`、`cdd(const raw_t*, dim)`、`cdd_reduce` 一类现成语义来组织

换句话说，这个方向应当是：

- 用 UDBM 原生 `fed_t` 表示 zone 联邦
- 用 UCDD 原生 `cdd` 表示统一 DD 图
- 在 C++ 层围绕这两者做最薄的桥接

而不是：

- 在 Python 层把 federation 先拆成一堆自定义矩阵协议
- 再用我们自己的转换逻辑去“模拟” UCDD 的语义

只要 UCDD/UDBM 已经提供了原生可表达的方法，就应优先调用它们，而不是自造新语义。

### 设计原则五：从 `CDD` 回到 `Federation` 也必须支持，但要明确条件

`CDD.to_federation()` 不应当无条件成功。

因为：

- 纯 BDD 没有可直接对应的 Federation
- 含非平凡 BDD 底部的混合图，也不等于单纯 zone 联邦

所以建议语义为：

- 若图是纯 CDD，或其 BDD 部分等价于 `true`
  - 可以无损转成 `Federation`
- 若图包含非平凡布尔条件
  - 默认报错
  - 可提供 `split_to_guarded_federations()` 之类的高级接口，后续再做

这比悄悄丢失 BDD 条件安全得多。

这部分同样应遵循“优先用原生方法”的约束：

- `CDD -> Federation` 不应通过我们自己重新解释整棵图的内部节点结构来完成
- 应优先基于 UCDD 已经提供的：
  - `cdd_reduce`
  - `cdd_remove_negative`
  - `cdd_extract_bdd_and_dbm`
  - `cdd_equiv`
- 再把抽出的原生 DBM 分量交给 UDBM 原生 `fed_t` 去重建联邦

这样做的好处是：

- 转换逻辑与 UCDD 上游自己的操作套路一致
- 我们不用自己重新实现一遍图遍历和 zone 解释
- 后续定位 bug 时，更容易把问题归因到“桥接层”还是“上游语义”

对于混合图，首选策略也不是强行压平成 `Federation`，而是：

- 在条件允许时支持 `split_to_guarded_federations()` 一类的受控拆分接口
- 让每个结果保留一个 UCDD BDD/guard 部分和一个 UDBM federation/zone 部分

这样能最大程度保留原语义，而不是为了迁就现有 API 悄悄丢信息。

### 设计原则六：`extract_bdd_and_dbm` 应成为两套模型的标准接口

这是最自然的联动形式：

- UCDD 负责表达“布尔条件 + 一个 zone 分量”
- 现有 `DBM` / `Federation` 负责表达 zone 本身

所以推荐把这个结果高层化为：

- `CDDExtraction.bdd_part`
- `CDDExtraction.dbm`
- `CDDExtraction.remainder`

其中：

- `bdd_part` 是 `CDD`
- `dbm` 是现有 `DBM`
- `remainder` 是 `CDD`

这会形成很清楚的职责分层。

### 设计原则七：现有可视化与文档能力应尽量复用 DBM 路线

仓库当前已经在 `DBM` / `Federation` 可视化上有规划和实现基础。

因此：

- CDD 的图结构可视化走 `to_dot()`
- zone 几何可视化优先走“先抽 DBM，再用现有 `DBM.plot()` / `Federation.plot()`”

这样不会在 UCDD 侧重复发明 zone 几何渲染。

## 推荐的 Python 模块布局

### pybinding 层

建议将当前单一 native 扩展拆分成两个名字明确的扩展：

- `pyudbm/binding/_udbm.cpp`
- `pyudbm/binding/_ucdd.cpp`

其中：

- `_udbm.cpp` 负责现有 UDBM / DBM / Federation binding
- `_ucdd.cpp` 负责新增 UCDD binding

这样做的原因：

- 避免继续维持语义不清晰的 `_binding` 名称
- 避免把 UDBM binding 与 UCDD binding 混在一个巨大 pybind11 文件里
- 更容易独立测试运行时初始化与对象生命周期
- 便于后续在 packaging 上确认依赖和符号边界

### Python 包装层

建议新增：

- `pyudbm/binding/ucdd.py`

可选增加：

- `pyudbm/ucdd/__init__.py`

但首版未必需要再开一层新 package；只要导出路径清晰即可。

### 与现有 `udbm.py` 的关系

建议不是“立刻把所有 CDD 能力塞进现有 `udbm.py`”，而是：

- 第一阶段独立放在 `ucdd.py`
- 与 `udbm.py` 通过互转方法联动
- 等接口稳定后，再决定是否从包根重导出

这样能降低对现有 API 的扰动。

## Python 实现与文档规范约束

后续进入 Python 层实现时，不能把 `ucdd.py`、`udbm.py` 里的工作当成“先随便写通再说”的快速胶水代码。

这里需要明确一条硬约束：

- Python 部分代码必须严格遵照仓库当前 `AGENTS.md` 中对 Python 代码的规范来写
- Python 部分的文档字符串与 pydoc 也必须严格遵照仓库当前 `AGENTS.md` 的规范来写
- 不能为了赶 phase、减少工作量或图省事而跳过这些规范

这条约束至少包含以下含义：

- Python 高层 API 不能退化成缺少校验、缺少错误信息、缺少类型边界说明的临时包装层
- 公开方法的命名、参数设计、返回值语义、错误处理和非变异/变异约定，要与现有高层 API 一样认真维护
- 新增 Python 文件时，代码风格、注释粒度和可读性要求，应与仓库现有高层 binding 代码保持一致，而不是退回到“能跑就行”的脚本式写法
- 新增或修改公开 Python API 时，对应的 docstring/pydoc 不能省略，也不能只留极简占位文本
- pydoc 应写清楚语义、参数、返回值、异常、必要的前置条件，以及在适合的地方给出与现有 `Context` / `DBM` / `Federation` 工作流一致的示例
- 如果某个阶段引入了临时实现，但其公开面已经可见给用户，那么文档质量也必须达到仓库规范要求，不能把“以后再补文档”当成默认做法

换句话说，后续 Phase 2 及之后的 Python 层工作，完成标准不只是：

- 接口能调用
- 测试能通过

还包括：

- Python 代码本身达到仓库规范要求
- 公开 API 的 pydoc 达到仓库规范要求

否则即使功能勉强可用，也不应视为该阶段真正完成。

## 建议的仓库路径结构与文件职责

这部分给出“后续真正上代码时，代码应该写到哪里”的明确建议。

原则只有两个：

- 不修改 `UCDD/`、`UDBM/`、`UUtils/` 子模块源码
- 新增代码尽量落在现有 `pyudbm/` 与 `test/` 的 wrapper 责任范围内

### 一、建议新增和修改的路径

建议按下面的目标结构推进：

```text
.
|- CMakeLists.txt                         # 需要接入新的 pybind11 扩展目标或源文件
|- pyudbm/
|  |- __init__.py                        # 后续若决定从包根导出 CDD API，这里做重导出
|  `- binding/
|     |- __init__.py                     # 绑定层导出整理
|     |- _udbm.cpp                       # 现有 UDBM / DBM / Federation 绑定，原 _binding.cpp 建议重命名而来
|     |- _ucdd.cpp                       # 新增：UCDD pybind11 薄绑定入口
|     |- ucdd.py                         # 新增：UCDD 高层 Python 包装
|     |- udbm.py                         # 现有高层 UDBM API，补充互转钩子和轻量联动入口
|     `- visual.py                       # 现有 DBM/Federation 可视化，可复用其 zone 几何能力
`- test/
   `- binding/
      |- test_api.py                     # 现有 UDBM 高层 API 测试，补纯 clock 互操作对照
      |- test_ucdd_native.py             # 新增：_ucdd 薄绑定测试
      |- test_ucdd_api.py                # 新增：ucdd.py 高层 API 测试
      |- test_ucdd_interop.py            # 新增：UCDD 与 DBM/Federation 互操作测试
      `- test_ucdd_visual.py             # 可选：后续若做 CDD 到 zone 可视化联动，则在此覆盖
```

如果后续 `_ucdd.cpp` 变得较大，还可以再拆，但首批不建议一开始就切太碎。

更稳妥的方式是：

- 先把 pybind11 绑定集中在 `pyudbm/binding/_ucdd.cpp`
- 等对象面稳定后，再酌情拆出局部 helper 头文件

### 二、各文件的职责边界

#### 1. `pyudbm/binding/_ucdd.cpp`

这是 UCDD 的 native 薄绑定入口。

职责应严格限制为：

- 包装 UCDD runtime 生命周期
- 包装 `cdd` 值对象
- 包装 `LevelInfo` / `extraction_result` / `bdd_arrays` 这类结果对象
- 把裸指针和引用计数语义封装成 Python 可安全持有的对象
- 做必要的参数转换和异常翻译

不应在这里做的事情：

- 大段 Python 友好接口语义
- clock/bool 名称层映射策略
- 高层 DSL
- 与现有 `Context` / `Federation` 的 Python 级对象拼装逻辑

也就是说，`_ucdd.cpp` 的目标是“正确、薄、可测”，而不是“用户体验完善”。

#### 2. `pyudbm/binding/ucdd.py`

这是 UCDD 的高层 Python 包装层。

建议这里承接的职责包括：

- `CDDContext`
- `CDD`
- `CDDExtraction`
- `BDDTraceSet`
- 对 pybinding 参数进行 Python 友好化
- 与现有 `Context` / `DBM` / `Federation` 发生互转
- 帮用户自动处理底层 `reduce()` 前置条件和校验逻辑

简单说：

- `_ucdd.cpp` 负责“能调”
- `ucdd.py` 负责“好用”

#### 3. `pyudbm/binding/udbm.py`

这个文件不应被 UCDD 接入重写，但需要适度补互操作入口。

建议只做轻量更新，例如：

- `Federation.to_cdd(...)`
- `DBM.to_cdd(...)`
- `Context.to_cdd_context(...)`

不要在这个阶段把 `udbm.py` 改造成“同时完整承载 UDBM 和 UCDD 全部高层 API”的超级文件。

#### 4. `pyudbm/__init__.py`

包根导出要谨慎。

建议策略是：

- 第一阶段不从包根直接导出所有 UCDD 对象
- 先要求用户从 `pyudbm.binding.ucdd` 或后续明确的 `pyudbm.ucdd` 命名空间导入
- 等接口稳定后，再考虑提升到包根公开面

这样更利于控制 API 稳定性。

#### 5. `CMakeLists.txt`

这里需要修改以编译新的 pybind11 扩展。

建议方向是：

- 将现有 `_binding` 扩展目标重命名为 `_udbm`
- 新增 `_ucdd` 扩展目标
- 为 `_ucdd` 单独链接 UCDD 及其依赖链

不建议的方式：

- 把 UCDD 代码直接糅进现有 `_udbm` 单一扩展里

原因：

- 编译和链接边界更难看清
- 测试定位更难
- 后续若需要单独控制加载顺序或初始化策略会更麻烦

### 三、如果 `_ucdd.cpp` 后续需要继续拆分

若后续对象面扩张，可考虑再拆成如下结构：

```text
pyudbm/binding/
|- _ucdd.cpp
|- _ucdd_runtime.hpp
|- _ucdd_types.hpp
|- _ucdd_convert.hpp
`- _ucdd_ops.hpp
```

其中：

- `_ucdd_runtime.hpp` 放 runtime 包装
- `_ucdd_types.hpp` 放结果型轻量包装结构
- `_ucdd_convert.hpp` 放 DBM/Federation 与 UCDD 的桥接 helper
- `_ucdd_ops.hpp` 放 `cdd` 相关绑定注册函数

但这是第二步优化，不是第一步硬要求。

## 新 C++ 代码应该如何组织

这部分把“新 cpp 代码写在哪里、怎么分层、怎么避免后续变成一团”说清楚。

### 一、推荐分层

`_ucdd.cpp` 内部建议也按三层组织：

1. native 资源包装层
2. pybind11 暴露层
3. 轻量桥接 helper 层

除此之外，还建议增加一条更上位的组织原则：

- `_udbm.cpp` 与 `_ucdd.cpp` 不应通过“导入对方 Python 扩展模块”的方式联动
- 更合理的方式是共享一层内部 C++ core 或 helper
- 也就是说，联动应发生在：
  - 共享的 C++ 包装层
  - UDBM/UCDD 原生库类型
  - Python 高层对象包装层

而不应发生在“一个 pybind11 扩展在 C++ 里再去 import 另一个 pybind11 扩展”的层面

原因是：

- C++ 扩展之间的 Python 级 import 会引入初始化顺序耦合
- 会让 native 层依赖 Python 模块路径和命名细节
- 一旦扩展名、导入路径或包结构调整，native 联动就会变脆
- 也不利于单独测试 `_udbm` 或 `_ucdd`

对本仓库来说，更推荐的结构是：

- `_udbm.cpp` 和 `_ucdd.cpp` 都依赖同一套底层 UDBM/UCDD 库
- 如有必要，再共享一层仓库内自有的 C++ helper/core
- Python 层只负责把两边已经成型的 native 值对象重新包装成高层 API

#### 1. native 资源包装层

这层建议定义若干 C++ 小包装类，例如：

- `NativeCDDRuntime`
- `NativeCDD`
- `NativeCDDLevelInfo`
- `NativeCDDExtraction`
- `NativeBDDTraceSet`

职责是：

- 承接 UCDD 的 C++ RAII 语义
- 管理抽取结果里的 DBM 内存
- 管理 `bdd_arrays` 的数组释放
- 隔离 pybind11 与底层 UCDD 结构的直接耦合

如果后续需要让 `_udbm.cpp` 与 `_ucdd.cpp` 共享 native 包装能力，推荐做法是：

- 把共享部分下沉到单独的内部 C++ 头文件或 core 文件
- 例如让 `NativeDBM` / `NativeFederation` 这类与 pybind11 无关的包装逻辑独立出来
- 然后由 `_udbm.cpp` 和 `_ucdd.cpp` 共同包含或链接

这样可实现的目标是：

- `_ucdd.cpp` 能直接拿到现有 UDBM 包装能力
- 但不会形成“_ucdd.cpp 在运行时 import _udbm 模块”的耦合
- 联动仍然是 C++ 层的静态依赖，而不是 Python 模块级动态依赖

#### 2. pybind11 暴露层

这层只负责：

- `py::class_` 注册
- 参数签名
- 返回值策略
- Python 名称设计

不应在 lambda 里堆太多业务逻辑。

#### 3. 轻量桥接 helper 层

这里主要解决：

- `raw_t*` 到 Python list / bytes / capsule 的安全转换
- `bdd_arrays` 到 C++ 可拥有对象的转换
- 从现有 DBM 快照中提取原始矩阵用于 `cdd_from_dbm`

如果这部分逻辑过多，应该抽成静态 helper 函数，不要散落在 `.def(...)` 里。

不过桥接层的优先原则仍然是：

- 能直接围绕 UCDD/UDBM 原生方法完成的，优先直接调用原生方法
- helper 层的任务是“把原生方法接进来并托管资源”，不是“替代原生方法重做语义转换”

特别是 `Federation <-> CDD` 这条桥接，建议在 helper 层中坚持：

- `fed -> cdd` 优先按 UCDD `cppext.cpp` 的既有思路组织
- `cdd -> fed` 优先按 `extract_bdd_and_dbm` 的既有套路组织
- 不去自行解析 `cddnode_` / `bddnode_` 内部结构来实现转换

### 二、建议首批在 `_ucdd.cpp` 中直接实现的类

#### `NativeCDDRuntime`

建议提供：

- `ensure_running()`
- `init(maxsize=..., cache_size=..., stack_size=...)`
- `done()`
- `version()`
- `is_running()`
- `add_clocks(n)`
- `add_bddvars(n)`
- `get_level_count()`
- `get_bdd_level_count()`
- `get_level_info(level)`

并考虑在内部记录“当前 runtime 配置是否已经初始化过”，以便 Python 层能更容易做错误提示。

#### `NativeCDD`

建议提供：

- 静态工厂：`true`, `false`, `upper`, `lower`, `interval`, `bddvar`, `bddnvar`, `from_dbm`
- 基础代数：`and_op`, `or_op`, `minus_op`, `xor_op`, `invert`
- 图语义：`equiv`, `reduce`, `reduce2`, `nodecount`, `edgecount`, `is_bdd`
- 时间语义：`remove_negative`, `delay`, `past`, `delay_invariant`, `predt`
- transition 语义：`apply_reset`, `transition`, `transition_back`, `transition_back_past`
- 转换抽取：`extract_dbm`, `extract_bdd`, `extract_bdd_and_dbm`, `bdd_to_array`
- 输出：`to_dot`

#### `NativeCDDExtraction`

建议这是一个真正拥有资源的值对象，而不是简单视图：

- 内部持有抽出的 DBM 缓冲区
- 内部持有 `CDD_part` 和 `BDD_part`
- Python 层访问 `dbm` 时再转成高层 `DBM` 或原始矩阵

#### `NativeBDDTraceSet`

建议内部就先把原始 `vars/values` 托管好，再向 Python 暴露：

- `num_traces`
- `num_bools`
- `vars_matrix()`
- `values_matrix()`

之后再由 `ucdd.py` 转成高层 trace 表示。

### 三、推荐不要在 `_ucdd.cpp` 里做的事情

- 不要直接 import Python 的 `Context` / `Federation` 类并拼对象
- 不要在 C++ 层通过 Python import 去依赖 `_udbm` 扩展
- 不要在 C++ 层直接做复杂 clock name 决策
- 不要在 C++ 层做“是否应该自动 reduce”这类高层便利策略
- 不要在 C++ 层尝试承接整套用户 DSL

这些都属于 Python 层更合适。

## 编译与拆分配套要求

本方案允许后续把 `_udbm` / `_ucdd` 以及共享 helper 继续拆分成多个文件，但拆分本身不是目的，配套维护才是重点。

需要明确的要求是：

- 允许拆分文件
- 但每次拆分都必须同步维护构建配置
- 不能出现“代码拆开了，但 `CMakeLists.txt`、目标链接关系、测试导入路径没有一起更新”的状态

具体要求包括：

- 新增或重命名源文件时，同步调整 `CMakeLists.txt`
- 如果引入共享 core / helper 源文件，需要明确它们是：
  - 被 `_udbm` 和 `_ucdd` 分别编译引用
  - 还是先组成一个内部静态库再被两个扩展链接
- 若拆出头文件和实现文件，需要保证包含路径、编译顺序和导出边界明确
- `_udbm` 和 `_ucdd` 的测试必须在拆分后仍能独立导入和运行

这里尤其要避免两种情况：

- 为了省事，把越来越多不相关代码重新塞回单一扩展
- 只拆源文件，不同步维护构建和测试，导致联动在编译阶段或加载阶段失稳

因此，本文档里的总体建议是：

- 可以拆分
- 但拆分必须伴随构建、链接、导入路径和测试的同步维护
- 任何结构调整都应保证 `_udbm` / `_ucdd` 联通顺畅，同时仍能各自独立构建和定位问题

## `_binding` 重命名为 `_udbm` 的具体建议

这项调整建议尽早做，原因是：

- 当前 `_binding` 这个名称在只有一个 native 扩展时还勉强成立
- 一旦同时引入 UDBM 与 UCDD 两个 native 扩展，`_binding` 就会变得语义含混
- 采用 `_udbm` / `_ucdd` 并列命名后，仓库结构、导入路径、测试覆盖和构建配置都会更清晰

建议调整的内容包括：

- `pyudbm/binding/_binding.cpp` 重命名为 `pyudbm/binding/_udbm.cpp`
- pybind11 模块名从 `_binding` 改为 `_udbm`
- `pyudbm/binding/udbm.py` 中的导入从 `from ._binding import ...` 改为 `from ._udbm import ...`
- 相关测试中若有直接导入 native 模块名，也同步调整
- `CMakeLists.txt` 中扩展目标、输出模块名和源文件路径同步调整

这项重命名本身不属于 UCDD 特性，但它是后续双扩展结构清晰化的前置整理工作。

## Python 高层应该如何操作

这里明确说明 Python 层对象之间的调用关系和职责边界。

### 一、建议的高层对象关系

推荐形成下面这个关系图：

- `Context`
  - 现有纯 clock 上下文
- `CDDContext`
  - 复用一个 `Context` 作为 clock 语义基底
  - 在其上增加 bool 变量集合
- `Federation`
  - 现有纯 zone 联邦对象
- `CDD`
  - 新的统一符号图对象
  - 可表示纯 zone，也可表示布尔+zone 混合图

它们之间建议有如下互操作入口：

- `Context.to_cdd_context(bools=..., name=None)`
- `CDDContext.from_context(context, bools=..., name=None)`
- `Federation.to_cdd()`
- `DBM.to_cdd()`
- `CDD.from_federation(fed)`
- `CDD.to_federation(require_pure=True)`

### 二、推荐的高层调用模式

#### 1. 纯 clock 用户的升级路径

已有用户可能先写出：

```python
from pyudbm import Context

c = Context(["x", "y"], name="c")
fed = (c.x <= 10) & (c.x - c.y < 3)
```

后续希望接入 UCDD 时，升级路径应该尽量平滑：

```python
from pyudbm.binding.ucdd import CDD

cdd = CDD.from_federation(fed)
future = cdd.delay()
back = future.past()
```

也就是说，对纯 zone 用户来说，CDD 先应当表现为“更强的一层符号语义”，而不是一套彻底新的建模起点。

#### 2. 需要布尔变量的用户路径

这类用户才真正需要 `CDDContext`：

```python
from pyudbm import Context
from pyudbm.binding.ucdd import CDDContext

base = Context(["x", "y"], name="c")
ctx = CDDContext.from_context(base, bools=["b1", "b2"])

state = (ctx.x <= 10) & ctx.b1 & ~ctx.b2
delayed = state.delay()
```

这里要求的是：

- `ctx.x` 尽量保持和现有 `Clock` 直觉一致
- `ctx.b1` 这种布尔变量能自然进入图代数

#### 3. 需要 transition/reset 的用户路径

高层接口应允许用户用 Python dict 或序列表达更新，而不是手搓多组并行数组：

```python
guard = (ctx.x <= 5) & ctx.b1
target = state.transition(
    guard,
    clock_resets={ctx.x: 0},
    bool_resets={ctx.b1: False, ctx.b2: True},
)
```

反向 transition 也应采用类似格式：

```python
source = target.transition_back(
    guard=guard,
    update=(ctx.x == 0) & ~ctx.b1 & ctx.b2,
    clock_resets=[ctx.x],
    bool_resets=[ctx.b1, ctx.b2],
)
```

### 三、`ucdd.py` 中建议提供的具体接口

#### `CDDContext`

建议至少支持：

- `from_context(context, bools, name=None)`
- `clock_names`
- `bool_names`
- `clocks`
- `bools`
- `__getitem__`
- 属性式访问 clock/bool
- `true()`
- `false()`
- `level_info(level)`
- `all_level_info()`

#### `CDD`

建议至少支持：

- `from_federation(fed)`
- `from_dbm(dbm)`
- `to_federation(require_pure=True)`
- `extract_bdd_and_dbm()`
- `bdd_traces()`
- `delay()`
- `past()`
- `delay_invariant(inv)`
- `predt(safe)`
- `apply_reset(clock_resets=None, bool_resets=None)`
- `transition(...)`
- `transition_back(...)`
- `transition_back_past(...)`
- `to_dot(path=None, push_negate=False)`

#### `CDDExtraction`

建议至少支持：

- `remainder`
- `bdd_part`
- `dbm`
- `to_federation()`

#### `BDDTraceSet`

建议至少支持：

- `__iter__`
- `__len__`
- `to_dicts(sparse=True)`
- `to_rows()`

## 最终产物期望的使用方式

这里不是讨论内部实现，而是明确“做完以后，用户应该怎么用，什么算是一个令人满意的最终体验”。

### 一、纯 zone 用户的最终体验

目标是：现有 `pyudbm` 用户不需要重学整套系统。

期望的使用方式应接近：

```python
from pyudbm import Context
from pyudbm.binding.ucdd import CDD

c = Context(["x", "y"], name="c")
zone = (c.x <= 10) & (c.x - c.y < 3)

cdd = CDD.from_federation(zone)
assert cdd.to_federation() == zone

future = cdd.delay()
past = future.past()
```

这里体现的是：

- `CDD` 可以自然承接现有 `Federation`
- `Federation` 仍然是纯 zone 工作流的一等对象
- `CDD` 是增强层，不是替换层

### 二、混合 bool/clock 用户的最终体验

目标是：用户能用一个上下文同时表达 clock 条件和布尔条件。

期望用法应接近：

```python
from pyudbm import Context
from pyudbm.binding.ucdd import CDDContext

base = Context(["x", "y"], name="c")
ctx = CDDContext.from_context(base, bools=["door_open", "alarm"])

safe = (ctx.x <= 5) & ~ctx.alarm
state = ((ctx.x <= 10) & ctx.door_open) | ((ctx.y <= 3) & ~ctx.door_open)

bad_predecessor = state.predt(safe)
```

这里要求：

- 布尔变量能像现有 clock DSL 一样自然使用
- 混合语义对象不需要用户手动区分“这是 BDD 还是 CDD”

### 三、抽取与分解的最终体验

用户应能很容易地把混合图拆成“布尔条件 + zone 分量”：

```python
part = state.extract_bdd_and_dbm()

print(part.bdd_part)
print(part.dbm)

rest = part.remainder
```

如果要进一步检查布尔轨迹，也应该非常直接：

```python
traces = part.bdd_part.bdd_traces()
for row in traces.to_dicts():
    print(row)
```

### 四、transition/reset 的最终体验

这里的目标是让 API 贴近 timed-automata 建模直觉，而不是暴露底层并行数组接口：

```python
next_state = state.transition(
    guard=(ctx.x <= 5) & ctx.door_open,
    clock_resets={ctx.x: 0},
    bool_resets={ctx.door_open: False, ctx.alarm: True},
)

prev_state = next_state.transition_back_past(
    guard=(ctx.x <= 5) & ctx.door_open,
    update=(ctx.x == 0) & ~ctx.door_open & ctx.alarm,
    clock_resets=[ctx.x],
    bool_resets=[ctx.door_open, ctx.alarm],
)
```

### 五、图结构调试的最终体验

用户应当可以在不理解底层 node 结构的情况下拿到图输出：

```python
state.to_dot("state.dot", push_negate=True)
```

如果后续还需要更细的诊断能力，再考虑加：

- `state.levels()`
- `state.nodecount()`
- `state.edgecount()`

但首批不应要求用户学习内部 node manager 细节。

## 推荐的首批开发产物定义

为了避免后续实现时“做了很多，但不清楚什么算完成”，建议把首批完成标准明确成一组可观察产物。

### 一、native 产物

以下内容完成后，说明 `_ucdd` 薄绑定达标：

- 能导入 `_ucdd`
- 能初始化 runtime
- 能构造 `true/false`、clock interval、BDD 变量
- 能做基础图运算
- 能做 `delay/past/predt`
- 能做 `extract_bdd_and_dbm`
- 能做 `bdd_to_array`

### 二、Python 高层产物

以下内容完成后，说明 `ucdd.py` 高层包装达标：

- `CDDContext.from_context(...)`
- `CDD.from_federation(...)`
- `CDD.to_federation(require_pure=True)`
- `CDD.delay() / past() / predt()`
- `CDD.transition(...)`
- `CDD.extract_bdd_and_dbm()`
- `CDD.bdd_traces()`

### 三、互操作产物

以下内容完成后，说明“UCDD 已与现有 DBM binding 联动成功”：

- 抽取出的 DBM 复用现有 `DBM` 包装
- 纯 clock 的 `CDD.from_federation(f).to_federation()` 往返保持语义一致
- `delay/past/predt` 在纯 clock 场景下可与现有 Federation 行为做对照验证
- 现有 `Context` 能平滑升级成 `CDDContext`

## 分阶段落地计划

## 实施状态维护规则

后续这份文档不应只作为一次性方案说明，而应作为实现过程中的状态记录文件持续维护。

维护规则建议如下：

- 每个 phase 都使用 Markdown checklist 维护状态
- 未完成项使用 `[ ]`
- 完成项使用 `[x]`
- 当某个 phase 实际完成后，需要同时勾选：
  - 该 phase 的实施清单
  - 该 phase 的产物清单
  - 该 phase 的完成后检查清单
- 每个 phase 完成后，都应执行一次基于当前仓库真实构建链路的完整回归验证，而不是只跑局部 smoke test
- 这里的“完整回归验证”至少应覆盖：
  - native 依赖可重新编译
  - Python 扩展可重新编译并成功导入
  - 现有测试集与该 phase 新增测试可一起运行
  - 若某个 phase 影响 `_udbm` / `_ucdd` 命名、导入路径、互操作或运行时生命周期，则应优先执行完整测试而不是只做定向测试
- 如果实现过程中出现拆分或调整，应优先更新本节 checklist，再开始继续开发

### Phase 0：设计与文档

目标：

- 明确对象模型
- 明确首批暴露接口
- 明确与现有 DBM binding 的联动边界
- 明确目录结构、命名调整与实施顺序

实施清单：

- [x] 建立 `mds/` 设计文档
- [x] 盘点 UCDD 主要公开数据结构与内部结构边界
- [x] 明确 pybinding 层与 Python 高层 API 分层
- [x] 明确 UCDD 与现有 `Context` / `DBM` / `Federation` 联动方案
- [x] 明确 `_binding -> _udbm` 的命名整理建议
- [x] 明确目标路径结构、新增文件职责与最终使用方式

本 phase 产物：

- [x] 本文档
- [x] PR 说明与文档双向链接

完成后检查清单：

- [x] 文档已包含对象模型、路径结构、阶段计划和最终用法示例
- [x] 文档已说明哪些内容是首批公开承诺，哪些不是
- [x] 文档已明确后续 phase 需要继续在本文档中打勾维护
- [x] 文档已明确要求后续每个 phase 结束后执行一次完整编译与回归验证

### Phase 1：命名整理与 native 薄绑定

目标：

- 将现有 `_binding` 命名整理为 `_udbm`
- 新增 `_ucdd` pybind11 模块
- 只做生命周期安全和内存所有权安全的薄包装

实施清单：

- [x] 将 `pyudbm/binding/_binding.cpp` 重命名为 `pyudbm/binding/_udbm.cpp`
- [x] 将 pybind11 模块名从 `_binding` 调整为 `_udbm`
- [x] 调整 `pyudbm/binding/udbm.py` 对 native 模块的导入路径
- [x] 调整 `CMakeLists.txt` 里的源文件路径、目标名和输出模块名
- [x] 检查是否有测试或辅助代码仍直接引用 `_binding`
- [x] 新增 `pyudbm/binding/_ucdd.cpp`
- [x] 在 `_ucdd.cpp` 中接入 runtime 包装
- [x] 在 `_ucdd.cpp` 中接入 `NativeCDD`
- [x] 在 `_ucdd.cpp` 中接入 `NativeCDDLevelInfo`
- [x] 在 `_ucdd.cpp` 中接入 `NativeCDDExtraction`
- [x] 在 `_ucdd.cpp` 中接入 `NativeBDDTraceSet`
- [x] 暴露基础构造与集合代数接口
- [x] 暴露 `reduce` / `equiv`
- [x] 暴露 `delay` / `past` / `predt`
- [x] 暴露 `extract_*` 与 `bdd_to_array`
- [x] 暴露 `transition` / `transition_back` / `transition_back_past`

本 phase 产物：

- [x] 可导入的 `_udbm` 扩展
- [x] 可导入的 `_ucdd` 扩展
- [x] `test/binding/test_ucdd_native.py`

完成后检查清单：

- [x] `python -c "import pyudbm.binding._udbm"` 可成功执行
- [x] `python -c "import pyudbm.binding._ucdd"` 可成功执行
- [x] 现有 UDBM 高层 API 在 `_binding -> _udbm` 重命名后仍能正常导入
- [x] 不依赖 Python 高层包装也能通过测试调用 UCDD 核心 native 接口
- [x] `_ucdd` 相关对象不存在裸指针泄漏和明显生命周期错误
- [x] 已完成一次完整编译后的回归测试，而不只是 `_ucdd` 定向 smoke test

### Phase 2：Python 高层包装与现有 DBM 联动

目标：

- 实现 `CDDContext`
- 实现 `CDD`
- 实现 `CDDExtraction`
- 实现 `BDDTraceSet`
- 打通 `Federation <-> CDD`
- 抽取出的 DBM 直接复用现有 `DBM`

实施清单：

- [x] 新增 `pyudbm/binding/ucdd.py`
- [x] 实现 `CDDContext`
- [x] 实现 `CDD`
- [x] 实现 `CDDExtraction`
- [x] 实现 `BDDTraceSet`
- [x] 实现 `CDDContext.from_context(context, bools=...)`
- [x] 实现 `Context.to_cdd_context(...)`
- [x] 实现 `Federation.to_cdd(...)`
- [x] 实现 `DBM.to_cdd(...)`
- [x] 实现 `CDD.from_federation(federation)`
- [x] 实现 `CDD.from_dbm(dbm)`
- [x] 实现 `CDD.to_federation(require_pure=True)`
- [x] 将 `extract_bdd_and_dbm()` 的 DBM 部分包装成现有 `DBM`
- [x] 将 `bdd_arrays` 高层化为可迭代的 `BDDTraceSet`
- [x] 自动处理 `extract_*` 所需的 `reduce()` 前置条件

本 phase 产物：

- [x] `pyudbm/binding/ucdd.py`
- [x] `test/binding/test_ucdd.py`

完成后检查清单：

- [x] 现有 `Federation` 用户能无缝把纯 zone 提升成 CDD
- [x] 纯 CDD 结果能在满足条件时回落成 `Federation`
- [x] 抽取出的 DBM 可以直接复用现有 `DBM` 方法与表示
- [x] 纯 clock 场景下的 UCDD 互操作不引入新的命名或维度歧义
- [x] 已完成一次完整编译后的回归测试，并覆盖 `_udbm`、`_ucdd` 与高层 Python API 联动

### Phase 3：高层 DSL 与易用接口

目标：

- 提供 bool 变量对象
- 提供 clock/bool 混合表达式
- 提供 reset/transition 的 Python 友好参数格式

实施清单：

- [x] 在 `CDDContext` 中暴露 bool 变量对象
- [x] 支持属性式和下标式访问 bool 变量
- [x] 让 clock 条件与 bool 条件可自然组合
- [x] 为 `apply_reset` 提供 `{clock: value}` / `{boolvar: bool}` 风格输入
- [x] 为 `transition` 提供 Python 友好参数格式
- [x] 为 `transition_back` 提供 Python 友好参数格式
- [x] 为 `transition_back_past` 提供 Python 友好参数格式
- [x] 明确 clock 变量对象与现有 `Clock` 的关系
- [x] 明确 bool 命名冲突处理规则
- [x] 明确 `Context` 与 `CDDContext` 的共存边界

本 phase 产物：

- [x] 用户可直接编写 mixed bool/clock symbolic expression
- [x] `test/binding/test_ucdd.py` 中覆盖 DSL 和 transition/reset 用例

完成后检查清单：

- [x] 用户可以用 Python 友好方式表达 guard / update / mixed symbolic state
- [x] 不需要用户手工拼并行数组即可完成 reset / transition 操作
- [x] bool 与 clock 的命名、打印和上下文归属清晰一致
- [x] 已完成一次完整编译后的回归测试，并覆盖 mixed bool/clock DSL 与 transition/reset 工作流

## 当前公开用法示例

下面给出当前仓库中已经实现并通过测试的典型用法，作为后续文档和回归验证的对照基线。

### 一、纯 clock Federation 与 CDD 互转

```python
from pyudbm import Context

base = Context(["x", "y"], name="c")
fed = ((base.x <= 3) & (base.y <= 2)) | (base.x - base.y <= 1)

cdd = fed.to_cdd()
relaxed = cdd.delay()
fed_back = relaxed.to_federation()
```

这个例子体现的是：

- 现有 `Federation` 可以直接提升为 `CDD`
- `CDD.delay()` 可以继续进行时间推进
- 在结果仍为纯 clock 语义时，可以再安全回落成 `Federation`

### 二、mixed bool/clock 工作流

```python
from pyudbm import Context

ctx = Context(["x", "y"], name="c").to_cdd_context(bools=["door_open", "alarm"])

state = ((ctx.x <= 5) & ctx.door_open) | ((ctx.x == 0) & ~ctx.door_open)
step = state.transition(
    guard=ctx.x <= 5,
    clock_resets={"x": 0},
    bool_resets={"door_open": False, "alarm": True},
)
extraction = step.extract_bdd_and_dbm()
```

这个例子体现的是：

- bool 与 clock 条件可以在同一个 `CDD` 中自然组合
- `transition(...)` 支持 Python 友好的 reset 参数格式
- `extract_bdd_and_dbm()` 可以把 mixed symbolic state 拆成：
  - 继续待处理的 remainder
  - 当前片段上的 bool guard
  - 可直接复用现有 `DBM` API 的 DBM 片段

### Phase 4：文档、测试与对照验证

目标：

- 增补高层 API 文档
- 增补联动示例
- 做与现有 UDBM 操作的对照测试

实施清单：

- [x] 为 UCDD 高层 API 增补文档字符串和使用示例
- [x] 在仓库文档或 `mds/` 中补充 UCDD 与 DBM 联动示例
- [x] 新增纯 clock 对照测试
- [x] 新增 mixed bool/clock 工作流测试
- [x] 新增 `extract_bdd_and_dbm()` 稳定性测试
- [x] 新增内存安全和生命周期回归测试
- [x] 新增 `_udbm` 重命名后的回归测试

建议优先完成的对照测试：

- [x] `Federation.up()` 与 `CDD.from_federation(f).delay().to_federation()` 对照
- [x] `Federation.down()` 与 `CDD.from_federation(f).past().to_federation()` 对照
- [x] `predt` 与现有 Federation `predt` 的纯 clock 语义对照
- [x] `extract_bdd_and_dbm()` 的稳定性与内存安全

本 phase 产物：

- [x] 完整的 UCDD 高层 API 测试集
- [x] 关键纯 clock 对照测试集
- [x] 文档化的使用示例

完成后检查清单：

- [x] 纯 clock 场景下，UCDD 与现有 Federation 关键语义可对照验证
- [x] mixed bool/clock 场景下，核心流程有稳定测试覆盖
- [x] 文档中的主要示例代码能与当前 API 保持一致
- [x] 已完成一次完整编译后的回归测试，并确认新增文档示例与当前实现一致

### Phase 5：状态收尾与文档回填

目标：

- 确保实现完成后，这份文档本身也被更新成真实状态记录

实施清单：

- [x] 完成一个 phase 后立即回到本文档勾选 checklist
- [x] 若实现过程中拆分 phase 或增加新任务，先更新本文档再继续开发
- [x] 在 PR 讨论中引用本文档中对应 phase 的完成状态

本 phase 产物：

- [x] 本文档中的 checklist 与实际实现状态一致

完成后检查清单：

- [x] 不存在“代码已完成但文档 checklist 未更新”的偏差
- [x] 后续读者仅查看本文档即可知道目前推进到哪个 phase
- [x] 各个已完成 phase 的完整编译与回归验证结果已在实现记录或 PR 讨论中可追溯

## 实现与验证记录

为满足“每个 phase 结束后执行完整编译与完整回归”的要求，后续每次实际收尾都应至少能追溯到：

- `make bin`
- `make build`
- `make unittest`

对于 UCDD 相关补充验证，还应能追溯到：

- `pytest -q test/binding/test_ucdd.py`
- `pytest -q test/binding/test_ucdd_native.py`
- `pytest -q test/binding`

本轮 Phase 4 / Phase 5 收尾验证记录（2026-03-24）：

- `pytest -q test/binding/test_ucdd.py` 通过，`12 passed`
- `pytest -q test/binding/test_ucdd_native.py` 通过，`9 passed`
- 文档示例脚本顺序执行通过
- `pytest -q test/binding` 通过，`117 passed`
- `make bin` 通过，`UUtils` / `UDBM` / `UCDD` 原生 `ctest` 全通过
- `make build` 通过
- `make unittest` 通过，`118 passed`
- PR 讨论记录：<https://github.com/HansBug/pyudbm/pull/8#issuecomment-4115550359>

## 首批不建议进入公开承诺的内容

以下内容建议先不要对外形成稳定 API 承诺：

- `MULTI_TERMINAL` 相关 extra terminal 语义
- GBC / rehash hook 注册
- 直接节点级访问
- `dump_nodes`
- 原始 `FILE*` 打印回调接口

原因不是它们没价值，而是：

- 用户面不够稳定
- 与当前仓库主目标关系不够强
- 很容易把首版接口面铺得过宽

## 风险与注意事项

### 1. 全局 runtime 风险

UCDD 带有显式全局状态。

这意味着后续 Python API 需要非常明确：

- 一个进程内如何管理多个上下文
- 是否允许重复初始化
- 不同 `CDDContext` 之间如何共存

这将是实现设计里最敏感的部分之一。

### 2. 生命周期与内存所有权风险

`cdd` 本身依赖引用计数。

同时：

- `extraction_result.dbm` 需要释放
- `bdd_arrays.vars` / `bdd_arrays.values` 需要释放

因此 pybinding 层必须在 C++ 侧做安全封装，不能把裸指针所有权留给 Python。

### 3. 等价性语义风险

UCDD 的 C++ `operator==` 更接近句柄相等，而不是一般用户直觉中的语义相等。

所以 Python 层必须明确：

- `==` 应代表语义等价
- 若需要句柄级 identity，应另设专家接口

### 4. `extract_*` 前置条件风险

`extract_dbm` 和 `extract_bdd` 在原库语义里有“先 reduce”的前提。

Python API 应尽量自动完成该前置处理，避免把坑直接暴露给用户。

### 5. 与现有 API 割裂的风险

如果后续实现只做 `_ucdd` 而不做互转层，那么：

- 用户会得到一套新的 native helper
- 但不会真正得到可用的 Python 级新能力

因此必须坚持把联动层列为首批目标，而不是后续“有空再补”。

## 建议的后续实现顺序

推荐顺序如下：

1. 新增 `mds/` 设计文档并达成方案共识
2. 实现 `_ucdd` 薄绑定
3. 实现 `CDDContext` / `CDD` / `CDDExtraction` / `BDDTraceSet`
4. 打通 `Federation <-> CDD` 与 `DBM` 抽取复用
5. 补高层 DSL、transition 友好接口和测试

这里特别强调第 4 步：

**没有 `Federation <-> CDD` 与 `DBM` 复用，就不算真正完成 UCDD 接入设计。**

## 推荐的首批任务拆分

为了后续上代码时更稳，建议把实现工作拆成以下任务：

### 任务 A：runtime 与基础 `cdd` 包装

- `_ucdd` 模块骨架
- runtime init/done
- 基础 `cdd` 值对象
- 基础代数与 reduce/equiv

### 任务 B：抽取与结果包装

- `extract_dbm`
- `extract_bdd`
- `extract_bdd_and_dbm`
- `bdd_to_array`
- Python 结果包装

### 任务 C：与现有 DBM/Federation 联动

- `CDD.from_federation`
- `CDD.to_federation`
- `DBM` 快照复用
- 对照测试

### 任务 D：时间与 transition 语义

- `delay`
- `past`
- `delay_invariant`
- `predt`
- `apply_reset`
- `transition`
- `transition_back`
- `transition_back_past`

### 任务 E：高层 DSL

- `CDDContext`
- bool 变量对象
- Python 友好 reset/update 参数

## 总结

这份方案的核心判断可以归纳为四点：

1. UCDD 的主公开对象应是统一 `CDD` 图对象，而不是把 `BDD` 与 `CDD` 机械拆成两套顶级 Python 类。
2. `ddNode`、`cddnode_`、`bddnode_`、`nodemanager_` 等应明确留在内部，不进入 Python 主 API。
3. `LevelInfo`、`extraction_result`、`bdd_arrays` 这些结果型对象有实际公开价值，但必须包装成 Python 友好的值对象。
4. UCDD 接入必须与现有 `Context` / `DBM` / `Federation` 联动，尤其要把 `Federation <-> CDD` 和 DBM 快照复用列为首批能力，而不是后补项。

后续如果按这个方向推进，`pyudbm` 才能在保持现有高层 API 连续性的前提下，把能力从“基于 DBM/Federation 的 zone 操作”扩展到“包含布尔状态与混合 symbolic graph 的统一 CDD 工作流”。
