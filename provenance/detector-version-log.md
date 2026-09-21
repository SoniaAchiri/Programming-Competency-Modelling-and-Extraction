# Detector version log — built from real artifacts, not reconstructed from the paper

This replaces the speculative version history in the earlier `VERSIONING.md` scaffold (which was
reconstructed purely from the paper's prose, before any real code/conversation history had been supplied, and
turns out to be wrong on several specifics — see "Corrections to the earlier scaffold" at the bottom).
Sonia does not have granular commit history; instead she is supplying the intermediate states she
actually saved, one at a time, each identified by whatever label/date she gave it. This doc is the
running, evidence-grounded log — updated as each new artifact arrives.

Rule for this log: every claim here is either (a) read directly from the supplied code (via `diff`
against the previous checkpoint, so "changed" claims are literal, not remembered), or (b) quoted/
paraphrased from the matching conversation-history document Sonia supplied for that checkpoint. Nothing is
inferred or guessed. Where evidence is silent on something, this log says so explicitly rather than
filling the gap.

---

## V1.0.0 — "Test real data_Q2_3_V1.0.0"

**Real date:** 2026-07-18 (per the conversation-history doc's own "18/07/2026 — step back and use what exists"
checkpoint marker — this is the exact point the supplied code snapshot corresponds to).

**Source artifacts:**
- `competency.py` (571 lines) — the framework: Evidence/Result, primitive detectors, CoverageRule
  types, StructuralConstraint types, Competency/CompetencyModel resolver.
- `test_real_data.py` (212 lines) — registers the working competencies and runs them against the
  Refactory dataset at `/home/claude/refactory/data/...`.
- Corroborating conversation history: `I want to define a structure of competencies.docx`, up to its
  "18/07/2026" marker. The conversation's own end-of-round summary matches the code line-for-line, confirming
  this is genuinely the state at that checkpoint, not a later or earlier snapshot mislabeled.

### What's actually in it

**8 primitive detectors** (`PRIMITIVE_DETECTORS` dict): `DECL`, `INPUT`, `PARAM`, `OUTPUT`, `TEST`,
`LOOP`, `ASSIGN`, `BUILTIN_REDUCE`.
- `ASSIGN` covers `Assign`, `AugAssign`, and collection mutation via `.append()`/`.add()` only —
  `.pop()`/`.remove()` are NOT yet captured (added at `ex2_3_4`, see below).
- `PARAM` was added specifically to fix a real bug: `GuardedInput` scored 0 on every function-graded
  submission (data arrives as parameters, never `input()`) until `source` was redefined to accept
  `("INPUT", "PARAM")` as alternatives.

**Coverage rules:** `ALL`, `ANY`, `K_OF_N`, `WEIGHTED`.

**Structural constraints:** `NESTED`, `SEQUENTIAL`, `SHARED_BINDING`, `SELF_REFERENTIAL`, `TUPLE_SWAP`,
`AND`, `OR`, `COOCCUR`.
- `NESTED` is **span-containment only** — **not** true AST ancestry.
- `SEQUENTIAL` uses **raw `max_line_gap`** — **not** statement-list position.
- `SHARED_BINDING` is a simple pairwise bindings-equality check over `(id, role)` pairs — no scope
  awareness, no `all_names` widening.
- Composite-evidence propagation **already guards against the zero-score/phantom-span leak**: a fixed
  slot only gets its child's evidence when `res.final_score > 0` (the "Swap span-corruption" fix — this
  is bug #3 in the canonical numbered bug table, see the "Methodology V24" section below).

**Registered competencies** (`test_real_data.py`): `Accumulation`, `Swap3Step`, `SwapTuple`, `Swap =
ANY(Swap3Step, SwapTuple)`, `GuardedInput`, `SelectionStep`, `FindExtremumBuiltin`, `FindExtremum =
ANY(SelectionStep-as-manual, FindExtremumBuiltin)`, `TopKPattern`, `ConditionalCount`, `BubbleSortPass`.

- **No `LinearSearch`** distinct from `GuardedInput`.
- **No `SortByKey` composite** — `BubbleSortPass` registered standalone.
- **No `DELEGATES` / `CALL`** — cross-function delegation "sketched but not finished or wired in."

### Real, confirmed fixes already incorporated by V1.0.0

1. **Swap's role collision (bug #1)** — `components` changed from a flat list to a `dict` of `slot_name
   -> type_id`, so `Swap` can require three distinct `ASSIGN` slots. Verified: correct swap 1.00, buggy
   swap 0.67.
2. **`GuardedInput` false-zero on function-graded code (bug #2)** — added `PARAM` primitive; `source`
   widened to `("INPUT", "PARAM")`. 3 Q1 submissions that scored 0.00 → all scored 1.00.
3. **`TUPLE_SWAP` + `SwapTuple` added** — recognizes `a, b = b, a`, composed via `Swap = ANY(Swap3Step,
   SwapTuple)`.
4. **Span-corruption fix (bug #3)** — a losing `OR` branch produced a placeholder `(0,0)` span that
   leaked into the parent's span whenever the *other* branch won, corrupting downstream `NESTED` checks.
   Fixed: a sub-competency only contributes evidence/span to its parent if it scored `> 0`. Per the
   canonical bug table (see below), the symptom that surfaced this was specifically `BubbleSortPass`
   scoring 0 on a textbook-match submission, traced to `Swap`'s own `Swap3Step`/`SwapTuple` `OR`.
5. **`BUILTIN_REDUCE` + `FindExtremum = ANY(manual, builtin)`** — 127/418 (30%) correct Top-K
   submissions use `max()`/`min()`; previously invisible, now credited. **This is the change that later
   opens the "TopKPattern missing-removal" blind spot (bug #12)** documented below under the
   `files_Report_*` checkpoint — see that section for the mechanism.
6. **`ConditionalCount` (Q2) redefined directly over primitives (bug #4)** (`decl`, `loop`, `test`,
   `increment`) instead of composing `Accumulation` inside `NESTED(test, Accumulation)` — `Accumulation`'s
   span includes its `DECL` line, which legitimately sits *outside* the `TEST`. `correct_2_003` → 1.00;
   `correct_2_001` (tuple-accumulate-then-`.count()`) correctly still 0 (different strategy, not a bug).
7. **`SelectionStep` reused as-is for Q3** — zero code changes, 1.0 on the 2 files spot-tested.
8. **`BubbleSortPass` added, validated on 4 real Q4 submissions** — correctly separates genuine bubble
   sort (swap nested inside the comparison) from selection-sort-with-swap-after.

### Explicitly documented open limitations at V1.0.0

1. No function-scoping — `SHARED_BINDING` could theoretically coincide across unrelated functions.
2. `NESTED` on a composite's full span only works when the whole child is meant to be contained — the
   *general* problem is open; only the `ConditionalCount` instance was worked around.
3. Cross-function delegation "sketched but not finished or wired in."

### Validation scope at V1.0.0

Every result comes from **spot-testing 2-4 real files per question**, not full-corpus batch validation.
No percentage coverage figures from the paper are established yet.

**Note, added retroactively from a later conversation passage (pre-V1.0.0 in the transcript, describing the raw
dataset before `BUILTIN_REDUCE` existed):** the collaborator already flagged `wrong_5_058.py` by name at
this stage as "has DECL + LOOP + ASSIGN(append) but is missing the 'remove max from source list' step,"
and a subsequent early test run confirmed `TopKPattern` correctly scored **0.0** on it — but only because
no `TEST` primitive existed in that file at all, and at that point in the transcript `BUILTIN_REDUCE`/
`FindExtremumBuiltin` hadn't been added yet either. This context matters for dating the later
"missing-removal bug" — see the `files_Report_*` section below.

---

## ex1_taxo — "files_ex1_taxo"

**Real date:** 2026-07-19 (conversation marker; this and `ex2_3_4` are part of the same dated round, applying
the shared model to a *different* course's exercises, Ex1–Ex4 — the material behind the paper's §5.2).

**Source artifacts:** `competency.py` (679 lines, up from 571), `test_real_data.py` (byte-identical to
V1.0.0), `pw01_competencies.py` (new, 143 lines).

**What changed vs. V1.0.0** (confirmed by direct `diff`):

1. **`FUNC_DEF` primitive added** — `name`, `n_params`, `has_return` bindings.
2. **`LOOP` evidence gained a `kind` binding** (`"for"`/`"while"`) — additive.
3. **Every `StructuralConstraint.score()` gained a `ctx=None` parameter** — declared, not yet used.
4. **`REFERENCES` and `CONTAINS_TEXT` constraints added.**
5. **`DELEGATES` constraint class added — confirmed NOT wired into the resolver at this checkpoint.**
   The class is fully implemented (memoization, cycle protection), but `resolve()` still calls
   `.score(evmap)` with no `ctx`, and there is no `CALL` primitive detector and no `function_index`
   anywhere in the file — so `DELEGATES` is dead code here (`ctx is None` → always 0.0). Fixed two
   checkpoints later, at `V1.2.0` below.

**New competencies** (`pw01_competencies.py`): `IsPrime`, `CountedSearch` (Ex1.3/1.4 — deliberately
loose, "a first-pass approximation"), `CollectInput` (Ex1.5), `Average` (Ex1.2, reuses `Accumulation` +
`REFERENCES` + `CONTAINS_TEXT` — 1.00 on a correct reference, 0.00 forgetting `/n`). Ex1.6 needed zero
new code, reusing `SelectionStep`/`FindExtremum` unmodified. All tested against synthetic
reference/buggy pairs — no real student data for this PW yet.

---

## ex2_3_4 — "files_ex2_3_4"

**Real date:** same 2026-07-19 round, immediately after `ex1_taxo`.

**Source artifacts:** `competency.py` (679 lines — only a 2-line change from `ex1_taxo`),
`test_real_data.py` / `pw01_competencies.py` (byte-identical to `ex1_taxo`), `ex2_3_4_competencies.py`
(new, 214 lines).

**What changed vs. `ex1_taxo`:**

1. **`ASSIGN` extended to `.pop()`/`.remove()` (bug #7)**, and `kind` now stores the real matched
   attribute (`node.func.attr`) instead of a hardcoded `"append"`. Motivated by Ex3.3's stack exercise —
   per the canonical bug table (see "Methodology V24" section below), this same fix is what made the
   `TopKPattern` missing-removal check (bug #12, added later) and the balanced-parentheses stack exercise
   possible at all.
2. No other framework changes — `DELEGATES` still unwired; no `CALL` primitive; no
   `EXHAUSTIVE_CHAIN`/`MultiWayBranch` yet.

**New competencies** (`ex2_3_4_competencies.py`): `GameLoop` (Ex2), `GreedyReduction` +
`ArithmeticReduction` + `GreedyChange = ANY(...)` (Ex3.1), `CounterBalance` + `StackBalance` +
`BalancedCheck = ANY(...)` (Ex3.3 — already past the two symmetric "kind"-typing bugs the canonical bug
table numbers #5 (`StackBalance` scored 1.0 on a pure-counter solution — its push/pop slots were typed
only as `ASSIGN` with no check on *which* `ASSIGN`) and #6 (`CounterBalance` scored 1.0 on a stack-based
solution, the symmetric miss) — fixed with `CONTAINS_TEXT`/operator checks; this snapshot is post-fix for
both), `GridIteration` (Ex4, nested-loop primitive only — no win-checking, no delegation, consistent with
`DELEGATES` still unwired). All tested against synthetic pairs.

---

## V1.2.0 — "V1.2.0.rar"

**Real date:** 2026-07-19 (later in the same session as `ex2_3_4` — the multi-way-branching and
cross-function-delegation work) through **2026-07-21** (the per-file-vs-per-function scoping fix,
confirmed by the conversation's own date marker directly preceding it). This single zip is the merged endpoint
of *both* checkpoints flagged as "pending" in earlier log entries — both are now confirmed with code.

**Source artifacts:** `competency.py` (884 lines, up from 679), `ex2_3_4_competencies.py` (267 lines, up
from 214), `pw01_competencies.py` (180 lines, up from 143), `test_real_data.py` (byte-identical to every
prior checkpoint — confirmed via diff, zero changes since V1.0.0).

### 1. Multi-way branching (`EXHAUSTIVE_CHAIN`) — resolved

**What changed** (confirmed by diff): a new `_walk_elif_chain(if_node)` helper walks an `ast.If`'s
`elif` links directly (Python represents `elif` as a single-element `orelse` containing another `If`),
returning `(branch_count, has_final_else, variable_sets)` — one frozenset of referenced variable names
per branch. A new `EXHAUSTIVE_CHAIN` constraint uses this: checks `total_outcomes = count + (1 if
has_else else 0)` against `min_branches`, optionally requires a terminal `else`, and optionally requires
every branch to share at least one common variable (via set intersection over `variable_sets`, not an
identical operand string — this is what lets a compound `and`/`or` branch still count as "the same
decision" as a plain `Compare`).

**Two real bugs fixed along the way, per the conversation, and the code confirms the fixed state (not the buggy
intermediate) — both now independently numbered by the canonical bug table (see "Methodology V24"
section below):**
- **Bug #8** — the underlying DAG-composition approach (hand-unrolled `Chain2`/`Chain3`/...) silently
  failed past depth 1, because a composed sub-competency's `Evidence.node` is `None` by design, so a
  constraint checking "is this literally the next elif" has nothing left to compare once one side is a
  composite. This is *why* `EXHAUSTIVE_CHAIN` walks the raw AST directly instead of composing DAG slots
  — not a bug in `EXHAUSTIVE_CHAIN` itself, but the reason it exists in this form.
- **Bug #9** — off-by-one in outcome counting: originally counted `If` nodes traversed (`if` + each
  `elif`), so an `if/elif/else` (2 `If` nodes, 3 real outcomes) undercounted itself as 2, never reaching
  `min_branches=3`. Fixed: count total distinguishable outcomes (each `If`-test, plus the terminal
  `else` if present). The canonical bug table adds one detail not previously logged: this bug surfaced
  specifically as `MultiWayBranch` still scoring 0 on a real if/elif/else *after* the earlier too-narrow
  "same operand" check had already been fixed to compare variable sets instead — i.e. bug #9 was found
  only after a *different* fix (the operand-to-variable-set change) was believed to have already resolved
  the case.

**New competency registered** (`ex2_3_4_competencies.py`, confirmed by diff): `MultiWayBranch =
EXHAUSTIVE_CHAIN("test", min_branches=3, require_else=True, require_same_operand=True)`. Tested against
exactly 5 cases (confirmed present in the file's `__main__` block, matching the conversation's own table):
a positive-control grade chain (3 branches, same operand, has else → expected 1.00), the real Ex2 RPS
reference (3-way, compound-boolean branch, has else → expected 1.00 after the variable-set fix), a
2-way if/else (below `min_branches` → 0.00), a 3-way chain with a different operand per branch (not
truly one decision → 0.00), and a 3-way chain with no final `else` (not exhaustive → 0.00).

**Two more constraint classes present in `competency.py` but not exercised by any registered
competency in the supplied files:** `DISTINCT_BINDINGS` (checks no two slots in a list share the same
combined value across a set of roles — e.g. two `TEST` branches shouldn't have an identical
`(operand, op, comparator)` tuple; comparing the full tuple rather than operand alone avoids misfiring
on the common `if x==1: elif x==2:` shape) and `HAS_ELSE` (checks a `TEST` evidence's `If` node ends the
chain with a genuine terminal `else`, not another `elif`). Neither is named in the conversation text read so
far, and neither is referenced by `MultiWayBranch` or any other registered competency — flagging as
present-but-unused rather than guessing their intended purpose. **Confirmed still unused, and still
undocumented as a named constraint, in the "Methodology V24" doc's own structural-constraint table (11
entries, neither `DISTINCT_BINDINGS` nor `HAS_ELSE` listed) — see below.**

### 2. Cross-function delegation — now actually wired in (was dead code through `ex2_3_4`)

**What changed** (confirmed by diff, in `resolve()`): a `function_index` (name → `FunctionDef`) is now
built from `module_tree` (defaults to `tree` itself when not given). `CALL` evidence is detected inline
inside `resolve()` — **not** via the `PRIMITIVE_DETECTORS` registry pattern used by every other
primitive — by walking for `ast.Call` nodes whose callee name is in `function_index`. A `ctx` dict
(`model`, `function_index`, `module_tree`, `delegate_cache`, `in_progress`) is now threaded into every
`comp.structural.score(evmap, ctx)` call (both call sites in the combinatorial search).

**New competency registered** (`pw01_competencies.py`, confirmed by diff): `DelegatesUniqueness =
{test, call}`, `structural=AND([NESTED("test","call"), DELEGATES("call", "ConditionalCount")])` — for
Refactory **Question 2**'s `contains_unique_day` delegating to `unique_day`. (Registered in
`pw01_competencies.py`, the Ex1-4 course-exercises file, even though it targets a Refactory Q2 case —
the conversation's own words: "it belongs there conceptually.")

**Validated three ways, per the conversation, matching the code's own `__main__` test block:**
- Real positive case: `contains_unique_day` → `unique_day` → `DelegatesUniqueness = 1.00`.
- Negative case: same caller, callee's counter never incremented (`ConditionalCount = 0`) →
  `DelegatesUniqueness = 0.00` — correctly propagates the callee's failure, not just "a call exists."
- Recursion guard: a self-calling function resolves without hanging (`in_progress` set catches it,
  returns 0.0 for the in-progress resolution).

### 3. Per-file vs. per-function scoping — now fixed (was the #1 open limitation since V1.0.0)

**Real bug (bug #10), confirmed before the fix, per the conversation:** `GuardedInput` scored `1.0` on a
`search()` function with no parameter or input of its own, purely because an unrelated sibling function
`helper(x)`'s parameter `x` coincidentally shared a name with `search`'s loop variable —
`SHARED_BINDING` has no location awareness of its own; only `NESTED` was ever incidentally protecting
against this, and only for competencies that happened to tie every slot together via containment.

**Fix, confirmed by diff:** `Evidence` gained a `scope` field (its enclosing `FunctionDef`, or `None`
for module-level). A new `_ParentIndex.enclosing_function()` finds it. Every piece of primitive evidence
is tagged with `.scope` after detection. The resolver's combinatorial search now rejects any combination
whose evidence spans more than one non-`None` scope (`fixed_scopes | combo_scopes` check) — the same
style of guard as the pre-existing same-AST-node-reuse check. Composite evidence propagates its child's
scope onward when reused as a fixed sub-competency (so scoping survives composition).

**One real bug in the fix itself (bug #11), caught before calling it done (per the conversation, directly
confirmed by the code's comment):** the first version of the guard didn't work — `GuardedInput` still
returned `1.0`. Root cause: `PARAM` evidence stores the whole `FunctionDef` node itself as `.node`
(there's no separate per-argument AST node), so `enclosing_function(ev.node)` walked *past* the function
to its own parent — every parameter's scope silently came out `None` (module-level), exempting every
`PARAM` from the guard regardless of which function it belonged to. Fixed by special-casing `PARAM`:
`ev.scope = ev.node` directly, rather than calling `enclosing_function`. The code's own comment states
this exact rationale verbatim.

**A `resolve_by_scope()` public API is also present** — partitions a module into independent
per-function resolutions (`{scope_name: {competency_id: Result}}`, plus a synthetic `"<module>"` scope
for top-level code) rather than relying solely on the in-resolver guard. **Noteworthy honesty in the
conversation itself:** the assistant explicitly said it did not have "a clean account in my own edit history of
writing that specific piece" but confirmed the method works correctly by testing it directly rather than
assuming — recorded here because it's a genuine provenance gap in the *narrative* (not the code, which
is fully present and tested either way).

**Verified three ways, per the conversation:** the cross-function false positive → now `0.0`; a legitimate
same-function `GuardedInput` case → still `1.0` (guard isn't over-restrictive); full regression across
`test_real_data.py`, `pw01_competencies.py`, `ex2_3_4_competencies.py` — every previously-established
score unchanged, including `DelegatesUniqueness` (still `1.00`, confirming scoping and delegation
coexist) and all 5 `MultiWayBranch` cases.

### Updated limitations list at V1.2.0 (down from the original five, per the conversation)

- ~~Cross-function delegation~~ — done.
- ~~Multi-way branching~~ — done.
- ~~Per-file vs. per-function scoping~~ — done.
- Single-language (Python/`ast`) scope — unchanged by design; the Evidence/CoverageRule/
  StructuralConstraint abstractions are language-agnostic in principle but untested against anything
  else.
- First-pass approximations (`CountedSearch`, `CollectInput`) — still untested against real student
  data, since the PW01 course assignment has none yet.

### The 2026-07-21 paper-regeneration round — first genuinely grounded appearance of a Table-4-style number

The conversation's own "21/07/2026" marker precedes a request to regenerate the paper without a Related Work
section. Per the conversation (narrative only at the time this section was first written — the underlying code
has since been supplied, see the `files_Report_*` checkpoint below):

- A new **§5 Case Study 3**: "the full 526-submission batch run, the unscoped-vs-scoped correction
  (83.0% → 78.2%), and the reconfirmed-at-scale finding that 75% of 'wrong'-labeled submissions still
  structurally implement the pattern correctly." 526 matches Table 3's Q5 total (418 correct + 108
  wrong).
- A bug table extended to **13 entries**, including two named for the first time here: a "TopKPattern
  missing-removal bug" (bug #12) and a "magus_sort cross-function-credit bug" (bug #13) — both said to
  be found via the reporting/batch tools. **The full canonical text of all 13 bugs is now available —
  see the "Methodology V24" section below, which supplies `Competency_Extraction_Methodology_V24.docx`'s
  own bug table verbatim.**
- §2.10 (per-submission reporting) and §2.11 (the CodeBERT semantic backup layer, including its
  confirmed lack of discriminative power) were added to the paper in this same round.

---

## Reporting/batch tooling — "files_Report_batch" + "files_Report_per_submmision"

Two zips supplied together, evidently two adjacent stages of the same tool's development (confirmed by
direct diff of the shared `report.py`, see below). This is the first supplied code for the tooling that
the 2026-07-21 paper-regeneration narrative (previous section) described but did not include.

**Source artifacts:**
- `files_Report_per_submmision.zip` → `report.py` (131 lines), `report_demo.py` (26 lines, new),
  `test_real_data.py` (212 lines — same line count as every prior checkpoint, but **not** byte-identical:
  see the `TopKPattern` change below).
- `files_Report_batch.zip` → `report.py` (156 lines — a superset of the per-submission version, see
  diff below), `batch_report.py` (75 lines, new), `topk_report.csv` (526 data rows — a real, complete
  output, not a placeholder).

No `competency.py` was included in either zip; both `report.py` files import `PRIMITIVE_DETECTORS`,
`_ParentIndex`, `CompetencyModel` from it, so the framework itself is assumed unchanged from `V1.2.0`.

### The `TopKPattern` fix — the "missing-removal bug" (bug #12), now with real code

**Confirmed by diff against `V1.2.0`'s `test_real_data.py`:** `TopKPattern`'s definition changed from

```
components={"loop": "LOOP", "select": "FindExtremum"}
coverage=ALL(["loop", "select"])
structural=NESTED("loop", "select")
```

to

```
components={"loop": "LOOP", "select": "FindExtremum", "remove": "ASSIGN"}
coverage=ALL(["loop", "select", "remove"])
structural=AND([
    NESTED("loop", "select"),
    NESTED("loop", "remove"),
    CONTAINS_TEXT("remove", "kind", ("remove", "pop")),
])
```

This is present, unchanged, in both zips' `test_real_data.py`/import chain — no code comment explains
the rationale inline, but `report_demo.py` (in `files_Report_per_submmision`) directly demonstrates it
by running the report against `wrong_5_058.py`, titled in the script itself as **"wrong_5_058.py
(Top-K, missing removal)"** — a direct, code-level naming match to the "TopKPattern missing-removal bug"
the conversation named on 2026-07-21, and now also to bug #12's canonical description in `Competency_Extraction_
Methodology_V24.docx`'s own bug table: "TopKPattern scored 1.0 on a submission known to be wrong — it
appends the same maximum k times and never removes it," root cause "TopKPattern composed FindExtremum
(correctly, for its OTHER uses) without separately checking that the found value is then removed;
FindExtremum alone doesn't and shouldn't imply removal," fix "Added an explicit remove slot to
TopKPattern... fixing this at TopKPattern, not at the reusable FindExtremum, kept Ex1.6's unrelated use
of FindExtremum unaffected." This matches the diff exactly, slot-for-slot.

**Mechanism, worked out from the diff (not stated explicitly in either supplied file, though now fully
corroborated by the canonical bug-table text above):** once `BUILTIN_REDUCE`/`FindExtremumBuiltin` were
added back at `V1.0.0` (so that `max()`/`min()` calls count toward `FindExtremum` without a manual
comparison loop), a submission that calls `max(lst)` inside a loop but never removes the found element
from `lst` — exactly `wrong_5_058.py`'s pattern, appending the same max `k` times — would satisfy
`TopKPattern`'s old definition (`loop` + `select`, nothing else) with a final score of `1.00`, because
the builtin branch of `FindExtremum` needs no removal step at all. The fix adds a third required slot,
`remove`, and a `CONTAINS_TEXT` check that it's specifically a `.remove()`/`.pop()` call — closing
exactly that gap. **Note on dating:** an earlier conversation passage (quoted under `V1.0.0` above) already used
`wrong_5_058.py` as an example and reported `TopKPattern` correctly scoring `0.0` on it — but at that
point in the transcript neither `BUILTIN_REDUCE` nor `FindExtremumBuiltin` existed yet, so the file
scored 0 for an unrelated reason (no `TEST` at all). The evidence is consistent with the missing-removal
blind spot being an unintended side effect of the later builtin-support fix, though no conversation passage
explicitly states this causal chain — flagging it as a well-supported inference from the diffs and dates,
not a directly quoted fact. **Confirmed independently, one checkpoint later** by the full
primitive-inventory output in `The_output_Results_26.docx` — see the "Q2 fix + third strategy" section
below. **Superseded at the `files_Fix_Q4` checkpoint** (see below), where `TopKPattern` is refactored
again to accommodate the "level" convention.

### The reporting/batch tool itself

`report.py`'s `generate_report()` builds a two-layer report per submission: every primitive detected
(with a human-readable one-line description via `_describe()`), plus, for a chosen list of target
competency ids, `final_score`/`coverage_score`/`structural_score` and which named slots were present vs.
missing (made possible because composite `Evidence` keeps a `children` map). `format_report_text()`
renders it. The module's own docstring states a known limitation plainly: when coverage is 1.0 but
structural score is `< 1.0`, the report can only surface the *aggregate* structural score, not which
specific sub-constraint inside an `AND`/`OR` failed — `StructuralConstraint`s don't yet expose a
per-part breakdown.

**Confirmed by diff, the batch zip's `report.py` adds exactly one capability over the per-submission
zip's `report.py`:** an optional `function_name` parameter. When given, `generate_report()` finds that
named `FunctionDef` in the module, and scopes **both** the primitive inventory and `model.resolve()`
(via `module_tree=tree` for delegation support) to just that function's body — not the whole file. The
new code's own docstring is explicit about *why* this is a distinct mechanism from `V1.2.0`'s
`Evidence.scope` guard: the guard already prevents evidence from two *different* functions from
combining within one competency, but it does **nothing** to stop an *unrelated* helper function
elsewhere in the same file from independently satisfying a competency on its own — which then gets
credited to the file as a whole even though the function actually being graded (the docstring's own
example: `top_k`) might not implement it. This is, concretely, the "unscoped-vs-scoped correction"
named in the paper's Case Study 3, and directly mirrors bug #13's canonical description (see
"Methodology V24" section below): "TopKPattern credited 83.0% of correct submissions at whole-file
scope; a sampled case showed the actual top_k function had no loop, test, or removal logic of its own"
— root cause "Whole-file resolution let an unrelated helper function (`magus_sort`) elsewhere in the
same file independently satisfy the competency" — fix "Added function-scoped reporting (§2.10)." This is
the first confirmation that bug #13 (`magus_sort`) is specifically what *motivated* building the
`function_name` parameter, not a coincidentally-related finding.

`batch_report.py` runs `generate_report()` across every `.py` file in one or more labeled folders,
writing one row per submission to a CSV (`{cid}_final`, `{cid}_missing` per target competency); a file
that fails to parse is recorded as an error row rather than crashing the whole batch.

### `topk_report.csv` — real, computed Case Study 3 data, not a placeholder

526 data rows: 418 labeled `correct`, 108 labeled `wrong` — an exact match to Table 3's Q5 corpus split,
and to the "526-submission batch run" named in the 21/07 conversation. Zero parse errors. Computed directly from
the file (not from the conversation) for `TopKPattern_final`:

| | correct (n=418) | wrong (n=108) |
|---|---|---|
| `TopKPattern_final == 1.0` | 327 → **78.2%** | 81 → **75.0%** |

Both figures are **exact matches** to numbers the conversation quoted from the regenerated paper: the "78.2%"
half of the "83.0% → 78.2%" scoping correction, and the "75% of 'wrong'-labeled submissions still
structurally implement the pattern correctly" finding — word for word. This is the strongest evidence
yet connecting a specific reported number to a specific, inspectable artifact rather than to prose alone.

**What this CSV does not resolve, stated explicitly:**
- **No CSV or code for the *unscoped* run exists in the supplied artifacts**, so the "83.0%" half of the
  correction is still not directly reproducible from evidence — only the post-fix ("78.2%") side is.
  (The batch zip's `report.py` — the one with `function_name` scoping — is almost certainly what
  produced this exact CSV, given the exact 78.2%/75.0% match to the *scoped* paper figures, but no driver
  script recording the actual `process_folders(...)` call, including which `function_name` value was
  passed, was included — only the two library modules and the CSV output. `top_k` is the function name
  used as an example in the docstring, not confirmed as the literal argument used for this run.)
- **No code for the `magus_sort` cross-function-credit bug (bug #13)** — still not present in any
  supplied artifact; `Competency_Extraction_Methodology_V24.docx`'s bug table (see below) gives its
  canonical symptom/root-cause/fix description, but no source file defining `magus_sort` itself has been
  supplied.
- **`SelectionStep_final` and `FindExtremum_final` columns are also present in the CSV** (62.2%/62.0%
  and 89.7%/95.4% correct/wrong respectively) but are not directly named against any paper figure read
  so far — left unremarked rather than force-matched to a number.

---

## Q2 fix + third strategy — "files_fixQ2" + "files_Q2_competencies_3rd strategie" + "The output_Results_26.docx"

Two code zips (`fixQ2`, then `3rd_strategie` — order confirmed by monotonic file growth, see below) plus
a conversation-history document (`The_output_Results_26.docx`, pandoc/python-docx confirm it is genuinely a
short, truncated export — 149 paragraphs + 1 table, ending mid-paragraph at "Purpose & context" with no
further content in the file's XML — logged as-is, not padded).

**Real date:** 2026-07-28, 18:42 (the docx's own trailing date/time marker, after all the content
described below).

**Source artifacts:**
- `files_fixQ2.zip` → `competency.py` (921 lines, up from `V1.2.0`'s 884), `q2_competencies.py` (new,
  76 lines).
- `files_Q2_competencies_3rd strategie.zip` → `competency.py` (956 lines), `q2_competencies.py`
  (131 lines). Both files strictly larger than `fixQ2`'s, and `fixQ2`'s two-strategy `q2_competencies.py`
  content is a byte-for-byte subset of this one's first 40 lines — confirms `fixQ2` → `3rd_strategie` is
  the real order, consistent with the names given.

Neither zip includes `test_real_data.py` or `pw01_competencies.py`; `q2_competencies.py` imports `model`
from `pw01_competencies`, so this checkpoint only shows what changed in `competency.py` and the new file.

### 1. `fixQ2`: two real Q2 strategies wired together, plus a documented-but-unenforced "level" convention

**Confirmed by diff against `V1.2.0`'s `competency.py`:**
- `is_simple_init` (used by the `DECL` detector) widened to also accept `ast.Tuple` — needed so
  `all_days = ()` (a tuple accumulator, not a list) is recognized as a `DECL`.
- A 37-line comment block appended to the end of the file, titled "DESIGN PRINCIPLE (documented
  convention, NOT enforced by the code below)". It defines competency **level**: 0 for a primitive,
  `1 + max(level(child))` for a composite, and states the convention that a level-*n* competency should
  compose only level-(*n*-1) children, not a mix. It names the then-current violators by id —
  `TopKPattern`, `BubbleSortPass`, `CountedSearch`, `Average` — and explains why each is a genuine
  exception (a removal step, a swap, a search loop, an output division each need to sit *alongside* a
  higher-level sibling, not nested under it), and separately flags a real technical blocker to ever
  enforcing this strictly: a composite `Evidence`'s `bindings` dict is always `{}`, so `SHARED_BINDING`/
  `SELF_REFERENTIAL`/`TUPLE_SWAP` (which read `.bindings` directly, unlike `CONTAINS_TEXT`/`REFERENCES`,
  which already resolve dotted paths via `_resolve_evidence`) would silently break if a primitive were
  ever hidden behind a lifting wrapper. **This is a comment only — `level()`, `check_layering()`, and
  `allow_mixed_levels` do not exist as code in this file.**

  **Dating correction, now resolved with strong independent evidence (see the "Methodology V24" section
  below for the full analysis):** this comment's *content* — the `level()` definition, the exact 4-name
  violator list, the "8-10 new definitions... zero semantic content" cost framing, and the composite-
  `bindings={}` technical blocker — was demonstrably designed and written up in prose **a full week
  earlier, around 2026-07-21**, per `Levels_of_competencies_21_07.docx`'s own leading date marker and
  per `Competency_Extraction_Methodology_V24.docx`'s §2.12 (which documents this exact content, including
  the same 4 violators and the same technical blocker, while explicitly still describing it as
  "documented as a convention, not enforced in code"). What changed at *this* (`fixQ2`, 28/07) checkpoint
  is that the already-designed comment text was actually pasted into the saved `competency.py` file for
  the first time — a code-checkpoint event, not the concept's origin. The two dates are not in conflict
  once "when the idea was designed and written up" is separated from "when it was committed into this
  particular saved snapshot."

**A genuine intermediate save-point within this same round, now directly evidenced:** a standalone
`competency.py` (921 lines) was supplied on its own, with no accompanying zip or conversation doc. Diffed
directly against `V1.2.0`'s `competency.py`, it is **exactly** `V1.2.0` plus the 37-line DESIGN PRINCIPLE
comment appended, and *nothing else* — zero other lines changed. Diffed against `fixQ2`'s own saved
`competency.py` (the 921-line file described above), the two are identical except for **one single
line**: this standalone file's `is_simple_init` check (used by the `DECL` detector) is still
`isinstance(node.value, (ast.Constant, ast.List, ast.Dict, ast.Set))` — **missing** the `ast.Tuple`
alternative that `fixQ2`'s saved version has. In other words, this file captures the exact moment between
two edits: the level-concept comment had just been pasted in, but the `DECL`-widening fix that lets
`all_days = ()` (a tuple accumulator) register as a `DECL` had not yet been made.

**Directly executed, not just diffed, to confirm the consequence:** paired with `V1.2.0`'s
`pw01_competencies.py`/`test_real_data.py` and `fixQ2`'s own `q2_competencies.py` (the file that defines
`AccumulateThenCount` and runs the tuple-strategy test case), this standalone `competency.py` reproduces
a real, reasoned-out failure — not the `1.00` the finished `fixQ2` checkpoint reports:

```
def unique_day(day, possible_birthdays):
    all_days = ()
    for i in possible_birthdays:
        all_days += (i[1],)
    return all_days.count(day) == 1

  ConditionalCount     final=0.00  (coverage=0.50 structural=0.00)
  AccumulateThenCount  final=0.00  (coverage=0.50 structural=0.00)   <- fixQ2's finished file: 1.00
  UniqueCheck          final=0.00  (coverage=0.00 structural=1.00)
```

Without the `ast.Tuple` case, `all_days = ()` never registers as `DECL`, so `Accumulation` itself scores
`coverage=0.50` (only `LOOP`+`ASSIGN` present, `DECL` missing) — and that failure cascades straight
through `AccumulateThenCount` to `UniqueCheck`. This is direct, executed proof of the exact mechanism the
`is_simple_init` fix closes, not an inference from the diff alone: the tuple-strategy test case in
`q2_competencies.py`'s own `__main__` block is almost certainly what surfaced this specific gap and
motivated the one-line fix, within the same working session. No date marker accompanies this standalone
file, so it can only be bounded, not pinned: strictly after `V1.2.0` (2026-07-21) and strictly before the
finished `fixQ2` checkpoint's own trailing marker (2026-07-28, 18:42) — consistent with, though not proof
of, this being the literal moment the comment landed in a saved file, one step before the tuple-DECL fix
that the rest of that same session's work (`AccumulateThenCount`, `UniqueCheck`) actually depended on.

**New file `q2_competencies.py` (76 lines) registers:**
- `OutputStep` — a trivial level-1 lift of `OUTPUT` (`components={"out": "OUTPUT"}`), explicitly to keep
  the next competency's siblings same-level.
- `AccumulateThenCount` — the real second Q2 strategy found in the data (`correct_2_001.py` and
  siblings): accumulate matching values into a collection, then check `.count()` on it, instead of an
  explicit counter. `components={"acc": "Accumulation", "check": "OutputStep"}`,
  `structural=AND([REFERENCES("acc.decl", "target", "check.out", "source"), CONTAINS_TEXT("check.out",
  "source", (".count(",))])` — the `REFERENCES` check specifically ties the accumulated collection to
  the one being counted, not just "some accumulation and some `.count()` exist somewhere."
- `ConditionalCountStep` — trivial level-2 lift of the existing `ConditionalCount`, so both `UniqueCheck`
  branches sit at the same level.
- `UniqueCheck = ANY(ConditionalCountStep, AccumulateThenCount)` — two strategies only, at this
  checkpoint.

The file's own `__main__` block runs exactly the two synthetic cases the conversation quotes verbatim
(tuple+`.count()` strategy scoring `AccumulateThenCount=1.00`/`ConditionalCount=0.00`; counter strategy
scoring the reverse; `UniqueCheck=1.00` on both) — output matches the docx line-for-line.

### 2. `3rd_strategie`: the functional map()/filter() branch, plus two new but unused primitives

**Confirmed by diff against `fixQ2`'s `competency.py`:** two new detector functions,
`detect_functional_collect` (matches `map(...)`/`filter(...)` calls, registered as primitive type
`FUNCTIONAL_COLLECT`) and `detect_count_check` (matches `.count(...)` or `len(...)` calls, registered as
`COUNT_CHECK`), both added to `PRIMITIVE_DETECTORS`. **Confirmed by grep: neither `FUNCTIONAL_COLLECT`
nor `COUNT_CHECK` is referenced by any competency registered in the supplied `q2_competencies.py`** — the
actual functional-strategy competencies below use `CONTAINS_TEXT` directly on the *existing*
`OUTPUT`/`ASSIGN`/`TEST` primitives instead, and the new file's own comment states why explicitly:
"map()/filter() are ordinary Call nodes already visible inside ASSIGN.source / OUTPUT.source, so no new
primitive detector is needed." So these two detectors are present-but-unused in what was supplied — the
same pattern as `DISTINCT_BINDINGS`/`HAS_ELSE` at `V1.2.0`, flagged rather than assumed to matter.

**`q2_competencies.py` grows to 131 lines, adding** (confirmed by diff): three sub-shape competencies for
the real third strategy the conversation describes finding in 32 of the remaining 41 previously-unmatched Q2
files — `InlineFunctionalCheck` (shape a: `return tuple(map(...)).count(day) == 1`, one expression, via
`CONTAINS_TEXT` on `OUTPUT.source`), `GuardedFunctionalCheck` (shape b: build the collection then check
it in a separate statement, via `CONTAINS_TEXT` on `ASSIGN.source` + `TEST.operand` tied together with
`REFERENCES`), and `InlineTestFunctionalCheck` (shape c: the pipeline embedded directly inside the `if`
condition, via `CONTAINS_TEXT` on `TEST.operand`) — composed as `FunctionalUniqueCheck = ANY(inline,
guarded, inline_test)`. `UniqueCheck` is redefined to `ANY(ConditionalCountStep, AccumulateThenCount,
FunctionalUniqueCheck)` — now three same-level (level 2) siblings.

### 3. The conversation's own reported result — full-corpus Q2 validation, not a spot-check

Per the docx (quoted, with its own table reproduced exactly): **"UniqueCheck now covers three real
strategies, validated against all 291 real Q2 submissions with proper function scoping"** —

| Strategy | Coverage |
|---|---|
| Explicit counter (`ConditionalCount`) | 85.2% |
| Tuple-accumulate-then-`.count()` (`AccumulateThenCount`) | 0.7% |
| Functional map()/filter() pipeline (`FunctionalUniqueCheck`, 3 sub-shapes) | 4.5% |
| **`UniqueCheck` (any of the three)** | **90.4%, up from 85.9% before this** |

291 matches the Refactory Q2 corpus total logged earlier in this doc (291 correct, cross-confirmed again
by `Competency_Extraction_Methodology_V24.docx`'s Table 2 — see below). This is the **first full-corpus
(not spot-check) batch-validation figure with both a real percentage and function scoping** confirmed
for any question besides Q5 — and 90.4% is the exact figure the old (fabricated) `VERSIONING.md` had
guessed for Q2, now genuinely confirmed rather than coincidental. **No batch-runner code or CSV for this
specific 291-submission Q2 run was included in these zips** (unlike Q5's `topk_report.csv`) — the
90.4%/85.2%/0.7%/4.5% figures are conversation-reported only at this checkpoint.

The docx also reproduces the same three `report_demo.py` cases already evidenced under the
`files_Report_*` checkpoint (`correct_5_050.py`, `wrong_5_058.py`, the `moyenne()` division bug) with
full primitive-inventory output this time — this independently corroborates that `report.py`/
`report_demo.py` runs as described, and specifically confirms the `TopKPattern` fix mechanism inferred
earlier: on `wrong_5_058.py`, `TopKPattern` shows `present: loop, select, remove` but `final=0.00`, with
the note "all slots had SOME matching candidate, but the required arrangement (or specific kind) was not
satisfied" — i.e., an `ASSIGN` was found for the `remove` slot, but it was `.append()`, not `.remove()`/
`.pop()`, exactly the `CONTAINS_TEXT("remove", "kind", ("remove", "pop"))` check working as designed.

### 4. The "level" concept — code-confirmed and directly executed, resolving what was previously conversation-only

Sonia's own framing that round ("I introduce a level concept") matched the docx's fuller narrative, which
went beyond the unenforced comment in `fixQ2`'s `competency.py`:

- "Let's implement this properly — a level() method plus an actual enforcement mechanism at registration
  time, not just a passive check." Per the conversation, this was done "in pw01_competencies.py": an
  `allow_mixed_levels` flag, applied to the same 4 violators the `fixQ2` comment had already named
  (`TopKPattern`, `BubbleSortPass`, `CountedSearch`, `Average`), each with an inline comment.
- `Average` was given "a clean, validated, level-2-compliant replacement" — `AverageStrict`, in a new
  file `level2_examples.py`, built via an `OutputStep`-style lifting wrapper, "produces identical
  scores." `CountedSearch`'s siblings were lifted behind trivial `LoopStep`/`OutputStep` wrappers to sit
  at level 1. **`level2_examples.py` itself has now been supplied directly (standalone upload, not in a
  zip) and re-run against a real `V1.2.0` `competency.py` + `pw01_competencies.py` pairing (the earliest
  checkpoint whose `REFERENCES`/`CONTAINS_TEXT` dotted-path resolution and registered `GuardedInput`/
  `Accumulation`/`Average` are sufficient for it to run at all) — see the dedicated section immediately
  below this one for the full diff/execution writeup. Both `AverageStrict` and `ValidatedAccumulation`
  are now fully code-confirmed, not just conversation-quoted.**
- "Final audit: library-wide violations down to 2 — `TopKPattern` and `BubbleSortPass`, both genuinely
  irreducible... correctly marked `allow_mixed_levels=True` and visible via `check_layering()`." **This
  specific claim — that `TopKPattern` was irreducible — turned out not to hold; see the `files_Fix_Q4`
  checkpoint below, where it's cleanly resolved via lifting wrappers after all.**
- The conversation is explicit that this was a **taxonomy-hygiene exercise, not a correctness fix**: "nothing
  functional. Both TopKPattern and BubbleSortPass scored correctly the entire time... A 'layering
  violation' was never a correctness bug, only a taxonomy-hygiene mismatch against the level(c)
  convention."

At the time this section was first written, none of `level()`/`check_layering()`/`allow_mixed_levels`
had been seen in code. **Resolved at the `files_Enforcement` checkpoint below.**

### 5. `level2_examples.py` — the standalone file, now supplied and directly executed

Sonia uploaded `level2_examples.py` (117 lines) standalone. This is the first time the actual file has
been supplied — previously its content was known only via conversation quotes in `Levels_of_competencies_21_07
.docx` and prose description in `Competency_Extraction_Methodology_V24.docx`'s §2.12 (see the
"Methodology V24" section below).

**File contents, confirmed by direct read:**
```
model.register(Competency(
    id="ValidatedAccumulation",
    components={"guard": "GuardedInput", "accumulate": "Accumulation"},
    coverage=ALL(["guard", "accumulate"]),
    structural=REFERENCES("guard.source", "target", "accumulate.assign", "source"),
))

model.register(Competency(
    id="OutputStep",
    components={"out": "OUTPUT"},
    coverage=ALL(["out"]),
    structural=None,
))

model.register(Competency(
    id="AverageStrict",
    components={"acc": "Accumulation", "output": "OutputStep"},
    coverage=ALL(["acc", "output"]),
    structural=AND([
        REFERENCES("acc.assign", "target", "output.out", "source"),
        CONTAINS_TEXT("output.out", "source", ("/",)),
    ]),
))
```
This matches every prior conversation-quoted description exactly: `ValidatedAccumulation`'s `REFERENCES` path
names (`guard.source`→`target`, `accumulate.assign`→`source`) are byte-for-byte what this log already
recorded from the two docx sources; `AverageStrict` preserves *both* checks from the original `Average`
(`REFERENCES` for "same variable" and `CONTAINS_TEXT("/",)` for "actually divided") — confirming the
`Levels_of_competencies_21_07.docx` narrative detail that an initially-dropped `CONTAINS_TEXT("/")` check
was a real mistake caught and fixed before this file reached its final state, since the check is present
here. The file imports `model` from `pw01_competencies` (not `test_real_data`) — also consistent with
that same document's account of a first wrong-module-import mistake having been corrected.

**Directly executed** (not just read) against a real `competency.py` + `pw01_competencies.py` pairing —
specifically the `V1.2.0` checkpoint's versions, chosen because that is the earliest checkpoint in this
log where `REFERENCES`/`CONTAINS_TEXT` already resolve dotted paths into composite children and
`GuardedInput`/`Accumulation`/`Average` are already registered, matching this file's own comments ("this
already works today... built for the Average fix earlier"). Output, run directly in this session:

```
########## Example A: ValidatedAccumulation ##########
  GuardedInput           final=1.00  (coverage=1.00 structural=1.00)
  Accumulation           final=1.00  (coverage=1.00 structural=1.00)
  ValidatedAccumulation  final=1.00  (coverage=1.00 structural=1.00)

Negative control: validates x, but sums an UNVALIDATED y instead
  GuardedInput           final=1.00  (coverage=1.00 structural=1.00)
  Accumulation           final=1.00  (coverage=1.00 structural=1.00)
  ValidatedAccumulation  final=0.00  (coverage=1.00 structural=0.00)

########## Example B: Average vs AverageStrict (should match) ##########
  Average                final=1.00  (coverage=1.00 structural=1.00)
  AverageStrict          final=1.00  (coverage=1.00 structural=1.00)

Buggy variant: forgot the division
  Average                final=0.00  (coverage=1.00 structural=0.00)
  AverageStrict          final=0.00  (coverage=1.00 structural=0.00)
```

This is an **exact match** to every figure both prior conversation documents quoted (`ValidatedAccumulation`
1.00 positive / 0.00 negative control with structural dropping to 0 despite both sub-competencies
individually still scoring 1.00; `AverageStrict` tracking `Average` exactly on both the correct and
"forgot to divide" cases) — now independently re-derived from the actual file and the actual framework
code, not taken on the conversation's word. Levels compute directly (no `level()` method exists yet in `V1.2.0`,
so computed by hand from `components`): `GuardedInput`=1, `Accumulation`=1, `ValidatedAccumulation`=2
(clean, `AND` of two different level-1 skills — the second level-2 shape, distinct from `UniqueCheck`'s
`ANY`-of-alternatives shape); `OutputStep`=1, `AverageStrict`=2 (clean, both children level 1) — matching
the "clean level 2" claim in every prior source exactly.

**This resolves the last "unsupplied file" gap around the level-2 work.** `level2_examples.py` no longer
needs to be treated as narrative-only or conversation-quoted-only anywhere in this log — every remaining
reference to it below is updated accordingly. No date marker of its own accompanies the file (uploaded
standalone, no conversation doc alongside it this round) — its content is consistent with, and was almost
certainly produced during, the 2026-07-21 design work `Levels_of_competencies_21_07.docx` narrates, but
this upload event itself carries no independent timestamp evidence beyond that corroboration.

---

## Enforcement + Q1's LinearSearch — "files_Enforcement" + "q1_competencies.py" + "Q3_Q4_Results_28.docx"

**Real date:** 2026-07-28 (same day as the Q2 third-strategy checkpoint; `Q3_Q4_Results_28.docx`'s own
leading marker is "28/07/2026," and its content — a Q3/Q4 equivalence-class check "same scrutiny Q1/Q2
just got" — reads as the direct continuation of that day's work).

**Source artifacts:**
- `files_Enforcement.zip` → `competency.py` (1030 lines, up from `3rd_strategie`'s 956),
  `test_real_data.py` (224 lines, up from the `files_Report_*` checkpoint's 212), `pw01_competencies.py`
  (191 lines, up from `V1.2.0`'s 180).
- `q1_competencies.py` (38 lines, new, uploaded standalone rather than in a zip) — imports from
  `competency` and `test_real_data`, so belongs in the same working directory as the above.
- `Q3_Q4_Results_28.docx` — a short conversation export (16 paragraphs, 0 tables, read in full via
  python-docx).

### 1. The `level()` enforcement mechanism — now real code, confirming last checkpoint's narrative

**Confirmed by diff against `3rd_strategie`'s `competency.py` — a pure 74-line addition, zero deletions:**
a `Competency.allow_mixed_levels: bool = False` field; a new `LayeringViolation(ValueError)` exception;
and, on `CompetencyModel`, a memoized `level(cid)` method (0 for anything not in `self.definitions`,
otherwise `1 + max(level of each component)`), a `child_levels(cid)` helper, `check_layering(cid=None)`
(audits the *currently registered* library for mixed-level composites, independent of
`allow_mixed_levels` — a read-only report), and `register()` itself now raises `LayeringViolation` if a
*new* registration mixes levels and doesn't set `allow_mixed_levels=True` — computed from the
`Competency` object being registered, not from `self.definitions`, so a rejected registration leaves the
model genuinely unmodified rather than storing the violator before raising. This matches the conversation's own
description from the prior checkpoint almost exactly, including the "turns a documented-in-prose
exception into a documented-in-code one" framing — except the conversation had said this lived "in
pw01_competencies.py"; the actual enforcement mechanism (`level()`/`check_layering()`/`register()`) is in
**`competency.py`** itself, in the `CompetencyModel` class — `pw01_competencies.py` only carries the
per-competency `allow_mixed_levels=True` flags (see below). Logged as a correction to the prior
checkpoint's conversation-derived note on where the code lives.

**A genuine oddity in the supplied file, flagged rather than silently corrected:** `competency.py`
contains two consecutive `class CompetencyModel:` definitions (lines 768 and 773) — the first a 4-line
stub with only `__init__`, immediately followed by the second, complete definition (all methods,
including `resolve`/`resolve_by_scope`/`register`). In Python this is harmless (the second definition
fully shadows the first; nothing else in the file references the stub), but it's a literal duplication in
the source, most likely an editing artifact — noted for accuracy, not treated as a functional bug.

**`allow_mixed_levels=True` confirmed applied to all 4 originally-named violators, by diff:**
`CountedSearch` and `Average` in `pw01_competencies.py` (each with an inline comment matching the prior
checkpoint's conversation quotes almost verbatim — Average's comment specifically references `AverageStrict`/
`level2_examples.py` as already existing); `TopKPattern` and `BubbleSortPass` in `test_real_data.py`
(each with a similar inline comment). **This is the "turn on enforcement with all 4 documented
exceptions" state — not yet the "final audit down to 2" state** the prior checkpoint's conversation described.
`level2_examples.py` (now supplied and executed, see above) and `AverageStrict` are still not bundled
into this specific checkpoint's zip — that file remains a standalone upload, not part of any zip
snapshot. **`TopKPattern`'s own exception was removed one checkpoint later — see `files_Fix_Q4` below.**

**This checkpoint is also where "documented convention, not enforced" genuinely becomes false for the
first time.** Cross-checked this round against `Competency_Extraction_Methodology_V24.docx`, whose own
§2.12 still describes the level concept as "documented as a convention, not enforced in code" and lists
`allow_mixed_levels`/`LayeringViolation`/`check_layering` nowhere in its text — confirming that document
predates this checkpoint. See "Methodology V24" section below for the full dating analysis.

### 2. `q1_competencies.py` — `LinearSearch`, resolving a long-standing pending item

**New competency, confirmed by direct read (no prior version to diff against):**
```
model.register(Competency(
    id="LinearSearch",
    components={"target": ("INPUT", "PARAM"), "test": "TEST", "loop": "LOOP"},
    coverage=ALL(["target", "test", "loop"]),
    structural=AND([
        NESTED("loop", "test"),
        SHARED_BINDING([("target", "target", "test", "operand")]),
    ]),
))
```
All-primitive components (level 1) — no `allow_mixed_levels` needed, consistent with it not being named
among the 4 violators. The file's own comment explains the design choice at length: `LinearSearch` is
structurally identical to `GuardedInput`, but registering it as an independent competency (rather than a
lifting wrapper around `GuardedInput`) is deliberate — wrapping would encode a false "search is a kind of
guarded input" relationship in the taxonomy's dependency graph, when the two are only accidentally the
same AST shape (retry-until-valid input vs. scan-and-compare). **This is a near-verbatim match, in
mechanism, to what the old fabricated `VERSIONING.md` had guessed** ("`LinearSearch` registered as an
independent competency distinct from `GuardedInput` despite identical structure (avoids encoding a false
relationship)") — the guess was right about *why*, wrong about *when*: the old doc placed this at an
early "v1.1.0," but real evidence now dates it to 2026-07-28, well after the Q1–Q5 full-corpus validation
work, not near the start. No batch/corpus validation numbers for `LinearSearch` itself were included in
this checkpoint's docx (`Q3_Q4_Results_28.docx` covers Q3/Q4, not Q1) — only the file's own 3-file
`__main__` spot-check against real `question_1` submissions. **Confirmed absent from
`Competency_Extraction_Methodology_V24.docx` as well** (no mention of `LinearSearch` or Q1 anywhere in
that document's text) — consistent with V24 predating this checkpoint too.

### 3. `Q3_Q4_Results_28.docx` — full-corpus Q3 and Q4 results, and the strongest transfer result in the project

Per the conversation (quoted), Q3 and Q4 got "the same scrutiny Q1/Q2 just got": full batch validation, function
scoped, "exactly matching the Q1/Q2 methodology."

**Q3 (`remove_extras`, `SelectionStep`): 93.6% → 94.0%.** The gap was traced to `.insert()` not being
recognized as a collection mutation by the `ASSIGN` detector (only `.append()`/`.pop()`/`.remove()`
were) — "extending `detect_assign`'s recognized collection-mutation kinds" and mirroring the earlier
`.pop()`/`.remove()` precedent from `ex2_3_4`. The remaining misses (a list comprehension, a
ternary-guarded assignment, a recursive delegate — "each only 2-3 files") were sampled, quantified, and
explicitly not chased: "not worth the engineering for 2-3 files each." **Per `Detect_primitive_advanced_
Refactory.docx` (see below), Q3 still has no dedicated advanced competency of its own as of that
document — it explicitly calls this a documented "Gap," reusing `SelectionStep` as-is rather than
defining something like a hypothetical `MembershipGuardedAccumulation` — consistent with everything
logged here about Q3.**

**Q4 (`sort_age`): the conversation calls this "the actual finding of this round," not a minor fix.** The
original Q4 taxonomy assumed swap-based sorting (`BubbleSortPass`), matching the reference solution's own
strategy. Batch validation found `BubbleSortPass` alone covers only **13.1%** of real submissions. The
dominant real strategy, **64.4%**, turned out to be "repeatedly find the max, remove it, build a new
list" — structurally identical to `TopKPattern`, built entirely for Q5's `top_k`. Tested directly against
`sort_age`: "zero new code needed, it already scored correctly" — a genuine cross-exercise transfer.
`SortByKey = ANY(BubbleSortPass, TopKPattern)` was then built, "clean level 4, zero layering violations,"
reaching **77.6%** combined coverage — the conversation calls this "the strongest cross-exercise transfer result
in the whole project." The remaining 22.4% is named as "recursive partition-based sorting — literally the
same magus_sort-style algorithm found in Q5 much earlier — and an actual quicksort delegate," flagged as
a distinct, bigger undertaking, not built. This is the first time `magus_sort` is given any concrete
description ("recursive partition-based sorting") beyond its bare name in the earlier bug-table mention —
still no code for it in any supplied artifact, but no longer entirely unexplained.

**A discrepancy was flagged here previously** — this docx states the Q4 fix was saved into
"files_Enforcement," but neither `.insert()` nor `SortByKey` was present in that zip. **Now resolved —
see the `files_Fix_Q4` checkpoint immediately below, which supplies both.**

---

## `files_Fix_Q4` + standalone `test_real_data.py` — resolves the prior checkpoint's discrepancy

**Real date:** 2026-07-28, 04:03 — this time not inferred from conversation prose but read directly from the
zip's own per-file modification timestamps (`unzip -l`), which the archive preserved: both `competency.py`
and `test_real_data.py` show `2026-07-28 04:03`.

**Source artifacts:**
- `test_real_data.py` (224 lines, uploaded standalone) — same line count as the `files_Enforcement`
  checkpoint's `test_real_data.py`, but **not** byte-identical: see below.
- `files_Fix_Q4.zip` → `competency.py` (1040 lines, up from `files_Enforcement`'s 1030),
  `test_real_data.py` (249 lines).

**Confirmed by diff, the standalone `test_real_data.py` vs. `files_Enforcement`'s:** `TopKPattern` is
substantially refactored, and this is the resolution of the "irreducible" claim flagged two checkpoints
ago. Three new lifting-wrapper competencies are added: `LoopStep = ALL(inner: LOOP)` (level 1),
`LoopStep2 = ALL(inner: LoopStep)` (level 2), `RemovalAssign = ALL(assign: ASSIGN)` with
`structural=CONTAINS_TEXT("assign", "kind", ("remove", "pop"))` (level 1, moving the
"specifically `.remove()`/`.pop()`" check down from `TopKPattern` itself), and
`RemovalAssignStep = ALL(inner: RemovalAssign)` (level 2). `TopKPattern` is redefined:
```
components={"loop": "LoopStep2", "select": "FindExtremum", "remove": "RemovalAssignStep"}
coverage=ALL(["loop", "select", "remove"])
structural=AND([NESTED("loop", "select"), NESTED("loop", "remove")])
```
Computing levels directly: `LoopStep2`=2, `FindExtremum`=2 (unchanged, `ANY(SelectionStep, 
FindExtremumBuiltin)`, both level 1), `RemovalAssignStep`=2 — all three of `TopKPattern`'s components are
now level 2, so `TopKPattern` itself is a clean level 3 with **no mixed-level composition** — and
**`TopKPattern`'s `allow_mixed_levels=True` flag is gone from this registration**, consistent with the
level check no longer being violated. Only `BubbleSortPass` still carries `allow_mixed_levels=True` in
this file. Since `BubbleSortPass`'s own level is also computed as 3 (its mix of level-0 primitives and
level-2 `Swap` still needs the flag, but the composite itself resolves to level 3), this is exactly what
makes `SortByKey = ANY(BubbleSortPass, TopKPattern)` land as "clean level 4, zero layering violations" —
the prior checkpoint's conversation quote is now directly verified against the actual computed levels, not just
taken on faith.

**A second, necessary bug fix, confirmed by diff of `competency.py` (`files_Enforcement` 1030 lines →
`files_Fix_Q4` 1040 lines):**
1. `.insert()` added to `detect_assign`'s recognized collection-mutation kinds — the exact Q3 fix
   `Q3_Q4_Results_28.docx` described (`("append", "add", "pop", "remove")` → `(..., "insert")`).
2. `NESTED.score()`'s same-evidence reuse guard changed from `outer_ev.node is not inner_ev.node` to
   `outer_ev is not inner_ev`, with a code comment explaining exactly why: a composite `Evidence`
   *always* has `.node = None` (it doesn't correspond to one particular AST node), so the old check would
   compare `None is not None` → `False` whenever **two different composites** both sat in a `NESTED`
   check's two slots — incorrectly treating them as "the same evidence reused" and rejecting the match.
   This is precisely the situation the new `LoopStep2`/`RemovalAssignStep` wrappers create inside
   `TopKPattern`'s own `NESTED("loop", "remove")` check (both composites, both `node=None`) — **without
   this fix, the level-driven `TopKPattern` refactor above would have silently broken `TopKPattern`
   itself**, always scoring `NESTED("loop","remove")` as `0.0` between two different lifting wrappers. Not
   named in any supplied conversation document; identified directly from the diff and dated to this checkpoint by
   its necessity alongside the `TopKPattern` refactor and by the zip's own file timestamp.

**`SortByKey` itself, confirmed present, resolving the prior checkpoint's discrepancy:** the zip's
`test_real_data.py` (249 lines) is the standalone 224-line file plus exactly one clean addition:
```
model.register(Competency(
    id="SortByKey",
    components={"inplace_swap": "BubbleSortPass", "repeated_extraction": "TopKPattern"},
    coverage=ANY(["inplace_swap", "repeated_extraction"]),
    structural=None,
))
```
with a comment quoting the same figures as `Q3_Q4_Results_28.docx` almost verbatim: "Batch validation
against all 419 real sort_age submissions found BubbleSortPass... covers only 13.1%... TopKPattern...
64.4% alone... Combined: 77.6%." 419 matches the Refactory Q4 corpus total logged earlier in this doc
(419 correct). **This directly resolves the discrepancy flagged in the prior checkpoint** — the `.insert()`
fix and `SortByKey` composition described in `Q3_Q4_Results_28.docx` are now both present in code, just
one checkpoint later than that conversation's own "saved in files_Enforcement" description suggested. No
`__main__`-block smoke test for `SortByKey` itself is present in either supplied `test_real_data.py` — the
77.6% figure remains conversation-reported, not re-derivable from a script in these files, though the composition
and its constituent pieces are now fully code-confirmed.

---

## Methodology V24 + Detect_primitive table + Levels_of_competencies (21/07) + Summaize (28/07) — a four-document contradiction check

Sonia supplied four docx documents together and asked directly whether they contradict each other or the
rest of this log. Findings below, organized by document, then a synthesis at the end.

### `Competency_Extraction_Methodology_V24.docx` — 104 paragraphs, 6 tables, read in full

This is the single most information-dense document supplied so far — effectively a complete methodology
write-up (Motivation, Methodology §2.1-2.12, three Case Studies, Bugs Found, Design Principles,
Limitations, Conclusion). Cross-checked exhaustively against every checkpoint above; **no numeric or
structural contradiction was found against any code-confirmed fact in this log.** Every figure this
document states matches: the Refactory corpus counts (Table 2: Q1 768/575, Q2 291/435, Q3 546/308, Q4
419/357, Q5 418/108 — exact match to every corpus total already logged); the 30% Top-K builtin-usage
figure and 33% Q2 counter-vs-alternative figure (both already logged); the 83.0%→78.2% / 75.0% Case
Study 3 figures (exact match to `topk_report.csv`, already logged); the primitives table (10 entries,
matching every detector this log has confirmed through `V1.2.0` — `ASSIGN`'s described mutations stop at
`.append()/.add()/.pop()/.remove()`, with **no `.insert()`**); the structural-constraints table (11
entries — `NESTED`, `SEQUENTIAL`, `SHARED_BINDING`, `SELF_REFERENTIAL`, `TUPLE_SWAP`, `CONTAINS_TEXT`,
`REFERENCES`, `AND`/`OR`, `COOCCUR`, `EXHAUSTIVE_CHAIN`, `DELEGATES` — consistent with `V1.2.0`, and
**`DISTINCT_BINDINGS`/`HAS_ELSE` are absent**, consistent with this log's own note that both are
present-but-unused in the code); the Ex2-4 competency/level table (Table 4: exactly the 9 competencies
this log already described, with `GreedyChange` and `BalancedCheck` the only two reaching level 2 —
matching §4.1's own text, "only 2 reach level 2"); and Ex4's DELEGATES status ("validated on question_2's
contains_unique_day → unique_day... but not yet applied to this exercise's own win-checker" — an exact
match to this log's existing `V1.2.0` section).

**What this document does NOT contain — checked directly by full-text search, not by omission alone —
is what places it precisely in this log's timeline:** no mention anywhere of `LinearSearch`, `SortByKey`,
`AccumulateThenCount`, `.insert()`, `allow_mixed_levels`, `LayeringViolation`, `check_layering`,
`LoopStep2`, `RemovalAssign`, `q1_competencies`, or any of the specific percentages 90.4% (Q2), 94.0%/
93.6% (Q3), 77.6%/13.1% (Q4). Its own §2.12 explicitly frames the level concept as **"a documented, not
enforced, design principle"** (that is the section's literal title) and its closing paragraph states the
remaining technical work explicitly as future work: "...before strict layering could move from documented
convention to something safe to enforce." Both `ValidatedAccumulation` and `AverageStrict` ARE described
in full, in prose matching `Levels_of_competencies_21_07.docx` closely, and now also matching
`level2_examples.py`'s actual, directly-executed code exactly (see above).

**Conclusion: this document is a genuine, internally-consistent snapshot, but it predates every
2026-07-28 checkpoint in this log** (`fixQ2`'s Q2 third strategy, `files_Enforcement`'s actual
enforcement code, `q1_competencies.py`'s `LinearSearch`, `Q3_Q4_Results_28.docx`'s Q3/Q4 results, and
`files_Fix_Q4`'s `SortByKey`/`TopKPattern` refactor) — while clearly postdating `V1.2.0` (DELEGATES wired,
per-function scoping live) and the reporting/batch-tooling work (§2.10, §5, bug #13). Its content is
consistent with having been written around **2026-07-21**, the same date `Levels_of_competencies_21_07
.docx` carries, and the same window `level2_examples.py`'s own content is now confirmed to belong to.

**This creates one genuine, unresolved puzzle worth stating plainly rather than papering over:**
`Summaize_to_move_the_project_28.docx` (read in full, see below), dated 28/07/2026, describes actively
regenerating and expanding *the methodology doc itself* that same day — "Let's view the end of §6.2 to
add §6.3 and §6.4... regenerate and verify the methodology doc: 15 pages (up from 14), clean numbering,
zero 'Related Work' mentions" — explicitly in the context of documenting the Q3/Q4 results and "a design
principle reinforcing this stronger transfer finding" (i.e. the `SortByKey` cross-exercise-transfer
result). If that description is of the same document, the resulting file should describe Q3/Q4 results,
`SortByKey`, and (very likely) the enforcement mechanism — none of which `Competency_Extraction_
Methodology_V24.docx` contains. **The most likely resolution, based on the evidence actually in hand: the
"V24" supplied this round is an earlier version than the one `Summaize_to_move_the_project_28.docx`
describes regenerating — i.e., there exists a later version (V25 or beyond, not yet supplied) that
would contain the Q3/Q4/enforcement content, and "V24" itself is genuinely a ~21/07-era snapshot that
happens to have been bundled into this later upload batch.** This is stated as the best-supported reading
of the evidence, not as a confirmed fact — no document actually states V24's own generation date, and the
version-numbering scheme (what "V24" counts, how many prior versions exist) has not been explained in any
supplied artifact. Flagging as **open** rather than resolved.

#### The canonical bug table (Table 5, 13 entries) — now recorded here in full for the first time

This is new, load-bearing information: every bug this log has referenced by number, in one place, in the
document's own words (condensed):

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| 1 | `Swap` could not be defined at all | three roles needed the same primitive type, but `components` was a flat list keyed by type id | `components` became a `dict` of `slot_name -> type_id` |
| 2 | `GuardedInput` scored 0 on every function-graded submission | only recognized `input()`; data arrives via parameters | added `PARAM`; slots accept `(INPUT, PARAM)` |
| 3 | `BubbleSortPass` scored 0 even on a textbook match | a losing `Swap3Step` `OR`-branch produced a placeholder `(0,0)`-span `Evidence` that leaked into `Swap`'s composite span | a sub-competency's evidence only propagates to its parent if its own score is `> 0` |
| 4 | `ConditionalCount` scored 0 on an exact match | composing `Accumulation` inside `NESTED(test, Accumulation)` broke because `Accumulation`'s span includes its `DECL` line, legitimately outside the `TEST` | redefined directly over primitives instead of nesting a full composite's span |
| 5 | `StackBalance` scored 1.0 on a pure-counter solution | push/pop slots typed only as `ASSIGN`, no check on *which* `ASSIGN` | `CONTAINS_TEXT` checks requiring actual `.append()`/`.pop()` |
| 6 | `CounterBalance` scored 1.0 on a stack-based solution | symmetric to #5 — incr/decr slots accepted any `ASSIGN` with a matching target | required the source text to contain the AugAssign operator, bound to a `DECL`'d counter |
| 7 | `.remove()`/`.pop()` invisible to the model | `ASSIGN` detector only treated `.append()`/`.add()` as mutation evidence | extended detection to `.pop()`/`.remove()`, tagged in `kind` |
| 8 | hand-unrolled elif-chain composition (`Chain2`→`Chain3`) silently failed past depth 1 | a composed `Evidence.node` is `None` by design — nothing left to compare once one side is a composite | abandoned DAG-based chain composition; walk the elif chain directly from the raw AST (§2.7, `EXHAUSTIVE_CHAIN`) |
| 9 | `MultiWayBranch` still scored 0 on a real if/elif/else after the operand-check fix | off-by-one: only `If`-nodes traversed were counted, undercounting an if/elif/else's 3 outcomes as 2 | count total distinguishable outcomes (each `If`-test plus terminal `else`) |
| 10 | `GuardedInput` scored 1.0 on a function with no input/parameter of its own | `SHARED_BINDING` has no location awareness; an unrelated sibling function's same-named parameter satisfied the slot | tagged every evidence with its enclosing function; resolver rejects combinations spanning >1 function scope |
| 11 | the scope guard from bug #10 didn't fix the bug on the first attempt | `PARAM` evidence stores the `FunctionDef` node itself, so walking up skipped past the function, giving every parameter scope `None` | special-cased `PARAM`'s scope to be the function it belongs to |
| 12 | `TopKPattern` scored 1.0 on a submission that appends the same max k times and never removes it | `TopKPattern` composed `FindExtremum` without separately checking removal; `FindExtremum` alone doesn't and shouldn't imply removal | added an explicit `remove` slot to `TopKPattern`, not to the reusable `FindExtremum` |
| 13 | `TopKPattern` credited 83.0% of correct submissions at whole-file scope; a sampled case's actual `top_k` function had no loop/test/removal logic of its own | whole-file resolution let an unrelated helper (`magus_sort`) elsewhere in the file independently satisfy the competency, crediting the file even though the graded function delegates to it | added function-scoped reporting (§2.10) — resolve only against the named function's own subtree |

Bugs #1-#7 were previously logged individually, scattered across the `V1.0.0`/`ex2_3_4` sections above
(now cross-referenced back to this table by number, in place). Bugs #8-#11 were previously logged as part
of the `V1.2.0` narrative (now numbered explicitly). Bugs #12-#13 were previously known only by name
("TopKPattern missing-removal," "magus_sort cross-function-credit") — this is the first time their full
canonical symptom/root-cause/fix text has been available, and it confirms bug #13 is specifically what
motivated building the `function_name`-scoped reporting parameter.

### `Detect_primitive_advanced_Refactory.docx` — 1 table (9 rows × 6 cols), no date marker of its own

Maps each Refactory question to its advanced competency, type/level, pedagogical meaning, and structural
shape. **No contradictions found; two points corroborate and sharpen existing log content:**

- **Q3: "— no dedicated competency documented —", explicitly marked "Gap"** — states a hypothetical
  `MembershipGuardedAccumulation` is "worth defining explicitly" but doesn't exist. This matches this
  log's own repeated note that Q3 reuses `SelectionStep` as-is, with zero new competency code across every
  checkpoint supplied.
- **Q5's `TopKPattern` row describes the *older*, pre-`files_Fix_Q4` definition** — `remove: ASSIGN`
  directly, not the `LoopStep2`/`RemovalAssignStep`-lifted version — with the note "Structure =
  NESTED(loop → select, remove) — added explicitly after bug #12, since FindExtremum alone doesn't imply
  removal." This is the document that first named the missing-removal fix "bug #12" in a form this log
  could cross-reference; it's now been given the same number and the same wording independently in
  `Competency_Extraction_Methodology_V24.docx`'s Table 5 (confirms bug numbering is consistent across
  documents, not something being reconstructed here). This document's own dating (implicitly pre-
  `files_Fix_Q4`, since it describes the *unlifted* `TopKPattern`) is therefore also consistent with a
  ~21/07–pre-28/07 origin, the same window as V24.
- Q2's `DELEGATES(call, ConditionalCount)` row (cross-function, `contains_unique_day` → `unique_day`)
  matches `DelegatesUniqueness` exactly as logged under `V1.2.0`.

### `Levels_of_competencies_21_07.docx` — 100 paragraphs, 0 tables, dated 21/07/2026 by its own leading marker

Already analyzed against `V1.2.0`'s code and `fixQ2`'s comment above (see the dating-correction note
under "Q2 fix + third strategy" §1 and §5). Restating the conclusion here since it's central to this
round's findings: this document, `Competency_Extraction_Methodology_V24.docx`, `level2_examples.py`
itself (now directly executed, see above), and the later `fixQ2` code checkpoint together tell a
*consistent*, three-part story once "designed/written up" is separated from "committed into a saved code
snapshot": the level concept, its 4-violator count, its technical blocker, `ValidatedAccumulation`, and
the `AverageStrict` fix were all designed and demonstrated (with real, quoted test output, including two
of the assistant's own mistakes caught and fixed along the way — a wrong module import, and an
initially-dropped `CONTAINS_TEXT("/")` check, both visible as already-fixed in the final supplied file)
on **21/07/2026**; the actual 37-line design-principle comment was pasted into the saved `competency.py`
file for the first time at the `fixQ2` checkpoint, dated **28/07/2026**; and full code-level
*enforcement* (`allow_mixed_levels`, `LayeringViolation`, `check_layering()`) didn't exist until
`files_Enforcement`, the same day. No contradiction remains open here — the one flagged in an earlier
round of this log is now resolved by `Competency_Extraction_Methodology_V24.docx` and, this round,
`level2_examples.py`'s own executed content, both independently corroborating the 21/07 dating.

One item from this document not yet incorporated elsewhere in this log: paragraph 26's "Synthesis of the
architecture" section states, in Sonia's own words as of 21/07/2026, that the reporting layer was
"optionally scoped to one named function" and the batch CSV processor was "validated against 526 real
submissions" — both **already true by 21/07**, consistent with this log's dating of the reporting/batch
checkpoint as preceding `fixQ2`/`Enforcement` (though the reporting zips themselves carry no date marker
of their own and were placed in this log by inference from the 21/07 conversation narrative, not a direct
timestamp — this remains the one soft spot in an otherwise well-corroborated chronology).

### `Summaize_to_move_the_project_28.docx` — 8 paragraphs, 0 tables, dated 28/07/2026

Confirms, verbatim-consistent with `Q3_Q4_Results_28.docx`, the Q3 (93.6%→94.0%) and Q4 (13.1%→64.4%→
77.6%, "the strongest cross-exercise transfer result in the whole project") figures — no new
contradiction on the numbers themselves. **One new structural fact, not previously captured in this
log:** paragraph 6 states "I'm treating 'the paper' as the separate standalone article
(`Competency_Extraction_Article.docx`), which is more out of date than the methodology doc — it predates
enforcement, the NESTED bug, and all of Q1–Q4 entirely." This means, going forward, any future reference
to "the paper" (as distinct from "the methodology doc"/"the methodology note") in a supplied document
should be read as referring to a *third*, still-unsupplied document (`Competency_Extraction_Article.docx`)
that is explicitly *older* than everything currently in this log — not as a synonym for the methodology
doc. Paragraph 6 also states both documents were being updated together on 28/07, which is the basis for
this section's "V24 is likely an earlier version than what this describes" conclusion above.

### Synthesis — direct answer to "is there any contradiction?"

**No contradiction was found between any of these four documents' factual claims and the code-confirmed
facts already in this log.** Every number and structural detail either matches exactly or fills a
previously-open gap (the canonical bug table; bug #13's role in motivating function-scoped reporting; the
Q3 "gap" status; `ValidatedAccumulation`'s exact test results, now doubly confirmed by direct execution).
**The one apparent contradiction found — `Competency_Extraction_Methodology_V24.docx` describing level
enforcement as still-undone, despite being supplied alongside documents describing 28/07 work that (per
this log) happened after enforcement was built — is resolved, not left standing:** it's evidence that
"V24" is an earlier snapshot than its supplied-together siblings, not a factual error in the document
itself. The one **genuinely open** question is whether a later methodology-doc version (V25+, matching
`Summaize_to_move_the_project_28.docx`'s "15 pages, Q3/Q4 results" description) exists and simply hasn't
been supplied yet — worth asking Sonia directly rather than guessing further.

---

## "To copy to new project" + "Transfert to new project" — a retrospective system summary, not a checkpoint

Sonia supplied two documents explaining she had moved her work from a free-tier assistant project into a
new Pro-account project, and these are what she used to do it. Unlike every artifact above, neither is a
dated code checkpoint or a raw conversation export — `To_copy_to_new_project.docx` (81 paragraphs, 0 tables) is a
**condensed system summary** (almost certainly produced by asking the assistant to "summarize the project's
purpose and reproduce the instructions in a structured format," per `Transfert_to_new_project.docx`'s own
advice — see below), and `Transfert_to_new_project.docx` (29 paragraphs, 0 tables) is mostly
**administrative** (how assistant-project migration works) with one small but important tail. Both are dated
here only as "after everything already in this log," since neither carries its own date marker or code.

### `To_copy_to_new_project.docx` — largely corroborating, with a few genuinely new facts

Cross-checked against the whole log: the primitive list (12 entries, including `CALL`,
`FUNCTIONAL_COLLECT`, `COUNT_CHECK`) and the structural-constraint list (13 entries, including `HAS_ELSE`
and `DISTINCT_BINDINGS`) both match the framework exactly as diffed through `files_Fix_Q4` — this is the
first document to explicitly count `FUNCTIONAL_COLLECT`/`COUNT_CHECK`/`HAS_ELSE`/`DISTINCT_BINDINGS` as
first-class parts of the system's vocabulary despite this log's own repeated note that none of the four
is referenced by any registered competency in any supplied file — a useful confirmation that "present but
unused" is the right characterization, not "abandoned" or "mistakenly left in."

**One real ambiguity is resolved:** "Enforced at register() time via LayeringViolation, with
allow_mixed_levels=True as a documented escape hatch (**only BubbleSortPass still needs it**)" — this is
the first document to state plainly, as a settled fact, that `BubbleSortPass` is the *sole* remaining
exception. This confirms what `files_Fix_Q4` already made computable (`TopKPattern`'s flag is gone,
`BubbleSortPass`'s remains) is also the system's actual final state, not an intermediate one still being
worked on.

**A genuinely new, and more specific, explanation for *why* `BubbleSortPass` stays an exception:** "same
wrapped sub-competency in two sibling slots resolves once and gets shared → correctly left as a known,
documented exception (needs a resolver core change)." This is more precise than anything logged so
far — every prior source described `BubbleSortPass`'s exception only as "a swap needs to sit alongside a
higher-level sibling," but this names an actual resolver-level obstacle to giving it the same
`LoopStep2`-style lifting treatment `TopKPattern` got: if `BubbleSortPass` needed the *same* lifted
wrapper competency to fill two different sibling slots, the resolver's per-competency memoization cache
(`cache: dict` in `resolve()`, confirmed present in every supplied `competency.py`) would resolve it once
and share that single `Result` across both slots — a real, distinct mechanism from the `NESTED`
identity-comparison bug fixed at `files_Fix_Q4`, and still open (no fix, no code, described as needing "a
resolver core change"). **This is new: not previously in this log at any level of detail.**

**A bug list that goes beyond the canonical 13 — three or four additional items, not in
`Competency_Extraction_Methodology_V24.docx`'s Table 5:**
- "Diagnostic script float-vs-string bug → false 0% regression" — no prior mention anywhere in this log.
- "Duplicate competency registration silently overwrote a working definition" — no prior mention.
- "Layering-violation check stored the violator before rejecting it → compute levels pre-registration" —
  this describes an *earlier, buggier* version of the exact `register()`-time enforcement mechanism this
  log already documents at `files_Enforcement` (which computes from the `Competency` object being
  registered, "so a rejected registration leaves the model genuinely unmodified rather than storing the
  violator before raising" — see that section). This document confirms that safeguard was **itself a bug
  fix**, not the mechanism's original design — an earlier version really did store the violator into
  `self.definitions` before checking, then got corrected. `files_Enforcement`'s supplied `competency.py`
  only shows the already-fixed form; no earlier, buggy version of `register()` has been supplied as code.

None of these three has a numbered slot, a symptom/root-cause/fix writeup as detailed as the V24 table's,
or any accompanying code — they're compressed to one line each in a summary, not evidenced the way this
log otherwise requires. Logged here as **named but not yet evidenced**, consistent with this log's rule
of stating what's known vs. what's still owed, rather than folding them into the canonical 13-bug table
as if they were equally well-supported.

**Confirms a real file this log has never seen:** "Key module: competency.py (core system), with
supporting files: test_real_data.py, pw01_competencies.py, ex2_3_4_competencies.py, level2_examples.py,
q2_competencies.py, report.py, batch_report.py, **semantic_backup.py**, report_demo.py." Every file named
here except `semantic_backup.py` has now been supplied to this log in some form. `semantic_backup.py`
— the actual CodeBERT/stand-in-embedding implementation behind §2.11 — is confirmed to be a real,
existing file in Sonia's original project, not just a described-in-prose section. Not yet supplied here.

**A page-count figure that doesn't match a prior source, flagged rather than silently reconciled:**
"Internal methodology paper (~11 pages): full development arc including bugs and fixes" — vs.
`Summaize_to_move_the_project_28.docx`'s "regenerate and verify the methodology doc: 15 pages (up from
14)." Both describe what sounds like the same document (the internal, full-development-arc methodology
write-up, as opposed to the separate condensed article). An 11-vs-15-page gap is large enough that it's
worth naming as an open, unresolved inconsistency rather than assuming it's simply an approximate
("~11") rounding of a more precisely-remembered 14/15 — no artifact supplied so far pins down which
figure describes which actual document version.

**Corroborates, rather than contradicts, the methodology-doc/article split** already logged from
`Summaize_to_move_the_project_28.docx`: "Two formal deliverables have been produced: Internal methodology
paper (~11 pages)... Condensed standalone article (~5 pages): publication-style, external audience,
third-person voice, design lessons distilled from the bug table." This matches the existing
methodology-doc-vs-`Competency_Extraction_Article.docx` distinction exactly — internal/detailed vs.
external/condensed — just restated with its own page-count estimate.

**One data-integrity note, about a different project's copy of a familiar filename — not about this
log's evidence:** the document's trailing conversation excerpt states "All 13 project files are ready..." then
"Note: topk_report.csv came through empty in the project — if you were expecting it populated with the
batch run results, it looks like that file didn't get saved with data before the project was created."
This describes a mishap in transferring files into Sonia's **separate assistant project** (the one this
session is attached to, distinct from this reproducibility-audit conversation's own evidence chain) — **it
does not cast any doubt on the `topk_report.csv` already supplied directly to and validated in this log**
(526 rows, 418/108 split, zero parse errors, exact 78.2%/75.0% match to the paper's figures — see the
"Reporting/batch tooling" section above). Flagging the distinction explicitly so the two don't get
conflated: the corrupted copy lives in Sonia's project knowledge base as a side effect of the account
migration described in `Transfert_to_new_project.docx`; the copy already audited here came from a direct
upload to this conversation and remains fully validated.

### `Transfert_to_new_project.docx` — administrative, plus one unrelated leftover fragment

Almost entirely about the mechanics of moving an assistant project between a free and a Pro account (no
built-in transfer exists between separate personal accounts; the workaround is copying project
instructions, downloading source knowledge files, and re-uploading into a freshly created project) — this
explains, procedurally, why `To_copy_to_new_project.docx` exists as a condensed summary in the first
place (paragraph 8 explicitly suggests asking the assistant to "summarize the project's purpose and reproduce
the instructions in a structured format" as a shortcut, which is almost certainly how the companion
document was produced). No technical content relevant to the detector/taxonomy history.

**One small, apparently unrelated fragment at the very end** (paragraphs 27-28): "Prompt for Related
work / can you see the related works from literature for these part of my research, specifically from
2023 to 2026" — reads as the start of a *different*, not-yet-acted-on request (a literature review for
the paper's Related Work section), possibly pasted in by accident alongside the migration content, or
saved here as a reminder of a prompt Sonia intended to reuse in the new project. Not acted on in this
log — flagged for visibility only, since it doesn't bear on version history or reproducibility.

---

## Semantic backup layer — `files_semantic_Backup.zip` + `semantic_20_07.docx`

**Real date: 2026-07-20, 19:47** — confirmed two independent ways: the zip's own per-file timestamps
(`unzip -l`, preserved: both `semantic_backup.py` and `report.py` show `2026-07-20 19:47`) and
`semantic_20_07.docx`'s own leading date marker ("20/07/2026"). This is **earlier** than the
21/07 level-concept design work and earlier than every 07-28 checkpoint already logged — it slots in
right after `V1.2.0` (2026-07-19→21) and before the "Reporting/batch tooling" section above
chronologically, even though it's being logged here, out of date order, as the point it was actually
supplied to this log. This resolves the "**`semantic_backup.py` — not yet supplied**" item that has been
open since the "To copy to new project" round.

**Source artifacts:**
- `semantic_backup.py` (147 lines) — read in full.
- `report.py` (179 lines) — diffed directly against the `files_Report_batch` checkpoint's `report.py`
  (156 lines, logged above).
- `semantic_20_07.docx` (14 paragraphs, including one longer "Architecture" narrative paragraph and a
  "what's actually verified" list) — read in full.

### `semantic_backup.py` — content, confirmed by direct read

A self-contained module, not yet imported by `competency.py`/`test_real_data.py` at this point (only
`report.py` imports it — see below). Structure:
- **`EXEMPLARS` dict** — `competency_id -> [known-correct reference snippet strings]`. Two entries only at
  this checkpoint: `FindExtremum` (3 exemplars: manual-comparison loop, `max()`, a `functools.reduce`
  variant) and `Accumulation` (2 exemplars: running-total loop, `sum()`).
- **`_codebert_embed(code)`** — real `microsoft/codebert-base` inference via `transformers`/`torch`
  (`AutoTokenizer`/`AutoModel`, mean-pooled last hidden state). The module's own docstring states plainly:
  "HONEST STATUS OF THIS FILE: ... this development sandbox's network egress does NOT permit that
  (confirmed directly: 403, x-deny-reason: host_not_allowed — not assumed). ... it has NOT been executed
  end-to-end here." `semantic_20_07.docx` confirms this in the conversation's own words: "transformers and torch
  are already installed here... I just can't execute that download inside this sandbox."
- **`_stub_embed(code)`** — a bag-of-AST-node-type-and-identifier `Counter` (walks the tree, collects
  `ast.Name.id`s plus every node's type name). The docstring is explicit that this is "NOT semantically
  meaningful... it will generically over-rate similarity between any two well-formed Python functions."
- **`embed()`/`_cosine_counter()`/`_cosine_vec()`/`similarity()`** — dispatch by `backend` string
  (`"stub"` default, `"codebert"` real).
- **`semantic_backup_score(source_snippet, competency_id, backend="stub")`** — returns `None` if no
  exemplars are registered for that competency ("silence, not a fabricated zero" — the function's own
  docstring), otherwise the max similarity to any registered exemplar plus which exemplar index and which
  backend produced it, "always to be reported as unverified/heuristic, never folded into `final_score`."
- Exemplar embeddings are `@lru_cache`d per `(competency_id, exemplar_index, backend)`.

### `report.py` — confirmed by diff against `files_Report_batch`'s `report.py`, a clean additive change

```
26a27
> from semantic_backup import semantic_backup_score
64c65,67
< def generate_report(source, model, target_ids, function_name=None):
---
> def generate_report(source, model, target_ids, function_name=None,
>                      semantic_backup=False, semantic_threshold=0.5,
>                      semantic_backend="stub"):
103a115,116
>     snippet_source = ast.get_source_segment(source, scan_tree) if function_name else source
115c128
<         competencies[cid] = {...}
---
>         entry = {...}
122a136,140
>         if semantic_backup and entry["final_score"] < semantic_threshold and snippet_source:
>             backup = semantic_backup_score(snippet_source, cid, backend=semantic_backend)
>             if backup is not None:
>                 entry["semantic_backup"] = backup
>         competencies[cid] = entry
155a174,178
>         if "semantic_backup" in c:
>             ... renders "semantic backup ({backend}): {sim:.2f} similarity to exemplar #{idx}
>                 -- UNVERIFIED, flag for manual review, not auto-credited"
```

Zero lines of the pre-existing report logic were changed — every new parameter defaults to off/inert.
`final_score` itself is never touched anywhere in this diff, matching the non-negotiable design principle
stated in both `semantic_backup.py`'s docstring and `semantic_20_07.docx`'s own words: "semantic
similarity never touches final_score. It's a separately-labeled 'flag for review,' triggered only when
the rule-based signal is weak, never silently blended in."

### `semantic_20_07.docx` — the honest, self-reported limits of the stub backend

Quoted directly, this is the single most important finding in this document: testing the stub backend
against "a genuinely-related `sorted(data, reverse=True)[0]` variant" (not in the exemplar registry) and
"a completely unrelated string-reversal function" gave **0.77 similarity for the related case and 0.79
for the unrelated one** — "That's essentially no discriminative power... generic AST-node tokens (Name,
Load, For, Assign) dominate the signal regardless of actual meaning. I won't paper over that." A separate,
easier test (a `functools.reduce`-based extremum finder, invisible to both `SelectionStep` and
`FindExtremumBuiltin` since it has no `ast.If`, no explicit loop, and no `max()`/`min()` call) did
correctly trigger the backup and flag it — but the doc itself calls this test "too easy" (exemplar #2 in
the registry is nearly identical to it) and immediately follows up with the harder, discriminative-power
test above specifically to avoid overstating the result. The doc's own closing "to actually use this"
list states plainly that `semantic_threshold=0.5` "was used arbitrarily" and that the exemplar registry
"is currently seeded with just 2-3 hand-written examples per competency, enough to test wiring, not enough
for real coverage."

**Cross-checked against `Competency_Extraction_Methodology_V24.docx`'s §2.11** (already logged above,
described only in prose at the time): consistent — no contradiction. Both describe the same architecture,
the same sandbox network block, and the same honest "wiring proven, not semantically validated" status.

---

## The 28/07 methodology note (`Competency_Extraction_Methodology.docx`, actually plain-text Markdown) + `Structural_Competency_Extraction_Paper.docx` — the finished paper

Sonia supplied two more documents this round: "the last one for the 28/07" methodology paper, and a
separate paper file. Both required a real, worth-recording discovery about file format, and together they
resolve several previously-open items in this log while also surfacing one genuine correction to this
log's own prior text and two newly-flagged, unresolved discrepancies.

### File-format note: `Competency_Extraction_Methodology.docx` is not actually a `.docx`

`python-docx` failed on it with `PackageNotFoundError: Package not found` — not a corrupted zip, a
byte-level check (`b'\x00' in data` → `False`) confirmed no binary corruption. `file`/manual inspection
confirmed it is **plain UTF-8 Markdown text**, saved with a `.docx` extension. Copied to a `.md`-suffixed
path and read directly (52,705 bytes, 310 lines). Logged here as a factual note about the artifact, not a
correctness issue in its content.

### What this document is: internally consistent, and it postdates every checkpoint logged so far

Cross-checked exhaustively against this log. No numeric or structural contradiction was found against any
code-confirmed fact. It confirms, directly and for the first time as **prose written from the perspective
of already having enforcement live**: "reducing known violations from 4 to 1" (§ near the limitations
section, paragraph quoted: "...strict competency layering has moved from a documented convention to
something `register()` actually enforces (§2.12) — reducing known violations from 4 to 1"). It also
supplies, for the first time in one place, a **Case Study 4** ("Completing the Target-Competency
Taxonomy") covering:

- **§6.1, Q1**: `LinearSearch` vs. `GuardedInput`, "validated against the FULL Question 1 dataset (1,343
  submissions, correct and wrong combined): zero mismatches between `LinearSearch` and `GuardedInput`
  across all 1,342 usable files." **This resolves the "full-corpus batch validation for Q1" item that has
  been open in this log's "Still-pending items" since the first round.** (One file among the 1,343 is
  implicitly unusable/unparseable — the doc doesn't name why, and no batch CSV was supplied alongside this
  narrative, so the exact identity of that one file and the script that produced this count remain
  unevidenced beyond the doc's own sentence.)
- **§6.2, Q2**: the same 85.2% / 0.7% / 4.5% / 90.4% breakdown already logged from `The_output_Results_26
  .docx`, restated here with the same exact numbers — no new figures, but now cross-confirmed by a third
  independent document.

### A precise, quoted internal inconsistency within this document itself — the stale "33%" figure

Two passages in this same file describe the pre-correction Q2 estimate, and they characterize it
oppositely. Quoted exactly:

- **Line 160** (the paper-narrative section, describing Case Study 1's original findings): "33% of correct
  Question 2 submissions (95 of 291) use an explicit counter (`count = 0 ... count += 1`) **rather than
  the alternative** tuple-accumulate-then-`.count()` strategy" — i.e., 33% is described as the share using
  the **counter** strategy.
- **Line 224** (§6.2 itself, introducing the correction): "an initial estimate that 33% of correct
  submissions used **'the alternative strategy'** turned out to be inaccurate on inspection" — i.e., the
  same 33% figure is now described as the share using **not** the counter, but "the alternative."

These are opposite readings of what the stale 33% number meant, inside one document, and neither is
merely a rounding or rephrasing difference — one names the counter strategy, the other explicitly names
"the alternative." **`Structural_Competency_Extraction_Paper.docx` (read in full this round, see below)
resolves which reading the project's own finished prose actually settled on**: its §5.1 states, in nearly
identical wording to this document's line 160, "33% of correct Question 2 submissions (95 of 291) use an
explicit counter rather than a tuple-accumulate-then-`.count()` strategy" — matching line 160's version,
not line 224's. This is recorded as a real, quoted internal inconsistency in the 28/07 methodology note,
resolved in favor of line 160's reading by the separately-supplied finished paper — not silently corrected
away.

### Q5's 82.1% figure — resolved, not a contradiction, once the exact passage is read

This document adds a note not present in `topk_report.csv` or any other artifact logged so far, quoted
exactly: "TopKPattern was later restructured for strict layering compliance (§2.12). Re-running this same
batch against the restructured definition reproduced the scoped figure (78.2% / 75.0%) exactly, confirming
the fix changed structure, not behavior. **The unscoped figure shifted slightly (83.0% → 82.1% correct)**,
traced to a smaller-scale instance of the same limitation described in §2.12 (a wrapped primitive resolved
once and shared, rather than searched independently) — a further, independent reason the unscoped figure
was never the one to trust."

So: **82.1% is the *unscoped* re-run after the `TopKPattern` → `LoopStep2`/`RemovalAssignStep` refactor**
(`files_Fix_Q4`, already logged above); it is a distinct, smaller shift from the original 83.0% unscoped
figure, and is explicitly attributed to the *same class* of resolver-level shared-slot-resolution
limitation as `BubbleSortPass`'s own unfixed obstacle (bug #19, see below) — not the same number as, and
not in tension with, the **scoped** 78.2%/75.0% figures, which this passage states explicitly were
re-verified unchanged. `Structural_Competency_Extraction_Paper.docx` does not mention this 82.1%
refinement at all — its own Case Study 3 only reports the original 83.0%→78.2%/76.9%→75.0% correction —
so this detail exists only in the internal methodology note, not in the finished paper's own prose. No
contradiction; the two documents simply differ in how much of the post-refactor story they carry forward.

### The NESTED identity bug (bug #18) — **a correction to this log's own prior attribution**

This log's `files_Fix_Q4` section (above) previously stated, about the `NESTED.score()` fix
(`outer_ev.node is not inner_ev.node` → `outer_ev is not inner_ev`): *"Not named in any supplied conversation
document; identified directly from the diff and dated to this checkpoint by its necessity alongside the
TopKPattern refactor."* **That attribution of *why the bug was found* is now superseded by direct
documentary evidence, though the diff-level facts it was based on remain correct and unchanged.**

Quoted exactly from this document: "Fixing `CountedSearch` also surfaced a second, independently real
bug: `NESTED`'s guard against one AST node satisfying both sides of a nesting check compared node identity
(`outer_ev.node is not inner_ev.node`), which incorrectly evaluates false when BOTH sides are composite
Evidence (`node=None` by design) — rejecting two genuinely different composites the first time strict
layering produced a `NESTED` check between two composites at once." The canonical bug table entry (#18,
quoted in full below) says the same thing in table form: **"CountedSearch's score dropped to 0
immediately after restructuring it to fix a layering violation"** is the symptom that surfaced this bug —
not `TopKPattern`.

**What this means concretely, stated precisely so nothing is silently overwritten:**
- The **diff evidence still stands**: the fix (`outer_ev is not inner_ev`) is genuinely present in
  `files_Fix_Q4`'s `competency.py`, and it is genuinely necessary for `TopKPattern`'s own
  `NESTED("loop","remove")` check to work once `loop`/`remove` are both `LoopStep2`/`RemovalAssignStep`
  composites — that mechanical claim was never in doubt and isn't being retracted.
- What's corrected is the **motivating discovery case**: this log's own inference guessed the bug was
  found *via* the `TopKPattern` refactor itself, because that's the checkpoint where the fixed code first
  appeared in a supplied file. The new documentary evidence states plainly that the bug was actually first
  surfaced by **`CountedSearch`'s restructuring** (part of `files_Enforcement`'s "three of the four
  violations fixed outright" work — `CountedSearch`'s own lifted-siblings code is still not itself present
  in any supplied artifact, only referenced), and the already-fixed `NESTED` guard was simply *reused*,
  not independently rediscovered, when `TopKPattern` was refactored one checkpoint later at `files_Fix_Q4`.
  This is consistent with (not contradicted by) the diff evidence — `CountedSearch`'s restructuring
  chronologically precedes `files_Fix_Q4` within the same 2026-07-28 day, per `files_Enforcement`'s own
  section above.

### Bug #19 — `BubbleSortPass`'s resolver-caching obstacle, now fully canonical (resolves a "named but not yet evidenced" item)

Quoted exactly: "Attempting the same layering fix on `BubbleSortPass` produced a competency that scored 0
on a textbook-correct submission | Its outer and inner slots both needed the same wrapped-primitive
competency (`LoopStep2`); once registered, that competency resolves ONCE and both slots end up bound to
the literal same loop instance, which the bug #18 fix then correctly rejects as degenerate self-nesting |
Not fixed — correctly identified as needing a resolver change (independent per-slot search when one
sub-competency type fills multiple sibling slots), not another lifting wrapper; left as the one remaining
documented exception rather than risk the core matching loop for zero correctness gain."

This is the same mechanism `To_copy_to_new_project.docx` described in less detail (logged above as "named
but not yet evidenced"), now given a full numbered symptom/root-cause/fix entry, an explicit "attempted
and reverted once already" framing (elsewhere in this document: "a change to the resolver's core matching
loop... attempted and reverted once already (§2.12, bug #19)"), and independent confirmation in
`Structural_Competency_Extraction_Paper.docx`'s own Table 4 ("Shared-slot resolution | ... | Not fixed —
identified as requiring a resolver change... left as a single documented exception via
`allow_mixed_levels`"). **This item is now fully evidenced and removed from "named but not yet
evidenced."**

### The 19-entry canonical bug table (bugs #14-19 new) — full text of the new entries

Bugs #1-#13 are already logged verbatim above (`Competency_Extraction_Methodology_V24.docx`'s Table 5).
This document extends the same table to 19 entries; #14-19 quoted in full for the first time:

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| 14 | `ConditionalCount` scored 1.0 on a Question 2 submission using an entirely different (tuple-accumulate) strategy | Whole-file resolution matched a guarded accumulation pattern inside a DIFFERENT function (`contains_unique_day`) instead of the function actually being checked (`unique_day`) | Same root cause and same fix as bug #13, confirming function-scoped resolution as a general requirement, not a one-off |
| 15 | A batch coverage check appeared to show 0% for a competency that was independently verified working | The diagnostic script's own row values were floats, compared against the string `'1.0'` — always unequal regardless of actual value | Corrected the comparison in the diagnostic script itself; not a defect in the model |
| 16 | A newly built functional-strategy competency (`map()`/`filter()` detection) was silently never used | Two competing definitions of `UniqueCheck` were registered under the same id in the same file; the second, referencing a misspelled competency id, silently overwrote the first (`register()` has no duplicate-id warning) | Removed the redundant first attempt; kept the more precise second one after verifying it independently |
| 17 | `register()`'s new layering-enforcement check could reject a competency but still leave it stored in the model | The violating `Competency` was added to `self.definitions` BEFORE the validity check ran | Compute child levels directly from the `Competency` object being registered, before it is stored |
| 18 | `CountedSearch`'s score dropped to 0 immediately after restructuring it to fix a layering violation | `NESTED`'s same-node guard (`outer_ev.node is not inner_ev.node`) evaluates false when BOTH sides are composite Evidence (`node=None` by design), incorrectly rejecting two genuinely different composites | Only compare node identity when both sides are real, non-`None` primitive nodes |
| 19 | Attempting the same layering fix on `BubbleSortPass` produced a competency scoring 0 on a textbook-correct submission | Both slots needed the same wrapped-primitive competency (`LoopStep2`), which resolves ONCE and gets shared, so both slots bind to the literal same loop instance | Not fixed — needs a resolver change; left as the one remaining documented exception |

Bug #16 (duplicate registration) and the diagnostic-script float/string bug (#15) directly match, and now
give full numbered detail to, the two items this log previously recorded from `To_copy_to_new_project
.docx` as "named but not yet evidenced." Bug #17 similarly gives full detail to that document's third such
item ("layering-violation check stored the violator before rejecting it"), which this log had already
partly corroborated by inference at the `files_Enforcement` checkpoint (see that section above) — now the
canonical symptom/root-cause/fix text exists for all three. **All three "named but not yet evidenced"
items from `To_copy_to_new_project.docx` are now fully evidenced (#15, #16, #17) and are removed from that
status below.**

### `Structural_Competency_Extraction_Paper.docx` — the finished paper, read in full (95 paragraphs, 4 tables)

This is a complete, polished paper draft (Title/Abstract/Introduction/Related Work/Model/Validation
Methodology/Results §5.1-5.6/Discussion/Limitations/Conclusion/References), not a conversation export or a code
checkpoint. It is **the single most comprehensive document supplied to this log so far** — more complete
than either "V24" or the 28/07 methodology note, because it is the only document that combines Case Study
4 (Q1/Q2, from the methodology note) *and* a **new Case Study 5** covering Q3/Q4 batch results, which the
28/07 methodology note (confirmed by an exhaustive grep sweep across its full text for "SortByKey",
"77.6", "13.1", "64.4", "93.6", "94.0", "insert", "sort_age", "remove_extras", "Q3", "Q4" — every term,
zero matches) **does not contain at all.**

**This resolves the puzzle flagged earlier this round** (the 28/07 methodology note's total silence on
Q3/Q4 despite being dated the same day as `Q3_Q4_Results_28.docx`): Q3/Q4's batch results were folded into
a *separate* document — this finished paper's own §5.5 — rather than into "the methodology doc" as
referenced by that name. §5.5 ("Case Study 5: Extending batch validation to Q3 and Q4"), quoted precisely
where it matters:

- **Q3** (`remove_extras`): "`SelectionStep`... scored 1.0 on 93.6% of real Q3 submissions at function
  scope. Sampling the remaining 6.4% (35 files) showed genuine long-tail diversity: a list comprehension,
  a ternary-guarded assignment, an `.insert()`-based variant, and a recursive delegate-based strategy...
  Only the `.insert()` case was fixed... This raised coverage to 94.0%." — an exact match to every Q3
  figure already logged from `Q3_Q4_Results_28.docx` and `files_Fix_Q4`, now with the corpus denominator
  made explicit for the first time (**546 correct submissions**, per Table 3 — 93.6% of 546 ≈ 511, 94.0%
  of 546 ≈ 513, consistent).
- **Q4** (`sort_age`): "Batch validation at full scale (**419 correct submissions**) found `BubbleSortPass`
  alone covers only 13.1%... TopKPattern... 64.4%... `SortByKey = ANY(BubbleSortPass, TopKPattern)`...
  raising combined coverage from 13.1% to 77.6%... The remaining 22.4% is genuinely different territory —
  recursive partition-based sorting and an explicit quicksort delegate." — an exact match to every Q4
  figure already logged from `Q3_Q4_Results_28.docx` and `files_Fix_Q4`'s own code comment.

**No new code or CSV accompanies this — the Q3/Q4 figures remain narrative-only across every source that
states them (`Q3_Q4_Results_28.docx`, `files_Fix_Q4`'s comment, and now this paper) — but this is now the
third independent document stating the identical numbers, the strongest corroboration these figures have
had.**

**Other content cross-checked, all consistent, no contradictions found:**
- **Table 3** (corpus composition): Q1 768/575, Q2 291/435, Q3 546/308, Q4 419/357, Q5 418/108 — exact
  match to every corpus total already logged in this doc from multiple independent sources.
- **Table 1** (12 primitives) and **Table 2** (13 structural constraints, `AND`/`OR` counted as one row) —
  exact match to `To_copy_to_new_project.docx`'s counts (12 primitives; "13 entries, including `HAS_ELSE`
  and `DISTINCT_BINDINGS`") and to the fully-diffed, post-`files_Fix_Q4` state of `competency.py`
  (`ASSIGN`'s description explicitly includes `.insert()` in this table — confirming this paper's own
  primitive table reflects the *post*-Q3-fix framework state, unlike V24's table, which stopped at
  `.append()/.add()/.pop()/.remove()`).
- **§5.3 (Case Study 3)**: reports the original, unrefined 83.0%→78.2% / 76.9%→75.0% correction — does
  **not** carry forward the 82.1% unscoped-after-refactor refinement that only the 28/07 methodology note
  states (see above) — the two documents simply differ in depth here, not in conflict.
- **§5.6 / Table 4** (14 grouped defect categories): a categorized grouping of the same defects, not a
  second independent numbering — its prose explicitly says "Table 4 groups the **nineteen** structural
  defects found during development... by recurring root cause," and its own "Identity comparison on
  composites" and "Shared-slot resolution" category rows describe bugs #18 and #19 in language consistent
  with (though less detailed than) the 28/07 methodology note's numbered entries — no contradiction.
- The paper's own **Abstract and Limitations (§7)** explicitly and repeatedly defer all semantic-backup
  evaluation to **"a companion paper"**: "All results in this paper concern the structural, AST-only
  layer" / "a semantic-similarity backup signal... is architecturally integrated but was not empirically
  validated in the environment used for this work, and its evaluation... is deliberately deferred to a
  companion paper rather than reported alongside results that are validated at real scale." This means the
  previously-flagged pending item — "the embedding-based validation (Table 5 of the paper — 10 train/test
  splits, codet5p) and the semantic backup layer's lexical-vs-codet5p comparison" — refers to a **still
  entirely separate, still-unsupplied "companion paper"**, distinct from both this finished structural
  paper and the `semantic_backup.py`/`semantic_20_07.docx` stub-backend work logged above. Restated more
  precisely in "Still-pending items" below.

**One open question this document raises rather than resolves:** it was initially hypothesized (in the
prior round of this log) that `Structural_Competency_Extraction_Paper.docx` might be the older, separate
"article" document (`Competency_Extraction_Article.docx`-equivalent) flagged as unsupplied — `Summaize_to
_move_the_project_28.docx` had described that article as predating enforcement, the `NESTED` bug, and all
of Q1-Q4. **That hypothesis is now disproven**: this document contains bug #18/#19 (the `NESTED` bug and
its aftermath), full Q1-Q4 Case Studies, and the complete 19-defect account — it cannot be the
pre-enforcement, pre-Q1-Q4 article Sonia described. It is, if anything, the newest and most complete
single document supplied to this log so far. **`Competency_Extraction_Article.docx` itself remains
entirely unsupplied and unidentified** — this document is not it.

### Bug-count accounting: a small, precise, unresolved discrepancy worth flagging rather than smoothing over

The 28/07 methodology note's canonical table numbers exactly 19 bugs (#1-19), of which **one (#15) is
explicitly self-described in its own "Fix" column as "not a defect in the model."** The finished paper's
own §5.6 states: "Table 4 groups the **nineteen** structural defects found during development (**a
further two informational script bugs, not defects in the model, are omitted**)." Read literally, this
implies the paper's own accounting is **19 structural + 2 informational = 21 total findings**, with only
the 19 structural ones appearing in its Table 4 — but the 28/07 methodology note's own numbered table
tops out at 19 total, and already includes at least one entry (#15) that is itself explicitly informational
rather than structural. If the paper's "two informational script bugs" are meant to include bug #15, then
its own "nineteen structural defects" figure and the methodology note's "19" total cannot both be counting
the same 19 items on a like-for-like basis. No document identifies what the *second* informational bug
would be. **Flagged here as an open, unresolved small inconsistency in how the two documents' "19" figures
are being counted — not resolved by guessing which bug is the second "informational" one.**

---

## `Competency_Extraction_Article.docx` — the long-hypothesized older article, now supplied and read in full

Sonia supplied this document with only "here is a version of the article" — no accompanying conversation export,
no explicit date. This is the document `Summaize_to_move_the_project_28.docx` (logged above) described,
in Sonia's own 28/07/2026 words, as "the separate standalone article... more out of date than the
methodology doc — it predates enforcement, the NESTED bug, and all of Q1–Q4 entirely." **That description
is now directly, textually confirmed, not just taken on trust:**

- **§7 Limitations states plainly:** "Strict level-2 layering (Section 2.8) is documented as a design
  convention, **not enforced in code**; four of the competencies built so far mix a primitive directly
  alongside a higher-level competency as siblings" — the pre-`files_Enforcement` state (4 violators:
  `TopKPattern`, `BubbleSortPass`, `CountedSearch`, `Average`, matching every other source), with no
  mention anywhere in the document of `allow_mixed_levels`, `LayeringViolation`, or `check_layering()`.
- **The Abstract states "Thirteen concrete bugs were found and fixed"** — matching
  `Competency_Extraction_Methodology_V24.docx`'s canonical 13-entry bug table exactly, not the 19-entry
  table the 28/07 methodology note and `Structural_Competency_Extraction_Paper.docx` both report. No bug
  is referenced by number anywhere in this document (it names mechanisms in Section 5's design lessons,
  not a numbered table), but the total count matches V24's era precisely.
- **No mention anywhere of `LinearSearch`, `SortByKey`, `q1_competencies`, `.insert()`, Q1/Q2/Q3/Q4 by
  number, or any of the 85.2%/0.7%/4.5%/90.4% (Q2), 93.6%/94.0% (Q3), or 13.1%/64.4%/77.6% (Q4) figures**
  — checked directly by full-text reading, not omission alone. Exercises are named descriptively
  ("sequential search," "occurrence counting," "duplicate elimination," "sort by key (selection / bubble
  sort)," "repeated extremum extraction") rather than by Refactory question number, and Table 1's own
  exercise-count row for the fourth exercise, "Sort by key (selection / bubble sort) | 419 | 357," is
  itself evidence the author had not yet arrived at the eventual `SortByKey = ANY(BubbleSortPass,
  TopKPattern)` taxonomy correction — it's still framed as "selection / bubble sort," not yet naming the
  dominant real strategy (repeated extremum extraction transferred from Q5) that batch validation would
  later reveal accounts for 64.4% of real submissions.
- **§2.6/§2.7 (cross-function composition via `DELEGATES`, function-scoped resolution) and §4.3 (the
  526-submission batch run, 83.0%→78.2%/76.9%→75.0%) are all present** — confirming this document postdates
  `V1.2.0` (2026-07-19→21) and the reporting/batch-tooling checkpoint, and §6 discusses the semantic-backup
  extension as already built (consistent with the 2026-07-20 `semantic_backup.py`/`semantic_20_07.docx`
  work logged above) — so this document's real date is now boundable on both sides by direct textual
  evidence, not just Sonia's own later description: **after 2026-07-20/21, before 2026-07-28.** This is
  the same ~21/07 window `Competency_Extraction_Methodology_V24.docx` and `Levels_of_competencies_21_07
  .docx` occupy — consistent with `Summaize_to_move_the_project_28.docx`'s framing of "the article" and
  "the methodology doc" as two documents being maintained together, both from that same era, before either
  was updated with 28/07's work.
- **Table 3's corpus counts** (768/575, 291/435, 546/308, 419/357, 418/108) are an exact match to every
  other source's Refactory totals logged in this doc.
- **§4.1's 30% built-in-reduction figure** for top-k matches exactly.

**This resolves the "`Competency_Extraction_Article.docx` — not yet supplied" item** that has been open
since the first four-document contradiction-check round of this log.

### A sharper reading of the "33%" inconsistency, now with three data points instead of two

The 28/07 methodology note's §3.2/§6.2 self-contradiction was flagged above (two passages in the same
document describing the stale Q2 "33%" estimate oppositely: one calling it the counter strategy's share,
the other calling it "the alternative strategy"'s share), and it was tentatively read as resolved in favor
of the counter-strategy phrasing, because `Structural_Competency_Extraction_Paper.docx`'s finished prose
matched that reading. **This article changes that picture — it is independent, older evidence, and it
sides with the *other* phrasing.** Quoted exactly from §4.1: "33% of correct occurrence-counting
submissions (95 of 291) use **an alternative accumulate-then-count strategy rather than an explicit
counter**" — i.e., 33% is described here as the share using the non-counter, alternative strategy, the
same reading as the 28/07 note's §6.2 ("an initial estimate that 33% of correct submissions used 'the
alternative strategy'"), not the reading in that same note's §3.2 or the finished paper's §5.1 (both of
which describe 33% as the counter-strategy's share).

Restated as a tally, since this is now a three-document, four-passage question: this article (oldest,
predates Q1-Q4 entirely) and the 28/07 note's own §6.2 agree that 33% meant "the alternative strategy";
the 28/07 note's own §3.2 and the finished paper's §5.1 agree that 33% meant "an explicit counter." **Given
that this article is now confirmed, by direct textual dating evidence, to be the oldest of the four
passages — closer to whenever the original 33% estimate was first produced — the "alternative strategy"
reading now has the stronger claim to being what was actually meant originally, reversing the tentative
lean recorded earlier in this log.** This is still not being resolved by assumption: both readings remain
directly quoted and attributed above and here, exactly as found, precisely because the corrected 85.2%/
0.7%/4.5%/90.4% breakdown they were both gesturing at imprecisely makes the original 33% figure moot for
any actual result now being reported — this is a historical-accuracy question about four passages across
three documents, not a live discrepancy affecting any number this log currently relies on.

---

## Real-CodeBERT/CodeT5+ Colab validation of the semantic backup layer — `semantic_29.docx` + two notebooks

Sonia supplied a conversation-history export and "the 2 versions of the first notebooks," introduced only as
"here is a conversation about the semantic-similarity backup... This work will be continued with other versions"
— i.e. explicitly not a finished result, an open thread.

**Source artifacts:**
- `semantic_29.docx` — a conversation export. Read via `pandoc` (unlike `Competency_Extraction_Methodology.docx`,
  this one is a genuine `.docx`, not mislabeled Markdown). 557 lines of plain text, spanning five numbered
  prompts on **29/07/2026**, then a sixth exchange explicitly labeled by Sonia's own words "File= 'Semantic
  backup validation.IPYNB' from 30/07," then a closing prompt dated **31/07/2026**.
- `semantic_backup_validation.ipynb` (18 cells, no date of its own — dated by content-matching below).
- `semantic_backup_validation_30.ipynb` (19 cells, no date of its own — dated by content-matching below).

Both notebooks are **companion validation harnesses for the still-unsupplied "companion paper"** already
flagged in "Still-pending items" (the embedding-based Table 5 work `Structural_Competency_Extraction_
Paper.docx`'s own Abstract/Limitations defer entirely) — this is the first real evidence toward that item,
though, as detailed below, **no real similarity/AUC number has actually been produced by either notebook
in any form supplied so far.** Everything here is either directly-executed code (the notebooks themselves)
or conversation-quoted output Sonia pasted back into the conversation — nothing is inferred.

### Dating the two notebooks against the conversation, by content match, not filename alone

**`semantic_backup_validation.ipynb` (no suffix) = the artifact built in direct response to Prompt 2**
("I want to create a project in colab to implement and use embeddings"). Confirmed by structural match to
the conversation's own description of what it built: raw `microsoft/codebert-base`; a Drive-mount cell present but
commented out ("Optional: mount Google Drive instead of re-uploading every session"), matching "if you'd
rather not re-upload each session, use the commented-out Drive-mount cell instead"; bare local paths in
cells 4/9/11/13 (`topk_report.csv`, `refactory/data/question_5/code/correct/*.py`) with no `PROJECT_DIR`
prefix, matching the conversation's own flagged caveat verbatim: "cells 4–6 have placeholder paths... you'll need
to point those at wherever your actual data lands." This is the **pre-Drive-mount-rework, pre-anisotropy-
discovery** state — i.e. earlier than Prompt 3 and Prompt 4 in the same conversation.

**`semantic_backup_validation_30.ipynb` = the "File... from 30/07" artifact.** Confirmed two ways: (1) it
has Drive-mounting as the *default* path (cell-3/cell-4, "Option A — Google Drive (persists across
sessions)... recommended"), matching Prompt 3's rework ("I updated the notebook so Drive-mounting is now
the primary path, not a commented-out afterthought"); (2) its cell-7/cell-8 already uses
`Salesforce/codet5p-110m-embedding` with the exact config-attribute-patching fix and the exact "an earlier
version of this notebook pinned an older transformers... dragged in an old tokenizers release with no
prebuilt wheel... requiring a Rust toolchain" caveat as a markdown cell (cell-1) — this exact sentence
appears nowhere in the conversation text itself, so the notebook file is independent, corroborating evidence for a
detail the conversation only alludes to indirectly ("Prompt 5" pins codet5p as the final choice, but the
Rust-toolchain/tokenizers detail is new information found only in the file). This places the file after
Prompt 5 (31/07 conversation marker not reached yet — Prompt 5 itself carries no explicit date, bounded only by
sitting between the 29/07 and 31/07 markers).

**A real gap: no supplied file matches the intermediate state that actually produced the anisotropy
numbers.** The conversation's Prompt 4 (raw-codebert anisotropy result, see below) fires *after* Prompt 3's
Drive-mount rework but *before* Prompt 5's codet5p swap — i.e. the notebook that was actually run to get
those numbers would have had Drive-mounting as default **and** raw `codebert-base` in its embedding cell.
Neither supplied file matches that description (the no-suffix file lacks the Drive default; the `_30` file
already has codet5p, not raw codebert-base). That specific intermediate notebook state exists only as
prose/quoted-output in the conversation, not as a file in hand — stated here explicitly rather than assumed to be
recoverable from either supplied notebook.

### Real, executed output: the anisotropy finding (29/07/2026, Prompt 4)

Quoted exactly, Sonia's own pasted cell output: **"related vs related: 0.9579190015792847, related vs
unrelated: 0.9641265273094177."** This is real, Colab-executed output — the first real embedding-model run
this project has ever produced (the sandboxed `semantic_backup.py`/`semantic_20_07.docx` work logged
above never got past a 403 network block). It is also a second, independently-obtained negative result,
for a *different* underlying reason than the sandbox's own `_stub_embed` result (0.77 vs. 0.79, "no
discriminative power" from a bag-of-AST-tokens signal): here, a real transformer model's own pooled
embeddings collapse into a narrow cone regardless of content — **anisotropy** — so unrelated code scores
*higher* than related code (0.964 vs. 0.958), not merely "similarly high."

**Citation trail, quoted from the conversation and independently corroborated by `semantic_backup_validation_30
.ipynb`'s own cell-7 markdown (near-identical wording, confirming the notebook and the conversation narrate the
same investigation, not two different ones):** anisotropy is "a well-documented property of BERT-family
models... reproduced directly by other users hitting this exact symptom with `codebert-base`" — cites
Ethayarajh (2019), Li et al. (2020), and a specific corroborating report, `microsoft/CodeBERT` GitHub
issue #13. `codebert-base`'s own pretraining objectives (masked-language-modeling, replaced-token-
detection) are named as the root cause: neither makes pooled-embedding cosine similarity meaningful on its
own. This diagnosis is real content (present verbatim in the notebook file's own markdown, not only in
the conversation), not a guess reconstructed after the fact.

### The interim jina recommendation — proposed, never run, dropped within the same session

Before landing on `codet5p-110m-embedding`, the conversation's response to the anisotropy finding first recommended
`jinaai/jina-embeddings-v2-base-code` as the fix ("Confirmed real option... purpose-built for code-to-code
similarity via sentence-transformers... 8192 token context"), with an *expected* (not measured) rough range
("something like related≈0.6–0.8 vs unrelated≈0.1–0.3, roughly — exact numbers will vary"). Sonia never
ran this version — the very next prompt in the same conversation asks about a CodeT5+-family prefix syntax
instead, and the swap to `codet5p-110m-embedding` happens before jina is ever executed. **No real jina
number exists in any supplied artifact.** Neither of the two supplied notebook files contains any jina
reference — consistent with the conversation's own closing confirmation that "no sentence-transformers, no jina
references left anywhere in the notebook."

### The codet5p-110m-embedding swap — real code, config-compatibility fix, no sanity-check number confirmed yet

**Confirmed by direct read of `semantic_backup_validation_30.ipynb`, cell-8** (matching the conversation's Prompt 5
exchange almost line-for-line): switches to `Salesforce/codet5p-110m-embedding`, using its official,
no-prefix `trust_remote_code=True` usage pattern (the earlier `<s> <encoder_only> </s>` prefix Sonia asked
about is confirmed inapplicable — that syntax belongs to CodeT5+'s general multi-mode checkpoints
(`codet5p-220m`/`770m`), not this dedicated embedding checkpoint). Output is pre-L2-normalized ("already
normalized: norm == 1.0" per the model card, quoted in the conversation and matching the notebook's own comment
`# already L2-normalized: norm == 1.0`), so `cosine_sim` collapses to a plain dot product in the notebook's
code.

**A real `transformers`-version compatibility bug and its fix, code-confirmed (cell-8's own comment,
quoted in full since it's the clearest primary-source account available):** "`codet5p-110m-embedding`'s
remote config code (written in 2023) never calls `super().__init__()`, so several base `PretrainedConfig`
attributes are never actually set on the instance. Older transformers tolerated this via class-level
defaults; recent transformers enforces attributes strictly and raises `AttributeError`." Fixed by loading
`AutoConfig` directly and patching four missing attributes onto it by hand (`is_decoder=False`,
`is_encoder_decoder=True`, `pad_token_id=0`, `eos_token_id=2`) before passing that config into
`AutoModel.from_pretrained(...)` — no version pin required. **An earlier, unsupplied notebook attempt at
the alternative fix (pinning an older `transformers`) is referenced but not itself supplied as a file** —
per cell-1's own markdown, that pin "turned out to drag in an old `tokenizers` release with no prebuilt
wheel for Colab's current Python, which fails to build from source without a Rust toolchain" — a real,
specific, code-documented dead end, not a vague aside.

**A citable real figure, sourced from the model's own card, not independently measured by Sonia's own
run:** "74.23% average retrieval accuracy across 6 languages (including Python) on CodeXGLUE code-search
benchmarks" — quoted identically in both the conversation and the notebook's cell-7 markdown. This is the model
publisher's reported benchmark figure, not a result this project has itself reproduced.

**No sanity-check similarity number for codet5p has been supplied anywhere.** Cell-8's own "related vs
related" / "related vs unrelated" print statements exist in the code, but neither the conversation nor either
notebook file contains an actual printed output for them — unlike the raw-codebert anisotropy numbers
above, which are real, pasted, executed output. Stated explicitly so this isn't conflated with a
confirmed result.

### The real exemplar-registry and test-set-construction methodology — distinct from the small stub registry already logged

Both notebooks build a **larger, mined exemplar registry** (`load_exemplars()`, 6 real correct submissions
per competency, pulled via `glob` from `refactory/data/question_{2,5}/code/correct/*.py`) — this is a
different, more thorough registry than the 2–3 hand-written snippets in `semantic_backup.py`'s own
`EXEMPLARS` dict (already logged under "Semantic backup layer" above, and still the only registry actually
reflected in this repo's `data/exemplar_registry/`). The design intent is stated directly in `semantic_29
.docx`'s Prompt 1: "Pull real reference exemplars straight from the Refactory `correct/` folders you
already have (a handful of diverse correct submissions per competency, not just one canonical style) —
that's a much more honest test of whether the model generalizes."

**The test-set construction (both notebooks' cell 11/cell-12, identical logic), confirmed by direct read:**
filters the real `topk_report.csv` batch report for two groups against `FindExtremum` — "novel-correct"
(`label == "correct"` and `FindExtremum_final == 0`: test-suite-correct submissions the structural detector
scored 0 on, i.e. genuinely novel strategies like `functools.reduce`-based extremum finding) and
"genuinely-wrong" (`label == "wrong"` and `FindExtremum_final == 0`, the *original* filter, unmodified in
either supplied file).

**Real, executed counts (conversation-quoted, matching what the unmodified `_30` notebook's own cell-12 code would
produce against the real `topk_report.csv`):** novel-correct = **43**, genuinely-wrong = **5**. The conversation
immediately flags `n=5` as too small for a meaningful ROC/AUC and proposes a fix (see below) — this
exchange is what dates this run to *after* the `_30` notebook file's codet5p swap (Drive-mounted, codet5p
embeddings) but strictly *before* any of the hand-edits discussed next, since the supplied `_30` file's
cell-12 still has the unmodified two-group filter that produces exactly this 43/5 split.

### The hand-edited fixes — conversation-quoted only, NOT present in either supplied notebook file

Sonia explicitly asked for the fix as text to apply herself ("give me the content of the fix, so I can
change the notebook by hand"), rather than a re-uploaded file — so everything from here on is conversation-quoted
output describing edits made to Sonia's own local copy, not verifiable against a supplied artifact.

1. **"Option 1"**: broaden the `genuinely_wrong` filter to every `label == "wrong"` row, dropping the
   `FindExtremum_final == 0` constraint — rationale quoted: "you're not testing 'wrong submissions that
   also miss this specific competency,' you're testing 'does similarity meaningfully separate
   genuinely-novel-correct code from genuinely-incorrect code.'" Sonia reports running it: **genuinely-wrong
   count becomes 108** — an exact match to the 108 wrong-labeled Q5 submissions already established in this
   log from `topk_report.csv` (418 correct + 108 wrong = 526), a strong, independent cross-check that this
   conversation exchange genuinely describes a real run against the real data, even though no file captures the
   edited cell itself.
2. **Real, conversation-quoted `cell 6` output after Option 1**, using codet5p similarity against the broadened
   groups: **novel-correct: mean=0.851 std=0.086 n=43; genuinely-wrong: mean=0.930 std=0.027 n=108.**
3. **A real, self-diagnosed contamination problem with this result**, flagged by the conversation before any AUC
   was computed: the broadened "wrong" group is dominated by submissions that structurally implement
   `FindExtremum` correctly and fail the test suite elsewhere — per this project's own already-established
   finding (§5.3 of the finished paper, already logged above: most wrong-labeled submissions still score
   1.0 structurally) — so the comparison silently became "unusual-but-correct vs. textbook-correct-but-
   fails-elsewhere" rather than "novel-correct vs. actually-wrong," which plausibly explains why the
   "wrong" group's mean (0.930) came out *higher* than the "correct" group's (0.851) — backwards from what
   the layer is supposed to show.
4. **A second proposed fix, given as cell-5 code to hand-apply, never confirmed as applied or run**: pull
   true negatives from a *different* Refactory exercise entirely (Q1 or Q3 — "none of them are attempting
   to find an extremum at all"), reading a second CSV (`question_1_report.csv`, named as an example, not
   confirmed to exist as a real file). The conversation ends this thread with "Let me know once you have n for both
   groups and we'll move to cell 6" — **open, unresolved, no further response in the supplied document.**

**No AUC or ROC number has been produced by either notebook, in any form supplied to this log.** The
threshold-sweep code (cell 15/16) exists and is real, but was never reached with a valid two-group
comparison before the conversation thread ends — the 43-vs-5 split was too small to trust, and the 43-vs-108 split
was flagged as contaminated before cell 7 was run. This is stated plainly because it would be easy to
over-read "cell 7's ROC sweep exists in the code" as "an AUC was computed" — it was not.

### 31/07/2026 — a requested summary document, outline only, not itself supplied

The conversation closes with a different request: "can you summarize in a clear document what's the role of this
semantic backup, and what is the relation with the first part with AST." The response describes a
seven-part outline (AST layer's one limitation; what the semantic layer is for; the `final_score`-isolation
rule; a side-by-side comparison table; why the semantic layer isn't in the published structural paper; a
status summary of exactly the Colab work above, including "the contaminated-comparison-group issue we just
caught and are fixing"; a one-sentence thesis statement) and offers to produce it as a `.docx`. **The
resulting document itself, if produced, has not been supplied to this log** — only the conversation's own outline
of what it would contain.

### What this means for `configs/stage_manifest.yaml`'s `table5.semantic_backup` block

Two things are now real and code/conversation-confirmed that were not before: (1) a real, executed, Colab
raw-codebert-base anisotropy result (0.9579/0.9641) — a second negative result, independent of the sandbox
stub's 0.77/0.79 finding, and for a structurally different reason; (2) real code (with a real, documented
`transformers`-compatibility fix) for a `codet5p-110m-embedding` backend, plus a real exemplar-registry-
building and test-set-construction methodology — but **no real similarity or AUC number for codet5p itself
has been supplied**, and the one real similarity comparison that was run under it (43 vs. 108, post-"Option
1") is explicitly self-flagged as contaminated, not a usable result. `q4_sortbykey_splits`/`q5_topk_splits`
(the "10 train/test splits" embedding experiments named in the project's own reproducibility scope) are
**not** the same experiment as this exemplar-similarity-threshold validation — nothing here should be read
as resolving those two still-entirely-unsupplied items.

---

## AST taxonomy cross-validation via embeddings — `ast_taxonomy_crossvalidation.ipynb` + real results CSV + `Steps for semantic_backup.docx`

Sonia supplied a conversation export, a standalone notebook, and its real output CSV together, introduced as
"here the independent external check on the AST taxonomy itself, using a pretrained embedding model as a
validation tool" — her own words, quoted directly from the conversation inside `Steps for semantic_backup.docx`,
describing exactly what this batch is (not a semantic-backup-layer validation, a *taxonomy* validation).

**Source artifacts:**
- `Steps for semantic_backup.docx` — a conversation export, read via `pandoc`. Spans **31/07/2026** (14:50 through
  16:30+) through **04/08/2026**. Its own leading line is odd and logged as-is, not interpreted: "31/07/2026
  (Summarize from Pro in Gey PC)".
- `ast_taxonomy_crossvalidation.ipynb` (21 cells, self-contained — "doesn't depend on the other one being
  open first," per the conversation).
- `ast_taxonomy_crossvalidation_results.csv` (158 data rows) — real output, not a placeholder.

### This resolves a previously-open pending item: the 31/07 "summary document" now exists

This log's prior entry ("31/07/2026 — a requested summary document, outline only, not itself supplied")
noted that a seven-part summary of the semantic layer's role, requested at the end of the previous
notebook-conversation round, had only been described as an outline, never supplied as a document. **§1-7 of this
docx's opening section (14:50, 31/07/2026) is that document.** It matches the previously-logged outline
exactly, point for point: (1) the AST layer's one named limitation, with the same `functools.reduce`
example already in this log; (2) what the semantic layer is for; (3) the `final_score`-isolation design
rule, quoted near-identically to `semantic_backup.py`'s own docstring; (4) a side-by-side comparison table
(Input/Output/Basis/Determinism/Inspectability/Role/Validated?); (5) why the semantic layer isn't in the
published structural paper (scope discipline + genuinely not validated yet at the time); (6) a status
summary of the Colab validation work already logged in this doc's "Real-CodeBERT/CodeT5+ Colab validation"
section — including, verbatim, "the contaminated-comparison-group issue we just caught and are fixing,"
confirming this is the same thread continuing, not a new one; (7) the one-sentence thesis statement. No
new facts here — full corroboration of everything already logged, now from a primary-source document
rather than an outline. **This pending item is resolved and removed below.**

### A new, distinct experiment: does semantic similarity independently confirm the AST taxonomy's own categories?

At 15:50 (31/07), Sonia asked a different question from anything logged before: not "can embeddings catch
novel-but-correct submissions the AST rules miss" (the semantic-backup-layer's own validation question,
already logged), but "does an independent embedding-based method agree with the AST taxonomy's *existing*,
already-published `SelectionStep`/`FindExtremum` manual-vs-builtin split, as a check on the taxonomy
itself?" The design went through two iterations in the conversation, confirmed by direct comparison against the
supplied notebook's own code:

1. **First proposal (15:50, not what shipped):** hand-picked `N_EXEMPLARS=8` per class, held out, rest
   classified by nearest exemplar centroid. **This version is not in the supplied notebook.**
2. **Revised design (16:30, matches the supplied notebook exactly):** the same three structural labels
   (`manual`/`builtin`/`novel`, via a `structural_label(row, threshold=0.99)` function reading
   `SelectionStep_final`/`FindExtremum_final` from `topk_report.csv`), but built from a proper 70/30
   split — one centroid per label from the training 70%, the held-out 30% classified blind to the
   structural label, purely by nearest centroid in embedding space. **Confirmed by direct code comparison:
   the docx's 16:30 code block and `ast_taxonomy_crossvalidation.ipynb`'s cells 8-16 match line for line**
   (same `structural_label` function, same `SHUFFLE_BEFORE_SPLIT` flag defaulting to `False`, same
   centroid-building and classification logic) — strong confirmation the notebook is a direct, faithful
   packaging of this exact conversation exchange, not a separately-drifted artifact.

### Real, executed results — independently recomputed from the raw CSV, not just taken on the conversation's word

This is the most rigorously cross-checked result in this entire log: the conversation-quoted numbers, the
notebook's own code, and the raw supplied CSV all agree, and this session **recomputed every figure
directly from `ast_taxonomy_crossvalidation_results.csv`** (158 rows) rather than trusting any one source
alone.

**Label distribution (conversation-quoted, and matching the CSV's row count exactly):** across the full labeled
Q5 corpus, `manual`=327, `builtin`=151, `novel`=48, `partial`=0 — sums to 526, the full Q5 corpus (418
correct + 108 wrong), confirming the `0.99` threshold cleanly separates every submission with no
in-between cases. **`novel`=48 is itself a real cross-check against two independently-logged prior
figures**: 43 novel-correct (from the semantic-backup-validation notebook, already logged) + 5
novel-wrong (the original, unbroadened `genuinely_wrong` count from that same earlier round, also already
logged) = 48 exactly.

**Train/test split (conversation-quoted; test-side independently reconfirmed by this session against the raw
CSV):** train manual=230/builtin=101/novel=37 (368 total); test manual=97/builtin=50/novel=11 (158 total).
**Directly recomputed from the supplied CSV this session: label counts are manual=97, builtin=50,
novel=11 — an exact match**, confirming the 158-row CSV is genuinely this experiment's real test-set
output, not a different or partial run.

**Confusion matrix and accuracy (conversation-quoted; independently recomputed by this session from the raw CSV
to full floating-point precision):**

| structural \\ predicted | manual | builtin | novel |
|---|---|---|---|
| manual (n=97) | 83 | 14 | 0 |
| builtin (n=50) | 2 | 48 | 0 |
| novel (n=11) | 5 | 1 | 5 |

- Overall 3-way accuracy: **0.8607594936708861** (136/158) — recomputed by this session, matches the
  conversation's quoted `0.8607594936708861` to all 16 digits.
- **Manual/builtin-only accuracy: 0.8911564625850340 (89.1%, n=147)** — recomputed by this session; this
  is the figure Sonia and the conversation settled on as the one to report, and the one that reportedly went into
  the paper's new §5.5 (see below).
- Novel recall: **0.45454545454545453** (5/11) — recomputed by this session, matches "recall 0.45" quoted
  in the conversation.

Precision/recall breakdown, quoted from the conversation's own `classification_report` output (not independently
recomputed beyond the confusion-matrix-level figures above, which fully determine it): manual
precision=0.92/recall=0.86, builtin precision=0.76/recall=0.96, novel precision=1.00/recall=0.45.

**The novel-centroid tightness diagnostic (cell 9), conversation-quoted and spot-checked against the raw CSV:**
`sim_novel` mean=0.772, std=0.028 across the 11 novel test submissions — a *tight* spread, ruling out the
initially-expected explanation ("novel is a scattered grab-bag of unrelated strategies"). **A specific,
real, verifiable finding: `correct_5_389.py` and `correct_5_391.py` have byte-identical similarity values
across all three centroids** (`sim_manual=0.6784468293190002`, `sim_builtin=0.6516886949539185`,
`sim_novel=0.7658414244651794` in both the conversation's quoted table and the raw CSV, confirmed by this session)
— strong evidence of near-identical or duplicate source code between two real student submissions, flagged
in the conversation as worth a manual diff but not chased further.

**The actual finding, reasoned out in the conversation from the real numbers above:** novel's low recall is not
because the embedding model fails to represent novel code, and not because `novel` is an incoherent
grab-bag (the tight std rules that out) — it's a magnitude effect. When a submission's similarity to
*every* centroid is uniformly depressed (both `sim_manual` and `sim_builtin` collapse into the 0.65-0.70
range), `novel` wins the argmax by default; when a submission's similarity to the *other* two centroids
stays high even though `sim_novel` is also fairly high, one of those two wins instead, absorbing a
genuinely-novel submission into the wrong bucket. Practical conclusion, stated in the conversation: nearest-centroid
argmax is the wrong decision rule for *detecting* novelty specifically — an anomaly-style threshold rule
(flag when similarity to every known centroid drops low, regardless of which one is nearest) is a better
fit for the semantic-backup layer's actual "flag for review" use case. This is real analysis of real,
verified numbers, not speculation.

### What went into the actual paper — and what stayed out, by deliberate scope decision

Sonia and the conversation treated the two findings differently, and the reasoning is real and worth preserving
precisely:

- **The manual/builtin 89.1% agreement result was judged in-scope for the published AST paper itself**
  (`Structural_Competency_Extraction_Paper.docx`) — reasoning quoted: "an independent external check on the
  AST taxonomy itself, using a pretrained embedding model as a validation tool, not as the thing being
  evaluated... legitimately in-scope... using a method that happens to involve embeddings incidentally."
  Per the conversation, this was actually inserted as a new subsection, **§5.5, "External validation of a taxonomic
  split via code embeddings,"** placed "right after §5.4 (taxonomy completion)" — reporting only the
  confusion matrix, the 89.1% figure (stated as such in the conversation's own summary, distinct from the 86.1%
  3-way figure), and the asymmetric-error observation (14 manual submissions misclassified as builtin vs.
  only 2 the other way). A real citation was added — **Wang et al. (2023), the CodeT5+ paper (EMNLP
  2023)** — since the embedding model is now a substantive part of the AST paper's own reported results,
  not just background tooling. The Abstract was updated with one sentence. Per the conversation: "Done — 20 pages
  now" (up from the 95-paragraph/4-table version already logged in this doc).
- **The novel/recall-0.45/anomaly-detection story was deliberately excluded from the AST paper**, with
  explicit reasoning quoted in full because it's a genuine, documented editorial judgment call, not an
  omission: it's an *open* research question (why nearest-centroid gives weak recall, the magnitude-effect
  finding, an untried threshold-based fix) rather than a *closed* check, its own evidence is thin (n=11,
  one unshuffled split), and including it "would substantively preview the companion paper's main
  contribution before that paper has even validated the fix." Sonia agreed; the sole change made to the
  AST paper for this finding was one forward-pointing sentence proposed for §7 Limitations: "A preliminary
  check using the same embedding model to attempt automatic novel-strategy detection, rather than
  validation of an existing split, is reported in the companion paper; early results suggest this is a
  harder problem than the manual/builtin check above, requiring a different decision rule than
  nearest-centroid classification." **Whether this exact sentence was actually inserted is not confirmed
  by any code/diff evidence** — only proposed and apparently accepted in the conversation's flow ("Add a sentence"
  is Sonia's own instruction immediately following the proposal).

**Important: the resulting updated `Structural_Competency_Extraction_Paper.docx` (the "20 pages now"
version, with the new §5.5, the Wang et al. citation, and the renumbered sections) has NOT itself been
supplied to this log.** Everything above about what changed in the paper is conversation-described, not
diff-confirmed against an actual updated file. **A section-numbering detail is flagged, not resolved,
rather than guessed past:** this round's conversation states the new subsection was inserted "between 5.4 and 5.5"
and that defects/Table 4 is "now 5.6" — but this log's own prior direct reading of the previously-supplied
`Structural_Competency_Extraction_Paper.docx` recorded Case Study 5 (Q3/Q4 batch results) at §5.5 and
Table 4/defects at §5.6 already, before this round's edit. If Case Study 5 was already at §5.5 before this
edit, inserting new content "between 5.4 and 5.5" and shifting everything after it by one would put Table
4/defects at §5.7, not §5.6 as this round's conversation states. This may simply be loose paraphrasing in the
conversation's own summary rather than a real inconsistency, but it cannot be resolved without the actual updated
document — flagged here explicitly rather than assumed away.

### A real, executed alternate split (04/08/2026) — the 89.1% figure is shown, with real data, not to be stable

Sonia separately supplied a standalone document, `multi-seed loop.docx` (277-line conversation export, own leading
date marker "04/08/2026"), that turns out to be the fuller, primary-source version of the same 04/08/2026
exchange this log had previously summarized from `Steps for semantic_backup.docx` — its Cell A/Cell B code
(below) matches this log's own prior paraphrase of that document logic-for-logic, strongly indicating the
same underlying conversation excerpt (not independently re-diffed byte-for-byte against `Steps for
semantic_backup.docx` itself, since that document's raw text is not in this session's active context —
flagged as "almost certainly the same or an overlapping export," not confirmed identical). **This document
adds one real, executed result that the prior round's summary did not capture**, and it changes this log's
own prior framing: the 89.1% figure did *not* "currently rest on one, unshuffled 70/30 split" with no
alternate yet tried, as the previous round's entry stated — a real alternate split had already been run,
with real, quoted output, before the 10-seed loop code was even requested.

**Real, conversation-quoted output** (`ast_taxonomy_crossvalidation.ipynb`'s own `SHUFFLE_BEFORE_SPLIT` flag —
previously logged as defaulting to `False` — flipped to `True` and re-run once, called "seed=0" in the
document's own comparison table):

- Confusion matrix: manual `[83, 15, 0]`, builtin `[6, 38, 0]`, novel `[5, 0, 11]`.
- Overall 3-way accuracy: `0.8354430379746836`.
- `classification_report`: manual precision 0.88/recall 0.85/f1 0.86 (support 98); builtin precision
  0.72/recall 0.86/f1 0.78 (support 44); novel precision 1.00/recall 0.69/f1 0.81 (support 16); accuracy
  0.84 (158); macro avg 0.87/0.80/0.82; weighted avg 0.85/0.84/0.84.

**Side-by-side comparison, quoted directly from the document** (its own table, "Unshuffled (original)" vs.
"Shuffled, seed=0"):

| | Unshuffled (original) | Shuffled, seed=0 |
|---|---|---|
| Overall 3-way accuracy | 86.1% | 83.5% |
| manual precision/recall | 0.92 / 0.86 | 0.88 / 0.85 |
| builtin precision/recall | 0.76 / 0.96 | 0.72 / 0.86 |
| novel precision/recall | 1.00 / 0.45 | 1.00 / 0.69 |
| manual/builtin-only accuracy (the exact number reported in the paper) | 89.1% (131/147) | 85.2% (121/142) |

**This is a real, substantive finding, not a footnote:** the headline 89.1% manual/builtin figure — the one
now published in the paper's own §5.5 — moved to 85.2% (a 4-point drop) under one single alternate
train/test split, and novel recall swung 24 points (0.45 → 0.69) in the same re-run. The document's own
stated reasoning, quoted directly: "that 89.1% wasn't a stable estimate, it was one draw from a
distribution. Reporting it alone, without acknowledging that variance, overstates the precision of the
claim." This is the real motivating result behind the 10-seed-loop request below — not a hypothetical
concern, an observed one.

**This also fully resolves the precision discrepancy flagged as unresolved in the prior round** (the
published paper's manual-precision figure, 0.98, versus an earlier conversation-quoted `classification_report`
figure, 0.92, for what this log had assumed was the same computation). The two figures are **both
independently correct — they are computed over different denominators, not in conflict.** Verified this
session, directly from the "Unshuffled (original)" confusion matrix (`manual[83,14,0]`, `builtin[2,48,0]`,
`novel[5,1,5]`, already logged above): the conversation's 0.92 is the **full 3-way** `classification_report`
precision for `manual` — predicted-manual count across *all three* actual classes is `83 (from manual) + 2
(from builtin) + 5 (from novel)` = 90, so `83/90 = 0.9222 ≈ 0.92`. The paper's 0.98 is precision **within
the manual/builtin-only restricted comparison** the paper's own §5.5 text explicitly describes — since
neither the `manual` nor `builtin` actual rows ever predict `novel` (both confusion-matrix rows have a `0`
in the novel column), restricting to just those 147 rows drops the 5 novel-actual-but-predicted-manual
submissions from the denominator entirely: `83/(83+2) = 83/85 = 0.9765 ≈ 0.98`. The same arithmetic confirms
builtin precision too: full 3-way `48/(14+48+1) = 48/63 = 0.762 ≈ 0.76` (conversation) vs. restricted
`48/(14+48) = 48/62 = 0.774 ≈ 0.77` (paper) — both recall figures (0.86 manual, 0.96 builtin) are identical
either way, since recall's denominator is the actual-class count, unaffected by the restriction. **No
inconsistency remains; the two documents were simply reporting two different, equally legitimate
computations, and this is now stated with certainty rather than left as an open flag.**

### The multi-seed robustness code — real, and now confirmed as a direct response to the instability finding above

The conversation's response to the real instability shown above was, per the document, a direct recommendation:
"don't just pick whichever number looks better — run this across several more seeds (5–10) and report a
mean ± spread in the paper instead of a single decimal." Sonia's own reply, quoted: "ok do the first one"
(i.e., give the loop code, not yet the paper update). This produced the same Cell A/Cell B code already
summarized in this log's prior round:

- **Cell A**: embed every file once into an `embedding_cache` dict (since embeddings don't depend on the
  split, avoiding N redundant re-embeddings).
- **Cell B**: `SEEDS = list(range(10))` — for each seed, shuffle (`labeled.sample(frac=1,
  random_state=seed)`), re-split 70/30, rebuild centroids from cached embeddings, classify, and record
  `acc_3way`, `acc_manual_builtin`, and `novel_recall` per seed; finally report mean/std across all ten
  seeds for each metric.

New in this document, not previously logged: explicit placement instructions (append as a new markdown +
two code cells after the notebook's existing §10 "Save results" cell, since Cell A depends on `labeled`
from §5 and `read_src` from §6, and Cell B depends on `codebert_embed`/`cosine_sim` from §3), and an
explicit sanity-check expectation the conversation itself flagged: "Seed 0 in this loop should reproduce almost
exactly the 83.5%/85.2% numbers you just got by hand" — i.e., the shuffled single-run above was expected,
by the conversation's own reasoning, to closely match what `SEEDS`'s `seed=0` iteration would independently
produce (not confirmed by execution here, since Python's `pandas.sample(random_state=0)` and whatever
mechanism produced the earlier "seed=0" labeled run may not be bit-identical — flagged as an expectation,
not a verified match).

**This is a strong, well-evidenced candidate for what the project's own stated scope — "the ten train/test
split indices used for the embedding experiments" — actually refers to.** `SEEDS = list(range(10))` is a
literal match to "ten... splits," and this is real, dated, working code for exactly that. This is flagged
as the leading hypothesis, not a settled fact: it is specific to *this* experiment (the Q5
manual/builtin/novel taxonomy-validation check), not to the Q4 `SortByKey` embedding work named separately
in `configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits` entry, which remains completely unrelated
and still entirely unsupplied. **No execution output for the full 10-seed loop has been supplied anywhere**
— the document ends immediately after the placement Q&A, with no `summary_df` or mean/std output present.
The real, executed numbers from this experiment are now: the original unshuffled split (89.1%/86.1%/45.5%,
already recomputed above) and the one real shuffled alternate split (85.2%/83.5%/69% novel recall, just
logged above) — two real data points showing real instability, but not yet the full ten-seed mean/std the
paper would need to report a defensible confidence interval.

### What this means for the repository

Unlike the semantic-backup-layer's own Colab work (still real but inconclusive), this is a complete,
independently-reproducible result: real code, a real CSV, and this session's own direct recomputation from
that CSV all agree exactly. It is now added to the reproducibility repo as a real, regenerable stage (see
`configs/stage_manifest.yaml` and `detectors/2026-07-31_ast_taxonomy_crossvalidation/`) — the first
embedding-related result in this entire project with `evidence: real_csv` status, joining `q5_final` as
only the second stage in the whole repo to reach that standard.

---

## The real 10-seed sweep — executed, with real output, resolving the leading pending item

Sonia supplied the actual executed multi-seed robustness check: two notebooks
(`ast_taxonomy_crossvalidation_with_results.ipynb`, cell outputs intact; `Copie_de_ast_taxonomy_crossvalidation.ipynb`,
an identical-code, outputs-stripped copy — confirmed cell-for-cell identical code between the two), a raw
results CSV (`ast_taxonomy_crossvalidation_results 1.csv`, 158 rows), three rendered chart images, and a
conversation export (`1. The Semantic Backup Layer Findings_by cross_ validation.docx` — its filename does not
match its content, which is squarely about this AST-taxonomy 10-seed update, not the separate
semantic-backup-layer novel-detection thread; logged as-is, not silently retitled). **This is real,
executed output, not proposed code** — the leading candidate flagged over the last two rounds for the
project's own "ten train/test split indices used for the embedding experiments" scope requirement is now
fulfilled with an actual result.

### Two things arrived bundled together — kept separate here since they are different runs

1. **The notebook's default `SHUFFLE_BEFORE_SPLIT` flag is now hardcoded `True`** (not `False` as in every
   prior round) with `SPLIT_SEED = 0`. Running just this single-split cell (§5–§8 of the notebook)
   reproduces, **exactly**, the "shuffled seed=0" figures this log already recorded last round from
   `multi-seed loop.docx`'s conversation-quoted output: confusion matrix `manual[83,15,0]`/`builtin[6,38,0]`/
   `novel[5,0,11]`, overall accuracy `0.8354430379746836`, `classification_report` (manual 0.88/0.85/0.86
   support 98; builtin 0.72/0.86/0.78 support 44; novel 1.00/0.69/0.81 support 16). **New this round: the
   supplied CSV (`ast_taxonomy_crossvalidation_results 1.csv`) is the actual raw per-file output of this
   exact run** — independently recomputed directly from the CSV this session (158 rows, label counts
   manual=98/builtin=44/novel=16, matching the notebook's own printed "test label counts" exactly):
   confusion matrix `[83,15,0]`/`[6,38,0]`/`[5,0,11]`, overall accuracy `0.8354430379746836`,
   manual/builtin-only accuracy `0.852112676056338` (121/142, i.e. 85.2%), novel recall `0.6875` (11/16,
   i.e. ~69%) — an exact match, to full floating-point precision, of both the notebook's own printed output
   and last round's conversation-quoted figures. **This upgrades that finding's evidence status from
   `conversation_reported_only` to `real_csv`** — it is no longer resting on a conversation quote alone.

2. **The actual 10-seed sweep (Cell A/Cell B, run this round for the first time) — real, printed,
   executed output**, quoted exactly from the notebook's own output cell:

   | seed | acc_3way | acc_manual_builtin | novel_recall | n_test | n_novel_test |
   |---|---|---|---|---|---|
   | 0 | 0.835443 | 0.868966 | 0.461538 | 158 | 13 |
   | 1 | 0.854430 | 0.889655 | 0.461538 | 158 | 13 |
   | 2 | 0.791139 | 0.826389 | 0.428571 | 158 | 14 |
   | 3 | 0.835443 | 0.876812 | 0.550000 | 158 | 20 |
   | 4 | 0.835443 | 0.855172 | 0.615385 | 158 | 13 |
   | 5 | 0.854430 | 0.888889 | 0.500000 | 158 | 14 |
   | 6 | 0.867089 | 0.897959 | 0.454545 | 158 | 11 |
   | 7 | 0.854430 | 0.875862 | 0.615385 | 158 | 13 |
   | 8 | 0.829114 | 0.874126 | 0.400000 | 158 | 15 |
   | 9 | 0.810127 | 0.841379 | 0.461538 | 158 | 13 |

   **Summary statistics, quoted exactly:** 3-way accuracy mean=0.837 std=0.023; manual/builtin accuracy
   mean=0.870 std=0.023; novel recall mean=0.495 std=0.075. **Pooled predictions across all 10 seeds: 1,580
   total** (each seed's 158-row test set concatenated — the code's own comment is explicit that these are
   *not* 1,580 independent data points, since the same ~526 underlying files recur reshuffled across all 10
   splits; the conversation itself flags this as "a legitimate, more stable summary... but not 10x the statistical
   power"). Pooled confusion matrix: `manual[859,134,0]`, `builtin[54,394,0]`, `novel[67,3,69]`. Pooled
   3-way `classification_report`: manual precision 0.88/recall 0.87/f1 0.87 (support 993); builtin
   precision 0.74/recall 0.88/f1 0.80 (support 448); novel precision 1.00/recall 0.50/f1 0.66 (support
   139); accuracy 0.84 (1580). **Pooled manual/builtin-only report** (n=1,441 — this is the number that
   actually goes in the paper): manual precision 0.94/recall 0.87/f1 0.90 (support 993); builtin precision
   0.75/recall 0.88/f1 0.81 (support 448); accuracy 0.87 (1441).

   **Verified this session:** the pooled manual/builtin accuracy, `(859+394)/1441 = 0.8696`, matches the
   per-seed mean (0.870) almost exactly, as the source conversation itself points out as an internal consistency
   check. The three supplied chart images (a per-seed accuracy-stability line chart with a shaded
   mean±SD=0.870±0.023 band; a row-normalized 2×2 pooled confusion-matrix heatmap showing 859/134 and
   54/394 with 87%/13% and 12%/88% row percentages; a pooled precision/recall bar chart showing manual
   0.94/0.87 and builtin 0.75/0.88) all match this printed text exactly — three independent renderings
   (raw printed numbers, conversation-quoted prose, and rendered figures) agreeing to the same values.

   **This is now a real, executed answer to the previously-open "10-seed robustness check" item.** The
   manual/builtin figure that matters for the paper is **87.0% ± 2.3% across 10 splits (range 82.6%–89.8%,
   from the min/max of the per-seed column above), or 87% pooled** — not the original single-run 89.1%,
   and not the one alternate shuffled run's 85.2% either; both of those sit within this range, near its
   ends, rather than being wrong. Novel recall is confirmed genuinely unstable (mean 49.5%, std 7.5%,
   range 40.0%–61.5% from a 11–20-example test slice per split) — consistent with, and now quantifying,
   the "thin sample, unstable centroid" diagnosis already logged from earlier rounds.

### The source conversation's own reasoning, quoted directly, on why this replaces the single-run figure

"The single run you originally got (89.1%) sits right near the top of this range, not way outside it — so
it wasn't a fluke, but it was on the favorable end rather than representative. 87.0% ± 2.3% is the more
honest number to publish." The conversation explicitly proposed replacement text for §5.5 built around this
figure, and — separately — proposed and then delivered a follow-up (the pooled-confusion-matrix addition
to Cell B) specifically because "I don't want to keep a stale, non-aggregated statistic [0.98/0.86 etc.]
sitting next to a properly averaged one — that'd be an inconsistency a careful reviewer would catch." This
directly explains why the paper's precision/recall figures needed to change too, not just its headline
accuracy — see below.

---

## The published paper, updated again — the Abstract and §5.5 now report the 10-seed mean, not the single run

Sonia supplied a new `Structural_Competency_Extraction_Paper.pdf` (uuid `46af4398`, distinct from last
round's `b2299c85` copy already preserved in `papers/`). **Read in full, page by page, and diffed against
the immediately-prior PDF version already logged and preserved.** The diff is precisely localized to two
passages — everything else in the 20-page document, including Table 3, Tables 1/2, Figure 1/2, §5.1–5.4,
§5.6/Table 4 (still "nineteen structural defects... a further two informational script bugs... omitted,"
word for word unchanged), §6, §7, §8, and the References list (still the same 4 entries, Wang et al. 2023
included, unchanged) — is byte-for-byte identical to the prior version, confirmed by direct comparison.

**Abstract, confirmed exact wording change:**

Old (prior round's PDF): "...which recovers the same strategy split with 89.1% agreement."
New (this PDF, page 1): "...which recovers the same strategy split with **87.0% mean agreement across 10
random train/test splits (SD = 2.3%)**."

**§5.5, confirmed exact wording change (PDF page 13):** the methodology paragraph now explicitly justifies
why a mean is reported: "A single 70/30 split (368 train, 158 test) was used to build one embedding
centroid per label from the training set, with the held-out 30% then classified purely by nearest centroid
and the structural label withheld from the classifier until scoring. Because a single split's agreement
figure can vary considerably depending on which specific submissions happen to land in the training set,
this was repeated across 10 random 70/30 splits, and results are reported as mean ± SD across splits rather
than from one run." The results paragraph now reads: "embedding-based classification agreed with the
structural label at a mean of 87.0% across the 10 splits (SD = 2.3%, range 82.6%–89.8%). Pooling
predictions across all 10 splits (1,441 manual/builtin predictions total) for a more stable precision/
recall estimate than any single split affords — noting that these pooled predictions are not fully
independent, since the same underlying submissions recur across different splits — gives `manual`
precision 0.94/recall 0.87 and `builtin` precision 0.75/recall 0.88." The asymmetric-misclassification
sentence is retained but reworded from a single-run framing ("14 of 16 errors") to a cross-split framing
("misclassifications ran predominantly from manual predicted as builtin... consistently asymmetric across
splits"), since the specific 14-of-16 count no longer applies once the figure is a 10-split aggregate.

**Every number in the new PDF text is an exact match to this session's own independent verification above**
(87.0%/2.3%/82.6%–89.8% from the per-seed table; 0.94/0.87 and 0.75/0.88 from the pooled manual/builtin
report; 1,441 from `993+448`) — the published paper, the executed notebook, the conversation's quoted output, and
the three chart images all agree, to the same precision, across four independent artifacts.

**This retires the "New, minor, open item" flagged two rounds ago** (the paper's manual precision, 0.98,
vs. an earlier conversation-quoted 0.92 for the same confusion matrix) **in a different way than originally
expected: the paper no longer reports the single-run 0.98/0.77 figures at all** — they have been replaced
by the pooled 10-seed figures (0.94/0.75). The arithmetic resolution already logged (both were correct,
computed over different denominators) remains true of the *old* PDF version and is preserved above for the
record, but is no longer the figure a reader of the current paper would encounter.

---

## The internal methodology note, substantially rewritten — a real new version, not the same "V24"/28-07 document

`files_update_methdoclogy_04_08.zip` contains a genuine `.docx` this time (127 paragraphs — unlike the
earlier `Competency_Extraction_Methodology.docx`, which turned out to be plain-text Markdown mislabeled
with a `.docx` extension, logged several rounds ago) plus a matching `.pdf` export. **Read in full and
cross-checked against every prior methodology-note version in this log** (`V24`, the earlier
plain-text-mislabeled 28/07 note). This is neither of those — it is a real, more polished restructuring:
§1 Motivation, §2 Methodology (§2.1–2.12, including a new §2.11.1 "A narrower, successful validation:
cross-checking a taxonomic split" — the embedding cross-validation writeup), §3 Case Study 1, §4 Case
Study 2, §5 Case Study 3 (with §5.1 "Extending batch validation: Q3 and Q4" folded inside it — the same
Case-Study-merge pattern already found in the published paper's own §5.3, done here to the internal note
too), §6 Case Study 4 (Q1/Q2), §7 Bugs Found During Development, §8 Design Principles, §9 Limitations,
§10 Conclusion.

**§2.11.1's own figures are an exact match to everything verified above:** "embedding-based classification
agreed with the structural label at a mean of 87.0% across splits (SD = 2.3%, range 82.6%–89.8%)" —
identical wording appears in the note's own §9 Limitations too ("validate one specific taxonomic split
(87.0% mean agreement...)"). The note explicitly states this is "the same finding now reported in the
published paper (§5.5 there)" — directly confirming, in the source's own words, that the methodology note
and the published paper were updated together, consistent with everything diffed above.

**The bug table has grown from 19 to 21 entries.** Two new, real, canonically-numbered entries formalize
findings this log already had on record only as narrative, not as numbered table rows:

- **#20** — Q3's remaining `.insert()` detection gap (previously logged under the `files_Fix_Q4` checkpoint
  and `Q3_Q4_Results_28.docx`, never before given a bug number): "A handful of real Q3 (remove_extras)
  submissions scored 0 on SelectionStep despite doing the intended edit-in-place removal... Added
  `.insert()` to the recognized collection-mutation calls."
- **#21** — Q4's `SortByKey` taxonomy correction (previously logged extensively under the same
  checkpoints, likewise never before numbered): "TopKPattern/SortByKey taxonomy: Q4's target competency
  was assumed to be BubbleSortPass... Registered SortByKey = ANY(BubbleSortPass, TopKPattern); combined
  coverage 13.1% → 77.6%."

Bugs #1–19 are otherwise unchanged, word-for-word, from the 19-entry canonical table already logged in
full from the 28/07 methodology note.

**This bears directly on the previously-flagged, still-open bug-count discrepancy** (the published paper's
own text saying "nineteen structural defects... a further two informational script bugs... are omitted,"
implying 19+2=21 total, versus the methodology note's prior 19-entry table with only one entry, #15,
self-described as informational). **Still not cleanly resolved, now with sharper evidence:** this new
21-entry table has #1–21, of which only #15 is explicitly self-described as "not a defect in the model" —
i.e., by this table's own accounting, 20 structural + 1 informational = 21, not the paper's stated
"19 structural + 2 informational = 21." The two new entries (#20, #21) are both genuinely structural (real
detector/taxonomy defects, not informational script bugs), so adding them does not supply the paper's
missing second "informational" bug — if anything it sharpens the mismatch, since the paper's Table 4 body
text was not updated this round (confirmed unchanged above) even though the methodology note it's meant to
track gained two new numbered entries. **Flagged as still open, with more precise numbers than before, not
resolved by this round's evidence.**

---

Sonia supplied a PDF, introduced only as "here is the corresponding paper version." This is the "20 pages
now" file the immediately-prior round's conversation described editing (new §5.5, a Wang et al. 2023 citation,
renumbered sections) — **now directly read, page by page, and diffed word-for-word against the
previously-supplied `Structural_Competency_Extraction_Paper.docx`** (the 95-paragraph/4-table version
already logged above, converted to plain text via `pandoc` for the diff), rather than taken on the conversation's
description. Every claim below is either a direct quote from the PDF or a specific, located textual
diff against the prior docx — nothing is inferred from the earlier conversation summary alone.

### The Abstract change — confirmed, two real edits

**Note (2026-09-19): this section originally quoted the Abstract's old and new wording verbatim. Replaced
with a paraphrase** — the paper is not yet published; see `../papers/README.md`'s header note for why the
raw files and verbatim excerpts were removed from this public repo. The Abstract picked up a new sentence
reporting the 89.1% embedding-agreement figure for the manual/builtin split, and the pre-existing
companion-paper sentence was expanded to clarify that the embedding check above is used solely as external
validation of the AST taxonomy — a distinct concern from the companion paper's own semantic-backup-layer
validation, which remains out of scope for this paper. Both edits are diff-confirmed against the prior
revision, not conversation-paraphrased.

### §5.5 "External validation of a taxonomic split via code embeddings" — confirmed present

**Note (2026-09-19): this section originally quoted the new §5.5 in full. Replaced with a paraphrase**, for
the same reason as above. The section motivates the check (does the manual/builtin distinction inside
FindExtremum correspond to anything an AST-independent method would also recover, or is it an artifact of
how the structural rules happen to be written), describes the method (a pretrained
`codet5p-110m-embedding` model, with no access to AST structure or scores; every Q5 submission labeled
`manual`/`builtin`/`novel` by its structural match — 327/151/48 of 526 — then a 70/30 train/test split
used to build one embedding centroid per label and classify the held-out 30% by nearest centroid, label
withheld from the classifier), and reports the result: 131 of 147 manual/builtin submissions agreed with
their structural label (89.1%; manual precision 0.98/recall 0.86, builtin precision 0.77/recall 0.96),
with misclassifications running almost entirely one direction (manual predicted as builtin), attributed to
builtin solutions forming a tighter embedding cluster (a small, syntactically homogeneous family of
`max()`/`min()` calls) than the more variable manual implementations. The section concludes this is
independent evidence the manual/builtin split is a real, recoverable distinction rather than an artifact of
the taxonomy.

**Confirmed exact matches to this log's own independent recomputation** (from the "AST taxonomy
cross-validation via embeddings" section above): 327/151/48 label counts, 368/158 train/test split, 131/147
= 89.1%, confusion-matrix-derived asymmetry ("14 of 16 errors" — matches this log's own confusion matrix
manual row `[83,14,0]`/builtin row `[2,48,0]`: total manual/builtin errors = 14+2 = 16, 14 of them
manual→builtin). **New information, not previously in this log**: the paper states manual
precision=0.98/recall=0.86 and builtin precision=0.77/recall=0.96 explicitly. This session verified these
are arithmetically consistent with the previously-recomputed confusion matrix: predicted-manual count =
83+2=85, precision=83/85=0.976≈0.98 ✓, recall=83/97=0.855≈0.86 ✓; predicted-builtin count = 14+48=62,
precision=48/62=0.774≈0.77 ✓, recall=48/50=0.96 ✓. (The conversation's own quoted precision/recall figures from the
"AST taxonomy cross-validation via embeddings" section above — 0.92/0.86 manual, 0.76/0.96 builtin — are
close to but not identical to the paper's 0.98/0.86 and 0.77/0.96; the paper's manual-precision figure in
particular differs by 6 points, 0.92 vs 0.98. This log recomputed 0.98/0.77 directly from the same
confusion matrix both figures claim to describe, so the paper's numbers are the ones independently
verified here — the conversation's own earlier 0.92 figure is flagged as a discrepancy against both the raw
confusion matrix and the paper's own published precision, not resolved further since no `classification_report`
recomputation script has been run in this session.)

### The Wang et al. (2023) citation — confirmed present in the References list

**Confirmed absent from the prior docx's References** (3 entries: Hu et al. 2019, Keuning et al. 2018,
Messer et al. 2024 — verified by direct text search of the converted docx, zero matches for "Wang"). **Confirmed present in the PDF's References** (page 20, 4th entry, quoted in full): "Wang, Y., Le, H.,
Gotmare, A. D., Bui, N. D. Q., Li, J., & Hoi, S. C. H. (2023). CodeT5+: Open code large language models
for code understanding and generation. In *Proceedings of the 2023 Conference on Empirical Methods in
Natural Language Processing (EMNLP 2023)* (pp. 1069–1088). Association for Computational Linguistics."

### The §7 Limitations forward-pointer sentence — confirmed present, exact wording, resolving the previously-unconfirmed item

**Old** (prior docx §7, confirmed by direct extraction) ends its semantic-backup paragraph at: "...its
evaluation — including whether it adds real signal beyond the structural layer described here — is
deliberately deferred to a companion paper rather than reported alongside results that are validated at
real scale."

**New** (PDF page 19) adds exactly one sentence immediately after that, word-for-word the sentence this
log's prior round recorded as "proposed for §7 Limitations" but explicitly flagged as unconfirmed: "A
preliminary check using the same embedding model to attempt automatic novel-strategy detection, rather
than validation of an existing split, is reported in the companion paper; early results suggest this is a
harder problem than the manual/builtin check above, requiring a different decision rule than
nearest-centroid classification." **This resolves pending item (the §7 forward-pointer) as genuinely
inserted, not merely proposed-and-assumed.**

### The section-numbering discrepancy — resolved by diff, and the real mechanism was a merge, not a simple insert

This log's prior round flagged an unresolved numbering puzzle: the conversation said the new §5.5 was inserted
"between 5.4 and 5.5" and that defects/Table 4 is "now 5.6" — but this log's own prior reading of the
pre-edit paper had already recorded Case Study 5 (Q3/Q4 batch results) at §5.5 and defects/Table 4 at
§5.6, which would make a simple insertion push defects to §5.7, not leave it at §5.6.

**Directly diffing the prior docx against the new PDF resolves this precisely.** The prior docx's own
section list, read directly (`pandoc` conversion, headings extracted): §5.1 Case Study 1, §5.2 Case Study
2, §5.3 Case Study 3 (batch validation, TopKPattern only), §5.4 Case Study 4 (taxonomy completion, Q1/Q2),
**§5.5 Case Study 5: Extending batch validation to Q3 and Q4**, §5.6 Robustness/defects, §6 Discussion, §7
Limitations, §8 Conclusion.

The new PDF's section list: §5.1 Case Study 1, §5.2 Case Study 2, **§5.3 Case Study 3: Batch validation at
scale — now covering TopKPattern *and* the Q3/Q4 content, word-for-word identical to the old §5.5's "Q3: a
minor detector gap." and "Q4: a taxonomy correction, not a gap-fill." paragraphs**, §5.4 Case Study 4
(taxonomy completion, unchanged), **§5.5 External validation of a taxonomic split via code embeddings
(new)**, §5.6 Robustness/defects (unchanged), §6/§7/§8 (unchanged numbers).

**What actually happened, confirmed by direct text comparison:** the old, standalone §5.5 ("Case Study 5:
Extending batch validation to Q3 and Q4") was **merged into §5.3**, not kept as its own section — its Q3
and Q4 paragraphs are reproduced verbatim in the new PDF's §5.3, with only the connective/reference text
adjusted (old: "The same function-scoped batch methodology used in Section 5.3 was subsequently applied
to..."; new: "The same function-scoped batch methodology was subsequently applied to..." with the
self-reference to "Section 5.3" removed, since the content is now *inside* §5.3; old: "structurally
identical to TopKPattern, built entirely for the Top-K exercise (Section 5.1)"; new: "...built entirely
for the Top-K exercise earlier in this section," since Q4 content is now in the same section as Q5's
original TopKPattern coverage). This merge freed up the number 5.5, which the brand-new embedding-
validation subsection then took. Net section count is unchanged (one merged in, one new added), which is
why defects/Table 4 stayed at §5.6 exactly as the conversation said — but the *mechanism* was "merge Case Study 5
into Case Study 3, then insert new content at 5.5," not a simple insertion after 5.4. This is corroborated
independently by two cross-references in unrelated sections: the Conclusion (§8) changed its own citation
from "as Section 5.5 shows concretely" (old docx) to "as Section 5.3 shows concretely" (new PDF) when
referring to the Q4-taxonomy-was-wrong-by-a-factor-of-six point; and §7 Limitations changed its citation
from "Section 5.5 demonstrates concretely why this matters" (old) to "Section 5.3 demonstrates concretely
why this matters" (new) — both edits are exactly what the Case-Study-5-into-5.3 merge would require, and
both are present in the actual PDF text, not inferred.

**This closes the previously-open item.** The prior round's log entry ("A section-numbering detail is
flagged, not resolved... cannot be resolved without the actual updated document") is superseded: the
document is now in hand, and the discrepancy is fully explained by a real, diff-confirmed merge rather
than a loose paraphrase in the conversation.

### Everything else in the paper — cross-checked, no further changes found

A full page-by-page read of the PDF (all 20 pages) against the prior docx's converted text found no other
content changes beyond the four described above (Abstract, §5.5 insertion, the Wang et al. 2023 reference,
and the §7 sentence) plus the mechanical consequences of the §5.3/§5.5 merge (the two Section-number
cross-references corrected above, and the loop-removal of the redundant "(Section 5.1)"/"used in Section
5.3" phrasing already quoted). Table 3 (corpus composition), Table 1 (12 primitives), Table 2 (structural
constraints), the full defect table (Table 4, still nineteen entries across the same categories), and
every other section's prose are otherwise unchanged, word for word, between the two documents.

### What this resolves and what remains open

- **Resolved:** the paper genuinely contains the new §5.5, in the form the conversation described (confirmed by
  direct quotation above).
- **Resolved:** the Wang et al. (2023) CodeT5+ citation is genuinely present in the References list.
- **Resolved:** the Abstract genuinely carries the new sentence (and a real, previously-unrecorded
  expansion of the companion-paper sentence).
- **Resolved:** the §7 forward-pointer sentence about the companion-paper's preliminary novel-detection
  check is genuinely present, exact wording confirmed.
- **Resolved:** the section-numbering discrepancy — explained by a real merge-plus-insert mechanism, not
  a simple insertion, fully diff-confirmed on both sides (the content move and two corrected
  cross-references).
- **Resolved (as of `multi-seed loop.docx`, see the dedicated section below):** the paper's own
  manual-precision figure (0.98) does not conflict with an earlier conversation-quoted `classification_report`
  figure (0.92) for the same confusion matrix — the two are both correct, computed over different
  denominators (full 3-way vs. manual/builtin-restricted), confirmed by direct arithmetic against the
  confusion matrix. What was flagged as an open discrepancy last round is now fully explained.
- **Superseded by a later round, not merely "materially updated" — see "The real 10-seed sweep" and "The
  published paper, updated again" sections further below.** At the time this bullet was first written, the
  paper's §5.5 still reported only the single, unshuffled 70/30 split's 89.1% figure, with the shuffled
  85.2% single-split result flagged as a warning sign and the full 10-seed sweep itself unexecuted. Both of
  those gaps have since been closed with real evidence: the 10-seed sweep was executed (real per-seed
  table, pooled confusion matrix, pooled classification reports — all independently cross-checked against
  three chart images), and the paper itself was revised a second time to report the resulting 87.0% ± 2.3%
  mean (10 splits) and pooled precision/recall (manual 0.94/0.87, builtin 0.75/0.88) in place of the single
  89.1%/0.98/0.77 run. The companion paper itself (with the novel/recall-0.45 story, the anomaly-detection
  reframing, and its own validation of the semantic-backup layer) remains entirely unsupplied.

---

## A real batch-validation script for Q1-Q4 — `run_q1_q4_batch_validation.py` + `Conversation for run Q1-Q4 batch validation.docx`

Sonia supplied a new conversation export and a real Python script, `run_q1_q4_batch_validation.py`. **Real date:
2026-08-05, per Sonia directly** — this corrects an initial dating of this checkpoint to 2026-09-13, which
was inferred from the accompanying docx's own `dcterms:created`/`dcterms:modified` metadata
(2026-09-13T08:38-09:02 UTC). That metadata reflects when the conversation was exported/saved as a `.docx` file,
not when the underlying conversation actually happened — the same distinction this log has already drawn
elsewhere between a document's save/export timestamp and its real content date. Corrected throughout this
log, `configs/stage_manifest.yaml`, and the repository's checkpoint folder name
(`detectors/2026-08-05_q1_q4_batch_validation/`, not `2026-09-13_...`) per Sonia's explicit correction. This
is the first-ever supplied driver script for Q1-Q4's full-corpus batch validation — directly answering a
bullet that has sat in "Still-pending items" since early in this log: "no batch scripts or CSVs" exist for
the 90.4% Q2, 94.0% Q3, 77.6% Q4, or LinearSearch's Q1 figures, unlike Q5 (which has `topk_report.csv`).

### What the script actually does — real, verified reuse of already-confirmed machinery

The script imports `process_folders` from `batch_report.py` and calls it once per question with a
`target_ids` list, an `output_csv` path, and a `function_name` for scoping — **this is checked directly
against `detectors/2026-07-21_reporting_batch/batch_report.py` already in this repo, not taken on faith**:
`process_folders(folder_labels, model, target_ids, output_path, function_name=None)` is the real, exact
signature, and `process_folder` passes `function_name` straight through to `generate_report`. The new
script's calls match this signature exactly. Real, not invented.

### Cross-verified claims: some confirmed exactly, one confirmed FALSE, one operational risk found

Direct inspection of files already in this project's possession (not just the new conversation's own say-so)
turned up a precise, mixed picture:

- **Confirmed true, by direct read:** the script's own docstring claims "Q1's original
  `q1_competencies.py` `__main__` block used whole-file resolution instead" of function-scoping. Checked
  directly against `cfecda73-q1_competencies.py`'s own `__main__` block: `r = model.resolve(ast.parse(src),
  ["GuardedInput", "LinearSearch"])` — no `function_name` argument, no scoping at all. The claim is exactly
  right.
- **Confirmed true, by direct read:** the script's import block assumes two real module filenames,
  `ex2_3_4_competencies.py` and `q2_competencies.py`. Both are exactly the filenames inside
  `files_ex2_3_4.zip` and `files_Q2_competencies_3rd_strategie.zip` respectively, already supplied and
  logged in earlier rounds. Not a guessed or hallucinated import.
- **Confirmed true, by direct read:** the shared-model architecture the script depends on is real and
  coherent, not assumed. `test_real_data.py` is the module that actually instantiates
  `model = CompetencyModel()`; `q1_competencies.py`, `pw01_competencies.py`, and `ex2_3_4_competencies.py`
  all do `from test_real_data import model` and register onto that same object as an import side effect;
  `q2_competencies.py` does `from pw01_competencies import model`, which — because Python caches modules —
  is transitively the identical object. So the script's import order (`test_real_data` → `q1_competencies`
  → `q2_competencies` → `ex2_3_4_competencies`) does build one single, consistent registry, exactly as
  intended.
- **Confirmed FALSE, by direct read — a real error in the conversation's own claim, not smoothed over.** The conversation
  states: "Confirmed: unique_day (Q2) is a real, verified function name straight from the code... verified
  against your code (`pw01_competencies.py` and `q2_competencies.py` both define and resolve against a
  function literally named `unique_day`)." `q2_competencies.py`'s own `__main__` block does exactly this —
  two embedded test snippets both define `def unique_day(day, possible_birthdays):`. But `pw01_competencies.py`
  (read in full from `files_ex2_3_4.zip`) contains **zero** mentions of `unique_day` anywhere — it registers
  entirely different competencies (`IsPrime`, `CountedSearch`, `CollectInput`, `Average`) for entirely
  different exercises (Ex1.3/1.4 next-N-primes, Ex1.5 collect-input, Ex1.2 average), with no Q2 material at
  all. The claim about `pw01_competencies.py` is simply wrong; only `q2_competencies.py` supports it. Note
  that even the true half of this claim only establishes that the model's own hand-written test fixtures
  use the name `unique_day` — not independent proof that the real Refactory Q2 submission files themselves
  define a function by that exact name, which no supplied artifact can confirm without the actual
  submission data.
- **A real, unflagged operational risk found by direct diff, not present in the script's own caveats.**
  Q4's `target_ids` include `SortByKey`, but `SortByKey` is registered in only ONE of the two versions of
  `test_real_data.py` this project has ever supplied: it is present in `files_Fix_Q4/test_real_data.py` and
  **absent** from the standalone `c8f2a77d-test_real_data.py` supplied separately — confirmed by an exact
  `diff`, which shows the *only* difference between the two files is the `SortByKey` registration block
  itself (added on top of an otherwise byte-identical file). If Sonia's actual local `PROJECT_DIR` contains
  the earlier, pre-`SortByKey` version of `test_real_data.py` under that name, Q4's `SortByKey_final`/
  `SortByKey_missing` columns will come back empty for every row rather than erroring loudly — the new
  script does not check for or warn about this version dependency anywhere in its docstring or comments.
  Not something either conversation state addressed.
- **Also checked and found harmless:** the script's own comment hedges `import ex2_3_4_competencies # if
  SelectionStep/other Q3-relevant competencies live here`. Direct read of `ex2_3_4_competencies.py` shows
  it does NOT register `SelectionStep` at all — it registers `GameLoop` (rock-paper-scissors), `GreedyReduction`/
  `ArithmeticReduction`/`GreedyChange` (a change-making exercise), `CounterBalance`/`StackBalance`/
  `BalancedCheck` (balanced parentheses), and `GridIteration` (tic-tac-toe) — an entirely different exercise
  set (looks like a separate, non-Refactory course's "Ex1-Ex4" series, based on the French variable names
  and print strings) that doesn't correspond to any of this project's Q1-Q5 questions. This doesn't break
  the script, though, because `SelectionStep` is already registered by the very first import
  (`test_real_data.py` itself, confirmed at line 66 of both supplied versions) — the `ex2_3_4_competencies`
  import is genuinely unnecessary for any of the four questions' `target_ids`, but harmless, since it just
  registers additional, unused competencies onto the shared model.

### What's genuinely new evidence vs. what's still only Sonia's own unconfirmed word

Per the conversation's own final state (the "last conversation" quoted in the docx, with the summary table Q1=`search`,
Q2=`unique_day`, Q3=`remove_extras`, Q4=`sort_age`, "all four function names are now confirmed"): Q2's name
was checked against actual code (see above — true for `q2_competencies.py`, false for the `pw01_` half of
the claim); Q1's `search`, Q3's `remove_extras`, and Q4's `sort_age` are stated as confirmed "directly by
the person running this" (i.e., by Sonia against her own real Refactory source files) — **none of these
three is independently checkable from any artifact supplied to this project**, since no real Q1/Q3/Q4
submission source file has ever been supplied here. They are logged as Sonia-asserted, not
independently-verified-by-diff, consistent with this log's standing evidence discipline.

### Evidence status: real code, not yet executed

This script is real, was read in full, and (per the analysis above) is internally consistent with every
other real artifact already in this project — a genuine advance from "no batch script exists for Q1-Q4" to
"a real, checkable batch script exists." But per the conversation's own explicit statement — "I don't have your
actual Refactory dataset files in this environment... I can write and validate this script, but I can't
run it myself; you'll run it wherever your Refactory data/ folder actually lives" — **it has not been run,
and no output CSV for any of Q1-Q4 has been supplied.** This remains `evidence: conversation_reported_only` for the
underlying Q1-Q4 percentages until Sonia runs it and supplies the resulting `q1_report.csv`/`q2_report.csv`/
`q3_report.csv`/`q4_report.csv` files — at which point this project would gain its first-ever real,
independently-regenerable CSVs for these four questions, mirroring what already exists for Q5.

---

## Real batch-validation RESULTS for Q1-Q4 — `run_q1_Q4_batch_validation.docx` + `q1_report.csv`/`q2_report.csv`/`q3_report.csv`/`q4_report.csv` + `files_run_Q1_batch_report_Last_version_files.zip` + `Methodology_and_paper_after_batch_report.zip` + `Structural_Competency_Extraction_Paper_modif_2.pdf`

Sonia supplied a new conversation export plus the actual output of running the batch-validation script logged in
the previous section, along with a code fix for a real gap the run surfaced in Q1, and the resulting
updated methodology doc and paper. **Real date: 2026-08-05**, confirmed independently three ways: the
conversation export docx's own `dcterms:created`/`dcterms:modified` metadata (2026-08-05T12:10:00Z /
2026-08-05T16:52:00Z), the new methodology docx's metadata (`dcterms:created`/`modified`
2026-08-05T13:58:00Z, matching its own PDF's `pdfinfo` `CreationDate` of 13:58:02 UTC exactly), and the new
paper docx/PDF's metadata (2026-08-05T13:55:51Z docx / 13:55:54 UTC PDF `CreationDate`). All four land the
same day as the prior checkpoint's corrected date (2026-08-05) — this round is a same-day continuation of
that work, not a later session.

**Source artifacts, all read/diffed in full:**
- `q1_report.csv` (1,343 data rows), `q2_report.csv` (726 rows), `q3_report.csv` (854 rows), `q4_report.csv`
  (776 rows) — the actual output of `run_q1_q4_batch_validation.py`, run by Sonia against her real
  Refactory dataset. These are this project's first-ever real per-submission CSVs for Q1-Q4, mirroring what
  `topk_report.csv` has provided for Q5 since an earlier round.
- `files_run_Q1_batch_report_Last_version_files.zip` (unzipped to `q1fix/`): `competency.py`,
  `q1_competencies.py`, `test_real_data.py`, and `q1_report_FIXED.csv` — a real code fix for a Q1-specific
  gap the batch run surfaced, plus the CSV it produced. `q1_report_FIXED.csv` is byte-identical (md5
  `34edf41aeae25df5bb04617807b77a2e`) to the standalone `q1_report.csv` above — the two are the same file,
  not independent runs.
- `Methodology_and_paper_after_batch_report.zip`: `Competency_Extraction_Methodology.docx`/`.pdf` (28
  pages) and `Structural_Competency_Extraction_Paper.docx`/`.pdf` (21 pages) — an intermediate paper
  revision, superseded within the same round (see below).
- `Structural_Competency_Extraction_Paper_modif_2.pdf` (22 pages, top-level upload, `CreationDate`
  2026-08-05 14:05:28 UTC — about 10 minutes after the zip's 21-page PDF) — the final, current paper
  version for this round, confirmed genuinely different from the zip's copy by direct `pdftotext -layout`
  diff, not a duplicate upload.

### The headline event: Q1-Q4 move from `conversation_reported_only` to `real_csv`, independently re-verified

Every one of this round's headline percentages was recomputed directly from the four CSVs (correct-labeled
rows scoring the target competency > 0, divided by total correct-labeled rows, matching how every other
`real_csv` figure in this log — e.g. Q5's — has been computed), not taken from the conversation's or paper's own
tables on faith. The independent recomputation matches the paper's brand-new consolidated Table 4
(quoted in full below) exactly, cell for cell:

| Q | Task | Target competency | Correct (n) | Wrong (n) |
|---|------|---|---|---|
| 1 | Sequential search | GuardedInput / LinearSearch | 99.5% (764/768) | 97.6% (561/575) |
| 2 | Unique day/month | UniqueCheck | 90.4% (263/291) | 74.3% (323/435) |
| 3 | Duplicate elimination | SelectionStep | 94.0% (513/546) | 74.7% (230/308) |
| 4 | Sort tuples by age | SortByKey | 77.6% (325/419) | 45.9% (164/357) |

(Q5's 78.2%/75.0% row, already `real_csv`-backed from `topk_report.csv` in an earlier round, is unchanged
and not re-verified here.) This is the first time Q2's `UniqueCheck` (previously only conversation-asserted at
90.4%), Q3's `SelectionStep` (94.0%), and Q4's `SortByKey` (77.6%) have a real CSV behind their headline
figures — not just Q1. **`configs/stage_manifest.yaml`'s `q1_final`/`q2_final`/`q3_final`/`q4_final`
stages are upgraded from `evidence: conversation_reported_only` to `evidence: real_csv` below**, the single biggest
evidence-tier change in this log to date.

### The Q1 diagnostic story: 383 zero-scores, resolved into 19 genuine gaps + 364 structural-detector misses

Before the fix (i.e. against the pre-fix `competency.py` already in this repo at
`detectors/2026-07-28_fixQ4/`), the conversation reports `GuardedInput` scored 1.0 on only 76.8% of correct-labeled
submissions (64.2% wrong-labeled) — markedly lower than Q2/Q3's real figures above. Of 383 zero-scoring
submissions, the conversation's own diagnosis, arrived at by direct inspection of sampled real files (not
guessed), splits into two categories:

- **19 files: a genuine coverage gap** (the loop or test primitive is simply absent) — "14 missing loop, 3
  missing both test+loop, 2 missing test," per the conversation verbatim.
- **364 files (95% of the zero-scores): a structural-detector limitation, not a coverage gap.** Every
  required primitive (target, test, loop) is present, but `SHARED_BINDING`'s check — comparing only against
  `TEST` evidence's `operand` binding (the literal left-hand side of a simple comparison) — cannot see the
  relationship in three real, quantified shapes real students wrote:
  - **199 files (55%):** the searched value on the *right* side of a simple comparison (e.g. `elem >= x`
    rather than `x <= elem`) — captured by `detect_test` as `comparator`, but never checked by
    `SHARED_BINDING` at all.
  - **107 files (29%) + 50 files (14%) = 157 files (43% combined, the grouping the paper and methodology
    doc both use):** a compound `and`/`or` condition (e.g. `x > seq[i] and x <= seq[i+1]`) or Python's
    native chained comparison (`seq[i] < x <= seq[i+1]`) — both fall into `detect_test`'s single-op
    `ast.Compare` branch and get flattened into one opaque string.
  - **8 files (2%):** the test is a `while` loop's own condition (e.g. `while x > seq[count]:`), never
    captured as `TEST` evidence at all, since `detect_test` only ever walked `ast.If` nodes.
  - 199 + 107 + 50 + 8 = 364, exactly. All three mechanisms share one root cause: `detect_test` and
    `SHARED_BINDING` were both built around a single syntactic shape (a simple, single-op comparison with
    the target on the left).

### The verified code fix — real, additive, confirmed by direct diff against the pre-fix checkpoint

`diff` against `detectors/2026-07-28_fixQ4/competency.py` (the already-verified pre-fix baseline in this
repo) confirms all three changes the conversation describes are real and genuinely additive — the original
equality-check code path is untouched in every case:

1. **A new `all_names` binding on every `TEST` evidence**, populated in the existing If-branch: `all_names
   = frozenset(n.id for n in ast.walk(test) if isinstance(n, ast.Name))` — every bare identifier referenced
   anywhere in the test expression, regardless of its AST shape (simple compare, `BoolOp`, or chained
   compare). Added to the `Evidence` bindings dict alongside the pre-existing `operand`/`comparator`/`op`.
2. **A new `elif isinstance(node, ast.While)` branch**, synthesizing `TEST` evidence from the loop's own
   condition exactly as the `If` branch already does, with `node=None` (the same convention composite
   evidence already uses, so the resolver's node-reuse guard — which only inspects non-`None` nodes — never
   treats it as colliding with the `LOOP` evidence generated for the same `while` statement) and `scope`
   set directly from the real `while` node inside `detect_test` itself (rather than via the generic
   post-resolve scope-tagging pass, which skips `node=None` evidence).
3. **`SHARED_BINDING.score()` extended with two new `elif` branches** (confirmed via direct read, not
   inferred): `elif isinstance(vb, (set, frozenset, list, tuple)) and va in vb: matches += 1` and its
   mirror with `va`/`vb` swapped — containment matching when one side's binding is a set, purely additive
   alongside the original `if va == vb: matches += 1`.
4. **The only competency-definition-level change**: `GuardedInput` (in `test_real_data.py`) and
   `LinearSearch` (in `q1_competencies.py`) both switched
   `SHARED_BINDING([("source"/"loop","target","test","operand")])` to use `"all_names"` in place of
   `"operand"` as the fourth tuple element. Every other competency using `TEST` or `SHARED_BINDING` in the
   library is untouched, confirmed by the diff showing no other registration blocks changed.

Re-run against all 1,343 real Question 1 submissions with the fixed code: coverage rose from 76.8%/64.2% to
**99.5%/97.6% (correct/wrong)** — independently confirmed above against the real `q1_report.csv` — with
zero regressions (no submission that scored 1.0 before scores lower afterward; this project cannot
independently re-verify "zero regressions" without the pre-fix CSV, which was not supplied, so this
specific claim remains conversation-reported, though it is consistent with the fix being purely additive per the
code diff itself).

### A genuine error found in the fix's own code comment: "526" should be "383"

`test_real_data.py`'s new comment above `GuardedInput`'s definition reads, quoted verbatim from
`q1fix/test_real_data.py` lines 56-65:

> `# SHARED_BINDING now checks against TEST's all_names (every identifier`
> `# referenced anywhere in the test, however it's shaped) rather than just`
> `# operand (the literal left-hand side of a simple comparison). Batch`
> `# validation against the real Question 1 dataset found this matters a lot:`
> `# 364 of 526 zero-scoring submissions had every slot present but still`
> `# scored 0, because the searched value appeared on the right side of a`
> `# comparison ("elem >= x", 55% of cases), inside a compound "and"/"or" or`
> `# chained condition ("x > seq[i] and x <= seq[i+1]", 43%), or as a while`
> `# loop's own condition rather than a nested if (2%) -- none of which the`
> `# old operand-only check could see.`

**"526" is wrong.** The conversation's own text, the paper's own text ("Of the 383 zero-scoring submissions, only
19 were a genuine coverage gap"), and this log's own independent recomputation above all agree the correct
denominator is **383** (364 structural-fail + 19 genuine gap = 383), not 526. 526 is Q5's unrelated total
submission count (418 + 108 = 526, from the `topk_report.csv` dataset logged in an earlier round) —
apparently an accidental carry-over into this comment, not a new or different figure. This is a defect in
a source-code comment only; it does not affect behavior, and does not appear in either the methodology
doc's bug #22 entry or the paper's own §5.3 text, both of which correctly say "383" (confirmed by direct
grep of both documents — see below). Flagged here per this log's standing discipline of not smoothing over
found errors, however small.

### Reconciling "19" (pre-fix) vs. "17" (post-fix) genuine gap files — derived independently from the CSV, not stated by any document

Every document this round (conversation, paper, methodology doc) states the genuine coverage gap as "19
submissions" without distinguishing a pre-fix from a post-fix count. Direct analysis of the real, post-fix
`q1_report.csv` finds **18 rows still score 0 on `GuardedInput` after the fix** (matching `LinearSearch`'s
zero-set exactly, row for row — confirmed by diff, zero disagreements): 17 with no `error` field set, and
1 (`wrong_1_434.py`) with a genuine parse/lookup error ("function 'search' not found in submission"),
consistent with the conversation's own claim that this file is a dataset quirk literally named `search2`, though
that specific claim about the file's actual contents cannot be independently confirmed from the CSV alone
(no source `.py` file was supplied). Of the 17 error-free zero-scoring rows, `GuardedInput_missing` reads
`'loop'` for 14 of them and `'test,loop'` for 3 — **an exact match, file-count for file-count, to the
pre-fix breakdown's "14 missing loop, 3 missing both test+loop" categories**, with the pre-fix breakdown's
remaining "2 missing test" category now absent entirely. This is a clean, fully-explained reconciliation
this log derives on its own: the 2 pre-fix "test-only-missing" files are exactly the 2 that the new
`ast.While`-condition `TEST` detection fixed (a loop existed with only a `while`-condition test, previously
invisible to `detect_test` entirely), leaving 19 − 2 = 17 files with the loop primitive itself genuinely
absent post-fix. No document states this explicitly; it follows directly from the CSV's own `_missing`
column values.

### The "99.93% agreement" claim between `GuardedInput` and `LinearSearch` — resolved as a `pandas` NaN-comparison artifact, not a real difference

Both the conversation, the methodology doc (§5.2), and the finished paper (§5.3) state LinearSearch "moved
identically" to GuardedInput, landing at 99.5%/97.6%, with "99.93% agreement... 1,342 of 1,343 rows," the
one difference attributed to `wrong_1_434.py`. **Direct comparison of the real CSV's own
`GuardedInput_final`/`LinearSearch_final` and `GuardedInput_missing`/`LinearSearch_missing` columns, cell
by cell across all 1,343 rows, finds zero differences anywhere** — the two competencies' columns are
byte-for-byte identical in this CSV, including on `wrong_1_434.py` itself (both score 0 with the same
`missing` value on that row). This is not a contradiction: the conversation's own text explains the "1 of 1,343"
figure came from an earlier `pandas`-based before/after diff where `NaN != NaN` evaluates `True` (a `NaN`
never equals itself), so a genuinely-unchanged row with an error on both sides still registered as
"changed" in that diff tool — the conversation itself identifies this as "NaN-comparison noise... not because
anything about it actually moved," and both the methodology doc and paper carry the "99.93%" figure forward
as the headline framing anyway, from before that explanation. This log's own direct string-equality check
on the final CSV (which has no `NaN`-comparison step involved) is a cleaner, stronger confirmation than the
"99.93%" figure: it is exact, 100% agreement, on this delivered data.

### Two successive paper revisions this round — Q1 added (20p→21p), then a new consolidated Table 4 + full renumbering cascade (21p→22p)

Confirmed via `pdftotext -layout` diff across all three PDF versions (`2026-08-04...` 20p already in this
repo → the zip's 21p → `_modif_2`'s 22p, the final version):

- **20p → 21p:** Abstract changed ("two exercises" → "three additional exercises"; "nineteen" → "twenty"
  defects). New §5.3 text added, quoted in full above (the Q1 diagnostic narrative — 76.8%/64.2%, 383
  zero-scores, three mechanisms, 99.5%/97.6% after the fix). A forward-pointer sentence added to §5.4. A
  new Table 4 row, "Overly narrow structural matching," added with the same symptom/root-cause/fix content
  as the methodology doc's bug #22 (below).
- **21p → 22p (final):** a brand-new §5.5, "Summary: full-corpus coverage across all five Refactory
  exercises," inserted between taxonomy completion (§5.4) and the embeddings-validation section, containing
  the consolidated Table 4 quoted above (verbatim match to this log's own independent recomputation) plus
  two paragraphs: one noting three exercises (1, 3, 4) reached their final number only after a defect was
  found and fixed, versus two (2, 5) reflecting the taxonomy as originally built; the other naming the
  cross-exercise pattern that wrong-labeled coverage is always substantially lower than correct-labeled but
  never near zero. This triggered a full renumbering, confirmed fully consistent by diff with no stale
  references remaining: old Table 4 (defects) → Table 5; old §5.5 (embeddings) → §5.6; old §5.6
  (Robustness) → §5.7; every downstream cross-reference in the document updated to match (the conversation's own
  account of "two more found" stray references during its own grep sweep is corroborated — the final PDF
  shows a fully clean result).

### The methodology doc's own, separate write-up — confirmed NOT to include the consolidated table, per the conversation's own explicit statement

The methodology doc (28 pages, up from the prior round's 27) got its own, more detailed version of the Q1
story rather than the paper's condensed one:

**Note (2026-09-19): this bullet list originally quoted the methodology doc verbatim in several places.
Replaced with a paraphrase** — the methodology doc's raw files were also removed from this public repo, for
the same reason as the paper's (see `../papers/README.md`'s header note).

- **New §5.2, "Extending batch validation further: Q1"** — contains the same diagnostic narrative as the
  paper's §5.3, but in more depth: it splits the compound/chained-condition category out into its two
  sub-counts (107 compound, 50 chained) rather than merging them into the paper's single 43%/157-file
  figure, and closes by restating the post-fix residual gap (0.5% correct, 2.4% wrong) as a much smaller,
  more honest number than the pre-fix starting point.
- **§6.1 corrected** — the old text overclaimed that GuardedInput matched "every" real Q1 submission
  tested, which stopped being accurate once the pre-fix 76.8%/64.2% figure (and even the 99.5%/97.6%
  post-fix residual) were known; the revised text drops that overclaim and instead just states the
  structural-shape relationship to `search`, plus a forward-pointer to the new §5.2.
- **A new canonical bug #22** in the §7 table (extending the table this log has tracked from 13 → 19 → now
  22 entries), covering the same symptom/root-cause/fix already described above (364 of 383 zero-scores
  from `SHARED_BINDING`'s three blind spots; the same four-part code fix; coverage rising to 99.5%/97.6%
  with zero regressions). **This entry correctly says "383," not "526"** — confirming the "526" typo found
  above is isolated to the `test_real_data.py` code comment and does not appear anywhere in the methodology
  doc's own canonical bug table.
- **A new §9 Limitations bullet** — restates the post-fix residual gap (0.5% correct, 2.4% wrong) as the
  genuine coverage-gap portion identified from the start (19 submissions where the loop or test primitive
  is truly absent, not a structural-matching issue), noting it wasn't investigated further given the small
  count. (This "19" is the pre-fix count; see the "17 vs 19" reconciliation above, derived independently by
  this log, not stated in the methodology doc itself.)
- **Confirmed, per the conversation's own explicit exchange, that the consolidated Table 4 / §5.5 addition was made
  to the paper only, not to the methodology doc** — Sonia asked whether the same consolidated table should
  go into the methodology doc too, and the answer was no, that table lives only in the paper. This is why
  the methodology doc's page count (28) did not change between the two paper revisions described above,
  while the paper's did (20→21→22).
- **Genuineness check, `python-docx`:** `Competency_Extraction_Methodology.docx` has 143 paragraphs and 7
  tables; its own `dcterms:created`/`modified` metadata (2026-08-05T13:58:00Z) matches its PDF's `pdfinfo`
  `CreationDate` (13:58:02 UTC) to the second, consistent with genuine same-session docx→PDF export rather
  than a mismatched or backdated file.
- **A minor rounding discrepancy, newly flagged**: the §5.2 residual-gap sentence above says "the
  23.2%/35.7% the batch run started from." 100 − 76.8 = 23.2 ✓, but 100 − 64.2 = 35.8, not 35.7 — a
  1-tenth-of-a-point rounding slip in the doc's own prose, not a computation this log can otherwise
  attribute to a different rounding convention (both source figures, 76.8% and 64.2%, are themselves
  already-rounded conversation-reported figures, so the discrepancy is internal to the doc's own arithmetic on its
  own stated numbers). Flagged for completeness; does not affect any of the real, CSV-verified figures
  above.

### Evidence status: `real_csv`, for the first time, across all of Q1-Q4

This round is the first time any of Q1, Q2, Q3, or Q4's headline percentages are backed by a real,
independently-recomputable CSV rather than being `conversation_reported_only` — closing a gap this log has flagged
as open since early in the project ("no batch scripts or CSVs exist for the 90.4% Q2, 94.0% Q3, 77.6% Q4,
or LinearSearch's Q1 figures, unlike Q5"). `configs/stage_manifest.yaml`'s `q1_final`/`q2_final`/
`q3_final`/`q4_final` stages are updated accordingly below, alongside a new stage documenting the Q1
`SHARED_BINDING`/`all_names` fix itself (evidence: `real_csv`, before/after 76.8%/64.2% → 99.5%/97.6%,
zero regressions per the code diff being purely additive — though "zero regressions" specifically remains
conversation-reported, as noted above, absent a supplied pre-fix CSV).

---

## Q4/Q2 embedding cross-validation — `2. The Colab embeddings validation.docx` + `q2_q4_embeddings_crossvalidation_with_Results.ipynb` + `Copie_de_q2_q4_embeddings_crossvalidation.ipynb`

Sonia supplied a conversation export and two notebooks (one real, executed; one an unexecuted copy), continuing the
Q1-Q4 batch-validation thread with an embedding cross-validation extending the already-verified Q5
methodology (`ast_taxonomy_crossvalidation.ipynb`, "The real 10-seed sweep" section above) to Q4 and Q2.
**Real date: 2026-08-05, 17:40** — read directly from the conversation export's own opening line, "05/08/2026 at
17:40" (the docx's own `dcterms:created`/`modified` metadata reads 2026-09-11/2026-09-13, which — per the
same distinction this log has drawn repeatedly — reflects when the conversation was exported/saved as a file, not
when the underlying conversation happened; the DD/MM/YYYY marker inside the conversation itself is the real date,
consistent with the export-vs-content-date convention established earlier in this log). This places the
round later the same evening as the batch-validation run and the Q1 `SHARED_BINDING` fix (both also dated
2026-08-05) — a third, same-day continuation of that round's work.

### Scoping decision, quoted in full: why Q4 and Q2, not Q1 and Q3

The conversation's own opening reasoning, before any code was written: "What made Q5's embeddings check
meaningful: FindExtremum genuinely splits into two real, well-populated strategies (manual loop vs.
max()/min()), so there was a real taxonomic distinction worth asking an independent method to recover."
Checking each of Q1-Q4 against that criterion: "Q4 — yes, directly analogous... SortByKey =
ANY(BubbleSortPass, TopKPattern) is exactly the same shape as Q5"; "Q2 — yes, with one adjustment...
AccumulateThenCount is only 0.7%... too rare for a stable centroid, the same problem novel had in Q5";
"Q1 and Q3 — not a good fit... both are single-strategy competencies (GuardedInput/LinearSearch,
SelectionStep) — their real finding was a structural-matching bug..., not a taxonomic split between
multiple legitimate strategies. There's nothing analogous for an embedding model to independently
'recover' there." This reasoning is sound and consistent with everything already independently verified
in this log about Q1/Q3 (the SHARED_BINDING fix, the .insert() fix) versus Q2/Q4/Q5 (real multi-strategy
`ANY`-composed taxonomies) — not taken on faith, but checked against this project's own prior findings.

### Independent verification: every figure recomputed directly from the notebook's own real output

`q2_q4_embeddings_crossvalidation_with_Results.ipynb` is confirmed genuinely executed (every code cell has
a non-`None` `execution_count` and populated `outputs`, checked directly, not assumed from the filename).
Every number below was recomputed independently from its printed per-seed table and pooled confusion
matrix, not copied from the conversation's own summary:

**Q4 (BubbleSortPass vs. TopKPattern):** 489 files labeled, 420 `topk` / 69 `bubblesort` (the 22.4%
unmatched "novel" group excluded, mirroring Q5's own `novel` handling). Recomputed mean accuracy across
the 10 listed per-seed values: 93.6% (SD 2.1%, range 89.8%-95.9%, `numpy`/`pandas` sample-std convention,
ddof=1) — exact match to the conversation's own quoted "93.6% ± 2.1%." Recomputing precision/recall/support
directly from the pooled confusion matrix (bubblesort→bubblesort 200, bubblesort→topk 4, topk→bubblesort
90, topk→topk 1176; 1,470 total) reproduces the printed classification report's every cell exactly:
bubblesort precision 0.69/recall 0.98/support 204; topk precision 1.00/recall 0.93/support 1266; accuracy
0.94. **This is a stronger, tighter result than Q5's own manual/builtin check (87.0% ± 2.3%, from "The real
10-seed sweep" section above)** — both the mean is higher and the spread is comparably tight. The
confusion-matrix asymmetry runs the *opposite* direction from Q5's: here `bubblesort` (precision 0.69,
recall 0.98) is the broad, easy-to-fall-into cluster and `topk` (precision 1.00, recall 0.93) is the
narrow, tight one — the reverse of Q5, where `builtin` was the tight cluster and `manual` the broad one.
The conversation's own structural explanation for this reversal — real bubble-sort implementations are homogeneous
(nested loops, a comparison, a swap — little room for variation), while the "find max, remove, append"
topk strategy admits more surface variety (different ways to find the max, different removal idioms), so
an unusual topk submission can drift into the tighter bubblesort cluster — is a plausible interpretation
consistent with the confirmed numbers, though (like all such structural narratives in this log) it is the
conversation's own reasoning, not independently provable from the embeddings alone.

**Q2 (counter vs. functional):** 581 files labeled, 564 `counter` / 17 `functional` (`AccumulateThenCount`,
~0.7%, dropped as too rare for a stable centroid — the same reasoning that excluded `novel` from Q5's
headline number). Recomputed mean accuracy: 95.9% (SD 1.6%) — matches the conversation's quoted figure. **This
headline number is independently confirmed to be a class-imbalance artifact, not a validated finding**:
`counter` is 96.8% of the pooled 1,750-prediction test set (1,694/1,750, computed directly from the pooled
confusion matrix) — a classifier that always predicted `counter` regardless of input would score *higher*
(96.8%) than what this classifier actually achieved (95.9%). The number that actually matters,
`functional`'s own precision/recall, recomputed directly from the same confusion matrix
(counter→counter 1663, counter→functional 31, functional→counter 41, functional→functional 15): precision
15/(15+31) = 0.326 ≈ 0.33, recall 15/(15+41) = 0.268 ≈ 0.27, support 56 — exact match to the conversation's own
figures. Both directions of error are present in similar magnitude (31 vs. 41), consistent with 17 real
examples being too few for a stable conclusion, not a real negative structural finding. The conversation's own
explicit recommendation, quoted in full: "don't report this as a finding at all, positive or negative...
17 real examples is not enough to determine whether it can [recover the split]... If you want this
documented anywhere, the honest version belongs in Limitations, not Results... consistent with how we
already handled Q1's smaller while-condition gap (8 files) and Q5's novel group." This recommendation is
methodologically sound and consistent with this log's own standing evidence discipline — logged here
verbatim rather than smoothed into a headline percentage.

### A real, diff-confirmed difference between the two notebooks, not narrated in the conversation

`Copie_de_q2_q4_embeddings_crossvalidation.ipynb` is confirmed genuinely unexecuted (every code cell has
`execution_count: None` and zero outputs — checked directly). Direct `diff` of the two notebooks' code
cells (20 cells each, markdown and code) finds **exactly two differing cells, both a Drive folder-path
fix**: the unexecuted copy uses `Q4_FOLDER = f"{PROJECT_DIR}/refactory/data/question_4/code"` (and the
identical pattern for Q2), matching the layout the conversation's own scope note expected ("same layout as Q5");
the executed, real-output version instead uses `Q4_FOLDER = f"{PROJECT_DIR}/data/question_4/code"` — no
`refactory/` prefix — and it worked (489/489 Q4 files cached, 581/581 Q2 files cached, no "0 cached embeddings"
symptom in either). The conversation's own text warns this exact failure mode is possible ("If Q2/Q4's data lives
somewhere else in your Drive, the way Q1's did initially, you'll hit the same '0 cached embeddings' symptom
we debugged before") but does not narrate this specific fix happening for Q2/Q4 in this round's own
transcript — the fix itself is real and diff-confirmed (not invented), but *why* Sonia's Drive layout for
Q2/Q4 differs from Q5's own (`refactory/data/question_5/code`, per the already-verified Q5 notebook logged
earlier in this project), and what exactly happened with "Q1's" folder initially, are not independently
checkable from any artifact supplied to this project — the "Q1's did initially" claim is conversation-asserted
only. **Resolved 2026-09-17 — see "A direct clarification from Sonia" section below**: this is not
actually a Q2/Q4-vs-Q5 discrepancy specifically — the identical unexecuted-uses-`refactory/data/...`,
executed-uses-`data/...` pattern recurs for Q5's own notebook pair too (see the parallel note below, "A
real code diff exists between the two notebook copies"), so the real pattern is *template/unexecuted
copy vs. actual execution environment*, consistent across all three questions, not specific to Q2/Q4.

### Evidence status: `real_notebook_output`, matching Q5's own 10-seed sweep, for the same reason

Both new stages (`q4_taxonomy_embedding_crossvalidation_10seed_pooled`,
`q2_taxonomy_embedding_crossvalidation_10seed_pooled` in `configs/stage_manifest.yaml`) are tagged
`evidence: real_notebook_output`, not `real_csv`: the notebook's own last cell saves
`q4_embeddings_crossvalidation.csv`/`q2_embeddings_crossvalidation.csv` (one row per seed/file prediction)
to Sonia's Drive, but neither file was supplied to this project — only the real, executed notebook's own
printed per-seed table and pooled confusion matrices, independently re-verified above and by
`scripts/regenerate_q2q4_taxonomy_crossvalidation.py` (all checks pass). **This is explicitly NOT the same
experiment as `configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits` entry**, which remains entirely
`PENDING` — that entry refers to a still-unsupplied companion-paper train/test-split experiment, while this
notebook validates the AST taxonomy's own Q4/Q2 splits using embeddings purely as an external check,
mirroring `q5_taxonomy_embedding_crossvalidation` rather than `table5.q5_topk_splits` (the same distinction
already drawn for Q5 earlier in this log). Neither new stage is cited in the published paper as of this
writing (`required_for_publication: false` for both) — Q4's own strong, tight result would be a natural
candidate for a future paper revision; Q2's is explicitly recommended against publication as a headline
figure by the source conversation itself.

---

## The Q4 embedding result written into the paper — `Docs_after adding embed for Q4.zip`

Supplied as a bare zip with no accompanying conversation export this round — `Structural_Competency_Extraction_Paper.pdf`
and the matching `.docx`. Per this log's usual dating discipline (real content date, not upload date), the
date used below is the files' own internal metadata, since no conversation text was supplied to override it:
`pdfinfo` reports `CreationDate: Wed Aug 5 18:02:35 2026 UTC`; the docx's own `dcterms:created`/`modified`
both read `2026-08-05T18:02:31Z`. That is the same day as, and about four hours after, the prior
`..._final_22p.pdf` revision (14:05:28 UTC, see the "Real batch-validation RESULTS for Q1-Q4" section
above) — a third same-day paper revision, not a new day's work.

### Confirmed genuinely distinct, not a duplicate upload

`pdftotext -layout` on both files, full diff: 390 changed lines, but the overwhelming majority are
line-wrap/pagination reflow only (table column widths and paragraph breaks shifting because the added text
pushed content down — e.g. Table 2's "Constraint"/"Checks" columns reflow with no wording change, and the
20-defect table on pp.15-17 reflows across a page boundary with no cell content change). Still 22 pages,
no section renumbering — confirmed by checking every visible section number against the prior 22p file:
identical throughout.

### Exactly three substantive content changes

**Note (2026-09-19): this section originally quoted each change verbatim. Replaced with a paraphrase** —
same reason as the §5.5 note above; see `../papers/README.md`'s header note.

**1. Abstract.** Now reports both taxonomic-split agreement figures side by side (87.0% ± 2.3% for Q5,
93.6% ± 2.1% for the new Q4 split) instead of only Q5's.

**2. §5.6, restructured and extended** (retitled to cover "two taxonomic splits" instead of one). The
existing Q5 material survives under its own "Q5: manual vs. builtin" subheading; a new "Q4: BubbleSortPass
vs. TopKPattern" subsection applies the identical embedding-classification methodology to Q4's split.
**Reported figures** (independently verified — see `scripts/regenerate_q2q4_taxonomy_crossvalidation.py`
and `configs/stage_manifest.yaml`'s `q4_taxonomy_embedding_crossvalidation_10seed_pooled` entry): 93.6%
mean agreement across 10 splits (SD 2.1%, range 89.8%–95.9%), pooled precision/recall bubblesort
0.69/0.98, topk 1.00/0.93, pooled support 204 bubblesort / 1,266 topk. Higher and more stable than Q5's own
figure; the misclassification asymmetry runs the opposite direction (bubblesort is the broad, high-recall
class; topk the tight, high-precision one), attributed to bubble-sort implementations being structurally
more homogeneous in real code than topk implementations, which admit more variety in how the extremum is
found and removed. The section's closing paragraph frames both splits' results together as independent
evidence that each taxonomic distinction is real and recoverable rather than an artifact of the taxonomy,
and notes the consistent, mechanistically-explicable asymmetry between the two splits as a further finding
in its own right.

**3. §7 Limitations.** The existing "harder problem" sentence is generalized from referring only to the Q5
check to referring to both taxonomic-split checks.

### Independent verification: exact match, no discrepancy

Every number in the new Q4 paragraph was already independently recomputed from the notebook in the prior
round, before this paper revision was ever supplied — see the "Q4/Q2 embedding cross-validation" section
above and `configs/stage_manifest.yaml`'s `q4_taxonomy_embedding_crossvalidation_10seed_pooled` entry:
93.6% mean, 2.1% SD, 89.8%-95.9% range, 204 bubblesort/1,266 topk pooled support, bubblesort
precision 0.69/recall 0.98, topk precision 1.00/recall 0.93 — all match the paper's new text exactly. This
round's finding is that the paper is simply writing in an already-verified result, not introducing a new
empirical claim; there is nothing here to reconcile or flag as a discrepancy, unlike the "526"/"35.7%"
slips found in an earlier round.

### Evidence status

No evidence-tier change: `q4_taxonomy_embedding_crossvalidation_10seed_pooled` remains
`evidence: real_notebook_output` (the underlying source is still the notebook's own printed output, not a
newly-supplied CSV), but its `source` field in `configs/stage_manifest.yaml` now also cites this paper file
and section as a second, verbatim-matching corroborating source — the same treatment already given to
`q5_taxonomy_embedding_crossvalidation_10seed_pooled`'s own paper citation. Both new files are preserved as
`papers/2026-08-05_Structural_Competency_Extraction_Paper_final_22p_q4embedding_added.pdf`/`.docx`; see
`papers/README.md` for the full table entry and diff.

---

## The Q4/Q2 embedding cross-validation raw CSVs supplied — `q4_embeddings_crossvalidation.csv` + `q2_embeddings_crossvalidation.csv`

Supplied as two bare CSVs, no accompanying conversation this round. These are exactly the two per-seed/per-file
prediction files the "Q4/Q2 embedding cross-validation" section above already named and flagged as
supplied-to-Drive-but-not-to-this-project: `q4_embeddings_crossvalidation.csv` (1,470 rows) and
`q2_embeddings_crossvalidation.csv` (1,750 rows), columns `file, seed, true_label, predicted` — one row
per seed/file test-set prediction across the 10-seed sweep.

### Independently recomputed from the raw rows, not the notebook's printed summary — exact match

For each file: grouped rows by `seed`, computed per-seed accuracy (`true_label == predicted`), then
mean/sample-stdev across the 10 seeds; separately pooled all 10 seeds' rows into one confusion matrix and
derived precision/recall/support per label from it. Results, compared against everything already logged
from the notebook's own printed output in the "Q4/Q2 embedding cross-validation" section above:

- **Q4**: per-seed accuracies (147 test rows every seed) 93.20%, 91.84%, 93.20%, 95.24%, 94.56%, 95.92%,
  91.16%, 89.80%, 95.24%, 95.92% → mean 93.61%, sample SD 2.13% (rounds to the reported "93.6% ± 2.1%"),
  range 89.80%–95.92% (reported "89.8%–95.9%"). Pooled confusion matrix from the raw rows:
  `{bubblesort: {bubblesort: 200, topk: 4}, topk: {bubblesort: 90, topk: 1176}}` — identical, cell for
  cell, to the matrix already logged from the notebook's printed output. Precision/recall: bubblesort
  0.6897/0.9804 (support 204), topk 0.9966/0.9289 (support 1266), pooled accuracy 0.9361 — all match the
  previously-logged rounded figures (0.69/0.98, 1.00/0.93, 0.94) exactly.
- **Q2**: per-seed accuracies (175 test rows every seed) 97.14%, 94.86%, 96.57%, 97.14%, 92.00%, 97.14%,
  96.00%, 96.00%, 95.43%, 96.57% → mean 95.89%, sample SD 1.57% (rounds to the reported "95.9% ± 1.6%").
  Pooled confusion matrix: `{counter: {counter: 1663, functional: 31}, functional: {counter: 41,
  functional: 15}}` — identical to the previously-logged matrix. Precision/recall: counter 0.9759/0.9817
  (support 1694), functional 0.3261/0.2679 (support 56), pooled accuracy 0.9589 — match the
  previously-logged rounded figures (0.98/0.98, 0.33/0.27, 0.96) exactly. The majority-class-baseline
  argument (counter = 96.8% of the pooled test set, 1694/1750) also reconfirms exactly from the raw rows.

**No discrepancy anywhere.** Every figure this round traces to the identical underlying predictions the
notebook printed a summary of — this is a confirmation of the existing record, not a correction to it.

### Files added, script rewritten to read the real data directly

New files: `data/labels_scores/q4_embeddings_crossvalidation.csv`, `q2_embeddings_crossvalidation.csv`
(exact copies of the supplied files). `scripts/regenerate_q2q4_taxonomy_crossvalidation.py` was rewritten
to read these two files directly and compute every figure from them — mirroring how
`scripts/regenerate_taxonomy_crossvalidation.py` already works for Q5's own two real-CSV single-split
stages — rather than checking a set of numbers hand-transcribed from the notebook's printed output.
Re-run: all checks pass (`OK` on every line, including the Q2 majority-baseline check).

### Evidence status: upgraded from `real_notebook_output` to `real_csv`

`configs/stage_manifest.yaml`'s `q4_taxonomy_embedding_crossvalidation_10seed_pooled` and
`q2_taxonomy_embedding_crossvalidation_10seed_pooled` entries are now `evidence: real_csv`, each with a
`data_file` field pointing at its CSV. The stages' `source`, `verification`, and `note` fields were
extended (not overwritten) to record both provenance stages — real_notebook_output first, then upgraded to
real_csv once the raw predictions arrived — so a reader can see the evidence tier's own history, not just
its current state. This closes the one remaining "supplied notebook output, but not the underlying CSV"
gap for this pair of stages; the same gap still applies to 9 of Q5's own 10 seeds (only seed 0's raw
predictions were ever supplied there — see `q5_taxonomy_embedding_crossvalidation_10seed_pooled`, still
`real_notebook_output`), and to the still-entirely-unsupplied `table5.q4_sortbykey_splits`/`q5_topk_splits`
companion-paper scope, which this round's CSVs do not touch.

---

## Semantic backup layer validation — the layer's actual job, first real AUC (inverted) — `semantic_backup_layer_validation.ipynb` + `Semantic Backup_Second Role_08_08_Before clustering.docx`

**Real date: 2026-08-08**, per the conversation export's own header ("Steps for semantic Backup (second role)
08-08-2026", DD-MM-YYYY). Three days after the Q4/Q2 embedding-taxonomy round above.

### What this closes

Every embedding check so far in this project (Q5/Q4/Q2 taxonomy cross-validation) tested whether
embeddings *agree with an existing AST split*. This round is the first real attempt at the semantic backup
layer's actual job: separating genuinely-novel-correct submissions from genuinely-wrong ones, with no AST
information at all. It's explicitly built to fix two problems already diagnosed and left unresolved in
`detectors/2026-07-29to30_semantic_colab_validation/`: the contaminated-comparison-group problem (an
earlier attempt restricted "wrong" to submissions that also scored 0 structurally, accidentally selecting
for submissions that already look correct-ish; this notebook uses ALL wrong-labeled submissions as the
negative class instead) and single-draw instability (this notebook bootstraps the exemplar registry itself
across 10 independent draws of `N_EXEMPLARS=8`, reporting AUC mean±SD across draws plus a separate pooled
AUC/ROC).

### The notebook itself: confirmed entirely unexecuted

Direct JSON inspection, as in every prior round: 22 cells (11 markdown, 11 code), every code cell's
`execution_count` is `None`, every code cell's `outputs` list is empty. Consistent with the user's own
framing this round ("here the first part before clustering").

### A real, quoted result — from a run this exact notebook copy doesn't reflect

The conversation quotes real printed output from "Result of cell 13" and "result of cell 15." **First, the
important correction the conversation itself makes, quoted in full:**

> "this is NOT 'no separation.' Look at the scale — AUC=0.5 means no separation (chance). AUC=0.098 is
> nowhere near 0.5; it's close to 0, at the opposite end of the scale from 1.0. An AUC near 0 means the
> model separates the two groups very well — just in the reverse direction from what the layer is designed
> to assume."

Genuinely-wrong submissions score *systematically more* similar to correct exemplars (~0.94–0.96, every
one of 10 runs) than genuinely-novel-correct submissions do (~0.79–0.81) — "not noise... std=0.039 on the
AUC across 10 different exemplar draws is tight." Cell 15's pooled figure: "Pooled AUC across all 10 runs
(1510 scored pairs): 0.097. Suggested threshold for ~80% recall on novel-correct: 0.719 (false-positive
rate at this point: 0.997)."

**Why, per the conversation's own explanation**, connecting to the paper's own §5.1 finding: most wrong-labeled
submissions aren't wrong because they attempted something different — they correctly implement the
standard pattern and fail on an unrelated edge case, so they read as close to a "textbook" correct
exemplar. `novel_correct` submissions are, by definition, doing something atypical (that's the entire
reason the AST rules missed them), so they read as *less* similar to a registry built from typical correct
examples, even though they behave correctly. As designed, "high similarity to a correct exemplar" turns
out to be a better signal for "attempted the standard approach" than for "is correct." Deployment
relevance, also quoted: to catch 80% of `novel_correct`, the required threshold also flags 99.7% of
`genuinely_wrong` — not a useable filter as designed.

### A real, flagged, unresolved discrepancy: the conversation's cell numbers don't map cleanly onto this notebook

"Cell 13" and "cell 15," under any simple counting convention over this notebook's own 11 code cells
(0-indexed 0–10), would land on the bootstrap loop (8th code cell) and the pooled-ROC calculation (9th code
cell) respectively — not literal indices 13/15. Flagged, not resolved: it's possible extra cells were run
or re-run in the actual session that this "before clustering" copy doesn't contain. The result itself is
internally corroborated regardless (the bootstrapped mean AUC and the pooled AUC agree almost exactly, as
expected if both come from the same underlying data) and matches the notebook's own described methodology
exactly (10 bootstrap runs, `N_EXEMPLARS=8`, `FindExtremum`/Q5).

### Evidence status: `conversation_reported_only` — real, strong, deployment-relevant, not yet artifact-backed

New `configs/stage_manifest.yaml` entry:
`semantic_backup.backends.codet5p_bootstrap_novel_vs_wrong_auc`. This is the first real AUC/ROC number
this project has ever produced for the layer's actual novel-vs-wrong task — resolving, with an honest
inverted-negative answer, the "no valid AUC yet" gap flagged since `2026-07-29to30_semantic_colab_validation`.
Neither the executed notebook nor the two CSVs its own final cell would have saved
(`semantic_backup_bootstrap_summary.csv`/`semantic_backup_pooled_scores.csv`) were supplied. New checkpoint
folder: `detectors/2026-08-08_semantic_backup_layer_validation/`. **Not the same experiment as**
`table5.q4_sortbykey_splits`/`q5_topk_splits` (still entirely unsupplied) or the Q4/Q2/Q5 embedding
*taxonomy* cross-validations (which test agreement with an existing AST split, not this layer's actual
job).

---

## A third paper revision (2026-08-08) — new §7, "The Semantic Backup Layer: Architecture Overview"

Supplied inside `files_Docs with _section for semantic_backup_layer.zip` (containing a full docx, its PDF
sibling, a no-images docx sibling, and a `.md` export), alongside a standalone
`Structural_Competency_Extraction_Paper_no_images_before_cluster.docx` explicitly supplied as a "before"
baseline for diffing. No conversation accompanies this specific file trio — real dates come from internal
metadata alone (docx `dcterms:created`, PDF `pdfinfo CreationDate`): "before_cluster" baseline
2026-08-08 10:44:27 UTC; zip's full docx 10:58:55 UTC; its PDF 10:58:59 UTC; its no-images docx
10:59:11 UTC — a 15-minute window.

### The "before_cluster" baseline, confirmed identical to the prior logged revision

Direct `pandoc`-then-`diff` against `papers/2026-08-05_Structural_Competency_Extraction_Paper_final_22p_q4embedding_added.docx`:
the only difference is the absence of the two pre-existing figures (Figure 1, Figure 2, both real embedded
PNGs — confirmed by checking the zip's own docx's `word/media/` entries: `rId25.png`/`rId38.png`, same
byte sizes as the already-logged 2026-08-05 revision's own media files), consistent with a no-images
export. This is the confirmed starting point, not a new revision in its own right.

### Exactly one substantive content change

**Note (2026-09-19): this section originally quoted the new §7 in full. Replaced with a paraphrase** — same
reason as above. A new §7, "The Semantic Backup Layer: Architecture Overview," is inserted between §6
(Discussion) and the old §7 (Limitations, renumbered §8; Conclusion §8→§9; References unaffected). It
explains the semantic-similarity backup layer's purpose and design in plain terms: it exists to flag
submissions that are likely correct but that the structural rules missed because no rule was ever written
for that particular strategy, not to auto-grade or close the gap itself. It describes the mechanism
(comparing a submission's code embedding, via Salesforce/codet5p-110m-embedding, against a small
per-competency registry of known-correct exemplars; a high similarity score is framed explicitly as "a
signal for human review," never folded into `final_score`) and states plainly that nothing in the section
constitutes a validated result — the layer's actual accuracy, its exemplar registry, and any decision
threshold are explicitly deferred to the companion paper.

The renumbered Limitations section (old §7 → new §8) also gets a small wording change, pointing at the new
§7 instead of describing the layer inline: "Finally, a semantic-similarity backup signal... was
constructed on top of this model..." → "Finally, the semantic-similarity backup layer described in
Section 7 was not empirically validated...". Confirmed, by full diff, that nothing else in the 22/23-page
document changed — every prior section, every figure, the References, all byte-identical.

### This section does NOT include this round's own inverted-AUC finding

Consistent with §7's own text deferring all accuracy/validation claims to "the companion paper" — the real
AUC=0.097 result logged above (same round, same day) is not written into the paper anywhere yet.

### New files

`papers/2026-08-08_Structural_Competency_Extraction_Paper.docx`/`.pdf` (23 pages). The zip's no-images
docx and the standalone "before_cluster" baseline are not separately preserved in the repository — both
are confirmed content-subset duplicates (image-only differences) of files already preserved, so they carry
no unique evidentiary value beyond the diff already performed and recorded here.

---

## `Competency_Extraction_Methodology.docx` re-supplied — confirmed a byte-identical duplicate

Supplied again this round, alongside the files above. `md5sum` confirms it is byte-identical to
`methodology/2026-08-05_Competency_Extraction_Methodology.docx`, already in this repository and already
logged (see "The 2026-08-05 revision — bug #22, the Q1 fix" in `methodology/README.md`). No new content
this round; noted here only so a reader who sees this filename among this round's uploads doesn't wonder
whether it was examined.

---

## Semantic backup layer validation — the raw CSVs, then the executed notebook — `semantic_backup_bootstrap_summary.csv` + `semantic_backup_pooled_scores.csv` + `Copie_de_semantic_backup_layer_validation.ipynb`

Two further uploads this round, in immediate succession, both concerning the AUC finding logged above in
"Semantic backup layer validation — the layer's actual job, first real AUC (inverted)":

**First, the two raw CSVs** (Sonia: "ok, here are results", alongside two pasted chart images). These are
exactly the two files the unexecuted notebook's own final cell was written to save —
`semantic_backup_bootstrap_summary.csv` (10 rows, one per bootstrap run: `run, auc, novel_mean, novel_std,
wrong_mean, wrong_std, n_novel, n_wrong`; `n_novel=43`, `n_wrong=108` on every row) and
`semantic_backup_pooled_scores.csv` (1,510 rows: `run, file, group, similarity`). Independently recomputed
directly from the raw 1,510-row file, with no dependency on the summary file's own numbers being trusted:
per-run AUC (rank-based Mann-Whitney-U-equivalent, computed from scratch) and per-run `novel_correct`/
`genuinely_wrong` group means, for all 10 runs, exactly match `semantic_backup_bootstrap_summary.csv`'s own
values to floating-point precision. Mean AUC across the 10 runs = 0.098, SD = 0.039 — exact match to the
conversation's quoted "mean=0.098... std=0.039." Pooling all 10 runs' 1,510 scored pairs and computing one AUC =
0.097 — exact match to the conversation's quoted pooled figure. The 80%-novel-correct-recall threshold, found by a
manual ROC-threshold sweep (no sklearn dependency), = 0.719, at a 99.7% false-positive rate — exact match
to the conversation's quoted "threshold: 0.719 (false-positive rate at this point: 0.997)." **No discrepancy found
anywhere.** At this point I told Sonia I would hold this round open rather than finalize it, since she had
said mid-turn, "I'll send the notebook with execution too" — the executed notebook was still needed to
close the "cell 13/15" numbering question the earlier `conversation_reported_only` entry had flagged.

**Second, the executed notebook itself** (Sonia: "this is the notebook after run" — a single file,
`Copie_de_semantic_backup_layer_validation.ipynb`). **Note the reversed naming convention versus the
Q4/Q2 embedding round**: there, `Copie_de_q2_q4_embeddings_crossvalidation.ipynb` was the *unexecuted*,
outputs-stripped copy and the non-`Copie_de_` file carried real output. Here it is the opposite — Sonia's
own message is unambiguous ("after run"), so this is logged as stated, not silently normalized to match
the earlier round's pattern. **Corrected in a later round**: Sonia re-supplied this same file (content
verified byte-identical by md5sum) renamed to `semantic_backup_layer_validation_with_Results.ipynb`, fixing
this discrepancy — see "A naming correction" below.

Direct JSON inspection of this notebook confirms: 22 cells (11 markdown, 11 code, matching the unexecuted
original's structure exactly), and every code cell's `outputs` list is populated with real content —
CUDA/device info, a Google Drive mount confirmation and directory listing, Hugging Face model-download
progress logs, printed tables, and one embedded `image/png` chart output. Extracted and read the real
printed output of 8 of the 11 code cells directly, including:
- A **new sanity-check similarity pair for `codet5p-110m-embedding`**, never supplied in any prior round
  (the manifest's existing entry for this backend explicitly noted this gap): "related vs related:
  0.8398723602294922 / related vs unrelated: 0.3819599151611328" — a real, usable separation (unlike the
  `codebert` backend's documented anisotropy failure logged in the "Real-CodeBERT/CodeT5+ Colab validation"
  section above).
- `novel_correct` n=43, `genuinely_wrong` n=108 — matching the CSV counts above exactly.
- The full bootstrap table (10 rows) and the pooled-AUC/threshold summary — matching the conversation's quoted
  figures and the independently-recomputed CSV figures exactly, to the printed precision.

**However — one anomaly does NOT resolve, even in this "after run" copy**: every one of the 11 code cells'
`execution_count` field is `None`, despite the real, populated outputs. This means the conversation's own "Result
of cell 13" / "result of cell 15" references still cannot be mapped to actual cell positions under any
counting convention — the notebook that was explicitly supplied as proof of execution carries no positional
metadata to check that mapping against. Flagged as genuinely still open, not resolved by this notebook's
arrival, and not something to guess at.

**A real code diff exists between the two notebook copies** — exactly one of the 11 code cells differs.
`DATA_FOLDER` changes from `f"{PROJECT_DIR}/refactory/data/question_5/code"` (unexecuted original) to
`f"{PROJECT_DIR}/data/question_5/code"` (executed copy) — a Drive folder-path fix, identical in kind to the
one already found and logged in the Q4/Q2 embedding round (there, for Q4/Q2's own data folders; here, for
Q5's). Every other code cell is byte-identical between the two copies. **See "A direct clarification from
Sonia" below (2026-09-17)** for why this same unexecuted/executed split recurs identically across all
three questions.

**The embedded chart** was extracted directly from the executed notebook's own `image/png` cell output
(base64-decoded from the `.ipynb` JSON, 45,851 bytes, md5 `e0fcf18f91375fadc5a3dfe3c7900341`) and compared
against the chart image Sonia had separately pasted directly into conversation in the prior turn: visually
identical (same two-panel AUC-stability/similarity-distribution layout, same data), but byte-different
(different export resolution/pipeline) — not a discrepancy, just two renderings of the same underlying
result. The notebook's own embedded copy was preferred as the repository's preserved artifact, being the
more primary source.

**Evidence-tier upgrade**: `configs/stage_manifest.yaml`'s
`semantic_backup.backends.codet5p_bootstrap_novel_vs_wrong_auc` entry is upgraded from
`evidence: conversation_reported_only` to **`evidence: real_csv`**, `status: REAL_INVERTED_RESULT_CSV_BACKED`. A
new regeneration script, `scripts/regenerate_semantic_backup_auc.py`, recomputes every figure above
directly from the two raw CSVs (a from-scratch, no-sklearn-dependency AUC/ROC implementation, deliberately
kept dependency-light) and confirms `[OK]` across all checks. This is now the strongest evidence tier this
project uses — the same tier as the Q1-Q4 batch-validation results and the Q4/Q2 embedding-taxonomy
cross-validation.

**What this round does NOT change**: the result is still a *different* experiment from
`configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits`/`q5_topk_splits` (the still entirely
unsupplied companion-paper "10 train/test splits" experiment) and from the Q4/Q2/Q5 embedding-*taxonomy*
cross-validations (which test agreement with an existing AST split, not this layer's actual novel-vs-wrong
job). The paper's own new §7 (logged above) still does not include this finding, consistent with Sonia's
own framing that it belongs to the still-unsupplied companion paper.

---

## A naming correction — both semantic-backup notebooks re-supplied, renamed to match this project's convention

Sonia's message this round: "Here the two files renamed as the first ones, to keep the same nomination,"
uploading two files: `Copie_de_semantic_backup_layer_validation.ipynb` and
`semantic_backup_layer_validation_with_Results.ipynb`.

**Verified via `md5sum` against the repository's existing copies — this is a pure rename, not new
content:**

| Newly-uploaded filename | md5 | Matches existing repo file |
|---|---|---|
| `Copie_de_semantic_backup_layer_validation.ipynb` (18,844 bytes) | `1851eff7eead9aa70bac82989e63155a` | `semantic_backup_layer_validation.ipynb` — the original, confirmed-unexecuted notebook logged in "Semantic backup layer validation — the layer's actual job, first real AUC (inverted)" above |
| `semantic_backup_layer_validation_with_Results.ipynb` (314,621 bytes) | `cdadeec58c4358ea5ee071be6854b67e` | `Copie_de_semantic_backup_layer_validation_with_Results.ipynb` — the executed notebook logged in "Semantic backup layer validation — the raw CSVs, then the executed notebook" above |

Both md5s are exact matches to the files already in this repository. No cell content, output, or figure
changed — only the filenames.

**What this resolves**: the previous section flagged, explicitly, that the executed notebook had arrived
named `Copie_de_semantic_backup_layer_validation.ipynb` — the reverse of the Q4/Q2 embedding round's
convention (`Copie_de_...` = unexecuted there). Sonia's re-upload this round fixes exactly that: the
unexecuted copy is now named `Copie_de_semantic_backup_layer_validation.ipynb` and the executed copy is now
`semantic_backup_layer_validation_with_Results.ipynb` — matching the Q4/Q2 pattern
(`Copie_de_q2_q4_embeddings_crossvalidation.ipynb` / `q2_q4_embeddings_crossvalidation_with_Results.ipynb`)
exactly. This repository's own checkpoint files were renamed to match, and every reference to the old
filenames in `configs/stage_manifest.yaml` and the checkpoint's own `README.md` was updated accordingly.

**What this does NOT resolve**: the persisting `execution_count=None` anomaly in the executed notebook
(unchanged, since the file content itself didn't change) — still flagged as open in the sections above; a
rename alone cannot and does not resolve it.

**Per this project's evidence-preservation discipline**, the prior sections' own text (which described the
files under their original names, including the "reversed naming convention" flag) is left as written
rather than silently rewritten — this section, and forward-notes added to those sections, record the
correction instead.

---

## Embedding-guided clustering discovers a real Q5 delegation pattern — a code fix, and a genuine methodological catch

Sonia's message this round: "The second part contains the clustering notebook, their results and docs,"
uploading five files plus two pasted dendrogram images:

- `Chat_Semantic_Backup_Second_Role_08_08_After_clustering.docx` — conversation export (converted to `.txt`/`.md`
  via pandoc for full-text reading; unlike its "before clustering" predecessor, this export carries **no**
  internal conversation date-header).
- `Copie_de_semantic_backup_layer_validation.ipynb` — 32 cells / 16 code cells, confirmed entirely
  unexecuted by direct JSON inspection (`execution_count: null` and empty `outputs: []` on every code
  cell). This is the *unexecuted* extension of the semantic-backup-layer notebook already logged above,
  now carrying a new §11 clustering section.
- `semantic_backup_layer_validation_with_Results.ipynb` — 34 cells / 18 code cells, the executed
  counterpart, with real populated outputs on 14 of the 18 code cells (the other 4 confirmed genuinely
  empty by direct inspection — one cell has no source and no output at all, not a gap in what was
  supplied).
- `files_extended_after_clustering.zip` — containing `competency.py`, `test_real_data.py`, and
  `topk_report_EXTENDED2.csv` (526 rows), a real code fix and its real batch-validation run.
- `Structural_Competency_Extraction_Paper.docx` — a fifth paper checkpoint, same day.
- Two pasted images, both dendrogram charts — confirmed visually and via extraction to match the executed
  notebook's own embedded chart output exactly (`chart_novel_correct_dendrogram.png`, extracted from cell
  13's output, md5 `e2d1bc4b603d4439bbeebf0d606a469e`).

**Dating**: no internal conversation-header this time, so the date is established via a same-day internal-metadata
chain instead: the zip's own `competency.py` file modification timestamp (2026-08-08 13:59:04) precedes the
new paper docx's internal `dcterms:created` (2026-08-08T14:06:13Z) by about seven minutes — both land on
2026-08-08, the same date already established for the semantic-backup-layer AUC round logged above, so
this is a later round on the *same* real day, not a new day.

### The clustering notebooks — a real §11 added to the semantic-backup-layer notebook

Both notebooks are direct extensions of the semantic-backup-layer notebook already in this repository (see
"Semantic backup layer validation" above) — same file lineage, now with a new §11 "clustering" section
appended: hierarchical clustering (`scipy.cluster.hierarchy.linkage`, cosine distance, `method="average"`)
applied to the embeddings of Q5's **43 correct-labeled "novel" submissions** — "novel" here defined the
same way the paper itself defines it (`FindExtremum_final == 0` in the original, unscoped
`topk_report.csv`), matching the paper's own "43 of the 48 novel submissions" text and every filename
quoted in the conversation. (This is worth stating precisely because an earlier pass of my own verification this
round mis-selected the population using `TopKPattern_final == 0` instead, giving 85/91 — an internal error
caught and corrected before anything was written to the repo; the notebook's own `COMPETENCY` variable is
`"FindExtremum"`, not `"TopKPattern"`.)

The persisting anomaly noted in every earlier round involving this notebook lineage recurs here too:
`execution_count` is `None` on every code cell in **both** the unexecuted and the executed copy, despite
the executed copy having real, populated outputs on 14 of its 18 code cells. Still open, still not resolved
by this round's arrival.

**A real methodological catch, independently verified from the executed notebook's own printed output
and matching the conversation's quoted text exactly:**

- A silhouette-score sweep over k=2..9 clusters was run first. The silhouette score was still *rising* at
  k=9, the edge of the tested range — the classic small-sample-overfitting signature (more clusters always
  looks better on 43 points if you never test past the edge), not a stable interior peak.
- Cutting the *same* dendrogram by a distance threshold (0.30) instead — rather than trusting the
  silhouette sweep's k=9 — recovered a structure that manual file-reading then confirmed was real, not an
  artifact of the metric: `{correct_5_192.py, correct_5_247.py}` (2), `{correct_5_011.py, correct_5_016.py}`
  (2), one dominant 38-file cluster, and `{correct_5_029.py}` (1, a singleton). This is presented, both in
  the conversation and in the notebook's own commentary, as the trustworthy cut — and it is what led directly to
  reading real files from the 38-file cluster and finding the delegation pattern below.

**Evidence tier for the clustering step itself**: `real_notebook_output`, not `real_csv`. No standalone
embeddings or distance-matrix CSV was ever saved by the notebook — only the dendrogram chart image and the
printed cluster-membership listing survive, both extracted directly from the executed notebook's real
output. This is a deliberately thinner evidence tier than the AUC finding logged in the round above (which
has raw per-file CSVs backing it), and is recorded as such rather than blurred together with it.

### The real code fix this discovery motivated

Reading real files from the 38-file cluster surfaced a cross-function delegation pattern that the existing
`DELEGATES` mechanism (already present in the codebase, but — per the conversation's own words — "never applied to
TopKPattern") had never been used to catch for Q5. Diffed directly against
`detectors/2026-08-05_q1_shared_binding_fix/` (the immediately preceding checkpoint):

- **`competency.py`** — exactly one new function, `detect_self_recursive()`, registering a new primitive
  `SELF_RECURSIVE` (an AST walk for a function directly calling itself) and its entry in
  `PRIMITIVE_DETECTORS`. 39-line diff total; nothing else in the file changed.
- **`test_real_data.py`** — `DELEGATES` added to the import line, then four new/changed competency
  registrations:
  - `TopKViaDelegate` — `components={"call": "CALL"}`, `coverage=ALL(["call"])`,
    `structural=DELEGATES("call", "TopKPattern")` — catches a helper function that repeats TopKPattern's
    own find-max/remove/append shape under a different function name.
  - `HasSubstantialWork` — `components={"loop": ("LOOP", "SELF_RECURSIVE")}`, `coverage=ALL(["loop"])`,
    `structural=None` — the check originally only recognized `LOOP` and completely missed a
    pure-recursion `merge_sort` helper found in this same cluster, which is exactly why the new
    `SELF_RECURSIVE` primitive above was needed.
  - `SortThenSlice` — `components={"call": "CALL", "output": "OUTPUT"}`, `coverage=ALL(["call", "output"])`,
    `structural=AND([DELEGATES("call", "HasSubstantialWork"), SEQUENTIAL(["call", "output"],
    max_line_gap=10)])` — catches a helper doing a genuinely different, general-purpose sort (a recursive
    `merge_sort`, or an in-place bubble-style sort found by direct file-reading) and then slicing the
    result, rather than TopKPattern's own repeated find-max loop.
  - `TopKPatternExtended` — `components={"direct": "TopKPattern", "delegate": "TopKViaDelegate",
    "sort_then_slice": "SortThenSlice"}`, `coverage=ANY(["direct", "delegate", "sort_then_slice"])`,
    `structural=None`, `allow_mixed_levels=True` (the same documented layering exception already used for
    `BubbleSortPass`, per canonical bug #19 above — not a new kind of exception).
- **`topk_report_EXTENDED2.csv`** — the real batch-validation run of the above against all 526 submissions;
  columns `file, label, error, TopKPattern_final, TopKPattern_missing, TopKViaDelegate_final,
  TopKViaDelegate_missing, SortThenSlice_final, SortThenSlice_missing, TopKPatternExtended_final,
  TopKPatternExtended_missing`.

**Independently verified, not just repeated from the conversation** — recomputed directly from
`topk_report_EXTENDED2.csv` via `common.config.coverage_pct`:

- Headline: `TopKPatternExtended` correct-side 91.9% (384/418), wrong-side 80.6% (87/108) — exact match to
  the conversation's and the new paper checkpoint's quoted figures.
- Zero regressions: every submission `TopKPattern` already caught, `TopKPatternExtended` still catches.
- 57 new catches over plain `TopKPattern` alone, breaking down as 17 caught via `TopKViaDelegate` (all 17
  of which *also* match `SortThenSlice` — full overlap, not an independent 17) plus 40 caught via
  `SortThenSlice` only.
- Two wrong-labeled submissions newly (and correctly, per their own test-suite label) caught by delegation:
  `wrong_5_011.py`, `wrong_5_101.py` — named explicitly, matching the conversation.

**An honest, uncharacterized false-positive caveat — not hidden.** `correct_5_416.py`'s helper is a
bubble-sort-style `.insert()`/`.pop()` shuffle that coincidentally satisfies `TopKPattern`'s abstract
loop/test/removal shape without actually implementing the find-max/remove/append pattern the check exists
to identify — a latent bug in `TopKPattern` itself, newly *exposed* (not created) by testing it against a
wider variety of real helper-function bodies than inline-only resolution ever reached. Manually
sample-checked 7 of the 17 `TopKViaDelegate` catches by reading the actual source: 6 genuine, 1 false
positive (~14% of the sampled subset) — explicitly **not** extrapolated to the full population. Both the
new paper checkpoint's own §8 Limitations and this repository's `configs/stage_manifest.yaml` flag Q5's
91.9%/80.6% as "very likely a slight overstatement by an uncharacterized amount" as a direct result — an
explicit, deliberate contrast with Q1's 99.5%/97.6%, which is fully row-verified rather than sample-checked.

**A real, explained baseline drift, confirmed independently.** `TopKPattern`'s own (non-extended)
correct-side coverage moved from 78.2% (327/418, the long-standing figure backing `q5_final.csv`) to 79.7%
(333/418) when re-measured against the current codebase for this round. Traced by the conversation to an
intervening, unrelated fix — Q1's `SHARED_BINDING`/`all_names` change — incidentally shifting a handful of
`TopKPattern`'s own combinatorial matches. Independently confirmed by direct diff of the two source CSVs:
exactly 6 correct-labeled files flip 0→1 (`correct_5_064.py`, `correct_5_159.py`, `correct_5_170.py`,
`correct_5_282.py`, `correct_5_321.py`, `correct_5_362.py`), zero wrong-labeled files change. Both figures
are real and both are preserved in this repository — `q5_final.csv` (78.2%/75.0%, the original) is not
amended in place; `q5_final_extended.csv` (91.9%/80.6%, the delegation-extended figure) is a new,
independently-dated stage added alongside it.

### A fifth paper revision, same day (2026-08-08)

`Structural_Competency_Extraction_Paper.docx` (internal `dcterms:created` 2026-08-08T14:06:13Z) folds this
finding into five places, confirmed by direct diff against the immediately preceding checkpoint: the
Abstract, §5.3, Table 4 (Q5's row now reads `TopKPatternExtended`, 91.9%/80.6%), a new paragraph in §6
Discussion describing the delegation mechanism and the clustering discovery that led to it, and a new
paragraph in §8 Limitations carrying the false-positive caveat above verbatim in substance.

### A striking, purely coincidental resemblance to an earlier fabricated guess

This repository's own `VERSIONING.md` already documents (see "Corrected from an earlier, guessed version
of this file," logged in an earlier round) that a now-deleted, explicitly-fabricated early scaffold —
built from the paper's prose alone, before any real checkpoint existed — guessed a Q5 progression of
"→ 79.7% → 91.9%," a fabricated `TopKPatternExtended` competency, and a nonexistent `SELF_RECURSIVE`
primitive built via `DELEGATES`. This round's **real, independent** work — with no possible awareness of
that deleted guess — has now produced exactly those ingredients for real: the same competency name, the
same `DELEGATES`/`SELF_RECURSIVE` mechanism, and a correct-side figure landing on 91.9% (with a real
intermediate 79.7% baseline, matching the guessed progression almost exactly). This is recorded here, and
in `VERSIONING.md` itself, as a notable coincidence worth knowing about — explicitly **not** as vindication
of the guessing methodology that produced the earlier scaffold: every *other* specific claim in that same
guessed version (the `NESTED`/`SEQUENTIAL`/`SHARED_BINDING` mechanism guesses, the Table-5 embedding
numbers, the semver ladder) remained wrong once real evidence arrived, and the real fix's wrong-label
figure (80.6%) and the real intermediate 82.1% whole-file stage were never guessed at all.

### Repository changes made this round

- New checkpoint folder `detectors/2026-08-08_q5_delegation_clustering_fix/` (`competency.py`,
  `test_real_data.py`, `topk_report_EXTENDED2.csv`, and a new `README.md` covering all of the above).
- `detectors/2026-08-08_semantic_backup_layer_validation/` extended with both new notebooks, the conversation
  export (docx + txt), and the extracted dendrogram chart image; its `README.md` extended with a new
  "clustering extension" section and a note on the fifth paper revision.
- New paper checkpoint `papers/2026-08-08_Structural_Competency_Extraction_Paper_after_clustering.docx`;
  `papers/README.md` extended with the diff summary above.
- `scripts/build_labels_scores_from_batch_reports.py` extended with a Q5 entry producing
  `data/labels_scores/q5_final_extended.csv` (526 rows; verified 91.9%/80.6% via `coverage_pct`).
- `configs/stage_manifest.yaml`: new stage `q5_final_extended`, new semantic-backup backend
  `novel_correct_clustering` (`evidence: real_notebook_output`), and an updated section-level note.
- `configs/table4_config.yaml`: Q5's row repointed from `TopKPattern`/`q5_final` to
  `TopKPatternExtended`/`q5_final_extended`.
- New script `scripts/regenerate_q5_delegation_breakdown.py`, checking baseline drift, headline coverage,
  zero regressions, the new-catch breakdown, and the named wrong-labeled delegate catches against hardcoded
  expected values — all `[OK]` on a fresh run.
- `scripts/regenerate_q5_percentages.py` docstring and `Q5_STAGE_ORDER` updated to include the new stage.
- `README.md` (root), `docs/KNOWN_CAVEATS.md`, `VERSIONING.md`, and `data/labels_scores/README.md` all
  updated with cross-referenced summaries of the above (see each file directly for exact wording).
- `detectors/CHANGELOG.md` checked for stale references to this round's new competencies — none found —
  but confirmed to already be stale/incomplete for unrelated reasons (stops at `2026-07-28_fixQ4`, missing
  roughly seven later real checkpoints logged earlier this session). Deliberately left unfixed this round:
  out of scope, and a partial fix would look worse than the existing, at-least-consistent gap.

**What this does and does not resolve from "Still-pending items" below**: this round is a *structural*
detector fix motivated by a clustering discovery, not the still-entirely-unsupplied companion-paper
"10 train/test splits" embedding experiment (`configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits`/
`q5_topk_splits`) — those remain a distinct, still-open thread, unaffected by this round.

---

## A direct clarification from Sonia (2026-09-17) — why the Drive folder layout differed between notebooks

**Source note on evidence type**: this entry departs from this log's usual sourcing (a supplied artifact
or conversation-export document) in one respect — it records a direct, real-time statement Sonia gave in this
audit conversation itself, in response to a question about the open item below, rather than something
read out of a supplied file. It is logged with the same discipline as any other claim: attributed plainly
to its actual source (Sonia, stated directly, this date) rather than blurred into the artifact-sourced
material around it, and not extended beyond what she actually said.

**The open item, as it stood**: two prior sections of this log (the Q4/Q2 embedding cross-validation round,
and the Q5 semantic-backup-layer notebook round) each independently found the same shape of discrepancy —
an "unexecuted copy" notebook using a Drive path with a `refactory/` prefix
(`f"{PROJECT_DIR}/refactory/data/question_N/code"`), while the corresponding *executed*, real-output
notebook used the same path without that prefix (`f"{PROJECT_DIR}/data/question_N/code"`) — and it worked.
This recurred identically for Q5's own notebook pair and for the Q2/Q4 embedding notebook pair. Nothing in
any supplied artifact explained *why* the layout differed, only that it did, and that the no-`refactory/`
form is the one that actually ran successfully in every case.

**Sonia's direct explanation, asked and answered in this conversation**: she worked in two different
places — i.e., two different working environments/Drive mounts across the project's timeline — which is
why the "template"/unexecuted-copy notebooks (apparently authored or copied from one environment) carry the
`refactory/` prefix, while every notebook that was actually executed and produced real output was run from
the other environment, without that prefix. She confirmed the real, canonical layout is the one without the
prefix: `data/question_N/code`.

**What this resolves**: the "why" question flagged as open in both the Q4/Q2 embedding section and the Q5
semantic-backup-layer section above is now answered, directly by Sonia, rather than left as conversation-asserted
speculation or guessed at. It also corrects a framing error in this log's own earlier wording: the
discrepancy was described in the Q4/Q2 section as being between "Q2/Q4's own layout" and "Q5's own layout,"
as if Q5 used one convention and Q2/Q4 used another — but the same executed-vs-unexecuted split recurs
*within* Q5's own notebook pair too (see the "real code diff exists between the two notebook copies" note
in the semantic-backup-layer section above). The real, single explanation covering both observations is
Sonia's own: two working environments, one of which used the `refactory/` prefix and was never actually run
successfully, the other of which used the bare `data/` path and is what every real execution in this
project's evidence actually reflects.

**What this does not change**: no figure, finding, or evidence tier is affected — this was always a
path-string difference between a template copy and its executed counterpart, with the executed copy's
figures already being what every reported number in this project traces back to. Per this project's
evidence-preservation discipline, the original sections' text (describing the discrepancy as unexplained)
is left as written, with forward-pointing notes added at each — not rewritten — recording this resolution.

---

## The "mine_exemplars" thread: two reference documents, an explicit scoping decision, then real code

### Context documents received first, not yet acted on

Sonia opened this thread by supplying two documents "to know what are the possible fixes" before
sending real artifacts: `Competency_Extraction_Methodology_V2.docx` (dated 2026-08-13T19:57:06Z) and
`Structural_Competency_Extraction_Paper_v1_2.docx` (a sixth same-day paper revision, dated
2026-08-08T14:17:43Z, ~11 minutes after the "after clustering" checkpoint already in this repo). Both
were read and diffed in full against their immediate predecessors. They describe a substantial,
already-"finished" state going well beyond exemplar mining alone: a real semantic-backup-layer
SAME/CROSS/UNRELATED validation (final registry: 10 competencies, 27 exemplars, "partly real-mined,
partly hand-written," lexical 90.6%/74.1%, codet5p 84.2%/81.5%, after fixing a 40%-capping harness bug
and a DelegatesUniqueness scope-mismatch bug), a Q2 taxonomy correction (a fourth real strategy,
`FilteredAccumulateThenLenCheck`, found via a `NOT`-constraint fix after full-corpus mining across all
five questions), and a claim that the Q1 `SHARED_BINDING`/`all_names` fix already in this repo
retroactively improved Q3 (94.0%/74.7% → 96.2%/80.5%) and Q4 (77.6%/45.9% → 79.0%/47.6%) — none of
which this repo's Table 4 currently reflects.

**Two specific numeric discrepancies were flagged, not resolved, at that point**: (1) the paper's own
claim that a full audit of "51 newly-matched [Q5] submissions (15 via TopKViaDelegate, 36 via
SortThenSlice)" found only one genuine false positive and reclassified the rest as a legitimate fourth
strategy — directly at odds with this repo's own already-independently-verified
`topk_report_EXTENDED2.csv` breakdown (57 new catches: 17 via TopKViaDelegate, all overlapping with 40
SortThenSlice-only; caveat: "likely a slight overstatement by an uncharacterized amount," from a 7-of-17
sample check). (2) The paper's Table 4 for Q2/Q3/Q4 differs from what's currently logged as final, with
no supplied code or CSV behind any of it.

### Sonia's explicit instruction: keep everything already logged as final

Verbatim intent: "Don't change Table 4 results, keep the numbers we already logged as final, since this
is not reported in the final paper. For the audit for Q5, make the same decision and keep what is
already verified. Same for the 91.9%/80.6%." Per this instruction:

- **Table 4 stays exactly as previously verified**: Q1 99.5%/97.6%, Q2 90.4%/74.3%, Q3 94.0%/74.7%, Q4
  77.6%/45.9%, Q5 91.9%/80.6%. The two documents' narrative claims about Q2's wrong-labeled figure
  moving to 73.3%, Q3 to 96.2%/80.5%, and Q4 to 79.0%/47.6% are **not** folded into
  `configs/table4_config.yaml`, `configs/stage_manifest.yaml`, or any `data/labels_scores/*.csv` file.
- **The Q5 delegation breakdown stays exactly as previously verified**: 57 new catches (17 via
  TopKViaDelegate, all overlapping with 40 SortThenSlice-only), and the existing false-positive caveat
  ("likely a slight overstatement by an uncharacterized amount," from this repo's own 7-of-17 sample
  check) — the new paper's "51 matches, only 1 false positive, not inflated" claim is **not** adopted.
- Nothing in `stage_manifest.yaml`, `table4_config.yaml`, `KNOWN_CAVEATS.md`, or
  `regenerate_q5_delegation_breakdown.py` was touched on account of these two documents. They remain on
  file as context only — read, diffed, and quoted above for the record, per this project's discipline of
  never silently discarding evidence — but their claims are explicitly not evidenced by any supplied
  code or CSV and are not part of this repo's reported numbers.

### Real artifacts: `files_semantic_mine_factory.zip` + `mine_exemplars.docx` (2026-08-07)

Sonia then supplied the actual mine_exemplars artifacts: `mine_exemplars.py`, `semantic_backup.py`,
`validate_semantic_backup.py`, `semantic_backup_validation.ipynb` (all four files share an identical
internal mtime, 2026-08-07 19:32), and `mine_exemplars.docx` (a development-session transcript,
`dcterms:created` 2026-08-07T19:34:00Z — two minutes later, same-day chain). This is a real, dated
checkpoint distinct from, and clearly earlier than, the "final" state the two reference documents above
describe — confirmed directly, not assumed (see "What this is not yet" below).

**What the transcript describes, and what this audit independently re-executed and confirmed, not
merely trusted**: building `mine_exemplars.py` (the real mining logic: resolve each candidate submission
against the live structural rules, keep only `final_score >= 0.999`, deduplicate via an AST-level
alpha-renaming canonical key) forced every hand-written exemplar through `model.resolve()` for the
first time, surfacing a real integrity bug — both of GuardedInput's original exemplars scored
`final_score=0.0` (a bare `while` condition, no nested `if`, never actually satisfied GuardedInput's own
rule). Fixed, and a new `audit_registry()` utility added so this bug class can't silently recur.

Running the delivered code myself, directly, against the closest-dated real competency model this repo
has (`detectors/2026-08-05_q1_shared_binding_fix/test_real_data.py`, the checkpoint immediately preceding
this round's own date):

- `audit_registry(model)` returns exactly one flagged competency, `AccumulateThenCount` — every exemplar
  reported as "not registered in the given model," exactly matching the transcript's own claim that it's
  registered in `q2_competencies.py`/`pw01_competencies.py`, neither ever supplied to this project, and
  is therefore genuinely unverifiable rather than assumed fine.
- Both corrected GuardedInput exemplars individually score `final_score == 1.0` — confirmed directly.
- `validate_semantic_backup.py --backend lexical` reproduces the transcript's own reported pairwise win
  rate **exactly**: 470/542 (86.7%), verdict "strong discriminative power." The worst-case
  correct-ranking figure (9/19, 47.4%) is not quoted in the transcript at all — an independently-produced
  number from this same execution, not a check against a stated figure.
- `mine_exemplars.py`'s canonicalization mechanism was independently unit-tested (an alpha-renamed-only
  function pair collapses to the same canonical key; a genuinely different function body does not) —
  confirmed working as designed.

All of this is captured in a new script, `scripts/regenerate_semantic_backup_exemplar_audit.py`, which
reproduces every check above end-to-end and passes cleanly (`[OK]` on all four checks).

**A genuinely open question, found while trying to verify the root-cause diagnosis precisely, not
resolved by guessing.** Reconstructing the described original, broken GuardedInput shape (a bare
`while <comparison>:` loop with a reassignment inside, tried in three independent phrasing variants) and
resolving it against this repo's own closest-dated real `competency.py`
(`2026-08-05_q1_shared_binding_fix`) scores `final_score == 1.0` in every variant, **not 0.0**. This
does not mean the transcript's finding is wrong — the literal original exemplar text was never supplied
(already replaced in the delivered file) — but it is a real, precisely-characterized discrepancy. Most
likely explanation, consistent with this project's own already-logged "two different working
environments" pattern (see "A direct clarification from Sonia," 2026-09-17, above): the `competency.py`
this session actually ran against most likely predates the Q1 `SHARED_BINDING`/`all_names` fix
(2026-08-05), which is what added `while`-condition `TEST` synthesis in the first place — under the
current, most-recent `competency.py`, a bare `while` condition already registers as `TEST` evidence, so
this specific bug would no longer reproduce. Recorded as an explained-but-unconfirmed hypothesis, not a
settled fact, since the exact `competency.py` version actually used for this round's development was
never supplied.

**What this is not yet**: the registry here is still entirely hand-written — 8 competencies, 19
exemplars (expanded from 5 exemplars/2 competencies) — not the "10 competencies, 27 exemplars, partly
real-mined" state the two reference documents above describe as finished. `mine_exemplars.py`'s own
`CONFIG` only covers 6 of the eventual competencies (`Accumulation` and `AccumulateThenCount` are
explicit `TODO`s in the script itself), no `mined_exemplars.json` output exists in this upload, and this
sandbox has no Refactory corpus available either (checked directly: `/home/claude/refactory` does not
exist here) to run the mining step independently. The lexical win rate here (86.7%) is a real, different,
earlier number than the reference paper's final 90.6% — the two are not the same measurement, and the
gap is explained in the reference paper by two bug fixes (the 40%-cap harness bug, the
DelegatesUniqueness scope-mismatch bug) this round's code shows no trace of yet. The codet5p backend
could not be independently checked either — `huggingface.co` is confirmed blocked from this sandbox too
(a direct request returns a 403 at the network proxy), consistent with every earlier round of this
project.

**Repository changes this round**: new checkpoint folder `detectors/2026-08-07_mine_exemplars/`
(`mine_exemplars.py`, `semantic_backup.py`, `validate_semantic_backup.py`,
`semantic_backup_validation.ipynb` — confirmed entirely unexecuted by direct JSON inspection —,
`mine_exemplars_chat.txt`/`.docx`, and a new `README.md` covering all of the above); new script
`scripts/regenerate_semantic_backup_exemplar_audit.py`; `configs/stage_manifest.yaml`'s
`exemplar_registry_real_mined` entry extended with a note distinguishing this round's mining
implementation from the one referenced in the AUC notebooks, plus a new
`exemplar_discriminative_validation_lexical` stage (`evidence: real_execution`, a new tier introduced
here meaning "independently executed by this audit against the delivered code," stronger than
`conversation_reported_only` but distinct from `real_csv`/`real_notebook_output` since no notebook was run and no
CSV backs it); `docs/KNOWN_CAVEATS.md` and root `README.md` both updated with cross-referenced summaries.
**Table 4, `configs/table4_config.yaml`, and the Q5 delegation breakdown were not touched by any of
this**, per Sonia's explicit instruction above — this round is scoped entirely to the semantic backup
layer's exemplar registry, a separate axis from Q1-Q5's own structural coverage.

### A second mine_exemplars batch ("A second version is here," 2026-09-17) — real corpus mining, and the round above's own open question resolved with hard evidence

Sonia's message this round: "A second version is here," uploading four files: a second dev-session conversation
transcript (docx metadata: created 2026-08-08T18:54Z, modified 2026-09-17 — the modified date is this
export's own timestamp, the same pattern every conversation-history docx in this project has shown, not a
meaningful authorship date), a RAR archive ("Original files to load"), a "final" mining zip (internal zip
timestamps 2026-08-09 16:07), and a semantic embedding cache zip (internal timestamps 2026-08-08 21:15).
Per Sonia's standing instructions this session, **Table 4 and the Q5 delegation breakdown are untouched
by any of this** (nothing in this batch even mentions either), and **the zip continues to be held**, not
repackaged or resent, per the earlier "hold off until all files are sent" instruction.

**What the batch is, at a high level**: the conversation describes closing the real-corpus-mining gap the round
above left open (`mine_exemplars.py`'s `CONFIG` had `AccumulateThenCount`/`Accumulation` as explicit
`TODO`s) by running the actual mining pipeline in Colab against the real Refactory corpus, for four
Question-2 competencies: `ConditionalCount`, `AccumulateThenCount`, and two new ones,
`FunctionalUniqueCheck` (map/filter pipelines with no explicit loop) and `DelegatesUniqueness`
(cross-function: does `contains_unique_day` genuinely delegate to a `unique_day` that itself satisfies
`ConditionalCount`).

**Real-corpus scan counts (conversation-reported only — this sandbox has never had the Refactory corpus, checked
again this round: no path matching `question_2/code/correct` exists anywhere)**: `ConditionalCount`
248/291 (85%, 66 distinct shapes); `AccumulateThenCount` only 2/291, both collapsing to the identical
shape, independently cross-checked per the conversation against the analogous `unique_month` function (same two
students, same pattern) — a real, standalone finding if true: a genuinely rare strategy (<1% of correct
submissions), not merely under-sampled; `FunctionalUniqueCheck` 13/291 (4.5%, 11 shapes, one exemplar
chosen per real sub-strategy); `DelegatesUniqueness` 227/291 (78%, 96 shapes, needs the whole module tree
since `DELEGATES` reasons across the function boundary).

**A second, independent instance of the same class of integrity bug the round above found in
`GuardedInput`**: the conversation describes discovering that 2 of the first round's 3 `AccumulateThenCount`
exemplars (`count_evens`, `count_long_words`) also scored `final_score=0.0` under the real rule — it
specifically requires `.count(` in the output text; their `len(...)`-based versions didn't qualify. Now
corrected in the delivered registry (one real-mined exemplar, two corrected synthetic replacements).

**The registry is now real, delivered code — not narrative — at exactly 10 competencies, 27 exemplars.**
Direct inspection of the delivered `semantic_backup.py`'s `EXEMPLAR_REGISTRY` confirms: Swap (2),
Accumulation (3), ConditionalCount (5), AccumulateThenCount (3), GuardedInput (2), SelectionStep (2),
FindExtremumBuiltin (2), TopKPattern (2), FunctionalUniqueCheck (3), DelegatesUniqueness (3) = 27. This is
the exact figure `Competency_Extraction_Methodology_V2.docx` and `Structural_Competency_Extraction_Paper_v1_2.docx`
(received two rounds ago, flagged then as narrative-only) described as a finished future state — that
state is now backed by real, independently-runnable code for the exemplar registry itself, specifically
and only. It still does not extend to the real-corpus mining scan counts above (conversation-reported only), and
per Sonia's standing instruction it still does not extend to Table 4 or the Q5 delegation breakdown.

**A confirmed, but differently-caused, verification gap: the delivered "real model chain" does not
actually run in this sandbox.** The conversation describes retiring an earlier `q2_extra.py` workaround in favor
of the real `test_real_data.py -> pw01_competencies.py -> q2_competencies.py` chain, and the RAR delivers
all five files this needs. Directly attempting to import them here shows the chain is broken:

```
$ python3 -c "import pw01_competencies"
ImportError: attempted relative import with no known parent package
```

`pw01_competencies.py` uses package-relative imports (`from .core import ...`,
`from .base_competencies import model, show`) to submodules never supplied to this project in any round.
`q2_competencies.py` imports its `model` from `pw01_competencies`, so it fails the same way, transitively.
Practically: `AccumulateThenCount`, `FunctionalUniqueCheck`, and `DelegatesUniqueness` remain
unverifiable in this sandbox — the same practical outcome as the round above, but for a genuinely
different, more specific reason this time (a broken import chain in code that *was* delivered, not a
module that was never delivered at all). Running `audit_registry()` against the only model this sandbox
can actually construct (`test_real_data.py`'s own model) correctly reports exactly these three
competencies as unregistered — confirmed by direct execution — while `Swap`, `Accumulation`,
`ConditionalCount`, `GuardedInput`, `SelectionStep`, `FindExtremumBuiltin`, and `TopKPattern` all audit
clean, including both of `GuardedInput`'s corrected exemplars, individually confirmed at `final_score ==
1.0`.

**A real, precise dating finding, established by diffing the delivered "Original files to load" against
every checkpoint already in this repo**: `competency.py` and `test_real_data.py` are byte-for-byte
identical (0 diff lines) to `detectors/2026-07-28_fixQ4`; `report.py` is byte-for-byte identical to
`detectors/2026-07-20_semantic_backup`. This mine_exemplars development session's actual environment was
running a `competency.py` that **predates** the 2026-08-05 Q1 `SHARED_BINDING`/`all_names` fix — this
repo's own current HEAD is several rounds ahead of what this particular round's mining was actually built
against.

**This directly resolves, with hard evidence, the previously-open "bare-while GuardedInput reconstruction
scores 1.0, not 0.0" discrepancy recorded in the section above.** That earlier reconstruction used this
repo's then-closest-dated real `competency.py` (`detectors/2026-08-05_q1_shared_binding_fix`) because the
exact version the developer's session had actually used was never supplied — and it scored 1.0, leaving an
explained-but-unconfirmed hypothesis on file (most likely a pre-Q1-fix environment, per this project's own
"two different working environments" pattern). This round supplies that exact version. Diffing
`2026-07-28_fixQ4/competency.py` against `2026-08-05_q1_shared_binding_fix/competency.py` shows precisely
why the discrepancy existed: the Q1 fix didn't only change `SHARED_BINDING`'s comparison from `operand` to
`all_names` — it also added an entirely new `elif isinstance(node, ast.While):` branch to the `TEST`
primitive detector, synthesizing `TEST` evidence directly from a while loop's own condition (`node=None`,
matching this project's composite-evidence convention). Before that fix, `TEST` evidence could only ever
come from an `ast.If` node. Reconstructing the same bare-while `GuardedInput` shape and resolving it
against the now-supplied, actual `fixQ4`-era `competency.py` gives:

```
final_score: 0.0   coverage_score: 0.667   structural_score: 0.0
```

— exactly the originally-claimed `0.0`. This is no longer a hypothesis; it is diff-confirmed and then
execution-confirmed. The earlier paragraph recording the hypothesis is left unedited in the section above,
per this project's evidence-preservation discipline — it was a correct hypothesis, now proven, not a
mistake to be erased.

**The delivered `semantic_cache.zip` contains real, verified embeddings — not placeholders.** It is the
actual on-disk content-hash-keyed cache `semantic_backup.py`'s own caching functions read and write,
downloaded from Colab per the notebook's own final cell. Unpickling both files directly confirms:
`lexical.pkl` holds 24 real 4096-dimension vectors (matching `LexicalEmbedder`'s
`HashingVectorizer(n_features=4096)`); `codet5p.pkl` holds 24 real 256-dimension `float32` vectors
(matching `Salesforce/codet5p-110m-embedding`'s actual output dimensionality — this sandbox still cannot
confirm the values genuinely came from that model, since `huggingface.co` remains blocked here too, but
shape, dtype, and content-hash keying are all consistent with real model output). Cross-referencing the 27
registry exemplars' content-hash keys against the cache: 21 of 27 match exactly (the 8-competency subset
that excludes `FunctionalUniqueCheck`/`DelegatesUniqueness`, added later in the same dev session, after
this cache was saved), plus 3 further entries matching `validate_semantic_backup.py`'s own
`UNRELATED_SNIPPETS` exactly — 24 total, fully accounted for.

**Independently reproduced using ONLY the real cached embeddings — no network call made or possible.**
Loading the delivered `semantic_backup.py` with its cache directory pointed at this checkpoint's real
cache, and patching the codet5p embedder to raise loudly instead of silently falling back if anything not
already cached were requested (proving nothing below is fabricated or network-backed): running the
delivered `validate_semantic_backup.py`'s own `run()` function against the 8-competency subset the cache
covers reproduces the conversation's first codet5p block **exactly** — every mean/median/n, all 5 named failure
lines, and the headline pairwise win rate 696/852 (81.7%), worst-case ranking 16/21 (76.2%). Separately,
the lexical backend (deterministic, no cache needed at all) run against the full, current 27-exemplar/
10-competency registry reproduces the conversation's later "10/08" lexical block **exactly** — all three summary
rows, all 12 named failure lines, pairwise win rate 1262/1428 (88.4%), worst-case ranking 15/27 (55.6%).
This is the first time this project has independently reproduced a codet5p discriminative-power number
from real cached model output, without trusting the transcript and without needing live `huggingface.co`
access — recorded as `evidence: real_csv` (the underlying pickle cache is real, preserved model output,
functionally the same evidentiary weight as a CSV of raw scores, even though it is not literally a CSV
file).

**What this round does NOT establish, explicitly, so it is not assumed later**: the 10-competency codet5p
run (84.2% win rate, 81.5% worst-case) is not independently checkable — `FunctionalUniqueCheck`/
`DelegatesUniqueness`'s codet5p embeddings were never cached in the delivered `semantic_cache.zip`, and
`huggingface.co` is still blocked. A later scoping fix the same conversation describes as implemented and shipped
(`DELEGATING_FUNCTION`/`runtime_scoped_exemplar()`, addressing a `DelegatesUniqueness`/`ConditionalCount`
surface-containment confound, reported lexical 90.6%/74.1%) is grep-confirmed **absent** from the
delivered `semantic_backup.py` — described in the conversation, never actually delivered to this project. Three
documents the conversation's closing sections describe as finalized (`semantic_backup_findings_v4.docx`, an edited
`Structural_Competency_Extraction_Paper_v1.docx`, `DOCUMENT_INDEX.md`) were likewise not included in this
batch's four uploaded files. The real-corpus mining scan counts above remain conversation-reported only. **Table 4
and the Q5 TopKPatternExtended delegation breakdown remain exactly as previously verified** — nothing in
this round touches either.

**Repository changes this round**: new checkpoint folder
`detectors/2026-08-09_mine_exemplars_real_corpus/` (`mine_exemplars.py`, `semantic_backup.py`,
`validate_semantic_backup.py` — extracted from the notebook's own source cell, since the delivered zip did
not include it standalone —, `semantic_backup_validation.ipynb` — confirmed entirely unexecuted, 16/16
cells, same pattern as every notebook this project has received —, `.semantic_cache/{codet5p,lexical}.pkl`,
`mine_exemplars_v2_chat.txt`, `original_files_used_this_round/` holding the five real project files this
round's mining environment actually ran against, preserved exactly as delivered, and a new comprehensive
`README.md`); new script `scripts/regenerate_semantic_backup_v2_audit.py` (13 checks, all passing);
`scripts/regenerate_semantic_backup_exemplar_audit.py`'s closing message updated to point at the resolution
instead of calling the bare-while question still open; `detectors/2026-08-07_mine_exemplars/README.md`
given a forward-pointing "UPDATE" note (original hypothesis paragraph left unedited); `configs/
stage_manifest.yaml`'s `exemplar_registry_real_mined` entry given the same forward-pointing update, plus a
new `exemplar_registry_real_mined_v2` entry; `docs/KNOWN_CAVEATS.md` and root `README.md` both updated
with cross-referenced summaries. Full test suite (`pytest tests/`, 11 tests) and both Table 4 / Q5
delegation regeneration scripts re-run clean after all changes — zero drift. **The zip has not been
repackaged or resent** — still holding per the standing "wait until all files are sent" instruction.

### A third delivery (2026-09-17) — the first genuinely EXECUTED semantic_backup_validation.ipynb, and both remaining gaps from the round above closed

Sonia's message this round: "here is the last version of 'semantic_backup_validation' notebook" — a
single `.ipynb` upload, no conversation transcript, no docx metadata to date it by. **There is no independent
dating evidence for this file beyond today's delivery** — recorded plainly as such, not guessed at. What
the content itself establishes: it embeds this repo's own current-HEAD structural model and the full
10-competency/27-exemplar registry from the round immediately above, so it chronologically postdates
both, whatever its exact date is. Per the standing instructions, **Table 4 and the Q5 delegation
breakdown remain untouched**, and **the zip continues to be held** — a single notebook upload isn't
treated as a signal that the broader thread is complete.

**This is the first genuinely executed copy of this specific notebook this project has ever received.**
Every earlier copy (both mine_exemplars rounds above) was confirmed, by direct JSON inspection, to be
entirely unexecuted — a template only. This one has 20 cells, 10 code cells, `execution_count` set
sequentially 1 through 10, and 9 of 10 with real outputs, including things that are hard to fabricate
convincingly: real `pip install` output, real Colab-style download progress bars for
`Salesforce/codet5p-110m-embedding`'s weight files, real `transformers`/`huggingface_hub` warnings, real
weight-loading progress bars.

**Two real fixes land here, closing both of the round above's remaining gaps.** First: the broken
`pw01_competencies.py` import chain (relative imports to submodules never supplied) is fixed — this
notebook's embedded `pw01_competencies.py` (written out directly by cell 4, alongside `competency.py`,
`test_real_data.py`, `q2_competencies.py`, `report.py` — all five embedded as strings now, no upload step
needed) uses `from competency import ...` / `from test_real_data import model, show` instead, a 2-line
diff (the import statements only) against the broken version. **Confirmed by direct execution in this
sandbox**: `python3 -c "import q2_competencies"` now succeeds against these files, which it could not do
against the round above's. Second: the `DelegatesUniqueness`/`ConditionalCount` surface-containment
scoping fix (`DELEGATING_FUNCTION` + `runtime_scoped_exemplar()`) — described in the round above's conversation
as implemented and tested, but grep-confirmed absent from that round's own delivered `semantic_backup.py`
— is now present as real code, and wired into both `semantic_backup_score()` (report.py's live scoring
path) and `validate_semantic_backup.py`'s held-out test. The `EXEMPLAR_REGISTRY` content itself (all 27
exemplar snippets) is byte-identical to the round above's registry — only what gets embedded for
similarity changed.

**A real, precise dating finding**: diffing the notebook's embedded `competency.py`/`test_real_data.py`
against every checkpoint in this repo finds them substantively identical (one leading blank line from
the string-embedding convention, nothing else) to `detectors/2026-08-08_q5_delegation_clustering_fix` —
**this repo's own current HEAD**, not a stale snapshot. Unlike both earlier mine_exemplars rounds, whose
"Original files to load" turned out to predate even the 2026-08-05 Q1 fix, this notebook's environment is
genuinely up to date. `report.py` remains substantively identical to `detectors/2026-07-20_semantic_backup`
— consistent with every earlier round, since `report.py` itself was never touched by the 2026-08-08 Q5
round.

**Independently re-verified in this audit, not just read from the notebook's own printed output**:
`audit_registry()` now reports ZERO problems against the complete real chain — all 10 competencies, all
27 exemplars verify clean — for the first time ever in this project (every earlier round could only check
7 or 8 of the 10, since the chain didn't import). The lexical discriminative-power numbers, post-scoping-
fix, reproduce exactly by direct execution (deterministic, no network or cache needed): pairwise win rate
1294/1428 (**90.6%**), worst-case ranking 20/27 (**74.1%**), 7 named failure lines — critically, ZERO of
them involve `DelegatesUniqueness` (down from 5 of 12 in the round above's pre-fix run), confirming the
fix specifically and only removes that one confound. Three synthetic `TopKPatternExtended` structural
regression cases (cell 17, explicitly labeled in the notebook itself as "structural, not
semantic-similarity" and "independent of the semantic backup layer") reproduce exactly against this
repo's own current model: a delegate-based helper (`TopKViaDelegate` fires), a pure-recursion quicksort
helper (`SortThenSlice` only, cleanly isolating `SELF_RECURSIVE`), and a merge-sort helper reproducing the
already-documented Table-5/§8 false positive — none of these three change any real corpus-derived
percentage; they are demonstration/regression checks against the unmodified model, read directly to
confirm this rather than assumed from the cell's own label.

**What could not be independently checked, for the same reason as every prior round**: the codet5p
backend's numbers for the full 10-competency, post-scoping-fix registry — pairwise win rate 1202/1428
(**84.2%**), worst-case ranking 22/27 (**81.5%**) — match the round above's conversation-reported "after fix"
figure exactly, and now come with a genuinely executed notebook's real output behind them, but
`huggingface.co` remains blocked from this sandbox, so this audit could not re-run them itself — recorded
as `evidence: real_notebook_output`, a step up from `conversation_reported_only` but short of independent
re-execution. The `moyenne()`/`DelegatesUniqueness` codet5p similarity smoke-test values (0.42, 0.97,
0.975/0.977/0.961) are the same — real notebook output, not independently recomputable here, though the
STRUCTURAL scores in those same cells (`Accumulation final=1.00`, `TopKPattern final=0.00`,
`DelegatesUniqueness final=0.00`) are ordinary structural-resolver output and were independently confirmed
by this audit as a byproduct of reproducing the TopKPatternExtended cases above. The real-corpus mining
scan counts remain exactly as the round above recorded them (conversation-reported only) — this notebook
validates the already-mined registry, it does not re-run mining.

**Repository changes this round**: new checkpoint folder
`detectors/2026-09-17_semantic_backup_validation_executed/` (the notebook itself, plus
`semantic_backup.py`/`validate_semantic_backup.py` extracted verbatim from the notebook's own source
cells — the only two files that changed relative to the round above; `competency.py`/`test_real_data.py`/
`report.py`/`pw01_competencies.py`/`q2_competencies.py` are not duplicated as static copies, since they
are confirmed substantively identical to existing checkpoints except for the one import fix, and the new
regeneration script extracts and diffs all five directly from the notebook on every run instead); new
script `scripts/regenerate_semantic_backup_v3_audit.py` (19 checks, all passing); `configs/
stage_manifest.yaml` given a new `exemplar_registry_real_mined_v3_executed` entry; `docs/KNOWN_CAVEATS.md`
and root `README.md` both updated with cross-referenced summaries. Full test suite (`pytest tests/`, 11
tests) and both Table 4 / Q5 delegation regeneration scripts re-run clean after all changes — zero drift.
**The zip has still not been repackaged or resent** — continuing to hold per Sonia's standing instruction,
now across three full rounds of this thread.

---

## Still-pending items (mentioned in the conversation, no code supplied yet)

- The **unscoped** run that produced the paper's "83.0%" pre-fix Q5 figure — only the post-fix ("78.2%")
  side is evidenced by `topk_report.csv`. (The *later*, post-`TopKPattern`-refactor unscoped re-run,
  82.1%, is now narrative-evidenced by the 28/07 methodology note — see above — but likewise has no CSV or
  driver script of its own.)
- The **`magus_sort` cross-function-credit bug (bug #13)** — canonical symptom/root-cause/fix text is now
  recorded (see "Methodology V24" section above), but still no code in any supplied artifact.
- ~~The exact driver invocations (folder paths, `function_name` arguments, target competency lists) behind
  the 90.4% Q2, 94.0% Q3, 77.6% Q4 `SortByKey`, and 1,343/1,342 Q1 `LinearSearch` figures — no batch
  scripts or CSVs for any of them have been supplied.~~ — **fully resolved this round.** The real driver
  script (`run_q1_q4_batch_validation.py`, logged in the prior section) has now actually been run by Sonia
  against her real Refactory dataset, and the four resulting CSVs (`q1_report.csv`, `q2_report.csv`,
  `q3_report.csv`, `q4_report.csv`) were supplied and independently re-verified — see "Real
  batch-validation RESULTS for Q1-Q4" above for the complete write-up, including a real Q1-specific
  structural-matching bug found and fixed as a direct result of this run. Q1-Q4's headline percentages are
  `evidence: real_csv` as of this round, no longer `conversation_reported_only`. (The Q4 `SortByKey`-registration
  operational risk flagged in the prior round — whether Sonia's actual `test_real_data.py` had `SortByKey`
  registered — is moot now that a real, successful `q4_report.csv` with populated `SortByKey_final`/
  `SortByKey_missing` columns exists, confirming it was registered for this run.)
- The **"final audit down to 1 violator"** state of the level-enforcement work — **fully resolved**: per
  the 28/07 methodology note ("reducing known violations from 4 to 1") and `To_copy_to_new_project.docx`
  ("only BubbleSortPass still needs it"), `TopKPattern`, `Average`, and `CountedSearch` are all fixed;
  `BubbleSortPass` alone remains, with its specific resolver-level obstacle now fully documented as
  canonical bug #19 (see above). **`CountedSearch`'s own lifted-siblings replacement code (`LoopStep`/
  `OutputStep` wrappers) is still not itself present in any supplied artifact** — only referenced in prose
  (`level2_examples.py`'s supplied content covers `Average`/`AverageStrict` and `ValidatedAccumulation`
  only, not `CountedSearch`).
- The embedding-based validation described in earlier conversation text as "Table 5 of the paper — 10 train/test
  splits, codet5p" — **now confirmed to belong to a wholly separate, still-unsupplied "companion paper"**,
  per `Structural_Competency_Extraction_Paper.docx`'s own Abstract/Limitations, which explicitly defer all
  semantic-backup evaluation to that companion document and state "all results in this paper concern the
  structural, AST-only layer." Not to be conflated with `semantic_backup.py`/`semantic_20_07.docx` (now
  fully supplied and logged above), which is the stub-backend *plumbing*, honestly self-documented as
  having "essentially no discriminative power" (0.77 vs. 0.79 on a related/unrelated pair) and never
  claims to be the codet5p-backed validation this item refers to. **Partial progress in an earlier round
  (see the "Real-CodeBERT/CodeT5+ Colab validation" section above): a real, executed raw-codebert
  anisotropy result and real (though not yet numerically validated) codet5p exemplar/test-set-construction
  code now exist. Further real progress this round (see "Q4/Q2 embedding cross-validation" above): the Q5
  10-seed embedding-taxonomy methodology was extended to Q4 and Q2, with real, verified, `evidence:
  real_notebook_output` results for both — but these are explicitly a DIFFERENT experiment (validating the
  AST taxonomy's own splits via embeddings) from whatever this item's own "10 train/test splits" scope
  refers to (the companion-paper novel-detection/train-test-split experiment) — no AUC/threshold result and
  no train/test-split experiment of that specific kind has been produced yet. **Further real progress in
  the following round (2026-08-08, see "Semantic backup layer validation" above): a real AUC/threshold
  result now exists for the closely-related novel-vs-wrong separation question (0.097 pooled, strongly
  inverted) — originally `conversation_reported_only`, now upgraded to `evidence: real_csv` once the raw CSVs and
  the executed notebook itself were independently verified (see "Semantic backup layer validation — the raw
  CSVs, then the executed notebook" above). Still not the "10 train/test splits" experiment this item's own
  wording names.** Still genuinely open, not resolved.**
- **Whether a later methodology-doc version exists** (V25 or beyond) containing the Q3/Q4 results,
  `SortByKey`, and the enforcement mechanism — **partially resolved, but with a new twist.** The 28/07
  methodology note supplied this round ("the last one for the 28/07") does contain the enforcement
  mechanism, `LinearSearch`, and the Case-Study-4 Q1/Q2 content — but, per an exhaustive full-text grep
  sweep, **still contains no Q3/Q4/`SortByKey` material at all**, even though it is dated the same day as
  `Q3_Q4_Results_28.docx`. The Q3/Q4 content instead turned up in a *different* document,
  `Structural_Competency_Extraction_Paper.docx` (the finished paper, §5.5) — meaning either this 28/07
  methodology note is itself not the final 28/07 revision `Summaize_to_move_the_project_28.docx` described
  regenerating (an even-later "V25+" methodology note, containing Q3/Q4, might still exist and be
  unsupplied), or Q3/Q4's home was always meant to be "the paper" rather than "the methodology doc" and
  the two threads never merged. Genuinely open; not yet asked of Sonia directly.
- ~~`Competency_Extraction_Article.docx`~~ — **now supplied and read in full** (see the dedicated section
  above). Confirmed, by direct textual evidence rather than description alone, to predate enforcement, the
  `NESTED` bug, and all of Q1–Q4 by number — matches its 28/07-described profile exactly. This item is
  resolved and removed. (`Structural_Competency_Extraction_Paper.docx` was briefly, and incorrectly,
  hypothesized to possibly be this document in the prior round; that hypothesis stands disproven, and this
  newly-supplied article confirms it independently — the two documents are unrelated in age and content.)
- **A small, precise bug-count accounting discrepancy, newly flagged this round**: the 28/07 methodology
  note's canonical table numbers exactly 19 bugs total, including one (#15) explicitly self-described as
  "not a defect in the model." The finished paper's own text says its Table 4 groups "nineteen structural
  defects... a further two informational script bugs... are omitted" — implying 21 total findings, 19 of
  them structural. These two "19"s do not obviously refer to the same set on a like-for-like basis (see
  the dedicated write-up above). Not resolved; no document names what the second informational bug is.
- **The methodology doc's true page count** — "~11 pages" (`To_copy_to_new_project.docx`) vs. "15 pages,
  up from 14" (`Summaize_to_move_the_project_28.docx`) — an open, unreconciled discrepancy between two
  summary-style descriptions of what appears to be the same document. (Still unresolved; the 28/07
  methodology note and the finished paper supplied this round carry no page-count marker of their own.)
- ~~The two real-embedding-validation notebooks' own unresolved thread (from the prior round). The
  "contaminated comparison group" problem (novel-correct vs. a broadened wrong-group dominated by
  structurally-correct-but-test-suite-failing code) was diagnosed but not fixed in any supplied artifact —
  Sonia was given a proposed cross-exercise-negative-set fix to hand-apply, but no confirmation that it was
  applied or run has been supplied. No AUC/ROC number exists anywhere yet for either the codebert or the
  codet5p backend.~~ — **substantially resolved this round (2026-08-08).** A redesigned notebook
  (`semantic_backup_layer_validation.ipynb`, see "Semantic backup layer validation" above) fixes the
  contamination directly — ALL wrong-labeled submissions as the negative class, not the cross-exercise
  fix originally proposed — and produces the first real AUC/ROC number this project has ever generated:
  a strongly inverted 0.097 (pooled, 1,510 pairs). **Now further resolved in a later round**: both raw
  per-submission CSVs and the executed notebook itself were supplied and independently verified —
  `evidence: real_csv` as of "Semantic backup layer validation — the raw CSVs, then the executed notebook"
  above. **One thread remains genuinely open even now**: every code cell's `execution_count` is `None` in
  the executed notebook too, so the conversation's own "cell 13"/"cell 15" numbering still cannot be checked against
  real cell positions — not resolved by the executed notebook's arrival, flagged rather than guessed at.
- ~~The 31/07 "summary document" describing the semantic layer's role has not itself been supplied, only
  its outline.~~ — **resolved this round.** `Steps for semantic_backup.docx`'s own opening section (31/07,
  14:50) is that document, matching the previously-logged seven-part outline point for point. See the "AST
  taxonomy cross-validation via embeddings" section above.
- ~~The updated `Structural_Competency_Extraction_Paper.docx`/PDF (with the new §5.5, a Wang et al. 2023
  CodeT5+ citation, and renumbered downstream sections) has not itself been supplied.~~ — **resolved.**
  `Structural_Competency_Extraction_Paper.pdf` (20 pages) was supplied and read in full, word-for-word
  diffed against the prior docx. §5.5, the Wang et al. 2023 citation, the Abstract change, and the §7
  forward-pointer sentence are all confirmed present with exact wording; the section-numbering discrepancy
  is resolved (a real merge of old §5.5 into §5.3, freeing the number for the new §5.5, not a simple
  insertion — see "The updated paper" section above for the full diff).
- ~~The paper's own manual-precision figure (0.98) does not match an earlier conversation-quoted
  `classification_report` figure (0.92) for the same confusion matrix.~~ — **resolved.** `multi-seed
  loop.docx` (see the dedicated section below) supplied the arithmetic needed: 0.92 is the full 3-way
  `classification_report` precision (denominator includes 5 novel-actual submissions misclassified as
  manual); 0.98 is precision restricted to just the manual/builtin subset the paper's own §5.5 describes
  (those 5 submissions excluded). Both are correct; verified directly against the confusion matrix this
  session.
- ~~The 10-seed (`SEEDS = list(range(10))`) multi-split robustness check for the AST taxonomy
  cross-validation (manual/builtin/novel) still has no execution output.~~ — **resolved this round.** Two
  notebooks (`ast_taxonomy_crossvalidation_with_results.ipynb`, with real printed output, and
  `Copie_de_ast_taxonomy_crossvalidation.ipynb`, a code-identical outputs-stripped copy) plus a raw
  per-file CSV for the shuffled seed=0 run and three chart images were all supplied and cross-checked
  against each other and against the conversation's own quoted figures — see "The real 10-seed sweep" section
  above for the full per-seed table, pooled confusion matrix, and pooled classification reports. The paper
  itself has since been updated a second time to report this sweep's mean±SD rather than the single-run
  figure — see "The published paper, updated again" section above. Distinct from, and not resolving, the
  still-entirely-unsupplied Q4 `SortByKey` embedding-split experiment (`configs/stage_manifest.yaml`'s
  `table5.q4_sortbykey_splits`).

## Corrections to the earlier (fabricated) `VERSIONING.md`

The scaffold repo's `VERSIONING.md`, written before any real artifacts were available, guessed at a
detector version history from the paper's prose alone. Real evidence now contradicts it on specifics:

- Guessed: Q1 fixed via `SHARED_BINDING` widened to `all_names`. **Real:** fixed via a `PARAM` primitive
  and widening `GuardedInput`'s `source` slot to `("INPUT", "PARAM")` — a different mechanism, and it
  happened at V1.0.0, earlier than guessed.
- Guessed: `NESTED` fixed to true AST ancestry (`is_ancestor`). **Real:** still span-containment through
  the most recent checkpoints supplied — the one `NESTED` fix confirmed so far (`files_Fix_Q4`) is a
  same-evidence identity-comparison fix (`.node`-based → whole-object-based), unrelated to ancestry;
  no ancestry-based fix evidenced yet.
- Guessed: `SEQUENTIAL` fixed to statement-list position. **Real:** still raw `max_line_gap` through the
  most recent checkpoints supplied; no fix evidenced yet.
- Guessed: `LinearSearch` split from `GuardedInput` early (grouped under an early "v1.1.0"), for the
  reason "avoids encoding a false relationship." **Real: the mechanism/reasoning guess was essentially
  correct** (now confirmed by `q1_competencies.py`'s own comment, argued at greater length) **but the
  timing guess was wrong** — real evidence dates this to 2026-07-28, after the Q1–Q5 full-corpus
  validation work, not near the project's start.
- Guessed: the scoping fix was "whole-file → function-scoped" via `SHARED_BINDING` changes. **Real, and
  now fully confirmed:** it's an `Evidence.scope` tag + combinatorial-search guard (`V1.2.0`,
  2026-07-21) **plus a second, independent scoping layer added afterward in the reporting tool itself**
  (the `function_name` parameter) — the paper's "unscoped → scoped" correction is this second layer, not
  the first.
- **Now confirmed with an exact numeric match, not just a described origin:** the paper's Q5 "78.2%"
  figure and its "75% of wrong-labeled submissions still structurally correct" finding are both
  reproduced bit-for-bit from `topk_report.csv` (327/418 and 81/108 respectively). The "83.0%" unscoped
  side of that correction is still not directly evidenced.
- **Now confirmed with real code:** the "TopKPattern missing-removal bug" (bug #12) named in the paper's
  bug table has a real fix in `test_real_data.py` (originally a `remove` slot + `CONTAINS_TEXT` check
  directly on `TopKPattern`; refactored again at `files_Fix_Q4` into a `RemovalAssign`/`RemovalAssignStep`
  lifting pair for level-convention reasons, same underlying check), a real demonstration file
  (`report_demo.py`) naming `wrong_5_058.py` exactly as the paper's bug name suggests, a full
  primitive-inventory trace in `The_output_Results_26.docx` confirming the fix behaves exactly as
  designed, and now a full canonical symptom/root-cause/fix description in `Competency_Extraction_
  Methodology_V24.docx`'s own bug table. `magus_sort` (bug #13) now has a concrete description
  ("recursive partition-based sorting," first found in Q5) but still no code.
- **A correction to this log's own prior claim about the `NESTED` identity-comparison bug's origin:** this
  log previously attributed the `outer_ev.node is not inner_ev.node` → `outer_ev is not inner_ev` fix
  (`files_Fix_Q4`) to "necessity alongside the TopKPattern refactor," explicitly flagged at the time as an
  inference from the diff, not a quoted fact. The 28/07 methodology note (bug #18, quoted in full in that
  section above) now states directly that this bug was actually **discovered via `CountedSearch`'s own
  layering-compliance restructuring**, one checkpoint earlier, and `TopKPattern`'s refactor simply reused
  the already-fixed guard. The diff-level facts (the fix is genuinely present and genuinely necessary for
  `TopKPattern`) are unchanged; only the "why/how it was found" attribution is corrected, with both the
  original inference and the new documentary evidence preserved in place (see the dedicated write-up
  above, "The NESTED identity bug (bug #18) — a correction to this log's own prior attribution").
- **Now confirmed, Q2's own figure:** the guessed Q2 coverage figure (90.4%) is genuinely correct, per a
  full 291-submission batch run reported in `The_output_Results_26.docx` — though, unlike Q5, no CSV or
  driver script for this specific run has been supplied, only the conversation's own summary table.
- **Now confirmed, Q3 and Q4's own figures, with code closing the gap flagged in the prior checkpoint:**
  Q3's guessed figure (93.6%→94.0%, the `.insert()` fix) and Q4's guessed figure (13.1%→77.6%,
  `SortByKey = ANY(BubbleSortPass, TopKPattern)`, the project's strongest cross-exercise transfer result)
  are both genuinely correct and **now code-confirmed** at the `files_Fix_Q4` checkpoint — resolving the
  discrepancy noted at the prior (`files_Enforcement`) checkpoint, where the same conversation's own claim of
  where these were saved didn't match what was actually in that zip. **Now a third independent document,
  `Structural_Competency_Extraction_Paper.docx`'s §5.5, states the identical 93.6%/94.0%/13.1%/64.4%/77.6%
  figures**, with corpus denominators made explicit for the first time (Q3: 546 correct; Q4: 419 correct)
  — see above. No batch script or CSV for either question has still been supplied by any source.
- **Now confirmed, Q1's own figure, previously entirely unvalidated at full scale:** the 28/07 methodology
  note's §6.1 states `LinearSearch` was "validated against the FULL Question 1 dataset (1,343 submissions,
  correct and wrong combined): zero mismatches between LinearSearch and GuardedInput across all 1,342
  usable files" — 1,343 matches the Refactory Q1 corpus total (768 + 575) logged from Table 3/Table 2
  everywhere else in this doc. No batch script or CSV for this run has been supplied.
  **Superseded by the real batch run logged below** — see "Real batch-validation RESULTS for Q1-Q4," which
  supplies the actual `q1_report.csv` this claim was made about, and finds the "1,342 mismatch-free" framing
  itself needs a small correction (it's actually a full 1,343/1,343 exact match once a `pandas` NaN-vs-NaN
  comparison artifact is accounted for — see that section for the direct CSV proof).
- **A "level" convention for competencies** (0 = primitive, level-*n* composed only of level-(*n*-1)
  children) — not anticipated by the old `VERSIONING.md` at all. **Dating now fully resolved (previously
  an open puzzle in this log): the concept, its 4-violator count, its technical blocker, and both
  level-2 shapes (`ANY`-of-alternatives and `ValidatedAccumulation`'s `AND`-of-different-skills) were
  designed and demonstrated around 2026-07-21** (`Levels_of_competencies_21_07.docx`, independently
  corroborated by `Competency_Extraction_Methodology_V24.docx`'s own §2.12, which still calls it
  "documented, not enforced" and is therefore itself dated to on/around 21/07); **the design-principle
  comment was first committed into a saved `competency.py` at the `fixQ2` checkpoint (2026-07-28); and
  code-level enforcement (`level()`/`check_layering()`/`register()`-time `LayeringViolation`) is
  code-confirmed as of `files_Enforcement` (same day)** — living in the core framework, not in
  `pw01_competencies.py` as the intervening conversation narrative had suggested. The conversation's claim that
  `TopKPattern`'s violation was "genuinely irreducible" **did not hold** — `files_Fix_Q4` resolves it via
  `LoopStep2`/`RemovalAssignStep` lifting wrappers, which also required a real, undocumented-in-conversation
  `NESTED` bug fix (composite-evidence identity comparison) to work correctly. `BubbleSortPass` remains
  the one confirmed-irreducible exception across every supplied file. **`level2_examples.py` (the
  standalone file) has now been supplied and directly executed** — `AverageStrict` and
  `ValidatedAccumulation` are fully code-confirmed, matching every conversation-quoted figure exactly (see the
  "Q2 fix + third strategy" §5 above for the full execution transcript).
- **A canonical, numbered bug table, originally 13 entries, now extended to 19**, supplied in full by
  `Competency_Extraction_Methodology_V24.docx` (bugs #1-13) and the 28/07 methodology note (bugs #14-19) —
  every bug number this log had previously cited individually is now cross-referenced against a single
  authoritative, growing table rather than reconstructed from scattered mentions across multiple conversation
  documents. Bugs #15-17 also resolve the three "named but not yet evidenced" items previously sourced
  only from `To_copy_to_new_project.docx`'s one-line summaries; bug #19 similarly resolves that document's
  `BubbleSortPass`-resolver-obstacle item. (See "The 19-entry canonical bug table" section above for full
  text of #14-19, and the separately-flagged, still-open discrepancy over whether the paper's own "19
  structural + 2 informational = 21" framing counts the same set as this table's 19.)
- Still not reached in any supplied checkpoint: the embedding/Table-5 experiments (now confirmed to belong
  to a distinct, still-unsupplied "companion paper," not `semantic_backup.py` — though this round adds the
  first real Colab-executed evidence toward it, see the "Real-CodeBERT/CodeT5+ Colab validation" section
  above), `CountedSearch`'s own lifted-siblings replacement code, and a possible later methodology-doc
  version (V25+ — now a sharper question, since the 28/07 note supplied this round still lacks Q3/Q4
  content despite matching `Summaize_to_move_the_project_28.docx`'s date). Full Q1 batch validation is
  **now resolved** (1,343/1,342, zero mismatches, per the 28/07 methodology note's §6.1) — removed from
  this list. **`Competency_Extraction_Article.docx` is now also resolved** — supplied and read in full
  (see the dedicated section above), and directly confirmed, by its own text (still-unenforced layering,
  13 bugs, no Q1-Q4 numbering, no `SortByKey`), to predate everything the finished paper and the 28/07
  note contain — removed from this list too. It also supplies a fourth, older data point on the "33%"
  Q2-figure inconsistency (see the dedicated write-up above), shifting the balance of evidence toward
  "33% meant the alternative, non-counter strategy" as the originally-intended reading.

**Action:** once enough real checkpoints are logged here to reconstruct the actual chronology up to the
paper's final state, rewrite `VERSIONING.md` and populate `detectors/vX.Y.Z/` from this log instead of
the earlier guesses. Until then, treat every specific claim in the old `VERSIONING.md` as unconfirmed.

---

## The finished paper draft cross-checked against the repo's own held-back Table 4 and Table 5 — `Ver. 2026.8.23 IJIES_Format_paper.docx`

Sonia's question: "Is Table 4 adequate to the paper draft" — accompanied by the paper draft itself
(docx metadata: created and modified both 2026-08-23, consistent with the filename). This is the same
version already on file as the Project doc of the same name (content compared directly, not assumed
identical).

**Table 4, cell for cell, is an exact match** between the paper draft and this repo's own
`scripts/regenerate_table4.py --stage final --check`, including sample sizes:

| Q | Task | Target competency | Correct (n) | Wrong (n) |
|---|---|---|---|---|
| 1 | Sequential search | GuardedInput / LinearSearch | 99.5% (768) | 97.6% (575) |
| 2 | Unique day/month | UniqueCheck | 90.4% (291) | 74.3% (435) |
| 3 | Duplicate elimination | SelectionStep | 94.0% (546) | 74.7% (308) |
| 4 | Sort tuples by age | SortByKey | 77.6% (419) | 45.9% (357) |
| 5 | Top-K | TopKPatternExtended | 91.9% (418) | 80.6% (108) |

Both sides agree on every cell; the regeneration script's own output was re-run fresh against this
question (not read from memory) and confirms the same five rows verbatim. The narrative around Table 4
in this draft is also consistent with everything already logged: the Q4 SortByKey = ANY(BubbleSortPass,
TopKPattern) story (13.1%/64.4%/77.6%, still conversation/paper-reported only, no CSV — a caveat already on file
in `docs/KNOWN_CAVEATS.md` and unaffected by this cross-check), the Q5 79.7%→91.9% delegation-fix
progression with the same "latent false-positive mode, not yet fully characterized" caveat this repo's
own `TopKPatternExtended` README carries, the Q1 GuardedInput/LinearSearch naming distinction, and Q2's
90.4% three-strategy story.

**Table 5 (semantic backup layer validation) is also an exact match** to the numbers this session's third
mine_exemplars-thread round (`detectors/2026-09-17_semantic_backup_validation_executed/`) independently
reproduced by direct execution, down to three decimal places on the SAME/CROSS/UNRELATED means:

| Metric | lexical | codet5p |
|---|---|---|
| Pairwise win rate | 90.6% | 84.2% |
| Worst-case ranking | 74.1% | 81.5% |
| SAME mean | 0.643 | 0.695 |
| CROSS mean | 0.402 | 0.434 |
| UNRELATED mean | 0.296 | 0.283 |

This is the first time a finished paper draft supplied to this project has reported the *post-scoping-fix*
Table 5 numbers — the earlier reference documents (flagged two rounds ago) described an intermediate,
pre-fix state, and the round immediately above this one independently verified the fix itself
(`DELEGATING_FUNCTION`/`runtime_scoped_exemplar()`) as real, delivered code producing exactly these
numbers by direct execution, not merely reading them here. The paper's own narrative matches precisely:
the scope-mismatch bug, its effect on lexical only (88.4%→90.6%, 55.6%→74.1%) and not on codet5p (84.2%
and 81.5% both before and after), and the corrected, smaller worst-case gap (7.4 points, not the earlier
apparent 25.9). The paper's further "call-site blind spot" probe (codet5p 0.961–0.977 vs. lexical
0.776–0.813 across three broken-delegation variants) also matches this session's independently-executed
`Case 1/2/3` moyenne()/DelegatesUniqueness checks and the notebook's own real output exactly — the
lexical-side structural values (`0.811/0.776/0.813` vs. the notebook's `0.811, 0.776, 0.813`) line up
figure for figure.

**Answer to Sonia's question**: yes — Table 4 is fully adequate to this paper draft, and so is Table 5,
which is a new, stronger confirmation than has existed before this round (the repo's own independent
execution and the finished paper's reported numbers now agree exactly, not just narratively). No
discrepancy found anywhere in either table or their surrounding narrative text.

---

## Refactory corpus license check (2026-09-18) — `POPULATE.md` step 9, and a real misattribution corrected

**A note on evidence type, since it departs from this log's own rule above**: every other entry in this
log is grounded in something Sonia supplied — code, a conversation export, a paper draft. This entry's evidence is
different in kind: a live fetch of the corpus's own public GitHub repository, performed directly by
the assistant during this round, not something Sonia provided. It is included here under the same discipline —
quoted, not paraphrased from memory, and the exact source URL is given — but flagged explicitly as a
different evidentiary basis than the rest of this log.

**Source checked**: [github.com/githubhuyang/refactory](https://github.com/githubhuyang/refactory), the
repository released by Hu, Ahmed, Mechtaev, Leong & Roychoudhury alongside "Re-factoring Based Program
Repair Applied to Programming Assignments" (ASE 2019) — this project's own paper reference [3]. Fetched
directly, 2026-09-18.

**Findings, quoted from the fetched pages:**

- Root file listing includes a file literally named `LICENSE`, alongside `data.zip`, `README.md`,
  `ASE19.pdf`, and the tool's own source (`basic_framework/`, `docker/`, `run.py`, etc.) — no subdirectory
  or file carves out separate terms for `data.zip`.
- The `LICENSE` file's fetched content is the full GNU Lesser General Public License v3 (dated 29 June
  2007) — not a stub or placeholder. GitHub's own license-detection badge on the repo page independently
  agrees: "LGPL-3.0 license".
- README, quoted verbatim: "If you use any part of our Refactory tool or data present in this repository,
  then please do cite our ASE-2019 Refactory paper." — a citation request, not a separate legal
  restriction beyond LGPL-3.0 itself.
- README also states `data.zip` contains "2442 correct and 1783 buggy program attempts by 361
  undergraduate students" from an NUS intro-Python course — matching this project's own Table 3 exactly in
  total submission count (2,442 correct + 1,783 wrong = 4,225, matching the sum of Table 3's five rows: 768
  +291+546+419+418=2,442 correct; 575+435+308+357+108=1,783 wrong).
- No sentence anywhere in the fetched README addresses student consent, anonymization, or any
  dataset-specific redistribution restriction separate from the blanket LGPL-3.0 grant.

**A real documentation bug found in the course of this check**: `data/submission_ids/README.md` previously
read "The Refactory corpus (Ureel & Wallace — paper reference [3])". No such name appears anywhere in this
project's own paper, its reference list, or any artifact in this log. The paper's actual reference [3] is
Hu, Ahmed, Mechtaev, Leong & Roychoudhury, confirmed directly against `paper.txt`'s own bibliography
(`[3] Y. Hu, U. Z. Ahmed, S. Mechtaev, B. Leong, and A. Roychoudhury, "Re-factoring Based Program Repair
Applied to Programming Assignments," ... ASE 2019`). The origin of "Ureel & Wallace" is not established —
corrected in `data/submission_ids/README.md` rather than left standing.

**Conclusion, and what did/didn't change**: LGPL-3.0, taken literally, would not prohibit redistributing
the submission source code itself. But it is a software-library license applied, without any
dataset-specific carve-out, to a corpus of identifiable student coursework whose own authors' consent to
redistribution is undocumented — a real gap the license text itself is silent on. This repository's
existing design already never redistributes the source (`data/submission_ids/*.csv` holds only
`submission_id` + `label`; `data/labels_scores/qN_final.csv` holds only IDs and derived scores), so no
script or data file changes as a result of this check. `POPULATE.md` step 9 is marked done, and
`data/submission_ids/README.md`'s "On redistributing the corpus itself" section now records these findings
directly, with the citation the source README requests.

---

## The "nineteen vs 21/22 bug count" discrepancy — checked directly against the actual IJIES submission draft (2026-09-18)

This log's own prior entries (see line references below) correctly documented, round by round, that the
"Structural_Competency_Extraction_Paper" lineage's §5.6/Table 4 text kept saying "nineteen structural
defects... a further two informational... = 21" even as the methodology note's own canonical bug table
grew past 21 (to 22, per the mine_exemplars-era rounds). Every one of those entries was accurate against
the specific paper draft it was checking at the time. What had not been checked directly until now:
whether that sentence survives into `Ver. 2026.8.23 IJIES_Format_paper.docx` — the actual journal
submission draft, already confirmed exact on Table 4 and Table 5 in "The finished paper draft cross-checked
..." section above.

**Direct check, this round**: `grep -i "nineteen"` against `/tmp/paper_check/paper.txt` (the extracted text
of `Ver. 2026.8.23 IJIES_Format_paper.docx`, same extraction already used for the Table 4/5 cross-check)
returns zero matches anywhere in the document. §6 Discussion, read in full, is prose design principles
(strict layering enforcement and its behavioral-neutrality check via `AverageStrict`, coverage/structure
separation, "a broad primitive type is not a safe proxy for a specific operation," composite-evidence
upward-propagation only on nonzero score, equivalence-as-explicit-ANY, the shared-library argument via
TopKPattern's and FindExtremum's transfers, the clustering-needs-checking-not-just-running lesson from the
Q5 delegation discovery, the DAG-vs-single-node-recursion boundary motivating `EXHAUSTIVE_CHAIN`, and the
provisional-until-batch-validated caution the Q4 taxonomy correction illustrates) — no numbered bug table,
no "nineteen," no bug count of any kind.

`pdftotext` run against every dated PDF snapshot in `papers/` locates the sentence precisely:

| Snapshot | Contains "nineteen"? |
|---|---|
| `2026-08-04_Structural_Competency_Extraction_Paper.pdf` | Yes |
| `2026-08-05_..._final_22p.pdf` | No |
| `2026-08-05_..._final_22p_q4embedding_added.pdf` | No |
| `2026-08-05_..._intermediate_21p.pdf` | No |
| `2026-08-08_Structural_Competency_Extraction_Paper.pdf` | No |
| `2026-09-10_Structural_Competency_Extraction_Paper.pdf` | Yes |

The two "Yes" rows are both the internal "Structural_Competency_Extraction_Paper" lineage — the
later-dated 2026-09-10 snapshot is a later save of the *same* unreformatted lineage as 2026-08-04, not a
revision of the three 2026-08-05/2026-08-08 snapshots in between (consistent with `papers/README.md`'s
existing note that PDF save dates in this project don't always track a single linear revision history).
`Ver. 2026.8.23 IJIES_Format_paper.docx` is a separate reformatting track entirely — confirmed by its own
`docProps/core.xml` (`dcterms:created`/`dcterms:modified` both `2026-08-23`) — and its §6 has no bug-count
narrative in any form, not a corrected one.

**Conclusion**: this was a real, correctly-reported discrepancy against every paper draft checked up to and
including the 2026-09-12 round, and remains real and uncorrected within the internal
"Structural_Competency_Extraction_Paper" lineage if that lineage is ever revisited. But it does not apply
to `Ver. 2026.8.23 IJIES_Format_paper.docx` — the actual submission draft dropped the entire numbered
bug-count narrative when reformatted into IJIES style, rather than updating its count. Nothing in the
paper Sonia is actually submitting needs correcting on this point. (Prior mentions of this discrepancy,
for reference: lines ~1507, ~1536-1542, ~2195, ~2272, ~2441, ~2758, ~4048 above, each accurate to the draft
it was checking at the time and left as originally written, per this log's own evidence-preservation
discipline.)

## Exemplar registry (`data/exemplar_registry/`) merged into the repo — POPULATE.md step 6, done (2026-09-18)

Sonia asked directly, about step 6's own framing ("le registre d'exemplaires enrichi et réellement miné
existe déjà en code... mais n'est pas encore fusionné dans `data/exemplar_registry/`"): *"Que dois je faire
au juste?"* Investigated before answering: the real, verified 10-competency/27-exemplar `EXEMPLAR_REGISTRY`
already existed as delivered code in
`detectors/2026-09-17_semantic_backup_validation_executed/semantic_backup.py` — this repo's own most
current and most audit-clean semantic-backup checkpoint (that checkpoint's own README documents
`audit_registry()` reporting zero problems against the complete real chain, for the first time in this
project). Nothing new was needed from Sonia; the merge was mechanical, in the same spirit as
`scripts/build_submission_ids_from_batch_reports.py`.

**What was built and run**: `scripts/build_exemplar_registry.py`. It extracts the checkpoint's embedded
`competency.py`/`test_real_data.py`/`pw01_competencies.py`/`q2_competencies.py`/`report.py` (they live only
inside `semantic_backup_validation.ipynb`'s own source cells in this checkpoint — same extraction routine
as `scripts/regenerate_semantic_backup_v3_audit.py`), builds the real, full competency model
(`test_real_data -> pw01_competencies -> q2_competencies`), and for every one of the 27 exemplars calls
`model.resolve()` directly — the live structural rules, not a copied prior score. Result, this run:
`audit_registry()` reports 0 problems; all 27 exemplars score `final_score=1.0000`. Written to
`data/exemplar_registry/exemplars.csv` (replacing the earlier 2-competency/5-exemplar stub) and
`data/exemplar_registry/code/*.py`.

**Per-exemplar provenance** (the `source` / `source_submission_id` / `notes` columns) was transcribed
directly from `semantic_backup.py`'s own inline comments, not inferred or guessed. Quoted verbatim, the
comments that establish this:

- `ConditionalCount` exemplar #3 (index 3): *"Real, mined via mine_exemplars.py from
  question_2/code/correct (correct_2_010.py), verified final_score=1.00."* — exact submission ID
  `correct_2_010` recorded.
- `ConditionalCount` exemplar #4: *"Real, mined (correct_2_016.py), verified final_score=1.00."* — exact
  submission ID `correct_2_016` recorded.
- `AccumulateThenCount` exemplar #0: *"Real, verified: this is one of only 2 (of 291) question_2
  submissions that structurally satisfy AccumulateThenCount, mined via mine_exemplars.py -- both real
  matches collapse to this exact shape."* — marked `mined`, no single filename named in the comment, so
  `source_submission_id` left blank rather than invented.
- `AccumulateThenCount` exemplars #1-2: both explicitly *"CORRECTED (see semantic_backup_findings.md,
  finding #7)"* — replacements for originals that scored `final_score=0.00` (`len()`-based, not
  `.count()`-based) — marked `hand-written (corrected)`.
- `GuardedInput` exemplars #0-1: both explicitly *"CORRECTED... the original two exemplars here BOTH
  scored final_score=0.0 under the actual structural resolver"* (bare `while`-condition, no nested `if`,
  so no TEST evidence registers) — marked `hand-written (corrected)`.
- `FunctionalUniqueCheck` (all 3): comment above the dict entry — *"Real, mined via mine_exemplars.py from
  question_2/code/correct (unique_day), all verified final_score=1.00... 13/291 (4.5%)... 11 distinct
  structural shapes"* — marked `mined`, no per-exemplar filename named, so `source_submission_id` left
  blank; the `notes` column records the shape name (`InlineFunctionalCheck` / `GuardedFunctionalCheck` /
  `InlineTestFunctionalCheck`) and the mining-run proportion instead.
- `DelegatesUniqueness` (all 3): comment above the dict entry — *"Real, mined via mine_exemplars.py's
  mine_cross_function()... 227/291 (78%)... 96 distinct structural shapes"* — same treatment: `mined`,
  `source_submission_id` blank, shape description in `notes`. These three store both `unique_day` and
  `contains_unique_day` (needed for `DELEGATES` verification via `audit_registry()`); `runtime_scoped_exemplar()`
  scopes them to `contains_unique_day` alone at every actual embedding call site, matching what
  `report.py` passes for a real submission — the registry storage (and this merge's `.py`/CSV files)
  reflect the full, unscoped two-function form, per the module's own documented design.
- Everything else (`Swap` both, `Accumulation` all 3, `ConditionalCount` #0-2, `SelectionStep` both,
  `FindExtremumBuiltin` both, `TopKPattern` both) carries no mined/corrected claim in its comment — marked
  `hand-written`.

Full per-row detail is in `data/exemplar_registry/README.md`, rewritten this round to replace the old
stub's documentation. `POPULATE.md` step 6 marked DONE; `configs/stage_manifest.yaml`'s
`exemplar_registry_real_mined` (v1) and `exemplar_registry_real_mined_v3_executed` entries each got a short
forward-pointer `UPDATE (2026-09-18)` note pointing at this merge — their original descriptions, written at
the time of each round, are left exactly as they were, per this log's own evidence-preservation discipline.

**What this does NOT touch**: Table 4, the Q5 TopKPatternExtended delegation breakdown, and POPULATE.md
step 4 (the embedding train/test split indices) — step 4 remains the only genuinely unsupplied item in
this repo, still dependent on Sonia's own Colab/Drive artifacts. `scripts/regenerate_table4.py --stage
final --check` (5/5 rows match) and `pytest tests/ -q` (11 passed) both re-run clean after this merge.

**Evidence type note, same caveat as this log's other recent entries**: this entry's own verification (the
`model.resolve()` re-run, the `audit_registry()` re-run) is a live re-execution performed in this session
against Sonia-supplied code, not a claim taken from a conversation transcript — consistent with everything else
`scripts/build_exemplar_registry.py` writes being freshly computed, not copied.

## Checkpoint-naming pilot rename — `detectors/2026-07-21_reporting_batch` → `detectors/reporting-batch` (2026-09-19)

Sonia asked to remove dates from this repo's checkpoint-folder naming, given its actual destination
(published on GitHub, read by reviewers) — the recommended approach (git-native versioning: stable
kebab-case folder slugs; real dates kept exactly where they already live in prose/CHANGELOG/this log; git
tags/commits, honestly dated at actual push time and never backdated, as the citable version mechanism once
this is a real repo) was approved for a scoped pilot on exactly one checkpoint first: `detectors/
2026-07-21_reporting_batch/` → `detectors/reporting-batch/`.

**Mechanics**: confirmed the checkpoint's own `README.md` independently states the real date in prose
("Dating is by inference from the 2026-07-21 conversation narrative...") before renaming, so nothing is lost; `mv`'d
the folder; `grep -rl` found 18 files referencing the old path string; `sed -i` updated 17 of them
(`VERSIONING.md`, both build/regenerate scripts that name it, `configs/stage_manifest.yaml`,
this log, `data/labels_scores/README.md`, `data/submission_ids/README.md`, five checkpoint READMEs,
`detectors/CHANGELOG.md`, `taxonomy/CHANGELOG.md`, `taxonomy/2026-07-18_V1.0.0_baseline/taxonomy.yaml`,
`POPULATE.md`, `docs/KNOWN_CAVEATS.md`, `papers/README.md`); `data/labels_scores/q5_final.csv` was
deliberately excluded from the blind sed pass, since it's mechanically-generated and this project's own
discipline is to regenerate those files, never hand-edit them.

**What that surfaced**: regenerating `q5_final.csv` properly (rather than hand-patching its stale path
string) required first fixing a real, pre-existing gap — `scripts/build_labels_scores_from_batch_reports.py`'s
Q5 entry had only ever built `q5_final_extended.csv`; `q5_final.csv` itself dated from an earlier, pre-script
round and had never actually been wired into the mechanical build path, even though both
`data/labels_scores/README.md` and `configs/stage_manifest.yaml`'s `q5_final` entry already (a little
prematurely) called its derivation "mechanical." Fixed by extending `QUESTION_CONFIG[5]` from a single dict
to a two-item list — the original TopKPattern-only config (source `detectors/reporting-batch/topk_report.csv`,
output `q5_final.csv`) alongside the existing TopKPatternExtended config — so `--question 5` and `--all` now
build both Q5 outputs. Regenerated against the renamed checkpoint and diffed directly against the pre-rename
file: all 526 rows' `submission_id`/`test_suite_label`/`target_competency`/`coverage_score`/`structure_score`/
`final_score`/`matched_branch` are byte-for-byte identical — only the `notes` column's embedded path string
changed, from the old `detectors/2026-07-21_reporting_batch/...` to `detectors/reporting-batch/...`.
`configs/stage_manifest.yaml`'s `q5_final` entry gained the `regenerate_script` field it had been missing
(present on `q5_final_extended` but not on `q5_final` itself). Also fixed: `taxonomy/2026-07-18_V1.0.0_baseline/
taxonomy.yaml` line 57's prose, whose only date anchor for the removal-check fix was the checkpoint name
itself — restored `(~2026-07-21)` inline alongside the renamed checkpoint reference, so the real date isn't
silently dropped by the rename.

**Re-verified clean**: `grep -rl "2026-07-21_reporting_batch" .` finds nothing outside this entry's and
`configs/stage_manifest.yaml`'s own new historical notes (which document the rename event itself, not a live
reference); `pytest tests/ -q` — 11/11 passed; `scripts/regenerate_table4.py --stage final --check` — all
five rows match, Q5 still 91.9%/80.6%; `scripts/regenerate_table5.py --section all` and
`scripts/regenerate_q5_percentages.py --all-stages` both ran clean, `q5_final`/`q5_final_extended` still
showing `detectors/reporting-batch` as the detector checkpoint with figures matching exactly (78.2%/75.0%
and 91.9%/80.6%).

**Scope**: this is a pilot on one checkpoint only, per Sonia's own request ("before I touch the rest") — the
other 23 dated checkpoint directories and their cross-references are untouched pending her review of this
one. The zip has not been rebuilt/redelivered for this round.

## Checkpoint-naming rollout complete — all remaining 23 dated checkpoints renamed repo-wide (2026-09-19)

Following review of the pilot rename above (`detectors/reporting-batch`), Sonia said to proceed with the
rest. All 19 remaining `detectors/<date>_<label>/` directories and all 4 remaining
`taxonomy/<date>_<label>/` directories were renamed to stable, date-free kebab-case slugs, using the exact
mechanics validated by the pilot: `detectors/2026-07-18_V1.0.0` → `detectors/v1.0.0`,
`detectors/2026-07-19_ex1_taxo` → `detectors/ex1-taxo`, `detectors/2026-07-19_ex2_3_4` →
`detectors/ex2-3-4`, `detectors/2026-07-19to21_V1.2.0` → `detectors/v1.2.0`,
`detectors/2026-07-20_semantic_backup` → `detectors/semantic-backup`, `detectors/2026-07-28_enforcement` →
`detectors/enforcement`, `detectors/2026-07-28_fixQ2` → `detectors/fixq2`, `detectors/2026-07-28_fixQ4` →
`detectors/fixq4`, `detectors/2026-07-28_q2_3rd_strategy` → `detectors/q2-3rd-strategy`,
`detectors/2026-07-29to30_semantic_colab_validation` → `detectors/semantic-colab-validation`,
`detectors/2026-07-31_ast_taxonomy_crossvalidation` → `detectors/ast-taxonomy-crossvalidation`,
`detectors/2026-08-05_q1_q4_batch_validation` → `detectors/q1-q4-batch-validation`,
`detectors/2026-08-05_q1_shared_binding_fix` → `detectors/q1-shared-binding-fix`,
`detectors/2026-08-05_q2_q4_embeddings_crossvalidation` → `detectors/q2-q4-embeddings-crossvalidation`,
`detectors/2026-08-07_mine_exemplars` → `detectors/mine-exemplars`,
`detectors/2026-08-08_q5_delegation_clustering_fix` → `detectors/q5-delegation-clustering-fix`,
`detectors/2026-08-08_semantic_backup_layer_validation` → `detectors/semantic-backup-layer-validation`,
`detectors/2026-08-09_mine_exemplars_real_corpus` → `detectors/mine-exemplars-real-corpus`,
`detectors/2026-09-17_semantic_backup_validation_executed` → `detectors/semantic-backup-validation-executed`;
`taxonomy/2026-07-18_V1.0.0_baseline` → `taxonomy/v1.0.0-baseline`,
`taxonomy/2026-07-28_enforcement_LinearSearch` → `taxonomy/enforcement-linearsearch`,
`taxonomy/2026-07-28_fixQ4_SortByKey` → `taxonomy/fixq4-sortbykey`,
`taxonomy/2026-07-28_q2_3rd_strategy_UniqueCheck` → `taxonomy/q2-3rd-strategy-uniquecheck`.
`detectors/_intermediate_unlabeled/` was already undated by design and untouched.

**Precondition checked before renaming, for every one of the 23**: each checkpoint's real date is
independently documented — in its own `README.md` (detector checkpoints; every one carries a real-date
statement, most in the title line itself) or `taxonomy.yaml` header comment (the four taxonomy-only
snapshots, which have no README), and/or in `detectors/CHANGELOG.md`/`taxonomy/CHANGELOG.md`'s own
tables — never solely via the folder name. Confirmed via direct grep/read of every affected README and
taxonomy.yaml before any `mv`.

**Mechanics**: a repo-wide scan for all 23 old directory-basename strings found 38 non-CSV files
referencing them (364 total string replacements — POPULATE.md, README.md, VERSIONING.md, this log, the
status doc, `configs/stage_manifest.yaml` (95 replacements alone), every affected checkpoint's own
README/taxonomy.yaml, both CHANGELOGs, `docs/KNOWN_CAVEATS.md`, `methodology/README.md`,
`papers/README.md`, and 11 scripts under `scripts/`), all updated by plain string substitution — safe
because the full dated basename (e.g. `2026-08-08_q5_delegation_clustering_fix`) is specific enough to
only ever appear as a path/identifier reference, the same reasoning validated in the pilot. 6
mechanically-generated CSVs whose `notes` columns embed a checkpoint path
(`data/exemplar_registry/exemplars.csv`, `data/labels_scores/q1_final.csv`, `q2_final.csv`,
`q3_final.csv`, `q4_final.csv`, `q5_final_extended.csv`) were deliberately excluded from that substitution
pass — this project's standing discipline is to regenerate a mechanically-produced file, never hand-edit
one, even for a path-string-only fix — and were instead rebuilt via `scripts/build_exemplar_registry.py
--write` and `scripts/build_labels_scores_from_batch_reports.py --all` once those scripts' own path
constants had already been corrected by the substitution pass above. Regenerated files were then diffed
programmatically against pre-rename backups, column by column, across all 4,252 rows (27 + 1,343 + 726 +
854 + 776 + 526): zero data-column mismatches; the only columns that ever changed were the path-bearing
ones (`notes` for the labels_scores files, `verified_detector_checkpoint` for the exemplar registry) —
confirmed by enumerating exactly which columns differed, not by spot-checking a sample.

**Three prose sentences lost their only inline date anchor** — the same failure mode as the pilot's single
`taxonomy.yaml` fix, where a sentence's grammatical point was timing something ("fixed at the X
checkpoint") and X was the *only* place that date appeared on the line. Found by narrowing the search to
temporal-anchor phrasing ("at the", "since the", "as of the", etc.) immediately before an old checkpoint
name, rather than flagging every line that merely mentions a checkpoint and loses an incidental date —
that broader, naive check flagged 276 lines, the overwhelming majority of them plain path citations (e.g.
"see `detectors/2026-08-05_q1_q4_batch_validation/README.md`") where losing the date from the *path* is
exactly the intended effect of this whole change, not a loss of evidence (the real date is still fully
recoverable from that checkpoint's own README/CHANGELOG entry, same as `reporting-batch` already
demonstrates). The 3 genuine hits, fixed by hand: `detectors/semantic-backup-layer-validation/README.md`
("a gap flagged repeatedly since the `semantic-colab-validation` checkpoint" → "(~2026-07-29/30)" added
inline) and two lines in `taxonomy/v1.0.0-baseline/taxonomy.yaml` ("added at the enforcement checkpoint"
→ "(2026-07-28)"; "Corrected at q2-3rd-strategy" → "(2026-07-28)").

**`VERSIONING.md` and `README.md` needed more than mechanical substitution**: both files had prose
*describing* the naming convention itself ("Every checkpoint folder is named `<real-date>_<label>`..."),
which the blind substitution pass correctly updated the example checkpoint names inside but left
self-contradictory, since the sentence's own claim about the naming pattern was now wrong. Both rewritten
to describe the actual new convention (stable, date-free slug; real dates live in each checkpoint's own
README/taxonomy.yaml, the CHANGELOGs' "Real date" column, and this log) and the reasoning behind it (this
repo's real destination — public GitHub, reviewer-accessed — makes a stable, citable slug clearly better
than a path that needs editing whenever a date is later corrected, which has already happened once here:
`reporting-batch`'s own date is only an inferred "~2026-07-21", not a certain one). `VERSIONING.md` also
now states plainly that git tags/commits, honestly dated at actual push time and never backdated, become
the citable version mechanism once this repo is pushed to GitHub — the folder slugs are for internal
code/doc references, not a substitute for real git history.

**Re-verified clean, full suite, after the complete rollout**: `pytest tests/ -q` — 11/11 passed;
`scripts/regenerate_table4.py --stage final --check` — all five questions match reported figures exactly,
Q5 still 91.9%/80.6%; `scripts/build_exemplar_registry.py --check` — 0 problems, all 27 exemplars
`final_score=1.0000`; `scripts/regenerate_q5_percentages.py --all-stages` — both real Q5 stages
(`q5_final`, `q5_final_extended`) match their reported figures against the renamed
`detectors/reporting-batch`/`detectors/q5-delegation-clustering-fix` checkpoints; a final repo-wide grep
for any of the 23 old directory-name strings, anywhere in the tree, returns zero hits — not even a
historical note, since (unlike the pilot) there was no prior rename event on record to document.

**Scope note**: this only ever renamed directories and updated references to them. No checkpoint's own
internal contents changed — the real, unedited batch-report CSVs each checkpoint carries
(`topk_report.csv`, `q1_report.csv`, etc.) moved with their parent folder and were never opened or edited.
`detectors/_intermediate_unlabeled/` was already undated by design and is unaffected.

## Paper and methodology raw files withheld ahead of GitHub push (2026-09-19)

Sonia asked to remove "all docs" for the paper before pushing this repo to GitHub, since the paper isn't
published yet. Scope and mechanism were clarified first rather than guessed at, given the request was both
destructive and judgment-call-heavy: whether to remove just the raw files or also strip quoted excerpts
elsewhere in this repo, and whether to delete outright or just exclude from git while keeping a local copy.
Sonia's answers: raw files only at first (brief citations elsewhere to stay), delete outright (this repo
has one local commit and no remote configured yet, so nothing has actually gone public).

**Removed**: all 15 raw files under `papers/` (11 files, 4.2MB — five dated revisions of
`Structural_Competency_Extraction_Paper`, `.docx`/`.pdf`) and `methodology/` (4 files, 712KB — two dated
revisions of the internal methodology note). Both folders' own `README.md` (a structural revision
history) are kept. Confirmed via grep before deleting that no script or test in this repo references these
files programmatically — reference-only.

**A second pass followed, prompted by re-reading `papers/README.md` and this log after the deletion**:
removing the raw docx/pdf files alone didn't actually achieve the stated goal, because both documents
contained long, verbatim block-quoted excerpts reproducing substantial parts of the unpublished paper — the
entire new §7 "Semantic Backup Layer: Architecture Overview" section, full new Abstract/§5.5/§5.6
paragraphs from the embedding-validation and Q4-split revisions, plus a methodology-doc cluster (§5.2,
§6.1, bug #22, a §9 Limitations bullet) — 125+ quoted lines combined, several full paragraphs, found by
grepping for markdown blockquote lines (`^>`) and manually classifying each hit as paper prose, methodology
prose, a code diff/comment, or a dev-session conversation-transcript quote. This was surfaced back to Sonia
explicitly, with the exact line counts and an example, rather than silently deciding either way — it
directly determines whether her actual goal (nothing paper-derived exposed pre-publication) is met, not
just the letter of "remove the raw files." She confirmed: replace the long quotes with short paraphrases
that keep the factual claim (what changed, verified against what data) but drop the paper's own prose.

**What was paraphrased**: the 4 genuine paper-manuscript quote blocks above, in both `papers/README.md` and
this log, plus the methodology-doc bullet cluster in all three of `papers/README.md`, this log, and
`methodology/README.md`. Every real, independently-verified figure these passages cited (89.1%/131 of 147,
93.6%±2.1%/204+1,266 pooled, etc.) is preserved exactly, with its script/CSV citation intact — only the
paper's/methodology note's own sentences were removed. **Left alone, after checking each was not
paper-manuscript text**: the `report.py` code diff, `test_real_data.py`'s own inline code comment, and
several dev-session conversation-transcript quotes (e.g. the AUC-interpretation correction at line ~3074, the
Q2/Q4 embedding scoping-decision reasoning) — these reproduce Sonia's own conversation messages or this repo's own
code, not the paper.

**Re-verified clean after both passes**: `pytest tests/ -q` — 11/11 passed; `scripts/build_exemplar_registry.py
--check` — 0 problems, all 27 exemplars `final_score=1.0000`; `scripts/regenerate_q5_percentages.py
--all-stages` — both real Q5 stages still match their reported figures exactly. `papers/`+`methodology/`
combined size dropped from 4.9MB to 36KB (README.md files only). A final grep for `^>` blockquote lines
across the repo (outside `detectors/`/`taxonomy/` checkpoint files, which were never touched) finds only
this repo's own reviewer-question quote in the top-level `README.md`, the `report.py` diff, the
`test_real_data.py` comment, and the one remaining conversation-transcript quote — confirmed none are paper text.

**Not yet decided**: whether to create a git commit and/or configure a remote for the actual push — this
repo has one local commit and no remote; per this session's own git-safety discipline, nothing was
committed without being explicitly asked. The zip was rebuilt and redelivered with this round's changes.

## POPULATE.md step 4 (train/test split indices) supplied and merged — discovered to be the same experiment as the already-real Q4/Q5 taxonomy embedding cross-validations, not a distinct one (2026-09-20)

Sonia supplied a zip (`split_manifests_q4_q5.zip`) containing real `split_manifest.json` +
`split_NN_{train,test}_ids.txt` files (seeds 00-09, 70/30) for both `q4_sortbykey` and `q5_topk`, pulled
from her real Colab/Drive notebooks — the last entirely unsupplied item on `POPULATE.md`.

**A conflict surfaced immediately, before anything was written.** Multiple places in this repo
(`POPULATE.md` step 4, `configs/stage_manifest.yaml`'s `table5:` notes, `README.md`'s "What's here" table)
repeatedly and explicitly stated — attributed to "the source conversation's own repeated framing" — that
`table5.q4_sortbykey_splits`/`q5_topk_splits` was a *distinct, still-unsupplied companion-paper experiment*
("likely the novel-detection/anomaly-scoring validation"), separate from the already-real
`q4_taxonomy_embedding_crossvalidation_10seed_pooled`/`q5_taxonomy_embedding_crossvalidation_10seed_pooled`
stages. But the supplied files traced back to the *same* two notebooks that back those already-real
stages (`ast_taxonomy_crossvalidation.ipynb` for Q5, `q2_q4_embeddings_crossvalidation_with_Results.ipynb`
for Q4), same source report CSVs, same seeded 70/30 split code, same reported mean/SD to the reported
precision — and for Q4, the supplied evidence CSV was byte-for-byte identical (sorted diff, zero output)
to `data/labels_scores/q4_embeddings_crossvalidation.csv`, already in this repo as `evidence: real_csv`.

Rather than silently pick an interpretation on something touching numerical-result provenance, this was
surfaced to Sonia directly: either (a) the repeated "distinct companion-paper experiment" framing was
simply wrong, and what she supplied *is* the table5 experiment, or (b) table5 really is a different,
still-missing novel-detection experiment, and what she supplied is genuine but separate evidence that
should strengthen the already-real stages rather than fill table5's PENDING fields. She confirmed (a).

**What changed, mechanically:**
- `data/splits/q4_sortbykey/` and `data/splits/q5_topk/` now hold the real `split_manifest.json` +
  20 `split_NN_{train,test}_ids.txt` files each.
- `scripts/regenerate_splits.py` was rewritten end to end — the old version was a scaffold placeholder
  assuming a single `seed` field and sklearn's stratified `train_test_split`, neither of which matches
  what the notebooks actually did (a `seeds` list, plain pandas `.sample(frac=1, random_state=seed)`,
  no stratification). The new version recomputes each experiment's labeled subset directly from
  `detectors/q1-q4-batch-validation/q4_report.csv` / `detectors/reporting-batch/topk_report.csv`,
  replays the real split code for all 10 seeds, and diffs against the recorded ID files. Independently
  reproduced in this session: `--check` passes with an exact match on every seed, both experiments,
  computed entirely from files already in this repo (not from Sonia's supplied evidence CSVs).
- `configs/stage_manifest.yaml`'s `table5.q4_sortbykey_splits`/`q5_topk_splits` PENDING fields are now
  filled with real values (`split_dir`, `taxonomy_checkpoint`, `detector_checkpoint`, `embedding_model`,
  `reported_mean`, `reported_sd`, `status`), each with a full evidence-trail note. Four separate places in
  the same file that previously asserted these were distinct/unsupplied companion-paper experiments
  (`q4_taxonomy_embedding_crossvalidation_10seed_pooled`'s own note, `q5_taxonomy_embedding_crossvalidation`'s
  note, the `semantic_backup` section's note, and `table5:`'s own header comment) each got an appended
  `UPDATE (2026-09-20):` correction — the original wrong text was kept, not deleted, per this repo's
  evidence-preservation practice.
- `data/splits/README.md`, `POPULATE.md` (step 4, step 7, step 8), `README.md`'s "What's here" table, and
  `VERSIONING.md` were all updated the same way — correction appended, original claim preserved for
  history.
- Also corrected in `data/splits/README.md`: the ID scheme. The earlier scaffold-only version claimed
  split IDs would match bare `submission_id` values (`data/submission_ids/*.csv`, no extension); the real
  files actually use the `file` column with its `.py` extension, matching `q4_report.csv`/`topk_report.csv`
  exactly — confirmed, not assumed, since those are the same files the split code itself reads.

**Verification asymmetry, carried over honestly rather than smoothed out**: Q4's all 10 seeds are
independently confirmed (byte-exact match to the notebook's own saved pooled predictions). Q5's seed 0 is
independently confirmed (byte-exact match to a separately-recorded single-run CSV already in this repo);
seeds 1-9 are real split-membership, newly recorded for the first time, but produced by replaying the
confirmed deterministic code rather than checked against an independently-recorded per-seed artifact —
because the notebook's multi-seed loop never exported per-seed file lists, only the printed aggregate
accuracy. `q5_taxonomy_embedding_crossvalidation_10seed_pooled`'s `evidence:` field is therefore left as
`real_notebook_output`, not upgraded to `real_csv`, by this round — the accuracy figures for seeds 1-9 are
still transcribed from printed output, not recomputed from a raw predictions file. Only the split
membership is new; the underlying per-file predictions for those 9 seeds still don't exist as a raw
artifact anywhere in this project.

**Re-verified clean after this round**: `python3 scripts/regenerate_splits.py --experiment q4_sortbykey
--check` and `--experiment q5_topk --check` — all 10 seeds exact match, both experiments;
`scripts/regenerate_table4.py --stage final --check` — all five questions still match; `pytest tests/ -q`
— 11/11 passed; `scripts/regenerate_table5.py --section all` — Q4/Q5 sections now print real values
instead of `PENDING` (the semantic-backup section's two unrelated `PENDING` backend items,
`jina_v2_code`/`codet5p_110m_embedding`, are untouched and still open, per `POPULATE.md`).

Every item on `POPULATE.md`'s list is now done. What remains open in this repo is unrelated: the two
semantic-backup-layer backend items just named, and whether to create a git commit/remote for the actual
GitHub push (still not done, per this session's git-safety discipline — nothing committed without an
explicit ask).

**One more thing this round's fresh-venv extraction check caught**: `environment/requirements.txt` never
declared `pandas`, even though `scripts/regenerate_semantic_backup_auc.py` already imported it — a
pre-existing gap, not something this round introduced, just never hit before because that script hadn't
been run in a genuinely clean venv as part of this repo's own verification loop. The new
`scripts/regenerate_splits.py` also needs it. Added `pandas>=2.0` to `environment/requirements.txt` and
re-ran the fresh-venv check (`python3 -m venv` + `pip install -r environment/requirements.txt`, then every
regeneration script + `pytest`) end to end — clean.

## Sonia asked whether `codet5p_110m_embedding` was actually executed, and where to find the code — found a second, smaller manifest inconsistency in the same session (2026-09-20)

Following the split-index work above, Sonia asked directly: was the `codet5p_110m_embedding` semantic-backup
backend (marked `PENDING`/`CODE_EXISTS_NOT_VALIDATED` in `stage_manifest.yaml`) actually run anywhere, or
where could she find the code to run it herself. Checked the notebook `stage_manifest.yaml`'s own entry
cites, `detectors/semantic-colab-validation/semantic_backup_validation_30.ipynb`: parsed the raw `.ipynb`
JSON directly (not just the manifest's prose) — all 19 cells have `execution_count: None` and zero
outputs, confirming that specific notebook was genuinely never run; cell 8 (the compatibility-fix +
model-load code) was extracted and shown to Sonia as the code she could take and run herself.

But the same cell-8 code (same checkpoint, same `trust_remote_code` compatibility fix, near byte-identical)
turned out to already be executed, with real output, in a *different* checkpoint's notebook:
`detectors/semantic-backup-layer-validation/semantic_backup_layer_validation_with_Results.ipynb`, cell 8 —
confirmed via the same raw-JSON check (17 real outputs, including Hugging Face download logs) and its
printed result extracted directly: `related vs related: 0.8398723602294922`, `related vs unrelated:
0.3819599151611328`, a real, clean separation (unlike `codebert`'s anisotropy failure). This same number
was already logged elsewhere in `stage_manifest.yaml`, under the sibling `codet5p_bootstrap_novel_vs_wrong_auc`
stage's own `reported_result` ("the first-ever codet5p-110m-embedding sanity-check pair"), and in that
checkpoint's own `README.md` — but `codet5p_110m_embedding`'s own note still flatly said "No sanity-check
similarity number... has ever been supplied for this backend," uncross-referenced to either.

Unlike the split-index conflict above, this one wasn't ambiguous — the evidence was unambiguous and already
present, twice, in the same file — so it was corrected directly rather than escalated: appended an `UPDATE
(2026-09-20):` note to `codet5p_110m_embedding` in `configs/stage_manifest.yaml` pointing to the real number,
its actual source location, and explaining why it doesn't change this entry's own `status` (the 43-vs-108
contaminated/backwards comparison this entry describes is still the only result run under *that specific*
description; the fixed, non-contaminated version of the layer's actual job is the separate, already-real
`codet5p_bootstrap_novel_vs_wrong_auc` stage). Original text left in place, not deleted. Re-verified: YAML
still parses, `pytest tests/ -q` still 11/11, `regenerate_table5.py --section all` still prints the same
`[PENDING] status = CODE_EXISTS_NOT_VALIDATED` line (only the note field changed, not the status a reader
sees in the table).

## Sonia asked to remove references to "chat" from the narrative documents; the `chat_reported_only` evidence label was renamed system-wide to `conversation_reported_only` (2026-09-21)

Sonia's message: "So, is it possible to remove all references to the word 'chat' in the
detector-version-log.md and other narrative documents?" I scoped this before touching anything, since two
things made a blind find/replace unsafe: (1) 12 real, on-disk filenames legitimately contain "chat" as a
literal token (e.g. `mine_exemplars_chat.txt`, `semantic_29_chat_export.txt`) and must never be renamed —
this repo's whole reproducibility premise is that filenames cited in prose match what's actually on disk;
(2) the evidence-grading vocabulary in `configs/stage_manifest.yaml` (`evidence: real_csv` >
`evidence: real_notebook_output` > `evidence: chat_reported_only`) uses "chat" as a controlled-vocabulary
value, not just prose, so a rename there has to be applied consistently everywhere that value is quoted,
not just where the bare word "chat" appears.

Asked via AskUserQuestion whether the intent was purely cosmetic (reword prose, leave the evidence label
alone) or whether the evidence-grading label itself should be renamed too. Sonia's answer: **"Rename the
evidence label too"** — reword the prose AND rename `chat_reported_only` system-wide, keeping its exact
meaning (still the weakest evidence tier: a number only ever stated in a conversation, never independently
checked against raw data).

**What changed.** Chose "conversation" as the neutral replacement word (not "transcript" — "chat
transcript" would have collapsed to the redundant "transcript transcript"; "conversation" composes cleanly
with every existing compound: "chat export" -> "conversation export", "chat transcript" -> "conversation
transcript", "chat history" -> "conversation history", "chat's" -> "conversation's"). Renamed the evidence
label `chat_reported_only` -> `conversation_reported_only` throughout.

**Protected from the rewrite, explicitly enumerated before running anything:**
- All 12 real on-disk filenames containing "chat" (untouched — confirmed by re-running `find . -iname
  "*chat*" -type f` after the edit and diffing against the same list taken before it: byte-identical).
- Two verbatim historical-filename citations that do NOT match any current on-disk name (delivered docx
  files this project never checked in, cited only for provenance): `Chat_Semantic_Backup_Second_Role_08_08_
  After_clustering.docx` (cited in `configs/stage_manifest.yaml`, this file, and
  `detectors/semantic-backup-layer-validation/README.md`) and `This is the real Refactory
  corpus_mines_exemplar_2ndt chat.docx` (cited in `detectors/mine-exemplars-real-corpus/README.md`) —
  confirmed via `find . -iname "*corpus_mines_exemplar*"` that the second one exists nowhere on disk under
  any name, i.e. it is a pure historical citation, not a stale reference to a removed file.

**Method.** Wrote a small script (not a blind `sed`) that (1) masks every protected string above with a
placeholder before touching anything, (2) applies `\bchat_reported_only\b` -> `conversation_reported_only`
as its own exact-token pass (underscore-joined, so the word-boundary regex in step 3 would not reach it on
its own), (3) applies a case-preserving `\b[Cc]hat\b` -> `conversation`/`Conversation` word-boundary
replace (word boundaries mean this automatically leaves every underscore-joined filename token alone, since
`_` counts as a word character — no boundary exists between `_` and `chat`), (4) unmasks the protected
strings back to their original text. Applied across 29 `.md`/`.yaml` files (`README.md`, `POPULATE.md`,
`VERSIONING.md`, this file, `provenance/reproducibility-repo-scaffold-status.md`, `configs/stage_manifest.yaml`,
every `detectors/*/README.md`, `taxonomy/*.yaml`, `taxonomy/CHANGELOG.md`, `detectors/CHANGELOG.md`,
`docs/KNOWN_CAVEATS.md`, `methodology/README.md`, `papers/README.md`, `data/labels_scores/README.md`) plus
7 `scripts/regenerate_*.py` files whose docstrings/comments referenced "chat" or `chat_reported_only`
narratively (confirmed first, via grep, that no script does an actual string-comparison against the literal
value `"chat_reported_only"` anywhere — every hit was in a comment or docstring, so this was safe prose
cleanup, not a functional change). 528 replacements across the doc set, 26 more across the scripts.

**Verified, not assumed:**
- Real filenames: identical before/after (`find . -iname "*chat*" -type f` diff, zero changes).
- Both historical citations: grepped for their exact original strings after the run — both present,
  character-for-character, in every file that cites them.
- No stray bare "chat"/"Chat" left anywhere in the 36 touched files except inside the two protected
  citation strings themselves (expected, since the citation text legitimately contains that word as part of
  someone else's original filename).
- `python3 -c "import yaml; yaml.safe_load(...)"` — YAML still parses.
- `python3 -m py_compile` on all 7 touched scripts — all compile.
- Full fresh-venv rebuild (`python3 -m venv`, `pip install -r environment/requirements.txt`) then ran every
  `scripts/regenerate_*.py` script and `pytest tests/ -q`: Table 4, Table 5, Q5 percentages, both split
  regenerations (`--check`, all 10+10 seeds exact match), the semantic-backup AUC audit, and the taxonomy
  cross-validation script all ran clean and printed the same numbers as before this change (only the prose
  around them changed); `pytest tests/ -q` — 11/11 passed, same as before.
- `configs/stage_manifest.yaml`'s `chat_reported_only` count before this change was 16 (matching the count
  already recorded when this task was first scoped); `conversation_reported_only` count in the same file
  after the change is 16 — a 1:1 rename, nothing added or dropped.

## Hardcoded `/home/claude/refactory` sandbox path made portable (2026-09-21)

**Why.** 14 scripts under `detectors/` (mostly `test_real_data.py` per checkpoint, plus two
`mine_exemplars.py` variants and `report_demo.py`) hardcode `/home/claude/refactory/...` as the location
of the real Refactory corpus. That path is an artifact of the sandbox this project was originally
developed in, not something anyone cloning this repository would have — verified directly (`ls
/home/claude/refactory` → does not exist), and already noted as such earlier in this log ("A second
mine_exemplars batch," 2026-09-17) and in two detector READMEs. Sonia asked whether this could be made a
relative path instead.

**What changed.** Each of the 14 files now resolves the corpus location as `REFACTORY_ROOT`: the
`REFACTORY_ROOT` environment variable if set, otherwise a path computed relative to the script's own file
location (`os.path.dirname(os.path.abspath(__file__))`, walking up two directories for files directly
under `detectors/<name>/`, three for the one nested under
`detectors/mine-exemplars-real-corpus/original_files_used_this_round/`) pointing at
`<repo-root>/refactory/`. Every `"/home/claude/refactory/..."` string literal became an f-string
(`f"{REFACTORY_ROOT}/..."`); nothing about the actual sub-path structure under the corpus root changed.
The corpus itself is still not redistributed with the repo (third-party data), so `refactory/` is not
committed — a reader who wants to actually run these specific test/mining scripts against real data
drops the corpus at the repo root themselves, or points `REFACTORY_ROOT` elsewhere.

**Deliberately left untouched:** the historical narrative mentions of the literal
`/home/claude/refactory/...` path elsewhere in this log (the V1.0.0 entry above, and the "second
mine_exemplars batch" entry) and in `detectors/mine-exemplars-real-corpus/README.md` /
`detectors/mine-exemplars/README.md` — those describe what the code and the checking sandbox actually
used/found at specific past checkpoints, and rewriting them to match today's mechanism would misstate
history rather than record it.

**Verified, not assumed:**
- `grep -rn "/home/claude/refactory" --include="*.py"` outside this log: 0 hits after the change (was 66
  occurrences across the 14 files before).
- `python3 -c "import ast; ast.parse(...)"` on all 14 touched files: all parse (an earlier pass of this
  same edit inserted the new block in the middle of a multi-line `from competency import (...)` statement
  in 11 of the 14 files and broke them — caught by this exact check, fixed by making the header-insertion
  logic paren-aware, and re-verified).
- Manually resolved `REFACTORY_ROOT` for the two path depths involved (2 levels, 3 levels) against the
  actual repo root: both resolve to `<repo-root>/refactory`, and setting the `REFACTORY_ROOT` env var
  overrides it as expected.
- Ran `detectors/v1.0.0/test_real_data.py` directly: executes cleanly through the synthetic-code checks
  and reaches the real-corpus section without error (empty results there, since the corpus itself is not
  present in this sandbox either — the same honest gap already documented throughout this project).
- Full fresh-venv verification: all `scripts/regenerate_*.py` scripts and `pytest tests/ -q` (11/11)
  unaffected — none of them depend on these 14 detector-level scripts.
