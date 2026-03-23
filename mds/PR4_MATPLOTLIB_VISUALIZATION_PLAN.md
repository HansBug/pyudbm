# DBM 与 Federation 的 Matplotlib 可视化实施方案

## PR 关联

本方案对应的 GitHub Pull Request：

- PR #4: <https://github.com/HansBug/pyudbm/pull/4>

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

模块级函数形态：

```python
def plot_dbm(dbm, ax=None, **kwargs):
    ...


def plot_federation(federation, ax=None, **kwargs):
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

这样可以同时满足两个目标：

- 使用方式足够自然
- 避免在模块初始化阶段产生循环 import

### 建议的关键字参数

第一版公开 API 应保持克制，但要覆盖关键控制点。

通用参数：

- `ax=None`
- `facecolor=None`
- `edgecolor=None`
- `alpha=None`
- `linewidth=None`
- `linestyle=None`
- `label=None`
- `zorder=None`

可视化特定参数：

- `limits=None`
  - 用于裁剪无界区域的 render box 或坐标轴边界
- `strict_epsilon=None`
  - 仅用于渲染的内缩量，用来区分开边界与填充内部
- `show_unbounded=True`
  - 是否给无界区域加箭头或其他明确提示
- `color_mode="shared"`
  - federation 内所有 DBM 共用一种样式，或为每个 DBM 循环颜色
- `annotate=False`
  - 是否附带轻量注释，例如 DBM 编号或文本摘要

维度特定参数：

- 1D：
  - `baseline=0.0`
- 2D：
  - `xclock=None`、`yclock=None`
- 3D：
  - `xclock=None`、`yclock=None`、`zclock=None`

如果第一版坚持更简单的规则，那么轴选择参数可以先不开放，直接约定：

- 1 维时，唯一用户时钟映射到 x 轴
- 2 维时，两个用户时钟映射到 `(x, y)`
- 3 维时，三个用户时钟映射到 `(x, y, z)`

这是最简单的第一版，也最符合当前范围限制。

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
2. 对每个 DBM 分别绘制
3. 再把所有 artists 汇总成一个 `PlotResult`

### 样式策略

第一版支持两种模式即可：

- `color_mode="shared"`
  - federation 内所有 DBM 共用一套 face / edge 样式
- `color_mode="per_dbm"`
  - 对不同 DBM 循环颜色

默认值建议用 `"shared"`，因为这更符合“一个 federation，由多个凸片段组成”的语义。

### 重叠策略

第一版不需要尝试对各个 DBM 做精确布尔并集。

原因：

- federation 本来就应该以 DBM 并集的形式存在
- 精确 polygon / polyhedron union 是另一类几何问题
- 使用适当 alpha 叠加多个凸片段，已经足够表达正确语义

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
- `test/plotting/__init__.py`
- `test/plotting/test_geometry.py`
- `test/plotting/test_matplotlib.py`
- `requirements-plot.txt`

可能会跟着调整的已有文件：

- `pyudbm/binding/__init__.py`
- `pyudbm/binding/udbm.py`
- `setup.py`

如果第一版只想先走对象方法入口，那么也可以暂时不把 `plot_dbm` / `plot_federation` 额外从包根暴露出去。

## 分阶段实施计划

### 第一阶段：几何基础层

目标：

- 先把 1D / 2D 的内部几何提取做出来，不依赖 matplotlib

任务：

- 定义内部几何对象
- 实现从 DBM 到半空间的提取
- 实现 render box 处理
- 实现 1D 区间 / 射线 / 点提取
- 实现 2D 凸多边形裁剪
- 保留 strictness 和 clip 来源元信息

成功标准：

- 纯 Python 单元测试可以验证代表性 DBM 的几何输出

### 第二阶段：1D / 2D 的 matplotlib 渲染与对象方法接入

目标：

- 先把最常用、最有价值的 1D / 2D 画通

任务：

- 在 `pyudbm/binding/visual.py` 中增加 lazy import matplotlib 的入口
- 渲染 1D 区间、射线和点
- 渲染 2D 多边形、线段和点
- 支持开 / 闭边界样式
- 支持无界提示
- 返回 `PlotResult`
- 在 `DBM` 和 `Federation` 上增加懒导入对象方法

成功标准：

- 用户可以把常见 zone 和 federation 画到已有 `ax` 上
- 开闭边界和有界 / 无界差异可以在图上清晰看出来

### 第三阶段：3D 几何与渲染

目标：

- 将同样的语义扩展到 3D

任务：

- 实现凸多面体裁剪
- 用 `Poly3DCollection` 渲染
- 支持 3D 下的退化输出
- 支持无界截断提示

成功标准：

- 常见三时钟 zone 能正确显示
- 高于 3 维的情况仍然显式报错

### 第四阶段：打磨与扩展

目标：

- 让这套能力更像 `pyudbm` 原生功能，而不是外接脚本

任务：

- 评估是否需要为 `Context` 增加额外便捷入口
- 优化默认颜色、图例和 label 行为
- 补充 docstring 示例
- 决定是否要从 `binding/__init__.py` 或包级别导出模块级绘图函数

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

如果要开始实现，建议先只做第一阶段和第二阶段：

- 几何提取
- 1D 绘图
- 2D 绘图
- 可选依赖接入
- 对应测试

这条路径价值最高、复杂度最低，而且能尽早验证几个最关键的语义决策：

- 开边界与闭边界怎么表示
- infinity 截断后如何不误导用户
- DBM 与 federation 的分层渲染语义

3D 应当从一开始就在 API 设计上预留，但实现上作为后续独立里程碑推进。
