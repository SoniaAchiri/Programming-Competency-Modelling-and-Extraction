# Detector snapshot — "V1.2.0.rar" (merges 2026-07-19 through 2026-07-21)

The merged endpoint of two rounds of work: multi-way branching / cross-function delegation (same day as
`ex2_3_4`), and per-file-vs-per-function scoping (2026-07-21, per the conversation's own date marker).

- `EXHAUSTIVE_CHAIN` constraint added (walks an `if/elif/.../else` chain directly from the raw AST,
  rather than composing it in the DAG — composing it failed past depth 1, since a composite
  Evidence.node is always None).
- `DELEGATES` now actually wired in: `function_index`, inline `CALL` evidence detection, `ctx` threaded
  through `resolve()`. New competency: `DelegatesUniqueness` (Q2's `contains_unique_day` -> `unique_day`).
- Per-function scoping: `Evidence.scope` field, `_ParentIndex.enclosing_function()`, resolver rejects any
  combination spanning >1 non-None scope. Two real bugs fixed along the way (canonical bugs #10, #11).

See `../../provenance/detector-version-log.md`, section "## V1.2.0" for the full bug-by-bug account.
