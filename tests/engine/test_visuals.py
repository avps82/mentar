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
import re
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
    "au2_length_compare": AU_JUNIOR_MATHS_FILL[2]["au2_length_compare"][0],
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


# Measured 2026-08-21 in headless chromium at a REAL 360px mobile viewport
# (Emulation.setDeviceMetricsOverride -- squeezing a container instead leaves the
# viewport wide, so @media never fires and every number is a fake; that mistake
# was made first and produced a budget 6 characters too generous).
#
# At that width .ascii-art gets a 270px text area at 9.11px a character, so
# exactly 29 CHARACTERS FIT without scrolling. This cap is NOT 29, because the
# shapes that need more are shapes, not sloppiness: a readable clock face is 30
# and a two-way table 35. Those scroll, which is precisely what .ascii-art's
# overflow-x:auto is for, and the alternative -- shrinking the font -- is a bad
# trade for a picture a six-year-old has to read.
#
# So the cap pins the widest shipped picture and catches the absurd. It earned
# its place immediately: the fraction bar was 51 characters at d=10 (four-wide
# cells) while its own docstring claimed it "stays inside a phone's monospace
# width", and the two-way table was 40.
PHONE_COLUMNS = 35


def test_every_question_picture_fits_a_phone_without_scrolling():
    for node, gen in _VISUAL_NODES.items():
        for seed in range(40):
            item = _draw(node, gen, seed)
            if item is None or not item.visual:
                continue
            widest = max(len(line) for line in item.visual)
            assert widest <= PHONE_COLUMNS, (
                f"{node} seed={seed} draws {widest} columns, past the "
                f"{PHONE_COLUMNS} the widest shipped picture needs. Only 29 fit "
                f"a 360px phone unscrolled, so this one is well past a swipe"
            )


def test_a_picture_says_the_same_thing_its_answer_does():
    """The severest failure this feature could have, and the one no other guard
    catches: a picture drawn from different numbers than the answer marks a child
    WRONG for reading it correctly.

    test_a_question_picture_never_asserts_its_own_answer proves the picture does
    not GIVE the answer away. This is the opposite direction -- that the picture
    genuinely ENCODES it. Both are needed: a bar showing 8 cells under the answer
    1/6 passes the give-away guard and is still a broken question.

    Decoded per shape rather than by trusting the renderer, so the assertion is
    independent of the code it checks.
    """
    for seed in range(60):
        item = _draw("unit_fractions", DEFAULT_GENERATORS["unit_fractions"], seed)
        bar = item.visual[0]
        denominator = int(item.answer.split("/")[1])
        assert bar.count("|") - 1 == denominator, f"seed={seed} {item.answer} {bar}"
        assert bar.count("██") == 1, f"seed={seed} not a UNIT fraction: {bar}"

        area = _draw("au4_area_count_squares",
                     AU_JUNIOR_MATHS_FILL[4]["au4_area_count_squares"][0], seed)
        cells = sum(len(re.findall("###", line)) for line in area.visual)
        assert str(cells) == str(area.answer), (
            f"seed={seed} answer is {area.answer} but the grid shows {cells} shaded squares"
        )

        mult = _draw("au2_mult_facts_2_5_10",
                     AU_YEAR2_GENERATORS["au2_mult_facts_2_5_10"], seed)
        rows = [line for line in mult.visual if "*" in line]
        if rows:
            widths = {line.count("*") for line in rows}
            assert len(widths) == 1, f"seed={seed} ragged array: {widths}"
            assert str(len(rows) * widths.pop()) == str(mult.answer), (
                f"seed={seed} answer is {mult.answer} but the array is {len(rows)} rows"
            )

        skip = _draw("au1_skip_count_2s",
                     AU_YEAR1_MATHS_GENERATORS["au1_skip_count_2s"], seed)
        marks = [int(n) for n in re.findall(r"\d+", skip.visual[0])]
        assert all(b - a == 2 for a, b in zip(marks, marks[1:])), (
            f"seed={seed} a COUNT-BY-2s number line that does not step by 2: {marks}"
        )


def test_length_bars_never_lie_about_which_is_longer():
    """Rounding is allowed to distort the RATIO -- the drawing is proportional,
    not literal -- but never the ORDER. Two objects a centimetre apart still have
    to read as different, or the picture contradicts the question.

    Also pins the property that makes proportional scaling worth having: the
    width is the same whether the objects are 5 cm or 100 cm, so no draw can
    scroll off a phone.
    """
    from mentar.engine.visuals import length_bars

    pairs = [(18, 4), (12, 8), (10, 6), (15, 9), (30, 25), (100, 95),
             (21, 20), (7, 6), (5, 1), (2, 1), (99, 98)]
    for longer, shorter in pairs:
        out = length_bars("pencil", longer, "crayon", shorter)
        assert out, f"{longer}/{shorter} drew nothing"
        drawn_long, drawn_short = out[0].count("─"), out[1].count("─")
        assert drawn_long > drawn_short, (
            f"{longer} vs {shorter} drew {drawn_long} and {drawn_short} -- the "
            f"longer object must be visibly longer"
        )
        assert max(len(line) for line in out) == 29, (
            f"{longer}/{shorter} is {max(len(line) for line in out)} cols; the bar's\n"
            f"length is DERIVED from the budget, so the row is 29 whatever the\n"
            f"labels are and however many digits the lengths have"
        )
        # reversed arguments must reverse the picture, not just relabel it
        rev = length_bars("crayon", shorter, "pencil", longer)
        assert rev[1].count("─") > rev[0].count("─")


def test_the_length_picture_deliberately_does_not_encode_its_answer():
    """The opposite of test_a_picture_says_the_same_thing_its_answer_does, and
    the reason that test names its nodes instead of sweeping all of them.

    A fraction bar or an area grid IS the question, so it must encode the answer.
    These bars are SUPPORTIVE: they show what "how much longer" means while the
    numbers stay in the prose. Drawing them in countable centimetre cells would
    let a child read the gap straight off the picture and never subtract -- the
    node would still score, and BKT would record subtraction mastery for
    counting. Proportional scaling removes the unit to count.

    10-vs-6 and 15-vs-9 have the same ratio and so draw identically, which is the
    proof: one picture, two different answers.
    """
    from mentar.engine.visuals import length_bars

    ten_six = length_bars("Pencil", 10, "Crayon", 6)
    fifteen_nine = length_bars("Pencil", 15, "Crayon", 9)
    assert [l.count("─") for l in ten_six] == [l.count("─") for l in fifteen_nine], (
        f"same ratio must draw the same bars: {ten_six} vs {fifteen_nine}"
    )


def test_a_what_comes_next_question_leaves_somewhere_for_the_answer_to_go():
    """Maintainer, 2026-08-21: "This diagram makes no sense."

    The skip-count line was drawn from the first KNOWN value to the last known
    value, so a child asked what follows 6 was looking at a picture that stopped
    at 6. The answer had nowhere to be. Under it sat a row of stray underscores
    -- a `jumps` arc feature whose only caller was this broken draw.

    The line now ends in a `?` cell: one more tick than there are known values,
    and the `?` is never filled in.
    """
    for seed in range(30):
        item = _draw("au1_skip_count_2s",
                     AU_YEAR1_MATHS_GENERATORS["au1_skip_count_2s"], seed)
        labels, rule = item.visual[0], item.visual[1]
        assert labels.rstrip().endswith("?"), f"seed={seed} no slot for the answer: {labels!r}"
        assert item.answer not in labels, f"seed={seed} the picture states the answer"
        assert "_" not in "".join(item.visual), f"seed={seed} stray underscore row is back"
        known = [n for n in re.findall(r"\d+", labels)]
        assert rule.count("+") == len(known) + 1, (
            f"seed={seed} the line has {rule.count('+') - 1} segments for "
            f"{len(known)} known values plus the unknown: {rule!r}"
        )
