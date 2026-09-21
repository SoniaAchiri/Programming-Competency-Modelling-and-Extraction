# Detector snapshot — "files_ex1_taxo" (2026-07-19)

Applies the shared model to a different course's exercises (PW01, Ex1-Ex4). Adds `FUNC_DEF`
primitive, `LOOP.kind` binding, `REFERENCES`/`CONTAINS_TEXT` constraints, and a `DELEGATES` constraint
class that is present in code but **confirmed not wired into the resolver yet** (no `CALL` primitive, no
`function_index`, `ctx` unused) — dead code at this checkpoint, wired in two checkpoints later.

New competencies (`pw01_competencies.py`): `IsPrime`, `CountedSearch`, `CollectInput`, `Average`.

See `../../provenance/detector-version-log.md`, section "## ex1_taxo".
