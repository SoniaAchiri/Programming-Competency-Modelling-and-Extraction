#!/usr/bin/env python3
"""Regenerate the Q4 (BubbleSortPass/TopKPattern) and Q2 (counter/functional) embedding
cross-validation sweeps -- the same multi-seed nearest-centroid methodology already validated for
Q5's manual/builtin split, extended to the two other Refactory questions with a real taxonomic split
worth checking (Q1 and Q3 are single-strategy competencies, deliberately excluded -- see
provenance/detector-version-log.md).

Unlike the first version of this script, this now reads the REAL per-seed/per-file prediction CSVs
directly -- `data/labels_scores/q4_embeddings_crossvalidation.csv` and
`q2_embeddings_crossvalidation.csv` (columns: file, seed, true_label, predicted; one row per
seed/file prediction) -- rather than hand-transcribing the notebook's printed summary. These are the
exact files the notebook's own last cell saved to Sonia's Drive; they were not supplied in the round
that first reported these figures (hence the original `evidence: real_notebook_output` tag), but were
supplied in a later round and now let every figure be recomputed from the raw predictions themselves.
The `expected` values below are regression pins -- read once from this same CSV, then checked on every
run -- exactly the pattern used by regenerate_taxonomy_crossvalidation.py for Q5's own real_csv stages.

What this script verifies, mechanically, from the real CSV:
  1. Per-seed accuracy for each of the 10 seeds, and that the mean/std across seeds matches the
     notebook's own printed summary (and the paper's own §5.6 text) to the reported precision.
  2. The pooled confusion matrix across all 10 seeds' test-set predictions, and that every cell of
     both pooled classification reports (precision, recall, support, accuracy) is exactly what falls
     out of that confusion matrix.
  3. For Q2, the majority-class baseline argument (the log/conversation's own honesty check): that always
     predicting `counter` would itself outscore the actual classifier.

This is why both stages in configs/stage_manifest.yaml are now `evidence: real_csv`, upgraded from
`real_notebook_output` -- the raw per-submission predictions are supplied, so no figure here depends on
a transcription of printed output.

Usage:
    python scripts/regenerate_q2q4_taxonomy_crossvalidation.py
"""
from __future__ import annotations

import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.config import REPO_ROOT  # noqa: E402

RUNS = [
    {
        "name": "Q4 (bubblesort/topk)",
        "csv": "data/labels_scores/q4_embeddings_crossvalidation.csv",
        "labels": ["bubblesort", "topk"],
        "expected_mean_std": (0.936, 0.021),
        "expected_pooled_total": 1470,
        "expected_report": {
            "bubblesort": {"precision": 0.69, "recall": 0.98, "support": 204},
            "topk": {"precision": 1.00, "recall": 0.93, "support": 1266},
            "accuracy": 0.94,
        },
    },
    {
        "name": "Q2 (counter/functional)",
        "csv": "data/labels_scores/q2_embeddings_crossvalidation.csv",
        "labels": ["counter", "functional"],
        "expected_mean_std": (0.959, 0.016),
        "expected_pooled_total": 1750,
        "expected_report": {
            "counter": {"precision": 0.98, "recall": 0.98, "support": 1694},
            "functional": {"precision": 0.33, "recall": 0.27, "support": 56},
            "accuracy": 0.96,
        },
    },
]

# The majority-class baseline the log/conversation uses to argue Q2's 95.9% headline number is uninformative:
# a classifier that always predicts the majority class ('counter') would score this well.
Q2_MAJORITY_CLASS_BASELINE_PCT = 96.8  # 1694 / 1750


def load_rows(csv_path: Path) -> list[dict]:
    with open(csv_path, newline="") as f:
        return list(csv.DictReader(f))


def per_seed_accuracy(rows: list[dict]) -> list[tuple[int, float, int]]:
    by_seed: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        by_seed[int(row["seed"])].append(row)
    out = []
    for seed in sorted(by_seed):
        seed_rows = by_seed[seed]
        correct = sum(1 for r in seed_rows if r["true_label"] == r["predicted"])
        out.append((seed, correct / len(seed_rows), len(seed_rows)))
    return out


def pooled_confusion_matrix(rows: list[dict], labels: list[str]) -> dict:
    cm = {a: {b: 0 for b in labels} for a in labels}
    for row in rows:
        cm[row["true_label"]][row["predicted"]] += 1
    return cm


def check_mean_std(name: str, per_seed: list[tuple[int, float, int]], reported: tuple[float, float]) -> bool:
    print(f"== {name}: per-seed table (from real CSV) -> mean/std ==")
    for seed, acc, n in per_seed:
        print(f"  seed {seed}: accuracy={acc:.6f} n_test={n}")
    values = [row[1] for row in per_seed]
    mean = statistics.mean(values)
    std = statistics.stdev(values)  # sample std (ddof=1), matches pandas' .std() default
    exp_mean, exp_std = reported
    match = abs(mean - exp_mean) < 5e-4 and abs(std - exp_std) < 5e-4
    print(f"  computed mean={mean:.4f} std={std:.4f}  |  reported mean={exp_mean} std={exp_std}"
          f"  [{'OK' if match else 'MISMATCH'}]\n")
    return match


def precision_recall(cm: dict, actual: str, labels: list[str]) -> tuple[float, float, int]:
    tp = cm[actual][actual]
    support = sum(cm[actual][pred] for pred in labels)
    predicted_total = sum(cm[a][actual] for a in labels)
    precision = tp / predicted_total if predicted_total else float("nan")
    recall = tp / support if support else float("nan")
    return precision, recall, support


def check_pooled_report(name: str, cm: dict, labels: list[str], reported: dict, expected_total: int) -> bool:
    print(f"== {name}: pooled confusion matrix (from real CSV) -> classification report ==")
    print(f"  confusion matrix: {cm}")
    total = sum(cm[a][b] for a in labels for b in labels)
    correct = sum(cm[a][a] for a in labels)
    accuracy = correct / total
    ok = total == expected_total
    print(f"  total predictions: {total} (expected {expected_total}) [{'OK' if ok else 'MISMATCH'}]")
    for label in labels:
        precision, recall, support = precision_recall(cm, label, labels)
        exp = reported[label]
        match = (
            round(precision, 2) == exp["precision"]
            and round(recall, 2) == exp["recall"]
            and support == exp["support"]
        )
        ok = ok and match
        print(f"  {label:>10}: precision={precision:.4f} (reported {exp['precision']}), "
              f"recall={recall:.4f} (reported {exp['recall']}), support={support} "
              f"(reported {exp['support']})  [{'OK' if match else 'MISMATCH'}]")
    acc_match = round(accuracy, 2) == reported["accuracy"]
    ok = ok and acc_match
    print(f"  accuracy: {accuracy:.4f} (reported {reported['accuracy']})  "
          f"[{'OK' if acc_match else 'MISMATCH'}]\n")
    return ok


def check_q2_majority_baseline(cm: dict, labels: list[str]) -> bool:
    total = sum(cm[a][b] for a in labels for b in labels)
    counter_actual = sum(cm["counter"][b] for b in labels)
    baseline_pct = 100.0 * counter_actual / total
    match = abs(baseline_pct - Q2_MAJORITY_CLASS_BASELINE_PCT) < 0.05
    print("== Q2 majority-class baseline check (the log/conversation's own honesty argument) ==")
    print(f"  'counter' share of pooled test set: {baseline_pct:.1f}% (reported {Q2_MAJORITY_CLASS_BASELINE_PCT}%)"
          f"  [{'OK' if match else 'MISMATCH'}]")
    print(f"  i.e. always predicting 'counter' would itself score ~{baseline_pct:.1f}% accuracy -- "
          f"higher than the classifier's own 95.9%, confirming the headline number is a class-imbalance\n"
          f"  artifact, not evidence the taxonomic split was recovered.\n")
    return match


def main() -> int:
    ok = True
    pooled_by_name: dict[str, tuple[dict, list[str]]] = {}
    for run in RUNS:
        csv_path = REPO_ROOT / run["csv"]
        if not csv_path.exists():
            print(f"[PENDING] {run['csv']} not found -- cannot regenerate {run['name']}.")
            ok = False
            continue
        rows = load_rows(csv_path)
        per_seed = per_seed_accuracy(rows)
        cm = pooled_confusion_matrix(rows, run["labels"])
        pooled_by_name[run["name"]] = (cm, run["labels"])
        ok = check_mean_std(run["name"], per_seed, run["expected_mean_std"]) and ok
        ok = check_pooled_report(
            run["name"], cm, run["labels"], run["expected_report"], run["expected_pooled_total"]
        ) and ok

    if "Q2 (counter/functional)" in pooled_by_name:
        cm, labels = pooled_by_name["Q2 (counter/functional)"]
        ok = check_q2_majority_baseline(cm, labels) and ok

    print("=" * 88)
    if ok:
        print("All figures recomputed directly from the real per-seed/per-file CSVs match the reported values for both Q4 and Q2.")
    else:
        print("[MISMATCH] One or more figures above do not reconcile -- see flags.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
