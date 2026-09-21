"""
Regenerates every independently-checkable claim from the second mine_exemplars
batch (detectors/mine-exemplars-real-corpus/, delivered 2026-09-17,
content-dated 2026-08-08/09 in the accompanying conversation transcript).

This is a VERIFICATION script, not a re-run of the original mining. This
sandbox has never had the real Refactory corpus, so the corpus-scan claims
in the conversation (e.g. "ConditionalCount: 248/291 real submissions verify") stay
evidence: conversation_reported_only -- they are not checked here and this script
does not pretend otherwise.

What IS independently checked here, all against the exact files delivered
this round (nothing patched to make it pass):

  1. The "Original files to load" bundle's competency.py and test_real_data.py
     are byte-for-byte IDENTICAL to detectors/fixq4 (0 diff lines)
     -- i.e. this round's mining environment used a competency.py that
     PREDATES the 2026-08-05 Q1 SHARED_BINDING/all_names fix. report.py is
     byte-for-byte identical to detectors/semantic-backup (predates
     the 2026-07-21 function_name-scoping fix). Confirmed by diff, not
     assumed.

  2. pw01_competencies.py, as delivered, cannot be imported standalone in
     this sandbox: it has unresolved relative imports (`from .core import
     ...`, `from .base_competencies import model, show`) to submodules never
     supplied to this project in any round. Confirmed by direct import
     attempt (ImportError), not inferred from reading the source.

  3. Because of (2), AccumulateThenCount, FunctionalUniqueCheck, and
     DelegatesUniqueness cannot be independently audited against a live
     model in this sandbox -- audit_registry() correctly reports them as
     "not registered" when run against test_real_data.py's model alone
     (which is everything this sandbox CAN construct from the delivered
     files). This is the same practical gap as the first mine_exemplars
     round, but for a different, more specific reason this time (a broken
     import chain in code that WAS delivered, not a module that was never
     delivered at all).

  4. GuardedInput's two (corrected) exemplars both verify at final_score=1.0
     against test_real_data.py's own model -- independently confirmed, not
     just re-quoted.

  5. THE PREVIOUSLY-OPEN BARE-WHILE DISCREPANCY FROM ROUND 1 IS NOW RESOLVED
     WITH HARD EVIDENCE. Round 1's audit reconstructed the original,
     pre-fix bare-while GuardedInput exemplar and resolved it against this
     repo's closest-dated real competency.py at the time
     (detectors/q1-shared-binding-fix) -- scoring final_score=1.0,
     not the claimed 0.0, leaving an open, hypothesized-but-unconfirmed
     explanation on file. This round supplies the ACTUAL competency.py used
     for the original mine_exemplars work (confirmed identical to fixQ4 per
     check #1), and resolving the same bare-while reconstruction against
     THAT exact file scores final_score=0.0 -- exactly as originally
     claimed. The reason: fixQ4's TEST primitive detector only synthesizes
     evidence from `ast.If` nodes; the `elif isinstance(node, ast.While):`
     branch that lets a while loop's own condition register as TEST
     evidence was added BY the 2026-08-05 Q1 fix. Round 1's reconstruction
     used a competency.py that had already gained that branch, which is
     exactly why it scored differently. This confirms round 1's own
     hypothesis (the "two different working environments" pattern) was
     correct, but it was a hypothesis then and is now a diff-and-execution
     confirmed fact.

  6. The delivered semantic_backup.py's EXEMPLAR_REGISTRY is real: 10
     competencies, 27 exemplars total (matches the "10 competencies, 27
     exemplars" figure the two 2026-08-xx reference documents described as
     a finished future state -- that state is now backed by real delivered
     code for the registry itself, though NOT for Table 4/Q5, which remain
     untouched per Sonia's explicit instruction, and NOT for the real
     corpus mining numbers, which remain conversation_reported_only).

  7. The delivered semantic_cache.zip contains REAL cached embeddings (not
     placeholders): lexical.pkl (24 x 4096-d vectors) and codet5p.pkl (24 x
     256-d vectors, the real Salesforce/codet5p-110m-embedding output
     dimensionality). Of the 27 registry exemplars, exactly 21 (the
     8-competency subset that excludes FunctionalUniqueCheck and
     DelegatesUniqueness, added later in the same dev session) have cached
     codet5p vectors, plus 3 more cache entries matching
     validate_semantic_backup.py's 3 UNRELATED_SNIPPETS exactly -- 24
     total, confirmed by content-hash cross-reference, not assumed.

  8. Using ONLY those real cached codet5p vectors (a guard raises loudly if
     anything not already cached is requested, proving no live network call
     or fabricated value sneaks in), running the delivered
     validate_semantic_backup.py's own run() function against the
     8-competency subset EXACTLY reproduces every number in the conversation's
     first codet5p block: SAME mean=+0.615/median=+0.552/n=42, CROSS
     mean=+0.400/median=+0.374/n=378, UNRELATED mean=+0.303/median=+0.294/
     n=63, worst-case 16/21 (76.2%), all 5 named failure lines, and the
     pairwise win rate 696/852 (81.7%).

  9. Running the same delivered validate_semantic_backup.py's lexical
     backend (deterministic, no cache/network dependency at all) against
     the FULL current 10-competency/27-exemplar registry EXACTLY reproduces
     every number in the conversation's "10/08" lexical block: SAME
     mean=+0.648/median=+0.657/n=54, CROSS mean=+0.416/median=+0.408/n=648,
     UNRELATED mean=+0.295/median=+0.285/n=81, worst-case 15/27 (55.6%),
     all 12 named failure lines, and the pairwise win rate 1262/1428
     (88.4%).

What this script deliberately does NOT check (left exactly as
conversation_reported_only, no code/CSV/corpus to check them against in this
sandbox):
  - The real-corpus mining scan counts (248/291, 2/291, 13/291, 227/291,
    etc.) -- no Refactory corpus has ever been supplied to this project.
  - The 10-competency codet5p run (84.2% win rate, 81.5% worst-case) --
    6 of the 10 competencies' exemplars (FunctionalUniqueCheck,
    DelegatesUniqueness) have no cached codet5p vectors in the delivered
    semantic_cache.zip, and huggingface.co remains blocked from every
    sandbox this project has used.
  - The DelegatesUniqueness/ConditionalCount surface-containment scoping
    fix (DELEGATING_FUNCTION / runtime_scoped_exemplar, reported lexical
    90.6%/74.1%) -- not present anywhere in the delivered semantic_backup.py
    (grep-confirmed absent). Described in the conversation as implemented and
    tested, but the code implementing it was never actually delivered to
    this project.
  - Table 4 and the Q5 TopKPatternExtended delegation breakdown -- nothing
    in this batch touches either; both remain exactly as previously
    verified, per Sonia's explicit standing instruction.

Exits 1 if any check fails.
"""
from __future__ import annotations

import difflib
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
V2_DIR = REPO_ROOT / "detectors" / "mine-exemplars-real-corpus"
ORIG_FILES_DIR = V2_DIR / "original_files_used_this_round"
FIXQ4_DIR = REPO_ROOT / "detectors" / "fixq4"
REPORT_2026_07_20_DIR = REPO_ROOT / "detectors" / "semantic-backup"

FAILED = []


def check(label, condition, detail=""):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" -- {detail}" if detail and not condition else ""))
    if not condition:
        FAILED.append(label)


def diff_line_count(a: Path, b: Path) -> int:
    a_lines = a.read_text().splitlines()
    b_lines = b.read_text().splitlines()
    return sum(1 for _ in difflib.unified_diff(a_lines, b_lines, lineterm=""))


def main() -> int:
    # --- 1. Dating: original files used this round match specific, earlier
    #        real checkpoints exactly -----------------------------------
    n = diff_line_count(FIXQ4_DIR / "competency.py", ORIG_FILES_DIR / "competency.py")
    check("original competency.py == detectors/fixq4/competency.py (0 diff lines)",
          n == 0, f"{n} diff lines")

    n = diff_line_count(FIXQ4_DIR / "test_real_data.py", ORIG_FILES_DIR / "test_real_data.py")
    check("original test_real_data.py == detectors/fixq4/test_real_data.py (0 diff lines)",
          n == 0, f"{n} diff lines")

    n = diff_line_count(REPORT_2026_07_20_DIR / "report.py", ORIG_FILES_DIR / "report.py")
    check("original report.py == detectors/semantic-backup/report.py (0 diff lines)",
          n == 0, f"{n} diff lines")

    # --- 2. pw01_competencies.py is confirmed broken (relative imports) --
    result = subprocess.run(
        [sys.executable, "-c", "import pw01_competencies"],
        cwd=str(ORIG_FILES_DIR), capture_output=True, text=True,
    )
    check("pw01_competencies.py fails to import standalone (relative import to "
          "never-supplied .core/.base_competencies)",
          result.returncode != 0 and "attempted relative import" in result.stderr,
          result.stderr.strip().splitlines()[-1] if result.stderr else "(no stderr)")

    # --- 3/4. audit_registry against the only model this sandbox CAN build,
    #          and GuardedInput specifically clean -----------------------
    sys.path.insert(0, str(ORIG_FILES_DIR))
    sys.path.insert(0, str(V2_DIR))
    for mod in ("test_real_data", "semantic_backup"):
        sys.modules.pop(mod, None)
    import test_real_data as trd_v2  # noqa: E402
    import semantic_backup as sb_v2  # noqa: E402

    problems = sb_v2.audit_registry(trd_v2.model)
    expected_unverifiable = {"AccumulateThenCount", "FunctionalUniqueCheck", "DelegatesUniqueness"}
    check("audit_registry flags exactly {AccumulateThenCount, FunctionalUniqueCheck, "
          "DelegatesUniqueness} as unverifiable (broken pw01_competencies.py chain), nothing else",
          set(problems.keys()) == expected_unverifiable, f"got {set(problems.keys())}")
    check("GuardedInput has zero audit warnings (both corrected exemplars verify at 1.0)",
          "GuardedInput" not in problems)

    # --- 5. The bare-while discrepancy from round 1, resolved -----------
    import ast
    bare_while_src = '''
def guarded(items, target):
    i = 0
    while i < len(items) and items[i] != target:
        i += 1
    return i
'''
    res = trd_v2.model.resolve(ast.parse(bare_while_src), ["GuardedInput"])["GuardedInput"]
    check("bare-while GuardedInput reconstruction scores final_score=0.0 against the ACTUAL "
          "competency.py used this round (fixQ4-era) -- resolves round 1's open discrepancy",
          res.final_score == 0.0, f"got final_score={res.final_score}")

    # --- 6. Registry shape: 10 competencies, 27 exemplars ----------------
    total = sum(len(v) for v in sb_v2.EXEMPLAR_REGISTRY.values())
    check("EXEMPLAR_REGISTRY has exactly 10 competencies", len(sb_v2.EXEMPLAR_REGISTRY) == 10,
          f"got {len(sb_v2.EXEMPLAR_REGISTRY)}")
    check("EXEMPLAR_REGISTRY has exactly 27 exemplars total", total == 27, f"got {total}")

    # --- 7/8/9. Cache-backed codet5p (8-competency subset) + lexical (full
    #            10-competency) reproduction, using ONLY real cached data --
    os.environ["SEMANTIC_BACKUP_CACHE_DIR"] = str(V2_DIR / ".semantic_cache")
    for mod in ("semantic_backup", "validate_semantic_backup"):
        sys.modules.pop(mod, None)
    import semantic_backup as sb  # noqa: E402  (re-import with cache dir set)
    sys.path.insert(0, str(V2_DIR))
    import validate_semantic_backup as vsb  # noqa: E402

    class _NoNetworkGuard:
        def embed(self, texts):
            raise RuntimeError(
                f"tried to compute {len(texts)} FRESH codet5p embeddings (would need network) "
                "-- these are not already in the delivered cache"
            )

    def guarded_get_embedder(backend):
        if backend == "codet5p":
            return _NoNetworkGuard()
        return sb.get_embedder.__wrapped__(backend) if hasattr(sb.get_embedder, "__wrapped__") \
            else _orig_get_embedder(backend)

    _orig_get_embedder = sb.get_embedder
    sb.get_embedder = guarded_get_embedder
    vsb.get_embedder = guarded_get_embedder
    vsb.embed_cached = sb.embed_cached

    import io
    import contextlib
    import re

    EIGHT = {k: v for k, v in sb.EXEMPLAR_REGISTRY.items()
             if k not in ("FunctionalUniqueCheck", "DelegatesUniqueness")}

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        vsb.run("codet5p", registry=EIGHT, label="8-competency subset, real cache only")
    out = buf.getvalue()
    m = re.search(r"win rate.*?:\s*(\d+)/(\d+)\s*\((\d+\.\d)%\)", out)
    check("codet5p (8-competency, real cache) pairwise win rate == 696/852 (81.7%)",
          bool(m) and m.group(1) == "696" and m.group(2) == "852",
          out if not m else f"got {m.group(0)}")
    m2 = re.search(r"Worst-case correct ranking.*?:\s*(\d+)/(\d+)\s*\((\d+\.\d)%\)", out)
    check("codet5p (8-competency, real cache) worst-case ranking == 16/21 (76.2%)",
          bool(m2) and m2.group(1) == "16" and m2.group(2) == "21",
          out if not m2 else f"got {m2.group(0)}")

    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        vsb.run("lexical")  # full current 10-competency registry, no cache needed
    out2 = buf2.getvalue()
    m3 = re.search(r"win rate.*?:\s*(\d+)/(\d+)\s*\((\d+\.\d)%\)", out2)
    check("lexical (full 10-competency registry) pairwise win rate == 1262/1428 (88.4%)",
          bool(m3) and m3.group(1) == "1262" and m3.group(2) == "1428",
          out2 if not m3 else f"got {m3.group(0)}")
    m4 = re.search(r"Worst-case correct ranking.*?:\s*(\d+)/(\d+)\s*\((\d+\.\d)%\)", out2)
    check("lexical (full 10-competency registry) worst-case ranking == 15/27 (55.6%)",
          bool(m4) and m4.group(1) == "15" and m4.group(2) == "27",
          out2 if not m4 else f"got {m4.group(0)}")

    print()
    if FAILED:
        print(f"{len(FAILED)} check(s) FAILED:")
        for f in FAILED:
            print(f"  - {f}")
        return 1
    print("All checks OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
