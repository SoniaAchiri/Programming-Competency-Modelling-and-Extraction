# Public reproducibility repository — status

Delivered as `competency-extraction-repro.zip`.

## What's real and done

- **Real code for every detector checkpoint** — `detectors/<real-date>_<Sonia's-own-label>/` (fourteen
  checkpoints, `V1.0.0` through `semantic_backup_layer_validation`, plus the
  semantic-backup extension, two diff-bounded intermediate saves, and a real Colab semantic-backup
  validation checkpoint), not an invented `v1.0.0`-`v1.4.0` ladder. Provenance is checkpoint label + real
  date (zip-preserved mtime / diff-bounding / PDF/docx metadata), since no commit
  history exists.
- **Real taxonomy snapshots** for every taxonomy-affecting checkpoint, each scoped to the question(s) it
  actually changed, with real coverage figures and explicit `evidence: real_csv`/`conversation_reported_only`/
  `real_notebook_output` tagging.
- **`configs/stage_manifest.yaml`** — every number cross-checked against the log. **Every `*_final` stage
  for all five Refactory questions (Q1 through Q5) is `evidence: real_csv`.** The AST-taxonomy embedding
  cross-validation now has **five** real stages: Q5's original single unshuffled split, Q5's single
  shuffled alternate split, Q5's full 10-seed sweep (`evidence: real_notebook_output` — only seed 0 of its
  10 seeds ever got a raw CSV), and Q4's and Q2's own 10-seed sweeps — **now `evidence: real_csv`, upgraded
  this round** once the raw per-seed/per-file prediction CSVs (previously saved to Drive but not supplied)
  arrived and were independently recomputed to full precision. Intermediate/superseded stages (the pre-fix
  Q1 baseline, Q4's two sub-strategy figures, Q5's unscoped runs) remain `conversation_reported_only`. **Update
  (part 21): the `q4_sortbykey_splits`/`q5_topk_splits` train/test-split entries are now real
  too** — real split-index files (seeds 00-09, 70/30) were supplied and independently verified, and turned
  out to be the *same* experiment as the real Q4/Q5 embedding-taxonomy cross-validations above, not the
  distinct "companion paper" scope this line previously described (that framing, repeated in several
  files, was wrong — see part 21 below for the full evidence trail). The `table5:` block's
  `semantic_backup.backends` list still has two genuinely separate, unrelated `PENDING` items
  (`jina_v2_code`, `codet5p_110m_embedding`).
- **Real submission-ID manifests for all five questions** (`data/submission_ids/qN_*.csv`), mechanically
  projected from the real batch-report CSVs via `scripts/build_submission_ids_from_batch_reports.py`.
  Correct/wrong counts confirmed exact against Table 3 for every question.
- **Real per-submission labels/scores for all five questions** (`data/labels_scores/qN_final.csv`), via
  `scripts/build_labels_scores_from_batch_reports.py`.
- **All regeneration scripts verified to run cleanly**, including a new one this round
  (`scripts/regenerate_q2q4_taxonomy_crossvalidation.py`). `scripts/regenerate_table4.py --stage final
  --check` passes end to end for all five questions. `pytest tests/` — 11/11 passing.
- `provenance/detector-version-log.md` itself is included in the repo (`provenance/`) and kept in sync with
  the Project doc of the same name, since it's the actual audit trail every other file cites.
- **Four real, dated paper snapshots** in `papers/` (pre-embedding-validation, first embedding-validation,
  the 10-seed-sweep version, and — new this round — the version with the Q4 embedding result written into
  §5.6), each diffed against its predecessor word-for-word rather than assumed.

**Re-verified clean, full suite**: `pytest tests/ -q` — 11/11; `scripts/regenerate_table4.py --stage final
--check` — all five questions match (Q5 still 91.9%/80.6%); `scripts/build_exemplar_registry.py --check`
— 0 problems, all 27 `final_score=1.0000`; `scripts/regenerate_q5_percentages.py --all-stages` — both Q5
stages match reported figures against their renamed checkpoints; a final repo-wide grep for any of the 23
old directory-name strings anywhere in the tree returns **zero hits** (not even a historical note this
time — unlike the pilot, there was no prior rename event to document).

## New this round, part 17: the exemplar registry — merged into `data/exemplar_registry/`, no new artifact needed

 The real, verified `EXEMPLAR_REGISTRY` (10 competencies, 27 exemplars)
already existed as delivered code in`detectors/semantic_backup_validation_executed/semantic_backup.py` — this repo's own most
current and most audit-clean semantic-backup checkpoint, where `audit_registry()` already reports zero
problems against the complete real chain in this project. The merge into 
`data/exemplar_registry/`'s CSV+files format was mechanical, as this repo's existing
`scripts/build_submission_ids_from_batch_reports.py`.

**What was built**: `scripts/build_exemplar_registry.py`. It extracts the checkpoint's embedded
`competency.py`/`test_real_data.py`/`pw01_competencies.py`/`q2_competencies.py`/`report.py` (they exist
only inside the notebook's own source cells in this checkpoint, same extraction routine as
`scripts/regenerate_semantic_backup_v3_audit.py`), builds the real full competency model, and — for every
one of the 27 exemplars — calls the live structural resolver (`model.resolve()`) directly to get a
freshly-computed `final_score`, rather than trusting any previously-reported number. This run:
`audit_registry()` reports 0 problems, all 27 exemplars score `final_score=1.0000`.

**Result**: `data/exemplar_registry/exemplars.csv` and `code/*.py` now hold the full 27-exemplar registry. 
Per-exemplar provenance (`mined` with an exact
submission ID where `semantic_backup.py`'s own comment names one — 2 `ConditionalCount` exemplars,
`correct_2_010`/`correct_2_016`; `mined` with the method/proportion documented but no individual filename
for 7 others; `hand-written` for 14; `hand-written (corrected)` for 4 that replaced originals
`audit_registry()` found scoring `final_score=0.00`) is transcribed directly from `semantic_backup.py`'s
own inline comments — nothing inferred. Full breakdown in `data/exemplar_registry/README.md` and
`provenance/detector-version-log.md`'s new entry for this round. `POPULATE.md` step 6 is now marked DONE.
`scripts/regenerate_table4.py --stage final --check` (5/5) and `pytest tests/` (11/11) both re-run clean
after this merge; Table 4 and the Q5 TopKPatternExtended delegation breakdown are untouched.



## New this round, part 15: the Refactory corpus license check — done, and a real misattribution corrected

`POPULATE.md`'s step 9 ("Refactory corpus license check") had sat as the one open item on that list not
gated on Sonia supplying a new artifact — it only required checking a public, third-party repository. Done
this round, directly against the corpus's own source, [github.com/githubhuyang/refactory](https://github.com/githubhuyang/refactory)
(Hu, Ahmed, Mechtaev, Leong & Roychoudhury, "Re-factoring Based Program Repair Applied to Programming
Assignments," ASE 2019 — paper reference [3]):

- **License: LGPL-3.0**, via a root `LICENSE` file (confirmed by fetching it directly — full LGPLv3 text,
  not a stub); GitHub's own license badge on the repo agrees. `data.zip` (the corpus archive: 2,442
  correct / 1,783 buggy attempts by 361 students, 5 assignments, an NUS intro Python course) sits in the
  same repository root as that `LICENSE` file, and no separate, dataset-specific license or terms exist
  anywhere in the README for it — the repository-wide LGPL-3.0 is the only license on file that could
  govern it.
- **A citation request, confirmed as a request rather than a separate binding term**: "If you use any part
  of our Refactory tool or data present in this repository, then please do cite our ASE-2019 Refactory
  paper" (quoted directly from the fetched README). Already satisfied by this project's own paper
  (reference [3]); now also recorded in this repository's own docs, independent of the paper.
- **No student consent/privacy language anywhere in the source repository or README** — a real gap the
  license itself doesn't address, since LGPL-3.0 is written for software libraries, not a corpus of
  identifiable student coursework.
  
**Practical conclusion, recorded in `data/submission_ids/README.md`'s own "On redistributing the corpus
itself" section**: LGPL-3.0, read literally, would not forbid redistributing the submission source code
itself. But applying a software library license to a corpus of student programming-assignment submissions
is not what LGPL-3.0 was written for, and no statement anywhere confirms the students themselves consented
to redistribution beyond the original research use. This repository therefore keeps its existing,
independently-already-conservative stance unchanged: it publishes `submission_id`s and derived
labels/scores only, never the students' own source code — exactly what `data/submission_ids/*.csv` and
every regeneration script already do. Nothing in those files or scripts changed as a result of this check;
it was a documentation-only round.


## New this round, part 13: the first genuinely EXECUTED semantic_backup_validation notebook, closing both gaps part 12 left open

A single-file upload — "here is the last version of `semantic_backup_validation` notebook", no
dating metadata (named by delivery date; its content places it after part 12 regardless of its unknown
exact date). **The first genuinely executed copy of this notebook this project has ever received** — 10
code cells, all with real `execution_count` (1–10) and 9 with real output (genuine download progress for
`codet5p-110m-embedding`'s weights, real weight-loading logs) — every earlier copy was confirmed entirely
unexecuted.

**Independently reproduced by direct execution in this audit**: `audit_registry()` is now fully clean
across all 10 competencies for the first time ever. The
post-fix lexical numbers reproduce exactly — 1294/1428 (90.6%) win rate, 20/27 (74.1%) worst-case, **zero**
remaining `DelegatesUniqueness` failures (down from 5 of 12) — confirming the fix does precisely what it
claims. Three synthetic `TopKPatternExtended` structural regression cases (explicitly labeled in the
notebook as "structural, not semantic-similarity," changing no real corpus percentage) reproduce exactly.
The codet5p numbers (84.2% win rate, 81.5% worst-case) match part 12's conversation-reported "after fix" figure
exactly, now backed by real notebook output (`evidence: real_notebook_output`).

New checkpoint `detectors/semantic_backup_validation_executed/`; new script
`scripts/regenerate_semantic_backup_v3_audit.py` (19/19 checks passing). **Table 4 and the Q5
TopKPatternExtended delegation breakdown are confirmed byte-for-byte unchanged.** Full test suite (11
tests) and both Table 4/Q5 regeneration scripts re-run clean. **The zip has still not been repackaged or
resent** — continuing to hold, now across three full rounds of this thread; a single notebook upload
isn't being treated as a signal the broader thread is complete.

## New this round, part 12: real corpus mining closes the exemplar-registry gap, and part 11's own open question is resolved with hard evidence

A second mine_exemplars batch — "A second version is here" — closed the real-corpus-mining gap part 11
left open. Real Refactory corpus mining, 
found `ConditionalCount` in 248/291 real submissions and two new competencies, `FunctionalUniqueCheck`
(13/291) and `DelegatesUniqueness` (227/291, cross-function); `AccumulateThenCount` verified in only
2/291 — a genuinely rare strategy, not just under-sampled. A second integrity bug, same class as
GuardedInput's: 2 of 3 `AccumulateThenCount` exemplars also scored `final_score=0.0` (needed `.count(`,
had `len(...)`) — now corrected. The delivered `semantic_backup.py`'s registry is confirmed, by direct
inspection, at exactly **10 competencies, 27 exemplars** — the exact figure the two reference documents
from an earlier round described as a finished future state, now backed by real, delivered,
independently-runnable code for the registry itself (not for Table 4, the Q5 breakdown, or the
real-corpus scan counts, none of which this round touches).

The delivered `semantic_cache.zip` turned out to hold **real, verified embeddings, not placeholders** —
unpickling it directly confirms 24 real 4096-d lexical vectors and 24 real 256-d codet5p vectors (correct
dimensionality for `Salesforce/codet5p-110m-embedding`), content-hash cross-referenced to 21 of the 27
registry exemplars (the 8-competency subset predating `FunctionalUniqueCheck`/`DelegatesUniqueness`) plus
the 3 `UNRELATED_SNIPPETS`. Using ONLY those real cached vectors (a guard raises loudly if anything
uncached were requested, so no live network call or fabricated value could sneak in), this audit exactly
reproduced the reported codet5p numbers for that 8-competency subset (696/852 = 81.7% win rate,
16/21 = 76.2% worst-case) and, separately via the network-free deterministic lexical backend, the 
reported numbers for the full 10-competency registry (1262/1428 = 88.4% win rate, 15/27 = 55.6%
worst-case); this time, the project has independently reproduced a codet5p number from real cached
model output.

**Most notably, this round resolves — with hard evidence — part 11's own genuinely
open question.** Diffing the delivered "Original files to load" against every checkpoint already in this
repo found `competency.py`/`test_real_data.py` byte-for-byte identical (0 diff lines) to
`detectors/fixQ4`, and `report.py` byte-for-byte identical to
`detectors/semantic_backup` — i.e. this is the ACTUAL `competency.py` the first mine_exemplars
round's development used, and it predates the Q1 fix, exactly as part 11 hypothesized but
could not confirm. The Q1 fix's own diff shows why the bare-while discrepancy existed: it added a brand
new `elif isinstance(node, ast.While):` branch to the `TEST` primitive detector (synthesizing `TEST`
evidence from a while loop's own condition) that fixQ4's version simply doesn't have. Reconstructing the
same bare-while GuardedInput shape against this now-supplied, actual `competency.py` scores exactly
`final_score=0.0` — matching the original claim precisely. Part 11's hypothesis paragraph is left
unedited in the log, per this project's evidence-preservation discipline; it was correct, and is now
proven.

New checkpoint `detectors/mine_exemplars_real_corpus/`; new script
`scripts/regenerate_semantic_backup_v2_audit.py` (13/13 checks passing); forward-pointing update notes
added to part 11's own README/script/manifest entry rather than editing them in place. **Table 4 and the
Q5 TopKPatternExtended delegation breakdown are confirmed byte-for-byte unchanged** (re-ran both
regeneration scripts fresh — still 91.9%/80.6% and the same 57-catch breakdown). Full test suite (11
tests) still passes. 
## New this round, part 11: a real exemplar-registry bug found and fixed — Table 4 and Q5's breakdown deliberately untouched

The real artifacts arrived: `mine_exemplars.py` (the actual mining logic), a corrected
`semantic_backup.py`, `validate_semantic_backup.py`, and an unexecuted notebook, plus a dev-session
transcript, a real, independently-verifiable checkpoint. Building the mining
script forced every hand-written exemplar through the real structural resolver for the first time and
found both of GuardedInput's original exemplars scored `final_score=0.0` (a bare `while` condition, no
nested `if`) — fixed, plus a new `audit_registry()` utility so this bug class can't silently recur.

**Independently re-executed in this audit, not just read from the transcript**: running the delivered
code directly against the closest-dated real competency model in this repo reproduces every claimed
figure exactly — `audit_registry()` flags only the already-known-unverifiable `AccumulateThenCount`
(registered in a module never supplied to this project); both corrected GuardedInput exemplars score
`final_score == 1.0`; the lexical backend's SAME/CROSS/UNRELATED validation reproduces the reported
86.7% pairwise win rate exactly (470/542) and additionally produces a worst-case ranking figure, 9/19
(47.4%), the transcript itself never quoted. New script:
`scripts/regenerate_semantic_backup_exemplar_audit.py`, all checks `[OK]`.

One genuinely open, precisely-characterized question surfaced while checking the root cause directly:
reconstructing the described broken GuardedInput shape and running it against this repo's own real
`competency.py` scores 1.0, not 0.0. Most likely explained by the same "two different working
environments" pattern already resolved earlier this session (the dev session's `competency.py` most
likely predates the Q1 while-condition fix); recorded as a hypothesis, not asserted as settled.

This round is explicitly **not yet** the "10 competencies, 27 exemplars, partly real-mined" state the
reference documents describe — the registry here is still 8 competencies/19 exemplars, all hand-written;
no real corpus mining has been run in any supplied artifact. **Table 4 and the Q5 TopKPatternExtended
delegation breakdown are confirmed byte-for-byte unchanged** (re-ran `regenerate_table4.py --check` and
`regenerate_q5_delegation_breakdown.py` fresh after this round's changes — both still report exactly
91.9%/80.6% and the same 57-catch breakdown as before). Full test suite (11 tests) still passes.

- **A real discovery, thinner evidence tier than parts 6-7's AUC finding.** Hierarchical clustering
  (cosine distance, average linkage) of Q5's 43 correct-labeled "novel" submissions' embeddings. A
  silhouette-score sweep (k=2..9) picked k=9 — but was still rising at the edge of the tested range, the
  classic small-sample overfitting signature. Cutting the *same* dendrogram by a distance threshold (0.30)
  instead recovered a trustworthy structure (two 2-file pairs, one dominant 38-file cluster, one singleton)
  that manual file-reading then confirmed was real. Unlike parts 6-7's AUC, no standalone
  embeddings/distance-matrix CSV survives — only the dendrogram chart and printed cluster listing, both
  extracted from the executed notebook's real output (`evidence: real_notebook_output`, not `real_csv`).
- **The real code fix this led to**: reading files from the 38-file cluster found a cross-function
  delegation pattern the existing `DELEGATES` mechanism had never been applied to for Q5. A new
  `SELF_RECURSIVE` primitive plus three new/changed competencies (`TopKViaDelegate`, `HasSubstantialWork`,
  `SortThenSlice`) compose into `TopKPatternExtended = ANY(TopKPattern, TopKViaDelegate, SortThenSlice)`.
  This *is* `real_csv`-backed on its own terms, via the real 526-row batch-validation run supplied
  alongside it.
- **Independently verified**: correct-side coverage 91.9% (384/418,
  up from a re-measured 79.7%), wrong-side 80.6% (87/108), zero regressions, 57 new catches (17 via
  delegation — all overlapping with the 40 via sort-then-slice), two named wrong-labeled catches
  (`wrong_5_011.py`, `wrong_5_101.py`). A new script, `scripts/regenerate_q5_delegation_breakdown.py`,
  checks all of this against hardcoded expected values — all `[OK]` on a fresh run.
- **An honest, uncharacterized false-positive caveat, not hidden**: a bubble-sort helper
  (`correct_5_416.py`) coincidentally satisfies `TopKPattern`'s abstract shape without implementing the
  actual pattern — a latent bug newly exposed, not created, by delegation testing. Sample-checked 7 of 17
  delegate catches (6 genuine, 1 false positive), explicitly not extrapolated — so 91.9%/80.6% is flagged,
  in both the paper's §8 and `configs/stage_manifest.yaml`, as likely a slight overstatement by an
  uncharacterized amount, unlike Q1's fully row-verified 99.5%/97.6%.
- **A real, explained baseline drift**: `TopKPattern`'s own correct-side coverage moved from 78.2% to
  79.7% between the two source CSVs, traced to an intervening, unrelated fix (Q1's `SHARED_BINDING`/
  `all_names` change) and confirmed by direct diff (exactly 6 named files flip, zero wrong-labeled files
  change). Both `q5_final.csv` (78.2%/75.0%, unamended) and the new `q5_final_extended.csv`
  (91.9%/80.6%) are preserved as separate, independently-dated stages.
- **A fifth paper revision, same day**, folding this into the Abstract, §5.3, Table 4, §6 Discussion, and
  §8 Limitations — confirmed by direct diff.
  
## New this round, part 7: the semantic backup layer's AUC finding upgraded to `real_csv` — raw CSVs, then the executed notebook itself

Two further uploads arrived in sequence for the same finding logged in part 6 below: first the two raw
per-run/per-file CSVs the notebook's own final cell was written to save
(`semantic_backup_bootstrap_summary.csv`, `semantic_backup_pooled_scores.csv`), the executed notebook itself
(`Copie_de_semantic_backup_layer_validation.ipynb`, described as "the notebook after run").

Both were independently verified against every figure part 6 had logged as `reported_only`: per-run
AUC and group means recomputed directly from the raw 1,510-row CSV (all 10 runs `[OK]`), mean±SD across
runs (0.098 ± 0.039, exact match), pooled AUC across all runs (0.097, exact match), and the 80%-recall
threshold (0.719 at 99.7% FPR, exact match) — a new from-scratch (no-sklearn-dependency) AUC/ROC script,
`scripts/regenerate_semantic_backup_auc.py`, now backs this stage the same way the Q1-Q4 and Q4/Q2
embedding-taxonomy stages are backed. **No numerical discrepancy found anywhere.**

**Evidence-tier result**: `configs/stage_manifest.yaml`'s
`semantic_backup.backends.codet5p_bootstrap_novel_vs_wrong_auc` is now `evidence: real_csv`,
`status: REAL_INVERTED_RESULT_CSV_BACKED` — the strongest tier this project uses, the same tier as the
Q1-Q4 batch-validation results and the Q4/Q2 embedding-taxonomy cross-validation. The result itself is
unchanged from part 6 (a strongly inverted, deployment-relevant negative finding, not a usable filter as
designed) — what changed is how solidly it's backed, not what it says. Updated: this checkpoint's own
README, root `README.md`, `POPULATE.md` step 6, `docs/KNOWN_CAVEATS.md`, and
`provenance/detector-version-log.md` (new "Semantic backup layer validation — the raw CSVs, then the executed
notebook" section). See that log section for the complete writeup.

## New this round, part 5: the Q4/Q2 embedding cross-validation raw CSVs supplied — evidence upgraded to `real_csv`

Supplied `q4_embeddings_crossvalidation.csv` (1,470 rows) and `q2_embeddings_crossvalidation.csv`
(1,750 rows) — exactly the per-seed/per-file prediction files part 3 below had already named and flagged
as "saved to Drive but not supplied." Recomputing per-seed accuracy, mean/SD, the pooled confusion matrix,
and every precision/recall/support figure directly from these raw rows reproduces everything already
logged from the notebook's own printed output to full floating-point precision — no discrepancy found.

- `scripts/regenerate_q2q4_taxonomy_crossvalidation.py` was rewritten to read the two real CSVs directly
  (mirroring how `regenerate_taxonomy_crossvalidation.py` already works for Q5's own real-CSV stages)
  instead of checking hand-transcribed numbers. All checks still pass.
- `configs/stage_manifest.yaml`'s `q4_taxonomy_embedding_crossvalidation_10seed_pooled` and
  `q2_taxonomy_embedding_crossvalidation_10seed_pooled` entries are now **`evidence: real_csv`**, each with
  a `data_file` field — upgraded from `real_notebook_output`, the same tier Q5's own 10-seed sweep is still
  stuck at (only seed 0 of Q5's own 10 seeds ever got a raw CSV). New files:
  `data/labels_scores/q4_embeddings_crossvalidation.csv`, `q2_embeddings_crossvalidation.csv`.
- This does **not** touch the still-entirely-unsupplied `table5.q4_sortbykey_splits`/`q5_topk_splits`
  companion-paper scope — a different experiment, unaffected by this round.

See `provenance/detector-version-log.md`'s "The Q4/Q2 embedding cross-validation raw CSVs supplied" section for
the complete per-seed recomputation.


## New this round, part 3: the Q5 embedding-taxonomy methodology extended to Q4 and Q2

Supplied two notebooks (onereal and executed, one an unexecuted copy) extending the 
already-validated Q5 manual/builtin embedding
cross-validation to Q4 (`BubbleSortPass` vs. `TopKPattern`) and Q2 (`counter` vs. `functional`). **Q1 and
Q3 are deliberately excluded**, per the conversation's own sound scoping reasoning (quoted in full in the log):
both are single-strategy competencies whose real finding this round was a structural-matching bug, not a
taxonomic split — there's no analogous "does an independent method recover this split" question to ask.

- **Q4: a genuinely strong, independently-verified result — stronger than Q5's own.** 489 files labeled
  (420 topk / 69 bubblesort). Mean accuracy across 10 seeds: 93.6% ± 2.1% (range 89.8%–95.9%), recomputed
  directly from the notebook's own per-seed table and exactly matching the conversation's own figure. Recomputing
  precision/recall from the pooled confusion matrix (1,470 predictions) exactly reproduces the printed
  classification report: bubblesort precision 0.69/recall 0.98; topk precision 1.00/recall 0.93. The
  confusion-matrix asymmetry runs the *opposite* direction from Q5's own (here bubblesort is the broad,
  easy-to-fall-into cluster; in Q5 manual was the broad one, not builtin) — a real, structurally-explicable
  reversal, not an inconsistency.
- **Q2: a class-imbalance artifact, independently confirmed, not a validated finding — and the source conversation
  itself says so.** 581 files labeled (564 counter / 17 functional). The headline 95.9% accuracy is
  independently confirmed to be uninformative: `counter` is 96.8% of the pooled test set — a
  classifier that always predicted `counter` would score *higher* (96.8%) than what this classifier
  actually achieved. `functional`'s own precision/recall (0.33/0.27, support 56) is close to
  uninformative, consistent with 17 real examples being too few for a stable conclusion. The conversation's own
  explicit recommendation, logged verbatim: "don't report this as a finding at all, positive or
  negative... If you want this documented anywhere, the honest version belongs in Limitations, not
  Results."
- **Evidence status: `real_notebook_output`**, same tag and same reason as Q5's own 10-seed sweep — real
  execution output exists and is independently verified (`scripts/regenerate_q2q4_taxonomy_crossvalidation.py`,
  all checks pass).
New checkpoint folder: `detectors/q2_q4_embeddings_crossvalidation/`. See
`provenance/detector-version-log.md`'s "Q4/Q2 embedding cross-validation" section for the complete
word-for-word verification writeup.

## New this round, part 2: the batch script was actually run — Q1-Q4 upgraded to real_csv, plus a real Q1 bug found and fixed

Ran `run_q1_q4_batch_validation.py` against
the real Refactory dataset for the first time and supplied the four resulting CSVs, a code fix for a gap
the run surfaced in Q1, and the resulting updated methodology doc and paper. **This is the single biggest
evidence-tier event in this project to date**: every one of Q1-Q4's headline percentages moves
to `real_csv` in the same round.

- **Every Table 4 figure independently re-verified against the real CSVs, exact match:** Q1
  `GuardedInput`/`LinearSearch` 99.5%/97.6%, Q2 `UniqueCheck` 90.4%/74.3%, Q3 `SelectionStep` 94.0%/74.7%,
  Q4 `SortByKey` 77.6%/45.9% (correct/wrong) — cell-for-cell identical to the paper's own brand-new
  consolidated Table 4 and to this repo's own `regenerate_table4.py --check` output.
- **A real Q1-specific structural-detector bug, found and fixed.** The run surfaced `GuardedInput`/
  `LinearSearch` scoring only 76.8%/64.2% — far below Q2/Q3. Direct diagnosis (quantified, not guessed)
  found 364 of 383 zero-scores (95%) were not a coverage gap at all, but `SHARED_BINDING` only ever
  checking a `TEST`'s literal left-hand `operand`, missing three real shapes: the searched value on the
  right side of a comparison (199 files, 55%), inside a compound/chained condition (157 files, 43%), or as
  a `while` loop's own condition (8 files, 2%). Fix (new checkpoint,
  `detectors/q1_shared_binding_fix/`, canonical bug #22): a new `all_names` binding on every
  `TEST` evidence (every identifier referenced anywhere in the test), a new `ast.While`-condition branch in
  the TEST-detection function, and containment matching added to `SHARED_BINDING` — all three confirmed
  genuinely additive by direct diff against the pre-fix baseline already in this repo. Re-run coverage:
  99.5%/97.6%, zero regressions (conversation-reported; no pre-fix CSV was supplied to independently confirm this
  specific sub-claim).
- - **A genuine "17 vs 19" reconciliation, derived independently from the CSV**
  every document states the genuine coverage gap as "19 files" without distinguishing pre/post-fix. The
  real post-fix CSV shows exactly 17 files still genuinely gapped (plus 1 unrelated parse-error row) — an
  exact match, category by category, once you notice the 2 "test-only-missing" pre-fix files are precisely
  the 2 the new `while`-condition detection fixed incidentally.
- **The "99.93% agreement / 1,342 of 1,343" claim (quoted in both the methodology doc and the paper)
  resolved as a `pandas` `NaN != NaN` comparison artifact, not a real difference** — this repo's own direct
  column-by-column diff of the real CSV finds `GuardedInput` and `LinearSearch` are byte-for-byte identical
  across all 1,343 rows (0 differences), a cleaner and stronger result than the "99.93%" figure that
  predates the conversation's own explanation of that artifact.
- - **Submission-ID manifests populated for all five questions** (a previously entirely-unpopulated
  reproducibility-brief deliverable), mechanically projected from the same real batch-report CSVs.

See `provenance/detector-version-log.md`'s "Real batch-validation RESULTS for Q1-Q4" section for the complete
word-for-word verification writeup — every quoted claim, every diff, every reconciliation.

## New this round, part 1: a real, verified batch-validation script for Q1-Q4 — the driver script itself

Supplied a document export and a real Python script, `run_q1_q4_batch_validation.py` — the first-ever
driver script for Q1-Q4's full-corpus batch validation, reusing the same already-verified
`batch_report.py` machinery that produced `topk_report.csv` for Q5. New checkpoint folder:
`detectors/q1_q4_batch_validation/` (now updated, per "part 2" above, with the real run results
too).

- **Thoroughly cross-verified against files already in this repository, not taken at face value.**
  Confirmed true by direct diff: the `process_folders(..., function_name=...)` call signature matches
  the real `batch_report.py` exactly; Q1's original `q1_competencies.py` really did use whole-file
  resolution (no `function_name` argument in its own `__main__` block); the shared-`model` import chain
  across `test_real_data.py` → `q1_competencies.py`/`pw01_competencies.py`/`ex2_3_4_competencies.py` →
  `q2_competencies.py` is genuinely one consistent `CompetencyModel()` instance, not several diverging
  ones.
  
## New this round: the real 10-seed sweep, resolved

Supplied six files and three chart images: a conversation-export docx continuing the multi-seed thread, a
raw per-file CSV for the previously conversation-only "shuffled seed=0" run, two notebooks (one with real printed
execution output, one a code-identical outputs-stripped copy), a methodology-update zip.

- **The 10-seed (`SEEDS = list(range(10))`) robustness sweep flagged as "remains unrun" in the prior round
  has now actually been run, with real output.** `ast_taxonomy_crossvalidation_with_results.ipynb` carries
  the full real per-seed table, mean/SD summary, pooled confusion matrix, and both pooled classification
  reports — independently cross-checked against a code-identical copy notebook, a matching conversation export,
  and three chart images (all match to full precision). Result: manual/builtin agreement 87.0% ± 2.3%
  (range 82.6%-89.8%), 3-way accuracy 83.7% ± 2.3%, novel recall 49.5% ± 7.5%. Pooled across all 10 seeds
  (1,580 predictions, explicitly flagged by the source as not fully independent — same ~526 files
  reshuffled 10 ways): pooled manual/builtin precision/recall — manual 0.94/0.87, builtin 0.75/0.88
  (n=1441). New script: `scripts/regenerate_10seed_taxonomy_sweep.py` — verifies this transcribed real
  output is internally consistent (mean/SD arithmetic, and that both classification reports are exactly
  what the pooled confusion matrix's own arithmetic produces), tagged `evidence: real_notebook_output`
  since no raw per-submission CSV exists for 9 of the 10 seeds.
- **The previously "shuffled seed=0" figure (85.2% manual/builtin) is now backed by a real raw
  CSV** and upgraded to `evidence: real_csv` — independently
  recomputed this round, matching the prior conversation quote to full floating-point precision. Interestingly,
  this standalone run and the 10-seed sweep's own internal "seed 0" are close but NOT identical (flagged,
  not silently reconciled, in both the log and the manifest) — two different code paths evidently used
  slightly different shuffle state despite both being labeled "seed 0."

## New this round: the multi-seed instability finding (prior round)

Before the 10-seed sweep itself arrived, Sonia had supplied `multi-seed loop.docx`, documenting a single
real, executed alternate (shuffled) split showing the published 89.1% figure was not stable split-to-split
(dropped to 85.2%), plus the arithmetic resolving an earlier flagged precision discrepancy (0.92 vs. 0.98
— both correct, different denominators). That single alternate split is now also backed by a real raw CSV
(see above) and is superseded, for publication purposes, by the full 10-seed sweep.

## New this round (third/fourth passes): AST-taxonomy embedding cross-validation — first real result.

Supplied `ast_taxonomy_crossvalidation.ipynb`, its real output CSV, a conversation export, and the paper PDF
version that first added a new §5.5 reporting this single unshuffled split's 89.1% manual/builtin
agreement (86.1% 3-way, 45.5% novel recall) — the first embedding-related result in the project with
`evidence: real_csv` status, and the first confirmed section-numbering resolution (Case Study 5's Q3/Q4
content merged into §5.3, freeing §5.5 for the new subsection). Both of these are now superseded, for
publication purposes, by the second paper update and the 10-seed sweep documented above, but remain in the
repo as real, historically-important, independently-reproducible stages.


## New this round: real train/test split indices supplied and merged — turned out to be the same experiment as the already-real Q4/Q5 taxonomy embedding cross-validations, not a distinct one

Supplied `split_manifests_q4_q5.zip`: real `split_manifest.json` + `split_NN_{train,test}_ids.txt`
files (seeds 00-09, 70/30) for `q4_sortbykey` and `q5_topk`, from her real Colab/Drive notebooks —
`POPULATE.md`'s last entirely-unsupplied item.

A conflict surfaced before anything was written: several places in this repo (`POPULATE.md` step 4,
`stage_manifest.yaml`'s `table5:` notes, `README.md`'s file table) repeatedly stated this was a *distinct,
still-unsupplied companion-paper experiment* (likely novel-detection/anomaly-scoring), separate from the
already-real `q4_taxonomy_embedding_crossvalidation_10seed_pooled`/`q5_taxonomy_embedding_crossvalidation_10seed_pooled`
stages. But the supplied files traced to the *same* two notebooks backing those stages, same source
report CSVs, same split code, same reported mean/SD — and for Q4, the supplied evidence CSV was
byte-for-byte identical to a CSV already in this repo. 
**What changed**: `data/splits/q4_sortbykey/` and `data/splits/q5_topk/` now hold the real files.
`scripts/regenerate_splits.py` was rewritten (the old version assumed sklearn's stratified split and a
single seed, neither matching the real plain-pandas seeded-shuffle method) and now independently
reproduces every recorded split, for both experiments, all 10 seeds, entirely from files already in this
repo. `configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits`/`q5_topk_splits` PENDING fields are
filled with real values. Every place that previously asserted the "distinct companion-paper" framing —
four spots in `stage_manifest.yaml` alone, plus `POPULATE.md`, `README.md`, `VERSIONING.md`,
`data/splits/README.md` — got an appended `UPDATE:` correction; the original text was kept,
not deleted, per this repo's evidence-preservation practice. Also corrected: `data/splits/README.md`'s ID
scheme claim (real files use the `file` column with its `.py` extension, not the bare `submission_id`
scheme it previously described).

**Verification stayed honest about the asymmetry, not smoothed over**: Q4's all 10 seeds are independently
confirmed byte-exact against the notebook's own saved pooled predictions. Q5's seed 0 is independently
confirmed byte-exact against a separately-recorded CSV already in this repo; seeds 1-9 are real, newly
recorded split membership, but only replay-confirmed (the notebook's multi-seed loop never exported
per-seed file lists) — so `q5_taxonomy_embedding_crossvalidation_10seed_pooled`'s `evidence:` field stays
`real_notebook_output`, not upgraded to `real_csv`, by this round. See `provenance/detector-version-log.md`'s
matching entry for the full evidence trail.

**Re-verified clean**: `regenerate_splits.py --check` (both experiments, all 10 seeds, exact match),
`regenerate_table4.py --stage final --check`, `pytest tests/ -q` (11/11), `regenerate_table5.py
--section all` (Q4/Q5 sections now print real values instead of `PENDING`).

**Every item on `POPULATE.md` is now done.** What remains open in this repo: two unrelated
semantic-backup-layer backend items (`jina_v2_code`, never executed; `codet5p_110m_embedding`, code exists
but not validated against a real corpus), and whether to create a git commit/remote for the actual GitHub
push — still not done, per this session's git-safety discipline.

## Next step

Every `*_final` stage for Q1-Q5 is now real, CSV-backed, and independently regenerable — Q5's own headline
figure is now `TopKPatternExtended` (91.9%/80.6%, `configs/table4_config.yaml`'s current pointer), a real
delegation-based fix discovered via embedding clustering (part 9), with the original `TopKPattern`-only
figure (78.2%/75.0%) preserved alongside it as its own dated stage, not overwritten. The AST taxonomy's own
multi-strategy splits (Q5, Q4, Q2) all still have a real, independently-verified embedding cross-validation
too. The reproducibility brief's core ask (immutable detector/taxonomy versions, real submission IDs, real
per-submission labels/scores, and scripts that regenerate Table 4) is substantially met for the structural
layer, with real bonus coverage on the taxonomy-validation and now the delegation-discovery side too. What
remains is mostly the separate embedding/semantic-backup "companion paper" scope: the 10 train/test splits
(still entirely unsupplied), and a usable/positive exemplar-similarity result (the AUC finding is now
`real_csv`-backed, but still real and inverted — a negative finding, not a deployable one) — Sonia to
supply those Colab/Drive artifacts per `POPULATE.md`'s remaining steps (4 and 6) when available. Parts 11,
12, and 13 above are real, independently-verified progress toward that same exemplar-registry side of the
companion paper — two genuine bugs found and fixed (GuardedInput, then AccumulateThenCount), real corpus
mining closing what part 11 left as `TODO` (part 12), a broken import chain and a surface-containment
scoping fix both landing as real code, and `audit_registry()` fully clean across all 10 competencies for
the first time ever (part 13) — by design leaving Table 4 and the Q5 delegation breakdown exactly as they
already were throughout. That same registry is now actually
merged into this repo's own `data/exemplar_registry/`, so POPULATE.md step 6 is DONE, not partial. Still
outstanding on this same axis: the codet5p numbers remain `real_notebook_output` rather than independently
re-run (`huggingface.co` still blocked here), and the real-corpus scan counts themselves stay conversation-reported
only (no corpus ever supplied here) — neither blocks the merge itself, since the merge only needed the
registry's own code, not those separate results. `POPULATE.md` step 4 is done — real
split-index files were supplied and merged, and turned out to be the same experiment as the already-real
Q4/Q5 embedding-taxonomy cross-validations, not the "still entirely unsupplied," separate companion-paper
train/test-split experiment described two paragraphs up. Every item on `POPULATE.md` is now done. 

