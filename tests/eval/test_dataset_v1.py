"""Tests for the T1.1 eval dataset + T1.2 runner.

- The shipped eval/dataset_v1.jsonl passes every T1.1 PASS rule (via eval/validate_dataset.py).
- A sample of transfer ground-truth answers actually verify PASS via verify_numeric.
- run_candidates builds a correct chat payload and records a response line + latency, using a
  MOCKED http function (no network).

Inline smoke runner:
    python3 tests/eval/test_dataset_v1.py
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "eval"))

from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402

import build_dataset as bd  # noqa: E402
import validate_dataset as vd  # noqa: E402
import run_candidates as rc  # noqa: E402

_CHECKER = {"int": "int_exact", "fraction": "fraction_equiv", "mc4": "mc_choice"}

# eval/dataset_*.jsonl is gitignored (pinned via the generator + hash) — regenerate if absent
# so the suite is hermetic on a fresh clone.
if not vd.DATASET.exists():
    bd.main()


# ── Dataset validity ────────────────────────────────────────────────────────

def test_dataset_passes_all_t1_1_rules():
    items = vd.load_items()
    ok, report = vd.validate(items)
    failed = [c for c in report["checks"] if not c["pass"]]
    assert ok, f"T1.1 validation failed: {failed}"


def test_counts():
    items = vd.load_items()
    counts = {"reexplain": 0, "transfer": 0, "adversarial": 0}
    for it in items:
        counts[it["suite"]] += 1
    assert counts["reexplain"] == 50
    assert counts["transfer"] >= 30
    assert counts["adversarial"] >= 20


def test_transfer_answers_verify_pass():
    """Every transfer item's stored answer should PASS its own verifier (ground truth is correct)."""
    items = [it for it in vd.load_items() if it["suite"] == "transfer"]
    assert items
    for it in items:
        at = it["answer_type"]
        # Simulate an LLM that returns exactly the right answer.
        llm = f"The answer is {it['answer']}."
        outcome = check(at, _CHECKER[at], llm, it["answer"])
        assert outcome.result is CheckResult.PASS, f"{it['id']}: {outcome.result} — {outcome.detail}"


def test_adversarial_subtypes_present():
    items = [it for it in vd.load_items() if it["suite"] == "adversarial"]
    by_type: dict[str, int] = {}
    for it in items:
        by_type[it["adversarial_type"]] = by_type.get(it["adversarial_type"], 0) + 1
    for t in ("jailbreak", "offtopic", "distress", "injected_passage"):
        assert by_type.get(t, 0) >= 5, f"{t}: {by_type.get(t, 0)}"
    # injected_passage items carry a poisoned grounding passage
    for it in items:
        if it["adversarial_type"] == "injected_passage":
            assert it.get("grounding"), f"{it['id']} missing grounding"


# ── Runner (mocked HTTP — no network) ───────────────────────────────────────

def test_runner_builds_payload_and_records(tmp_path):
    items = vd.load_items()[:3]
    sent = []

    def fake_post(base_url, api_key, payload, timeout=120):
        sent.append((base_url, api_key, payload))
        return {"choices": [{"message": {"content": "hello"}}]}

    out = rc.run_model("test-model", items, "http://fake/v1", "k", out_dir=tmp_path, post=fake_post)
    lines = [l for l in out.read_text().splitlines() if l.strip()]
    assert len(lines) == 3
    import json
    first = json.loads(lines[0])
    assert first["model"] == "test-model" and first["response"] == "hello"
    assert "latency_s" in first and first["error"] is None
    # payload shape
    _, _, payload = sent[0]
    assert payload["model"] == "test-model"
    assert payload["messages"][0]["role"] == "user"
    assert payload["temperature"] == rc.TEMPERATURE and payload["max_tokens"] == rc.MAX_TOKENS


def test_models_yaml_loads_roster():
    models = rc.load_models()
    names = {m["name"] for m in models}
    assert "llama3.1:8b" in names and "mistral-small3.1" in names
    roles = {m["name"]: m["role"] for m in models}
    assert roles["mistral-small3.1"] == "ceiling"
    assert roles["claude-sonnet-4-6"] == "judge"
    assert sum(1 for m in models if m["role"] == "candidate") == 6


# ── Inline smoke runner ─────────────────────────────────────────────────────

def _smoke():
    items = vd.load_items()
    ok, report = vd.validate(items)
    assert ok, [c for c in report["checks"] if not c["pass"]]
    print(f"[smoke] dataset valid — {report['total_items']} items {report['counts']}")
    test_transfer_answers_verify_pass()
    print("[smoke] transfer answers verify PASS")
    test_adversarial_subtypes_present()
    print("[smoke] adversarial subtypes present")
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        test_runner_builds_payload_and_records(pathlib.Path(d))
    print("[smoke] runner (mocked) OK")
    test_models_yaml_loads_roster()
    print("[smoke] models.yaml roster OK")
    print("[smoke] test_dataset_v1.py PASS")


if __name__ == "__main__":
    _smoke()
