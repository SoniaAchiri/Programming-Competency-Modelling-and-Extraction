import ast
import glob
from competency import (
    CompetencyModel, Competency, ALL, ANY, NESTED, SHARED_BINDING,
    SELF_REFERENTIAL, TUPLE_SWAP, CONTAINS_TEXT, AND, SEQUENTIAL
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
model.register(Competency(
    id="GuardedInput",
    components={"source": ("INPUT", "PARAM"), "test": "TEST", "loop": "LOOP"},
    coverage=ALL(["source", "test", "loop"]),
    structural=AND([
        NESTED("loop", "test"),
        SHARED_BINDING([("source", "target", "test", "operand")]),
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
