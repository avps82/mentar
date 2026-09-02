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

    def update_skill_state(self, learner_id, node_id, p, **kw):
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

    ctrl.step(None)          # R11: first pick among equal fringe nodes is rng-based —
    helped = ctx.current_node_id      # capture whichever node was presented
    unhelped = "node_b" if helped == "node_a" else "node_a"
    ctrl.step("?")           # child-initiated help -> help_by_node[helped] = True
    ctx.mastery[helped] = 0.9     # simulate the helped node at the probe threshold
    ctrl.step("2")           # correct hinted recheck -> BRANCH_DECISION -> probe fires
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value
    ctrl.step("999")  # readable-but-wrong (E2.4: unreadable input now re-prompts)       # first probe attempt wrong; help_pressed=True suppresses
                             # false_confidence -> slip_suspect -> ONE retry granted
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value  # confirms the retry, not NODE_SELECT
    ctrl.step("999")  # readable-but-wrong (E2.4: unreadable input now re-prompts)       # retry also wrong -> logs slip_suspect, demotes, advances

    # Force the node switch directly (NODE_SELECT's re-pick among the demoted
    # helped node and the fresh one is orthogonal to what this test exercises).
    ctx.current_node_id = unhelped
    ctx.mastery[unhelped] = 0.9
    ctx.state = FSMState.PATTERN_SELECT
    result = ctrl.step(None)  # drives PATTERN_SELECT -> PRESENT -> the unhelped node's Q
    assert ctx.current_node_id == unhelped
    assert _ITEMS[unhelped].problem in result.text

    ctrl.step("2")            # unhelped node answered correctly, unaided -> probe fires (mastery 0.9)
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value
    ctrl.step("999")           # first probe wrong. Since 2026-08-16 EVERY first
                               # failure gets the retry (SPEC §14), whatever the
                               # provisional class -- this used to classify
                               # false_confidence on one wrong answer.
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value, "first failure must be retried"
    ctrl.step("999")           # retry wrong too -> slip ruled out -> false_confidence

    classes = dict(store.probe_events)
    assert classes.get(helped) == "slip_suspect", (
        f"{helped} (help pressed) must not classify false_confidence: {store.probe_events}"
    )
    assert classes.get(unhelped) == "false_confidence", (
        f"{unhelped} (help never pressed) should classify false_confidence: {store.probe_events}"
    )


def test_auto_help_alone_still_classifies_false_confidence():
    """The system's own auto-help (triggered by a wrong UNAIDED answer, in
    _do_bkt_update) must NOT set help_by_node — only a child-INITIATED help
    request should. A node that only ever saw auto-help, with mastery at
    threshold, must still classify false_confidence on a failed probe."""
    store = _ColdStartStore()
    ctrl = _ctrl(store)
    ctx = ctrl._ctx

    ctrl.step(None)           # presents whichever node the R11 policy picked first
    node = ctx.current_node_id
    ctrl.step("999")  # readable-but-wrong (E2.4: unreadable input now re-prompts)        # WRONG unaided answer -> auto-help scaffolding kicks in
                              # (help_modalities_used reset, but help_by_node NOT set)
    assert not ctx.help_by_node.get(node), (
        "auto-help must not set help_by_node — only a child-initiated request should"
    )
    ctx.mastery[node] = 0.9
    ctrl.step("2")            # correct hinted recheck -> BRANCH_DECISION -> probe fires
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value
    ctrl.step("999")           # first probe wrong -> retry granted (SPEC §14: exactly
                               # one retry on a first failure, whatever the class)
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value, "first failure must be retried"
    ctrl.step("999")           # retry wrong too, help_pressed=False (auto-help does
                               # not count) -> false_confidence

    classes = dict(store.probe_events)
    assert classes.get(node) == "false_confidence", (
        f"auto-help-only node at threshold must still classify false_confidence: "
        f"{store.probe_events}"
    )


# ── SPEC §14: exactly one retry on a FIRST probe failure ────────────────────
# Lives here because this module already builds a two-node controller over the
# real FSM. Until 2026-08-16 the retry was granted only when the provisional
# class was slip_suspect, so the two SERIOUS classes skipped it -- the inverse
# of the spec, which asserts them "only when slip is ruled out (both variants
# failed)". The false_confidence half is covered by the two tests above; this
# covers forgetting_suspect, which nothing exercised.

def test_stale_mastery_first_failure_is_retried_before_forgetting_is_asserted():
    store = _ColdStartStore()
    ctrl = _ctrl(store)
    ctx = ctrl._ctx

    ctrl.step(None)
    node = ctx.current_node_id
    ctx.mastery[node] = 0.9
    ctrl.step("2")                       # correct -> probe fires
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value
    # Set the stale clock AFTER the answer: the BKT update refreshes
    # mastery_updated_at (R11's in-session staleness reset), so setting it
    # earlier is silently undone before the probe is classified.
    ctx.mastery_updated_at[node] = "2020-01-01T00:00:00Z"   # far outside the window

    before = ctx.mastery[node]
    ctrl.step("999")                     # FIRST probe failure
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value, (
        "a stale-mastery first failure must still get its retry, not be classified"
    )
    assert store.probe_events == [], "no probe_event may be written before the retry"
    assert ctx.mastery[node] == before, "mastery must not be demoted on one failure"

    ctrl.step("999")                     # retry also fails -> slip ruled out
    assert dict(store.probe_events).get(node) == "forgetting_suspect", store.probe_events
    assert ctx.mastery[node] < before, "both variants failed -> demote"


def test_recovering_on_the_retry_is_a_slip_not_a_forgetting_signal():
    """The retry has to be able to change the verdict, or granting it is theatre."""
    store = _ColdStartStore()
    ctrl = _ctrl(store)
    ctx = ctrl._ctx

    ctrl.step(None)
    node = ctx.current_node_id
    ctx.mastery[node] = 0.9
    ctrl.step("2")
    ctx.mastery_updated_at[node] = "2020-01-01T00:00:00Z"   # see note above
    ctrl.step("999")                     # first probe wrong
    assert ctrl.state == FSMState.PROBE_AWAIT_ANSWER.value
    ctrl.step("2")                       # recovered on the retry

    assert dict(store.probe_events).get(node) == "slip_suspect", store.probe_events


if __name__ == "__main__":
    test_help_on_one_node_does_not_leak_to_another()
    print("  ✓ test_help_on_one_node_does_not_leak_to_another")
    test_auto_help_alone_still_classifies_false_confidence()
    print("  ✓ test_auto_help_alone_still_classifies_false_confidence")
