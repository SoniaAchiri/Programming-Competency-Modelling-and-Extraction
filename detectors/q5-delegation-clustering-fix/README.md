# Q5 delegation fix — closing the novel gap found by embedding-guided clustering

**Real date: 2026-08-08**, same day as (and directly downstream of) the semantic backup layer AUC finding
in `../semantic-backup-layer-validation/` — internal evidence: this folder's `competency.py`
carries a zip-embedded mtime of `2026-08-08 13:59:04`, and the paper revision this fix was folded into
(`../../papers/2026-08-08_Structural_Competency_Extraction_Paper_after_clustering.docx`) has its own
`dcterms:created` of `2026-08-08T14:06:13Z`, ~7 minutes later — a coherent same-day sequence: code fix →
batch validation → paper update. The accompanying conversation export
(`../semantic-backup-layer-validation/semantic_backup_second_role_08_08_after_clustering_chat.docx`)
carries no internal date header of its own (unlike its "before clustering" predecessor); its own filename
and this internal-metadata chain are what establish the date.

## What this is

The semantic backup AUC round (`../semantic-backup-layer-validation/`) established that Q5's
43 correct-labeled + 5 wrong-labeled "novel" submissions (test-suite-correct, scored 0 on `FindExtremum`)
read as *dissimilar* to a typical-correct exemplar registry. This round asks the natural follow-up: are
those 43 correct-labeled files each doing something wildly different from every other one, or do they form
their own coherent sub-clusters worth reading? Embedding-based hierarchical clustering (added as a new §11
to the same notebook — see the extended notebook files in
`../semantic-backup-layer-validation/`) answers this directly, and the answer feeds a real code
fix, not just a descriptive finding.

## What's here

- `competency.py` — adds exactly one new primitive, `SELF_RECURSIVE` (`detect_self_recursive`): one
  evidence per function that calls itself directly, closing a real gap where a pure-recursion `merge_sort`
  helper had zero `LOOP` nodes and so was invisible to any loop-only "does real work" check. Diffed against
  the most recent prior checkpoint (`../q1-shared-binding-fix/competency.py`): this is the
  *only* change — one new function (22 lines) plus its one-line registration in `PRIMITIVE_DETECTORS`.
- `test_real_data.py` — adds four new competency registrations, diffed against
  `../q1-shared-binding-fix/test_real_data.py`:
  - `TopKViaDelegate` — `DELEGATES("call", "TopKPattern")`: catches a helper function, called by `top_k`
    under a different name, that repeats TopKPattern's own find-max/remove/append shape.
  - `HasSubstantialWork` — `ALL(["loop"])` where `loop` covers `("LOOP", "SELF_RECURSIVE")`: a helper
    "does real work" if it has a loop *or* calls itself recursively.
  - `SortThenSlice` — `DELEGATES("call", "HasSubstantialWork")` `AND` `SEQUENTIAL(["call", "output"],
    max_line_gap=10)`: catches a helper that does a genuinely different general-purpose sort (recursive
    `merge_sort`, an in-place bubble-style sort) and slices the result.
  - `TopKPatternExtended` — `ANY(["direct", "delegate", "sort_then_slice"])` over `TopKPattern`,
    `TopKViaDelegate`, and `SortThenSlice`, `allow_mixed_levels=True` (documented layering exception, same
    convention as `BubbleSortPass`: the delegate branches are inherently shallower than the inline branch,
    since their real depth lives inside `DELEGATES`' own independently-scoped resolution of the callee).
    The original `TopKPattern` registration is untouched — `SortByKey`, which wraps it, is unaffected.
- `topk_report_EXTENDED2.csv` — the real batch-validation run this fix was verified against: 526 rows
  (418 correct, 108 wrong — the same Q5 corpus as every other Q5 checkpoint), with
  `TopKPattern_final`/`_missing`, `TopKViaDelegate_final`/`_missing`, `SortThenSlice_final`/`_missing`, and
  `TopKPatternExtended_final`/`_missing` columns.

## Independently verified, not just repeated from the conversation

Every headline and secondary figure in the source conversation was independently recomputed directly from
`topk_report_EXTENDED2.csv` and cross-checked against the original
`../reporting-batch/topk_report.csv` — see `scripts/regenerate_q5_delegation_breakdown.py` (all
checks `[OK]`) and `scripts/build_labels_scores_from_batch_reports.py --question 5` (builds
`data/labels_scores/q5_final_extended.csv`, matching Table 4's own arithmetic via
`scripts/regenerate_table4.py --check`):

- **Headline coverage**: correct 79.7% → 91.9% (333/418 → 384/418), wrong 75.0% → 80.6% (81/108 → 87/108).
  Zero regressions: no row with `TopKPattern_final == 1` has `TopKPatternExtended_final == 0`.
- **The exact new-catch breakdown**: 57 new catches total; 17 via `TopKViaDelegate` (**all 17** also
  caught by `SortThenSlice` — `TopKViaDelegate` never fires on its own in this real data, a genuine,
  honest wrinkle the source conversation flags rather than glosses over); 40 further catches via `SortThenSlice`
  alone.
- **The two wrong-labeled `TopKViaDelegate` catches, named**: `wrong_5_011.py` (a genuine match — its
  helper compares tuple elements, consistent with age-sorting logic) and `wrong_5_101.py` (a genuine
  match too — wrong for an unrelated reason: `sort=sort(lst)` shadows the function name with a local
  variable, which would crash at runtime with `UnboundLocalError`).
- **A real, explained baseline drift**: TopKPattern's own (non-extended) coverage moved from 78.2%
  (327/418, the figure `../reporting-batch/topk_report.csv` and every earlier Q5 checkpoint
  report) to 79.7% (333/418) when re-measured against the current codebase — confirmed by direct diff:
  exactly 6 correct-labeled files flip 0→1 (`correct_5_064/159/170/282/321/362.py`), zero wrong-labeled
  files change. Attributed by the source conversation to the intervening Q1 `SHARED_BINDING`/`all_names` fix
  (`../q1-shared-binding-fix/`) incidentally shifting a handful of TopKPattern's own
  combinatorial matches — a real, structural side effect of a broadly-shared constraint, not an error in
  either measurement. Both figures are real; `data/labels_scores/q5_final.csv` (the original, still
  preserved) correctly keeps reporting 78.2% as its own checkpoint's real figure at the time it was
  measured, not amended in place.

## An honest, uncharacterized false-positive caveat — not hidden

Manually sample-checking 7 of the 17 `TopKViaDelegate` catches found 6 genuine matches and 1 confirmed
false positive: `correct_5_416.py`'s helper is a bubble-sort-style adjacent-swap using `.insert()`/
`.pop()` — nothing like "find the max, remove it, append it" — but TopKPattern's own combinatorial matcher
found a coincidental combination of loop, test, and tagged assignment that satisfies its abstract
structural shape anyway. This is **not a defect introduced by delegation** — it was always latent in
TopKPattern's own definition, only ever tested inline within `top_k` itself before; delegation newly
exposes it against a wider variety of helper-function bodies. The ~14% sample false-positive rate (1 of 7
checked) was **not extrapolated to the full 17** — the source conversation explicitly declines to report a
"fully verified" number the way the Q1 fix's 99.5%/97.6% was, and this repository preserves that same
honesty: 91.9%/80.6% is reported as *likely a slight overstatement by an uncharacterized amount*, not as a
clean, closed figure. See `../../docs/KNOWN_CAVEATS.md`.

## The clustering discovery itself — real notebook output, not a separately-exportable dataset

The clustering analysis that motivated this fix (hierarchical clustering + a distance-threshold cut at
0.30, recovering one 38-file dominant cluster and three true outlier files/pairs from Q5's 43 novel
correct submissions) lives in `../semantic-backup-layer-validation/`'s extended notebook files,
not here — see that checkpoint's own README for the full writeup, including the real silhouette-sweep
values, the real distance-cut cluster membership (independently extracted from the executed notebook's own
output and confirmed to match the source conversation's quoted listing exactly), and the embedded dendrogram chart.
**Evidence tier for the clustering step itself is `real_notebook_output`, not `real_csv`**: no standalone
embeddings or distance-matrix file was ever saved by the notebook (unlike the AUC section's own CSVs), so
the clustering result is independently verifiable only by reading the executed notebook's own printed/
plotted output directly — which this repository does, but cannot independently recompute from a smaller
raw artifact the way the AUC and delegation-fix figures above can.

## A striking, purely coincidental resemblance to an earlier fabricated guess

Worth recording precisely, in the same spirit that led this repository to preserve its own corrected
`VERSIONING.md` rather than silently delete it: an earlier, explicitly-fabricated version of this
repository's scaffold — built from the paper's prose alone, before any real checkpoint had been
examined — guessed a nonexistent `TopKPatternExtended` competency built with `DELEGATES` and a nonexistent
`SELF_RECURSIVE` primitive, and a Q5 figure of "79.7% → 91.9%". This round's real, independently-verified
work — done months later, with no possible awareness of that deleted guess — produces exactly those
ingredients for real. This is flagged as a notable coincidence, not as vindication of guessing: every
*other* specific claim in that same fabricated version (the `NESTED`/`SEQUENTIAL`/`SHARED_BINDING`
mechanism guesses, the fabricated Table-5 embedding numbers, the invented semver ladder) turned out wrong
once real evidence arrived. See `../../VERSIONING.md`'s corrections section and
`../../provenance/detector-version-log.md` for the complete writeup.
