#!/usr/bin/env python3
"""Build the runtime item bank from the eval transfer suite.

The eval dataset (`eval/dataset_v1.jsonl`, suite="transfer") already carries
verified, node-keyed (problem, answer) pairs — checked through verify_numeric in
tests/eval/test_dataset_v1.py. We reuse those authored answers but strip the eval
instruction wrapper so the *problem text* is child-facing, then write a clean item
bank the dialogue controller can score against.

This DECOUPLES runtime from the eval artifact: regenerate the bank with this script;
the controller only ever reads the generated jsonl.

Usage:
    python3 scripts/build_itembank.py
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "eval" / "dataset_v1.jsonl"
OUT = REPO / "curriculum" / "itembank" / "pilot_fractions.jsonl"

# Eval transfer prompts end with this phrase followed by the child-facing problem.
DELIM = "give only the final answer:"

# verify_numeric checker for each answer_type (see verify_numeric.check docstring).
CHECKER = {"int": "int_exact", "fraction": "fraction_equiv", "mc4": "mc_choice", "free_text": "none"}


def main() -> int:
    rows = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]
    transfer = [r for r in rows if r.get("suite") == "transfer"]

    items, skipped = [], []
    for r in transfer:
        prompt = r["prompt"]
        if DELIM not in prompt:
            skipped.append(r["id"])
            continue
        problem = prompt.split(DELIM, 1)[1].strip()
        atype = r.get("answer_type", "free_text")
        items.append({
            "id": r["id"],
            "node": r["node"],
            "problem": problem,
            "answer": str(r["answer"]),
            "answer_type": atype,
            "checker": CHECKER.get(atype, "none"),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    print(f"wrote {len(items)} items -> {OUT.relative_to(REPO)}")
    if skipped:
        print(f"  skipped {len(skipped)} (no delimiter): {skipped}")
    from collections import Counter
    print("  per node:", dict(Counter(i["node"] for i in items)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
