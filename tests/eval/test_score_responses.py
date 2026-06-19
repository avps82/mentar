"""Tests for eval/score_responses.py (T1.3 numeric correctness scoring).

No network, no response files needed — scoring is exercised with synthetic inputs.

Inline smoke runner:
    python3 tests/eval/test_score_responses.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "eval"))

import score_responses as sr  # noqa: E402

_TRUTH = {
    "transfer-x-01": {"id": "transfer-x-01", "suite": "transfer", "answer": "3/8", "answer_type": "fraction"},
    "transfer-x-02": {"id": "transfer-x-02", "suite": "transfer", "answer": "4", "answer_type": "int"},
    "transfer-x-03": {"id": "transfer-x-03", "suite": "transfer", "answer": "B", "answer_type": "mc4"},
}


def test_score_file_mixed_outcomes():
    resp = [
        {"id": "transfer-x-01", "response": "The answer is 3/8.", "latency_s": 1.0},   # PASS
        {"id": "transfer-x-02", "response": "I think it is 5.", "latency_s": 3.0},      # FAIL
        {"id": "transfer-x-03", "response": "The answer is B.", "latency_s": 2.0},      # PASS
    ]
    res = sr.score_file(resp, _TRUTH)
    assert res["transfer_scored"] == 3
    assert res["pass"] == 2
    assert res["fail"] == 1
    assert res["pass_rate"] == round(2 / 3, 3)
    assert res["median_latency_s"] == 2.0
    assert res["items_in_file"] == 3


def test_score_file_equivalent_fraction_passes():
    # 2/4 is equivalent to 1/2 — verifier should PASS
    truth = {"t": {"id": "t", "suite": "transfer", "answer": "1/2", "answer_type": "fraction"}}
    res = sr.score_file([{"id": "t", "response": "2/4", "latency_s": 0.5}], truth)
    assert res["pass"] == 1 and res["pass_rate"] == 1.0


def test_score_file_missing_response_not_scored():
    res = sr.score_file([{"id": "transfer-x-01", "response": "3/8", "latency_s": 1.0}], _TRUTH)
    # only 1 of the 3 truth items has a response
    assert res["transfer_scored"] == 1 and res["pass"] == 1


def test_real_dataset_truth_loads():
    # The real dataset's transfer items load and every one carries answer+answer_type
    import build_dataset as bd
    if not (REPO / "eval" / "dataset_v1.jsonl").exists():
        bd.main()
    truth = sr.transfer_truth(sr.load_jsonl(sr.DATASET))
    assert len(truth) >= 30
    assert all(it.get("answer") and it.get("answer_type") for it in truth.values())


def _smoke():
    test_score_file_mixed_outcomes()
    print("[smoke] mixed outcomes OK")
    test_score_file_equivalent_fraction_passes()
    print("[smoke] equivalent-fraction PASS OK")
    test_score_file_missing_response_not_scored()
    print("[smoke] missing-response skip OK")
    test_real_dataset_truth_loads()
    print("[smoke] real dataset truth loads OK")
    print("[smoke] test_score_responses.py PASS")


if __name__ == "__main__":
    _smoke()
