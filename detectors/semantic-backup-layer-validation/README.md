# Semantic backup layer validation — the layer's actual job, first real AUC (inverted, now CSV-backed)

**Real date: 2026-08-08** (per the conversation export's own header, "Steps for semantic Backup (second role)
08-08-2026" — DD-MM-YYYY, this project's usual convention) — three days after the Q4/Q2 embedding-taxonomy
round (`../q2-q4-embeddings-crossvalidation/`). See `../../provenance/detector-version-log.md`'s
"Semantic backup layer validation" section for the full verification writeup this README summarizes.

**Evidence status upgraded to `real_csv`** in a later round: the two raw CSVs the notebook's own final
cell saved, and then the executed notebook itself, were both independently supplied and verified — see
"Evidence status" below, which supersedes the original `conversation_reported_only` framing this checkpoint
started with.

**Filenames corrected in a still-later round (see "A naming correction" below):** Sonia re-supplied both
notebooks renamed to match this project's established convention (`Copie_de_...` = the unexecuted copy,
`..._with_Results.ipynb` = the executed one — the same pattern used in the Q4/Q2 embedding round). Content
is byte-identical to what was already in this repository under the old names; only the filenames listed
below changed.

**Extended with a real new §11 (clustering) in a still-later round** — see "The clustering extension"
below. The notebook itself grew from 22 to 32 cells (11 to 16 code cells); the underlying AUC section
(§§1-10) is unchanged and re-verified identical. This clustering pass led directly to a real code fix —
see `../q5-delegation-clustering-fix/README.md`.

## What this is

Every embedding check in this project up to this point (Q5/Q4/Q2 taxonomy cross-validation) tested whether
embeddings *agree with an existing AST split* — a different question from what the semantic backup layer
is actually supposed to do: separate genuinely-novel-correct submissions (test-suite-correct, but scored 0
by every structural rule) from genuinely-wrong ones, using no AST information at all. This notebook is the
first real attempt at that actual question, built to fix two specific problems already diagnosed in
earlier attempts logged in this project:

- **The contaminated-comparison-group problem** (flagged in `detectors/semantic-colab-validation/`
  and never resolved there): an earlier attempt restricted the "wrong" comparison group to submissions
  that ALSO scored 0 structurally, which accidentally selected for submissions that already look similar
  to correct code. This notebook uses **every** wrong-labeled submission as the negative class instead.
- **Single-draw instability**: every embeddings check in this project has turned out to have real
  seed/draw-to-draw variance. This notebook **bootstraps the exemplar registry itself** — 10 independent
  draws of `N_EXEMPLARS=8` real correct submissions (held out from the `novel_correct` scoring pool) — and
  reports AUC as a mean ± SD across draws, plus a separate pooled-AUC/ROC calculation across all draws
  combined.

Default competency: `FindExtremum` (Q5), the one with an already-confirmed, reasonably-sized
`novel_correct` population (43 real candidates, per earlier rounds' own count).

## What's here

- `Copie_de_semantic_backup_layer_validation.ipynb` — the notebook Sonia was first given (originally
  supplied as plain `semantic_backup_layer_validation.ipynb`; renamed in a later round — see "A naming
  correction" below; **content unchanged, confirmed by md5**). **Confirmed entirely UNEXECUTED** by direct
  JSON inspection: 22 cells (11 markdown, 11 code), every code cell's `execution_count` is `None` and every
  code cell's `outputs` list is empty. This matches the conversation's own framing of this round ("here the first
  part before clustering") and the notebook's own final markdown cell's instruction ("Report the AUC mean
  +/- std... whichever way it comes out"), consistent with a just-delivered, not-yet-run notebook.
- `semantic_backup_second_role_chat_export.txt` — the accompanying conversation (converted via `pandoc` from
  `Semantic Backup_Second Role_08_08_Before clustering.docx`).
- `semantic_backup_layer_validation_with_Results.ipynb` — supplied in a later round, described by
  Sonia as "the notebook after run" (originally supplied as `Copie_de_semantic_backup_layer_validation.ipynb`
  — a reversed naming vs. the Q4/Q2 embedding round's convention, flagged at the time; **renamed in a
  still-later round to match that convention — see "A naming correction" below; content unchanged,
  confirmed by md5**). Real, populated `outputs` confirmed on every code cell by direct JSON
  inspection (CUDA/Drive-mount info, HF download logs, printed AUC tables, an embedded chart image) —
  **but every code cell's `execution_count` is still `None`**, a persisting anomaly that survives even in
  this "after run" copy (see "A real, quoted result exists" below — the anomaly means the conversation's own "cell
  13"/"cell 15" references still can't be cross-checked against actual cell positions in this notebook).
  Diffing its 11 code cells against the unexecuted original found exactly **one** differing cell — the
  `DATA_FOLDER` path drops a `refactory/` path segment
  (`f"{PROJECT_DIR}/refactory/data/question_5/code"` → `f"{PROJECT_DIR}/data/question_5/code"`), the same
  kind of Drive folder-path fix already found and logged in the Q4/Q2 embedding round. **Resolved
  2026-09-17**: per Sonia, stated directly in the audit conversation, this reflects two different working
  environments/Drive mounts used across the project — the `refactory/`-prefixed path belongs to whichever
  environment the unexecuted "template" copies came from; every actual execution, here and in the Q2/Q4
  round, ran from the other, prefix-free environment. See
  `../../provenance/detector-version-log.md`'s "A direct clarification from Sonia" section.
- `semantic_backup_bootstrap_summary.csv` — 10 rows (one per bootstrap run): `run, auc, novel_mean,
  novel_std, wrong_mean, wrong_std, n_novel, n_wrong`. `n_novel=43`, `n_wrong=108` on every run.
- `semantic_backup_pooled_scores.csv` — 1,510 rows (one per run × scored file): `run, file, group,
  similarity`.
- `chart_auc_stability_and_similarity_distributions.png` — the two-panel AUC-stability / similarity-
  distribution chart, extracted directly from the executed notebook's own embedded `image/png` cell output
  (base64-decoded from the `.ipynb` JSON) — the most primary source available, preferred over the visually
  identical (but byte-different, different export/resolution) chart image Sonia separately pasted into
  conversation.

## A real, quoted result exists — now independently reproduced from raw data and the executed notebook itself

The conversation quotes real printed output from "Result of cell 13" and "result of cell 15" of an actual run. The
originally-supplied notebook copy was confirmed unexecuted, so that mismatch could not be checked at all at
the time. **It still can't be fully resolved even now**: the later-supplied "after run" copy's 11 code
cells don't obviously map to cell indices 13/15 under any simple counting convention (0-indexed among code
cells: the bootstrap loop is the 8th code cell, the pooled-ROC calculation the 9th), and because every code
cell's `execution_count` is `None` in that copy too, there is no positional evidence to check the mapping
against — flagged as genuinely still open, not resolved by the executed notebook's arrival.

**What is now resolved:** the result itself. Both the two raw CSVs and the executed notebook's own printed
cell outputs were independently supplied in later rounds, and both were independently recomputed/read
directly (see `scripts/regenerate_semantic_backup_auc.py` and the log) — every figure below matches to
floating-point precision, with no discrepancy found anywhere. The executed notebook's real printed output
also included counts not previously confirmed in a file: `novel_correct` n=43, `genuinely_wrong` n=108 (per
run), Drive-mount and CUDA session info, and a **new, previously-never-supplied sanity-check similarity
pair** for the `codet5p-110m-embedding` backend's own model load: "related vs related: 0.8398723602294922 /
related vs unrelated: 0.3819599151611328" — a real, usable separation, unlike the `codebert` backend's
documented anisotropy failure elsewhere in this project.

**Quoted verbatim, the reported result:**

> First, the important correction: this is NOT "no separation." Look at the scale — AUC=0.5 means no
> separation (chance). AUC=0.098 is nowhere near 0.5; it's close to 0, at the opposite end of the scale
> from 1.0. An AUC near 0 means the model separates the two groups very well — just in the reverse
> direction from what the layer is designed to assume.
>
> Genuinely-wrong submissions are systematically more similar to the correct exemplars than the
> novel-correct submissions are [novel_correct mean similarity ~0.79–0.81; genuinely_wrong mean similarity
> ~0.94–0.96, every one of 10 runs]. And this isn't noise — std=0.039 on the AUC across 10 different
> exemplar draws is tight, meaning this reversal shows up no matter which 8 exemplars get picked.

> [cell 15] Pooled AUC across all 10 runs (1510 scored pairs): 0.097. Suggested threshold for ~80% recall
> on novel-correct: 0.719 (false-positive rate at this point: 0.997).

**Why, per the conversation's own explanation** (connecting to the paper's own §5.1 finding): most wrong-labeled
submissions in this dataset aren't wrong because they attempted something different — they correctly
implement the standard pattern and fail on an unrelated edge case, so they read as structurally close to a
"textbook" correct exemplar. `novel_correct` submissions, by definition, are doing something atypical —
that's the entire reason the AST rules missed them — so they read as *less* similar to a registry built
from typical correct examples, even though they behave correctly. As designed, "high similarity to a
correct exemplar" is actually a better signal for "attempted the standard approach" (correlating with
typical near-miss wrong submissions) than for "is correct."

**Deployment-relevance, also quoted:** to catch 80% of `novel_correct` submissions, the required threshold
(0.719) also flags 99.7% of `genuinely_wrong` submissions — as designed, this mechanism would not function
as a useful filter; it would tell a human reviewer to look at essentially everyone.

## Evidence status: `real_csv` — a real, strong, deployment-relevant finding, now independently reproducible

This is the **first real AUC/ROC number this project has ever produced** for the semantic backup layer's
actual novel-vs-wrong separation task — resolving, with an honest inverted-negative answer, a gap flagged
repeatedly since the `semantic-colab-validation` checkpoint (~2026-07-29/30) ("no valid AUC yet"). Originally
only the conversation's own pasted printed output was supplied (`evidence: conversation_reported_only`); in later rounds,
both raw CSVs (`semantic_backup_bootstrap_summary.csv`, `semantic_backup_pooled_scores.csv`) and the
executed notebook itself arrived and were independently verified — recomputing per-run AUC/group means
directly from the 1,510 raw pooled-scores rows, reproducing the bootstrap summary's own values, the mean/SD
across runs, the pooled AUC, and the 80%-recall threshold, all via a from-scratch (no-sklearn-dependency)
AUC/ROC implementation in `scripts/regenerate_semantic_backup_auc.py` — every figure matches to
floating-point precision. See `configs/stage_manifest.yaml`'s
`semantic_backup.backends.codet5p_bootstrap_novel_vs_wrong_auc` entry, now `status:
REAL_INVERTED_RESULT_CSV_BACKED`.

**Still genuinely open, not resolved by this upgrade:** the persisting `execution_count=None` anomaly on
every code cell, even in the notebook explicitly supplied as "after run" — meaning the conversation's own "cell
13"/"cell 15" numbering still cannot be independently cross-checked against real cell positions (see
above).

**Not the same experiment as** `configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits`/`q5_topk_splits`
(still entirely unsupplied) or the Q4/Q2/Q5 embedding-*taxonomy* cross-validations
(`q{4,2,5}_taxonomy_embedding_crossvalidation_*`, which test agreement with an *existing* AST split, not
this layer's actual novel-vs-wrong job).

## A naming correction — Sonia re-supplied both notebooks renamed to fix the earlier flagged inconsistency

The previous round's evidence-tier upgrade flagged, explicitly and without guessing at a resolution, that
the executed notebook had arrived named `Copie_de_semantic_backup_layer_validation.ipynb` — the reverse of
the Q4/Q2 embedding round's own convention, where `Copie_de_...` denoted the *unexecuted*, outputs-stripped
copy. In a later round, Sonia re-supplied both notebooks with corrected filenames, her own message reading
"here the two files renamed as the first ones, to keep the same nomination": the unexecuted copy renamed to
`Copie_de_semantic_backup_layer_validation.ipynb`, and the executed copy renamed to
`semantic_backup_layer_validation_with_Results.ipynb` — now matching the Q4/Q2 convention exactly
(`Copie_de_q2_q4_embeddings_crossvalidation.ipynb` / `q2_q4_embeddings_crossvalidation_with_Results.ipynb`).

**Verified via `md5sum` that this is a pure rename, not new content**: both re-supplied files are
byte-identical to the files already in this repository under their old names. No figure, output, or cell
content changed. This repository's own copies were renamed to match, and every reference to these two
filenames elsewhere in this repo (this README, `configs/stage_manifest.yaml`,
`provenance/detector-version-log.md`) was updated accordingly. The historical log entries describing the
original (differently-named) uploads are preserved as written, with a forward note added rather than
silently rewritten — consistent with this project's practice of stating corrections plainly rather than
overwriting prior entries.

## The paper's new §7 does NOT yet include this finding

The same round's paper revision (`../../papers/2026-08-08_Structural_Competency_Extraction_Paper.docx`,
see `../../papers/README.md`) adds a new §7, "The Semantic Backup Layer: Architecture Overview" — a purely
descriptive section explicitly stating "Nothing in this section constitutes a validated result... its
actual accuracy... [is] addressed empirically in the companion paper, not here." The inverted-AUC finding
documented above is not yet reflected there — consistent with the conversation's own framing that this result
belongs in the still-unsupplied companion paper, not this structural paper. (This remains true of that
specific revision; a still-later, same-day revision does fold in a *related but distinct* finding from
this checkpoint's own clustering extension below — see "The clustering extension.")

## The clustering extension — a real §11, added in a still-later round, that led directly to a code fix

Supplied alongside `Chat_Semantic_Backup_Second_Role_08_08_After_clustering.docx` (no internal date header
of its own; dated by the same-day chain of internal metadata described in
`../q5-delegation-clustering-fix/README.md`): two more notebook files —
`Copie_de_semantic_backup_layer_validation_after_clustering.ipynb` (32 cells, 16 code, confirmed entirely
**unexecuted** by direct JSON inspection — every code cell's `execution_count` is `None` and every code
cell's `outputs` list is empty) and
`semantic_backup_layer_validation_after_clustering_with_Results.ipynb` (34 cells, 18 code, real populated
outputs on 14 of 18 code cells — the remaining 4 are genuinely empty markdown-adjacent or import-only
cells with nothing to print, confirmed by direct inspection, not a gap). **The same persisting anomaly as
every other executed notebook in this project**: every code cell's `execution_count` is still `None`
despite the real outputs.

**What §11 adds** (three new subsections, reusing the embeddings already cached in §7 — no new model
calls): §11.1 a hierarchical-clustering dendrogram (cosine distance); §11.2 a silhouette-score sweep over
k=2..9 to pick a cluster count, then real per-cluster file listings; §11.3 a quantified-tightness check
(mean pairwise similarity within each cluster vs. `genuinely_wrong`'s own internal tightness as a
baseline). A 7th code cell, `from scipy.cluster.hierarchy import fcluster` (a distance-threshold cut,
`DISTANCE_THRESHOLD = 0.30`), was added interactively during the conversation session itself, after the notebook
was first delivered — present only in the executed copy (18 code cells vs. the unexecuted copy's 16).

**A real methodological catch, verified directly against the notebook's own printed output, not just
quoted from the conversation**: the silhouette sweep alone picked k=9 (silhouette scores, k=2 through k=9:
0.389, 0.440, 0.488, 0.531, 0.536, 0.545, 0.508, 0.599 — still rising at the edge of the tested range, the
textbook signature of silhouette overfitting toward small clusters on a modest sample size, n=43). Cutting
the same dendrogram by distance threshold (0.30) instead — reading the merge heights directly — recovered
a starkly different, and on manual file-reading, correct picture: **4 clusters** — `{correct_5_192,
correct_5_247}` (2 files), `{correct_5_011, correct_5_016}` (2 files), one dominant **38-file** cluster,
and `{correct_5_029}` (1 file, singleton). This exact cluster membership was independently extracted
directly from the executed notebook's own output cell and confirmed to match the source conversation's quoted
listing file-for-file.

**The dendrogram chart** (`chart_novel_correct_dendrogram.png`) was extracted directly from the executed
notebook's own embedded `image/png` cell output — visually identical to the two chart images Sonia pasted
directly into conversation in the same round (not byte-compared, since conversation-pasted images go through a different
export pipeline than a notebook's own embedded output, the same non-discrepancy already established for
the AUC section's chart in the prior round).

**Reading real files from the 38-file cluster is what produced the actual fix**: `top_k` itself, in every
file in that cluster, does nothing but call a differently-named helper and slice the result
(`return sort_descending(lst)[:k]`), so function-scoped resolution correctly finds zero loop/test/removal
inside `top_k` — the real work happens one function away, somewhere the resolver had never been told to
look. Two distinct sub-shapes were found within the cluster (some helpers repeat TopKPattern's own
find-max/remove/append shape verbatim; others use a structurally unrelated general sort, e.g. recursive
`merge_sort`, then slice) — leading directly to the `TopKViaDelegate`/`SortThenSlice`/`TopKPatternExtended`
fix documented in full, with independent verification, at
`../q5-delegation-clustering-fix/README.md`.

**Evidence tier for the clustering step itself: `real_notebook_output`, not `real_csv`.** Unlike the AUC
section (§§1-10), no standalone embeddings, distance-matrix, or cluster-membership CSV was ever saved by
this notebook — the dendrogram image and the printed cluster listings are the only preserved artifacts,
extracted directly from the executed notebook's own real output. The downstream *code fix* this clustering
led to (`../q5-delegation-clustering-fix/`) is independently `real_csv`-verified against its own
batch-report CSV; the clustering discovery step that motivated it is not independently re-derivable from
any smaller raw data file in this repository, only auditable by reading this notebook's own real output
directly, which this repository preserves in full.

## A fifth paper revision (still 2026-08-08) DOES fold in this finding

Unlike the §7-only revision above, `../../papers/2026-08-08_Structural_Competency_Extraction_Paper_after_clustering.docx`
(created 2026-08-08T14:06:13Z, ~3h07m after the §7 revision) adds the full Q5 delegation-clustering story
to §5.3, updates Table 4's Q5 row to `TopKPatternExtended` (91.9%/80.6%), adds a design-principle paragraph
to §6 Discussion explicitly naming clustering's methodological role (per Sonia's own request to highlight
it), and adds an honest, uncharacterized-false-positive paragraph to §8 Limitations. See
`../../papers/README.md`'s "A fifth revision, same day" section for the complete diff.
