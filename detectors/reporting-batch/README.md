# Reporting / batch tooling — "files_Report_batch" + "files_Report_per_submmision" (~2026-07-21)

No `competency.py` included in either original zip — both `report.py` files import from it, so the
framework itself is assumed to be `V1.2.0`, unchanged. Dating is by inference from the 2026-07-21 conversation
narrative (`Levels_of_competencies_21_07.docx` already describes the reporting layer and the 526-submission
batch run as done) — the reporting zips themselves carry no date marker of their own; this is the one
soft spot in an otherwise well-corroborated chronology, noted explicitly rather than smoothed over.

`TopKPattern` gains an explicit `remove` slot + `CONTAINS_TEXT` check (the "missing-removal" fix, canonical
bug #12) — `report_demo.py` demonstrates it directly against `wrong_5_058.py`. `report.py` (the
`files_Report_batch` version included here) adds `function_name`-scoped reporting — a **second,
independent scoping layer** on top of `V1.2.0`'s `Evidence.scope` guard, closing the "unrelated helper
function credited to the file" gap (canonical bug #13). `topk_report.csv` here is real, computed output:
526 rows (418 correct / 108 wrong), zero parse errors — the source of the paper's 78.2%/75.0% figures
(reproduced exactly from this file: 327/418 and 81/108).

**What this checkpoint does NOT include:** a CSV or driver script for the *unscoped* 83.0% run, or any
code for the "magus_sort cross-function-credit" helper function itself (bug #13's symptom, not its
own source).

See `../../provenance/detector-version-log.md`, section "## Reporting/batch tooling".
