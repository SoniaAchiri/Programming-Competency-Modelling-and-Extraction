# Detector snapshot — "Test real data_Q2_3_V1.0.0" (2026-07-18)

Real date confirmed by the matching conversation-history checkpoint marker ("18/07/2026 — step back and use
what exists" in `I want to define a structure of competencies.docx`).

Baseline: 8 primitive detectors (`DECL`, `INPUT`, `PARAM`, `OUTPUT`, `TEST`, `LOOP`, `ASSIGN`,
`BUILTIN_REDUCE`); coverage rules `ALL`/`ANY`/`K_OF_N`/`WEIGHTED`; structural constraints `NESTED`,
`SEQUENTIAL`, `SHARED_BINDING`, `SELF_REFERENTIAL`, `TUPLE_SWAP`, `AND`, `OR`, `COOCCUR`. Whole-file
scanning throughout — no per-function scoping yet. Registered competencies: `Accumulation`, `Swap`,
`GuardedInput`, `SelectionStep`, `FindExtremum`, `TopKPattern`, `ConditionalCount`, `BubbleSortPass`.
No `LinearSearch`, no `SortByKey` composite, no `DELEGATES`/`CALL` (sketched but not wired in).

Full narrative, real fixes already incorporated (bugs #1-4 in the canonical bug table), and validation
scope: see `../../provenance/detector-version-log.md`, section "## V1.0.0".
