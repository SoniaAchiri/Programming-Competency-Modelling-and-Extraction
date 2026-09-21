# Level enforcement + Q1's LinearSearch — "files_Enforcement" + "q1_competencies.py" (2026-07-28)

`level()`/`child_levels()`/`check_layering()` added to `CompetencyModel`; `register()` now raises
`LayeringViolation` on a new mixed-level registration unless `allow_mixed_levels=True`. All 4
previously-named violators (`TopKPattern`, `BubbleSortPass`, `CountedSearch`, `Average`) marked with the
flag — this is the "turn on enforcement with all 4 exceptions" state, not yet the "down to 1" state
(`files_Fix_Q4`, next). `q1_competencies.py`: `LinearSearch` registered as an independent, all-primitive
competency (deliberately not a wrapper around `GuardedInput`, despite identical structure — see the
file's own comment). Per the 28/07 methodology note, later validated against the full Q1 dataset (1,343
submissions, 1,342 usable): zero mismatches against `GuardedInput`.

See `../../provenance/detector-version-log.md`, section "## Enforcement + Q1's LinearSearch".
