"""T3.7 — SESSION_FSM.md conformance test.

Parses docs/SESSION_FSM.md's §3 transition table and cross-checks it against
the REAL reachable (from_state -> to_state) edges in dialogue/controller.py
(derived by AST: the `_tick` match statement's state->handler mapping, plus
every `ctx.state = FSMState.X` assignment inside each handler). Catches drift
in both directions:
  - an edge reachable in code but not documented (REVIEW's "undocumented
    auto-help/probe->help/probe-demote transitions")
  - an edge documented but never actually reachable in code (REVIEW's dead
    PARENT_ACK_WAIT state)

The escalation-freeze global pre-empt (any non-terminal -> ESCALATION_FREEZE
on safety_trigger) lives outside `_tick`'s per-state dispatch (in
`_step_core`'s pre-empt block) and is documented once, globally, in §3's
"Global pre-empts" table — both sides exempt it from the per-state edge
check rather than requiring a doc row for every single state.

Inline smoke runner:
    python3 tests/dialogue/test_session_fsm.py
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

CONTROLLER_PATH = REPO / "src" / "mentar" / "dialogue" / "controller.py"
DOC_PATH = REPO / "docs" / "SESSION_FSM.md"


# ESCALATION_FREEZE isn't dispatched via _tick's match statement at all — the child-input
# path is absorbed earlier in _step_core's pre-empt block, and the only real way OUT of
# ESCALATION_FREEZE is the parent control plane (parent_acknowledge -> _handle_parent_ack,
# gated on `ctx.state is FSMState.ESCALATION_FREEZE`), called outside _tick entirely.
_EXTRA_DISPATCH: dict[str, list[str]] = {
    "ESCALATION_FREEZE": ["_handle_parent_ack"],
}


def _code_edges() -> set[tuple[str, str]]:
    """Every (from_state, to_state) pair reachable via a per-state handler."""
    tree = ast.parse(CONTROLLER_PATH.read_text(encoding="utf-8"))
    class_node = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "SessionController")
    methods = {n.name: n for n in class_node.body if isinstance(n, ast.FunctionDef)}
    tick = methods["_tick"]

    # Find the `match state:` statement inside _tick and build state -> handler-method-name(s).
    match_stmt = next(n for n in ast.walk(tick) if isinstance(n, ast.Match))
    state_to_methods: dict[str, list[str]] = {}
    for case in match_stmt.cases:
        state_names = []
        pattern = case.pattern
        patterns = pattern.patterns if isinstance(pattern, ast.MatchOr) else [pattern]
        for p in patterns:
            # ast.MatchValue(value=Attribute(value=Name('FSMState'), attr='X'))
            if isinstance(p, ast.MatchValue) and isinstance(p.value, ast.Attribute):
                state_names.append(p.value.attr)
        # Find a `self._do_xxx(...)` call in the case body (terminal no-op cases have none).
        method_name = None
        for stmt in ast.walk(ast.Module(body=case.body, type_ignores=[])):
            if (isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Attribute)
                    and stmt.func.attr.startswith("_do_")):
                method_name = stmt.func.attr
                break
        for sn in state_names:
            if method_name:
                state_to_methods.setdefault(sn, []).append(method_name)

    for sn, extra_methods in _EXTRA_DISPATCH.items():
        state_to_methods.setdefault(sn, []).extend(extra_methods)

    edges: set[tuple[str, str]] = set()
    for from_state, method_names in state_to_methods.items():
        for method_name in method_names:
            fn = methods[method_name]
            for node in ast.walk(fn):
                if (isinstance(node, ast.Assign) and len(node.targets) == 1
                        and isinstance(node.targets[0], ast.Attribute) and node.targets[0].attr == "state"
                        and isinstance(node.value, ast.Attribute)
                        and isinstance(node.value.value, ast.Name) and node.value.value.id == "FSMState"):
                    edges.add((from_state, node.value.attr))
    return edges


_ROW_RE = re.compile(r"^\|\s*`([A-Z_]+)`\s*\|[^|]*\|\s*`([A-Z_]+)`\s*\|")


def _doc_edges() -> set[tuple[str, str]]:
    """Every (from_state, to_state) pair from §3's state-specific transition table.

    Rows whose `To` column isn't a backtick-quoted state name (e.g. "(persisted
    state)", "(suspended)") are skipped — they're not a concrete state edge.
    """
    text = DOC_PATH.read_text(encoding="utf-8")
    section = text.split("State-specific transitions:", 1)[1]
    edges = set()
    for line in section.splitlines():
        m = _ROW_RE.match(line.strip())
        if m:
            edges.add((m.group(1), m.group(2)))
    return edges


def test_every_code_edge_is_documented():
    code = _code_edges()
    doc = _doc_edges()
    undocumented = {(f, t) for (f, t) in code if t != "ESCALATION_FREEZE"} - doc
    assert not undocumented, (
        f"Transition(s) reachable in code but not documented in SESSION_FSM.md §3: "
        f"{sorted(undocumented)}"
    )


def test_every_documented_edge_is_reachable():
    code = _code_edges()
    doc = _doc_edges()
    dead = doc - code
    assert not dead, (
        f"Transition(s) documented in SESSION_FSM.md §3 but never reachable in code "
        f"(dead documentation): {sorted(dead)}"
    )


def test_parent_ack_wait_state_removed():
    """REVIEW §3.1: PARENT_ACK_WAIT was documented + in the enum but never
    actually reachable (parent_acknowledge() drives resume/end directly from
    ESCALATION_FREEZE). Regression guard: not in the enum, and not documented
    as a live state in §3's transition table (a historical removal note may
    still mention the name in prose — that's not drift, it's context)."""
    from mentar.dialogue.controller import FSMState
    assert not hasattr(FSMState, "PARENT_ACK_WAIT")
    doc_states = {s for edge in _doc_edges() for s in edge}
    assert "PARENT_ACK_WAIT" not in doc_states


if __name__ == "__main__":
    test_every_code_edge_is_documented()
    print("  ✓ test_every_code_edge_is_documented")
    test_every_documented_edge_is_reachable()
    print("  ✓ test_every_documented_edge_is_reachable")
    test_parent_ack_wait_state_removed()
    print("  ✓ test_parent_ack_wait_state_removed")
