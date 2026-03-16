# 导读

## 在整套论文中的位置

这个条目在本仓库里主要是一个历史引用节点。仓库中的后续教程型文献，尤其是 `by04` 和 `bengtsson02`，在 normalization 这条文献线上都引用了 `Rok93`。

由于 thesis 本文目前并不在本目录可读获取，这个目录更适合被当成 citation anchor 和历史线索，而不是主要阅读入口。

## 阅读时要抓住什么

如果你在别处拿到了 thesis，建议重点关注：

- 从 timed-circuit verification 走向 symbolic timing constraints 的历史路线
- 早期基于 normalization 的有限抽象
- 后来的 zone-normalization 工作如何继承 timed-circuit verification 中的思路

对本仓库来说，最关键的问题反而更窄：

"为什么当前以 timed automata 和 DBM 为核心的 UDBM，参考文献里仍然会保留这篇 thesis？"

## 在本仓库中的对应位置

- UDBM 自己的参考文献列表：`UDBM/README.md`
- 本目录下后续引用 normalization 文献线的教程论文：`papers/by04/paper.pdf`、`papers/bengtsson02/paper.pdf`
- 当代的有界 symbolic 操作：`UDBM/include/dbm/dbm.h`、`pyudbm/binding/udbm.py`

更具体地说：

- 这篇 thesis 属于 normalization 风格有限抽象的历史背景
- 而本目录中的后续论文，才是把这条历史线真正接到今天 UDBM 的 DBM 操作上的实用桥梁

## 为什么它对 UDBM 特别重要

它的重要性主要体现在历史溯源上。它解释了为什么 UDBM 的参考文献里，会出现一些早于现代 `UPPAAL` 风格 DBM 库形态的工作。

在实践里，如果你想尽快搞清 normalization 的可操作故事，通常会从 `by04`、`bblp04` 和 `bengtsson02` 学得更快。

## 如何阅读

除非你特别需要补齐早期历史引用链，否则优先读后续论文更合适。

可获取性说明：
在最初收集阶段没有找到合法公开全文；本次更新也额外尝试了一轮检索，仍未找到可公开下载的 PDF。
