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

- native pybind11 入口位于 `pyudbm/binding/_binding.cpp`
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

建议在现有 `_binding` 之外新增独立模块，例如：

- `pyudbm/binding/_ucdd.cpp`

原因：

- 避免把当前 UDBM binding 与 UCDD binding 混在一个巨大 pybind11 文件里
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

## 分阶段落地计划

### 阶段 0：设计与文档

目标：

- 明确对象模型
- 明确首批暴露接口
- 明确与现有 DBM binding 的联动边界

产出：

- 本文档

### 阶段 1：native 薄绑定

目标：

- 新增 `_ucdd` pybind11 模块
- 只做生命周期安全和内存所有权安全的薄包装

首批必做对象：

- runtime 管理对象
- `NativeCDD`
- `NativeLevelInfo`
- `NativeExtractionResult`
- `NativeBDDTraceSet`

首批必做接口：

- 基础构造与代数
- reduce/equiv
- delay/past/predt
- extract 系列
- bdd_to_array
- transition 系列

阶段验收标准：

- 不依赖 Python 高层包装也能从测试中完整调用这些操作

### 阶段 2：Python 高层包装与现有 DBM 联动

目标：

- 实现 `CDDContext`
- 实现 `CDD`
- 实现 `CDDExtraction`
- 实现 `BDDTraceSet`
- 打通 `Federation <-> CDD`
- 抽取出的 DBM 直接复用现有 `DBM`

首批必须完成的互操作：

- `CDDContext.from_context(context, bools=...)`
- `CDD.from_federation(federation)`
- `CDD.to_federation(require_pure=True)`
- `CDDExtraction.dbm -> DBM`

阶段验收标准：

- 现有 `Federation` 用户能无缝把纯 zone 提升成 CDD
- 纯 CDD 结果能回落到 `Federation`

### 阶段 3：高层 DSL 与易用接口

目标：

- 提供 bool 变量对象
- 提供 clock/bool 混合表达式
- 提供 reset/transition 的 Python 友好参数格式

这一步需要重点处理：

- clock 变量对象与现有 `Clock` 的关系
- bool 变量命名冲突
- 是否允许 `Context` 与 `CDDContext` 共存、互嵌或共享

阶段验收标准：

- 用户可以用 Python 友好方式表达 guard / update / mixed symbolic state

### 阶段 4：文档、测试与对照验证

目标：

- 增补高层 API 文档
- 增补联动示例
- 做与现有 UDBM 操作的对照测试

建议新增测试方向：

- `Federation.up()` 与 `CDD.from_federation(f).delay().to_federation()` 对照
- `Federation.down()` 与 `CDD.from_federation(f).past().to_federation()` 对照
- `predt` 与现有 Federation `predt` 的纯 clock 语义对照
- `extract_bdd_and_dbm()` 的稳定性与内存安全

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
