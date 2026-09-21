# Train/test split indices for the embedding experiments

**Status: real, populated, independently verified (2026-09-20).**

## Update (2026-09-20): these are the same experiment already logged as real in `stage_manifest.yaml`

The prior version of this README (and `POPULATE.md` step 4, and `README.md`'s top-level "What's here"
table) said this directory held indices for a *distinct, still-unsupplied companion-paper experiment* —
"likely the novel-detection/anomaly-scoring validation," separate from the AST-taxonomy embedding
cross-validations already in `configs/stage_manifest.yaml`. **That framing was wrong, not merely
unconfirmed.** Once the real split files arrived, they turned out to trace back to the exact same two
notebooks that already back `q4_taxonomy_embedding_crossvalidation_10seed_pooled` and
`q5_taxonomy_embedding_crossvalidation_10seed_pooled` in `configs/stage_manifest.yaml` — same source
report CSVs, same seeded 70/30 split code, same reported mean/SD. For Q4, the supplied evidence CSV is
byte-for-byte identical to the CSV already in this repo at `data/labels_scores/q4_embeddings_crossvalidation.csv`.
The earlier "distinct companion-paper experiment" text is left in place in `POPULATE.md`'s and
`stage_manifest.yaml`'s own history (as an appended `UPDATE:` correction, not a silent rewrite) rather than
deleted, per this repo's evidence-preservation practice — see `configs/stage_manifest.yaml`'s
`table5.q4_sortbykey_splits`/`q5_topk_splits` entries for the full evidence trail.

## What's here

- `q4_sortbykey/split_manifest.json` + `split_NN_train_ids.txt` / `split_NN_test_ids.txt` (seeds 00-09) —
  bubblesort (`BubbleSortPass`) vs. topk (`TopKPattern`) taxonomic split, 489 labeled files, 70/30.
- `q5_topk/split_manifest.json` + `split_NN_train_ids.txt` / `split_NN_test_ids.txt` (seeds 00-09) —
  manual (`SelectionStep`) vs. builtin (`FindExtremum`) vs. novel taxonomic split, 526 labeled files, 70/30.

Both experiments use the same real, confirmed generation method (found in the source notebooks, not
inferred from the paper): `shuffled = labeled_df.sample(frac=1, random_state=seed).reset_index(drop=True)`,
`split_point = int(len(shuffled) * 0.7)`, for `seed in range(10)`.

## ID scheme (corrected)

The earlier scaffold-only version of this README claimed split IDs would match `submission_id` values in
`data/submission_ids/*.csv` (e.g. `correct_5_226`, no extension). The real files actually use the `file`
column exactly as the source notebooks and `batch_report.py`-generated CSVs record it — **with the `.py`
extension** (e.g. `correct_5_226.py`), matching `detectors/q1-q4-batch-validation/q4_report.csv` and
`detectors/reporting-batch/topk_report.csv`'s own `file` column, not the bare `submission_id` scheme.

## Verification

- **Q4 (`q4_sortbykey`): all 10 seeds independently confirmed, exact match.** The source notebook itself
  saved its full 10-seed pooled test predictions to Drive
  (`data/labels_scores/q4_embeddings_crossvalidation.csv`, 1,470 rows = 10 seeds × 147 test rows/seed,
  already `evidence: real_csv` in `configs/stage_manifest.yaml` for `q4_taxonomy_embedding_crossvalidation_10seed_pooled`).
  Every one of the 10 recorded test-set file lists here is a byte-for-byte exact match to that CSV's
  per-seed test-set membership.
- **Q5 (`q5_topk`): seed 0 independently confirmed, exact match; seeds 1-9 replayed, not independently
  recorded elsewhere.** The notebook's earlier single-split cell (`SPLIT_SEED=0`, before the multi-seed
  loop was added) saved its result to Drive, matching
  `data/labels_scores/q5_taxonomy_crossvalidation_shuffled_seed0_results.csv` (158/158 files, byte-for-byte
  exact). The multi-seed loop itself (cell 24 of the notebook) never exported per-seed file lists to Drive
  or as a download — only the aggregate mean/SD accuracy was printed and saved. Seeds 1-9's split files
  here are produced by replaying the exact confirmed deterministic code against the exact confirmed input
  CSV; given seed 0's exact match and pandas' seeded `.sample()` being fully deterministic for a fixed
  input frame, these are expected to reproduce the original notebook run exactly, but this rests on
  procedure-replay, not an independently recorded artifact, for those 9 specifically. This is why
  `q5_taxonomy_embedding_crossvalidation_10seed_pooled`'s own `evidence:` field in `stage_manifest.yaml`
  remains `real_notebook_output` rather than `real_csv` even after this update — the accuracy figures for
  seeds 1-9 are still transcribed from printed output, not recomputed from a raw predictions file. The
  split *membership* for those seeds is new and real; the per-file *predictions* for those seeds still
  don't exist as a raw artifact.

`scripts/regenerate_splits.py --experiment <q4_sortbykey|q5_topk> --check` reproduces this independently
in this repo: it recomputes each experiment's labeled subset directly from the real source report CSV,
regenerates all 10 seeds' train/test membership from the same seeded-shuffle code, and diffs the result
against the recorded `split_NN_*_ids.txt` files. Both experiments currently pass with an exact match on
every seed.

## Layout

```
<experiment_name>/
  split_manifest.json       # generation method, label rule, seeds, source report CSV, verification detail
  split_00_train_ids.txt    # one file name per line (e.g. correct_5_226.py)
  split_00_test_ids.txt
  ...
```

## Why both a seed-based regeneration path AND explicit recorded ID files

`scripts/regenerate_splits.py` regenerates the splits deterministically from `split_manifest.json`'s
`seeds` field and the real source CSV, as a cross-check. But "here is the seed, trust the regeneration"
and "here are the exact IDs used in the reported run" are different auditability claims. Both are kept
here: if the regenerated IDs and the recorded IDs ever disagreed, the recorded ID files would be
authoritative for what actually produced the reported numbers, and a mismatch would itself be worth
flagging in `docs/KNOWN_CAVEATS.md`. As of this writing they agree exactly, for every seed, in both
experiments.
