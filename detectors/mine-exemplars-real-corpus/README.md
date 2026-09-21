# 2026-08-09 (content-dated) / delivered 2026-09-17 — a second mine_exemplars batch: real corpus mining, and the round-1 bare-while question resolved

*Note (2026-09-21): the `/home/claude/refactory/...` path below is the historical record of what this
round's script actually hardcoded and what this project's own sandbox checked for — not something to
run against today. The checked-in `mine_exemplars.py` in this repository now resolves the corpus location
portably (`REFACTORY_ROOT` env var, or a path relative to the script's own location); see
`provenance/detector-version-log.md`, "Hardcoded `/home/claude/refactory` sandbox path made portable."*

Sonia's message: "A second version is here," uploading four files as a follow-up to the first
mine_exemplars delivery (`../mine-exemplars/`): a second dev-session conversation transcript
(`This is the real Refactory corpus_mines_exemplar_2ndt chat.docx`, docx metadata: created
2026-08-08T18:54Z, modified 2026-09-17 — the modified date is this export's own timestamp, same
pattern as every other conversation-history docx this project has received, not a meaningful authorship date),
a RAR archive of "original files to load," a "final" mining zip
(`semantic_backup.py`/`mine_exemplars.py`/`semantic_backup_validation.ipynb`, internal zip timestamps
2026-08-09 16:07), and a semantic embedding cache zip (`codet5p.pkl`/`lexical.pkl`, internal timestamps
2026-08-08 21:15).

Per Sonia's standing instructions this session: **Table 4 and the Q5 TopKPatternExtended delegation
breakdown are untouched by any of this** (nothing in this batch's conversation or code even mentions either),
and **the zip has not been repackaged or resent** — this round is being held for a future "all files
sent" signal, same as the first mine_exemplars round.

## What this round is: real corpus mining, replacing the earlier CONFIG-TODO gaps

The first mine_exemplars round's `mine_exemplars.py` had `AccumulateThenCount` and `Accumulation` as
explicit `TODO` entries in `CONFIG`, and no real Refactory corpus was ever supplied to actually run
mining against. This round's conversation describes exactly that gap being closed — in Colab, with the real
corpus mounted at `/home/claude/refactory/data/question_2/code/correct` — for four Q2 competencies:
`ConditionalCount`, `AccumulateThenCount`, `FunctionalUniqueCheck` (new), and `DelegatesUniqueness`
(new, cross-function). `mine_exemplars.py` here is a different, narrower script than the first round's
(`mine.py` and `mine_cross_function()`, hardcoded to `QUESTION_2_DIR`) rather than an extension of the
first round's general `CONFIG`-driven one — copied verbatim from the delivered zip, not rewritten by
this audit.

**None of the real-corpus-scan numbers below could be independently checked** — this sandbox has never
had the Refactory corpus (confirmed absent again this round: `find / -ipath "*question_2/code/correct*"`
finds nothing anywhere). They remain `conversation_reported_only`, exactly like every other real-corpus
population count this project has ever reported:

- `ConditionalCount`: 248/291 (85%) real submissions verify at `final_score=1.0`, 66 distinct
  structural shapes.
- `AccumulateThenCount`: only 2/291 verify, both collapsing to the same shape — independently
  cross-checked (per the conversation) against the analogous `unique_month` function, same two students, same
  shape. A real, standalone finding if true: a genuinely rare strategy (<1% of correct submissions),
  not just under-sampled.
- `FunctionalUniqueCheck`: 13/291 (4.5%), 11 distinct shapes, one exemplar chosen per real sub-strategy
  (`InlineFunctionalCheck` / `GuardedFunctionalCheck` / `InlineTestFunctionalCheck`).
- `DelegatesUniqueness`: 227/291 (78%), 96 distinct shapes — needs the whole module tree, not just the
  target function, since `DELEGATES` reasons across the function boundary.

## A real integrity finding, independently confirmed: 2 of 3 original AccumulateThenCount exemplars were also invalid

The conversation describes discovering, while setting up mining, that 2 of the first round's 3
`AccumulateThenCount` exemplars (`count_evens`, `count_long_words`) scored `final_score=0.0` under the
real rule — they used `len(...)`-based counting, but the rule specifically requires `.count(` in the
output text. This is a second, independent instance of the same class of bug the first round found in
`GuardedInput` (hand-written exemplars never run through the real resolver before being trusted). The
delivered `semantic_backup.py`'s `AccumulateThenCount` entry now has one real-mined exemplar plus two
corrected synthetic replacements, with a code comment explaining exactly this.

**This audit cannot independently verify any of `AccumulateThenCount`'s three current exemplars** —
see "A confirmed, but differently-caused, verification gap" below.

## The registry is now real, delivered code: 10 competencies, 27 exemplars

Confirmed by direct inspection of the delivered `semantic_backup.py`'s `EXEMPLAR_REGISTRY` (not the
conversation's own count): `Swap` (2), `Accumulation` (3), `ConditionalCount` (5), `AccumulateThenCount` (3),
`GuardedInput` (2), `SelectionStep` (2), `FindExtremumBuiltin` (2), `TopKPattern` (2),
`FunctionalUniqueCheck` (3), `DelegatesUniqueness` (3) = **27 exemplars across 10 competencies**. This
is the exact figure the two reference documents from an earlier round
(`Competency_Extraction_Methodology_V2.docx`, `Structural_Competency_Extraction_Paper_v1_2.docx`)
described as a finished future state — that state is now backed by real, delivered, independently
runnable code for the exemplar registry itself. It remains true, and is restated here for clarity, that
this does **not** extend to Table 4, the Q5 delegation breakdown, or the real-corpus mining counts
above, none of which are touched by this round either.

## A confirmed, but differently-caused, verification gap: the "real chain" doesn't actually run here

The conversation describes retiring an earlier `q2_extra.py` workaround in favor of "the real
`test_real_data.py -> pw01_competencies.py -> q2_competencies.py` chain." The "Original files to load"
RAR delivers all five files this chain needs
(`original_files_used_this_round/{competency,test_real_data,report,pw01_competencies,q2_competencies}.py`).
**Directly attempting to import them in this sandbox shows the chain does not actually run here**:

```
$ python3 -c "import pw01_competencies"
  File ".../pw01_competencies.py", line 2, in <module>
    from .core import Competency, ALL, NESTED, AND, REFERENCES, CONTAINS_TEXT, DELEGATES
ImportError: attempted relative import with no known parent package
```

`pw01_competencies.py` uses package-relative imports (`from .core import ...`,
`from .base_competencies import model, show`) to submodules (`core.py`, `base_competencies.py`) that
have never been supplied to this project in any round — presumably because the developer's Colab
environment has them as part of a larger, not-fully-uploaded project structure. `q2_competencies.py`
imports `model` from `pw01_competencies`, so it fails the same way, transitively.

Practically, this means `AccumulateThenCount`, `FunctionalUniqueCheck`, and `DelegatesUniqueness` are
**still unverifiable in this sandbox** — the same practical gap as the first mine_exemplars round, but
for a genuinely different, more specific reason this time: not "the module was never supplied" (it
nominally was, this round), but "the module that WAS supplied has a broken import chain to code that
was not." `audit_registry()`, run against the only model this sandbox can actually construct
(`test_real_data.py`'s own model, which registers `ConditionalCount` directly but none of the other
three), correctly reports exactly these three competencies as `"not registered in the given model"` —
confirmed by direct execution, not assumed. `Swap`, `Accumulation`, `ConditionalCount`, `GuardedInput`,
`SelectionStep`, `FindExtremumBuiltin`, and `TopKPattern` — the seven competencies `test_real_data.py`
alone can check — all audit clean, including both of `GuardedInput`'s corrected exemplars, confirmed
individually at `final_score == 1.0`.

## The round-1 "bare-while GuardedInput" open question is now resolved with hard evidence

The first mine_exemplars round's audit reconstructed the original, pre-fix bare-`while` `GuardedInput`
exemplar the source conversation described, and resolving it against this repo's then-closest-dated real
`competency.py` (`../q1-shared-binding-fix/competency.py`) scored `final_score == 1.0`, not
the claimed `0.0` — recorded as a genuinely open, hypothesized-but-unconfirmed discrepancy (most likely
explained by the developer's session using an older `competency.py`, consistent with this project's
"two different working environments" pattern, but never confirmed since the exact version actually used
was never supplied).

**This round supplies that exact version.** Diffing `original_files_used_this_round/competency.py` and
`test_real_data.py` against every checkpoint in this repo finds a 0-diff-line exact match against
`../fixq4/` for both files (`report.py` similarly matches `../semantic-backup/`
exactly) — i.e. this mine_exemplars session's actual environment was running a `competency.py` that
**predates** the 2026-08-05 Q1 `SHARED_BINDING`/`all_names` fix.

Reading the diff between `fixq4/competency.py` and `q1-shared-binding-fix/competency.py`
shows exactly why this matters: the Q1 fix didn't just change `SHARED_BINDING`'s comparison from
`operand` to `all_names` — it also **added an entirely new `elif isinstance(node, ast.While):` branch**
to the `TEST` primitive detector, synthesizing `TEST` evidence directly from a while loop's own
condition (with `node=None`, matching this project's composite-evidence convention). Before that fix,
`TEST` evidence could only ever come from an `ast.If` node — a bare `while` condition with no nested
`if` genuinely could not produce a `TEST` primitive at all.

Reconstructing the same bare-while `GuardedInput` shape and resolving it against the ACTUAL,
now-supplied `fixQ4`-era `competency.py` (not a later one) scores:

```
final_score: 0.0   coverage_score: 0.667   structural_score: 0.0
(source + loop present; test missing entirely)
```

**Exactly the claimed `0.0`.** This is no longer a hypothesis — it is a diff-confirmed, then
execution-confirmed fact: round 1's own reconstruction attempt used the wrong (later, post-Q1-fix)
`competency.py`, not because the reconstructed code was wrong, but because that competency.py had
already gained new behavior the developer's actual environment never had. See
`../../scripts/regenerate_semantic_backup_v2_audit.py` for the automated re-check of this exact claim,
and `../mine-exemplars/README.md`'s own update note.

## The delivered semantic_cache.zip contains real, verified codet5p and lexical embeddings

`semantic_cache.zip` (`.semantic_cache/codet5p.pkl`, `.semantic_cache/lexical.pkl` in this checkpoint)
is not a placeholder — it is the actual on-disk content-hash-keyed embedding cache
`semantic_backup.py`'s `_save_cache`/`_load_cache` read and write, downloaded from Colab per the
notebook's own cell 15 ("Pulls the embedding cache back down"). Directly unpickling both files
confirms: `lexical.pkl` holds 24 real 4096-dimension vectors (matching `LexicalEmbedder`'s
`HashingVectorizer(n_features=4096)`); `codet5p.pkl` holds 24 real 256-dimension `float32` vectors
(matching `Salesforce/codet5p-110m-embedding`'s actual output dimensionality — this sandbox cannot
verify the values came from that specific model, since huggingface.co remains blocked here too, but the
shape, dtype, and content-hash keying are all consistent with real model output, not synthetic data).

Cross-referencing the 27 registry exemplars' content-hash keys against the 24 cached `codet5p.pkl`
entries: **21 of 27 match exactly** (the 8-competency subset that excludes `FunctionalUniqueCheck` and
`DelegatesUniqueness`, added later in the same dev session — after this cache was saved), plus 3
further cache entries matching `validate_semantic_backup.py`'s own `UNRELATED_SNIPPETS` exactly
(`greet`, `read_config`, `Point`). 24 total, precisely accounted for — no unexplained entries.

### Independently reproduced, using ONLY the real cached embeddings — no network call made or needed

Loading `semantic_backup.py` with `SEMANTIC_BACKUP_CACHE_DIR` pointed at this checkpoint's
`.semantic_cache/`, and patching `get_embedder("codet5p")` to raise loudly instead of silently falling
back if anything not already cached is requested (proving nothing below is fabricated or network-backed):

Running the delivered `validate_semantic_backup.py`'s own `run()` function against the 8-competency
subset (the exact set with cached codet5p vectors) reproduces the conversation's first codet5p block **exactly**
— every mean/median/n, every one of the 5 named failure lines, and the headline number:

> Pairwise win rate (SAME beats random OTHER): 696/852 (**81.7%**). Worst-case correct ranking: 16/21
> (**76.2%**).

This is the first time this project has ever independently reproduced a codet5p discriminative-power
number from real cached model output, without trusting the transcript and without needing live
huggingface.co access. `evidence: real_csv` is the closest existing tier for this — the underlying data
is real, preserved model output (a pickle cache, functionally the same evidentiary weight as a CSV of
raw scores), independently reprocessed by this audit's own code, not re-typed from the conversation.

### Lexical, full 10-competency registry — no cache dependency at all, deterministic

`LexicalEmbedder` needs no network and no cache to begin with (`HashingVectorizer`, always available).
Running the same delivered `validate_semantic_backup.py`'s lexical backend against the full, current
27-exemplar/10-competency registry reproduces the conversation's "10/08" lexical block **exactly** — all three
summary rows, all 12 named failure lines, and:

> Pairwise win rate: 1262/1428 (**88.4%**). Worst-case correct ranking: 15/27 (**55.6%**).

## What this round does NOT establish (explicitly, so it isn't assumed later)

- **The 10-competency codet5p run (84.2% win rate, 81.5% worst-case)** is not independently checkable
  here — `FunctionalUniqueCheck` and `DelegatesUniqueness`'s codet5p embeddings were never cached in the
  delivered `semantic_cache.zip` (confirmed by content-hash cross-reference above), and
  huggingface.co is still blocked from this sandbox. Remains `conversation_reported_only`.
- **The DelegatesUniqueness/ConditionalCount scoping fix** (`DELEGATING_FUNCTION`,
  `runtime_scoped_exemplar()`, reported lexical 90.6%/74.1%) described later in the same conversation as
  implemented, tested, and shipped to "outputs" is **not present anywhere in the delivered
  `semantic_backup.py`** (grep-confirmed absent: no `DELEGATING_FUNCTION`, no `runtime_scoped_exemplar`
  in this file). The code implementing this fix was described in the conversation but never actually delivered
  to this project. Remains `conversation_reported_only`.
- **`semantic_backup_findings_v4.docx`, an edited `Structural_Competency_Extraction_Paper_v1.docx`
  (with a new §7 Limitations sentence about a call whose result is discarded), and a `DOCUMENT_INDEX.md`**
  are all referenced in the conversation's closing sections as delivered/finalized, but **none of these three
  documents were included in this batch's four uploaded files**. Only the code
  (`mine_exemplars.py`/`semantic_backup.py`/the notebook) and the embedding cache were delivered.
- **The real-corpus mining scan counts** (248/291, 2/291, 13/291, 227/291, and the "0 mismatches across
  20 real submissions" `q2_extra.py` sanity check) — no Refactory corpus has ever reached this project.
- **Table 4 and the Q5 TopKPatternExtended delegation breakdown** — nothing in this batch touches
  either. Both remain exactly as previously verified (99.5%/97.6%, 90.4%/74.3%, 94.0%/74.7%,
  77.6%/45.9%, 91.9%/80.6%; 57 total new Q5 catches, 17 via `TopKViaDelegate`), per Sonia's explicit
  standing instruction.

## Files in this checkpoint

- `mine_exemplars.py` — the real-corpus miner for the four Q2 competencies, copied verbatim.
- `semantic_backup.py` — the 10-competency/27-exemplar registry, copied verbatim (predates the
  DelegatesUniqueness scoping fix — see above).
- `validate_semantic_backup.py` — extracted verbatim from the notebook's own cell 7 (the delivered zip
  did not include this file standalone; the notebook writes it out at execution time).
- `semantic_backup_validation.ipynb` — copied verbatim; confirmed entirely unexecuted (16/16 cells,
  `execution_count: None`, no outputs) — same pattern as every notebook this project has received as a
  template rather than an executed artifact.
- `.semantic_cache/{codet5p,lexical}.pkl` — the real embedding cache, copied verbatim.
- `mine_exemplars_v2_chat.txt` — the second dev-session transcript, converted from docx.
- `original_files_used_this_round/` — the five real project files this round's mining environment
  actually ran against, preserved exactly as delivered (fixQ4/2026-07-20-era, NOT this repo's current
  HEAD state — see "The round-1 bare-while question resolved" above for why that dating matters).

See `../../scripts/regenerate_semantic_backup_v2_audit.py` for the automated re-verification of every
claim above that this sandbox can check.
