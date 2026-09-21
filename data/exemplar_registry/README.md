# Exemplar registry (semantic backup layer)

**Merged 2026-09-18 from the real, delivered `EXEMPLAR_REGISTRY`** in
`../../detectors/semantic-backup-validation-executed/semantic_backup.py` — this repo's most
current and most audit-clean semantic-backup checkpoint (see that checkpoint's own `README.md`). This
replaces the earlier 2-competency/5-exemplar stub (`FindExtremum`, `Accumulation`, never independently
verified against the live structural rules — see git history / `provenance/detector-version-log.md` for that
stub's own record).

## What's actually here

`exemplars.csv` holds all **10 competencies, 27 exemplars** — the exact figure this project's papers and
`configs/stage_manifest.yaml` (`exemplar_registry_real_mined_v3_executed`) already document. `code/` holds
each exemplar's source verbatim (minus the notebook's triple-quote formatting artifact — one leading/
trailing blank line stripped).

**Every `final_score` in this CSV was freshly computed in this merge**, not copied from a prior report:
`scripts/build_exemplar_registry.py` imports the real competency model (the same
`test_real_data -> pw01_competencies -> q2_competencies` chain the checkpoint's own `audit_registry()`
uses) and calls `model.resolve()` directly on every exemplar. All 27 score `final_score = 1.0000` against
the live structural rules — `audit_registry()` reports zero problems. Re-run
`python scripts/build_exemplar_registry.py --check` at any time to reproduce this without writing
anything.

## Provenance, per exemplar

The `source` / `source_submission_id` / `notes` columns are transcribed directly from
`semantic_backup.py`'s own inline comments (quoted in full in
`../../provenance/detector-version-log.md`'s 2026-09-18 entry for this merge) — nothing here is inferred or
guessed:

| `source` value | Count | Meaning |
|---|---|---|
| `hand-written` | 14 | Written directly as an exemplar, never found invalid |
| `hand-written (corrected)` | 4 | Replaces an original exemplar that `audit_registry()` found scored `final_score=0.00` (2 `GuardedInput`: bare `while`-condition had no TEST evidence; 2 `AccumulateThenCount`: `len()`-based instead of `.count()`-based) — see `notes` on each row and `semantic_backup_findings.md` finding #7 |
| `mined` | 9 | A real Refactory submission (or one of a documented real-mined set), verified `final_score=1.00` by construction |

Of the 9 `mined` rows, 2 (`ConditionalCount`) carry an exact `source_submission_id`
(`correct_2_010`, `correct_2_016`) because the source comment names the file. The other 7 (1
`AccumulateThenCount`, 3 `FunctionalUniqueCheck`, 3 `DelegatesUniqueness`) come from mining runs the
comments describe by *method and corpus proportion* (e.g. "227/291, 78%, 96 distinct shapes" for
`DelegatesUniqueness`) but do not name an individual submission file per exemplar — `source_submission_id`
is left blank for these rather than invented, and the `notes` column says so explicitly.

`DelegatesUniqueness`'s three exemplars store **both** `unique_day` and `contains_unique_day` (the full
two-function text), because `DELEGATES` needs the callee's own body present to verify structurally. A real
submission, though, is only ever scored — and its snippet embedded for similarity — as
`contains_unique_day` alone; `semantic_backup.py`'s `DELEGATING_FUNCTION` / `runtime_scoped_exemplar()`
scope these three exemplars down accordingly at every embedding call site. The registry storage didn't
need to change for this fix, only what gets embedded — this CSV/`.py` files reflect the stored (full,
two-function) form, matching what `audit_registry()` verifies.

## Which checkpoint verified these

`verified_detector_checkpoint` is kept short in the CSV (`detectors/q5-delegation-clustering-fix
+ semantic-backup-validation-executed`) — spelled out in full:

- `competency.py` / `test_real_data.py` are confirmed byte-identical (modulo one string-embedding blank
  line) to `../../detectors/q5-delegation-clustering-fix` — this repo's own current HEAD
  structural model.
- `pw01_competencies.py` / `q2_competencies.py` (the extra registrations needed for
  `AccumulateThenCount`, `FunctionalUniqueCheck`, `DelegatesUniqueness`) exist only embedded inside
  `../../detectors/semantic-backup-validation-executed/semantic_backup_validation.ipynb`'s own
  source cells — not duplicated as standalone files anywhere in this repo — so that checkpoint is cited
  directly rather than a plain `detectors/<name>/` folder that doesn't exist for them.

`verified_taxonomy_checkpoint` is `N/A` for every row: no `taxonomy/<checkpoint>/taxonomy.yaml` snapshot
postdates the detector checkpoint above (the newest is `fixq4-sortbykey`), and the three extra
Q2 competencies this registry exercises were never given their own `taxonomy/` snapshot. Recorded honestly
as not applicable rather than pointing at a taxonomy checkpoint that doesn't actually cover this code.

## Schema — `exemplars.csv`

| Column | Type | Meaning |
|---|---|---|
| `exemplar_id` | string | Stable identifier, `<competency_slug>_<NN>` |
| `competency` | string | One of the 10 registered competencies |
| `source` | `hand-written` \| `hand-written (corrected)` \| `mined` | Origin — see table above |
| `source_submission_id` | string, nullable | Exact Refactory submission file when individually named in the source comment; blank otherwise (see above) |
| `final_score` | float | Freshly computed this merge via `model.resolve()` against the live structural rules; all 27 are `1.0000` |
| `verified_taxonomy_checkpoint` / `verified_detector_checkpoint` | string | Which real checkpoint(s) this exemplar was verified against — see above for the full story |
| `code_path` | string | Relative path to the exemplar's source file within this directory |
| `notes` | string, nullable | Shape name, mining-run description, or correction history transcribed from `semantic_backup.py`'s own comments |

## Still pending

Real CodeBERT-backed (`codet5p-110m-embedding`) similarity numbers for this exact merged registry are
already `real_notebook_output`-backed (see `configs/stage_manifest.yaml`'s
`exemplar_registry_real_mined_v3_executed` / `codet5p_bootstrap_novel_vs_wrong_auc` entries) but not
independently re-executable in this sandbox (`huggingface.co` blocked). The embedding **train/test split
indices** (step 4 of `../../POPULATE.md`) remain entirely separate and unsupplied — do not confuse the two;
this registry merge does not touch step 4 at all.
