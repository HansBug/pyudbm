# Papers Guide

This directory collects the theory, tool, and historical-background papers that are most useful for understanding why UDBM and this wrapper project look the way they do.

For the Chinese version of this guide, see [README_zh.md](./README_zh.md).

## Directory structure

The default structure for one paper subdirectory under `papers/` is:

- `bibtex.bib`
  The canonical citation metadata for the paper.
- `paper.pdf`
  A locally vendored copy of the paper when a lawful public full text is available or otherwise intentionally included.
- `README.md`
  The English reading guide for the paper.
- `README_zh.md`
  The Chinese reading guide for the paper.
- `content.md`
  A GitHub-readable, manually refined Markdown transcription of the paper content when full-text refinement has been done.
- `content_assets/`
  Image assets used by `content.md`, typically extracted or manually re-cropped figures and tables.

Some directories may also contain a small number of additional reference files when there is a concrete need, but the files above are the standard maintenance target.

## Maintenance rules

When adding or updating a paper entry in this directory:

- create or keep one subdirectory named by a stable citation key such as `by04` or `dhlp06`
- always include `bibtex.bib`
- include `paper.pdf` only when there is a lawful source worth vendoring; if no public full text is available, say that explicitly in `README.md` and `README_zh.md` instead of adding a placeholder PDF
- keep `README.md` and `README_zh.md` paired, cross-linked, and structurally aligned
- keep the paper-level guides focused on repository-relevant reading advice: position in the stack, what to extract, where it maps into the codebase, and why it matters for UDBM
- if you create `content.md`, treat it as a human-facing reading artifact rather than a raw extractor dump
- treat figure and table assets as a first-class part of refinement work, not as an afterthought; every referenced screenshot must be visually checked and, when necessary, manually re-cropped
- when refining a paper substantially, do not stop at cleaning the screenshots that already exist; also verify that materially relevant figures and tables from the covered pages have actually been included, and supplement any missing assets
- keep `content_assets/` limited to assets actually referenced by `content.md`
- update this top-level `papers/README.md` and `papers/README_zh.md` whenever new papers are added or the reading paths change

## Recommended reading paths

### Fast path for work in this repository

1. `by04`
   Start here for the semantic and symbolic-zone baseline and for the best compact tutorial on regions, zones, DBMs, and algorithms.
2. `dhlp06`
   Read this when you need the theory reason for federations and subtraction.
3. `bblp04`
   Read this for extrapolation, abstraction, and termination.
4. `llpy97`
   Read this when touching `mingraph` or compact DBM storage.
5. `bengtsson02`
   Read this for the deeper implementation-oriented DBM and normalization story.

### Tool-context path

- `lpw95`
  Early symbolic / compositional verification foundation for UPPAAL.
- `lpy97`
  Short overview of the UPPAAL toolbox and its design criteria.
- `bdl04`
  Mature UPPAAL tutorial with modeling patterns and practical usage.
- `behrmann03`
  Broader system-level architecture around federations, CDDs, sharing, and priced extensions.

### Historical-root path

- `dill89`
  Early dense-time symbolic verification precursor.
- `ad90`
  Original timed-automata source paper.
- `rokicki93`
  Historical citation point in the normalization line; full text is not locally available here.

If you want the shortest path to the parts most directly visible in today's Python wrapper, use:
`by04 -> dhlp06 -> bblp04 -> llpy97`.

## What each paper contributes

### `by04`

Role:
primary entry point and best compact tutorial on timed automata semantics, regions, zones, DBMs, and verification algorithms.

Main UDBM support:

- the meaning of a convex zone
- why zones replace regions in practice
- the canonical DBM view and how canonical DBMs encode zones
- core operations such as delay, past, reset, and guard intersection
- what symbolic operations a verification tool repeatedly needs
- why normalization / bounded abstraction matters

### `dhlp06`

Role:
DBM subtraction and the direct theoretical motivation for federations.

Main UDBM support:

- subtraction on zones
- non-convex results
- unions of DBMs as the result domain
- reduction after subtraction

### `bblp04`

Role:
lower/upper-bound abstractions for zone-based verification.

Main UDBM support:

- why extrapolation is sound
- why extrapolation can force termination
- why multiple extrapolation schemes exist

### `llpy97`

Role:
minimal graph and compact storage of DBMs.

Main UDBM support:

- why `mingraph` exists
- why canonical DBMs are not always the best stored form

### `bengtsson02`

Role:
deep implementation-oriented thesis on clocks, DBMs, states, normalization, and storage in timed verification.

Main UDBM support:

- the full DBM operation set behind symbolic exploration
- normalization with difference constraints
- storage, compression, and hashing motivations

### `lpw95`

Role:
early UPPAAL foundation paper on symbolic and compositional model checking.

Main UDBM support:

- why solving clock-constraint systems is central
- why symbolic state exploration beats explicit region handling in practice
- why UDBM sits below, not inside, the whole model-checking stack

### `lpy97`

Role:
short overview of the UPPAAL toolbox and its user-facing design.

Main UDBM support:

- why constraint solving and on-the-fly reachability dominate the engine design
- why usability and readable symbolic modeling matter

### `bdl04`

Role:
practical UPPAAL tutorial for modeling language, queries, and patterns.

Main UDBM support:

- the user-side timed-automata dialect served by the symbolic engine
- why high-level clock-oriented APIs matter more than raw matrix helpers

### `behrmann03`

Role:
system-level synthesis across symbolic data structures used around UPPAAL.

Main UDBM support:

- why unions of zones are important at the tool level
- why CDDs were explored as an alternative
- why sharing, storage layout, and priced extensions matter

### `dill89`

Role:
historical precursor from timing assumptions to symbolic dense-time verification.

Main UDBM support:

- the early move toward symbolic timing-state representations
- the deeper motivation for representing sets of clock valuations symbolically

### `ad90`

Role:
original timed-automata language-theoretic source.

Main UDBM support:

- the clock / guard / reset model underneath later symbolic techniques
- the formal timed-automaton object that zone and DBM methods later encode

### `rokicki93`

Role:
historical reference point in the normalization literature.

Main UDBM support:

- mainly provenance for the normalization line later cited by `by04` and `bengtsson02`

Note:
no lawful public full-text PDF was found for `rokicki93` during collection or during the follow-up retrieval attempt for this update.

## How this maps to the Python wrapper work in this repository

The restored Python API in `pyudbm/binding/udbm.py` is not just wrapping raw matrix primitives. It is trying to reconstruct the historical `Context` / `Clock` / `Federation` model on top of UDBM.

That means:

- `ad90` and `dill89` explain the older semantic roots of clock-based symbolic reasoning
- `by04` explains the single-zone / DBM layer that the DSL manipulates
- `dhlp06` explains why `Federation` must remain a real union-based object instead of collapsing to one DBM
- `bblp04` explains why methods like `extrapolateMaxBounds` belong in the public surface
- `llpy97` and `bengtsson02` explain the compressed-storage and implementation machinery already present in native UDBM
- `lpw95`, `lpy97`, `bdl04`, and `behrmann03` explain the larger UPPAAL tool context and user-facing expectations around that engine

## Practical advice

If you are reading for implementation work in this repository:

- start with `by04/README.md`
- then read `dhlp06/README.md`
- then read `bblp04/README.md`
- use `llpy97/README.md` and `bengtsson02/README.md` when touching `mingraph`, storage, or lower-level DBM machinery
- use `lpy97/README.md` and `bdl04/README.md` when thinking about high-level API ergonomics
- use `behrmann03/README.md` when you need the larger UPPAAL architecture

## Content Refinement Workflow

When refining one paper into a publishable Markdown reading version, use the following process.

### Goal

The goal is not to keep a rough machine extraction. The goal is a `content.md` that a human can read directly on GitHub with clean structure, correct formulas, correct figure and table placement, and captions that line up with the surrounding discussion.

More importantly, "refinement" here means fidelity, not loose summarization or free rewriting. The final `content.md` must be checked against the original PDF page by page and must stay strictly consistent with it. A paper is not considered refined unless every page that is being covered has been individually verified against the source PDF. If even one page has not been checked carefully, the work is not complete.

Only Step 1 is an extraction step. From Step 2 through Step 5, the workflow must be driven purely by the LLM's own text understanding and page-level visual reading ability. Do not use additional rough cleanup scripts, batch heuristics, or secondary tool-based post-processing in those later steps.

### Step 1: Export the two working views

Always export both:

1. a Markdown text draft
2. a page-image draft

Use `tools.papers_to_content` directly on the PDF file. The tool is intentionally decoupled from the `papers/` directory structure, so pass explicit paths.

Example:

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

Notes:

- text mode writes one Markdown file and, by default, an asset directory beside it such as `content_assets/`
- image mode renders one image per page for visual inspection
- do not write page-image output directly into a paper subdirectory under `papers/`; page-image exports are often too large and should go to a temporary path such as `/tmp/...`
- use explicit output paths every time; do not assume a batch mode or repository-coupled defaults

### Step 2: Refine page by page using only LLM text and vision

From this step onward, refinement must be performed directly by the LLM while reading both the text draft and the rendered page images. Do not hand the draft to another rough processing tool for cleanup.

This page-by-page check is mandatory. "Looks right overall" is not sufficient. Each page must be reconciled against the PDF until the Markdown for that covered page is strictly faithful to the source.

If a paper is long, refine it in batches when necessary. Do not assume that a long paper should always be refined in one full pass. For example, it is acceptable to process a paper section by section, chapter by chapter, or page-range by page-range, as long as each batch is refined carefully and consistently.

For each page:

- compare the extracted Markdown against the actual page layout and visual content
- rewrite broken paragraph boundaries, headings, lists, tables, footnotes, and references
- convert malformed inline math and display math into proper LaTeX
- remove extractor noise such as page separators, garbled ligatures, duplicated fragments, OCR artifacts, and broken symbols
- ensure terminology, notation, and variable names are consistent with the source PDF
- ensure that the refined Markdown for that page matches the source page in substance, structure, formulas, and figure/table references rather than merely paraphrasing it

Do not accept "mostly readable" output. If a formula, symbol, or paragraph is ambiguous, resolve it by reading the page visually and rewriting it carefully.

### Step 3: Validate figures and tables visually using LLM judgment

All figures and tables referenced in `content.md` must be checked against the PDF visually, and this check must also be driven by the LLM's direct reading of the rendered pages rather than by automatic heuristics.

Figures are a high-priority acceptance item. A paper is not "refined" if the prose was cleaned up but the screenshots are still poorly cropped, incomplete, missing captions, or inserted at the wrong textual location.

Completeness is part of figure validation. It is not enough to polish the screenshots that are already present in `content.md`. You must also re-read the page images and verify that the covered portion of the paper does not contain missing figures or tables that should have been included but were omitted earlier. If the prose discusses Fig. *n* or Table *n* but no corresponding asset is present, that is a refinement failure and must be fixed.

In particular:

- verify figure/table completeness, not only crop quality; compare the figure inventory visible in the PDF against what is currently present in `content.md` and `content_assets/`
- verify that the extracted screenshot matches the intended figure or table
- verify that the crop is complete on every edge and does not cut away axes, labels, legends, table borders, rightmost nodes, top headers, bottom rows, or any other semantically relevant content
- verify that the crop is not too loose; avoid carrying unrelated paragraphs, neighboring figures, section headings, or page furniture when the target figure can be isolated more precisely
- verify that the original caption is included inside the image crop whenever the PDF layout allows it
- also preserve a readable Markdown caption immediately below the image in `content.md`; the image caption and the text caption should both exist so humans can verify the match quickly and LLMs can retrieve figures reliably
- verify that the figure or table is inserted at the strictly corresponding point in the surrounding discussion, not merely somewhere in the same section
- if one PDF page contains multiple separately discussed figures, split them into separate assets instead of keeping a combined screenshot unless the paper itself presents them as one inseparable figure

Practical screenshot workflow:

- first build a figure/table inventory for the covered pages by re-reading the rendered page images; if helpful, use the PDF text only to locate candidate figure numbers or pages, but treat the page images as the source of truth
- compare that PDF-side inventory against the current figures referenced in `content.md` and the files present in `content_assets/`
- if figures are missing, add them before finalizing crop quality; do not accept a paper where the text refers to figures that were never inserted
- inspect each referenced asset at full size, not only as a small thumbnail
- when adding missing figures, make rough candidate crops first, review them as a set, and then inspect each candidate again at full size before accepting it
- compare the asset against the source page and check all four edges deliberately
- if any side is clipped or if extra context is leaking in, re-crop and replace the asset rather than tolerating a "good enough" screenshot
- if a figure spans a page boundary in the Markdown structure, move the page marker and the image placement so the insertion remains faithful to the PDF flow
- after replacing assets, update `content.md` if the figure split, order, or placement changed
- when new figures are added, insert both the image and an explicit Markdown caption at the exact point where the surrounding prose begins to discuss that figure
- remove superseded assets that are no longer referenced
- finish with a consistency check that every image referenced in `content.md` exists in `content_assets/`, that `content_assets/` does not retain stale unused screenshots, and that the figure numbering now present in `content.md` no longer has obvious gaps caused by omitted assets

The extraction script may produce incorrect screenshots or poor crops. When that happens, do not keep the bad asset. Re-screenshot or re-crop the page content manually, replace the asset in `content_assets/`, and update `content.md` to reference the corrected file.

### Step 4: Produce a GitHub-readable final version through LLM editing

The final `content.md` should read like a carefully edited technical note on GitHub, not like OCR output. This stage must still be pure LLM editorial work rather than bulk mechanical cleanup.

GitHub readability does not relax fidelity requirements. The final text must remain strictly aligned with the source PDF page by page. Readability improvements are allowed only when they preserve exact content, ordering, notation, and figure/table correspondence.

For very long papers, this finalization step may also be completed batch by batch. The important rule is editorial quality and consistency, not forcing a single all-at-once pass.

That means:

- use normal Markdown headings and paragraph spacing
- use LaTeX for inline and display formulas when needed
- keep figure and table captions readable and explicit, and preserve the "caption in image + caption in Markdown" pattern whenever a figure asset is used
- preserve the logical order of the paper
- avoid raw page markers, extraction diagnostics, or internal tool noise

When the PDF is incomplete, low-quality, or only a preview, say so explicitly near the top of `content.md` and only transcribe what can be justified from the available pages.

### Step 5: Treat LLM editorial judgment as mandatory

This workflow is editorial, not purely mechanical.

Required principle:

- use tooling only to obtain the initial text draft and page-image draft in Step 1
- use the LLM's own text reasoning and visual reasoning to perform all later refinement
- do not use broad automatic cleanup passes as a substitute for page-aware editorial correction
- prefer careful manual correction over rough automation
- treat page-by-page source fidelity as a hard acceptance criterion rather than a best-effort goal

If there is a conflict between what an extractor emitted and what the page visually shows, trust the page and fix the Markdown accordingly.
