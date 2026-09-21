# Paper revision history (files withheld — paper not yet published)

**Updated 2026-09-19: the raw paper files themselves (`.docx`/`.pdf`) have been removed from this public
repository, and every verbatim excerpt below has been replaced with a paraphrase** — the paper is not yet
published, and this repo's own earlier practice of block-quoting full paragraphs from each revision
(originally done so the exact wording behind a claim was itself auditable) would have exposed unpublished
manuscript text on GitHub. What's preserved instead: the real, independently-established dates for each
revision, exactly what changed at a structural level (which section, which figures, which claims), and —
for every number — a citation to the script/CSV in this repo that independently verifies it, so a reviewer
can still check every reported figure without needing the paper's own prose. `provenance/detector-version-log.md`
was edited the same way, for the same reason.

Five real, dated revisions of `Structural_Competency_Extraction_Paper` were tracked during this repo's
construction. Dates below are each revision's own internal metadata (PDF `CreationDate` / docx
`dcterms:created`), not the upload date, except where noted.

| File | Real date (internal metadata) | What it is |
|---|---|---|
| `2026-07_Structural_Competency_Extraction_Paper_prior.docx` | uploaded 2026-09-09; content dated by internal evidence to after 2026-07-28 | The pre-embedding-validation version: Case Studies 1-5 (Case Study 5 = Q3/Q4 batch results, its own §5.5), defects/Table 4 at §5.6, 3-reference bibliography (no Wang et al. 2023). |
| `2026-09-10_Structural_Competency_Extraction_Paper.pdf` | 2026-08-01 08:59 UTC (uploaded/read 2026-09-10) | The first embedding-validation version: Case Study 5's Q3/Q4 content merged into §5.3, a new §5.5 ("External validation of a taxonomic split via code embeddings," the single-run 89.1% manual/builtin embedding-agreement result), defects/Table 4 still at §5.6, a 4th reference (Wang et al., 2023, CodeT5+/EMNLP 2023), and an expanded Abstract/§7 Limitations. |
| `2026-08-04_Structural_Competency_Extraction_Paper.pdf` | 2026-08-04 16:28 UTC (uploaded/read 2026-09-12) | The current version — same day as `multi-seed loop.docx` and the updated methodology note (see `../methodology/`). Only the Abstract and §5.5 changed from the file above: the single-run 89.1%/0.98/0.77 figures are replaced by the 10-seed sweep's pooled mean±SD (87.0% ± 2.3% manual/builtin agreement; manual precision 0.94/recall 0.87; builtin precision 0.75/recall 0.88). Everything else in the 20-page document is byte-for-byte unchanged, confirmed by full page-by-page diff. |

**A note on the filename dates:** this file's internal `CreationDate` (2026-08-04) is *earlier* than the
prior file's supplied/read date (2026-09-10) even though it is the *later* paper revision — the paper
drafts were apparently generated out of upload order relative to Sonia's own review cadence. The
`provenance/detector-version-log.md` entries and this table both use each file's own internal metadata date,
not upload order, so "2026-08-04" here correctly denotes the second, more recent revision by content, not
an earlier one — always resolve ordering by reading the log's diff, not by string-sorting these filenames.

See `provenance/detector-version-log.md`'s "The updated paper" section (first revision) and "The published
paper, updated again" section (second revision) for the same structural summary of both revisions.

**Also tracked, same day:** the internal methodology note was substantially rewritten alongside the second
paper revision above (its canonical bug table grew from 19 to 21 entries) — see `../methodology/README.md`
(file withheld, same reasoning as this folder).

## Two more revisions, same round (2026-08-05) — Q1 added, then a new consolidated Table 4

Two further paper PDFs, both confirmed genuinely distinct by direct `pdftotext -layout` diff (not
duplicate uploads):

| File | Real date (internal metadata) | What it is |
|---|---|---|
| `2026-08-05_Structural_Competency_Extraction_Paper_intermediate_21p.pdf`/`.docx` | 2026-08-05 13:55:54 UTC (PDF) / 13:55:51Z (docx) | 21 pages — Q1's finding added. Abstract: "two exercises" → "three additional exercises"; "nineteen" → "twenty" defects. New §5.3 (the full Q1 diagnostic narrative — 383 zero-scores, three mechanisms, 99.5%/97.6% after the fix). New Table 4 row, "Overly narrow structural matching." |
| `2026-08-05_Structural_Competency_Extraction_Paper_final_22p.pdf` | 2026-08-05 14:05:28 UTC | 22 pages — the current, final version. New §5.5, "Summary: full-corpus coverage across all five Refactory exercises," with a brand-new consolidated Table 4 (all five Refactory questions, verbatim-matching this repo's own `scripts/regenerate_table4.py --check` output). Triggered a full renumbering, confirmed fully consistent by diff: old Table 4 (defects) → **Table 5**; old §5.5 (embeddings) → §5.6; old §5.6 (Robustness) → §5.7; every downstream cross-reference updated. |

Both are same-day continuations of the batch-validation run and Q1 fix logged at
`../detectors/q1-q4-batch-validation/` and `../detectors/q1-shared-binding-fix/` — see
`provenance/detector-version-log.md`'s "Real batch-validation RESULTS for Q1-Q4" section for the complete
word-for-word diff of both revisions.

**Naming note — this repository's own `table5_config.yaml`/`scripts/regenerate_table5.py` predate this
renumbering** and refer to the *embeddings/semantic-backup* experiments (the manifest's original "table5"
block), NOT the paper's new "Table 5" (the former defects table, renumbered this round). This is a real
naming collision between this repo's internal config names and the paper's own current section/table
numbers — flagged here rather than silently resolved, since renaming this repo's own config would itself
need to be logged as a distinct, deliberate change. The paper's *new* Table 4 (all-five-questions summary)
is what `configs/table4_config.yaml` and `scripts/regenerate_table4.py` already regenerate.

**Still not preserved here:** `Competency_Extraction_Article.docx` (the older, separate, pre-Q1-Q4
"article") and `Competency_Extraction_Methodology_V24.docx` / the 28/07 methodology note (earlier
methodology-note versions, superseded by the 2026-08-04 one now in `../methodology/`) — all real, all
logged extensively in `provenance/detector-version-log.md`, but not yet copied into this repository. Ask
Sonia if a future round should add them here too.

## A fourth same-day revision (2026-08-05, 18:02 UTC) — the Q4 embedding result written into §5.6

Supplied as `Docs_after adding embed for Q4.zip` (no accompanying conversation export this round — the real date
below comes directly from the file's own internal metadata, per this repo's usual dating discipline, since
no conversation text was supplied to override it):

| File | Real date (internal metadata) | What it is |
|---|---|---|
| `2026-08-05_Structural_Competency_Extraction_Paper_final_22p_q4embedding_added.pdf`/`.docx` | 2026-08-05 18:02:35 UTC (PDF) / 18:02:31Z (docx) | Still 22 pages, no renumbering — same-day continuation of `..._final_22p.pdf` above (14:05:28 UTC), roughly four hours later. Confirmed by direct `pdftotext -layout` diff against that file: exactly three substantive content changes, everything else identical (the rest of the raw diff is line-wrap/pagination reflow only, caused by the added text, not content changes). |

The three real changes, summarized (not quoted — see the note at the top of this file):

1. **Abstract.** Now reports both taxonomic-split agreement figures side by side (87.0% ± 2.3% for Q5's
   manual/builtin split, 93.6% ± 2.1% for the new Q4 split), rather than only the Q5 figure.

2. **§5.6, restructured and extended.** Retitled to cover "two taxonomic splits" instead of one; the
   existing Q5 material is kept, now under its own "Q5: manual vs. builtin" subheading, and a new "Q4:
   BubbleSortPass vs. TopKPattern" subsection is added applying the identical embedding-classification
   methodology to Q4's split. **Reported figures** (independently verified in this repo — see
   `scripts/regenerate_q2q4_taxonomy_crossvalidation.py` and
   `configs/stage_manifest.yaml`'s `q4_taxonomy_embedding_crossvalidation_10seed_pooled` entry): 93.6% mean
   agreement across 10 splits (SD 2.1%, range 89.8%–95.9%), pooled precision/recall bubblesort 0.69/0.98,
   topk 1.00/0.93, pooled support 204 bubblesort / 1,266 topk. Higher and more stable than Q5's own figure,
   with the misclassification asymmetry running the opposite direction (bubblesort is the broad,
   high-recall class here; topk is the tight, high-precision one) — attributed to bubble-sort
   implementations being structurally more homogeneous in real code than topk implementations, which admit
   more surface variety in how the extremum is found and removed. The section's closing paragraph frames
   both splits' results together as independent evidence that each taxonomic distinction is real and
   recoverable rather than an artifact of how the taxonomy happens to be written, and notes the consistent,
   mechanistically-explicable asymmetry between the two splits as a further finding in its own right.

3. **§7 Limitations.** The existing sentence about embedding-based novel-detection being a harder problem
   is generalized from referring only to the Q5 (manual/builtin) check to referring to both taxonomic-split
   checks.

**Every number in the new Q4 paragraph was independently verified against the notebook in the prior round,
before this paper revision was even supplied** — 93.6%/SD 2.1%/range 89.8%–95.9%, the 204/1,266 pooled
support counts, and both precision/recall pairs all match
`configs/stage_manifest.yaml`'s `q4_taxonomy_embedding_crossvalidation_10seed_pooled` entry exactly (see
`scripts/regenerate_q2q4_taxonomy_crossvalidation.py`). This revision is the paper simply writing in an
already-verified result, not a new empirical claim — no discrepancy found. See
`provenance/detector-version-log.md`'s "The Q4 embedding result written into the paper" section for the same
diff with full line-by-line sourcing.

## A fifth revision (2026-08-08) — a new §7, "The Semantic Backup Layer: Architecture Overview"

Supplied inside `files_Docs with _section for semantic_backup_layer.zip`, alongside a standalone
`Structural_Competency_Extraction_Paper_no_images_before_cluster.docx` that Sonia provided as an explicit
"before" baseline for diffing. Real dates, all from internal metadata (docx `dcterms:created`/PDF
`pdfinfo CreationDate`, no conversation accompanies this specific file trio): the "before_cluster" baseline is
2026-08-08 10:44:27 UTC; the zip's own full docx is 10:58:55 UTC; its PDF sibling 10:58:59 UTC; its
no-images docx sibling 10:59:11 UTC — all within a 15-minute window.

**The "before_cluster" baseline is confirmed, by direct diff, to be textually identical to the prior
22-page revision already in this repository** (`2026-08-05_Structural_Competency_Extraction_Paper_final_22p_q4embedding_added.docx`) —
the only difference is the absence of the two pre-existing figures (Figure 1, Figure 2), since it's a
no-images export. It is not a new revision in its own right; it's the confirmed starting point this
round's real new content was added to.

| File | Real date (internal metadata) | What it is |
|---|---|---|
| `2026-08-08_Structural_Competency_Extraction_Paper.docx`/`.pdf` | 2026-08-08 10:58:55/10:58:59 UTC | 23 pages (up from 22) — the current, final version. Both real embedded images (`word/media/rId25.png`, `rId38.png`) are byte-identical to the prior revision's — unchanged, not new. |

**Exactly one substantive content change, confirmed by direct diff against the "before_cluster" baseline:
a new §7, "The Semantic Backup Layer: Architecture Overview,"** inserted between §6 (Discussion) and the
old §7 (Limitations, renumbered §8; Conclusion renumbered §8→§9, References unaffected). Summarized (not
quoted — see the note at the top of this file): the new section explains the semantic-similarity backup
layer's purpose and design in plain terms — it exists to flag submissions that are likely correct but that
the structural rules missed because no rule was ever written for that particular strategy, not to
auto-grade or close the gap itself. It describes the mechanism (comparing a submission's code embedding,
via Salesforce/codet5p-110m-embedding, against a small per-competency registry of known-correct exemplars;
a high similarity score is framed explicitly as "a signal for human review," never folded into
`final_score`) and states plainly that nothing in the section constitutes a validated result — the layer's
actual accuracy, its exemplar registry, and any decision threshold are explicitly deferred to the companion
paper.

The renumbered Limitations section (old §7 → new §8) also gets a small wording change, from describing the
semantic layer inline to pointing at the new §7 instead. Everything else — every prior section's content,
all figures, the References — is confirmed byte-identical.

**This section does NOT include the real, inverted AUC=0.097 finding** logged the same round at
`../detectors/semantic-backup-layer-validation/` — consistent with its own text deferring all
accuracy/validation claims to "the companion paper." See
`provenance/detector-version-log.md`'s "A third paper revision — new §7" section for the same diff with full
sourcing, and the "Semantic backup layer validation" section for the AUC finding itself.

## The re-supplied methodology doc, this round — confirmed a byte-identical duplicate

`Competency_Extraction_Methodology.docx`, supplied alongside the files above, is confirmed via `md5sum` to
be byte-identical to `../methodology/2026-08-05_Competency_Extraction_Methodology.docx`, already in this
repository. No new methodology-doc content this round.

## A fifth revision, same day (2026-08-08) — Q5's delegation-clustering fix folded in

| File | Real date (internal metadata) | What it is |
|---|---|---|
| `2026-08-08_Structural_Competency_Extraction_Paper_after_clustering.docx` | 2026-08-08 14:06:13 UTC | Same day as the §7 revision above (10:58:55 UTC), roughly 3h07m later. No PDF supplied this round. |

Full text diff against `2026-08-08_Structural_Competency_Extraction_Paper.docx` (the §7-only revision)
confirms five real, localized content changes, every one independently verified against the real batch
report and clustering-notebook output (see `../provenance/detector-version-log.md`'s "Q5 delegation fix via
embedding-guided clustering" section for the complete verification):

1. **Abstract** — a new sentence: the same codet5p-110m-embedding model, "used as a discovery tool rather
   than a validator," clustered Q5's 43 uncategorized submissions into one dominant group, leading to the
   delegation-pattern fix.
2. **§5.3, new "Q5: closing the novel gap via embedding-guided clustering" paragraphs** — the full story:
   the silhouette-vs-dendrogram methodological trap and how it was caught, the two real sub-patterns found
   (delegate-to-repeated-extraction vs. delegate-to-general-sort), DELEGATES + the new SELF_RECURSIVE
   primitive, coverage rising 79.7%→91.9% (correct) / 75.0%→80.6% (wrong) with zero regressions, and the
   honest false-positive caveat (not hidden in a footnote).
3. **Table 4** — Q5's row updated to target competency `TopKPatternExtended`, 91.9% (418) / 80.6% (108);
   the summary sentence changed from "three of five" to "four of five exercises needed a fix."
4. **§6 Discussion, new design-principle paragraph** — elevates clustering beyond a one-off anecdote,
   framing an unexplained residual population as worth clustering before reading file-by-file, but stating
   the caveat that the clustering method itself needs checking, not just running — naming the
   silhouette-overfitting pitfall explicitly as the generalizable lesson.
5. **§8 Limitations, new paragraph** — the confirmed-but-uncharacterized TopKPattern false-positive mode
   (exposed, not created, by delegation), stated plainly rather than buried.

**A real, explained baseline discrepancy, caught and documented rather than left unreconciled**: this
revision's own re-measured "before" figure for TopKPattern is 79.7%, not the 78.2% already published in
this same section's earlier text. The source conversation traces this to an intervening, unrelated fix (Q1's
`SHARED_BINDING`/`all_names` change) incidentally shifting a handful of TopKPattern's own combinatorial
matches — independently confirmed in this repository by a direct diff against the original
`detectors/reporting-batch/topk_report.csv` (exactly 6 correct-labeled files flip 0→1, zero
wrong-labeled files change). See `scripts/regenerate_q5_delegation_breakdown.py`.

**A striking, purely coincidental resemblance to this repo's own corrected (fabricated) `VERSIONING.md`
note** is worth flagging here too, even though it belongs to the code/data side, not the paper: months
before any of this was real, an earlier, explicitly-fabricated scaffold of this repository guessed a
nonexistent `TopKPatternExtended` competency built with `DELEGATES` + a nonexistent `SELF_RECURSIVE`
primitive, and a Q5 figure of "79.7% → 91.9%" — the exact ingredients this real revision now independently
confirms. See `../VERSIONING.md`'s corrections section and `../provenance/detector-version-log.md` for the
full, carefully-hedged writeup: this is recorded as a notable coincidence, not as vindication of guessing
— every other specific claim in that same fabricated version remained wrong.
