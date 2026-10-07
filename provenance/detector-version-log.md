# Detector/taxonomy version log — audit index

**The full, original narrative is not lost.** It is preserved verbatim in this repository's git history,
in the initial commit (`cea8b80`, "Reproducibility repository for AST-based competency extraction") —
`git log --follow -p -- provenance/detector-version-log.md` recovers it in full, including every quoted
conversation excerpt, cross-referencing chain, and discovery narrative this index below only summarizes.
This file's own path, section structure, and the specific heading strings other files quote are all
unchanged, so every existing cross-reference into this file (44 files, confirmed by
`grep -rl "detector-version-log.md"` at distillation time) still resolves to the right place.

**Evidence tiers**, weakest to strongest, as used throughout this repo (`configs/stage_manifest.yaml` is
the machine-readable source of truth; this file gives the narrative behind each tier assignment):
`conversation_reported_only` (a figure stated in a conversation export, never independently checked) <
`real_notebook_output` (an executed notebook with printed output, but no raw CSV/artifact backing it) <
`real_execution` (independently re-run against delivered code in this project's own audit, no CSV/notebook
artifact survives) < `real_csv` (the strongest tier — a literal CSV/JSON artifact, or a functionally
equivalent preserved artifact such as a content-hash-keyed pickle embedding cache).

**Standing constraint, still in force**: per Sonia's explicit instruction (recorded in full under "The
'mine_exemplars' thread" below), nothing in this project may silently change Table 4's numbers, the Q5
percentages already logged as final, or the 91.9%/80.6% Q5 delegation breakdown, without her say-so — this
index reports what was already verified, not a re-derivation.

---

## Named checkpoint sections

A handful of files elsewhere in this repo cite the checkpoints below by this exact section heading
(e.g. `taxonomy/v1.0.0-baseline/taxonomy.yaml` cites section `"## V1.0.0"`). Each heading is kept as a
real anchor; the chronological index below has the same information in table form.

## V1.0.0

First supplied code (`Test real data_Q2_3_V1.0.0`), Q2/Q3 exploratory only.

## ex1_taxo

First taxonomy pass.

## ex2_3_4

Bugs #1-#7 found (Swap role collision, GuardedInput no-PARAM, BubbleSortPass span leak,
ConditionalCount/NESTED, StackBalance/CounterBalance false positives, `.remove()`/`.pop()` blind spot).

## V1.2.0

Bugs #8-#11 (elif-chain composition, MultiWayBranch off-by-one, SHARED_BINDING
cross-function false positive, PARAM scope fix).

## Reporting/batch tooling

`detectors/reporting-batch/`. First batch/reporting tooling, 526 real
submissions.

## Semantic backup layer

`files_semantic_Backup.zip` + `semantic_20_07.docx` — stub-backend plumbing; honestly
self-documented as near-zero discriminative power (0.77 vs 0.79).

## Q2 fix + third strategy

`fixq2`-era. Q2 85.2% / 0.7% / 4.5% / 90.4% breakdown.

## Enforcement + Q1's LinearSearch

`register()` layering enforcement live; `LinearSearch` added for Q1. Q1 (pre-fix)
76.8%/64.2%.

## `files_Fix_Q4`

Q3 `.insert()` gap fixed (93.6%→94.0%); Q4 `SortByKey = ANY(BubbleSortPass, TopKPattern)`
taxonomy fix (13.1%→77.6%); bugs #20-#21 formalized.

---

## Chronological index

| Checkpoint / folder | What changed | Headline figure(s) |
|---|---|---|
| `detectors/v1.0.0/` | First supplied code (`Test real data_Q2_3_V1.0.0`) | Q2/Q3 exploratory only |
| `detectors/ex1-taxo/` | First taxonomy pass | — |
| `detectors/ex2-3-4/` | Bugs #1-#7 found (Swap role collision, GuardedInput no-PARAM, BubbleSortPass span leak, ConditionalCount/NESTED, StackBalance/CounterBalance false positives, `.remove()`/`.pop()` blind spot) | — |
| `detectors/v1.2.0/`  Bugs #8-#11 (elif-chain composition, MultiWayBranch off-by-one, SHARED_BINDING cross-function false positive, PARAM scope fix) | — |
| `detectors/reporting-batch/` | First batch/reporting tooling, 526 real submissions | — |
| Semantic backup layer, level-enforcement design | `ValidatedAccumulation`, `AverageStrict`, layering enforcement designed , code committed | — |
| Q2 fix + third strategy (`fixq2`-era ) | Q2 85.2% / 0.7% / 4.5% / 90.4% breakdown | Q2 90.4% |
| Enforcement + Q1 LinearSearch (2026-07-28) | `register()` layering enforcement live; `LinearSearch` added for Q1 | Q1 (pre-fix) 76.8%/64.2% |
| `files_Fix_Q4` | Q3 `.insert()` gap fixed (93.6%→94.0%); Q4 `SortByKey = ANY(BubbleSortPass, TopKPattern)` taxonomy fix (13.1%→77.6%); bugs #20-#21 formalized | Q3 94.0%, Q4 77.6% |
| Methodology V24 + `Detect_primitive` table + `Levels_of_competencies` + `Summaize` (code, four-document contradiction check) | Canonical 13-entry bug table first recorded in full; four documents cross-checked, no contradictions found | — |
| "To copy to new project" / "Transfert to new project" (retrospective) | System summary naming 3 not-yet-evidenced bugs (later #15-#17) | — |
| Semantic backup layer — `files_semantic_Backup.zip` + `semantic_20_07.docx` | Stub-backend plumbing; honestly self-documented as near-zero discriminative power (0.77 vs 0.79) | — |
| The methodology note | 19-entry bug table (bugs #14-#19 added); Case Study 4 (Q1/Q2) and Case Study 5 (Q3/Q4) confirmed; corpus totals Q1 768/575, Q2 291/435, Q3 546/308, Q4 419/357, Q5 418/108 | Q1 (unfixed) matches LinearSearch; Q2 90.4%; Q3 94.0%; Q4 77.6% |
| Real-CodeBERT/CodeT5+ Colab validation of the semantic backup layer | First real, executed raw-CodeBERT anisotropy result; codet5p exemplar/test-set code exists but not yet numerically validated | codebert anisotropy: failure (no separation) |
| AST taxonomy cross-validation via embeddings | Q5 manual/builtin/novel split validated via embeddings; single shuffled run 89.1% | Q5 taxonomy split 89.1% (single run) |
| A real, executed alternate split | Confirms 89.1% is not a fluke — one real alternate/shuffled split re-run, consistent range | Q5 taxonomy split, alternate run |
| The real 10-seed sweep | `SEEDS = list(range(10))` executed with real printed output; pooled confusion matrix + classification reports; resolves the leading pending item | Q5 taxonomy split, 10-seed mean±SD (supersedes single 89.1% run) |
| The paper, updated again | Abstract and §5.5 rewritten to report the 10-seed mean instead of the single 89.1% run | — |
| The internal methodology note, substantially rewritten | Real new version (not the same "V24" document); bug table grows 19→21 (#20 Q3 `.insert()` gap, #21 Q4 `SortByKey` taxonomy — both previously narrative-only, now numbered) | — |
| A real batch-validation script for Q1-Q4 | `run_q1_q4_batch_validation.py` delivered — first real driver script for headline Q1-Q4 figures | — |
| Real batch-validation RESULTS for Q1-Q4 | Script actually run against real Refactory corpus; `q1_report.csv`/`q2_report.csv`/`q3_report.csv`/`q4_report.csv` supplied. Real Q1-specific bug found: `SHARED_BINDING` had three blind spots causing 364 of 383 zero-scores on GuardedInput at 76.8%/64.2% pre-fix; four-part fix raised Q1 to 99.5%/97.6% with zero regressions (bug #22, extending the table 19→22). "99.93% agreement" claim resolved as a pandas `NaN != NaN` diff artifact, not a real difference — direct cell-by-cell check finds 100% agreement. "17 vs 19" genuine-gap reconciliation: post-fix `q1_report.csv` shows 17 genuine loop-missing rows + 1 parse-error row, not 19 — the pre-fix 19 included 2 files whose only gap was the new `ast.While`-condition `TEST` detection, now fixed | Q1 99.5%/97.6% (was 76.8%/64.2%) |
| Two successive paper revisions this round | Q1 diagnostic added; consolidated Table 4 (Table 5 after renumbering) added in new §5.5; full downstream renumbering confirmed clean | — |
| Q4/Q2 embedding cross-validation | Q5's 10-seed embedding-taxonomy methodology extended to Q4 and Q2 | Q4/Q2 taxonomy embedding cross-validation, real notebook output |
| The Q4 embedding result written into the paper | Already-verified embedding result written into paper text as-is — no new empirical claim, no discrepancy | — |
| The Q4/Q2 embedding cross-validation raw CSVs supplied | Raw CSVs supplied for the above — upgrades evidence tier | Q4/Q2 embedding cross-validation |
| Semantic backup layer validation, first pass | Layer's actual job tested for the first time: novel-vs-wrong separation, first real AUC (inverted design) | — |
| A third paper revision — new §7, "The Semantic Backup Layer: Architecture Overview" | New architecture section added; defers all accuracy/validation claims | — |
| Semantic backup layer validation, raw CSVs + executed notebook | `semantic_backup_bootstrap_summary.csv` + `semantic_backup_pooled_scores.csv` + executed notebook supplied — contamination-fixed design (all wrong-labeled submissions as negative class) | Novel-vs-wrong AUC 0.097 pooled (strongly inverted), 1,510 pairs |
| A naming correction | Both semantic-backup notebooks re-supplied under this project's naming convention — content unchanged | — |
| Embedding-guided clustering discovers a real Q5 delegation pattern (; cited elsewhere as "Q5 delegation fix via embedding-guided clustering") | ~38 of 43 correct-novel files share a delegation shape (`top_k` calling a helper); real code fix + genuine methodological catch, independently reproduced, not a re-guess of an earlier hunch | Q5 delegation breakdown 91.9%/80.6% (57-catch breakdown) |
| `mine_exemplars` — first round (`detectors/mine-exemplars/`) | Exemplar registry expanded 5→19 exemplars/8 competencies (still hand-written); real GuardedInput integrity bug found and fixed (both original exemplars scored 0.0, root cause: bare `while` condition not yet recognized as TEST evidence pre-Q1-fix); lexical win rate 86.7% (worst-case ranking 9/19). Per Sonia's explicit instruction, this round does not touch Table 4 or the Q5 91.9%/80.6% figures | Semantic backup registry: 86.7% pairwise win rate |
| A direct clarification | Explains why the Drive folder layout differed between notebooks — resolves the "two different working environments" question that the GuardedInput bug hypothesis above depended on | — |
| `mine_exemplars` real-corpus round (`detectors/mine-exemplars-real-corpus/`) confirms the GuardedInput hypothesis | Original `competency.py`/`test_real_data.py` used for the first mine_exemplars round supplied — byte-identical to `fixq4`'s files, confirming it predates the Q1 SHARED_BINDING fix; reconstructed bare-`while` GuardedInput exemplar now reproduces `final_score == 0.0` exactly against that era's `competency.py` | — |
| Refactory corpus license check + Exemplar registry merge (POPULATE.md step 6) | `data/exemplar_registry/` populated from `semantic_backup.py`'s own inline comments | — |
| The "nineteen vs 21/22 bug count" discrepancy checked against the actual submission draft | `Format_paper.docx` dropped the entire numbered bug-count narrative on reformatting — the 19-vs-21 mismatch is real within the older internal paper lineage but does not affect the actual paper | — |
| The finished paper draft cross-checked against Table 4/Table 5 | `Format_paper.docx` confirmed exact match to this repo's own Table 4/Table 5 | — |
| POPULATE.md step 4 (train/test split indices) supplied and merged | `split_manifests_q4_q5.zip` (seeds 00-09, 70/30) traced back to the *same* notebooks already backing the real Q4/Q5 taxonomy embedding cross-validations. `scripts/regenerate_splits.py` rewritten and independently reproduced: exact match all 10 seeds, both experiments | Q4 all 10 seeds real_csv; Q5 seed 0 real_csv, seeds 1-9 split-membership real, per-seed predictions still real_notebook_output only |
| `codet5p_110m_embedding` manifest inconsistency found and corrected | A real, executed sanity-check similarity result for this backend already existed elsewhere in the repo (`related vs related: 0.8398`, `related vs unrelated: 0.3820`) but was uncross-referenced; corrected in place, original text preserved | — |

---
