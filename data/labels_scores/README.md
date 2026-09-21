# Per-submission structural labels and scores

One CSV per **stage** listed in `configs/stage_manifest.yaml` (each stage is a real, dated checkpoint —
see `../../VERSIONING.md` — plus a scoping mode), so that a stage's output is never ambiguous about which
configuration produced it. Naming convention: `q{N}_{stage_id}.csv`, matching the `id` field of the
corresponding entry in `configs/stage_manifest.yaml` (e.g. `q5_final.csv` for stage id `q5_final`).

**`q5_final.csv` is real, populated data** — mechanically derived, via
`../../scripts/build_labels_scores_from_batch_reports.py --question 5`, from
`../../detectors/reporting-batch/topk_report.csv` (the real 526-row batch-CSV output Sonia
supplied). Its own `notes` column documents the one honest limitation of that derivation: the raw source
CSV recorded only `TopKPattern_final` per submission, not a separate coverage/structural breakdown, so
`coverage_score`/`structure_score` here are conservatively backfilled from `final_score` rather than
independently measured. (Until 2026-09-19 this file was actually hand-built with no code path of its own
— the build script's Q5 entry only ever produced `q5_final_extended.csv` below, despite this file already
claiming a "mechanical" derivation. The script's Q5 entry is now a two-item list covering both Q5 outputs,
so this claim is accurate; regenerating reproduced every score/label byte-for-byte, confirmed by direct
diff — see `configs/stage_manifest.yaml`'s `q5_final` stage note.)

**`q1_final.csv` (1,343 rows), `q2_final.csv` (726 rows), `q3_final.csv` (854 rows), and `q4_final.csv`
(776 rows) are now also real, populated data** (added the same round Q1's `SHARED_BINDING`/`all_names` fix
was found and applied — see `../../provenance/detector-version-log.md`'s "Real batch-validation RESULTS for
Q1-Q4"). All four are mechanically derived, via `../../scripts/build_labels_scores_from_batch_reports.py`,
from the real batch-report CSVs at `../../detectors/q1-q4-batch-validation/q{1,2,3,4}_report.csv`
— the same conservative `coverage_score`/`structure_score` ← `final_score` backfill as `q5_final.csv`
above, since the raw batch reports never separated the two axes for any question, not just Q5. Two
question-specific notes:

- **Q1** (`q1_final.csv`): derived from `GuardedInput_final`/`_missing` only. The raw CSV's
  `LinearSearch_final`/`_missing` columns are confirmed byte-identical to `GuardedInput`'s across all 1,343
  rows (0 differences via direct diff) — not re-derived as a separate file, since it would be a pure
  duplicate.
- **Q4** (`q4_final.csv`): `SortByKey` is `ANY(BubbleSortPass, TopKPattern)`. `matched_branch` is filled in
  by the build script from whichever of `BubbleSortPass_final`/`TopKPattern_final` is `>0` on that row
  (`BubbleSortPass` checked first) — a real, per-row provenance the raw `SortByKey_final` column alone
  doesn't carry.

**`q5_final_extended.csv` (526 rows) is real, populated data for Q5's current Table-4 headline** — added
in a later round than `q5_final.csv` above, once an embedding-clustering discovery pass (see
`../../detectors/semantic-backup-layer-validation/README.md`'s "The clustering extension")
found that Q5's structural rules were missing a real cross-function delegation pattern. Mechanically
derived, via the same `build_labels_scores_from_batch_reports.py` script (Q5's entry in that script covers
both this file and `q5_final.csv` above),
from `../../detectors/q5-delegation-clustering-fix/topk_report_EXTENDED2.csv`, target
competency `TopKPatternExtended` (`= ANY(TopKPattern, TopKViaDelegate, SortThenSlice)`); `matched_branch`
is filled in from whichever of `TopKPattern_final`/`TopKViaDelegate_final`/`SortThenSlice_final` is `>0`
on that row, in that priority order. **This file supersedes `q5_final.csv` as Table 4's reported Q5
figure (`configs/table4_config.yaml` now points Q5's row at stage id `q5_final_extended`) but does not
replace it** — `q5_final.csv` remains, unedited, as a real, independently-dated checkpoint of the earlier
TopKPattern-only figure (78.2%/75.0%). See `configs/stage_manifest.yaml`'s `q5_final` vs.
`q5_final_extended` stage entries and `scripts/regenerate_q5_delegation_breakdown.py` for the full,
independently-verified breakdown (zero regressions, exact new-catch counts, and a real, explained
78.2%→79.7% TopKPattern-alone baseline drift between the two source CSVs).

A row with a raw parse/lookup error (e.g. "function 'x' not found in submission") is kept, not dropped —
scored `final_score: 0.0`, matching the paper's and conversation's own reported correct/wrong denominators exactly
(confirmed: e.g. Q1's 768 correct + 575 wrong = 1,343 total rows, including its one error row). The error
text itself is preserved in that row's `notes` column, alongside the raw `_missing` field content, for full
per-submission auditability.

**`q5_taxonomy_crossvalidation_results.csv`** (158 rows) and **`q5_taxonomy_crossvalidation_shuffled_seed0_results.csv`**
(158 rows) are both real, populated data for a *different* experiment from `q5_final.csv` above — the
embedding-based external validation of the AST taxonomy's own manual/builtin split (see
`../../detectors/ast-taxonomy-crossvalidation/`), not the Q5 detector's own coverage/structure
scoring. Columns: `file`, `structural_label`, `semantic_predicted`, `sim_manual`, `sim_builtin`,
`sim_novel` — not the `submission_id`/`coverage_score`/`structure_score` schema documented below, which
applies only to the `qN_final`-style stage files. The 10-seed sweep built on top of these two single-split
runs has no per-seed raw CSV of its own for 9 of its 10 seeds — see
`configs/stage_manifest.yaml`'s `q5_taxonomy_embedding_crossvalidation_10seed_pooled` entry.

**`q4_embeddings_crossvalidation.csv`** (1,470 rows) and **`q2_embeddings_crossvalidation.csv`** (1,750
rows) are real, populated data for the Q4/Q2 extension of the same embedding-taxonomy methodology
(`BubbleSortPass`/`TopKPattern` and `counter`/`functional` respectively — see
`../../detectors/q2-q4-embeddings-crossvalidation/`). Unlike the Q5 10-seed sweep above, these
ARE the real per-seed/per-file prediction outputs the notebook's own last cell saved to Sonia's Drive —
supplied in a later round than the notebook that first reported these figures, which is why
`configs/stage_manifest.yaml`'s `q4_taxonomy_embedding_crossvalidation_10seed_pooled` and
`q2_taxonomy_embedding_crossvalidation_10seed_pooled` entries were upgraded from `evidence:
real_notebook_output` to `evidence: real_csv` once these arrived. Columns: `file`, `seed` (0-9),
`true_label`, `predicted` — one row per seed/file test-set prediction, not the `submission_id`/
`coverage_score`/`structure_score` schema below. `scripts/regenerate_q2q4_taxonomy_crossvalidation.py`
recomputes every reported mean/SD, pooled confusion matrix, and precision/recall figure directly from
these two files.

## Schema

| Column | Type | Meaning |
|---|---|---|
| `submission_id` | string | Joins to `data/submission_ids/*.csv` |
| `test_suite_label` | `correct` \| `wrong` | The assignment's own pass/fail verdict (same as `data/submission_ids`, repeated here for convenience) |
| `target_competency` | string | Name of the target competency evaluated for this question at this taxonomy checkpoint (e.g. `SortByKey`, `TopKPattern`) |
| `coverage_score` | float, 0-1 | The coverage axis score |
| `structure_score` | float, 0-1 | The structure axis score |
| `final_score` | float, 0-1 | `coverage_score * structure_score` (the model's stated combination rule) |
| `matched_branch` | string, optional | For `ANY`-composed competencies, which branch matched (e.g. `BubbleSortPass` vs `TopKPattern`) — needed to reproduce sub-strategy breakdowns like the 13.1%/64.4%/77.6% figures |
| `notes` | string, optional | Free text — used in `q5_final.csv` to flag the coverage/structure-score backfill described above |

`configs/stage_manifest.yaml`'s `coverage_threshold: 1.0` is **confirmed**, not a guess — verified
directly by recomputing `q5_final.csv`'s percentages at that threshold and matching every reported Q5
figure (78.2%/75.0%) exactly.

## Which stages are required

See `configs/stage_manifest.yaml`'s `required_for_publication: true` entries — those are the stages that
back a number actually printed in the paper. Every other historical stage is nice-to-have for a complete
audit trail but not blocking. `evidence: real_csv` vs. `evidence: conversation_reported_only` on each stage says
plainly whether this directory's file backs it yet.
