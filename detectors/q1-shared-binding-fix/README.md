# Q1 `SHARED_BINDING`/`all_names` fix — `files_run_Q1_batch_report_Last_version_files.zip` (canonical bug #22)

**Real date:** 2026-08-05, same day as `../q1-q4-batch-validation/` (this is a same-session
continuation: the driver script in that checkpoint was run for the first time, surfaced a real Q1-specific
gap, and this checkpoint is the fix that resulted). See `../../provenance/detector-version-log.md`'s "Real
batch-validation RESULTS for Q1-Q4" section for the complete verification writeup this README summarizes.

## What this is

Running `run_q1_q4_batch_validation.py` against the real Refactory corpus for the first time found
`GuardedInput`/`LinearSearch` scoring only 76.8%/64.2% (correct/wrong) — far below Q2/Q3's real figures.
Direct inspection of sampled real files traced 364 of 383 zero-scores (95%) to a single root cause:
`SHARED_BINDING` only ever checked a `TEST` evidence's `operand` binding (the literal left-hand side of a
simple comparison), and real student code diverges from that one shape in three quantified ways — see the
log for the full breakdown (199/55% flipped comparisons, 157/43% compound-or-chained conditions, 8/2%
`while`-loop conditions). This checkpoint's four files are the fix.

## What's here

- `competency.py` — the framework, with three additive changes (confirmed by direct `diff` against
  `../fixq4/competency.py`, the pre-fix baseline already in this repo): (1) a new `all_names`
  binding on every `TEST` evidence (every identifier referenced anywhere in the test, via `ast.walk`,
  regardless of shape); (2) a new `elif isinstance(node, ast.While)` branch in the TEST-detection function,
  synthesizing `TEST` evidence from a `while` loop's own condition; (3) `SHARED_BINDING.score()` extended
  with containment matching (`va in vb` / `vb in va`) when one side's binding is a set, alongside its
  original exact-equality check.
- `test_real_data.py` — `GuardedInput`'s structural check switched from
  `SHARED_BINDING([("source","target","test","operand")])` to `SHARED_BINDING([("source","target","test",
  "all_names")])`. **Contains a real, flagged error in its own comment**: "364 of **526** zero-scoring
  submissions" should read "364 of **383**" — 526 is Q5's unrelated total-submission count
  (`../reporting-batch/topk_report.csv`), apparently an accidental carry-over. Does not affect
  behavior; the methodology doc's own canonical bug #22 entry correctly says 383. See the log for the exact
  quoted comment and cross-check.
- `q1_competencies.py` — `LinearSearch`'s definition changed identically (`operand`→`all_names`), with an
  analogous, numerically-correct comment.
- `q1_report_FIXED.csv` — the actual post-fix batch output. **Byte-identical** (md5
  `34edf41aeae25df5bb04617807b77a2e`) to `../q1-q4-batch-validation/q1_report.csv` — the two are
  the same file, supplied twice (once standalone, once inside this fix's own zip), not independent runs.

## Verification performed this round

- The three code changes above were confirmed real and genuinely additive by direct `diff` against
  `../fixq4/competency.py` — the original `if va == vb: matches += 1` branch in
  `SHARED_BINDING.score()` is untouched; the new containment branches are `elif`s alongside it.
- Coverage recomputed directly from `q1_report_FIXED.csv` (== `q1_report.csv`): 764/768 correct (99.5%),
  561/575 wrong (97.6%) — exact match to every reported figure and to the paper's new consolidated Table 4.
- `GuardedInput_final`/`_missing` and `LinearSearch_final`/`_missing` are **byte-identical across all 1,343
  rows** (0 differences via direct column diff) — a stronger, cleaner result than the "99.93% / 1,342 of
  1,343" figure quoted in the methodology doc and paper, which traces (per the conversation's own explanation) to a
  `pandas` `NaN != NaN` comparison artifact in an earlier before/after diff, not a real difference.
- The pre-fix "19 genuine coverage gap" files (14 missing-loop, 3 missing-both, 2 missing-test-only) were
  reconciled against the post-fix CSV's own 17 remaining zero-scoring rows (14 missing-loop, 3
  missing-both, 0 missing-test-only) — an exact match confirming the 2 "test-only-missing" files were
  incidentally fixed by the new `while`-condition `TEST` detection. This reconciliation is derived
  independently in this repo's own log, not stated by any supplied document.

## Evidence status

`real_csv` — this is the first checkpoint in this project where a Q1-Q4 structural fix has a real,
independently-recomputable before/after CSV pair (`q1_prefix`/`q1_final` in `configs/stage_manifest.yaml`).
"Zero regressions" (no submission that scored 1.0 before scores lower after) is conversation-reported only — no
pre-fix CSV was supplied to independently confirm this specific claim, though it is consistent with the
fix being purely additive per the code diff itself.
