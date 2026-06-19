"""T3 — the SessionController persists escalations (SAFETY wiring).

Contract: a triggering child input must (1) freeze the session (state ESCALATION_FREEZE,
escalated=True) AND (2) call db_store.write_escalation exactly once with the FULL, UNTRUNCATED
text + a non-empty trigger class. A normal input must never call write_escalation.

Inline smoke runner:
    python3 tests/safety/test_escalation_wiring.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.dialogue.controller import SessionController  # noqa: E402

PROMPTS = REPO_ROOT / "prompts"
CURRICULUM = {
    "unit_fractions": {
        "concept": "unit fractions", "answer_type": "fraction", "checker": "fraction_equiv",
        "expected_answer": "1/3", "grounding": {}, "prerequisites": [],
    }
}


class RecordingStore:
    """Minimal store that records write_escalation calls."""

    def __init__(self):
        self.escalations: list[tuple[str, str]] = []

    def get_skill_state(self, learner_id, node_id):
        return None

    def update_skill_state(self, learner_id, node_id, p, **kw):
        pass

    def write_escalation(self, learner_id, trigger_class, trigger_text_verbatim) -> int:
        self.escalations.append((trigger_class, trigger_text_verbatim))
        return len(self.escalations)


def _ctrl(store: RecordingStore) -> SessionController:
    return SessionController(
        llm_call=lambda m: "Q?", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=CURRICULUM, db_store=store, learner_id="L1", item_bank=None,
    )


def test_escalation_persists_untruncated():
    store = RecordingStore()
    c = _ctrl(store)
    c.step(None)                                   # -> AWAIT_ANSWER
    text = "I want to hurt myself " * 5            # long, to prove no truncation
    r = c.step(text)
    assert r.escalated is True
    assert r.state == "ESCALATION_FREEZE"
    assert len(store.escalations) == 1
    cls, verbatim = store.escalations[0]
    assert verbatim == text                        # UNTRUNCATED, verbatim
    assert cls and isinstance(cls, str)


def test_normal_input_no_escalation():
    store = RecordingStore()
    c = _ctrl(store)
    c.step(None)
    c.step("1/3")
    assert store.escalations == []


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} escalation-wiring tests passed.")
