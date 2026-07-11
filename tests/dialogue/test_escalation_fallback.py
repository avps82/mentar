"""A15 — escalation-log fallback sink.

Regression guard: write_escalation failures used to be swallowed by a bare
`except Exception: logger.warning(...)`, meaning a genuine DB outage could
silently drop a distress disclosure (SAFETY §3.1: never silently dropped).
Now a failed write also appends one JSON line to escalation_fallback.log next
to the DB file, so the parent can still recover it.

Inline smoke runner:
    python3 tests/dialogue/test_escalation_fallback.py
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import FSMState, SessionController

PROMPTS = REPO / "prompts"
_CURRICULUM = {
    "unit_fractions": {
        "label": "unit fractions", "answer_type": "fraction", "checker": "fraction_equiv",
        "expected_answer": "1/3", "grounding": {}, "prerequisites": [],
    }
}


class _RaisingStore:
    """db_path is present (so the fallback sink can find a place to write) but
    write_escalation always raises, simulating a DB outage."""

    def __init__(self, db_path):
        self.db_path = db_path

    def get_skill_state(self, learner_id, node_id):
        return None

    def update_skill_state(self, learner_id, node_id, p):
        pass

    def write_escalation(self, *args, **kwargs):
        raise RuntimeError("simulated DB outage")


class _WorkingStore(_RaisingStore):
    def write_escalation(self, *args, **kwargs):
        return 1


def _ctrl(store):
    return SessionController(
        llm_call=lambda m: "ok", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=store, learner_id="L",
    )


def test_db_failure_still_freezes_and_writes_fallback(tmp_path):
    db_path = tmp_path / "mentar.db"
    store = _RaisingStore(db_path)
    ctrl = _ctrl(store)
    ctrl.step(None)
    text = "I want to hurt myself"
    r = ctrl.step(text)

    # Freeze behaviour is unchanged by the DB failure.
    assert r.escalated is True
    assert ctrl.state == FSMState.ESCALATION_FREEZE.value

    fallback = tmp_path / "escalation_fallback.log"
    assert fallback.exists(), "fallback log must be written on write_escalation failure"
    lines = fallback.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["verbatim_text"] == text          # untruncated, verbatim
    assert row["trigger_class"] == "harm_to_self"
    assert row["severity"] == "critical"
    assert "iso_ts" in row


def test_happy_path_writes_no_fallback_file(tmp_path):
    db_path = tmp_path / "mentar.db"
    store = _WorkingStore(db_path)
    ctrl = _ctrl(store)
    ctrl.step(None)
    ctrl.step("I want to hurt myself")

    fallback = tmp_path / "escalation_fallback.log"
    assert not fallback.exists(), "no fallback file when the DB write succeeds"


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        test_db_failure_still_freezes_and_writes_fallback(pathlib.Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_happy_path_writes_no_fallback_file(pathlib.Path(d))
    print("OK: escalation fallback sink smoke passed")
