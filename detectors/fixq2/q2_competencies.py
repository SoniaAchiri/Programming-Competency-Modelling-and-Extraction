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

# The completed Q2 target competency: either real strategy counts.
model.register(Competency(
    id="UniqueCheck",
    components={"counter": "ConditionalCountStep", "accumulate_count": "AccumulateThenCount"},
    coverage=ANY(["counter", "accumulate_count"]),
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
