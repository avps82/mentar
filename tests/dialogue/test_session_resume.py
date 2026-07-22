"""R-RES — session resume across a server-process restart.

A fresh SessionController instance simulates "the process restarted" — the
in-memory controller from before is gone, and a new one is constructed with
an optional `resume_checkpoint` (what a real caller would load from the DB's
`session.checkpoint_state` column via `store.get_open_session`).

Covers:
  - no checkpoint -> unchanged behaviour (NODE_SELECT)
  - checkpoint says frozen -> ESCALATION_FREEZE, unconditionally, absorbing
  - checkpoint names a valid unmastered node -> PATTERN_SELECT onto that SAME
    node, seeded items_completed/items_since_probe, fresh item presented
  - checkpoint names a node that's since been mastered -> degrades to NODE_SELECT
  - checkpoint names a node missing from the curriculum (wrong subject / template
    changed) -> degrades to NODE_SELECT
  - the per-turn checkpoint write itself: step() persists current_node_id/frozen/
    counters via the store adapter
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController
from mentar.engine.fringe import DEFAULT_MASTERY_THRESHOLD

PROMPTS = REPO / "prompts"

_TWO_NODE_CURRICULUM = {
    "alpha": {
        "label": "alpha", "answer_type": "int", "checker": "int_exact",
        "expected_answer": "5", "grounding": {}, "prerequisites": [],
    },
    "beta": {
        "label": "beta", "answer_type": "int", "checker": "int_exact",
        "expected_answer": "5", "grounding": {}, "prerequisites": [],
    },
}


class _FakeStore:
    """Minimal in-memory store stub that also records checkpoint writes."""

    def __init__(self, mastery: dict | None = None):
        self._mastery = mastery or {}
        self.checkpoints: list[tuple[str, str]] = []  # (session_id, json_str)

    def get_skill_state(self, learner_id, node_id):
        v = self._mastery.get(node_id)
        return {"p_mastery": v} if v is not None else None

    def update_skill_state(self, learner_id, node_id, p):
        self._mastery[node_id] = p

    def update_session_checkpoint(self, session_id, checkpoint_json):
        self.checkpoints.append((session_id, checkpoint_json))

    def write_escalation(self, learner_id, trigger_class, trigger_text_verbatim, **kwargs):
        return 1

    def max_turn_index_for_session(self, session_id):
        return -1  # no transcript rows in the fake store


def _make_controller(mastery=None, resume_checkpoint=None, session_id=None, curriculum=None):
    return SessionController(
        llm_call=lambda msgs: "6",
        prompt_dir=PROMPTS,
        grounding_cfg={},
        curriculum=curriculum or _TWO_NODE_CURRICULUM,
        db_store=_FakeStore(mastery),
        learner_id="test-learner",
        session_id=session_id,
        resume_checkpoint=resume_checkpoint,
    )


def test_no_checkpoint_behaves_exactly_as_before():
    ctrl = _make_controller(resume_checkpoint=None)
    result = ctrl.step(None)
    assert result.state == FSMState.AWAIT_ANSWER.value
    assert not result.escalated


def test_frozen_checkpoint_resumes_frozen_unconditionally():
    ctrl = _make_controller(resume_checkpoint={"frozen": True, "current_node_id": "alpha"})
    result = ctrl.step(None)
    assert ctrl.state == FSMState.ESCALATION_FREEZE.value
    assert result.escalated
    assert not result.done
    # Absorbing: even a normal child message can't lift it -- only parent_acknowledge().
    result2 = ctrl.step("hello")
    assert ctrl.state == FSMState.ESCALATION_FREEZE.value
    assert result2.escalated


def test_frozen_checkpoint_ignores_mastery_and_node_validity():
    """The frozen branch is unconditional -- it must not fall through to the
    node-validity check even if current_node_id is garbage."""
    ctrl = _make_controller(resume_checkpoint={"frozen": True, "current_node_id": "not_a_real_node"})
    ctrl.step(None)
    assert ctrl.state == FSMState.ESCALATION_FREEZE.value


def test_valid_node_checkpoint_resumes_same_topic_fresh_question():
    ctrl = _make_controller(resume_checkpoint={
        "frozen": False, "current_node_id": "beta",
        "items_completed": 3, "items_since_probe": 2,
    })
    result = ctrl.step(None)
    assert ctrl.current_node_id == "beta"                  # same topic
    assert result.state == FSMState.AWAIT_ANSWER.value      # fresh question presented
    assert ctrl._ctx.items_completed == 3                   # counters seeded
    assert ctrl._ctx.items_since_probe == 2


def test_mastered_node_checkpoint_degrades_to_node_select():
    """If the checkpointed node was mastered since the checkpoint was written
    (e.g. via another channel), forcing it back onto screen would be wrong --
    falls through to normal fringe selection instead."""
    ctrl = _make_controller(
        mastery={"alpha": DEFAULT_MASTERY_THRESHOLD + 0.01},
        resume_checkpoint={"frozen": False, "current_node_id": "alpha"},
    )
    ctrl.step(None)
    # alpha is mastered -> normal NODE_SELECT picks the only remaining fringe node.
    assert ctrl.current_node_id == "beta"


def test_missing_node_checkpoint_degrades_to_node_select():
    """A checkpoint naming a node absent from THIS curriculum (wrong subject,
    or the template changed) must never raise or get force-selected -- safe
    degrade to whatever normal NODE_SELECT would have picked anyway."""
    ctrl = _make_controller(resume_checkpoint={
        "frozen": False, "current_node_id": "some_other_subjects_node",
    })
    result = ctrl.step(None)
    assert result.state == FSMState.AWAIT_ANSWER.value
    assert ctrl.current_node_id in _TWO_NODE_CURRICULUM


def test_step_writes_a_checkpoint_every_turn():
    ctrl = _make_controller(session_id="sess-checkpoint-test")
    ctrl.step(None)
    store = ctrl._store
    assert store.checkpoints, "expected at least one checkpoint write"
    session_id, payload = store.checkpoints[-1]
    assert session_id == "sess-checkpoint-test"
    data = json.loads(payload)
    assert data["current_node_id"] in _TWO_NODE_CURRICULUM
    assert data["frozen"] is False
    assert isinstance(data["items_completed"], int)
    assert isinstance(data["items_since_probe"], int)


def test_step_checkpoint_reflects_frozen_state():
    ctrl = _make_controller(session_id="sess-freeze-checkpoint")
    ctrl.step(None)
    ctrl.step("I want to die")  # distress -> freeze (same phrase as test_escalation_resume.py)
    assert ctrl.state == FSMState.ESCALATION_FREEZE.value
    session_id, payload = ctrl._store.checkpoints[-1]
    assert json.loads(payload)["frozen"] is True
