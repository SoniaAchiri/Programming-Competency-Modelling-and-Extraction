# Competency Extraction — Result Regeneration Repository

This repository is the **provenance and regeneration companion** to the competency-extraction system. It
exists to answer one reviewer question precisely, for any number reported anywhere in this project:

> *Which exact taxonomy checkpoint, which exact detector checkpoint, and which exact scoping mode
> produced this number — and can I recompute it myself from the same submission IDs and splits?*

It is deliberately **not** just "the code." The implementation alone cannot answer the question above,
because several reported values changed after detector, scoping, or taxonomy corrections made during the
study (see `VERSIONING.md`). This repository freezes the inputs and configuration for every reported
stage so each number is independently regenerable and attributable to a specific real checkpoint.

**A note on provenance:** there is no granular commit history for this project — real checkpoints were
saved periodically (zips, standalone files), not committed incrementally. Every claim in this repository
is sourced from `provenance/detector-version-log.md`, an evidence-grounded log built by diffing those real
checkpoints against each other and cross-referencing conversation-history exports and paper drafts. Checkpoint
folders are named with a **stable, date-free label** (Sonia's own label for that checkpoint, e.g.
`fixq4`) rather than an invented version ladder — real dates are never guessed, and live instead in each
checkpoint's own `README.md`/`taxonomy.yaml`, in `detectors/CHANGELOG.md`/`taxonomy/CHANGELOG.md`'s own
"Real date" column, and in the log itself, which is the canonical citation for every claim; the files
under `detectors/`, `taxonomy/`, `VERSIONING.md`, and `configs/stage_manifest.yaml` are compressed indexes
into it. (Folder names briefly carried the real date as a prefix instead — dropped 2026-09-19, once this
repo's actual publication target, a public GitHub repo cited by reviewers, made a stable slug clearly the
better fit than a name that would need editing every time a date turned out to need correcting; see
`VERSIONING.md` and the log's "Checkpoint-naming pilot rename" entry for the full reasoning and the
verification that nothing was lost in the change.)

## What's here

| Path | Contents |
|---|---|
| `taxonomy/<checkpoint>/` | Immutable snapshot of the competency taxonomy (target competencies, composition rules) as it existed at that real, dated checkpoint — scoped to only the question(s) it changed. |
| `detectors/<checkpoint>/` | Immutable, real snapshot of the detector implementation (`competency.py` and supporting files) as it existed at that checkpoint. **Populated with real code**, not placeholders. |
| `data/submission_ids/` | The Refactory submission identifiers assigned to each analysis cohort (per question, per correct/wrong label). **Real and populated for all five questions** — mechanically projected from each question's real batch-report CSV via `scripts/build_submission_ids_from_batch_reports.py`; correct/wrong counts confirmed exact against Table 3. |
| `data/splits/` | Train/test split index files for the Q4/Q5 embedding-taxonomy cross-validation experiments (`table5.q4_sortbykey_splits`/`q5_topk_splits`). **Real and populated (2026-09-20)** — seeds 00-09, 70/30, independently reproduced by `scripts/regenerate_splits.py --check`. **Update:** this table previously described these as a distinct, unsupplied companion-paper experiment; that was wrong — they are the same experiment as the `real_csv`/`real_notebook_output`-backed Q4/Q5 embedding *taxonomy* cross-validations below, not a different one. See `data/splits/README.md`. |
| `data/labels_scores/` | Per-submission structural labels and scores, keyed by which real checkpoint + scoping mode produced them. **`q1_final.csv` through `q5_final.csv` are all real**, mechanically derived via `scripts/build_labels_scores_from_batch_reports.py`; `q5_taxonomy_crossvalidation_results.csv` and its shuffled-seed0 sibling are real, independent embedding-based taxonomy validation (see `detectors/ast-taxonomy-crossvalidation/`). |
| `papers/` | **Raw files withheld — the paper isn't published yet.** A structural revision history (five real, dated revisions of `Structural_Competency_Extraction_Paper`: pre-embedding-validation, first embedding-validation, the 10-seed-sweep version, the version with the Q4 embedding result written into §5.6, and the version adding §7, "The Semantic Backup Layer: Architecture Overview") — what changed, when, and what independently verifies each figure, without reproducing the paper's own text. See `papers/README.md`. |
| `methodology/` | **Raw files withheld, same reason.** The real, dated (2026-08-04, then 2026-08-05) internal methodology note's revision history — the one whose canonical bug table grew from 19 to 22 entries. See `methodology/README.md`. |
| `data/exemplar_registry/` | **The real, full exemplar registry — 10 competencies, 27 exemplars, merged 2026-09-18** from `detectors/semantic-backup-validation-executed/semantic_backup.py` via `scripts/build_exemplar_registry.py`; every `final_score` freshly computed against the live structural resolver in this merge (all 1.0000, `audit_registry()` clean). The `codet5p` embedding backend remains `real_notebook_output`-backed but not independently re-runnable here (`huggingface.co` blocked); see `data/exemplar_registry/README.md` for the full provenance breakdown. |
| `configs/stage_manifest.yaml` | **The audit index.** Maps every reported number to the exact checkpoint/scoping-mode combination that produced it, and states plainly whether a real CSV backs it (`evidence: real_csv`) or it's conversation/paper-reported only (`evidence: conversation_reported_only`) — never implies more certainty than exists. |
| `scripts/` | Regeneration scripts. Each reads `stage_manifest.yaml` and either recomputes a real figure or reports `[PENDING]` honestly rather than crashing or guessing. |
| `tests/` | Regression tests — pass where real data exists, skip/fail-loudly where it doesn't (by design, not a bug). |
| `docs/` | Data dictionary and schema documentation for everything under `data/`. |
| `provenance/detector-version-log.md` | **The actual audit trail** — every claim in this repository traces back to a specific diff, conversation quote, or paper passage recorded here. |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r environment/requirements.txt

# Regenerate Table 4 — all five questions now have real data
python scripts/regenerate_table4.py --stage final --check

# Report status of the companion-paper embedding-splits/semantic-backup experiments (train/test splits
# still PENDING; three real backend results exist for the exemplar-similarity side though — the stub and
# codebert_colab negative tests, plus a real, CSV-backed, INVERTED AUC=0.097 for the layer's actual
# novel-vs-wrong job — a DIFFERENT scope than the AST-taxonomy embedding cross-validations below; see
# table5_config.yaml's own naming note in papers/README.md)
python scripts/regenerate_table5.py

# Regenerate the real Q5 progression (83.0% whole-file -> 78.2% scoped -> 82.1% unscoped-post-refactor);
# the first and third stages print [PENDING] since no CSV backs them yet
python scripts/regenerate_q5_percentages.py --all-stages

# Regenerate the real, independently-verified AST-taxonomy embedding cross-validation for Q5 — both the
# original unshuffled split (89.1% manual/builtin agreement) and the shuffled seed=0 alternate (85.2%)
python scripts/regenerate_taxonomy_crossvalidation.py

# Verify the full 10-seed robustness sweep's internal arithmetic (mean/SD and both pooled classification
# reports) against its own real, transcribed notebook output — this is the figure the paper currently
# reports (87.0% +/- 2.3% manual/builtin agreement), superseding the single-run 89.1% figure above
python scripts/regenerate_10seed_taxonomy_sweep.py

# Regenerate the same 10-seed embedding-taxonomy methodology extended to Q4 (93.6% +/- 2.1%, a stronger
# result than Q5's) and Q2 (95.9% — independently confirmed to be a class-imbalance artifact, not a
# validated finding; the source conversation itself recommends against reporting it as a headline number) —
# directly from the real per-seed/per-file prediction CSVs, not transcribed output
python scripts/regenerate_q2q4_taxonomy_crossvalidation.py

# Regenerate the semantic backup layer's real novel-vs-wrong separation AUC (INVERTED, AUC=0.097) directly
# from the raw per-run/per-file CSVs the notebook itself saved -- a from-scratch AUC/ROC implementation,
# no sklearn dependency
python scripts/regenerate_semantic_backup_auc.py

# Regenerate Q5's delegation fix (91.9%/80.6%, up from 79.7%/75.0%) -- a real embedding-CLUSTERING
# discovery (distinct from the AUC above) found that 38 of Q5's 43 "novel" correct submissions share a
# cross-function delegation shape the structural rules never saw; verifies the fix's zero-regression
# property, its exact new-catch breakdown, and the 78.2%->79.7% baseline drift this round also caught
python scripts/regenerate_q5_delegation_breakdown.py

# Re-run the semantic backup layer's own exemplar-registry audit and discriminative-power check
# (a real GuardedInput exemplar bug found and fixed, and a lexical-backend SAME/CROSS/UNRELATED
# validation) directly against the delivered code and the closest-dated real competency model --
# does NOT touch Table 4 or the Q5 delegation breakdown above, which stay exactly as verified
python scripts/regenerate_semantic_backup_exemplar_audit.py

# Re-run the SECOND mine_exemplars batch's checks: dating (this round's dev environment used a
# competency.py predating the Q1 fix -- confirmed byte-identical to detectors/fixq4),
# the broken pw01_competencies.py import chain, the resolved bare-while GuardedInput discrepancy,
# and the real cached-embedding reproduction of both the codet5p (8-competency subset) and lexical
# (full 10-competency) discriminative-power numbers -- also does NOT touch Table 4 or Q5
python scripts/regenerate_semantic_backup_v2_audit.py

# Re-run the THIRD delivery's checks (the first genuinely EXECUTED semantic_backup_validation
# notebook this project has received): the embedded model files match this repo's own current
# HEAD, the broken pw01_competencies.py import chain from the round above is now fixed, the
# DelegatesUniqueness scoping fix is now real delivered code (not just described), audit_registry
# is fully clean for the first time (all 10 competencies), the post-fix lexical numbers reproduce
# exactly, and three TopKPatternExtended structural regression cases reproduce exactly -- also does
# NOT touch Table 4 or Q5
python scripts/regenerate_semantic_backup_v3_audit.py

# Build data/submission_ids/*.csv and data/labels_scores/qN_final.csv from the real batch-report CSVs
# (already done in this repo; re-run only after supplying updated raw batch reports)
python scripts/build_submission_ids_from_batch_reports.py --all
python scripts/build_labels_scores_from_batch_reports.py --all

# Verify every regenerated number matches its reported value
pytest tests/test_regeneration_matches_paper.py -v
```

Every script takes an explicit stage id, never a floating "latest" — see `VERSIONING.md`. This is what
makes "which configuration produced this number" answerable rather than ambiguous.

## Status of this repository

**Real, not guessed.** An earlier version of this repository was scaffolded from the paper's prose alone,
before any of the project's real checkpoints, conversation exports, or paper drafts had been examined — that
version invented a version ladder and several specific numeric results that turned out to have no basis
in anything real (see `VERSIONING.md`'s "Corrected from an earlier, guessed version" note). This version
is built from `provenance/detector-version-log.md` instead. Real code is populated for every detector and
taxonomy checkpoint; real per-submission data now backs the final, published figure for **every** Refactory
question, Q1 through Q5 (`data/labels_scores/q{1,2,3,4}_final.csv` plus Q5's own current headline,
`q5_final_extended.csv` — see below — all `evidence: real_csv` in `configs/stage_manifest.yaml`) — the
driver script at
`detectors/q1-q4-batch-validation/run_q1_q4_batch_validation.py` has now actually been run
against the real Refactory corpus, and the run itself surfaced and fixed a real Q1-specific structural
gap (`detectors/q1-shared-binding-fix/`, canonical bug #22). Several earlier/superseded stages
(the pre-fix Q1 baseline, Q4's two intermediate sub-strategy figures, Q5's unscoped runs) remain
conversation-reported only, since no CSV exists for those specific intermediate configurations. The same round's
embedding-taxonomy methodology (validated for Q5 across an earlier round) has also been extended to Q4 and
Q2 (`detectors/q2-q4-embeddings-crossvalidation/`, now `evidence: real_csv` — the raw
per-seed/per-file prediction CSVs the notebook saved to Drive arrived in a later round than the notebook
itself, upgrading both stages from the initial `real_notebook_output`) — a different question from the
still-`PENDING` companion-paper train/test-split experiment. The semantic backup layer's actual job
(separating novel-correct from genuinely-wrong submissions, as opposed to validating an existing AST
split) now has its first real result too, and it is now `real_csv`-backed as well: a bootstrapped,
uncontaminated-comparison AUC of 0.097 — strongly *inverted*, not merely null — independently reproduced
from the raw per-run/per-file CSVs the notebook itself saved, and corroborated by the later-supplied
executed notebook's own printed output (`configs/stage_manifest.yaml`'s
`semantic_backup.backends.codet5p_bootstrap_novel_vs_wrong_auc`, `evidence: real_csv`,
`status: REAL_INVERTED_RESULT_CSV_BACKED`; see `detectors/semantic-backup-layer-validation/`).
One anomaly persists even in the executed notebook: every code cell's `execution_count` is `None` despite
real, populated outputs, so the conversation's own "cell 13"/"cell 15" references still cannot be independently
cross-checked against actual cell positions — flagged as open, not resolved. The published paper's own new
§7 (as of the 2026-08-08 revision) documents the layer's architecture but deliberately does not yet include
this finding, deferring it to the still-unsupplied companion paper.

**A separate, still-later-round discovery, distinct from the AUC finding above, closed a real Q5
structural gap.** The same embedding model, used this time purely as a *discovery tool* rather than a
validator, clustered Q5's 43 correct-labeled "novel" submissions and found one dominant 38-file cluster
sharing a cross-function delegation shape (`top_k` calls a differently-named helper and slices the
result) that function-scoped inline resolution could never see. This led to a real code fix — a new
`TopKViaDelegate`/`SortThenSlice`/`TopKPatternExtended` competency set, plus a new `SELF_RECURSIVE`
primitive — independently verified (`evidence: real_csv`) to raise Q5's coverage from 79.7%/75.0% to
91.9%/80.6% with zero regressions (`data/labels_scores/q5_final_extended.csv`,
`scripts/regenerate_q5_delegation_breakdown.py`). Table 4 above now reports this figure as Q5's headline;
the original 78.2%/75.0% TopKPattern-only figure remains preserved, unchanged, at
`data/labels_scores/q5_final.csv` as its own real, earlier checkpoint. This round's own paper revision
(2026-08-08, ~3 hours after the §7 revision above) folds the full story — including an honest,
uncharacterized TopKPattern false-positive caveat exposed by delegation testing, and a real, explained
78.2%→79.7% baseline drift traced to the earlier Q1 fix — into §5.3, Table 4, §6 Discussion, and §8
Limitations. See `detectors/q5-delegation-clustering-fix/README.md` and
`detectors/semantic-backup-layer-validation/README.md`'s "The clustering extension" section for
the complete writeup, including a notable, purely coincidental resemblance between this real fix and an
early, explicitly-fabricated guess this repository's own `VERSIONING.md` already documents having
corrected. See `POPULATE.md` for exactly what's still outstanding and why.

**A further, separate round (2026-08-07) fixed a real bug in the semantic backup layer's own exemplar
registry** — a different axis again from both findings above (this is about whether the registry's
exemplars are genuine examples of what they claim to be, not about Q5's structural coverage or the
layer's novel-vs-wrong AUC). Building a real mining script (`mine_exemplars.py`) forced every
hand-written exemplar through the actual structural resolver for the first time and found both of
GuardedInput's original exemplars scored `final_score=0.0` — fixed, and independently re-verified in
this audit by directly executing the delivered code against the closest-dated real competency model
(both exemplars now score exactly 1.0; a new `audit_registry()` utility correctly flags
`AccumulateThenCount` as unverifiable rather than assuming it's fine; the lexical backend's reported
86.7% pairwise win rate is reproduced exactly). The registry expanded from 5 exemplars/2 competencies to
19/8, all still hand-written — real progress toward, but explicitly not yet, the "10 competencies, 27
exemplars, partly real-mined" state a later paper/methodology revision describes as finished. See
`detectors/mine-exemplars/README.md`. **This round does not touch Table 4 or the Q5
delegation breakdown above, which remain exactly as previously verified.**

**A second mine_exemplars batch (content-dated 2026-08-08/09, delivered 2026-09-17) closed that gap
with real corpus mining, and — as a direct side effect — resolved a discrepancy this repository had
previously left open.** Real Refactory corpus mining (per the conversation, not independently checkable here —
no corpus ever supplied) found `ConditionalCount` in 248/291 real submissions and two new competencies,
`FunctionalUniqueCheck` (13/291) and `DelegatesUniqueness` (227/291, cross-function); `AccumulateThenCount`
verified in only 2/291, a genuinely rare strategy. A second integrity bug, same class as GuardedInput's:
2 of 3 `AccumulateThenCount` exemplars also scored `final_score=0.0` (needed `.count(`, had `len(...)`) —
now corrected. The delivered registry is confirmed at exactly 10 competencies / 27 exemplars — real,
delivered code, not narrative. Using the delivered semantic embedding cache (real, content-hash-keyed
codet5p/lexical vectors, independently unpickled and reprocessed — not re-typed from the transcript, with
a guard against any live network fallback), this audit exactly reproduced the reported codet5p numbers
for the 8-competency subset the cache covers (81.7% win rate, 76.2% worst-case) and the reported lexical
numbers for the full 10-competency registry (88.4% win rate, 55.6% worst-case). **Most notably, this
round supplied the actual `competency.py` the first mine_exemplars round's development used — confirmed
byte-identical to `detectors/fixq4` (predating the Q1 fix) — which resolves, with hard
evidence, the previously-open "bare-while GuardedInput reconstruction scores 1.0, not the claimed 0.0"
discrepancy: reconstructing that same shape against the now-supplied, actual competency.py scores exactly
0.0, confirming the earlier hypothesis.** The delivered "real model chain" doesn't actually run in this
sandbox either (`pw01_competencies.py` has unresolved relative imports to submodules never supplied), so
`AccumulateThenCount`/`FunctionalUniqueCheck`/`DelegatesUniqueness` remain unverifiable here — same
practical gap as the first round, a different specific cause. See
`detectors/mine-exemplars-real-corpus/README.md`. **This round, too, does not touch Table 4 or
the Q5 delegation breakdown, which remain exactly as previously verified.**

**A third delivery — a single notebook, "here is the last version of `semantic_backup_validation`
notebook," delivered 2026-09-17 with no accompanying conversation or dating metadata — turned out to be the
first genuinely EXECUTED copy of this notebook this project has ever received, and it closed both gaps
the round above left open.** Every earlier copy was confirmed entirely unexecuted; this one has real
execution_counts (1–10) and real output (download progress for `codet5p-110m-embedding`'s weights,
weight-loading logs) on 9 of 10 code cells. It is self-contained and, diff-confirmed, embeds this repo's
own **current HEAD** structural model — unlike the earlier two mine_exemplars rounds, which were running
against a pre-Q1-fix snapshot. Two real fixes land here: `pw01_competencies.py`'s broken relative
imports are fixed (confirmed by direct execution: the full real model chain now imports cleanly in this
sandbox for the first time), and the `DelegatesUniqueness` scoping fix the round above's conversation described
but never delivered is now real, present code. **Independently reproduced in this audit**:
`audit_registry()` is now fully clean across all 10 competencies for the first time ever; the post-fix
lexical numbers reproduce exactly (90.6% win rate, 74.1% worst-case, zero `DelegatesUniqueness`
failures, down from 5); three synthetic `TopKPatternExtended` structural regression cases (explicitly
non-semantic, changing no real percentage) reproduce exactly. The codet5p numbers (84.2%/81.5%) match
the round above's conversation-reported figure, now backed by real notebook output rather than a transcript
(`huggingface.co` still blocked here, so not independently re-run). See
`detectors/semantic-backup-validation-executed/README.md`. **This round, too, does not touch
Table 4 or the Q5 delegation breakdown.**

## Citing

See `CITATION.cff`.

## License

See `LICENSE`. Note: the Refactory corpus itself is a third-party dataset and is **not redistributed
here** — only submission identifiers, derived labels/scores, and split indices over it, once supplied.
See `data/submission_ids/README.md` for how to obtain the corpus and align IDs, and the license check
noted in `POPULATE.md` step 9.
