"""
Full-scale batch validation for Refactory Questions 1-4, mirroring exactly
the process already used for Q5 (topk_report.csv). Produces one CSV per
question, one row per submission, using the existing batch_report.py /
competency.py machinery -- no new validation logic, just running the
established pipeline against the remaining four exercises.

USAGE NOTES -- READ BEFORE RUNNING:

1. Function names below are marked CONFIRMED or UNVERIFIED. "search" (Q1),
   "unique_day" (Q2), "remove_extras" (Q3), and "sort_age" (Q4) are all now
   directly confirmed -- Q2 against actual project code, Q1/Q3/Q4 directly
   by the person running this. Q1's original q1_competencies.py __main__
   block used whole-file resolution instead, but function-scoped resolution
   is used here regardless, both because it's now confirmed and because
   it's the safer choice in general (avoids the whole-file over-crediting
   risk documented in Table 4 of the paper).

2. Adjust REFACTORY_ROOT below to wherever your data/ folder actually lives.

3. This uses the AST/structural resolver (competency.py), completely
   separate from the Colab embedding-validation work -- no network access
   needed, runs entirely locally.
"""

import sys
import os

# --- adjust this to your actual environment -------------------------------
REFACTORY_ROOT = "C:/data"  # confirmed against your actual q1_competencies.py path
PROJECT_DIR = "."          # wherever competency.py / batch_report.py / the
                            # various *_competencies.py modules live
OUTPUT_DIR = "./batch_reports"
# ----------------------------------------------------------------------------

sys.path.insert(0, PROJECT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)

from batch_report import process_folders

# Import whichever module(s) actually register the competencies you need.
# Adjust these imports to match your real module layout -- these are the
# modules that, in the project as shown to me, register the relevant
# competencies onto the shared `model`.
from test_real_data import model          # GuardedInput, LinearSearch base primitives, etc.
import q1_competencies                     # registers LinearSearch onto model
import q2_competencies                     # registers UniqueCheck and its branches onto model
import ex2_3_4_competencies                # if SelectionStep/other Q3-relevant competencies live here
# If SortByKey / BubbleSortPass / TopKPattern aren't already registered by
# one of the above (they should be, via test_real_data.py per the current
# project state), import whatever module does.


# ---------------------------------------------------------------------------
# One entry per question: (question_number, target_ids, function_name, confirmed)
# ---------------------------------------------------------------------------
RUNS = [
    {
        "question": "question_1",
        "target_ids": ["GuardedInput", "LinearSearch"],
        "function_name": "search",   # CONFIRMED directly by user -- overrides the
                                      # earlier whole-file assumption inferred from
                                      # q1_competencies.py's own __main__ block.
                                      # Scoping to the real function name is also
                                      # the safer choice regardless (avoids the
                                      # whole-file over-crediting risk from an
                                      # unrelated helper elsewhere in the file --
                                      # see Table 4, "Whole-file over-crediting").
        "output_csv": f"{OUTPUT_DIR}/q1_report.csv",
    },
    {
        "question": "question_2",
        "target_ids": ["ConditionalCount", "UniqueCheck", "AccumulateThenCount"],
        "function_name": "unique_day",   # CONFIRMED against actual code
        "output_csv": f"{OUTPUT_DIR}/q2_report.csv",
    },
    {
        "question": "question_3",
        "target_ids": ["SelectionStep"],
        "function_name": "remove_extras",   # CONFIRMED directly by user
        "output_csv": f"{OUTPUT_DIR}/q3_report.csv",
    },
    {
        "question": "question_4",
        "target_ids": ["BubbleSortPass", "TopKPattern", "SortByKey"],
        "function_name": "sort_age",   # CONFIRMED directly by user
        "output_csv": f"{OUTPUT_DIR}/q4_report.csv",
    },
]


def main():
    for run in RUNS:
        q = run["question"]
        correct_folder = os.path.join(REFACTORY_ROOT, q, "code", "correct")
        wrong_folder = os.path.join(REFACTORY_ROOT, q, "code", "wrong")

        if not os.path.isdir(correct_folder) or not os.path.isdir(wrong_folder):
            print(f"[SKIP] {q}: expected folders not found at "
                  f"{correct_folder} / {wrong_folder} -- check REFACTORY_ROOT")
            continue

        folder_labels = {
            correct_folder: "correct",
            wrong_folder: "wrong",
        }

        print(f"[RUN] {q} -- targets={run['target_ids']} "
              f"function_name={run['function_name']!r}")

        rows = process_folders(
            folder_labels,
            model,
            run["target_ids"],
            run["output_csv"],
            function_name=run["function_name"],
        )

        n_correct = sum(1 for r in rows if r["label"] == "correct")
        n_wrong = sum(1 for r in rows if r["label"] == "wrong")
        n_errors = sum(1 for r in rows if r.get("error"))
        print(f"       -> {len(rows)} rows written to {run['output_csv']} "
              f"({n_correct} correct, {n_wrong} wrong, {n_errors} parse errors)")


if __name__ == "__main__":
    main()
