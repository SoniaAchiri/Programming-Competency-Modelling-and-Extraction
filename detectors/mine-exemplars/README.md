# 2026-08-07 — mine_exemplars: expanding and auditing the semantic backup layer's exemplar registry

*Note (2026-09-21): the `/home/claude/refactory` path below is the historical record of what this round's
script actually hardcoded and what this project's own sandbox checked for — not something to run against
today. The checked-in `mine_exemplars.py` in this repository now resolves the corpus location portably
(`REFACTORY_ROOT` env var, or a path relative to the script's own location); see
`provenance/detector-version-log.md`, "Hardcoded `/home/claude/refactory` sandbox path made portable."*

Sonia's message: "here are a version of files," uploading `files_semantic_mine_factory.zip`
(`mine_exemplars.py`, `semantic_backup.py`, `validate_semantic_backup.py`,
`semantic_backup_validation.ipynb`) and `mine_exemplars.docx` (a development-session transcript
describing what was built and why).

**Dating**: the zip's four files share an identical internal modification timestamp,
2026-08-07 19:32; `mine_exemplars.docx`'s own `dcterms:created` is 2026-08-07T19:34:00Z, two minutes
later — a same-day, tightly-sequenced chain, same convention as every other round in this project.
This is a real, dated checkpoint **distinct from, and earlier than**, the "final registry" (10
competencies, 27 exemplars, partly real-mined) that `Structural_Competency_Extraction_Paper_v1_2.docx`
(2026-08-08) and `Competency_Extraction_Methodology_V2.docx` (2026-08-13) already describe as
finished — see "What this is not yet" below.

## What this is

The exemplar registry backing the semantic-similarity layer (`semantic_backup.py`) had, until this
round, a real and previously-documented limitation: most competencies had exactly one hand-written
exemplar (unscoreable in a held-out test — nothing to hold it out against), and none had ever been
run through the actual structural resolver to confirm they really satisfy the competency they claim to
represent. This round is the first real work on fixing both problems, plus the first real
implementation of mining exemplars from actual submissions instead of hand-writing them.

**What's here:**

- `semantic_backup.py` — the exemplar registry expanded from ~5 exemplars (2 competencies) to **19
  exemplars across 8 competencies** (Swap, Accumulation, ConditionalCount, AccumulateThenCount,
  GuardedInput, SelectionStep, FindExtremumBuiltin, TopKPattern — each now with 2-3 exemplars, all
  still hand-written), plus a new `audit_registry(model, registry=None)` function that resolves every
  exemplar against the real structural rules and flags anything scoring below `final_score >= 0.999`,
  including anything not registered at all in the given model (reported as a warning, not silently
  skipped).
- `mine_exemplars.py` — the real mining logic: for a configured competency, scan a corpus glob, keep
  only submissions the structural resolver already scores `final_score >= 0.999` on, deduplicate via
  an AST-level canonical key (every identifier alpha-renamed to `v0, v1, ...` in order of first
  appearance, so naming-only variants collapse to one representative), then take a capped, seeded
  random sample across the surviving unique shapes. Deliberately never uses an embedding to pick its
  own training data — the deterministic structural rules stay the sole selection criterion, avoiding
  circularity with whatever gets validated against the result.
- `validate_semantic_backup.py` — the discriminative-power check: for every competency with ≥2
  exemplars, each exemplar is held out and compared against SAME (its own competency's remaining
  exemplars), CROSS (other competencies' exemplars), and UNRELATED (three deliberately irrelevant
  snippets — string formatting, file I/O, a `Point` class). Reports both "worst-case correct ranking"
  (best SAME beats worst of every other comparison — strict, near all-or-nothing at this registry
  size) and "pairwise win rate" (the standard AUC/Mann-Whitney statistic across every SAME-vs-OTHER
  pair — the metric actually trusted). New `--registry-file` (load a mined JSON registry instead of
  the hand-written one) and `--compare-registries` (run both side by side) flags, connecting it to
  `mine_exemplars.py`'s `--out` file for the first time.
- `semantic_backup_validation.ipynb` — 16 cells / 8 code cells, **confirmed entirely unexecuted** by
  direct JSON inspection (every code cell has `execution_count: None` and no outputs). No real
  notebook-run figures exist for this specific checkpoint; everything numeric here comes from the
  dev-session transcript and this repo's own independent execution below.
- `mine_exemplars_chat.txt`/`.docx` — the development-session transcript this round's narrative is
  drawn from.

## A real bug found and fixed: both original GuardedInput exemplars were never real examples of GuardedInput

Building `mine_exemplars.py` forced every hand-written exemplar through `model.resolve()` for the
first time — something the original registry had never been checked against. That surfaced a real
integrity bug: **both of GuardedInput's original exemplars scored `final_score=0.0`** under the actual
structural resolver, not the 1.0 their author had assumed. Root cause, per the transcript: the
original pair used a bare `while n <= 0: n = input(...)` shape with no explicit `if` statement, and
(in whatever `competency.py` the developer was running against at the time) GuardedInput's rule
required a `TEST` (an `if`) genuinely nested inside the loop — a bare `while` condition did not
register as `TEST` evidence at all. Fixed by replacing both exemplars with a shape that does contain
an explicit nested `if` (see `semantic_backup.py`'s `GuardedInput` entry, "CORRECTED" comment), and
adding a second, differently-shaped exemplar (a yes/no retry loop with no running total) for genuine
diversity.

**Independently re-verified in this audit, not just repeated from the transcript.** Running the
delivered `semantic_backup.py` and `test_real_data.py` against the closest-dated real competency model
this repo has (`../q1-shared-binding-fix/test_real_data.py`, the checkpoint immediately
preceding this round's own 2026-08-07 date):

- `audit_registry(model)` returns exactly one flagged competency, `AccumulateThenCount` (every
  exemplar reported as "not registered in the given model — cannot verify, don't assume it's fine") —
  everything else, including the corrected GuardedInput pair, is clean. Exact match to the transcript's
  own claim.
- Both corrected GuardedInput exemplars individually score `final_score == 1.0` against the real
  resolver — confirmed directly, not assumed.
- `validate_semantic_backup.py --backend lexical` reproduces the transcript's own reported pairwise win
  rate **exactly**: 470/542 (86.7%), verdict "strong discriminative power." The worst-case
  correct-ranking figure (9/19, 47.4%) is not quoted anywhere in the transcript — it's an
  independently-produced number from this same run, not merely a check against a stated figure. See
  `../../scripts/regenerate_semantic_backup_exemplar_audit.py`, which reproduces all of this
  end-to-end and passes cleanly.

**A genuinely open question, found while trying to verify the root-cause diagnosis precisely, not
resolved by guessing.** Reconstructing the described "original, broken" GuardedInput shape (a bare
`while <comparison>:` loop with a reassignment inside, no nested `if` — tried in three separate
phrasing variants) and resolving it against this repo's own closest-dated real `competency.py`
(q1-shared-binding-fix) scores `final_score == 1.0` in every variant tried, **not 0.0**.
This is not a contradiction of the transcript's finding — the actual original exemplar text was never
supplied (it was already replaced in the delivered file), so this is a reconstruction, not the literal
original — but it is a real, precisely-characterized discrepancy worth recording rather than silently
smoothing over. The most likely explanation, consistent with this project's own already-documented
"two different working environments" pattern (see `provenance/detector-version-log.md`'s "A direct
clarification from Sonia," 2026-09-17): the `competency.py` this mine_exemplars session was actually
running against most likely predates the Q1 `SHARED_BINDING`/`all_names` fix (2026-08-05), which is
what added `while`-condition `TEST` synthesis in the first place (`detect_test` now also walks
`ast.While` nodes) — under the *current*, most-recent competency.py, a bare `while` condition already
registers as `TEST` evidence, so the specific bug as described would no longer reproduce. This is
recorded as an explained-but-unconfirmed hypothesis, not a settled fact — the exact `competency.py`
version actually used for this round's development was never supplied.

**UPDATE (2026-08-09 content / 2026-09-17 delivery) — this hypothesis is now confirmed with hard
evidence, not just reasoned about.** A second mine_exemplars batch supplied the actual
`competency.py`/`test_real_data.py`/`report.py` files used for this original round's development
(`../mine-exemplars-real-corpus/original_files_used_this_round/`), and they are
byte-for-byte identical (0 diff lines) to `../fixq4/competency.py` and
`../fixq4/test_real_data.py` — a competency.py that indeed predates the 2026-08-05 Q1 fix.
Direct execution confirms the mechanism precisely: fixQ4's `TEST` primitive detector only synthesizes
evidence from `ast.If` nodes; the `elif isinstance(node, ast.While):` branch that lets a while loop's
own condition register as `TEST` evidence was added specifically by that Q1 fix. Reconstructing the
same bare-while GuardedInput exemplar and resolving it against this exact, now-supplied fixQ4-era
`competency.py` scores `final_score == 0.0` — exactly as originally claimed. The hypothesis above is
left in place rather than deleted, per this project's evidence-preservation discipline; it was correct,
and is now proven rather than merely plausible. See
`../mine-exemplars-real-corpus/README.md` and
`../../scripts/regenerate_semantic_backup_v2_audit.py` for the full re-verification.

## AccumulateThenCount: explicitly flagged as unverified, not assumed fine

The transcript is explicit and this audit confirms it directly: `AccumulateThenCount` cannot be
audited from this project's own supplied files. It is registered in `q2_competencies.py`, which
imports its model from `pw01_competencies.py` — neither file has ever been supplied to this project.
`audit_registry()` reports this plainly (a `cid` not found in the given model is flagged as a warning,
not silently skipped) rather than assuming the exemplars are fine because no other check caught a
problem. `mine_exemplars.py`'s own `CONFIG` dict leaves both `AccumulateThenCount` and `Accumulation`
as explicit `TODO` entries for the same reason — their real corpus source folders were never confirmed
rather than guessed at.

## What this is not yet

This round is real, independently-executed progress — not the finished state the later paper
(`Structural_Competency_Extraction_Paper_v1_2.docx`) and methodology note
(`Competency_Extraction_Methodology_V2.docx`) describe. Specifically, and worth stating plainly so
nothing here is over-read:

- The registry is **still entirely hand-written** — 8 competencies, 19 exemplars — not the "10
  competencies, 27 exemplars, partly real-mined from the Refactory corpus" the later documents
  describe as final. `mine_exemplars.py`'s mining logic exists and its core canonicalization/dedup
  mechanism is independently unit-verified in this audit (an alpha-renamed-only pair collapses to one
  key; a genuinely different function body does not), but it has never been run against the real
  corpus in this round — no `mined_exemplars.json` output file exists in this upload, `CONFIG` only
  covers 6 of the eventual competencies, and this sandbox has no Refactory corpus available either
  (checked directly: `/home/claude/refactory` does not exist here).
- The lexical win rate here (86.7%) is a different, earlier number than the later paper's final
  90.6% — the paper's own text attributes part of that gap to a harness bug (single-exemplar
  competencies counted in the denominator, capping results near 40% before the fix) and a
  scope-mismatch bug (DelegatesUniqueness) that this round's code does not yet contain any trace of
  fixing. Both numbers are real; they are not the same measurement.
- The codet5p backend was not run and could not be independently checked in this audit either —
  `huggingface.co` is confirmed blocked from this sandbox too (a direct request returns a 403 at the
  network proxy), consistent with every earlier round of this project.
- **Per Sonia's explicit instruction, nothing in this round touches or changes Table 4 (the five
  Refactory questions' headline coverage) or the Q5 `TopKPatternExtended` delegation breakdown
  (91.9%/80.6%, the 57-catch breakdown already logged) — both stay exactly as previously verified.**
  This checkpoint is scoped entirely to the semantic backup layer's exemplar registry (Table 5 /
  companion-paper territory), which is a separate axis from Q1-Q5's own structural coverage.

See `../../provenance/detector-version-log.md` for the complete writeup and
`../../scripts/regenerate_semantic_backup_exemplar_audit.py` for the reproducible check.
