"""Audit what "explain" actually produces for every curriculum node.

Answers two questions per node, by RUNNING the real code rather than reading it:
  1. Does "Explain more" show a deterministic ASCII step-grid, a computed METHOD
     CARD, LLM prose, or -- the interesting case -- a coin-flip between them
     depending on the draw?
  2. Which visual scaffold does the node's label route to?

Why it lives here rather than in a scratchpad: this has now found real, shipped
bugs twice. The 2026-07-25 pass found 5 (including a decimal-multiplication node
that was step-grid-eligible on 1% of draws, invisible to anyone reading the
regex, since its text shape is identical to the always-eligible integer case).
The 2026-08-11 full-corpus re-run found a 5th scaffold mis-route and showed the
draw-dependent problem had quadrupled to 16 nodes as the generic packs
replicated one root cause.

2026-08-15 audit: this tool was written before explain-mode's method cards
shipped, so it counted every non-step-grid node as "prose" -- including the
hundreds that now show a deterministic Type-2/4 card. It reported "always prose:
389" for a corpus where most of those nodes explain themselves without the model.
An instrument that under-reports coverage is worse than none, because the next
session reads it and re-solves a solved problem. It now classifies three ways,
straight off the drawn item (`item.method_steps` is what the controller checks).

Deliberately a REPORTER, not a gate. It prints and exits 0 -- there is no
"correct" number of prose nodes to assert. Judging the output is the human's job;
what this removes is the cost of gathering it.

    python3 -m mentar.tools.audit_explain_paths            # summary
    python3 -m mentar.tools.audit_explain_paths --json OUT # full per-node data
    python3 -m mentar.tools.audit_explain_paths --partial  # only the coin-flip nodes
"""

import json
import random
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

from mentar.engine.arithmetic_steps import (  # noqa: E402
    extract_addition_operands,
    extract_decimal_multiplication_operands,
    extract_division_operands,
    extract_multiplication_operands,
    extract_signed_addition_operands,
    extract_signed_multiplication_operands,
    extract_subtraction_operands,
)
from mentar.engine.curriculum import load_curriculum, load_template_meta  # noqa: E402
from mentar.engine.item_sources import build_registry  # noqa: E402
from mentar.engine.itembank import load_item_bank  # noqa: E402
from mentar.engine.itemgen import CompositeItemSource, ItemGenerator  # noqa: E402
from mentar.engine.visual_scaffold import load_visual_scaffold  # noqa: E402

SCAFFOLD_ROOT = REPO / "curriculum" / "visual_scaffolds"
REGISTRY = build_registry(REPO / "curriculum" / "itembank" / "pilot_fractions.jsonl")
DRAWS = 200  # enough to expose a 1%-eligibility node

# Which scaffold FILE a body came from -- load_visual_scaffold returns only the body,
# so map body->filename once up front to report routing targets.
BODY_TO_FILE = {}
for sub in ("maths", "english", "science"):
    d = SCAFFOLD_ROOT / sub
    if not d.exists():
        continue
    for f in d.glob("*.md"):
        if f.name in ("index.md", "log.md"):
            continue
        text = f.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        body = parts[2].strip() if len(parts) >= 3 else text
        BODY_TO_FILE[body.strip()] = f"{sub}/{f.name}"


def step_grid_kind(problem: str):
    """Which extractor (if any) claims this problem text. Mirrors the controller's
    add -> sub -> mult -> div chain order in _build_steps_grid_if_eligible."""
    if extract_addition_operands(problem) is not None:
        return "addition"
    if extract_subtraction_operands(problem) is not None:
        return "subtraction"
    if extract_multiplication_operands(problem) is not None:
        return "multiplication"
    if extract_decimal_multiplication_operands(problem) is not None:
        return "multiplication_decimal"
    if extract_signed_multiplication_operands(problem) is not None:
        return "multiplication_signed"
    if extract_signed_addition_operands(problem) is not None:
        return "addition_signed"
    if extract_division_operands(problem) is not None:
        return "division"
    return None


def audit():
    rows = []
    templates = sorted(p for p in (REPO / "curriculum" / "templates").rglob("*.md")
                       if p.name not in ("index.md", "log.md"))
    for tpl in templates:
        rel = str(tpl.relative_to(REPO / "curriculum" / "templates"))
        try:
            meta = load_template_meta(tpl)
            curriculum = load_curriculum(tpl)
        except Exception as e:
            rows.append({"template": rel, "error": f"load failed: {e!r}"})
            continue
        subject = meta.get("subject") or ""
        src_name = meta.get("item_source")
        src = REGISTRY.get(src_name)
        if src is None:
            rows.append({"template": rel, "error": f"item_source {src_name!r} not in registry"})
            continue

        for node_id, node in curriculum.items():
            label = node.get("label", node_id)
            gen = ItemGenerator(generators=src["generators"], rng=random.Random(20260811))
            # mirror web/app.py: the registry holds a PATH; the bank must be loaded
            bank_path = src["itembank"]
            bank = load_item_bank(bank_path) if bank_path and Path(bank_path).exists() else None
            source = CompositeItemSource(gen, bank)

            kinds = Counter()
            sample_problem = None
            answer_types = Counter()
            for _ in range(DRAWS):
                item = source.sample(node_id)
                if item is None:
                    kinds["<no item>"] += 1
                    continue
                if sample_problem is None:
                    sample_problem = item.problem
                answer_types[item.answer_type] += 1
                # Mirrors controller._do_help_explain's order exactly: a step grid
                # wins, else the live item's method card, else LLM prose.
                kind = step_grid_kind(item.problem)
                if kind is None:
                    kind = "method-card" if item.method_steps else "prose"
                kinds[kind] += 1

            body = load_visual_scaffold(SCAFFOLD_ROOT, subject, label)
            scaffold_file = BODY_TO_FILE.get(body.strip()) if body else None

            total = sum(kinds.values()) or 1
            card_hits = kinds.get("method-card", 0)
            grid_hits = total - card_hits - kinds.get("prose", 0) - kinds.get("<no item>", 0)
            rows.append({
                "template": rel,
                "subject": subject,
                "node": node_id,
                "label": label,
                "answer_types": dict(answer_types),
                "grid_pct": round(100.0 * grid_hits / total, 1),
                "card_pct": round(100.0 * card_hits / total, 1),
                "deterministic_pct": round(100.0 * (grid_hits + card_hits) / total, 1),
                "grid_kinds": {k: v for k, v in kinds.items()
                               if k not in ("prose", "method-card", "<no item>")},
                "no_item": kinds.get("<no item>", 0),
                "scaffold": scaffold_file,
                "sample": sample_problem,
            })
    return rows


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    rows = audit()
    errs = [r for r in rows if "error" in r]
    nodes = [r for r in rows if "error" not in r]

    if "--json" in argv:
        out = Path(argv[argv.index("--json") + 1])
        out.write_text(json.dumps(rows, indent=1), encoding="utf-8")
        print(f"wrote {out}")

    partial = sorted((r for r in nodes if 0 < r["grid_pct"] < 100), key=lambda r: r["grid_pct"])
    if "--partial" in argv:
        for r in partial:
            print(f"{r['grid_pct']:6.1f}%  {r['node']:34s} {r['template']}")
        return 0

    always = sum(1 for r in nodes if r["grid_pct"] == 100)
    cards = sum(1 for r in nodes if r["card_pct"] == 100)
    never = sum(1 for r in nodes if r["deterministic_pct"] == 0)
    partial_det = [r for r in nodes if 0 < r["deterministic_pct"] < 100]
    by_subject = Counter(r["subject"] for r in nodes)
    unscaffolded = [r for r in nodes if not r["scaffold"]]

    print(f"nodes {len(nodes)} across {len({r['template'] for r in nodes})} templates "
          f"({', '.join(f'{k} {v}' for k, v in sorted(by_subject.items()))})")
    print(f"  always step-grid : {always}")
    print(f"  always method-card: {cards}")
    print(f"  always prose (no deterministic explanation at all): {never}")
    if partial_det:
        print(f"  PART-DETERMINISTIC: {len(partial_det)}"
              "  <-- some draws explain themselves, some fall to the model")
        for r in partial_det[:10]:
            print(f"      {r['deterministic_pct']:6.1f}%  {r['node']}")
    print(f"  DRAW-DEPENDENT   : {len(partial)}"
          + ("  <-- same concept, different output per draw" if partial else ""))
    for r in partial:
        print(f"      {r['grid_pct']:6.1f}%  {r['node']}")
    print(f"  no scaffold      : {len(unscaffolded)}")
    for r in unscaffolded[:10]:
        print(f"      {r['node']} ({r['label']!r})")
    for e in errs:
        print(f"  TEMPLATE ERROR: {e['template']}: {e['error']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
