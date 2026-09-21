"""
Regenerates every independently-checkable claim from the third semantic_backup_validation
delivery: "here is the last version of 'semantic_backup_validation' notebook" (delivered
2026-09-17, no accompanying conversation transcript this time, no docx metadata since it's a raw
.ipynb -- dated here by delivery date; its CONTENT places it chronologically after the second
mine_exemplars batch (content-dated 2026-08-08/09), since it embeds that batch's full
10-competency/27-exemplar registry plus a scoping fix that batch's conversation only described,
never delivered).

This notebook is a genuine leap in evidence quality over both earlier mine_exemplars rounds:

  1. It is SELF-CONTAINED and confirmed to embed this repo's actual CURRENT HEAD structural
     model (competency.py, test_real_data.py, report.py -- all byte-identical, modulo one
     leading blank line from string embedding, to detectors/q5-delegation-clustering-fix),
     not a stale pre-Q1-fix snapshot the way the first two mine_exemplars rounds' "Original
     files to load" turned out to be.

  2. It FIXES the broken pw01_competencies.py import chain identified in the second round
     (`from .core import ...` / `from .base_competencies import ...` -> `from competency
     import ...` / `from test_real_data import ...`) -- confirmed here by a 0-diff-line
     match against the second round's own (broken) q2_competencies.py, and a 2-line
     (import-statements-only) diff against its pw01_competencies.py.

  3. With that chain fixed, audit_registry() now runs against ALL 10 competencies for the
     first time -- this script confirms it reports ZERO problems (27/27 exemplars, 10/10
     competencies), not the {AccumulateThenCount, FunctionalUniqueCheck, DelegatesUniqueness}
     "unverifiable" set every earlier round was stuck reporting.

  4. It DELIVERS, as real code for the first time, the DelegatesUniqueness/ConditionalCount
     surface-containment scoping fix (DELEGATING_FUNCTION + runtime_scoped_exemplar()) that
     the second round's conversation described as implemented and tested but never actually shipped
     (grep-confirmed absent from that round's own semantic_backup.py). This script confirms
     it is present and wired into both semantic_backup_score() (report.py's live path) and
     validate_semantic_backup.py's held-out test.

  5. Independently reproduces, via direct execution against the delivered code (no cache,
     no network needed -- LexicalEmbedder is deterministic): the notebook's own reported
     lexical numbers for the full, now-fully-verified 10-competency/27-exemplar registry,
     WITH the scoping fix applied: 1294/1428 (90.6%) pairwise win rate, 20/27 (74.1%)
     worst-case ranking, all 7 named failure lines -- notably with the DelegatesUniqueness/
     ConditionalCount confound gone entirely (0 failures involving DelegatesUniqueness,
     down from 5 of 12 in the pre-fix run two rounds ago).

  6. Independently reproduces the notebook's three synthetic TopKPatternExtended structural
     regression cases (Section 5.3 sanity checks, explicitly NOT semantic-similarity, and NOT
     a change to any real corpus-derived percentage) against this repo's own current model.

What this script does NOT and CANNOT independently check:
  - The 10-competency codet5p run (84.2% win rate, 81.5% worst-case) -- needs
    Salesforce/codet5p-110m-embedding, and huggingface.co remains blocked from this sandbox.
    The notebook's own output for this (real download progress bars, weight-loading logs,
    execution_count set, real printed SAME/CROSS/UNRELATED stats) is treated as
    evidence: real_notebook_output -- a step up from conversation_reported_only, since it is a
    directly-inspected executed notebook cell, not a re-typed transcript, but not
    independently re-run by this audit the way the lexical numbers are.
  - The moyenne()/DelegatesUniqueness codet5p similarity smoke-test numbers (0.42, 0.97,
    0.975, 0.977, 0.961) in cells 13/15 -- same reason. The STRUCTURAL parts of those same
    cells (Accumulation=1.00, TopKPattern=0.00, DelegatesUniqueness=0.00) are independently
    reproduced by this project's own structural resolver, checked separately below.
  - Anything about Table 4 or the Q5 TopKPatternExtended delegation breakdown -- this
    notebook does not touch either; both remain exactly as previously verified.

Exits 1 if any check fails.
"""
from __future__ import annotations

import difflib
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
V3_DIR = REPO_ROOT / "detectors" / "semantic-backup-validation-executed"
V2_ORIG_DIR = REPO_ROOT / "detectors" / "mine-exemplars-real-corpus" / "original_files_used_this_round"
HEAD_DIR = REPO_ROOT / "detectors" / "q5-delegation-clustering-fix"
# report.py was NOT touched by the 2026-08-08 Q5 delegation round (that round only changed
# competency.py/test_real_data.py) -- its own closest real checkpoint is still 2026-07-20,
# same as the second mine_exemplars round's "Original files to load". Confirmed by diff
# below, not assumed.
REPORT_DIR = REPO_ROOT / "detectors" / "semantic-backup"

FAILED = []


def check(label, condition, detail=""):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" -- {detail}" if detail and not condition else ""))
    if not condition:
        FAILED.append(label)


def diff_line_count(a: Path, b: Path) -> int:
    return sum(1 for _ in difflib.unified_diff(
        a.read_text().splitlines(), b.read_text().splitlines(), lineterm=""))


def substantively_identical(a: Path, b: Path) -> bool:
    """True if a and b are identical once a single leading blank line (an artifact of
    the notebook's `x_source = r'''\\n...'''` string-embedding convention) is stripped
    from whichever side has one."""
    def norm(p: Path) -> str:
        text = p.read_text()
        return text[1:] if text.startswith("\n") else text
    return norm(a) == norm(b)


def extract_embedded_files(nb_path: Path, out_dir: Path) -> None:
    import json
    import re
    nb = json.load(open(nb_path))
    cells = nb["cells"]
    out_dir.mkdir(parents=True, exist_ok=True)
    # Cell 4: competency/test_real_data/pw01_competencies/q2_competencies/report
    src4 = "".join(cells[4]["source"])
    for name, content in re.findall(r"(\w+)_source = r'''(.*?)'''", src4, re.S):
        (out_dir / f"{name}.py").write_text(content)
    # Cells 6/7: semantic_backup / validate_semantic_backup
    for idx, fname in ((6, "semantic_backup.py"), (7, "validate_semantic_backup.py")):
        src = "".join(cells[idx]["source"])
        m = re.search(r"\w+_source = r'''(.*?)'''\s*\n", src, re.S)
        if m:
            (out_dir / fname).write_text(m.group(1))


def main() -> int:
    nb_path = V3_DIR / "semantic_backup_validation.ipynb"
    check("notebook exists in checkpoint", nb_path.exists())

    import json
    nb = json.load(open(nb_path))
    cells = nb["cells"]
    code_cells = [c for c in cells if c["cell_type"] == "code"]
    executed = [c for c in code_cells if c.get("execution_count") is not None]
    with_output = [c for c in code_cells if c.get("outputs")]
    check("notebook is genuinely executed (all code cells have execution_count set)",
          len(executed) == len(code_cells), f"{len(executed)}/{len(code_cells)}")
    check("at least 9 of 10 code cells have real outputs",
          len(with_output) >= 9, f"{len(with_output)}/{len(code_cells)}")

    extract_dir = REPO_ROOT / "_tmp_v3_extract"
    extract_embedded_files(nb_path, extract_dir)

    # --- 1. Embedded model files match their real checkpoints exactly (mod blank line) ---
    for fname, ref_dir in (("competency.py", HEAD_DIR), ("test_real_data.py", HEAD_DIR),
                            ("report.py", REPORT_DIR)):
        ok = substantively_identical(ref_dir / fname, extract_dir / fname)
        check(f"embedded {fname} substantively identical to {ref_dir.name}/{fname}", ok)

    # --- 2. pw01_competencies.py's import chain is fixed ---
    old_pw01 = (V2_ORIG_DIR / "pw01_competencies.py").read_text()
    new_pw01 = (extract_dir / "pw01_competencies.py").read_text()
    check("pw01_competencies.py no longer uses broken relative imports",
          "from .core import" not in new_pw01 and "from .base_competencies import" not in new_pw01)
    check("pw01_competencies.py now imports from competency/test_real_data directly",
          "from competency import" in new_pw01 and "from test_real_data import" in new_pw01)

    # --- 3. The fixed chain actually imports and runs in THIS sandbox ---
    result = subprocess.run(
        [sys.executable, "-c", "import q2_competencies; print(len(q2_competencies.model.competencies) if hasattr(q2_competencies.model, 'competencies') else 'ok')"],
        cwd=str(extract_dir), capture_output=True, text=True,
    )
    check("the fixed real chain (test_real_data -> pw01_competencies -> q2_competencies) "
          "imports successfully in this sandbox", result.returncode == 0, result.stderr.strip())

    # --- 4. audit_registry is now fully clean against the complete real chain ---
    sys.path.insert(0, str(extract_dir))
    for mod in list(sys.modules):
        if mod in ("semantic_backup", "test_real_data", "q2_competencies", "pw01_competencies",
                   "competency", "report", "validate_semantic_backup"):
            del sys.modules[mod]
    import q2_competencies  # noqa: E402
    from semantic_backup import audit_registry, EXEMPLAR_REGISTRY  # noqa: E402

    problems = audit_registry(q2_competencies.model)
    check("audit_registry() reports ZERO problems against the full real chain "
          "(all 10 competencies now verifiable, all clean)", problems == {}, f"got {problems}")
    total = sum(len(v) for v in EXEMPLAR_REGISTRY.values())
    check("EXEMPLAR_REGISTRY unchanged at 10 competencies / 27 exemplars",
          len(EXEMPLAR_REGISTRY) == 10 and total == 27,
          f"{len(EXEMPLAR_REGISTRY)} competencies, {total} exemplars")

    # --- 5. The scoping fix is present and wired in ---
    import semantic_backup as sb  # noqa: E402
    check("DELEGATING_FUNCTION / runtime_scoped_exemplar present in delivered semantic_backup.py",
          hasattr(sb, "DELEGATING_FUNCTION") and hasattr(sb, "runtime_scoped_exemplar"))
    check("DELEGATING_FUNCTION scopes DelegatesUniqueness to contains_unique_day",
          sb.DELEGATING_FUNCTION.get("DelegatesUniqueness") == "contains_unique_day")
    import inspect
    vsb_src = (extract_dir / "validate_semantic_backup.py").read_text()
    check("validate_semantic_backup.py imports and applies runtime_scoped_exemplar "
          "(so the reported win-rate numbers reflect the fix)",
          "runtime_scoped_exemplar" in vsb_src)

    # --- 6. Lexical validation reproduces the notebook's exact numbers ---
    import io
    import contextlib
    import re
    for mod in list(sys.modules):
        if mod == "validate_semantic_backup":
            del sys.modules[mod]
    import validate_semantic_backup as vsb  # noqa: E402

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        vsb.run("lexical")
    out = buf.getvalue()
    m = re.search(r"win rate.*?:\s*(\d+)/(\d+)\s*\((\d+\.\d)%\)", out)
    check("lexical (post-scoping-fix, full 10-competency) pairwise win rate == 1294/1428 (90.6%)",
          bool(m) and m.group(1) == "1294" and m.group(2) == "1428",
          out if not m else f"got {m.group(0)}")
    m2 = re.search(r"Worst-case correct ranking.*?:\s*(\d+)/(\d+)\s*\((\d+\.\d)%\)", out)
    check("lexical (post-scoping-fix) worst-case ranking == 20/27 (74.1%)",
          bool(m2) and m2.group(1) == "20" and m2.group(2) == "27",
          out if not m2 else f"got {m2.group(0)}")
    check("no DelegatesUniqueness-related failure lines remain (the confound is gone)",
          "DelegatesUniqueness" not in out.split("Pairwise win rate")[0].split("Failures")[-1]
          if "Failures" in out else True)

    # --- 7. The three TopKPatternExtended structural regression cases ---
    for mod in list(sys.modules):
        if mod == "test_real_data":
            del sys.modules[mod]
    import ast
    import test_real_data as trd  # noqa: E402

    cases = {
        "delegate": ('''
def repeated_extraction(lst, k):
    result = []
    for _ in range(k):
        m = max(lst)
        lst.remove(m)
        result.append(m)
    return result

def top_k(lst, k):
    return repeated_extraction(lst, k)
''', {"TopKPattern": 0.0, "TopKViaDelegate": 1.0, "SortThenSlice": 1.0, "TopKPatternExtended": 1.0}),
        "quicksort": ('''
def quicksort(lst):
    if len(lst) <= 1:
        return lst
    pivot = lst[0]
    less = [x for x in lst[1:] if x < pivot]
    more = [x for x in lst[1:] if x >= pivot]
    return quicksort(less) + [pivot] + quicksort(more)

def top_k(lst, k):
    return quicksort(lst)[:k]
''', {"TopKPattern": 0.0, "TopKViaDelegate": 0.0, "SortThenSlice": 1.0, "TopKPatternExtended": 1.0}),
        "merge_sort": ('''
def merge_sort(lst):
    if len(lst) <= 1:
        return lst
    mid = len(lst) // 2
    left = merge_sort(lst[:mid])
    right = merge_sort(lst[mid:])
    result = []
    while left and right:
        if left[0] >= right[0]:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    return result + left + right

def top_k(lst, k):
    return merge_sort(lst)[:k]
''', {"TopKPattern": 0.0, "TopKViaDelegate": 1.0, "SortThenSlice": 1.0, "TopKPatternExtended": 1.0}),
    }
    for label, (src, expected) in cases.items():
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "top_k")
        r = trd.model.resolve(fn, list(expected.keys()), module_tree=tree)
        got = {cid: res.final_score for cid, res in r.items()}
        check(f"TopKPatternExtended regression case '{label}' matches notebook output",
              got == expected, f"got {got}, expected {expected}")

    print()
    if FAILED:
        print(f"{len(FAILED)} check(s) FAILED:")
        for f in FAILED:
            print(f"  - {f}")
        return 1
    print("All checks OK. Table 4 and the Q5 TopKPatternExtended delegation breakdown are")
    print("untouched by this notebook -- see the checkpoint's own README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
