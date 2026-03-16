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
  被 `content.md` 引用的图片资源，通常是抽取出的图表，或人工重新裁剪后的图表。

个别目录在确有必要时，可以额外放少量参考文件，但以上这些文件是默认应维护齐全的标准结构。

## 维护规则

当你在这个目录里新增或更新一篇论文时：

- 为该论文建立或保留一个稳定的 citation key 目录名，例如 `by04`、`dhlp06`
- 始终提供 `bibtex.bib`
- 只有在存在合法来源且确实值得随仓库保存时，才加入 `paper.pdf`；如果没有公开全文，就在 `README.md` 和 `README_zh.md` 里明确写清楚，而不是放占位 PDF
- 保持 `README.md` 和 `README_zh.md` 成对存在、互相链接、结构基本对齐
- 论文级导读要聚焦仓库相关的阅读建议：它在整套材料中的位置、阅读重点、和代码库的对应关系、以及它为什么对 UDBM 重要
- 如果创建了 `content.md`，要把它当作面向人类读者的阅读成品，而不是粗糙的抽取结果
- 把图表截图与裁图当作精修工作的核心组成部分，而不是事后补救；凡是被正文引用的截图都必须经过视觉核对，并在必要时人工重裁
- `content_assets/` 中只保留 `content.md` 实际引用的资源
- 新增论文或调整阅读路径后，要同步更新这个顶层 `papers/README.md` 与 `papers/README_zh.md`

## 建议阅读路径

### 面向本仓库实现工作的主线

1. `ta_tools`
   先建立 timed automata、zones、DBMs 和基本 symbolic 算法的基线。
2. `by04`
   然后补 regions、zones、DBMs 和验证算法的最佳紧凑教程。
3. `dhlp06`
   接着补 federation 与 subtraction 的理论动机。
4. `bblp04`
   再补外推、抽象与终止性的理论。
5. `llpy97`
   动 `mingraph` 和紧凑存储时读它。
6. `bengtsson02`
   需要更深入的 DBM / normalization / 存储实现视角时读它。

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
  原始 timed automata 源头论文。
- `rokicki93`
  normalization 文献线上的历史引用点；本地没有可读全文。

如果你只想走最短路径，直接读：
`ta_tools -> by04 -> dhlp06 -> bblp04 -> llpy97`。

## 每篇论文分别起什么作用

### `ta_tools`

作用：
提供 timed automata 语义、zones、DBMs 和基本 symbolic 算法的基础。

它为 UDBM 提供的主要理论支撑：

- 凸 zone 的语义
- canonical DBM 的视角
- `delay`、`past`、`reset`、`guard intersection` 这些基本操作

### `by04`

作用：
给出 timed automata 语义、regions、zones、DBMs 与验证算法的紧凑型总教程。

它为 UDBM 提供的主要理论支撑：

- 为什么实践里要从 regions 转向 zones
- canonical DBM 如何编码 zone
- 验证工具反复需要哪些 symbolic 操作
- 为什么 normalization / bounded abstraction 重要

### `dhlp06`

作用：
给出 DBM subtraction 以及 federation 最直接的理论动机。

它为 UDBM 提供的主要理论支撑：

- zone subtraction
- 非凸结果
- 用 DBM 的并来表示结果
- subtraction 后的规约与简化

### `bblp04`

作用：
给出 zone-based verification 里的 lower / upper bound abstraction。

它为 UDBM 提供的主要理论支撑：

- 为什么 extrapolation 是安全的
- 为什么 extrapolation 能帮助保证终止
- 为什么会存在多种外推方案

### `llpy97`

作用：
解释 minimal graph 和 DBM 的紧凑存储。

它为 UDBM 提供的主要理论支撑：

- 为什么会有 `mingraph`
- 为什么 canonical DBM 虽然适合运算，但不一定是最佳存储形式

### `bengtsson02`

作用：
从实现视角深入讨论 clocks、DBMs、states、normalization 与存储。

它为 UDBM 提供的主要理论支撑：

- symbolic exploration 背后的完整 DBM 操作集
- 带 difference constraints 的 normalization
- 存储、压缩与 hashing 的动机

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
- `ta_tools` 和 `by04` 解释了这个 DSL 所操作的单个 zone / DBM 层
- `dhlp06` 说明为什么 `Federation` 必须保持为真正的 union 对象，而不能退化成单个 DBM
- `bblp04` 说明为什么 `extrapolateMaxBounds` 这类方法应该存在于公开接口里
- `llpy97` 和 `bengtsson02` 说明原生 UDBM 中已经存在的压缩存储与实现机制背后的理论
- `lpw95`、`lpy97`、`bdl04` 和 `behrmann03` 说明这个引擎所在的更大 `UPPAAL` 工具语境，以及用户侧对它的期待

## 实用建议

如果你是为了本仓库的实现工作来读这些论文，建议这样用：

- 先看 `ta_tools/README_zh.md`
- 然后看 `by04/README_zh.md`
- 再看 `dhlp06/README_zh.md`
- 之后看 `bblp04/README_zh.md`
- 当你碰 `mingraph`、存储或更底层 DBM 机制时，去看 `llpy97/README_zh.md` 和 `bengtsson02/README_zh.md`
- 当你在想高层 API 的易用性和建模风格时，看 `lpy97/README_zh.md` 与 `bdl04/README_zh.md`
- 当你需要更大的 `UPPAAL` 架构语境时，看 `behrmann03/README_zh.md`

## 论文内容精修流程

当你要把某篇论文整理成可发布的 Markdown 阅读版本时，使用如下流程。

### 目标

目标不是保留一个粗糙的机器抽取稿，而是产出一个可以直接放到 GitHub 上供人阅读的 `content.md`：结构清晰、公式正确、图表位置正确、caption 能和上下文对照起来。

更重要的是，这里所说的“精修”首先指向忠实性，而不是宽松的改写、概述或二次创作。最终的 `content.md` 必须逐页对照原始 PDF 核验，并且与原文保持严格一致。只要某一页还没有被单独、仔细地和源 PDF 对过，这篇论文就不能算精修完成。

只有 Step 1 是抽取步骤。从 Step 2 到 Step 5，整个流程都必须纯粹依赖 LLM 自身的文本理解能力与页面级视觉阅读能力来完成。不要在这些后续步骤里再使用额外的粗糙清洗脚本、批处理启发式规则或其他工具式后处理。

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

图表是精修结果里的高优先级验收项。正文就算已经清理得很干净，只要截图还存在裁切错误、内容残缺、缺少 caption，或者插入位置不严格对应原文，都不能算精修完成。

尤其要检查：

- 抽取出的截图是否真的是目标图或目标表
- 裁剪在四个边上是否都完整，不能截掉坐标轴、标签、图例、表格边框、最右侧节点、顶部标题、底部行等任何语义上重要的内容
- 裁剪是否过松，不能把无关段落、相邻图、章节标题、页眉页脚等多余上下文一并带进来；如果目标图可以单独裁干净，就不要保留大块无关区域
- 原始 PDF 里的 caption 在版面允许时是否已经一并裁进图片
- `content.md` 里图片下方是否也保留了一份清晰可读的 Markdown caption；也就是说，图内 caption 和正文 caption 都应当存在，方便人类核查，也方便 LLM 检索定位
- 图表在正文中的插入位置是否与讨论它的原文位置严格对应，而不是只要放在同一节里就算通过
- 如果同一页上有多个在正文中分别讨论的图，是否拆成了多个独立资源；除非原论文本来就是一个不可分割的组合图，否则不要偷懒保留成一张混合截图

推荐采用如下截图工作流：

- 每个被引用的图片资源都要看原尺寸，不要只看缩略图
- 把资源和源页面逐一对照，并且有意识地检查四条边
- 只要某一边有残缺，或者混入了多余上下文，就重新裁切并替换资源，不接受“差不多能看”的结果
- 如果重裁后图的拆分方式、顺序或位置发生变化，要同步更新 `content.md`
- 删除那些已经被替换、但不再被正文引用的旧资源
- 最后做一次一致性检查：`content.md` 里引用的每一张图都必须真实存在于 `content_assets/` 中，而 `content_assets/` 里也不应残留未使用的过期截图

抽取脚本可能会截错图，也可能裁剪质量很差。出现这种情况时，不要保留错误资源。应当手工重新截图或重新裁剪页面内容，替换 `content_assets/` 中的文件，并更新 `content.md` 的引用。

### Step 4：通过 LLM 编辑产出 GitHub 可读终稿

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

### Step 5：将 LLM 的编辑判断视为硬性要求

这个流程本质上是编辑流程，不是纯机械流程。

必须遵守的原则：

- 工具只用于在 Step 1 里拿到初始文字草稿和页面图像草稿
- Step 2 到 Step 5 的所有后续精修都必须依赖 LLM 自身的文本推理与视觉推理
- 不要用大范围自动清洗来替代基于页面理解的编辑修订
- 宁可细致地人工修正，也不要依赖粗糙自动化
- 必须把“逐页与源 PDF 严格一致”当作验收标准，而不是尽力而为的目标

如果抽取器输出的内容和页面视觉显示的内容冲突，应当以页面为准，修正 Markdown。
