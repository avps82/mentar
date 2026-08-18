"""CONCERN tier behaviour through the controller (2026-08-18, maintainer-authorised).

The classifier side is tests/safety/test_escalation_tiers.py; this file proves
what the SESSION does with a CONCERN: logged + lesson continues, threshold
freeze, checkpoint survival.

    python3 -m pytest tests/dialogue/test_concern_tier.py
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import (
    CONCERN_FREEZE_THRESHOLD,
    FSMState,
    SessionController,
)

PROMPTS = REPO / "prompts"

_CURRICULUM = {
    "unit_fractions": {
        "label": "unit fractions",
        "answer_type": "fraction",
        "checker": "fraction_equiv",
        "expected_answer": "1/3",
        "grounding": {},
        "prerequisites": [],
    }
}

# A phrasing the classifier maps to CONCERN (pinned in test_escalation_tiers.py).
CONCERN_TEXT = "i'm scared to go home"


class _FakeStore:
    def __init__(self):
        self._mastery = {}
        self.escalations: list[dict] = []
        self.checkpoints: list[str] = []

    def get_skill_state(self, learner_id, node_id):
        v = self._mastery.get(node_id)
        return {"p_mastery": v} if v is not None else None

    def update_skill_state(self, learner_id, node_id, p):
        self._mastery[node_id] = p

    def write_escalation(self, learner_id, trigger_class, text, **kw):
        self.escalations.append({"class": trigger_class, "text": text, **kw})
        return len(self.escalations)

    def update_session_checkpoint(self, session_id, cp):
        self.checkpoints.append(cp)


def _make(store=None, resume=None):
    return SessionController(
        llm_call=lambda msgs: "Think about the pieces.",
        prompt_dir=PROMPTS,
        grounding_cfg={},
        curriculum=_CURRICULUM,
        db_store=store if store is not None else _FakeStore(),
        learner_id="test-learner",
        resume_checkpoint=resume,
    )


def test_one_concern_logs_and_the_lesson_continues():
    """The whole point of the tier: the child sees a NORMAL turn — no freeze, no
    handoff message — while the parent record is written."""
    store = _FakeStore()
    ctrl = _make(store)
    ctrl.step(None)
    r = ctrl.step(CONCERN_TEXT)

    assert ctrl._ctx.state is not FSMState.ESCALATION_FREEZE, "one concern must not freeze"
    assert not r.escalated
    assert "grown-up" not in (r.text or ""), "the child must not see handoff wording"
    assert len(store.escalations) == 1
    row = store.escalations[0]
    assert row["severity"] == "concern"
    assert row["session_outcome"] == "logged_concern"
    assert row["text"] == CONCERN_TEXT, "verbatim, untruncated"


def test_the_threshold_th_concern_freezes():
    """Multi-turn distress: no single line alarming, the accumulation is."""
    store = _FakeStore()
    ctrl = _make(store)
    ctrl.step(None)
    for _ in range(CONCERN_FREEZE_THRESHOLD):
        r = ctrl.step(CONCERN_TEXT)
    assert ctrl._ctx.state is FSMState.ESCALATION_FREEZE
    assert r.escalated
    # The freezing row records the frozen outcome; the earlier one stays a note.
    assert store.escalations[-1]["session_outcome"] == "frozen"
    assert store.escalations[0]["session_outcome"] == "logged_concern"


def test_critical_still_freezes_on_the_first_hit():
    """The tier must not have inserted itself in front of CRITICAL."""
    ctrl = _make()
    ctrl.step(None)
    r = ctrl.step("i want to kill myself")
    assert r.escalated
    assert ctrl._ctx.state is FSMState.ESCALATION_FREEZE


def test_concern_count_survives_a_restart():
    """One concern, restart, one more concern -> freeze. Without the checkpoint
    field the count resets and the threshold quietly never fires."""
    store = _FakeStore()
    ctrl = _make(store)
    ctrl.step(None)
    ctrl.step(CONCERN_TEXT)
    ctrl.step("1/3")                      # a normal turn so a checkpoint is written
    cp = json.loads(store.checkpoints[-1])
    assert cp.get("concern_hits") == 1

    resumed = _make(_FakeStore(), resume=cp)
    resumed.step(None)
    r = resumed.step(CONCERN_TEXT)
    assert resumed._ctx.state is FSMState.ESCALATION_FREEZE, (
        "restart reset the concern count -- accumulation must survive"
    )
    assert r.escalated
