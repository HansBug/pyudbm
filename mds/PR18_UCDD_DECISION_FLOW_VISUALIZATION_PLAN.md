# UCDD 判定链路可视化方案

## PR 关联

本方案对应的 GitHub Pull Request：

- PR #18: <https://github.com/HansBug/pyudbm/pull/18>

## 说明

这份文档用于收敛 `pyudbm` 中 UCDD 可视化的后续实施方向，重点不是“把一个图画出来”，而是把下面几件事串成一条可落地的技术链路：

1. 从 `CDD` 对象中稳定提取可视化所需的判定链路数据。
2. 用统一的中间表示同时支持 `Mermaid` 和 `PlantUML` 文本导出。
3. 提供一个适合本地快速查看的轻量预览窗口，而不是要求用户每次都手工复制图代码到外部工具。
4. 让这一套能力与现有 `DBM` / `Federation` 的 matplotlib 可视化思路并存，而不是互相替代。

本文档的目标不是立即提交实现代码，而是先把数据边界、接口分层、导出格式、预览方式、测试策略和阶段计划讲清楚，便于后续连续讨论与迭代。

本文档已经按仓库约定完成 PR 编号回填：

- 首次提交使用不含 PR 编号的临时描述性文件名
- PR 创建后，已将真实 PR 编号回填到文件名前缀
- PR 链接也已回填进本文档，并应与 PR 描述中的文档链接保持双向关联

## 背景

当前仓库已经具备两条与本方案直接相关的基础能力。

第一条是现有 `UCDD` Python 封装已经不只是一个空薄层，而是提供了足够多的高层语义对象：

- `pyudbm/binding/ucdd.py` 已经提供 `CDDContext`、`CDD`、`CDDBool`、`CDDClock`、`CDDExtraction`、`BDDTraceSet`
- `CDDContext.all_level_info()` 可以拿到当前 runtime 的 level 描述
- `CDD.bdd_traces()` 可以导出布尔轨迹
- `CDD.extract_dbm()`、`CDD.extract_bdd()`、`CDD.extract_bdd_and_dbm()` 可以从混合 CDD 中拆出局部信息
- `CDD.transition()`、`CDD.transition_back()`、`CDD.transition_back_past()` 已经表达了“判定链路”最终要服务的典型 symbolic workflow

第二条是现有 `DBM` / `Federation` 可视化已经建立了一个很重要的实现基线：

- `pyudbm/binding/visual.py` 先做纯 Python 几何快照，再做 matplotlib 渲染
- matplotlib 被保持为可选依赖，而不是核心运行时硬依赖
- 对象方法入口放在高层 binding 上，而不是把可视化语义塞进 native 子模块

这两点意味着：UCDD 可视化不应该直接跳进 GUI 细节，而应先做一层“可视化中间表示”，再在此基础上导出图代码与本地预览。

## 为什么 UCDD 可视化不能照搬 UDBM 的 matplotlib 方案

`DBM` / `Federation` 的 matplotlib 可视化，本质上是在画几何对象：

- 一维区间
- 二维多边形
- 三维多面体

而 `CDD` 的主要问题不是“区域边界是什么”，而是“一个 symbolic 状态是如何沿着布尔判断和 clock-difference 判断被逐层分解的”。

因此，UCDD 可视化的核心对象不是几何区域，而是判定流程：

- 当前节点判断的是布尔变量还是 clock difference
- 当前分支对应什么条件
- 某个分支继续进入哪个子节点
- 某条路径何时收敛到 `true` / `false`
- 在混合场景下，某条路径对应的布尔守卫和 DBM 片段如何组合

这更接近：

- 流程图
- 活动图
- 判定树
- DAG 结构图

而不是 matplotlib 最擅长的欧氏几何作图。

所以本方案的结论是：

- UCDD 的主可视化方向应当是“判定链路图”
- `Mermaid` 与 `PlantUML` 是更贴合的文本导出目标
- matplotlib 最多承担“嵌入宿主窗口”和“与现有小窗体验衔接”的角色，不应成为 UCDD 图本身的语义承载层

## 当前代码基线下已经能拿到什么

按仓库当前状态，可以直接复用的数据主要有三类。

### 一、运行时 level 元数据

`CDDContext.level_info()` 与 `CDDContext.all_level_info()` 已经能拿到：

- `level`
- `type`
- `clock1`
- `clock2`
- `diff`

这足以建立“这个判定节点代表哪个布尔层或哪个 clock-difference 层”的静态标注能力。

### 二、布尔路径层面的抽取结果

`CDD.bdd_traces()` 已经能导出：

- 一条条 BDD 路径
- 每条路径上的布尔变量赋值

这对下面两类可视化很有用：

- 纯 BDD 视图
- 混合 CDD 的布尔守卫摘要视图

但它不够解决“完整判定链路图”的问题，因为它没有暴露：

- 中间节点
- 节点间边
- clock-difference 节点的多分支区间信息
- DAG 共享子结构

### 三、按路径抽取 DBM 片段

`CDD.extract_bdd_and_dbm()` 已经能拿到：

- 一段抽取后的布尔守卫 `bdd_part`
- 一个抽取后的 `DBM`
- 剩余图 `remainder`

这为“从 CDD 中逐步枚举出 guarded-DBM 片段”提供了很强的基础。

如果后续要做“路径列表视图”或“分支摘要表格”，这条链路非常有价值。

但它仍然不是完整图结构导出，因为它拿到的是抽取结果，不是完整 DAG 的节点与边。

## 当前还缺什么

如果目标是展示“完整判定链路”，当前 Python 层还缺一层显式的图结构只读导出能力。

也就是说，除了已有的：

- level metadata
- BDD trace arrays
- extraction helpers

还需要一种新的 graph snapshot API，用来导出：

- 节点列表
- 节点类型
- 节点对应的 level
- 终端节点类型
- 边列表
- 边条件
- negation / mask / complemented-edge 一类语义
- CDD interval 边的上下界与开闭性
- DAG 共享节点关系

这是后续整个方案的第一关键前提。

## 上游 UCDD 已有能力对本方案的启发

虽然当前 Python 绑定还没有公开完整图结构，但上游 `UCDD` 本身并不是完全没有这类信息。

从仓库当前 vendored 的 `UCDD/` 代码可以看到：

- `cdd_fprintdot(...)`
- `cdd_printdot(...)`
- `cdd_fprint_code(...)`
- `cdd_fprint_graph(...)`
- `cdd_get_levelinfo(...)`

这说明上游内部已经具备遍历图结构并输出结构化文本的能力。

这对本方案有两个直接启发：

1. 完整判定图的遍历在 native 层是可做的，不是空想。
2. 第一版 Python 绑定不一定要一开始就暴露非常底层的 node 指针细节，但至少可以在仓库自己的 `_ucdd.cpp` 薄层中增加一个“只读快照导出”接口。

需要强调的是：

- 本仓库不能直接修改 `UCDD/` 子模块源码
- 但可以在本仓库自有的 `pyudbm/binding/_ucdd.cpp` 里新增对上游公开 API 的包装

因此，本方案推荐的做法不是去 patch `UCDD/`，而是：

- 尽量基于上游已经公开的遍历与打印能力做桥接
- 如果上游公开 API 还不够，就在本仓库薄 binding 层里补只读转换，而不是改 submodule

## 总体设计原则

### 1. 先做结构化数据，再做渲染

公开 API 不应一开始就只提供：

- `to_mermaid()`
- `to_plantuml()`

否则后续所有测试、扩展与本地预览都会被字符串格式绑死。

更合理的分层是：

1. `CDD` -> 结构化 graph snapshot
2. graph snapshot -> `Mermaid` / `PlantUML`
3. graph snapshot 或导出文本 -> 本地 preview

### 2. 区分“原始图结构”与“解释后的判定链路”

UCDD 原生 DAG 更接近决策图内部结构，而用户想看的常常是“判定链路”。

这两者不完全相同：

- 原始图结构强调节点共享、底层边和终端
- 判定链路视图强调可读性、条件文字、顺序感和局部摘要

因此建议同时保留两层表示：

- `CDDGraphSnapshot`：忠实反映原始 DAG
- `CDDDecisionFlow`：面向展示的解释后流程图表示

第一版也可以只先落 `CDDGraphSnapshot`，由导出器在内部生成更易读的 flow 表达。

### 3. 对 mixed CDD 要优先可解释性，而不是图形学炫技

第一版不追求复杂的自动布局引擎，也不追求在本地窗口里做高度交互式节点拖拽。

首要目标应是：

- 条件文本正确
- 节点类型清楚
- 终端语义清楚
- 布尔与 clock 分支都可追踪
- 支持导出标准文本格式，便于用户粘贴到文档、Issue、PR、笔记中

### 4. 保持依赖最小化

像 `DBM` matplotlib 方案一样，UCDD 可视化也应尽量做到：

- 核心数据提取无额外 GUI 依赖
- 文本导出无重量级图形依赖
- 本地快速预览走可选依赖路线

## 拟议的数据模型

建议在 Python 层新增一个独立模块，例如：

- `pyudbm/binding/ucdd_visual.py`

这个模块不负责 native 运算，只负责：

- graph snapshot 的高层包装
- 文本导出
- 预览入口

### 一、原始快照对象

建议定义如下公共只读对象：

- `CDDGraphNode`
- `CDDGraphEdge`
- `CDDGraphSnapshot`

建议字段大致如下。

`CDDGraphNode`：

- `id`
- `kind`
  - `terminal_true`
  - `terminal_false`
  - `bdd`
  - `cdd`
- `level`
- `label`
- `bool_name`
- `clock1`
- `clock2`
- `diff`
- `is_negated_view`

`CDDGraphEdge`：

- `source`
- `target`
- `kind`
  - `bdd_low`
  - `bdd_high`
  - `cdd_interval`
- `label`
- `lower`
- `upper`
- `lower_strict`
- `upper_strict`
- `is_complemented`

`CDDGraphSnapshot`：

- `context`
- `root_id`
- `nodes`
- `edges`
- `level_info`
- `node_count`
- `terminal_ids`

### 二、面向展示的流程对象

如果后续证明原始 snapshot 直接导出图代码过于底层，再补一层：

- `CDDDecisionNode`
- `CDDDecisionBranch`
- `CDDDecisionFlow`

这层可以负责：

- 把底层 negated-edge 语义转成用户可读条件
- 把 CDD interval 边格式化成 `x - y < 3`、`2 <= x - y < 5` 一类文本
- 给 mixed CDD 生成更像“活动图/流程图”的结构

## Native 与 Python 的分层建议

### 一、native 薄层职责

建议在本仓库自有的 `pyudbm/binding/_ucdd.cpp` 中增加只读导出接口，职责仅限于：

- 遍历 `cdd` 图
- 生成稳定节点编号
- 把节点和边快照转成 Python 容器
- 保留足够的 level / interval / terminal 信息

不建议在 native 层直接：

- 拼接 Mermaid 文本
- 拼接 PlantUML 文本
- 处理 UI

因为这些都属于高层可变策略，放 Python 层更适合演进。

### 二、Python 高层职责

建议在 `pyudbm/binding/ucdd_visual.py` 里负责：

- 快照对象包装
- 标签格式化
- `Mermaid` 导出
- `PlantUML` 导出
- 轻量 preview 调度

### 三、对象方法入口

为了贴近现有高层 API，可以考虑在 `CDD` 上增加懒导入入口，例如：

```python
cdd.visualize(...)
cdd.to_mermaid(...)
cdd.to_plantuml(...)
cdd.graph_snapshot(...)
```

但第一版更稳妥的顺序是先落模块级函数，再决定是否绑定实例方法：

```python
from pyudbm.binding.ucdd_visual import (
    extract_cdd_graph,
    cdd_to_mermaid,
    cdd_to_plantuml,
    preview_cdd,
)
```

等接口稳定后，再在 `CDD` 上加薄方法转发，避免过早承诺最终 API 形态。

## Mermaid 导出方案

`Mermaid` 适合作为第一优先导出目标，原因是：

- 文本短
- 易嵌入 Markdown
- 适合放进 GitHub 讨论和设计文档
- 对流程图语义支持直接

但要注意 `Mermaid` 不是 DAG 细节表达能力最强的格式，因此建议支持两种模式。

### 一、结构图模式

使用 `flowchart TD` 或 `flowchart LR`：

- 每个 node 对应一个图节点
- BDD 节点显示布尔变量名
- CDD 节点显示 clock-difference 及其 level
- 边标签显示 `true` / `false` 或区间条件
- 终端显示 `TRUE` / `FALSE`

这适合忠实展示实际 DAG。

### 二、判定链路模式

把共享子结构按可读性适度展开，生成更接近活动图的导出：

- 用“判断”节点表达分支
- 用“终止”节点表达 `accept` / `reject`
- 对一条路径的条件做更自然的文本呈现

这会牺牲一定 DAG 压缩度，但更适合人看。

建议：

- `to_mermaid(mode="graph")`
- `to_mermaid(mode="flow")`

第一版至少先实现 `graph` 模式。

## PlantUML 导出方案

`PlantUML` 的价值主要在于：

- 活动图表达成熟
- 复杂流程图的排版控制比 `Mermaid` 更强
- 很适合后续放进更正式的设计文档和教程

这里建议也支持双模式：

- `diagram="activity"`：更接近你提出的“活动图式判定链路”
- `diagram="flow"` 或 `diagram="state"`：保留对原始结构的较忠实表示

不过第一版不建议强行追求所有 PlantUML 方言。

更稳妥的策略是：

- 第一版统一用一个流程图式模板
- 把布尔和 clock 判断都翻译成 decision 节点
- 路径终端翻译为 `stop` 或命名终端节点

## 本地快速预览方案

这是本方案里最容易被实现细节带偏的部分，所以需要先定边界。

### 一、不要把 matplotlib 当成 UCDD 图语义引擎

matplotlib 对 `DBM` 几何可视化很合适，但对流程图布局和渲染不是它的强项。

因此，“把 Mermaid 集成到 matplotlib 里”可以作为加分方向，但不应成为主路线。

更实际的主路线应是：

- 生成 `Mermaid` 或 `PlantUML` 文本
- 用一个轻量本地预览容器直接渲染它

### 二、优先考虑原生小窗 + 内嵌 WebView

推荐优先级如下：

1. `tkinter` + 内嵌 HTML 预览能力
2. 如 `tkinter` 不能稳定承载内嵌 Web 内容，则考虑更适合嵌入浏览内核的轻量原生 UI
3. 无论具体宿主选型如何，核心都应保持“渲染器与宿主分离”

更具体地说，预览功能应拆成：

- Python 端负责生成图文本和一段固定 HTML 壳
- 宿主窗口负责承载这段 HTML
- HTML 中的少量 JS 负责把 `Mermaid` 初始化并渲染到 DOM

这样即使将来：

- 从 `tkinter` 切换到别的宿主
- 增加导出 SVG
- 增加保存 HTML 快照

也不会影响上层 graph snapshot 和导出逻辑。

### 三、建议先支持 HTML preview，再考虑 matplotlib 桥接

推荐第一版快速预览接口：

```python
preview_cdd(cdd, backend="mermaid", mode="graph")
preview_cdd(cdd, backend="plantuml", mode="flow")
```

但实际第一版最好先只落：

- `backend="mermaid"`
- 生成临时 HTML
- 用本地窗口或浏览器打开

PlantUML 的本地实时渲染链更复杂，可以晚一阶段。

### 四、matplotlib 集成的现实位置

如果后续确实要做“像 `dbm.plot()` 那样的体验”，更现实的理解应是：

- matplotlib figure 负责作为宿主容器之一
- 真正的图仍然是 HTML / SVG 渲染结果

例如后续可探索：

- 把 Mermaid 渲染成 SVG，再嵌到 matplotlib image/artist 中
- 或者只提供“从 `CDD` 导出 SVG 字符串”后由用户自行嵌入

但这不应影响第一版路线，也不应阻塞整体设计。

## 推荐的模块布局

建议按下面的层次落代码。

### 第一层：native 薄绑定

- `pyudbm/binding/_ucdd.cpp`

建议新增：

- `_NativeCDD.graph_snapshot()`

返回值可以是简单 Python dict/list，也可以是轻量 native helper 对象。

### 第二层：Python 可视化核心

- `pyudbm/binding/ucdd_visual.py`

建议包含：

- graph snapshot dataclass
- 标签格式化器
- `cdd_to_mermaid(...)`
- `cdd_to_plantuml(...)`
- `preview_cdd(...)`

### 第三层：高层入口

- `pyudbm/binding/ucdd.py`
- `pyudbm/binding/__init__.py`
- `pyudbm/__init__.py`

其中：

- `pyudbm.binding` 可以重导出 UCDD 可视化入口
- 包根 `pyudbm/__init__.py` 是否重导出，可放到后续再定，避免初期暴露过宽

## 阶段计划

### 阶段 1：把 graph snapshot 打通

目标：

- 能从 `CDD` 提取完整只读图快照
- 单测覆盖纯 BDD、纯 CDD、mixed CDD
- 明确节点类型、边标签、终端和 level 映射

产出：

- `_NativeCDD.graph_snapshot()`
- Python 层 `CDDGraphSnapshot`
- 面向 snapshot 的测试

这是整个工作的关键里程碑；没有这一层，后面的导出与预览都会变成拼凑。

### 阶段 2：先导出 Mermaid

目标：

- 基于 snapshot 导出稳定、可测试的 Mermaid 文本
- 至少支持 `graph` 模式
- 保证标签中能正确表达布尔分支和区间分支

产出：

- `cdd_to_mermaid(...)`
- 文本快照测试

### 阶段 3：补 PlantUML

目标：

- 生成更接近活动图的可读流程
- 允许把 mixed CDD 的判定链路放进更正式的设计文档

产出：

- `cdd_to_plantuml(...)`
- 针对活动图文本的测试

### 阶段 4：本地快速预览

目标：

- 用户一行调用即可看到图
- 不要求外部手工粘贴
- 保持核心逻辑与宿主窗口分离

产出：

- `preview_cdd(...)`
- HTML 模板
- 内嵌少量 JS 的 Mermaid preview

### 阶段 5：与现有可视化体验对齐

目标：

- 评估是否给 `CDD` 增加实例方法
- 评估是否提供 SVG 导出
- 评估是否需要与 matplotlib 小窗体验进一步统一

这阶段不应阻塞前面四阶段。

## API 方向建议

第一版建议控制公开面，不要一次暴露过多入口。

推荐优先级：

1. `extract_cdd_graph(cdd)`
2. `cdd_to_mermaid(cdd, mode="graph")`
3. `cdd_to_plantuml(cdd, mode="activity")`
4. `preview_cdd(cdd, backend="mermaid")`

等这些稳定后，再考虑：

- `CDD.graph_snapshot()`
- `CDD.to_mermaid()`
- `CDD.to_plantuml()`
- `CDD.preview()`

## 测试与验证策略

这类功能最容易掉进“肉眼看起来差不多”的陷阱，所以测试应按三层做。

### 一、snapshot 层单测

验证：

- 节点数
- 边数
- root 节点类型
- level 映射
- interval 标签解码
- mixed CDD 的布尔与 clock 层次都正确出现

### 二、导出文本快照测试

验证：

- Mermaid 文本稳定
- PlantUML 文本稳定
- 标签中关键条件未丢失

这里不要求字面永远不可变，但至少要保证结构可预期。

### 三、预览层烟测

验证：

- 能生成 HTML
- 能正确注入 Mermaid 源码
- 在没有 GUI 或没有可选依赖时给出清晰错误

不建议把 GUI 像素级截图比对作为第一版硬要求。

## 风险与主要取舍

### 一、完整 DAG 与活动图可读性之间有张力

原始图结构更忠实，但不一定最好看。

这就是为什么本文档推荐：

- 先做 snapshot
- 再允许多个导出模式

### 二、上游打印接口未必足够直接复用

虽然 `UCDD` 有 `dot` / `graph` / `code` 打印函数，但它们更像：

- 调试输出
- 面向 C 风格回调的文本生成

不一定直接适合作为最终用户 API。

因此它们更适合作为：

- native traversal 的参考
- 第一版桥接的过渡能力
- 测试对照

而不是最终公开接口本身。

### 三、PlantUML 本地渲染链路可能比 Mermaid 更重

所以第一版优先 Mermaid 是工程上更稳的取舍。

### 四、matplotlib 集成不应阻塞整体落地

如果一开始就强求 “Mermaid 嵌 matplotlib 并保持和 `DBM.plot()` 一样顺滑”，很容易把本来清晰的数据导出工作拖进 GUI 细节。

更合理的顺序是：

- 先 snapshot
- 再文本导出
- 再 HTML preview
- 最后再讨论 matplotlib 对接

## 本 PR 之后的直接工作建议

这个 PR 合并后，下一步最应该启动的不是 UI，而是数据抽取层。

建议紧接着做：

1. 盘点 `_ucdd.cpp` 当前能直接桥接哪些图遍历信息。
2. 明确 `graph_snapshot()` 的最小字段集合。
3. 先做纯 Python 层 dataclass 和文本导出接口骨架。
4. 用 3 组最小示例建立测试样本：
   - 纯 BDD
   - 纯 clock CDD
   - mixed bool/clock CDD

## 结论

UCDD 可视化应当被理解为“判定链路可视化”而不是“几何区域可视化”。

因此最合理的路线不是照搬 `DBM` 的 matplotlib 方案，而是建立：

- `CDD` 图结构快照
- `Mermaid` / `PlantUML` 文本导出
- 基于 HTML 的本地快速预览

其中：

- graph snapshot 是技术前提
- Mermaid 是第一优先导出目标
- PlantUML 活动图是增强方向
- 原生小窗预览是体验层
- matplotlib 集成是后续可选扩展，而不是第一阶段阻塞项

这个方向既贴合 `UCDD` 的判定图本质，也与 `pyudbm` 当前“先做 Python 高层抽象，再做可选渲染”的实现风格一致。
