"""
Semantic similarity backup layer.

Purpose: when the rule-based AST detectors (primitives + structural
constraints) find little or nothing for a competency, ask a second,
INDEPENDENT question -- "does this code look semantically similar to
known-correct implementations of this competency?" -- via code
embeddings (CodeBERT).

Non-negotiable design principle, consistent with every other part of
this system: this NEVER modifies final_score. Structural/coverage
scoring stays the sole, evidence-backed, inspectable source of truth.
Semantic similarity is reported as a SEPARATE, clearly labeled field --
a flag for a human to review, not a substitute for structural evidence.
A high similarity score means "this is worth a second look," not
"credit this."

Concrete gap this fills: things like functools.reduce-based extremum
finding (no ast.If, no explicit loop, no max()/min() call -- invisible
to SelectionStep AND FindExtremumBuiltin) or other genuinely novel
strategies no one has written a structural constraint for yet.

HONEST STATUS OF THIS FILE:
Real CodeBERT inference requires downloading microsoft/codebert-base
from huggingface.co. This development sandbox's network egress does
NOT permit that (confirmed directly: 403, x-deny-reason:
host_not_allowed -- not assumed). The `_codebert_embed` function below
is written to be correct and usable as-is in any environment with
Hugging Face access, but it has NOT been executed end-to-end here.

A lightweight stand-in backend (`stub`) is provided so the surrounding
architecture -- exemplar registry, caching, thresholding, report
integration -- can be built and tested now. The stub is a bag-of-AST-
tokens cosine similarity: NOT semantically meaningful the way a trained
code model is, and it will generically over-rate similarity between any
two well-formed Python functions (they share many common AST node types
regardless of actual content). Do not use stub-mode scores as evidence
of anything; it exists only to prove the plumbing works. Switching to
real CodeBERT is a one-line change: backend="codebert".
"""

import ast
import math
from collections import Counter
from functools import lru_cache


# ---------------------------------------------------------------------------
# Exemplar registry: competency_id -> known-correct reference snippets.
# Instructors extend this as they see novel real strategies show up in
# submissions that the structural rules don't recognize.
# ---------------------------------------------------------------------------

EXEMPLARS = {
    "FindExtremum": [
        "def f(lst):\n    best = lst[0]\n    for x in lst:\n        if x > best:\n            best = x\n    return best",
        "def f(lst):\n    return max(lst)",
        "def f(lst):\n    import functools\n    return functools.reduce(lambda a, b: a if a > b else b, lst)",
    ],
    "Accumulation": [
        "def f(nums):\n    total = 0\n    for x in nums:\n        total += x\n    return total",
        "def f(nums):\n    return sum(nums)",
    ],
}


# ---------------------------------------------------------------------------
# Embedding backends
# ---------------------------------------------------------------------------

def _codebert_embed(code: str):
    """Real CodeBERT embedding via microsoft/codebert-base. Requires
    Hugging Face network access on first call (cached locally after that
    by the `transformers` library itself). NOT executed in this sandbox --
    written to be correct, not verified end-to-end here."""
    import torch
    from transformers import AutoTokenizer, AutoModel

    if not hasattr(_codebert_embed, "_model"):
        _codebert_embed._tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        _codebert_embed._model = AutoModel.from_pretrained("microsoft/codebert-base")
        _codebert_embed._model.eval()

    tok = _codebert_embed._tokenizer
    model = _codebert_embed._model
    inputs = tok(code, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        out = model(**inputs)
    return out.last_hidden_state.mean(dim=1).squeeze().numpy()


def _stub_embed(code: str) -> Counter:
    """NOT semantically meaningful. A bag-of-AST-node-type-and-identifier
    vector, used only to test that registry/caching/thresholding/report
    wiring works end-to-end where real CodeBERT cannot be reached."""
    try:
        tree = ast.parse(code)
        tokens = [n.id for n in ast.walk(tree) if isinstance(n, ast.Name)]
        tokens += [type(n).__name__ for n in ast.walk(tree)]
    except SyntaxError:
        tokens = code.split()
    return Counter(tokens)


def embed(code: str, backend: str = "stub"):
    return _codebert_embed(code) if backend == "codebert" else _stub_embed(code)


def _cosine_counter(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def _cosine_vec(a, b) -> float:
    import numpy as np
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na and nb else 0.0


def similarity(a, b, backend: str = "stub") -> float:
    return _cosine_vec(a, b) if backend == "codebert" else _cosine_counter(a, b)


@lru_cache(maxsize=None)
def _cached_exemplar_embedding(competency_id: str, exemplar_index: int, backend: str):
    return embed(EXEMPLARS[competency_id][exemplar_index], backend=backend)


def semantic_backup_score(source_snippet: str, competency_id: str, backend: str = "stub"):
    """Returns None if no exemplars are registered for this competency
    (nothing to compare against -- silence, not a fabricated zero).
    Otherwise returns the max similarity to any registered exemplar, the
    matching exemplar's index, and which backend produced it -- always
    to be reported as unverified/heuristic, never folded into final_score."""
    if not EXEMPLARS.get(competency_id):
        return None
    target_emb = embed(source_snippet, backend=backend)
    best_sim, best_idx = -1.0, -1
    for i in range(len(EXEMPLARS[competency_id])):
        ex_emb = _cached_exemplar_embedding(competency_id, i, backend)
        sim = similarity(target_emb, ex_emb, backend=backend)
        if sim > best_sim:
            best_sim, best_idx = sim, i
    return {"max_similarity": round(best_sim, 3), "best_match_exemplar_index": best_idx, "backend": backend}
