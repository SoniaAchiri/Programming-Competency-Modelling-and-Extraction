"""
Per-submission competency report.

Two layers, matching the model itself:
  - Primitive inventory: every primitive construct found, with its
    location and a short human-readable description.
  - Advanced competency scorecard: for a chosen list of target
    competency ids, the resolved coverage/structural/final scores, PLUS
    which named slots were actually satisfied vs. missing -- this part
    is only possible because composite Evidence keeps a `children` map,
    so we can compare a competency's declared slots against which ones
    actually got evidence.

Known limitation, stated plainly rather than glossed over: when a
composite's STRUCTURAL score is < 1.0 but coverage is 1.0 (all pieces
present, wrong arrangement), the report can currently only surface the
aggregate structural score, not which specific sub-constraint inside an
AND/OR failed. Constraints don't yet expose per-part results, only a
combined float. Surfacing that would need each StructuralConstraint to
optionally report its own breakdown, not just a score -- worth doing if
this report is used for actual student-facing feedback, since "structure
failed" alone doesn't tell a student what to fix.
"""

import ast
from competency import PRIMITIVE_DETECTORS, _ParentIndex, CompetencyModel


def _describe(ev) -> str:
    """One short human-readable line per evidence, by primitive type."""
    b = ev.bindings
    cid = ev.competency_id
    if cid == "DECL":
        return f"{b.get('target')} declared"
    if cid == "INPUT":
        return f"input() -> {b.get('target')}"
    if cid == "PARAM":
        return f"parameter {b.get('target')}"
    if cid == "FUNC_DEF":
        ret = "returns a value" if b.get("has_return") == "yes" else "no return value"
        return f"def {b.get('name')}({b.get('n_params')} params), {ret}"
    if cid == "OUTPUT":
        return f"output: {b.get('source')}"
    if cid == "TEST":
        if b.get("comparator") is not None:
            return f"if {b.get('operand')} {b.get('op')} {b.get('comparator')}"
        return f"if {b.get('operand')}"
    if cid == "LOOP":
        if b.get("kind") == "for":
            return f"for {b.get('iterator_var')} in {b.get('bound_expr')}"
        return f"while {b.get('bound_expr')}"
    if cid == "ASSIGN":
        kind = b.get("kind")
        if kind in ("append", "add", "pop", "remove"):
            return f"{b.get('target')}.{kind}({b.get('source')})"
        return f"{b.get('target')} = {b.get('source')}"
    if cid == "BUILTIN_REDUCE":
        return f"{b.get('op')}({b.get('source')})"
    if cid == "CALL":
        return f"calls {b.get('callee')}(...)"
    return str(b)


def generate_report(source: str, model: CompetencyModel, target_ids: list, function_name: str = None) -> dict:
    """Build the structured report dict for one submission's source code.

    If function_name is given, both the primitive inventory and the
    competency resolution are scoped to JUST that function's own body --
    this matters because resolving against the whole file only guards
    against evidence from two DIFFERENT unrelated functions combining
    within one competency (the per-function scoping guard); it does
    nothing to stop an unrelated helper function elsewhere in the file
    from satisfying a competency on its own, which then gets credited to
    the file as a whole even though the function actually being graded
    (e.g. `top_k`) might not implement it at all. When you know which
    function the assignment asks students to write, always pass it.
    """
    tree = ast.parse(source)

    if function_name is not None:
        target_node = next(
            (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == function_name),
            None,
        )
        if target_node is None:
            return {"error": f"function '{function_name}' not found in submission",
                    "primitives": {}, "competencies": {}}
        scan_tree = target_node
        results = model.resolve(target_node, target_ids, module_tree=tree)
    else:
        scan_tree = tree
        results = model.resolve(tree, target_ids)

    pidx = _ParentIndex(scan_tree)
    primitives = {}
    for pid, detector in PRIMITIVE_DETECTORS.items():
        evs = detector(scan_tree, pidx)
        if evs:
            primitives[pid] = [
                {"line": ev.start_line, "end_line": ev.end_line, "summary": _describe(ev)}
                for ev in evs
            ]

    competencies = {}
    for cid in target_ids:
        if cid not in results:
            competencies[cid] = {"error": "not found / unresolved"}
            continue
        res = results[cid]
        comp_def = model.definitions.get(cid)
        declared_slots = list(comp_def.components.keys()) if comp_def else []
        present_evmap = res.evidences[0].children if res.evidences else {}
        present = [s for s in declared_slots if s in present_evmap]
        missing = [s for s in declared_slots if s not in present_evmap]
        competencies[cid] = {
            "final_score": round(res.final_score, 2),
            "coverage_score": round(res.coverage_score, 2),
            "structural_score": round(res.structural_score, 2),
            "present_slots": present,
            "missing_slots": missing,
            "detail": res.detail,
        }

    return {"primitives": primitives, "competencies": competencies}


def format_report_text(report: dict, title: str = "") -> str:
    """Render the structured report as readable text."""
    lines = []
    if title:
        lines.append(f"{'='*60}\n{title}\n{'='*60}")

    lines.append("\nPRIMITIVES DETECTED")
    if not report["primitives"]:
        lines.append("  (none)")
    for pid, evs in report["primitives"].items():
        lines.append(f"  {pid} x{len(evs)}")
        for ev in evs:
            lines.append(f"      line {ev['line']:>3}: {ev['summary']}")

    lines.append("\nADVANCED COMPETENCIES")
    for cid, c in report["competencies"].items():
        if "error" in c:
            lines.append(f"  {cid:20s}  {c['error']}")
            continue
        marker = "OK  " if c["final_score"] >= 0.999 else ("--  " if c["final_score"] == 0 else "~~  ")
        lines.append(f"  {marker}{cid:20s} final={c['final_score']:.2f}  "
                      f"(coverage={c['coverage_score']:.2f} structural={c['structural_score']:.2f})")
        if c["present_slots"]:
            lines.append(f"        present: {', '.join(c['present_slots'])}")
        if c["missing_slots"]:
            lines.append(f"        missing: {', '.join(c['missing_slots'])}")
        if c["coverage_score"] >= 0.999 and c["structural_score"] < 0.999:
            lines.append("        note: all slots had SOME matching candidate, "
                         "but the required arrangement (or specific kind) was not satisfied")
    return "\n".join(lines)
