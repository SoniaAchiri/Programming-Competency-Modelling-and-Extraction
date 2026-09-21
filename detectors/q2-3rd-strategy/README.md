# Q2 fix, part 2 — "files_Q2_competencies_3rd strategie" (2026-07-28, same round as fixQ2)

Adds the functional `map()`/`filter()` strategy: three sub-shape competencies (`InlineFunctionalCheck`,
`GuardedFunctionalCheck`, `InlineTestFunctionalCheck`) composed as `FunctionalUniqueCheck`.
`UniqueCheck` redefined to `ANY(ConditionalCountStep, AccumulateThenCount, FunctionalUniqueCheck)` — three
same-level (level 2) siblings. Per the paired conversation export (`The_output_Results_26.docx`), validated against
all 291 real Q2 submissions, function-scoped: 85.2% / 0.7% / 4.5% -> 90.4% combined. **No batch
script/CSV for this specific run was ever supplied** — the figures are conversation-reported only, though now
independently corroborated by three separate documents (see the log).

See `../../provenance/detector-version-log.md`, section "## Q2 fix + third strategy", subsections 2-3.
