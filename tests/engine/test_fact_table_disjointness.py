"""Every mc4 fact table must have categories that are genuinely disjoint.

`itemgen.mc_which_is` builds an item by picking one category as the answer and
drawing distractors from the OTHERS, which is only sound if no option is right
for two categories. When that breaks, a child picks a defensible answer and is
told they are wrong -- the worst failure this app can have, because it teaches
them to distrust their own correct reasoning.

Found for real on 2026-08-15 in senior biology: "carbon dioxide" sat under
"a REACTANT of photosynthesis" while "carbon dioxide and water" sat under "a
PRODUCT of aerobic respiration". Carbon dioxide IS a product of respiration, so
asked for one, a child choosing it was marked wrong. Fixed by naming the process
in each option.

This sweep uses SUBSTRING containment as its proxy: it cannot see semantics, but
the real defect showed up that way, and everything it flags is either a genuine
overlap or a coincidence worth a one-line entry below. New content that trips it
needs a decision, which is the point.

SECOND failure mode, found 2026-08-21 by READING real draws rather than by any
test: Year 1's "comparing things" table held LONGER/SHORTER *and*
HEAVIER/LIGHTER, so "which is the HEAVIER one?" offered "a bus (next to a
pencil)" as a distractor -- filed under LONGER, but a bus IS heavier than a
pencil. Labels disjoint, MEANINGS overlapping, and invisible to a substring
sweep. The fix is structural (one dimension per draw), and the lesson is that
this file is a floor, not a ceiling: new fact tables still need someone to read
what a child would actually see.

    python3 tests/engine/test_fact_table_disjointness.py
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

# Coincidences of spelling, not of meaning: no child could think "ant" is the
# answer to a question about mammals because it hides inside "elephant".
_BENIGN = {
    ("ant", "elephant"),
    ("ice", "juice"),
    ("pea", "pear"),
    ("car", "carrot"),
    ("men", "women"),
    ("carbon", "carbon dioxide (CO2)"),        # element vs compound: the point of the item
    ("grass", "a rabbit eating grass"),        # the option names the rabbit, not the grass
    ("Bb", "the b in Bb"),
    ("BB", "the b in Bb"),
    ("bb", "the b in Bb"),
}


def _fact_tables():
    # Every module holding mc_which_is tables. The list was written when four
    # existed and was never extended, so the content added on 2026-08-21 was
    # invisible to this sweep -- which is part of why the overlaps that day had
    # to be found by reading draws instead.
    import mentar.engine.au_english_items as english
    import mentar.engine.au_junior_english_fill_items as junior_english
    import mentar.engine.au_junior_science_fill_items as junior_science
    import mentar.engine.au_senior_english_items as senior_english
    import mentar.engine.au_year1_items as year1
    import mentar.engine.practice_items as practice
    import mentar.engine.science_items as science
    import mentar.engine.senior_science_depth_items as depth
    import mentar.engine.senior_science_items as senior

    for mod in (english, practice, science, senior, year1, junior_science,
                junior_english, senior_english, depth):
        for name in dir(mod):
            table = getattr(mod, name)
            if not isinstance(table, dict) or not table:
                continue
            if all(isinstance(v, list) and v for v in table.values()):
                yield f"{mod.__name__.split('.')[-1]}.{name}", table


def test_no_option_belongs_to_two_categories():
    overlaps = []
    tables = 0
    for where, table in _fact_tables():
        tables += 1
        members = [(cat, m) for cat, ms in table.items() for m in ms]
        for cat_a, member_a in members:
            for cat_b, member_b in members:
                if cat_a == cat_b or member_a == member_b:
                    continue
                if str(member_a).lower() in str(member_b).lower():
                    if (member_a, member_b) in _BENIGN:
                        continue
                    overlaps.append(f"{where}: {member_a!r} ({cat_a}) inside {member_b!r} ({cat_b})")
    assert tables >= 20, f"expected to sweep the fact tables, saw {tables}"
    assert not overlaps, (
        "an option that fits two categories makes a correct answer look wrong:\n"
        + "\n".join(f"  {o}" for o in dict.fromkeys(overlaps))
    )


if __name__ == "__main__":
    test_no_option_belongs_to_two_categories()
    print("  ✓ test_no_option_belongs_to_two_categories")


def test_year1_comparison_never_mixes_length_with_weight():
    """Regression, 2026-08-21: one table held LONGER/SHORTER and HEAVIER/LIGHTER,
    so "which is the HEAVIER one?" could offer "a bus (next to a pencil)" -- filed
    under LONGER, but genuinely heavier than a pencil. A child reasoning correctly
    was marked wrong. Every draw must now stay on the axis its question asks about."""
    import random

    from mentar.engine.au_year1_items import _Y1_LENGTH, _Y1_WEIGHT, gen_longer_shorter
    from mentar.engine.itemgen import ItemGenerator

    length = {o for v in _Y1_LENGTH.values() for o in v}
    weight = {o for v in _Y1_WEIGHT.values() for o in v}
    assert not (length & weight), "an option appears on both axes"

    problems = []
    for seed in range(120):
        item = ItemGenerator({"n": gen_longer_shorter}, rng=random.Random(seed))._make("n")
        options = set(item.choices)
        if not (options <= length or options <= weight):
            problems.append(f"seed {seed}: options span both axes: {sorted(options)}")
            continue
        correct = item.choices["ABCD".index(str(item.answer))]
        asks_weight = "HEAVIER" in item.stem or "LIGHTER" in item.stem
        if asks_weight != (correct in weight):
            problems.append(f"seed {seed}: {item.stem!r} answered by {correct!r}")
    assert not problems, "\n".join(problems[:5])


# A universal quantifier in a category label ("true of ALL THREE", "true of
# BOTH kinds of cell") means that category's members are ALSO true of the
# sibling categories -- so asked about a sibling, a child picking the shared
# fact is right and marked wrong. Seen three times on 2026-08-21 alone: Year 4
# sun/earth/moon, senior electrochemistry, and (as an overlap of MEMBERS rather
# than labels) Year 1 length-vs-weight.
#
# The pattern is only safe when the sibling labels name the exclusion, as
# electrochemistry now does ("true of a galvanic cell but NOT an electrolytic
# one"). That is exactly what this test requires.
_UNIVERSAL = ("all ", "both ", "any ", "every ", "either ")


def test_no_category_is_a_superset_of_its_siblings():
    problems = []
    for where, table in _fact_tables():
        labels = [str(k) for k in table]
        if len(labels) < 2:
            continue
        # Parentheses hold DEFINITIONS, not claims about the siblings: Newton's
        # THIRD law is glossed "(every action has an equal and opposite
        # reaction)" — that "every" quantifies actions, not categories.
        bare = {c: re.sub(r"\([^)]*\)", "", c).casefold() for c in labels}
        quantified = [c for c in labels
                      if any(u in bare[c] for u in _UNIVERSAL)]
        if not quantified:
            continue
        unguarded = [c for c in labels
                     if c not in quantified and "not" not in c.casefold()]
        if unguarded:
            problems.append(
                f"{where}: {quantified[0]!r} covers its siblings, but "
                f"{unguarded[0]!r} does not exclude it"
            )
    assert not problems, (
        "a category that is true of the others makes a correct answer wrong — "
        "delete it, or name the exclusion in every sibling label:\n  "
        + "\n  ".join(problems)
    )
