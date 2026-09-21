# Q4 and Q2 embedding taxonomy cross-validation — extending the Q5 methodology

**Real date: 2026-08-05, 17:40** (per the conversation export's own opening timestamp, "05/08/2026 at 17:40") —
same day as the batch-validation run and Q1 fix (`../q1-q4-batch-validation/`,
`../q1-shared-binding-fix/`), later in the evening. See
`../../provenance/detector-version-log.md`'s "Q4/Q2 embedding cross-validation" section for the full
verification writeup this README summarizes.

## What this is

A direct extension of the already-validated Q5 (Top-K) manual/builtin embedding cross-validation (same
10-random-70/30-split, pooled-confusion-matrix methodology as
`../ast-taxonomy-crossvalidation/`) to the two other Refactory questions with an analogous
multi-strategy taxonomic split: Q4 (`SortByKey` = `ANY(BubbleSortPass, TopKPattern)`) and Q2 (`UniqueCheck`'s
counter vs. functional-pipeline branches). **Q1 and Q3 are deliberately excluded**, per the conversation's own
explicit scoping note: both are single-strategy competencies whose real finding this round was a
structural-matching *bug* (see `../q1-shared-binding-fix/`), not a taxonomic split between
multiple legitimate strategies — there's no analogous "does an independent method recover this same
distinction" question to ask for either.

## What's here

- `q2_q4_embeddings_crossvalidation_with_Results.ipynb` — the real, executed notebook (12 code cells, all
  with real printed output; confirmed via direct inspection — non-`None` `execution_count` and populated
  `outputs` on every code cell).
- `Copie_de_q2_q4_embeddings_crossvalidation.ipynb` — an unexecuted copy (confirmed: every code cell has
  `execution_count: None` and zero outputs). **NOT byte-identical to the executed version** — a real, direct
  `diff` finds exactly two differing cells, both a folder-path fix: the copy uses
  `Q4_FOLDER = f"{PROJECT_DIR}/refactory/data/question_4/code"` (and the Q2 analog), matching the layout
  the conversation's own scope note expected ("same layout as Q5"); the executed version uses
  `Q4_FOLDER = f"{PROJECT_DIR}/data/question_4/code"` (no `refactory/` prefix) instead — and it worked
  (489/489 Q4 files cached, 581/581 Q2 files cached, no "0 cached" symptom). The conversation's own text warns this
  exact failure mode can occur ("the way Q1's did initially") but does not narrate this specific fix
  happening for Q2/Q4 — the fix is real and diff-confirmed. **Resolved 2026-09-17**: asked directly in the
  audit conversation, Sonia explained she worked in two different environments/Drive mounts across this
  project — one (used for the unexecuted "template" copies) had the `refactory/` prefix, the other (the one
  every actual execution ran from) did not. This is not specific to Q2/Q4 vs. Q5 — the identical pattern
  recurs within Q5's own notebook pair too (see `../semantic-backup-layer-validation/README.md`).
  See `../../provenance/detector-version-log.md`'s "A direct clarification from Sonia" section for the full
  writeup.
- `colab_embeddings_validation_chat_export.txt` — the accompanying conversation (converted via `pandoc` from `2.
  The Colab embeddings validation.docx`).

## Verification performed this round

Every number below was independently recomputed from the notebook's own real printed output (per-seed
accuracy table + pooled confusion matrix), not taken from the conversation's own summary on faith — see
`../../scripts/regenerate_q2q4_taxonomy_crossvalidation.py`, which passes cleanly for all checks.

**Q4 (BubbleSortPass vs. TopKPattern):** 489 files labeled (420 topk, 69 bubblesort — the 22.4%
"novel"/unmatched group excluded, same convention as Q5's own `novel` handling). Mean accuracy across 10
seeds: 93.6% ± 2.1% (range 89.8%–95.9%) — computed directly from the per-seed table, matching the conversation's
own quoted "93.6% ± 2.1%" exactly. Pooled confusion matrix (1,470 predictions): bubblesort→bubblesort 200,
bubblesort→topk 4, topk→bubblesort 90, topk→topk 1176 — recomputing precision/recall/support from this
matrix directly reproduces the classification report's own printed cells exactly (bubblesort precision
0.69/recall 0.98/support 204; topk precision 1.00/recall 0.93/support 1266; accuracy 0.94). **This is a
stronger, tighter result than Q5's own manual/builtin check** (87.0% ± 2.3%) — and the confusion-matrix
asymmetry runs the *opposite* direction from Q5's (here `bubblesort` is the "broad, easy-to-fall-into"
cluster and `topk` the "narrow, tight" one; in Q5 `builtin` was the tight cluster and `manual` the broad
one) — a real, structurally-explicable finding (real bubble-sort implementations are homogeneous; the
"find max, remove, append" topk strategy admits more surface variety), not a copy-paste inconsistency.

**Q2 (counter vs. functional):** 581 files labeled (564 counter, 17 functional — `AccumulateThenCount`,
~0.7%, dropped as too rare for a stable centroid, same reasoning that excluded `novel` from Q5's headline
number). The headline 95.9% ± 1.6% accuracy is a **class-imbalance artifact, independently confirmed**:
`counter` is 96.8% of the pooled test set (1,694/1,750) — a classifier that always predicted `counter`
would score *higher* (96.8%) than what this classifier actually achieved (95.9%). The number that actually
matters, `functional`'s own precision/recall (0.33/0.27, support 56), is close to uninformative — the
model correctly identifies only 15 of 56 pooled functional examples, with errors running in both
directions in similar magnitude (31 counter→functional, 41 functional→counter), consistent with 17 real
examples being too few for a stable conclusion rather than a real negative finding. Every one of these
figures was independently recomputed from the pooled confusion matrix and matches the conversation's own
description exactly.

## Evidence status

**Upgraded to `real_csv` in a later round.** The notebook's own `q4_embeddings_crossvalidation.csv`/
`q2_embeddings_crossvalidation.csv` per-row outputs (saved to Sonia's Drive by the notebook's own last
cell) were not supplied alongside these notebooks — this checkpoint's stages were originally tagged
`real_notebook_output`, the same tag used for Q5's own 10-seed sweep, since only the printed execution
output could be independently verified. Both raw CSVs were supplied in a later round and now live at
`../../data/labels_scores/q4_embeddings_crossvalidation.csv` (1,470 rows) and
`q2_embeddings_crossvalidation.csv` (1,750 rows) — one row per seed/file test-set prediction
(`file, seed, true_label, predicted`). `scripts/regenerate_q2q4_taxonomy_crossvalidation.py` now reads
these files directly rather than transcribing printed output, and every per-seed accuracy, pooled
confusion matrix, and precision/recall figure above was reconfirmed to full floating-point precision — no
discrepancy found between the notebook's own printed summary and the raw predictions behind it.
`q4_taxonomy_embedding_crossvalidation_10seed_pooled` / `q2_taxonomy_embedding_crossvalidation_10seed_pooled`
in `configs/stage_manifest.yaml` are now `evidence: real_csv`. **This is NOT the same experiment as
`configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits` entry**, which remains `PENDING` — that entry
refers to the still-unsupplied companion-paper novel-detection/train-test-split experiment, while this
notebook validates the AST taxonomy's own Q4/Q2 splits using embeddings as an external check, mirroring
`q5_taxonomy_embedding_crossvalidation` rather than `table5.q5_topk_splits`. See
`../../provenance/detector-version-log.md` for the same distinction already drawn for Q5.
