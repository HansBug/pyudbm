# UTAP Pythonic Builder 方案展开

## 说明

这份文档只聚焦一件事：

- `UTAP Pythonic Builder` 到底应该怎么做，才能让 Python 用户真正愿意用它写模型

本文不再展开已经独立推进的 `UTAP` 文本导出、缩进控制、`ModelDocument` 只读检查层等工作。这里的重点不是 parser helper，也不是现有导出接口补丁，而是：

- Python 用户侧的作者体验应该是什么样
- builder 的最小公开面应该长什么样
- 内部应该如何落到当前 `UTAP` 语义路径

## PR 信息

- Pull Request: <https://github.com/HansBug/pyudbm/pull/15>
- 当前文件路径：`mds/PR15_UTAP_PYTHONIC_BUILDER_PLAN.md`

## 核心判断

`UTAP` 接入如果只停留在：

- 读模型
- 看模型
- 解析 query
- 导出文本

那么它对 Python 用户的价值仍然偏“互操作层”，还不是“作者层”。

真正能把这块能力做深的关键，是让 Python 用户可以：

- 主要用 Python 构造 timed automata 模型
- 只在必要时把 `XML` / `XTA` / `TA` 当作导入导出格式

所以 `UTAP Pythonic Builder` 不是附属特性，而是 `UTAP` 这条线往“Python-first 工作流”继续推进时最关键的一步。

## 本文聚焦范围

本文只讨论以下内容：

1. Python 用户理想中的建模体验。
2. builder 的公开 API 应该长什么样。
3. builder 的内部落地路径应该怎么选。
4. 第一阶段和后续阶段分别做什么。

本文明确不展开这些方向：

- 现有 `to_xta` / `to_ta` 的文本导出细节
- 现有只读 `ModelDocument` 字段覆盖面
- 一般性的 parser / query binding 扩展事项
- 与 builder 无直接关系的 `UTAP` 零散增强项

## 为什么 builder 必须做轻

builder 一旦做重，用户会立刻退回：

- 写 XML
- 写 XTA 字符串
- 手动拼 declaration 文本

所以这个特性的成败，不在于“理论上能不能表达完整模型”，而在于“用户写一个小模型时，愿不愿意真的用它”。

这里最重要的产品判断是：

- builder 首先是作者接口，不是 AST 展示接口
- builder 首先要让常见路径顺手，不是先把所有角落语法对象化

## Python 用户侧应该是什么体验

我建议先围绕三类最真实的 Python 用户场景设计。

### 场景 1：脚本里快速写一个最小模型

这是最核心的 happy path。

理想体验应该接近这样：

```python
from pyudbm.binding import ModelBuilder

doc = (
    ModelBuilder()
    .clock("x")
    .template("P")
        .location("Init", initial=True)
        .location("Done")
        .edge("Init", "Done", when="x >= 5", reset={"x": 0})
        .end()
    .process("P1", "P")
    .system("P1")
    .query("A[] not deadlock")
    .build()
)
```

这个例子里最重要的不是具体名字，而是这几个感觉必须成立：

- 不需要写 XML
- 不需要手动写 `P1 = P();`
- 不需要手动写 `system P1;`
- update 不一定非要写成原始字符串，可以接受一个 Python 映射

### 场景 2：写一个稍微真实一点的双模板系统

builder 不能只在最小例子里好看。

更有代表性的体验应该像这样：

```python
from pyudbm.binding import ModelBuilder

m = (
    ModelBuilder()
    .clock("x")
    .chan("start", "done")
)

with m.template("Worker") as t:
    t.location("Idle", initial=True)
    t.location("Busy", invariant="x <= 5")
    t.edge("Idle", "Busy", recv="start", reset={"x": 0})
    t.edge("Busy", "Idle", when="x >= 3", send="done")

doc = (
    m.process("W1", "Worker")
     .process("W2", "Worker")
     .system("W1", "W2")
     .query("A[] not deadlock", comment="basic sanity")
     .build()
)
```

这个场景说明了几个关键设计点：

- builder 应该有模板上下文写法，避免长链条里反复 `.end()`
- 同步最好支持 `send=` / `recv=` 这样的 Python 语义糖
- 声明最好支持常见 helper，例如 `clock()` / `chan()`

### 场景 3：程序化批量生成模型

builder 如果只适合人手写，不适合程序生成，那它只能覆盖一半场景。

批量生成场景里，用户体验更应该接近这样：

```python
from pyudbm.binding import ModelSpec, TemplateSpec, LocationSpec, EdgeSpec, build_model

spec = ModelSpec(
    clocks=("x",),
    templates=(
        TemplateSpec(
            name="P",
            locations=(
                LocationSpec("Init", initial=True),
                LocationSpec("Done"),
            ),
            edges=(
                EdgeSpec("Init", "Done", when="x >= 1"),
            ),
        ),
    ),
    processes=(("P1", "P", ()),),
    system=("P1",),
    queries=("A[] not deadlock",),
)

doc = build_model(spec)
```

所以 builder 不应该只有链式写法，还应有一层适合代码生成的 spec。

### 场景 4：导入已有模型后，基于 Python 补一点结构

这个不是第一阶段必须做完，但应该从一开始就预留。

理想上后续用户应该能写：

```python
from pyudbm.binding import load_xml, ModelBuilder

doc = load_xml("base.xml")
builder = ModelBuilder.from_document(doc)
builder.query("A[] not deadlock")
new_doc = builder.build()
```

这类“导入后轻改”的路径，对自动化实验和论文脚本很重要。

## 设计原则

### 1. 先服务常见建模路径

第一阶段先覆盖：

- 全局声明中的常见时钟/通道/整数
- 模板
- location
- edge
- process instantiation
- system
- query

不要一上来试图覆盖所有高级语法角落。

### 2. 名字优先，而不是对象优先

builder 里最自然的引用方式应该是按名称。

例如：

```python
t.edge("Idle", "Busy", when="x >= 3")
```

而不是要求用户先持有 `Location` 对象再传进去。

名字优先更适合：

- 短脚本
- notebook
- 自动生成
- 配置驱动

### 3. 字符串友好，但不是字符串唯一

builder 不应过早强迫用户构造表达式对象。

例如这些都应该自然成立：

- `when="x >= 5"`
- `sync="tick?"`
- `update="x = 0"`

但对于最常见的 Python 场景，builder 还应该提供轻量语义糖：

- `send="tick"` -> `sync="tick!"`
- `recv="tick"` -> `sync="tick?"`
- `reset={"x": 0, "y": 1}` -> `update="x = 0, y = 1"`

也就是说：

- 原始字符串接口要保留
- 常见语义糖要补上

### 4. 不让用户直接碰 XML 细节

builder 的意义之一，就是把 `UTAP` 的兼容格式边界藏到后面。

用户不应该需要知道：

- `<template>` 怎么排
- `<init ref=...>` 怎么写
- `<system>` 怎么拼

这些都应由 builder 自动处理。

### 5. 最终稳定产物仍应是 `ModelDocument`

builder 最终应该落到：

- `ModelDocument`

这样现有和未来的工作流才能统一：

- 导入模型 -> `ModelDocument`
- builder 构模 -> `ModelDocument`

用户只需要记住一个后续操作中心。

## 建议的公开 API

我建议公开面分两层：

1. 链式/上下文化的作者层
2. dataclass/spec 风格的程序生成层

### 一、作者层

#### `ModelBuilder`

建议负责：

- 全局声明
- 模板收集
- process 收集
- system 声明
- query 收集
- `build()`

建议方法：

- `declaration(text)`
- `clock(*names)`
- `chan(*names, broadcast=False, urgent=False)`
- `integer(name, *, lower=None, upper=None, init=None, const=False)`
- `template(name, *, parameters="", declaration="", type=None, mode=None)`
- `process(name, template, *arguments)`
- `system(*process_names)`
- `query(formula, *, comment="", options=(), expectation=None, location="")`
- `build()`

其中最重要的是：

- `clock()` / `chan()` / `integer()` 这种 helper 一定要有
- 不能把所有 declaration 都丢给原始字符串

#### `TemplateBuilder`

建议负责：

- local declaration
- location / branchpoint
- edge
- init

建议方法：

- `declaration(text)`
- `location(name, *, initial=False, invariant="", urgent=False, committed=False, exp_rate="", cost_rate="")`
- `branchpoint(name)`
- `edge(source, target, *, when="", guard="", sync="", send="", recv="", update="", reset=None, select="", action_name="")`
- `end()`

这里建议明确：

- `guard` 是原始名
- `when` 是更 Python 用户友好的别名
- `update` 是原始名
- `reset` 是常见赋值更新的 Python 侧别名

也就是说：

- API 要对 UPPAAL 老用户友好
- 也要对纯 Python 用户友好

#### 是否需要 `with ... as ...`

我倾向于要。

因为下面这种写法比长链更稳：

```python
m = ModelBuilder().clock("x")

with m.template("P") as t:
    t.location("Init", initial=True)
    t.location("Done")
    t.edge("Init", "Done", when="x >= 1")
```

原因很简单：

- 模板内部逻辑经常会变复杂
- 长链加 `.end()` 容易变得难读
- 上下文写法更像 Python，而不是迷你 DSL 语言

我建议：

- `with ... as ...` 作为主推荐写法
- `.end()` 作为兼容链式写法保留

### 二、spec 层

spec 层的目标不是替代作者层，而是服务：

- 配置驱动生成
- 批量实验生成
- 快照测试
- 结构化序列化

建议对象：

- `ModelSpec`
- `TemplateSpec`
- `LocationSpec`
- `EdgeSpec`
- `QuerySpec`

建议关系：

- 作者层内部先产出 spec
- `build_model(spec)` 统一落地

这样好处很明确：

- 内部规范化更清楚
- 默认值填充更清楚
- 校验逻辑更清楚
- 后续如果要支持 `from_document()`，也更容易做中间转换

## 我更推荐的 Python 用户主路径

如果只选一条“官方最想推荐给用户的写法”，我建议是这条：

```python
from pyudbm.binding import ModelBuilder

m = (
    ModelBuilder()
    .clock("x")
    .chan("start", "done")
)

with m.template("Worker") as t:
    t.location("Idle", initial=True)
    t.location("Busy", invariant="x <= 5")
    t.edge("Idle", "Busy", recv="start", reset={"x": 0})
    t.edge("Busy", "Idle", when="x >= 3", send="done")

doc = (
    m.process("W1", "Worker")
     .system("W1")
     .query("A[] not deadlock")
     .build()
)
```

这条主路径有几个优点：

- 看起来像 Python，不像 XML
- 看起来像建模，不像手写字符串拼接
- 常见同步和 reset 场景足够简洁
- 最终产物还是 `ModelDocument`

我认为这是最值得围绕它打磨 API 的使用姿势。

## 不建议做成什么样

为了保证 builder 真正可用，我建议明确避免以下几种方向。

### 1. 不要做成回调事件模拟器

不要把 native `DocumentBuilder` 的细碎构造事件原样公开到 Python。

那样用户最终只会觉得：

- 这不是 builder
- 这只是 parser callback 在 Python 的翻译

### 2. 不要过早做完整表达式 AST DSL

如果一开始就要求用户写：

- `GuardExpr`
- `UpdateExpr`
- `SyncExpr`

builder 会一下变重。

第一阶段最合理的策略仍然是：

- 字符串优先
- 常见语义糖辅助
- AST DSL 以后再补

### 3. 不要把图形坐标当第一优先级

第一阶段 builder 应优先解决：

- 语义结构能自然写

而不是：

- 每个 location 的图形坐标都要精细编辑

布局信息是次优先级。

### 4. 不要让用户既写 helper 又写 declaration 重复样板

如果用户已经写了：

```python
m.clock("x")
```

就不应该还逼他再写：

```python
m.declaration("clock x;")
```

helper 必须真地减少样板，而不是只是换一种入口。

## builder 的内部落地路径

这里我倾向于一个很明确的选择：

- 第一阶段不要直接驱动 native `DocumentBuilder`
- 第一阶段优先走 Python builder -> spec -> 受控 XML -> `load_xml`

### 为什么第一阶段先走 XML

理由很现实：

1. 当前仓库已经有稳定的 `load_xml` -> `ModelDocument` 路径。
2. 这条路径天然会复用官方 `UTAP` 解析和语义检查。
3. Python builder 的主要问题是作者体验，不是 native callback 性能。
4. 这样能更快把公开 API 形态稳定下来。

### 为什么不建议第一阶段手写 XTA/TA 生成

原因也很明确：

- 文本 writer 容易和上游 pretty-printer 漂移
- 复杂语法下文本生成更难维护
- 一旦 writer 自己长逻辑，builder 的风险会被放大

builder 第一阶段应专注：

- 用户怎么写舒服
- 产物怎么稳定落到 `ModelDocument`

而不是急着把文本 writer 再造一遍。

### 为什么暂不建议一开始走 C++ 直接构造

长期看，C++ 侧受控构造器未必没有价值。

但第一阶段它的问题是：

- 研发成本高
- 接口收敛更难
- 生命周期、异常、约束回传都更重

所以现阶段更合理的顺序是：

1. 先把 Python builder 公开面做对
2. 再看内部实现是否值得往 C++ 下沉

## builder 应该自己做的校验

builder 不能把所有错误都交给底层 parser。

至少以下几类错误，builder 自己就应该先挡住：

- 重名模板
- 重名 location
- 多个 `initial=True`
- edge 引用未知 location
- process 引用未知模板
- `system()` 引用未知 process

这层错误信息要尽量贴近用户输入，而不是底层内部语汇。

例如：

- 好的错误：`template 'P' has duplicate location 'Idle'`
- 不好的错误：`XML parse failed near ...`

## 我建议分几期做

### Phase A：最小可用 builder

范围：

- `ModelBuilder`
- `TemplateBuilder`
- `clock()` / `chan()`
- `location()` / `edge()`
- `process()` / `system()`
- `query()`
- `build() -> ModelDocument`

这是最应该先落地的一期。

### Phase B：Python 语义糖补齐

范围：

- `send=` / `recv=`
- `reset={...}`
- 常见整数/常量 helper
- builder 侧轻量校验完善

这期的目标是把“顺手程度”再提升一档。

### Phase C：spec 层正式化

范围：

- `ModelSpec` / `TemplateSpec` / `LocationSpec` / `EdgeSpec` / `QuerySpec`
- `build_model(spec)`
- builder 与 spec 的互转

这期完成后，builder 就不只是作者工具，也会成为生成工具。

### Phase D：导入后编辑路径

范围：

- `ModelBuilder.from_document(...)`
- 常见 patch helper
- 更顺的 import-edit-export 工作流

这期很重要，但不应该压在第一阶段。

## 测试建议

builder 测试应主要围绕“用户会怎么用”，而不是只围绕内部结构。

我建议至少做这几类：

### 1. happy path 全量文本快照

例如：

- 最小单模板模型
- 双 location 单 edge
- 带 query
- 带两个 process

这些都应该直接断言：

- `doc.to_xta() == ...`
- `doc.to_ta() == ...`

并继续用 `TextAligner` 做跨平台文本归一。

### 2. builder 结构错误测试

例如：

- 重复 location
- 缺 init
- 未知 source/target
- 未知模板 process

这层重点不是“抛异常”本身，而是错误消息是否清楚。

### 3. round-trip 测试

例如：

- builder -> `ModelDocument` -> `to_xta()` -> `loads_xta()`
- builder -> `ModelDocument` -> `dump()` -> `load_xml()`

这能证明 builder 不是一次性字符串玩具。

### 4. spec 与 builder 等价测试

同一个模型：

- 用链式 builder 造一次
- 用 spec 造一次

最后应得到等价 `ModelDocument`。

## 验收标准

我建议用下面这些问题判断 builder 是否真的做对了。

1. Python 用户能在不写 XML 的情况下写出一个最小 timed automata 模型。
2. 用户能在二十行左右写出一个带两个 location、两个 edge、一个 query 的模型。
3. 常见同步和 reset 场景不需要手写原始 `sync="a?"` / `update="x = 0"` 字符串。
4. builder 产物天然落到 `ModelDocument`，后续工作流不割裂。
5. 错误信息主要反映用户输入问题，而不是底层 parser 细节。

## 结论

如果 `UTAP` 在 `pyudbm` 里只是 parser 和 pretty-printer，那么它对 Python 用户仍然主要是互操作层。

只有把 `UTAP Pythonic Builder` 做出来，而且做得足够轻、足够自然、足够像 Python，`UTAP` 才会真正成为：

- Python 端建模入口
- UPPAAL 兼容格式之上的作者层
- 后续 timed automata / property / symbolic workflow 的组织中心之一

这份文档的核心建议可以压缩成一句话：

- 第一阶段先做一个 string-friendly、name-first、带少量语义糖、最终落到 `ModelDocument` 的轻量 builder

我认为这就是当前最值得推进的方向。
