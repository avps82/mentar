"""Task 1.1 — durable DB logging is wired (transcript / response / help / probe).

Regression guard for the gap found 2026-06-24: `write_response`, `write_transcript`,
`write_help_event`, `write_probe_event` existed in the store but had ZERO callers, so
sessions persisted nothing but escalations + mastery. Here we drive a scripted session
through the real `SessionController` + `_DbStoreAdapter` + a real SQLite `LearnerStore`
and assert every per-session table is populated.

Inline smoke runner + pytest fns (project convention): `python3 tests/dialogue/test_db_logging.py`.
"""
from __future__ import annotations

import uuid
from pathlib import Path

from mentar.db.adapter import _DbStoreAdapter
from mentar.db.store import LearnerStore
from mentar.dialogue.controller import SessionController
from mentar.engine.itembank import Item

_REPO = Path(__file__).resolve().parents[2]
_PROMPTS = _REPO / "prompts"

# One deterministic checkable item, reused for every node: "1+1?" -> "2".
_ITEM = Item(
    id="it1", node="n1", problem="What is 1+1?", answer="2",
    answer_type="int", checker="int_exact",
)


class _FixedBank:
    """Minimal item source duck-typing ItemBank: every node gets the same int item."""

    def has(self, node_id: str) -> bool:
        return True

    def sample(self, node_id: str) -> Item:
        return _ITEM

    def example(self, node_id: str, exclude_id: str | None = None) -> Item:
        return _ITEM


def _fake_llm(messages: list[dict]) -> str:
    # Only ever called for Help explanations (questions come from the item bank).
    return "Think of it like sharing a pizza — that's a helpful hint."


def _curriculum() -> dict:
    # 4 independent nodes so the fringe never empties during the script (no early
    # SESSION_END_COMPLETE), letting the probe cadence (every 5 items) fire.
    nodes = {}
    for i in range(1, 5):
        nodes[f"n{i}"] = {
            "label": f"node {i}",
            "answer_type": "int",
            "checker": "int_exact",
            "expected_answer": "2",
            "grounding": {},
            "prerequisites": [],
        }
    return nodes


def _build(tmp_path: Path):
    store = LearnerStore(tmp_path / "logging.db")
    db_id = store.create_learner("Tess", "pilot", "GB", "parent_mediated")
    ctrl = SessionController(
        llm_call=_fake_llm,
        prompt_dir=_PROMPTS,
        grounding_cfg={},
        curriculum=_curriculum(),
        db_store=_DbStoreAdapter(store, db_id),
        learner_id="learner-" + uuid.uuid4().hex[:8],
        item_bank=_FixedBank(),
    )
    return store, db_id, ctrl


def _drive(ctrl) -> None:
    """A deterministic session: first turn, one Help round, then enough correct
    answers to trigger at least one probe (cadence = every 5 items)."""
    ctrl.step(None)          # present first item (state AWAIT_ANSWER)
    ctrl.step("?")           # request Help -> modality explanation + recheck question
    ctrl.step("2")           # answer the Help recheck correctly -> help_event + hinted response
    for _ in range(12):      # correct answers; absorbs probe present/answer cycles
        ctrl.step("2")


def run_smoke(tmp_path: Path) -> None:
    store, db_id, ctrl = _build(tmp_path)
    sid = ctrl._session_id
    _drive(ctrl)

    # session row exists
    assert store.get_session(db_id, sid) is not None, "no session row created"

    # transcript: both roles, ordered, populated
    tr = store.transcript_for_session(db_id, sid)
    roles = {t["role"] for t in tr}
    assert {"learner", "tutor"} <= roles, f"transcript roles incomplete: {roles}"
    assert [t["turn_index"] for t in tr] == sorted(t["turn_index"] for t in tr)

    # response_log: scored answers persisted, incl. the hinted Help recheck + a check_result
    resp = store.session_responses(db_id, sid)
    assert len(resp) >= 3, f"too few responses logged: {len(resp)}"
    assert any(r["hinted"] == 1 for r in resp), "no hinted (Help) response logged"
    assert all(r["check_result"] for r in resp), "check_result not persisted"

    # help_event + probe_event populated and FK-linked
    helps = store.session_help_events(db_id, sid)
    assert len(helps) >= 1, "no help_event logged"
    probes = store.session_probe_events(db_id, sid)
    assert len(probes) >= 1, "no probe_event logged"
    resp_ids = {r["id"] for r in resp}
    assert all(h["response_log_id"] in resp_ids for h in helps), "help_event FK dangling"
    assert all(p["response_log_id"] in resp_ids for p in probes), "probe_event FK dangling"

    store.close()


# ── pytest entry points ────────────────────────────────────────────────────────

def test_session_logging_populates_all_tables(tmp_path):
    run_smoke(tmp_path)


def test_logging_is_best_effort_without_store_methods(tmp_path):
    """A store missing the new methods must not break the turn loop (fake-store compat)."""

    class _BareStore:
        def __init__(self):
            self._m = {}

        def get_skill_state(self, learner_id, node_id):
            return None

        def update_skill_state(self, learner_id, node_id, p):
            self._m[node_id] = p

    ctrl = SessionController(
        llm_call=_fake_llm,
        prompt_dir=_PROMPTS,
        grounding_cfg={},
        curriculum=_curriculum(),
        db_store=_BareStore(),
        learner_id="x",
        item_bank=_FixedBank(),
    )
    # Should run cleanly despite the store implementing none of the logging methods.
    ctrl.step(None)
    r = ctrl.step("2")
    assert r is not None


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        run_smoke(Path(d))
    print("OK: db logging smoke passed")
