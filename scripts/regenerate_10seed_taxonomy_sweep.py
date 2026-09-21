#!/usr/bin/env python3
"""Verify the 10-seed AST-taxonomy embedding cross-validation robustness sweep (Q5).

Unlike regenerate_taxonomy_crossvalidation.py, this does NOT regenerate from a raw per-submission CSV —
no such CSV exists in this repository for 9 of the 10 seeds (only seed 0 has one; see
data/labels_scores/q5_taxonomy_crossvalidation_shuffled_seed0_results.csv and the sibling script above).
The per-seed table and pooled confusion matrix below are transcribed verbatim from real, executed
notebook output —
detectors/ast-taxonomy-crossvalidation/ast_taxonomy_crossvalidation_with_results.ipynb — and
independently cross-checked against three chart images in the same folder
(chart_per_seed_accuracy.png, chart_pooled_confusion_matrix.png, chart_pooled_precision_recall.png) and
against the matching conversation export (semantic_backup_layer_findings_chat_export.txt). See
../provenance/detector-version-log.md's "The real 10-seed sweep" section for the full provenance writeup.

What this script DOES verify, honestly and mechanically, from that transcribed real data:
  1. That the per-seed mean/std the notebook printed is arithmetically correct given its own per-seed
     table (numpy mean/std of the 10 listed values).
  2. That every cell of the pooled 3-way and manual/builtin-only classification reports (precision,
     recall, accuracy) is exactly what falls out of the pooled confusion matrix — i.e. the reports are
     not just pasted numbers sitting next to the matrix, they are the matrix's own arithmetic.

This is the appropriate evidence tag for this stage in configs/stage_manifest.yaml: `real_notebook_output`
rather than `real_csv` — real execution output exists and is internally verified here, but the raw
per-submission predictions for 9 of the 10 seeds were never supplied as a file this repository can
independently re-derive them from.

Usage:
    python scripts/regenerate_10seed_taxonomy_sweep.py
"""
from __future__ import annotations

import statistics

# Transcribed verbatim from the real, executed notebook output (and cross-checked against
# semantic_backup_layer_findings_chat_export.txt and chart_per_seed_accuracy.png).
PER_SEED = [
    # seed, acc_3way, acc_manual_builtin, novel_recall, n_test, n_novel_test
    (0, 0.835443, 0.868966, 0.461538, 158, 13),
    (1, 0.854430, 0.889655, 0.461538, 158, 13),
    (2, 0.791139, 0.826389, 0.428571, 158, 14),
    (3, 0.835443, 0.876812, 0.550000, 158, 20),
    (4, 0.835443, 0.855172, 0.615385, 158, 13),
    (5, 0.854430, 0.888889, 0.500000, 158, 14),
    (6, 0.867089, 0.897959, 0.454545, 158, 11),
    (7, 0.854430, 0.875862, 0.615385, 158, 13),
    (8, 0.829114, 0.874126, 0.400000, 158, 15),
    (9, 0.810127, 0.841379, 0.461538, 158, 13),
]

REPORTED_SUMMARY = {
    "acc_3way": (0.837, 0.023),
    "acc_manual_builtin": (0.870, 0.023),
    "novel_recall": (0.495, 0.075),
}

# Pooled confusion matrix, 10 seeds, 1580 total predictions (rows=structural label, cols=semantic
# prediction) — transcribed verbatim from the notebook's own printed output.
POOLED_CM = {
    "manual": {"manual": 859, "builtin": 134, "novel": 0},
    "builtin": {"manual": 54, "builtin": 394, "novel": 0},
    "novel": {"manual": 67, "builtin": 3, "novel": 69},
}
LABELS_3WAY = ["manual", "builtin", "novel"]
LABELS_MB = ["manual", "builtin"]

REPORTED_3WAY = {
    "manual": {"precision": 0.88, "recall": 0.87, "support": 993},
    "builtin": {"precision": 0.74, "recall": 0.88, "support": 448},
    "novel": {"precision": 1.00, "recall": 0.50, "support": 139},
    "accuracy": 0.84,
}
REPORTED_MB = {
    "manual": {"precision": 0.94, "recall": 0.87, "support": 993},
    "builtin": {"precision": 0.75, "recall": 0.88, "support": 448},
    "accuracy": 0.87,
}


def check_mean_std() -> bool:
    print("== Per-seed table -> mean/std ==")
    header = f"{'seed':>4} {'acc_3way':>10} {'acc_mb':>10} {'novel_recall':>13} {'n_test':>7} {'n_novel':>8}"
    print(header)
    for seed, a3, amb, nr, nt, nn in PER_SEED:
        print(f"{seed:>4} {a3:>10.6f} {amb:>10.6f} {nr:>13.6f} {nt:>7} {nn:>8}")

    ok = True
    for key, idx in (("acc_3way", 1), ("acc_manual_builtin", 2), ("novel_recall", 3)):
        values = [row[idx] for row in PER_SEED]
        mean = statistics.mean(values)
        std = statistics.stdev(values)  # sample std (ddof=1) — matches pandas' .std() default,
        # confirmed against the notebook's own printed mean/std below (pstdev/ddof=0 does NOT match)
        exp_mean, exp_std = REPORTED_SUMMARY[key]
        match = abs(mean - exp_mean) < 5e-4 and abs(std - exp_std) < 5e-4
        ok = ok and match
        flag = "OK" if match else "MISMATCH"
        print(f"\n{key}: computed mean={mean:.4f} std={std:.4f}  |  reported mean={exp_mean} std={exp_std}"
              f"  [{flag}]")
    return ok


def precision_recall(cm: dict, actual: str, labels: list[str]) -> tuple[float, float, int]:
    tp = cm[actual][actual]
    support = sum(cm[actual][pred] for pred in labels)
    predicted_total = sum(cm[a][actual] for a in labels)
    precision = tp / predicted_total if predicted_total else float("nan")
    recall = tp / support if support else float("nan")
    return precision, recall, support


def check_pooled_reports() -> bool:
    ok = True

    print("\n\n== Pooled confusion matrix (3-way) -> classification report ==")
    total = sum(POOLED_CM[a][b] for a in LABELS_3WAY for b in LABELS_3WAY)
    correct = sum(POOLED_CM[a][a] for a in LABELS_3WAY)
    accuracy = correct / total
    print(f"total predictions: {total} (expected 1580)")
    ok = ok and (total == 1580)
    for label in LABELS_3WAY:
        precision, recall, support = precision_recall(POOLED_CM, label, LABELS_3WAY)
        exp = REPORTED_3WAY[label]
        match = (
            round(precision, 2) == exp["precision"]
            and round(recall, 2) == exp["recall"]
            and support == exp["support"]
        )
        ok = ok and match
        flag = "OK" if match else "MISMATCH"
        print(f"  {label:>8}: precision={precision:.4f} (reported {exp['precision']}), "
              f"recall={recall:.4f} (reported {exp['recall']}), support={support} "
              f"(reported {exp['support']})  [{flag}]")
    acc_match = round(accuracy, 2) == REPORTED_3WAY["accuracy"]
    ok = ok and acc_match
    print(f"  accuracy: {accuracy:.4f} (reported {REPORTED_3WAY['accuracy']})  "
          f"[{'OK' if acc_match else 'MISMATCH'}]")

    print("\n== Pooled confusion matrix, manual/builtin actual rows only -> classification report ==")
    mb_total = sum(POOLED_CM[a][b] for a in LABELS_MB for b in LABELS_MB)
    mb_correct = sum(POOLED_CM[a][a] for a in LABELS_MB)
    mb_accuracy = mb_correct / mb_total
    print(f"total predictions: {mb_total} (expected 1441)")
    ok = ok and (mb_total == 1441)
    for label in LABELS_MB:
        precision, recall, support = precision_recall(POOLED_CM, label, LABELS_MB)
        exp = REPORTED_MB[label]
        match = (
            round(precision, 2) == exp["precision"]
            and round(recall, 2) == exp["recall"]
            and support == exp["support"]
        )
        ok = ok and match
        flag = "OK" if match else "MISMATCH"
        print(f"  {label:>8}: precision={precision:.4f} (reported {exp['precision']}), "
              f"recall={recall:.4f} (reported {exp['recall']}), support={support} "
              f"(reported {exp['support']})  [{flag}]")
    mb_acc_match = round(mb_accuracy, 2) == REPORTED_MB["accuracy"]
    ok = ok and mb_acc_match
    print(f"  accuracy: {mb_accuracy:.4f} (reported {REPORTED_MB['accuracy']})  "
          f"[{'OK' if mb_acc_match else 'MISMATCH'}]")

    return ok


def main() -> int:
    ok = check_mean_std()
    ok = check_pooled_reports() and ok
    print("\n" + "=" * 88)
    if ok:
        print("All transcribed notebook figures are internally consistent (mean/std and pooled "
              "confusion-matrix arithmetic both check out).")
    else:
        print("[MISMATCH] One or more figures above do not reconcile — see flags.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
