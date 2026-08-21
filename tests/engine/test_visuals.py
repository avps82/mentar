"""Question-side pictures: they must show, and must never tell.

Visual-first (2026-08-21, docs/design/visual_first_gap.md): for a "constitutive"
topic the picture IS the question. Two properties have to hold, and only one of
them is obvious:

  1. the picture is DRAWN (a node that should have one, does);
  2. the picture does NOT contain the answer.

(2) is the subtle one and it is a live trap, not a hypothetical. Every ASCII
renderer in this repo was written for the explain CARD, which is shown AFTER an
attempt, so they all end with an answer-bearing summary ("1 of 5 equal parts
shaded = 1/5"). That line is correct there and fatal on the question, where the
child is still thinking. Copying a correct convention across the boundary is
exactly how this would break.

    python3 -m pytest tests/engine/test_visuals.py
"""

from __future__ import annotations

import pathlib
import random
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.engine.au_items import AU_YEAR2_GENERATORS  # noqa: E402
from mentar.engine.au_junior_maths_fill_items import AU_JUNIOR_MATHS_FILL  # noqa: E402
from mentar.engine.au_senior_maths_items import (  # noqa: E402
    gen_correlation_direction,
    gen_shortest_path,
    gen_two_way_table,
)
from mentar.engine.au_year1_items import AU_YEAR1_MATHS_GENERATORS  # noqa: E402
from mentar.engine.itemgen import (  # noqa: E402
    DEFAULT_GENERATORS,
    ItemGenerator,
    _dedup_key,
    _fraction_bar,
)

# Nodes asserted to draw a picture, BY NAME. A generic "some node has one" would
# pass on the wrong source: CompositeItemSource silently falls back to the
# authored item bank for a node the generator does not cover, so the picture
# would simply be absent with no error.
_VISUAL_NODES = {
    "unit_fractions": DEFAULT_GENERATORS["unit_fractions"],
    "au4_area_count_squares": AU_JUNIOR_MATHS_FILL[4]["au4_area_count_squares"][0],
    "au2_time_oclock": AU_JUNIOR_MATHS_FILL[2]["au2_time_oclock"][0],
    "au2_mult_facts_2_5_10": AU_YEAR2_GENERATORS["au2_mult_facts_2_5_10"],
    "au1_skip_count_2s": AU_YEAR1_MATHS_GENERATORS["au1_skip_count_2s"],
    # senior constitutive — these are the ones whose PROSE used to hand over the
    # skill (shortest path was "add 12 vs add 11"; correlation stated the trend)
    "au12e_shortest_path": gen_shortest_path,
    "au11g_two_way_table": gen_two_way_table,
    "au11g_correlation_direction": gen_correlation_direction,
}


def _draw(node: str, gen, seed: int):
    return ItemGenerator({node: gen}, rng=random.Random(seed))._make(node)


def test_named_visual_nodes_actually_draw_a_picture():
    for node, gen in _VISUAL_NODES.items():
        item = _draw(node, gen, 0)
        assert item is not None and item.visual, f"{node} drew no picture"
        assert all(isinstance(line, str) for line in item.visual)


def test_a_question_picture_never_asserts_its_own_answer():
    """The give-away guard.

    Tests the real failure mode, which is an ASSERTION -- the card-side summary
    line "1 of 5 equal parts shaded = 1/5" copied onto the question. It is NOT a
    bare substring check: a clock dial legitimately carries all twelve hour
    numbers, so the answer's digits appearing somewhere in the art proves
    nothing (that false positive was caught by the review tool on the first
    clock render, which is what the review tool is for).

    So the two properties are: no `=` anywhere in a question picture, and no
    line that IS just the answer. Re-add a summary line to any question-side
    renderer and this goes red."""
    leaks = []
    for node, gen in _VISUAL_NODES.items():
        for seed in range(60):
            item = _draw(node, gen, seed)
            if not (item and item.visual):
                continue
            for line in item.visual:
                if "=" in line:
                    leaks.append((node, "asserts with '=':", line))
                    break
                if line.strip() == str(item.answer):
                    leaks.append((node, "line is the answer:", line))
                    break
    assert not leaks, f"picture states the answer: {leaks[:3]}"


def test_the_card_keeps_its_summary_line():
    """The other half: withholding the summary on the QUESTION must not strip it
    from the CARD, where naming the result is the whole point."""
    item = _draw("unit_fractions", DEFAULT_GENERATORS["unit_fractions"], 3)
    assert item.method_steps and item.answer in item.method_steps[-1]


def test_fraction_bar_withholds_its_summary_on_request():
    assert len(_fraction_bar(1, 4)) == 2
    assert len(_fraction_bar(1, 4, summary=False)) == 1
    assert "1/4" not in _fraction_bar(1, 4, summary=False)[0]
    # out-of-range still yields nothing rather than a broken picture
    assert _fraction_bar(1, 99) == ()
    assert _fraction_bar(5, 3) == ()


def test_dedup_key_includes_the_picture():
    """sample()'s no-repeat window keys on this. Visual questions repeat identical
    PROSE while only the picture changes, so prose-only keying made every draw
    look like a repeat and silently killed the guarantee. Revert _dedup_key to
    `item.stem or item.problem` and this goes red."""
    a = _draw("unit_fractions", DEFAULT_GENERATORS["unit_fractions"], 1)
    b = _draw("unit_fractions", DEFAULT_GENERATORS["unit_fractions"], 2)
    if (a.stem or a.problem) == (b.stem or b.problem) and a.visual != b.visual:
        assert _dedup_key(a) != _dedup_key(b), "same key for different pictures"
    # and a picture genuinely changes the key
    same_prose = a.stem or a.problem
    assert _dedup_key(a) != same_prose, "key ignored the picture entirely"


def test_sample_still_varies_when_only_the_picture_differs():
    gen = ItemGenerator(dict(_VISUAL_NODES), rng=random.Random(11))
    pictures = {tuple(gen.sample("unit_fractions").visual) for _ in range(24)}
    assert len(pictures) >= 4, f"only {len(pictures)} distinct pictures in 24 draws"
