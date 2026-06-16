"""Tests for eval/pairwise.py — position-bias-controlled pairwise comparison.

The critical test is `test_score_pair_cancels_position_bias`: it pins exactly the bug the local
model's first draft had (ignoring which slot X was shown in), which would have defeated the whole
point of swapping order. No network — the judge call is mocked.

Inline smoke runner: python3 tests/eval/test_pairwise.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "eval"))

import pairwise as pw  # noqa: E402


def test_score_pair_clear_win_and_loss():
    # X shown A then B; judge picks X both times (A in order1, B in order2) -> 1.0
    assert pw.score_pair("A", "B") == 1.0
    # judge picks Y both times (B in order1, A in order2) -> 0.0
    assert pw.score_pair("B", "A") == 0.0
    # ties -> 0.5
    assert pw.score_pair("tie", "tie") == 0.5


def test_score_pair_cancels_position_bias():
    # Judge picked 'A' in BOTH orders. In order1 A=X (X wins); in order2 A=Y (X loses).
    # A position-biased judge -> this must average to 0.5 (a wash), NOT 1.0.
    assert pw.score_pair("A", "A") == 0.5
    assert pw.score_pair("B", "B") == 0.5


def test_score_pair_case_insensitive_and_unknown():
    assert pw.score_pair("a", "b") == 1.0
    assert pw.score_pair("", "garbage") == 0.5  # unrecognised -> tie


def test_compare_item_consistent_winner(monkeypatch):
    item = {"id": "r1", "suite": "reexplain", "node": "n", "modality": "visual", "grounding": "g"}
    # Judge always prefers whichever is in slot A -> pure position bias -> 0.5
    def call_prefers_A(prompt):
        return {"winner": "A"}
    assert pw.compare_item(item, "X-answer", "Y-answer", call_prefers_A) == 0.5

    # Judge always prefers X's actual text regardless of slot -> X wins -> 1.0
    def call_prefers_X(prompt):
        return {"winner": "A"} if prompt.index("X-answer") < prompt.index("Y-answer") else {"winner": "B"}
    assert pw.compare_item(item, "X-answer", "Y-answer", call_prefers_X) == 1.0


def test_run_pairwise_aggregates(monkeypatch, tmp_path):
    dataset = [
        {"id": "r1", "suite": "reexplain", "node": "n", "modality": "visual", "grounding": "g"},
        {"id": "r2", "suite": "reexplain", "node": "n", "modality": "story", "grounding": "g"},
        {"id": "t1", "suite": "transfer"},  # ignored (not reexplain)
    ]
    monkeypatch.setattr(pw, "responses_by_id",
                        lambda m: {"r1": f"{m}-a", "r2": f"{m}-a"} if m == "X" else {"r1": "y", "r2": "y"})
    # judge always prefers X's real text
    def call(prompt):
        return {"winner": "A"} if "X-a" in prompt.split("<b>")[0] else {"winner": "B"}
    res = pw.run_pairwise("X", "Y", dataset, call)
    assert res["n"] == 2 and res["x_win_rate"] == 1.0 and res["x_wins"] == 2


def _smoke():
    assert pw.score_pair("A", "B") == 1.0 and pw.score_pair("B", "A") == 0.0
    assert pw.score_pair("A", "A") == 0.5, "position-bias control broken"
    print("[smoke] score_pair (incl. position-bias) OK")
    item = {"id": "r1", "suite": "reexplain", "node": "n", "modality": "visual", "grounding": "g"}
    assert pw.compare_item(item, "X-answer", "Y-answer", lambda p: {"winner": "A"}) == 0.5
    print("[smoke] compare_item OK")
    print("[smoke] test_pairwise.py PASS")


if __name__ == "__main__":
    _smoke()
