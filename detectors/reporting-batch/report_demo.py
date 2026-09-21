from report import generate_report, format_report_text
from test_real_data import model  # the shared competency library built up across this whole project

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


if __name__ == "__main__":
    # 1. A real correct Top-K submission (manual comparison-loop strategy)
    src1 = open(f"{REFACTORY_ROOT}/data/question_5/code/correct/correct_5_050.py").read()
    r1 = generate_report(src1, model, ["Accumulation", "SelectionStep", "FindExtremum", "TopKPattern"])
    print(format_report_text(r1, title="correct_5_050.py (Top-K, manual strategy)"))

    # 2. A real WRONG Top-K submission -- missing the removal step
    src2 = open(f"{REFACTORY_ROOT}/data/question_5/code/wrong/wrong_5_058.py").read()
    r2 = generate_report(src2, model, ["SelectionStep", "TopKPattern", "FindExtremum"])
    print(format_report_text(r2, title="wrong_5_058.py (Top-K, missing removal)"))

    # 3. PW01 Ex1.2 average -- the "forgot to divide" bug case
    src3 = """
def moyenne(n):
    total = 0
    for i in range(n):
        note = float(input("Note: "))
        total += note
    return total
"""
    from pw01_competencies import model as pw01_model  # same shared model, imported for its registrations
    r3 = generate_report(src3, pw01_model, ["Accumulation", "Average"])
    print(format_report_text(r3, title="moyenne() -- forgot the division"))
