#!/usr/bin/env python3
"""Regenerate the detailed Q5 delegation-fix breakdown, not just the headline coverage number.

regenerate_table4.py and regenerate_q5_percentages.py already confirm the headline 91.9%/80.6%
TopKPatternExtended figures against data/labels_scores/q5_final_extended.csv. This script goes one level
deeper, directly against the real source batch report
(detectors/q5-delegation-clustering-fix/topk_report_EXTENDED2.csv), and checks the specific,
more easily-lost claims from that round's conversation and paper revision:

  1. Zero regressions: no submission with TopKPattern_final == 1 has TopKPatternExtended_final == 0.
  2. TopKViaDelegate never fires independently of SortThenSlice on the same row (a real, honest wrinkle
     flagged in the source conversation, not something to assume without checking).
  3. The exact new-catch breakdown: 17 rows gain coverage via TopKViaDelegate (all 17 also caught by
     SortThenSlice), 40 further rows gain coverage via SortThenSlice alone -- 57 new catches total.
  4. The two wrong-labeled TopKViaDelegate catches are exactly wrong_5_011.py and wrong_5_101.py (named,
     not just counted, so a reader can open them directly -- see the source conversation's own manual check).
  5. The 78.2% -> 79.7% TopKPattern-alone baseline drift: recomputed directly against the original
     detectors/reporting-batch/topk_report.csv, confirming exactly 6 correct-labeled files flip
     0 -> 1 (and zero wrong-labeled files change), attributable to an intervening, unrelated fix
     (Q1's SHARED_BINDING/all_names change) rather than to anything in this round's own work.

Usage:
    python scripts/regenerate_q5_delegation_breakdown.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.config import REPO_ROOT  # noqa: E402

ORIGINAL_CSV = REPO_ROOT / "detectors" / "reporting-batch" / "topk_report.csv"
EXTENDED_CSV = REPO_ROOT / "detectors" / "q5-delegation-clustering-fix" / "topk_report_EXTENDED2.csv"

EXPECTED_ORIGINAL_CORRECT = (327, 418)   # 78.2%
EXPECTED_ORIGINAL_WRONG = (81, 108)      # 75.0%
EXPECTED_REMEASURED_CORRECT = (333, 418)  # 79.7% -- same corpus, current codebase
EXPECTED_REMEASURED_WRONG = (81, 108)     # 75.0% -- unchanged
EXPECTED_EXTENDED_CORRECT = (384, 418)   # 91.9%
EXPECTED_EXTENDED_WRONG = (87, 108)      # 80.6%
EXPECTED_NEW_CATCHES_TOTAL = 57
EXPECTED_VIA_DELEGATE = 17
EXPECTED_VIA_DELEGATE_ONLY = 0
EXPECTED_VIA_SORTSLICE_ONLY = 40
EXPECTED_WRONG_DELEGATE_CATCHES = {"wrong_5_011.py", "wrong_5_101.py"}
EXPECTED_BASELINE_DRIFT_FILES = {
    "correct_5_064.py", "correct_5_159.py", "correct_5_170.py",
    "correct_5_282.py", "correct_5_321.py", "correct_5_362.py",
}


def numf(x: str):
    try:
        return float(x)
    except ValueError:
        return None


def load(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ok = True

    if not ORIGINAL_CSV.exists() or not EXTENDED_CSV.exists():
        print(f"[PENDING] {ORIGINAL_CSV} / {EXTENDED_CSV} not found.")
        return 1

    original = load(ORIGINAL_CSV)
    extended = load(EXTENDED_CSV)
    orig_by_file = {r["file"]: r for r in original}
    ext_by_file = {r["file"]: r for r in extended}

    print(f"original rows: {len(original)}  extended rows: {len(extended)}")
    ok = ok and len(original) == len(extended) == 526

    # -- 1. Baseline drift: TopKPattern_final alone, original CSV vs. extended CSV (re-measured against
    #    the current codebase) --
    def coverage(rows, label, col):
        grp = [r for r in rows if r["label"] == label]
        n = sum(1 for r in grp if numf(r[col]) == 1.0)
        return n, len(grp)

    orig_c = coverage(original, "correct", "TopKPattern_final")
    orig_w = coverage(original, "wrong", "TopKPattern_final")
    remeasured_c = coverage(extended, "correct", "TopKPattern_final")
    remeasured_w = coverage(extended, "wrong", "TopKPattern_final")
    print(f"\n== TopKPattern baseline: original {orig_c[0]}/{orig_c[1]} ({orig_c[0]/orig_c[1]*100:.1f}%), "
          f"re-measured {remeasured_c[0]}/{remeasured_c[1]} ({remeasured_c[0]/remeasured_c[1]*100:.1f}%) ==")
    ok = ok and orig_c == EXPECTED_ORIGINAL_CORRECT and orig_w == EXPECTED_ORIGINAL_WRONG
    ok = ok and remeasured_c == EXPECTED_REMEASURED_CORRECT and remeasured_w == EXPECTED_REMEASURED_WRONG

    flips = {
        f for f in orig_by_file
        if numf(orig_by_file[f]["TopKPattern_final"]) != numf(ext_by_file[f]["TopKPattern_final"])
    }
    print(f"files whose TopKPattern_final flipped: {sorted(flips)}  [{'OK' if flips == EXPECTED_BASELINE_DRIFT_FILES else 'MISMATCH'}]")
    ok = ok and flips == EXPECTED_BASELINE_DRIFT_FILES

    # -- 2. Headline TopKPatternExtended coverage, zero regressions --
    ext_c = coverage(extended, "correct", "TopKPatternExtended_final")
    ext_w = coverage(extended, "wrong", "TopKPatternExtended_final")
    print(f"\n== TopKPatternExtended: correct {ext_c[0]}/{ext_c[1]} ({ext_c[0]/ext_c[1]*100:.1f}%), "
          f"wrong {ext_w[0]}/{ext_w[1]} ({ext_w[0]/ext_w[1]*100:.1f}%) ==")
    ok = ok and ext_c == EXPECTED_EXTENDED_CORRECT and ext_w == EXPECTED_EXTENDED_WRONG

    regressions = [r for r in extended
                   if numf(r["TopKPattern_final"]) == 1.0 and numf(r["TopKPatternExtended_final"]) == 0.0]
    print(f"regressions: {len(regressions)}  [{'OK' if len(regressions) == 0 else 'MISMATCH'}]")
    ok = ok and len(regressions) == 0

    # -- 3. New-catch breakdown --
    new_catches = [r for r in extended
                   if numf(r["TopKPattern_final"]) == 0.0 and numf(r["TopKPatternExtended_final"]) == 1.0]
    via_delegate = [r for r in new_catches if numf(r["TopKViaDelegate_final"]) == 1.0]
    via_delegate_only = [r for r in via_delegate if numf(r["SortThenSlice_final"]) != 1.0]
    via_sortslice_only = [r for r in new_catches
                           if numf(r["SortThenSlice_final"]) == 1.0 and numf(r["TopKViaDelegate_final"]) != 1.0]
    print(f"\n== New-catch breakdown: {len(new_catches)} total new catches "
          f"(expected {EXPECTED_NEW_CATCHES_TOTAL})  [{'OK' if len(new_catches) == EXPECTED_NEW_CATCHES_TOTAL else 'MISMATCH'}]")
    print(f"  via TopKViaDelegate: {len(via_delegate)} (expected {EXPECTED_VIA_DELEGATE})  "
          f"[{'OK' if len(via_delegate) == EXPECTED_VIA_DELEGATE else 'MISMATCH'}]")
    print(f"  via TopKViaDelegate ONLY (not also SortThenSlice): {len(via_delegate_only)} "
          f"(expected {EXPECTED_VIA_DELEGATE_ONLY} -- TopKViaDelegate never fires alone)  "
          f"[{'OK' if len(via_delegate_only) == EXPECTED_VIA_DELEGATE_ONLY else 'MISMATCH'}]")
    print(f"  via SortThenSlice ONLY: {len(via_sortslice_only)} (expected {EXPECTED_VIA_SORTSLICE_ONLY})  "
          f"[{'OK' if len(via_sortslice_only) == EXPECTED_VIA_SORTSLICE_ONLY else 'MISMATCH'}]")
    ok = ok and len(new_catches) == EXPECTED_NEW_CATCHES_TOTAL
    ok = ok and len(via_delegate) == EXPECTED_VIA_DELEGATE
    ok = ok and len(via_delegate_only) == EXPECTED_VIA_DELEGATE_ONLY
    ok = ok and len(via_sortslice_only) == EXPECTED_VIA_SORTSLICE_ONLY

    # -- 4. Named wrong-labeled TopKViaDelegate catches --
    wrong_delegate = {r["file"] for r in extended if r["label"] == "wrong" and numf(r["TopKViaDelegate_final"]) == 1.0}
    print(f"\nwrong-labeled TopKViaDelegate catches: {sorted(wrong_delegate)}  "
          f"[{'OK' if wrong_delegate == EXPECTED_WRONG_DELEGATE_CATCHES else 'MISMATCH'}]")
    ok = ok and wrong_delegate == EXPECTED_WRONG_DELEGATE_CATCHES

    print("\n" + "=" * 88)
    if ok:
        print("All figures recomputed directly from the real batch-report CSVs match the reported values --")
        print("the delegation fix, its zero-regression property, its exact new-catch breakdown, the two")
        print("named wrong-labeled catches, and the 78.2% -> 79.7% baseline drift are all independently")
        print("confirmed, not merely repeated from the source conversation.")
    else:
        print("[MISMATCH] One or more figures above do not reconcile -- see flags.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
