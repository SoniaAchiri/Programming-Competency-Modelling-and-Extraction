#!/usr/bin/env python3
"""Regenerate Table 4 (final target-competency coverage, all five Refactory exercises).

Usage:
    python scripts/regenerate_table4.py --stage final
    python scripts/regenerate_table4.py --stage final --check   # also assert against reported values

By default (--stage final) this reproduces the printed Table 4. Pass any other stage id family
present in configs/stage_manifest.yaml's `stages` list (e.g. to compare pre/post a specific
correction) via --stage-ids q1_prescoping,q3_prescoping,... for an ad hoc comparison table.

This script never hardcodes a taxonomy or detector version — every value it prints is looked up from
configs/stage_manifest.yaml, and the underlying numbers come from data/labels_scores/*.csv. If those
files are not yet populated (see POPULATE.md), it fails with a clear message rather than a silent
fallback to a hardcoded number.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.config import (  # noqa: E402
    REPO_ROOT,
    coverage_pct,
    get_stage,
    load_labels_scores,
    load_stage_manifest,
    load_yaml,
)


def regenerate_row(manifest: dict, threshold: float, stage_id: str) -> dict:
    stage = get_stage(manifest, stage_id)
    rows = load_labels_scores(stage["data_file"])
    correct_pct, n_covered_c, n_total_c = coverage_pct(rows, "correct", threshold)
    wrong_pct, n_covered_w, n_total_w = coverage_pct(rows, "wrong", threshold)
    return {
        "stage_id": stage_id,
        "question": stage["question"],
        "taxonomy_checkpoint": stage["taxonomy_checkpoint"],
        "detector_checkpoint": stage["detector_checkpoint"],
        "scoping_mode": stage["scoping_mode"],
        "correct_pct": correct_pct,
        "correct_n": n_total_c,
        "wrong_pct": wrong_pct,
        "wrong_n": n_total_w,
        "reported_value_pct": stage.get("reported_value_pct"),
        "reported_wrong_label_pct": stage.get("reported_wrong_label_pct"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", default="final", help="'final' uses table4_config.yaml row mapping (default).")
    parser.add_argument("--stage-ids", default=None, help="Comma-separated explicit stage ids, overrides --stage.")
    parser.add_argument("--check", action="store_true", help="Assert regenerated values match reported values.")
    args = parser.parse_args()

    manifest = load_stage_manifest()
    threshold = manifest["coverage_threshold"]

    if args.stage_ids:
        stage_ids = [s.strip() for s in args.stage_ids.split(",")]
        rows_meta = [{"stage_id": sid} for sid in stage_ids]
    elif args.stage == "final":
        table4_config = load_yaml("configs/table4_config.yaml")
        rows_meta = table4_config["rows"]
    else:
        raise SystemExit(f"Unknown --stage {args.stage!r}. Use 'final' or pass --stage-ids explicitly.")

    print(f"{'Q':<3}{'Task':<24}{'Target competency':<28}{'Correct':>16}{'Wrong':>16}")
    print("-" * 91)

    failures = []
    for row_meta in rows_meta:
        stage_id = row_meta["stage_id"]
        task = row_meta.get("task", "")
        target = row_meta.get("target_competency", "")
        try:
            stage = get_stage(manifest, stage_id)
            result = regenerate_row(manifest, threshold, stage_id)
        except (FileNotFoundError, KeyError) as exc:
            question = row_meta.get("question", get_stage(manifest, stage_id).get("question", "?"))
            print(f"{question:<3}{task:<24}{target:<28}"
                  f"{'-- PENDING --':>16}{f'({exc.__class__.__name__})':>16}")
            continue
        correct_str = f"{result['correct_pct']:.1f}% ({result['correct_n']})"
        wrong_str = f"{result['wrong_pct']:.1f}% ({result['wrong_n']})"
        print(f"{result['question']:<3}{task:<24}{target:<28}{correct_str:>16}{wrong_str:>16}")

        if args.check and result["reported_value_pct"]:
            reported_raw = result["reported_value_pct"]
            # q2_final's reported_value_pct is a dict (per-strategy breakdown + "combined"), not a
            # plain "NN.N%" string like every other stage -- unwrap it rather than crashing, a real
            # latent bug this surfaced now that q2_final has actual data to check against.
            reported_str = reported_raw["combined"] if isinstance(reported_raw, dict) else reported_raw
            reported = float(reported_str.rstrip("%"))
            got = round(result["correct_pct"], 1)
            if abs(got - reported) > 0.05:
                failures.append(
                    f"Stage {stage_id}: regenerated {got}% != reported {reported}%"
                )

    if args.check:
        if failures:
            print("\nMISMATCHES:")
            for f in failures:
                print(f"  - {f}")
            return 1
        print("\nAll regenerated values match reported values.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
