




"""
Discriminative-power validation for the semantic backup layer.

The methodology doc is explicit that this was the one thing never actually
checked: "the stand-in embedding used to test the surrounding plumbing was
directly shown to have essentially no discriminative power between related
and unrelated code." This script is that check, run properly, using the
same positive-control / negative-control discipline used everywhere else in
this project's validation methodology (Section 2.6 / Section 4).

For every competency with >=2 exemplars, each exemplar is held out in turn
and compared against:
  - SAME:      its own competency's remaining exemplar(s)      -- should be HIGH
  - CROSS:     other competencies' exemplars                   -- should be LOWER
  - UNRELATED: deliberately irrelevant code (string formatting,
               file I/O, etc., sharing no structural pattern
               with anything in the registry)                  -- should be LOWEST

Two summary metrics are reported, deliberately not just one:

  - "worst-case correct ranking": requires the BEST same-competency
    similarity to beat the WORST cross/unrelated similarity, out of every
    comparison made. This is what earlier runs of this script reported as
    a single "correct ranking %" number. It is an extremely strict
    criterion -- with 8 competencies here, each held-out case is compared
    against ~110+ cross/unrelated exemplars, and it only takes ONE outlier
    among those to fail the case. At this exemplar-set size, the metric
    is close to all-or-nothing regardless of embedding quality, which is
    why it stayed pinned at 20% for codet5p even though the underlying
    similarity means clearly separated further than lexical's did. Kept
    here for continuity with earlier runs, not as the primary verdict.

  - "pairwise win rate" (the standard AUC / Mann-Whitney statistic): the
    fraction of ALL (same-pair, other-pair) comparisons where the
    same-competency similarity is higher. 0.5 = no better than chance,
    1.0 = perfect separation. This is the metric actually used for the
    verdict below, because it reflects average-case separation instead of
    being decided by a single worst-case outlier -- the right lens given
    how few exemplars exist per competency right now.

Usage:
    python validate_semantic_backup.py --backend lexical
    python validate_semantic_backup.py --backend codet5p   # needs torch+transformers+network
    python validate_semantic_backup.py --backend all       # both, side by side
"""

from __future__ import annotations

import argparse
import itertools
import json
import statistics

import numpy as np

from semantic_backup import EXEMPLAR_REGISTRY, embed_cached, get_embedder, runtime_scoped_exemplar

UNRELATED_SNIPPETS = [
    """
def greet(name):
    print("Hello, " + name + "!")
""",
    """
def read_config(path):
    with open(path) as f:
        lines = f.readlines()
    return [line.strip() for line in lines]
""",
    """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
""",
]


def run(backend: str, registry: dict | None = None, label: str = "") -> None:
    registry = registry if registry is not None else EXEMPLAR_REGISTRY
    header = f"backend = {backend!r}" + (f"  registry = {label!r}" if label else "")
    print(f"\n{'='*72}\n{header}\n{'='*72}")
    try:
        get_embedder(backend)  # fail fast with a clear error, before any comparisons
    except RuntimeError as e:
        print(f"  SKIPPED -- backend unavailable: {e}")
        return

    cids = [cid for cid, exs in registry.items() if len(exs) >= 1]
    scoreable_cids = [cid for cid in cids if len(registry[cid]) >= 2]
    # Scope every exemplar down to what report.py would actually embed at
    # runtime before any similarity is computed (identity for every cid
    # except DelegatesUniqueness right now). Without this, exemplars that
    # need extra context to VERIFY (DELEGATES needing its callee present)
    # also get embedded WITH that extra context -- comparing against a
    # strictly easier, unrealistic target no real submission ever produces.
    all_exemplars = {
        cid: [runtime_scoped_exemplar(cid, e) for e in exs]
        for cid, exs in registry.items()
    }

    skipped = [cid for cid in cids if cid not in scoreable_cids]
    if skipped:
        print(f"  (skipping held-out test for {len(skipped)} single-exemplar "
              f"competencies -- nothing to hold them out against: {', '.join(skipped)})")

    same_sims, cross_sims, unrelated_sims = [], [], []
    correct_margin = 0
    total_cases = 0
    win_count = 0
    win_total = 0
    # For diagnosing REAL confusions (e.g. two competencies that are
    # legitimately similar in shape) vs. noise: track, per held-out case,
    # what beat it and by how much.
    worst_case_failures = []

    unrelated_vecs = embed_cached(backend, UNRELATED_SNIPPETS)

    for cid in scoreable_cids:
        exemplars = all_exemplars[cid]
        vecs = embed_cached(backend, exemplars)
        for held_out_idx in range(len(exemplars)):
            query = vecs[held_out_idx]
            others_same = [vecs[i] for i in range(len(exemplars)) if i != held_out_idx]

            same_vals = [float(query @ v) for v in others_same]
            cross_pairs = [
                (other_cid, float(query @ v))
                for other_cid in cids if other_cid != cid
                for v in embed_cached(backend, all_exemplars[other_cid])
            ]
            unrel_vals = [float(query @ v) for v in unrelated_vecs]
            other_vals = [v for _, v in cross_pairs] + unrel_vals

            same_sims.extend(same_vals)
            cross_sims.extend(v for _, v in cross_pairs)
            unrelated_sims.extend(unrel_vals)

            total_cases += 1
            best_same = max(same_vals) if same_vals else None
            worst_other = max(other_vals) if other_vals else None
            if best_same is not None and worst_other is not None:
                if best_same > worst_other:
                    correct_margin += 1
                else:
                    beater_cid = next(
                        (c for c, v in cross_pairs if v == worst_other), "UNRELATED"
                    )
                    worst_case_failures.append((cid, beater_cid, best_same, worst_other))

            # Pairwise win rate: every (same, other) comparison counts
            # independently, so one outlier can't flip an entire case.
            for s in same_vals:
                for o in other_vals:
                    win_total += 1
                    if s > o:
                        win_count += 1

    def summarize(name, vals):
        if not vals:
            print(f"  {name:10s}  (n/a -- no pairs)")
            return
        print(f"  {name:10s}  mean={statistics.mean(vals):+.3f}  "
              f"median={statistics.median(vals):+.3f}  n={len(vals)}")

    print(f"\n  Competencies with exemplars: {len(cids)}  |  held-out cases: {total_cases}\n")
    summarize("SAME", same_sims)
    summarize("CROSS", cross_sims)
    summarize("UNRELATED", unrelated_sims)

    pct = 100.0 * correct_margin / total_cases if total_cases else 0.0
    print(f"\n  Worst-case correct ranking (best SAME > worst of ALL others): "
          f"{correct_margin}/{total_cases} ({pct:.1f}%)  [strict, see docstring]")
    if worst_case_failures:
        print("    Failures (what beat the held-out SAME pair):")
        for cid, beater_cid, best_same, worst_other in worst_case_failures:
            print(f"      {cid:20s} best_same={best_same:+.3f}  "
                  f"beaten by {beater_cid:20s} sim={worst_other:+.3f}")

    win_rate = win_count / win_total if win_total else 0.0
    print(f"\n  Pairwise win rate (SAME beats random OTHER): "
          f"{win_count}/{win_total} ({win_rate:.1%})  [standard AUC-style metric]")
    if win_rate >= 0.85:
        verdict = "strong discriminative power"
    elif win_rate >= 0.65:
        verdict = "real, moderate discriminative power -- better than chance, not yet strong"
    elif win_rate >= 0.55:
        verdict = "weak discriminative power -- only marginally better than chance"
    else:
        verdict = "little to no discriminative power (same failure mode as the original stub)"
    print(f"  Verdict: {verdict}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        choices=["lexical", "codet5p", "both", "all"],
        default="all",
    )
    parser.add_argument(
        "--registry-file", default=None,
        help="Path to a JSON exemplar registry (e.g. from mine_exemplars.py's "
             "--out) to validate INSTEAD OF the hand-written EXEMPLAR_REGISTRY "
             "in semantic_backup.py. Use --compare-registries to run both.",
    )
    parser.add_argument(
        "--compare-registries", action="store_true",
        help="With --registry-file set, run BOTH the hand-written and the "
             "mined registry for each backend, back to back, instead of "
             "replacing one with the other. No effect without --registry-file.",
    )
    args = parser.parse_args()

    if args.backend in ("both", "all"):
        backends = ["lexical", "codet5p"]
    else:
        backends = [args.backend]

    mined_registry = None
    if args.registry_file:
        with open(args.registry_file, encoding="utf-8") as f:
            mined_registry = json.load(f)

    for b in backends:
        if mined_registry is None:
            run(b)
        elif args.compare_registries:
            run(b, registry=None, label="hand-written")
            run(b, registry=mined_registry, label="mined")
        else:
            run(b, registry=mined_registry, label="mined")




