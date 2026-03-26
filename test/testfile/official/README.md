# Official UPPAAL Example Files

This directory stores the retained official example/model/query files collected from public UPPAAL sources on `2026-03-26`.

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
  - source URL / archive member / local path / hash / size for every retained file
- `catalog.json`
  - parser-oriented catalog for every retained example file
  - records each file's path relative to this directory, finite parse-kind enum, short English/Chinese descriptions, parse status, parse message, and optional `context_path` for context-dependent query files
- `failures.json`
  - official links that were still referenced by official pages but returned download failures during collection

Current retained summary:

- Retained files: `178`
- By extension:
  - `.xml`: `102`
  - `.q`: `47`
  - `.ta`: `29`

Notes:

- Official pages currently expose some textual model examples as `.ta` rather than `.xta`. They are included here to avoid missing official textual examples.
- The `status` / `message` / `message_zh` / `context_path` fields in `catalog.json` are filled from real UTAP API probing, using the compiled local `UTAP` library rather than filename-only inference.
- The original raw fetch contained `216` files. After UTAP probing, `38` `status=error` entries and their corresponding files were removed from this retained set.
- As of `2026-03-26`, the removed `30` HTML-wrapper failures under `linked/www.it.uu.se/.../benchmarks/` did not appear to be fixable by simply re-downloading from the same official URLs:
  - the current direct URLs resolve to official HTML/404 pages rather than model/query payloads
  - the official benchmark page itself says that some referenced source files are unfortunately missing and are still being relocated: `https://uppaal.org/benchmarks/`
- Two official docs links were still referenced but were not downloadable from the public site at fetch time:
  - `https://docs.uppaal.org/extensions/cora/airland1R2.q`
  - `https://docs.uppaal.org/extensions/cora/airland1R2.xta`
- Those unresolved upstream links are recorded in `failures.json`.
