# Known caveats affecting reported numbers

**Regenerated from `../provenance/detector-version-log.md`.** An earlier version of this file described a
`TopKPatternExtended`/`DELEGATES`+`SELF_RECURSIVE` fix and a 79.7%→91.9% Q5 progression, a v1.1.0-scoped
`ConditionalCount` span bug, and a "measured, not assumed" CodeBERT-vs-lexical Table 5 comparison — none
of that corresponds to anything in any real artifact gathered for this project. It has been replaced
below with what the evidence actually supports; see `../VERSIONING.md`'s "Corrected from an earlier,
guessed version" note.

- **`BubbleSortPass` is the one competency in the whole library that still mixes a primitive directly
  alongside a higher-level sibling** (canonical bug #19, detector checkpoint `fixq4`) — a real,
  documented resolver limitation, not a bug in the reported scores themselves: two sibling slots needing
  the same wrapped competency (`LoopStep2`) resolve once and share a single `Result`, so an independent
  per-slot fix (the treatment `TopKPattern` got) would require a change to the resolver's core matching
  loop. Left unfixed deliberately, with zero established correctness impact.
- **The `NESTED` identity-comparison bug (canonical bug #18) was discovered via `CountedSearch`'s
  restructuring, not via `TopKPattern`'s** — this repository's own `detector-version-log.md` documents a
  correction to its own earlier, diff-based inference on this point. The fix itself
  (`detectors/fixq4`) is unaffected; only which real submission/case first surfaced it is
  corrected.
- **Q4's remaining gap (22.4%, `SortByKey = ANY(BubbleSortPass, TopKPattern)`):** recursive
  partition-based sorting and an explicit quicksort delegate are real, unmodeled diversity — flagged, not
  built, because it represents a disproportionate engineering cost relative to real-world frequency. No
  batch script or CSV for the 13.1%/64.4%/77.6% figures behind this has been supplied (conversation/paper-reported
  only, corroborated across 2 independent documents).
- **Q3's remaining long tail (~6%, before/after the `.insert()` fix):** a list comprehension form, a
  ternary-guarded assignment, and a recursive delegate are unmodeled for the same reason. Same evidence
  status as Q4: conversation/paper-reported (93.6%→94.0%), no batch script or CSV.
- **Function-scoping is two independent layers, not one** — `Evidence.scope` (a resolver-level guard
  against combining evidence from two different functions within one competency, added at
  `detectors/v1.2.0`) and a separate `function_name` parameter on the reporting layer
  (restricts resolution to one named function's own subtree, closing a different gap — an unrelated
  helper function elsewhere in the file independently satisfying a competency, canonical bug #13, added
  at `detectors/reporting-batch`). Conflating the two is a real risk when reading the code.
- **Q5's whole-file-vs-scoped correction is real, CSV-backed, and symmetric**: 83.0%→78.2%
  (correct-labelled), 76.9%→75.0% (wrong-labelled) — see `data/labels_scores/q5_final.csv`, derived from
  `detectors/reporting-batch/topk_report.csv`. A further, smaller unscoped shift to 82.1% (not
  78.2% — the scoped figure is unaffected) was reported once, after `TopKPattern`'s later level-layering
  refactor, traced to a smaller-scale instance of the same resolver limitation as `BubbleSortPass`'s own
  exception above — conversation-reported only, no CSV.
- **A stale "33%" Q2 figure is described inconsistently across four passages in three documents** — two
  read it as the counter-strategy's share, two read it as the alternative (non-counter) strategy's share.
  The corrected, load-bearing figures (85.2%/0.7%/4.5%/90.4%) supersede it regardless of which reading is
  correct; see `../provenance/detector-version-log.md`'s dedicated write-up if the historical question matters
  to you.
- **The stub semantic-backup backend has no real discriminative power, measured directly** (0.77
  similarity on a genuinely related function pair vs. 0.79 on a genuinely unrelated pair) — this is a
  real, negative result (`data/exemplar_registry/`), not a placeholder. Real CodeBERT inference has never
  been run in any sandbox used for this project (huggingface.co blocked). This is unrelated to, and
  should not be confused with, the separate "companion paper" embedding-model work referenced in
  `configs/stage_manifest.yaml`'s `table5:` block, which remains entirely unsupplied.
- **A real, out-of-sandbox Colab run of raw `microsoft/codebert-base` (2026-07-29) also produced no
  discriminative signal** — `related vs related: 0.958`, `related vs unrelated: 0.964`, i.e. unrelated
  code scored *higher* — but for a different, well-documented reason (anisotropy in raw pooled
  transformer embeddings, not a lack of semantic content in the signal). A follow-up switch to
  `Salesforce/codet5p-110m-embedding` has real code and a documented `transformers`-compatibility fix
  (see `detectors/semantic-colab-validation/`); the first comparison run under it was
  self-flagged in the source conversation as contaminated (a filtered, non-representative "wrong" group).
- **A redesigned attempt (2026-08-08), fixing that contamination, produced the first real AUC this
  project has ever generated for the semantic backup layer's actual job — and it's a strong, inverted
  negative result, not a positive one.** Bootstrapped across 10 exemplar-registry draws: mean AUC
  0.098 (SD 0.039), pooled AUC 0.097 across 1,510 scored pairs — genuinely-wrong submissions score
  *systematically more* similar to correct exemplars (~0.94–0.96) than genuinely-novel-correct
  submissions do (~0.79–0.81), the reverse of what the layer's design assumes. See
  `detectors/semantic-backup-layer-validation/README.md`. **Originally `conversation_reported_only`
  (pasted Colab output, internally self-consistent but nothing else on file); now upgraded to
  `evidence: real_csv`** — the two raw per-run/per-submission CSVs, and then the executed notebook itself,
  were both later supplied and independently reproduce every figure exactly (see
  `scripts/regenerate_semantic_backup_auc.py`), plus a previously-unsupplied sanity-check similarity pair
  for the `codet5p-110m-embedding` backend. One anomaly remains genuinely unresolved even in the executed
  notebook: every code cell's `execution_count` is `None` despite real, populated outputs, so the conversation's
  own "cell 13"/"cell 15" references still can't be checked against actual cell positions. Still not a
  finished companion-paper result — that's a separate, larger scope — but the AUC number itself is now as
  solid as this project's evidence gets.
- **Q5's TopKPattern has a confirmed but uncharacterized false-positive mode, found while validating a
  real 2026-08-08 delegation-based extension (`TopKPatternExtended`).** A bubble-sort-style helper
  (`correct_5_416.py`) coincidentally satisfies TopKPattern's combinatorial loop/test/removal shape
  without actually implementing the find-max/remove/append pattern the check exists to identify — not a
  defect introduced by delegation, but a latent bug newly exposed by testing TopKPattern against a wider
  variety of helper-function bodies than inline-only resolution ever did. Manually sample-checked 7 of 17
  `TopKViaDelegate` catches (6 genuine, 1 false positive), not extrapolated to a full-population rate — so
  Q5's reported 91.9%/80.6% (Table 4) is explicitly flagged, in both the paper's own §8 Limitations and
  this repo's `configs/stage_manifest.yaml`, as very likely a slight overstatement by an uncharacterized
  amount, not a fully row-by-row-verified figure the way Q1's 99.5%/97.6% is. See
  `detectors/q5-delegation-clustering-fix/README.md` and
  `scripts/regenerate_q5_delegation_breakdown.py`.
- **A real, explained baseline drift**: TopKPattern's own correct-side coverage moved from 78.2%
  (`data/labels_scores/q5_final.csv`, the original figure) to 79.7% when re-measured against the current
  codebase for the delegation-fix round above — confirmed by direct diff (exactly 6 correct-labeled files
  flip 0→1, zero wrong-labeled files change) and traced to an intervening, unrelated fix (Q1's
  `SHARED_BINDING`/`all_names` change) incidentally shifting a handful of TopKPattern's own combinatorial
  matches. Both figures are real and both are preserved — `q5_final.csv` is not amended in place.
- **A real embedding-CLUSTERING discovery (2026-08-08, a later round than the AUC finding above) is what
  actually motivated the TopKPatternExtended fix — and it has a thinner evidence tier than everything
  else on this page.** Hierarchical clustering of Q5's 43 correct-labeled novel submissions' embeddings
  found one dominant 38-file cluster; reading real files from it found the delegation pattern the fix
  above addresses. Unlike the AUC finding, no standalone embeddings/distance-matrix CSV was ever saved by
  the notebook — only the dendrogram chart and the printed cluster listing survive, both extracted
  directly from the executed notebook's own real output (`evidence: real_notebook_output`, not
  `real_csv`). A real methodological catch is preserved alongside it: a silhouette-score sweep alone
  picked k=9 (still rising at the edge of the tested range — the classic overfitting signature on a small
  sample), while cutting the same dendrogram by distance threshold instead recovered the structure that
  manual file-reading then confirmed was real. See
  `detectors/semantic-backup-layer-validation/README.md`'s "The clustering extension" section.
- **A real bug in the semantic backup layer's own exemplar registry, found and fixed 2026-08-07, dated
  earlier than the clustering finding above but scoped to a different question entirely (the registry's
  own integrity, not Q5's structural coverage).** Building a real exemplar-mining script
  (`mine_exemplars.py`) forced every hand-written exemplar through the actual structural resolver for the
  first time, surfacing that both of GuardedInput's original exemplars scored `final_score=0.0` — a bare
  `while` condition, no nested `if`, never actually satisfied GuardedInput's own rule. Fixed and
  independently re-verified in this audit (both exemplars now score exactly 1.0; a new `audit_registry()`
  utility correctly flags `AccumulateThenCount` as unverifiable — it lives in a module never supplied to
  this project — rather than assuming it's fine). The registry expanded from 5 exemplars/2 competencies to
  19 exemplars/8 competencies, all still hand-written; a SAME/CROSS/UNRELATED discriminative-power check
  independently reproduced the developer's own reported 86.7% lexical pairwise win rate exactly. This is
  real progress toward, but is explicitly **not yet**, the "10 competencies, 27 exemplars, partly
  real-mined" registry that a later paper/methodology revision describes as finished — no real corpus
  mining has actually been run in any artifact supplied to this project, and this repo's Table 4 and Q5
  delegation breakdown are unaffected either way. See
  `detectors/mine-exemplars/README.md` and
  `scripts/regenerate_semantic_backup_exemplar_audit.py`.
- **A second mine_exemplars batch (content-dated 2026-08-08/09, delivered 2026-09-17) closed the real-
  corpus-mining gap the round above left open, expanded the exemplar registry to the "10 competencies,
  27 exemplars" state a reference document once described as finished, and — as a direct side effect of
  supplying the actual files that round's development used — resolved a discrepancy this audit had
  previously left open as an unconfirmed hypothesis.** Real Refactory corpus mining (conversation-reported only,
  no corpus ever supplied here) found `ConditionalCount` in 248/291 submissions, `AccumulateThenCount`
  in only 2/291 (a genuinely rare strategy, not just under-sampled), and two new competencies,
  `FunctionalUniqueCheck` (13/291) and `DelegatesUniqueness` (227/291, cross-function). A second,
  independent instance of the same class of integrity bug GuardedInput had: 2 of 3
  `AccumulateThenCount` exemplars also scored `final_score=0.0` (`.count(` required, `len(...)` doesn't
  qualify) — now corrected. The delivered `semantic_backup.py`'s registry is confirmed, by direct
  inspection, at exactly 10 competencies / 27 exemplars. Using the delivered `semantic_cache.zip`'s real,
  content-hash-keyed embedding cache (24 real vectors per backend, unpickled and independently
  reprocessed, not re-typed from the transcript, with a guard that raises if any live network call would
  be needed), this audit exactly reproduced the reported codet5p numbers for the 8-competency subset the
  cache covers (696/852 = 81.7% win rate, 16/21 = 76.2% worst-case) and the reported lexical numbers for
  the full 10-competency registry (1262/1428 = 88.4% win rate, 15/27 = 55.6% worst-case). **The
  previously-open "bare-while GuardedInput reconstruction scores 1.0, not the claimed 0.0" discrepancy is
  now resolved with hard evidence**: this round supplied the actual `competency.py` that round's
  development used, confirmed byte-for-byte identical to `detectors/fixq4` (predating the Q1
  fix that added `while`-condition `TEST` synthesis) — reconstructing the same bare-while shape against
  that exact file now scores `final_score=0.0`, exactly as originally claimed. Also confirmed by direct
  execution: the delivered "real model chain" (`test_real_data.py -> pw01_competencies.py ->
  q2_competencies.py`) does not actually run in this sandbox (`pw01_competencies.py` has unresolved
  relative imports to submodules never supplied), so `AccumulateThenCount`/`FunctionalUniqueCheck`/
  `DelegatesUniqueness` remain unverifiable here — same practical gap as the first round, different,
  more specific cause. A later scoping fix described in the same conversation (lexical 90.6%/74.1%) and three
  documents it references were never actually delivered to this project — remain conversation-reported only.
  **Table 4 and the Q5 delegation breakdown are untouched by any of this.** See
  `detectors/mine-exemplars-real-corpus/README.md` and
  `scripts/regenerate_semantic_backup_v2_audit.py`.
- **A third delivery — "here is the last version of `semantic_backup_validation` notebook" (delivered
  2026-09-17, no dating evidence beyond the delivery itself) — is the first GENUINELY EXECUTED copy of
  this notebook this project has ever received, and it fixes both remaining gaps the round above left
  open.** Every earlier copy of this notebook was confirmed entirely unexecuted; this one has all 10 code
  cells with `execution_count` set 1–10 and 9 with real output (real download progress bars for
  `codet5p-110m-embedding`'s weights, real weight-loading logs). It is self-contained (embeds
  `competency.py`/`test_real_data.py`/`report.py`/`pw01_competencies.py`/`q2_competencies.py` directly),
  and diff-confirmed to embed this repo's own **current HEAD** structural model — unlike both earlier
  mine_exemplars rounds, which turned out to be running against a pre-Q1-fix snapshot. Two real fixes
  land here: (1) `pw01_competencies.py`'s broken relative imports are fixed (`from .core import ...` →
  `from competency import ...`), confirmed by direct execution that the real
  `test_real_data → pw01_competencies → q2_competencies` chain now imports cleanly in this sandbox for
  the first time; (2) the `DelegatesUniqueness`/`ConditionalCount` scoping fix
  (`DELEGATING_FUNCTION`/`runtime_scoped_exemplar()`), which the round above's conversation described as
  implemented but was grep-confirmed absent from that round's delivered code, is now real, present code.
  **Independently reproduced by direct execution in this audit**: `audit_registry()` now reports **zero**
  problems against the complete real chain (all 10 competencies, all 27 exemplars) for the first time
  ever in this project; the post-fix lexical numbers reproduce exactly (1294/1428 = 90.6% win rate, 20/27
  = 74.1% worst-case, with **zero** remaining `DelegatesUniqueness` failures, down from 5 of 12); three
  synthetic `TopKPatternExtended` structural regression cases (explicitly labeled in the notebook as
  "structural, not semantic-similarity," changing no real corpus-derived percentage) reproduce exactly.
  The codet5p numbers for the full 10-competency registry (84.2% win rate, 81.5% worst-case) match the
  round above's conversation-reported figure exactly, now backed by a genuinely executed notebook rather than a
  transcript (`evidence: real_notebook_output` — `huggingface.co` still blocked here, so not independently
  re-run). **Table 4 and the Q5 delegation breakdown are untouched by any of this.** See
  `detectors/semantic-backup-validation-executed/README.md` and
  `scripts/regenerate_semantic_backup_v3_audit.py`.
