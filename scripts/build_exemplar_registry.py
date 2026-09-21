#!/usr/bin/env python3
"""Populate data/exemplar_registry/{exemplars.csv,code/} from the real, delivered
EXEMPLAR_REGISTRY in detectors/semantic-backup-validation-executed/semantic_backup.py.

This is POPULATE.md step 6, second half: "the enriched/really-mined exemplar registry exists
already in code (the mine_exemplars rounds) but is not yet merged into data/exemplar_registry/."
That checkpoint is this project's most current, most audit-clean semantic-backup delivery --
audit_registry() runs clean against it (0/27 problems, all 10 competencies verifiable for the
first time, see that checkpoint's own README.md) -- so this script does not need any new
artifact from Sonia. It:

  1. Extracts the checkpoint's embedded competency.py / test_real_data.py / pw01_competencies.py /
     q2_competencies.py / report.py (they live only inside the notebook's own source cells --
     see that checkpoint's README for why they aren't duplicated as plain files) using the same
     extraction routine as scripts/regenerate_semantic_backup_v3_audit.py.
  2. Builds the real, full competency model (test_real_data -> pw01_competencies -> q2_competencies)
     and, for every exemplar in EXEMPLAR_REGISTRY, calls model.resolve() directly -- the SAME
     structural rules the paper's own results run against -- to get a real, freshly-computed
     final_score. This script does not trust or copy any previously-reported score; every value in
     the CSV it writes came from executing the delivered code in this run.
  3. Writes each exemplar's source to data/exemplar_registry/code/<exemplar_id>.py and rebuilds
     exemplars.csv, replacing the old 2-competency/5-exemplar stub.

Per-exemplar provenance (mined vs. hand-written, and which real submission where documented) is
NOT re-derived or guessed here -- it is transcribed directly from semantic_backup.py's own inline
comments (read and quoted in provenance/detector-version-log.md's 2026-09-18 entry for this step).
Where a comment names an exact source file (e.g. "correct_2_010.py"), that goes in
source_submission_id. Where a comment documents real mining but does not name individual
submission files for each exemplar (FunctionalUniqueCheck, DelegatesUniqueness, and
AccumulateThenCount's first exemplar -- each covers a mined *set*, not one file per exemplar),
source_submission_id is left blank and the `notes` column says so explicitly, rather than
inventing a filename. Two exemplars (GuardedInput's original pair) were themselves found invalid
by audit_registry() in an earlier round and hand-corrected; that history is preserved in `notes`
rather than silently dropped.

Usage:
    python scripts/build_exemplar_registry.py --check   # verify only, print report, write nothing
    python scripts/build_exemplar_registry.py --write   # write exemplars.csv and code/*.py
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_DIR = REPO_ROOT / "detectors" / "semantic-backup-validation-executed"
NOTEBOOK_PATH = CHECKPOINT_DIR / "semantic_backup_validation.ipynb"
OUT_DIR = REPO_ROOT / "data" / "exemplar_registry"
CODE_DIR = OUT_DIR / "code"
CSV_PATH = OUT_DIR / "exemplars.csv"

# Kept short in the CSV (repeated on all 27 rows) -- the full story (which files come from which
# checkpoint, and why no taxonomy/ snapshot applies) is in data/exemplar_registry/README.md rather
# than repeated 27 times in exemplars.csv itself.
DETECTOR_CHECKPOINT = (
    "detectors/q5-delegation-clustering-fix + "
    "semantic-backup-validation-executed (see README.md)"
)
TAXONOMY_CHECKPOINT = "N/A -- see README.md"

# Per-exemplar provenance, transcribed from semantic_backup.py's own inline comments
# (detectors/semantic-backup-validation-executed/semantic_backup.py, lines ~107-488).
# Key: (competency, index within that competency's list, 0-based, in EXEMPLAR_REGISTRY's own order).
PROVENANCE: dict[tuple[str, int], dict[str, str]] = {
    # Swap: no per-exemplar comment claims either is mined -- treated as hand-written.
    ("Swap", 0): {"source": "hand-written"},
    ("Swap", 1): {"source": "hand-written"},
    # Accumulation: all three are hand-written; the third is explicitly a deliberately-different
    # shape (while-loop, no input()) added to stop overlap with GuardedInput, not a mined case.
    ("Accumulation", 0): {"source": "hand-written"},
    ("Accumulation", 1): {"source": "hand-written"},
    ("Accumulation", 2): {"source": "hand-written",
                           "notes": "added to structurally separate this competency's exemplars from GuardedInput's"},
    # ConditionalCount: first three hand-written; last two explicitly mined with named source files.
    ("ConditionalCount", 0): {"source": "hand-written"},
    ("ConditionalCount", 1): {"source": "hand-written"},
    ("ConditionalCount", 2): {"source": "hand-written",
                               "notes": "deliberately not a near-duplicate of any AccumulateThenCount exemplar, to avoid confounding same/cross similarity with surface text overlap"},
    ("ConditionalCount", 3): {"source": "mined", "source_submission_id": "correct_2_010",
                               "notes": "mine_exemplars.py, question_2/code/correct"},
    ("ConditionalCount", 4): {"source": "mined", "source_submission_id": "correct_2_016",
                               "notes": "mine_exemplars.py, question_2/code/correct"},
    # AccumulateThenCount: exemplar 0 is real/mined (one of only 2 of 291 matches, both collapse
    # to this shape -- no single filename singled out in the comment). Exemplars 1-2 are corrected
    # synthetic replacements for two originals that scored final_score=0.00 (len()-based, not
    # .count()-based) -- see semantic_backup_findings.md finding #7.
    ("AccumulateThenCount", 0): {"source": "mined",
                                  "notes": "one of only 2 (of 291) question_2 submissions that structurally satisfy this competency; both collapse to this exact shape, so mine_exemplars.py's output did not distinguish a single source filename"},
    ("AccumulateThenCount", 1): {"source": "hand-written (corrected)",
                                  "notes": "replaces an original exemplar that scored final_score=0.00 under the real resolver (len()-based, not .count()-based); verified final_score=1.00 -- see semantic_backup_findings.md finding #7"},
    ("AccumulateThenCount", 2): {"source": "hand-written (corrected)",
                                  "notes": "replaces an original exemplar that scored final_score=0.00 (same len()-vs-.count() bug); verified final_score=1.00 -- see semantic_backup_findings.md finding #7"},
    # GuardedInput: both original exemplars scored final_score=0.00 (bare `while` condition has no
    # nested `if`, so no TEST evidence registers) -- both replaced, both re-verified.
    ("GuardedInput", 0): {"source": "hand-written (corrected)",
                           "notes": "replaces an original that scored final_score=0.00 (bare while-condition, no nested if -- no TEST evidence); verified final_score=1.00 -- see semantic_backup_findings.md finding #7"},
    ("GuardedInput", 1): {"source": "hand-written (corrected)",
                           "notes": "replaces an original that scored final_score=0.00 (same bare-while bug); verified final_score=1.00 -- see semantic_backup_findings.md finding #7"},
    ("SelectionStep", 0): {"source": "hand-written"},
    ("SelectionStep", 1): {"source": "hand-written"},
    ("FindExtremumBuiltin", 0): {"source": "hand-written"},
    ("FindExtremumBuiltin", 1): {"source": "hand-written"},
    ("TopKPattern", 0): {"source": "hand-written"},
    ("TopKPattern", 1): {"source": "hand-written"},
    # FunctionalUniqueCheck: comment above the whole list says all three are real, mined via
    # mine_exemplars.py from question_2/code/correct (13/291, 11 distinct shapes) -- one exemplar
    # per named sub-strategy shape, but no individual submission filename per exemplar.
    ("FunctionalUniqueCheck", 0): {"source": "mined",
                                    "notes": "InlineFunctionalCheck shape; mine_exemplars.py, question_2/code/correct, 13/291 (4.5%) submissions match across 11 distinct shapes -- no individual submission filename recorded per exemplar"},
    ("FunctionalUniqueCheck", 1): {"source": "mined",
                                    "notes": "GuardedFunctionalCheck shape; same mining run as above"},
    ("FunctionalUniqueCheck", 2): {"source": "mined",
                                    "notes": "InlineTestFunctionalCheck shape; same mining run as above"},
    # DelegatesUniqueness: comment above the whole list says all three are real, mined via
    # mine_exemplars.py's mine_cross_function() (227/291, 78%, 96 distinct shapes). Each exemplar
    # stores BOTH unique_day and contains_unique_day (needed for DELEGATES verification) --
    # DELEGATING_FUNCTION/runtime_scoped_exemplar() scope it down to contains_unique_day alone at
    # embedding time, matching what report.py actually passes for a real submission.
    ("DelegatesUniqueness", 0): {"source": "mined",
                                  "notes": "clean/idiomatic shape; mine_exemplars.py's mine_cross_function(), 227/291 (78%) submissions match across 96 distinct shapes -- no individual submission filename recorded per exemplar; stored as full two-function text for DELEGATES verification, scoped to contains_unique_day alone at embedding time (see DELEGATING_FUNCTION / runtime_scoped_exemplar in semantic_backup.py)"},
    ("DelegatesUniqueness", 1): {"source": "mined",
                                  "notes": "compact/single-condition shape; same mining run as above; same storage/scoping note"},
    ("DelegatesUniqueness", 2): {"source": "mined",
                                  "notes": "messier real student style; same mining run as above; same storage/scoping note"},
}

CSV_FIELDS = [
    "exemplar_id", "competency", "source", "source_submission_id", "final_score",
    "verified_taxonomy_checkpoint", "verified_detector_checkpoint", "code_path", "notes",
]


def extract_embedded_files(nb_path: Path, out_dir: Path) -> None:
    """Same extraction routine as scripts/regenerate_semantic_backup_v3_audit.py -- these files
    live only inside the notebook's own source cells in this checkpoint."""
    nb = json.load(open(nb_path))
    cells = nb["cells"]
    out_dir.mkdir(parents=True, exist_ok=True)
    src4 = "".join(cells[4]["source"])
    for name, content in re.findall(r"(\w+)_source = r'''(.*?)'''", src4, re.S):
        (out_dir / f"{name}.py").write_text(content)
    for idx, fname in ((6, "semantic_backup.py"), (7, "validate_semantic_backup.py")):
        src = "".join(cells[idx]["source"])
        m = re.search(r"\w+_source = r'''(.*?)'''\s*\n", src, re.S)
        if m:
            (out_dir / fname).write_text(m.group(1))


def normalize_source(src: str) -> str:
    """Strip leading/trailing blank lines (same convention as semantic_backup.py's own
    _normalize_source) so the written code/*.py files don't carry the triple-quote formatting
    artifact."""
    lines = src.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"


def slug(competency: str) -> str:
    out = []
    for i, ch in enumerate(competency):
        if ch.isupper() and i > 0:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="verify only, write nothing")
    mode.add_argument("--write", action="store_true", help="write exemplars.csv and code/*.py")
    args = parser.parse_args()

    if not NOTEBOOK_PATH.exists():
        print(f"ERROR: {NOTEBOOK_PATH} not found", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        extract_dir = Path(tmp)
        extract_embedded_files(NOTEBOOK_PATH, extract_dir)

        sys.path.insert(0, str(extract_dir))
        import q2_competencies  # noqa: E402  (imports pw01_competencies -> test_real_data -> competency)
        from semantic_backup import EXEMPLAR_REGISTRY, audit_registry  # noqa: E402

        model = q2_competencies.model

        problems = audit_registry(model)
        if problems:
            print(f"ERROR: audit_registry() reports problems -- refusing to merge: {problems}", file=sys.stderr)
            return 1

        total = sum(len(v) for v in EXEMPLAR_REGISTRY.values())
        print(f"audit_registry(): 0 problems. {len(EXEMPLAR_REGISTRY)} competencies, {total} exemplars, all real, freshly-verified code.")

        rows = []
        seen_ids: set[str] = set()
        for cid, exemplars in EXEMPLAR_REGISTRY.items():
            for i, src in enumerate(exemplars):
                key = (cid, i)
                if key not in PROVENANCE:
                    print(f"ERROR: no provenance entry for {key} -- add one before merging", file=sys.stderr)
                    return 1
                prov = PROVENANCE[key]

                results = model.resolve(ast.parse(src), [cid])
                res = results.get(cid)
                if res is None:
                    print(f"ERROR: {cid} exemplar #{i} not registered in the model", file=sys.stderr)
                    return 1
                final_score = res.final_score

                exemplar_id = f"{slug(cid)}_{i:02d}"
                if exemplar_id in seen_ids:
                    print(f"ERROR: duplicate exemplar_id {exemplar_id}", file=sys.stderr)
                    return 1
                seen_ids.add(exemplar_id)

                rows.append({
                    "exemplar_id": exemplar_id,
                    "competency": cid,
                    "source": prov["source"],
                    "source_submission_id": prov.get("source_submission_id", ""),
                    "final_score": f"{final_score:.4f}",
                    "verified_taxonomy_checkpoint": TAXONOMY_CHECKPOINT,
                    "verified_detector_checkpoint": DETECTOR_CHECKPOINT,
                    "code_path": f"code/{exemplar_id}.py",
                    "notes": prov.get("notes", ""),
                })

        n_mined = sum(1 for r in rows if r["source"] == "mined")
        n_hw = sum(1 for r in rows if r["source"] == "hand-written")
        n_corrected = sum(1 for r in rows if r["source"] == "hand-written (corrected)")
        print(f"Provenance breakdown: {n_mined} mined, {n_hw} hand-written, {n_corrected} hand-written (corrected).")
        print(f"All {len(rows)} final_score values: "
              + ("1.0000 (uniform)" if all(r["final_score"] == "1.0000" for r in rows) else "NOT uniform -- see rows"))

        if args.check:
            print("\n--check mode: nothing written.")
            return 0

        CODE_DIR.mkdir(parents=True, exist_ok=True)
        # Remove the old stub's files first so nothing stale is left behind.
        for old in CODE_DIR.glob("*.py"):
            old.unlink()

        for cid, exemplars in EXEMPLAR_REGISTRY.items():
            for i, src in enumerate(exemplars):
                exemplar_id = f"{slug(cid)}_{i:02d}"
                (CODE_DIR / f"{exemplar_id}.py").write_text(normalize_source(src))

        with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\nWrote {len(rows)} rows to {CSV_PATH.relative_to(REPO_ROOT)}")
        print(f"Wrote {len(rows)} exemplar files to {CODE_DIR.relative_to(REPO_ROOT)}/")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
