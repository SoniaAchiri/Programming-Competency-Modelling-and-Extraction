#!/usr/bin/env python3
"""Populate data/submission_ids/qN_*.csv from the real per-question batch report CSVs.

This is the "exact submission identifiers assigned to each analysis cohort" artifact called for
explicitly in this project's reproducibility brief. Each qN_report.csv (Q1-Q4) / topk_report.csv (Q5)
enumerates every submission the detector was actually run against, with its own `file`/`label` columns
-- this script just projects those two columns into data/submission_ids/'s documented schema
(submission_id,label), stripping the .py extension. It does not touch scoring at all (see
build_labels_scores_from_batch_reports.py for that).

Usage:
    python scripts/build_submission_ids_from_batch_reports.py --all
    python scripts/build_submission_ids_from_batch_reports.py --question 5
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

QUESTION_SOURCES = {
    1: ("detectors/q1-q4-batch-validation/q1_report.csv", "data/submission_ids/q1_sequential_search.csv"),
    2: ("detectors/q1-q4-batch-validation/q2_report.csv", "data/submission_ids/q2_unique_day.csv"),
    3: ("detectors/q1-q4-batch-validation/q3_report.csv", "data/submission_ids/q3_remove_extras.csv"),
    4: ("detectors/q1-q4-batch-validation/q4_report.csv", "data/submission_ids/q4_sort_age.csv"),
    5: ("detectors/reporting-batch/topk_report.csv", "data/submission_ids/q5_top_k.csv"),
}


def build_one(question: int) -> None:
    source_rel, output_rel = QUESTION_SOURCES[question]
    src_path = REPO_ROOT / source_rel
    out_path = REPO_ROOT / output_rel
    with open(src_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [
            {"submission_id": row["file"].rsplit(".py", 1)[0], "label": row["label"].strip()}
            for row in reader
        ]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["submission_id", "label"])
        writer.writeheader()
        writer.writerows(rows)
    n_correct = sum(1 for r in rows if r["label"] == "correct")
    n_wrong = sum(1 for r in rows if r["label"] == "wrong")
    print(f"Q{question}: wrote {len(rows)} rows to {output_rel} ({n_correct} correct / {n_wrong} wrong)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--question", type=int, choices=sorted(QUESTION_SOURCES))
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if not args.all and args.question is None:
        parser.error("Pass --question N or --all")
    for q in sorted(QUESTION_SOURCES) if args.all else [args.question]:
        build_one(q)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
