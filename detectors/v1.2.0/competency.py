"""
Competency extraction model.

Two layers of competencies over a Python AST:
  - Primitive competencies: DECL, INPUT, OUTPUT, TEST, LOOP, ASSIGN
  - Advanced competencies: composed of primitives and/or other Advanced
    competencies, via a CoverageRule (how much must be present) and a
    StructuralConstraint (how the pieces must relate).

Every resolved competency (primitive or advanced) produces an Evidence
object exposing a line-span and role bindings, so Advanced competencies
can be nested inside further Advanced competencies uniformly.
"""

from __future__ import annotations
import ast
from dataclasses import dataclass, field
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

@dataclass
class Evidence:
    """A single match for a competency, primitive or composite."""
    competency_id: str
    node: Optional[ast.AST]          # underlying AST node (None for pure composites)
    start_line: int
    end_line: int
    bindings: dict = field(default_factory=dict)   # role -> variable/expr name (str)
    enclosing: Optional[ast.AST] = None             # nearest enclosing block, for NESTED checks
    scope: Optional[ast.AST] = None                  # enclosing FunctionDef (None = module-level); guards against cross-function contamination
    score: float = 1.0                               # own resolved score (matters for composites)
    children: dict = field(default_factory=dict)     # for composites: component_id -> Evidence

    def contains_line(self, line: int) -> bool:
        return self.start_line <= line <= self.end_line


@dataclass
class Result:
    """Outcome of resolving one competency against one submission."""
    competency_id: str
    coverage_score: float
    structural_score: float
    final_score: float
    evidences: list          # list[Evidence] chosen as the best match(es)
    detail: str = ""         # human-readable explanation, for feedback


# ---------------------------------------------------------------------------
# Helpers for reading source text and enclosing blocks
# ---------------------------------------------------------------------------

def _expr_str(node: Optional[ast.AST]) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node).strip()
    except Exception:
        return ""


def _line_span(node: ast.AST):
    start = node.lineno
    end = getattr(node, "end_lineno", None) or start
    for child in ast.walk(node):
        cl = getattr(child, "end_lineno", None)
        if cl:
            end = max(end, cl)
    return start, end


class _ParentIndex:
    """Maps each node to its parent, so we can find 'enclosing block'."""
    def __init__(self, tree: ast.AST):
        self.parent = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                self.parent[child] = node

    def enclosing_block(self, node: ast.AST):
        """Nearest ancestor that is a For/While/If/FunctionDef (a 'block')."""
        cur = self.parent.get(node)
        block_types = (ast.For, ast.While, ast.If, ast.FunctionDef)
        while cur is not None and not isinstance(cur, block_types):
            cur = self.parent.get(cur)
        return cur

    def enclosing_function(self, node: ast.AST):
        """Nearest ancestor FunctionDef, skipping past For/While/If -- this
        is 'which function's scope is this evidence in', distinct from
        enclosing_block which stops at the first block of any kind.
        Returns None for genuinely module-level evidence."""
        cur = self.parent.get(node)
        while cur is not None and not isinstance(cur, ast.FunctionDef):
            cur = self.parent.get(cur)
        return cur


# ---------------------------------------------------------------------------
# Primitive detectors
# Each takes (tree, parent_index) and returns a list[Evidence]
# ---------------------------------------------------------------------------

def detect_decl(tree, pidx) -> list:
    """Heuristic: first assignment to a name in a scope, with a simple
    literal/empty-collection value -> treated as a 'declaration'."""
    seen = set()
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in seen:
                continue
            is_simple_init = isinstance(node.value, (ast.Constant, ast.List, ast.Dict, ast.Set)) \
                or (isinstance(node.value, ast.Call) and _expr_str(node.value) in ("list()", "dict()", "set()"))
            if is_simple_init:
                seen.add(name)
                s, e = _line_span(node)
                out.append(Evidence("DECL", node, s, e,
                                     bindings={"target": name},
                                     enclosing=pidx.enclosing_block(node)))
    return out


def detect_input(tree, pidx) -> list:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "input":
            # find the assignment this input() feeds, if any
            target = None
            p = pidx.parent.get(node)
            hops = 0
            while p is not None and hops < 4:
                if isinstance(p, ast.Assign) and len(p.targets) == 1 and isinstance(p.targets[0], ast.Name):
                    target = p.targets[0].id
                    break
                p = pidx.parent.get(p)
                hops += 1
            s, e = _line_span(node)
            out.append(Evidence("INPUT", node, s, e,
                                 bindings={"target": target},
                                 enclosing=pidx.enclosing_block(node)))
    return out


def detect_builtin_reduce(tree, pidx) -> list:
    """Calls to max()/min() -- the 'find the extremum via builtin' alternative
    to a manual TEST-based comparison loop. Whether a competency should
    credit this as equivalent to the manual form is a modeling choice, not
    something this detector decides; it just surfaces the evidence so a
    competency definition can choose ALL, ANY, or ignore it."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("max", "min"):
            s, e = _line_span(node)
            out.append(Evidence("BUILTIN_REDUCE", node, s, e,
                                 bindings={"op": node.func.id, "source": ", ".join(_expr_str(a) for a in node.args)},
                                 enclosing=pidx.enclosing_block(node)))
    return out


def detect_func_def(tree, pidx) -> list:
    """One evidence per function definition. Distinct from PARAM (which
    fires once per parameter): this is 'a function exists' as its own
    checkable fact, with whether it returns a value as a binding so
    'defined a function' and 'defined a function that returns something'
    can be told apart."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            has_return = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))
            s, e = _line_span(node)
            out.append(Evidence("FUNC_DEF", node, s, e,
                                 bindings={"name": node.name,
                                           "n_params": str(len(node.args.args)),
                                           "has_return": "yes" if has_return else "no"},
                                 enclosing=node))
    return out


def detect_param(tree, pidx) -> list:
    """Function parameters are also a 'data enters here' primitive, distinct
    from INPUT (console input). Function-graded assignments (the common case
    in autograded exercises) receive data via parameters, not input()."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for a in node.args.args:
                out.append(Evidence("PARAM", node, node.lineno, node.lineno,
                                     bindings={"target": a.arg},
                                     enclosing=node))
    return out


def detect_output(tree, pidx) -> list:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and node.value is not None:
            s, e = _line_span(node)
            out.append(Evidence("OUTPUT", node, s, e,
                                 bindings={"source": _expr_str(node.value)},
                                 enclosing=pidx.enclosing_block(node)))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            s, e = _line_span(node)
            args = ", ".join(_expr_str(a) for a in node.args)
            out.append(Evidence("OUTPUT", node, s, e,
                                 bindings={"source": args},
                                 enclosing=pidx.enclosing_block(node)))
    return out


_CMP_OPS = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=", ast.Eq: "==", ast.NotEq: "!="}


def detect_test(tree, pidx) -> list:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            operand = comparator = op = None
            test = node.test
            if isinstance(test, ast.Compare) and len(test.ops) == 1:
                operand = _expr_str(test.left)
                comparator = _expr_str(test.comparators[0])
                op = _CMP_OPS.get(type(test.ops[0]), "?")
            else:
                operand = _expr_str(test)
            s, e = _line_span(node)
            out.append(Evidence("TEST", node, s, e,
                                 bindings={"operand": operand, "comparator": comparator, "op": op},
                                 enclosing=pidx.enclosing_block(node)))
    return out


def detect_loop(tree, pidx) -> list:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            iterator_var = None
            bound_expr = None
            kind = "for" if isinstance(node, ast.For) else "while"
            if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                iterator_var = node.target.id
                bound_expr = _expr_str(node.iter)
            elif isinstance(node, ast.While):
                bound_expr = _expr_str(node.test)
            s, e = _line_span(node)
            out.append(Evidence("LOOP", node, s, e,
                                 bindings={"iterator_var": iterator_var, "bound_expr": bound_expr, "kind": kind},
                                 enclosing=pidx.enclosing_block(node)))
    return out


def detect_assign(tree, pidx) -> list:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = _expr_str(node.targets[0])
            source = _expr_str(node.value)
            s, e = _line_span(node)
            out.append(Evidence("ASSIGN", node, s, e,
                                 bindings={"target": target, "source": source},
                                 enclosing=pidx.enclosing_block(node)))
        elif isinstance(node, ast.AugAssign):
            target = _expr_str(node.target)
            op = type(node.op).__name__
            source = f"{target} {op} {_expr_str(node.value)}"
            s, e = _line_span(node)
            out.append(Evidence("ASSIGN", node, s, e,
                                 bindings={"target": target, "source": source},
                                 enclosing=pidx.enclosing_block(node)))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("append", "add", "pop", "remove"):
            # collection mutation counts as an assignment-like effect
            target = _expr_str(node.func.value)
            source = ", ".join(_expr_str(a) for a in node.args)
            s, e = _line_span(node)
            out.append(Evidence("ASSIGN", node, s, e,
                                 bindings={"target": target, "source": source, "kind": node.func.attr},
                                 enclosing=pidx.enclosing_block(node)))
    return out


PRIMITIVE_DETECTORS: dict = {
    "DECL": detect_decl,
    "INPUT": detect_input,
    "PARAM": detect_param,
    "FUNC_DEF": detect_func_def,
    "OUTPUT": detect_output,
    "TEST": detect_test,
    "LOOP": detect_loop,
    "ASSIGN": detect_assign,
    "BUILTIN_REDUCE": detect_builtin_reduce,
}


# ---------------------------------------------------------------------------
# Coverage rules
# ---------------------------------------------------------------------------

class CoverageRule:
    def score(self, component_scores: dict) -> float:
        raise NotImplementedError


@dataclass
class ALL(CoverageRule):
    ids: list
    def score(self, component_scores):
        if not self.ids:
            return 1.0
        return sum(component_scores.get(i, 0.0) for i in self.ids) / len(self.ids)


@dataclass
class ANY(CoverageRule):
    ids: list
    def score(self, component_scores):
        return max((component_scores.get(i, 0.0) for i in self.ids), default=0.0)


@dataclass
class K_OF_N(CoverageRule):
    k: int
    ids: list
    def score(self, component_scores):
        vals = sorted((component_scores.get(i, 0.0) for i in self.ids), reverse=True)
        top_k = vals[: self.k]
        return sum(top_k) / self.k if self.k else 1.0


@dataclass
class WEIGHTED(CoverageRule):
    weights: dict   # id -> weight
    def score(self, component_scores):
        total_w = sum(self.weights.values()) or 1.0
        return sum(self.weights[i] * component_scores.get(i, 0.0) for i in self.weights) / total_w


# ---------------------------------------------------------------------------
# Structural constraints
# Each evaluates against a dict: component_id -> Evidence (best match chosen)
# ---------------------------------------------------------------------------

class StructuralConstraint:
    def score(self, evmap: dict, ctx: dict = None) -> float:
        raise NotImplementedError


@dataclass
class NESTED(StructuralConstraint):
    outer: str
    inner: str
    def score(self, evmap, ctx=None):
        outer_ev, inner_ev = evmap.get(self.outer), evmap.get(self.inner)
        if not outer_ev or not inner_ev:
            return 0.0
        if outer_ev.start_line <= inner_ev.start_line and inner_ev.end_line <= outer_ev.end_line \
                and outer_ev.node is not inner_ev.node:
            return 1.0
        return 0.0


@dataclass
class SEQUENTIAL(StructuralConstraint):
    ids: list
    max_line_gap: int = 3
    def score(self, evmap, ctx=None):
        evs = [evmap.get(i) for i in self.ids]
        if any(e is None for e in evs):
            return 0.0
        evs_sorted = sorted(evs, key=lambda e: e.start_line)
        for a, b in zip(evs_sorted, evs_sorted[1:]):
            if b.start_line - a.end_line > self.max_line_gap:
                return 0.0
        return 1.0


@dataclass
class SHARED_BINDING(StructuralConstraint):
    # list of (id_a, role_a, id_b, role_b); order-independent set match optional
    pairs: list
    as_set: bool = False
    def score(self, evmap, ctx=None):
        matches = 0
        for (ida, ra, idb, rb) in self.pairs:
            ea, eb = evmap.get(ida), evmap.get(idb)
            if not ea or not eb:
                continue
            va, vb = ea.bindings.get(ra), eb.bindings.get(rb)
            if va is None or vb is None:
                continue
            if va == vb:
                matches += 1
        return matches / len(self.pairs) if self.pairs else 1.0


@dataclass
class SELF_REFERENTIAL(StructuralConstraint):
    """Checks that the ASSIGN's own target variable also appears in its source expr."""
    id: str
    def score(self, evmap, ctx=None):
        ev = evmap.get(self.id)
        if not ev:
            return 0.0
        target = ev.bindings.get("target")
        source = ev.bindings.get("source", "")
        if target and target in source:
            return 1.0
        return 0.0


def _split_tuple_text(s: str) -> list:
    s = s.strip()
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1]
    return [p.strip() for p in s.split(",") if p.strip()]


@dataclass
class TUPLE_SWAP(StructuralConstraint):
    """Checks that a single ASSIGN evidence is Python's idiomatic tuple swap:
    `a, b = b, a` (one Assign node, target and value both 2-tuples, reversed)."""
    id: str
    def score(self, evmap, ctx=None):
        ev = evmap.get(self.id)
        if not ev:
            return 0.0
        target_parts = _split_tuple_text(ev.bindings.get("target", ""))
        source_parts = _split_tuple_text(ev.bindings.get("source", ""))
        if len(target_parts) == 2 and len(source_parts) == 2 \
                and target_parts == list(reversed(source_parts)):
            return 1.0
        return 0.0


def _resolve_evidence(evmap: dict, dotted_id: str):
    """Resolve 'acc.assign' -> evmap['acc'].children['assign'], so
    constraints can reach into a composite's inner evidence."""
    parts = dotted_id.split(".")
    ev = evmap.get(parts[0])
    for p in parts[1:]:
        if ev is None:
            return None
        ev = ev.children.get(p)
    return ev


@dataclass
class REFERENCES(StructuralConstraint):
    """Checks that a value bound at (source_id, source_role) appears
    textually inside the expression bound at (target_id, target_role).
    E.g. the accumulator variable from Accumulation's inner ASSIGN
    appearing in the OUTPUT expression that's supposed to average it."""
    source_id: str
    source_role: str
    target_id: str
    target_role: str
    def score(self, evmap, ctx=None):
        se = _resolve_evidence(evmap, self.source_id)
        te = _resolve_evidence(evmap, self.target_id)
        if not se or not te:
            return 0.0
        needle = se.bindings.get(self.source_role)
        haystack = te.bindings.get(self.target_role, "") or ""
        return 1.0 if needle and needle in haystack else 0.0


@dataclass
class CONTAINS_TEXT(StructuralConstraint):
    """Checks that a binding's text contains at least one of the given
    substrings -- a deliberately blunt tool (e.g. '/' to confirm an
    OUTPUT expression actually divides, not just prints the running sum)."""
    id: str
    role: str
    substrings: tuple
    def score(self, evmap, ctx=None):
        ev = _resolve_evidence(evmap, self.id)
        if not ev:
            return 0.0
        text = ev.bindings.get(self.role, "") or ""
        return 1.0 if any(s in text for s in self.substrings) else 0.0


def _walk_elif_chain(if_node):
    """Walk forward through an ast.If's elif links (Python represents
    `elif` as a single-element orelse containing another If). Returns
    (branch_count, has_final_else, variable_sets) where variable_sets is
    one frozenset of referenced variable names per branch -- used to check
    whether branches are 'the same decision' even when their tests have
    different shapes (a plain Compare vs. a compound and/or expression),
    rather than requiring an identical single operand string. This is a
    property of ONE AST node's own recursive shape, not a composition of
    separate pieces, which is precisely why it's computed directly rather
    than via nested Advanced competencies (see module docstring note on
    multi-way branching)."""
    def _vars_of(test_expr):
        return frozenset(n.id for n in ast.walk(test_expr) if isinstance(n, ast.Name))

    count = 1
    variable_sets = [_vars_of(if_node.test)]
    node = if_node
    has_else = False
    while True:
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            node = node.orelse[0]
            count += 1
            variable_sets.append(_vars_of(node.test))
        elif len(node.orelse) > 0:
            has_else = True
            break
        else:
            break
    return count, has_else, variable_sets


@dataclass
class EXHAUSTIVE_CHAIN(StructuralConstraint):
    """Checks a TEST evidence's own if/elif/.../else chain: at least
    min_branches total distinguishable outcomes (each If-test, PLUS a
    terminal else if present -- an if/elif/else has 3 outcomes from only
    2 If nodes, which is easy to undercount if you only count If nodes),
    optionally requiring a final else and/or that every branch shares at
    least one common variable across its condition (mutual exclusivity on
    the same decision, not just unrelated ifs that happen to be
    elif-chained) -- checked via shared variables rather than an identical
    operand string, so compound boolean branches (e.g. an `and`/`or` of
    several comparisons) still count as 'the same decision' as long as
    they reference a common variable."""
    id: str
    min_branches: int = 2
    require_else: bool = False
    require_same_operand: bool = False
    def score(self, evmap, ctx=None):
        ev = evmap.get(self.id)
        if not ev or not isinstance(ev.node, ast.If):
            return 0.0
        count, has_else, variable_sets = _walk_elif_chain(ev.node)
        total_outcomes = count + (1 if has_else else 0)
        if total_outcomes < self.min_branches:
            return 0.0
        if self.require_else and not has_else:
            return 0.0
        if self.require_same_operand:
            common = set.intersection(*[set(v) for v in variable_sets]) if variable_sets else set()
            if not common:
                return 0.0
        return 1.0


@dataclass
class AND(StructuralConstraint):
    parts: list
    def score(self, evmap, ctx=None):
        vals = [p.score(evmap, ctx) for p in self.parts]
        return min(vals) if vals else 1.0


@dataclass
class OR(StructuralConstraint):
    parts: list
    def score(self, evmap, ctx=None):
        vals = [p.score(evmap, ctx) for p in self.parts]
        return max(vals) if vals else 0.0


@dataclass
class COOCCUR(StructuralConstraint):
    ids: list
    def score(self, evmap, ctx=None):
        return 1.0 if all(evmap.get(i) for i in self.ids) else 0.0


@dataclass
class DISTINCT_BINDINGS(StructuralConstraint):
    """Checks that no two slots in `ids` share the same combined value across
    `roles` -- e.g. two TEST branches shouldn't have identical
    (operand, op, comparator), or the 'multi-way' branching is really just
    the same condition repeated. Comparing operand alone would misfire on
    the extremely common `if x==1: elif x==2:` (same operand, different
    comparator) -- comparing the full tuple avoids that false negative."""
    ids: list
    roles: tuple
    def score(self, evmap, ctx=None):
        keys = []
        for i in self.ids:
            ev = evmap.get(i)
            if ev is None:
                return 0.0
            keys.append(tuple(ev.bindings.get(r) for r in self.roles))
        return 1.0 if len(set(keys)) == len(keys) else 0.0


@dataclass
class HAS_ELSE(StructuralConstraint):
    """Checks that a TEST evidence's If node ends the chain with a genuine
    terminal `else:` -- not another `elif` (which is itself a nested If in
    orelse) and not simply absent."""
    id: str
    def score(self, evmap, ctx=None):
        ev = evmap.get(self.id)
        if not ev or not isinstance(ev.node, ast.If):
            return 0.0
        orelse = ev.node.orelse
        if not orelse:
            return 0.0
        if len(orelse) == 1 and isinstance(orelse[0], ast.If):
            return 0.0   # that's an elif, not a terminal else
        return 1.0


@dataclass
class DELEGATES(StructuralConstraint):
    """Cross-function composition: the evidence in call_slot must be a CALL
    to a sibling function whose OWN body, independently resolved, satisfies
    callee_competency_id. This is fundamentally different from NESTED/etc,
    which reason about AST containment within one block -- this reasons
    about a call edge between two separately-resolved function scopes.

    Requires ctx = {"model": CompetencyModel, "function_index": {name: FunctionDef}}
    supplied by CompetencyModel.resolve(); falls back to 0.0 without it.
    Memoizes per (callee, competency_id) and guards against recursive calls
    (a function delegating to itself, directly or via a cycle) by treating
    an in-progress resolution as a non-match rather than looping forever.
    """
    call_slot: str
    callee_competency_id: str
    def score(self, evmap, ctx=None):
        ev = evmap.get(self.call_slot)
        if not ev or ctx is None:
            return 0.0
        callee_name = ev.bindings.get("callee")
        func_node = ctx["function_index"].get(callee_name)
        if func_node is None:
            return 0.0
        key = (callee_name, self.callee_competency_id)
        if key in ctx["in_progress"]:
            return 0.0
        if key in ctx["delegate_cache"]:
            return ctx["delegate_cache"][key]
        ctx["in_progress"].add(key)
        try:
            result = ctx["model"].resolve(func_node, [self.callee_competency_id], module_tree=ctx.get("module_tree"))
            score = result[self.callee_competency_id].final_score if self.callee_competency_id in result else 0.0
        finally:
            ctx["in_progress"].discard(key)
        ctx["delegate_cache"][key] = score
        return score


# ---------------------------------------------------------------------------
# Competency definition + resolver
# ---------------------------------------------------------------------------

@dataclass
class Competency:
    id: str
    # slot_name -> type_id, where type_id is either:
    #   - a single competency id (primitive or advanced), or
    #   - a tuple of alternative ids (any one of them may fill the slot,
    #     e.g. ("INPUT", "PARAM") for "a value enters here, console or arg")
    # Slot names are what CoverageRule / StructuralConstraint refer to.
    # Using slot names (not raw type ids) is what lets a competency like
    # Swap require three ASSIGN evidences in three distinct roles.
    components: dict
    coverage: CoverageRule = None
    structural: StructuralConstraint = None
    is_primitive: bool = False


def _alt_ids(type_id):
    """Normalize a slot's type_id (str or tuple) to a tuple of alternatives."""
    return type_id if isinstance(type_id, tuple) else (type_id,)


class CompetencyModel:
    def __init__(self):
        self.definitions: dict = {}   # id -> Competency

    def register(self, comp: Competency):
        self.definitions[comp.id] = comp

    def _topo_order(self, root_ids):
        order = []
        visited = set()
        temp = set()

        def visit(cid):
            if cid in visited:
                return
            if cid in temp:
                raise ValueError(f"Cycle detected at {cid}")
            if cid not in self.definitions:
                return  # primitive with no separate def entry
            temp.add(cid)
            for type_id in self.definitions[cid].components.values():
                for alt in _alt_ids(type_id):
                    visit(alt)
            temp.discard(cid)
            visited.add(cid)
            order.append(cid)

        for rid in root_ids:
            visit(rid)
        return order

    def resolve_by_scope(self, tree: ast.AST, target_ids: list) -> dict:
        """Resolve target_ids independently per function (plus a synthetic
        '<module>' scope for top-level code outside any function), instead
        of pooling every primitive across the whole file into one flat
        evidence pool. This is what actually prevents SHARED_BINDING (or
        any future variable-name-based check) from matching two unrelated
        functions that happen to use the same variable name -- resolve()
        alone only protects nested-containment checks like NESTED, which
        naturally can't span two functions' non-overlapping line ranges,
        but SHARED_BINDING has no such protection on its own.

        Returns {scope_name: {competency_id: Result}}. Cross-function
        DELEGATES still works inside each per-function resolve() call,
        because the sibling function index is always built from the whole
        module_tree regardless of which function's primitives are in scope.
        """
        if not isinstance(tree, ast.Module):
            # Nothing to partition -- already a single function/snippet.
            return {"<single>": self.resolve(tree, target_ids, module_tree=tree)}

        results = {}
        top_level_functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        for func in top_level_functions:
            results[func.name] = self.resolve(func, target_ids, module_tree=tree)

        non_function_stmts = [n for n in tree.body if not isinstance(n, ast.FunctionDef)]
        if non_function_stmts:
            module_scope = ast.Module(body=non_function_stmts, type_ignores=[])
            results["<module>"] = self.resolve(module_scope, target_ids, module_tree=tree)

        return results

    def resolve(self, tree: ast.AST, target_ids: list, module_tree: ast.AST = None) -> dict:
        import itertools
        pidx = _ParentIndex(tree)

        # 1. run primitive detectors once, scoped to `tree` -- when called
        # via resolve_by_scope, `tree` is a single function's subtree, so
        # DECL/LOOP/TEST/ASSIGN/etc. evidence can never spuriously match
        # across two unrelated functions (SHARED_BINDING in particular has
        # no location awareness of its own; scoping the detector pass is
        # what actually prevents cross-function name collisions, not NESTED,
        # which only protects nested-containment checks).
        primitive_evidence = {pid: fn(tree, pidx) for pid, fn in PRIMITIVE_DETECTORS.items()}

        # 1b. Sibling function lookup for CALL/DELEGATES is intentionally
        # NOT scoped to `tree` -- it always comes from module_tree (the
        # whole file), defaulting to `tree` itself when not given (e.g. the
        # original single-call usage, or resolving a function in isolation
        # with no siblings in view). This is what lets per-function primitive
        # scoping and cross-function delegation coexist: a function can be
        # analyzed in isolation for its own DECL/LOOP/etc., while still being
        # able to delegate to a sibling defined elsewhere in the same file.
        module_tree = module_tree if module_tree is not None else tree
        function_index = {n.name: n for n in ast.walk(module_tree) if isinstance(n, ast.FunctionDef)}
        call_evidence = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in function_index:
                s, e = _line_span(node)
                call_evidence.append(Evidence("CALL", node, s, e,
                                               bindings={"callee": node.func.id},
                                               enclosing=pidx.enclosing_block(node)))
        primitive_evidence["CALL"] = call_evidence

        # Tag every piece of evidence with its enclosing function (None =
        # module-level). This is what lets the resolver refuse to combine
        # evidence from two unrelated functions just because a structural
        # constraint (typically SHARED_BINDING, which has no line-based
        # containment check of its own) happens to match on variable name.
        for evs in primitive_evidence.values():
            for ev in evs:
                if ev.node is None:
                    continue
                if ev.competency_id == "PARAM" and isinstance(ev.node, ast.FunctionDef):
                    # PARAM stores the FunctionDef itself as .node (there's
                    # no separate AST node per-argument worth tracking), so
                    # enclosing_function would walk PAST it to the parent
                    # scope -- a parameter belongs to the function it's a
                    # parameter of, not that function's enclosing context.
                    ev.scope = ev.node
                else:
                    ev.scope = pidx.enclosing_function(ev.node)

        ctx = {"model": self, "function_index": function_index, "module_tree": module_tree,
               "delegate_cache": {}, "in_progress": set()}

        cache: dict = {}   # competency_id -> Result

        order = self._topo_order(target_ids)
        for cid in order:
            comp = self.definitions[cid]

            # Split slots into: fixed (resolves to a single advanced-competency
            # evidence) vs. candidate lists (one or more primitive occurrences,
            # possibly pooled across alternative types for an OR-slot).
            fixed = {}
            candidate_lists = {}
            for slot, type_id in comp.components.items():
                alts = _alt_ids(type_id)
                if len(alts) == 1 and alts[0] in cache:
                    res = cache[alts[0]]
                    has_evidence = res.final_score > 0 and res.evidences
                    fixed[slot] = (res.final_score, res.evidences[0] if has_evidence else None)
                else:
                    pool = []
                    for alt in alts:
                        pool.extend(primitive_evidence.get(alt, []))
                    candidate_lists[slot] = pool if pool else [None]

            # Search combinations of primitive evidence (capped to keep it cheap)
            keys = list(candidate_lists.keys())
            combos = list(itertools.product(*[candidate_lists[k] for k in keys])) if keys else [()]
            MAX_COMBOS = 300
            if len(combos) > MAX_COMBOS:
                combos = combos[:MAX_COMBOS]

            best = None  # (final_score, coverage_score, structural_score, evmap)
            fixed_scopes = {ev.scope for (_, ev) in fixed.values() if ev is not None and ev.scope is not None}
            for combo in combos:
                # skip combos that reuse the exact same AST node in two slots
                nodes_used = [ev.node for ev in combo if ev is not None]
                if len(nodes_used) != len(set(id(n) for n in nodes_used)):
                    continue

                # skip combos that mix evidence from two different functions
                # (a coincidental variable-name match across unrelated
                # functions should not satisfy a competency)
                combo_scopes = {ev.scope for ev in combo if ev is not None and ev.scope is not None}
                if len(fixed_scopes | combo_scopes) > 1:
                    continue

                evmap = {slot: ev for slot, (_, ev) in fixed.items() if ev is not None}
                component_scores = {slot: score for slot, (score, _) in fixed.items()}
                for slot, ev in zip(keys, combo):
                    component_scores[slot] = 1.0 if ev is not None else 0.0
                    if ev is not None:
                        evmap[slot] = ev

                coverage_score = comp.coverage.score(component_scores) if comp.coverage else 1.0
                structural_score = comp.structural.score(evmap, ctx) if comp.structural else 1.0
                final_score = coverage_score * structural_score
                if best is None or final_score > best[0]:
                    best = (final_score, coverage_score, structural_score, evmap)

            if best is None:
                # every combo was rejected by the node-reuse guard; fall back
                # to the empty combination so we still report 0 rather than crash
                evmap = {slot: ev for slot, (_, ev) in fixed.items() if ev is not None}
                component_scores = {slot: score for slot, (score, _) in fixed.items()}
                for slot in keys:
                    component_scores.setdefault(slot, 0.0)
                coverage_score = comp.coverage.score(component_scores) if comp.coverage else 1.0
                structural_score = comp.structural.score(evmap, ctx) if comp.structural else 1.0
                best = (coverage_score * structural_score, coverage_score, structural_score, evmap)

            final_score, coverage_score, structural_score, evmap = best

            if evmap:
                lines = [e.start_line for e in evmap.values()] + [e.end_line for e in evmap.values()]
                span = (min(lines), max(lines))
            else:
                span = (0, 0)

            composite_ev = Evidence(cid, None, span[0], span[1],
                                     bindings={}, score=final_score, children=evmap)
            child_scopes = {e.scope for e in evmap.values() if e.scope is not None}
            composite_ev.scope = child_scopes.pop() if len(child_scopes) == 1 else None

            detail = f"coverage={coverage_score:.2f} structural={structural_score:.2f}"
            cache[cid] = Result(cid, coverage_score, structural_score, final_score,
                                 [composite_ev], detail)

        return {tid: cache[tid] for tid in target_ids if tid in cache}
