"""Shared helpers for loading the stage manifest and table configs.

All regeneration scripts go through this module rather than reading YAML ad hoc, so there is exactly
one place that resolves a stage id to its data file and one place that raises a clear error when a
data file hasn't been populated yet (see POPULATE.md).
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required. Install with: pip install -r environment/requirements.txt"
    ) from exc

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {relative_path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_stage_manifest() -> dict[str, Any]:
    return load_yaml("configs/stage_manifest.yaml")


def get_stage(manifest: dict[str, Any], stage_id: str) -> dict[str, Any]:
    for stage in manifest["stages"]:
        if stage["id"] == stage_id:
            return stage
    raise KeyError(
        f"No stage with id={stage_id!r} in configs/stage_manifest.yaml. "
        f"Known stage ids: {[s['id'] for s in manifest['stages']]}"
    )


@dataclass
class LabelRow:
    submission_id: str
    test_suite_label: str
    target_competency: str
    coverage_score: float
    structure_score: float
    final_score: float
    matched_branch: str | None
    notes: str | None


def load_labels_scores(relative_csv_path: str) -> list[LabelRow]:
    path = REPO_ROOT / relative_csv_path
    if not path.exists():
        raise FileNotFoundError(
            f"Data file not populated yet: {relative_csv_path}\n"
            f"See POPULATE.md step 5 (per-submission labels and scores)."
        )
    rows: list[LabelRow] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                LabelRow(
                    submission_id=r["submission_id"],
                    test_suite_label=r["test_suite_label"],
                    target_competency=r["target_competency"],
                    coverage_score=float(r["coverage_score"]),
                    structure_score=float(r["structure_score"]),
                    final_score=float(r["final_score"]),
                    matched_branch=r.get("matched_branch") or None,
                    notes=r.get("notes") or None,
                )
            )
    if not rows:
        raise ValueError(
            f"Data file exists but is empty (header only): {relative_csv_path}\n"
            f"Populate it per POPULATE.md step 5 before regenerating."
        )
    return rows


def coverage_pct(rows: list[LabelRow], label: str, threshold: float) -> tuple[float, int, int]:
    """Return (percentage, n_covered, n_total) for rows with test_suite_label == label."""
    subset = [r for r in rows if r.test_suite_label == label]
    n_total = len(subset)
    if n_total == 0:
        raise ValueError(f"No rows found with test_suite_label={label!r}")
    n_covered = sum(1 for r in subset if r.final_score >= threshold)
    return (100.0 * n_covered / n_total, n_covered, n_total)


def load_split_manifest(experiment_dir: str) -> dict[str, Any]:
    path = REPO_ROOT / experiment_dir / "split_manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing split manifest: {experiment_dir}/split_manifest.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_split_ids(experiment_dir: str, split_index: int, part: str) -> list[str]:
    assert part in ("train", "test")
    path = REPO_ROOT / experiment_dir / f"split_{split_index:02d}_{part}_ids.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"Split file not populated yet: {experiment_dir}/split_{split_index:02d}_{part}_ids.txt\n"
            f"See POPULATE.md step 4 (train/test split index files)."
        )
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
