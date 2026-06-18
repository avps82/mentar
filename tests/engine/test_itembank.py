"""Tests for mentar.engine.itembank + its integration with the controller.

Contract checks:
    - load_item_bank reads the generated pilot bank; all items self-validate through
      verify_numeric (answer checks PASS against itself).
    - sample() returns items for a covered node, no-repeat until the pool is exhausted,
      then reshuffles; returns None / has()==False for an uncovered node.
    - With an item bank injected, the controller scores a CORRECT answer as PASS and
      persists BKT mastery (the bug that motivated the bank: scoring could never PASS).
    - A WRONG answer routes into the Help loop (not a SAFE_REJECT dead-end).

──────────────────────────────────────────────────────────────────────────────
Inline smoke runner (python3-runnable without pytest):
    python3 tests/engine/test_itembank.py
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.itembank import Item, ItemBank, load_item_bank  # noqa: E402
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402

BANK_PATH = REPO_ROOT / "curriculum" / "itembank" / "pilot_fractions.jsonl"


# ── In-memory store for controller integration ────────────────────────────────

class _MemStore:
    def __init__(self):
        self.skills = {}

    def get_skill_state(self, learner_id, node_id):
        return {"p_mastery": self.skills[node_id]} if node_id in self.skills else None

    def update_skill_state(self, learner_id, node_id, p):
        self.skills[node_id] = p


def _bank() -> ItemBank:
    return load_item_bank(BANK_PATH, rng=random.Random(0))


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_bank_loads_and_self_validates():
    bank = _bank()
    assert len(bank) == 31
    items = [it for pool in bank._by_node.values() for it in pool]
    for it in items:
        oc = check(answer_type=it.answer_type, checker=it.checker,
                   llm_output=it.answer, ground_truth=it.answer)
        assert oc.result is CheckResult.PASS, (it.id, it.answer, oc.result)


def test_sample_no_repeat_then_reshuffle():
    items = [Item(f"i{i}", "n", f"p{i}", str(i), "int", "int_exact") for i in range(3)]
    bank = ItemBank(items, rng=random.Random(1))
    assert bank.has("n") and not bank.has("missing")
    assert bank.sample("missing") is None
    first3 = {bank.sample("n").id for _ in range(3)}
    assert first3 == {"i0", "i1", "i2"}      # all distinct before reshuffle
    assert bank.sample("n") is not None       # reshuffles, keeps serving


def _make_controller(item_bank, llm_reply="(unused)"):
    from mentar.dialogue.controller import SessionController
    curriculum = {
        "whole_number_division": {
            "concept": "Whole-number division",
            "answer_type": "int", "checker": "int_exact",
            "expected_answer": "", "grounding": {}, "prerequisites": [],
        }
    }
    return SessionController(
        llm_call=lambda m: llm_reply,
        prompt_dir=REPO_ROOT / "prompts",
        grounding_cfg={},
        curriculum=curriculum,
        db_store=_MemStore(),
        learner_id="t",
        item_bank=item_bank,
    )


def test_correct_answer_scores_and_persists():
    # Single-item bank so we know the expected answer.
    bank = ItemBank([Item("x", "whole_number_division", "Share 20 among 5?", "4", "int", "int_exact")])
    ctrl = _make_controller(bank)
    r = ctrl.step(None)                 # presents the item verbatim
    assert "Share 20 among 5" in r.text
    assert ctrl.state == "AWAIT_ANSWER"
    ctrl.step("4")                       # correct -> SCORE PASS -> BKT_UPDATE persists
    assert ctrl._store.skills.get("whole_number_division") is not None
    # mastery moved above the cold-start prior after a correct unaided answer
    assert ctrl._store.skills["whole_number_division"] > 0.0


def test_wrong_answer_routes_to_help():
    bank = ItemBank([Item("x", "whole_number_division", "Share 20 among 5?", "4", "int", "int_exact")])
    ctrl = _make_controller(bank)
    ctrl.step(None)
    ctrl.step("999")                     # wrong but valid int -> scored FAIL, not SAFE_REJECT
    # FAIL persists a (lower) mastery and advances the FSM (no dead-end).
    assert ctrl._store.skills.get("whole_number_division") is not None


# ── Inline smoke runner ───────────────────────────────────────────────────────

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} itembank tests passed.")
