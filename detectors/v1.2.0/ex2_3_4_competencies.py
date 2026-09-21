import ast
from competency import (
    Competency, ALL, ANY, NESTED, SHARED_BINDING, SELF_REFERENTIAL,
    CONTAINS_TEXT, EXHAUSTIVE_CHAIN, AND
)
from test_real_data import model

# --- Ex2: rock-paper-scissors -------------------------------------------
# GameLoop: wrapping INPUT/TEST/OUTPUT in a loop so the interaction can
# repeat. Deliberately generic -- this is the same shape as any REPL-style
# program (quizzes, menus), not specific to this exercise.
model.register(Competency(
    id="GameLoop",
    components={"loop": "LOOP", "input": "INPUT", "test": "TEST", "output": "OUTPUT"},
    coverage=ALL(["loop", "input", "test", "output"]),
    structural=AND([
        NESTED("loop", "input"),
        NESTED("loop", "test"),
        NESTED("loop", "output"),
    ]),
))

# --- Ex3.1: rendre_monnaie (change-making) -------------------------------
# Two legitimate strategies: iterative subtraction (a while-loop repeatedly
# subtracting the denomination) vs. arithmetic (//, % in one step) --
# same manual/builtin-style fork as FindExtremum, made explicit via ANY.
model.register(Competency(
    id="GreedyReduction",
    components={"outer": "LOOP", "inner": "LOOP", "reduce": "ASSIGN", "collect": "ASSIGN"},
    coverage=ALL(["outer", "inner", "reduce", "collect"]),
    structural=AND([
        NESTED("outer", "inner"),
        NESTED("inner", "reduce"),
        NESTED("inner", "collect"),
        SELF_REFERENTIAL("reduce"),
        CONTAINS_TEXT("collect", "kind", ("append",)),
    ]),
))

model.register(Competency(
    id="ArithmeticReduction",
    components={"outer": "LOOP", "div": "ASSIGN", "mod": "ASSIGN"},
    coverage=ALL(["outer", "div", "mod"]),
    structural=AND([
        NESTED("outer", "div"),
        NESTED("outer", "mod"),
        CONTAINS_TEXT("div", "source", ("//",)),
        CONTAINS_TEXT("mod", "source", ("%",)),
    ]),
))

model.register(Competency(
    id="GreedyChange",
    components={"iterative": "GreedyReduction", "arithmetic": "ArithmeticReduction"},
    coverage=ANY(["iterative", "arithmetic"]),
    structural=None,
))

# --- Ex3.3: balanced parentheses -----------------------------------------
# Two legitimate strategies: a running counter (works for one bracket type,
# which is all this exercise needs) vs. an explicit stack (the textbook
# general solution). Both approximated loosely for now -- neither checks
# the final "balanced at the end" comparison, flagged as a known gap to
# tighten once real submissions are available.
model.register(Competency(
    id="CounterBalance",
    components={"decl": "DECL", "loop": "LOOP", "incr": "ASSIGN", "decr": "ASSIGN"},
    coverage=ALL(["decl", "loop", "incr", "decr"]),
    structural=AND([
        NESTED("loop", "incr"),
        NESTED("loop", "decr"),
        SHARED_BINDING([
            ("decl", "target", "incr", "target"),
            ("decl", "target", "decr", "target"),
        ]),
        CONTAINS_TEXT("incr", "source", ("Add",)),
        CONTAINS_TEXT("decr", "source", ("Sub",)),
    ]),
))

model.register(Competency(
    id="StackBalance",
    components={"decl": "DECL", "loop": "LOOP", "push": "ASSIGN", "pop": "ASSIGN"},
    coverage=ALL(["decl", "loop", "push", "pop"]),
    structural=AND([
        NESTED("loop", "push"),
        NESTED("loop", "pop"),
        SHARED_BINDING([
            ("decl", "target", "push", "target"),
            ("decl", "target", "pop", "target"),
        ]),
        CONTAINS_TEXT("push", "kind", ("append",)),
        CONTAINS_TEXT("pop", "kind", ("pop",)),
    ]),
))

model.register(Competency(
    id="BalancedCheck",
    components={"counter": "CounterBalance", "stack": "StackBalance"},
    coverage=ANY(["counter", "stack"]),
    structural=None,
))

# --- Ex4: tic-tac-toe -----------------------------------------------------
# GridIteration: a doubly-nested loop over a 2D structure -- the building
# block for board display / win-checking, reused as-is by any board game.
model.register(Competency(
    id="GridIteration",
    components={"outer": "LOOP", "inner": "LOOP"},
    coverage=ALL(["outer", "inner"]),
    structural=NESTED("outer", "inner"),
))


model.register(Competency(
    id="MultiWayBranch",
    components={"test": "TEST"},
    coverage=ALL(["test"]),
    structural=EXHAUSTIVE_CHAIN("test", min_branches=3, require_else=True, require_same_operand=True),
))


def run(label, src, targets):
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    print(src)
    r = model.resolve(ast.parse(src), targets)
    for tid, res in r.items():
        print(f"  {tid:16s} final={res.final_score:.2f}  ({res.detail})")


if __name__ == "__main__":
    print("\n\n########## Ex2: rock-paper-scissors ##########")
    rps_ref = """
import random
def jouer():
    rejouer = "o"
    while rejouer == "o":
        choix = input("pierre, feuille ou ciseaux: ")
        ordi = random.choice(["pierre", "feuille", "ciseaux"])
        if choix == ordi:
            print("Egalite")
        elif (choix == "pierre" and ordi == "ciseaux") or \\
             (choix == "feuille" and ordi == "pierre") or \\
             (choix == "ciseaux" and ordi == "feuille"):
            print("Gagne")
        else:
            print("Perdu")
        rejouer = input("Rejouer? (o/n): ")
"""
    run("Ex2 reference (has replay loop)", rps_ref, ["GameLoop"])

    rps_no_replay = """
import random
def jouer():
    choix = input("pierre, feuille ou ciseaux: ")
    ordi = random.choice(["pierre", "feuille", "ciseaux"])
    if choix == ordi:
        print("Egalite")
    else:
        print("Resultat")
"""
    run("Ex2 buggy (single-shot, no replay loop)", rps_no_replay, ["GameLoop"])

    print("\n\n########## Ex3.1: rendre_monnaie (change-making) ##########")
    change_iterative = """
def rendre_monnaie(montant):
    valeurs = [2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1]
    resultat = []
    for v in valeurs:
        while montant >= v:
            montant = montant - v
            resultat.append(v)
    return resultat
"""
    run("Iterative subtraction", change_iterative, ["GreedyReduction", "ArithmeticReduction", "GreedyChange"])

    change_arith = """
def rendre_monnaie(montant):
    valeurs = [2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1]
    resultat = []
    for v in valeurs:
        nb = montant // v
        montant = montant % v
        resultat.append(nb)
    return resultat
"""
    run("Arithmetic (//, %)", change_arith, ["GreedyReduction", "ArithmeticReduction", "GreedyChange"])

    print("\n\n########## Ex3.3: balanced parentheses ##########")
    parens_counter = """
def est_equilibre(expr):
    compteur = 0
    for c in expr:
        if c == "(":
            compteur += 1
        elif c == ")":
            compteur -= 1
    return compteur == 0
"""
    run("Counter strategy", parens_counter, ["CounterBalance", "StackBalance", "BalancedCheck"])

    parens_stack = """
def est_equilibre(expr):
    pile = []
    for c in expr:
        if c == "(":
            pile.append(c)
        elif c == ")":
            pile.pop()
    return len(pile) == 0
"""
    run("Stack strategy", parens_stack, ["CounterBalance", "StackBalance", "BalancedCheck"])

    print("\n\n########## Ex4: tic-tac-toe board display ##########")
    grid_display = """
def afficher(A):
    for ligne in A:
        for case in ligne:
            print(case, end=" ")
        print()
"""
    run("Grid display (nested loop)", grid_display, ["GridIteration"])

    print("\n\n########## MultiWayBranch (exhaustive if/elif/.../else) ##########")
    grade_chain = """
if note >= 16:
    mention = "tres bien"
elif note >= 14:
    mention = "bien"
elif note >= 12:
    mention = "assez bien"
else:
    mention = "passable"
"""
    run("Positive control: same operand, 3+ branches, has else", grade_chain, ["MultiWayBranch"])

    run("Ex2 reference: 3-way, has else", rps_ref, ["MultiWayBranch"])

    two_way = """
if x > 0:
    print("positive")
else:
    print("non-positive")
"""
    run("Only 2-way (below min_branches=3)", two_way, ["MultiWayBranch"])

    unrelated_elif = """
if x > 0:
    print("a")
elif y < 0:
    print("b")
elif z == 0:
    print("c")
else:
    print("d")
"""
    run("3-way but different operands each branch (not truly one decision)", unrelated_elif, ["MultiWayBranch"])

    no_else = """
if x == 1:
    print("a")
elif x == 2:
    print("b")
elif x == 3:
    print("c")
"""
    run("3-way, same operand, but no final else (not exhaustive)", no_else, ["MultiWayBranch"])
