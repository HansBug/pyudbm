# UTAP Python Binding 集成实施方案

## 说明

这份文档用于把当前关于 `UTAP` 接入 `pyudbm` 的讨论，整理成一份可以直接指导后续工程实施的仓库内方案文档。

本文档的目标不是立即改代码，而是先明确下面几件事：

1. `UTAP` 在当前仓库里应该扮演什么角色。
2. Python binding 的边界应该放在哪里。
3. 它和现有 `UDBM` / `UCDD` Python 层的关系应该如何设计。
4. 构建、打包、测试、文档需要补哪些工作。
5. 这项工作应该如何分阶段落地，避免一开始就把对象模型和 API 做重。

本文档是设计与实施计划，不是最终 public API 承诺。实际命名和模块布局可以在实现时做小幅调整，但不应偏离本文档定义的边界与阶段计划。

## PR 信息

- Pull Request：待创建，创建后回填
- 当前文件路径：`mds/UTAP_PYBINDING_INTEGRATION_PLAN.md`

## 相关背景

当前仓库已经完成了两条核心 native / Python binding 链路：

- `UDBM`
  - native pybind11 模块 `_udbm`
  - Python 高层兼容 API `Context` / `Clock` / `Constraint` / `DBM` / `Federation`
- `UCDD`
  - native pybind11 模块 `_ucdd`
  - Python 高层 API `CDDContext` / `CDD` / mixed bool/clock DSL

这意味着当前仓库已经不再是“只暴露几个 C 函数”的低层封装，而是开始形成面向 Python 工作流的分层接口。

但当前仓库仍缺失一块关键前端层：

- UPPAAL 模型的导入前端
- query / property 的语言前端
- 与 XML / XTA 的互操作层

`UTAP` 正好对应这块能力。

## 一、总体判断

### 1. `UTAP` 是什么

`UTAP` 不是验证后端，也不是 DBM / CDD 算法库。

更准确地说，`UTAP` 是一套 UPPAAL 语言前端(frontend)基础设施，主要覆盖：

- `XML` / `XTA` / `TA` 模型解析
- 文本语法与表达式解析
- 类型检查
- 特性检查
- 查询 / 属性解析
- 文档对象构建
- pretty print
- XML 写回

因此，把 `UTAP` 接进 `pyudbm` 的意义，不在于“再多一个 native 库”，而在于把 `pyudbm` 往“Python-first 的 UPPAAL 工作流平台”推进一层：

- `UTAP` 做模型与查询语言前端
- `UDBM` / `UCDD` 做底层符号语义核心
- `pyudbm` Python 层负责组织稳定、易用、可组合的工作流 API

### 2. 它不是什么

在本仓库里，`UTAP` 不应被误判为：

- 一个直接替代 `verifyta` 的模型检查器
- 一个天然就能把所有模型语义自动转成 `Federation` / `CDD` 的库
- 一个应该被完整原样暴露成 Python 可变 AST 的对象系统

这几种理解都会把边界做错。

### 3. 对项目方向的价值

把 `UTAP` 接进来后，仓库能补上的不是“更多底层 helper”，而是下面几类真正缺失的能力：

- 读官方模型
- 看官方模型
- 解析并检查查询语言
- 做模型级别的 introspection
- 为后续 Python DSL / workflow 提供 import-export 兼容面
- 为后续 timed automata / symbolic workflow 打基础

因此，`UTAP` 的角色应该是：

- 第一阶段做互操作前端
- 第二阶段做语义桥接入口
- 长期做 Python-first 建模工作流与 UPPAAL 兼容格式之间的桥梁

## 二、当前仓库现实与接入前提

### 1. 当前已经有的构建基础

当前仓库已经不是“完全没接 UTAP”。

现状是：

- `UTAP` 已经作为 submodule 存在
- `Makefile` 已经提供 `utap_build` / `utap_test` / `utap_install`
- `make bin` 已经把 `UTAP` 纳入完整 native 依赖链
- 本地 `bin_install/` 已经能看到 `UTAP` 安装产物
- `cibuildwheel` 的 Linux / macOS / Windows 预构建脚本也已经在编译、测试并安装 `UTAP`

这意味着：

- native 依赖进入仓库的路径已经打通
- CI 并不需要从零开始理解 `UTAP`
- 真正还没有落地的是“根 Python 扩展构建如何消费 `UTAP`”和“Python 层暴露什么 API”

### 2. 当前还缺的接入点

目前根构建系统和 Python public API 还没有纳入 `UTAP`：

- 根 `CMakeLists.txt` 目前只消费 `UUtils` / `UDBM` / `UCDD`
- `setup.py` 目前只构建 `_udbm` / `_ucdd`
- `pyudbm.binding` 还没有 `utap.py` 包装层
- 根 `pyudbm` 包也还没有任何面向模型导入的接口

因此，这次工作不是“把 UTAP submodule 加进仓库”，而是“把它真正接进 binding 层和 Python API 层”。

### 3. 依赖与工具链现实

`UTAP` 会给当前仓库带来比 `UDBM` / `UCDD` 更重一些的前端依赖现实：

- `flex`
- `bison`
- `libxml2`

这几个依赖对本地构建与 wheel 构建都有影响。

但当前仓库已经针对三大平台做了相当多准备：

- Linux 的 `cibw` 预构建脚本会自建 / 配置 `flex` 与 `bison`
- macOS 脚本会通过 Homebrew 安装 `flex` / `bison`
- Windows 脚本会安装 `winflexbison3`

所以新的工作重点不是“有没有工具链”，而是：

- `_utap` 模块最终如何链接
- wheel 内是否需要额外打包 runtime library
- 文档与测试如何跟上

## 三、集成目标与边界

### 1. 范围内目标

本方案建议把第一阶段的 `UTAP` 集成目标限定为下面几类能力：

- 提供 `XML` / `XTA` 的 Python 侧导入接口
- 提供文档对象的只读访问能力
- 提供查询 / property 的 Python 侧解析接口
- 提供 pretty print / 规范化文本输出能力
- 提供模型的 feature summary / capability summary
- 提供面向后续语义桥接的稳定中间层

### 2. 明确不在第一阶段范围内的内容

第一阶段不应承诺下面这些事情：

- 完整可编辑 AST
- Python 继承 `ParserBuilder` / `StatementBuilder` 的 callback 风格扩展
- 任意 `UTAP` 表达式自动转 `Federation` / `CDD`
- 完整验证工作流
- witness / trace replay / simulator 风格接口
- 与 `verifyta` 的命令级绑定

### 3. 实施原则

本方案建议遵循下面几个原则：

#### 原则一：先窄后宽

先做一条窄而稳的 binding 边界，把模型导入、查询解析、只读 introspection 先做好，再逐步加深。

#### 原则二：先读后写

先解决 read path：

- parse
- inspect
- pretty print
- query parse

再考虑 write path 和可编辑对象模型。

#### 原则三：先前端互操作，再语义编译

先把 `UTAP` 当成前端和互操作层，而不是一上来就把它和 `UDBM/UCDD` 强耦合成“自动求解前端”。

#### 原则四：Python 层要给稳定 facade

不要把 `UTAP` 内部复杂对象图直接暴露成最终 public API。应当由 Python 层提供更稳定、更薄、更容易长期维护的 facade。

## 四、推荐的分层结构

### 1. 总体分层

建议采用三层结构：

#### A. native binding 层

新增一个独立 pybind11 模块：

- `pyudbm.binding._utap`

该层职责：

- 持有 native `UTAP::Document`
- 调用 `parse_XML_*` / `parse_XTA`
- 调用 query parser / property parser
- 提供少量稳定的原生只读访问器
- 负责 C++ 生命周期管理

该层不应直接成为最终 public API。

#### B. Python 包装层

新增一个 Python 包装模块：

- `pyudbm.binding.utap`

该层职责：

- 对 `_utap` 的 native handle 做 Pythonic 包装
- 定义面向用户的对象命名与行为
- 负责把 native object graph 转成更稳定的只读视图或 dataclass
- 负责异常信息、可选参数、文本接口与文档字符串

#### C. 更高层 workflow / model 层

长期可以在这层之上继续长出：

- `pyudbm.model`
- `pyudbm.workflow`
- 更高层 Python DSL

但这不是第一阶段必须做的事情。

### 2. 模块命名建议

第一阶段建议采用下面的命名策略：

- native：`pyudbm.binding._utap`
- Python 包装：`pyudbm.binding.utap`

根包 `pyudbm/__init__.py` 第一阶段不建议直接 re-export `UTAP` 相关对象。

原因：

- 当前根包 public surface 仍以历史 UDBM 高层兼容 API 为主
- 直接把一整批 `Model` / `Template` / `Query` 暴露到根命名空间，会让 public API 膨胀得太快
- 先放在 `pyudbm.binding.utap` 更利于后续调整

等接口稳定后，再决定是否提升到根包。

## 五、建议暴露的 Python API 形状

### 1. 第一阶段推荐暴露的入口函数

建议优先提供以下函数：

- `load_xml(path, *, new_syntax=True, libpaths=None) -> ModelDocument`
- `loads_xml(text, *, new_syntax=True, libpaths=None) -> ModelDocument`
- `load_xta(path, *, new_syntax=True) -> ModelDocument`
- `loads_xta(text, *, new_syntax=True) -> ModelDocument`
- `parse_query(text, document, *, tiga=False) -> ParsedQuery`
- `builtin_declarations() -> str`

如果 `UTAP` 某些底层写接口只支持文件路径，则 Python 层可以先只公开：

- `document.write_xml(path)`

不要在第一阶段为了“必须支持字符串写出”而强行发明不稳定方案。

### 2. 第一阶段推荐暴露的对象

建议 Python 层以“只读 facade + 小型 value object”为主，优先提供：

- `ModelDocument`
- `ModelTemplate`
- `ModelLocation`
- `ModelEdge`
- `ModelProcess`
- `ModelQuery`
- `ParsedQuery`
- `ModelFeatures`

### 3. `ModelDocument` 的推荐职责

`ModelDocument` 应该是 Python 侧的主入口对象，建议提供：

- `templates`
- `processes`
- `queries`
- `options`
- `features`
- `has_dynamic_templates`
- `has_strict_invariants`
- `has_stop_watch`
- `has_urgent_transition`
- `pretty()`
- `write_xml(path)`

另外可以提供一些轻量辅助方法：

- `find_template(name)`
- `template_names()`
- `clock_names(scope=...)`
- `bool_like_names(scope=...)`

### 4. 表达式对象的建议边界

表达式是整个接口设计里最需要克制的一块。

不建议第一阶段就把 `UTAP::expression_t` 的完整 AST 结构原样暴露给 Python。

更稳妥的做法是：

- 第一阶段只提供规范化文本表示和基础元数据
- 第二阶段如果确实需要，再逐步补 AST 访问能力

第一阶段的表达式包装建议只暴露：

- `text`
- `kind`
- `position`
- `is_empty` 或类似基础状态

如果某些位置目前没有稳定的 kind/value 提取接口，也可以先只暴露：

- `text`

### 5. 查询对象的建议边界

查询层比表达式层更适合尽早暴露，因为：

- `UTAP` 对 query parse 和 quantifier 类型已经有较稳定抽象
- `query` 是用户直接感知的高层对象
- 后续和 `verifyta` / symbolic workflow 的连接点也更自然

建议 `ParsedQuery` 至少包含：

- `text`
- `quantifier`
- `options`
- `expression`
- `is_smc`
- `declaration`
- `expectation`

对于复杂 query 子结构，可以先保留为规范化文本，不要一开始就追求完整结构化。

## 六、native binding 设计建议

### 1. 为什么不建议直接完整暴露 `UTAP::Document` 对象图

`UTAP` 的内部数据结构包含：

- `list`
- `deque`
- 多个对象之间的裸指针和内部引用关系
- 稳定迭代器 / 稳定地址假设

这类对象图如果按“节点全绑定”的思路做 pybind，会立刻遇到几个问题：

- Python 侧对象生命周期和父对象持有关系难以讲清
- 子对象引用在父对象析构后容易悬空
- 可变接口很难约束一致性
- 维护成本高

因此第一阶段建议优先采用：

- `Document` 由 native handle 持有
- 其他对象以只读 snapshot 或受控 view 的形式暴露

### 2. 建议的 native 暴露策略

推荐两种可以混用的策略：

#### 策略 A：handle + read-only method

例如：

- `_NativeUTAPDocument`
- `_NativeUTAPQuery`

对象保留 native 生命周期，但 Python 侧只能通过只读方法访问。

#### 策略 B：native 转 Python 友好的 value snapshot

例如：

- location summary
- edge summary
- query summary

在 C++ 层直接提取为简单结构，再交给 Python 层包装。

综合来看，第一阶段更推荐：

- `Document` 保持 handle
- template / location / edge / query 多数以 snapshot 或轻量只读 wrapper 提供

### 3. Builder 接口为什么不宜先开放

`UTAP` 的 `ParserBuilder` / `StatementBuilder` / `DocumentBuilder` 体系很强，但不适合作为第一阶段的 Python public surface。

原因：

- 虚函数面太大
- Python override 的回调开销和异常边界复杂
- 这更像“高级插件接口”，不是普通用户入口
- 一旦开放，就会形成较强兼容承诺

因此建议：

- 第一阶段不开放 Python 侧 builder subclassing
- 第二阶段若确有需求，再单独评估受控 callback 方案

## 七、与 UDBM / UCDD 的衔接方案

### 1. 总体思路

`UTAP` 与 `UDBM/UCDD` 的关系不应是“任意模型直接自动翻译”，而应是：

- `UTAP` 提供前端文档、模板、查询和表达式语义入口
- `pyudbm` Python 层负责挑选其中可落到符号语义核心的子集
- `UDBM/UCDD` 只处理自己真正能忠实承接的那部分语义

### 2. 第一阶段建议做的桥接

建议第一阶段只提供“信息提取级”桥接：

- 从文档中提取 clock 名
- 从模板中提取局部 clock
- 从查询中提取规范化文本
- 从 guard / invariant 中提取表达式文本

这已经足够支撑下面几类工作：

- Python 侧模型 introspection
- 后续 subset compiler 的输入
- query tooling
- 文档和教程示例

### 3. 第二阶段建议做的桥接

第二阶段再实现“表达式子集编译”：

- `x <= c`
- `x < c`
- `x - y <= c`
- `x - y < c`
- conjunction

这些表达式可以编译为：

- `Constraint`
- `Federation`
- `CDD`

这一步必须显式限定语义子集，不要伪装成“通用模型语义翻译器”。

### 4. 为什么不能直接自动生成一个全局 `Context`

UPPAAL 模型里的时钟来源不止一种：

- global clock
- template-local clock
- instance 相关命名环境
- 参数化展开后的名字

如果第一阶段直接做：

- `document.to_context()`

并偷偷把一切拍平成一个全局上下文，风险很高：

- 容易搞错名字作用域
- 容易搞错 template-local 与 instance-local 的关系
- 容易让后续用户误以为这就是完整系统语义

因此更好的方案是让提取策略显式化，例如：

- `document.clock_names(scope="global")`
- `template.clock_names(include_global=True)`
- `document.make_context(scope=..., naming=...)`

### 5. 推荐的长期方向

长期真正合理的路线不是“让 UTAP 替代 Python DSL”，而是：

- Python-first DSL 是主 authoring 体验
- `UTAP` 提供 XML/XTA import-export 兼容面
- 一部分模型 / 查询子集可以落到 `UDBM/UCDD`
- 更完整的 workflow 再逐步长出来

## 八、构建与打包方案

### 1. 根构建系统需要的变化

根 `CMakeLists.txt` 需要新增：

- `find_package(UTAP CONFIG REQUIRED)`
- 一个新的 pybind11 模块 `_utap`
- `_utap` 链接 `UTAP`

`setup.py` 需要同步新增：

- `CMakeExtension('pyudbm.binding._utap')`

### 2. wheel 打包层面的关键点

`_utap` 模块引入后，需要重点检查：

- `libUTAP` 是否会作为动态库参与装载
- `libxml2` 是否会进入 wheel 的 runtime 依赖
- Linux 下 `auditwheel repair` 是否能正确处理
- macOS 下 `delocate` 路径是否正确
- Windows 下是否需要额外复制 DLL

当前 `setup.py` 只显式复制 MinGW runtime DLL，不处理 `UTAP` 自身或其他第三方 DLL。

因此这块不能靠“它大概能跑”。

建议把 wheel 相关检查列为实现阶段的显式验收项，而不是收尾时再补。

### 3. 平台差异判断

Windows 上 `UTAP` 默认更偏静态构建，这可能减轻一部分 runtime DLL 问题；但 Linux / macOS 仍要认真检查动态链接路径。

建议实施时明确验证：

- `ldd` / `otool -L` / `dumpbin` 或等效方式
- wheel 修复前后依赖变化
- 干净环境下 `import pyudbm.binding._utap` 是否成功

## 九、测试方案

### 1. 单元测试优先级

建议新增以下几类 Python 测试：

#### A. 解析入口测试

- `load_xml`
- `loads_xml`
- `load_xta`
- `loads_xta`

覆盖：

- 正常模型
- 空 query / 多 query
- 错误输入的异常路径

#### B. 文档只读访问测试

覆盖：

- template 数量
- process 数量
- query 数量
- location / edge 基本信息
- feature flags

#### C. 查询解析测试

覆盖：

- 普通 `A[]` / `E<>`
- `leads_to`
- SMC 类 query
- 部分 TIGA / bounds 类 query

#### D. pretty print / roundtrip 测试

如果第一阶段引入 pretty print 或 XML 写出，则应补：

- parse -> pretty / write -> reparse
- 关键字段保持可识别一致

#### E. 语义桥接前置测试

即便第一阶段还不落地 subset compiler，也应提前写一些针对 guard / invariant 文本提取的测试，为第二阶段做准备。

### 2. 测试数据来源

优先复用：

- `UTAP/test/models/*.xml`

这些模型已经是上游自己在用的样例，最适合作为第一批 Python binding 侧 fixture。

### 3. native smoke test

除 Python 层单测外，建议实现时增加最小 smoke coverage：

- `_utap` 模块能 import
- 能 parse 一个最小 XML
- 能 parse 一个最小 query

这样能更快识别 wheel/runtime 问题。

## 十、文档与用户沟通策略

### 1. 第一期文档重点

第一阶段文档不应把 `UTAP` 描述成“完整模型检查器接口”，而应明确它是：

- 模型导入 / 检查 / 查询解析前端
- 与 `UDBM/UCDD` 互补的前端层

### 2. 用户示例建议

第一阶段最合适的示例不是复杂验证，而是：

- 读取现有 UPPAAL XML
- 列出 templates / locations / queries
- 解析一个 query
- 读取 clock 名并构造 `Context` / `CDDContext`

### 3. 需要明确写在文档里的限制

至少要明确写出：

- 当前不保证完整 AST 编辑能力
- 当前不保证任意表达式都能编译到 `Federation/CDD`
- 当前 query parse 不等于 query 执行

## 十一、实施阶段划分

### Phase 0：设计与脚手架确认

目标：

- 明确模块命名
- 明确对象边界
- 明确第一阶段 public surface

产出：

- 本文档

### Phase 1：native 接入

目标：

- 根 CMake 接入 `UTAP`
- `setup.py` 增加 `_utap`
- 最小 smoke 测试跑通

完成标准：

- 本地 `make bin`
- `make build`
- `import pyudbm.binding._utap`

### Phase 2：只读文档与 query 包装

目标：

- 增加 `pyudbm.binding.utap`
- 暴露 `load_xml` / `loads_xml` / `parse_query`
- 暴露只读 `ModelDocument` / `ModelQuery`

完成标准：

- 能读取上游样例模型
- 能列出模板与查询
- 能解析至少一批典型 query

### Phase 3：pretty / roundtrip / introspection 完善

目标：

- 增加 pretty print
- 增加更多 feature flags
- 增加 clock / declaration introspection

完成标准：

- 能做一轮 parse + pretty / write + reparse 验证

### Phase 4：与 `UDBM/UCDD` 的子集桥接

目标：

- 提供 subset compiler
- 对支持子集生成 `Federation` / `CDD`

完成标准：

- 对纯 zone-friendly guard / invariant 子集给出稳定结果
- 对不支持语义给出清晰异常

### Phase 5：更高层模型工作流

目标：

- 视需要发展更高层 Python 模型对象或 DSL
- 再评估根包 re-export 或 `pyudbm.model` 方案

## 十二、风险清单

### 1. API 做得过宽

如果第一阶段就完整暴露整个对象图，后续会很难收敛 public API。

### 2. 误判语义覆盖范围

如果过早承诺“UTAP 模型可直接变成 `Federation/CDD`”，很容易制造错误语义预期。

### 3. wheel runtime 问题被低估

`_utap` 一旦接入，runtime dynamic library 处理就不能再只靠现有 `_udbm/_ucdd` 的经验推断。

### 4. query 层做得太深

query AST 是一个容易膨胀的方向。第一阶段应该先满足 parse / classify / pretty，而不是完整查询中间表示。

## 十三、建议的近期执行顺序

如果后续要真正开工，建议按下面顺序推进：

1. 接入 `_utap` 原生模块，先把构建和 import 跑通。
2. 只做最小 parse + 只读 document/query 包装。
3. 用 `UTAP/test/models` 补齐 Python 测试。
4. 完成 pretty / feature summary / clock 提取。
5. 再开始 subset compiler 和 `UDBM/UCDD` 桥接。

## 十四、结论

`UTAP` 非常适合接入当前仓库，但它最合理的位置不是“又一个孤立 native binding”，而是：

- `pyudbm` 的模型与查询前端层
- 与 `UDBM/UCDD` 并列但职责不同的原生能力模块
- 后续 Python-first UPPAAL workflow 的互操作基础设施

因此，推荐路线是：

- 先做 `_utap + pyudbm.binding.utap`
- 先做只读导入、query parse、pretty print、模型 introspection
- 再做 subset compiler 与符号语义桥接
- 暂不在第一阶段承诺完整可编辑 AST 与完整验证语义

这条路线既符合当前仓库已经形成的分层结构，也能最大程度降低对象模型、打包和 public API 一开始就失控的风险。
