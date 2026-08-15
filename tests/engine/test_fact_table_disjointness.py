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

    python3 tests/engine/test_fact_table_disjointness.py
"""

from __future__ import annotations

import pathlib
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
    import mentar.engine.au_english_items as english
    import mentar.engine.practice_items as practice
    import mentar.engine.science_items as science
    import mentar.engine.senior_science_items as senior

    for mod in (english, practice, science, senior):
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
