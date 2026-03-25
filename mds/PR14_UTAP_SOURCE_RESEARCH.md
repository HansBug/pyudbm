# UTAP 源码调研笔记

## 说明

本文记录对 `UPPAALModelChecker/utap` 官方仓库的一轮源码级调研结果，目标不是复述 README，而是回答下列更偏工程实现的问题：

- `utap` 现在到底在官方生态中扮演什么角色
- 它实际支持哪些语法面
- 语法是如何定义、解析、分发到内部对象图的
- 最终解析产物是什么样
- “模型解析结果”和“查询解析结果”是否是同一套内部表示
- 它是否适合作为 `pyudbm` 未来的模型导入前端
- 如果要导出到 Python 层或其他 C/C++ binding，合理边界应该在哪里

本文是仓库内的内部研究笔记，不代表最终设计结论。

## PR 信息

- Pull Request: <https://github.com/HansBug/pyudbm/pull/14>
- 当前文件路径：`mds/PR14_UTAP_SOURCE_RESEARCH.md`

## 后续计划说明

基于本轮调研，后续我计划继续评估如何将 `UTAP` 以内置依赖、紧耦合前端组件或其他适合本仓库构建/发布模型的方式纳入 `pyudbm`，以便更直接地支持官方 UPPAAL 模型导入，同时仍然把最终工作流落到 `pyudbm` 的 Python-first 建模与符号分析接口上。

## 调研对象与快照

- 上游仓库：<https://github.com/UPPAALModelChecker/utap>
- 调研本地快照：`main@5b152dbdfd9e4921594f95a0f0d1bb41be43709a`
- 快照提交日期：`2025-10-24`
- 提交标题：`Added fortification for macOS GH CI (#86)`

需要特别说明的一点：

- 上游 README 的架构图和术语里仍然写着 `TAS` / `SystemBuilder`
- 但当前公开源码中的默认模型承载对象已经是 `UTAP::Document`
- 默认构建器类是 `DocumentBuilder`

因此在理解 `utap` 时，不能只依赖 README 里的旧名词，必须以当前头文件和实现文件为准。

## 一、总体判断

`utap` 不是“一个读取 UPPAAL XML 的轻量工具”。

更准确地说，它是一个完整的 UPPAAL 语言前端(frontend)，至少包含：

- 基于 `flex + bison` 的词法与语法分析器
- 基于 `libxml2` 的 XML 读取器
- 一套统一的 `ParserBuilder` 事件接口
- 默认的模型对象构造器 `DocumentBuilder`
- 表达式和类型对象图
- 类型检查 `TypeChecker`
- 特性检查 `FeatureChecker`
- 查询属性(property)的单独解析/类型检查路径
- XML 写回能力
- pretty printer

也就是说，它不是“只 parse 不 check”，也不是“只收 XML 不收文本语法”，而是一整套官方语言前端基础设施。

## 二、输入格式与总体信息流

上游 README 明确说明 `libutap` 可以解析 UPPAAL 支持的三种文件格式，并且会对模型做类型检查。

对应当前源码，可以概括出这样的输入面：

- `.xml`
- `.xta`
- `.ta`
- property / query 字符串
- 表达式子片段

当前 API 入口大致分为两层。

### 1. 面向默认 `Document` 产物的便捷入口

公开头文件 `include/utap/utap.hpp` 暴露了这些入口：

- `parse_XTA(FILE*, UTAP::Document&, bool)`
- `parse_XTA(const char*, UTAP::Document&, bool)`
- `parse_XML_buffer(const char*, UTAP::Document&, bool, libpaths)`
- `parse_XML_file(path, UTAP::Document&, bool, libpaths)`
- `parse_XML_fd(fd, UTAP::Document&, bool, libpaths)`
- `parse_expression(const char*, UTAP::Document&, bool)`
- `write_XML_file(const char*, UTAP::Document&)`

其中最重要的事实是：

- `parse_XTA(..., Document&, ...)`
- `parse_XML_* (..., Document&, ...)`

最终都会走 `DocumentBuilder`，并在 parse 之后运行 `static_analysis(doc)`。

而 `static_analysis(doc)` 又会做：

- `TypeChecker`
- `FeatureChecker`

所以默认 `Document` 路径并不是“原始未检查语法树”，而是“已完成语法构建，并跑过类型检查/特性检查的模型对象”。

### 2. 面向自定义后端的 Builder 入口

`include/utap/builder.hpp` 同时暴露了另一组 API：

- `parse_XTA(..., UTAP::ParserBuilder&, ...)`
- `parse_XML_* (..., UTAP::ParserBuilder&, ...)`
- `parse_property(..., UTAP::ParserBuilder&, ...)`

这意味着：

- `utap` 的 parser 本身并不强绑定 `Document`
- 它可以把语法事件送入任意 `ParserBuilder` 实现
- `DocumentBuilder` 只是官方默认后端之一

这对后续绑定设计非常重要，因为它说明 `utap` 并不是“只能先落一个固定 AST 再说”，理论上可以直接接自定义 IR builder。

## 二补充、构建依赖边界与工具链注入确认

这部分是对“如果未来要把 `UTAP` 接进 `pyudbm`，它到底会给现有构建链带来什么新依赖”的专项确认。

### 1. `UTAP` 不依赖 `UUtils` / `UDBM` / `UCDD`

这件事已经直接从 `UTAP` 当前仓库的 CMake 构建入口确认过。

顶层 `CMakeLists.txt` 中可见的构建前置只有：

- `find_package(FLEX 2.6.4 REQUIRED)`
- `find_package(BISON 3.6.0 REQUIRED)`
- `include(cmake/libxml2.cmake)`

而 `src/CMakeLists.txt` 里：

- 直接构建 `UTAP` 这个库
- 链接的是 `LibXml2::LibXml2`
- 没有 `find_package(UUtils)`
- 没有 `find_package(UDBM)`
- 没有 `find_package(UCDD)`

因此当前可以明确判断：

- `UTAP` 是官方语言前端层
- 它不吃当前仓库已有的 `UUtils/UDBM/UCDD` 依赖链
- 如果把它内置进来，新增的是 parser / XML toolchain 依赖，而不是 zone / CDD 内核依赖

### 2. 真正新增的构建依赖是什么

当前源码可确认的直接构建依赖是：

- `flex`
- `bison`
- `libxml2`

测试相关还会拉上：

- `doctest`

其中：

- `libxml2` 在上游仓库里已经有 `FetchContent` fallback
- `flex` / `bison` 是构建时工具，而不是普通链接库

这意味着如果未来要把 `UTAP` 接进本仓库，真正需要提前设计的是：

- 开发环境如何稳定拿到 parser generator
- CI 与 wheel 流水线如何解决 `flex/bison`

### 3. `FLEX_EXECUTABLE` / `BISON_EXECUTABLE` 是否真的可以注入

这件事这次已经做了源码确认和最小实证，不再停留在推测层。

#### A. `UTAP` 自己的 CMake 确实直接使用这两个变量

在 `src/CMakeLists.txt` 中，生成 lexer/parser 的命令直接写成：

- `COMMAND ${FLEX_EXECUTABLE} ...`
- `COMMAND ${BISON_EXECUTABLE} ...`

也就是说：

- 对 `UTAP` 自身而言，只要这两个变量在配置阶段有值
- 后续生成步骤就会直接使用它们

它没有在仓库内部再包一层自己专用的变量名，也没有把这两个值重新改写掉。

#### B. 当前 CMake 官方模块确实把这两个变量作为查找结果变量

本地确认时使用的 CMake 版本是：

- `3.31.10`

对应的官方模块文件中可以直接看到：

- `FindFLEX.cmake` 里有  
  `find_program(FLEX_EXECUTABLE NAMES flex win-flex win_flex ...)`
- `FindBISON.cmake` 里有  
  `find_program(BISON_EXECUTABLE NAMES bison win-bison win_bison ...)`

这说明两件事：

1. 如果工具在 `PATH` 上，`find_package(FLEX)` / `find_package(BISON)` 会自动找到它们。
2. 如果配置时显式传入：
   - `-DFLEX_EXECUTABLE=...`
   - `-DBISON_EXECUTABLE=...`

   那么模块会采用这些值，而不是必须重新自行探测。

#### C. 已做最小配置实验验证显式注入有效

这次本地做了一个最小 CMake 工程，内容只有：

- `find_package(FLEX 2.6.4 REQUIRED)`
- `find_package(BISON 3.6.0 REQUIRED)`
- 打印 `FLEX_EXECUTABLE`
- 打印 `BISON_EXECUTABLE`

实验结果分两步：

1. 默认配置时，输出的是系统上的 `flex` / `bison` 路径。
2. 显式传入自定义脚本路径：
   - `-DFLEX_EXECUTABLE=<tmp>/bin/flex`
   - `-DBISON_EXECUTABLE=<tmp>/bin/bison`

   配置输出中对应变量就变成了注入路径。

这说明：

- 对当前 `UTAP + CMake 3.31` 组合来说
- 通过 `FLEX_EXECUTABLE` / `BISON_EXECUTABLE` 注入具体程序路径是可行且生效的

#### D. 这对 Windows 尤其重要

因为 `FindFLEX` / `FindBISON` 当前明确支持的可执行名里就包含：

- `win-flex` / `win_flex`
- `win-bison` / `win_bison`

因此未来如果在 Windows CI 中采用例如 `winflexbison3` 这一类工具包，理论上有两种路径：

1. 让 `win_flex` / `win_bison` 出现在 `PATH`
2. 更稳地在 CMake 配置时显式传：
   - `-DFLEX_EXECUTABLE=...`
   - `-DBISON_EXECUTABLE=...`

从可控性和可维护性看，后者更适合本仓库现有 CI 与 wheel 脚本。

### 4. 对 `pyudbm` 集成的直接含义

目前能较明确地收敛成这几个判断：

1. 把 `UTAP` 接进来，不会把仓库重新耦回 `UUtils/UDBM/UCDD` 上游依赖树。
2. 新问题主要集中在 parser toolchain，而不是 symbolic core。
3. `libxml2` 相对容易通过 `FetchContent` 或系统包解决。
4. `flex/bison` 才是发布链路上更需要专门设计的部分。
5. 至少从 CMake 接口层面，`FLEX_EXECUTABLE/BISON_EXECUTABLE` 已经足够构成一个稳定注入点。

## 三、XML 与文本语法并不是两套独立前端

这是本轮调研里最值得记录的一个结论。

从 `src/xmlreader.cpp` 可以看到，XML reader 不是自己重新解释所有语义字段，而是：

1. 用 `libxml2` 遍历 XML 结构
2. 在遇到 `<declaration>`、`<system>`、`<label>`、`<formula>` 等文本块时
3. 把该文本块重新送进 `parse_XTA(..., part, xpath)` 或 property parser

也就是说：

- XML 负责结构壳子
- 真正的语言片段仍由同一套 `bison/flex` grammar 解析

这样做的工程意义是：

- `.xml`
- `.xta`
- `.ta`

在语义前端层最终汇合到同一套 grammar/builder 协议，而不是维护三套彼此漂移的解释器。

对 `pyudbm` 来说，这一点很有价值，因为这说明如果未来复用 `utap`：

- 可以一次获得官方 XML/XTA 兼容前端
- 不需要自己分别做 XML label 解析和 XTA 文本语法解析

## 四、语法面比“经典 timed automata”大得多

从 `src/parser.y` 的 token 定义和 `ParserBuilder` 接口面看，`utap` 当前覆盖的语法面已经明显超出最小 timed automata 核心。

### 1. 声明与类型系统

至少包括：

- `bool`
- `int`
- `double`
- `string`
- `clock`
- `chan`
- `scalar`
- `struct`
- `typedef`
- range-bounded int
- array
- function
- external function

也就是说，`utap` 的类型前端本身就已经是一个较完整的“小语言”。

### 2. 模型结构

至少包括：

- template / process
- location
- branchpoint
- transition / edge
- `select`
- `guard`
- `sync`
- `assign`
- `probability`
- `urgent`
- `committed`
- `init`
- system instantiation / process list
- channel priority
- before/after update

### 3. 查询与性质语言

至少包括：

- `A[]`
- `A<>`
- `E[]`
- `E<>`
- `-->`
- deadlock
- supremum / infimum / bounds 查询

### 4. 扩展分析语法

还包括：

- SMC 概率与期望查询
- simulation queries
- TIGA / control synthesis 相关语法
- MITL
- strategy load/save / subject / imitate

### 5. 更扩展的建模面

当前源码里还能看到：

- dynamic templates
- `spawn`
- `exit`
- `numof`
- LSC
- Gantt
- IO declarations

因此如果未来把 `utap` 作为 `pyudbm` 的语法前端候选，必须清醒地意识到：

- 它不是只服务“基础 TA + zone”那一点点语法
- 它已经天然带有一大块 UPPAAL 扩展语法包袱

这既是优势，也是 API 设计上的风险来源。

## 五、核心中间表示是什么

### 1. 模型对象主树：`UTAP::Document`

当前默认模型承载对象是 `UTAP::Document`。

其主要内容包括：

- 全局声明 `Declarations global`
- 模板列表 `templates`
- 动态模板 `dyn_templates`
- instance 列表
- process 列表
- channel priorities
- before/after update
- 模型级 options
- query 元数据列表
- errors / warnings
- source positions
- strings intern table
- `SupportedMethods`

可以把它理解成“官方模型前端产出的语义化文档对象”。

### 2. 模板、位置、边

`Template` 结构大体包含：

- 参数 frame
- 声明块 `Declarations`
- `init`
- `locations`
- `branchpoints`
- `edges`
- dynamic evals
- 是否动态模板
- LSC 相关结构

`Location` 至少包含：

- `uid`
- `name`
- `invariant`
- `exp_rate`
- `cost_rate`
- 编号

`Edge` 至少包含：

- source / target location 或 branchpoint
- `select` frame
- `guard`
- `assign`
- `sync`
- `prob`
- controllable 标记

### 3. 声明、符号、作用域

`utap` 的符号系统不是简单字符串表，而是：

- `Symbol`
- `Frame`
- `Type`

的组合。

其中：

- `Symbol` 是名字、类型和用户数据的句柄
- `Frame` 表示有父子关系的作用域/符号集合
- `Type` 是树状类型对象

这个设计明显是为“语法前端 + 语义检查”服务的，不是为轻量序列化格式服务的。

### 4. 表达式对象：`UTAP::Expression`

`Expression` 不是字符串，而是共享式树状对象，带有：

- `kind`
- `position`
- `type`
- `subexpressions`
- 某些节点的额外值，如 constant/sync/index/symbol

提供的方法包括：

- `get_kind`
- `get_size`
- `get_type`
- `get_value` / `get_double_value`
- `get_symbol`
- `get_symbols`
- `uses_clock` / `uses_fp` / `uses_hybrid`
- `contains_deadlock`
- `changes_variable`
- `depends_on`
- `subst`
- `clone` / `clone_deeper`
- `str()`

也就是说，它已经接近一套可分析、可变换、可打印的通用表达式 IR。

### 5. 类型对象：`UTAP::Type`

`Type` 同样是树状对象。

它不仅能表示基础类型，还能表示：

- array
- record
- function
- instance
- process
- process set
- typedef label
- range
- ref

并且还能附带：

- record labels
- range bound expressions

这说明 `utap` 的类型系统本身是解析产物的重要组成部分，而不是 parse 后临时算一下的附属信息。

## 六、模型解析结果与查询解析结果不是同一条产物链

这是理解 `utap` 很容易混淆的一点。

### 1. `Document` 里的 `queries` 先只是元数据

XML 中 `<queries>` 部分通过 `DocumentBuilder` 进入 `Document::queries`。

但 `Query` 结构里主要保存的是：

- `formula` 字符串
- `comment`
- `options`
- `expectation`
- `location`

这不是“已编译好的 query expression tree”，只是 query 文本与附属元数据。

### 2. 真正的性质表达式 AST 走 `PropertyBuilder`

如果需要把 query 变成真正的内部表达式对象，需要走：

- `parse_property(...)`
- `PropertyBuilder`
- `TigaPropertyBuilder`

这一条链。

它的核心产物是 `PropInfo`，其中包含：

- `quant_t type`
- `Expression intermediate`
- `options`
- strategy 相关信息
- expected result

也就是说：

- 模型文档中的 query 文本存储
- query/property 的真正 AST 编译

在 `utap` 里是分层的，不是一次 `parse_XML_file` 就全部完成。

对未来 Python API 设计，这个事实非常关键：

- 不能把 `Document.get_queries()` 理解成“查询 AST 列表”
- 模型导入接口和 query 编译接口应该分开建模

## 七、默认路径并非“纯 parse”，还会做语义检查

`parse_XTA(..., Document&, ...)` 和 `parse_XML_* (..., Document&, ...)` 在底层都会执行：

1. `DocumentBuilder`
2. `TypeChecker`
3. `FeatureChecker`

其中：

- `TypeChecker` 负责类型正确性和一部分语义约束
- `FeatureChecker` 会总结模型支持哪些分析方式，例如 symbolic/stochastic/concrete

因此 `Document` 的默认生成流程更接近：

```text
parse -> build document -> typecheck -> feature classify
```

而不是：

```text
parse -> dump raw tree
```

这件事对 binding 设计有两面性。

好处：

- Python 层拿到的是更“干净”的已分析对象

代价：

- 如果用户想要“只 parse，不 check”的中间态，默认 API 并不直接提供
- 如果用户想自己决定错误恢复、类型检查时机、部分语法降级策略，需要改走更底层 builder 接口

## 八、`ParserBuilder` 的可插拔性很强，但并不适合直接跨语言暴露

从 `include/utap/builder.hpp` 可以看到，`ParserBuilder` 几乎覆盖整个语言表面：

- type methods
- declaration methods
- process / edge methods
- statement methods
- expression methods
- property methods
- query metadata methods
- dynamic template methods
- priority/guiding methods

这意味着什么？

### 1. 对 C++ 内部扩展来说，这是很强的能力

如果是纯 C++ 场景，可以：

- 自己实现一个 builder
- 直接把 parse 结果翻译到自定义 IR
- 不必先构造 `Document`

这是 `utap` 很强的一面。

### 2. 但对 Python / C ABI / 其他 binding 来说，这个接口太细、太宽

问题主要在于：

- 纯虚方法非常多
- 回调粒度很细
- 语义状态机复杂
- 表达式是逆波兰式 builder 协议，而不是简单节点回调
- 错误处理依赖异常和内部位置状态

因此：

- “把 `ParserBuilder` 原样绑定到 Python，让 Python 子类接回调”

在技术上不是不可能，但工程上非常不划算。

这条路的问题会包括：

- 跨语言回调成本高
- 错误传播复杂
- API 非常不 Pythonic
- 维护成本远高于收益

## 九、导出到 Python 层的现实可行性

我的判断是：可以接，但不应该按“原始 C++ 对象全量直出”的方式接。

### 1. 最容易做的层次

最容易落地的是：

- 绑定 `parse_XML_file / parse_XML_buffer / parse_expression`
- 暴露一个受控的只读/半只读模型对象视图
- 或者把 `Document` lower 到你们自己的 Python IR 后再暴露

这两条都比“把所有 builder/type/property internals 全部端到 Python”要稳得多。

### 2. 直接暴露 `Document` 的问题

`Document` 不是不能绑，但会遇到这些现实问题：

- `std::list` / `std::deque` / `std::map` 边界
- `Symbol` / `Frame` / `Expression` / `Type` 之间互相引用
- `void* user data`
- `pimpl + shared_ptr` 风格对象
- 部分字段语义依赖 typecheck 后才稳定
- query 需要走单独 property path

这意味着：

- 直接 pybind 出来并不等于拿到了“好用的 Python API”

你很容易得到一个“能看见很多 C++ 结构，但用户并不舒服”的绑定层。

### 3. 更合理的 Python 边界

我更倾向于下面这类边界：

#### A. 把 `utap` 当导入前端

输入：

- `.xml`
- `.xta`
- query 字符串

输出：

- `pyudbm` 自己定义的 Python 友好 IR

例如：

- `Model`
- `Template`
- `Location`
- `Edge`
- `Declaration`
- `Query`
- `Expr`

### B. 把官方 C++ 对象限制在内部层

内部可以继续持有：

- `UTAP::Document`
- `UTAP::Expression`
- `UTAP::Type`

但 public API 不直接承诺这些对象的稳定形态。

### C. query 编译和模型导入分开

因为上游本来就是两条产物链，所以 Python API 也建议分开：

- `load_model(...)`
- `compile_query(model, text)`

而不是幻想“一次 parse XML 得到完整 property AST 全家桶”。

## 十、导出到其他 C/C++ binding 的可行性

### 1. 对 C++ binding 使用者

如果对方本来就是 C++ 项目，那么 `utap` 已经相对友好：

- 有公开头文件
- 有安装导出
- 有 `UTAP::UTAP` CMake target
- 可以直接复用 parser 和 `Document`

从复用角度看，这很成熟。

### 2. 对需要稳定 ABI 的其他语言

如果目标是：

- C ABI
- Rust FFI
- Java/JNI
- C#
- Python wheel

那就不应把原始 C++ API 直接当外部 ABI。

更稳妥的方案是：

1. 在 C++ 内部调用 `utap`
2. 转换成自定义稳定 IR
3. 通过更薄、更可控的 API 对外暴露

这个稳定 IR 可以是：

- C 结构体树
- protobuf/json 风格中间对象
- repository-internal C++ POD-ish model

总之，不应让外部语言直接依赖 `utap` 那一整套内部 C++ 面。

## 十一、结合 `pyudbm` 的适配判断

结合当前仓库路线，我认为 `utap` 很适合被定位成：

- “官方模型兼容导入前端”
- 而不是“未来 Python-first 作者接口本体”

这两者要严格区分。

### 1. 适合做什么

它很适合负责：

- 导入官方 XML/XTA
- 保持与官方语法兼容
- 避免自己重写 parser
- 为后续 Python IR 建模提供稳定来源

### 2. 不适合做什么

它不适合直接成为：

- `pyudbm` 长期 public Python API 的核心对象模型
- Python-first DSL 的直接宿主
- 未来所有用户交互的唯一模型表示

原因很简单：

- `utap` 的对象模型是为 C++ parser/typechecker 服务的
- `pyudbm` 的长期方向则是 Python-first workflow / DSL / symbolic interface

这两者可以衔接，但不应该被混为一谈。

### 3. 对本仓库最现实的方向

更合理的路线是：

1. Python-first authoring 继续建设自己的 DSL / object model
2. 兼容导入官方模型时，引入 `utap`
3. 导入后尽快 lower 到 `pyudbm` 自己的 IR
4. 再往下对接：
   - `UDBM`
   - `UCDD`
   - 将来的 timed-symbolic workflow

换句话说：

- `utap` 是前端导入桥，而不是最终用户世界观本身

## 十二、源码层值得继续深挖的点

如果下一轮还要继续深入，我认为最值得展开的是这些主题。

### 1. `Expression` 到 timed-symbolic semantics 的可降阶方式

重点问题：

- clock guard / invariant / update / sync 在 `Expression` 里分别长什么样
- 哪些表达式能机械地 lower 到 `pyudbm` 自己的 IR
- 哪些语法需要保留为 opaque 节点

### 2. `TypeChecker` 对“合法 UPPAAL 模型”的实际约束边界

重点问题：

- 哪些约束只是 parse 阶段检查
- 哪些约束在 typecheck 阶段才补齐
- 是否存在对 Python 导入层有价值的“已归一化信息”

### 3. `FeatureChecker` 如何总结 symbolic/stochastic/concrete 支持

这可能直接影响未来 Python API 中：

- 模型能否走 symbolic verification
- 何时必须切换到 stochastic / concrete 工作流

### 4. query/property 的更细分 IR

当前已知：

- `Document::queries` 只是文本元数据
- `PropInfo` 才持有真正的中间表达式

下一轮可继续细看：

- `PropInfo::intermediate` 的节点形状
- 不同 query 类型在 `Expression::kind` 上如何区分
- 是否适合抽成 Python 侧查询 IR

### 5. 动态模板与扩展语法是否值得进入首批 Python 兼容面

这类特性包括：

- dynamic templates
- `spawn`
- LSC
- Gantt

它们会显著抬高绑定复杂度，未必应进入第一阶段。

## 十三、当前阶段的建议结论

如果以 `pyudbm` 的当前方向为前提，我建议把本轮结论压缩成以下几条工程判断：

1. `utap` 值得继续跟踪，且非常有潜力成为官方模型导入前端。
2. 不建议一开始就做“全量原始 `UTAP::Document` Python 绑定”。
3. 更适合先做 import-only 方案，把 `utap` 结果 lower 到仓库自有 IR。
4. 模型导入与 query/property 编译应设计成两条 API。
5. 不要把 `ParserBuilder` 原样暴露给 Python。
6. 若需要跨语言复用，应优先设计稳定适配层，而不是直接暴露 `utap` C++ ABI。
7. 若进入 CI / wheel 链路，应把 `flex/bison` 视为单独的发布工程问题处理，不要把它和 `UDBM/UCDD` 这类 native 库依赖混为一谈。

## 参考入口

### 官方仓库

- <https://github.com/UPPAALModelChecker/utap>

### 本轮重点查看的源码文件

- `README.md`
- `include/utap/utap.hpp`
- `include/utap/builder.hpp`
- `include/utap/document.hpp`
- `include/utap/expression.hpp`
- `include/utap/type.hpp`
- `include/utap/property.hpp`
- `src/parser.y`
- `src/lexer.l`
- `src/xmlreader.cpp`
- `src/DocumentBuilder.cpp`
- `src/TypeChecker.cpp`
- `src/CMakeLists.txt`

## 后续可落地的两个研究方向

如果要把这份调研继续往前推进，下一步最自然的是二选一：

### 方向 A：做 `utap -> pyudbm IR` 的降阶设计草案

产出形式可以是：

- Python dataclass 草图
- 映射表
- 不支持语法清单
- import API 轮廓

### 方向 B：做最小可行 binding 面分析

产出形式可以是：

- 第一阶段只绑定哪些类型
- 哪些类型只做内部适配不公开
- pybind11 层边界
- 构建与 wheel 风险清单

目前看，方向 A 比方向 B 更符合本仓库长期路线。
