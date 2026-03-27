# UPPAAL 生态调研、pyudbm 现状判断与长期技术路线

## 说明

这份文档用于整合三类信息：

- `pyudbm` 当前仓库的实际状态
- 本轮关于 `CDD`、时间自动机(timed automata) 与形式化验证能力边界的讨论结论
- 对 `UPPAALModelChecker` GitHub 组织公开仓库的调研结果

本文档是仓库内的长期判断与路线文档，不替代现有的分阶段落地文档：

- [PR8_UCDD_BINDING_INTEGRATION_PLAN.md](/home/hansbug/oo-projects/pyudbm-2/mds/PR8_UCDD_BINDING_INTEGRATION_PLAN.md)

## 调研范围与时间

本次外部调研基于 `2026-03-24` 可见的 `UPPAALModelChecker` GitHub 组织公开仓库页面与各仓库 README / 描述信息。

主要入口：

- GitHub 组织主页：<https://github.com/UPPAALModelChecker/>
- 仓库列表页：<https://github.com/orgs/UPPAALModelChecker/repositories?type=all>

截至 `2026-03-24`，该组织公开可见仓库共 `13` 个。

## 一、pyudbm 当前现状

### 1. 当前已经完成的事情

从当前仓库状态看，`pyudbm` 已经不再只是“原始 DBM helper 的薄壳”。

目前已经具备：

- 面向历史 Python binding 兼容方向恢复的高层 `UDBM` API
  - `Context`
  - `Clock`
  - `Constraint`
  - `DBM`
  - `Federation`
- 已完成的 `UCDD` 接入
  - native 层 `_udbm` / `_ucdd` 分离
  - Python 高层 `CDDContext` / `CDD` / `CDDExtraction` / `BDDTraceSet`
  - `Federation <-> CDD` / `DBM -> CDD` 互操作
  - mixed bool/clock DSL
- 较完整的 Python public API 测试与 native 覆盖测试
- `ucdd.py` 的完整 pydoc 与示例
- 根目录的可执行示例脚本：
  - [test_cdd_timed_automaton_example.py](/home/hansbug/oo-projects/pyudbm-2/test_cdd_timed_automaton_example.py)

从最近提交历史看，`dev/ucdd` 分支已经完成了 UCDD 引入的主线阶段，并在 `2026-03-24` 之前补完了相应文档与回归记录。

### 2. 当前还没有完成的事情

即便如此，`pyudbm` 仍然不能被误判成“已经具备完整时间自动机模型检查能力”。

当前缺失的核心层主要是：

- 时间自动机模型层
  - `Location`
  - `Edge`
  - `Template`
  - `System`
  - channel / synchronization / update 等语义对象
- 明确的 symbolic reachability engine
  - waiting / passed
  - fixpoint 探索
  - subsumption / inclusion
  - 反向可达与前向可达工作流
- 与查询语言对应的检查层
  - `E<>`
  - `A[]`
  - witness / diagnostic trace
- 与上游 parser / trace 工具链的系统对接

所以当前更准确的判断是：

- `pyudbm` 已经接近“UPPAAL 符号状态与符号算子内核的 Python 暴露层”
- 但还不是一个完整的“UPPAAL 风格模型检查器”

## 二、刚才讨论得到的关键结论

### 1. CDD 不是 Federation 的别名

这点必须反复强调。

- `DBM`：一个凸的 clock zone
- `Federation`：多个 `DBM` 的并集
- `CDD`：统一的决策图对象，既能承载纯 clock 集合，也能承载 bool + clock 的混合符号状态

在纯 clock 场景下：

- `CDD` 与 `Federation` 经常语义可互转
- 但二者内部表示方式不同
- `CDD` 更适合继续承接 mixed symbolic analysis

在 mixed bool/clock 场景下：

- `Federation` 语义不够
- `CDD` 才是统一表示层

### 2. 时间自动机里的经典 symbolic state 本来就不是“只有 zone”

经典 timed automata / UPPAAL 文献里，常见写法本来就是：

- `(l, Z)`
- `(l, ν, Z)`

也就是：

- 离散位置 `l`
- 离散变量赋值 `ν`
- 时间约束 `Z`

相关出处：

- *Unification & Sharing in Timed Automata Verification*：
  <https://uppaal.org/texts/spin03.pdf>
- UPPAAL 相关综述 / 教程材料：
  <https://uppaal.org/texts/mm-master.pdf>
- UPPAAL 官方文档 `Symbolic Traces`：
  <https://docs.uppaal.org/gui-reference/symbolic-simulator/symbolic-traces/>

所以“真正的符号状态”从来都不是单独一个 zone。

### 3. 用 bool 编码 location，是对经典语义的工程映射

论文里通常直接写 `(l, Z)` 或 `(l, ν, Z)`。

而在 UCDD / Python 高层里，把 location 写成若干 bool，例如：

- `loc_closed`
- `loc_opening`
- `loc_open`
- `loc_closing`

本质上是在做这样一个工程映射：

- BDD 部分承载 `l` 与 `ν`
- CDD / DBM 部分承载 `Z`

这不是“论文逐字这么写”，但它和经典 symbolic semantics 是一致的，而且非常适合 UCDD 的混合图结构。

### 4. 有了 CDD，不等于已经自动拥有完整模型检查器

有了 `CDD` 以后，可以说：

- 时间自动机验证器最关键的“符号状态表示 + 符号算子层”已经基本可搭

因为已经有：

- `delay`
- `past`
- `predt`
- `transition`
- `transition_back`
- `transition_back_past`
- mixed bool/clock state
- `extract_bdd_and_dbm`

但距离“完整模型检查器”仍然差：

- 自动机建模层
- 系统组合与同步语义
- 查询语言
- 诊断轨迹生成
- 探索算法与状态空间管理
- 抽象 / 外推 / 剪枝策略

因此，`CDD` 的意义应理解为：

- 它让 `pyudbm` 有机会从“clock constraint wrapper”升级为“timed symbolic analysis kernel wrapper”
- 但后续仍然需要明确的建模层和验证层建设

## 三、UPPAALModelChecker 全部公开仓库调研结果

### 1. 仓库总览

截至 `2026-03-24`，`UPPAALModelChecker` 组织公开仓库共 `13` 个：

| 仓库 | 主要作用 | 与 `pyudbm` 的关系 |
| --- | --- | --- |
| `UPPAAL-Meta` | issue / roadmap / feature request 的元仓库 | 了解官方路线与需求入口 |
| `docs.uppaal.org` | 官方文档源仓库 | 官方概念、语义与用户文档参考 |
| `utap` | UPPAAL timed automata parser | 未来模型导入与语法前端的重要候选 |
| `UDBM` | DBM / Federation 核心库 | `pyudbm` 当前最核心上游之一 |
| `UCDD` | CDD / BDD / mixed symbolic 库 | `pyudbm` 当前新增核心上游之一 |
| `UUtils` | 公共工具库 | `UDBM` / `UCDD` 的底层依赖 |
| `tracer` | trace interpreter | 未来 witness / diagnostic trace 对接候选 |
| `uls` | UPPAAL language server | IDE / 编辑器生态配套，不是当前核心验证依赖 |
| `uppaal-libs` | 模型可动态加载的库 | 模型外部函数 / 数据交互扩展方向参考 |
| `uppaal-latex` | LaTeX typesetting 工具 | 文档与论文排版配套 |
| `toolchains` | 通用构建 toolchain | CI / 构建环境复用参考 |
| `libffi-build` | libffi 构建辅助 | 构建基础设施配套 |
| `python_dbm` | 历史 Python DBM binding | `pyudbm` 的重要行为参考源之一 |

### 2. 按生态角色分层

如果不按“仓库列表”而按“生态角色”看，可以更清楚。

#### A. 核心验证内核层

- `UUtils`
- `UDBM`
- `UCDD`
- `utap`
- `tracer`

这是最值得 `pyudbm` 长期盯紧的一层。

其中：

- `UDBM` 负责传统 zone / federation 语义
- `UCDD` 负责更强的 mixed symbolic 表示
- `utap` 负责模型语法前端
- `tracer` 负责 trace 解释与诊断结果消费
- `UUtils` 作为底层依赖支撑整个 C++ 栈

对 `pyudbm` 来说，这五个仓库共同勾勒出了一个非常清晰的未来方向：

- 不是只做 DBM wrapper
- 而是有条件进一步做“可由 Python 编排的 timed automata symbolic toolkit”

#### B. 文档与路线层

- `UPPAAL-Meta`
- `docs.uppaal.org`

这两者不直接提供求解能力，但提供：

- 官方术语
- 官方语义口径
- 官方路线与需求聚合入口

如果 `pyudbm` 长期希望和官方生态在概念上保持一致，这两者应当作为持续参考源。

#### C. 开发与编辑器配套层

- `uls`
- `toolchains`
- `libffi-build`

这层更多服务于：

- IDE / LSP 体验
- 构建环境统一
- 依赖构建自动化

它们说明 `UPPAAL` 生态已经不只是“单一模型检查器”，而是在往完整工程化工具链发展。

#### D. 模型扩展与外围使用层

- `uppaal-libs`
- `uppaal-latex`

这层说明官方生态也在覆盖：

- 模型运行时扩展
- 文档 / 论文 / 教学表达

它们不是 `pyudbm` 的近期主线，但对长期生态定位有参考意义。

#### E. 历史桥接层

- `python_dbm`

这个仓库尤其重要。

虽然它老、停更久、且明显带有 Python 2 / SWIG / Linux-only 时代痕迹，但它不是无关遗迹。

它至少说明了三件事：

1. UPPAAL / UDBM 生态历史上确实认真做过 Python binding
2. 高层 `Context` / `Clock` / `Federation` 风格不是本仓库自己的发明
3. `pyudbm` 的“先恢复历史 binding 语义，再现代化实现”这个方向是有历史依据的

### 3. 对每一个仓库的更具体判断

#### `UPPAAL-Meta`

官方自己把它定位为 issue reporting、feature request 和 public roadmap 的元仓库。

判断：

- 对 `pyudbm` 不提供直接技术复用
- 但它是观察官方生态优先级变化的窗口

补充记录（`2026-03-24` 再看）：

- 这个仓库更像公开问题池，而不是持续维护的技术路线文档仓库
- 仓库本体内容很少，真正有价值的信息主要在 issue、标签和讨论里
- 因此更准确的定位应当是：
  - 它适合拿来观察用户长期痛点、官方公开回应和需求聚集方向
  - 但不应把它当成 `pyudbm` 技术路线的主要依据

从现有 issue 池看，对 `pyudbm` 最值得关注的信号主要不是底层 `DBM/CDD` API 本身，而是：

- 文本化建模与非 XML 工作流需求
  - 例如用户明确偏好 `XTA` 这类更适合文本编辑和版本控制的格式
- 命令行与自动化输出需求
  - 例如结构化 query 结果、CLI 友好的结果消费、终端工作流
- trace / witness / counterexample 的可消费性需求
  - 例如更稳定的 trace 导出、更多条 counterexample、有限反例轨迹
- 外部扩展与 FFI 使用需求
  - 但官方讨论也明确暴露出 side effect 容易破坏验证语义健全性的问题
- symbolic 与 concrete 工作流边界的精细化需求
  - 例如某些变量、ODE 或扩展语义应在 symbolic 分析中被忽略，而在 concrete 分析中重新引入

这些信号对本路线的启发是：

- `pyudbm` 的价值不应停留在“再多包几层底层 binding”
- 更值得优先建设的是 Python-first 的建模、查询、trace、脚本化和结果消费工作流
- 但同时必须明确区分：
  - 哪些能力属于符号验证安全子集
  - 哪些能力只适合具体执行、外部交互或辅助分析

来源：

- <https://github.com/UPPAALModelChecker/UPPAAL-Meta>

#### `docs.uppaal.org`

官方文档源仓库，README 直接说明这是 `https://docs.uppaal.org` 的内容来源。

判断：

- 是术语、语义、用户面文档的第一参考源
- 后续写本仓库 tutorial / foundations 文档时，应持续对齐

来源：

- <https://github.com/UPPAALModelChecker/docs.uppaal.org>

#### `utap`

官方描述就是 `Uppaal Timed Automata Parser`。

判断：

- 如果未来 `pyudbm` 要从“符号内核 wrapper”走向“时间自动机建模与验证”
- 那么 `utap` 是最值得优先考虑的上游衔接点之一

来源：

- <https://github.com/UPPAALModelChecker/utap>

#### `UDBM`

官方 DBM 库，README 明确强调：

- 用于表示 timed automata 中的 clock constraints
- 支持 `up` / `down` / update / extrapolation / subtraction 等

判断：

- 这是 `pyudbm` 的历史主心骨
- 也是纯 zone 工作流永远不能丢的基础层

来源：

- <https://github.com/UPPAALModelChecker/UDBM>

#### `UCDD`

README 直接说明：

- `CDD` 是一种类似 `BDD` 的结构
- 用于高效表示 timed automata verification 中出现的某些非凸集合
- 支持 set-theoretic operations 与 clock operations

判断：

- 这不是“UDBM 的小补丁”
- 而是向 fully symbolic timed analysis 更进一步的关键库
- 本仓库当前已经把它拉进了真正的公开 API 主线，这是正确方向

来源：

- <https://github.com/UPPAALModelChecker/UCDD>

#### `UUtils`

官方描述是 utility library。

判断：

- 对 Python 用户不可见
- 但在工程上是 `UDBM` / `UCDD` 的基础依赖，必须尊重其上游边界

来源：

- <https://github.com/UPPAALModelChecker/UUtils>

#### `tracer`

官方描述是 `Uppaal trace interpreter`。

判断：

- 如果未来 `pyudbm` 要做 witness / diagnostic trace 或反例解释
- 这是最应优先研究的官方配套仓库之一

来源：

- <https://github.com/UPPAALModelChecker/tracer>

#### `uls`

官方描述是 `UPPAAL Language Server for syntax highlighting and auto-completion`。

判断：

- 它不是验证内核
- 但说明 UPPAAL 正在工程化编辑器生态
- 未来若 `pyudbm` 发展出 Python 侧模型 DSL，IDE 集成可以借鉴其语义对象与补全思路

来源：

- <https://github.com/UPPAALModelChecker/uls>

#### `uppaal-libs`

README 说明它是可被 Uppaal 模型动态加载的库示例。

判断：

- 它更偏模型运行时扩展与集成接口
- 对 `pyudbm` 近期不构成主线依赖
- 但对“如何让模型与外部世界交互”很有参考价值

来源：

- <https://github.com/UPPAALModelChecker/uppaal-libs>

#### `uppaal-latex`

LaTeX 排版工具仓库。

判断：

- 对实现层影响很小
- 但说明官方对模型表达、论文排版、教学传播有长期积累

来源：

- <https://github.com/UPPAALModelChecker/uppaal-latex>

#### `toolchains`

官方描述是 `Common Toolchains for Building UPPAAL`。

判断：

- 这是非常工程化的仓库
- 对 `pyudbm` 的直接 API 设计帮助不大
- 但对 cross-platform 构建与 CI 统一有现实参考价值

来源：

- <https://github.com/UPPAALModelChecker/toolchains>

#### `libffi-build`

官方描述是 `Builds Foreign Function Interface library`。

判断：

- 是底层构建支持仓库
- 说明官方也在维护自己的依赖构建链
- 对 `pyudbm` 的直接业务语义帮助有限

来源：

- <https://github.com/UPPAALModelChecker/libffi-build>

#### `python_dbm`

仓库页与旧页面信息表明，它是历史 Python 2 SWIG binding，对 Linux 和旧安装流程有明显时代局限。

判断：

- 不是实现模板
- 但仍然是行为语义与 API 风格的最重要历史参照之一
- 本仓库 `srcpy2/` 的长期意义，正是把这一历史 binding 作为“语义考古参考”，而不是直接照搬代码

来源：

- <https://github.com/UPPAALModelChecker/python_dbm>
- <https://github.com/UPPAALModelChecker/python_dbm#readme>

## 四、对整体形势的判断

### 1. 官方生态的真实形势

把全部仓库放在一起看，最明显的结论是：

- UPPAAL 生态并不是“只有一个 GUI 工具”
- 它实际上已经形成了一个分层的工程生态

至少可以分成：

- 语法前端：`utap`
- clock symbolic core：`UDBM`
- mixed symbolic core：`UCDD`
- trace / diagnostic：`tracer`
- 文档与路线：`docs.uppaal.org` / `UPPAAL-Meta`
- IDE / tooling：`uls` / `toolchains`
- 外部扩展：`uppaal-libs`

这意味着：

- `pyudbm` 如果只把自己理解成“给 DBM 暴露几个 C API”
- 那么它会天然低估自己在整个生态中的潜在位置

### 2. pyudbm 当前所在的位置

当前 `pyudbm` 已经处在一个很关键、但仍未完全定型的位置：

- 它已经越过“只有原始 DBM helper”的阶段
- 也已经越过“只做纯 zone DSL”的阶段
- 现在正处于从“高层 UDBM Python binding”向“Python 可编排的 timed symbolic kernel”演进的节点

这是一个很好的位置，但也有风险。

### 3. 当前最大的机会

最大的机会是：

- 目前官方生态里的关键验证内核库都已经公开且模块化
- `pyudbm` 又已经打通了 `UDBM + UCDD`
- 这使得它很适合成为“Python 侧 timed symbolic experimentation / teaching / prototyping 入口”

这条路的价值非常实际：

- 教学上，Python 比纯 C++ 更容易演示 symbolic semantics
- 研究上，Python 更适合快速验证建模和探索算法原型
- 工程上，Python 更适合做胶水层，把模型、文档、可视化、脚本化分析拼接起来

### 4. 当前最大的风险

最大的风险不是技术做不到，而是路线走偏。

主要风险有四类：

1. 只停留在 binding 层，不继续上探模型层与验证层
2. 把 `CDD` 误降级成“又一个 Federation 容器”
3. 为了快而堆出一层不稳定的 Python API，丢掉与历史 binding / 上游语义的一致性
4. 过早尝试“做一个完整 UPPAAL 替代品”，导致项目面过大、交付失焦

### 5. 补充：完整验证链路、公开官方仓库边界与 `verifyta`

如果把目标进一步收紧成“搭出一条完整可用的 UPPAAL 形式化验证链路”，那么必须把“公开官方仓库能提供什么”与“仍需依赖官方发行版或本仓库自建什么”分开看。

基于 `2026-03-24` 可见的 `UPPAALModelChecker` 公开仓库列表，一个重要判断是：

- 公开官方仓库里已经有 parser、symbolic core、trace interpreter、LSP、动态库示例等组件
- 但没有看到一个公开的、可直接作为完整 verifier engine 源码依赖的 `verifyta` 仓库

这意味着一个非常实际的边界：

- 如果目标是“尽快让完整链路跑起来”，那就不能只靠继续引入公开 GitHub 仓库
- 还必须准备官方 UPPAAL 发行版中的 `verifyta` 命令行工具，或者由本仓库自行实现验证主循环

因此，对 `pyudbm` 来说，近期最现实的完整链路应该理解为：

- Python 建模 DSL / 内部 IR
- Python 性质 DSL / query 对象
- 模型导出为 UPPAAL 兼容格式
- 调用 `verifyta`
- 消费验证结果、`xtr` trace 与相关诊断输出
- 在 Python 中提供结构化结果对象

也就是说，更现实的近期链路是：

- `Python DSL -> XML/XTA -> verifyta -> result/trace -> Python object`

而不是误以为：

- `UTAP + UDBM + UCDD + tracer = 完整 verifier`

它们并不等价。

对公开官方仓库的更精确角色判断如下：

- `UDBM` / `UCDD` / `UUtils`
  - 负责底层符号数据结构与算子
  - 是验证内核的重要底座
  - 但不是完整模型检查器
- `utap`
  - 负责模型解析、类型检查与文档表示
  - 适合作为 import / type-check / compatibility front-end
  - 但不负责性质验证主循环
- `tracer`
  - 负责解释 `xtr` trace
  - 适合作为 witness / diagnostic trace 的消费后端
  - 但本身不产生 trace，也不做验证
- `uls`
  - 主要服务编辑器与自动补全
  - 不是验证链路主依赖
- `uppaal-libs`
  - 主要服务 external functions / 动态库扩展
  - 不是验证链路主依赖
- `toolchains`
  - 主要服务构建环境统一
  - 不是验证语义组件

这直接导出一个近期优先级判断：

- 真正的下一个阻塞项不是“再引一个官方 repo”
- 而是先把 `Location / Edge / Template / System`、query 表示、结果对象和 `verifyta bridge` 做出来

在这之后，再评估：

- `utap` 是否作为模型导入 / 语法对齐 / 类型检查层引入
- `tracer` 是否作为 trace 解释后端引入

这里还有一个工程现实必须记录：

- 当前本仓库本地构建仍然是 `CMake 3.15 + C++17` 体系
- 而公开上游当前 `UDBM` / `UCDD` 已经明显向更高的工具链要求移动
- `utap` 也会新增 `libxml2`、`flex`、`bison` 等依赖

因此，后续如果要接官方更多原生仓库，不应默认理解成“直接追最新 upstream head 即可”。
更稳妥的方式应是：

- 先把验证链路的 Python 层边界定义好
- 再谨慎决定哪些原生仓库做 hard dependency，哪些先做 optional / sidecar integration

`verifyta` 的官方资源入口也值得单独记一下：

- 官方文档页：
  - <https://docs.uppaal.org/toolsandapi/verifyta/>
  - 文档明确说明 `verifyta` 是 UPPAAL 发行版 `bin` 目录中的命令行 verifier
- 官方下载页：
  - <https://uppaal.org/downloads/>
  - 这里提供当前平台发行包，也明确写了如果只使用 `verifyta`，则 Java 不是必需条件
- 官方 Docker 文档：
  - <https://docs.uppaal.org/toolsandapi/docker/>
  - 这里给出了把 UPPAAL engine 放进容器、调用 `verifyta.sh --version`、以及处理 libc 兼容问题的方式
- 官方文件格式文档：
  - <https://docs.uppaal.org/toolsandapi/file-formats/>
  - 这里说明了 `.xml` / `.xta` / `.ta` / `.q` / `.xtr` 等格式关系
- 官方 symbolic trace 文档：
  - <https://docs.uppaal.org/gui-reference/symbolic-simulator/symbolic-traces/>
  - 这里明确指出 `verifyta` 可以生成 forward stable traces

综合起来，对“完整链路”更准确的近期判断是：

- 官方公开仓库已经足够支撑“模型前后处理 + 符号内核 + trace 消费”
- 但若想尽快得到完整、可运行、与官方工具兼容的验证链路，`verifyta` 仍然是必须认真对接的核心外部资源
- 若未来希望摆脱 `verifyta` 依赖，则那一部分不会通过“再多引几个官方 repo”自动完成，而必须由本仓库自行补出 verifier 层

## 五、补充定位：面向 Python 的“UPPAAL 工作流重建”

基于当前仓库现状与本轮讨论，我认为可以把长期定位进一步收紧成下面这句话：

- `pyudbm` 的长期目标，不应只是一个 Python binding
- 它应当逐步发展成一个“面向 Python 的 UPPAAL 工作流实现”

但这里有一个必须写清楚的边界：

- “面向 Python 的 UPPAAL 工作流实现”不等于“在本仓库里把 DBM / CDD / parser / verifier 全部从零重写成纯 Python 算法实现”
- 更合理也更符合本仓库约束的定义是：
  - 用户侧工作流、建模语言、性质语言、编排体验、自动化接口都以 Python 为主
  - 核心符号算法层继续优先复用 `UDBM` / `UCDD` / 其他官方成熟内核

也就是说，应该追求的是：

- Python-first
- DSL-first
- LLM-friendly
- workflow-complete

而不是：

- 重新在 Python 中发明一套独立的 DBM / CDD 算法栈

### 1. 这个新定位的核心含义

如果按照你的思路把目标再往前推进，那么 `pyudbm` 的长期愿景可以表述为：

- 用户不需要接触 XML 才能建模
- 用户不需要离开 Python 才能写系统、写性质、跑验证、读结果
- LLM 可以直接参与模型生成、性质生成、验证脚本编排和结果解释
- 最终体验上，它应当像一个“Python 化、DSL 化、可编排”的 UPPAAL

这意味着本项目的主线会从：

- “暴露 DBM / CDD API”

进一步升级为：

- “在 Python 中重建 UPPAAL 的主要使用工作流”

### 2. 为什么这个方向是有现实价值的

这条路的价值不只是“写起来更爽”，而是有明确工程意义。

#### A. 比 XML 更适合人写，也更适合程序生成

UPPAAL 传统 XML 格式适合工具持久化和 GUI 交换，但并不适合作为人类首选建模语言。

相比之下，Python DSL 的优势是：

- 更接近程序员与研究者的自然表达
- 更容易做抽象、复用、参数化、组合
- 更容易嵌入现有 Python 数据处理、可视化、实验脚本工作流

#### B. 更适合 LLM 参与

如果建模语言和性质语言都采用结构清晰、语义显式的 Python DSL，那么 LLM 更容易：

- 读懂系统结构
- 生成模型草稿
- 修改 guard / invariant / reset
- 生成验证问题
- 解释反例或轨迹

而 XML 更像序列化格式，不适合作为 LLM 的主要工作界面。

#### C. 更适合脚本化验证与实验

如果 `pyudbm` 真的把模型、性质、验证器、轨迹、可视化都放进 Python 工作流里，那么它就会天然适合：

- 研究原型
- 教学
- 批量实验
- 自动生成与自动分析

### 3. 但为什么仍然不能把“全 Python”理解成“重写所有内核”

这里必须保留技术纪律。

本仓库的合理方向应该是：

- 用 Python 重建建模层、性质层、工作流层和自动化层
- 用上游成熟 native 库支撑底层时钟符号运算

原因很直接：

- `UDBM` / `UCDD` 已经是经过长期积累的核心内核
- 这些部分重写成本高、风险大，而且极易与官方语义漂移
- 本仓库真正稀缺的，不是“再实现一遍 DBM 算法”，而是“把官方符号内核变成一个现代 Python 工作流平台”

所以这个定位更准确的说法应当是：

- “全 Python 版的使用体验和工作流”
- 而不是“所有底层算法都改写成 Python”

## 六、建议的长期技术路线

这里给出的不是“下一个 PR 做什么”，而是一个更长线的技术路线。

### 路线一：先把 `pyudbm` 稳定成“符号内核层”

这是最近期、也是最关键的一步。

目标：

- 稳定 `Context` / `Clock` / `Federation` 主线
- 稳定 `CDDContext` / `CDD` 主线
- 明确 pure / mixed 两条工作流的边界
- 把 public API、pydoc、示例、互操作、回归体系全部做扎实

需要坚持的原则：

- 保持高层 API 面向用户，而不是面向 pybind11 细节
- 保持与历史 `python_dbm` 行为的一致性优先
- 保持对上游 `UDBM` / `UCDD` 语义的忠实映射

### 路线二：把建模语言主轴明确切到 Python DSL

这一步不是简单补几个类，而是要明确：

- 本项目的主建模语言应当是 Python DSL
- XML 最多作为互操作格式，而不应继续是主作者接口

建议把 Python 建模 DSL 拆成两层：

#### A. 用户 DSL 层

面向用户直接写：

- 时钟
- 离散变量
- 位置
- 边
- 不变式
- guard
- reset
- 同步

并保持尽量自然的书写体验。

#### B. 规范中间表示层

在 DSL 之下建立一个稳定的内部 IR：

- `Model`
- `Template`
- `Location`
- `Edge`
- `VariableDecl`
- `ClockDecl`
- `BoolDecl`
- `Property`

这样做的价值是：

- DSL 可以演进，但执行层不必跟着混乱
- 后续如果要支持 XML import/export，也有稳定落点
- LLM 生成 DSL 后，可以先编译进 IR 再做验证

### 路线三：把性质语言也做成 Python DSL

如果目标真的是“面向 Python 的 UPPAAL 工作流”，那么性质语言不能继续缺席。

建议把性质语言也设计成 Python DSL，而不是文本拼字符串。

例如长期可以支持：

- `Exists.finally_(...)`
- `Always.globally_(...)`
- `LeadsTo(...)`
- `DeadlockFree()`

或者等价但更 Pythonic 的形式。

需要注意：

- 第一版不必贪大求全
- 但一定要从一开始就避免“性质写成随手拼接的字符串”

这样做的原因是：

- 结构化 DSL 更易检查
- 更易做语义报错
- 更易做自动补全
- 更易被 LLM 安全生成和修改

### 路线四：在 Python 层引入最小时间自动机模型对象

当符号内核层稳定后，下一步最值得做的不是直接上查询语言，而是先补“模型对象层”。

建议引入：

- `Location`
- `Edge`
- `Template`
- `System`
- `Guard`
- `Reset`
- `Invariant`
- `Synchronization`

这一层的目标不是重新实现 parser，而是让 Python 侧能自然表达：

- 一个系统由哪些位置和边组成
- 哪些变量是 clock，哪些是 bool / discrete
- 边上的 guard / update / synchronization 是什么

这样做的价值是：

- CDD 的 mixed state 才有稳定语义归宿
- symbolic reachability 才有明确输入对象

这里和上面的 DSL / IR 不是冲突关系，而是同一条主线的不同层次：

- DSL 负责“怎么写”
- 模型对象层负责“系统最终长什么样”
- 符号执行层负责“如何验证”

### 路线五：引入最小可用的 reachability engine

有了模型对象以后，再做：

- forward symbolic reachability
- backward predecessor exploration
- safety / emptiness 级别检查

第一版不必上来就追求完整 CTL / TCTL。

第一阶段建议只做：

- 初始符号状态生成
- 基于 `delay` / `transition` 的前向扩展
- 基于 `transition_back_past` / `predt` 的后向分析
- passed / waiting 去重
- 基础 inclusion / subsumption

这一步完成后，`pyudbm` 才真正开始具备“面向时间自动机的形式化验证原型框架”。

### 路线六：做“LLM 友好”的错误模型与结果模型

如果要把 LLM 真正拉进工作流，那么不能只提供“能跑”。

还必须让系统输出：

- 结构化错误
- 稳定的 pretty-print
- 语义明确的异常信息
- 可机器消费的验证结果对象

建议长期提供：

- 结构化建模错误
- 结构化性质编译错误
- 结构化验证结果
- 可遍历的 witness / counterexample / symbolic trace 对象

这样 LLM 才能真正参与：

- 自动修模型
- 自动修性质
- 自动解释失败原因

### 路线七：向上游前端与 trace 工具对接

这一步最值得优先评估两个方向：

- `utap`
- `tracer`

建议：

- 优先研究 `utap` 是否适合作为模型导入前端
- 优先研究 `tracer` 是否适合作为 witness / diagnostic trace 的解释后端

原因很简单：

- parser 和 trace 解释器这两层自己重造，成本高而且容易和官方语义漂移

### 路线八：最后再考虑更完整的查询层

等前面三层都稳了，再考虑：

- `E<>`
- `A[]`
- maybe 更多分支语义与 trace 输出

否则很容易出现：

- 语法先做了
- 背后的 symbolic engine 还不够稳
- 查询语言反而变成表面功能

### 路线九：XML 只做互操作，不再做主接口

如果目标是 Python DSL 主导，那么 XML 在本项目中最合理的位置应当是：

- import
- export
- compatibility bridge

而不是：

- 主建模格式
- 主性质格式
- 主工作流入口

建议原则：

- 用户优先写 Python DSL
- 需要与传统 UPPAAL 生态交换时，再做 XML 转换
- XML 语义支持应服务兼容，而不是主导 API 设计

## 七、具体建议

### 1. 对本仓库的角色定位建议

建议把 `pyudbm` 的长期定位明确成：

- “以 Python DSL 为主接口、以官方符号内核为底座的 UPPAAL 工作流平台”

而不是：

- “只做 UDBM 的 Python 包装”
- 或“在本仓库里重写所有内核算法的纯 Python 替代品”

这个定位最稳，也最符合当前仓库现实。

### 2. 对近期研发优先级的建议

优先顺序建议如下：

1. 稳定 public API、文档和示例
2. 定义 Python 建模 DSL 与内部 IR
3. 定义 Python 性质 DSL 与属性对象模型
4. 补最小时间自动机模型层
5. 做 reachability 原型
6. 设计结构化结果、错误和 trace API
7. 评估 `utap` / `tracer` 对接
8. 最后再扩更完整查询层与 XML 互操作

补充记录：

- 如果近期目标不是“研究原型”，而是“尽快打通一条完整可运行的官方兼容验证链路”
- 那么在上述顺序之外，还应尽早插入：
  - `verifyta bridge`
  - `verifyta` 结果解析
  - `xtr` / trace 消费链路

换句话说：

- `utap` / `tracer` 的深度集成可以稍后评估
- 但 `verifyta` 的调用编排与结果对象化，反而更早会成为真正的工程阻塞项

### 3. 对文档体系的建议

建议后续文档分成三类：

- `mds/`
  - 内部设计、路线、阶段计划、生态判断
- `docs/source/foundations/`
  - 面向用户和学习者的概念教程
- 根目录可执行脚本
  - 面向快速理解的 runnable examples

尤其是 `CDD` 相关内容，建议后续持续保留三种表达：

- 一份设计文档
- 一份教程文档
- 一份可直接运行的示例脚本

而在未来引入 Python DSL 后，建议再增加两类材料：

- Python DSL 建模指南
- Python DSL 性质表达指南

### 4. 对实现策略的建议

建议长期保持以下约束：

- 不在 `UUtils/`、`UDBM/`、`UCDD/` 子模块内做本地修补
- wrapper 尽量薄，但 public API 必须是高层、可用、可解释的
- 不把 Python 层写成无法维护的临时胶水
- 每一个阶段完成后都做完整重编译与完整回归

同时再增加三个面向 DSL / LLM 的长期约束：

- Python DSL 必须可静态检查、可 pretty-print、可稳定序列化
- 错误信息必须结构化，而不是只抛一串难以消费的文本
- 内部 IR 与执行层边界必须稳定，避免 DSL 直接耦合 native binding 细节

### 5. 对产品化方向的进一步建议

如果真要朝“Python 版 UPPAAL 工作流”推进，我建议把最终产品目标拆成三个层次：

#### A. Core

- `UDBM` / `UCDD` 的 Python 暴露
- 高层 symbolic state / operation API

#### B. Modeling

- Python DSL 建模
- Python DSL 性质表达
- IR
- 验证入口

#### C. Workflow

- 轨迹对象
- 结果解释
- 可视化
- notebook / script / LLM 协作体验

这样分层之后，项目既不会失焦，也不会把“Python 版 UPPAAL”误解成“什么都先重写一遍”。

## 八、结论

截至 `2026-03-24`，综合本仓库现状与官方生态调研，可以给出一个明确判断：

- `pyudbm` 已经从“历史 UDBM Python binding 的恢复工程”走到了“Python 化 UPPAAL 工作流平台”的门口
- `UCDD` 的引入不是附属改造，而是把项目从纯 zone 世界推进到 mixed symbolic 世界的关键一步，也是后续时间自动机工作流 Python 化的基础
- 官方公开生态已经给出了足够清晰的上下游拼图：`utap`、`UDBM`、`UCDD`、`tracer`、`docs`
- 因此，本项目长期最有价值的方向，不是停在 binding 层，也不是在本仓库里重写所有底层算法，而是分阶段把“以 Python DSL 为主、以官方符号内核为底座的 UPPAAL 工作流”搭起来

如果这个方向坚持下去，那么 `pyudbm` 的长期价值会非常明确：

- 它既能服务历史 `python_dbm` 兼容与现代化
- 又能成为 UPPAAL 生态在 Python 侧最自然的建模、验证、实验与 LLM 协作平台
