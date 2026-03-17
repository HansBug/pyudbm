# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这篇 thesis 不是单一算法论文，而是横跨了 UPPAAL 体系里的三类工作：

- 大型有限状态 `visualSTATE` 模型的符号验证
- timed systems 的替代型符号数据结构，尤其是 CDD
- priced timed automata 的最优代价可达性

对 UDBM 相关工作来说，最有价值的是 CDD 那篇以及后面三篇 priced timed automata 论文。它们最能解释为什么 UPPAAL 这条技术线会长期关注非凸 symbolic set、共享、以及带代价的符号状态表示。

## 内嵌子论文架构

这个条目现在分成两层：

- `papers/behrmann03/` 根目录下的 thesis 级材料，包括完整的 [paper.pdf](./paper.pdf)、thesis 级 README，以及整理后的 [content.md](./content.md)
- `paper-intro/` 以及 `paper-a/` 到 `paper-f/` 这些二级子目录

仓库里仍然把根目录下的 thesis PDF 视为这篇条目的规范完整版本。新增的这些子目录把 thesis 的 introduction 部分以及其中列出的六篇子论文分别拆开，便于单独阅读和引用。现在每个子目录都已经有：

- `paper.pdf`
- `README.md`
- `README_zh.md`

当前二级结构对应关系如下：

- [paper-intro/README.md](./paper-intro/README.md)：thesis introduction、motivation、data-structure overview、UPPAAL architecture 与 papers A-F summary（根 PDF 第 15-54 页）
- [paper-a/README.md](./paper-a/README.md)：`Verification of Large State/Event Systems using Compositionality and Dependency Analysis`（根 PDF 第 55-76 页）
- [paper-b/README.md](./paper-b/README.md)：`Verification of Hierarchical State/Event Systems using Reusability and Compositionality`（根 PDF 第 77-98 页）
- [paper-c/README.md](./paper-c/README.md)：`Efficient Timed Reachability Analysis using Clock Difference Diagrams`（根 PDF 第 99-114 页）
- [paper-d/README.md](./paper-d/README.md)：`Minimum-Cost Reachability for Priced Timed Automata`（根 PDF 第 115-138 页）
- [paper-e/README.md](./paper-e/README.md)：`Efficient Guiding Towards Cost-Optimality in Uppaal`（根 PDF 第 139-162 页）
- [paper-f/README.md](./paper-f/README.md)：`As Cheap as Possible: Efficient Cost-Optimal Reachability for Priced Timed Automata`（根 PDF 第 163-193 页）

如果你需要读完整 dissertation 语境或者统一参考文献，请留在根目录阅读。如果你想把 introduction 部分单独读出来，就看 [paper-intro/README.md](./paper-intro/README.md)。若你只是想单独跟某一篇子论文，直接进入对应的 `paper-a` 到 `paper-f` 子目录更合适。

## 这六篇子论文之间是什么关系

这六篇并不是一条完全单线的故事；连同拆出来的 introduction 一起看，更像四层结构。

- [paper-intro/README.md](./paper-intro/README.md) 是 thesis 级 framing 层。
  它包含 motivation、modeling formalism overview、data-structure overview、`The Making of Uppaal`，以及 papers A-F 的 thesis summary。
- [paper-a/README.md](./paper-a/README.md) 和 [paper-b/README.md](./paper-b/README.md) 属于 `visualSTATE` / ROBDD 簇。
  这两篇更像是 UDBM 之前的背景：先做大型有限状态符号验证，再把层次化复用叠上去。
- [paper-c/README.md](./paper-c/README.md) 是 CDD 桥接论文。
  从这一篇开始，论文才明显进入 UDBM 风格的问题：非凸 symbolic set、zone 的并、存储、以及 symbolic-state 压缩。
- [paper-d/README.md](./paper-d/README.md)、[paper-e/README.md](./paper-e/README.md) 和 [paper-f/README.md](./paper-f/README.md) 是 priced timed automata 簇。
  它们从 priced regions 的可判定性出发，走到均匀价格模型上的 DBM 实现，再走到一般线性价格情形下的 priced zones。

如果你想按最贴近 UDBM 的路径读这篇 thesis，建议顺序是：

1. [paper-intro/README.md](./paper-intro/README.md)
2. [paper-c/README.md](./paper-c/README.md)
3. [paper-d/README.md](./paper-d/README.md)
4. [paper-e/README.md](./paper-e/README.md)
5. [paper-f/README.md](./paper-f/README.md)

Paper A-B 主要用来补作者的符号模型检测背景和工具工程风格。

## 六篇子论文各自补什么

### Paper A

标题：
`Verification of Large State/Event Systems using Compositionality and Dependency Analysis`

对仓库的价值：

- 这是 timed systems 之前的组合式符号搜索背景
- 如果你想理解 dependency analysis 和 symbolic reuse 这类思路后来如何影响验证引擎设计，它很有参考价值

### Paper B

标题：
`Verification of Hierarchical State/Event Systems using Reusability and Compositionality`

对仓库的价值：

- 它把 paper A 那套符号验证思路扩展到了层次化系统
- 更适合作为工具架构和结构化状态空间分解的背景材料，而不是直接的 UDBM 论文

### Paper C

标题：
`Efficient Timed Reachability Analysis using Clock Difference Diagrams`

对仓库的价值：

- 这是本地最直接讨论 CDD、zones 的并以及非凸 symbolic set 紧凑表示的一篇
- 当你需要解释“有限个 zone 的并”为什么是一个真正的算法对象，而不只是包装层便利接口时，它最重要

### Paper D

标题：
`Minimum-Cost Reachability for Priced Timed Automata`

对仓库的价值：

- 它用 priced regions 建立了 thesis 里第一条 priced timed automata 最优代价可达性路线
- 虽然实现感不如 E-F 两篇强，但它是后续 priced-zone 工作的理论前驱

### Paper E

标题：
`Efficient Guiding Towards Cost-Optimality in Uppaal`

对仓库的价值：

- 这是从普通 DBM 机械到 UPPAAL 中实际代价引导搜索之间最直接的一座桥
- 当你关心 zone-based symbolic state、搜索顺序和 branch-and-bound 风格启发式如何在真实引擎里配合时，这篇很关键

### Paper F

标题：
`As Cheap as Possible: Efficient Cost-Optimal Reachability for Priced Timed Automata`

对仓库的价值：

- 它是 thesis 里和 priced zones、facets、以及把普通 zone machinery 提升到一般线性价格最优可达性最接近的一篇
- 如果你想找一篇最像“经典 DBM / zone 工具链的 priced 扩展”的本地论文，优先看它

## 阅读时要抓住什么

不建议把整本 thesis 等权来读。对 UDBM 工作来说，建议重点关注：

- CDD 对有限个 zone 并集的处理
- symbolic-state 表示背后的存储与共享动机
- 从 priced regions 到基于 DBM 的 priced search，再到 priced zones 的演进
- 偏理论的 symbolic object 和偏实现友好的 symbolic object 之间的区别

对本仓库来说，最关键的问题是：

"UPPAAL 这条技术线里，哪些非凸和带价格的 symbolic structure 重要到值得变成一等数据结构？"

## 在本仓库中的对应位置

- Federation 类型与操作：`UDBM/include/dbm/fed.h`
- Federation 实现：`UDBM/src/fed.cpp`
- Priced federation 类型：`UDBM/include/dbm/pfed.h`
- 面向 partition 的规约支持：`UDBM/include/dbm/partition.h`、`UDBM/src/partition.cpp`
- Python 高层 `Federation` 包装：`pyudbm/binding/udbm.py`

更具体地说：

- paper C 最清楚地讨论了“非凸 symbolic set 不能只看成单个 DBM”这件事
- papers D-F 解释了为什么 priced symbolic state representation 会和普通 zone 操作并存
- thesis 里对存储和共享的讨论，有助于理解更广义的 hashing、interning 风格思路，以及紧凑 symbolic representation

## 为什么它对 UDBM 特别重要

这篇 thesis 不一定直接对应每一个 UDBM API，但它给出了一个架构层面的答案：为什么 UPPAAL 生态最后会超出“每次只处理一个 DBM”。

如果你想理解下面这些问题，它会很有帮助：

- 为什么有限个 zone 的并会反复出现
- 为什么 CDD 会被拿来和 DBM 路线并行探索
- 为什么 priced 扩展会自然地和普通 federation 支持放在一起

## 如何阅读

建议把它当成选择性深挖的参考。

- 如果你想先看 thesis 层面对六篇论文为什么会放在一起的解释，先读 [paper-intro/README.md](./paper-intro/README.md)。
- 如果你的问题是非凸 symbolic set、CDD 或者 plain DBM list 的替代方案，先看 [paper-c/README.md](./paper-c/README.md)。
- 如果你的问题是最优代价可达性和 priced 扩展，重点看 [paper-d/README.md](./paper-d/README.md)、[paper-e/README.md](./paper-e/README.md) 和 [paper-f/README.md](./paper-f/README.md)。
- 如果你想补的是 thesis 更早期的符号模型检测背景，再看 [paper-a/README.md](./paper-a/README.md) 和 [paper-b/README.md](./paper-b/README.md)。
