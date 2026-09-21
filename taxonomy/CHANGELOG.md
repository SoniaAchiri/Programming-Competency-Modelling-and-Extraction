# Taxonomy changelog

**Regenerated from `../provenance/detector-version-log.md`.** Replaces an earlier version built by guessing
from the paper's prose before any real artifact existed — see `../VERSIONING.md`.

| Snapshot | Change | Real coverage evidence |
|---|---|---|
| `v1.0.0-baseline` | Baseline: one assumed target competency per question, unvalidated against the full corpus. | Spot-checked only (2-4 files/question). |
| `q2-3rd-strategy-uniquecheck` | Q2: `UniqueCheck = ANY` of 3 real strategies (85.2% / 0.7% / 4.5%). | Conversation-reported, 3-document corroborated, no CSV. |
| `enforcement-linearsearch` | Q1: `LinearSearch` split from `GuardedInput` (same structure, different skill — deliberately not a wrapper). | 1,343/1,342, zero mismatches. Conversation-reported once, no CSV. |
| `fixq4-sortbykey` | Q3: `.insert()` gap closed (detector-level, no taxonomy change). Q4: `SortByKey = ANY(BubbleSortPass, TopKPattern)` — the project's strongest cross-exercise transfer result. | Conversation-reported, 2-document corroborated, no CSV. |

Each `taxonomy.yaml` is a complete, standalone snapshot for the question(s) it changed — not a diff — but
is scoped to only the question(s) named in its filename; for every other question, the most recent earlier
snapshot still applies (Q5's `TopKPattern` was never given its own taxonomy-level correction — only
detector-level fixes, see `../detectors/CHANGELOG.md`).

**No question in this project ever reached a fully evidenced, batch-script-and-CSV-backed final coverage
figure except Q5** (`detectors/reporting-batch/topk_report.csv`, real, 526 rows). Every other
question's percentage above is real — independently corroborated across 2-3 separate conversation/paper documents
in every case — but not yet regenerable from a script in this repo. See `POPULATE.md`.
