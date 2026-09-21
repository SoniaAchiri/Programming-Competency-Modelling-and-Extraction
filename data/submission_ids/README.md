# Submission ID manifests

One CSV per question: `qN_<name>.csv`, columns `submission_id,label`, where `label` is exactly
`correct` or `wrong` (the assignment's own test-suite verdict — this is the same axis as Table 3 in the
paper, and is independent of the structural competency score computed later).

**All five are now real, populated data** (added 2026-08-05, the same round Q1's `SHARED_BINDING`/
`all_names` fix was found — see `../../provenance/detector-version-log.md`), mechanically projected via
`../../scripts/build_submission_ids_from_batch_reports.py` from each question's real batch-report CSV
(`../../detectors/q1-q4-batch-validation/q{1,2,3,4}_report.csv` for Q1-Q4;
`../../detectors/reporting-batch/topk_report.csv` for Q5) — the `file` column with its `.py`
suffix stripped, and the `label` column, copied verbatim. Every file's correct/wrong split matches Table 3
exactly (confirmed by direct count, shown below), since these ARE the actual corpus enumerations the
reported percentages were computed over, not a separately-sampled or re-derived list.

| File | Question | Task | Correct/wrong counts (Table 3, confirmed exact) |
|---|---|---|---|
| `q1_sequential_search.csv` | 1 | Sequential search | 768 / 575 |
| `q2_unique_day.csv` | 2 | Unique day/month (occurrence counting) | 291 / 435 |
| `q3_remove_extras.csv` | 3 | Duplicate elimination | 546 / 308 |
| `q4_sort_age.csv` | 4 | Sort tuples by age | 419 / 357 |
| `q5_top_k.csv` | 5 | Top-K (repeated extremum extraction) | 418 / 108 |

`submission_id` is the batch report's own `file` column (e.g. `correct_1_313`), which is the same scheme
`data/labels_scores/qN_final.csv` already uses — the two join cleanly on `submission_id` as designed. This
is the identifier scheme the detector scripts themselves used when run against Sonia's local Refactory
`data/` folder, not independently verified against the Refactory corpus's own official/canonical IDs (no
official ID mapping has been supplied to this project) — see `data/splits/README.md` for the same caveat
applied to the split-index files, which are still not yet supplied.

## On redistributing the corpus itself — license check DONE (2026-09-18)

This directory holds only identifiers and the correct/wrong label, not source code or the corpus's own
files. The Refactory corpus is the dataset released alongside Hu, Ahmed, Mechtaev, Leong & Roychoudhury,
"Re-factoring Based Program Repair Applied to Programming Assignments," ASE 2019 — this is paper
reference [3] in the published paper (an earlier note in this file misattributed it as "Ureel & Wallace";
corrected here). The corpus (`data.zip`: 2,442 correct / 1,783 buggy attempts by 361 undergraduates in an
NUS introductory Python course, across 5 assignments) ships from the authors' own repository,
[github.com/githubhuyang/refactory](https://github.com/githubhuyang/refactory), confirmed directly against
that repository (2026-09-18):

- **License: LGPL-3.0**, via a `LICENSE` file at the repository root (GitHub's own license badge reads
  "LGPL-3.0 license"). `data.zip` sits in the same repository root alongside that `LICENSE` file, with no
  separate, dataset-specific license carved out for it anywhere in the README or repository — so the
  repository-wide LGPL-3.0 is the only license terms on file that could apply to it.
- **A citation request, not a separate legal restriction**: the README states, "If you use any part of our
  Refactory tool or data present in this repository, then please do cite our ASE-2019 Refactory paper."
  This project already cites it as reference [3] in the published paper; this repository's own docs should
  carry the same citation (added above) so the request is honored here too, independently of the paper.
- **No student consent/privacy language found.** The README documents the corpus's composition (361
  students, 5 assignments) but says nothing about student consent, anonymization, or any restriction
  specific to redistributing the students' own submitted code, separate from the blanket LGPL-3.0 terms.

**Practical conclusion.** LGPL-3.0 is a permissive, copyleft-lite software license; read literally, it does
not forbid redistributing the submission source code itself, only requires preserving license/copyright
notices and the license text. But LGPL-3.0 is written for software libraries, not a corpus of student
programming-assignment submissions, and its terms don't address the actual sensitivity here — students did
not themselves license their own code, and no separate statement confirms they consented to
redistribution beyond the original research use. Given that ambiguity, and because it costs this project
nothing (every figure and script here already treats `submission_id` + derived label/score as the unit of
provenance, never the source text), **this repository keeps its existing stance: submission identifiers
and derived labels/scores only, never the students' source code itself.** Anyone wanting to run the
detectors themselves obtains `data.zip` directly from the authors' repository (as this project's own
scripts already assume — `scripts/run_detector_on_corpus.py`'s docstring documents "bring your own corpus,
aligned by these IDs" as the normal path) and aligns it to the IDs in this directory.
