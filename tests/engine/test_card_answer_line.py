"""Every explain-mode card must end by naming the answer.

Maintainer, 2026-08-16: "answer should have 'Answer:' in all explain responses
... English where it was not exactly clear".

The numeric families always did. The "fact in category" shape built by
itemgen.mc_which_is did not: it carried the answer only on the stem line, after
an arrow and ahead of two further lines that each contain other options and
arrows. That is hardest to read exactly where the options are whole sentences --

    Which of these is a complex sentence? → She writes poetry because it calms her.
      She writes poetry because it calms her. → a complex sentence (...)
      The others: She writes poetry and she paints. → a compound sentence (...)

382 of 541 cards had no Answer: line, across 340 generators, all from that one
builder plus practice_odd_one_out (whose last line was a strategy hint).

A sweep rather than a fixture: the point is that NO generator may ship a card
without it, including ones added later.

    python3 -m pytest tests/engine/test_card_answer_line.py
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.item_sources import build_registry  # noqa: E402


def _cards():
    reg = build_registry(REPO_ROOT / "curriculum" / "item_bank.json")
    rng = random.Random(20260816)
    for src, entry in sorted(reg.items()):
        for node, fn in sorted((entry.get("generators") or {}).items()):
            for _ in range(3):
                try:
                    res = fn(rng)
                except Exception:  # noqa: BLE001 -- generator health is other tests' job
                    break
                card = res[5] if len(res) > 5 and res[5] else None
                if card:
                    yield f"{src}/{node}", tuple(str(x) for x in card)


def test_every_explain_card_names_its_answer():
    missing = [
        name for name, card in _cards()
        if not any(line.strip().lower().startswith("answer:") for line in card)
    ]
    assert not missing, (
        f"{len(missing)} generator(s) build a card with no 'Answer:' line: {missing[:8]}"
    )


def test_the_answer_line_is_the_last_thing_on_the_card():
    """It closes the card. A card that ends on a strategy hint or a diagram
    leaves the child hunting for the answer again -- practice_odd_one_out ended
    on "Look for what MOST of them share" until this landed.

    Place-value cards are the deliberate exception: their computed table is
    appended AFTER the answer, as a picture of it.
    """
    late = []
    for name, card in _cards():
        body = [line for line in card if line.strip()]
        if not body or "place_value" in name:
            continue
        if not body[-1].strip().lower().startswith("answer:"):
            late.append((name, body[-1][:60]))
    assert not late, f"card does not END on its answer: {late[:6]}"
