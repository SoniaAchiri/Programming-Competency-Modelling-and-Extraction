# Q2 fix, part 1 — "files_fixQ2" (2026-07-28, per the paired conversation export's trailing marker 18:42)

`is_simple_init` widened to accept `ast.Tuple` (so `all_days = ()` registers as `DECL`). A 37-line
"DESIGN PRINCIPLE (documented convention, NOT enforced)" comment defining competency level() is appended
to `competency.py` — comment only, no `level()`/`check_layering()`/`allow_mixed_levels` code yet. New file
`q2_competencies.py`: `OutputStep`, `AccumulateThenCount` (the real second Q2 strategy), `UniqueCheck =
ANY(ConditionalCountStep, AccumulateThenCount)` — two strategies at this point.

`level2_examples_standalone/level2_examples.py` is a standalone upload (not part of this zip) — directly
executed in this session against this checkpoint's framework; both `ValidatedAccumulation` and
`AverageStrict` reproduce every conversation-quoted figure exactly. See the dedicated writeup in the log.

See `../../provenance/detector-version-log.md`, section "## Q2 fix + third strategy", subsections 1 and 5.
