"""A5 — per-node, child-initiated help_pressed for probe classification.

Regression guard: help_pressed used to be `len(ctx.help_modalities_used) > 0`,
which (a) stayed set from a PREVIOUS node's help use (stale-across-nodes) and
(b) was also set by the system's own auto-help on a wrong unaided answer, not
just child-initiated help. Both pollute the false-confidence probe signal.

This drives two independent-mastery nodes through the real FSM: help is
pressed only on node_a; node_b gets a wrong probe with NO help ever pressed on
it. node_a's probe failure must NOT classify false_confidence (help WAS
pressed there); node_b's must (help was never pressed, mastery is high).

Inline smoke runner:
    python3 tests/dialogue/test_probe_help_pressed.py
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController
from mentar.engine.itembank import Item

PROMPTS = REPO / "prompts"
_CURRICULUM = {
    "node_a": {
        "label": "node a", "answer_type": "int", "checker": "int_exact",
        "expected_answer": "2", "grounding": {}, "prerequisites": [],
    },
    "node_b": {
        "label": "node b", "answer_type": "int", "checker": "int_exact",
        "expected_answer": "2", "grounding": {}, "prerequisites": [],
    },
}

_ITEMS = {
    "node_a": Item(id="a1", node="node_a", problem="Q_A", answer="2",
                   answer_type="int", checker="int_exact"),
    "node_b": Item(id="b1", node="node_b", problem="Q_B", answer="2",
                   answer_type="int", checker="int_exact"),
}


class _PerNodeBank:
    def has(self, node_id):
        return True

    def sample(self, node_id):
        return _ITEMS[node_id]

    def example(self, node_id, exclude_id=None):
        return _ITEMS[node_id]


class _ColdStartStore:
    """Cold-start mastery (P_L0) for every node — the test pokes ctx.mastery
    directly to simulate a node reaching the probe threshold, since a node
    already >= threshold at session start is excluded from the fringe entirely
    (never selected/presented) and so could never naturally reach a probe."""

    def __init__(self):
        self.probe_events: list[tuple[str, str]] = []  # (skill_id, class_)
        self._next_id = 1

    def get_skill_state(self, learner_id, node_id):
        return None

    def update_skill_state(self, learner_id, node_id, p):
        pass

    def write_response(self, session_id, skill_id, prompt_ref, answer, scored, hinted, check_result):
        rid = self._next_id
        self._next_id += 1
        return rid

    def write_probe_event(self, session_id, skill_id, response_log_id, retry_response_log_id, class_):
        self.probe_events.append((skill_id, class_))
        return len(self.probe_events)


def _ctrl(store):
    return SessionController(
        llm_call=lambda m: "probe question?", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=store, learner_id="L1", item_bank=_PerNodeBank(),
    )


def test_help_on_one_node_does_not_leak_to_another():
    """node_a: help pressed, mastery poked to threshold -> a failed probe must
    classify slip_suspect (retried once), NOT false_confidence. Then move to
    node_b (ctx.mastery/current_node_id set directly — sidesteps NODE_SELECT's
    alphabetical fringe re-pick, which is orthogonal to what A5 changed): no
    help ever pressed there -> the SAME kind of failed probe MUST classify
    false_confidence. Proves help_by_node is per-node, not a leftover flag."""
    store = _ColdStartStore()
    ctrl = _ctrl(store)
    ctx = ctrl._ctx

    ctrl.step(None)          # fringe={node_a, node_b}, alphabetical -> node_a presented
    assert ctx.current_node_id == "node_a"
    ctrl.step("?")           # child-initiated help -> help_by_node["node_a"] = True
    ctx.mastery["node_a"] = 0.9   # simulate node_a at the probe threshold
    ctrl.step("2")           # correct hinted recheck -> BRANCH_DECISION -> probe fires
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value
    ctrl.step("wrong")       # first probe attempt wrong; help_pressed=True suppresses
                             # false_confidence -> slip_suspect -> ONE retry granted
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value  # confirms the retry, not NODE_SELECT
    ctrl.step("wrong")       # retry also wrong -> logs slip_suspect, demotes, advances

    # Force the node switch directly (NODE_SELECT would otherwise re-pick node_a,
    # since it's alphabetically first and demoted back below threshold — not
    # what this test is exercising).
    ctx.current_node_id = "node_b"
    ctx.mastery["node_b"] = 0.9
    ctx.state = FSMState.PATTERN_SELECT
    result = ctrl.step(None)  # drives PATTERN_SELECT -> PRESENT -> node_b's Q_B
    assert ctx.current_node_id == "node_b"
    assert "Q_B" in result.text

    ctrl.step("2")            # node_b answered correctly, unaided -> probe fires (mastery 0.9)
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value
    ctrl.step("wrong")        # node_b's probe wrong, help NEVER pressed on node_b ->
                              # false_confidence immediately (no retry, since help_pressed=False)

    classes = dict(store.probe_events)
    assert classes.get("node_a") == "slip_suspect", (
        f"node_a (help pressed) must not classify false_confidence: {store.probe_events}"
    )
    assert classes.get("node_b") == "false_confidence", (
        f"node_b (help never pressed) should classify false_confidence: {store.probe_events}"
    )


def test_auto_help_alone_still_classifies_false_confidence():
    """The system's own auto-help (triggered by a wrong UNAIDED answer, in
    _do_bkt_update) must NOT set help_by_node — only a child-INITIATED help
    request should. A node that only ever saw auto-help, with mastery at
    threshold, must still classify false_confidence on a failed probe."""
    store = _ColdStartStore()
    ctrl = _ctrl(store)
    ctx = ctrl._ctx

    ctrl.step(None)           # presents node_a
    ctrl.step("wrong")        # WRONG unaided answer -> auto-help scaffolding kicks in
                              # (help_modalities_used reset, but help_by_node NOT set)
    assert not ctx.help_by_node.get("node_a"), (
        "auto-help must not set help_by_node — only a child-initiated request should"
    )
    ctx.mastery["node_a"] = 0.9
    ctrl.step("2")            # correct hinted recheck -> BRANCH_DECISION -> probe fires
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value
    ctrl.step("wrong")        # failed probe, help_pressed=False (auto-help doesn't count) ->
                              # false_confidence immediately

    classes = dict(store.probe_events)
    assert classes.get("node_a") == "false_confidence", (
        f"auto-help-only node at threshold must still classify false_confidence: "
        f"{store.probe_events}"
    )


if __name__ == "__main__":
    test_help_on_one_node_does_not_leak_to_another()
    print("  ✓ test_help_on_one_node_does_not_leak_to_another")
    test_auto_help_alone_still_classifies_false_confidence()
    print("  ✓ test_auto_help_alone_still_classifies_false_confidence")
