#!/usr/bin/env python3
"""Regenerate the intermediate Question 5 percentages quoted across this project's conversation exports and
paper drafts.

Question 5 has the most reported intermediate stages of any question, because it was the stress test
for the function-scoping fix and, independently, the only question with real supplied batch CSVs. This
script walks every q5_* stage in configs/stage_manifest.yaml in the real, evidence-grounded order —
    83.0% (whole-file, pre-scoping-fix)
    -> 78.2% (function-scoped, TopKPattern alone — real CSV)
    -> 82.1% (whole-file, re-run after TopKPattern's later level-layering refactor — conversation-reported only)
    -> 91.9% (function-scoped, TopKPatternExtended = ANY(TopKPattern, TopKViaDelegate, SortThenSlice) —
       real CSV; see q5_final_extended below)
so the progression is regenerable stage-by-stage where data exists, and clearly marked PENDING where it
does not, rather than silently skipped or crashing the whole run.

A remarkable, purely coincidental footnote, worth recording precisely rather than glossing over: an
earlier version of this script's docstring and stage list described a DIFFERENT progression, at the time
explicitly fabricated with no basis in any real artifact -- "83.0% -> 78.2% -> 79.7% -> 91.9%", ending in
a "final" stage motivated by a "nonexistent DELEGATES/SELF_RECURSIVE taxonomy extension." Months later,
real, independent work -- an embedding-clustering discovery pass over Q5's own uncharacterized "novel"
population, entirely unrelated to and unaware of that earlier guess (see
provenance/detector-version-log.md's "Q5 delegation fix via embedding-guided clustering" section) -- produced
a real fix using exactly those ingredients: a real DELEGATES-based TopKViaDelegate competency, a real new
SELF_RECURSIVE primitive, and a real 79.7% -> 91.9% correct-side coverage jump (see q5_final_extended
below). This is flagged as a striking coincidence, not as vindication of guessing -- every OTHER specific
claim in that same earlier fabricated version (the NESTED/SEQUENTIAL/SHARED_BINDING mechanism guesses,
the Table-5 embedding-validation numbers, the semver ladder) remained wrong, and this script's own
progression above differs from the old guess in real, load-bearing ways (82.1% sits in between here, and
the real fix's wrong-label figure, 80.6%, was never guessed at all). See ../VERSIONING.md's "Corrected
from an earlier, guessed version" note and ../provenance/detector-version-log.md for the full writeup.

Usage:
    python scripts/regenerate_q5_percentages.py --all-stages
    python scripts/regenerate_q5_percentages.py --stage q5_final
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.config import coverage_pct, get_stage, load_labels_scores, load_stage_manifest  # noqa: E402

Q5_STAGE_ORDER = [
    "q5_whole_file",
    "q5_final",
    "q5_unscoped_post_refactor",
    "q5_final_extended",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--all-stages", action="store_true", help="Print every Q5 stage listed above, in order.")
    parser.add_argument("--stage", default=None, help="Print a single stage id.")
    args = parser.parse_args()

    manifest = load_stage_manifest()
    threshold = manifest["coverage_threshold"]

    stage_ids = Q5_STAGE_ORDER if (args.all_stages or not args.stage) else [args.stage]

    print(f"{'Stage':<28}{'Taxonomy':<38}{'Detector':<32}{'Scoping':<16}{'Correct':>14}{'Wrong':>14}")
    print("-" * 150)
    for stage_id in stage_ids:
        stage = get_stage(manifest, stage_id)
        try:
            rows = load_labels_scores(stage["data_file"])
        except (FileNotFoundError, ValueError) as exc:
            print(f"{stage_id:<28}{'-- PENDING, not yet regenerable --':<38}  ({exc.__class__.__name__}: {stage.get('source', 'no source cited')})")
            continue
        correct_pct, _, n_c = coverage_pct(rows, "correct", threshold)
        wrong_pct, _, n_w = coverage_pct(rows, "wrong", threshold)
        print(
            f"{stage_id:<28}{stage['taxonomy_checkpoint']:<38}{stage['detector_checkpoint']:<32}"
            f"{stage['scoping_mode']:<16}{correct_pct:>10.1f}% n={n_c:<3}{wrong_pct:>10.1f}% n={n_w:<3}"
        )
        reported = stage.get("reported_value_pct")
        reported_wrong = stage.get("reported_wrong_label_pct")
        if reported:
            print(f"{'  (reported)':<28}{'':<38}{'':<32}{'':<16}{reported:>15}{(reported_wrong or ''):>15}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
