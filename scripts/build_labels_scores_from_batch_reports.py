#!/usr/bin/env python3
"""Mechanically derive data/labels_scores/*.csv from a real per-question batch report CSV.

The batch reports Sonia's own run of the detector produces (topk_report.csv for Q5,
q1_report.csv/q2_report.csv/q3_report.csv/q4_report.csv for Q1-Q4, all real, unedited files supplied
into this project) share one shape: one row per submission file, `file`/`label`/`error` columns, and a
pair of `{Competency}_final`/`{Competency}_missing` columns per competency registered against that
question. This script converts that shape into this repo's own labels_scores schema (see
data/labels_scores/README.md) — one row per submission per TARGET competency — without touching or
re-deriving any of the underlying numbers themselves.

The raw batch reports never separated a coverage score from a structural score (only a single 0/1
`{Competency}_final` per submission, plus which named slot(s) were `missing` when it was 0). This
script does NOT invent that split: `coverage_score` and `structure_score` are both conservatively
backfilled from `final_score`, exactly as was already done by hand for q5_final.csv in an earlier round
(see that file's own `notes` column) — this script makes that same, previously ad hoc transform explicit
and re-runnable for Q1 through Q4, plus TWO Q5 entries: the original q5_final.csv (target competency
TopKPattern alone, from detectors/reporting-batch/topk_report.csv — until 2026-09-19 this file was
hand-built with no regeneration path of its own; it is now built by this script like every other
question) and the later-added q5_final_extended.csv (target competency TopKPatternExtended, from the real
post-delegation-fix batch report topk_report_EXTENDED2.csv). Both Q5 outputs are kept, since both are
real, independently-dated checkpoints; see configs/stage_manifest.yaml's q5_final vs q5_final_extended.
`--question 5` (and `--all`) now build both files.

Usage:
    python scripts/build_labels_scores_from_batch_reports.py --question 1
    python scripts/build_labels_scores_from_batch_reports.py --all
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Each entry: source batch-report CSV (relative to repo root), the column(s) that hold the raw
# per-submission score for the TARGET competency this stage reports on, and (for an ANY-composed
# target) the branch columns to check, in priority order, to fill in `matched_branch`.
QUESTION_CONFIG = {
    1: {
        "source": "detectors/q1-q4-batch-validation/q1_report.csv",
        "target_competency": "GuardedInput",
        "target_final_col": "GuardedInput_final",
        "target_missing_col": "GuardedInput_missing",
        "branch_cols": [],
        "output": "data/labels_scores/q1_final.csv",
        "note": (
            "derived from detectors/q1-q4-batch-validation/q1_report.csv (post-SHARED_BINDING/"
            "all_names fix); raw file recorded only GuardedInput_final/_missing (and an identical "
            "LinearSearch_final/_missing pair, confirmed byte-identical across every row in this repo's "
            "own verification -- see provenance/detector-version-log.md), not separate coverage/structural "
            "scores -- coverage_score and structure_score columns are populated from final_score as a "
            "conservative stand-in, not independently measured"
        ),
    },
    2: {
        "source": "detectors/q1-q4-batch-validation/q2_report.csv",
        "target_competency": "UniqueCheck",
        "target_final_col": "UniqueCheck_final",
        "target_missing_col": "UniqueCheck_missing",
        "branch_cols": [],
        "output": "data/labels_scores/q2_final.csv",
        "note": (
            "derived from detectors/q1-q4-batch-validation/q2_report.csv; raw file recorded "
            "only UniqueCheck_final/_missing (a directly-registered competency, not itself an ANY of the "
            "sibling ConditionalCount/AccumulateThenCount columns also present in that file), not separate "
            "coverage/structural scores -- coverage_score and structure_score columns are populated from "
            "final_score as a conservative stand-in, not independently measured"
        ),
    },
    3: {
        "source": "detectors/q1-q4-batch-validation/q3_report.csv",
        "target_competency": "SelectionStep",
        "target_final_col": "SelectionStep_final",
        "target_missing_col": "SelectionStep_missing",
        "branch_cols": [],
        "output": "data/labels_scores/q3_final.csv",
        "note": (
            "derived from detectors/q1-q4-batch-validation/q3_report.csv (post-.insert() fix); "
            "raw file recorded only SelectionStep_final/_missing, not separate coverage/structural scores "
            "-- coverage_score and structure_score columns are populated from final_score as a "
            "conservative stand-in, not independently measured"
        ),
    },
    4: {
        "source": "detectors/q1-q4-batch-validation/q4_report.csv",
        "target_competency": "SortByKey",
        "target_final_col": "SortByKey_final",
        "target_missing_col": "SortByKey_missing",
        "branch_cols": ["BubbleSortPass_final", "TopKPattern_final"],
        "output": "data/labels_scores/q4_final.csv",
        "note": (
            "derived from detectors/q1-q4-batch-validation/q4_report.csv; SortByKey = "
            "ANY(BubbleSortPass, TopKPattern) -- matched_branch is filled in from whichever of "
            "BubbleSortPass_final/TopKPattern_final is >0 in the same row, in that priority order; raw "
            "file recorded only *_final/_missing pairs, not separate coverage/structural scores -- "
            "coverage_score and structure_score columns are populated from final_score as a conservative "
            "stand-in, not independently measured"
        ),
    },
    5: [
        {
            "source": "detectors/reporting-batch/topk_report.csv",
            "target_competency": "TopKPattern",
            "target_final_col": "TopKPattern_final",
            "target_missing_col": "TopKPattern_missing",
            "branch_cols": [],
            "output": "data/labels_scores/q5_final.csv",
            "note": (
                "derived from detectors/reporting-batch/topk_report.csv; raw file recorded only "
                "TopKPattern_final (and _missing, the unsatisfied slot names), not separate "
                "coverage/structural scores -- coverage_score and structure_score columns are populated "
                "from final_score as a conservative stand-in, not independently measured"
            ),
        },
        {
            "source": "detectors/q5-delegation-clustering-fix/topk_report_EXTENDED2.csv",
            "target_competency": "TopKPatternExtended",
            "target_final_col": "TopKPatternExtended_final",
            "target_missing_col": "TopKPatternExtended_missing",
            "branch_cols": ["TopKPattern_final", "TopKViaDelegate_final", "SortThenSlice_final"],
            "output": "data/labels_scores/q5_final_extended.csv",
            "note": (
                "derived from detectors/q5-delegation-clustering-fix/topk_report_EXTENDED2.csv; "
                "TopKPatternExtended = ANY(TopKPattern, TopKViaDelegate, SortThenSlice) -- matched_branch is "
                "filled in from whichever of TopKPattern_final/TopKViaDelegate_final/SortThenSlice_final is "
                ">0 in the same row, in that priority order (note: in the real data, TopKViaDelegate never "
                "fires without SortThenSlice also firing on the same row -- see "
                "provenance/detector-version-log.md's 'Q5 delegation fix' section). This supersedes q5_final.csv's "
                "own 78.2%/75.0% TopKPattern-only figure as Table 4's reported headline for Q5, but does NOT "
                "replace that file -- both are preserved as real, independently-dated checkpoints (see "
                "configs/stage_manifest.yaml's q5_final vs q5_final_extended stage entries). Raw file recorded "
                "only *_final/_missing pairs, not separate coverage/structural scores -- coverage_score and "
                "structure_score columns are populated from final_score as a conservative stand-in, not "
                "independently measured."
            ),
        },
    ],
}


def build_one(question: int) -> None:
    cfgs = QUESTION_CONFIG[question]
    if isinstance(cfgs, dict):
        cfgs = [cfgs]
    for cfg in cfgs:
        build_one_config(question, cfg)


def build_one_config(question: int, cfg: dict) -> None:
    src_path = REPO_ROOT / cfg["source"]
    out_path = REPO_ROOT / cfg["output"]
    with open(src_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows_out = []
        for row in reader:
            final_raw = (row.get(cfg["target_final_col"]) or "").strip()
            # A blank score means a parse/lookup error on this row (e.g. "function 'x' not found in
            # submission") rather than a missing column. The paper's own reported correct/wrong
            # denominators (confirmed by this repo's own recount of this exact file) include these
            # rows counted as failing (final_score 0.0), not excluded -- so this script matches that
            # convention rather than dropping the row, to keep n_total identical to the reported figure.
            final_score = float(final_raw) if final_raw != "" else 0.0
            missing = (row.get(cfg["target_missing_col"]) or "").strip()
            matched_branch = ""
            for branch_col in cfg["branch_cols"]:
                branch_val = (row.get(branch_col) or "").strip()
                if branch_val not in ("", "0", "0.0") and float(branch_val) > 0:
                    matched_branch = branch_col.rsplit("_final", 1)[0]
                    break
            note_parts = [cfg["note"]]
            error = (row.get("error") or "").strip()
            if error:
                note_parts.append(f"error={error!r}")
            if missing:
                note_parts.append(f"missing={missing!r}")
            rows_out.append(
                {
                    "submission_id": row["file"].rsplit(".py", 1)[0],
                    "test_suite_label": row["label"].strip(),
                    "target_competency": cfg["target_competency"],
                    "coverage_score": final_score,
                    "structure_score": final_score,
                    "final_score": final_score,
                    "matched_branch": matched_branch,
                    "notes": "; ".join(note_parts),
                }
            )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "submission_id",
                "test_suite_label",
                "target_competency",
                "coverage_score",
                "structure_score",
                "final_score",
                "matched_branch",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"Q{question}: wrote {len(rows_out)} rows to {cfg['output']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--question", type=int, choices=sorted(QUESTION_CONFIG), help="Build a single question.")
    parser.add_argument("--all", action="store_true", help="Build all configured questions (1-5).")
    args = parser.parse_args()

    if not args.all and args.question is None:
        parser.error("Pass --question N or --all")

    questions = sorted(QUESTION_CONFIG) if args.all else [args.question]
    for q in questions:
        build_one(q)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
