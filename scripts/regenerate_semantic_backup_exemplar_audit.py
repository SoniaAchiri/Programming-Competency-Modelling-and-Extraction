#!/usr/bin/env python3
"""Regenerate the semantic backup layer's exemplar-registry audit and discriminative-power check
(the "mine_exemplars" round, 2026-08-07 -- detectors/mine-exemplars/).

This is a DIFFERENT stage from every other semantic-backup evidence already in this repo:
  - It is NOT the novel-vs-wrong AUC finding (regenerate_semantic_backup_auc.py) -- that measures
    whether the layer separates genuinely-novel-correct submissions from genuinely-wrong ones.
  - It is NOT the embedding-clustering discovery (detectors/q5-delegation-clustering-fix/)
    that led to the TopKPatternExtended fix -- that is Q5 structural-layer work, unaffected by
    anything here.
  - It IS a check of the exemplar registry itself: (a) does every exemplar actually satisfy the
    structural rule it claims to represent (audit_registry()), and (b) can an embedding backend tell
    one competency's exemplars apart from another's and from unrelated code at all (the SAME/CROSS/
    UNRELATED held-out design in validate_semantic_backup.py)?

What this script mechanically reproduces, importing the delivered code directly and running it
against the closest-dated real competency model this repo has (detectors/q1-shared-binding-fix,
the checkpoint immediately preceding this round's 2026-08-07 files):

  1. audit_registry() against the real resolver: every competency's exemplars should verify at
     final_score >= 0.999 EXCEPT AccumulateThenCount, which is expected to come back as "not
     registered in the given model" for all of its exemplars -- it lives in q2_competencies.py /
     pw01_competencies.py, neither of which this project has ever been supplied, so this project
     genuinely cannot verify it, and does not pretend otherwise.
  2. The two corrected GuardedInput exemplars individually score final_score == 1.0 (the bug this
     round found and fixed: the original pair used a bare `while` condition with no nested `if`,
     which the developer's own competency.py at the time did not recognize as TEST evidence at all).
  3. validate_semantic_backup.py's lexical-backend run reproduces the developer-reported pairwise win
     rate (86.7%) and this script additionally reports the worst-case correct-ranking figure (not
     quoted in the source conversation, so independently produced here, not merely checked).

What this script deliberately does NOT check, and why:
  - The codet5p backend: huggingface.co is confirmed blocked from this sandbox too (a 403 at the
    proxy, checked directly -- see the checkpoint's own README), consistent with every earlier round
    of this project. No codet5p number in any document is independently reproducible from here.
  - Whether the ORIGINAL (pre-fix) bare-`while` GuardedInput shape actually scores 0.0 -- reconstructing
    that exact shape and running it against THIS repo's closest-dated real competency.py
    (q1-shared-binding-fix) scores 1.0, not 0.0 (three independent phrasing variants all
    score 1.0). This does not mean the developer's finding was wrong -- it means whatever competency.py
    they were actually running against at the time most likely predates the Q1 all_names/while-condition
    fix (2026-08-05), consistent with this project's own already-documented "two different working
    environments" pattern. See the checkpoint's README for the full writeup; this script does not
    assert a specific final_score for that reconstructed shape, since the real original exemplar text
    was never supplied and reconstructing it exactly is guesswork this project's discipline avoids.
  - Mining against the real Refactory corpus: mine_exemplars.py's CONFIG only covers 6 of the
    eventual competencies (Accumulation and AccumulateThenCount are explicit TODOs in the script
    itself), and no mined_exemplars.json is present in this round's upload -- the corpus was not
    available in the environment that built this round. This script instead unit-tests the
    canonicalization/dedup mechanism directly (alpha-renaming should collapse naming-only variants,
    not genuine structural differences), since that is the only part of the mining logic checkable
    without the real corpus.

Per Sonia's explicit instruction, nothing here changes or touches Table 4 (Q1-Q5 headline coverage) or
the Q5 TopKPatternExtended delegation breakdown (91.9%/80.6%, the 57-catch breakdown) -- those stay
exactly as already logged and verified. This script is scoped entirely to the semantic backup layer's
exemplar registry.

Usage:
    python scripts/regenerate_semantic_backup_exemplar_audit.py
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_DIR = REPO_ROOT / "detectors" / "mine-exemplars"
MODEL_CHECKPOINT_DIR = REPO_ROOT / "detectors" / "q1-shared-binding-fix"

EXPECTED_LEXICAL_WIN_RATE = 0.867  # rounded to 3dp, as reported in the source conversation (470/542)
EXPECTED_LEXICAL_WIN_COUNT = (470, 542)
EXPECTED_CLEAN_EXCEPT = {"AccumulateThenCount"}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    # Load the real, dated competency model closest to this checkpoint's own date, and this
    # checkpoint's delivered semantic_backup.py / validate_semantic_backup.py / mine_exemplars.py.
    sys.path.insert(0, str(MODEL_CHECKPOINT_DIR))
    sys.path.insert(0, str(CHECKPOINT_DIR))
    trd = _load_module("test_real_data", MODEL_CHECKPOINT_DIR / "test_real_data.py")
    sb = _load_module("semantic_backup", CHECKPOINT_DIR / "semantic_backup.py")
    _load_module("validate_semantic_backup", CHECKPOINT_DIR / "validate_semantic_backup.py")
    mine = _load_module("mine_exemplars", CHECKPOINT_DIR / "mine_exemplars.py")

    ok = True

    # 1. audit_registry() -- expect clean except AccumulateThenCount.
    problems = sb.audit_registry(trd.model)
    flagged = set(problems.keys())
    print(f"audit_registry() flagged: {sorted(flagged) or '(nothing)'}")
    if flagged != EXPECTED_CLEAN_EXCEPT:
        print(f"  [FAIL] expected only {EXPECTED_CLEAN_EXCEPT} to be flagged")
        ok = False
    else:
        print(f"  [OK] registry is clean except the known-unverifiable {EXPECTED_CLEAN_EXCEPT}")
        for msg in problems["AccumulateThenCount"]:
            print(f"      {msg}")

    # 2. Both corrected GuardedInput exemplars score exactly 1.0.
    print("\nGuardedInput exemplar scores (post-fix):")
    for i, src in enumerate(sb.EXEMPLAR_REGISTRY["GuardedInput"]):
        res = trd.model.resolve(ast.parse(src), ["GuardedInput"])["GuardedInput"]
        status = "OK" if res.final_score == 1.0 else "FAIL"
        print(f"  exemplar #{i}: final_score={res.final_score}  [{status}]")
        if res.final_score != 1.0:
            ok = False

    # 3. Lexical discriminative-power validation -- reproduce the reported win rate exactly, and
    #    report the worst-case ranking figure the source conversation did not quote.
    print("\nLexical SAME/CROSS/UNRELATED validation:")
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        import validate_semantic_backup as vsb

        vsb.run("lexical")
    output = buf.getvalue()
    print(output)

    import re

    win_line = next(line for line in output.splitlines() if "Pairwise win rate" in line)
    match = re.search(r"(\d+)/(\d+)", win_line)
    win_count, win_total = int(match.group(1)), int(match.group(2))
    if (win_count, win_total) != EXPECTED_LEXICAL_WIN_COUNT:
        print(f"  [FAIL] win count/total {win_count}/{win_total} != expected {EXPECTED_LEXICAL_WIN_COUNT}")
        ok = False
    else:
        print(f"  [OK] pairwise win rate {win_count}/{win_total} matches the source conversation's reported 86.7% exactly")

    # 4. Unit-test the mining script's canonicalization/dedup mechanism directly (no real corpus
    #    available in this sandbox either -- see docstring).
    print("\nmine_exemplars.py canonicalization check (synthetic, no real corpus required):")
    a = "def f(x, y):\n    z = x + y\n    return z\n"
    b = "def f(p, q):\n    r = p + q\n    return r\n"  # alpha-renamed only
    c = "def f(x, y):\n    z = x - y\n    return z\n"  # genuinely different body
    same = mine.canonical_key(a) == mine.canonical_key(b)
    different = mine.canonical_key(a) == mine.canonical_key(c)
    print(f"  alpha-renamed-only pair collapses to the same key: {same}  [{'OK' if same else 'FAIL'}]")
    print(f"  genuinely-different body collapses too (should be False): {different}  "
          f"[{'OK' if not different else 'FAIL'}]")
    if not same or different:
        ok = False

    print("\n" + "=" * 88)
    if ok:
        print("All checks [OK]. Table 4 and the Q5 TopKPatternExtended delegation breakdown are")
        print("untouched by this stage -- see the checkpoint's own README.md for the full writeup.")
        print("The bare-while reconstruction question noted above is no longer open -- see")
        print("../detectors/mine-exemplars-real-corpus/ and")
        print("regenerate_semantic_backup_v2_audit.py, which resolve it with the actual")
        print("competency.py this round's development used.")
    else:
        print("Some checks [FAIL] -- see output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
