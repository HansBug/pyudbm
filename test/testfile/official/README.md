# Official UPPAAL Example Files

This directory stores official example/model/query files collected from public UPPAAL sources on `2026-03-26`.

Collected source categories:

- Official UPPAAL distribution archives published on `https://uppaal.org/downloads/`
  - stable `5.0.0` generic Linux package
  - beta `5.1.0-beta5` generic Linux package
- File links exposed by official pages from:
  - `https://uppaal.org/`
  - `https://docs.uppaal.org/`

Stored layout:

- `distribution/`
  - files extracted from official distribution archives, preserving versioned demo paths
- `linked/`
  - files downloaded from direct links exposed by official UPPAAL pages, preserving host/path layout
- `manifest.json`
  - source URL / archive member / local path / hash / size for every collected file
- `catalog.json`
  - parser-oriented catalog for every collected example file
  - records each file's path relative to this directory, finite parse-kind enum, and short English/Chinese descriptions
- `failures.json`
  - official links that were still referenced by official pages but returned download failures during collection

Collection summary at fetch time:

- Downloaded files: `216`
- By extension:
  - `.xml`: `106`
  - `.q`: `67`
  - `.ta`: `43`

Notes:

- Official pages currently expose some textual model examples as `.ta` rather than `.xta`. They are included here to avoid missing official textual examples.
- Two official docs links were still referenced but were not downloadable from the public site at fetch time:
  - `https://docs.uppaal.org/extensions/cora/airland1R2.q`
  - `https://docs.uppaal.org/extensions/cora/airland1R2.xta`
- Those unresolved upstream links are recorded in `failures.json`.
