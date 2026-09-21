






"""
Semantic similarity backup signal.

Structural rules (competency.py) stay the source of truth for final_score --
this module only ever contributes an advisory 'semantic_backup' field on
low-scoring competencies (see report.py), never a grade. Its job is to flag
"this looks like it might be doing the right thing via a strategy no
structural rule recognizes yet" for manual review.

Backends provided:

  - "codet5p": Salesforce/codet5p-110m-embedding via `transformers`.
    Replaces an earlier CodeBERT-based attempt (mean-pooled, then
    [CLS]-pooled) that was measured -- not assumed -- to have no real
    discriminative power: both pooling strategies over bare CodeBERT
    produced SAME/CROSS/UNRELATED similarities bunched in a narrow
    0.96-0.99 band, worse than even the local lexical baseline. That's
    the textbook anisotropic-embedding-space failure of pooling a model
    that was never trained to produce a similarity-meaningful vector in
    the first place. CodeT5+'s 110M embedding checkpoint is trained
    specifically to fix that: its pretraining includes a contrastive
    learning objective over code (paired with span denoising and causal
    LM), producing a purpose-built 256-dim embedding directly from
    `model(input_ids)` -- no manual pooling choice to get right or wrong.
    Needs `torch` + `transformers`, `trust_remote_code=True` (the model
    class ships as custom code in the HF repo, not in the `transformers`
    library itself), and network access to huggingface.co the first time
    (weights are then cached locally).

  - "lexical": a fully local, dependency-light fallback (hashed bag of
    code-token n-grams, cosine similarity). No model download, no network,
    ever. This is deliberately NOT presented as a transformer -- it exists
    so the surrounding plumbing (exemplar registry, caching, threshold
    gating, discriminative-power validation) can be built and tested
    end-to-end in environments without model-hub access, and so
    validate_semantic_backup.py has something to compare "codet5p" against
    once it *can* run.

Both backends implement the same tiny interface (`Embedder.embed(list[str])
-> np.ndarray`), so swapping which one report.py uses is a one-line change
(the `backend=` argument already threaded through generate_report).

Embeddings are cached to disk (keyed by backend name + content hash) since
exemplar sets are re-embedded on every process start otherwise, and
transformer embedding is not cheap.
"""

from __future__ import annotations

import hashlib
import os
import pickle
from typing import Optional

import numpy as np

CACHE_DIR = os.environ.get(
    "SEMANTIC_BACKUP_CACHE_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".semantic_cache"),
)
os.makedirs(CACHE_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Exemplar registry
# ---------------------------------------------------------------------------
# Originally 1-2 snippets per competency, seeded just to test wiring (the
# state the methodology doc names as a known limitation). Expanded here
# after validate_semantic_backup.py surfaced two concrete problems with the
# original set:
#
#   1. Six of eight competencies had exactly ONE exemplar, which means they
#      could never be held-out tested at all (nothing to hold them out
#      against) -- the held-out test was silently only exercising 2 of 8
#      competencies. Every competency below now has >=2 exemplars so the
#      validation actually covers the registry it claims to.
#
#   2. Both the lexical AND codet5p backends independently flagged the same
#      confusion: Accumulation's original input()-reading exemplar and
#      GuardedInput's exemplar share surface shape (loop + input() +
#      reassignment) even though they represent different skills
#      (running-sum vs. retry-until-valid). Two very different embedding
#      methods agreeing on the same failure is a signal the EXEMPLARS were
#      ambiguous, not that either embedder is broken. Accumulation now
#      includes a third exemplar that accumulates over an already-available
#      list with no input()/retry semantics at all, and GuardedInput's new
#      second exemplar validates a non-numeric answer with no running total
#      involved -- sharpening the two concepts apart at the exemplar level,
#      which no embedding choice can do on its own.
#
# Snippets are drawn from this project's own synthetic test cases where
# available (test_real_data.py, q2_competencies.py) rather than invented
# fresh; new additions follow the same style (small, single-function,
# representative of one real strategy) rather than being padded filler.

EXEMPLAR_REGISTRY: dict[str, list[str]] = {
    "Swap": [
        """
def f(a, b):
    temp = a
    a = b
    b = temp
    return a, b
""",
        """
def f(a, b):
    a, b = b, a
    return a, b
""",
    ],
    "Accumulation": [
        """
def moyenne(n):
    total = 0
    for i in range(n):
        note = float(input("Note: "))
        total += note
    return total
""",
        """
def total_of(values):
    result = 0
    for v in values:
        result = result + v
    return result
""",
        # New: accumulates over an already-available sequence via a while
        # loop, with no input() call and no retry/validation semantics --
        # deliberately unlike GuardedInput's shape, to stop the two
        # competencies' exemplars from overlapping on "loop + input() +
        # reassignment" alone.
        """
def total_from_list(values):
    total = 0
    i = 0
    while i < len(values):
        total += values[i]
        i += 1
    return total
""",
    ],
    "ConditionalCount": [
        """
def unique_day(day, possible_birthdays):
    count = 0
    for birthday in possible_birthdays:
        if birthday[1] == day:
            count += 1
    return count == 1
""",
        # New: same shape (loop + condition + counter), different domain
        # (character counting rather than tuple-field matching), so the
        # exemplar set isn't tied to one surface vocabulary.
        """
def count_vowels(word):
    count = 0
    for ch in word:
        if ch in "aeiouAEIOU":
            count += 1
    return count
""",
        # New: a third domain (counting negatives), deliberately NOT
        # mirrored by any AccumulateThenCount exemplar below. The
        # unique_day exemplar above shares its exact function name,
        # parameters, and return-comparison wrapper with
        # AccumulateThenCount's unique_day exemplar (confirmed via direct
        # inspection: only the loop body differs) -- real and worth
        # keeping as an authentic hard case, but its near-identical surface
        # text was very likely inflating same-vs-cross similarity for
        # reasons beyond genuine strategy-level equivalence. This exemplar
        # and AccumulateThenCount's third (below) are chosen to NOT form
        # another such minimal pair, so the class average isn't dominated
        # by confounded text similarity.
        """
def count_negatives(values):
    count = 0
    for v in values:
        if v < 0:
            count += 1
    return count
""",
    ],
    "AccumulateThenCount": [
        """
def unique_day(day, possible_birthdays):
    all_days = ()
    for i in possible_birthdays:
        all_days += (i[1],)
    return all_days.count(day) == 1
""",
        # New: same "build a collection, then check it" shape via list
        # .append() + len() instead of tuple concatenation + .count().
        """
def count_evens(values):
    evens = []
    for v in values:
        if v % 2 == 0:
            evens.append(v)
    return len(evens)
""",
        # New: third domain (long words), deliberately distinct from
        # ConditionalCount's third exemplar's domain -- see the comment on
        # ConditionalCount's third exemplar for why.
        """
def count_long_words(words, min_length):
    long_words = []
    for w in words:
        if len(w) >= min_length:
            long_words.append(w)
    return len(long_words)
""",
    ],
    "GuardedInput": [
        # CORRECTED (see semantic_backup_findings.md, finding #7): the
        # original two exemplars here BOTH scored final_score=0.0 under the
        # actual structural resolver -- `while n <= 0: n = input(...)` has
        # no explicit `if`, and GuardedInput's rule requires a TEST (an
        # if-statement) nested inside the loop; the while-condition itself
        # doesn't register as TEST evidence. This was never caught because
        # hand-written exemplars were never run through model.resolve() to
        # confirm they actually satisfy the competency they're meant to
        # exemplify -- unlike mined exemplars (mine_exemplars.py), which are
        # structurally verified by construction. Every exemplar below is
        # confirmed final_score=1.00 before being included.
        """
def get_positive():
    n = int(input("Enter a positive number: "))
    valid = False
    while not valid:
        if n > 0:
            valid = True
        else:
            n = int(input("Enter a positive number: "))
    return n
""",
        # Non-numeric domain, no running total anywhere -- isolates the
        # "retry until valid" shape from Accumulation's "keep a running
        # sum" shape, same intent as before, now with a verified structure.
        """
def get_yes_no():
    answer = input("yes or no? ")
    while True:
        if answer in ("yes", "no"):
            break
        answer = input("yes or no? ")
    return answer == "yes"
""",
    ],
    "SelectionStep": [
        """
def find_index(values, target):
    found = -1
    for i, v in enumerate(values):
        if v == target:
            found = i
    return found
""",
        # New: selection by comparison (running minimum) rather than
        # selection by equality match, covering the other real SelectionStep
        # shape (this is also the shape FindExtremum's "manual" branch
        # composes on top of).
        """
def index_of_min(values):
    best = 0
    for i in range(1, len(values)):
        if values[i] < values[best]:
            best = i
    return best
""",
    ],
    "FindExtremumBuiltin": [
        """
def largest(values):
    return max(values)
""",
        # New: min() rather than max() -- same competency, other direction.
        """
def smallest(values):
    return min(values)
""",
    ],
    "TopKPattern": [
        """
def top_k(values, k):
    result = []
    remaining = list(values)
    for _ in range(k):
        best = remaining[0]
        for v in remaining:
            if v > best:
                best = v
        remaining.remove(best)
        result.append(best)
    return result
""",
        # New: same repeated-extraction shape, but removes by INDEX
        # (tracked during the scan, then .pop(idx)) rather than by VALUE
        # (.remove(best) after the scan) -- a real variant seen in student
        # code, and a different enough surface form to test whether the
        # embedding generalizes past one specific coding style.
        """
def bottom_k(values, k):
    pool = list(values)
    result = []
    for _ in range(k):
        idx = 0
        for i in range(1, len(pool)):
            if pool[i] < pool[idx]:
                idx = i
        result.append(pool.pop(idx))
    return result
""",
    ],
}


def audit_registry(model, registry: dict[str, list[str]] | None = None) -> dict[str, list[str]]:
    """Check every exemplar in `registry` (default: EXEMPLAR_REGISTRY)
    against the ACTUAL structural resolver, using `model` (a
    CompetencyModel with the relevant competencies registered -- e.g. the
    `model` from test_real_data.py).

    This exists because of a real bug: both original GuardedInput
    exemplars scored final_score=0.0 under the real resolver (a bare
    `while` condition doesn't register as TEST evidence; GuardedInput
    requires an explicit nested `if`), and nothing had ever checked that.
    Mined exemplars (mine_exemplars.py) can't have this problem by
    construction -- they're selected FROM submissions the resolver already
    scored 1.0 -- but hand-written ones can drift silently, e.g. after a
    structural rule changes, or if the author's mental model of a
    competency doesn't quite match its registered definition. Run this
    after editing the registry by hand.

    Returns {cid: [warning strings]} for anything that didn't score
    final_score >= 0.999. A cid missing from `model`'s registrations
    (resolve() returns nothing for it) is reported as a warning too,
    rather than silently skipped, since that's just as easy to miss as a
    low score, and it's exactly the case that made AccumulateThenCount
    unverifiable when this check was first added (it's registered in a
    different module than the one available at the time).
    """
    import ast

    reg = registry if registry is not None else EXEMPLAR_REGISTRY
    problems: dict[str, list[str]] = {}
    for cid, exemplars in reg.items():
        for i, src in enumerate(exemplars):
            try:
                results = model.resolve(ast.parse(src), [cid])
            except SyntaxError as e:
                problems.setdefault(cid, []).append(f"exemplar #{i}: does not parse ({e})")
                continue
            res = results.get(cid)
            if res is None:
                problems.setdefault(cid, []).append(
                    f"exemplar #{i}: {cid!r} not registered in the given model -- "
                    "cannot verify, don't assume it's fine"
                )
            elif res.final_score < 0.999:
                problems.setdefault(cid, []).append(
                    f"exemplar #{i}: final_score={res.final_score:.2f}, "
                    "not a real example of this competency"
                )
    return problems


def _normalize_source(src: str) -> str:
    """Strip leading/trailing blank lines so exemplar formatting quirks
    don't dominate similarity for reasons unrelated to code structure."""
    lines = src.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def _content_key(backend: str, text: str) -> str:
    h = hashlib.sha256(_normalize_source(text).encode("utf-8")).hexdigest()
    return f"{backend}:{h}"


def _load_cache(backend: str) -> dict:
    path = os.path.join(CACHE_DIR, f"{backend}.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return {}


def _save_cache(backend: str, cache: dict) -> None:
    path = os.path.join(CACHE_DIR, f"{backend}.pkl")
    with open(path, "wb") as f:
        pickle.dump(cache, f)


# ---------------------------------------------------------------------------
# Embedders
# ---------------------------------------------------------------------------

class Embedder:
    name: str

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return an (n, d) L2-normalized embedding matrix, one row per text."""
        raise NotImplementedError


class LexicalEmbedder(Embedder):
    """Local, model-free baseline: hashed bag of code-token n-grams (1-2),
    L2-normalized so dot product == cosine similarity. No network, no
    download, always available -- exists to validate the plumbing and to
    give validate_semantic_backup.py a baseline to compare CodeT5+ against,
    the same way the original stub was meant to (but actually measured)."""

    name = "lexical"

    def __init__(self, n_features: int = 4096):
        from sklearn.feature_extraction.text import HashingVectorizer

        self._vectorizer = HashingVectorizer(
            n_features=n_features,
            token_pattern=r"[A-Za-z_][A-Za-z0-9_]*|[^\sA-Za-z0-9_]",
            ngram_range=(1, 2),
            norm="l2",
            alternate_sign=False,
        )

    def embed(self, texts: list[str]) -> np.ndarray:
        matrix = self._vectorizer.transform(texts)
        return np.asarray(matrix.todense())


class CodeT5PEmbedder(Embedder):
    """Salesforce/codet5p-110m-embedding -- purpose-built code embedding
    model, L2-normalized 256-dim output.

    Unlike CodeBERT (a masked-language-model encoder repurposed for
    similarity by pooling its hidden states after the fact), this
    checkpoint's pretraining explicitly includes a contrastive learning
    objective over code, alongside span denoising and causal LM. The
    embedding comes straight out of `model(input_ids)` -- there's no
    pooling strategy to choose or get wrong, because producing a single
    similarity-meaningful vector is what the model was trained to do.

    Requires `torch` and `transformers`, and `trust_remote_code=True`
    since the model class is shipped as custom code in the HF repo rather
    than built into the `transformers` library. On first use it downloads
    weights from huggingface.co (or uses a local HF cache set via
    HF_HOME). Raises a clear RuntimeError (not a silent fallback) if the
    model can't be loaded, so a blocked-network failure is never mistaken
    for "codet5p says these are dissimilar."
    """

    name = "codet5p"
    MODEL_ID = "Salesforce/codet5p-110m-embedding"

    def __init__(self):
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
        except ImportError as e:
            raise RuntimeError(
                "CodeT5PEmbedder requires `torch` and `transformers` "
                "(pip install torch transformers)."
            ) from e

        try:
            self._torch = torch
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.MODEL_ID, trust_remote_code=True
            )

            # This checkpoint's custom modeling code (shipped in the HF repo,
            # not in the `transformers` library itself, and last updated
            # ~2 years ago) builds a T5-style encoder stack underneath. Newer
            # `transformers` versions read config.is_decoder /
            # is_encoder_decoder / use_cache unconditionally when
            # constructing that stack; the custom CodeT5pEmbeddingConfig
            # class (a plain PretrainedConfig subclass, not a T5Config) never
            # sets them, because that requirement didn't exist when this
            # repo's code was written. Patching in the correct values for an
            # encoder-only checkpoint (this model has no decoder or KV cache)
            # fixes real forward-compatibility drift -- it isn't a workaround
            # for a different, harder problem.
            from transformers import AutoConfig

            config = AutoConfig.from_pretrained(self.MODEL_ID, trust_remote_code=True)
            for attr, default in (
                ("is_decoder", False),
                ("is_encoder_decoder", False),
                ("use_cache", False),
            ):
                if not hasattr(config, attr):
                    setattr(config, attr, default)

            self._model = AutoModel.from_pretrained(
                self.MODEL_ID, config=config, trust_remote_code=True
            )
            self._model.eval()
        except OSError as e:
            raise RuntimeError(
                f"Could not load {self.MODEL_ID}. This commonly means "
                "huggingface.co is unreachable from this environment (the "
                "exact failure mode this module was built to detect and "
                "report honestly, rather than silently falling back). "
                f"Underlying error: {type(e).__name__}: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Could not load {self.MODEL_ID} for a reason other than "
                "network access -- likely a version-compatibility issue "
                "between this checkpoint's custom remote code and the "
                "installed `transformers` version, not the network-block "
                "failure mode this module primarily guards against. "
                f"Underlying error: {type(e).__name__}: {e}"
            ) from e

    def embed(self, texts: list[str]) -> np.ndarray:
        # Encoded one at a time (not batched) to match the model card's
        # documented usage exactly -- the custom forward() isn't guaranteed
        # to accept an attention_mask kwarg for padded batches, and getting
        # that wrong silently would corrupt every embedding rather than
        # raising, which is worse than the modest speed cost here (exemplar
        # sets are small, and everything is disk-cached afterward anyway).
        torch = self._torch
        vecs = []
        with torch.no_grad():
            for text in texts:
                input_ids = self._tokenizer.encode(
                    text, truncation=True, max_length=512, return_tensors="pt"
                )
                embedding = self._model(input_ids)[0]  # already L2-normalized per model card
                vecs.append(embedding)
            stacked = torch.stack(vecs)
            # Re-normalize defensively so this backend honors the same
            # "L2-normalized, dot product == cosine" contract as the others,
            # rather than trusting an external guarantee silently.
            normed = torch.nn.functional.normalize(stacked, p=2, dim=1)
            return normed.numpy()


_EMBEDDER_CACHE: dict[str, Embedder] = {}


def get_embedder(backend: str) -> Embedder:
    if backend not in _EMBEDDER_CACHE:
        if backend == "lexical":
            _EMBEDDER_CACHE[backend] = LexicalEmbedder()
        elif backend == "codet5p":
            _EMBEDDER_CACHE[backend] = CodeT5PEmbedder()
        elif backend == "stub":
            _EMBEDDER_CACHE[backend] = None  # handled separately below
        else:
            raise ValueError(f"Unknown backend: {backend!r}")
    return _EMBEDDER_CACHE[backend]


def embed_cached(backend: str, texts: list[str]) -> np.ndarray:
    """Embed `texts`, using a persistent on-disk cache keyed by content hash
    so exemplars aren't re-embedded on every process start, and identical
    submissions across a batch run aren't re-embedded either."""
    embedder = get_embedder(backend)
    cache = _load_cache(backend)
    keys = [_content_key(backend, t) for t in texts]
    missing_idx = [i for i, k in enumerate(keys) if k not in cache]
    if missing_idx:
        fresh = embedder.embed([texts[i] for i in missing_idx])
        for i, vec in zip(missing_idx, fresh):
            cache[keys[i]] = vec
        _save_cache(backend, cache)
    return np.stack([cache[k] for k in keys])


# ---------------------------------------------------------------------------
# Public entry point (matches the signature report.py already calls)
# ---------------------------------------------------------------------------

def semantic_backup_score(
    snippet_source: str, cid: str, backend: str = "lexical"
) -> Optional[dict]:
    """Compare `snippet_source` against cid's exemplars under `backend`.

    Returns None if cid has no exemplars registered (nothing to compare
    against) or if `backend == "stub"` is explicitly requested (kept only
    for backward compatibility with callers that haven't opted into a real
    backend yet). Otherwise returns:
        {"backend": ..., "max_similarity": float in [-1, 1],
         "best_match_exemplar_index": int}

    Never raises on a missing/empty exemplar list (returns None instead,
    since "no exemplars" is a normal, expected state for most competencies
    right now, not an error). DOES raise if the backend itself can't be
    constructed (e.g. codet5p with no network/weights) -- see
    CodeT5PEmbedder's docstring for why that's deliberate.
    """
    if backend == "stub":
        return None

    exemplars = EXEMPLAR_REGISTRY.get(cid, [])
    if not exemplars:
        return None

    query_vec = embed_cached(backend, [snippet_source])[0]
    exemplar_vecs = embed_cached(backend, exemplars)

    sims = exemplar_vecs @ query_vec  # rows are L2-normalized -> dot == cosine
    best_idx = int(np.argmax(sims))
    return {
        "backend": backend,
        "max_similarity": float(sims[best_idx]),
        "best_match_exemplar_index": best_idx,
    }







