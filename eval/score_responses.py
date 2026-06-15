#!/usr/bin/env python3
"""T1.3 (numeric correctness) — score candidate responses on the transfer suite.

Reads eval/dataset_v1.jsonl (ground truth) + eval/responses/*.jsonl (from run_candidates.py),
runs each transfer answer through src/mentar/eval/verify_numeric.py, and reports per-model:
numeric pass-rate + outcome breakdown + median latency. Writes reports/T1.3/scores.csv.

    python3 eval/score_responses.py

Correctness here is the transfer suite only (checkable). Rubric/safety scoring (T1.4/T1.5)
and hallucination grading are separate (judge-based) — see docs/MODEL.md.
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mentar.eval.verify_numeric import check  # noqa: E402

DATASET = ROOT / "eval" / "dataset_v1.jsonl"
RESP_DIR = ROOT / "eval" / "responses"
OUT = ROOT / "reports" / "T1.3" / "scores.csv"

_CHECKER = {"int": "int_exact", "fraction": "fraction_equiv", "mc4": "mc_choice"}
_COLS = ["model", "items_in_file", "transfer_scored", "pass", "fail",
         "extract_fail", "safe_reject", "pass_rate", "median_latency_s"]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def transfer_truth(dataset: list[dict]) -> dict[str, dict]:
    return {it["id"]: it for it in dataset if it.get("suite") == "transfer"}


def score_file(resp_items: list[dict], truth: dict[str, dict]) -> dict:
    """Score one model's responses against the transfer ground truth."""
    by_id = {r["id"]: r for r in resp_items}
    out = {"transfer_scored": 0, "pass": 0, "fail": 0, "extract_fail": 0, "safe_reject": 0}
    for tid, it in truth.items():
        r = by_id.get(tid)
        if r is None:
            continue
        out["transfer_scored"] += 1
        outcome = check(it["answer_type"], _CHECKER[it["answer_type"]],
                        r.get("response", "") or "", it["answer"])
        out[outcome.result.value] = out.get(outcome.result.value, 0) + 1
    lat = [r["latency_s"] for r in resp_items if isinstance(r.get("latency_s"), (int, float))]
    out["pass_rate"] = round(out["pass"] / out["transfer_scored"], 3) if out["transfer_scored"] else 0.0
    out["median_latency_s"] = round(statistics.median(lat), 3) if lat else None
    out["items_in_file"] = len(resp_items)
    return out


def main() -> int:
    truth = transfer_truth(load_jsonl(DATASET))
    files = sorted(RESP_DIR.glob("*.jsonl")) if RESP_DIR.exists() else []
    rows = []
    for f in files:
        res = score_file(load_jsonl(f), truth)
        res["model"] = f.stem
        rows.append(res)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=_COLS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c) for c in _COLS})

    if not rows:
        print("No response files in eval/responses/ yet — run: python3 eval/run_candidates.py")
        return 0
    print(f"{'model':24}{'n':>5}{'transfer':>9}{'pass':>6}{'rate':>7}{'med_lat':>9}")
    for r in sorted(rows, key=lambda x: -x["pass_rate"]):
        print(f"{r['model']:24}{r['items_in_file']:>5}{r['transfer_scored']:>9}"
              f"{r['pass']:>6}{r['pass_rate']:>7}{str(r['median_latency_s']):>9}")
    print(f"\nwrote {OUT}  (transfer-suite numeric correctness + latency; T1.3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
