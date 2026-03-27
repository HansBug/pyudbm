# UTAP Pythonic Builder 方案展开

## 说明

这份文档聚焦一个比“只把 `UTAP` 暴露出来”更重要的方向：

- 给 Python 端用户提供一个轻量、自然、可组合、易写的 `UTAP` builder
- 让用户可以主要用 Python 来构造、编辑、导出 UPPAAL 模型
- 把 `XML` / `XTA` / `TA` 保持为兼容与互操作格式，而不是唯一作者接口

本文不是立即改代码的施工记录，而是下一阶段 builder 设计与实施提案。

## PR 信息

- Pull Request: <https://github.com/HansBug/pyudbm/pull/15>
- 当前文件路径：`mds/PR15_UTAP_PYTHONIC_BUILDER_PLAN.md`

## 问题背景

当前 `UTAP` 相关 Python API 已经覆盖了若干重要能力：

- 解析 `XML` / `XTA` / `TA`
- 解析 query / property
- 提供 `ModelDocument` 及其只读快照对象
- 提供 `dump` / `dumps` / `to_xta` / `to_ta` 一类导出能力

这些能力已经足够让 Python 用户：

- 读取现有模型
- 浏览模型结构
- 做格式转换
- 做静态检查和快照测试

但对于真正想“在 Python 里写模型”的用户来说，当前仍然有明显缺口：

- 只读对象多，作者接口少
- API 更偏 parser/introspection，而不是 builder/authoring
- 用户写一个小模型，仍然容易退回字符串、XML 或手工拼 declaration 文本
- Python 层还没有形成接近 DSL 的轻量构造体验

这会直接限制仓库向“Python-first 的 UPPAAL workflow”推进。

因此，`UTAP Pythonic Builder` 应该被视为 `UTAP` 接入之后最关键的下一步，而不是可选附属特性。

## 总体目标

`UTAP Pythonic Builder` 的目标，不是把官方内部 AST 原封不动挪到 Python，也不是一上来设计一套过重的元模型框架。

它更应该做到这几件事：

1. 让 Python 用户可以用很少的代码构造一个完整模型。
2. 让模型构造代码读起来像 Python，而不是像手写 XML。
3. 让对象层足够稳定，适合作为 notebook、脚本、单测、批处理的工作流接口。
4. 保持与官方 `UTAP` 解析/pretty-print/类型检查路径对齐，而不是另起炉灶搞一套脱离上游的表示。
5. 为后续和 `UDBM` / `UCDD` / property workflow 的联动预留空间。

一句话概括：

- 不是“把 `UTAP` 暴露给 Python”
- 而是“在 `UTAP` 之上给 Python 用户做一个自然的作者层”

## 设计原则

### 1. 以轻量和顺手为第一原则

builder 如果太重，用户最终还是会退回字符串和 XML。

因此应优先保证：

- 少样板代码
- 少显式中间对象
- 少必须记忆的复杂构造顺序
- 常见路径可以一屏写完

用户应该能很自然地写出类似这样的代码：

```python
from pyudbm.binding import ModelBuilder

model = (
    ModelBuilder()
    .global_decl("clock x;")
    .template("P")
        .location("Init", initial=True)
        .location("Done")
        .edge("Init", "Done", guard="x >= 5", update="x = 0")
        .end()
    .system("P")
    .query("A[] not deadlock")
    .build()
)
```

语法细节可以调整，但这个级别的轻量感是必须目标。

### 2. 优先围绕公开语义对象设计，而不是复制 native 内部结构

builder 不应直接把 `UTAP::DocumentBuilder` 那套细碎 callback 模型搬到 Python。

Python 端用户关心的是：

- 全局声明
- 模板
- location
- edge
- 系统实例
- query

而不是 parser 回调级别的构造事件。

因此，Python builder 应围绕“用户可理解的模型单元”设计，不应围绕 native 回调事件设计。

### 3. 优先做声明式 authoring，不优先做完全可变 AST

从用户体验角度看，第一阶段最值钱的是：

- 容易构造
- 容易导出
- 容易做小范围编辑

而不是一开始就支持一切 AST 就地变异操作。

所以第一阶段更合理的方向是：

- Python 侧 builder object
- `build()` 产出 `ModelDocument`
- 再提供少量常见编辑 helper

而不是先承诺“所有节点任意增删改”。

### 4. 保持官方语义路径为准

builder 构造出的模型，最终应尽量走官方 `UTAP` 的 parse / typecheck / pretty-print 路径来校验和落地。

这意味着：

- Python builder 可以是高层作者接口
- 但最终不要脱离 `UTAP` 的语义入口

理想状态是：

- builder 负责组织 Python 侧模型描述
- 最终仍通过受控序列化再交给 `UTAP` 校验
- `ModelDocument` 仍然是主要稳定产物

这样可以避免 Python builder 慢慢长成一套和上游分叉的“平行模型系统”。

### 5. 用户优先，不是 XML 优先

builder 的中心不是“如何更方便地产生 XML”。

builder 的中心应该是：

- 如何让用户更自然地表达 timed automata 模型

也就是说：

- `XML` / `XTA` / `TA` 是输出与互操作面
- Python builder 才是理想作者面

## 建议的能力边界

### 1. 第一阶段应覆盖的 builder 范围

第一阶段 builder 建议覆盖：

- global declarations
- template 定义
- location 定义
- branchpoint 定义
- edge 定义
- process instantiation
- system declaration
- query 附加
- 导出到 `ModelDocument`

这些能力已经足以覆盖大部分“脚本式构模”和“单测构模”场景。

### 2. 第一阶段不必强做的内容

下面这些能力不建议第一阶段就硬上：

- 完整表达式 AST builder
- 完整类型系统 builder
- 所有 UPPAAL 角落语法的 Python 一等对象化
- 完整图形坐标与布局编辑
- 所有 stochastic / strategy / MITL 特性的全量 Python DSL

原因很简单：

- 这些内容会迅速把 builder 做重
- 它们对“先让 Python 端写模型顺手起来”的贡献不成正比

第一阶段应先把 80% 常见建模路径做顺，再逐步补高阶语法面。

## 推荐 API 形态

我建议不要只做一种入口，而是同时给两层：

### 1. 面向脚本用户的链式 builder

这是最直接的作者体验层。

建议提供：

- `ModelBuilder`
- `TemplateBuilder`
- `EdgeBuilder`

大致示意：

```python
model = (
    ModelBuilder()
    .global_decl("clock x;")
    .template("Worker")
        .location("Idle", initial=True)
        .location("Busy", invariant="x <= 5")
        .edge("Idle", "Busy", sync="start?", update="x = 0")
        .edge("Busy", "Idle", guard="x >= 3", sync="done!")
        .end()
    .instance("W1", "Worker")
    .system("W1")
    .query("A[] not deadlock", comment="basic safety")
    .build()
)
```

这个层次的重点是：

- 构造快
- 可读性强
- 适合 notebook / demo / tests

### 2. 面向程序化生成用户的 dataclass 风格 spec

链式 builder 很顺手，但对自动化生成、批量转换、配置驱动建模未必最好。

因此建议再提供一层简单 spec 对象，例如：

- `ModelSpec`
- `TemplateSpec`
- `LocationSpec`
- `EdgeSpec`
- `QuerySpec`

这样用户也可以写：

```python
spec = ModelSpec(
    global_declarations="clock x;",
    templates=(
        TemplateSpec(
            name="P",
            locations=(
                LocationSpec("Init", initial=True),
                LocationSpec("Done"),
            ),
            edges=(
                EdgeSpec("Init", "Done", guard="x >= 1"),
            ),
        ),
    ),
    instances=(("P1", "P", ()),),
    system=("P1",),
)

document = build_model(spec)
```

这层的价值在于：

- 更适合配置驱动和代码生成
- 更适合做快照测试
- 更适合序列化/反序列化

### 3. 两层关系

推荐关系是：

- 链式 builder 最终产出 spec
- spec 再统一进入构建函数
- 构建函数再产出 `ModelDocument`

这样内部实现会更清楚：

- 用户体验层与内部落地层分离
- 后续做验证、归一化、默认值填充都更方便

## 推荐的核心对象

### 1. `ModelBuilder`

建议它负责：

- 收集全局声明
- 收集模板
- 收集实例
- 收集系统定义
- 收集 query
- 最终 `build()`

建议方法：

- `global_decl(text)`
- `global_decls(*texts)`
- `template(name, *, parameters="", declaration="", type=None, mode=None)`
- `instance(name, template, *arguments)`
- `system(*process_names)`
- `query(formula, comment="", options=(), expectation=None, location="")`
- `build()`
- `to_document()`

### 2. `TemplateBuilder`

建议负责：

- local declaration
- location / branchpoint / edge
- init location

建议方法：

- `declaration(text)`
- `location(name, *, initial=False, invariant="", urgent=False, committed=False, exp_rate="", cost_rate="")`
- `branchpoint(name)`
- `edge(source, target, *, guard="", update="", sync="", select="", action_name="")`
- `end()`

### 3. `LocationSpec`

建议至少包含：

- `name`
- `invariant`
- `urgent`
- `committed`
- `initial`
- `exp_rate`
- `cost_rate`

第一阶段不建议强行要求用户提供图形坐标。

如果没有坐标，就让导出路径走一个稳定默认值或干脆不以图形布局为第一目标。

### 4. `EdgeSpec`

建议至少包含：

- `source`
- `target`
- `guard`
- `update`
- `sync`
- `select`
- `action_name`

这个层次已经能满足绝大多数 timed automata 脚本建模。

### 5. `QuerySpec`

建议保持与当前 `Query` 接近，避免重复心智负担。

也就是说，builder 端 query 最好最终还是能自然落到当前已有的 `Query` 数据结构或兼容结构上。

## 构建落地路径建议

这里是最关键的工程问题。

我建议不要让 Python builder 直接去驱动 native `DocumentBuilder` callback。

更稳妥的路线是：

1. Python builder 产出一份 Python spec。
2. Python spec 被序列化为受控的中间表示。
3. 中间表示进入官方 `UTAP` 可验证入口。
4. 得到最终 `ModelDocument`。

### 方案 A：builder -> XML -> `load_xml`

这是最容易落地的起点。

优点：

- 复用当前已经稳定的 `dump` / `load_xml` / `ModelDocument` 路径
- 容易做 round-trip
- 对现有代码侵入较小

缺点：

- 本质上还是先生成 XML
- builder 内部仍需维护一套 XML 序列化规则

但作为第一阶段，这个方案非常现实。

### 方案 B：builder -> XTA 文本 -> `loads_xta`

这个方案更接近“文本作者接口”，但要注意两点：

- 文本拼接的稳定性与复杂语法覆盖更难
- 一旦自己手写文本生成，容易和官方 pretty-printer 分叉

因此，我不建议第一阶段直接以手工文本生成作为主落地路径。

### 方案 C：builder -> C++ 侧受控构造器

长期看，这可能是最强的方案，但第一阶段成本偏高。

因为这意味着：

- 要在 C++ binding 层新建一套受控构造接口
- 处理对象生命周期、错误回传、类型约束
- 明确 native 与 Python 侧各自负责什么

这条路线适合在 builder 稳定后再考虑，而不适合最先做。

### 结论

第一阶段最推荐：

- Python builder -> XML 中间表示 -> `load_xml`

这样能最快把作者体验做出来，同时仍然复用当前已验证的官方语义入口。

## 为 Python 用户真正省事的具体点

builder 要让人感觉“真省事”，关键不只是对象名好看，而是要解决几个真问题。

### 1. 自动处理常见样板

例如：

- 单个 `initial=True` location 自动成为 init
- `system("P1", "P2")` 自动生成 system declaration
- `instance("P1", "P")` 自动生成 `P1 = P();`

不要让用户为这些固定模式写重复样板。

### 2. 对字符串接口保持包容

不要过早要求所有 guard / sync / update 都必须是复杂对象。

字符串是 Python 用户最自然的最低摩擦接口。

所以第一阶段可以明确接受：

- `guard="x >= 5"`
- `update="x = 0"`
- `sync="tick?"`

后续如果要加表达式对象，也应是增强而不是替代。

### 3. 提供名称级引用，而不是强迫用户先拿对象

例如 edge 定义时，应该允许直接写：

- `edge("A", "B", guard="x > 1")`

而不是要求：

- 先拿 `loc_a`
- 再拿 `loc_b`
- 再传对象

第一种方式对脚本和小模型明显更友好。

### 4. 保持错误信息贴近 builder 输入

如果 builder 构造失败，错误信息最好能指向：

- 重复 location 名字
- 缺失 init
- `system()` 里引用了未实例化 process
- edge 引用了不存在的 location

也就是说，builder 自己先做一轮轻量验证，不要所有问题都等到底层 parser 报错。

### 5. 导出 API 要顺滑

理想上用户拿到 builder 结果之后，应能立刻：

- `.build()`
- `.to_xta()`
- `.to_ta()`
- `.dump(path)`
- `.dump_xta(path)`

不要让用户在“builder 产物”和“document 产物”之间搞不清使用姿势。

## 建议的验证分层

builder 相关校验建议分成两层：

### 1. Python 侧轻量结构校验

负责抓明显错误：

- 重名模板
- 重名 location
- 空模板
- 多个 initial location
- 未知 source/target
- 未定义实例模板
- `system()` 引用未知 process

这层错误要尽量清楚、靠近用户输入。

### 2. `UTAP` 侧正式语义校验

负责最终语法与语义正确性：

- declaration 文本是否合法
- guard / update / sync 语义是否合法
- query 语义是否合法
- 特性限制是否满足

也就是说：

- Python builder 做结构层 guardrail
- `UTAP` 做最终语言权威校验

这个分层是合理的。

## 与现有 API 的关系

builder 不应该替代当前 `load_xml` / `load_xta` / `ModelDocument` 路径。

更合理的关系是：

- `load_*` 系列负责“导入现有模型”
- builder 负责“构造新模型”
- 两者最终都统一落到 `ModelDocument`

这样 Python 端用户会获得一个统一心智模型：

- 不管模型从哪里来，最后都是 `ModelDocument`
- 不管是 builder 还是 parser，后续操作都尽量一致

这会大幅降低 API 碎片化风险。

## 文本导出与 builder 的关系

当前已经有：

- `to_xta()`
- `dump_xta()`
- `to_ta()`
- `dump_ta()`

builder 应尽量直接复用这条导出链。

这里特别重要的一点是：

- builder 不应自己另搞一套“文本 writer”
- 仍应复用官方 pretty-printer 路径

这样才能保证：

- 文本格式稳定
- 与官方行为一致
- 不会再出现 Python 层手搓 writer 和上游输出慢慢漂移的问题

## 测试建议

builder 一旦开始做，测试要比普通 parser API 更重视使用体验。

我建议至少分四层。

### 1. 最小构模快照测试

例如：

- 单模板单 location
- 双 location 单 edge
- 带 query
- 带 system 多实例

这些测试应该直接断言：

- `build().to_xta()` 的完整文本
- `dump()` / `dump_xta()` 的完整内容

并继续使用 `TextAligner` 做跨平台换行归一。

### 2. 结构级 builder 校验测试

例如：

- 重复 location
- 缺失 init
- 未知 source/target
- 未知模板实例

这层要断言 Python 侧错误消息质量。

### 3. round-trip 测试

例如：

- builder -> document -> `to_xta()` -> `loads_xta()` -> snapshot
- builder -> document -> `dump()` -> `load_xml()` -> snapshot

这层能确保 builder 不是一次性字符串玩具。

### 4. 与官方 fixture 的互操作测试

这层重点不是“builder 重建所有官方模型”，而是：

- builder 造出的模型能走当前官方 parser / pretty-printer / query 路径
- 现有官方输入模型经过 Python 编辑后仍可稳定导出

## 分阶段实施建议

### Phase A：最小可用 builder

目标：

- `ModelBuilder`
- `TemplateBuilder`
- `location`
- `edge`
- `instance`
- `system`
- `query`
- `build() -> ModelDocument`

约束：

- declaration / guard / update / sync 先都以字符串为主
- 先不做复杂类型对象 DSL

这是最应该先做的一期。

### Phase B：spec 层与程序化生成

目标：

- `ModelSpec` / `TemplateSpec` / `LocationSpec` / `EdgeSpec`
- `build_model(spec)`
- builder 与 spec 互转

这期完成后，builder 就不仅适合人手写，也适合自动生成。

### Phase C：常见编辑 helper

目标：

- `document.with_queries(...)`
- `document.with_global_declarations(...)`
- `document.with_template_replaced(...)`
- `document.with_processes(...)`

这期会让“导入现有模型 -> Python 小改 -> 导出”的体验更顺。

### Phase D：高阶 DSL 与语义桥接

目标：

- 更强的 declaration 组织方式
- 常见 timed automata 模式 helper
- 与 `UDBM` / `UCDD` / property workflow 的桥接

这期再考虑，不应提前透支复杂度。

## 风险与注意点

### 1. 不要把 builder 做成“第二套 UTAP”

如果 Python builder 试图完整复制官方所有语法与内部结构，最后几乎一定会失控。

必须记住：

- builder 是高层作者接口
- `UTAP` 才是权威语言前端

### 2. 不要太早对象化 expression/type

很多时候字符串其实更实用。

如果过早要求：

- `GuardExpr`
- `SyncExpr`
- `UpdateExpr`
- `TypeExpr`

builder 会迅速变得啰嗦和难用。

### 3. 不要忽视 query 也是 builder 的一部分

对 Python 自动化用户来说，模型和 query 往往是一体的。

如果 builder 只管 automata，不管 queries，最终工作流还是会断裂。

### 4. 不要把图形布局放到第一优先级

第一阶段 builder 应优先解决“语义可写”，不是“编辑器坐标完美可控”。

布局信息可以后补，但轻量 authoring 不能后补。

## 我认为最值得优先落地的具体范围

如果只选一个最有价值、最现实的起步范围，我建议是：

1. `ModelBuilder`
2. `TemplateBuilder`
3. `location()` / `edge()`
4. `instance()` / `system()`
5. `query()`
6. `build() -> ModelDocument`

并且内部先走：

- builder spec -> XML -> `load_xml`

这是最稳妥、最符合当前仓库现实的落点。

## 建议的验收标准

这个 builder 真做出来以后，我建议用下面几条判断它是不是“有用”。

1. 用户能在不碰 XML 的情况下写出一个最小 timed automata 模型。
2. 用户能在十几行 Python 里写出一个带两个 location、两个 edge、一个 query 的模型。
3. 产出的 `ModelDocument` 能直接复用现有导出、查询、快照接口。
4. builder 错误信息主要反映用户输入问题，而不是暴露底层内部错误。
5. 单元测试能用完整 `to_xta()` / `to_ta()` 快照稳定验证。

如果这五条能成立，这个 builder 就已经是对 Python 端用户真正有价值的特性，而不是概念性包装。

## 结论

`UTAP Pythonic Builder` 不是锦上添花，而是决定 `UTAP` 接入是否真正服务 Python 用户的关键一步。

当前仓库已经基本具备三项前提：

- `UTAP` 解析与导出链已打通
- `ModelDocument` 只读语义层已存在
- `XML` / `XTA` / `TA` / query 的互操作基础已建立

下一步最合理的推进，不是继续只加 parser helper，而是把这些能力往 Python 作者体验层收束成一个轻量 builder。

如果方向正确，这个 builder 最终会成为：

- Python 端建模入口
- `UTAP` 互操作层上方的高层作者面
- 后续 timed automata / property / symbolic workflow 的组织中心之一

这才是 `UTAP` 在 `pyudbm` 里最值得做深的地方。
