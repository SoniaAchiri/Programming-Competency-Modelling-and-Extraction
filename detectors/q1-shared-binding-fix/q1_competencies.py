import ast
import glob
from competency import Competency, ALL, NESTED, SHARED_BINDING, AND
from test_real_data import model

# LinearSearch is structurally IDENTICAL to GuardedInput -- both reduce to
# "a value is tested against a condition inside a loop, with the tested
# value shared across both." That structural shape is genuinely ambiguous
# between two different skills: GuardedInput's original intent (retry
# input until it passes validation) and linear search (scan a sequence
# comparing each element to a target). Wrapping LinearSearch around
# GuardedInput would still imply "search is a kind of guarded input" in
# the taxonomy's own dependency graph, which is exactly the false
# relationship being fixed here -- so this is a deliberate independent
# duplication, not a lifting wrapper. If the two definitions ever need to
# diverge (e.g. requiring an early return/break specifically, which
# GuardedInput doesn't check), that's additional evidence they were never
# really the same competency, just accidentally the same shape.
model.register(Competency(
    id="LinearSearch",
    components={"target": ("INPUT", "PARAM"), "test": "TEST", "loop": "LOOP"},
    coverage=ALL(["target", "test", "loop"]),
    structural=AND([
        NESTED("loop", "test"),
        # Checks against TEST's all_names (every identifier referenced
        # anywhere in the test) rather than just operand (the left-hand
        # side of a simple comparison alone) -- see the matching comment on
        # GuardedInput in test_real_data.py for the real-data evidence this
        # is based on. Applies identically here since LinearSearch shares
        # the exact same structural shape and the exact same underlying
        # detector limitation.
        SHARED_BINDING([("target", "target", "test", "all_names")]),
    ]),
))


if __name__ == "__main__":
    print("########## LinearSearch on real question_1 submissions ##########")
    files1 = sorted(glob.glob("C:/data/question_1/code/correct/*.py"))
    for f in files1[:3]:
        src = open(f, encoding="utf-8").read()
        r = model.resolve(ast.parse(src), ["GuardedInput", "LinearSearch"])
        print(f"{f.split('/')[-1]}: " +
              ", ".join(f"{cid}={res.final_score:.2f}" for cid, res in r.items()))
