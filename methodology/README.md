# Internal methodology note (real, dated, substantially rewritten) — files withheld, paper not yet published

**Updated 2026-09-19: the raw methodology-note files (`.docx`/`.pdf`) have been removed from this public
repository**, for the same reason as `../papers/README.md` — the companion paper is not yet published, and
this file's earlier practice of quoting verbatim passages from the note would have exposed unpublished
material on GitHub. What's preserved below: the real, independently-established dates, exactly what
changed at a structural level, and citations to whatever in this repo independently verifies each figure.

`2026-08-04_Competency_Extraction_Methodology.docx` (and its `.pdf` sibling) is Sonia's internal
methodology note, confirmed genuine via `python-docx` (127 paragraphs) — supplied and read in full
2026-09-12, alongside the second paper revision in `../papers/2026-08-04_Structural_Competency_Extraction_Paper.pdf`
(both dated the same day: the paper's own `CreationDate` is 2026-08-04 16:28 UTC, this docx's
`dcterms:created` is 2026-08-04 18:03 UTC — the methodology note was regenerated roughly 90 minutes after
the paper).

**Update, same round:** `2026-08-05_Competency_Extraction_Methodology.docx`/`.pdf` supersede this file —
see "The 2026-08-05 revision — bug #22, the Q1 fix" below. Both are kept, since each is a real, dated
snapshot in its own right.

This 2026-08-04 version supersedes, but does not replace in this repository, two earlier methodology-note
versions already logged in `provenance/detector-version-log.md`:

- `Competency_Extraction_Methodology_V24.docx` (104 paragraphs, 6 tables)
- The 28/07 methodology note (`Competency_Extraction_Methodology.docx`, at that time actually plain-text
  Markdown despite its `.docx` extension — see the log's file-format note)

Neither earlier version is copied into this repository yet; only this 2026-08-04 version is preserved
here so far. Ask Sonia if a future round should backfill the earlier versions too.

## What changed: the canonical bug table grew from 19 to 21 entries

The most significant real, code-confirmed change: this version's own numbered bug table now runs #1
through #21, up from the 19-entry table logged from the 28/07 methodology note. The two new entries:

- **Bug #20** — Q3's `.insert()` detection gap
- **Bug #21** — Q4's `SortByKey` taxonomy correction

Both are formalizations of findings this project's log already carried as narrative-only prose (from
earlier checkpoints' own conversation descriptions) — this is the first time either one appears as a formally
numbered, canonical table entry. See `../provenance/detector-version-log.md`'s "The internal methodology note,
substantially rewritten" section for the exact quoted text of both new entries and the full section
renumbering (§1 Motivation through §10 Conclusion, with a new §2.11.1).

## An explicitly unresolved discrepancy, sharpened rather than fixed by this new evidence

This 21-entry table has #1-21, of which only #15 is explicitly self-described as "not a defect in the
model" (i.e., informational rather than structural) — by this table's own accounting, that is 20
structural + 1 informational = 21. The published paper's own Table 4 text (unchanged by this round's
paper revision) still says its table groups "nineteen structural defects... a further two informational
script bugs... are omitted," implying 19 structural + 2 informational = 21. These two "19"s and "21"s do
not obviously refer to the same accounting on a like-for-like basis. If anything, this round's two new
bugs sharpen the discrepancy rather than resolve it, since both #20 and #21 are genuinely structural, not
informational, and the paper's Table 4 body text was not updated this round even though the methodology
note's own table grew by two entries. **Flagged as still open in `provenance/detector-version-log.md`; no
document names what the paper's stated second informational bug actually is.**

## The 2026-08-05 revision — bug #22, the Q1 fix

`2026-08-05_Competency_Extraction_Methodology.docx`/`.pdf` (143 paragraphs, 7 tables, confirmed via
`python-docx`; `dcterms:created`/`modified` 2026-08-05T13:58:00Z, matching the PDF's own `pdfinfo`
`CreationDate` 13:58:02 UTC to the second) is the same-day continuation of the batch-validation run logged
at `../detectors/q1-q4-batch-validation/` and the fix at
`../detectors/q1-shared-binding-fix/`. Real, code-confirmed changes:

**Note (2026-09-19): this list originally quoted the note verbatim in several places. Replaced with a
paraphrase**, for the reason stated at the top of this file.

- **New §5.2, "Extending batch validation further: Q1"** — the full diagnostic narrative (76.8%/64.2% →
  99.5%/97.6%, 383 zero-scores split into 19 genuine gaps + 364 structural-detector misses across three
  quantified mechanisms), in more depth than the paper's own condensed §5.3 (splits the compound/chained
  category into its two sub-counts, 107 and 50, rather than merging them into one 43%/157-file figure). The
  section closes by restating the post-fix residual gap (0.5% correct, 2.4% wrong) against the pre-fix
  starting point — with **a minor rounding slip in that closing sentence's own arithmetic**: 100 − 64.2 =
  35.8, not the 35.7 the note states (100 − 76.8 = 23.2 is correct). Flagged, does not affect any
  CSV-verified figure.
- **§6.1 corrected** (an overclaiming statement removed): the old text claimed GuardedInput matched "every"
  real Q1 submission tested; the revised text drops that overclaim in favor of just stating the
  structural-shape relationship to `search`, plus a forward-pointer to §5.2.
- **New canonical bug #22** (table now #1-22, up from #1-21) — same symptom/root-cause/fix already
  described above (`GuardedInput`/`LinearSearch` scoring 0 on 364 of 383 zero-scoring real Q1 submissions
  despite every required primitive being present), matching the code-confirmed change at
  `../detectors/q1-shared-binding-fix/`. **Correctly says "383," not "526"** — confirming the "526" typo
  found in `test_real_data.py`'s own code comment (see that checkpoint's README) is isolated to the source
  code and does not appear in this canonical table.
- **New §9 Limitations bullet** — restates the post-fix residual gap (0.5% correct, 2.4% wrong) as the
  genuine coverage-gap portion identified from the start. (This "19" is the pre-fix count — the real
  post-fix `q1_report.csv` shows 17 genuine-gap rows plus 1 unrelated parse-error row; see
  `provenance/detector-version-log.md`'s "17 vs 19" reconciliation, derived independently, not stated in any
  document.)
- **Confirmed, per the accompanying conversation's own explicit exchange, that the consolidated Table 4 added to
  the paper this round (see `../papers/README.md`) was NOT added here** — Sonia asked whether the same
  table should go into the methodology doc too, and the answer was no, it belongs only in the paper. This
  is why this doc's page count (28) is unchanged between the paper's two successive revisions this round.
