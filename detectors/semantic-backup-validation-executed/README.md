# Delivered 2026-09-17 — "here is the last version of `semantic_backup_validation` notebook": a genuinely executed run, the import chain fixed, and the scoping fix finally shipped as real code

Sonia's message this round: "here is the last version of 'semantic_backup_validation' notebook" — a
single `.ipynb` upload, no accompanying conversation transcript, no docx metadata (it's a raw notebook, not a
docx export). **There is no independent dating evidence for this file beyond the delivery date** — this
checkpoint is named by delivery date, not content date, unlike every other checkpoint in this repo. What
the content itself establishes, precisely: it embeds this repo's own current-HEAD structural model
(`detectors/q5-delegation-clustering-fix`) and the full 10-competency/27-exemplar registry
from the second mine_exemplars round (content-dated 2026-08-08/09) — so it chronologically postdates
both, whatever its exact date is.

Per Sonia's standing instructions this session, **Table 4 and the Q5 TopKPatternExtended delegation
breakdown are untouched by this notebook** (nothing in it touches either), and **the zip is still being
held** — this single-file upload isn't treated as a signal that the broader mine_exemplars/semantic-backup
thread is complete.

## This is the first GENUINELY EXECUTED semantic_backup_validation.ipynb this project has ever received

Every earlier copy of this specific notebook (the first and second mine_exemplars rounds) was confirmed,
by direct JSON inspection, to be entirely unexecuted — a template, `execution_count: None` on every code
cell, no outputs. **This one is different**: 20 cells total, 10 code cells, all 10 with `execution_count`
set sequentially 1 through 10, 9 of 10 with real outputs (the exception, cell 19, downloads a zip and
produces no stdout, which is expected). The outputs include things that are extremely hard to fabricate
convincingly — real `pip install` output, real Colab-style download progress bars for
`Salesforce/codet5p-110m-embedding`'s tokenizer/config/weight files (`pytorch_model.bin: downloading
bytes: 25% 108M/439M ...`), real `transformers`/`huggingface_hub` deprecation and rate-limit warnings, and
real weight-loading progress bars.

## Two real fixes this notebook makes, confirmed by direct inspection and execution

**1. The broken `pw01_competencies.py` import chain (identified in the second mine_exemplars round) is
fixed.** That round's delivered `pw01_competencies.py` used package-relative imports
(`from .core import ...`, `from .base_competencies import model, show`) to submodules never supplied to
this project — confirmed broken by direct `ImportError` in that round's own audit. This notebook's
embedded `pw01_competencies.py` (written out by cell 4, alongside `competency.py`, `test_real_data.py`,
`q2_competencies.py`, and `report.py` — all five embedded directly as strings now, not uploaded) instead
uses `from competency import ...` and `from test_real_data import model, show` — otherwise identical (a
2-line diff, the import statements only). **Confirmed by direct execution in this sandbox**: the fixed
chain imports cleanly (`python3 -c "import q2_competencies"` now succeeds), something the second round's
files could not do.

**2. The DelegatesUniqueness/ConditionalCount scoping fix, described in the second round's conversation as
implemented and tested but never actually delivered as code (grep-confirmed absent from that round's
`semantic_backup.py`), is now real, delivered code.** `DELEGATING_FUNCTION` (`{"DelegatesUniqueness":
"contains_unique_day"}`) and `runtime_scoped_exemplar()` are both present in this notebook's embedded
`semantic_backup.py`, and `validate_semantic_backup.py` imports and applies
`runtime_scoped_exemplar()` to every exemplar pool before computing similarity — exactly the fix that
round's conversation described (`semantic_backup_score()`, report.py's live scoring path, gets the same
treatment). The `EXEMPLAR_REGISTRY` content itself (all 27 exemplar snippets) is byte-identical to the
second round's registry — only what gets embedded for similarity changed, not what's stored.

## The embedded model files: confirmed to be this repo's real, current checkpoints

Diffing the notebook's embedded `competency.py`/`test_real_data.py`/`report.py` (extracted directly from
cell 4's source strings) against every checkpoint in this repo:

- `competency.py`, `test_real_data.py`: substantively identical (one leading blank line from the
  `r'''\n...'''` string-embedding convention, nothing else) to
  `detectors/q5-delegation-clustering-fix` — **this repo's own current HEAD**, the most recent
  structural checkpoint that exists. Unlike both earlier mine_exemplars rounds, which turned out to be
  running against a `competency.py` that predated even the 2026-08-05 Q1 fix, this notebook's environment
  is genuinely up to date.
- `report.py`: substantively identical to `detectors/semantic-backup` — the same,
  earlier-than-`reporting-batch` version both mine_exemplars rounds also used. `report.py`
  itself was never touched by the 2026-08-08 Q5 delegation round, so this is not a discrepancy — it's
  this repo's own real dating, confirmed consistent across all three mine_exemplars-adjacent rounds.

## Independently re-verified in this audit, not just read from the notebook's own printed output

**`audit_registry()` now reports ZERO problems, against the complete real chain, for the first time ever
in this project.** Running the delivered code directly in this sandbox — now that the import chain is
fixed — against a model built from the full `test_real_data -> pw01_competencies -> q2_competencies`
chain: all 10 competencies, all 27 exemplars, all verify clean. Every earlier round could only check a
subset (7 or 8 of the 10 competencies) because the chain didn't import; this is the first genuinely
complete audit.

**The lexical discriminative-power numbers, post-scoping-fix, are exactly reproduced by direct
execution** (deterministic, no network or cache needed): pairwise win rate 1294/1428 (**90.6%**),
worst-case ranking 20/27 (**74.1%**), 7 named failure lines — critically, **zero of them involve
`DelegatesUniqueness`** (down from 5 of 12 failures in the second round's pre-fix run), confirming the
scoping fix does what it claims: it specifically and only removes the surface-containment confound
between `DelegatesUniqueness` and `ConditionalCount`, without meaningfully changing anything else (the
other 7 failures — `Accumulation`/`GuardedInput`/`ConditionalCount`/`SelectionStep` ambiguity, plus one
new, minor `AccumulateThenCount`/`FunctionalUniqueCheck` pair — are the same pre-existing confusions
carried forward).

**The three "Section 5.3" TopKPatternExtended structural regression cases (cell 17) are independently
reproduced exactly** against this repo's own current model — a delegate-based helper (`TopKViaDelegate`
fires), a pure-recursion quicksort helper (`SortThenSlice` only, cleanly isolating the `SELF_RECURSIVE`
case), and a merge-sort helper reproducing the already-documented Table-5/§8 false-positive
(`TopKViaDelegate` fires on shape alone, not genuine delegation). **This cell is explicitly labeled in
the notebook itself as "structural, not semantic-similarity" and "independent of the semantic backup
layer"** — it is a synthetic regression/demonstration check against the existing, unmodified model, not
a re-run against real corpus data, and it changes nothing about Q5's reported coverage. Confirmed by
reading it directly, not assumed from the label.

## What this audit could NOT independently check (network-blocked, same as every prior round)

The codet5p backend's numbers for the full 10-competency, post-scoping-fix registry — pairwise win rate
1202/1428 (**84.2%**), worst-case ranking 22/27 (**81.5%**) — cannot be independently re-run here;
`huggingface.co` remains blocked from this sandbox. This is the same figure the second round's conversation had
already reported (`conversation_reported_only` there), but it now comes with a genuinely executed notebook's real
output behind it (download logs, weight-loading progress, `execution_count` set) — upgraded here to
`evidence: real_notebook_output`, a step up from `conversation_reported_only`, though still short of independent
re-execution. The `moyenne()`/`DelegatesUniqueness` codet5p similarity smoke-test numbers (0.42 for an
unrelated pair, 0.97 for the broken-delegation false-positive probe, 0.975/0.977/0.961 for the three
call-site blind-spot variants) are the same — real notebook output, not independently re-computable here,
though the STRUCTURAL scores in those same cells (`Accumulation final=1.00`, `TopKPattern final=0.00`,
`DelegatesUniqueness final=0.00`) are ordinary structural-resolver output and match this repo's model
exactly by construction (the codet5p similarity is explicitly an advisory, never-scoring signal layered
on top, per this project's two-layer design).

## What this round does NOT establish

- Nothing about the real-corpus mining scan counts (248/291, 2/291, 13/291, 227/291) — this notebook
  doesn't re-run mining, it validates the already-mined registry. Those figures remain exactly as
  recorded in the second mine_exemplars round: conversation-reported only, no corpus ever supplied to this
  sandbox.
- **Table 4 and the Q5 TopKPatternExtended delegation breakdown** — nothing in this notebook touches
  either. Both remain exactly as previously verified (99.5%/97.6%, 90.4%/74.3%, 94.0%/74.7%, 77.6%/45.9%,
  91.9%/80.6%; 57 total new Q5 catches, 17 via `TopKViaDelegate`), per Sonia's explicit standing
  instruction.
- Whether this is genuinely the "last version" of this specific thread, or whether more files are still
  to come — no signal either way was given beyond the message itself. The zip continues to be held.

## Files in this checkpoint

- `semantic_backup_validation.ipynb` — the delivered notebook, copied verbatim, confirmed genuinely
  executed (20 cells, 10 code cells, execution_count 1–10, real outputs).
- `semantic_backup.py`, `validate_semantic_backup.py` — extracted verbatim from the notebook's own
  source cells (cells 6 and 7) — the only two files that changed relative to the second mine_exemplars
  round (the scoping fix). `competency.py`, `test_real_data.py`, `report.py`, `pw01_competencies.py`, and
  `q2_competencies.py` are NOT duplicated here since they are confirmed substantively identical to
  existing checkpoints (`q5-delegation-clustering-fix` and `semantic-backup`)
  except for `pw01_competencies.py`'s import fix — see
  `../../scripts/regenerate_semantic_backup_v3_audit.py`, which extracts and diffs all five directly
  from the notebook on every run rather than relying on a static copy.

See `../../scripts/regenerate_semantic_backup_v3_audit.py` for the automated re-verification of every
claim above that this sandbox can check (19/19 checks passing).
