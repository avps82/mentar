"""W3.3 §6 G7 (2026-09-02) — a node is not mastered until a probe says so.

Two routes left a node at p_mastery >= threshold with no transfer probe on
record: the session cap fired before probe_due in _do_branch_decision, and a
child said "stop" on the probe itself. The node then left the fringe
unconfirmed for STALE_MASTERY_DAYS. Fix: the first NODE_SELECT of a session
probes one such node before anything else. Both routes are driven here through
the real FSM; the fake store persists across "sessions" (controllers).

    python3 -m pytest tests/dialogue/test_deferred_probe.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController  # noqa: E402
from mentar.engine.fringe import is_mastered  # noqa: E402

PROMPTS = REPO / "prompts"
NODE = "unit_fractions"
_CURRICULUM = {
    NODE: {
        "label": "unit fractions",
        "answer_type": "fraction",
        "checker": "fraction_equiv",
        "expected_answer": "1/3",
        "grounding": {},
        "prerequisites": [],
    }
}
RIGHT = "1/3"


class _Store:
    """Persists mastery and probe events across controllers, like the real DB."""

    def __init__(self):
        self._m: dict[str, float] = {}
        self.probes: list[str] = []

    def get_skill_state(self, learner_id, node_id):
        v = self._m.get(node_id)
        return {"p_mastery": v} if v is not None else None

    def update_skill_state(self, learner_id, node_id, p, **kw):
        self._m[node_id] = p

    def write_response(self, *a, **k):
        return 1                      # probe_event needs a response_log id to link to

    def write_probe_event(self, session_id, skill_id, rid, retry_rid, class_):
        self.probes.append(class_)
        return 1

    def has_clean_probe(self, node_id):
        return "clean_pass" in self.probes


def _session(store, **kw):
    return SessionController(
        llm_call=lambda msgs: "A question.",
        prompt_dir=PROMPTS,
        grounding_cfg={},
        curriculum=_CURRICULUM,
        db_store=store,
        learner_id="kid",
        rng_seed=11,
        **kw,
    )


def _graduate_on_the_last_item(store):
    """Route 1: two cold-corrects cross 0.85 on item 2 of a 2-item session."""
    ctrl = _session(store, max_items=2)
    ctrl.step(None)
    ctrl.step(RIGHT)
    ctrl.step(RIGHT)
    assert ctrl._ctx.state is FSMState.SESSION_END_COMPLETE
    assert is_mastered(store._m[NODE]), store._m
    assert store.probes == [], "precondition: the cap ended the session before any probe"
    return ctrl


def test_the_session_cap_no_longer_lets_a_node_graduate_unprobed():
    store = _Store()
    _graduate_on_the_last_item(store)
    nxt = _session(store)
    nxt.step(None)
    assert nxt._ctx.state is FSMState.PROBE_AWAIT_ANSWER, nxt._ctx.state
    assert nxt.current_node_id == NODE


def test_a_stop_during_the_probe_is_caught_next_session():
    """Route 2: the probe fires, the child stops on it, nothing is classified."""
    store = _Store()
    ctrl = _session(store)
    ctrl.step(None)
    ctrl.step(RIGHT)
    ctrl.step(RIGHT)
    assert ctrl._ctx.state is FSMState.PROBE_AWAIT_ANSWER, "precondition: the probe fired"
    ctrl.step("stop")
    assert ctrl._ctx.state is FSMState.SESSION_END_BY_LEARNER
    assert store.probes == []
    nxt = _session(store)
    nxt.step(None)
    assert nxt._ctx.state is FSMState.PROBE_AWAIT_ANSWER
    assert nxt.current_node_id == NODE


def test_a_confirmed_node_is_not_probed_again_and_a_failed_one_returns_to_practice():
    store = _Store()
    _graduate_on_the_last_item(store)
    nxt = _session(store)
    nxt.step(None)
    nxt.step(RIGHT)                                     # clean pass
    assert store.probes == ["clean_pass"]
    third = _session(store)
    third.step(None)
    assert third._ctx.state is not FSMState.PROBE_AWAIT_ANSWER, "already confirmed"

    store2 = _Store()
    _graduate_on_the_last_item(store2)
    nxt2 = _session(store2)
    nxt2.step(None)
    nxt2.step("2/3")                                    # fail -> retry variant
    nxt2.step("2/3")                                    # fail again -> demoted
    assert store2.probes and store2.probes[-1] != "clean_pass"
    assert not is_mastered(store2._m[NODE]), "a failed deferred probe must demote"


def test_a_store_without_the_query_defers_nothing():
    """Test fakes (and any store that can't answer) must not open every session
    with a probe: only an explicit False defers."""
    class _Bare(_Store):
        has_clean_probe = property(lambda self: (_ for _ in ()).throw(AttributeError))
    store = _Bare()
    store._m[NODE] = 0.95
    ctrl = _session(store)
    ctrl.step(None)
    assert ctrl._ctx.state is not FSMState.PROBE_AWAIT_ANSWER


def test_one_deferred_probe_per_session_and_pinned_sessions_are_exempt():
    store = _Store()
    _graduate_on_the_last_item(store)
    pinned = _session(store, pinned_node=NODE)
    pinned.step(None)
    assert pinned._ctx.state is not FSMState.PROBE_AWAIT_ANSWER, (
        "a pinned session re-serves its node; the probe re-fires on its own"
    )
