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

补充说明：

- `PR16` 已经独立处理 `UTAP` 文本导出的缩进控制，因此本文不再把文本导出补丁类事项混入 builder 方案
- 本文后续所有 phase 都只围绕 builder 本身展开

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

## 实施硬约束

这一节不是建议，而是后续 builder 实施时应直接遵守的约束。

### 1. 代码风格必须遵守 `AGENTS.md`

后续 builder 相关实现，应明确遵守仓库当前 `AGENTS.md` / `CLAUDE.md` 中已经给出的代码规范，尤其是：

- 与现有 `pyudbm.binding.utap` 风格保持一致
- 默认使用 ASCII
- 不引入和现有 public API 风格冲突的命名
- 动作语义一律使用 method，不要误做成 property
- 注释保持克制，不写低信息量注释

### 2. 所有新增 public API 都必须补完整 pydoc

后续 builder 相关 public class / function / method 必须补齐和当前仓库一致的文档字符串风格。

最低要求：

- 一行清楚说明用途
- 对关键参数给出 `:param ...:` / `:type ...:` 风格说明
- 对返回值给出 `:return:` / `:rtype:` 说明
- 当方法语义不显然时，补充行为说明
- 必须带 `Example::` 或 `Examples::` 风格示例

这里的目标不是“有 docstring 就行”，而是和当前 `pyudbm.binding.utap` 里已有 public API 的 pydoc 风格一致。

### 3. 单元测试只能通过 public surface 访问能力

后续 builder 相关测试必须遵守下面这条硬规则：

- 只允许 import 和使用 public module / public class / public function / public method / public field

明确禁止：

- import 私有模块，例如 `pyudbm.binding._utap`
- import 任何下划线前缀对象
- 直接访问 protected/private field
- 用 monkeypatch 或反射方式绕过 public API 做覆盖率

换句话说：

- 测试必须站在真实 Python 用户的视角写

### 4. 每个 phase 都必须补单元测试，并在 phase 范围内把 public coverage 拉到最高

这里“覆盖率拉到最高”的含义是：

- 以当前 phase 新增的 public thing 为核心
- 在不使用 private/protected 接口的前提下
- 把正常路径、边界路径、错误路径、round-trip 路径尽可能都覆盖到

这不是要求盲目追求数字，而是要求：

- 不留明显未测的 public branch
- 不把“以后再测”当常态

### 5. 文本相关测试继续使用全量断言

builder 一旦产出 `ModelDocument` 并进入 `to_xta()` / `to_ta()` 路径，测试应该继续坚持：

- 文本全量断言，而不是 substring 弱断言
- 使用 `TextAligner` 做跨平台换行归一

也就是说，后续 builder 测试中应优先出现：

- `text_aligner.assert_equal(expected, doc.to_xta())`

而不是：

- `assert "process P()" in doc.to_xta()`

## 建议的文件落点

为了让实施路径更明确，这里把文件落点直接定死：

- builder 主实现放在 `pyudbm/binding/utap_builder.py`
- `pyudbm/binding/__init__.py` 负责 import / re-export builder 相关 public API
- `pyudbm/binding/utap.py` 保持 parser / snapshot / `ModelDocument` 这条主线，不继续承载 builder 主实现

- `pyudbm/binding/utap.py`
  - 继续保留现有 parser / snapshot / document 相关公开面
- `pyudbm/binding/utap_builder.py`
  - 放 builder / spec / build helper 的主要公开实现
- `pyudbm/binding/__init__.py`
  - import 并 re-export builder 相关 public API
- `docs/source/api_doc/binding/utap.rst`
  - 补 builder 相关 public API 文档入口
- `test/binding/test_utap_builder_phase1.py`
- `test/binding/test_utap_builder_phase2.py`
- `test/binding/test_utap_builder_phase3.py`
- `test/binding/test_utap_builder_phase4.py`
- `test/binding/test_utap_builder_phase5.py`
- `test/binding/test_utap_builder_phase6.py`
- `test/binding/test_utap_builder_phase7.py`

这里的重点是：

- builder 一律不要继续往 `utap.py` 里堆主实现
- `utap_builder.py` 是 builder 相关公开实现的唯一主落点
- `__init__.py` 是 builder 对外暴露的统一入口
- 但最终 public import 面仍然尽量统一在 `pyudbm.binding`

## 明确可执行的 phase 计划

### Phase 1：最小可用作者层

目标：

- 先把“Python 用户能不写 XML 地写一个最小模型”这件事做成

本 phase 范围：

- `ModelBuilder`
- `TemplateBuilder`
- `clock()`
- `chan()`
- `template()`
- `location()`
- `edge()`
- `process()`
- `system()`
- `query()`
- `build() -> ModelDocument`

本 phase 不做：

- `ModelSpec` 系列正式公开
- `from_document()`
- 复杂 declaration DSL
- 图形布局控制

建议交付文件：

- `pyudbm/binding/_utap_builder.cpp`
- `pyudbm/binding/_utap_bindings.hpp`
- `pyudbm/binding/utap_builder.py`
- `pyudbm/binding/__init__.py`
- `docs/source/api_doc/binding/utap.rst`
- `test/binding/test_utap_builder_phase1.py`

本 phase checklist：

* [x] 新增 public `ModelBuilder`
* [x] 新增 public `TemplateBuilder`
* [x] builder 主实现放在 `pyudbm/binding/utap_builder.py`
* [x] `pyudbm/binding/__init__.py` import 并 re-export `ModelBuilder` / `TemplateBuilder`
* [x] `ModelBuilder.clock()` 支持一个或多个 clock 名称
* [x] `ModelBuilder.chan()` 支持一个或多个 channel 名称
* [x] `ModelBuilder.template()` 能返回模板 builder
* [x] `TemplateBuilder.location()` 支持 `initial` / `invariant` / `urgent` / `committed`
* [x] `TemplateBuilder.edge()` 至少支持 `guard` / `when` / `sync` / `update`
* [x] `ModelBuilder.process()` 和 `system()` 能生成最小系统
* [x] `ModelBuilder.query()` 能附加最小 query
* [x] `build()` 产出 public `ModelDocument`
* [x] 所有新增 public API 补齐 pydoc 和 `Example::`
* [x] 所有测试只通过 public API 编写
* [x] 当前 phase 范围内 public coverage 拉到最高

本 phase 单元测试要求：

* [x] 最小单模板模型的 `to_xta()` 全量断言
* [x] 最小单模板模型的 `to_ta()` 全量断言
* [x] `dump()` / `dump_xta()` / `dump_ta()` round-trip 断言
* [x] `query()` 注入后的完整文本断言
* [x] builder 输出再通过 `load_xml()` / `loads_xta()` 重新加载的等价性断言
* [x] `TextAligner` 用于所有多行文本精确比较

### Phase 2：Python 语义糖与结构校验

目标：

- 把 builder 从“能用”推进到“真顺手”

本 phase 范围：

- `send=`
- `recv=`
- `reset={...}`
- `integer()`
- `const integer`
- builder 侧结构校验
- 上下文写法和 `.end()` 两种模板退出方式都稳定

建议交付文件：

- `pyudbm/binding/utap_builder.py`
- `docs/source/api_doc/binding/utap_builder.rst`
- `test/binding/test_utap_builder_phase2.py`

本 phase checklist：

* [x] `TemplateBuilder.edge()` 支持 `send=` 语义糖
* [x] `TemplateBuilder.edge()` 支持 `recv=` 语义糖
* [x] `TemplateBuilder.edge()` 支持 `reset={name: value}` 语义糖
* [x] `ModelBuilder.integer()` 支持常见整数声明
* [x] `ModelBuilder.integer(..., const=True)` 支持常见常量整数声明
* [x] builder 对重复模板名给出清晰错误
* [x] builder 对重复 location 名给出清晰错误
* [x] builder 对多个 `initial=True` 给出清晰错误
* [x] builder 对未知 edge source/target 给出清晰错误
* [x] builder 对未知 process template 给出清晰错误
* [x] builder 对 `system()` 中未知 process 给出清晰错误
* [x] 所有新增 public API 补齐 pydoc 和 `Example::`
* [x] 所有测试只通过 public API 编写
* [x] 当前 phase 范围内 public coverage 拉到最高

本 phase 单元测试要求：

* [x] `send=` / `recv=` 映射到同步文本的全量断言
* [x] `reset={...}` 映射到 update 文本的全量断言
* [x] `integer()` 和常量整数声明的文本快照断言
* [x] 所有结构错误路径都有 public API 层测试
* [x] 错误消息断言必须贴近用户输入语义

### Phase 3：spec 层正式公开

目标：

- 让 builder 不仅适合人手写，也适合程序生成和快照驱动

本 phase 范围：

- `ModelSpec`
- `TemplateSpec`
- `LocationSpec`
- `EdgeSpec`
- `QuerySpec`
- `build_model(spec)`
- builder 到 spec 的公开转换

建议交付文件：

- `pyudbm/binding/utap_builder.py`
- `pyudbm/binding/__init__.py`
- `docs/source/api_doc/binding/utap_builder.rst`
- `test/binding/test_utap_builder_phase3.py`

本 phase checklist：

* [x] 新增 public `ModelSpec`
* [x] 新增 public `TemplateSpec`
* [x] 新增 public `LocationSpec`
* [x] 新增 public `EdgeSpec`
* [x] 新增 public `QuerySpec`
* [x] 新增 public `build_model(spec)`
* [x] spec 主实现继续放在 `pyudbm/binding/utap_builder.py`
* [x] `pyudbm/binding/__init__.py` import 并 re-export spec 相关 public API
* [x] builder 能导出 public spec
* [x] spec 构建结果与链式 builder 构建结果语义等价
* [x] 所有新增 public API 补齐 pydoc 和 `Example::`
* [x] 所有测试只通过 public API 编写
* [x] 当前 phase 范围内 public coverage 拉到最高

本 phase 单元测试要求：

* [x] 用 spec 构建最小模型的 `to_xta()` 全量断言
* [x] 同一模型用 builder 构建和用 spec 构建的等价性断言
* [x] `build_model(spec)` 的错误路径测试
* [x] spec 默认值和边界值测试

### Phase 4：导入后编辑与 patch 工作流

目标：

- 让 builder 从“纯作者层”继续扩展到“导入后可轻量编辑”

本 phase 范围：

- `ModelBuilder.from_document(document)`
- 常见 patch helper
- modify/delete patch helper
- import-edit-export 工作流

建议交付文件：

- `pyudbm/binding/utap_builder.py`
- `docs/source/api_doc/binding/utap_builder.rst`
- `test/binding/test_utap_builder_phase4.py`

本 phase checklist：

* [x] 新增 public `ModelBuilder.from_document(document)`
* [x] 能从现有 `ModelDocument` 重建 builder
* [x] 能在导入模型后继续追加 query
* [x] 能在导入模型后追加 process 或 patch system
* [x] 能在导入模型后补充 template 内结构
* [x] builder 提供常见 modify/delete public patch helper
* [x] 导入后的 query/process/template 结构支持修改与删除
* [x] 所有新增 public API 补齐 pydoc 和 `Example::`
* [x] 所有测试只通过 public API 编写
* [x] 当前 phase 范围内 public coverage 拉到最高

本 phase 单元测试要求：

* [x] `load_xml()` -> `ModelBuilder.from_document()` -> `build()` round-trip 测试
* [x] 导入后追加 query 的完整文本快照测试
* [x] 导入后 patch system/process 的语义等价测试
* [x] 导入后 patch 模板结构的错误路径测试
* [x] 导入后 modify 操作的完整文本快照测试
* [x] 导入后 delete 操作的完整文本快照测试
* [x] modify/delete 错误路径测试

### Phase 5：自动化友好的语义编辑与验证工作流补面

目标：

- 让 builder 不只是“能手写小模型”，而是真正适合自动化流水线、脚本批量改模和 LLM 反复迭代 patch

本 phase 范围：

- edge / query 的非 index 优先 patch API
- list / inspect / enumerate 这类 public helper，作为无法完全脱离 index 时的兜底方案
- import-edit-export 路径中更稳定的对象寻址策略
- 优先基于 public `ModelDocument` snapshot 做导入重建，XML 只作为公开快照暂缺信息时的补充来源
- 把当前“验证流程高价值、但 builder 还未覆盖”的语义继续接进 builder
- builder 产物在 `to_xta()` / `to_ta()` 路径上的稳定性补强

本 phase 明确优先解决的问题：

- 现在 `update_edge(0, ...)` / `remove_edge(0)` 这类接口，对脚本和 LLM 来说不够稳，因为前面一处插入或删除就会导致后续 index 漂移
- 因此后续 patch API 应坚持“语义定位优先，index 兜底”，也就是：
  - 优先支持按名称、按选择器、按稳定 key、或按 public handle 定位
  - 当场景复杂到必须依赖 index 时，builder 必须公开提供 list / inspect helper，把当前对象列表及其 index 明确暴露出来，确保调用方始终有可操作的最后兜底路径
- 这个要求不是单纯为了易用性，而是为了后续把 builder 纳入自动验证流水线时，仍然可以做可重复、可恢复、可审计的 patch 操作

本 phase 明确优先补的验证相关语义：

- branchpoint
- branchpoint transition
- edge `select`
- edge `probability`
- controllable / uncontrollable edge
- location exp rate / cost rate
- `before_update`
- `after_update`
- channel priority

本 phase 明确不作为阻塞项的内容：

- GUI 坐标
- nail
- 纯编辑器布局 round-trip
- 只影响可视化、不影响验证语义的展示型 metadata

建议交付文件：

- `pyudbm/binding/utap_builder.py`
- `pyudbm/binding/utap.py`
- `docs/source/api_doc/binding/utap_builder.rst`
- `test/binding/test_utap_builder_phase5.py`

本 phase checklist：

* [ ] edge / query 的更新与删除不再只依赖裸 index 作为主入口
* [ ] builder 提供可公开调用的 list / inspect helper，允许调用方获取当前 templates / processes / queries / locations / edges 及其 index
* [ ] 上述 list / inspect 结果除 index 外，还暴露足够的公开语义字段，便于脚本和 LLM 做稳定位
* [ ] 当引入稳定 key 或其他 builder 内锚点时，明确其与序列化 / 导入重建之间的边界，不做含糊行为
* [ ] `from_document()` / import-edit 路径优先基于 public `ModelDocument` snapshot 重建，而不是继续以 XML 字符串解析作为主路径
* [ ] builder 接入 branchpoint 与 branchpoint transition
* [ ] builder 接入 edge `select` / `probability`
* [ ] builder 接入 controllable / uncontrollable edge
* [ ] builder 接入 location exp rate / cost rate
* [ ] builder 接入 `before_update` / `after_update`
* [ ] builder 接入 channel priority
* [ ] builder 产出的 `ModelDocument` 在多模板和较复杂模型下，`to_xta()` / `to_ta()` 保持稳定
* [ ] 对仍未支持的高阶特性，builder 给出清晰、面向用户语义的错误，而不是模糊 parser 失败
* [ ] 所有新增 public API 补齐 pydoc 和 `Example::`
* [ ] 所有测试只通过 public API 编写
* [ ] 当前 phase 范围内 public coverage 拉到最高

本 phase 单元测试要求：

* [ ] list / inspect helper 的返回结果做精确结构断言，并覆盖其中的 index 暴露路径
* [ ] 同一个 patch 目标至少覆盖三类定位方式中的两类：语义选择器、稳定 key / handle、index 兜底
* [ ] 对 import 后再 patch 的复杂模型做完整 round-trip 测试
* [ ] 对 branchpoint / select / probability / channel priority / before_update / after_update 至少各补一条 public-only 成功或清晰失败路径测试
* [ ] `to_xta()` / `to_ta()` 继续使用 `text_aligner.assert_equal(...)` 做全量文本断言，不退化为子串断言
* [ ] 不导入 `_utap`，不访问任何 private / protected module / class / function / method / field
* [ ] 在本 phase 允许的前提下，把 public-only 覆盖率拉到当前可达上限

### Phase 6：LLM 友好的稳定寻址、`inspect()` 与可审计 patch API

目标：

- 把 builder 收成真正适合脚本、流水线和 LLM agent 稳定驱动的 patch surface，减少 index 漂移带来的不确定性

本 phase 与上一 phase 的关系：

- Phase 5 已经明确提出“语义定位优先，index 兜底”的原则
- 本 phase 则把这条原则收成明确可实现、可测试、可文档化的 public API 设计

本 phase 范围：

- `ModelBuilder.update_query()` / `remove_query()` 支持 `where=` 语义选择器作为主入口
- `TemplateBuilder.update_edge()` / `remove_edge()` 支持 `where=` 语义选择器作为主入口
- builder 提供 `list_templates()`、`list_processes()`、`list_queries()`、`list_locations()`、`list_edges()` 这类稳定枚举 helper
- builder 提供公开 `inspect()` 快照接口，让调用方一次拿到当前可操作对象的结构化视图
- 保留现有基于裸 `index` 的入口以兼容旧调用，但明确降级为兜底路径
- 统一 0 命中、多命中、歧义命中时的错误语义和候选输出格式

建议公开 API 形状：

```python
builder.update_query(where={"formula": "A[] not deadlock"}, comment="patched")
builder.remove_query(where={"formula": "E<> done", "comment": "obsolete"})

with builder.edit_template("P") as template:
    template.update_edge(where={"source": "Init", "target": "Busy"}, sync="go?")
    template.remove_edge(where={"source": "Init", "target": "Busy", "sync": "go?"})

snapshot = builder.inspect()
```

本 phase 明确约束的选择器行为：

- `query` 选择器默认只做精确匹配，优先支持 `formula`、`comment`、`location`
- `edge` 选择器默认只做精确匹配，优先支持 `source`、`target`、`guard`、`sync`、`update`
- 匹配结果为 0 个时，报清晰错误，不做静默跳过
- 匹配结果多于 1 个时，报歧义错误，并把候选对象的 `index` 与关键语义字段一并暴露出来
- 不做模糊匹配，不做“默认取第一个”，不把隐式猜测塞进 public patch 行为

本 phase 明确约束的 `list_*` / `inspect()` 行为：

- `list_*` 的结果必须显式暴露 `index`
- `list_*` 的结果除 `index` 外，还要暴露足够的公开语义字段，便于脚本和 LLM 做稳定位
- `inspect()` 不是内部调试辅助，而是面向自动化的公开快照接口
- `inspect()` 的返回结构应尽量保持 JSON-friendly，只使用清晰、稳定、可序列化的公开字段
- `inspect()` 应能覆盖 model 级和 template 级当前可操作对象，而不是只给零散局部列表

为什么把 `inspect()` 单列为硬需求：

- 仅有 `list_*` 仍然要求调用方自己拼装上下文
- 对 LLM agent 来说，单次拿到完整结构化快照，比多轮调用多个 list helper 更稳，也更容易进入流水线
- 后续自动 patch 流程可以自然稳定为：`from_document()` / 构模 -> `inspect()` -> 生成 patch -> `build()` -> round-trip 校验

建议交付文件：

- `pyudbm/binding/utap_builder.py`
- `docs/source/api_doc/binding/utap_builder.rst`
- `test/binding/test_utap_builder_phase6.py`

本 phase checklist：

* [ ] `update_query()` / `remove_query()` 支持 `where=` 语义选择器作为主入口
* [ ] `update_edge()` / `remove_edge()` 支持 `where=` 语义选择器作为主入口
* [ ] 现有基于 `index` 的 patch API 继续保留并保持兼容
* [ ] `list_templates()` / `list_processes()` / `list_queries()` / `list_locations()` / `list_edges()` 公开可用
* [ ] 新增公开 `inspect()`，返回当前 builder 的完整结构化快照
* [ ] 歧义错误中明确列出候选对象的 `index` 和关键语义字段，便于调用方恢复
* [ ] 不引入模糊匹配、隐式首项回退或其他不可审计的猜测行为
* [ ] `from_document()` -> `inspect()` -> patch -> `build()` 路径保持稳定
* [ ] 所有新增 public API 补齐 pydoc 和 `Example::`
* [ ] 所有测试只通过 public API 编写
* [ ] 当前 phase 范围内 public coverage 拉到最高

本 phase 单元测试要求：

* [ ] `query` 与 `edge` 至少各覆盖一条语义选择器成功路径
* [ ] `query` 与 `edge` 至少各覆盖一条多命中歧义错误路径
* [ ] `query` 与 `edge` 至少各覆盖一条 `index` 兜底路径，确保兼容旧 API
* [ ] `list_*` 的返回结构做精确断言，并覆盖其中的 `index` 暴露路径
* [ ] `inspect()` 的返回结构做精确断言，覆盖 model 级与 template 级可操作对象
* [ ] 至少补一条 import 后经 `inspect()` 定位再 patch 的完整 round-trip 测试
* [ ] `to_xta()` / `to_ta()` 继续使用 `text_aligner.assert_equal(...)` 做全量文本断言，不退化为子串断言
* [ ] 不导入 `_utap`，不访问任何 private / protected module / class / function / method / field
* [ ] 在本 phase 允许的前提下，把 public-only 覆盖率拉到当前可达上限

### Phase 7：文档收口与 API 一致性整理

目标：

- 在 builder 基本定型后，把 public API、文档和测试口径完全收齐

本 phase 范围：

- 文档整理
- 公开 API 命名复核
- 示例一致性整理
- 交叉测试补齐

建议交付文件：

- `docs/source/api_doc/binding/utap.rst`
- 相关 public 模块的 pydoc
- `test/binding/test_utap_builder_phase7.py`

本 phase checklist：

* [ ] 统一 builder / spec 的命名和参数风格
* [ ] 所有 public API 文档示例都能反映主推荐用法
* [ ] 所有 `Example::` 与真实 public API 保持一致
* [ ] API 文档入口补齐 builder / spec 公开对象
* [ ] 补齐跨 phase 的组合测试
* [ ] 所有测试只通过 public API 编写
* [ ] 当前 phase 范围内 public coverage 拉到最高

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
