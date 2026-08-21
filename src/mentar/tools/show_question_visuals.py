"""Print the picture every visual question draws, so a human can look at it.

Visual-first (docs/design/visual_first_gap.md) puts a picture ON the question for
"constitutive" topics -- ones where the picture IS the question. ASCII art is
hand-editable, which is the point: the loop is look, tweak the renderer, look
again. This is the looking half.

A REPORT, not a gate -- same posture as tools/audit_curriculum_coverage.py. It
tells you which nodes draw a picture and which do not; it never fails a build.

The seed is derived from the NODE ID, not the clock, so re-running after a tweak
gives a readable diff of the art instead of a fresh random scramble.

The terminal is monospace by definition, so alignment here is real. It is NOT the
whole review: the browser is the only place the app's font, theme and wrapping
are real, so finish at MENTAR_DEV_GALLERY=1 /gallery. A picture nobody has SEEN
in a browser is not done.

    python3 -m mentar.tools.show_question_visuals
    python3 -m mentar.tools.show_question_visuals --node unit_fractions --draws 5
    python3 -m mentar.tools.show_question_visuals --all      # incl. picture-less
"""

from __future__ import annotations

import argparse
import random
import sys
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

from mentar.engine.item_sources import build_registry  # noqa: E402
from mentar.engine.itemgen import ItemGenerator  # noqa: E402

_BANK = REPO / "curriculum" / "itembank" / "pilot_fractions.jsonl"


def _stable_seed(node_id: str) -> int:
    """Same art for the same node every run -- so a re-run diffs, not scrambles."""
    return zlib.crc32(node_id.encode()) & 0xFFFF


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--node", help="only this node id")
    ap.add_argument("--draws", type=int, default=2, help="samples per node (default 2)")
    ap.add_argument("--all", action="store_true", help="also list nodes with no picture")
    args = ap.parse_args(argv)

    registry = build_registry(_BANK)
    drawn = silent = 0
    for source in sorted(registry):
        generators = registry[source]["generators"] or {}
        for node_id, fn in sorted(generators.items()):
            if args.node and node_id != args.node:
                continue
            gen = ItemGenerator({node_id: fn}, rng=random.Random(_stable_seed(node_id)))
            items = [gen._make(node_id) for _ in range(args.draws)]
            items = [i for i in items if i is not None]
            if not any(i.visual for i in items):
                silent += 1
                if args.all:
                    print(f"\n--- {node_id}  [{source}]  (no picture)")
                continue
            drawn += 1
            print(f"\n=== {node_id}  [{source}]")
            for item in items:
                if not item.visual:
                    continue
                for line in item.visual:
                    print(f"    {line}")
                print(f"    Q: {(item.stem or item.problem)}")
                print(f"    A: {item.answer}")
                # The one property a human should not have to check by eye.
                # An ASSERTION is the leak ("... = 1/5"). The answer's digits merely
                # APPEARING is not: a clock dial carries all twelve hour numbers.
                if any("=" in ln or ln.strip() == str(item.answer) for ln in item.visual):
                    print("    !! PICTURE STATES THE ANSWER — question-side renderers "
                          "must withhold their summary line")
                print()
    print("-" * 72)
    print(f"{drawn} node(s) draw a picture; {silent} do not. "
          "This is a report — look at the art, then confirm it in the browser "
          "(MENTAR_DEV_GALLERY=1, /gallery).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
