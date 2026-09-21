#!/usr/bin/env python3
"""Regenerate the AST-taxonomy embedding cross-validation result (Q5, manual/builtin/novel).

This is a real, independently-reproducible result: a pretrained code-embedding model
(Salesforce/codet5p-110m-embedding), given no knowledge of which AST rule matched a submission, is used
to check whether the AST taxonomy's own SelectionStep/FindExtremum ("manual"/"builtin") split corresponds
to a genuine distinction in embedding space. See ../provenance/detector-version-log.md's "AST taxonomy
cross-validation via embeddings" section for the full provenance writeup.

This script now regenerates BOTH real per-file CSVs that exist for this experiment, since both are now
`evidence: real_csv` in configs/stage_manifest.yaml:

  1. The original, unshuffled 70/30 split (`q5_taxonomy_crossvalidation_results.csv`) — the run reported
     in the published paper's original §5.5 (89.1% manual/builtin agreement).
  2. A single alternate run with `SHUFFLE_BEFORE_SPLIT=True`, `SPLIT_SEED=0`
     (`q5_taxonomy_crossvalidation_shuffled_seed0_results.csv`) — the run that first showed the headline
     figure was not stable split-to-split (85.2% manual/builtin agreement under this one different split).
     This is "seed 0" of the later 10-seed sweep (see regenerate_10seed_taxonomy_sweep.py), but was
     supplied and logged as its own standalone real CSV before the full sweep's own notebook output
     arrived.

What this script does NOT regenerate: the embeddings themselves (would require re-running
detectors/ast-taxonomy-crossvalidation/ast_taxonomy_crossvalidation.ipynb against the real
Refactory Q5 corpus and a live codet5p-110m-embedding model — out of scope for a static repo), and the
other 9 seeds of the 10-seed sweep, for which only the notebook's own printed summary/pooled output was
supplied, not per-seed raw CSVs — see regenerate_10seed_taxonomy_sweep.py for that separate, narrower
verification.

Usage:
    python scripts/regenerate_taxonomy_crossvalidation.py
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.config import REPO_ROOT  # noqa: E402

LABELS_ORDER = ["manual", "builtin", "novel"]

RUNS = [
    {
        "name": "Original unshuffled 70/30 split (paper's original §5.5 figure)",
        "csv": "data/labels_scores/q5_taxonomy_crossvalidation_results.csv",
        "expected": {
            "accuracy_3way": 0.8607594936708861,
            "accuracy_manual_builtin": 0.8911564625850340,
            "novel_recall": 0.45454545454545453,
        },
    },
    {
        "name": "Shuffled alternate split, SPLIT_SEED=0 (the run that first showed instability)",
        "csv": "data/labels_scores/q5_taxonomy_crossvalidation_shuffled_seed0_results.csv",
        "expected": {
            "accuracy_3way": 0.8354430379746836,
            "accuracy_manual_builtin": 0.852112676056338,
            "novel_recall": 0.6875,
        },
    },
]


def regenerate_one(name: str, relative_csv_path: str, expected: dict[str, float]) -> bool:
    path = REPO_ROOT / relative_csv_path
    print(f"\n{'=' * 88}\n{name}\n{'=' * 88}")
    if not path.exists():
        print(f"[PENDING] {relative_csv_path} not found.")
        return True  # not a failure — just not yet supplied

    with open(path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print(f"[PENDING] {relative_csv_path} is present but empty.")
        return True

    label_counts = Counter(r["structural_label"] for r in rows)
    cm = {a: {b: 0 for b in LABELS_ORDER} for a in LABELS_ORDER}
    for r in rows:
        sl, sp = r["structural_label"], r["semantic_predicted"]
        if sl in cm and sp in cm[sl]:
            cm[sl][sp] += 1

    total = len(rows)
    correct = sum(cm[a][a] for a in LABELS_ORDER)
    accuracy_3way = correct / total

    mb_rows = [r for r in rows if r["structural_label"] in ("manual", "builtin")]
    mb_correct = sum(1 for r in mb_rows if r["structural_label"] == r["semantic_predicted"])
    accuracy_manual_builtin = mb_correct / len(mb_rows)

    novel_rows = [r for r in rows if r["structural_label"] == "novel"]
    novel_recall = (
        sum(1 for r in novel_rows if r["semantic_predicted"] == "novel") / len(novel_rows)
        if novel_rows
        else float("nan")
    )

    print(f"{total} test-set rows; label counts: {dict(label_counts)}")
    print("\nconfusion matrix [rows=structural label, cols=semantic prediction]")
    header = "        " + "  ".join(f"{b:>8}" for b in LABELS_ORDER)
    print(header)
    for a in LABELS_ORDER:
        print(f"{a:>8}" + "  ".join(f"{cm[a][b]:>8}" for b in LABELS_ORDER))

    print(f"\noverall 3-way accuracy:       {accuracy_3way:.10f}  ({correct}/{total})")
    print(f"manual/builtin-only accuracy: {accuracy_manual_builtin:.10f}  ({mb_correct}/{len(mb_rows)})")
    print(f"novel recall:                 {novel_recall:.10f}  "
          f"({sum(1 for r in novel_rows if r['semantic_predicted'] == 'novel')}/{len(novel_rows)})")

    ok = True
    actuals = {
        "accuracy_3way": accuracy_3way,
        "accuracy_manual_builtin": accuracy_manual_builtin,
        "novel_recall": novel_recall,
    }
    for key, exp_val in expected.items():
        actual = actuals[key]
        if abs(actual - exp_val) > 1e-9:
            print(f"\n[MISMATCH] {key}: recomputed {actual!r} != logged {exp_val!r}")
            ok = False
    if ok:
        print("\nAll figures match provenance/detector-version-log.md / configs/stage_manifest.yaml exactly.")
    return ok


def main() -> int:
    ok = True
    for run in RUNS:
        ok = regenerate_one(run["name"], run["csv"], run["expected"]) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
