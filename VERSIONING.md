# Versioning scheme

Two independent axes are versioned, because they change for different reasons and at different times:

- **Taxonomy** (`taxonomy/<checkpoint>/`) — changes when the *set of target competencies or their
  composition rule* changes (a competency is added, split, renamed, or its `ANY`/`ALL` composition is
  redefined). A pedagogical judgment call (see `taxonomy/DESIGN_NOTES.md`), not a bug fix.
- **Detector** (`detectors/<checkpoint>/`) — changes when the *implementation* changes: a primitive's
  matching logic, a structural constraint's traversal, or the scoping mode used when running detectors
  over a submission.

A reported number is a function of both, plus the scoping mode. `configs/stage_manifest.yaml` pins all of
these per reported number.

## How checkpoints are named and dated

**There is no granular commit history for this project.** Sonia saved periodic checkpoints — zips,
standalone files — rather than committing incrementally, so this repo cannot cite commit SHAs and does
not pretend to.

Every checkpoint folder is named with a **stable, date-free kebab-case slug of Sonia's own label for
it** (e.g. `fixq4`, matching the zip filename `files_Fix_Q4.zip`) — not, as an earlier version of this
repo did, `<real-date>_<label>`. **Updated 2026-09-19**: the date prefix was dropped from every
checkpoint folder name (`detectors/`, `taxonomy/`), once this repo's actual publication target was
confirmed to be a public GitHub repository read by reviewers — a stable slug is what a reviewer can cite
in a footnote or link to in an issue without the link going stale the moment a date turns out to need
correcting (this has already happened once here: `reporting-batch`'s own real date was originally dated
2026-07-21 and is only inferred, "~2026-07-21", per its own `README.md`). **No dating evidence was lost
by this rename**: every real date this repo has ever established still lives exactly where it lived
before — each checkpoint's own `README.md` (or, for the four taxonomy-only snapshots, each
`taxonomy.yaml`'s header comment) states its real date in prose, independent of the folder name;
`detectors/CHANGELOG.md` and `taxonomy/CHANGELOG.md` carry it in an explicit "Real date" column; and
`../provenance/detector-version-log.md` is the full, original audit trail every one of those dates was
established from (zip-preserved per-file modification timestamps, a conversation-export's own date marker, or
bounding by direct diff against neighboring checkpoints — never assumed). When this repo is pushed to
GitHub, **git tags/commits, honestly dated at actual push time and never backdated**, become the citable
version mechanism going forward — the folder slugs are what code and docs reference internally; the git
history is what makes "which exact state of this repo produced Table 4" answerable the normal, git-native
way, without re-encoding dates that were never commit dates into the tree itself. See
`../provenance/detector-version-log.md`'s "Checkpoint-naming pilot rename" and subsequent full-rollout entries
for exactly how this was done and re-verified (every regenerated file, including the CSVs downstream of a
renamed checkpoint, diffed byte-for-byte against its pre-rename content: only the checkpoint-path strings
in `notes` columns changed, never any score or label).

The full citation for every date, and for every claim about what changed at each checkpoint, lives in
**`../provenance/detector-version-log.md`**, which is the actual audit trail this repo is built from. This
file, `detectors/CHANGELOG.md`, and `taxonomy/CHANGELOG.md` are compressed indexes into that log, kept
deliberately short so they don't drift out of sync with it — when in doubt, the log wins.

## Detector checkpoints (chronological)

See `detectors/CHANGELOG.md` for the full table. In order: `v1.0.0` →
`ex1-taxo` → `ex2-3-4` → `semantic-backup` (a parallel, opt-in
extension, not a version of the core detector) → `v1.2.0` → `reporting-batch`
→ `fixq2` → `q2-3rd-strategy` → `enforcement` → `fixq4`.

## Taxonomy checkpoints

See `taxonomy/CHANGELOG.md` for the full table: `v1.0.0-baseline` →
`q2-3rd-strategy-uniquecheck` (Q2) → `enforcement-linearsearch` (Q1) →
`fixq4-sortbykey` (Q3, Q4). Q5's `TopKPattern` never received a taxonomy-level correction —
only detector-level fixes (the missing-removal fix, then the level-layering lifting-wrapper refactor).

## What's real vs. what's still narrative-only

Only Q5 has a real, supplied batch CSV (`detectors/reporting-batch/topk_report.csv`, 526 rows)
backing its reported figures (83.0% unscoped → 78.2% scoped; a further, smaller unscoped shift to 82.1%
after `TopKPattern`'s later level-layering refactor, per the 28/07 methodology note — traced to the same
class of resolver limitation as `BubbleSortPass`'s own unfixed exception). Q1 (1,343/1,342, zero
mismatches), Q2 (85.2%/0.7%/4.5%/90.4%), Q3 (93.6%→94.0%), and Q4 (13.1%→64.4%→77.6%) are all real,
multiply-corroborated figures — each stated identically across 2-3 independent documents — but **none of
them has a supplied batch script or CSV**, unlike Q5. `configs/stage_manifest.yaml` marks this explicitly
per stage rather than implying every number is equally reproducible.

**Update (2026-09-20): `data/splits/` and the `table5:` block are now populated with real data** —
real split-index files (seeds 00-09, 70/30) were supplied from Sonia's Colab/Drive artifacts and
independently verified against this repo's own source CSVs via `scripts/regenerate_splits.py --check`.
They turned out to be the same experiment as the already-real Q4/Q5 embedding-taxonomy cross-validations
elsewhere in `configs/stage_manifest.yaml`, not the distinct, still-unsupplied experiment this file
previously described below — see `data/splits/README.md` for the full evidence trail. Original text, kept
for history: "`data/splits/`, and the embedding-based ('Table 5') validation in
`configs/stage_manifest.yaml`, are not yet populated with real data — per Sonia, those artifacts exist in
Colab/Drive and will be supplied in a later round; the structure is kept in place with explicit `PENDING`
markers rather than placeholder numbers, so nothing in this repo currently claims to be evidenced when it
isn't."

## Corrected from an earlier, guessed version of this file

An earlier version of this file (and of `configs/stage_manifest.yaml`) was generated by inference from
the paper's own prose, before any of Sonia's real checkpoints, conversation exports, or paper drafts had been
supplied. That version invented a clean `v1.0.0`→`v1.4.0` semver ladder that does not correspond to
anything Sonia actually saved, and — more seriously — stated specific numeric results that do not appear
in any real artifact gathered since: a Q1 figure of "76.8% → 99.5%", a Q5 figure of "→ 79.7% → 91.9%", a
fabricated `TopKPatternExtended` competency with `DELEGATES` + a nonexistent `SELF_RECURSIVE` primitive,
and an entire Table-5 embedding-validation block (codet5p/lexical win-rates 0.936/0.870/0.906/0.842, etc.)
with no basis in any supplied artifact. This is recorded here — rather than silently deleted — because a
reviewer checking this repo's history should be able to see that these numbers were once present and were
removed for lack of evidence, not merely absent by oversight. `detectors/CHANGELOG.md` and
`taxonomy/CHANGELOG.md` note the specific corrections inline where they replace a guessed claim.

**A striking postscript, worth recording precisely rather than treated as vindication.** In a much later
round (2026-08-08, folded into this repo well after the correction above was already written), real,
independent work — an embedding-clustering discovery pass over Q5's own uncharacterized "novel"
population, with no possible awareness of this deleted guess — produced a real `TopKPatternExtended`
competency, built with a real `DELEGATES` usage and a real new `SELF_RECURSIVE` primitive, raising Q5's
correct-side coverage from a real 79.7% to a real 91.9% — matching the guessed Q5 figure and fabricated
competency name above almost exactly. This is flagged as a notable coincidence, not as evidence the
guessing methodology was sound: every *other* specific claim in the same guessed version (the
`NESTED`/`SEQUENTIAL`/`SHARED_BINDING` mechanism guesses, the Table-5 embedding-validation numbers, the
semver ladder) remained wrong once real evidence arrived, and the real fix's wrong-label figure (80.6%)
and the intermediate 82.1% whole-file stage were never guessed at all. See
`detectors/q5-delegation-clustering-fix/README.md` and `provenance/detector-version-log.md` for the
complete, independently-verified writeup of the real finding.

## Note on commit SHAs

Earlier drafts of this scheme carried `<<FILL: commit sha>>` placeholders throughout. These have been
removed rather than left open, since no commit history exists to eventually fill them from — checkpoint
label + real date (established as described above) is this project's actual provenance mechanism, and is
what every file in `detectors/` and `taxonomy/` now cites instead.
