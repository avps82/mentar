#!/usr/bin/env python3
"""Pairwise model comparison (more reliable than absolute rubric for *ranking* candidates).

For each reexplain item, the judge sees two models' explanations and picks the better one. To
control position bias we ask TWICE with the order swapped, and average — so a model only "wins"
an item if it wins regardless of which slot it was shown in. Aggregated → a win-rate per pair.

Research basis: pairwise judging approximates human preference better than absolute scores, but is
itself position-biased — swap+average mitigates it (see docs/MODEL.md "alternatives"). Judge +
endpoint come from env (MENTAR_JUDGE_* | MENTAR_VLLM_*), same as eval/judge_responses.py.

    python3 eval/pairwise.py --a gemma2:9b --b nemotron-3-nano:4b

Stdlib only; the judge call is injectable for tests (no network).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))

from judge_responses import _content, parse_judge_json  # noqa: E402

DATASET = ROOT / "eval" / "dataset_v1.jsonl"
RESP_DIR = ROOT / "eval" / "responses"
OUT_DIR = ROOT / "reports" / "T1.4"

_SYS = ("You are a strict judge comparing two explanations written for a child (~8-9). "
        "Pick the better one. Reply with ONLY a JSON object, no prose.")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def responses_by_id(model: str) -> dict[str, str]:
    f = RESP_DIR / f"{model.replace('/', '_').replace(':', '_')}.jsonl"
    return {r["id"]: (r.get("response") or "") for r in load_jsonl(f)}


# ── Position-bias-controlled scoring (logic unit drafted by nemotron-3-nano:4b-q8_0;
#    audited + fixed here — its draft ignored the `x_is_a` flag, inverting order-2 scoring). ──

def score_pair(winner_order1: str, winner_order2: str) -> float:
    """X's averaged score in [0,1] over two position-swapped judge verdicts.

    order1: X shown as 'A', Y as 'B'.   order2: X shown as 'B', Y as 'A'.
    In each order X earns 1.0 if the judge picked X, 0.5 for 'tie', 0.0 for Y. Average the two.
    """
    def x_score(winner: str, x_is_a: bool) -> float:
        w = (winner or "").strip().lower()
        x_label, y_label = ("a", "b") if x_is_a else ("b", "a")
        if w == x_label:
            return 1.0
        if w == y_label:
            return 0.0
        return 0.5  # 'tie' or unrecognised
    return (x_score(winner_order1, True) + x_score(winner_order2, False)) / 2


def build_prompt(item: dict, ans_a: str, ans_b: str) -> str:
    return (
        f"Task the tutor was given: explain '{item.get('node')}' to a child (~8-9) using a "
        f"{item.get('modality')} representation, grounded only in this passage:\n"
        f"<passage>{item.get('grounding','')}</passage>\n\n"
        f"Explanation A:\n<a>{ans_a}</a>\n\nExplanation B:\n<b>{ans_b}</b>\n\n"
        "Which explanation is better for this child (clearer, in the right style, grounded, correct, "
        'no questions back)? Reply with ONLY: {"winner":"A"} or {"winner":"B"} or {"winner":"tie"}.'
    )


def _winner(verdict: dict) -> str:
    w = str(verdict.get("winner", "")).strip().lower()
    return w if w in ("a", "b", "tie") else "tie"


def compare_item(item: dict, ans_x: str, ans_y: str, call: Callable[[str], dict]) -> float:
    """Return X's score (0..1) on one item, judged in both orders to cancel position bias."""
    v1 = call(build_prompt(item, ans_x, ans_y))   # order1: X=A, Y=B
    v2 = call(build_prompt(item, ans_y, ans_x))   # order2: Y=A, X=B
    return score_pair(_winner(v1), _winner(v2))


def run_pairwise(model_x: str, model_y: str, dataset: list[dict], call: Callable[[str], dict]) -> dict:
    rx, ry = responses_by_id(model_x), responses_by_id(model_y)
    items = [it for it in dataset if it.get("suite") == "reexplain" and it["id"] in rx and it["id"] in ry]
    wins = ties = losses = 0
    total = 0.0
    for it in items:
        s = compare_item(it, rx[it["id"]], ry[it["id"]], call)
        total += s
        wins += s > 0.5
        ties += s == 0.5
        losses += s < 0.5
    n = len(items)
    return {
        "model_x": model_x, "model_y": model_y, "n": n,
        "x_win_rate": round(total / n, 3) if n else None,  # 0.5 = even; >0.5 X better
        "x_wins": wins, "ties": ties, "x_losses": losses,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pairwise reexplain comparison of two models.")
    ap.add_argument("--a", required=True, help="model X id (matches eval/responses/)")
    ap.add_argument("--b", required=True, help="model Y id")
    args = ap.parse_args(argv)

    base = os.environ.get("MENTAR_JUDGE_BASE_URL") or os.environ.get("MENTAR_VLLM_BASE_URL")
    cred = os.environ.get("MENTAR_JUDGE_API_KEY") or os.environ.get("MENTAR_VLLM_API_KEY")
    model = os.environ.get("MENTAR_JUDGE_MODEL", "claude-sonnet-4-6")
    if not base or not cred:
        print("ERROR: set MENTAR_JUDGE_BASE_URL/_API_KEY (or MENTAR_VLLM_*).")
        return 2

    def call(prompt: str) -> dict:
        try:
            return parse_judge_json(_content(_post(base, cred, model, prompt))) or {}
        except Exception:  # noqa: BLE001
            return {}

    res = run_pairwise(args.a, args.b, load_jsonl(DATASET), call)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"pairwise_{args.a}_vs_{args.b}".replace("/", "_").replace(":", "_")
    (OUT_DIR / f"{stem}.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    verdict = "even" if res["x_win_rate"] == 0.5 else (f"{args.a} better" if res["x_win_rate"] > 0.5 else f"{args.b} better")
    print(f"{args.a} vs {args.b}  (n={res['n']} reexplain): {args.a} win-rate {res['x_win_rate']} "
          f"[{res['x_wins']}W/{res['ties']}T/{res['x_losses']}L] -> {verdict}")
    return 0


def _post(base, cred, model, prompt):
    # Reuse judge transport but with the comparison system prompt.
    import json as _json
    import urllib.request
    payload = {"model": model, "messages": [{"role": "system", "content": _SYS},
                                            {"role": "user", "content": prompt}],
               "temperature": 0.0, "max_tokens": 60}
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions",
                                 data=_json.dumps(payload).encode("utf-8"), method="POST",
                                 headers={"Authorization": f"Bearer {cred}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:  # noqa: S310
        return _json.loads(r.read().decode("utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
