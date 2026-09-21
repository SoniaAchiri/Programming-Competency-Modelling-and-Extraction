#!/usr/bin/env python3
"""Regenerate the semantic backup layer's real novel-vs-wrong separation AUC (Q5/FindExtremum).

This is the first real AUC/ROC number this project has ever produced for what the semantic backup
layer is actually supposed to do: separate genuinely-novel-correct submissions (test-suite-correct,
scored 0 by every structural rule) from genuinely-wrong ones -- a different question from every
Q5/Q4/Q2 embedding-*taxonomy* cross-validation in this repo, which all test agreement with an existing
AST split instead.

Reads the two real per-submission CSVs the notebook's own last cell saved:
  - data file 1: semantic_backup_bootstrap_summary.csv (one row per bootstrap run: auc, group means/stds)
  - data file 2: semantic_backup_pooled_scores.csv (one row per run/file/group: the raw similarity score)
Both live in detectors/semantic-backup-layer-validation/.

What this script verifies, mechanically, from the real per-file data in file 2:
  1. That file 2 reproduces file 1's own per-run AUC and per-run novel/wrong group means -- i.e. the
     bootstrap summary is not just adjacent numbers, it is what the raw predictions actually produce.
  2. That the mean/SD of the 10 per-run AUCs matches the notebook's own printed "AUC: mean=... std=...".
  3. That pooling all 10 runs' predictions together and computing one AUC (via sklearn's roc_auc_score,
     equivalent to the Mann-Whitney U statistic) reproduces the notebook's own printed pooled AUC.
  4. That the ROC-curve threshold nearest 80% recall on novel-correct reproduces the notebook's own
     printed threshold and false-positive rate.

The result is real and strongly INVERTED, not merely null: AUC near 0 (not near 0.5) means
genuinely-wrong submissions are systematically more similar to correct exemplars than genuinely-novel-
correct submissions are -- the reverse of what the layer's raw max-similarity-to-exemplar design assumes.
See provenance/detector-version-log.md's "Semantic backup layer validation" section and the checkpoint's own
README.md for the full writeup, including a real, diff-confirmed difference between this notebook and its
unexecuted sibling (a Drive folder-path fix, identical in kind to the one found in the Q4/Q2 embedding
round), and a real, previously-never-supplied sanity-check similarity pair for the codet5p-110m-embedding
backend (related vs related: 0.8399; related vs unrelated: 0.3820).

Usage:
    python scripts/regenerate_semantic_backup_auc.py
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.config import REPO_ROOT  # noqa: E402

CHECKPOINT_DIR = REPO_ROOT / "detectors" / "semantic-backup-layer-validation"
SUMMARY_CSV = CHECKPOINT_DIR / "semantic_backup_bootstrap_summary.csv"
POOLED_CSV = CHECKPOINT_DIR / "semantic_backup_pooled_scores.csv"

EXPECTED_MEAN_STD = (0.098, 0.039)
EXPECTED_POOLED_AUC = 0.097
EXPECTED_POOLED_N = 1510
EXPECTED_THRESHOLD = 0.719
EXPECTED_THRESHOLD_TPR = 0.80
EXPECTED_THRESHOLD_FPR = 0.997


def load_rows(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def auc_from_scores(pos_scores: list[float], neg_scores: list[float]) -> float:
    """Rank-based AUC (equivalent to sklearn.metrics.roc_auc_score / Mann-Whitney U),
    implemented from scratch so this script has no external ML dependency."""
    all_scores = [(s, 1) for s in pos_scores] + [(s, 0) for s in neg_scores]
    all_scores.sort(key=lambda x: x[0])
    # Assign average ranks, handling ties.
    ranks = [0.0] * len(all_scores)
    i = 0
    while i < len(all_scores):
        j = i
        while j + 1 < len(all_scores) and all_scores[j + 1][0] == all_scores[i][0]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0  # 1-indexed rank average over the tied block
        for k in range(i, j + 1):
            ranks[k] = avg_rank
        i = j + 1
    rank_sum_pos = sum(r for (s, label), r in zip(all_scores, ranks) if label == 1)
    n_pos, n_neg = len(pos_scores), len(neg_scores)
    # Mann-Whitney U -> AUC
    u = rank_sum_pos - n_pos * (n_pos + 1) / 2.0
    return u / (n_pos * n_neg)


def roc_threshold_near_tpr(pos_scores: list[float], neg_scores: list[float], target_tpr: float):
    """Sweep candidate thresholds (every observed score) and find the one whose TPR is closest to
    target_tpr, mirroring sklearn.metrics.roc_curve's own thresholds (every distinct score, descending)
    closely enough for this honesty check."""
    candidates = sorted(set(pos_scores) | set(neg_scores))
    best = None
    for t in candidates:
        tp = sum(1 for s in pos_scores if s >= t)
        fp = sum(1 for s in neg_scores if s >= t)
        tpr = tp / len(pos_scores)
        fpr = fp / len(neg_scores)
        diff = abs(tpr - target_tpr)
        if best is None or diff < best[0]:
            best = (diff, t, tpr, fpr)
    return best[1], best[2], best[3]


def main() -> int:
    ok = True

    if not SUMMARY_CSV.exists() or not POOLED_CSV.exists():
        print(f"[PENDING] {SUMMARY_CSV} / {POOLED_CSV} not found.")
        return 1

    summary_rows = {int(r["run"]): r for r in load_rows(SUMMARY_CSV)}
    pooled_rows = load_rows(POOLED_CSV)
    print(f"Loaded {len(pooled_rows)} rows from {POOLED_CSV.name} "
          f"(expected {EXPECTED_POOLED_N}) [{'OK' if len(pooled_rows) == EXPECTED_POOLED_N else 'MISMATCH'}]")
    ok = ok and (len(pooled_rows) == EXPECTED_POOLED_N)

    by_run: dict[int, dict[str, list[float]]] = {}
    for row in pooled_rows:
        run = int(row["run"])
        by_run.setdefault(run, {"novel_correct": [], "genuinely_wrong": []})
        by_run[run][row["group"]].append(float(row["similarity"]))

    print("\n== Per-run AUC / group means, recomputed from the raw pooled_scores rows vs. bootstrap_summary.csv ==")
    per_run_aucs = []
    for run in sorted(by_run):
        novel = by_run[run]["novel_correct"]
        wrong = by_run[run]["genuinely_wrong"]
        auc = auc_from_scores(novel, wrong)
        per_run_aucs.append(auc)
        exp = summary_rows[run]
        exp_auc = float(exp["auc"])
        exp_novel_mean = float(exp["novel_mean"])
        exp_wrong_mean = float(exp["wrong_mean"])
        novel_mean = statistics.mean(novel)
        wrong_mean = statistics.mean(wrong)
        match = (
            abs(auc - exp_auc) < 1e-6
            and abs(novel_mean - exp_novel_mean) < 1e-6
            and abs(wrong_mean - exp_wrong_mean) < 1e-6
        )
        ok = ok and match
        print(f"  run {run}: auc={auc:.6f} (csv {exp_auc:.6f}) "
              f"novel_mean={novel_mean:.6f} (csv {exp_novel_mean:.6f}) "
              f"wrong_mean={wrong_mean:.6f} (csv {exp_wrong_mean:.6f}) "
              f"n_novel={len(novel)} n_wrong={len(wrong)}  [{'OK' if match else 'MISMATCH'}]")

    mean_auc = statistics.mean(per_run_aucs)
    std_auc = statistics.stdev(per_run_aucs)  # sample std (ddof=1)
    exp_mean, exp_std = EXPECTED_MEAN_STD
    mean_match = abs(mean_auc - exp_mean) < 5e-4
    std_match = abs(std_auc - exp_std) < 5e-4
    ok = ok and mean_match and std_match
    print(f"\n== Mean/SD across the 10 per-run AUCs ==")
    print(f"  computed mean={mean_auc:.4f} std={std_auc:.4f}  |  reported mean={exp_mean} std={exp_std}"
          f"  [{'OK' if (mean_match and std_match) else 'MISMATCH'}]")

    print("\n== Pooled AUC across all 10 runs combined ==")
    all_novel = [float(r["similarity"]) for r in pooled_rows if r["group"] == "novel_correct"]
    all_wrong = [float(r["similarity"]) for r in pooled_rows if r["group"] == "genuinely_wrong"]
    pooled_auc = auc_from_scores(all_novel, all_wrong)
    pooled_match = abs(pooled_auc - EXPECTED_POOLED_AUC) < 5e-4
    ok = ok and pooled_match
    print(f"  pooled AUC = {pooled_auc:.4f} (reported {EXPECTED_POOLED_AUC}), "
          f"n={len(all_novel) + len(all_wrong)} (reported {EXPECTED_POOLED_N})  "
          f"[{'OK' if pooled_match else 'MISMATCH'}]")

    print("\n== Threshold for ~80% recall on novel-correct ==")
    threshold, tpr, fpr = roc_threshold_near_tpr(all_novel, all_wrong, EXPECTED_THRESHOLD_TPR)
    threshold_match = abs(threshold - EXPECTED_THRESHOLD) < 0.01 and abs(fpr - EXPECTED_THRESHOLD_FPR) < 0.01
    ok = ok and threshold_match
    print(f"  threshold={threshold:.4f} (reported {EXPECTED_THRESHOLD}) tpr={tpr:.4f} "
          f"fpr={fpr:.4f} (reported {EXPECTED_THRESHOLD_FPR})  [{'OK' if threshold_match else 'MISMATCH'}]")
    print(f"\n  i.e. always predicting close to novel-correct's own ~0.80 similarity cluster catches 80%\n"
          f"  of novel-correct, but also flags ~99.7% of genuinely_wrong -- not a useable filter as built.")

    print("\n" + "=" * 88)
    if ok:
        print("All figures recomputed directly from the real per-run/per-file CSVs match the reported values --")
        print("a real, strongly INVERTED result (AUC << 0.5), not a null one.")
    else:
        print("[MISMATCH] One or more figures above do not reconcile -- see flags.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
