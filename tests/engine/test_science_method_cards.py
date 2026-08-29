"""explain-mode (2026-08-12) — Type 4 "fact in category" cards for all 24
science generators (docs/design/explain_mode_design.md §3 Type 4, §5 verification).

Science has no derivation to self-check arithmetically (unlike the Type 2 maths
cards in test_method_cards.py) -- the ground truth is the curated fact table, and
that's reviewed once at authoring. What CAN be verified over every real draw,
mechanically, without eyeballing any of the 24 x ~500 possible items:

  1. the card names the concept by its textbook term (the "stick with the name"
     rule from the light-scattering SVG review);
  2. the card states the item's ACTUAL correct answer, not a different member;
  3. every DISTRACTOR the item presents also appears in the card exactly once,
     each with its own true category -- the whole point of Type 4 (a child who
     picked the wrong option needs to hear why THAT one was wrong).

    python3 tests/engine/test_science_method_cards.py
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.itemgen import ItemGenerator  # noqa: E402
from mentar.engine.science_items import SCIENCE_GENERATORS  # noqa: E402

_LETTERS = "ABCD"


def test_every_science_generator_produces_a_method_card_every_draw():
    """No silent gaps: all 24 nodes, every draw, must carry a card."""
    ig = ItemGenerator(generators=SCIENCE_GENERATORS, rng=random.Random(11))
    for node_id in SCIENCE_GENERATORS:
        for _ in range(30):
            item = ig.sample(node_id)
            assert item is not None
            assert item.method_steps is not None, node_id
            # 4 fixed lines + one line PER distractor + the Answer line
            # (2026-08-20: "The others" became one line per option -- the
            # single joined line ran them together on screen).
            n_distractors = len(item.choices) - 1
            assert len(item.method_steps) == 4 + n_distractors + 1, (
                node_id, item.method_steps)


def test_card_names_the_concept_and_states_the_real_answer():
    ig = ItemGenerator(generators=SCIENCE_GENERATORS, rng=random.Random(22))
    for node_id in SCIENCE_GENERATORS:
        for _ in range(30):
            item = ig.sample(node_id)
            concept, question_line, answer_line = item.method_steps[:3]
            final = item.method_steps[-1]
            # rule: name the concept -- an all-caps textbook term, non-empty,
            # never just repeating the generic word "science".
            assert concept == concept.upper() and len(concept) > 3, (node_id, concept)
            correct_text = item.choices[_LETTERS.index(item.answer)]
            # The card names the answer where it TEACHES ("owl -> bird (birds
            # have feathers...)") and again on its closing line — but NOT on the
            # restated question. That opening duplicate was stripped centrally
            # on 2026-08-29: it put the answer on the card's first content line,
            # before any reasoning, while the app's repeat prompt tells the child
            # "the answer is on the last line".
            assert correct_text not in question_line, (node_id, question_line)
            assert correct_text in answer_line, (node_id, correct_text, answer_line)
            # ...and the card ends by naming it outright.
            assert final.strip() == f"Answer: {correct_text}", (node_id, final)


def test_every_distractor_appears_in_the_others_line_exactly_once():
    """Parses "the others" into (member, true_label) pairs on the " · "
    separator, rather than substring-searching -- a naive `in`/`.count()`
    check is fooled by one member's name being a substring of another's
    (e.g. distractor "ant" inside distractor "elephant")."""
    ig = ItemGenerator(generators=SCIENCE_GENERATORS, rng=random.Random(33))
    for node_id in SCIENCE_GENERATORS:
        for _ in range(50):
            item = ig.sample(node_id)
            correct_text = item.choices[_LETTERS.index(item.answer)]
            distractors = [c for c in item.choices if c != correct_text]
            # 2026-08-20 (maintainer): one line PER distractor -- the old
            # single "a · b · c" line ran the options together on screen.
            assert item.method_steps[3].strip() == "The others:", (node_id, item.method_steps[3])
            other_lines = item.method_steps[4:4 + len(distractors)]
            members_listed = [ln.split(" → ", 1)[0].strip() for ln in other_lines]
            assert sorted(members_listed) == sorted(distractors), (node_id, other_lines, distractors)
            assert correct_text not in members_listed, (node_id, other_lines)


def test_gloss_present_for_every_target_label_reached_over_many_draws():
    """A missing gloss degrades silently to '(...)'-less text (`why = ""` when
    `glosses.get(target, "")` is empty) -- catch that instead of letting a
    thin card pass. 200 draws per node is enough to hit both labels in every
    2-category table with overwhelming probability; a 4-category table
    (animals) needs more, hence the higher count there specifically."""
    ig = ItemGenerator(generators=SCIENCE_GENERATORS, rng=random.Random(44))
    for node_id in SCIENCE_GENERATORS:
        n_draws = 400 if node_id == "classify_animals" else 150
        for _ in range(n_draws):
            item = ig.sample(node_id)
            answer_line = item.method_steps[2]
            assert " (" in answer_line and answer_line.rstrip().endswith(")"), (
                node_id, answer_line,
            )


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
