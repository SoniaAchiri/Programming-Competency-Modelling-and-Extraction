# AST taxonomy cross-validation via embeddings (Q5, manual/builtin/novel)

**Real dates:** 2026-07-31 (design + first real run) through 2026-08-04 (the real, executed 10-seed
robustness sweep, plus a real, executed single alternate/shuffled split). See
`../../provenance/detector-version-log.md`'s "AST taxonomy cross-validation via embeddings", "A real, executed
alternate split", and "The real 10-seed sweep" sections for the full provenance writeup this README
summarizes.

## What this is — and what it is NOT

This is an **independent external check on the AST taxonomy itself**: does a pretrained code-embedding
model (`Salesforce/codet5p-110m-embedding`), given no knowledge of which AST rule matched a submission,
recover the same `manual` (`SelectionStep`) / `builtin` (`FindExtremum` but not `SelectionStep`) split
the structural competencies already assign? It is **not** the semantic-backup layer's own validation
(catching novel-but-correct submissions the AST rules miss) — that is a separate, still-inconclusive
thread, preserved at `../semantic-colab-validation/`.

## What's here

- `ast_taxonomy_crossvalidation.ipynb` (21 cells, self-contained) — the original notebook: 70/30 split
  (literal first-70%/last-30% by `topk_report.csv` row order, `SHUFFLE_BEFORE_SPLIT` flag defaults
  `False`), one embedding centroid per structural label built from the training 70%, held-out 30%
  classified by nearest centroid.
- `ast_taxonomy_crossvalidation_results.csv` (158 rows) — the real, unshuffled test-set output. Also
  copied to `../../data/labels_scores/q5_taxonomy_crossvalidation_results.csv`.
- `ast_taxonomy_crossvalidation_results_shuffled_seed0.csv` (158 rows) — a real per-file CSV for a single
  alternate run, `SHUFFLE_BEFORE_SPLIT=True`, "seed=0." Also copied to
  `../../data/labels_scores/q5_taxonomy_crossvalidation_shuffled_seed0_results.csv`.
- `ast_taxonomy_crossvalidation_with_results.ipynb` — the **primary source for the 10-seed sweep**: the
  same methodology re-run for `SEEDS = list(range(10))`, with all real printed execution output preserved
  (per-seed table, mean/std summary, pooled confusion matrix, both pooled classification reports).
- `Copie_de_ast_taxonomy_crossvalidation.ipynb` — a code-identical, outputs-stripped copy of the notebook
  above (confirmed cell-for-cell) — kept as the "code only" reference copy.
- `chart_per_seed_accuracy.png`, `chart_pooled_confusion_matrix.png`, `chart_pooled_precision_recall.png`
  — three real chart images, each independently confirming figures printed in the notebook above.
- `steps_for_semantic_backup_chat_export.txt` — the conversation accompanying the original 31/07 run, converted
  from `Steps for semantic_backup.docx` via `pandoc`.
- `multi_seed_loop_chat_export.txt` — the conversation accompanying the single shuffled-seed-0 alternate run,
  converted from `multi-seed loop.docx`.
- `semantic_backup_layer_findings_chat_export.txt` — the conversation accompanying the 10-seed sweep and the
  second paper/methodology-note revision, converted from `1. The Semantic Backup Layer Findings by
  cross-validation.docx` (its filename does not match its content — it continues this same AST-taxonomy
  thread, not the separate semantic-backup-layer thread its name suggests; flagged, not over-interpreted).

## Real, independently reproduced results

`../../scripts/regenerate_taxonomy_crossvalidation.py` recomputes the confusion matrix and every reported
figure directly from BOTH real CSVs above — this session independently recomputed both too, and each
matches its source's quoted output to full floating-point precision:

- **Unshuffled 70/30 split** — confusion matrix manual [83, 14, 0], builtin [2, 48, 0], novel [5, 1, 5];
  manual/builtin-only accuracy **89.1%** (131/147) — the figure originally published in the paper's §5.5,
  now superseded (see below); overall 3-way accuracy 86.1% (136/158); novel recall 45.5% (5/11).
- **Shuffled seed=0 split** — confusion matrix manual [83, 15, 0], builtin [6, 38, 0], novel [5, 0, 11];
  manual/builtin-only accuracy **85.2%** (121/142); overall 3-way accuracy 83.5% (132/158); novel recall
  68.75% (11/16). This was the first real evidence that the 89.1% figure was not stable split-to-split.

`../../scripts/regenerate_10seed_taxonomy_sweep.py` verifies the full 10-seed sweep's internal arithmetic
against its own transcribed real notebook output (no raw per-submission CSV exists for 9 of the 10 seeds,
so this checks that the reported mean/SD and both pooled classification reports are exactly what the
per-seed table and pooled confusion matrix arithmetically produce, not that they're independently
re-derivable from scratch):

- **10-seed sweep** — manual/builtin agreement: mean **87.0%**, SD 2.3%, range 82.6%-89.8%; 3-way
  accuracy: mean 83.7%, SD 2.3%; novel recall: mean 49.5%, SD 7.5%, range 40.0%-61.5%. Pooled across all
  10 seeds (1,580 predictions, explicitly NOT fully independent — the source itself flags this, since the
  same ~526 files recur reshuffled 10 ways): pooled manual/builtin-only report — manual precision
  0.94/recall 0.87 (support 993), builtin precision 0.75/recall 0.88 (support 448), accuracy 0.87 (n=1441).

## The published paper — now updated a second time to report the sweep, not the single run

`../../papers/2026-08-04_Structural_Competency_Extraction_Paper.pdf` (supplied 2026-09-12, read in full,
diffed page-by-page against the prior PDF) confirms the Abstract and §5.5 now report the 10-seed sweep's
87.0% ± 2.3% mean and the pooled 0.94/0.75 precision figures — the original single-run 89.1%/0.98/0.77
numbers no longer appear anywhere in the paper. Everything else in the 20-page document is byte-for-byte
unchanged. See `../../papers/README.md` and `../../provenance/detector-version-log.md`'s "The published
paper, updated again" section for the complete word-for-word diff.

The same-day methodology note (`../../methodology/2026-08-04_Competency_Extraction_Methodology.docx`) was
also substantially rewritten, extending its canonical bug table from 19 to 21 entries — see
`../../methodology/README.md`.

## What's still open

- The two "seed 0" runs above (the standalone shuffled-CSV run and the 10-seed sweep's own internal seed
  0) are numerically close but NOT identical (acc_3way matches exactly at 0.835443; acc_manual_builtin
  0.852113 vs. 0.868966; n_novel_test 16 vs. 13) — both real, both labeled "seed 0" by their own sources,
  but evidently two different code paths/shuffle states. Flagged in `configs/stage_manifest.yaml` rather
  than silently treated as duplicates.
- No raw per-submission CSV exists in this repo for 9 of the 10 seeds in the sweep — only the notebook's
  own printed summary/pooled output, cross-checked against three chart images and a conversation export. This is
  why `q5_taxonomy_embedding_crossvalidation_10seed_pooled` in `configs/stage_manifest.yaml` carries
  `evidence: real_notebook_output` rather than `evidence: real_csv`.
- The "19 vs 21 bug count" accounting discrepancy between the methodology note's own table and the
  paper's Table 4 body text remains open — see `../../methodology/README.md`.
