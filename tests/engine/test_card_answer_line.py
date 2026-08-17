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


def test_the_answer_line_closes_the_explanation():
    """It closes the WORKING. A card that ends its reasoning on a strategy hint
    leaves the child hunting for the answer again -- practice_odd_one_out ended
    on "Look for what MOST of them share" until 2026-08-16.

    A computed diagram may follow, after a blank-line separator: place value's
    column table, the fraction bar, the hundred-grid. Those are a PICTURE of the
    answer, drawn from the item's own numbers, so they belong after it -- which
    is why this checks the last line before the separator, not the last line.
    """
    late = []
    for name, card in _cards():
        head = []
        for line in card:
            if not line.strip():
                break            # blank line = start of the appended diagram
            head.append(line)
        if not head:
            continue
        if not head[-1].strip().lower().startswith("answer:"):
            late.append((name, head[-1][:60]))
    assert not late, f"the explanation does not end on its answer: {late[:6]}"


def test_the_stated_answer_would_itself_be_marked_correct():
    """A card must never show an answer its own verifier would reject.

    This is the trap class, not a hypothetical: rendering `*` as `×` looked like
    a pure display change until a check showed verify_numeric SAFE_REJECTed
    "6 × (x + 7)" -- a child copying the card would have been marked wrong. The
    same shape recurs whenever a card states an answer more richly than the bare
    ground truth (units: "-7°C" against truth "-7", "$300" against "300"), which
    is GOOD teaching and works only because the verifier extracts through it.

    So the check is not "card text == ground truth" -- that flags the unit cards
    as false positives. It is the thing that actually matters to a child: run the
    card's own answer through the item's own checker.
    """
    from mentar.eval.verify_numeric import CheckResult, check

    letters = "ABCD"
    # Walks the registry directly rather than _cards(), which yields only the
    # card -- choices and answer_type are needed to know what "correct" means.
    failures = []
    reg = build_registry(REPO_ROOT / "curriculum" / "item_bank.json")
    rng = random.Random(31)
    for src, entry in sorted(reg.items()):
        for node, fn in sorted((entry.get("generators") or {}).items()):
            try:
                res = fn(rng)
            except Exception:  # noqa: BLE001
                continue
            answer_type, checker, _problem, answer = res[:4]
            choices = tuple(res[4]) if len(res) > 4 and res[4] else None
            card = res[5] if len(res) > 5 and res[5] else None
            if not card:
                continue
            stated = [x for x in card if str(x).strip().lower().startswith("answer:")]
            if not stated:
                continue
            text = str(stated[0]).split(":", 1)[1].strip()
            if choices:
                if text != choices[letters.index(answer)].strip():
                    failures.append((f"{src}/{node}", text, choices[letters.index(answer)]))
            elif check(answer_type, checker, text, str(answer)).result is not CheckResult.PASS:
                failures.append((f"{src}/{node}", text, f"rejected against {answer!r}"))
    assert not failures, f"card answers their own verifier would reject: {failures[:6]}"
