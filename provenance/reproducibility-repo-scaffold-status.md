# Public reproducibility repository — status

Delivered as `competency-extraction-repro.zip`, last updated 2026-09-21 (part 22: removed narrative "chat" references, renamed the `chat_reported_only` evidence label to `conversation_reported_only` system-wide) — **regenerated from real
evidence (`provenance/detector-version-log.md`), replacing an earlier scaffold (delivered 2026-09-07) whose
`VERSIONING.md` and `configs/stage_manifest.yaml` were fabricated by inference from the paper's prose
before any real checkpoint, conversation export, or paper draft had been examined.** That earlier version stated
specific numbers that never appeared in any real artifact — a Q1 "76.8%→99.5%" trail, a Q5
"→79.7%→91.9%" trail, a nonexistent `TopKPatternExtended` competency with `DELEGATES`+`SELF_RECURSIVE`,
and an entire fabricated Table-5 embedding-validation section — found and corrected in that round rather
than silently patched.

## What's real and done

- **Real code for every detector checkpoint** — `detectors/<real-date>_<Sonia's-own-label>/` (fourteen
  checkpoints, `2026-07-18_V1.0.0` through `2026-08-08_semantic_backup_layer_validation`, plus the
  semantic-backup extension, two diff-bounded intermediate saves, and a real Colab semantic-backup
  validation checkpoint), not an invented `v1.0.0`-`v1.4.0` ladder. Provenance is checkpoint label + real
  date (zip-preserved mtime / conversation-export marker / diff-bounding / PDF/docx metadata), since no commit
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
  (2026-09-20, part 21): the `q4_sortbykey_splits`/`q5_topk_splits` train/test-split entries are now real
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

## New this round, part 20 (2026-09-19): paper and methodology raw files withheld, ahead of the actual GitHub push

Sonia asked to remove "all docs" for the paper before pushing this repo to GitHub, since the paper itself
isn't published yet. Clarified scope with two quick questions before touching anything (this is a
destructive, judgment-call-heavy request — worth confirming rather than guessing): (1) just the raw
paper/methodology files, or also the substantial verbatim excerpts quoted elsewhere in this repo; (2)
delete outright, or keep locally and just exclude from git. Sonia chose: raw files only removed at first
pass (brief citations to stay), delete outright (nothing has been pushed yet — one local commit, no
remote configured).

**What was removed**: all 15 raw paper/methodology files under `papers/` and `methodology/`
(`.docx`/`.pdf`, 4.2MB + 712KB) — full manuscript drafts and the internal methodology note. Both folders'
own `README.md` files (a structural revision history — dates, what changed, verification citations) are
kept. No script or test in this repo depends on these files programmatically (confirmed by grep before
deleting) — they were reference-only.

**A second pass was needed**: reviewing `papers/README.md` and `provenance/detector-version-log.md` after the
raw-file deletion found that deleting the docx/pdf files alone didn't actually achieve Sonia's goal — both
documents contained long, verbatim block-quoted passages reproducing substantial paper content (the entire
new §7 "Semantic Backup Layer" section, full new Abstract/§5.5/§5.6 paragraphs, methodology-doc bug-table
entries and Limitations bullets — 125+ quoted lines combined, several full paragraphs). This was flagged
back to Sonia explicitly rather than silently deciding either way, since it directly affects whether her
actual goal (nothing paper-derived exposed before publication) is met. She confirmed: replace with short
paraphrases, keeping the factual claims (what changed, verified against what data) but not the paper's own
prose.

**What was paraphrased**: 4 genuine paper-manuscript quote blocks (the §5.5 embedding-validation section,
the Q4 embedding paragraph + its closing paragraph, the §7 Architecture Overview section) across
`papers/README.md` and `provenance/detector-version-log.md`, plus one methodology-doc bullet cluster (§5.2,
§6.1, bug #22, a §9 Limitations bullet) in all three of `papers/README.md`,
`provenance/detector-version-log.md`, and `methodology/README.md`. Every paraphrase keeps the structural facts
(what section, what changed, exact verified figures with their script/CSV citations) and drops the actual
paper prose. **Deliberately left alone**, after checking each was not paper-manuscript text: code diffs
(`report.py`), code comments (`test_real_data.py`'s own inline comment), and dev-session conversation-transcript
quotes (Sonia's own conversation reasoning, e.g. the AUC-interpretation correction, the Q2/Q4 scoping-decision
reasoning) — none of these reproduce the unpublished paper itself. `README.md`'s two folder-table rows
updated to say the raw files are withheld and point at the (now paraphrase-only) README in each folder.

**Verified clean after both passes**: `pytest tests/ -q` — 11/11; `scripts/build_exemplar_registry.py
--check` — 0 problems; `scripts/regenerate_q5_percentages.py --all-stages` — both real Q5 stages still
match reported figures exactly. `papers/`+`methodology/` combined size: 4.9MB → 36KB (README.md files
only). A repo-wide grep for markdown blockquote lines (`^>`) outside `detectors/`/`taxonomy/` checkpoint
files, run after both passes, confirms the only remaining ones are this repo's own reviewer-question quote
in `README.md`, the `report.py` code diff, the `test_real_data.py` code comment, and one conversation-transcript
quote — none are paper-manuscript text.

**Not yet decided**: whether to actually create a git commit and/or configure a remote — this repo has one
local commit and no remote configured; per this session's own git safety discipline, no commit was created
without being asked. The zip has been rebuilt and redelivered with this round's changes.

## New this round, part 19 (2026-09-19): checkpoint-naming rollout complete — all remaining 23 dated checkpoints renamed, repo-wide

Sonia reviewed part 18's pilot rename (one checkpoint, `detectors/reporting-batch`) and said to go ahead.
The same pattern was applied to every remaining dated checkpoint directory in the repo:

**What changed**: all 19 remaining `detectors/<date>_<label>/` directories and all 4 remaining
`taxonomy/<date>_<label>/` directories renamed to stable, date-free kebab-case slugs — e.g.
`detectors/2026-08-08_q5_delegation_clustering_fix` → `detectors/q5-delegation-clustering-fix`,
`taxonomy/2026-07-18_V1.0.0_baseline` → `taxonomy/v1.0.0-baseline`. (`detectors/_intermediate_unlabeled/`
was already undated and untouched; `detectors/reporting-batch/` was already done in the pilot.) The full
23-item mapping and every checkpoint's own real-date evidence (its `README.md`/`taxonomy.yaml` header, or
`detectors/CHANGELOG.md`/`taxonomy/CHANGELOG.md`'s own "Real date" column) was checked before renaming —
confirmed independent of the folder name in every case, so nothing was lost.

**Mechanics, same discipline as the pilot, at full scale**: a repo-wide grep found every file referencing
any of the 23 old directory names (38 non-CSV files, 364 total string replacements) and updated them by
plain substitution; 6 mechanically-generated CSVs that embed checkpoint paths in their own `notes` columns
(`data/exemplar_registry/exemplars.csv`, `data/labels_scores/q{1,2,3,4}_final.csv`,
`q5_final_extended.csv`) were deliberately excluded from that substitution and instead regenerated via
their own build scripts (`build_exemplar_registry.py --write`, `build_labels_scores_from_batch_reports.py
--all`) once those scripts' own path constants had been updated — then diffed programmatically,
column-by-column, against pre-rename backups: **zero data mismatches across 4,252 rows**; the only columns
that ever differed were the path-bearing ones (`notes`, `verified_detector_checkpoint`), confirmed by
listing exactly which columns changed per file, not just eyeballing a sample.

**Three prose sentences that used a checkpoint's dated name as their only inline date anchor** (the same
failure mode as the pilot's one `taxonomy.yaml` fix) were found by scanning specifically for
temporal-anchor phrasing ("at the X checkpoint", "since the X checkpoint", etc.) immediately preceding an
old checkpoint name, rather than flagging every plain path citation losing an incidental date (that would
have flagged 276 lines, nearly all of them ordinary path mentions where the real date was never that
sentence's point and remains fully recoverable from the checkpoint's own README/CHANGELOG — exactly the
intended effect of this whole change). The 3 genuine hits — one in
`detectors/semantic-backup-layer-validation/README.md`, two in `taxonomy/v1.0.0-baseline/taxonomy.yaml`
— got the real date reinserted inline by hand.

**`VERSIONING.md` and `README.md` updated** to describe the new naming convention accurately (both had
been mechanically string-substituted but still described the *old* `<date>_<label>` scheme in their own
prose — caught and rewritten, not just left inconsistent) — including the reasoning (public GitHub repo,
cited by reviewers, wants stable slugs, not paths that need editing whenever a date is later corrected —
`reporting-batch`'s own date is already only an inferred "~2026-07-21") and the plan for git tags/commits,
honestly dated at actual push time, as the citable version mechanism once this repo is pushed.

**Re-verified clean, full suite**: `pytest tests/ -q` — 11/11; `scripts/regenerate_table4.py --stage final
--check` — all five questions match (Q5 still 91.9%/80.6%); `scripts/build_exemplar_registry.py --check`
— 0 problems, all 27 `final_score=1.0000`; `scripts/regenerate_q5_percentages.py --all-stages` — both Q5
stages match reported figures against their renamed checkpoints; a final repo-wide grep for any of the 23
old directory-name strings anywhere in the tree returns **zero hits** (not even a historical note this
time — unlike the pilot, there was no prior rename event to document).

**Not renamed, and not part of this change**: `detectors/_intermediate_unlabeled/` (already undated by
design) and the checkpoint directories' *internal* contents (their own real, unedited batch-report CSVs
like `topk_report.csv`, `q1_report.csv` etc. — these moved with their parent folder and were never
touched). The zip has been rebuilt and redelivered with this round's changes.

## New this round, part 18 (2026-09-19): checkpoint-naming pilot — one dated folder renamed end-to-end, awaiting Sonia's review before the rest

Sonia asked whether the dated checkpoint-folder naming (`detectors/2026-07-21_reporting_batch/`, etc.) could
be changed to remove dates, given the repo's actual destination: published on GitHub, read by reviewers. The
recommendation (git-native versioning: stable kebab-case slugs for folder names; real dates kept exactly
where they already live — checkpoint `README.md` prose, `CHANGELOG.md`'s own "Real date" column,
`provenance/detector-version-log.md`; git tags/commits, honestly dated at actual push time and never backdated,
as the citable version mechanism once this is a real repo) was approved for a scoped pilot on exactly one
checkpoint before touching the other 23: `detectors/2026-07-21_reporting_batch/` → `detectors/reporting-batch/`.

**What the pilot did**: renamed the folder; confirmed its own `README.md` independently documents the real
date in prose (so nothing is lost — "Dating is by inference from the 2026-07-21 conversation narrative..."); found
and updated all 18 files referencing the old path string via `grep -rl` + `sed`, except
`data/labels_scores/q5_final.csv` (a mechanically-generated file — never hand-edit those, regenerate them
instead).

**What the pilot found, beyond the rename itself**: fixing `q5_final.csv` properly surfaced a real,
pre-existing gap — `scripts/build_labels_scores_from_batch_reports.py`'s Q5 entry had only ever built
`q5_final_extended.csv`; `q5_final.csv` itself was still hand-built from an earlier round with no
regeneration script of its own, even though both `data/labels_scores/README.md` and
`configs/stage_manifest.yaml` already (slightly prematurely) called its derivation "mechanical." Fixed
properly rather than hand-editing around it: the script's Q5 entry is now a two-item list (original
TopKPattern-only config + the existing TopKPatternExtended config), so `--question 5`/`--all` regenerate
both `q5_final.csv` and `q5_final_extended.csv`. Regenerating against the renamed checkpoint reproduced all
526 rows' scores/labels byte-for-byte identical to the pre-rename file (verified by direct diff) — only the
`notes` column's path string changed. `configs/stage_manifest.yaml`'s `q5_final` entry gained the
`regenerate_script` field it had been missing. Also fixed: one prose line in
`taxonomy/2026-07-18_V1.0.0_baseline/taxonomy.yaml` (line 57) that named the checkpoint as its only date
anchor — restored the inline date (`~2026-07-21`) alongside the new checkpoint name, so the rename doesn't
silently drop that dating evidence.

**Re-verified clean after the pilot**: `grep -rl "2026-07-21_reporting_batch" .` finds nothing outside this
round's own historical note in `configs/stage_manifest.yaml` (documenting the rename event itself, not a
live reference); `pytest tests/ -q` — 11/11 passed; `scripts/regenerate_table4.py --stage final --check` —
all five questions match, including Q5's 91.9%/80.6%; `scripts/regenerate_table5.py --section all` and
`scripts/regenerate_q5_percentages.py --all-stages` both ran clean, with Q5's `q5_final`/`q5_final_extended`
rows still showing `detectors/reporting-batch` as the detector checkpoint and matching their reported
figures exactly (78.2%/75.0% and 91.9%/80.6%).

**This is a pilot, not yet applied repo-wide** — per Sonia's own framing ("rename one checkpoint end-to-end
... before I touch the rest"), the other 23 dated checkpoint directories and their cross-references are
untouched, awaiting her review of this one before the same pattern is applied to the rest of the repo. The
zip has not been rebuilt/redelivered for this round yet, for the same reason.

## New this round, part 17 (2026-09-18): the exemplar registry — merged into `data/exemplar_registry/`, no new artifact needed

Sonia asked directly about POPULATE.md step 6's own framing ("the enriched/really-mined exemplar registry
exists already in code... but isn't yet merged into the repo's own `data/exemplar_registry/`"): *"Que
dois-je faire au juste?"* Investigated before answering, rather than assuming — and the answer turned out
to be **nothing further from her**. The real, verified `EXEMPLAR_REGISTRY` (10 competencies, 27 exemplars)
already existed as delivered code in
`detectors/2026-09-17_semantic_backup_validation_executed/semantic_backup.py` — this repo's own most
current and most audit-clean semantic-backup checkpoint, where `audit_registry()` already reports zero
problems against the complete real chain for the first time in this project. The merge into
`data/exemplar_registry/`'s CSV+files format was mechanical, in the same spirit as this repo's existing
`scripts/build_submission_ids_from_batch_reports.py`.

**What was built**: `scripts/build_exemplar_registry.py`. It extracts the checkpoint's embedded
`competency.py`/`test_real_data.py`/`pw01_competencies.py`/`q2_competencies.py`/`report.py` (they exist
only inside the notebook's own source cells in this checkpoint, same extraction routine as
`scripts/regenerate_semantic_backup_v3_audit.py`), builds the real full competency model, and — for every
one of the 27 exemplars — calls the live structural resolver (`model.resolve()`) directly to get a
freshly-computed `final_score`, rather than trusting any previously-reported number. This run:
`audit_registry()` reports 0 problems, all 27 exemplars score `final_score=1.0000`.

**Result**: `data/exemplar_registry/exemplars.csv` and `code/*.py` now hold the full 27-exemplar registry
(replacing the earlier 2-competency/5-exemplar stub). Per-exemplar provenance (`mined` with an exact
submission ID where `semantic_backup.py`'s own comment names one — 2 `ConditionalCount` exemplars,
`correct_2_010`/`correct_2_016`; `mined` with the method/proportion documented but no individual filename
for 7 others; `hand-written` for 14; `hand-written (corrected)` for 4 that replaced originals
`audit_registry()` found scoring `final_score=0.00`) is transcribed directly from `semantic_backup.py`'s
own inline comments — nothing inferred. Full breakdown in `data/exemplar_registry/README.md` and
`provenance/detector-version-log.md`'s new entry for this round. `POPULATE.md` step 6 is now marked DONE.
`scripts/regenerate_table4.py --stage final --check` (5/5) and `pytest tests/` (11/11) both re-run clean
after this merge; Table 4 and the Q5 TopKPatternExtended delegation breakdown are untouched.

This still doesn't touch step 4 (the embedding train/test split indices) at all — that remains the only
genuinely unsupplied item in this repo, still dependent on Sonia's own Colab/Drive artifacts.

## New this round, part 16 (2026-09-18): the "19 vs 21/22 bug count" discrepancy — checked directly against the actual submission draft, and found moot

Sonia asked to see the correction proposed for this discrepancy before it was written. Checking which
document actually contains the disputed sentence, rather than assuming it still applies, changed the
answer: it does not need correcting, because it is not there.

`grep`-ing `Ver. 2026.8.23 IJIES_Format_paper.docx` (`/tmp/paper_check/paper.txt`, the same extracted text
already used for part 14's Table 4/5 cross-check) for "nineteen" returns nothing anywhere in the document.
Its §6 Discussion — read in full — consists of prose design principles (layering enforcement, coverage/
structure separation, composite-evidence propagation rules, the shared-library argument, etc.) with no
numbered bug-count narrative of any kind. `pdftotext` against every dated snapshot in `papers/` shows
exactly where the sentence does and doesn't live: present, verbatim, in `2026-08-04_...pdf` and in the
later-dated `2026-09-10_...pdf` (same "Structural_Competency_Extraction_Paper" internal lineage, not
reformatted for the journal); absent from the three 2026-08-05 snapshots and the 2026-08-08 snapshot
(already superseded stages); and — the one that matters — absent from the actual IJIES submission draft
confirmed by that file's own `docProps/core.xml` metadata to be created and modified 2026-08-23.

**Conclusion**: the discrepancy documented in the 2026-09-12 round (part 15 of that round's own numbering,
quoted above) was real and correctly reported against the paper draft being checked at the time. It simply
does not carry over to `Ver. 2026.8.23 IJIES_Format_paper.docx` — the bug-count narrative was dropped
entirely, not fixed, when that draft was reformatted into IJIES style. There is nothing to correct in the
paper Sonia is actually submitting. No file in this repository changed as a result of this check beyond
this documentation clarification (here and in `provenance/detector-version-log.md`); `POPULATE.md` is
unaffected since it never listed this item.

## New this round, part 15 (2026-09-18): the Refactory corpus license check — done, and a real misattribution corrected

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
- **A real documentation bug, found in the course of this check and corrected, not just the open item
  itself**: `data/submission_ids/README.md` previously attributed the corpus to "Ureel & Wallace" — no such
  citation exists anywhere in this project's own paper or sources. The paper's actual reference [3] is Hu
  et al., ASE 2019, as above. Origin of the "Ureel & Wallace" text is not established (not traceable to
  any real artifact in `provenance/detector-version-log.md`); flagged and corrected rather than silently
  carried forward.

**Practical conclusion, recorded in `data/submission_ids/README.md`'s own "On redistributing the corpus
itself" section**: LGPL-3.0, read literally, would not forbid redistributing the submission source code
itself. But applying a software library license to a corpus of student programming-assignment submissions
is not what LGPL-3.0 was written for, and no statement anywhere confirms the students themselves consented
to redistribution beyond the original research use. This repository therefore keeps its existing,
independently-already-conservative stance unchanged: it publishes `submission_id`s and derived
labels/scores only, never the students' own source code — exactly what `data/submission_ids/*.csv` and
every regeneration script already do. Nothing in those files or scripts changed as a result of this check;
it was a documentation-only round.

## New this round, part 14 (paper draft dated 2026-08-23, delivered and checked 2026-09-17): the finished paper's Table 4 AND Table 5 cross-checked — exact match

Sonia asked whether Table 4 is adequate to the paper draft (`Ver. 2026.8.23 IJIES_Format_paper.docx`,
the same file already on file as a Project doc). Direct comparison against `regenerate_table4.py`'s
fresh output: **exact match on all five rows, including sample sizes** — 99.5%/97.6% (768/575),
90.4%/74.3% (291/435), 94.0%/74.7% (546/308), 77.6%/45.9% (419/357), 91.9%/80.6% (418/108). Checked
further than asked: the paper's Table 5 (semantic backup layer, 90.6%/84.2% win rate, 74.1%/81.5%
worst-case, and all three SAME/CROSS/UNRELATED means to three decimals) is also an exact match to what
part 13 above independently reproduced by direct execution — the first time a supplied paper draft has
reported the post-scoping-fix numbers, and they agree with this repo's own independent run precisely,
not just narratively. No discrepancy anywhere in either table or their surrounding text. See
`provenance/detector-version-log.md`'s dedicated section for the full row-by-row and figure-by-figure
comparison.

## New this round, part 13 (no dating evidence, delivered 2026-09-17): the first genuinely EXECUTED semantic_backup_validation notebook, closing both gaps part 12 left open

A single-file upload — "here is the last version of `semantic_backup_validation` notebook," no conversation, no
dating metadata (named by delivery date; its content places it after part 12 regardless of its unknown
exact date). **The first genuinely executed copy of this notebook this project has ever received** — 10
code cells, all with real `execution_count` (1–10) and 9 with real output (genuine download progress for
`codet5p-110m-embedding`'s weights, real weight-loading logs) — every earlier copy was confirmed entirely
unexecuted.

It closes both of part 12's remaining gaps. First, `pw01_competencies.py`'s broken relative-import chain
is fixed (`from .core import ...` → `from competency import ...`) — confirmed by direct execution that
the real `test_real_data → pw01_competencies → q2_competencies` chain now imports cleanly in this
sandbox, which it could not do in part 12. Second, the `DelegatesUniqueness` scoping fix part 12's conversation
described as implemented but was grep-confirmed absent from part 12's own delivered code is now real,
present code (`DELEGATING_FUNCTION`/`runtime_scoped_exemplar()`), wired into both the live scoring path
and the validation script. Diff-confirmed: the embedded `competency.py`/`test_real_data.py` match this
repo's own **current HEAD** (`2026-08-08_q5_delegation_clustering_fix`) — unlike parts 11/12, whose
environment turned out to be running a pre-Q1-fix snapshot.

**Independently reproduced by direct execution in this audit**: `audit_registry()` is now fully clean
across all 10 competencies for the first time ever (every earlier round could only check 7-8 of 10). The
post-fix lexical numbers reproduce exactly — 1294/1428 (90.6%) win rate, 20/27 (74.1%) worst-case, **zero**
remaining `DelegatesUniqueness` failures (down from 5 of 12) — confirming the fix does precisely what it
claims. Three synthetic `TopKPatternExtended` structural regression cases (explicitly labeled in the
notebook as "structural, not semantic-similarity," changing no real corpus percentage) reproduce exactly.
The codet5p numbers (84.2% win rate, 81.5% worst-case) match part 12's conversation-reported "after fix" figure
exactly, now backed by real notebook output rather than a transcript — `huggingface.co` still blocked
here, so not independently re-run (`evidence: real_notebook_output`).

New checkpoint `detectors/2026-09-17_semantic_backup_validation_executed/`; new script
`scripts/regenerate_semantic_backup_v3_audit.py` (19/19 checks passing). **Table 4 and the Q5
TopKPatternExtended delegation breakdown are confirmed byte-for-byte unchanged.** Full test suite (11
tests) and both Table 4/Q5 regeneration scripts re-run clean. **The zip has still not been repackaged or
resent** — continuing to hold, now across three full rounds of this thread; a single notebook upload
isn't being treated as a signal the broader thread is complete.

## New this round, part 12 (content-dated 2026-08-08/09, delivered 2026-09-17): real corpus mining closes the exemplar-registry gap, and part 11's own open question is resolved with hard evidence

A second mine_exemplars batch — "A second version is here" — closed the real-corpus-mining gap part 11
left open. Real Refactory corpus mining (conversation-reported only; this sandbox has never had the corpus)
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
reproduced the conversation's reported codet5p numbers for that 8-competency subset (696/852 = 81.7% win rate,
16/21 = 76.2% worst-case) and, separately via the network-free deterministic lexical backend, the conversation's
reported numbers for the full 10-competency registry (1262/1428 = 88.4% win rate, 15/27 = 55.6%
worst-case) — the first time this project has independently reproduced a codet5p number from real cached
model output.

**Most notably, this round resolves — with hard evidence, not just reasoning — part 11's own genuinely
open question.** Diffing the delivered "Original files to load" against every checkpoint already in this
repo found `competency.py`/`test_real_data.py` byte-for-byte identical (0 diff lines) to
`detectors/2026-07-28_fixQ4`, and `report.py` byte-for-byte identical to
`detectors/2026-07-20_semantic_backup` — i.e. this is the ACTUAL `competency.py` the first mine_exemplars
round's development used, and it predates the 2026-08-05 Q1 fix, exactly as part 11 hypothesized but
could not confirm. The Q1 fix's own diff shows why the bare-while discrepancy existed: it added a brand
new `elif isinstance(node, ast.While):` branch to the `TEST` primitive detector (synthesizing `TEST`
evidence from a while loop's own condition) that fixQ4's version simply doesn't have. Reconstructing the
same bare-while GuardedInput shape against this now-supplied, actual `competency.py` scores exactly
`final_score=0.0` — matching the original claim precisely. Part 11's hypothesis paragraph is left
unedited in the log, per this project's evidence-preservation discipline; it was correct, and is now
proven.

Also confirmed by direct execution: the delivered "real model chain"
(`test_real_data.py -> pw01_competencies.py -> q2_competencies.py`) does not actually run in this
sandbox — `pw01_competencies.py` has unresolved relative imports (`from .core import ...`) to submodules
never supplied to this project — so `AccumulateThenCount`/`FunctionalUniqueCheck`/`DelegatesUniqueness`
remain unverifiable here, the same practical gap as part 11 but for a different, more specific cause. A
later scoping fix the same conversation describes as implemented and shipped (lexical 90.6%/74.1%) is
grep-confirmed absent from the delivered code, and three documents the conversation references as finalized were
not included in this batch — both noted, not assumed away.

New checkpoint `detectors/2026-08-09_mine_exemplars_real_corpus/`; new script
`scripts/regenerate_semantic_backup_v2_audit.py` (13/13 checks passing); forward-pointing update notes
added to part 11's own README/script/manifest entry rather than editing them in place. **Table 4 and the
Q5 TopKPatternExtended delegation breakdown are confirmed byte-for-byte unchanged** (re-ran both
regeneration scripts fresh — still 91.9%/80.6% and the same 57-catch breakdown). Full test suite (11
tests) still passes. **The zip has still not been repackaged or resent** — continuing to hold per
Sonia's standing instruction, now across two full rounds of this thread.

## New this round, part 11 (2026-08-07, delivered 2026-09-17): a real exemplar-registry bug found and fixed — Table 4 and Q5's breakdown deliberately untouched

Two reference documents arrived first (a sixth paper revision and a V2 methodology note, both dated
mid-August) describing a "finished" semantic-backup-layer validation and Q1-fix-driven retroactive
improvements to Q2/Q3/Q4's Table 4 figures — none of it backed by any supplied code or CSV, and one
internal numeric contradiction found against this repo's own already-verified Q5 delegation breakdown
(the new paper's "51 matches" vs. this repo's independently-verified 57). Sonia's explicit instruction:
keep Table 4 and the Q5 breakdown exactly as already logged and verified, since none of this is in the
final paper. Nothing in `table4_config.yaml`, `stage_manifest.yaml`, or any labels/scores CSV was
touched on account of those two documents — they're recorded as context only.

The real artifacts then arrived: `mine_exemplars.py` (the actual mining logic), a corrected
`semantic_backup.py`, `validate_semantic_backup.py`, and an unexecuted notebook, plus a dev-session
transcript — all dated 2026-08-07, a real, independently-verifiable checkpoint. Building the mining
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
likely predates the Q1 while-condition fix) — recorded as a hypothesis, not asserted as settled.

This round is explicitly **not yet** the "10 competencies, 27 exemplars, partly real-mined" state the
reference documents describe — the registry here is still 8 competencies/19 exemplars, all hand-written;
no real corpus mining has been run in any supplied artifact. **Table 4 and the Q5 TopKPatternExtended
delegation breakdown are confirmed byte-for-byte unchanged** (re-ran `regenerate_table4.py --check` and
`regenerate_q5_delegation_breakdown.py` fresh after this round's changes — both still report exactly
91.9%/80.6% and the same 57-catch breakdown as before). Full test suite (11 tests) still passes. Per
Sonia's own instruction from earlier in this round, **the zip has not been repackaged or resent yet** —
holding until this thread is confirmed complete, so it isn't redone multiple times.

## New this round, part 10 (2026-09-17): why the Drive folder layout differed — resolved directly by Sonia

Two open items (logged in the Q4/Q2 embedding round and the Q5 semantic-backup-layer round, part 9 below)
each found the same shape of discrepancy: an unexecuted "template" notebook using a Drive path with a
`refactory/` prefix, while the corresponding executed, real-output notebook used the same path without it
— and only the prefix-free version ever actually worked. Nothing supplied explained why. Asked directly in
this conversation, Sonia explained she worked in two different environments/Drive mounts across the
project; the `refactory/`-prefixed path belongs to whichever environment the template copies came from,
and every real execution ran from the other, prefix-free one — confirmed as the real, canonical layout.
This also corrects this repo's own earlier framing: the discrepancy isn't "Q2/Q4 vs. Q5," since the same
unexecuted/executed split recurs within Q5's own notebook pair too — it's template-environment vs.
execution-environment, consistently, across all three questions. No figure or finding changes; both
affected checkpoint READMEs and `provenance/detector-version-log.md` (new "A direct clarification from Sonia"
section) now record this, with the original "why" flagged as unexplained left in place per this project's
evidence-preservation discipline, plus forward-pointing notes.

## New this round, part 9 (2026-08-08, a later round than parts 6-8 above): embedding-guided clustering discovers a real Q5 delegation pattern — a code fix, and a methodological catch

Sonia supplied five files plus two pasted dendrogram images: "the clustering notebook, their results and
docs" — an unexecuted and an executed extension of the semantic-backup-layer notebook (now with a new §11
clustering section), the accompanying conversation export, a zip with a real code fix and its batch-validation CSV,
and a fifth paper checkpoint.

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
- **Independently verified, not just repeated from the conversation**: correct-side coverage 91.9% (384/418,
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
- **A striking, purely coincidental resemblance worth flagging directly**: this repo's own `VERSIONING.md`
  already records that an earlier, fabricated scaffold (built from the paper's prose alone, before any real
  checkpoint existed) guessed a Q5 "→79.7%→91.9%" trail and a fabricated `TopKPatternExtended`/`DELEGATES`/
  `SELF_RECURSIVE` competency. This round's real, independent work — with no possible awareness of that
  deleted guess — produced exactly those ingredients for real. Recorded in `VERSIONING.md`,
  `provenance/detector-version-log.md`, and this checkpoint's own README as a notable coincidence, explicitly
  **not** as vindication of guessing: every other specific claim in that same guessed version stayed wrong.

New stage `q5_final_extended` added to `configs/stage_manifest.yaml` and pointed to by `table4_config.yaml`
(alongside, not replacing, the original `q5_final`). New checkpoint folder
`detectors/2026-08-08_q5_delegation_clustering_fix/`; semantic-backup checkpoint extended with the two new
notebooks and chart; new paper checkpoint `papers/2026-08-08_..._after_clustering.docx`. Full test suite
(11 tests) and every regeneration script re-run clean with all of this in place — see
`provenance/detector-version-log.md`'s "Embedding-guided clustering discovers a real Q5 delegation pattern"
section for the complete writeup.

## New this round, part 8 (2026-09-15): a naming correction — both semantic-backup notebooks re-supplied, renamed

Sonia re-uploaded the two semantic-backup notebooks from part 7, renamed: "here the two files renamed as
the first ones, to keep the same nomination." Verified via `md5sum` that both are byte-identical to the
files already in this repository — a pure rename, no content change. The rename fixes exactly the
discrepancy part 7 had flagged: the executed notebook had originally arrived named
`Copie_de_semantic_backup_layer_validation.ipynb`, the reverse of the Q4/Q2 embedding round's own
convention (`Copie_de_...` = unexecuted there). It's now named
`semantic_backup_layer_validation_with_Results.ipynb`, and the unexecuted copy is now
`Copie_de_semantic_backup_layer_validation.ipynb` — matching the Q4/Q2 pattern exactly.

This repository's checkpoint files were renamed to match, and every reference to the old filenames
(`configs/stage_manifest.yaml`, the checkpoint's own README, `provenance/detector-version-log.md`) was updated.
The historical log entries describing the original uploads under their old names are preserved as written,
with forward notes added — not rewritten — per this project's evidence-preservation discipline. Full test
suite (11 tests) and all regeneration scripts re-run clean after the rename. **No figure, finding, or
evidence tier changed this round** — this was purely a filenames-and-cross-references correction, closing
an open flag rather than changing any reported number.

## New this round, part 7 (2026-09-15): the semantic backup layer's AUC finding upgraded to `real_csv` — raw CSVs, then the executed notebook itself

Two further uploads arrived in sequence for the same finding logged in part 6 below: first the two raw
per-run/per-file CSVs the notebook's own final cell was written to save
(`semantic_backup_bootstrap_summary.csv`, `semantic_backup_pooled_scores.csv`), then — after Sonia said
"I'll send the notebook with execution too" — the executed notebook itself
(`Copie_de_semantic_backup_layer_validation.ipynb`, described by Sonia as "the notebook after run").

Both were independently verified against every figure part 6 had logged as `conversation_reported_only`: per-run
AUC and group means recomputed directly from the raw 1,510-row CSV (all 10 runs `[OK]`), mean±SD across
runs (0.098 ± 0.039, exact match), pooled AUC across all runs (0.097, exact match), and the 80%-recall
threshold (0.719 at 99.7% FPR, exact match) — a new from-scratch (no-sklearn-dependency) AUC/ROC script,
`scripts/regenerate_semantic_backup_auc.py`, now backs this stage the same way the Q1-Q4 and Q4/Q2
embedding-taxonomy stages are backed. **No numerical discrepancy found anywhere.**

The executed notebook also surfaced one genuinely new fact: a previously-never-supplied
`codet5p-110m-embedding` sanity-check similarity pair for this notebook's own model load (related vs
related: 0.8399, related vs unrelated: 0.3820 — a real, usable separation, unlike `codebert`'s documented
anisotropy failure) — filling a gap the manifest had explicitly flagged as missing. It also confirmed
`novel_correct` n=43 / `genuinely_wrong` n=108, and the same kind of Drive folder-path fix already found in
the Q4/Q2 embedding round (`refactory/data/question_5/code` → `data/question_5/code`), diff-confirmed
between the two notebook copies (exactly one of 11 code cells differs).

**One thing did NOT resolve**: every code cell's `execution_count` is still `None` in the "after run" copy,
despite real, populated outputs — so the conversation's own "cell 13"/"cell 15" references still cannot be checked
against actual cell positions. Flagged as genuinely open, not resolved by the executed notebook's arrival —
consistent with this project's discipline of stating gaps plainly rather than assuming they've closed.

**Also flagged, not silently normalized**: this round's "Copie_de_" file is the *executed* copy — the
opposite convention from the Q4/Q2 embedding round, where "Copie_de_" meant the unexecuted, outputs-stripped
copy. Sonia's own message ("this is the notebook after run") was unambiguous, so it's logged as stated.

**Evidence-tier result**: `configs/stage_manifest.yaml`'s
`semantic_backup.backends.codet5p_bootstrap_novel_vs_wrong_auc` is now `evidence: real_csv`,
`status: REAL_INVERTED_RESULT_CSV_BACKED` — the strongest tier this project uses, the same tier as the
Q1-Q4 batch-validation results and the Q4/Q2 embedding-taxonomy cross-validation. The result itself is
unchanged from part 6 (a strongly inverted, deployment-relevant negative finding, not a usable filter as
designed) — what changed is how solidly it's backed, not what it says. Updated: this checkpoint's own
README, root `README.md`, `POPULATE.md` step 6, `docs/KNOWN_CAVEATS.md`, and
`provenance/detector-version-log.md` (new "Semantic backup layer validation — the raw CSVs, then the executed
notebook" section). See that log section for the complete writeup.

## New this round, part 6 (2026-08-08): the semantic backup layer's actual job gets its first real AUC — inverted — plus a new paper §7

Sonia supplied a new (unexecuted) notebook, an accompanying conversation with real pasted results, a third paper
revision, and a re-supply of an already-logged methodology doc.

- **The first real AUC/ROC number this project has ever produced for what the semantic backup layer is
  actually supposed to do** — separating genuinely-novel-correct submissions from genuinely-wrong ones,
  as opposed to validating an existing AST split. A redesigned notebook fixes the two problems earlier
  attempts left unresolved (a contaminated comparison group; single-draw instability) by using ALL
  wrong-labeled submissions as the negative class and bootstrapping the exemplar registry across 10 draws.
  Result, quoted from the conversation: bootstrap AUC mean 0.098 (SD 0.039), pooled AUC 0.097 across 1,510 scored
  pairs. **This is a strong result, but an inverted one, not a positive one** — an AUC near 0 (not near
  0.5) means genuinely-wrong submissions read as *more* similar to correct exemplars (~0.94–0.96) than
  genuinely-novel-correct ones do (~0.79–0.81), the reverse of what the layer's design assumes. A
  threshold catching 80% of novel-correct submissions would also flag 99.7% of genuinely-wrong ones — not
  a useable filter as built.
- **Confirmed entirely unexecuted, like the notebook itself, but the underlying finding is internally
  corroborated** (bootstrap mean and pooled AUC agree almost exactly, as expected from the same data) and
  matches the notebook's own described methodology exactly. One real, unresolved discrepancy flagged: the
  conversation's own cell numbers ("cell 13," "cell 15") don't cleanly map onto this notebook's 11 code cells
  under any simple counting convention — possibly extra cells were run in the actual session that this
  copy doesn't contain.
- `configs/stage_manifest.yaml`'s new `semantic_backup.backends.codet5p_bootstrap_novel_vs_wrong_auc`
  entry is `evidence: conversation_reported_only` — real, but not yet backed by the executed notebook or its raw
  CSVs. New checkpoint: `detectors/2026-08-08_semantic_backup_layer_validation/`.
- **A third same-week paper revision** (22p → 23p) adds a new §7, "The Semantic Backup Layer: Architecture
  Overview" — purely descriptive, deliberately deferring all validation claims (including this round's own
  AUC finding) to the still-unsupplied companion paper. Confirmed by direct diff against the prior logged
  revision: exactly one substantive change, everything else byte-identical. New files:
  `papers/2026-08-08_Structural_Competency_Extraction_Paper.docx`/`.pdf`.
- The re-supplied `Competency_Extraction_Methodology.docx` is confirmed, via `md5sum`, a byte-identical
  duplicate of the already-logged 2026-08-05 version — no new content.

See `provenance/detector-version-log.md`'s "Semantic backup layer validation" and "A third paper revision"
sections for the complete writeups.

## New this round, part 5: the Q4/Q2 embedding cross-validation raw CSVs supplied — evidence upgraded to `real_csv`

Sonia supplied `q4_embeddings_crossvalidation.csv` (1,470 rows) and `q2_embeddings_crossvalidation.csv`
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

## New this round, part 4 (2026-08-05, 18:02): the Q4 embedding result written into the published paper

A few hours after part 3 below, Sonia supplied a bare zip (no accompanying conversation this time) with a further
same-day paper revision: `Structural_Competency_Extraction_Paper.pdf`/`.docx`, dated by their own internal
metadata to 2026-08-05 18:02 UTC — about four hours after the `_final_22p.pdf` revision already in the
repo (14:05 UTC, part 2 below). Still 22 pages, no renumbering.

- **Confirmed genuinely distinct by direct `pdftotext -layout` diff, not a duplicate upload** — 390 raw
  diff lines, but almost all are pagination/line-wrap reflow from the added text pushing content down a
  page (table columns and page breaks shift; wording doesn't). Exactly three substantive content changes.
- **The Abstract and §5.6 now report the Q4 embedding-taxonomy result** (part 3's own 93.6% ± 2.1% figure,
  range 89.8%–95.9%) alongside Q5's 87.0% ± 2.3%, under a restructured "External validation of two
  taxonomic splits via code embeddings" section with separate "Q5: manual vs. builtin" / "Q4: BubbleSortPass
  vs. TopKPattern" subheadings. A third change updates a §7 Limitations sentence from "the manual/builtin
  check above" to "either taxonomic-split check above."
- **Every number in the new paragraph matches the already-verified figures exactly** — mean/SD/range,
  the 204/1,266 pooled support counts, and both precision/recall pairs. This round the paper is simply
  writing in a result already verified in part 3, not making a new claim — no discrepancy to flag, unlike
  the "526"/"35.7%" slips found two rounds ago.
- New files: `papers/2026-08-05_Structural_Competency_Extraction_Paper_final_22p_q4embedding_added.pdf`/
  `.docx`. `configs/stage_manifest.yaml`'s `q4_taxonomy_embedding_crossvalidation_10seed_pooled` entry now
  cites this paper section as a second, verbatim-matching corroborating source (evidence tier unchanged —
  still `real_notebook_output`, since the underlying source remains the notebook, not a new CSV).

See `provenance/detector-version-log.md`'s "The Q4 embedding result written into the paper" section for the
complete word-for-word diff.

## New this round, part 3 (2026-08-05, 17:40): the Q5 embedding-taxonomy methodology extended to Q4 and Q2

Later the same evening as the batch-run results below, Sonia supplied a conversation export and two notebooks (one
real and executed, one an unexecuted copy) extending the already-validated Q5 manual/builtin embedding
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
- **A real, diff-confirmed difference between the executed notebook and its "unexecuted copy" sibling, not
  narrated in the conversation**: the two notebooks differ in exactly two cells, both a Drive folder-path fix
  (`refactory/data/question_N/code` in the unexecuted copy → `data/question_N/code`, no `refactory/`
  prefix, in the executed version that actually worked). The conversation's own text warns this exact failure mode
  is possible ("the way Q1's did initially") but doesn't narrate this specific fix happening — the fix
  itself is real and diff-confirmed; why Sonia's Drive layout differs here from Q5's own is not
  independently checkable from anything supplied to this project.
- **Evidence status: `real_notebook_output`**, same tag and same reason as Q5's own 10-seed sweep — real
  execution output exists and is independently verified (`scripts/regenerate_q2q4_taxonomy_crossvalidation.py`,
  all checks pass), but the raw per-row CSVs the notebook saved to Drive were not supplied here. **Not the
  same experiment as `table5.q4_sortbykey_splits`**, which remains entirely unsupplied companion-paper
  scope — the manifest now says so explicitly on both entries.

New checkpoint folder: `detectors/2026-08-05_q2_q4_embeddings_crossvalidation/`. See
`provenance/detector-version-log.md`'s "Q4/Q2 embedding cross-validation" section for the complete
word-for-word verification writeup.

## New this round, part 2 (2026-08-05, ~13:00-14:00): the batch script was actually run — Q1-Q4 upgraded to real_csv, plus a real Q1 bug found and fixed

Same day as the driver-script checkpoint below (part 1), Sonia ran `run_q1_q4_batch_validation.py` against
her real Refactory dataset for the first time and supplied the four resulting CSVs, a code fix for a gap
the run surfaced in Q1, and the resulting updated methodology doc and paper. **This is the single biggest
evidence-tier event in this project to date**: every one of Q1-Q4's headline percentages moves from
`conversation_reported_only` to `real_csv` in the same round.

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
  `detectors/2026-08-05_q1_shared_binding_fix/`, canonical bug #22): a new `all_names` binding on every
  `TEST` evidence (every identifier referenced anywhere in the test), a new `ast.While`-condition branch in
  the TEST-detection function, and containment matching added to `SHARED_BINDING` — all three confirmed
  genuinely additive by direct diff against the pre-fix baseline already in this repo. Re-run coverage:
  99.5%/97.6%, zero regressions (conversation-reported; no pre-fix CSV was supplied to independently confirm this
  specific sub-claim).
- **A genuine error found and flagged in the fix's own code comment:** `test_real_data.py` says "364 of
  **526**" where it should say "364 of **383**" (526 is Q5's unrelated total-submission count, an apparent
  copy-paste carryover). Confirmed isolated to the code comment — the methodology doc's own canonical bug
  #22 entry correctly says 383.
- **A genuine "17 vs 19" reconciliation, derived independently from the CSV, not stated by any document:**
  every document states the genuine coverage gap as "19 files" without distinguishing pre/post-fix. The
  real post-fix CSV shows exactly 17 files still genuinely gapped (plus 1 unrelated parse-error row) — an
  exact match, category by category, once you notice the 2 "test-only-missing" pre-fix files are precisely
  the 2 the new `while`-condition detection fixed incidentally.
- **The "99.93% agreement / 1,342 of 1,343" claim (quoted in both the methodology doc and the paper)
  resolved as a `pandas` `NaN != NaN` comparison artifact, not a real difference** — this repo's own direct
  column-by-column diff of the real CSV finds `GuardedInput` and `LinearSearch` are byte-for-byte identical
  across all 1,343 rows (0 differences), a cleaner and stronger result than the "99.93%" figure that
  predates the conversation's own explanation of that artifact.
- **Two successive paper revisions this round**, both confirmed by direct `pdftotext -layout` diff: 20p →
  21p (Q1's finding added, new §5.3, a new Table 4 defect row) → 22p final (a brand-new §5.5 with a
  consolidated Table 4 across all five Refactory questions, triggering a full renumbering — old Table 4
  [defects] → Table 5, old §5.5/§5.6 → §5.6/§5.7 — confirmed fully consistent, no stale references
  remaining). New files: `papers/2026-08-05_Structural_Competency_Extraction_Paper_intermediate_21p.pdf`/
  `.docx` and `...final_22p.pdf`.
- **The methodology doc got its own, separate, more-detailed write-up** (new §5.2, a corrected §6.1
  overclaiming sentence, canonical bug #22, a new §9 Limitations bullet) — confirmed, per the conversation's own
  explicit exchange, to deliberately NOT include the paper's new consolidated table ("no changes to the
  methodology doc... the paper's the only place this table lives"). A minor rounding slip was also found
  and flagged in its own §5.2 text (100 − 64.2 = 35.8, not the "35.7%" quoted).
- **Submission-ID manifests populated for all five questions** (a previously entirely-unpopulated
  reproducibility-brief deliverable), mechanically projected from the same real batch-report CSVs.

See `provenance/detector-version-log.md`'s "Real batch-validation RESULTS for Q1-Q4" section for the complete
word-for-word verification writeup — every quoted claim, every diff, every reconciliation.

## New this round, part 1 (2026-08-05, ~09:00): a real, verified batch-validation script for Q1-Q4 — the driver script itself

Sonia supplied a conversation export and a real Python script, `run_q1_q4_batch_validation.py` — the first-ever
driver script for Q1-Q4's full-corpus batch validation, reusing the same already-verified
`batch_report.py` machinery that produced `topk_report.csv` for Q5. New checkpoint folder:
`detectors/2026-08-05_q1_q4_batch_validation/` (now updated, per "part 2" above, with the real run results
too).

- **Thoroughly cross-verified against files already in this repository, not taken at face value.**
  Confirmed true by direct diff: the `process_folders(..., function_name=...)` call signature matches
  the real `batch_report.py` exactly; Q1's original `q1_competencies.py` really did use whole-file
  resolution (no `function_name` argument in its own `__main__` block); the shared-`model` import chain
  across `test_real_data.py` → `q1_competencies.py`/`pw01_competencies.py`/`ex2_3_4_competencies.py` →
  `q2_competencies.py` is genuinely one consistent `CompetencyModel()` instance, not several diverging
  ones.
- **One claim in the accompanying conversation confirmed FALSE by direct read, not smoothed over:** the conversation
  states that both `pw01_competencies.py` and `q2_competencies.py` "define and resolve against a function
  literally named `unique_day`." Only `q2_competencies.py` does; `pw01_competencies.py` contains zero
  mentions of `unique_day` anywhere — it covers unrelated Ex1.2-1.6 exercises entirely. Logged plainly as
  a real error in the source conversation's own claim.
- **One real operational risk, flagged then confirmed moot by "part 2" above:** Q4's target list includes
  `SortByKey`, registered only in the `files_Fix_Q4` version of `test_real_data.py`. The real
  `q4_report.csv` (see above) confirms Sonia's live copy did have it registered — the risk did not
  materialize.

## New this round (2026-09-12): the real 10-seed sweep, resolved — and the paper updated a second time

Sonia supplied six files and three chart images: a conversation-export docx continuing the multi-seed thread, a
raw per-file CSV for the previously conversation-only "shuffled seed=0" run, two notebooks (one with real printed
execution output, one a code-identical outputs-stripped copy), a methodology-update zip, and a new version
of the paper PDF.

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
- **The previously conversation-only "shuffled seed=0" figure (85.2% manual/builtin) is now backed by a real raw
  CSV** and upgraded from `evidence: conversation_reported_only` to `evidence: real_csv` — independently
  recomputed this round, matching the prior conversation quote to full floating-point precision. Interestingly,
  this standalone run and the 10-seed sweep's own internal "seed 0" are close but NOT identical (flagged,
  not silently reconciled, in both the log and the manifest) — two different code paths evidently used
  slightly different shuffle state despite both being labeled "seed 0."
- **The published paper has been updated a second time**, confirmed by a full page-by-page diff against
  the prior PDF already in the repo: the Abstract and §5.5 no longer report the single-run 89.1%/0.98/0.77
  figures at all — they now report the 10-seed sweep's 87.0% ± 2.3% mean and pooled 0.94/0.75 precision
  figures instead. Every other page of the 20-page document is byte-for-byte unchanged. New file:
  `papers/2026-08-04_Structural_Competency_Extraction_Paper.pdf` (dated by its own internal PDF metadata,
  which is *earlier* than the prior paper's supplied date despite being the more recent revision by
  content — see `papers/README.md`'s note on this).
- **The internal methodology note has been substantially rewritten**, confirmed genuine via `python-docx`
  (127 paragraphs, not a mislabeled Markdown file like an earlier version). Its canonical bug table grew
  from 19 to 21 numbered entries, with two new ones (#20: Q3's `.insert()` detection gap; #21: Q4's
  `SortByKey` taxonomy correction) — both formalizing findings the log already carried as narrative-only.
  New folder: `methodology/` (see `methodology/README.md`, now also covering the 2026-08-05 revision
  above).
- **A precise discrepancy is sharpened, not resolved, by this round's evidence:** the methodology note's
  own 21-entry table has only #15 marked informational (20 structural + 1 informational = 21), while the
  paper's own Table 4 text still says "nineteen structural... a further two informational... = 21" — and
  the paper's Table 4 body text was not updated this round even though the methodology note gained two new
  (genuinely structural) entries. Flagged plainly as open; no document names the paper's stated second
  informational bug. **Clarified in part 16 (2026-09-18, below): this sentence is specific to the internal
  "Structural_Competency_Extraction_Paper" lineage and is absent from the actual IJIES submission draft —
  not an open item against what Sonia is submitting.**

This resolves what was the leading item in "Still-pending items" (the 10-seed sweep). See
`provenance/detector-version-log.md`'s "The real 10-seed sweep," "The published paper, updated again," and
"The internal methodology note, substantially rewritten" sections for full detail.

## New this round (2026-09-10 → 2026-09-12 bridge): the multi-seed instability finding (prior round)

Before the 10-seed sweep itself arrived, Sonia had supplied `multi-seed loop.docx`, documenting a single
real, executed alternate (shuffled) split showing the published 89.1% figure was not stable split-to-split
(dropped to 85.2%), plus the arithmetic resolving an earlier flagged precision discrepancy (0.92 vs. 0.98
— both correct, different denominators). That single alternate split is now also backed by a real raw CSV
(see above) and is superseded, for publication purposes, by the full 10-seed sweep.

## New this round (2026-09-10, third/fourth passes): AST-taxonomy embedding cross-validation — first real result, and the first paper update

Sonia supplied `ast_taxonomy_crossvalidation.ipynb`, its real output CSV, a conversation export, and the paper PDF
version that first added a new §5.5 reporting this single unshuffled split's 89.1% manual/builtin
agreement (86.1% 3-way, 45.5% novel recall) — the first embedding-related result in the project with
`evidence: real_csv` status, and the first confirmed section-numbering resolution (Case Study 5's Q3/Q4
content merged into §5.3, freeing §5.5 for the new subsection). Both of these are now superseded, for
publication purposes, by the second paper update and the 10-seed sweep documented above, but remain in the
repo as real, historically-important, independently-reproducible stages.

## Real Colab semantic-backup validation, still in progress (from an earlier round)

Sonia supplied a conversation export (`semantic_29.docx`) and two Colab notebooks documenting a real attempt to
validate the semantic-backup layer against real embeddings, outside the network-blocked sandbox. Key
findings, all in `detectors/2026-07-29to30_semantic_colab_validation/` (code + README) and
`configs/stage_manifest.yaml`:

- A real, executed anisotropy finding for raw `microsoft/codebert-base` run in Colab (0.958 related vs.
  0.964 unrelated — unrelated scores *higher*), independently diagnosed and cited (Ethayarajh 2019, Li et
  al. 2020, a `microsoft/CodeBERT` GitHub issue).
- A switch to `Salesforce/codet5p-110m-embedding` (real code, real `transformers`-compatibility fix), but
  **no valid similarity or AUC result yet** — the one comparison run under it is explicitly self-flagged,
  in the source conversation, as contaminated by a comparison-group confound.
- This is explicitly **not** the "10 train/test splits" companion-paper experiment already logged as
  pending — a separate, still entirely unsupplied item, and also not the same as the AST-taxonomy 10-seed
  sweep documented above (that sweep validates the structural taxonomy's own split; this thread validates
  the semantic-backup layer's own novel-detection capability).

## What's still not done (Sonia's artifacts live in Colab/Drive)

- The train/test split experiment for the Q4 `SortByKey` embedding work (`table5.q4_sortbykey_splits`) and
  the paper's own broader "10 train/test splits" companion-paper scope — still entirely unconfirmed
  against any real artifact. (This is distinct from the real, `evidence: real_notebook_output` Q5/Q4/Q2
  embedding-*taxonomy* cross-validations, which validate the AST taxonomy's own splits, not the
  companion-paper's own novel-detection/anomaly-scoring work — and also distinct from part 9's own
  embedding-*clustering* discovery, which is a discovery tool pointed at the structural detector, not a
  semantic-backup-layer result or a train/test-split experiment at all.)
- The companion paper itself (novel/recall-0.45 story, anomaly-detection reframing, the semantic-backup
  layer's own validation) — entirely unsupplied. The published structural paper's own Abstract/§7 both
  explicitly defer that work to it.
- A real, now `real_csv`-backed AUC exists for the semantic-backup layer's actual novel-vs-wrong job (0.097
  pooled, strongly inverted — see parts 6-7 above) — independently reproducible from the raw CSVs and
  corroborated by the executed notebook itself, but it's a negative/inverted finding, not a usable,
  deployable result. One anomaly remains genuinely unresolved even now: every code cell's `execution_count`
  is `None` in the executed notebook too, so the conversation's own "cell 13"/"cell 15" references still can't be
  checked against real cell positions. ~~A larger, real-mined exemplar registry (vs. this repo's small
  hand-written stub) also exists in code but is not merged.~~ — **done this round (part 17 below,
  2026-09-18): merged.** `data/exemplar_registry/` now holds the full, real 10-competency/27-exemplar
  registry, every `final_score` freshly re-verified against the live structural rules in this merge.
- ~~The "19 vs 21/22 bug count" discrepancy between the methodology note's own table and the paper's Table 4
  body text~~ — **clarified this round (part 16 below, 2026-09-18): moot for the actual submission
  draft.** The "nineteen structural defects... = 21" sentence exists only in the internal
  "Structural_Competency_Extraction_Paper" lineage (`papers/2026-08-04_...pdf`, still present verbatim in
  the later-dated `papers/2026-09-10_...pdf` snapshot of that same lineage) — it is absent entirely from
  `Ver. 2026.8.23 IJIES_Format_paper.docx`, the actual submission draft already cross-checked against
  Table 4/5 in part 14. That draft's §6 Discussion was rewritten as prose design principles with no
  numbered bug-count narrative at all when reformatted for IJIES. Nothing to fix in the paper Sonia is
  actually submitting.
- The `test_real_data.py` "364 of 526" comment typo (should read 383) — a real, harmless, source-level
  error, flagged this round, not yet corrected in Sonia's own working copy (this repo preserves the file
  as supplied, per its own evidence-preservation discipline, and documents the correction in the
  checkpoint's README rather than silently editing the artifact).
- ~~Why Sonia's Drive layout for Q2/Q4's embedding-crossvalidation notebook differs from Q5's own
  (`data/question_N/code` vs. `refactory/data/question_N/code`)~~ — **resolved this round (part 10 above)**:
  per Sonia, stated directly, this reflects two different working environments used across the project;
  `data/question_N/code` (no `refactory/` prefix) is the real, canonical layout, and the same
  template-vs-execution split recurs within Q5's own notebook pair too, not just between Q5 and Q2/Q4.
- ~~Refactory corpus license check (can redistribute submission IDs/labels?)~~ — **resolved this round
  (part 15 below, 2026-09-18)**: confirmed LGPL-3.0, repository-wide, no dataset-specific terms; this
  repository's existing IDs-and-derived-scores-only stance is kept regardless.
- Commit-SHA tracking dropped from the scheme entirely per Sonia's explicit choice (no granular history
  exists) — replaced by checkpoint label + real date throughout.

## New this round, part 21 (2026-09-20): real train/test split indices supplied and merged — turned out to be the same experiment as the already-real Q4/Q5 taxonomy embedding cross-validations, not a distinct one

Sonia supplied `split_manifests_q4_q5.zip`: real `split_manifest.json` + `split_NN_{train,test}_ids.txt`
files (seeds 00-09, 70/30) for `q4_sortbykey` and `q5_topk`, from her real Colab/Drive notebooks —
`POPULATE.md`'s last entirely-unsupplied item.

A conflict surfaced before anything was written: several places in this repo (`POPULATE.md` step 4,
`stage_manifest.yaml`'s `table5:` notes, `README.md`'s file table) repeatedly stated this was a *distinct,
still-unsupplied companion-paper experiment* (likely novel-detection/anomaly-scoring), separate from the
already-real `q4_taxonomy_embedding_crossvalidation_10seed_pooled`/`q5_taxonomy_embedding_crossvalidation_10seed_pooled`
stages. But the supplied files traced to the *same* two notebooks backing those stages, same source
report CSVs, same split code, same reported mean/SD — and for Q4, the supplied evidence CSV was
byte-for-byte identical to a CSV already in this repo. Rather than pick an interpretation silently, this
was surfaced to Sonia directly with the concrete evidence; she confirmed it is the same experiment, and
the repeated "distinct companion-paper" framing was wrong.

**What changed**: `data/splits/q4_sortbykey/` and `data/splits/q5_topk/` now hold the real files.
`scripts/regenerate_splits.py` was rewritten (the old version assumed sklearn's stratified split and a
single seed, neither matching the real plain-pandas seeded-shuffle method) and now independently
reproduces every recorded split, for both experiments, all 10 seeds, entirely from files already in this
repo. `configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits`/`q5_topk_splits` PENDING fields are
filled with real values. Every place that previously asserted the "distinct companion-paper" framing —
four spots in `stage_manifest.yaml` alone, plus `POPULATE.md`, `README.md`, `VERSIONING.md`,
`data/splits/README.md` — got an appended `UPDATE (2026-09-20):` correction; the original text was kept,
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
already were throughout. **Part 17 (2026-09-18) closes this thread**: that same registry is now actually
merged into this repo's own `data/exemplar_registry/`, so POPULATE.md step 6 is DONE, not partial. Still
outstanding on this same axis: the codet5p numbers remain `real_notebook_output` rather than independently
re-run (`huggingface.co` still blocked here), and the real-corpus scan counts themselves stay conversation-reported
only (no corpus ever supplied here) — neither blocks the merge itself, since the merge only needed the
registry's own code, not those separate results. **The only item left genuinely unsupplied in this entire
repository is POPULATE.md step 4** (the embedding train/test split indices) — everything else on this list
is either done or, for the codet5p/real-corpus-scan items just above, a real, honestly-labeled negative or
incomplete finding rather than missing data. The project is explicitly open-ended ("This work will be
continued with other versions") — expect further checkpoints in future rounds, including step 4's own
artifacts and the still-outstanding companion-paper items, whenever Sonia supplies them.

**Update (2026-09-20, part 21): the paragraph above is now stale.** `POPULATE.md` step 4 is done — real
split-index files were supplied and merged, and turned out to be the same experiment as the already-real
Q4/Q5 embedding-taxonomy cross-validations, not the "still entirely unsupplied," separate companion-paper
train/test-split experiment described two paragraphs up. Every item on `POPULATE.md` is now done. What's
genuinely still open in this repository: two unrelated semantic-backup-layer backend items
(`jina_v2_code`, `codet5p_110m_embedding` — see part 21 above), and whether to create a git commit/remote
for the actual GitHub push. The project remains explicitly open-ended; further checkpoints may still
arrive in future rounds.

## Part 22 (2026-09-21): narrative "chat" references removed; `chat_reported_only` evidence label renamed to `conversation_reported_only`

Sonia asked to remove references to the word "chat" from `detector-version-log.md` and the other narrative
documents. Scoped first (12 real on-disk filenames contain "chat" and must stay untouched; the
evidence-grading vocabulary in `configs/stage_manifest.yaml` uses `chat_reported_only` as a controlled
value, not just prose), then asked via AskUserQuestion whether the evidence label itself should be renamed
too — Sonia: "Rename the evidence label too." Reworded "chat" -> "conversation" in prose across 29
`.md`/`.yaml` files plus 7 script docstrings (528 + 26 replacements), and renamed `chat_reported_only` ->
`conversation_reported_only` everywhere it appears (16 occurrences in `configs/stage_manifest.yaml`, same
meaning: still the weakest evidence tier). All 12 real filenames and 2 verbatim historical-filename
citations (documents this project was told about but never received the raw file for) were masked before
the rewrite and confirmed byte-identical afterward. Full fresh-venv verification passed: YAML parses, all
`scripts/regenerate_*.py` run clean with unchanged numbers, `pytest tests/ -q` 11/11. Full detail in
`provenance/detector-version-log.md`'s own entry for this round.
