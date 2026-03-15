# PY2 Compatibility Checklist

## 目的

这份文档用于把 `srcpy2/` 中保留的历史 Python 2 绑定作为行为基线，逐项对照当前 `pyudbm/binding/` 的实现状态，确认：

1. 哪些高层 API 已经恢复。
2. 哪些行为与历史版本一致。
3. 哪些地方虽然“能用”，但已经偏离 legacy 语义。
4. 哪些低层兼容面尚未恢复。

对照基线：

- `srcpy2/udbm.py`
- `srcpy2/test.py`
- `srcpy2/udbm_int.i`
- `srcpy2/udbm_int.h`

当前实现：

- `pyudbm/binding/udbm.py`
- `pyudbm/binding/_binding.cpp`
- `pyudbm/binding/__init__.py`
- `pyudbm/__init__.py`
- `test/binding/test_api.py`

检查方式：

- 静态逐段对照 `srcpy2/udbm.py` 与 `pyudbm/binding/udbm.py`
- 对照 `srcpy2/test.py` 与 `test/binding/test_api.py`
- 对照旧 SWIG 暴露面与当前 pybind11 暴露面
- 动态验证若干边界行为
- 运行 `python -m pytest -q test/binding/test_api.py`

结果概览：

- 当前高层 API 形状已经基本恢复，`Context / Clock / Federation` 主线可用。
- `srcpy2/test.py` 中的核心历史行为大部分已有对应测试，当前 `test/binding/test_api.py` 运行结果为 `29 passed`。
- 仍存在若干明确的语义漂移，尤其是“只接受精确 `int`”和 `Clock` / `VariableDifference` 的 DSL 比较行为。
- 如果目标是“严格 legacy parity”，当前测试中有一部分新 edge-case 语义也需要回收。

## 总结结论

| 维度 | 结论 |
| --- | --- |
| 高层 API 是否基本齐全 | 是 |
| `srcpy2/test.py` 核心测试主题是否基本覆盖 | 是 |
| 是否存在行为不一致 | 是，且不止一处 |
| 是否存在高层“完全未实现”的旧方法 | 未发现 |
| 是否恢复了旧 `udbm_int` 低层公开兼容面 | 否 |

## 包导出对照

| 历史导出 | 当前导出 | 状态 | 说明 |
| --- | --- | --- | --- |
| `srcpy2/__init__.py` 导出 `Clock` | `pyudbm/__init__.py` 导出 `Clock` | 已实现 | 根包兼容 |
| `srcpy2/__init__.py` 导出 `Context` | `pyudbm/__init__.py` 导出 `Context` | 已实现 | 根包兼容 |
| `srcpy2/__init__.py` 导出 `Federation` | `pyudbm/__init__.py` 导出 `Federation` | 已实现 | 根包兼容 |
| 历史高层模块中存在 `Constraint` / `Valuation` / `IntValuation` / `FloatValuation` / `VariableDifference` | 当前根包和 `pyudbm.binding` 均导出这些对象 | 已实现 | 当前导出面比历史根包更宽 |

## 高层 API 逐项对照

### `Clock`

| 历史项 | 当前项 | 状态 | 备注 |
| --- | --- | --- | --- |
| `__init__(context, name, index)` | `__init__(context, name, index)` | 已实现 | 语义一致 |
| `__sub__(Clock)` | `__sub__(Clock)` | 实现但有异常模型差异 | 历史版非 `Clock` 走 `assert`；当前返回 `NotImplemented`，最终表现为 `TypeError` |
| `__le__(int)` | `__le__(int)` | 实现但有类型漂移 | 历史版要求 `type(c) == int`；当前 `isinstance(bound, int)`，会接受 `bool` |
| `__ge__(int)` | `__ge__(int)` | 实现但有类型漂移 | 同上 |
| `__lt__(int)` | `__lt__(int)` | 实现但有类型漂移 | 同上 |
| `__gt__(int)` | `__gt__(int)` | 实现但有类型漂移 | 同上 |
| `__eq__(int)` 生成约束 | `__eq__(int)` 生成约束 | 实现但非 `int` 路径漂移 | 历史版非 `int` 触发断言；当前对非 `int` 做对象比较 |
| `__ne__(int)` 生成约束 | `__ne__(int)` 生成约束 | 实现但非 `int` 路径漂移 | 历史版非 `int` 触发断言；当前对非 `int` 做对象比较 |
| `__hash__()` | `__hash__()` | 已实现 | 一致 |
| `getFullName()` | `getFullName()` | 已实现 | 一致 |
| 无 `__repr__` | 新增 `__repr__` | 扩展 | 非问题，但不是历史行为的一部分 |

关键差异：

- 历史版严格只接受精确 `int`，当前会把 `True` / `False` 当作 `1` / `0`。
- 历史版 `clock == something` 的设计目的是创建 Federation 约束，不是做对象等价比较；当前新增了对象比较语义。

### `Valuation` / `IntValuation` / `FloatValuation`

| 历史项 | 当前项 | 状态 | 备注 |
| --- | --- | --- | --- |
| `Valuation.__init__(context)` | 同名实现 | 已实现 | 一致 |
| `Valuation.__setitem__` 支持 `Clock` 或字符串键 | 同名实现 | 实现但异常模型差异 | 当前增加 `_normalize_key`，错误类型更明确 |
| `Valuation.check()` 记录缺失 clock | 同名实现 | 已实现 | 日志文案略有变化 |
| `IntValuation.__setitem__` 只允许 `type(value) == int` | 同名实现 | 实现但类型漂移 | 当前 `bool` 会被接受 |
| `FloatValuation.__setitem__` 允许 `float` 或 `int` | 同名实现 | 实现但类型漂移 | 当前 `bool` 也会被接受，因为 `bool` 是 `int` 子类 |

关键差异：

- 历史版对整数赋值是“精确 int”，当前是“`int` 子类也可”。
- 历史版错误多依赖 `assert` 或原生 `KeyError`，当前明确抛 `TypeError` / `ValueError`。

### `VariableDifference`

| 历史项 | 当前项 | 状态 | 备注 |
| --- | --- | --- | --- |
| `__init__([clock1, clock2])` | 同名实现 | 实现但异常模型差异 | 当前改为显式 `ValueError` |
| `__le__(int)` | 同名实现 | 实现但类型漂移 | 当前会接受 `bool` |
| `__ge__(int)` | 同名实现 | 实现但类型漂移 | 当前会接受 `bool` |
| `__lt__(int)` | 同名实现 | 实现但类型漂移 | 当前会接受 `bool` |
| `__gt__(int)` | 同名实现 | 实现但类型漂移 | 当前会接受 `bool` |
| `__eq__(int)` 生成约束 | 同名实现 | 实现但非 `int` 路径漂移 | 当前对非 `int` 返回 `False` |
| `__ne__(int)` 生成约束 | 同名实现 | 实现但非 `int` 路径漂移 | 当前对非 `int` 返回 `True` |

关键差异：

- 与 `Clock` 一样，历史版这里只有 DSL 语义，没有一般对象比较语义。

### `Constraint`

| 历史项 | 当前项 | 状态 | 备注 |
| --- | --- | --- | --- |
| `Constraint(arg1, arg2, val, isStrict)` | 同名实现 | 已实现 | 核心功能存在 |
| 参数校验大量靠 `assert` | 当前显式 `TypeError` / `ValueError` | 行为漂移 | 更清晰，但不是原始行为 |
| `udbm_int.Constraint(...)` | `_NativeConstraint(...)` | 已实现 | 命名变化，位于私有绑定层 |

备注：

- 历史代码里有一段 `if arg1 is None and arg2 is None: assert(arg1.context == arg2.context)`，这其实永远不可达且写法错误；当前显式改成拒绝双 `None`，这是合理修正。

### `Federation`

| 历史项 | 当前项 | 状态 | 备注 |
| --- | --- | --- | --- |
| `__init__(Constraint)` | 同名能力 | 已实现 | 一致 |
| `__init__(Context)` 返回零联邦 | 同名能力 | 已实现 | 一致 |
| `__str__()` | `__str__()` | 已实现 | 当前通过 `_NativeFederation.to_string()`，字符串替换逻辑保留 |
| `copy()` | `copy()` | 已实现 | 一致 |
| `__and__` / `__iand__` | 已实现 | 已实现 | 当前会做显式兼容性检查 |
| `__or__` / `__ior__` | 已实现 | 已实现 | 同上 |
| `__add__` / `__iadd__` | 已实现 | 已实现 | 同上 |
| `__sub__` / `__isub__` | 已实现 | 已实现 | 同上 |
| `up()` | 已实现 | 已实现 | 保持非原地语义 |
| `down()` | 已实现 | 已实现 | 保持非原地语义 |
| `reduce(level=0)` | 已实现 | 已实现 | 原地，兼容 |
| `freeClock(clock)` | 已实现 | 已实现但仍有旧风险 | 仍未校验 `clock.context` |
| `setZero()` | 已实现 | 已实现 | 原地，兼容 |
| `hasZero()` | 已实现 | 已实现 | 一致 |
| `setInit()` | 已实现 | 已实现 | 原地，兼容 |
| `convexHull()` | 已实现 | 已实现 | 保持非原地语义 |
| `__eq__` / `__ne__` | 已实现 | 已实现但异常模型差异 | 当前比较非 Federation 返回 `False` |
| `__le__` / `__ge__` / `__lt__` / `__gt__` | 已实现 | 已实现 | 当前显式校验类型和 context |
| `intern()` | 已实现 | 已实现 | 一致 |
| `predt()` | 已实现 | 已实现 | 保持非原地语义 |
| `contains(IntValuation / FloatValuation)` | 已实现 | 已实现但错误路径不同 | 当前未知 valuation 类型抛 `TypeError` |
| `updateValue(clock, value)` | 已实现 | 已实现 | 现在多了显式 context 校验 |
| `resetValue(clock)` | 已实现 | 已实现 | 一致 |
| `getSize()` | 已实现 | 已实现 | 一致 |
| `extrapolateMaxBounds(mapping)` | 已实现 | 已实现但有日志文案和键类型扩展 | 当前支持字符串键，同时仍允许缺失 bounds 时只记日志 |
| `isZero()` | 已实现 | 已实现 | 一致 |
| `isEmpty()` | 已实现 | 已实现 | 一致 |
| `__hash__()` / `hash()` | 已实现 | 已实现 | 一致 |

关键差异：

- `freeClock()` 依然没有检查 clock 是否来自同一 `Context`。
- `contains()` 在未知 valuation 类型上的行为与历史版不同。
- `extrapolateMaxBounds()` 仍然会在 bounds 不完整时继续运行，这一旧风险被保留了下来。

### `Context`

| 历史项 | 当前项 | 状态 | 备注 |
| --- | --- | --- | --- |
| `__init__(clock_names, name=None)` | 同名实现 | 已实现 | 一致 |
| 同时构造 `clocks` 列表和属性访问 | 同名实现 | 已实现 | 一致 |
| 属性名冲突时记录 warning | 同名实现 | 已实现 | 日志文案略有变化 |
| `setName(name)` | 已实现 | 已实现 | 一致 |
| `__getitem__(name)` | 已实现 | 实现但重复名行为漂移 | 历史版重复名时 `assert(len(names) == 1)`；当前抛 `KeyError("Ambiguous clock name: x")` |
| `getZeroFederation()` | 已实现 | 已实现 | 一致 |

## 历史测试逐项对照

| 历史测试 | 当前对应测试 | 状态 | 备注 |
| --- | --- | --- | --- |
| `test_int_valuation` | `test_int_valuation` | 已覆盖 | 主路径一致 |
| `test_float_valuation` | `test_float_valuation` | 已覆盖 | 主路径一致 |
| `test_set_operations` | `test_set_operations` | 已覆盖 | 核心 DSL 已覆盖 |
| `test_zero` | `test_zero` | 已覆盖 | 一致 |
| `test_update_clocks` | `test_update_clocks` | 已覆盖 | 一致 |
| `test_str` | `test_str` | 已覆盖 | 一致 |
| `test_copy` | `test_copy` | 已覆盖 | 一致 |
| `test_reduce` | `test_reduce` | 已覆盖 | 一致 |
| `test_convex_hull` | `test_convex_hull` | 已覆盖 | 一致 |
| `test_sub` | `test_sub` | 已覆盖 | 一致 |
| `test_up_down` | `test_up_down` | 已覆盖 | 一致 |
| `test_isnt_mutable` | `test_non_mutating_operations` | 已覆盖 | 名称调整 |
| `test_set_init` | `test_set_init` | 已覆盖 | 一致 |
| `test_federation_ops` | `test_federation_relations` | 已覆盖 | 名称调整 |
| `test_intern` | `test_intern` | 已覆盖 | 一致 |
| `testExtrapolateMaxBounds` | `test_extrapolate_max_bounds` | 已覆盖 | 名称调整 |
| `test_free_clock` | `test_free_clock` | 已覆盖 | 但未覆盖跨 context 风险 |
| `test_zero_federation` | `test_zero_federation` | 已覆盖 | 一致 |
| `test_hash` | `test_hash` | 已覆盖 | 一致 |
| `test_isempty` | `test_is_empty` | 已覆盖 | 名称调整 |

补充说明：

- 当前测试新增了多组 public validation / edge-case 测试。
- 这些新增测试中，有一部分实际上固化了与历史版不同的行为，例如：
  - `Clock` 的对象比较语义
  - `VariableDifference` 的对象比较语义
  - 更明确的异常类型

## 旧 `udbm_int` 低层接口对照

### 类与暴露面

| 历史 `udbm_int` | 当前 pybind11 绑定 | 状态 | 备注 |
| --- | --- | --- | --- |
| `VarNamesAccessor` | 无公开等价物 | 未恢复 | 当前由 C++ 内部 `IndexedClockAccessor` 处理 |
| `Constraint` | `_NativeConstraint` | 部分恢复 | 私有命名，不作为兼容公开面 |
| `IntClockValuation` | 无公开等价物 | 未恢复 | Python 层直接传 `List[int]` |
| `DoubleClockValuation` | 无公开等价物 | 未恢复 | Python 层直接传 `List[float]` |
| `IntVector` | 无公开等价物 | 未恢复 | Python 层直接传 `List[int]` |
| `Federation` | `_NativeFederation` | 部分恢复 | 私有命名，方法名整体改成 snake_case |

### 旧 `Federation` 低层方法对照

| 历史 SWIG 方法 | 当前 pybind 方法 | 状态 | 备注 |
| --- | --- | --- | --- |
| `toStr` | `to_string` | 已有等价能力 | 命名变化 |
| `orOp` | `or_op` | 已有等价能力 | 命名变化 |
| `andOp` | `and_op` | 已有等价能力 | 命名变化 |
| `addOp` | `add_op` | 已有等价能力 | 命名变化 |
| `minusOp` | `minus_op` | 已有等价能力 | 命名变化 |
| `up` | `up` | 已实现 | 一致 |
| `down` | `down` | 已实现 | 一致 |
| `mergeReduce` | `merge_reduce` | 已有等价能力 | 命名变化 |
| `freeClock` | `free_clock` | 已有等价能力 | 命名变化 |
| `lt` / `gt` / `le` / `ge` / `eq` | 同名小写 | 已实现 | 一致 |
| `setZero` | `set_zero` | 已有等价能力 | 命名变化 |
| `predt` | `predt` | 已实现 | 一致 |
| `intern` | `intern` | 已实现 | 一致 |
| `setInit` | `set_init` | 已有等价能力 | 命名变化 |
| `convexHull` | `convex_hull` | 已有等价能力 | 命名变化 |
| `containsIntValuation` | `contains_int` | 已有等价能力 | 参数类型变化 |
| `containsDoubleValuation` | `contains_float` | 已有等价能力 | 参数类型变化 |
| `myExtrapolateMaxBounds` | `extrapolate_max_bounds` | 已有等价能力 | 参数类型变化，命名变化 |
| `hasZero` | `has_zero` | 已有等价能力 | 命名变化 |
| `updateValue` | `update_value` | 已有等价能力 | 命名变化 |
| `size` | `size` | 已实现 | 一致 |
| `hash` | `hash` | 已实现 | 一致 |
| `isEmpty` | `is_empty` | 已有等价能力 | 命名变化 |

结论：

- 从“高层功能是否可用”的角度看，当前低层绑定已经支撑现有 Python DSL。
- 从“是否恢复旧 `udbm_int` 公开兼容面”的角度看，当前并没有做到兼容。

## 已确认的不一致与风险

### 1. `bool` 被当成 `int`

历史行为：

- `Clock.__le__`, `__ge__`, `__lt__`, `__gt__`, `__eq__`, `__ne__` 都要求 `type(c) == int`
- `VariableDifference` 同样要求 `type(c) == int`
- `IntValuation` 要求 `type(value) == int`
- `FloatValuation` 允许 `float` 或 `int`

当前行为：

- 上述逻辑大量使用 `isinstance(..., int)` 或 `isinstance(..., (int, float))`
- 因此 `True` / `False` 会进入 DSL 和 valuation

动态验证结果：

- `c.x <= True` 当前会生成 `(x<=1)`
- `(c.x - c.y) <= True` 当前会生成 `(x-y<=1)`
- `IntValuation(c)["x"] = True` 当前可成功赋值

这属于明确的 legacy drift。

### 2. `Clock` 的对象比较语义被引入

历史行为：

- `Clock.__eq__` / `Clock.__ne__` 的目的是构造约束
- 非 `int` 输入不属于支持路径

当前行为：

- `clock == other` 对非 `int` 走对象比较
- `clock != other` 对非 `int` 也返回普通布尔值

动态验证结果：

- `context.x == context.x` 当前返回 `True`
- `context.x != context.y` 当前返回 `True`

这会把 DSL 运算符和普通对象比较混在一起。

### 3. `VariableDifference` 的对象比较语义被引入

历史行为：

- `VariableDifference.__eq__` / `__ne__` 也是 DSL 构造器
- 非 `int` 输入不属于支持路径

当前行为：

- 非 `int` 时分别返回 `False` / `True`

动态验证结果：

- `difference == object()` 当前返回 `False`
- `difference != object()` 当前返回 `True`

这同样偏离了历史 DSL 设计。

### 4. 异常模型整体发生漂移

历史行为：

- 大量参数错误由 `assert` 驱动
- 某些路径直接触发原生 `KeyError`
- 某些错误路径甚至并没有精心设计

当前行为：

- 当前实现大量改成显式 `TypeError` / `ValueError` / 带消息 `KeyError`

这不一定是坏事，但如果要严格复刻旧行为，就必须正视这类漂移。

### 5. `Context.__getitem__` 对重复名 clock 的行为不同

历史行为：

- 找不到时 `raise KeyError`
- 找到多个时 `assert(len(names) == 1)`

当前行为：

- 找不到时 `raise KeyError(arg)`
- 找到多个时 `raise KeyError("Ambiguous clock name: x")`

这属于显式化的行为变更。

### 6. `contains()` 的未知 valuation 类型处理不同

历史行为：

- 仅记录 `"Unknown valuation type"` 日志
- 随后由于局部变量未定义，实际会在后续路径炸掉

当前行为：

- 直接抛 `TypeError("Unknown valuation type.")`

这属于“修正式漂移”。

### 7. 当前测试固化了部分非 legacy 语义

当前 `test/binding/test_api.py` 新增 edge-case 测试里，有几项明确依赖当前实现而非历史实现，例如：

- `assert context.x == context.x`
- `assert context.x != context.y`
- `assert not (difference == object())`
- `assert difference != object()`

如果后续要回归 legacy parity，这些测试也要一起调整。

### 8. 旧 `udbm_int` 的公开兼容面尚未恢复

当前实现虽然有 `_NativeConstraint` 和 `_NativeFederation`，但并没有恢复历史 SWIG 层的公开模块形状：

- 没有公开 `VarNamesAccessor`
- 没有公开 `IntClockValuation`
- 没有公开 `DoubleClockValuation`
- 没有公开 `IntVector`
- 低层对象命名和方法命名都改了

这意味着高层可用，不等于低层兼容。

### 9. `freeClock()` 仍有跨 `Context` 风险

这不是“当前新引入的不一致”，而是历史风险被保留下来：

- `freeClock(clock)` 只使用 `clock.dbm_index`
- 不检查 `clock.context is self.context`

动态验证中，传入其他 `Context` 的同索引 clock，当前不会报错，而是按索引作用在当前 federation 上。

### 10. `extrapolateMaxBounds()` 仍允许不完整 bounds

这同样是旧风险延续：

- 历史版发现 bounds 个数不完整时只记日志
- 当前实现仍然只是记日志，不会拒绝执行

当前只是把日志文案改成了：

- `extrapolateMaxBounds called without bounds for every clock.`

## 后续处理 Checklist

以下项目是后续需要逐个解决或确认取舍的事项。未解决前，不应宣称已经达到严格的 `srcpy2` 行为兼容。

* [ ] 明确 `Clock` 比较运算是否必须恢复为“只接受精确 `int`”，并禁止 `bool` 进入 DSL。
* [ ] 明确 `VariableDifference` 比较运算是否必须恢复为“只接受精确 `int`”，并禁止 `bool` 进入 DSL。
* [ ] 修正 `IntValuation` 的类型检查，使其与历史版一致，不再接受 `bool`。
* [ ] 修正 `FloatValuation` 的类型检查，确认是否需要排除 `bool` 但保留 `int` 和 `float`。
* [ ] 决定 `Clock.__eq__` / `Clock.__ne__` 是否要移除当前对象比较语义，恢复为纯 DSL 入口。
* [ ] 决定 `VariableDifference.__eq__` / `VariableDifference.__ne__` 是否要移除当前对象比较语义，恢复为纯 DSL 入口。
* [ ] 系统梳理当前所有从 `assert` 改为显式异常的地方，决定哪些是允许的现代化修正，哪些必须回退以贴近 legacy。
* [ ] 决定 `Context.__getitem__` 在重复 clock 名场景下是保持当前 `KeyError("Ambiguous ...")`，还是回到更接近历史版的行为。
* [ ] 决定 `Federation.contains()` 对未知 valuation 类型的处理是保留当前 `TypeError`，还是复刻历史行为。
* [ ] 审查并调整 `test/binding/test_api.py` 中已经固化非 legacy 语义的 edge-case 测试。
* [ ] 为 `freeClock()` 增加显式同 `Context` 校验，或者正式记录为兼容保留的历史风险。
* [ ] 决定 `extrapolateMaxBounds()` 在 bounds 不完整时应继续沿用历史宽松行为，还是升级为显式异常。
* [ ] 明确项目目标是否需要恢复旧 `udbm_int` 低层公开兼容面，而不仅仅是恢复高层 DSL。
* [ ] 如果需要低层兼容，补齐 `VarNamesAccessor`、`IntClockValuation`、`DoubleClockValuation`、`IntVector` 等旧公开接口或兼容层。
* [ ] 如果不需要低层兼容，在文档中明确写出“兼容目标仅限高层 API，不包含旧 `udbm_int`”。
* [ ] 在后续每次修复后，将本文件中的状态表和 checklist 同步更新，避免文档失真。

## 当前判断

截至本次检查，比较准确的表述应当是：

> 当前仓库已经恢复了大部分历史高层 Python DSL，并且历史测试关注的核心能力基本存在；但它尚未达到严格的 `srcpy2` 行为兼容，尤其在整数类型判定、DSL 比较语义、异常模型和低层 `udbm_int` 兼容面方面仍存在明确差异。
