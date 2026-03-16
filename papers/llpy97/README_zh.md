# 导读

英文版请见 [README.md](./README.md)。

## 在整套论文中的位置

这篇论文是从“DBM 是 canonical symbolic zone”走向“DBM 在工具里如何被紧凑存储和高效比较”的关键桥梁。

如果说 `by04` 解释了 DBM 的语义，这篇论文解释的就是为什么 UDBM 里会专门有一层 minimal graph。

## 阅读时要抓住什么

建议重点抓住下面几个想法：

- 一个 closed DBM 往往包含冗余约束
- 同一个 zone 可以只用更小的一组“必要约束”来表示
- 紧凑存储不只是省内存的小技巧，它会直接影响 passed-list 管理和状态空间探索代价

对 UDBM 来说，阅读时最重要的问题是：

"哪些约束在语义上是必需的，我们如何只存这些约束？"

## 在本仓库中的对应位置

- Minimal graph API：`UDBM/include/dbm/mingraph.h`
- Minimal graph 编码与写出：`UDBM/src/mingraph_write.c`
- UDBM 自己的 README 也显式把这条文献线索列了出来：`UDBM/README.md`

更具体地说：

- `dbm_analyzeForMinDBM(...)` 对应论文里的最小约束分析
- `dbm_writeToMinDBMWithOffset(...)` 对应 DBM 的紧凑持久化表示
- `mingraph.h` 和 `mingraph_write.c` 里多种编码格式，是“紧凑表示”思想落到实现层后的结果

## 为什么它对 UDBM 特别重要

如果不读这篇论文，UDBM 里的 `mingraph` 很容易看起来像一块纯工程化的旁支代码。但它其实不是。它是对“canonical DBM 适合运算，但不一定适合存储”这一事实的理论化回应。

这在下面这些场景里都很重要：

- 紧凑序列化
- 节省内存的状态存储
- 与缩减表示之间的快速比较

## 可获取性说明

这个目录现在已经同时包含书目信息和可读 PDF。当前 publisher 侧 DOI 页面并不开放全文，但该论文历史上曾由 Uppsala DARTS 作者页面公开提供；当前 `paper.pdf` 是从该作者托管 PDF 的 Internet Archive 归档中恢复得到的。

来源链：

- DOI: https://doi.org/10.1109/REAL.1997.641265
- DBLP: https://dblp.org/rec/conf/rtss/LarsenLPY97.html
- University of Twente metadata page: https://research.utwente.nl/en/publications/efficient-verification-of-real-time-systems-compact-data-structur/
- Archived author-hosted PDF: https://web.archive.org/web/20240919204934if_/https://www2.it.uu.se/research/group/darts/papers/texts/llpw-rtss97.pdf
