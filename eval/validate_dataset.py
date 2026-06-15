#!/usr/bin/env python3
"""Validate eval/dataset_v1.jsonl against the T1.1 PASS rules (docs/TESTS.md).

Stdlib only (no jsonschema dep — explicit checks). Writes reports/T1.1/result.json.
Exit 0 if PASS, 1 otherwise.

Checks:
  - every line parses; required keys present per suite; enums valid.
  - counts: reexplain == 50, transfer >= 30, adversarial >= 20.
  - reexplain covers all 8 nodes x 5 modalities.
  - 100% of checkable items (suite==transfer, or any item with `answer`) carry answer + answer_type.
  - all adversarial carry adversarial_type + expected_behavior, with >=5 of each adversarial_type.
  - ids are unique.
"""

from __future__ import annotations

import json
from pathlib import Path

NODES = [
    "whole_number_division", "fraction_as_part_of_whole", "equal_vs_unequal_parts",
    "unit_fractions", "equivalent_fractions", "comparing_equal_denom",
    "adding_equal_denom", "subtracting_equal_denom",
]
MODALITIES = ["analogy", "concrete", "formal", "story", "visual"]
SUITES = {"reexplain", "transfer", "adversarial"}
ANSWER_TYPES = {"int", "fraction", "mc4"}
ADV_TYPES = {"jailbreak", "offtopic", "distress", "injected_passage"}
BEHAVIORS = {"refuse_redirect", "defer_to_adult", "ignore_injection"}

DATASET = Path(__file__).resolve().parent / "dataset_v1.jsonl"
REPORT = Path(__file__).resolve().parents[1] / "reports" / "T1.1" / "result.json"


def load_items(path: Path = DATASET) -> list[dict]:
    items = []
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {ln}: invalid JSON: {exc}") from exc
    return items


def validate(items: list[dict]) -> tuple[bool, dict]:
    checks: list[dict] = []

    def chk(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    # Per-item structural validation
    item_errors: list[str] = []
    ids: set[str] = set()
    counts = {"reexplain": 0, "transfer": 0, "adversarial": 0}
    adv_type_counts = {t: 0 for t in ADV_TYPES}
    reexplain_combos: set[tuple[str, str]] = set()

    for it in items:
        iid = it.get("id", "<no-id>")
        suite = it.get("suite")
        if suite not in SUITES:
            item_errors.append(f"{iid}: bad/missing suite {suite!r}")
            continue
        counts[suite] += 1
        if iid in ids:
            item_errors.append(f"{iid}: duplicate id")
        ids.add(iid)
        for req in ("id", "suite", "node", "prompt"):
            if not it.get(req):
                item_errors.append(f"{iid}: missing required {req!r}")
        if "answer_type" in it and it["answer_type"] not in ANSWER_TYPES:
            item_errors.append(f"{iid}: bad answer_type {it['answer_type']!r}")
        if "answer" in it and "answer_type" not in it:
            item_errors.append(f"{iid}: has answer but no answer_type")

        if suite == "reexplain":
            if it.get("modality") not in MODALITIES:
                item_errors.append(f"{iid}: reexplain missing/bad modality")
            if not it.get("grounding"):
                item_errors.append(f"{iid}: reexplain missing grounding")
            if it.get("node") in NODES and it.get("modality") in MODALITIES:
                reexplain_combos.add((it["node"], it["modality"]))
        elif suite == "transfer":
            if not it.get("answer") or it.get("answer_type") not in ANSWER_TYPES:
                item_errors.append(f"{iid}: transfer missing answer/answer_type")
        elif suite == "adversarial":
            at = it.get("adversarial_type")
            if at not in ADV_TYPES:
                item_errors.append(f"{iid}: bad/missing adversarial_type")
            else:
                adv_type_counts[at] += 1
            if it.get("expected_behavior") not in BEHAVIORS:
                item_errors.append(f"{iid}: bad/missing expected_behavior")
            if at == "injected_passage" and not it.get("grounding"):
                item_errors.append(f"{iid}: injected_passage missing grounding")

    chk("all items structurally valid", not item_errors, "; ".join(item_errors[:10]))
    chk("reexplain == 50", counts["reexplain"] == 50, f"got {counts['reexplain']}")
    chk("transfer >= 30", counts["transfer"] >= 30, f"got {counts['transfer']}")
    chk("adversarial >= 20", counts["adversarial"] >= 20, f"got {counts['adversarial']}")

    missing_combos = [f"{n}/{m}" for n in NODES for m in MODALITIES if (n, m) not in reexplain_combos]
    chk("reexplain covers 8 nodes x 5 modalities", not missing_combos,
        f"missing: {missing_combos[:8]}")

    # Checkable items carry ground truth
    checkable = [it for it in items if it.get("suite") == "transfer" or "answer" in it]
    bad_gt = [it["id"] for it in checkable
              if not it.get("answer") or it.get("answer_type") not in ANSWER_TYPES]
    chk("100% checkable items carry answer+answer_type", not bad_gt, f"bad: {bad_gt[:8]}")

    # Adversarial subtype coverage
    low = {t: c for t, c in adv_type_counts.items() if c < 5}
    chk("adversarial >=5 of each subtype", not low, f"under 5: {low}")

    ok = all(c["pass"] for c in checks)
    report = {
        "dataset": str(DATASET.name),
        "total_items": len(items),
        "counts": counts,
        "adversarial_type_counts": adv_type_counts,
        "checks": checks,
        "pass": ok,
    }
    return ok, report


def main() -> int:
    items = load_items()
    ok, report = validate(items)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for c in report["checks"]:
        mark = "PASS" if c["pass"] else "FAIL"
        print(f"[{mark}] {c['check']}" + (f" — {c['detail']}" if c["detail"] and not c["pass"] else ""))
    print(f"\n{'PASS' if ok else 'FAIL'} — {report['total_items']} items, counts={report['counts']}")
    print(f"wrote {REPORT}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
