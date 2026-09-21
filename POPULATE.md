# Populating this repository with real artifacts

**Status as of 2026-08-08: steps 1, 2, 3, and 5 are done — real code/taxonomy snapshots, submission-ID
manifests, and per-submission labels/scores are all real, populated data for every question, Q1-Q5.**
**Update, 2026-09-18: step 6 (the exemplar registry) is now also done** — the full, real 10-competency/
27-exemplar registry is merged into `data/exemplar_registry/`, mechanically, from already-delivered code;
see step 6 below. **Step 9 (the Refactory corpus license check) is also done** — see step 9 below.
**Update, 2026-09-20: step 4 is now also done** — real split-index files were supplied from Sonia's
Colab/Drive artifacts, and turned out to be the same experiment as the already-real
`q4`/`q5_taxonomy_embedding_crossvalidation_10seed_pooled` stages below, not a distinct companion-paper
experiment as this file previously stated — see step 4. Every item on this list is now done. This file
tracks what's left, top to bottom; later steps depend on earlier ones except where noted.

## 1. Detector code snapshots (`detectors/<checkpoint>/`) — DONE

Real, frozen `competency.py` (and every supporting file) for all ten real checkpoints is in place —
`v1.0.0` through `fixq4`, plus `semantic-backup` and two undated,
diff-bounded intermediate saves under `detectors/_intermediate_unlabeled/`. Provenance for each is
checkpoint label + real date (zip-preserved mtime, conversation-export date marker, or diff-bounding), not a
commit SHA — there is no granular commit history for this project, so that placeholder scheme has been
dropped rather than left open (see `../VERSIONING.md`). Each folder's `README.md` cites the exact log
section backing its claims.

## 2. Taxonomy snapshots (`taxonomy/<checkpoint>/taxonomy.yaml`) — DONE

One snapshot per real taxonomy-affecting checkpoint (`v1.0.0-baseline`,
`q2-3rd-strategy-uniquecheck`, `enforcement-linearsearch`,
`fixq4-sortbykey`), each scoped to only the question(s) it actually changed. Every `*_final`
reported coverage figure is now marked `evidence: real_csv` (Q1 through Q5, as of the 2026-08-05 round —
see step 5 below); intermediate/superseded stages remain `conversation_reported_only`.

## 3. Submission ID manifests (`data/submission_ids/qN_*.csv`) — DONE

Populated 2026-08-05 via `scripts/build_submission_ids_from_batch_reports.py`, mechanically projected
from each question's real batch-report CSV (see step 5). Correct/wrong counts confirmed exact against
Table 3: 768/575 (Q1), 291/435 (Q2), 546/308 (Q3), 419/357 (Q4), 418/108 (Q5).

## 4. Split index files (`data/splits/`) — DONE (2026-09-20)

**UPDATE (2026-09-20): this step is done, and the framing below turned out to be wrong, not merely
unconfirmed — left in place rather than deleted, per this repo's evidence-preservation practice.**

Real split-index files were supplied from Sonia's Colab/Drive artifacts: for `q4_sortbykey` and `q5_topk`,
`data/splits/<experiment>/split_manifest.json` plus `split_NN_train_ids.txt`/`split_NN_test_ids.txt` for
seeds 00-09 (70/30, `.sample(frac=1, random_state=seed)`). `configs/stage_manifest.yaml`'s `table5:` block
is now filled in with real values. Contrary to the paragraph below (written under this repo's own
uncertainty, before real files existed), these turned out to be **the same experiment** as
`q4_taxonomy_embedding_crossvalidation_10seed_pooled`/`q5_taxonomy_embedding_crossvalidation_10seed_pooled`
(step 7 below), not a distinct companion-paper one — same source notebooks, same source report CSVs, same
split code, same reported mean/SD; for Q4 the evidence CSV is byte-for-byte identical to the one already
in this repo. See `data/splits/README.md` and `configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits`
note for the full evidence trail, and `stages.q4_taxonomy_embedding_crossvalidation_10seed_pooled`'s own
appended `UPDATE:` correcting its prior "NOT the same experiment" claim.

**Original framing (superseded, kept for history):** Unlike every other item on this list, the *shape* of
this experiment (how many splits, what ratio, which two taxonomic distinctions) is not yet confirmed
against any real artifact — the earlier version of this repo's description of it ("10 random 70/30
splits," specific named experiments) was inferred from the paper's prose, not from anything supplied. Per
Sonia (2026-09-10), the real specifics and split files exist in Colab/Drive. When supplied: export, for
each split, the exact `submission_id`s assigned to train vs. test (not just a seed — "regenerate from the
seed" and "these are the IDs actually used" are different auditability claims), fill in
`configs/stage_manifest.yaml`'s `table5:` block's `PENDING` markers with real values, and update
`data/splits/README.md` and this step to describe the confirmed experiment.

Do not confuse this with the real embedding-taxonomy cross-validations already in
`configs/stage_manifest.yaml`** (`q5_taxonomy_embedding_crossvalidation_*`,
`q4_taxonomy_embedding_crossvalidation_10seed_pooled`, `q2_taxonomy_embedding_crossvalidation_10seed_pooled`
— the latter two now `evidence: real_csv`, upgraded once the real per-seed/per-file prediction CSVs
arrived; Q5's 10-seed sweep remains `real_notebook_output` since its own raw CSVs were never supplied for
9 of its 10 seeds) — those validate the AST taxonomy's own multi-strategy splits (Q5 manual/builtin, Q4
bubblesort/topk, Q2 counter/functional) using embeddings as an external check, a real and already-supplied
experiment. This step 4 item is a distinct, still-unsupplied companion-paper scope
(`table5.q4_sortbykey_splits`/`q5_topk_splits`) — per the source conversation's own repeated framing, likely the
novel-detection/anomaly-scoring validation for that separate paper, not the taxonomy cross-validation this
repo already has. **(This entire paragraph is now known to be incorrect for q4/q5 — see the UPDATE above.
The Q2 case was never claimed to overlap and is unaffected.)**

## 5. Per-submission labels and scores (`data/labels_scores/`) — DONE

**`q1_final.csv`, `q2_final.csv`, `q3_final.csv`, `q4_final.csv`, and `q5_final.csv` are all real,
populated data**, every one `evidence: real_csv` in `configs/stage_manifest.yaml`. Q5's was derived first
(526 rows, from `detectors/reporting-batch/topk_report.csv`); Q1-Q4's were added 2026-08-05,
the same round the driver script (`detectors/q1-q4-batch-validation/run_q1_q4_batch_validation.py`)
was actually run by Sonia against her real Refactory `data/` folder for the first time — see that
checkpoint's own `README.md` for the run results, and `detectors/q1-shared-binding-fix/` for a
real Q1-specific structural-detector bug the run surfaced and its fix. All five files are now mechanically
derived, via `scripts/build_labels_scores_from_batch_reports.py`, from their respective real batch-report
CSVs — see `data/labels_scores/README.md` for the schema and the one honest caveat shared by all five
(coverage_score/structure_score are conservatively backfilled from final_score, since none of the raw
batch reports separated the two axes).

## 6. Exemplar registry (`data/exemplar_registry/`) — DONE (2026-09-18)

**The full, real exemplar registry is now merged** — `data/exemplar_registry/exemplars.csv` and `code/`
hold all 10 competencies / 27 exemplars from
`detectors/semantic-backup-validation-executed/semantic_backup.py` (this repo's most current,
most audit-clean semantic-backup checkpoint), mechanically via `scripts/build_exemplar_registry.py` — the
same "mechanically projected from real delivered code" pattern as
`build_submission_ids_from_batch_reports.py`. Every `final_score` in the CSV was freshly computed in this
merge by calling the live structural resolver directly (`model.resolve()`), not copied from a prior
report: all 27 verify at `final_score=1.0000`, `audit_registry()` reports zero problems. Per-exemplar
provenance (mined vs. hand-written, and source submission ID where the code comments name one) is
transcribed from `semantic_backup.py`'s own inline comments — see `data/exemplar_registry/README.md` for
the full breakdown. This did not require any new artifact from Sonia — the earlier framing ("a larger real
exemplar set... will be supplied in a later round") turned out to be stale; the real set already existed
as delivered, verified code and only needed merging.

This registry has still never been run against real CodeBERT/`codet5p` in this sandbox (network-blocked)
— the `codet5p` numbers for it are `real_notebook_output`-backed (from the checkpoint's own genuinely
executed notebook) but not independently re-executable here. See
`configs/stage_manifest.yaml`'s `exemplar_registry_real_mined_v3_executed` entry.

**A real AUC result for the layer's actual novel-vs-wrong job now exists, and is now `real_csv`-backed**
(2026-08-08, `configs/stage_manifest.yaml`'s `semantic_backup.backends.codet5p_bootstrap_novel_vs_wrong_auc`,
`status: REAL_INVERTED_RESULT_CSV_BACKED`) — a bootstrapped, uncontaminated-comparison-group redesign,
reporting a strong but *inverted* result (pooled AUC 0.097 across 1,510 scored pairs: genuinely-wrong
submissions read as more similar to correct exemplars than genuinely-novel-correct ones do). Both raw CSVs
(`semantic_backup_bootstrap_summary.csv`, `semantic_backup_pooled_scores.csv`) and the executed notebook
itself were supplied in later rounds and independently verified (see
`scripts/regenerate_semantic_backup_auc.py`) — every figure matches to floating-point precision, plus a
new sanity-check similarity pair for the `codet5p-110m-embedding` backend not previously on file. One
anomaly remains open even in the executed notebook: every code cell's `execution_count` is `None` despite
real, populated outputs, so the conversation's own "cell 13"/"cell 15" references still can't be cross-checked
against real cell positions. Per Sonia this result belongs to a separate "companion paper" whose full
artifact set (including any positive/deployable version, e.g. the proposed two-registry follow-up) may
still come in a later round. See `detectors/semantic-backup-layer-validation/README.md`.

## 7. Steps 4 and 6 — DONE

**Update (2026-09-20): both are now done.** `table5:`'s `PENDING —` string values have been replaced with
real file paths and values (step 4, this round; step 6, 2026-09-18). Every `*_final` stage for Q1-Q5 was
already done (step 5).

## 8. Run the checks

```bash
pip install -r environment/requirements.txt
python scripts/regenerate_table4.py --stage final --check
python scripts/regenerate_table5.py
python scripts/regenerate_q5_percentages.py --all-stages
pytest tests/ -v
```

`regenerate_table4.py --stage final --check` now passes cleanly end to end for all five questions — no
`[PENDING]` rows remain in that table. **Update (2026-09-20): `regenerate_table5.py`'s Q4/Q5 split
sections are now real too** — they print the confirmed `status`, `split_dir`, `reported_mean`,
`reported_sd`, and checkpoint fields rather than `PENDING`. The semantic-backup section still reports
`[PENDING]` for two specific, unrelated backend items (`jina_v2_code`, never executed;
`codet5p_110m_embedding`, code exists but not validated against a real corpus) — those remain open and are
not part of step 4 or step 6. A failing `pytest` assertion (as opposed to a skip) is exactly
the signal this repository exists to give: a reported number no longer matches its own frozen inputs,
worth chasing down before publication.

## 9. Refactory corpus license check — DONE (2026-09-18)

Confirmed directly against the corpus's own repository,
[github.com/githubhuyang/refactory](https://github.com/githubhuyang/refactory) (Hu, Ahmed, Mechtaev, Leong
& Roychoudhury, ASE 2019 — paper reference [3]; an earlier note in `data/submission_ids/README.md`
misattributed this to "Ureel & Wallace," now corrected): the repository carries a root `LICENSE` file,
LGPL-3.0, with no separate license terms for `data.zip` (the corpus archive) and no student
consent/privacy statement anywhere in the README. Full findings and the practical conclusion — this
repository keeps publishing submission identifiers and derived labels/scores only, never the students'
own source code, regardless of what LGPL-3.0 would technically permit — are in
`data/submission_ids/README.md`'s "On redistributing the corpus itself" section. This was a documentation
check, not a code change: nothing in `data/submission_ids/*.csv` or any regeneration script changes as a
result.
