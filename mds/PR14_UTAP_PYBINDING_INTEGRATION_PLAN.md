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

- Pull Request：<https://github.com/HansBug/pyudbm/pull/14>
- 当前文件路径：`mds/PR14_UTAP_PYBINDING_INTEGRATION_PLAN.md`

## 关联文档

与本文档直接相关的前置调研记录：

- `mds/PR14_UTAP_SOURCE_RESEARCH.md`

建议阅读顺序：

1. 先读 `PR14_UTAP_SOURCE_RESEARCH.md`，理解 `UTAP` 当前源码、构建边界和前端架构。
2. 再读本文档，理解 `pyudbm` 侧的集成边界、API 设计和实施阶段。

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

### 4. 官方样本集带来的新约束

基于当前仓库已经抓取、筛选并用真实 `UTAP` API 验证过的官方样本集，第一阶段方案需要新增一个更具体的工程约束：

- `test/testfile/official/catalog.json` 应作为第一阶段的重要验收基线之一
- 当前保留样本共 `178` 个，且都已经被真实 `UTAP` 解析验证为 `status=ok`
- 其中包括：
  - `102` 个 `XML_MODEL_FILE`
  - `29` 个 `TEXTUAL_MODEL_FILE`
  - `47` 个 `QUERY_PROPERTY_FILE`
- `47` 个 query 文件全部带有 `context_path`，说明 query 文件解析在工程上不能只提供“纯文本 parse”，还必须提供“带上下文模型的文件级 parse”

这带来几个直接约束：

- 第一阶段不能只做演示级 `load_xml`，必须把 `XML` / 文本模型 / query 文件这三条真实输入路径都做完整
- 测试不能只依赖几个手写 fixture，必须把当前官方样本集纳入 parameterized 测试
- API 设计上必须正视 query 对上下文模型的依赖，而不是把 `.q` 文件简化成“一段不带环境的字符串”

关于三种模型表示，还需要明确一个实现边界：

- `XML` 是一条独立的模型输入路径
- `XTA` / `TA` 属于同一类“文本模型输入路径”，都应通过 `parse_XTA` 家族进入
- 但这不等于可以在 API 层把 `XML` / `XTA` / `TA` 视为“完全无差别、无条件可互换的等价格式”

更准确地说：

- `TA` 在工程上应视为 `XTA` 家族中的文本输入子集
- `XML` 与 `XTA/TA` 在很多情况下表达的是同一模型语义，但不应在第一阶段承诺完全无损同构
- 因此 Python API 设计应以“明确输入路径和明确解析入口”为准，而不是假设扩展名背后全都等价

还有一个现实细节：

- 当前保留的官方样本集中没有可直接复用的 `.xta` 文件
- 这不意味着 `.xta` 支持可以不做
- 相反，第一阶段仍应提供 `load_xta` / `loads_xta`
- 只是测试上需要用额外的上游样例或手工 fixture 来补 `.xta` 专项覆盖

## 三、集成目标与边界

### 1. 范围内目标

本方案建议把第一阶段的 `UTAP` 集成目标限定为下面几类能力：

- 提供 `XML` / `XTA` 的 Python 侧导入接口
- 提供 `TA` 文本模型的 Python 侧导入接口
- 提供尽可能完整的文档对象只读访问能力
- 提供查询 / property 的 Python 侧解析接口，包括带上下文模型的 query 文件解析接口
- 提供 pretty print / 规范化文本输出能力
- 提供 `dump` / `dumps` 风格的语义级 XML 导出接口
- 提供模型的 feature summary / capability summary
- 提供面向后续语义桥接的稳定中间层
- 以当前 `test/testfile/official/catalog.json` 作为第一阶段必须支持的现实输入基线之一

这里需要明确一个补充目标：

- Python 侧应尽量能访问到 `UTAP` 自身已经拿到的全部关键语义信息
- 优先保证“语义层面完整没有关键缺失”
- 不以“字节级、排版级、布局级绝对无损”作为第一阶段目标

### 2. 明确不在第一阶段范围内的内容

第一阶段不应承诺下面这些事情：

- 完整可编辑 AST
- Python 继承 `ParserBuilder` / `StatementBuilder` 的 callback 风格扩展
- 任意 `UTAP` 表达式自动转 `Federation` / `CDD`
- 完整验证工作流
- witness / trace replay / simulator 风格接口
- 与 `verifyta` 的命令级绑定
- 字节级、排版级、布局级完全无损 round-trip

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

#### 原则五：读路径尽量完整，写路径以语义保真为准

第一阶段不应只暴露“方便演示的 summary”。

更合适的要求是：

- 只要 `UTAP` 原生已经有的关键信息，Python 侧应尽量能拿到
- 导出时允许重新规范化 XML
- 只要 reparse 后模型在语义上仍然是那个模型，就符合第一阶段目标

因此第一阶段追求的是：

- semantic completeness
- semantic round-trip

而不是：

- byte-perfect round-trip
- original layout preservation

#### 原则六：C++ 已可读取的字段，Python 原则上都要可读取

这里需要把“读路径完整”进一步具体化。

本方案在现阶段建议把下面这条要求写成强约束：

- 对于 `UTAP` 在当前仓库中不修改上游源码就已经能在 C++ 层读到的语义字段，Python binding 原则上都应提供可访问路径

这不要求：

- 第一阶段就开放可变编辑
- 第一阶段就保证每个字段都有最漂亮的高层 facade

但至少要求：

- 不允许大量可读字段 silent drop
- 不允许把对象整体压成“几个 summary + 一段字符串”
- 如果第一阶段确有字段暂不暴露，必须在实现 PR 中显式列出缺口清单，而不是默认忽略

对实现者来说，这意味着至少要针对下面这些头文件做字段覆盖审计：

- `utap/document.h`
- `utap/expression.h`
- `utap/property.h`
- `utap/type.h`
- `utap/symbols.h`
- `utap/statement.h`
- `utap/position.h`

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
- 提供尽可能完整但只读的原生访问器
- 负责 C++ 生命周期管理

该层不应直接成为最终 public API。

#### B. Python 包装层

新增一个 Python 包装模块：

- `pyudbm.binding.utap`

该层职责：

- 对 `_utap` 的 native handle 做 Pythonic 包装
- 定义面向用户的对象命名与行为
- 负责把 native object graph 包装成更稳定的只读视图
- 负责异常信息、可选参数、文本接口与文档字符串

这里要特别强调：

- Python 包装层不应把 `UTAP` 已有语义对象压缩成只剩 summary 的轻薄壳
- 对后续分析有价值的细节，第一阶段就应尽量保留访问路径
- 真正要克制的是“可变编辑能力”，不是“语义读取能力”

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
- `load_query(path, document, *, builder="auto") -> list[ParsedQuery]`
- `loads_query(text, document, *, builder="auto") -> list[ParsedQuery]`
- `parse_query(text, document, *, builder="auto") -> ParsedQuery`
- `builtin_declarations() -> str`

这里要特别说明 query 入口的要求：

- 不能只提供“给一段字符串 parse 一下”的 helper
- 必须把“query 文件 + 上下文模型”的文件级工作流作为正式 API 支持对象
- `builder="auto"` 模式应能覆盖普通 property 与 TIGA / controller synthesis 风格 property

在写出方向，建议第一阶段直接把 `dump` / `dumps` 作为正式接口规划进去：

- `document.dump(path) -> None`
- `document.dumps() -> str`

同时可以保留更直白的别名：

- `document.write_xml(path) -> None`
- `document.to_xml() -> str`

实现策略上：

- `dump(path)` 应直接对应 `UTAP` 的 `write_XML_file`
- `dumps()` 第一阶段允许通过受控临时文件桥接实现
- 如果后续增加内存写出包装，再把 `dumps()` 切换到更直接的 native 实现

也就是说，第一阶段不要求“原始文本无损”，但要求：

- Python 侧能稳定写出一个语义等价、可重新解析的 XML

### 2. 第一阶段推荐暴露的对象

建议 Python 层以“完整只读 facade + 小型 value object 辅助”为主，优先提供：

- `ModelDocument`
- `ModelTemplate`
- `ModelLocation`
- `ModelEdge`
- `ModelProcess`
- `ModelQuery`
- `ParsedQuery`
- `ModelFeatures`

### 2.1 全量只读字段暴露要求

仅仅有这些对象名还不够，第一阶段还需要明确字段覆盖要求。

建议把目标写成：

- 只要某个字段在当前 `UTAP` C++ 层已经是可读取的，Python 侧就应尽量提供对应的只读访问

这意味着第一阶段不应只覆盖：

- `name`
- `text`
- `kind`
- 几个列表长度

还应把下面这类字段纳入明确覆盖范围：

- declaration / parameter / option / feature / supported method
- position / warning / error / source-local metadata
- template / process / location / edge / branchpoint 的结构信息
- query 的 quantifier / intermediate expression / expectation / declaration / options
- expression / type / symbol 的可读语义信息

实现时建议把“字段覆盖检查表”作为实现 PR 的显式产出之一：

- 哪些 C++ 可读字段已经映射
- 哪些字段暂未映射
- 未映射的原因是什么
- 后续准备在哪个阶段补齐

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
- `dump(path)`
- `dumps()`
- `pretty()`
- `write_xml(path)`
- `load_query(path, *, builder="auto")`
- `loads_query(text, *, builder="auto")`

另外可以提供一些轻量辅助方法：

- `find_template(name)`
- `template_names()`
- `clock_names(scope=...)`
- `bool_like_names(scope=...)`

### 4. 表达式对象的建议边界

表达式是整个接口设计里最需要控制复杂度的一块，但这不意味着应当把它削成只剩字符串。

更合适的目标是：

- 第一阶段尽量让 Python 侧拿到 `UTAP::expression_t` 已有的关键只读语义信息
- 不急着开放可变 AST 编辑
- 允许先不覆盖极少数很冷门的内部细节，但不能把表达式整体降级成“仅文本”

因此第一阶段的表达式包装建议至少覆盖：

- `text`
- `kind`
- `position`
- `type`
- `size`
- `children`
- `is_empty`

如果某些节点种类还需要补更多专用 accessor，也应按“增加读取能力”的方向补，而不是退回只有 `text`。

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

对于复杂 query 子结构，第一阶段仍可接受部分位置先保留规范化文本，但总体方向应是：

- 尽量把 `UTAP` 原生已经拿到的 property 语义信息暴露出来
- 不要把 query 层过度压扁成只有一段字符串

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
- 其他对象以只读 wrapper 或受控 view 的形式暴露
- 对 `UTAP` 已有的重要语义字段尽量提供访问器，而不是只给摘要

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
- template / location / edge / query / expression 多数以轻量只读 wrapper 提供
- snapshot 只作为辅助，不应成为唯一读路径

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

### 0. 测试约束与断言纪律

本项目在 `UTAP` binding 上的测试，不应停留在“能跑通几个 demo”。

需要把下面几条约束明确写成实施要求：

- 每个实施阶段结束时，都必须补齐与该阶段范围直接对应的单元测试
- 不允许把大量功能留到最后统一补测
- 字段类、结构类、枚举类、计数类、路径类、位置类测试，应优先使用直接值对比
- 除非有足够明确的理由，否则不要用 `assert 'xxxx' in xxxx` 这类局部匹配代替精确断言
- 单元测试默认只允许使用 public API / public class / public method / public function
- 不允许在单元测试中导入、访问或依赖任何 protected / private 实现细节
- 唯一允许直接导入 `_utap` 的测试文件应是专门的 native 测试文件，例如 `test_utap_native.py`
- 除 `test_utap_native.py` 外，其他单元测试文件都不允许导入 `_utap`
- 即便在 `test_utap_native.py` 中，也只允许测试 `_utap` 公开暴露出来的接口，不允许依赖其内部 protected / private 细节

更具体地说，以下场景默认应直接对比：

- `name`
- `kind`
- `quantifier`
- `type`
- `position`
- `options`
- `expectation`
- `feature flag`
- `template/process/location/edge/query` 的数量
- `context_path`
- `dump` / `dumps` 后 reparse 得到的关键字段

只有在下面这类场景里，局部匹配或正则匹配才算合理：

- 上游错误消息跨平台存在稳定但不可控的细微差异
- pretty print 文本在空白或格式化细节上允许变化，但核心语义 token 必须存在
- 底层第三方库返回路径或系统错误前缀存在平台差异

即便在这些例外场景里，也应优先：

- 比较结构化字段
- 比较规范化后的文本
- 比较明确列出的关键 token 集

而不是直接退化成宽松的 substring 断言。

另外需要明确测试分层边界：

- `test_utap_native.py` 这类文件用于验证 `_utap` 公开 native surface 的最小正确性
- 其他更高层测试文件应只通过 `pyudbm.binding.utap` 或后续正式 public API 做验证
- 不允许为了“写测试方便”跨过 public facade 直接调用内部实现

### 1. 单元测试优先级

建议新增以下几类 Python 测试：

#### A0. 官方样本集参数化解析测试

这一类测试现在应被视为第一阶段的硬性要求，而不是可选增强。

建议直接把下面这套机制写进实施要求：

- 以 `test/testfile/official/catalog.json` 作为参数化测试清单
- 使用 `pytest.mark.parametrize` 按条目驱动测试
- 按 `parse_kind` 分派解析入口
- 对带 `context_path` 的 query 条目，先加载上下文模型，再解析 query 文件

也就是说，至少应形成下面三类 corpus-level 测试：

- `XML_MODEL_FILE` 全量参数化测试
- `TEXTUAL_MODEL_FILE` 全量参数化测试
- `QUERY_PROPERTY_FILE` 全量参数化测试

这类测试的最低要求不是“抽样跑几个”，而是：

- 当前保留官方样本集应整体通过
- 后续新增官方样本时，应天然纳入同一套参数化测试

需要补充说明：

- 当前保留官方样本集中没有 `.xta`
- 因此 `.xta` 仍需通过额外 fixture 补参数化覆盖
- 但这不影响 `catalog.json` 官方样本集本身作为第一阶段基线

#### A. 解析入口测试

- `load_xml`
- `loads_xml`
- `load_xta`
- `loads_xta`
- `load_query`
- `loads_query`

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
- expression / declaration / option 等关键语义字段可访问
- feature flags
- 同一类对象在不同官方样本中的字段访问稳定
- 对 C++ 可读字段的覆盖不止停留在 summary 级别

#### C. 查询解析测试

覆盖：

- 普通 `A[]` / `E<>`
- `leads_to`
- SMC 类 query
- 部分 TIGA / bounds 类 query
- 文件级 query 解析
- 带上下文模型的 query 文件解析
- `builder="auto"` 下普通 `PropertyBuilder` 与 `TigaPropertyBuilder` 路径都能命中

#### D. pretty print / roundtrip 测试

如果第一阶段引入 pretty print 或 XML 写出，则应补：

- parse -> pretty / write -> reparse
- 关键语义字段保持一致
- `dump(path)` 与 `dumps()` 都覆盖

这里的验收标准应明确写成：

- 不要求字节级一致
- 不要求图形布局一致
- 要求 reparse 后模型在语义层面没有关键缺失

#### E. 语义桥接前置测试

即便第一阶段还不落地 subset compiler，也应提前写一些针对 guard / invariant 文本提取的测试，为第二阶段做准备。

#### F. 字段覆盖参数化测试

这一类测试应直接服务于“C++ 可读字段原则上全量暴露”这条要求。

建议做法：

- 为每类 wrapper 维护代表性样本表
- 使用 `pytest.mark.parametrize` 驱动字段可访问性测试
- 对每个已承诺暴露的字段，至少有一个样本明确覆盖

如果实现 PR 中声明了“暂未暴露字段清单”，对应测试也应同步体现：

- 已暴露字段必须有测试
- 未暴露字段必须在文档中有明确缺口记录
- 后续补齐字段时，应先补测试再补实现

### 2. 测试数据来源

第一优先级应调整为：

- `test/testfile/official/catalog.json`

原因是：

- 这批样本已经经过真实 `UTAP` 验证
- 覆盖了 `XML` / 文本模型 / query 文件三条真实输入路径
- query 条目已经带有 `context_path`
- 更适合作为“binding 是否真能吃官方输入”的现实回归集

在此基础上，再补充：

- `UTAP/test/models/*.xml`
- 额外手工 `.xta` fixture
- 必要时补少量极小 synthetic fixture

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
- 语义级 round-trip 的模型读写层，而不是字节级无损 XML 保真层

### 2. 用户示例建议

第一阶段最合适的示例不是复杂验证，而是：

- 读取现有 UPPAAL XML
- 列出 templates / locations / queries
- 解析一个 query
- 读取 clock 名并构造 `Context` / `CDDContext`

### 3. 需要明确写在文档里的限制

至少要明确写出：

- 当前不保证完整 AST 编辑能力
- 当前优先保证读路径的语义完整，而不是原始 XML 的字节级保真
- 当前不保证任意表达式都能编译到 `Federation/CDD`
- 当前 query parse 不等于 query 执行

## 十一、实施阶段划分

下面的阶段划分不只是“按主题分块”，而是建议作为实际实施时的执行顺序。

每个阶段都包含三部分：

目标、checklist、阶段测试要求。

另外需要强调：

任何一个阶段结束时，都不应留下“核心功能已写但没有测试”的状态；每个阶段对应的测试至少要覆盖该阶段新引入的 public API、核心字段和失败路径。

### 0. 进度回填要求

这份 `mds/PR14_UTAP_PYBINDING_INTEGRATION_PLAN.md` 不只是前期方案文档，也必须作为实施过程中的持续回填文档使用。

需要明确要求：

* [ ] 每完成一个 phase，必须把对应进度落回到这份 md。
* [ ] 每次出现“计划与实际实现发生偏差”的情况，必须把偏差和原因落回到这份 md。
* [ ] 每次新增 public API、测试文件、fixture、catalog/字段清单时，必须把对应路径落回到这份 md。
* [ ] 每次完成阶段验收时，必须把实际跑过的验证命令和结果摘要落回到这份 md。
* [ ] 不允许只在聊天记录、commit message 或 PR review 里记录阶段进度，而不更新这份 md。
* [ ] 后续 phase 的 checklist 打勾状态，应以这份 md 为准，不允许代码与文档长期失配。

### 1. 当前进度回填

以下进度回填到 `2026-03-26` 为止。

#### 已完成：Phase 0

当前已经落地的内容：

* [x] `_utap` 与后续 `pyudbm.binding.utap` 的分层边界已明确，当前 Phase 1 只引入 `_utap` native surface。
* [x] `XML` / `XTA` / `TA` / `query file` 的输入分层已经在计划和测试辅助数据中明确。
* [x] 字段覆盖清单初稿已经落到 `test/binding/utap_phase0_data.py`。
* [x] 样本测试分层清单已经落到 `test/binding/utap_phase0_data.py`。
* [x] 官方样本集 `test/testfile/official/catalog.json` 已被纳入 Phase 0 的结构一致性校验入口。

已经新增的对应文件：

* [x] `test/binding/utap_phase0_data.py`
* [x] `test/binding/test_utap_phase0.py`
* [x] `test/testfile/utap/minimal_ok.xml`
* [x] `test/testfile/utap/minimal_ok.xta`

本阶段已经实际完成的验证：

* [x] 对 `official/catalog.json` 的 `path` 可达性做了直接断言。
* [x] 对 `official/catalog.json` 的 `status == "ok"` 做了直接断言。
* [x] 对所有 query 条目的 `context_path` 有效性做了直接断言。
* [x] 对字段覆盖清单和样本分层清单建立了可 parameterize 的测试辅助数据。

#### 已完成：Phase 1

当前已经落地的内容：

* [x] 根 `CMakeLists.txt` 已增加 `find_package(UTAP CONFIG REQUIRED)`。
* [x] `_utap` pybind11 模块已经新增，文件为 `pyudbm/binding/_utap.cpp`。
* [x] `setup.py` / `CMakeExtension` 已纳入 `_utap`。
* [x] `_utap` 已暴露最小 native 入口：`load_xml`、`loads_xml`、`load_xta`、`loads_xta`、`builtin_declarations`。
* [x] `_utap` 已引入 `_NativeDocument` 作为最小 native 返回对象。
* [x] native 异常边界已明确：缺文件映射到 `FileNotFoundError`，解析失败映射到 `_utap.ParseError`。
* [x] 本地 runtime 依赖路径已打通，`_utap` 构建后会补齐 `libUTAP` / `libxml2` 的运行时复制。

已经新增的对应文件：

* [x] `pyudbm/binding/_utap.cpp`
* [x] `test/binding/test_utap_native.py`

本阶段已经实际完成的验证：

* [x] `_utap` 可被 import。
* [x] 最小 XML fixture 可 parse。
* [x] 最小文本模型 fixture 可 parse。
* [x] 失败输入会抛出预期异常。
* [x] 对返回对象类型做了精确断言。
* [x] 对异常类型做了精确断言。
* [x] 对异常消息做了精确断言。
* [x] `_utap` native 测试被放在专门文件 `test_utap_native.py` 中。
* [x] 其他测试文件未导入 `_utap`。

已实际跑过的验证命令与结果摘要：

* [x] `make build`
* [x] `python -m pytest test/binding/test_utap_phase0.py test/binding/test_utap_native.py -m unittest -q`
* [x] `make clean_x`
* [x] `python -m pytest test/binding/test_utap_native.py -m unittest -q`
* [x] `python -m pytest test/binding -m unittest -q`

对应结果摘要：

* [x] `test_utap_phase0.py + test_utap_native.py`：`24 passed`
* [x] `make clean_x` 后仅跑 `test_utap_native.py`：`7 passed`
* [x] `test/binding` 全量 unittest：`141 passed`

### Phase 0：方案冻结与字段盘点

目标：
冻结第一阶段 public surface，明确 native 层与 Python 包装层边界，并建立一轮 `UTAP` C++ 可读字段盘点。

checklist：

* [x] 明确 `_utap` 与 `pyudbm.binding.utap` 的模块职责。
* [x] 明确 `XML` / `XTA` / `TA` / `query file` 四条输入路径的 API 归属。
* [x] 明确 `load_query` / `loads_query` / `parse_query` 的职责差异，并确认其实现落点属于 Phase 4。
* [x] 明确 `builder="auto"` 的行为边界，并确认其实现落点属于 Phase 4。
* [x] 建立字段覆盖清单初稿，至少覆盖 `Document`、`Template`、`Process`、`Location`、`Edge`、`Query`、`ParsedQuery`、`expression_t`、`type_t`、`symbol_t`、`position_t`。
* [x] 建立样本测试分层清单，至少覆盖官方保留样本集、`UTAP/test/models`、手工 `.xta` fixture、极小 synthetic fixture。

阶段测试要求：

* [x] 新增一个纯 Python 侧的计划一致性测试模块或测试辅助数据模块。
* [x] 对 `official/catalog.json` 做结构校验，并直接断言所有 `path` 可达。
* [x] 对 `official/catalog.json` 做结构校验，并直接断言所有 `status` 为 `ok`。
* [x] 对 `official/catalog.json` 做结构校验，并直接断言所有 query 条目具有有效 `context_path`。
* [x] 对字段覆盖清单建立测试占位映射，保证后续阶段能直接 parameterize 接入。

当前状态：
Phase 0 已完成；其中 `load_query` / `loads_query` / `parse_query` 与 `builder="auto"` 已在计划层明确边界，并已指定由 Phase 4 负责具体实现。

### Phase 1：native 模块接入与最小可导入能力

目标：
根构建系统正式接入 `UTAP`，生成可导入的 `_utap` native 模块，并打通最小 parse 能力和异常边界。

checklist：

* [x] 根 `CMakeLists.txt` 增加 `find_package(UTAP CONFIG REQUIRED)`。
* [x] 新增 `_utap` pybind11 模块 target。
* [x] `setup.py` / `CMakeExtension` 纳入 `_utap`。
* [x] 确认 `_utap` 的动态链接路径在本地可用。
* [x] 暴露最小 native 入口：`load_xml`、`loads_xml`、`load_xta`、`loads_xta`、`builtin_declarations`。
* [x] 明确 native 异常到 Python 异常的映射。

阶段测试要求：

* [x] `_utap` 可被 `import`。
* [x] 最小 XML fixture 可 parse。
* [x] 最小文本模型 fixture 可 parse。
* [x] 失败输入会抛出预期异常。
* [x] 对返回对象类型做精确断言。
* [x] 对异常类型做精确断言。
* [x] 对异常归一化消息或错误码做精确断言。
* [x] `_utap` 相关测试集中放在专门文件中，例如 `test_utap_native.py`。
* [x] 除专门的 native 测试文件外，其他测试文件不得导入 `_utap`。
* [x] `test_utap_native.py` 仅测试 `_utap` 的公开接口，不依赖其内部细节。

当前状态：
Phase 1 已完成；并额外验证了 `make clean_x` 之后 `_utap` native 测试仍然可以通过，用于覆盖 CI 中删除 `bin_install` 后的运行时场景。

### Phase 2：`ModelDocument` 与模型结构只读包装

目标：
建立 `ModelDocument` 主入口，并打通 `Document` / `Template` / `Process` / `Location` / `Edge` 等结构对象的只读访问。

checklist：

* [x] 新增 `pyudbm.binding.utap` Python 包装层。
* [x] `load_xml` / `load_xta` 返回 `ModelDocument`。
* [x] `ModelDocument` 提供 `templates`、`processes`、`queries`、`options`、`features`。
* [x] 模型结构对象提供基础只读字段：`name`、`id` 或稳定索引、`position`、`declaration`、`parameter`、location / edge 关系字段。
* [x] 明确父子对象生命周期关系。

阶段测试要求：

* [x] 官方样本集中的 `XML_MODEL_FILE` 全量参数化通过。
* [x] 官方样本集中的 `TEXTUAL_MODEL_FILE` 全量参数化通过。
* [x] 对每类结构对象的数量做直接比对。
* [x] 对每类结构对象的名称列表做直接比对。
* [x] 对每类结构对象的位置字段做直接比对。
* [x] 对每类结构对象的布尔/枚举字段做直接比对。
* [x] 不接受仅用 `assert len(...) > 0` 替代具体字段断言。

已完成进度回填：

当前已经落地的内容：

* [x] `pyudbm.binding.utap` Python 包装层已新增，文件为 `pyudbm/binding/utap.py`。
* [x] `pyudbm.binding.__init__` 已重新导出 `ModelDocument`、结构对象 dataclass 与 `load_xml` / `loads_xml` / `load_xta` / `loads_xta`。
* [x] `load_xml` / `loads_xml` / `load_xta` / `loads_xta` 现在返回 `ModelDocument`。
* [x] `ModelDocument` 已提供 `templates`、`processes`、`queries`、`options`、`features`、`errors`、`warnings`。
* [x] `Template` / `Process` / `Location` / `Edge` 已提供稳定索引、名称、位置和关系字段。
* [x] `ModelDocument` 会保留 `_utap._NativeDocument`，子对象则在初始化时转换为不可变 Python snapshot，生命周期边界已经明确。

已经新增的对应文件：

* [x] `pyudbm/binding/utap.py`
* [x] `test/binding/test_utap.py`

本阶段已经实际完成的验证：

* [x] 官方保留样本中的 `102` 个 `XML_MODEL_FILE` 已按 catalog 中真实 `newxta` 模式全量参数化通过。
* [x] 官方保留样本中的 `29` 个 `TEXTUAL_MODEL_FILE` 已按 catalog 中真实 `newxta` 模式全量参数化通过。
* [x] 对 `ModelDocument` 的 template/process/query 数量做了直接断言。
* [x] 对模板、进程、location、edge 的名称列表做了直接断言。
* [x] 对位置字段、布尔字段、枚举/kind 字段做了直接断言。

当前状态：
Phase 2 已完成；官方样本参数化测试已按 catalog 中记录的真实 `newxta` 组合跑通。

### Phase 3：表达式、类型、符号、位置与错误信息暴露

目标：
把模型和 query 里真正有分析价值的底层语义对象接出来，让 Python 侧不再停留在 summary 级读取。

checklist：

* [x] `expression_t` 包装至少提供 `text`、`kind`、`position`、`type`、`size`、`children`、`is_empty`。
* [x] `type_t` 包装至少提供关键只读判定和文本能力。
* [x] `symbol_t` 包装至少提供名字、种类、关联类型等可读信息。
* [x] `position_t` 与 error/warning 对象提供稳定可读字段。
* [x] `ModelDocument` 暴露 errors / warnings 读路径。
* [x] 建立“已映射字段清单”和“暂未映射字段清单”。

阶段测试要求：

* [x] 代表性样本驱动的字段覆盖参数化测试落地。
* [x] 每个已承诺字段至少有一个样本直接断言。
* [x] 对 errors 的 `line` / `column` / `message` / `context` 做结构化直接断言。
* [x] 对 warnings 的 `line` / `column` / `message` / `context` 做结构化直接断言。
* [x] 对 `position` 对象做结构化直接断言。
* [x] 默认不允许仅用 substring 判断字段正确性。

已完成进度回填：

当前已经落地的内容：

* [x] `_utap._NativeDocument.snapshot()` 已暴露 `expression_t`、`type_t`、`symbol_t`、`position_t`、diagnostic 等结构化 payload。
* [x] `Expression` 已提供 `text`、`kind`、`position`、`type`、`size`、`children`、`is_empty`。
* [x] `TypeInfo` 已提供关键类型判定与保守文本字段。
* [x] `Symbol` 已提供 `name`、`type`、`position`。
* [x] `Diagnostic` / `Position` 已作为稳定 Python dataclass 暴露。
* [x] `MAPPED_FIELDS` / `UNMAPPED_FIELDS` 清单已在 `pyudbm.binding.utap` 中建立。

本阶段已经实际完成的验证：

* [x] 代表性样本 `UTAP/test/models/simpleSystem.xml` 已用于 expression/type/symbol/position 字段直断言。
* [x] 错误诊断通过 `loads_xta(..., strict=False)` 做了结构化直断言。
* [x] warning 诊断通过 `loads_xml(...)` 做了结构化直断言。
* [x] 所有官方模型样本都已通过 public API 加载验证，且不会因 snapshot 访问触发 native 崩溃。

本阶段实现与原计划的偏差：

* [x] `Template.declaration` 字段当前保守返回空字符串，而没有直接调用 `templ.str(false)`。
原因：该上游字符串化 helper 在部分官方复杂模型上会崩溃；当前阶段优先保证 public API 稳定可用。
* [x] `TypeInfo.text` / `TypeInfo.declaration` 当前采用保守 kind-name 映射，而不是直接调用 `type.str()` / `type.declaration()`。
原因：上游类型 pretty printer 在部分复杂类型上会崩溃；当前阶段优先保留稳定、可测试的只读字段。
* [x] 官方样本集中的“成功 parse”按 `status=ok` 解释为“无 errors，可以带 warnings”。
原因：catalog 里已有一批官方样本会稳定产生 typechecking warning，但仍被真实 `UTAP` 验证为可解析样本。
* [x] XTA 诊断的 `position.start/end` 当前保留 `UTAP` 原生绝对偏移，不作为阶段测试中的 golden value。
原因：`UTAP` 在文本模型 parse 前会注入 builtin declarations，导致原生绝对偏移不适合作为用户输入层面的稳定断言；当前阶段测试改为直接断言 `line` / `column` / `path`。

已实际跑过的验证命令与结果摘要：

* [x] `make bin`
* [x] `make build`
* [x] `python -m pytest test/binding/test_utap_native.py test/binding/test_utap_phase0.py test/binding/test_utap.py -m unittest -q`
* [x] `python -m pytest test/binding -m unittest -q`

对应结果摘要：

* [x] Phase 0/1/2/3 专项 UTAP 测试：`162 passed`
* [x] `test/binding` 全量 unittest（含 UTAP 新增测试）：`279 passed`

当前状态：
Phase 3 已完成；native snapshot 路径在官方样本集上已经过崩溃清理，并已通过 public API 侧字段直断言测试。

### Phase 4：query 文件工作流与自动 builder 路径

目标：
把 query 解析从“字符串 helper”补全为正式文件级工作流，并支持普通 property 与 TIGA / controller synthesis query 的自动路由。

checklist：

* [ ] 实现 `load_query(path, document, *, builder="auto")`。
* [ ] 实现 `loads_query(text, document, *, builder="auto")`。
* [ ] 实现 `parse_query(text, document, *, builder="auto")`。
* [ ] `ModelDocument` 增加 `load_query(path, *, builder="auto")`。
* [ ] `ModelDocument` 增加 `loads_query(text, *, builder="auto")`。
* [ ] `builder="auto"` 至少覆盖 `PropertyBuilder` 与 `TigaPropertyBuilder`。
* [ ] query 结果对象暴露 `text`、`quantifier`、`options`、`expression`、`is_smc`、`declaration`、`expectation`。

阶段测试要求：

* [ ] 官方样本集中的 `QUERY_PROPERTY_FILE` 全量参数化通过。
* [ ] 对每个 `.q` 条目先加载 `context_path`。
* [ ] 对每个 `.q` 条目再解析 query 文件。
* [ ] 对每个 `.q` 条目直接断言返回 query 数量。
* [ ] 对每个 `.q` 条目直接断言 quantifier / builder 路径 / 关键字段。
* [ ] 对普通 query 与 TIGA query 分别保留代表性样本组。
* [ ] 对 `builder="auto"`、显式 builder、错误 builder 都补失败路径测试。

### Phase 5：完整只读字段覆盖补齐

目标：
把第一阶段承诺的“C++ 可读字段原则上都可读”落实到对象级实现，关闭大部分“只有 summary、没有细节”的读路径缺口。

checklist：

* [ ] 逐项补齐字段覆盖清单中的已承诺字段。
* [ ] 对每类对象形成字段矩阵，并区分“已实现 / 暂缓 / 不适合第一阶段暴露”。
* [ ] 对暂缓字段补明确说明，不允许 silent drop。
* [ ] 确保 Python facade 不会把底层结构压扁成仅字符串摘要。

阶段测试要求：

* [ ] 新增“字段矩阵驱动”的 parameterized 测试。
* [ ] 每个对象类型至少有一个代表样本组。
* [ ] 每个字段默认做精确比较，包括精确值、精确枚举、精确列表、精确位置对象。
* [ ] 如果某字段因为平台差异只能做归一化比较，测试里必须写明理由。

### Phase 6：`dump` / `dumps`、pretty 与语义 round-trip

目标：
提供正式写出接口，建立语义级 round-trip 能力，并补齐 introspection 相关辅助能力。

checklist：

* [ ] 实现 `document.dump(path)`。
* [ ] 实现 `document.dumps()`。
* [ ] 实现 `document.write_xml(path)`。
* [ ] 实现 `document.to_xml()`。
* [ ] 实现 `document.pretty()`。
* [ ] 增加更多 feature summary / capability summary。
* [ ] 增加 clock / declaration introspection 辅助方法。
* [ ] 明确 `dumps()` 的临时文件桥接实现边界。

阶段测试要求：

* [ ] 对代表性 XML 样本执行 parse。
* [ ] 对代表性 XML 样本执行 dump / dumps。
* [ ] 对代表性 XML 样本执行 reparse。
* [ ] 对 round-trip 后的 template 数量做直接比对。
* [ ] 对 round-trip 后的 process 数量做直接比对。
* [ ] 对 round-trip 后的 query 数量做直接比对。
* [ ] 对 round-trip 后的关键声明文本做直接比对或规范化后精确比对。
* [ ] 对 round-trip 后的 feature flags 做直接比对。
* [ ] 对 round-trip 后的代表性 expression / query 字段做直接比对。
* [ ] 不要求字节级一致，但不能只断言“重新 parse 成功”。

### Phase 7：官方样本集、`.xta` 补样本与平台硬化

目标：
把当前官方保留样本集测试真正纳入长期回归，补足 `.xta` 专项样本，并开始处理 wheel/runtime/platform 级稳定性。

checklist：

* [ ] 把 `official/catalog.json` 接入正式测试辅助工具。
* [ ] 补充手工 `.xta` 样本，并纳入参数化测试。
* [ ] 增加 Linux 平台 smoke。
* [ ] 增加 macOS 平台 smoke。
* [ ] 增加 Windows 平台 smoke。
* [ ] 验证 `ldd` / `otool -L` / `dumpbin` 等效输出。
* [ ] 验证 wheel 修复前后依赖。
* [ ] 验证干净环境导入 `_utap`。

阶段测试要求：

* [ ] 官方样本集全量回归测试在 CI 可稳定执行。
* [ ] `.xta` 补样本测试进入正式测试树。
* [ ] 平台 smoke 测试覆盖 `import`。
* [ ] 平台 smoke 测试覆盖最小 XML parse。
* [ ] 平台 smoke 测试覆盖最小文本模型 parse。
* [ ] 平台 smoke 测试覆盖最小 query parse。
* [ ] 平台测试仍遵循“字段尽量精确断言”的原则，而不是只看进程退出码。

### Phase 8：桥接前置层与第一阶段收口

目标：
为后续 `UDBM/UCDD` 子集桥接准备稳定前置层，并对第一阶段范围做一次收口验收。

checklist：

* [ ] 提供 guard / invariant / declaration / clock 提取辅助接口。
* [ ] 明确 subset compiler 的输入边界。
* [ ] 整理第一阶段“已支持 / 未支持 / 后续阶段”的公开说明。
* [ ] 审核字段缺口清单，确认哪些必须进入第二阶段。
* [ ] 评估是否需要将部分接口提升到更高层包路径。

阶段测试要求：

* [ ] 为语义桥接前置接口补精确断言测试。
* [ ] 对 guard / invariant / clock 提取做代表性样本直接比较。
* [ ] 形成第一阶段总体验收测试，并覆盖官方保留样本集。
* [ ] 形成第一阶段总体验收测试，并覆盖 `.xta` 补样本。
* [ ] 形成第一阶段总体验收测试，并覆盖字段覆盖测试。
* [ ] 形成第一阶段总体验收测试，并覆盖 round-trip 测试。
* [ ] 形成第一阶段总体验收测试，并覆盖平台 smoke。

第一阶段收口标准：

* [ ] 当前阶段承诺的 public API 全部有测试。
* [ ] 当前阶段承诺的字段暴露全部有测试。
* [ ] 没有“代码已写但测试未落”的开放项。
* [ ] 剩余缺口有清单、有原因、有后续阶段归属。

## 十二、风险清单

### 1. API 做得过宽

如果第一阶段就完整暴露整个对象图，后续会很难收敛 public API。

这里要区分两种“宽”：

- 读路径上的语义信息完整，这是需要的
- 可变编辑面和 callback 面过宽，这是要避免的

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
3. 把读路径补到尽量完整，不只停留在 summary 级对象。
4. 用 `UTAP/test/models` 补齐 Python 测试。
5. 完成 `dump` / `dumps`、feature summary、clock 提取。
6. 再开始 subset compiler 和 `UDBM/UCDD` 桥接。

## 十四、结论

`UTAP` 非常适合接入当前仓库，但它最合理的位置不是“又一个孤立 native binding”，而是：

- `pyudbm` 的模型与查询前端层
- 与 `UDBM/UCDD` 并列但职责不同的原生能力模块
- 后续 Python-first UPPAAL workflow 的互操作基础设施

因此，推荐路线是：

- 先做 `_utap + pyudbm.binding.utap`
- 先把 Python 侧读路径做到尽量完整
- 把当前官方保留样本集与 parameterized 测试当作第一阶段硬性基线
- 把 C++ 已可读字段的只读暴露当作明确要求，而不是“后续再看”
- 在此基础上提供 `dump` / `dumps` 和语义级 round-trip
- 再做 query parse、pretty print、模型 introspection 的完善
- 再做 subset compiler 与符号语义桥接
- 暂不在第一阶段承诺完整可编辑 AST 与完整验证语义

这条路线既符合当前仓库已经形成的分层结构，也能最大程度降低对象模型、打包和 public API 一开始就失控的风险。
