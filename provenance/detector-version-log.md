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

First supplied code (`Test real data_Q2_3_V1.0.0`), 2026-07-18. Q2/Q3 exploratory only.

## ex1_taxo

First taxonomy pass, 2026-07-19.

## ex2_3_4

2026-07-19. Bugs #1-#7 found (Swap role collision, GuardedInput no-PARAM, BubbleSortPass span leak,
ConditionalCount/NESTED, StackBalance/CounterBalance false positives, `.remove()`/`.pop()` blind spot).

## V1.2.0

2026-07-20. Bugs #8-#11 (elif-chain composition, MultiWayBranch off-by-one, SHARED_BINDING
cross-function false positive, PARAM scope fix).

## Reporting/batch tooling

`detectors/reporting-batch/` (was `2026-07-21_reporting_batch`). First batch/reporting tooling, 526 real
submissions.

## Semantic backup layer

2026-07-28. `files_semantic_Backup.zip` + `semantic_20_07.docx` — stub-backend plumbing; honestly
self-documented as near-zero discriminative power (0.77 vs 0.79).

## Q2 fix + third strategy

`fixq2`-era, 2026-07-28. Q2 85.2% / 0.7% / 4.5% / 90.4% breakdown.

## Enforcement + Q1's LinearSearch

2026-07-28. `register()` layering enforcement live; `LinearSearch` added for Q1. Q1 (pre-fix)
76.8%/64.2%.

## `files_Fix_Q4`

2026-07-28. Q3 `.insert()` gap fixed (93.6%→94.0%); Q4 `SortByKey = ANY(BubbleSortPass, TopKPattern)`
taxonomy fix (13.1%→77.6%); bugs #20-#21 formalized.

---

## Chronological index

| Checkpoint / folder | What changed | Headline figure(s) | Evidence tier |
|---|---|---|---|
| `detectors/v1.0.0/` (2026-07-18) | First supplied code (`Test real data_Q2_3_V1.0.0`) | Q2/Q3 exploratory only | conversation_reported_only |
| `detectors/ex1-taxo/` (2026-07-19) | First taxonomy pass | — | conversation_reported_only |
| `detectors/ex2-3-4/` (2026-07-19) | Bugs #1-#7 found (Swap role collision, GuardedInput no-PARAM, BubbleSortPass span leak, ConditionalCount/NESTED, StackBalance/CounterBalance false positives, `.remove()`/`.pop()` blind spot) | — | conversation_reported_only |
| `detectors/v1.2.0/` (2026-07-20) | Bugs #8-#11 (elif-chain composition, MultiWayBranch off-by-one, SHARED_BINDING cross-function false positive, PARAM scope fix) | — | conversation_reported_only |
| `detectors/reporting-batch/` (was `2026-07-21_reporting_batch`) | First batch/reporting tooling, 526 real submissions | — | conversation_reported_only |
| Semantic backup layer, level-enforcement design (2026-07-21 design / 2026-07-28 committed) | `ValidatedAccumulation`, `AverageStrict`, layering enforcement designed 21/07, code committed 28/07 | — | conversation_reported_only |
| Q2 fix + third strategy (`fixq2`-era, 2026-07-28) | Q2 85.2% / 0.7% / 4.5% / 90.4% breakdown | Q2 90.4% | conversation_reported_only, later real_csv |
| Enforcement + Q1 LinearSearch (2026-07-28) | `register()` layering enforcement live; `LinearSearch` added for Q1 | Q1 (pre-fix) 76.8%/64.2% | conversation_reported_only |
| `files_Fix_Q4` (2026-07-28) | Q3 `.insert()` gap fixed (93.6%→94.0%); Q4 `SortByKey = ANY(BubbleSortPass, TopKPattern)` taxonomy fix (13.1%→77.6%); bugs #20-#21 formalized | Q3 94.0%, Q4 77.6% | conversation_reported_only |
| Methodology V24 + `Detect_primitive` table + `Levels_of_competencies` + `Summaize` (2026-07-21 doc / 2026-07-28 code, four-document contradiction check) | Canonical 13-entry bug table first recorded in full; four documents cross-checked, no contradictions found | — | conversation_reported_only |
| "To copy to new project" / "Transfert to new project" (retrospective) | System summary naming 3 not-yet-evidenced bugs (later #15-#17) | — | conversation_reported_only |
| Semantic backup layer — `files_semantic_Backup.zip` + `semantic_20_07.docx` (2026-07-28) | Stub-backend plumbing; honestly self-documented as near-zero discriminative power (0.77 vs 0.79) | — | conversation_reported_only |
| The 28/07 methodology note + `Structural_Competency_Extraction_Paper.docx` (finished paper, 2026-07-28) | 19-entry bug table (bugs #14-#19 added); Case Study 4 (Q1/Q2) and Case Study 5 (Q3/Q4) confirmed; corpus totals Q1 768/575, Q2 291/435, Q3 546/308, Q4 419/357, Q5 418/108 | Q1 (unfixed) matches LinearSearch; Q2 90.4%; Q3 94.0%; Q4 77.6% | conversation_reported_only |
| `Competency_Extraction_Article.docx` (undated, pre-28/07 hypothesized) | Older, standalone article predating enforcement/NESTED fix/Q1-Q4 entirely — confirmed by direct read | — | n/a (context document) |
| Real-CodeBERT/CodeT5+ Colab validation of the semantic backup layer (2026-08-0x) | First real, executed raw-CodeBERT anisotropy result; codet5p exemplar/test-set code exists but not yet numerically validated | codebert anisotropy: failure (no separation) | real_notebook_output |
| AST taxonomy cross-validation via embeddings (2026-08-0x) | Q5 manual/builtin/novel split validated via embeddings; single shuffled run 89.1% | Q5 taxonomy split 89.1% (single run) | real_csv (single run) |
| A real, executed alternate split (04/08/2026) | Confirms 89.1% is not a fluke — one real alternate/shuffled split re-run, consistent range | Q5 taxonomy split, alternate run | real_execution |
| The real 10-seed sweep (2026-08-04→05) | `SEEDS = list(range(10))` executed with real printed output; pooled confusion matrix + classification reports; resolves the leading pending item | Q5 taxonomy split, 10-seed mean±SD (supersedes single 89.1% run) | real_notebook_output |
| The published paper, updated again (2026-08-05) | Abstract and §5.5 rewritten to report the 10-seed mean instead of the single 89.1% run | — | n/a (paper text, tracks the sweep above) |
| The internal methodology note, substantially rewritten (2026-08-05) | Real new version (not the same "V24"/28-07 document); bug table grows 19→21 (#20 Q3 `.insert()` gap, #21 Q4 `SortByKey` taxonomy — both previously narrative-only, now numbered) | — | conversation_reported_only |
| A real batch-validation script for Q1-Q4 (2026-08-05) | `run_q1_q4_batch_validation.py` delivered — first real driver script for headline Q1-Q4 figures | — | n/a (script delivery) |
| Real batch-validation RESULTS for Q1-Q4 (2026-08-05) | Script actually run against real Refactory corpus; `q1_report.csv`/`q2_report.csv`/`q3_report.csv`/`q4_report.csv` supplied. Real Q1-specific bug found: `SHARED_BINDING` had three blind spots causing 364 of 383 zero-scores on GuardedInput at 76.8%/64.2% pre-fix; four-part fix raised Q1 to 99.5%/97.6% with zero regressions (bug #22, extending the table 19→22). "99.93% agreement" claim resolved as a pandas `NaN != NaN` diff artifact, not a real difference — direct cell-by-cell check finds 100% agreement. "17 vs 19" genuine-gap reconciliation: post-fix `q1_report.csv` shows 17 genuine loop-missing rows + 1 parse-error row, not 19 — the pre-fix 19 included 2 files whose only gap was the new `ast.While`-condition `TEST` detection, now fixed | Q1 99.5%/97.6% (was 76.8%/64.2%) | real_csv |
| Two successive paper revisions this round (2026-08-05, 20p→21p→22p) | Q1 diagnostic added; consolidated Table 4 (Table 5 after renumbering) added in new §5.5; full downstream renumbering confirmed clean | — | n/a (paper text) |
| Q4/Q2 embedding cross-validation (2026-08-05) | Q5's 10-seed embedding-taxonomy methodology extended to Q4 and Q2 | Q4/Q2 taxonomy embedding cross-validation, real notebook output | real_notebook_output |
| The Q4 embedding result written into the paper (2026-08-05) | Already-verified embedding result written into paper text as-is — no new empirical claim, no discrepancy | — | n/a (paper text) |
| The Q4/Q2 embedding cross-validation raw CSVs supplied (2026-08-05) | Raw CSVs supplied for the above — upgrades evidence tier | Q4/Q2 embedding cross-validation | real_csv |
| Semantic backup layer validation, first pass (2026-08-08) | Layer's actual job tested for the first time: novel-vs-wrong separation, first real AUC (inverted design) | — | real_notebook_output |
| A third paper revision — new §7, "The Semantic Backup Layer: Architecture Overview" (2026-08-08) | New architecture section added; defers all accuracy/validation claims to "the companion paper" | — | n/a (paper text) |
| Semantic backup layer validation, raw CSVs + executed notebook (2026-08-08) | `semantic_backup_bootstrap_summary.csv` + `semantic_backup_pooled_scores.csv` + executed notebook supplied — contamination-fixed design (all wrong-labeled submissions as negative class) | Novel-vs-wrong AUC 0.097 pooled (strongly inverted), 1,510 pairs | real_csv |
| A naming correction (2026-08-08) | Both semantic-backup notebooks re-supplied under this project's naming convention — content unchanged | — | n/a (housekeeping) |
| Embedding-guided clustering discovers a real Q5 delegation pattern (2026-08-08; cited elsewhere as "Q5 delegation fix via embedding-guided clustering") | ~38 of 43 correct-novel files share a delegation shape (`top_k` calling a helper); real code fix + genuine methodological catch, independently reproduced, not a re-guess of an earlier hunch | Q5 delegation breakdown 91.9%/80.6% (57-catch breakdown) | real_csv |
| `mine_exemplars` — first round (`detectors/mine-exemplars/`, 2026-08-08→2026-08-13) | Exemplar registry expanded 5→19 exemplars/8 competencies (still hand-written); real GuardedInput integrity bug found and fixed (both original exemplars scored 0.0, root cause: bare `while` condition not yet recognized as TEST evidence pre-Q1-fix); lexical win rate 86.7% (worst-case ranking 9/19). Per Sonia's explicit instruction, this round does not touch Table 4 or the Q5 91.9%/80.6% figures | Semantic backup registry: 86.7% pairwise win rate | real_execution |
| A direct clarification from Sonia (2026-09-17) | Explains why the Drive folder layout differed between notebooks — resolves the "two different working environments" question that the GuardedInput bug hypothesis above depended on | — | n/a (clarification) |
| `mine_exemplars` real-corpus round (`detectors/mine-exemplars-real-corpus/`, 2026-09-17) confirms the GuardedInput hypothesis | Original `competency.py`/`test_real_data.py` used for the first mine_exemplars round supplied — byte-identical to `fixq4`'s files, confirming it predates the 2026-08-05 Q1 SHARED_BINDING fix; reconstructed bare-`while` GuardedInput exemplar now reproduces `final_score == 0.0` exactly against that era's `competency.py` | — | real_execution |
| Refactory corpus license check + Exemplar registry merge (POPULATE.md step 6, 2026-09-18) | `data/exemplar_registry/` populated from `semantic_backup.py`'s own inline comments | — | real_csv |
| The "nineteen vs 21/22 bug count" discrepancy checked against the actual submission draft (2026-09-18) | `Ver. 2026.8.23 IJIES_Format_paper.docx` (the real journal submission) dropped the entire numbered bug-count narrative on reformatting — the 19-vs-21 mismatch is real within the older internal paper lineage but does not affect the actual submitted paper | — | real_execution (direct grep/pdftotext check) |
| The finished paper draft cross-checked against Table 4/Table 5 (2026-09-18) | `Ver. 2026.8.23 IJIES_Format_paper.docx` confirmed exact match to this repo's own Table 4/Table 5 | — | real_execution |
| Checkpoint-naming pilot rename (2026-09-19) | `detectors/2026-07-21_reporting_batch` → `detectors/reporting-batch` — first stable, date-free kebab-case slug; every regenerated file, including downstream CSVs, diffed byte-for-byte against pre-rename content (only path strings changed) | — | n/a (housekeeping) |
| Checkpoint-naming rollout complete (2026-09-19) | All remaining 23 dated checkpoint folders renamed repo-wide to the same convention; same byte-for-byte re-verification | — | n/a (housekeeping) |
| Corrections to the earlier (fabricated) `VERSIONING.md` (2026-09-19) | Scaffold-era `VERSIONING.md`, written before real artifacts existed, had guessed at some structure; corrected against real supplied content | — | n/a (housekeeping) |
| Paper and methodology raw files withheld ahead of GitHub push (2026-09-19) | Verbatim paper/methodology excerpts replaced with paraphrases throughout this log and `papers/README.md`/`methodology/README.md`, since the paper is not yet published | — | n/a (housekeeping) |
| POPULATE.md step 4 (train/test split indices) supplied and merged (2026-09-20) | `split_manifests_q4_q5.zip` (seeds 00-09, 70/30) traced back to the *same* notebooks already backing the real Q4/Q5 taxonomy embedding cross-validations — confirmed with Sonia (not assumed) that this is the same experiment, not a distinct unsupplied one. `scripts/regenerate_splits.py` rewritten and independently reproduced: exact match all 10 seeds, both experiments | Q4 all 10 seeds real_csv; Q5 seed 0 real_csv, seeds 1-9 split-membership real, per-seed predictions still real_notebook_output only | real_csv (Q4), mixed (Q5, see entry) |
| `codet5p_110m_embedding` manifest inconsistency found and corrected (2026-09-20) | A real, executed sanity-check similarity result for this backend already existed elsewhere in the repo (`related vs related: 0.8398`, `related vs unrelated: 0.3820`) but was uncross-referenced; corrected in place, original text preserved | — | real_notebook_output |
| `chat_reported_only` evidence label renamed to `conversation_reported_only` (2026-09-21) | Prose and controlled-vocabulary rename across 36 files (528 + 26 replacements); 12 real on-disk filenames containing "chat" and 2 verbatim historical citations explicitly protected and confirmed unchanged; full fresh-venv + pytest re-run clean | — | n/a (housekeeping) |
| Hardcoded `/home/claude/refactory` sandbox path made portable (2026-09-21) | `REFACTORY_ROOT` env var / path-relative-to-`__file__` resolution added to 14 files, replacing the hardcoded sandbox path; each script's own README carries a note pointing here | — | n/a (housekeeping) |
| This distillation (2026-09-21) | `provenance/detector-version-log.md` condensed from ~4,800 lines of development narrative to this audit index, per Sonia's explicit request — full narrative preserved in git history (see header note above) | — | n/a (housekeeping) |

---

## Still-pending items

- **The unscoped Q5 pre-fix figure (83.0%) and its later unscoped re-run (82.1%)** — neither has a CSV or
  driver script; both remain `conversation_reported_only`. Per Sonia's explicit instruction, these stay as
  already logged, not re-derived.
- **Bug #13's `magus_sort` cross-function-credit bug** — canonical symptom/root-cause/fix text exists; no
  code was ever supplied for it.
- **`CountedSearch`'s lifted-siblings replacement code** (`LoopStep`/`OutputStep` wrappers) — referenced
  only in prose, never supplied as an artifact.
- **The companion paper** — the semantic-backup layer's own accuracy/validation claims are explicitly
  deferred to a separate, still-entirely-unsupplied document. Not to be confused with the structural,
  AST-only paper this repo otherwise tracks.
- **Two semantic-backup embedding backends remain `PENDING`**: `jina_v2_code` (no code or result supplied)
  and `codet5p_110m_embedding` (`CODE_EXISTS_NOT_VALIDATED` — a related sanity-check number exists
  elsewhere in the repo under a different stage, cross-referenced in place, but this backend's own
  contaminated-comparison description has not itself been re-run clean).
- **Bug-count discrepancy** (cosmetic, confined to a superseded lineage): the internal
  "Structural_Competency_Extraction_Paper" lineage's text says "nineteen structural defects... a further
  two informational... = 21," which doesn't cleanly match the canonical bug table's own accounting.
  Checked directly against `Ver. 2026.8.23 IJIES_Format_paper.docx` (the actual journal submission): that
  draft dropped the numbered bug-count narrative entirely on reformatting, so nothing in the submitted
  paper needs correcting on this point.
- **Methodology-doc page-count discrepancy** (cosmetic, unresolved): "~11 pages" vs. "15 pages, up from
  14" in two summary-style descriptions of what appears to be the same document.

---

## Notes preserved from the original narrative

- **"The updated paper" (first revision)**: the paper's first tracked revision beyond its original
  28/07 "finished paper" state — folding in the Case Study 5 (Q3/Q4) content and the early structural
  edits that preceded the 10-seed-sweep rewrite covered by "The published paper, updated again" below.
  `papers/README.md` treats these as two distinct, dated revisions in the same file tree; this index's
  chronological table above (the 2026-07-28 and 2026-08-05 paper-related rows) is the same structural
  summary in table form.
- **"A direct clarification from Sonia" (2026-09-17)**: resolves why two supplied notebooks appeared to
  come from different working environments (different Drive folder layouts) — the explanation this file's
  GuardedInput-bug hypothesis (see the chronological index, 2026-08-08→2026-08-13 row) depended on before
  it was confirmed with hard evidence the following round.
- **Evidence-preservation discipline**: earlier rounds of this project's own audit work followed a rule of
  never silently rewriting a superseded claim — appending a dated `UPDATE:` note instead and leaving the
  original text in place. This distillation follows the same rule going forward: any future correction to
  a line in this file should be appended, not silently edited out.
- **`docs/KNOWN_CAVEATS.md`** carries the current, corrected, load-bearing figures (85.2%/0.7%/4.5%/90.4%
  for Q2) as the ones that supersede any earlier reading, regardless of which historical document is being
  read.
