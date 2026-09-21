#!/usr/bin/env python3
"""Apply a pinned (taxonomy_checkpoint, detector_checkpoint, scoping_mode) to a submission cohort and
emit a data/labels_scores/*.csv file in this repository's schema.

This is the script that *produces* the files scripts/regenerate_table4.py and friends *consume* — it
is the bridge between "bring your own corpus" (see data/submission_ids/README.md) and this repo's
frozen, checkpoint-labeled outputs. Checkpoint names are real: they match the folder names under
detectors/ and taxonomy/, each named <real-date>_<Sonia's-own-label>, not an invented semver ladder —
see ../VERSIONING.md.

Usage:
    python scripts/run_detector_on_corpus.py \\
        --question 4 --taxonomy-version taxonomy/fixq4-sortbykey \\
        --detector-version detectors/fixq4 --scoping function-scoped \\
        --corpus-dir /path/to/local/refactory/q4/ \\
        --out data/labels_scores/q4_final.csv

The --taxonomy-version/--detector-version flag names are kept from the original scaffold for
compatibility with the rest of this script; pass them a checkpoint folder name (e.g.
"fixq4"), not a version number.

TODO(populate): this is a scaffold, not a working implementation, because it depends on real submission
source code Sonia has not yet supplied (see POPULATE.md and ../provenance/detector-version-log.md's
"Still-pending items"). The real detector/taxonomy snapshots this script would load ARE now populated —
see detectors/<checkpoint>/ and taxonomy/<checkpoint>/ — only the corpus and the actual per-submission
scoring loop remain to be wired in. Once that's done, implement `load_detector(detector_version)` and
`load_taxonomy(taxonomy_version)` below and this script becomes the single source of truth for
regenerating any labels_scores file from raw source code, not just re-deriving tables from
already-exported scores.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_detector(detector_version: str):
    """Dynamically import detectors/<version>/competency.py. Raises clearly if not yet populated."""
    module_path = REPO_ROOT / "detectors" / detector_version / "competency.py"
    if not module_path.exists():
        raise FileNotFoundError(
            f"detectors/{detector_version}/competency.py not populated yet. See POPULATE.md step 1."
        )
    spec = importlib.util.spec_from_file_location(f"competency_{detector_version}", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_taxonomy(taxonomy_version: str) -> dict:
    import yaml

    path = REPO_ROOT / "taxonomy" / taxonomy_version / "taxonomy.yaml"
    if not path.exists():
        raise FileNotFoundError(f"taxonomy/{taxonomy_version}/taxonomy.yaml not found.")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--question", type=int, required=True, choices=[1, 2, 3, 4, 5])
    parser.add_argument("--taxonomy-version", required=True)
    parser.add_argument("--detector-version", required=True)
    parser.add_argument("--scoping", required=True, choices=["whole-file", "function-scoped"])
    parser.add_argument("--corpus-dir", required=True, type=Path, help="Local directory of submission source files, not checked into this repo.")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    taxonomy = load_taxonomy(args.taxonomy_version)
    detector = load_detector(args.detector_version)  # noqa: F841 — populate to use

    if not args.corpus_dir.exists():
        raise SystemExit(f"--corpus-dir {args.corpus_dir} does not exist.")

    target = next((c for c in taxonomy["competencies"] if c["question"] == args.question), None)
    if target is None:
        raise SystemExit(f"No competency for question {args.question} in taxonomy {args.taxonomy_version}")

    print(f"TODO(populate): iterate submissions in {args.corpus_dir}, run the {args.detector_version} "
          f"detector for competency {target['name']!r} in {args.scoping} mode, and write rows to "
          f"{args.out} with columns: submission_id,test_suite_label,target_competency,coverage_score,"
          f"structure_score,final_score,matched_branch,notes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
