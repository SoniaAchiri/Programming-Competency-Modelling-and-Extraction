import ast
from competency import Competency, ALL, NESTED, AND, REFERENCES, CONTAINS_TEXT, DELEGATES
from test_real_data import model, show

# --- Ex1.3/1.4: next N primes -----------------------------------------
# IsPrime: a LOOP that TESTs divisibility (operand must involve '%').
model.register(Competency(
    id="IsPrime",
    components={"loop": "LOOP", "test": "TEST"},
    coverage=ALL(["loop", "test"]),
    structural=AND([
        NESTED("loop", "test"),
        CONTAINS_TEXT("test", "operand", ("%",)),
    ]),
))

# CountedSearch: an outer LOOP that both runs a primality check and
# produces output, on each iteration -- deliberately loose (siblings, not
# nested in each other) since "print inside the search" vs "collect then
# print after" are both reasonable strategies; a first-pass approximation,
# to be tightened once real student submissions show which shapes recur.
model.register(Competency(
    id="CountedSearch",
    components={"outer": "LOOP", "isprime": "IsPrime", "output": "OUTPUT"},
    coverage=ALL(["outer", "isprime", "output"]),
    structural=AND([
        NESTED("outer", "isprime"),
        NESTED("outer", "output"),
    ]),
))

# --- Ex1.5: collect N inputs into a list --------------------------------
model.register(Competency(
    id="CollectInput",
    components={"loop": "LOOP", "input": "INPUT", "assign": "ASSIGN"},
    coverage=ALL(["loop", "input", "assign"]),
    structural=AND([
        NESTED("loop", "input"),
        NESTED("loop", "assign"),
    ]),
))

# --- Ex1.2: average of n notes ------------------------------------------
# Reuses Accumulation (already in the shared library) and adds: the
# accumulator variable must actually flow into a division in the output.
model.register(Competency(
    id="Average",
    components={"acc": "Accumulation", "output": "OUTPUT"},
    coverage=ALL(["acc", "output"]),
    structural=AND([
        REFERENCES("acc.assign", "target", "output", "source"),
        CONTAINS_TEXT("output", "source", ("/",)),
    ]),
))


# --- Question 2 (contains_unique_day): cross-function delegation ---------
# contains_unique_day doesn't count anything itself -- it delegates the
# uniqueness check to unique_day. DELEGATES independently resolves
# ConditionalCount against the CALLED function's own body, so the score
# here reflects whether the callee genuinely implements it, not just
# whether a call exists.
model.register(Competency(
    id="DelegatesUniqueness",
    components={"test": "TEST", "call": "CALL"},
    coverage=ALL(["test", "call"]),
    structural=AND([
        NESTED("test", "call"),
        DELEGATES("call", "ConditionalCount"),
    ]),
))


if __name__ == "__main__":
    print("\n\n########## Ex1.2: average (reference) ##########")
    show_src = """
def moyenne(n):
    total = 0
    for i in range(n):
        note = float(input("Note: "))
        total += note
    return total / n
"""
    print(show_src)
    r = model.resolve(ast.parse(show_src), ["Accumulation", "Average"])
    for tid, res in r.items():
        print(f"  {tid:16s} final={res.final_score:.2f}  ({res.detail})")

    print("\n\n########## Ex1.2: average (buggy -- forgets the division) ##########")
    buggy_src = """
def moyenne(n):
    total = 0
    for i in range(n):
        note = float(input("Note: "))
        total += note
    return total
"""
    print(buggy_src)
    r = model.resolve(ast.parse(buggy_src), ["Accumulation", "Average"])
    for tid, res in r.items():
        print(f"  {tid:16s} final={res.final_score:.2f}  ({res.detail})")

    print("\n\n########## Ex1.3/1.4: next N primes ##########")
    primes_src = """
def nb_premiers(nb, n=3):
    count = 0
    candidate = nb + 1
    while count < n:
        is_prime = True
        for d in range(2, candidate):
            if candidate % d == 0:
                is_prime = False
        if is_prime:
            print(candidate)
            count += 1
        candidate += 1
"""
    print(primes_src)
    r = model.resolve(ast.parse(primes_src), ["IsPrime", "CountedSearch"])
    for tid, res in r.items():
        print(f"  {tid:16s} final={res.final_score:.2f}  ({res.detail})")

    print("\n\n########## Ex1.5: collect module names into a list ##########")
    collect_src = """
def lire_modules():
    A = []
    for i in range(5):
        nom = input("Module: ")
        A.append(nom)
    return A
"""
    print(collect_src)
    r = model.resolve(ast.parse(collect_src), ["CollectInput"])
    for tid, res in r.items():
        print(f"  {tid:16s} final={res.final_score:.2f}  ({res.detail})")

    print("\n\n########## Ex1.6: longest string (manual) -- reuses SelectionStep ##########")
    longest_manual = """
def plus_long(liste):
    longest = liste[0]
    for s in liste:
        if len(s) > len(longest):
            longest = s
    return longest
"""
    print(longest_manual)
    r = model.resolve(ast.parse(longest_manual), ["SelectionStep", "FindExtremum"])
    for tid, res in r.items():
        print(f"  {tid:16s} final={res.final_score:.2f}  ({res.detail})")

    print("\n\n########## Ex1.6: longest string (builtin) -- reuses FindExtremum ##########")
    longest_builtin = """
def plus_long(liste):
    return max(liste, key=len)
"""
    print(longest_builtin)
    r = model.resolve(ast.parse(longest_builtin), ["SelectionStep", "FindExtremum"])
    for tid, res in r.items():
        print(f"  {tid:16s} final={res.final_score:.2f}  ({res.detail})")

    print("\n\n########## Cross-function delegation: contains_unique_day -> unique_day ##########")
    q2_delegation_src = """
def unique_day(day, possible_birthdays):
    count = 0
    for birthday in possible_birthdays:
        if birthday[1] == day:
            count += 1
    return count == 1

def contains_unique_day(month, possible_birthdays):
    for birthday in possible_birthdays:
        if birthday[0] == month:
            if unique_day(birthday[1], possible_birthdays):
                return True
    return False
"""
    print(q2_delegation_src)
    r = model.resolve(ast.parse(q2_delegation_src), ["ConditionalCount", "DelegatesUniqueness"])
    for tid, res in r.items():
        print(f"  {tid:20s} final={res.final_score:.2f}  ({res.detail})")
