#!/usr/bin/env python3
"""Report status of the embedding-based experiments and semantic-backup layer referenced in
configs/stage_manifest.yaml's `table5` block.

**Every section this script reports on is currently PENDING real data**, with one exception: the stub
backend's own honesty test (semantic_20_07.docx) is real, already-run, and negative — it demonstrated
the stub has essentially no discriminative power (0.77 similarity on a related pair vs. 0.79 on an
unrelated one). There is no real CodeBERT result, no real train/test split data, and no pairwise
win-rate/worst-case-ranking computation possible yet — see ../VERSIONING.md's "Corrected from an
earlier, guessed version" note for what this script used to (incorrectly) claim to regenerate.

This script degrades honestly rather than crashing: every section prints [PENDING] with the reason
rather than raising, so `--section all` always completes and shows exactly what's missing.

Usage:
    python scripts/regenerate_table5.py
    python scripts/regenerate_table5.py --section embeddings
    python scripts/regenerate_table5.py --section semantic-backup
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.config import REPO_ROOT, load_stage_manifest, load_yaml  # noqa: E402


def report_embedding_experiment(name: str, cfg: dict) -> None:
    print(f"\n== {name} ==")
    print(f"  taxonomy_checkpoint = {cfg.get('taxonomy_checkpoint')}")
    print(f"  detector_checkpoint = {cfg.get('detector_checkpoint')}")
    print(f"  status = {cfg.get('status', 'unknown')}")
    if cfg.get("status") == "PENDING":
        print(f"  [PENDING] {cfg.get('note', 'no split data supplied yet')}")
        return
    print(f"  split_dir = {cfg.get('split_dir')}")
    print(f"  reported_mean = {cfg.get('reported_mean')}  reported_sd = {cfg.get('reported_sd')}")


def report_semantic_backup(cfg: dict) -> None:
    print("\n== Semantic backup layer ==")
    registry_path = REPO_ROOT / cfg["exemplar_registry"]
    if not registry_path.exists() or registry_path.stat().st_size == 0:
        print(f"  [PENDING] {cfg['exemplar_registry']} is empty.")
        return
    with open(registry_path, "r", encoding="utf-8", newline="") as f:
        exemplars = list(csv.DictReader(f))
    print(f"  exemplar registry: {len(exemplars)} real exemplars across "
          f"{len({e['competency'] for e in exemplars})} competencies (see {cfg['exemplar_registry']})")

    for backend_name, backend_cfg in cfg.get("backends", {}).items():
        print(f"\n  [{backend_name}]")
        result = backend_cfg.get("reported_result")
        if result:
            print(f"    result (real, already run): {result}")
            print(f"    source: {backend_cfg.get('source', 'unspecified')}")
        else:
            print(f"    [PENDING] status = {backend_cfg.get('status', 'unknown')} — "
                  f"{backend_cfg.get('description', '')}")

    if cfg.get("note"):
        print(f"\n  Note: {cfg['note']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--section", choices=["embeddings", "semantic-backup", "all"], default="all")
    args = parser.parse_args()

    manifest = load_stage_manifest()
    table5_config = load_yaml("configs/table5_config.yaml")
    t5 = manifest["table5"]

    if args.section in ("embeddings", "all"):
        for section in table5_config["sections"]:
            key = section["manifest_key"]
            if not key.startswith("table5.") or key == "table5.semantic_backup":
                continue
            cfg = t5[key.split(".", 1)[1]]
            report_embedding_experiment(section["name"], cfg)

    if args.section in ("semantic-backup", "all"):
        report_semantic_backup(t5["semantic_backup"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
