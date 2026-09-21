# Semantic backup layer — "files_semantic_Backup" (2026-07-20, 19:47)

Real date confirmed two independent ways: the original zips per-file timestamps (preserved on
extraction) and `semantic_20_07.docx`'s own leading date marker. This is a separate, opt-in extension
on top of the core detector, not a version of it — it never modifies `final_score`.

`semantic_backup.py`: an `EXEMPLARS` registry (`FindExtremum` x3, `Accumulation` x2), a real (but
never-executed-here — huggingface.co is blocked in every sandbox this project has run in, confirmed
directly: 403 x-deny-reason: host_not_allowed) CodeBERT embedding path, and a stub bag-of-AST-token
fallback honestly documented, and independently re-tested, as having "essentially no discriminative
power" (0.77 vs. 0.79 similarity on a related vs. unrelated function pair).

`report.py` here is `files_Report_batch`'s `report.py` (see `../reporting-batch/`) plus a
clean, additive integration: `semantic_backup`/`semantic_threshold`/`semantic_backend` params on
`generate_report()`, only ever adding a separately-labeled `semantic_backup` field, never touching
`final_score`.

See `../../provenance/detector-version-log.md`, section "## Semantic backup layer".
