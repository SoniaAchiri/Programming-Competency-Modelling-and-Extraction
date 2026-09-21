"""
Mine exemplars from real corpus submissions, instead of hand-writing them.

Every exemplar in semantic_backup.py's EXEMPLAR_REGISTRY today is something
I wrote by hand: clean, small, single-strategy illustrations. That made the
unique_day confound (see semantic_backup_findings.md, finding #5) easy to
diagnose precisely, but it also means the validation has been measuring
"can the embedding separate MY idealized examples," not "can it separate
the messy real code it will actually see in production" -- a train/test
mismatch worth closing.

This script does the mining half of that: for each competency, scan a
corpus of real submissions, keep only the ones the STRUCTURAL rules already
score a clean 1.0 on (so we're not trusting the embedding to pick its own
training data -- the deterministic rules remain the source of truth, same
as everywhere else in this project), deduplicate near-identical submissions
so the exemplar set isn't dominated by copy-paste clusters, and write out a
capped, diverse sample per competency as a separate registry file.

Deliberately NOT merged automatically into semantic_backup.py's
EXEMPLAR_REGISTRY -- mined output should get a human skim before being
trusted (the same "auditable, human-checked" principle this whole project
runs on), and keeping it separate lets validate_semantic_backup.py A/B the
hand-written registry against the mined one instead of silently overwriting
a baseline we already spent several rounds validating.

USAGE
-----
1. Fill in / extend CONFIG below with each competency's (model module,
   model attribute, corpus glob, optional function_name to scope to).
   Several entries are pre-filled from test_real_data.py's own __main__
   demos, which already point at real Refactory question folders. Others
   are left as TODO because they come from files not available when this
   script was written (e.g. AccumulateThenCount depends on
   pw01_competencies.py, which imports a corpus this project's other
   scripts reference but which wasn't included in the current uploads) --
   fill in the real path once you have it rather than guessing.

2. Run in an environment with the actual corpus on disk (e.g. Colab, next
   to your other project files):

       python mine_exemplars.py --cap 4 --out mined_exemplars.json

3. Skim mined_exemplars.json before trusting it -- this script prints a
   preview of what it selected specifically so that skim is easy, not so
   you can skip it.

4. To validate the mined registry instead of (or alongside) the
   hand-written one:

       python validate_semantic_backup.py --backend lexical \\
           --registry-file mined_exemplars.json
"""

from __future__ import annotations

import argparse
import ast
import glob
import json
import random
from collections import defaultdict

# --- Refactory corpus location -----------------------------------------
# Not the sandbox this was originally developed in: override with the
# REFACTORY_ROOT environment variable, or drop the corpus at
# <repo-root>/refactory/ (its default location, resolved relative to this
# file so it works regardless of the current working directory).
import os as _os
REFACTORY_ROOT = _os.environ.get(
    "REFACTORY_ROOT",
    _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "refactory")),
)
# -------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# CONFIG -- fill in per competency
# ---------------------------------------------------------------------------
# Each entry: cid -> {
#   "model_module": the .py file (without extension) that registers this
#       competency, e.g. "test_real_data" for the model built in that file,
#   "model_attr": the variable name of the CompetencyModel in that module
#       (almost always "model", per this project's own convention),
#   "corpus_glob": a glob pattern for the source folder,
#   "function_name": optional -- scope resolution to one function per file,
#       matching report.py's own function_name parameter. Leave None to
#       resolve against the whole file, same as test_real_data.py's demos.
# }
#
# Pre-filled from test_real_data.py's own __main__ block, which already
# demonstrates exactly which real folder each competency's example
# submissions live in -- not guessed.
CONFIG = {
    "Swap": {
        "model_module": "test_real_data",
        "model_attr": "model",
        "corpus_glob": f"{REFACTORY_ROOT}/data/question_4/code/correct/*.py",
        "function_name": None,
    },
    "GuardedInput": {
        "model_module": "test_real_data",
        "model_attr": "model",
        "corpus_glob": f"{REFACTORY_ROOT}/data/question_1/code/correct/*.py",
        "function_name": None,
    },
    "SelectionStep": {
        "model_module": "test_real_data",
        "model_attr": "model",
        "corpus_glob": f"{REFACTORY_ROOT}/data/question_5/code/correct/*.py",
        "function_name": None,
    },
    "FindExtremumBuiltin": {
        "model_module": "test_real_data",
        "model_attr": "model",
        "corpus_glob": f"{REFACTORY_ROOT}/data/question_5/code/correct/*.py",
        "function_name": None,
    },
    "TopKPattern": {
        "model_module": "test_real_data",
        "model_attr": "model",
        "corpus_glob": f"{REFACTORY_ROOT}/data/question_5/code/correct/*.py",
        "function_name": None,
    },
    "ConditionalCount": {
        "model_module": "test_real_data",
        "model_attr": "model",
        "corpus_glob": f"{REFACTORY_ROOT}/data/question_2/code/correct/*.py",
        "function_name": None,
    },
    # TODO: Accumulation isn't demonstrated against a specific Refactory
    # folder anywhere in the uploaded scripts (it's registered generically
    # in test_real_data.py, but only exercised there via synthetic
    # snippets, not a real corpus glob) -- find and fill in its real source
    # folder before mining it.
    # "Accumulation": {...},
    #
    # TODO: AccumulateThenCount is registered in q2_competencies.py against
    # a model imported from pw01_competencies.py, a file this script
    # doesn't have access to -- confirm whether its real submissions live
    # in the same question_2 folder as ConditionalCount above, or a
    # separate PW01-specific corpus, before filling this in. Do not assume
    # they're the same folder just because both handle "unique_day".
    # "AccumulateThenCount": {...},
}


# ---------------------------------------------------------------------------
# Canonicalization -- for near-duplicate detection, alpha-renaming based
# rather than embedding-based deliberately. Using either backend under test
# (lexical or codet5p) to pick that same backend's own exemplars would be
# circular; a structural, embedding-free method keeps mining independent of
# whichever backend gets validated against the result.
# ---------------------------------------------------------------------------

class _Canonicalizer(ast.NodeTransformer):
    """Renames every identifier (variables, function names, parameters) to
    v0, v1, ... in order of first appearance, so two submissions that are
    identical except for variable-naming choices collapse to the same key."""

    def __init__(self):
        self.mapping: dict[str, str] = {}
        self.counter = 0

    def _rename(self, name: str) -> str:
        if name not in self.mapping:
            self.mapping[name] = f"v{self.counter}"
            self.counter += 1
        return self.mapping[name]

    def visit_Name(self, node):
        node.id = self._rename(node.id)
        return node

    def visit_arg(self, node):
        node.arg = self._rename(node.arg)
        return node

    def visit_FunctionDef(self, node):
        node.name = self._rename(node.name)
        self.generic_visit(node)
        return node


def canonical_key(source: str) -> str:
    tree = ast.parse(source)
    tree = _Canonicalizer().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.dump(tree, annotate_fields=False, include_attributes=False)


# ---------------------------------------------------------------------------
# Mining
# ---------------------------------------------------------------------------

def find_full_score_submissions(corpus_glob, model, cid, function_name=None):
    """Real submissions the STRUCTURAL rules already score a clean 1.0 on
    for `cid`. The rules stay the source of truth for what counts as a
    valid exemplar -- this never trusts an embedding to select its own
    training data."""
    hits = []
    for filepath in sorted(glob.glob(corpus_glob)):
        try:
            source = open(filepath, encoding="utf-8").read()
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            continue

        if function_name is not None:
            target = next(
                (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == function_name),
                None,
            )
            if target is None:
                continue
            results = model.resolve(target, [cid], module_tree=tree)
            snippet = ast.get_source_segment(source, target)
        else:
            results = model.resolve(tree, [cid])
            snippet = source

        res = results.get(cid)
        if res is not None and res.final_score >= 0.999:
            hits.append((filepath, snippet))
    return hits


def select_diverse(hits, cap, seed=0):
    """One representative per unique structural shape (via canonical_key),
    then a capped random sample across those shapes -- so a handful of
    near-identical submissions (a common real-corpus pattern: several
    students converge on the exact same solution) don't crowd out genuinely
    different strategies."""
    groups = defaultdict(list)
    for filepath, snippet in hits:
        groups[canonical_key(snippet)].append((filepath, snippet))
    reps = [group[0] for group in groups.values()]
    random.Random(seed).shuffle(reps)
    return reps[:cap], len(groups)


def mine(cap: int, seed: int):
    import importlib

    mined: dict[str, list[str]] = {}
    for cid, cfg in CONFIG.items():
        module = importlib.import_module(cfg["model_module"])
        model = getattr(module, cfg["model_attr"])

        hits = find_full_score_submissions(
            cfg["corpus_glob"], model, cid, function_name=cfg["function_name"]
        )
        if not hits:
            print(f"  {cid:22s} 0 full-score submissions found -- check corpus_glob / cid")
            continue

        selected, n_unique_shapes = select_diverse(hits, cap, seed=seed)
        mined[cid] = [snippet for _, snippet in selected]

        print(f"  {cid:22s} {len(hits):4d} full-score  ->  {n_unique_shapes:3d} unique shapes  "
              f"->  kept {len(selected)}")
        for filepath, snippet in selected:
            first_line = snippet.strip().splitlines()[0]
            print(f"      {filepath.split('/')[-1]:24s} {first_line}")

    return mined


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cap", type=int, default=4, help="max exemplars per competency")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default="mined_exemplars.json")
    args = parser.parse_args()

    print(f"Mining up to {args.cap} exemplars per competency from {len(CONFIG)} configured competencies...\n")
    result = mine(args.cap, args.seed)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    skipped = [cid for cid in CONFIG if cid not in result]
    print(f"\nWrote {args.out} ({len(result)} competencies).")
    if skipped:
        print(f"Skipped (no full-score hits found): {', '.join(skipped)}")
    unconfigured = ["Accumulation", "AccumulateThenCount"]
    print(f"Not configured yet (see TODOs in CONFIG): {', '.join(unconfigured)}")
    print("\nSKIM THIS BEFORE TRUSTING IT -- these are real, unedited student submissions.")
