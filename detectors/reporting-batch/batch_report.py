"""
Batch competency report: run generate_report() across every .py file in a
folder (or several folders, each tagged with a label) and write one row
per submission to a CSV.

Column layout, per requested competency id `cid`:
  {cid}_final     -- final_score (coverage x structural)
  {cid}_missing   -- comma-joined list of slots with no matching evidence
                     at all (empty if final_score == 1.0, informative
                     when it's partial or zero)

Parse errors (a submission that doesn't even compile) are recorded as a
row with an `error` column set, rather than crashing the whole batch --
one bad file should not cost you the other 500 rows.
"""

import ast
import csv
import glob
import os
from report import generate_report


def process_folder(folder_path: str, model, target_ids: list, label: str = "", function_name: str = None) -> list:
    """Returns a list of row-dicts for every .py file directly inside folder_path."""
    rows = []
    for filepath in sorted(glob.glob(os.path.join(folder_path, "*.py"))):
        filename = os.path.basename(filepath)
        row = {"file": filename, "label": label, "error": ""}
        try:
            source = open(filepath, encoding="utf-8").read()
            ast.parse(source)  # fail fast with a clear error if it doesn't even parse
        except (SyntaxError, UnicodeDecodeError) as e:
            row["error"] = f"{type(e).__name__}: {e}"
            for cid in target_ids:
                row[f"{cid}_final"] = ""
                row[f"{cid}_missing"] = ""
            rows.append(row)
            continue

        report = generate_report(source, model, target_ids, function_name=function_name)
        if "error" in report:
            row["error"] = report["error"]
            for cid in target_ids:
                row[f"{cid}_final"] = ""
                row[f"{cid}_missing"] = ""
            rows.append(row)
            continue
        for cid in target_ids:
            c = report["competencies"].get(cid, {})
            row[f"{cid}_final"] = c.get("final_score", "")
            row[f"{cid}_missing"] = ",".join(c.get("missing_slots", []))
        rows.append(row)
    return rows


def write_csv(rows: list, target_ids: list, output_path: str):
    fieldnames = ["file", "label", "error"]
    for cid in target_ids:
        fieldnames += [f"{cid}_final", f"{cid}_missing"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_folders(folder_labels: dict, model, target_ids: list, output_path: str, function_name: str = None) -> list:
    """folder_labels: {folder_path: label}. Runs each folder, tags rows with
    its label, writes one combined CSV, and returns all rows (e.g. for a
    quick sanity check against known ground truth, when available)."""
    all_rows = []
    for folder, label in folder_labels.items():
        all_rows.extend(process_folder(folder, model, target_ids, label=label, function_name=function_name))
    write_csv(all_rows, target_ids, output_path)
    return all_rows
