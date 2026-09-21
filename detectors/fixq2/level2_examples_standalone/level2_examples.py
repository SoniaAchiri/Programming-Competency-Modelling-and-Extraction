import ast
from competency import Competency, ALL, AND, REFERENCES, CONTAINS_TEXT
from pw01_competencies import model  # registers Average, Accumulation, etc. onto the shared model

# ===========================================================================
# Example A: a NEW level-2 pattern -- AND-composition of two DIFFERENT
# level-1 skills (not alternatives for the same skill), tied together by a
# shared value. GuardedInput (level 1) validates a variable; Accumulation
# (level 1) sums a variable. Level 2 is not "either one or the other" --
# it's "the variable that got validated is the SAME one that got summed."
# ===========================================================================

model.register(Competency(
    id="ValidatedAccumulation",
    components={"guard": "GuardedInput", "accumulate": "Accumulation"},
    coverage=ALL(["guard", "accumulate"]),
    # dotted paths reach into each composite's own children -- this already
    # works today (built for the Average fix earlier), no new code needed.
    structural=REFERENCES("guard.source", "target", "accumulate.assign", "source"),
))

# ===========================================================================
# Example B: fixing an actual violation (Average) into strict level-2 form.
# BEFORE: Average = {acc: Accumulation (level 1), output: OUTPUT (level 0)}
#         -- a level-1 primitive sits directly alongside a level-1 competency.
# AFTER:  lift OUTPUT behind a trivial level-1 passthrough wrapper first.
# ===========================================================================

model.register(Competency(
    id="OutputStep",                      # trivial level-1 lift of OUTPUT
    components={"out": "OUTPUT"},
    coverage=ALL(["out"]),
    structural=None,
))

model.register(Competency(
    id="AverageStrict",                   # level-2: both children now level 1
    components={"acc": "Accumulation", "output": "OutputStep"},
    coverage=ALL(["acc", "output"]),
    # dotted paths need one extra hop (output.out) to reach through the new
    # wrapper to the real OUTPUT evidence's bindings -- exactly the
    # "bindings={} on composites" cost flagged as a prerequisite for
    # enforcing this rule. Both checks from the original Average are
    # preserved here, not just the REFERENCES one.
    structural=AND([
        REFERENCES("acc.assign", "target", "output.out", "source"),
        CONTAINS_TEXT("output.out", "source", ("/",)),
    ]),
))


if __name__ == "__main__":
    print("########## Example A: ValidatedAccumulation ##########")
    good_src = """
def read_and_sum(n):
    total = 0
    for i in range(n):
        x = int(input())
        for attempt in range(3):
            if x > 0:
                break
            x = int(input())
        total += x
    return total
"""
    print(good_src)
    r = model.resolve(ast.parse(good_src), ["GuardedInput", "Accumulation", "ValidatedAccumulation"])
    for cid, res in r.items():
        print(f"  {cid:22s} final={res.final_score:.2f}  ({res.detail})")

    print("\nNegative control: validates x, but sums an UNVALIDATED y instead")
    bug_src = """
def read_and_sum_bug(n):
    total = 0
    for i in range(n):
        x = int(input())
        for attempt in range(3):
            if x > 0:
                break
            x = int(input())
        y = int(input())
        total += y
    return total
"""
    print(bug_src)
    r2 = model.resolve(ast.parse(bug_src), ["GuardedInput", "Accumulation", "ValidatedAccumulation"])
    for cid, res in r2.items():
        print(f"  {cid:22s} final={res.final_score:.2f}  ({res.detail})")

    print("\n\n########## Example B: Average vs AverageStrict (should match) ##########")
    moyenne_good = """
def moyenne(n):
    total = 0
    for i in range(n):
        note = float(input("Note: "))
        total += note
    return total / n
"""
    print(moyenne_good)
    r3 = model.resolve(ast.parse(moyenne_good), ["Average", "AverageStrict"])
    for cid, res in r3.items():
        print(f"  {cid:22s} final={res.final_score:.2f}  ({res.detail})")

    print("\nBuggy variant: forgot the division")
    moyenne_bug = """
def moyenne(n):
    total = 0
    for i in range(n):
        note = float(input("Note: "))
        total += note
    return total
"""
    print(moyenne_bug)
    r4 = model.resolve(ast.parse(moyenne_bug), ["Average", "AverageStrict"])
    for cid, res in r4.items():
        print(f"  {cid:22s} final={res.final_score:.2f}  ({res.detail})")
