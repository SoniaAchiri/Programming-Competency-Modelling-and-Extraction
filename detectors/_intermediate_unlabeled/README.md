# Two standalone, undated intermediate saves — bounded but not pinned

Both files were uploaded standalone (no accompanying zip or conversation doc), so neither carries a date marker
of its own. Both are bounded to a real window by direct diff against neighboring checkpoints; kept
separate from the dated checkpoint folders above rather than force-fit into one.

- `competency_between_V1.2.0_and_fixQ2.py` — diffed directly against `V1.2.0`'s `competency.py`: it is
  *exactly* V1.2.0 plus the 37-line DESIGN PRINCIPLE (level concept) comment appended, and nothing else.
  Diffed against `files_fixQ2`'s own saved `competency.py`, the two differ by exactly one line: this file's
  `is_simple_init` check is still missing the `ast.Tuple` case that `fixQ2` has. Captures the literal
  moment between two edits within the same working session — strictly after `V1.2.0` (2026-07-21), strictly
  before `files_fixQ2`'s own trailing marker (2026-07-28, 18:42). Directly executed in this session to
  confirm the exact consequence (see the log).

- `test_real_data_standalone_from_fixQ4_round.py` — uploaded standalone alongside the `files_Fix_Q4.zip`
  round; same line count (224) as `files_Enforcement`'s `test_real_data.py` but not byte-identical —
  diffed to be the source of the `TopKPattern` level-fix (`LoopStep2`/`RemovalAssignStep`) that
  `files_Fix_Q4.zip`'s own 249-line `test_real_data.py` builds on by adding `SortByKey`.

See `../../provenance/detector-version-log.md`, section "## Q2 fix + third strategy" §1 (the first file) and
"## \`files_Fix_Q4\`..." (the second).
