"""Regression test: every 'required_for_publication' stage in configs/stage_manifest.yaml must
regenerate to within 0.05 percentage points of its reported value, and submission-ID manifest counts
must match Table 3 exactly.

Run with: pytest tests/ -v

Before real data is populated (see POPULATE.md), these tests are expected to fail with a clear
FileNotFoundError/ValueError pointing at the missing file rather than a silent pass — that is the
intended, honest state of an unpopulated scaffold, not a bug in the tests.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from common.config import REPO_ROOT, coverage_pct, load_labels_scores, load_stage_manifest  # noqa: E402

TABLE3_EXPECTED_COUNTS = {
    "q1_sequential_search.csv": (768, 575),
    "q2_unique_day.csv": (291, 435),
    "q3_remove_extras.csv": (546, 308),
    "q4_sort_age.csv": (419, 357),
    "q5_top_k.csv": (418, 108),
}


@pytest.fixture(scope="module")
def manifest():
    return load_stage_manifest()


def required_stage_ids(manifest) -> list[str]:
    return [s["id"] for s in manifest["stages"] if s.get("required_for_publication")]


@pytest.mark.parametrize("csv_name,expected", TABLE3_EXPECTED_COUNTS.items())
def test_submission_id_counts_match_table3(csv_name, expected):
    path = REPO_ROOT / "data" / "submission_ids" / csv_name
    if not path.exists():
        pytest.skip(f"{csv_name} not populated yet — see POPULATE.md step 3")
    with open(path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        pytest.fail(f"{csv_name} is present but empty — populate per POPULATE.md step 3")
    n_correct = sum(1 for r in rows if r["label"] == "correct")
    n_wrong = sum(1 for r in rows if r["label"] == "wrong")
    expected_correct, expected_wrong = expected
    assert (n_correct, n_wrong) == (expected_correct, expected_wrong), (
        f"{csv_name}: got correct={n_correct} wrong={n_wrong}, "
        f"Table 3 expects correct={expected_correct} wrong={expected_wrong}"
    )


def test_stage_manifest_has_required_stages(manifest):
    required = required_stage_ids(manifest)
    assert len(required) >= 5, "Expected at least the five Table 4 final-figure stages marked required_for_publication"


@pytest.mark.parametrize(
    "stage_id",
    [
        "q1_final", "q2_final", "q3_final", "q4_final", "q5_final",
    ],
)
def test_table4_stage_matches_reported_value(manifest, stage_id):
    stage = next(s for s in manifest["stages"] if s["id"] == stage_id)
    try:
        rows = load_labels_scores(stage["data_file"])
    except (FileNotFoundError, ValueError) as e:
        pytest.skip(str(e))
    threshold = manifest["coverage_threshold"]
    correct_pct, _, _ = coverage_pct(rows, "correct", threshold)
    # q2_final's reported_value_pct is a dict (per-strategy breakdown + "combined"), not a plain
    # "NN.N%" string like every other stage -- unwrap it rather than crashing (this test previously
    # never reached this line for q2_final, since its data_file was PENDING until this round).
    reported_raw = stage["reported_value_pct"]
    reported_str = reported_raw["combined"] if isinstance(reported_raw, dict) else reported_raw
    reported = float(reported_str.rstrip("%"))
    assert abs(round(correct_pct, 1) - reported) <= 0.05, (
        f"{stage_id}: regenerated {correct_pct:.1f}% != reported {reported}%"
    )

    if stage.get("reported_wrong_label_pct"):
        wrong_pct, _, _ = coverage_pct(rows, "wrong", threshold)
        reported_wrong = float(stage["reported_wrong_label_pct"].rstrip("%"))
        assert abs(round(wrong_pct, 1) - reported_wrong) <= 0.05, (
            f"{stage_id} (wrong-labelled): regenerated {wrong_pct:.1f}% != reported {reported_wrong}%"
        )
