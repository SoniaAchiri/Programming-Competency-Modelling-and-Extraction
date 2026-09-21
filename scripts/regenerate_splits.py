#!/usr/bin/env python3
"""Regenerate the 10 train/test splits deterministically from the recorded generation method, as a
cross-check against the recorded split_NN_{train,test}_ids.txt files (see data/splits/README.md for why
both a seed-based regeneration path and explicit recorded ID files are kept).

Real method (confirmed against the source notebooks, 2026-09-20 -- see data/splits/README.md):
    shuffled = labeled_df.sample(frac=1, random_state=seed).reset_index(drop=True)
    split_point = int(len(shuffled) * 0.7)
    train = shuffled.iloc[:split_point]; test = shuffled.iloc[split_point:]
for seed in range(10), applied to each experiment's labeled subset of its source report CSV.

Usage:
    python scripts/regenerate_splits.py --experiment q4_sortbykey --check
    python scripts/regenerate_splits.py --experiment q5_topk --check
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.config import REPO_ROOT, load_split_ids, load_split_manifest  # noqa: E402

EXPERIMENT_DIRS = {
    "q4_sortbykey": "data/splits/q4_sortbykey",
    "q5_topk": "data/splits/q5_topk",
}

# Real source report CSVs each experiment's split was computed over (see split_manifest.json's
# source_report_csv field for the same paths, spelled out relative to the repo root here).
SOURCE_REPORT_CSV = {
    "q4_sortbykey": "detectors/q1-q4-batch-validation/q4_report.csv",
    "q5_topk": "detectors/reporting-batch/topk_report.csv",
}


def _label_q4(row: pd.Series) -> str | None:
    bsp = pd.to_numeric(row["BubbleSortPass_final"], errors="coerce")
    tkp = pd.to_numeric(row["TopKPattern_final"], errors="coerce")
    if bsp >= 0.999:
        return "bubblesort"
    if tkp >= 0.999:
        return "topk"
    return None


def _label_q5(row: pd.Series) -> str:
    if pd.to_numeric(row["SelectionStep_final"], errors="coerce") >= 0.99:
        return "manual"
    if pd.to_numeric(row["FindExtremum_final"], errors="coerce") >= 0.99:
        return "builtin"
    if pd.to_numeric(row["FindExtremum_final"], errors="coerce") == 0:
        return "novel"
    return "partial"


def _labeled_subset(experiment: str) -> pd.DataFrame:
    report = pd.read_csv(REPO_ROOT / SOURCE_REPORT_CSV[experiment])
    if experiment == "q4_sortbykey":
        report["structural_label"] = report.apply(_label_q4, axis=1)
        return report[report["structural_label"].notna()][["file", "structural_label"]].reset_index(drop=True)
    report["structural_label"] = report.apply(_label_q5, axis=1)
    return report[report["structural_label"].isin(["manual", "builtin", "novel"])].reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--experiment", choices=list(EXPERIMENT_DIRS), required=True)
    parser.add_argument("--check", action="store_true", help="Compare regenerated IDs against recorded IDs.")
    args = parser.parse_args()

    experiment_dir = EXPERIMENT_DIRS[args.experiment]
    manifest = load_split_manifest(experiment_dir)
    seeds = manifest.get("seeds")
    if not seeds:
        raise SystemExit(f"{experiment_dir}/split_manifest.json has no 'seeds' list.")

    labeled = _labeled_subset(args.experiment)
    print(f"{args.experiment}: {len(labeled)} labeled rows from {SOURCE_REPORT_CSV[args.experiment]}")

    all_match = True
    for seed in seeds:
        shuffled = labeled.sample(frac=1, random_state=seed).reset_index(drop=True)
        split_point = int(len(shuffled) * manifest["split_fraction_train"])
        regenerated_train = set(shuffled.iloc[:split_point]["file"].tolist())
        regenerated_test = set(shuffled.iloc[split_point:]["file"].tolist())

        if args.check:
            try:
                recorded_train = set(load_split_ids(experiment_dir, seed, "train"))
                recorded_test = set(load_split_ids(experiment_dir, seed, "test"))
            except FileNotFoundError as e:
                print(f"  seed {seed:02d}: {e}")
                all_match = False
                continue
            train_match = regenerated_train == recorded_train
            test_match = regenerated_test == recorded_test
            all_match &= train_match and test_match
            print(
                f"  seed {seed:02d}: train match={train_match} ({len(regenerated_train)}) "
                f"test match={test_match} ({len(regenerated_test)})"
            )
        else:
            print(f"  seed {seed:02d}: train={len(regenerated_train)} test={len(regenerated_test)}")

    if args.check:
        print(f"\n>>> ALL SEEDS EXACT MATCH TO RECORDED FILES: {all_match}")
        if not all_match:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
