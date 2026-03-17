# 论文总导读

这个目录收集的是理解 UDBM 以及本仓库 wrapper 为什么会长成现在这个样子时，最值得读的一组理论论文、工具论文和历史背景文献。

英文版请见 [README.md](./README.md)。

## 目录结构

`papers/` 下单篇论文子目录的默认结构是：

- `bibtex.bib`
  这篇论文的标准引用元数据。
- `paper.pdf`
  当存在合法且值得随仓库保存的公开全文时，放本地 PDF。
- `README.md`
  这篇论文的英文导读。
- `README_zh.md`
  这篇论文的中文导读。
- `content.md`
  当完成全文精修后，用于 GitHub 在线阅读的人类可读 Markdown 正文版本。
- `content_assets/`
  被 `content.md` 引用的图片资源，通常是抽取出的图表，或人工重新裁剪后的图表。这些资源必须遵守下文定义的强制命名规范。

个别目录在确有必要时，可以额外放少量参考文件，但以上这些文件是默认应维护齐全的标准结构。

## 维护规则

当你在这个目录里新增或更新一篇论文时：

- 为该论文建立或保留一个稳定的 citation key 目录名，例如 `by04`、`dhlp06`
- 始终提供 `bibtex.bib`
- 只有在存在合法来源且确实值得随仓库保存时，才加入 `paper.pdf`；如果没有公开全文，就在 `README.md` 和 `README_zh.md` 里明确写清楚，而不是放占位 PDF
- 保持 `README.md` 和 `README_zh.md` 成对存在、互相链接、结构基本对齐
- 论文级导读要聚焦仓库相关的阅读建议：它在整套材料中的位置、阅读重点、和代码库的对应关系、以及它为什么对 UDBM 重要
- 如果创建了 `content.md`，要把它当作面向人类读者的阅读成品，而不是粗糙的抽取结果
- 如果创建或精修 `content.md`，成品必须逐页对照 PDF 的视觉内容严格校对；要确保正文文字和公式都没有缺漏，并且必须经过明确的人工校对，不能默认抽取结果天然正确
- 把图表截图与裁图当作精修工作的核心组成部分，而不是事后补救；凡是被正文引用的截图都必须经过视觉核对，并在必要时人工重裁
- 当一篇论文进入较完整的精修阶段时，不能只修已经存在的截图；还必须检查当前覆盖页里那些本来应该出现但尚未补进来的图表，并把缺失项补齐
- `content_assets/` 中只保留 `content.md` 实际引用的资源
- 新增论文或调整阅读路径后，要同步更新这个顶层 `papers/README.md` 与 `papers/README_zh.md`

### 强制资源命名规范

下面这套规则对 `content_assets/` 下所有被 `content.md` 引用的截图类资源都是强制要求。

- 不要保留 `paper.pdf-0031-00.png` 这类抽取器生成的临时文件名
- 这些资源统一使用 `.png`
- 如果资源对应论文中的正式编号图片，命名为 `figure-<n>.png`
- 如果资源对应论文中的正式编号表格，命名为 `table-<n>.png`
- 如果资源对应论文中的正式编号 listing，命名为 `listing-<n>.png`
- 其中 `<n>` 必须与原文中的正式编号严格一致；不要为了适配本地抽取顺序、页码顺序或 `content.md` 当前只选取了部分内容而重新编号
- `figure-<n>`、`table-<n>`、`listing-<n>` 只能用于论文原文里真实存在的正式编号对象
- 如果资源不是正式编号的图、表或 listing，则命名为 `other-<n>-<slug>.png`
- 在 `other-<n>-<slug>.png` 中，`<n>` 必须是该论文目录内唯一的顺序号，`<slug>` 只能使用小写字母、数字和连字符
- 资源重命名后，必须同步更新 `content.md` 中的全部图片引用；正文里不允许继续引用抽取阶段的临时文件名

## 建议阅读路径

### 面向本仓库实现工作的主线

1. `by04`
   先建立 timed automata、zones、DBMs 和基本 symbolic 算法的基线，同时它也是 regions、zones、DBMs 与验证算法的最佳紧凑教程。
2. `dhlp06`
   接着补 federation 与 subtraction 的理论动机。
3. `bblp04`
   再补外推、抽象与终止性的理论。
4. `llpy97`
   动 `mingraph` 和紧凑存储时读它。
5. `bengtsson02`
   需要更深入的 DBM / normalization / 存储实现视角时读它。

### 面向原生 UDBM 源码理解的主线

如果目标不是只理解 wrapper 语义，而是直接贴着 UDBM 原生实现读代码，建议改用下面这条路径。

1. `by04`
   先把语义基线和算法基线立住，尤其是 DBM 章节和附录算法。
2. `bengtsson02`
   第二篇就读它；当你在追 `dbm.h`、`dbm.c`、normalization、存储和 hashing 相关设计时，它是和 UDBM 实现形态最接近的一篇长文。
3. `dhlp06`
   接着补 `fed_t`、subtraction、非凸结果和 reduction heuristic 的理论。
4. `bblp04`
   当你开始读 `Extra_M`、`Extra_LU` 及其 diagonal 变体对应的代码路径时读它。
5. `llpy97`
   当你开始读 `mingraph` 分析、紧凑编码和缩减存储比较时读它。
6. `behrmann03`
   当你开始读 priced DBM、priced federation、partition 风格 reduction 或更大的 UPPAAL 数据结构架构时，再把它补上。

### 面向工具语境的补充路径

- `lpw95`
  早期 `UPPAAL` 的 symbolic / compositional verification 基础。
- `lpy97`
  `UPPAAL` toolbox 与设计准则的短综述。
- `bdl04`
  更成熟的 `UPPAAL` 教程，偏建模模式与实际使用。
- `behrmann03`
  federation、CDD、共享、priced extension 等更大系统视角。

### 面向历史根源的补线路径

- `dill89`
  更早的 dense-time symbolic verification 前驱。
- `ad90`
  原始 timed automata 源头论文；本地条目现在还补齐了完整扫描版 `paper.pdf` 和精修后的 `content.md`。
- `rokicki93`
  normalization 文献线上的历史引用点；本地没有可读全文。

如果你只想走最短路径，直接读：
`by04 -> dhlp06 -> bblp04 -> llpy97`。

如果你想走“直接读原生 UDBM 源码”的最短路径，建议读：
`by04 -> bengtsson02 -> dhlp06 -> bblp04 -> llpy97`，
而在碰到 priced 或系统级结构时再补 `behrmann03`。

## 每篇论文分别起什么作用

### `by04`

作用：
现在应作为整套材料的主入口；它给出 timed automata 语义、regions、zones、DBMs 与验证算法的紧凑型总教程。

它为 UDBM 提供的主要理论支撑：

- 凸 zone 的语义
- 为什么实践里要从 regions 转向 zones
- canonical DBM 的视角，以及它如何编码 zone
- `delay`、`past`、`reset`、`guard intersection` 这些基本操作
- 验证工具反复需要哪些 symbolic 操作
- 为什么 normalization / bounded abstraction 重要

当前已经精修出来的本地阅读版本，具体包含：

- 从具体语法、操作语义一路讲到 reachability、timed / untimed language、bisimulation 等验证问题的完整主线
- 从 regions 过渡到 zones 的核心内容，包括 region 划分示例、zone graph、infinite zone graph，以及为什么必须做 normalization
- 章节里分别讨论了无 difference constraints 和有 difference constraints 两条 normalization 线
- DBM 章节已经覆盖 graph interpretation、canonical closure、minimal form、property checking、transformations、normalization 与内存布局
- `UPPAAL` 章节已经包含建模、product automaton 直觉、non-convex timing 示例、`(T)CTL` 查询示意和 reachability pipeline 架构图
- 附录部分已经整理出核心 DBM 算法伪代码，包括 `close`、`relation`、`up`、`down`、`and`、`free`、`reset`、`copy`、`shift`、`norm_k`、`split` 以及相关 normalization 过程

这些补充内容为什么对实现特别有用：

- 如果你在判断哪些能力应该进入 thin wrapper、哪些只是 native UDBM 的内部机制，最直接能拿来对照的往往就是附录算法和 DBM 操作章节
- 如果你想弄清 `up`、`down`、`freeClock`、`updateValue`、`contains` 以及各类 extrapolation 操作为什么会自然地出现在公开接口里，这篇基本已经把那套操作词汇完整铺开了

### `dhlp06`

作用：
给出 DBM subtraction 以及 federation 最直接的理论动机。

它为 UDBM 提供的主要理论支撑：

- zone subtraction
- 非凸结果
- 用 DBM 的并来表示结果
- subtraction 后的规约与简化

当前已经精修出来的本地阅读版本，具体包含：

- 开头那个 priorities 示例，已经很具体地展示了低优先级边为什么会导出非凸可达集，以及朴素编码为什么会把边拆开
- 预备知识部分已经把 clock constraints、DBM、zone operations 以及 basic subtraction 的并集构造重新铺了一遍
- timed automata with priorities 的 symbolic semantics 也已经整理出来，包括 `block` / `Block` 的定义，以及 `UPPAAL` 里使用的 transition priority 规则
- subtraction 章节已经覆盖 minimal constraints 改进、disjoint subtraction，以及两个简单但实际很重要的 early-exit simplification
- 两个 heuristic 小节都已经在本地稿里：一个是动态重排 split 次序的 efficient heuristic，另一个是更贵的 facet-aware heuristic
- 实验部分也已经补到本地阅读稿里，包括 Fischer priorities 例子，以及 timed games / jobshop 的性能测量，这些内容能直接说明 subtraction 质量为什么会影响实际性能，而不只是理论美观

这些补充内容为什么对实现特别有用：

- 它不只是为 `Federation.__sub__` 提供依据，也为 `reduce`、`expensiveReduce`、merge 风格 reduction 和面向 disjointness 的启发式提供了论文层面的解释
- 当你需要说明“只暴露单个 DBM 结果的高层 API 在语义上是不完整的”时，它几乎就是最直接的一篇本地依据

### `bblp04`

作用：
给出 zone-based verification 里的 lower / upper bound abstraction。

它为 UDBM 提供的主要理论支撑：

- 为什么 extrapolation 是安全的
- 为什么 extrapolation 能帮助保证终止
- 为什么会存在多种外推方案

当前已经精修完成的本地阅读稿还具体包含：

- 引言部分连同 Fig. 1 的动机例子都已经整理好，这一段直接说明了为什么把 lower / upper bounds 分开以后，可以在不丢失 reachability 精确性的前提下大幅压缩符号状态
- 阅读后文所需的预备内容已经补齐在同一份本地稿里：TA syntax、具体语义、符号语义、abstraction 的基本术语，以及后面 extrapolation 小节要用到的 DBM 回顾
- classical maximal-bound abstraction、LU-preorder 和语义抽象 `a_{≺LU}` 都已经完整保留，包括从 bisimulation 转向 simulation 的关键语义变化；这正是论文能做到“更粗但对 reachability 仍然精确”的核心
- 第 4 节的四种 extrapolation operator 都已经在本地稿里：经典 `Extra_M`、对角线增强版 `Extra_M^+`、LU 版 `Extra_LU`、以及对角线 LU 版 `Extra_LU^+`，并且保留了对应的小几何示意图和 Fig. 3 的包含关系图
- successor acceleration 那一节也已经整理出来，包括 LU-form DBM、successor computation 的成本拆解，以及用 `LU-Canonize` 替代 Floyd-Warshall 式 closure 的实现思路
- 实现与实验部分已经保留完整的 prototype-in-UPPAAL 叙述，而且 Table 1 不只是保留成图片资源，还额外做了可读的 Markdown 转写
- 最后的 concluding discussion 也已经覆盖到 asymmetric DBM storage，这一点对理解 lower/upper bounded clocks 为什么会同时影响语义、存储和性能设计很有帮助

这些补充内容为什么对实现特别有用：

- 它给出的依据不只是公开的外推方法，例如 `extrapolateMaxBounds`，还解释了为什么 binding surface 里应该存在多种外推变体，而不是只给一个含糊的“更强 normalize”操作
- 在本地论文集中，它是把 extrapolation 语义和实现侧问题直接连起来最清楚的一篇，包括 closure 代价、LU-form 的稀疏结构，以及 asymmetric DBM storage 的可能性
- 如果你需要说明 LU-bounds 不是一个“小优化开关”，而是同时关联 correctness、finiteness 和实测性能的设计点，这篇论文就是最直接的本地材料

### `llpy97`

作用：
解释 minimal graph 和 DBM 的紧凑存储。

它为 UDBM 提供的主要理论支撑：

- 为什么会有 `mingraph`
- 为什么 canonical DBM 虽然适合运算，但不一定是最佳存储形式

当前已经精修完成的本地阅读稿还具体包含：

- 摘要和引言已经整理成一条完整的动机线，从 timed automata reachability 一直过渡到论文的两个具体目标：紧凑的 constraint storage，以及对 passed list 的全局缩减
- timed automata 与 symbolic semantics 的预备内容已经保留下来，因此现在可以在本地稿里直接读懂 paper 里的 states、zones 和 DBM closure，而不用不断跳回别处补定义
- DBM 回顾和 Fig. 3 那个贯穿全文的图论例子都已经整理好，从原始 constraint graph、shortest-path closure 一直到最后的 reduced graph 都在
- weighted graph reduction 的主线已经完整保住，包括 redundant edge 的直觉、zero-cycle 带来的困难、zero-equivalence class、quotient / expansion 构造，以及核心的 shortest-path-reduction theorem
- global reduction 那一半也没有被丢掉：dynamic loops、statical loops、entry nodes、covering states，以及“只保存 covering states 也足以保证 termination”的定理都已经保留
- 论文里的 4 张图现在都已经规范化成 `figure-1.png` 到 `figure-4.png`，而 `table-1.png` 不只是保留成截图，还额外做了可读的 Markdown 转写
- 附录里 Lemma 1、Theorem 2 和 Theorem 3 的证明也被保留进本地阅读稿，而不是像粗抽取稿那样在结尾被当成噪声丢掉

这些补充内容为什么对实现特别有用：

- 它给 `mingraph` 提供了一份仓库内就地可读的解释，而且和 UDBM 真实实现的距离比一句泛泛的“DBM 可以压缩存储”要近得多
- 它把紧凑 DBM 存储和两个真正影响工具性能的成本直接连起来了：passed list 占用的内存，以及后续拿已存状态做 inclusion checking 的代价
- 当你要理解“canonical closed DBM 很适合运算，但不一定适合作为序列化、缓存或密集存储格式”时，它是本地论文集中最直接的一篇
- 它还保住了论文的第二个贡献，这一点很重要，因为这里只看 `mingraph` 只看到了半篇论文；作者同时还在优化单个 symbolic state 的大小和搜索中需要保留的 state 总数

### `bengtsson02`

作用：
从实现视角深入讨论 clocks、DBMs、states、normalization 与存储。

它为 UDBM 提供的主要理论支撑：

- symbolic exploration 背后的完整 DBM 操作集
- 带 difference constraints 的 normalization
- 存储、压缩与 hashing 的动机

这个本地 thesis 条目现在实际包含：

- 一份覆盖整本 dissertation 的 thesis 级 `content.md`
- 五个拆分出的 paper 级子目录 `paper-a/` 到 `paper-e/`，可以分别作为聚焦阅读入口
- 一条很清楚的层次：A-C 最贴近 UDBM 内部，D-E 则补上更多 UPPAAL 引擎和案例背景

如果把这五篇拆开看，它们在仓库里的分工大致是：

- paper A 解释原始 DBM 结构以及最贴近 `dbm.h` / `dbm.c` 的基础操作词汇
- paper B 解释一旦引入 clock-difference constraints，normalization 会怎样变复杂
- paper C 解释内存约简、紧凑 symbolic-state 存储，以及 `mingraph` 一类机制背后的压力
- paper D 解释 timed systems 里的 local-time semantics 和 partial-order reduction
- paper E 解释 committed locations，并用一个工业级 UPPAAL 案例展示这些算法思路的实际收益

为什么这层更细的结构有意义：

- 它让 `bengtsson02` 不再只是“一本很厚的 thesis 可以略读”，而变成一套从 DBM 内核一路通到更高层引擎设计的分层阅读地图
- 当你需要区分“核心 DBM 语义问题”和“搜索策略 / 工具语境问题”时，它是本地最方便的一组材料
- 如果说 `by04` 给的是紧凑的概念基线，那么一旦你需要实现粒度，`bengtsson02` 就是仓库里最自然的下一站

### `lpw95`

作用：
早期 `UPPAAL` 的 symbolic 与 compositional model checking 基础论文。

它为 UDBM 提供的主要理论支撑：

- 为什么求解 clock-constraint systems 是核心
- 为什么实践里 symbolic state exploration 优于显式 region 处理
- 为什么 UDBM 处在 model-checking stack 的下层而不是整套工具本身

### `lpy97`

作用：
简明介绍 `UPPAAL` toolbox 与其面向用户的设计。

它为 UDBM 提供的主要理论支撑：

- 为什么 constraint solving 与 on-the-fly reachability 是引擎重心
- 为什么可用性和可读的 symbolic 建模表达同样重要

### `bdl04`

作用：
面向实际建模、查询和模式的 `UPPAAL` 教程。

它为 UDBM 提供的主要理论支撑：

- symbolic engine 所服务的用户侧 timed-automata 方言
- 为什么高层 clock-oriented API 比原始矩阵 helper 更重要

### `behrmann03`

作用：
从更高层次综合说明 UPPAAL 周边所使用的符号数据结构。

它为 UDBM 提供的主要理论支撑：

- 为什么 unions of zones 在工具层面重要
- 为什么 CDD 曾被作为替代方案探索
- 为什么共享、存储布局和 priced 扩展重要

### `dill89`

作用：
从 timing assumptions 走向 symbolic dense-time verification 的历史前驱。

它为 UDBM 提供的主要理论支撑：

- 早期 symbolic timing-state 表示的思路
- 为什么要把 clock valuation 的集合当作符号对象来表示

### `ad90`

作用：
timed automata 的原始语言论源头。

它为 UDBM 提供的主要理论支撑：

- 后来各种 symbolic technique 底下的 `clock / guard / reset` 模型
- zone 与 DBM 方法后来实际编码的 formal timed-automaton 对象

当前已经精修出来的本地阅读版本，具体包含：

- 现在本地已经有完整的 14 页扫描版 `paper.pdf`，不再只是一个很短的 preview
- 一份人工精修的 `content.md`，覆盖了摘要、trace semantics 的铺垫、timed traces、timed automata、closure properties、基于 region 的 emptiness 推导、inclusion 的不可判定性，以及 deterministic timed Muller automata
- 论文里用来解释 bounded response 和精确时间间隔性质的几个小 automaton 示例
- emptiness 小节里的 region equivalence 示意图，并将其作为可对照的图片资源保留下来

这些补充内容为什么对实现特别有用：

- 它给仓库内部提供了一份就地可读的“zone 之前的语义源头”，有助于在重建历史 `Context` / `Clock` / `Federation` 风格 API 时不偏离原模型
- 当你要确认 clocks、guards、resets、timed traces 与 timed-language 问题才是后来 DBM 操作真正服务的对象时，它是最直接的一份本地材料
- 它也能更直接地说明：Python 高层接口保持 clock-oriented，不只是为了语法好看，而是为了忠实反映原始 timed automata 模型

### `rokicki93`

作用：
normalization 文献线里的历史引用点。

它为 UDBM 提供的主要理论支撑：

- 主要体现在后来被 `by04` 与 `bengtsson02` 继续引用的 normalization 背景

说明：
`rokicki93` 在最初收集阶段和本次补充尝试中，都没有找到合法公开可下载的全文 PDF。

## 这些论文与本仓库 Python wrapper 的关系

本仓库恢复中的 Python API `pyudbm/binding/udbm.py`，并不是在包一层原始矩阵函数而已。它试图在现代绑定层之上重建历史上的 `Context` / `Clock` / `Federation` 编程模型。

因此：

- `ad90` 和 `dill89` 解释了以 clock 为中心的 symbolic reasoning 的更早语义根源
- `by04` 解释了这个 DSL 所操作的单个 zone / DBM 层
- `dhlp06` 说明为什么 `Federation` 必须保持为真正的 union 对象，而不能退化成单个 DBM
- `bblp04` 说明为什么 `extrapolateMaxBounds` 这类方法应该存在于公开接口里
- `llpy97` 和 `bengtsson02` 说明原生 UDBM 中已经存在的压缩存储与实现机制背后的理论
- `lpw95`、`lpy97`、`bdl04` 和 `behrmann03` 说明这个引擎所在的更大 `UPPAAL` 工具语境，以及用户侧对它的期待

## 实用建议

如果你是为了本仓库的实现工作来读这些论文，建议这样用：

- 先看 `by04/README_zh.md`
- 再看 `dhlp06/README_zh.md`
- 之后看 `bblp04/README_zh.md`
- 当你碰 `mingraph`、存储或更底层 DBM 机制时，去看 `llpy97/README_zh.md` 和 `bengtsson02/README_zh.md`
- 当你在想高层 API 的易用性和建模风格时，看 `lpy97/README_zh.md` 与 `bdl04/README_zh.md`
- 当你需要更大的 `UPPAAL` 架构语境时，看 `behrmann03/README_zh.md`

如果你是在直接阅读原生 UDBM 源码，可以按下面这个“文件到论文”的对应关系来查：

- `UDBM/include/dbm/dbm.h`、`UDBM/src/dbm.c`、`UDBM/docs/manual.tex`：先读 `by04`，再读 `bengtsson02`；如果是 extrapolation 相关代码路径，再补 `bblp04`。
- `UDBM/include/dbm/fed.h`、`UDBM/src/fed.cpp`、`UDBM/src/fed_dbm.cpp`：先读 `dhlp06`；如果想补 unions of zones 的更大架构语境，再读 `behrmann03`。
- `UDBM/include/dbm/mingraph.h` 和 `UDBM/src/mingraph*.c`：先读 `llpy97`，再读 `bengtsson02`。
- `UDBM/include/dbm/priced.h`、`UDBM/include/dbm/pfed.h`、`UDBM/src/priced.cpp`、`UDBM/src/pfed.cpp`、`UDBM/src/infimum.cpp`：先读 `behrmann03` 里的 priced-zone / priced timed automata 相关部分，再回来看代码。

## 论文内容精修流程

当你要把某篇论文整理成可发布的 Markdown 阅读版本时，使用如下流程。

### 目标

目标不是保留一个粗糙的机器抽取稿，而是产出一个可以直接放到 GitHub 上供人阅读的 `content.md`：结构清晰、公式正确、图表位置正确、caption 能和上下文对照起来。

更重要的是，这里所说的“精修”首先指向忠实性，而不是宽松的改写、概述或二次创作。最终的 `content.md` 必须逐页对照原始 PDF 核验，并且与原文保持严格一致。只要某一页还没有被单独、仔细地和源 PDF 对过，这篇论文就不能算精修完成。

只有 Step 1 是抽取步骤。从 Step 2 到 Step 6，整个流程都必须纯粹依赖 LLM 自身的文本理解能力与页面级视觉阅读能力来完成。不要在这些后续步骤里再使用额外的粗糙清洗脚本、批处理启发式规则或其他工具式后处理。

### Step 1：导出两种工作视图

始终同时导出：

1. 一份 Markdown 文字草稿
2. 一份逐页页面图像草稿

直接对 PDF 文件使用 `tools.papers_to_content`。这个工具现在已经与 `papers/` 目录结构解耦，因此需要显式传入路径。

示例：

```bash
python -m tools.papers_to_content \
  -i papers/by04/paper.pdf \
  -ot text \
  -o papers/by04/content.md

python -m tools.papers_to_content \
  -i papers/by04/paper.pdf \
  -ot image \
  -o /tmp/by04-pages
```

说明：

- `text` 模式会写出一个 Markdown 文件，并默认在旁边生成类似 `content_assets/` 的资源目录
- `image` 模式会把每一页渲染成图像，供视觉校对
- 不要把页面图像直接导出到 `papers/` 下的论文子目录里；逐页图像通常很大，应当导出到临时路径，例如 `/tmp/...`
- 每次都要显式指定输出路径，不要假定存在 batch 模式或与仓库路径绑定的默认行为

### Step 2：仅依赖 LLM 的文本与视觉能力逐页精修

从这一步开始，精修必须由 LLM 直接阅读文字草稿和逐页页面图像来完成。不要把草稿再交给其他粗处理工具去“自动清洗”。

这个逐页核对是硬性要求。“整体看起来差不多对”并不够。每一页都必须反复和 PDF 对齐，直到该页对应的 Markdown 在内容上对源页面保持严格忠实。

如果论文页数很多，必要时应当分批精修。不要默认长论文一定要一次性全量处理；可以按章节、按小节、按页码范围逐批处理，只要每一批都保持足够细致且前后一致即可。

对每一页都要：

- 对照抽取出的 Markdown 和真实页面版式与视觉内容
- 重写错误的段落边界、标题、列表、表格、脚注和引用
- 把损坏的行内公式和展示公式改写成正确的 LaTeX
- 删除抽取噪声，例如分页标记、错误连字、重复片段、OCR 伪影和错误符号
- 确保术语、记号和变量名与原 PDF 一致
- 确保该页精修后的 Markdown 在实质内容、结构、公式以及图表引用上都和源页面对得上，而不是只是做一个“意思差不多”的转述

不要接受“差不多能读”的结果。如果某个公式、符号或段落有歧义，必须通过视觉阅读页面并仔细重写来解决。

### Step 3：仅依赖 LLM 的视觉判断校验图表

凡是在 `content.md` 中引用的图和表，都必须和 PDF 做视觉比对；而且这个校验过程也必须由 LLM 直接阅读页面图像来完成，而不是依赖自动启发式判断。

但“校验过了”本身还不够。这一步只负责发现问题；只要在这里发现图表资源有错误、残缺、过松、拆分不当、合并不当，或者压根缺失，就必须继续进入下面单独的、强制性的“校对后重做/替换”步骤，把问题真正修掉。仅仅发现这些问题，不能算精修完成。

图表是精修结果里的高优先级验收项。正文就算已经清理得很干净，只要截图还存在裁切错误、内容残缺、缺少 caption，或者插入位置不严格对应原文，都不能算精修完成。

图表校验还必须包含“补全”这一层要求。不能只把 `content.md` 里已经出现的图片修漂亮，而不去重新阅读页面图像检查是否还有漏掉的图或表。只要正文已经讨论了 Fig. *n* 或 Table *n*，但 `content.md` 里没有对应资源和插图，这就是精修失败，必须补上。

尤其要检查：

- 图表是否补全，不只是裁切是否好看；要把 PDF 里实际出现的图表清单和 `content.md` / `content_assets/` 里当前已有的图表清单做对比
- 抽取出的截图是否真的是目标图或目标表
- 裁剪在四个边上是否都完整，不能截掉坐标轴、标签、图例、表格边框、最右侧节点、顶部标题、底部行等任何语义上重要的内容
- 裁剪是否过松，不能把无关段落、相邻图、章节标题、页眉页脚等多余上下文一并带进来；如果目标图可以单独裁干净，就不要保留大块无关区域
- 资源的阅读方向是否正确；如果原 PDF 里某个图或表因为页面横置、竖排等原因是侧着的，就必须在最终资源里旋正或重做，不能把一个侧着的图表原样插进 `content.md`
- 原始 PDF 里的 caption 在版面允许时是否已经一并裁进图片
- `content.md` 里图片下方是否也保留了一份清晰可读的 Markdown caption；也就是说，图内 caption 和正文 caption 都应当存在，方便人类核查，也方便 LLM 检索定位
- 图表在正文中的插入位置是否与讨论它的原文位置严格对应，而不是只要放在同一节里就算通过
- 如果同一页上有多个在正文中分别讨论的图，是否拆成了多个独立资源；除非原论文本来就是一个不可分割的组合图，否则不要偷懒保留成一张混合截图

推荐采用如下截图工作流：

- 先重新阅读所覆盖页的页面图像，建立一份图表清单；如果有帮助，可以用 PDF 文本层辅助定位 figure 编号或页码，但页面图像才是最终依据
- 把这份 PDF 侧的图表清单和当前 `content.md` / `content_assets/` 里的已有图表做对账
- 如果存在缺图，先补齐缺失项，再谈裁切质量；不能接受“正文提到了图，但图根本没插”的状态
- 每个被引用的图片资源都要看原尺寸，不要只看缩略图
- 对缺失图，先做一轮粗裁候选，再成组检查一遍，最后逐张原尺寸复核后再定稿
- 把资源和源页面逐一对照，并且有意识地检查四条边
- 只要某一边有残缺，或者混入了多余上下文，就重新裁切并替换资源，不接受“差不多能看”的结果
- 如果图或表因为原页面布局而是侧着的，重做时要一并纠正阅读方向；不要把一个竖着放、横着看的资源直接塞进 `content.md`
- 如果图像插入点横跨了 Markdown 的分页结构，要同时调整页标与图片落位，使整体顺序继续忠实于 PDF
- 如果重裁后图的拆分方式、顺序或位置发生变化，要同步更新 `content.md`
- 新增图片时，要在原文开始讨论该图的位置同时补上图片引用和明确的 Markdown caption
- 删除那些已经被替换、但不再被正文引用的旧资源
- 最后做一次一致性检查：`content.md` 里引用的每一张图都必须真实存在于 `content_assets/` 中，`content_assets/` 里也不应残留未使用的过期截图，而且 `content.md` 里当前出现的 figure 编号也不应再因为漏图而留下明显断档

### Step 4：把图表校对后的重做/替换作为单独且必须的环节

这一步是独立的强制步骤，不是可选的收尾清理。只要 Step 3 发现了图表问题，Step 4 就必须真的把资源修好；否则这篇论文不能算精修完成。

下面这些情况都必须进入重做/替换：

- 抽取出来的截图根本不是目标图或目标表
- 任意一条边裁残了语义上重要的内容
- 裁切过松，把无关正文、相邻图、页眉页脚等多余内容一起带了进来
- 资源保留成了错误的阅读方向，例如来自横页或竖排版面的图表仍然侧着，没有被旋正
- 原 PDF 里的 caption 本来应该随图保留，但当前资源没保住
- 一个原本应当整体呈现的单个图，被错误拆成了零散碎片
- 多个应当分开讨论的图，被错误保留成了一张混合截图
- 正文已经讨论了某个图或表，但资源根本缺失
- 某个表虽然在正文里做了粗略转写，但仍然缺少用于和 PDF 对照的视觉资源

一旦存在这类问题，不要保留错误资源。应当手工重新截图、重新裁剪，或者直接重做该图/表资源；把修正后的文件写回 `content_assets/`；同步更新 `content.md` 的引用；并删除那些已经被替换、但不再使用的旧资源。

如果某张图或表被重做了，写出新资源后还必须再按原尺寸做一次视觉复核。不要假定“第二次裁切大概就对了”。

如果重做后的资源改变了图的粒度、顺序或落位，还必须同步修改 `content.md`。例如：

- 如果若干碎片其实应当恢复成一张完整原图，就要合并成一个连贯资源
- 如果一张混合截图其实应当拆成多个分别讨论的图，就要拆分资源，并把 caption 与插入位置一起调回原文对应位置
- 如果某个表既需要保留可读的 Markdown 转写，也需要保留用于核对的视觉资源，那就两者都保留，但不能省略视觉资源本身

图表只做“检查”而没有做到“修正并替换”，不算通过精修验收。资源本身必须被修到可发布、可核对的状态。

### Step 5：通过 LLM 编辑产出 GitHub 可读终稿

最终的 `content.md` 应当读起来像一份经过认真编辑的技术文稿，而不是 OCR 输出。这一步依然必须是纯粹的 LLM 编辑工作，而不是机械式的大范围清洗。

GitHub 可读性并不意味着可以放松忠实性要求。所有可读性优化都只能建立在逐页严格对齐原 PDF 的前提上，不能改变原文内容、顺序、记号或图表对应关系。

对于特别长的论文，这一步也可以分批完成。核心要求是最终的编辑质量与前后一致性，而不是强行要求一次性全部做完。

具体要求：

- 使用正常的 Markdown 标题层级和段落间距
- 在需要时使用 LaTeX 书写行内与展示公式
- 保持图表 caption 清晰、明确、可读；只要使用了图片资源，就优先保持“图内有原 caption，正文里也有 Markdown caption”的双 caption 形式
- 保持论文原有的逻辑顺序
- 不要保留原始分页标记、抽取诊断信息或工具内部噪声

当 PDF 本身不完整、质量差，或者只是 preview 时，要在 `content.md` 顶部附近明确说明，并且只转写那些能够从现有页面中合理确认的内容。

### Step 6：将 LLM 的编辑判断视为硬性要求

这个流程本质上是编辑流程，不是纯机械流程。

必须遵守的原则：

- 工具只用于在 Step 1 里拿到初始文字草稿和页面图像草稿
- Step 2 到 Step 6 的所有后续精修都必须依赖 LLM 自身的文本推理与视觉推理
- 不要用大范围自动清洗来替代基于页面理解的编辑修订
- 宁可细致地人工修正，也不要依赖粗糙自动化
- 必须把“逐页与源 PDF 严格一致”当作验收标准，而不是尽力而为的目标

如果抽取器输出的内容和页面视觉显示的内容冲突，应当以页面为准，修正 Markdown。
