# Taxonomy design notes

Carried over from project documentation, for anyone extending the taxonomy:

- A taxonomy entry is a pedagogical judgment call ("what skill does this demonstrate") expressed in the
  detector's query language — not the reverse. The detector's vocabulary should never drive what gets
  defined as a competency.
- Equivalence between two implementation strategies (e.g. `BubbleSortPass` vs. `TopKPattern` both
  satisfying `SortByKey`) is made explicit via `ANY`, not inferred from whichever detector happens to be
  built first. This keeps the decision visible, reversible, and per-branch evidence inspectable.
- Any taxonomy entry built from a reference solution's own strategy, rather than checked against real
  submissions, should be treated as provisional until batch-validated (§5.3's central methodological
  point — this is exactly what happened with the original `BubbleSortPass`-only `SortByKey`).
- A shared competency library, checked against real code from unrelated problems, is a load-bearing
  design decision: `TopKPattern` (built for Q5) transferred to Q4 with zero new code; `FindExtremum`
  transferred to an unrelated live-course assignment (longest-string-in-a-list) with zero modification.
  Competencies should be defined at the level of the underlying skill, not the surface problem they were
  first built for.
