# Semantic backup layer — real Colab validation attempt (in progress, not yet numerically validated)

**Real dates:** notebook prompts span 2026-07-29 through 2026-07-31 (`semantic_29_chat_export.txt`'s own
date markers). This is **not** a finished result — Sonia's own framing when supplying these artifacts:
"This work will be continued with other versions." See `../../provenance/detector-version-log.md`'s
"Real-CodeBERT/CodeT5+ Colab validation of the semantic backup layer" section for the full,
evidence-by-evidence writeup this README summarizes.

## What's here

- `semantic_backup_validation.ipynb` — the earlier of the two notebooks (built in direct response to a
  "build me a Colab notebook" request, 29/07). Raw `microsoft/codebert-base`, Drive-mount optional/
  commented-out, bare local file paths (not yet `PROJECT_DIR`-prefixed).
- `semantic_backup_validation_30.ipynb` — the later notebook ("File... from 30/07"). Drive-mounting is
  the default path; the embedding backend has been swapped to `Salesforce/codet5p-110m-embedding`
  (including a real, documented `transformers`-compatibility fix — see cell-8's own comment) after raw
  `codebert-base` was shown, in the conversation, to suffer from anisotropy (near-identical similarity for
  related and unrelated code). This notebook's own `cell-12` (the test-set-construction cell) still has
  the **original**, unmodified filter — later hand-edits described in the conversation (broadening the
  comparison group, then a proposed cross-exercise fix) are **not** reflected in this file; they exist
  only as conversation-quoted text.
- `semantic_29_chat_export.txt` — the accompanying conversation history, converted from `semantic_29.docx` via
  `pandoc` (a genuine `.docx` this time, unlike `Competency_Extraction_Methodology.docx` elsewhere in
  this repo's history, which turned out to be plain Markdown saved under a `.docx` extension).

## What is and isn't real evidence here

**Real, executed output that exists:**
- The raw-codebert anisotropy result: `related vs related: 0.9579190015792847`,
  `related vs unrelated: 0.9641265273094177` — pasted, real Colab output, quoted in the conversation export.
- The real (unmodified) test-set counts from `semantic_backup_validation_30.ipynb`'s own cell-12 logic:
  novel-correct = 43, genuinely-wrong = 5 (against real `topk_report.csv`, `FindExtremum` competency).

**Conversation-quoted, NOT present in either notebook file (no re-uploaded edited version exists):**
- The "Option 1" broadened-filter edit (genuinely-wrong count becomes 108 — an exact match to this
  project's already-established 108 wrong-labeled Q5 submissions, a strong independent cross-check that
  this exchange really happened against the real data).
- The resulting `cell 6` similarity output (novel-correct mean=0.851/std=0.086 n=43; genuinely-wrong
  mean=0.930/std=0.027 n=108) — self-flagged in the same conversation as **contaminated and backwards** (the
  broadened "wrong" group is dominated by submissions that are structurally correct but fail the test
  suite elsewhere, per this paper's own already-published §5.3 finding).
- A second proposed fix (true negatives from an unrelated Refactory exercise) — given as code to
  hand-apply, never confirmed as applied or run.

**Does not exist anywhere in this repo or any supplied artifact:**
- Any real similarity number for `Salesforce/codet5p-110m-embedding`'s own sanity check.
- Any AUC/ROC number, for either backend.
- The "companion paper" itself, or its Table 5 (10 train/test splits) — that is a **separate,
  still-entirely-unsupplied experiment**, not the same thing as the exemplar-similarity-threshold work
  in these notebooks. See `../../configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits` /
  `q5_topk_splits` entries, which remain fully `PENDING`.

## Status

Preserved here as real, dated artifacts documenting real (if inconclusive) work — not because they
produce a citable number yet. `../../configs/stage_manifest.yaml`'s `table5.semantic_backup.backends`
block cites this checkpoint directly (`codebert_colab`, `jina_v2_code`, `codet5p_110m_embedding`,
`exemplar_registry_real_mined` entries).
