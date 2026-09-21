# Q1-Q4 batch validation script — real code, RUN, with real results (updated same day)

**Real date:** 2026-08-05, per Sonia directly. (This corrects an initial dating of this checkpoint to
2026-09-13, which had been inferred from the accompanying conversation export's own `dcterms:created`/
`dcterms:modified` docx metadata — that metadata reflects when the conversation was exported/saved as a file, not
when the underlying conversation actually happened.) See `../../provenance/detector-version-log.md`'s "A real
batch-validation script for Q1-Q4" and "Real batch-validation RESULTS for Q1-Q4" sections for the full
verification writeup this README summarizes.

**Update, same day:** this script has now actually been run by Sonia against her real Refactory dataset.
`q1_report.csv`/`q2_report.csv`/`q3_report.csv`/`q4_report.csv` below are the real output — see "What's
here (this update)" below. The run also surfaced a real, Q1-specific structural-detector gap, fixed at
`../q1-shared-binding-fix/`.

## What this is

The first-ever supplied driver script that runs the project's own already-verified `batch_report.py`
machinery (see `../reporting-batch/`) against Refactory Questions 1-4, mirroring exactly the
process that already produced `topk_report.csv` for Q5. Until this script arrived, no batch script or CSV
existed for any of the four questions' headline figures (90.4% Q2, 94.0% Q3, 77.6% Q4 `SortByKey`,
1,343/1,342 Q1 `LinearSearch`) — every one of them was real and multiply-corroborated across conversation/paper
text, but not independently regenerable.

## What's here

- `run_q1_q4_batch_validation.py` — the real script, read in full.
- `run_q1_q4_batch_validation_chat_export.txt` — the accompanying conversation, converted from `Conversation for run
  Q1-Q4 batch validation.docx` via `pandoc`. Contains two conversation states: an earlier draft (Q1's function
  name unresolved, `function_name=None`, whole-file) and a later, final state (all four function names
  "confirmed," fully function-scoped) — the supplied `.py` file matches the later, final state only.

## Verification performed this round — direct diff against files already in this repository

Rather than taking the script or its conversation at face value, every checkable claim was verified directly
against real project files already supplied in earlier rounds:

| Claim | Verified against | Result |
|---|---|---|
| `process_folders(..., function_name=...)` is the real batch_report.py API | `../reporting-batch/batch_report.py` | **Confirmed exact match** |
| Q1's original `q1_competencies.py` used whole-file resolution, no function scoping | the actual `q1_competencies.py` `__main__` block | **Confirmed exact match** |
| `ex2_3_4_competencies.py` / `q2_competencies.py` are real module filenames | `files_ex2_3_4.zip` / `files_Q2_competencies_3rd_strategie.zip` | **Confirmed exact match** |
| The shared-`model` import chain is coherent across all 4 modules | `test_real_data.py` / `pw01_competencies.py` / `q2_competencies.py` / `ex2_3_4_competencies.py` imports | **Confirmed coherent — one shared `CompetencyModel()` instance** |
| "`pw01_competencies.py` ... define[s] and resolve[s] against a function literally named `unique_day`" | full read of `pw01_competencies.py` | **FALSE** — zero mentions of `unique_day`; the file covers unrelated Ex1.2-1.6 exercises |
| `ex2_3_4_competencies.py` may register `SelectionStep` (script's own hedge) | full read of `ex2_3_4_competencies.py` | **False, but harmless** — registers an unrelated exercise set (rock-paper-scissors/change-making/balanced-parens/tic-tac-toe); `SelectionStep` is already registered by `test_real_data.py`, imported first |
| Q4's `SortByKey` will be registered when the script runs | diff of `c8f2a77d-test_real_data.py` vs. `../fixq4/test_real_data.py` | **Real, unflagged risk found** — `SortByKey` exists ONLY in the `fixQ4` version; the diff shows it is the *only* difference between the two files. If Sonia's live `test_real_data.py` is the earlier version, Q4's columns will silently come back empty. |
| Q1=`search`, Q3=`remove_extras`, Q4=`sort_age` are confirmed function names | no real Q1/Q3/Q4 submission source file has been supplied to this project | **Not independently checkable — logged as Sonia-asserted only** |

## What's here (this update) — the real run results

- `q1_report.csv` (1,343 rows), `q2_report.csv` (726 rows), `q3_report.csv` (854 rows), `q4_report.csv`
  (776 rows) — the actual output, run by Sonia against her real Refactory dataset. Independently
  recomputed in-session: Q1 `GuardedInput`/`LinearSearch` 99.5%/97.6%, Q2 `UniqueCheck` 90.4%/74.3%, Q3
  `SelectionStep` 94.0%/74.7%, Q4 `SortByKey` 77.6%/45.9% (correct/wrong) — exact match to the paper's new
  consolidated Table 4 and to `configs/stage_manifest.yaml`'s `q1_final`/`q2_final`/`q3_final`/`q4_final`
  stages, all now `evidence: real_csv`.
- `run_q1_Q4_batch_validation_RESULTS_chat_export.txt` — this update's own conversation export (converted via
  `pandoc` from `run_q1_Q4_batch_validation.docx`), covering the run itself, the Q1 diagnostic
  investigation (383 zero-scores → 19 genuine + 364 structural, three mechanisms), the fix (logged at
  `../q1-shared-binding-fix/`), and the resulting paper/methodology-doc updates.
- The Q4 `SortByKey`-registration operational risk flagged below (in the original verification table) did
  **not** materialize: `q4_report.csv`'s `SortByKey_final`/`SortByKey_missing` columns are populated for
  every row, confirming Sonia's live `test_real_data.py` did include the registration.

## Evidence status

`evidence: real_csv` for all four questions, as of this update — the first time any of Q1-Q4's headline
percentages are backed by a real, independently-recomputable CSV rather than being `conversation_reported_only`.
See `configs/stage_manifest.yaml` and `../../provenance/detector-version-log.md` for the full writeup,
including a real Q1-specific structural-matching bug this run surfaced and its fix
(`../q1-shared-binding-fix/`).
