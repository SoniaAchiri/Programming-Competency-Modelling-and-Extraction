import ast
import glob
from competency import (
    CompetencyModel, Competency, ALL, ANY, NESTED, SHARED_BINDING,
    SELF_REFERENTIAL, TUPLE_SWAP, CONTAINS_TEXT, AND, SEQUENTIAL, DELEGATES
)

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


model = CompetencyModel()

model.register(Competency(
    id="Accumulation",
    components={"decl": "DECL", "loop": "LOOP", "assign": "ASSIGN"},
    coverage=ALL(["decl", "loop", "assign"]),
    structural=AND([
        NESTED("loop", "assign"),
        SHARED_BINDING([("decl", "target", "assign", "target")]),
        SELF_REFERENTIAL("assign"),
    ]),
))

# Swap now recognizes two distinct correct forms: the 3-statement temp-variable
# version, and Python's idiomatic tuple-unpack `a, b = b, a` (a single ASSIGN
# node) -- real question_4 submissions use both, and the tuple form was
# invisible to the model until now.
model.register(Competency(
    id="Swap3Step",
    components={"tmp": "ASSIGN", "first": "ASSIGN", "second": "ASSIGN"},
    coverage=ALL(["tmp", "first", "second"]),
    structural=AND([
        SEQUENTIAL(["tmp", "first", "second"], max_line_gap=1),
        SHARED_BINDING([
            ("tmp", "source", "first", "target"),
            ("first", "source", "second", "target"),
            ("second", "source", "tmp", "target"),
        ]),
    ]),
))

model.register(Competency(
    id="SwapTuple",
    components={"assign": "ASSIGN"},
    coverage=ALL(["assign"]),
    structural=TUPLE_SWAP("assign"),
))

model.register(Competency(
    id="Swap",
    components={"three_step": "Swap3Step", "tuple_form": "SwapTuple"},
    coverage=ANY(["three_step", "tuple_form"]),
    structural=None,
))

# "source" slot now accepts either INPUT (console) or PARAM (function arg) --
# fixes the false-zero on every function-graded submission from last run.
#
# SHARED_BINDING now checks against TEST's all_names (every identifier
# referenced anywhere in the test, however it's shaped) rather than just
# operand (the literal left-hand side of a simple comparison). Batch
# validation against the real Question 1 dataset found this matters a lot:
# 364 of 526 zero-scoring submissions had every slot present but still
# scored 0, because the searched value appeared on the right side of a
# comparison ("elem >= x", 55% of cases), inside a compound "and"/"or" or
# chained condition ("x > seq[i] and x <= seq[i+1]", 43%), or as a while
# loop's own condition rather than a nested if (2%) -- none of which the
# old operand-only check could see. all_names is a strict superset of what
# operand alone matched, so nothing that used to pass stops passing.
model.register(Competency(
    id="GuardedInput",
    components={"source": ("INPUT", "PARAM"), "test": "TEST", "loop": "LOOP"},
    coverage=ALL(["source", "test", "loop"]),
    structural=AND([
        NESTED("loop", "test"),
        SHARED_BINDING([("source", "target", "test", "all_names")]),
    ]),
))

model.register(Competency(
    id="SelectionStep",
    components={"loop": "LOOP", "test": "TEST", "assign": "ASSIGN"},
    coverage=ALL(["loop", "test", "assign"]),
    structural=AND([
        NESTED("loop", "test"),
        NESTED("test", "assign"),
    ]),
))

# Whether "found the extremum via max()/min()" should count the same as
# "found it via a manual comparison loop" is a modeling choice -- ~30% of
# real Top-K submissions use the builtin. Rather than picking one answer,
# expose both forms and let the composite ANY over them; the evidence
# (which branch actually matched) is still inspectable per-submission.
model.register(Competency(
    id="FindExtremumBuiltin",
    components={"call": "BUILTIN_REDUCE"},
    coverage=ALL(["call"]),
    structural=None,
))

model.register(Competency(
    id="FindExtremum",
    components={"manual": "SelectionStep", "builtin": "FindExtremumBuiltin"},
    coverage=ANY(["manual", "builtin"]),
    structural=None,
))

model.register(Competency(
    id="LoopStep", components={"inner": "LOOP"}, coverage=ALL(["inner"]), structural=None,
))
model.register(Competency(
    id="LoopStep2", components={"inner": "LoopStep"}, coverage=ALL(["inner"]), structural=None,
))
model.register(Competency(
    id="RemovalAssign",
    components={"assign": "ASSIGN"},
    coverage=ALL(["assign"]),
    # the ".remove()/.pop() specifically" check now lives HERE, one level
    # down, instead of via a dotted path from TopKPattern itself.
    structural=CONTAINS_TEXT("assign", "kind", ("remove", "pop")),
))
model.register(Competency(
    id="RemovalAssignStep", components={"inner": "RemovalAssign"}, coverage=ALL(["inner"]), structural=None,
))
model.register(Competency(
    id="TopKPattern",
    components={"loop": "LoopStep2", "select": "FindExtremum", "remove": "RemovalAssignStep"},
    coverage=ALL(["loop", "select", "remove"]),
    structural=AND([
        NESTED("loop", "select"),
        NESTED("loop", "remove"),
    ]),
))

# Real-data finding: clustering the "novel" (score-0) Q5 submissions by
# embedding similarity found one dominant cluster (38 of 43 files) sharing
# a shape TopKPattern, defined purely inline, cannot see at all: top_k's
# OWN body does nothing but call a differently-named helper and slice the
# result --
#     def top_k(lst, k):
#         return sort_descending(lst)[:k]
# -- so function-scoped resolution correctly finds zero loop/test/assign
# inside top_k itself. Two genuinely different sub-shapes turned up inside
# that one cluster:
#
# (1) The helper itself repeatedly finds-and-removes the max -- structurally
#     IDENTICAL to TopKPattern's own existing definition, just living in a
#     function with a different name. DELEGATES (already built for exactly
#     this) recognizes it directly, checking the callee's own body against
#     TopKPattern with zero new detection logic needed.
model.register(Competency(
    id="TopKViaDelegate",
    components={"call": "CALL"},
    coverage=ALL(["call"]),
    structural=DELEGATES("call", "TopKPattern"),
))

# (2) The helper is a genuinely different, general-purpose sort (recursive
#     merge_sort, an in-place bubble-style sort) -- not a repeated-extraction
#     shape at all, so DELEGATES-to-TopKPattern would correctly score this
#     0. "Sort everything, then take the first k" is its own legitimate
#     strategy. HasSubstantialWork checks for a loop OR self-recursion --
#     rules out delegating to a stub, without trying to characterize "is
#     this a valid general sort," a much bigger question than this
#     competency needs to answer. Recursion matters here specifically: a
#     real submission's merge_sort was found to have ZERO LOOP primitives
#     at all (pure recursion), so a loop-only check misses genuinely
#     substantial recursive work entirely.
model.register(Competency(
    id="HasSubstantialWork",
    components={"loop": ("LOOP", "SELF_RECURSIVE")},
    coverage=ALL(["loop"]),
    structural=None,
))
model.register(Competency(
    id="SortThenSlice",
    components={"call": "CALL", "output": "OUTPUT"},
    coverage=ALL(["call", "output"]),
    structural=AND([
        DELEGATES("call", "HasSubstantialWork"),
        # Generous gap: real submissions in this shape sometimes have a
        # couple of intermediate statements between the call and the
        # final return (e.g. a .reverse() call, or building the sliced
        # result via a small loop rather than a literal [:k]), not just
        # a single one-line return.
        SEQUENTIAL(["call", "output"], max_line_gap=10),
    ]),
))

# Master competency: the original inline shape, plus both delegate shapes,
# as an explicit ANY -- same pattern as SortByKey. Registered separately
# from TopKPattern itself (rather than redefining TopKPattern in place) so
# existing code/results referencing "TopKPattern" specifically are
# unaffected; batch validation should target TopKPatternExtended to see
# the corrected coverage.
#
# Documented layering exception, same convention as BubbleSortPass: the two
# delegate-based branches are inherently shallower than the inline
# TopKPattern branch, because their real depth lives inside DELEGATES' own
# recursive resolution of the callee's body -- which correctly does not
# propagate into level(), since it is a separate, independently-scoped
# resolution rather than a component of THIS competency's own structure.
model.register(Competency(
    id="TopKPatternExtended",
    components={"direct": "TopKPattern", "delegate": "TopKViaDelegate", "sort_then_slice": "SortThenSlice"},
    coverage=ANY(["direct", "delegate", "sort_then_slice"]),
    structural=None,
    allow_mixed_levels=True,
))

# Question 2 pattern: count occurrences matching a condition. Note this is
# defined directly over primitives rather than composing Accumulation inside
# a TEST: Accumulation's own span includes its DECL line, which legitimately
# sits BEFORE/outside the TEST (only the increment belongs inside it), so a
# naive NESTED(test, Accumulation) on full composite span breaks. Composing
# advanced-in-advanced only works cleanly when the child's whole span is
# meant to be contained -- that wasn't true here.
model.register(Competency(
    id="ConditionalCount",
    components={"decl": "DECL", "loop": "LOOP", "test": "TEST", "increment": "ASSIGN"},
    coverage=ALL(["decl", "loop", "test", "increment"]),
    structural=AND([
        NESTED("loop", "test"),
        NESTED("test", "increment"),
        SHARED_BINDING([("decl", "target", "increment", "target")]),
        SELF_REFERENTIAL("increment"),
    ]),
))

# Real bubble sort: outer LOOP { inner LOOP { TEST { Swap } } } -- Swap nested
# *inside* the comparison, immediately swapping on the adjacent pair. This is
# structurally distinct from "selection sort" (find extremum across the whole
# inner loop, swap once *after* it ends) even though both use two LOOPs,
# a TEST, and a Swap.
model.register(Competency(
    id="BubbleSortPass",
    components={"outer": "LOOP", "inner": "LOOP", "test": "TEST", "swap": "Swap"},
    coverage=ALL(["outer", "inner", "test", "swap"]),
    structural=AND([
        NESTED("outer", "inner"),
        NESTED("inner", "test"),
        NESTED("test", "swap"),
    ]),
    # Documented layering exception: Swap (level 2) sits directly alongside
    # the primitives that locate it, matching the actual AST shape of a
    # bubble-sort pass -- see the level(c) design principle in competency.py.
    allow_mixed_levels=True,
))

# SortByKey: the real Q4 target competency. Batch validation against all
# 419 real sort_age submissions found BubbleSortPass (in-place swap, the
# reference solution's own strategy) covers only 13.1% -- most real
# submissions instead repeatedly find the max and remove it, building a
# new sorted list, i.e. exactly the TopKPattern shape already built for
# Q5's top_k (64.4% alone, requiring zero new code). Combined: 77.6%.
model.register(Competency(
    id="SortByKey",
    components={"inplace_swap": "BubbleSortPass", "repeated_extraction": "TopKPattern"},
    coverage=ANY(["inplace_swap", "repeated_extraction"]),
    structural=None,
))


def analyze(path, targets):
    src = open(path, encoding="utf-8").read()
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return None, f"SyntaxError: {e}"
    results = model.resolve(tree, targets)
    return results, None


def show(path, targets, src_override=None):
    print(f"\n{'='*70}\n{path}\n{'='*70}")
    if src_override:
        print(src_override)
        results = model.resolve(ast.parse(src_override), targets)
        err = None
    else:
        print(open(path, encoding="utf-8").read())
        results, err = analyze(path, targets)
    if err:
        print(err)
        return
    for tid, r in results.items():
        print(f"  {tid:16s} final={r.final_score:.2f}  ({r.detail})")


if __name__ == "__main__":
    print("\n\n########## Fix check 1: Swap (needs 3 distinct ASSIGN slots) ##########")
    good_swap = """
def f(a, b):
    temp = a
    a = b
    b = temp
    return a, b
"""
    buggy_swap = """
def f(a, b):
    temp = a
    b = a
    a = temp
    return a, b
"""
    show("synthetic: correct swap", ["Swap"], src_override=good_swap)
    show("synthetic: buggy swap (loses original b)", ["Swap"], src_override=buggy_swap)

    print("\n\n########## Fix check 2: GuardedInput on parameter-based code ##########")
    files1 = sorted(glob.glob(f"{REFACTORY_ROOT}/data/question_1/code/correct/*.py"))
    for f in [files1[0], files1[1], files1[2]]:
        show(f, ["GuardedInput"])

    print("\n\n########## Re-check question 5 still works ##########")
    files5 = sorted(glob.glob(f"{REFACTORY_ROOT}/data/question_5/code/correct/*.py"))
    for f in [files5[0], files5[49], files5[299]]:
        show(f, ["SelectionStep", "TopKPattern"])

    print("\n\n########## Fix check 3: BubbleSortPass on real question_4 code ##########")
    q4 = f"{REFACTORY_ROOT}/data/question_4/code/correct"
    show(f"{q4}/correct_4_121.py", ["Swap", "BubbleSortPass"])   # tuple-swap bubble sort
    show(f"{q4}/correct_4_164.py", ["Swap", "BubbleSortPass"])   # tuple-swap bubble sort
    show(f"{q4}/correct_4_043.py", ["Swap", "BubbleSortPass"])   # selection sort w/ swap AFTER inner loop
    show(f"{q4}/correct_4_010.py", ["Swap", "BubbleSortPass"])   # selection sort, no swap at all

    print("\n\n########## Fix check 4: FindExtremum (manual vs. builtin max/min) ##########")
    q5 = f"{REFACTORY_ROOT}/data/question_5/code/correct"
    show(f"{q5}/correct_5_001.py", ["FindExtremum", "TopKPattern"])   # builtin max()/remove()
    show(f"{q5}/correct_5_050.py", ["FindExtremum", "TopKPattern"])   # manual comparison loop

    print("\n\n########## Question 2: ConditionalCount (composes Accumulation) ##########")
    files2 = sorted(glob.glob(f"{REFACTORY_ROOT}/data/question_2/code/correct/*.py"))
    for f in [files2[0], files2[1]]:
        show(f, ["ConditionalCount"])

    print("\n\n########## Question 3: SelectionStep reused as-is (remove_extras) ##########")
    files3 = sorted(glob.glob(f"{REFACTORY_ROOT}/data/question_3/code/correct/*.py"))
    for f in [files3[0], files3[1]]:
        show(f, ["SelectionStep"])
