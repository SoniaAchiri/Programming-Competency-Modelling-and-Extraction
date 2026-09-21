"""
Exemplar mining: replace hand-written exemplars with real, structurally-
verified student submissions from the Refactory corpus.

Uses the REAL model chain (test_real_data.py -> pw01_competencies.py ->
q2_competencies.py) now that pw01_competencies.py is available -- this
replaces the earlier q2_extra.py reconstruction, which was verified to
match the real chain exactly (0 mismatches across 20 real submissions and
both ConditionalCount/AccumulateThenCount) before being retired.

Covers four competencies from question_2/code/correct/*.py:
  - ConditionalCount, AccumulateThenCount (scoped to `unique_day`)
  - FunctionalUniqueCheck (scoped to `unique_day`) -- the third real
    strategy the project's own comments describe: map()/filter() pipelines
    with no explicit loop at all.
  - DelegatesUniqueness (scoped to `contains_unique_day`, with the full
    module tree passed through) -- a cross-function competency: does
    contains_unique_day correctly delegate its uniqueness check to a
    unique_day that itself implements ConditionalCount, per DELEGATES.
"""

import ast
import glob
import hashlib

import q2_competencies  # registers ConditionalCount (via test_real_data),

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

                         # AccumulateThenCount, FunctionalUniqueCheck,
                         # DelegatesUniqueness, etc. onto one shared model
model = q2_competencies.model

QUESTION_2_DIR = f"{REFACTORY_ROOT}/data/question_2/code/correct"


def _extract_function(source: str, name: str):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None, None
    fn = next(
        (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name),
        None,
    )
    if fn is None:
        return None, None
    return fn, tree


def _normalized_shape(fn_node: ast.FunctionDef) -> str:
    """A crude structural fingerprint: the AST dumped with variable names
    stripped, so 'count vs counter vs num_matches' don't count as distinct
    shapes for diversity-selection purposes."""
    class Anonymize(ast.NodeTransformer):
        def visit_Name(self, node):
            return ast.copy_location(ast.Name(id="_", ctx=node.ctx), node)

        def visit_arg(self, node):
            node.arg = "_"
            return node

    anon = Anonymize().visit(ast.parse(ast.unparse(fn_node)))
    return ast.dump(anon)


def mine(cid: str, function_name: str, folder: str, limit: int = 6):
    candidates = []  # (filename, source_text, shape_hash)
    for filepath in sorted(glob.glob(f"{folder}/*.py")):
        source = open(filepath, encoding="utf-8").read()
        fn_node, tree = _extract_function(source, function_name)
        if fn_node is None:
            continue
        try:
            results = model.resolve(fn_node, [cid], module_tree=tree)
        except Exception:
            continue
        res = results.get(cid)
        if res is None or res.final_score < 0.999:
            continue
        snippet = ast.get_source_segment(source, fn_node)
        shape = hashlib.sha256(_normalized_shape(fn_node).encode()).hexdigest()
        candidates.append((filepath.split("/")[-1], snippet, shape))

    print(f"\n{cid}: {len(candidates)} / "
          f"{len(glob.glob(f'{folder}/*.py'))} submissions verified at final_score=1.0")

    # Diversity selection: keep the first submission seen for each distinct
    # normalized shape, so near-duplicates (same logic, renamed variables)
    # don't crowd out genuinely different implementations.
    seen_shapes = {}
    for fname, snippet, shape in candidates:
        if shape not in seen_shapes:
            seen_shapes[shape] = (fname, snippet)

    diverse = list(seen_shapes.values())[:limit]
    print(f"  {len(seen_shapes)} distinct structural shapes found; keeping {len(diverse)}")
    for fname, snippet in diverse:
        print(f"\n  --- {fname} ---")
        print("  " + snippet.replace("\n", "\n  "))

    return diverse


def mine_cross_function(cid: str, function_name: str, folder: str, limit: int = 6):
    """Like mine(), but for competencies (e.g. DelegatesUniqueness) whose
    structural constraints (DELEGATES) need to see sibling functions in the
    same file -- so the whole module tree is passed through to resolve(),
    not just the target function in isolation."""
    candidates = []
    for filepath in sorted(glob.glob(f"{folder}/*.py")):
        source = open(filepath, encoding="utf-8").read()
        fn_node, tree = _extract_function(source, function_name)
        if fn_node is None:
            continue
        try:
            results = model.resolve(fn_node, [cid], module_tree=tree)
        except Exception:
            continue
        res = results.get(cid)
        if res is None or res.final_score < 0.999:
            continue
        snippet = ast.get_source_segment(source, fn_node)
        shape = hashlib.sha256(_normalized_shape(fn_node).encode()).hexdigest()
        candidates.append((filepath.split("/")[-1], snippet, shape))

    print(f"\n{cid}: {len(candidates)} / "
          f"{len(glob.glob(f'{folder}/*.py'))} submissions verified at final_score=1.0")

    seen_shapes = {}
    for fname, snippet, shape in candidates:
        if shape not in seen_shapes:
            seen_shapes[shape] = (fname, snippet)

    diverse = list(seen_shapes.values())[:limit]
    print(f"  {len(seen_shapes)} distinct structural shapes found; keeping {len(diverse)}")
    for fname, snippet in diverse:
        print(f"\n  --- {fname} ---")
        print("  " + snippet.replace("\n", "\n  "))

    return diverse


if __name__ == "__main__":
    cc = mine("ConditionalCount", "unique_day", QUESTION_2_DIR)
    atc = mine("AccumulateThenCount", "unique_day", QUESTION_2_DIR)
    print("\n" + "=" * 70)
    print("Also checking unique_month (same strategy space, different domain)")
    print("=" * 70)
    cc_month = mine("ConditionalCount", "unique_month", QUESTION_2_DIR)
    atc_month = mine("AccumulateThenCount", "unique_month", QUESTION_2_DIR)

    print("\n" + "=" * 70)
    print("Third real strategy: FunctionalUniqueCheck (map()/filter() pipelines)")
    print("=" * 70)
    func = mine("FunctionalUniqueCheck", "unique_day", QUESTION_2_DIR)

    print("\n" + "=" * 70)
    print("Cross-function: DelegatesUniqueness (contains_unique_day -> unique_day)")
    print("=" * 70)
    deleg = mine_cross_function("DelegatesUniqueness", "contains_unique_day", QUESTION_2_DIR)
