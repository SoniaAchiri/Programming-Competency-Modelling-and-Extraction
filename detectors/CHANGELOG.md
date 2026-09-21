# Detector changelog

**This file was regenerated from `../provenance/detector-version-log.md` — the evidence-grounded log built
by diffing Sonia's real saved checkpoints against each other and cross-referencing her conversation-history
exports and paper drafts, one round at a time. It replaces an earlier version of this changelog that was
guessed from the paper's prose alone before any real artifact existed, and that guess turned out to be
wrong on several specifics (see `../VERSIONING.md`'s "Corrected from an earlier, guessed version" note).**

There is no granular commit history for this project — Sonia saved periodic checkpoints (zips, standalone
files) rather than committing incrementally — so provenance here is **checkpoint label + real date**
(established from zip-preserved mtimes, conversation-export date markers, or direct diff bounding), not a commit
SHA. Every claim below is either read directly from a diff between two real checkpoints, or
quoted/paraphrased from a conversation-history document that names that checkpoint — see the log for the full
citations; this table is a compressed index into it, not a replacement for it.

| Checkpoint | Real date | What changed | Detail |
|---|---|---|---|
| `v1.0.0` | 2026-07-18 | Baseline: 8 primitives, whole-file scanning, first bug fixes (#1-4). | `detectors/v1.0.0/README.md` |
| `ex1-taxo` | 2026-07-19 | `FUNC_DEF` primitive; `REFERENCES`/`CONTAINS_TEXT` constraints; `DELEGATES` class added but **not yet wired in**. | `detectors/ex1-taxo/README.md` |
| `ex2-3-4` | 2026-07-19 | `ASSIGN` extended to `.pop()`/`.remove()`. | `detectors/ex2-3-4/README.md` |
| `semantic-backup` | 2026-07-20, 19:47 | Semantic-similarity backup layer added (opt-in, never touches `final_score`). Stub backend honestly self-documented as having no real discriminative power; real CodeBERT path written but never executed (network blocked). | `detectors/semantic-backup/README.md` |
| `v1.2.0` | 2026-07-19 → 2026-07-21 | `EXHAUSTIVE_CHAIN` (multi-way branching); `DELEGATES` wired in; per-function `Evidence.scope` guard (bugs #8-11). | `detectors/v1.2.0/README.md` |
| `reporting-batch` | ~2026-07-21 (dating by inference — see README) | Reporting/batch-CSV tooling; `TopKPattern` "missing-removal" fix (#12); `function_name`-scoped reporting, a second independent scoping layer (#13). Real `topk_report.csv` (526 rows) included. | `detectors/reporting-batch/README.md` |
| `fixq2` | 2026-07-28, 18:42 | `is_simple_init` widened to `ast.Tuple`; level-concept comment appended (documented, **not yet enforced**); `AccumulateThenCount` (Q2 strategy 2 of 3). | `detectors/fixq2/README.md` |
| `q2-3rd-strategy` | 2026-07-28, same round | `FunctionalUniqueCheck` (Q2 strategy 3 of 3); `UniqueCheck` = 3-way `ANY`, 90.4% combined (conversation-reported, no CSV). | `detectors/q2-3rd-strategy/README.md` |
| `enforcement` | 2026-07-28 | `level()`/`check_layering()`/`register()`-time `LayeringViolation` — **enforcement goes live**, all 4 known violators flagged. `LinearSearch` registered (Q1). | `detectors/enforcement/README.md` |
| `fixq4` | 2026-07-28, 04:03 (zip mtime) | `TopKPattern` restructured via lifting wrappers — down to **1** violator (`BubbleSortPass`, canonical bug #19, not fixed). `NESTED` identity-comparison bug fixed (#18 — discovered via `CountedSearch`, not `TopKPattern`; see log correction). `.insert()` added (Q3 fix). `SortByKey = ANY(BubbleSortPass, TopKPattern)` (Q4 fix). | `detectors/fixq4/README.md` |

**Not yet supplied in any checkpoint**, per the log's "Still-pending items": `CountedSearch`'s own
lifted-siblings replacement code (only referenced in prose); any batch script or CSV backing the Q1
(1,343/1,342), Q2 (90.4%), Q3 (94.0%), or Q4 (77.6%) figures — Q5 is the only question with a real,
supplied CSV; the real CodeBERT-backed semantic-backup validation (network-blocked in every sandbox used);
and the separate "companion paper" embedding-model experiments referenced by early conversation text.

**Canonical bug table**: 19 numbered defects, quoted in full in the log (bugs #1-13 from
`Competency_Extraction_Methodology_V24.docx`'s Table 5, bugs #14-19 from the 28/07 methodology note). Not
reproduced here to avoid drift between two copies — the log is the single source.
