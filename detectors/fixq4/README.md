# TopKPattern level-fix + Q3/Q4 — "files_Fix_Q4" (2026-07-28, 04:03 per the zip's own preserved mtimes)

`TopKPattern` refactored via three lifting-wrapper competencies (`LoopStep`, `LoopStep2`,
`RemovalAssign`/`RemovalAssignStep`) so all three of its components are level 2 — clean level 3, its
`allow_mixed_levels` flag removed. `BubbleSortPass` remains the sole exception (a genuine resolver
limitation: two sibling slots needing the same wrapped competency resolve once and share a `Result` —
canonical bug #19, not fixed). `NESTED.score()`'s same-evidence guard fixed
(`outer_ev.node is not inner_ev.node` -> `outer_ev is not inner_ev`) — necessary for the `TopKPattern`
refactor above to work; per the 28/07 methodology note this fix was actually *discovered* via
`CountedSearch`'s own restructuring (canonical bug #18), one checkpoint earlier, and reused here — not
independently found via `TopKPattern`, correcting this log's own earlier inference. `.insert()` added
to `ASSIGN`'s recognized mutations (the Q3 fix, 93.6%->94.0%). `SortByKey = ANY(BubbleSortPass,
TopKPattern)` registered (the Q4 fix, 13.1%->64.4%->77.6% combined) — comment quotes the same figures as
`Q3_Q4_Results_28.docx` and the finished paper's §5.5 almost verbatim. **No batch script/CSV for the
Q3 or Q4 figures has been supplied by any source.**

See `../../provenance/detector-version-log.md`, sections "## Enforcement..." (bug #18/#19 correction, in the
newer "28/07 methodology note" section) and "## \`files_Fix_Q4\`...".
