# DBM 与 Federation 的 Matplotlib 可视化实施方案

## PR 关联

本方案对应的 GitHub Pull Request：

- PR #4: <https://github.com/HansBug/pyudbm/pull/4>
- PR #6: <https://github.com/HansBug/pyudbm/pull/6>

## 目的

这份文档用于把当前围绕 `DBM` / `Federation` 可视化的讨论，收敛成一份可执行的 `pyudbm` 实施方案。

这份文档的目标不是直接实现功能，而是先明确下面几个问题：

1. 面向用户的 API 应该长什么样。
2. 内部几何提取流水线应该怎么分层。
3. 开区间、闭区间与无穷区域应该如何精确表达。
4. matplotlib 的依赖和打包策略应该怎么处理。
5. 功能应该如何分阶段落地，以及测试怎么设计。

本方案建立在当前仓库状态之上：

- 高层 Python API 位于 `pyudbm/binding/udbm.py`
- `Federation.to_dbm_list()` 可以导出不可变的 `DBM` 快照
- `DBM` 已经提供 `raw()`、`bound()`、`is_strict()`、`is_infinity()` 和 `to_matrix()` 等接口

这点很重要，因为可视化应当建立在现有包装层之上，而不是额外再发明一套新的语义表示。

## 当前技术基线

现有 Python 层已经暴露出足够的信息，可以在不碰 native 子模块的前提下，恢复出精确的 zone 几何形状：

- `Federation.to_dbm_list()` 可以导出脱离原联邦生命周期的 `DBM` 快照。
- `DBM.clock_names` 给出了矩阵头部。
- `DBM.bound(i, j)` 可以解码 DBM 上界。
- `DBM.is_strict(i, j)` 可以判断边界是否严格。
- `DBM.is_infinity(i, j)` 可以判断边界是否无穷。
- `DBM.to_string(full=True)` 已经表明 Python 层拿到的是闭包后的 DBM，而不只是语法层面的原始约束。

因此，这项功能可以完全实现在 `pyudbm/` 和 `test/` 这些 wrapper 所属目录内，不需要修改 `UDBM/` 或 `UUtils/`。

## 范围

### 范围内

- 为 `DBM` 和 `Federation` 提供基于 matplotlib 的绘图支持
- 仅支持 `1D`、`2D` 和 `3D`
- 显式正确处理：
  - 闭边界
  - 开边界
  - 有界区域
  - 无界区域
  - 点、线段、射线、面、空集等退化结果
- matplotlib 作为可选依赖，而不是正常安装路径的强依赖
- 与 matplotlib 现有工作流兼容，支持 `ax` 注入和 artist 级别的返回值

### 范围外

- 维度高于 3 的可视化
- 从高维 zone 自动投影到低维
- 交互式 GUI 工具
- 动画 API
- 非 matplotlib 后端
- 修改 UDBM 语义，或顺手引入新的符号操作

对于任何用户时钟维度不在 `1..3` 之间的 `DBM` 或 `Federation`，绘图 API 应该直接抛出清晰异常，而不是猜测该怎么画。

## 设计原则

### 1. 使用精确几何，而不是栅格近似

可视化流水线应当从 DBM 约束恢复半空间，并计算精确裁剪后的几何对象。

实现上不应依赖：

- 稠密网格采样
- 图像 mask
- 基于 membership 布尔值的轮廓重建

这些方法会模糊开闭边界的差异，对细长或退化区域表现不稳定，也很难正确表达无穷区域。

### 2. 将几何提取与渲染分层

实现应拆成两层：

- 几何层：
  - 把 `DBM` 或 `Federation` 转成内部几何对象
  - 核心数据转换逻辑不依赖 matplotlib
- 渲染层：
  - 把几何对象转成 matplotlib artists
  - 负责样式、坐标轴集成、图例和绘制顺序

这样做的好处是：

- 几何逻辑更容易单测
- 不会把核心语义代码绑死在 matplotlib 细节上

### 3. 保持现有 UDBM 语义

绘图层必须反映当前 `DBM` 或 `Federation` 的真实符号语义。

不能悄悄做这些事：

- 自动把 federation 凸化
- 在调用方没要求的情况下偷偷 reduce
- 把开边界当成闭边界
- 对 infinity 做截断但不在图上明显标识

### 4. 贴合正常 matplotlib 用法

绘图 API 应尽量像常规 matplotlib helper：

- 能接收已有的 `ax`
- 只有在必要时才新建 figure / axes
- 返回可继续操作的 artists 或 artist container
- 允许通过熟悉的关键字参数自定义样式
- 不调用 `plt.show()`

## 拟议的公开 API

### 模块布局

建议不要单独再开一个新的 `pyudbm.plotting` 命名空间，而是把可视化实现放到现有 binding 层旁边，形成：

- `pyudbm/binding/visual.py`

这样做的理由是：

- 当前 `DBM` 和 `Federation` 本来就定义在 `pyudbm/binding/udbm.py`
- 可视化语义本质上就是这些高层 binding 对象的扩展能力
- 从代码组织上，`binding/visual.py` 比独立 plotting 包更贴近现有 API 层次
- 后续给主要类加便捷方法时，也更自然

这里仍然要避免在模块顶层直接互相 import 导致循环依赖。

建议结构是：

- `pyudbm/binding/visual.py`
  - 放公共绘图入口
  - 放几何提取和 matplotlib 渲染逻辑
- `pyudbm/binding/udbm.py`
  - 在主要类上增加薄薄的一层实例方法
  - 方法内部再懒导入 `visual.py` 中的函数

也就是说，推荐的调用链是：

- 用户直接调对象方法，如 `dbm.plot(...)`、`fed.plot(...)`
- 对象方法内部再 `from .visual import ...`
- 不在 `udbm.py` 模块顶层预先导入 `visual.py`

这样既方便用，也能避免循环 import。

### 主要入口

建议 `visual.py` 提供模块级函数，同时由主要类转发调用。

建议的第一版模块级函数签名：

```python
def plot_dbm(
    dbm,
    ax=None,
    *,
    limits=None,
    strict_epsilon=None,
    show_unbounded=True,
    annotate=False,
    baseline=0.0,
    facecolor=None,
    edgecolor=None,
    alpha=None,
    linewidth=None,
    linestyle=None,
    label=None,
    zorder=None,
):
    ...


def plot_federation(
    federation,
    ax=None,
    *,
    limits=None,
    strict_epsilon=None,
    show_unbounded=True,
    annotate=False,
    baseline=0.0,
    color_mode="shared",
    facecolor=None,
    edgecolor=None,
    alpha=None,
    linewidth=None,
    linestyle=None,
    label=None,
    zorder=None,
):
    ...
```

然后在主要类上增加对象方法，至少包括：

```python
DBM.plot(...)
Federation.plot(...)
```

如果后面认为 `Context` 上也需要便捷入口，可以再考虑：

```python
Context.plot(...)
```

但这不应作为第一版硬要求，第一版核心目标仍是 `DBM` 和 `Federation`。

这些对象方法不应在类定义时绑定外部模块对象，而应在方法体内部再导入 `visual.py` 中的函数。例如：

```python
def plot(self, ax=None, **kwargs):
    from .visual import plot_dbm
    return plot_dbm(self, ax=ax, **kwargs)
```

或 federation 对应版本：

```python
def plot(self, ax=None, **kwargs):
    from .visual import plot_federation
    return plot_federation(self, ax=ax, **kwargs)
```

推荐对象方法与模块级函数保持一致的参数面，也就是：

```python
DBM.plot(
    self,
    ax=None,
    *,
    limits=None,
    strict_epsilon=None,
    show_unbounded=True,
    annotate=False,
    baseline=0.0,
    facecolor=None,
    edgecolor=None,
    alpha=None,
    linewidth=None,
    linestyle=None,
    label=None,
    zorder=None,
)

Federation.plot(
    self,
    ax=None,
    *,
    limits=None,
    strict_epsilon=None,
    show_unbounded=True,
    annotate=False,
    baseline=0.0,
    color_mode="shared",
    facecolor=None,
    edgecolor=None,
    alpha=None,
    linewidth=None,
    linestyle=None,
    label=None,
    zorder=None,
)
```

这样可以同时满足两个目标：

- 使用方式足够自然
- 避免在模块初始化阶段产生循环 import

### 参数设计细化

第一版公开 API 应保持克制，但参数语义需要从一开始就说清楚。

#### 1. 目标对象参数

- `dbm`
  - `plot_dbm(...)` 的目标对象
  - 必须是 `DBM`
- `federation`
  - `plot_federation(...)` 的目标对象
  - 必须是 `Federation`

对象方法版本不再显式传入这两个参数，因为目标对象就是 `self`。

#### 2. 坐标轴与可视范围参数

- `ax=None`
  - 可选的 matplotlib axes
  - 如果为 `None`，函数内部负责创建合适的 axes
  - 如果用户传入已有 `ax`，函数只在该 `ax` 上绘图
- `limits=None`
  - 控制可视范围，也决定无界区域如何被裁剪显示
  - 1D 期望形态：`(xmin, xmax)`
  - 2D 期望形态：`((xmin, xmax), (ymin, ymax))`
  - 3D 期望形态：`((xmin, xmax), (ymin, ymax), (zmin, zmax))`
  - 若为 `None`，内部根据有限边界自动推断并加 padding
- `baseline=0.0`
  - 仅对 1D 渲染有意义
  - 决定 1D 区间 / 点 / 射线画在 y 轴的哪条水平线上
  - 便于在一个图里堆多条 1D zone

#### 3. 语义控制参数

- `strict_epsilon=None`
  - 仅用于渲染的内缩量，用来区分开边界与填充内部
  - 只影响 fill 的视觉表达，不应改变真实边界线位置
  - 若为 `None`，应根据当前数据尺度自动估算
- `show_unbounded=True`
  - 是否给无界区域加箭头或其他明确提示
- `annotate=False`
  - 是否附带轻量注释，例如 DBM 编号或文本摘要
- `color_mode="shared"`
  - 仅对 federation 有意义
  - `"shared"` 表示整个 federation 共用一套样式
  - `"per_dbm"` 表示对内部 DBM 循环颜色
  - 由于 2D federation 第一版追求精确边界，`"per_dbm"` 更适合作为调试视图，而不是默认渲染模式

#### 4. 样式参数

- `facecolor=None`
  - 区域填充色
- `edgecolor=None`
  - 边界颜色
- `alpha=None`
  - 整体透明度
- `linewidth=None`
  - 边界线宽
- `linestyle=None`
  - 默认边界线样式
  - 但最终不能覆盖开边界 / 闭边界的语义差异
- `label=None`
  - 用于 matplotlib 图例
- `zorder=None`
  - 控制绘制层级

#### 5. 参数适用性约束

第一版建议明确这些约束：

- `baseline` 只对 1D 有意义
- `color_mode` 只对 federation 有意义
- `limits` 对 1D / 2D / 3D 都有意义
- `strict_epsilon` 对存在 fill 的情况才真正起作用
- `annotate` 不是第一版核心能力，但建议先预留

对于“当前对象维度下没有意义”的参数，第一版更建议“忽略但不报错”，除非该参数会直接导致歧义或错误语义。

### 预期用法示例

至少应支持下面这些典型用法。

#### 1. 最简对象方法调用

```python
from pyudbm import Context

c = Context(["x", "y"])
fed = (c.x <= 5) & (c.y <= 3) & (c.x - c.y < 2)

result = fed.plot()
```

预期语义：

- 自动创建 axes
- 自动推断 `limits`
- 自动选择默认样式
- 返回 `PlotResult`

#### 2. 传入现有 `ax`

```python
import matplotlib.pyplot as plt
from pyudbm import Context

c = Context(["x"])
dbm = (c.x >= 1) & (c.x < 4)

fig, ax = plt.subplots()
result = dbm.plot(ax=ax, edgecolor="red", linewidth=2.0)
```

预期语义：

- 不新建 figure
- 在已有 `ax` 上绘制
- 使用调用方提供的边界样式

#### 3. 明确指定可视范围

```python
from pyudbm.binding.visual import plot_federation

result = plot_federation(
    fed,
    limits=((0, 10), (0, 10)),
    show_unbounded=True,
)
```

预期语义：

- 用给定 render box 裁剪无界区域
- 对被截断的无界方向给出明确提示

#### 4. 调试 federation 内部结构

```python
result = fed.plot(
    color_mode="per_dbm",
    alpha=0.25,
    annotate=True,
)
```

预期语义：

- 用于调试 federation 的内部组成
- 即使 2D federation 默认走精确边界，也应允许保留一定内部调试视图能力

#### 5. 1D baseline 控制

```python
result = dbm.plot(
    baseline=1.5,
    edgecolor="black",
)
```

预期语义：

- 1D 区间画在 `y=1.5` 的水平线上
- 适合同一个图中堆叠多条 1D zone

### 第一版不准备支持的用法

为了避免接口膨胀，第一版应明确不支持这些能力：

- 不支持用户手动指定任意高维投影矩阵
- 不支持 4 维及以上对象自动投影到 2D / 3D
- 不支持一开始就开放大量 marker / hatch / cmap 专用参数
- 不支持把对象方法做成同时隐式创建 figure、保存文件、show 图的一站式大方法
- 不支持引入与 matplotlib 常规工作流不兼容的自定义绘图库抽象

### 第一版刻意暂缓的参数

下面这些参数未来可能有价值，但不建议在第一版就开放：

- `xclock`、`yclock`、`zclock`
  - 一旦开放，就意味着要认真支持轴选择与局部投影语义
  - 第一版在只支持 `1..3` 维的前提下，按 clock 自然顺序映射到坐标轴更稳
- `show_vertices`
  - 适合调试，但不是第一版必需
- `boundary_style_open` / `boundary_style_closed`
  - 未来可能有用，但第一版可以先把语义样式内部固化
- `union_mode`
  - 第一版 1D / 2D federation 的精确并集不应交给用户切换，否则容易引入语义歧义

### 返回值

不要只返回 `ax`。建议返回一个小型 artist container。

推荐形态：

```python
class PlotResult:
    ax: Any
    fills: tuple
    boundaries: tuple
    markers: tuple
    indicators: tuple
```

这样调用方仍然可以按 matplotlib 的正常方式继续后处理。

## 打包与依赖策略

matplotlib 应保持为可选依赖。

### 依赖文件

新增一个可选 requirements 文件：

- `requirements-plot.txt`

第一版内容大概率只需要：

```text
matplotlib
```

当前 `setup.py` 已经会把 `requirements-*.txt` 自动转成 `extras_require`，因此这个文件会自然形成类似下面的安装方式：

```bash
pip install .[plot]
```

### 导入策略

基础导入路径：

```python
import pyudbm
```

不应隐式导入 matplotlib。

只有可视化相关代码路径才应该导入 matplotlib，最好在 `pyudbm/binding/visual.py` 内部，或者绘图函数内部再导入。

同样，`pyudbm/binding/udbm.py` 中新增的对象方法也应只在方法体内部导入 `visual.py`，不要在模块顶部导入。

### 错误信息策略

当 matplotlib 未安装而用户调用绘图功能时，应抛出直接清晰的 `ImportError`，例如：

```text
Matplotlib plotting support is optional. Install pyudbm with the 'plot' extra or install matplotlib manually.
```

## 内部架构

### 几何数据模型

几何层不应到处传裸元组，建议定义小而明确的内部对象。

可选的内部几何类型：

- `Interval1D`
- `Ray1D`
- `Point1D`
- `Polygon2D`
- `Segment2D`
- `Point2D`
- `Polyhedron3D`
- `Face3D`
- `Segment3D`
- `Point3D`
- `EmptyGeometry`

每个几何对象都应携带足够的元信息，以保留渲染语义：

- 坐标
- 每条边界是开还是闭
- 某条边或某个面是否仅仅来自 render box 裁剪
- 某条边界是否真的是 zone 的数学边界

这点很关键，因为同样是一条画出来的线段，它可能表示完全不同的东西：

- 真正的闭边界
- 真正的开边界
- 仅仅因为显示裁剪才出现的边界

### 几何流水线总览

建议流程如下：

1. 归一化输入：
   - `DBM` 作为一个凸 zone
   - `Federation` 通过 `to_dbm_list()` 转成 DBM 列表
2. 根据 context 时钟数确定绘图维度
3. 确定 render box
4. 把 DBM 矩阵单元转换成半空间约束
5. 从初始有界形状开始，逐步用有限半空间裁剪
6. 记录 strictness 和 truncation 元信息
7. 把几何对象转换成 matplotlib artists

## 从 DBM 约束到绘图半空间的映射

对于用户时钟为 `x1, ..., xn`、参考时钟为 `x0 = 0` 的 DBM，矩阵单元 `(i, j)` 表示：

`xi - xj < c` 或 `xi - xj <= c`

如果该值是 infinity，则表示没有这个有限上界。

这可以直接转换成 `R^n` 中的仿射半空间。

例如：

- `(x, 0) <= 5` 对应 `x <= 5`
- `(0, x) <= -2` 对应 `x >= 2`
- `(x, y) < 3` 对应 `x - y < 3`
- `(y, x) <= 7` 对应 `y - x <= 7`

只有有限且非对角线的约束需要参与构造半空间。

因此几何层应遍历所有满足下列条件的 `(i, j)`：

- `i != j`
- bound 有限

并把它们转换成可见坐标空间中的仿射不等式。

第一版不需要依赖 `to_min_dbm()`。

这是有意为之：

- 闭包后的完整 DBM 矩阵已经暴露，使用简单
- packed min-DBM 不太好直接消费
- 对裁剪流水线来说，冗余约束不是正确性问题

## 分维度实施方案

### 1D

#### 语义

1D DBM 表示的是单时钟非负实数轴上的一个凸子集。

典型情况：

- 闭区间：`0 <= x <= 5`
- 开区间：`1 < x < 4`
- 半直线：`x >= 0`、`x > 2`、`x <= 7`
- 单点：`x == 3`
- 空集

#### 几何提取

直接恢复：

- 下界来自 `(0, x)`
- 上界来自 `(x, 0)`

边界是否严格由对应 DBM 单元的 strictness 决定。

如果某一侧是 infinity，则解释成射线。

#### 渲染

推荐风格：

- 区间内部：
  - 水平线段，或很窄的填充带
- 闭端点：
  - 实心点
- 开端点：
  - 空心点
- 无界方向：
  - 向外的箭头

这种画法比纯矩形填充更容易表达开闭边界。

### 2D

#### 语义

2D DBM 表示的是两个时钟构成平面中的一个凸 zone。

该 zone 是有限个半平面的交：

- 来自 `x` 和 `y` 的轴对齐边界
- 来自 `x - y` 与 `y - x` 的对角线边界

#### 几何提取

先构造一个有限 render box：

- 如果 `limits` 显式给出，就直接使用
- 否则根据有限 DBM 边界推断，再加 padding
- 如果某个方向完全无界，则退回到基于原点或已知有限结构的保守默认范围

当前候选区域可以表示为一个凸多边形。

然后按顺序对每个有限 DBM 半平面做裁剪：

- 非严格不等式保留为闭边界
- 严格不等式把对应支撑线标记为开边界

因为区域始终保持凸，所以可以使用半平面版本的 Sutherland-Hodgman 风格裁剪。

#### 退化输出

结果可能退化为：

- 多边形
- 线段
- 点
- 空集

渲染层必须显式处理这些情况，而不是默认假设一定有正面积。

#### 渲染

建议把这些视觉元素拆开画：

- 内部填充
- 真实边界
- 仅由 clip box 引入的伪边界
- 无界提示

推荐语义：

- 真实闭边界：
  - 实线
- 真实开边界：
  - 虚线
- 仅由 clip box 引入的边：
  - 很淡的线，或者干脆不强调
- 无界方向：
  - 在被裁剪边附近加向外箭头，或其他无界指示符

### 3D

#### 语义

3D DBM 表示的是三个时钟构成空间中的一个凸多面体 zone。

#### 几何提取

先从 `R^3` 中的一个有限轴对齐 render box 开始。

再用 DBM 导出的每个有限仿射半空间逐个裁剪这个 box。

内部表示至少需要显式维护：

- 顶点
- 面
- 每个面的元信息

第一版不需要引入通用计算几何依赖，但需要一个针对凸半空间裁剪的稳定实现。

可以按这个思路写：

1. 显式维护各个面
2. 用平面逐个裁剪每个面多边形
3. 收集裁剪过程中形成的交线
4. 当平面真正切开多面体时，重建新的裁剪面

#### 渲染

建议用 `mpl_toolkits.mplot3d.art3d.Poly3DCollection` 画面，用普通 line artists 强化边。

第一版风格可以相对保守：

- 面使用较低 alpha
- 真正的边界线更明显
- 开面使用虚线边界
- 对无界截断使用边缘标识或图例说明

3D 下开边界的视觉语义天然不如 1D / 2D 明显，因此文档和图例需要更明确地解释。

## 开边界与闭边界的语义处理

这是最核心的语义要求，必须显式设计。

### 问题

只要用了 filled patch，视觉上就很容易让人误以为区域是闭的。

例如：

- `x < 5`
- `x - y < 3`

不能在视觉上与：

- `x <= 5`
- `x - y <= 3`

几乎没有区别。

### 拟议规则

同时使用两套机制：

1. 边界样式
2. 严格不等式的渲染内缩

### 边界样式

- 闭边界：
  - 实线
- 开边界：
  - 虚线

这是第一层最直接的视觉区分。

### 内部内缩

当区域存在填充时，对严格约束应使用一个很小的向内偏移来生成“填充区域”：

- `a^T x < b` 在渲染填充时可视作 `a^T x <= b - epsilon_render`

这个 epsilon 只用于渲染 fill，不用于外部可见的语义几何。

这样做的好处是：

- 填充不会看起来把开边界也“吃进去”
- 真正的边界线仍可画在数学上正确的位置

默认的 `strict_epsilon` 不应是全局固定常数，而应当与当前轴尺度相关。

## 无界区域的语义处理

这是第二个必须显式解决的问题。

### 问题

matplotlib 坐标轴是有限的，但 zone 可以是无界的。

例如：

- `x >= 0`
- `x - y < 3`
- `x >= 1 and y >= 1`

如果只是把区域裁到当前轴范围内，用户很难分辨：

- 这个区域本来就是有界的
- 还是图只是被截断了

### 拟议规则

所有绘图都在有限 render box 内完成，但所有截断都必须有明确视觉标识。

### Render box

`limits` 应支持：

- 1D：
  - `(xmin, xmax)`
- 2D：
  - `((xmin, xmax), (ymin, ymax))`
- 3D：
  - `((xmin, xmax), (ymin, ymax), (zmin, zmax))`

当 `limits` 未提供时：

- 尽量根据有限 DBM 边界推断可见范围
- 再加一定 padding
- 对完全无界方向则使用保守默认跨度

### 截断元信息

在裁剪过程中，应记录某条可见边或某个可见面是否只是因为 render box 被截出来，而真实 zone 还会继续延伸。

### 视觉提示

第一版建议：

- 1D：
  - 在无界侧端点加箭头
- 2D：
  - 在被裁剪边的中点附近加向外箭头
- 3D：
  - 第一版可以先用边界标记或图例说明，因为 3D 箭头往往不够直观

仅由 clip box 引入的边界，不应使用和真实 zone 边界同等强度的视觉权重。

## Federation 的渲染方案

`Federation` 应表示为各个 DBM 组成的精确并集，而不是自动做 convex hull。

### 默认行为

对 `plot_federation(fed, ...)`：

1. 先取 `dbms = fed.to_dbm_list()`
2. 在 2D 情况下，先求出 federation 并集的精确边界与面域
3. 在非 2D 情况下，按各个 DBM 分别处理
4. 再把所有 artists 汇总成一个 `PlotResult`

### 样式策略

第一版支持两种模式即可：

- `color_mode="shared"`
  - federation 内所有 DBM 共用一套 face / edge 样式
- `color_mode="per_dbm"`
  - 对不同 DBM 循环颜色

默认值建议用 `"shared"`，因为这更符合“一个 federation，由多个凸片段组成”的语义。

### 重叠策略

这里需要按维度区分。

对于 2D federation：

- 第一阶段就应支持 federation 的精确 2D 并集边界提取
- 不能只靠多个 DBM 透明叠加来“视觉近似” federation 形状
- 这是整个可视化能力里最重要的语义点之一

对于非 2D 情况：

- 1D federation 可以直接做精确区间并集
- 3D federation 第一版可以暂时仍按 DBM 片段渲染，而不要求立刻做精确 polyhedron union

也就是说，第一版策略不是“完全不做 federation 几何并集”，而是：

- 1D：做精确并集
- 2D：做精确并集与精确边界
- 3D：第一版允许暂不做精确并集

## 错误模型

绘图层对不支持或无意义的输入应明确失败。

建议的错误类型：

- `ImportError`
  - matplotlib 未安装
- `TypeError`
  - 输入对象不是 `DBM` 或 `Federation`
- `ValueError`
  - 用户时钟维度不在 `1..3`
- `ValueError`
  - `limits` 结构非法
- `RuntimeError`
  - 内部几何裁剪得到了不一致的凸对象

错误信息应明确说明维度计数是“用户时钟数”，不是包含隐式零时钟在内的 DBM 矩阵维度。

## 建议的文件布局

建议新增文件：

- `pyudbm/binding/visual.py`
- `requirements-plot.txt`

可能会跟着调整的已有文件：

- `pyudbm/binding/__init__.py`
- `pyudbm/binding/udbm.py`
- `setup.py`
- `test/binding/test_visual.py`
- `test/binding/test_matplotlib.py`

如果第一版只想先走对象方法入口，那么也可以暂时不把 `plot_dbm` / `plot_federation` 额外从包根暴露出去。

## 分阶段实施计划

这一部分不只是高层路线图，而是后续真正实施时的执行清单基线。

建议整体按四个 phase 推进，每个 phase 都应独立可提交、可测试、可 review。

### 当前状态快照

基于当前仓库代码、测试与文档状态，可以先给出一个同步结论：

- `Phase 0` 已基本完成，当前 plotting 测试继续保留在 `test/binding/`
- `Phase 1` 已完成 `1D / 2D` 几何提取、`1D federation` 精确区间并集、`2D federation` 精确边界提取，以及对应单元测试
- `Phase 2` 已完成 `1D / 2D` matplotlib 渲染、`plot_dbm(...)` / `plot_federation(...)`、`DBM.plot(...)` / `Federation.plot(...)`、`plot` extra 以及对应测试
- `Phase 3` 仍未开始，当前对 `3D` 仍显式保留为 `NotImplementedError`
- `Phase 4` 已完成一部分收尾工作，包括对象方法 docstring、模块级 docstring、`binding.__init__` 导出、默认颜色/图例行为和 API 文档页；但包根导出、示例整理与 `3D` 文档仍未完成

本次同步后，原始计划里有一条旧约束被直接删除：

- 删除“第一版不对 federation 做布尔并集几何化简”
  - 原因是当前实现已经明确采用 `1D` 精确区间并集与 `2D` 精确边界提取；继续保留这条旧约束会和现实现状直接冲突，反而误导后续开发

下面的 checklist 已按上述现状同步。

### Phase 0：准备与接口冻结

目标：

- 在正式实现前把接口、依赖、测试入口和错误模型先固定下来
- 避免 1D / 2D 做到一半又反复改公开 API

范围：

- 只做设计收口与实现前准备
- 不要求完成真实绘图功能

交付物：

- 更新后的方案文档
- 代码文件布局确认
- 第一版公开 API 草案
- 错误类型和参数约定

Checklist：

- [x] 确认实现文件落在 `pyudbm/binding/visual.py`
- [x] 确认第一版主入口为 `plot_dbm(...)` 与 `plot_federation(...)`
- [x] 确认第一版对象便捷方法至少覆盖 `DBM.plot(...)` 与 `Federation.plot(...)`
- [x] 确认对象方法采用方法体内懒导入，不在 `udbm.py` 顶层导入 `visual.py`
- [x] 确认 matplotlib 通过 `requirements-plot.txt` 作为可选依赖接入
- [x] 确认第一版仅支持用户时钟维度 `1..3`
- [x] 确认第一版不做高维投影
- [x] 确认 `limits`、`strict_epsilon`、`show_unbounded`、`color_mode` 作为保留参数进入第一版设计
- [x] 确认 `PlotResult` 作为统一返回容器
- [x] 确认错误模型至少覆盖 `ImportError`、`TypeError`、`ValueError`、`NotImplementedError`
- [x] 确认 plotting 测试继续保留在 `test/binding/`

完成判定：

- 团队对模块位置、公开 API、对象方法接入方式、依赖方式和维度边界没有未决分歧

### Phase 1：几何核心层

目标：

- 先把不依赖 matplotlib 的几何恢复做出来
- 优先保证“算得对”，不优先追求“画得好看”
- 在这一阶段直接拿到 `Federation` 的精确 2D 边界，这是整个方案最重要的里程碑之一

范围：

- 覆盖 1D / 2D 的几何提取
- 覆盖 1D federation 精确并集
- 覆盖 2D federation 精确并集与精确边界提取
- 为后续 3D 留接口，但不在本 phase 强行实现 3D

建议改动文件：

- `pyudbm/binding/visual.py`
- `test/binding/test_visual.py`

交付物：

- 内部几何对象
- 从 DBM 到半空间的转换逻辑
- render box 归一化逻辑
- 1D 几何恢复
- 2D 凸多边形裁剪
- 1D federation 精确并集结果
- 2D federation 精确面域结果
- 2D federation 精确边界结果

Checklist：

- [x] 在 `visual.py` 中定义内部几何对象或等价内部表示
- [x] 为内部对象补充足够的元信息字段：坐标、开闭边界、clip 来源、退化类型
- [x] 实现从 `DBM` 读取有限非对角约束并转换成半空间
- [x] 明确 reference clock `0` 到可视坐标的映射规则
- [x] 实现用户时钟维度检查，并对 `0` 维和 `>3` 维直接报错
- [x] 实现 `limits` 的归一化与结构校验
- [x] 实现默认 render box 推断规则
- [x] 实现 1D 上下界恢复逻辑
- [x] 支持 1D 下的区间、射线、点、空集分类
- [x] 实现 1D federation 的精确区间并集
- [x] 实现 2D 半平面裁剪
- [x] 支持 2D 下的多边形、线段、点、空集分类
- [x] 设计 2D federation 并集的内部表示，而不是只保留“多个 DBM 列表”
- [x] 实现 2D federation 的精确布尔并集
- [x] 实现 2D federation 的精确边界提取
- [x] 明确 2D federation 边界中的外边界与内部共享边处理规则
- [x] 明确 2D federation 边界在开 / 闭边界相邻时的归并规则
- [x] 明确 2D federation 边界在多个 DBM 重合边情况下的去重规则
- [x] 对严格不等式保留开边界元信息，而不是在几何阶段直接丢失
- [x] 记录哪些边界来自真实 zone，哪些边界仅来自 clip box
- [x] 为后续渲染准备统一的数据导出接口

Phase 1 测试 Checklist：

- [x] 在 `test/binding/test_visual.py` 中覆盖几何层测试
- [x] 覆盖 1D：`x == 0`
- [x] 覆盖 1D：`x < 5`
- [x] 覆盖 1D：`x <= 5`
- [x] 覆盖 1D：`x > 2`
- [x] 覆盖 1D：`x >= 0`
- [x] 覆盖 1D 空集
- [x] 覆盖 1D federation 的不相交区间并集
- [x] 覆盖 1D federation 的相邻区间归并
- [x] 覆盖 2D 有界矩形状 zone
- [x] 覆盖 2D 对角约束 zone
- [x] 覆盖 2D 无界楔形区域
- [x] 覆盖 2D 线段退化
- [x] 覆盖 2D 点退化
- [x] 覆盖 2D 空集
- [x] 覆盖 2D federation 的不相交并集
- [x] 覆盖 2D federation 的相交并集
- [x] 覆盖 2D federation 的共享边消解
- [x] 覆盖 2D federation 的孔洞不存在或被正确表达的约束情形
- [x] 覆盖 2D federation 中开边界与闭边界混合的边界提取
- [x] 断言 2D federation 边界结果不是简单的 DBM 边界拼接
- [x] 断言几何对象中的开闭边界标记
- [x] 断言哪些边界来自 clip box
- [x] 断言非法 `limits` 会抛出明确异常

完成判定：

- 不依赖 matplotlib，也能用测试证明 1D / 2D 的几何恢复是正确的
- 不依赖 matplotlib，也能拿到 federation 的精确 2D 边界，而不是仅有 DBM 片段集合

### Phase 2：1D / 2D 的 matplotlib 渲染与对象方法接入

目标：

- 在已有几何层之上，把 1D / 2D 先完整画通
- 把“开闭边界”“无界区域”“对象方法调用”这三个用户最关心的点打通
- 直接消费 Phase 1 产出的 federation 精确 2D 边界结果，而不是在渲染阶段临时重算粗略轮廓

范围：

- 覆盖 1D / 2D 渲染
- 接入 `DBM.plot(...)` 和 `Federation.plot(...)`

建议改动文件：

- `pyudbm/binding/visual.py`
- `pyudbm/binding/udbm.py`
- `pyudbm/binding/__init__.py`
- `requirements-plot.txt`
- `setup.py`
- `test/binding/test_matplotlib.py`

交付物：

- 模块级绘图函数
- `DBM.plot(...)`
- `Federation.plot(...)`
- `PlotResult`
- 1D / 2D matplotlib artists 渲染
- 基于 federation 精确 2D 边界的渲染输出

Checklist：

- [x] 在 `visual.py` 中加入 matplotlib 懒导入入口
- [x] 当 matplotlib 不存在时抛出清晰的 `ImportError`
- [x] 实现 `PlotResult`
- [x] 实现 `plot_dbm(...)`
- [x] 实现 `plot_federation(...)`
- [x] 1D 渲染支持区间、射线、点、空集
- [x] 2D 渲染支持多边形、线段、点、空集
- [x] 闭边界使用闭边界样式
- [x] 开边界使用开边界样式
- [x] 严格不等式对应的 fill 使用渲染内缩策略
- [x] clip box 引入的边界与真实边界区分显示
- [x] 无界区域添加视觉提示
- [x] `Federation` 在 1D / 2D 下优先使用精确并集几何结果进行渲染
- [x] `Federation` 在 2D 下优先使用精确边界结果渲染边界线
- [x] 支持 `ax` 透传
- [x] 支持 `facecolor`、`edgecolor`、`alpha`、`linewidth`、`linestyle`、`label`、`zorder`
- [x] 支持 `limits`、`strict_epsilon`、`show_unbounded`、`color_mode`
- [x] 在 `DBM` 上增加 `plot(...)`
- [x] 在 `Federation` 上增加 `plot(...)`
- [x] 两个对象方法都只在方法体内部导入 `visual.py`
- [x] 不在 `pyudbm/binding/udbm.py` 顶层导入 `visual.py`
- [x] 增加 `requirements-plot.txt`
- [x] 确认 `setup.py` 能把 `plot` extra 暴露出来

Phase 2 测试 Checklist：

- [x] 在 `test/binding/test_matplotlib.py` 中覆盖 matplotlib 渲染测试
- [x] 断言 `plot_dbm(...)` 在给定 `ax` 时不新建错误类型的 axes
- [x] 断言 `plot_federation(...)` 可以处理多 DBM federation
- [x] 断言返回值是 `PlotResult`
- [x] 断言开边界与闭边界对应不同 linestyle 或 marker 语义
- [x] 断言无界区域存在提示元素
- [x] 断言 1D 与 2D 的退化对象都能渲染而不报错
- [x] 断言 2D federation 渲染使用的是精确边界结果，而不是简单按 DBM 叠画
- [x] 断言 `DBM.plot(...)` 能正常转发
- [x] 断言 `Federation.plot(...)` 能正常转发
- [x] 断言缺失 matplotlib 时异常消息可理解

完成判定：

- 用户可以用对象方法或模块级函数，在 1D / 2D 下得到语义正确且样式可控的图

### Phase 3：3D 几何与渲染

目标：

- 在前两阶段稳定之后，把 3D 加进来
- 保持语义一致性，不为了“有图”而牺牲正确性

范围：

- 覆盖三时钟 zone 的几何恢复与渲染
- 不扩展到高维投影

建议改动文件：

- `pyudbm/binding/visual.py`
- `test/binding/test_visual.py`
- `test/binding/test_matplotlib.py`

交付物：

- 3D 凸多面体裁剪
- 3D face / edge / degenerate object 表示
- 3D matplotlib 渲染

Checklist：

- [ ] 在几何层增加 3D 多面体内部表示
- [ ] 实现 3D 半空间裁剪
- [ ] 支持 3D 下的面、线、点、空集退化分类
- [ ] 保留 3D 下的开闭边界元信息
- [ ] 保留 3D 下的 clip box 截断元信息
- [ ] 使用 `Poly3DCollection` 渲染 3D 面
- [ ] 使用单独 edge artists 强化边界
- [ ] 对无界截断提供至少一种可解释的视觉提示
- [ ] 保持 `plot_dbm(...)` / `plot_federation(...)` 的参数接口不破坏前两阶段
- [ ] 继续对高于 3 维直接报错

Phase 3 测试 Checklist：

- [ ] 覆盖 3D 有界 box 状 zone
- [ ] 覆盖 3D 带对角约束的有界 zone
- [ ] 覆盖 3D 无界但被 render box 截断的 zone
- [ ] 覆盖 3D 面、线、点级退化输出
- [ ] 断言 3D artist 类型合理
- [ ] 断言高于 3 维仍抛出明确异常

完成判定：

- 三时钟 zone 可以在 3D 下稳定显示，且没有破坏 1D / 2D 行为

### Phase 4：文档、默认值、导出面与收尾

目标：

- 把功能从“能用”打磨到“能维护、能解释、能发布”

范围：

- 文档、默认值、导出面、使用示例、回归补洞

建议改动文件：

- `pyudbm/binding/udbm.py`
- `pyudbm/binding/__init__.py`
- `pyudbm/__init__.py`
- `README.md`
- `test/binding/test_matplotlib.py`

交付物：

- 完整 docstring
- 公开导出策略
- 更稳的默认参数
- 示例代码

Checklist：

- [x] 为 `DBM.plot(...)` 补 docstring
- [x] 为 `Federation.plot(...)` 补 docstring
- [x] 为 `plot_dbm(...)` 和 `plot_federation(...)` 补 docstring
- [ ] 文档中明确说明 matplotlib 是可选依赖
- [ ] 文档中明确说明仅支持 `1..3` 维
- [ ] 文档中明确说明无界区域依赖有限裁剪加指示符表达
- [x] 评估是否要在 `binding/__init__.py` 导出模块级绘图函数
- [ ] 评估是否要在包根继续转发绘图函数
- [ ] 评估是否需要给 `Context` 增加额外便捷入口
- [x] 优化默认颜色与图例行为
- [ ] 补充至少一组 1D 示例
- [x] 补充至少一组 2D 示例
- [ ] 如 3D 已实现，补充至少一组 3D 示例
- [x] 回看异常消息是否一致、可理解
- [x] 回看公开参数命名是否符合现有项目风格

Phase 4 测试 Checklist：

- [ ] 补充针对公开导出面的测试
- [ ] 补充针对对象方法 docstring / 可见性的必要回归测试
- [x] 回归运行 plotting 测试全集
- [x] 回归运行现有 binding 测试，确认没有破坏原 API

完成判定：

- 功能具备明确文档、稳定默认值和可发布的公开入口

## 推荐的实施顺序与提交粒度

为了降低 review 难度，建议提交粒度如下：

1. `Phase 1` 几何层与纯几何测试
2. `Phase 2` 中的 `requirements-plot.txt`、懒导入、模块级 1D / 2D 绘图函数
3. `Phase 2` 中基于 federation 精确 2D 边界结果的渲染接入
4. `Phase 2` 中的 `DBM.plot(...)` / `Federation.plot(...)` 接入与对应测试
5. `Phase 3` 3D 几何与渲染
6. `Phase 4` 文档、导出面和默认值打磨

不建议把所有 phase 压成一个大提交，否则很难 review，也很难定位几何 bug 和渲染 bug。

## Phase 完成定义

每个 phase 完成前都应同时满足下面四类条件：

- 代码条件：
  - 本 phase 的目标能力已经落地
- 测试条件：
  - 本 phase 新增测试已经覆盖关键路径
- 回归条件：
  - 现有 `binding` 测试未被破坏
- 文档条件：
  - 公开 API 或行为变化已经在文档 / docstring 中解释清楚

## 测试策略

### 几何层单元测试

几何层应该独立于 matplotlib 做测试。

代表性用例：

- 1D：
  - `x == 0`
  - `x < 5`
  - `x <= 5`
  - `x > 2`
  - `x >= 0`
  - 空集
- 2D：
  - 有界矩形状 zone
  - 带对角线约束的有界 zone
  - 无界楔形区域
  - 由等式约束形成的线段
  - `x == c and y == d` 形成的点
  - 空集
- 3D：
  - 有界 box 状 zone
  - 带对角平面约束的有界 zone
  - 被 render box 截断的无界多面体

断言重点：

- 坐标
- 开闭标记
- 截断标记
- 退化对象分类

### 渲染测试

第一版渲染测试不建议依赖脆弱的像素级截图比对。

更稳妥的是断言：

- 返回的 artist container 类型
- 生成的 artists 数量
- 开边界与闭边界对应的 linestyle
- 无界区域是否存在提示元素
- 是否能兼容调用方传入的 `ax`

后续如果仓库有需要，可以再考虑加入图像回归测试。

## 文档计划

当功能开始实现时，文档至少应包括：

- plotting API 的 docstring
- 未来 README 或公开教程中的一两个示例
- 对以下事实的明确说明：
  - 高于 3 维不支持
  - matplotlib 是可选依赖
  - 无界区域通过“有限裁剪 + 明确提示”来表达

文档不应过度承诺 3D 语义。如果第一版 3D 可视化存在视觉权衡，应直接写清楚。

## 风险与权衡

### 1. 严格边界在视觉上天然不够显眼

只靠虚线边并不够，尤其是在存在填充时。

缓解方式：

- 填充与边界线分开绘制
- 对严格约束的 fill 使用向内渲染 epsilon

### 2. 无界区域的可视化一定依赖有限 render limits

任何有限图像本质上都要对 infinity 做裁剪。

缓解方式：

- 在 API 和视觉层面都显式承认裁剪
- 将 clip box 引入的伪边界与真实边界区分开

### 3. 3D 的实现复杂度明显高于 2D

缓解方式：

- 不让 3D 阻塞 1D / 2D 落地
- 先把 2D 路径做稳定，再上 3D

### 4. Federation 的并集叠加可能视觉上比较密

缓解方式：

- 默认共用颜色并配中等 alpha
- 第一版不尝试做精确几何并集

## 建议的直接下一步

当前分支已经基本把原方案中的 `Phase 1` 和 `Phase 2` 做完，因此后续开发建议直接转到下面几项：

- 补齐 `Phase 4` 里还没完成的公开导出面与示例策略，尤其是“包根是否继续转发绘图函数”与 `1D` 示例
- 明确 `clip box` 边界与真实边界的可视区分策略，并补一组对应渲染测试
- 在这些收尾项稳定后，再单开里程碑推进 `Phase 3` 的 `3D` 几何与渲染

如果要继续拆 PR，最稳的顺序是：

1. 导出面 / 示例 / 文档收尾
2. `clip box` 边界样式补完
3. `3D` 几何与渲染
