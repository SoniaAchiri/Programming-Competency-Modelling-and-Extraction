import ast
from competency import Competency, ALL, ANY, AND, REFERENCES, CONTAINS_TEXT
from pw01_competencies import model  # registers ConditionalCount, Accumulation, etc.

# Trivial level-1 lift of OUTPUT, same technique used for AverageStrict earlier --
# keeps AccumulateThenCount at clean level 2 (Accumulation + OutputStep, both
# level 1) rather than mixing a level-1 competency with a raw primitive.
model.register(Competency(
    id="OutputStep",
    components={"out": "OUTPUT"},
    coverage=ALL(["out"]),
    structural=None,
))

# The real alternative strategy found in Q2 data (correct_2_001.py and siblings):
# accumulate matching values into a collection, then check membership count on
# the collection directly, instead of an explicit counter.
model.register(Competency(
    id="AccumulateThenCount",
    components={"acc": "Accumulation", "check": "OutputStep"},
    coverage=ALL(["acc", "check"]),
    structural=AND([
        # the accumulated collection must be the SAME one being counted --
        # not just "some accumulation and some .count() exist somewhere"
        REFERENCES("acc.decl", "target", "check.out", "source"),
        CONTAINS_TEXT("check.out", "source", (".count(",)),
    ]),
))

# Trivial level-2 lift of ConditionalCount (level 1), so both branches of
# the ANY below are the same level (2) -- keeps UniqueCheck cleanly level 3
# instead of adding a third documented layering exception alongside
# TopKPattern and BubbleSortPass.
model.register(Competency(
    id="ConditionalCountStep",
    components={"inner": "ConditionalCount"},
    coverage=ALL(["inner"]),
    structural=None,
))

# --- Third real strategy found in the data: functional map()/filter()
# pipelines with no explicit loop at all. Modeled via CONTAINS_TEXT/
# REFERENCES on the existing ASSIGN/TEST/OUTPUT primitives directly --
# no new primitive detector needed. Three real sub-shapes found:
#   (a) one-liner: return tuple(map(...)).count(day) == 1
#   (b) assign-then-check: possible = tuple(filter(...)); if len(possible) == 1: ...
#       (or the map()+.count() equivalent of the same two-statement shape)
# Both checked via plain substring matching on the relevant expression
# text rather than a dedicated MAP/FILTER primitive -- map()/filter() are
# ordinary Call nodes already visible inside ASSIGN.source / OUTPUT.source,
# so no new primitive detector is needed.

model.register(Competency(
    id="InlineFunctionalCheck",           # shape (a): everything in one return
    components={"output": "OUTPUT"},
    coverage=ALL(["output"]),
    structural=AND([
        CONTAINS_TEXT("output", "source", ("map(", "filter(")),
        CONTAINS_TEXT("output", "source", (".count(", "len(")),
    ]),
))

model.register(Competency(
    id="GuardedFunctionalCheck",          # shape (b): build the collection, then check it
    components={"assign": "ASSIGN", "test": "TEST"},
    coverage=ALL(["assign", "test"]),
    structural=AND([
        CONTAINS_TEXT("assign", "source", ("map(", "filter(")),
        CONTAINS_TEXT("test", "operand", (".count(", "len(")),
        # the value being tested must be the SAME one the pipeline built,
        # not just "a pipeline and a check exist somewhere in the function"
        REFERENCES("assign", "target", "test", "operand"),
    ]),
))

model.register(Competency(
    id="InlineTestFunctionalCheck",       # shape (c): pipeline embedded directly
    components={"test": "TEST"},          # in the if-condition itself, e.g.
    coverage=ALL(["test"]),               # if (tuple(map(...))).count(day) == 1:
    structural=AND([
        CONTAINS_TEXT("test", "operand", ("map(", "filter(")),
        CONTAINS_TEXT("test", "operand", (".count(", "len(")),
    ]),
))

model.register(Competency(
    id="FunctionalUniqueCheck",
    components={"inline": "InlineFunctionalCheck", "guarded": "GuardedFunctionalCheck",
                "inline_test": "InlineTestFunctionalCheck"},
    coverage=ANY(["inline", "guarded", "inline_test"]),
    structural=None,
))

# Master competency, now with all three real strategies as same-level
# (level 2) siblings under one ANY, keeping UniqueCheck cleanly level 3.
model.register(Competency(
    id="UniqueCheck",
    components={"counter": "ConditionalCountStep", "accumulate_count": "AccumulateThenCount",
                "functional": "FunctionalUniqueCheck"},
    coverage=ANY(["counter", "accumulate_count", "functional"]),
    structural=None,
))


if __name__ == "__main__":
    print("########## AccumulateThenCount on the real tuple+count strategy ##########")
    src_tuple = """
def unique_day(day, possible_birthdays):
    all_days = ()
    for i in possible_birthdays:
        all_days += (i[1],)
    return all_days.count(day) == 1
"""
    print(src_tuple)
    r = model.resolve(ast.parse(src_tuple), ["ConditionalCount", "AccumulateThenCount", "UniqueCheck"])
    for cid, res in r.items():
        print(f"  {cid:20s} final={res.final_score:.2f}  ({res.detail})")

    print("\n########## UniqueCheck on the counter strategy (should also pass) ##########")
    src_counter = """
def unique_day(day, possible_birthdays):
    count = 0
    for birthday in possible_birthdays:
        if birthday[1] == day:
            count += 1
    return count == 1
"""
    print(src_counter)
    r2 = model.resolve(ast.parse(src_counter), ["ConditionalCount", "AccumulateThenCount", "UniqueCheck"])
    for cid, res in r2.items():
        print(f"  {cid:20s} final={res.final_score:.2f}  ({res.detail})")
