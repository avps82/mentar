"""A19 — a session's non-deterministic choices (pattern/modality/praise-variant
selection) can be replayed exactly given the same rng_seed.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import SessionController

PROMPTS = REPO / "prompts"
_CURRICULUM = {
    f"node_{i}": {
        "label": f"node {i}", "answer_type": "int", "checker": "int_exact",
        "expected_answer": "2", "grounding": {}, "prerequisites": [],
    }
    for i in range(5)
}


class _FakeStore:
    def get_skill_state(self, learner_id, node_id):
        return None

    def update_skill_state(self, learner_id, node_id, p):
        pass


def _drive(seed):
    """Two turns with a wrong-then-help-then-correct flow, capturing every
    piece of text influenced by the RNG (pattern choice affects the rendered
    question text; feedback phrasing on the correct answer)."""
    ctrl = SessionController(
        llm_call=lambda m: "An explanation.", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=_FakeStore(), learner_id="L",
        rng_seed=seed,
    )
    texts = [ctrl.step(None).text]
    texts.append(ctrl.step("wrong").text)   # wrong -> auto-help (modality choice)
    texts.append(ctrl.step("2").text)       # correct hinted recheck (feedback variant)
    return ctrl.rng_seed, texts


def test_same_seed_replays_identical_session():
    seed_a, texts_a = _drive(42)
    seed_b, texts_b = _drive(42)
    assert seed_a == seed_b == 42
    assert texts_a == texts_b


def test_default_seed_is_logged_and_reusable():
    """No explicit seed -> a random one is picked; passing it back in replays
    the same session."""
    ctrl1 = SessionController(
        llm_call=lambda m: "x", prompt_dir=PROMPTS, grounding_cfg={},
        curriculum=_CURRICULUM, db_store=_FakeStore(), learner_id="L",
    )
    seed = ctrl1.rng_seed
    assert isinstance(seed, int)

    _, texts_a = _drive(seed)
    _, texts_b = _drive(seed)
    assert texts_a == texts_b


if __name__ == "__main__":
    test_same_seed_replays_identical_session()
    print("  ✓ test_same_seed_replays_identical_session")
    test_default_seed_is_logged_and_reusable()
    print("  ✓ test_default_seed_is_logged_and_reusable")
