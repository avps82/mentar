"""Jump-to-topic: a pinned session serves ONE chosen concept through the normal loop.

docs/design/topic_jump_and_practice.md. The load-bearing property: pinning changes
WHICH node feeds the FSM, never the loop -- verify, help, probes and the session
cap must all behave exactly as in a guided session.

    python3 -m pytest tests/dialogue/test_pinned_session.py
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController

PROMPTS = REPO / "prompts"

# Two-node chain: `advanced` is NOT reachable by guided selection until `basics`
# is mastered -- which is exactly the case pinning exists for.
_CURRICULUM = {
    "basics": {
        "label": "basics",
        "answer_type": "fraction",
        "checker": "fraction_equiv",
        "expected_answer": "1/3",
        "grounding": {},
        "prerequisites": [],
    },
    "advanced": {
        "label": "advanced",
        "answer_type": "fraction",
        "checker": "fraction_equiv",
        "expected_answer": "1/2",
        "grounding": {},
        "prerequisites": ["basics"],
    },
}


class _FakeStore:
    def __init__(self, mastery: dict | None = None):
        self._mastery = mastery or {}
        self.checkpoints: list[str] = []

    def get_skill_state(self, learner_id: str, node_id: str):
        v = self._mastery.get(node_id)
        return {"p_mastery": v} if v is not None else None

    def update_skill_state(self, learner_id: str, node_id: str, p: float):
        self._mastery[node_id] = p

    def update_session_checkpoint(self, session_id: str, checkpoint_json: str):
        self.checkpoints.append(checkpoint_json)


def _make(pinned=None, mastery=None, max_items=None, resume=None, store=None):
    return SessionController(
        llm_call=lambda msgs: "Think about the pieces.",
        prompt_dir=PROMPTS,
        grounding_cfg={},
        curriculum=_CURRICULUM,
        db_store=store if store is not None else _FakeStore(mastery),
        learner_id="test-learner",
        pinned_node=pinned,
        max_items=max_items,
        resume_checkpoint=resume,
    )


def test_pinned_session_serves_only_the_pinned_node():
    """Guided selection would serve `basics` (the only fringe node). Pinned on
    `advanced`, every question must come from `advanced` -- including after
    correct answers, when interleave would otherwise move on."""
    ctrl = _make(pinned="advanced")
    ctrl.step(None)
    assert ctrl._ctx.current_node_id == "advanced"
    for _ in range(4):
        ctrl.step("1/2")   # correct for `advanced`
        if ctrl._ctx.state in (FSMState.SESSION_END_COMPLETE, FSMState.SESSION_END_BY_LEARNER):
            break
        assert ctrl._ctx.current_node_id == "advanced", (
            "a pinned session drifted off its topic"
        )


def test_unpinned_control_case_serves_the_fringe_node():
    """The mutation guard for the test above: WITHOUT a pin, the same curriculum
    starts on `basics` -- proving the pinned test asserts a real difference."""
    ctrl = _make()
    ctrl.step(None)
    assert ctrl._ctx.current_node_id == "basics"


def test_probe_still_fires_in_a_pinned_session():
    """Probes come from _do_branch_decision, not node selection -- pinning must
    not lose understanding-checks. Correct answers push mastery past the probe
    threshold quickly, so a probe state must appear within a few items."""
    ctrl = _make(pinned="advanced", max_items=None)
    ctrl.step(None)
    saw_probe = False
    for _ in range(8):
        r = ctrl.step("1/2")
        if "PROBE" in r.state:
            saw_probe = True
            break
    assert saw_probe, "no probe fired in 8 correct pinned items"


def test_session_cap_ends_a_pinned_session_warmly():
    ctrl = _make(pinned="advanced", max_items=2)
    ctrl.step(None)
    last = None
    for _ in range(6):
        last = ctrl.step("1/2")
        if last.done:
            break
    assert last is not None and last.done
    assert last.state == FSMState.SESSION_END_COMPLETE.value


def test_checkpoint_roundtrip_keeps_the_pin_across_restart():
    """A server restart rebuilds the controller from the checkpoint. Without the
    pinned_node field the session silently converts to a guided one -- which the
    control case above shows would mean `basics`, not `advanced`."""
    store = _FakeStore()
    ctrl = _make(pinned="advanced", store=store)
    ctrl.step(None)
    ctrl.step("1/2")
    assert store.checkpoints, "precondition: a checkpoint was written"
    cp = json.loads(store.checkpoints[-1])
    assert cp.get("pinned_node") == "advanced"

    resumed = _make(resume=cp, store=_FakeStore())   # NO constructor pin
    resumed.step(None)
    assert resumed._ctx.current_node_id == "advanced", (
        "restart converted a pinned session into a guided one"
    )


def test_stale_checkpoint_pin_degrades_to_guided():
    """A checkpointed pin naming a node this curriculum no longer has is dropped,
    same safe-degrade as a stale current_node_id."""
    cp = {"current_node_id": None, "pinned_node": "gone_node",
          "items_completed": 0, "items_since_probe": 0, "turn_index": 0}
    ctrl = _make(resume=cp)
    ctrl.step(None)
    assert ctrl._ctx.current_node_id == "basics"


def test_unknown_pinned_node_raises_at_construction():
    with pytest.raises(ValueError, match="not a concept"):
        _make(pinned="no_such_node")


def test_escalation_freezes_a_pinned_session():
    """The forbidden-shortcut guard: the pinned session runs the SAME turn path,
    so a disclosure must freeze exactly as in a guided session."""
    ctrl = _make(pinned="advanced")
    ctrl.step(None)
    r = ctrl.step("i want to kill myself")
    assert r.escalated
    assert ctrl._ctx.state is FSMState.ESCALATION_FREEZE
