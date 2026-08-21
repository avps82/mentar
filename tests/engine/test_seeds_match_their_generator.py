"""A template's example question must still be one its generator can produce.

`transfer_seeds` is a REAL draw, captured when the template was written. Change
the generator's fact table afterwards and the stored seed silently keeps
describing the old content -- so the example a child (or a reviewer) sees is one
the engine can no longer generate, and may even be one the fix removed on
purpose.

Hit three times: the Specialist parity item, and then Year 2 "how things move",
Year 4 "Sun, Earth and Moon" and Year 10 "describing motion" after 2026-08-21's
overlapping-category fixes -- where the stale seed still carried the exact
defective option set the fix existed to remove.

The check is deliberately one-directional: every option in the seed, and its
question STEM, must be something the generator still produces. It says nothing
about options the generator has that the seed lacks (a seed is one sample, not a
census).

The stem half was added after the options half passed a seed whose CATEGORY had
been renamed: options survive a relabelling, so an options-only check cannot see
that the question itself is one the engine no longer asks.

    python3 -m pytest tests/engine/test_seeds_match_their_generator.py
"""

from __future__ import annotations

import pathlib
import random
import re
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.item_sources import build_registry  # noqa: E402
from mentar.engine.itemgen import ItemGenerator  # noqa: E402

_BANK = REPO_ROOT / "curriculum" / "itembank" / "pilot_fractions.jsonl"
# "STEM A) one  B) two  C) three  D) four. Answer with the letter."
_OPTIONS = re.compile(r"\b([A-D])\)\s*(.+?)(?=\s\s+[A-D]\)|\.\s*Answer with the letter)", re.S)


def _seed_options(seed: str) -> list[str]:
    return [m.group(2).strip() for m in _OPTIONS.finditer(seed)]


def test_every_mc4_seed_uses_options_its_generator_still_draws():
    registry = build_registry(_BANK)
    stale = []
    for tpl in sorted((REPO_ROOT / "curriculum" / "templates").glob("**/*.md")):
        if tpl.name in ("index.md", "log.md"):
            continue
        fm = yaml.safe_load(tpl.read_text(encoding="utf-8").split("\n---\n")[0])
        source = registry.get(fm.get("item_source", ""))
        if not source:
            continue
        generators = source["generators"]
        for concept in fm.get("concepts") or []:
            nid, seeds = concept["id"], concept.get("transfer_seeds") or []
            if concept.get("verifier", {}).get("answer_type") != "mc4":
                continue
            if nid not in generators or not seeds:
                continue
            wanted = _seed_options(seeds[0])
            if not wanted:
                continue
            gen = ItemGenerator({nid: generators[nid]}, rng=random.Random(0))
            drawable: set[str] = set()
            stems: set[str] = set()
            for _ in range(60):
                drawn = gen._make(nid)
                drawable.update(drawn.choices or ())
                stems.add((drawn.stem or "").strip())
            missing = [o for o in wanted if o not in drawable]
            if missing:
                stale.append(f"{tpl.parent.name}/{tpl.name} [{nid}]: options {missing[:2]}")
            # Only FIXED-prompt generators can be stem-checked. A parameterised
            # stem ("In the number 472, what is the value of the digit 7?")
            # differs every draw, so the seed's own wording will never recur and
            # absence proves nothing. Fact-table generators cycle a handful of
            # category prompts instead, and those ARE checkable.
            # Case is normalised because some authored seeds SHOUT a word for
            # emphasis ("Which of these IS a planet?") where the generator does not.
            if 0 < len(stems) <= 15:
                seed_stem = seeds[0].split(" A) ")[0].strip().casefold()
                if seed_stem not in {st.casefold() for st in stems}:
                    stale.append(f"{tpl.parent.name}/{tpl.name} [{nid}]: stem {seed_stem!r}")
    assert not stale, (
        "template seeds offer options their generator no longer draws — re-draw "
        "the seed after changing a fact table:\n  " + "\n  ".join(stale[:10])
    )
