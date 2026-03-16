# Reading Guide

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Position in the stack

This entry is mainly a historical reference point in the UDBM literature trail. Later tutorial sources in this repository, especially `by04` and `bengtsson02`, cite `Rok93` in the normalization line of work.

Because the thesis itself is not locally available here, this directory is best treated as a citation anchor and historical breadcrumb rather than a primary reading source.

## What to extract while reading

If you obtain the thesis elsewhere, focus on:

- the historical route from timed-circuit verification to symbolic timing constraints
- early normalization-based finite abstractions
- how later zone-normalization work inherited ideas from timed-circuit verification

For this repository, the key question is narrower:

"Why does UDBM's reference list still include this thesis even though the current library is organized around timed automata and DBMs?"

## Where it maps into this repository

- UDBM's own reference list: `UDBM/README.md`
- Later tutorial papers in this collection that cite the normalization line: `papers/by04/paper.pdf`, `papers/bengtsson02/paper.pdf`
- Present-day bounded symbolic operations: `UDBM/include/dbm/dbm.h`, `pyudbm/binding/udbm.py`

Concrete correspondences:

- this thesis is part of the historical background behind normalization-style finite abstractions
- later papers in the set are the practical bridge from that history to the DBM operations exposed by UDBM today

## Why it matters for UDBM specifically

It matters mostly as historical provenance. It helps explain why the UDBM references include work that predates the modern shape of UPPAAL-style DBM libraries.

In practice, you will usually learn the actionable normalization story faster from `by04`, `bblp04`, and `bengtsson02`.

## How to read it

Prefer the later papers unless you specifically need the early historical citation chain.

Availability note:
no lawful public full-text PDF was found during collection, and an additional retrieval attempt for this update also did not locate a public downloadable copy.

Verified sources:

- Stanford SearchWorks record: https://searchworks.stanford.edu/view/2831295
- The SearchWorks record points to ProQuest access for Stanford-affiliated users, not to a public PDF.
