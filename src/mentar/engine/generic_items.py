"""Generic (board-agnostic) maths generators, shared across country packs.

Why this module exists: `SG_GENERIC`, `US_GENERIC` and `IN_GENERIC` all teach the
SAME universally-taught maths progression — place value, the four operations,
fractions, decimals, percentages, early algebra — because that progression is
genuinely common across national systems at roughly equivalent ages. Only the
LEVEL NAMES differ ("Primary 3" / "Grade 3" / "Class 3"). None of these packs
claims alignment to any authority's syllabus (their licences don't permit it —
see docs/CONTENT_LICENSES.md §2b for Singapore MOE, India's three boards and US
Common Core), so there is no per-country content to diverge on.

So the concept progression lives ONCE here, keyed by a neutral difficulty STAGE
(2-8), and each pack's generator dict is built from it with that pack's node-id
prefix. Adding a country = one line in PACK_LEVELS, not another hand-copied set
of dicts that can silently drift.

Every generator is REUSED from the existing, already-tested modules — this file
adds zero new item logic, exactly the discipline `in_generic_items.py` set for
the original Class-3 pack. `engine/au_items.py` keeps its own AU_YEARn dicts
(they carry ACARA code comments and a claimed alignment this file deliberately
does not).

Node ids are prefixed per pack+level and are therefore collision-free across
every shipped template (enforced by
tests/engine/test_template_catalog.py::test_no_skill_id_collides_across_any_shipped_template).
"""

from __future__ import annotations

from mentar.engine.au_items import (
    gen_add_sub_decimals,
    gen_add_within_100,
    gen_add_within_1000,
    gen_area_perimeter,
    gen_decimal_place_value,
    gen_div_decimal_by_decimal,
    gen_div_decimals,
    gen_division_facts,
    gen_division_remainder_as_decimal,
    gen_division_remainder_as_fraction,
    gen_fraction_decimal_equiv,
    gen_halves_quarters,
    gen_integers_add_sub,
    gen_mult_decimal_by_decimal,
    gen_mult_decimals,
    gen_mult_facts_2_5_10,
    gen_mult_facts_3_4_5_10,
    gen_mult_facts_to_10x10,
    gen_mult_fraction_whole,
    gen_negative_multiplication,
    gen_negative_numbers,
    gen_one_step_equations,
    gen_order_of_operations,
    gen_order_of_ops_negatives,
    gen_percentage_change,
    gen_percentage_of_quantity,
    gen_place_value_2digit,
    gen_place_value_3digit,
    gen_place_value_4digit,
    gen_squares,
    gen_sub_within_100,
    gen_sub_within_1000,
    gen_two_step_equations,
    gen_unlike_denom_fractions,
)
from mentar.engine.itemgen import (
    GenFn,
    _gen_adding_equal_denom,
    _gen_equivalent_fractions,
    _gen_fraction_as_part_of_whole,
    _gen_unit_fractions,
    _gen_whole_number_division,
)

# Difficulty STAGE -> {concept slug: generator}. The slug becomes the node id's
# suffix (prefix added per pack+level below), so slugs must stay stable once a
# pack ships — a renamed slug orphans that skill's mastery rows in the DB.
STAGE_CONCEPTS: dict[int, dict[str, GenFn]] = {
    2: {
        "place_value": gen_place_value_2digit,
        "addition": gen_add_within_100,
        "subtraction": gen_sub_within_100,
        "mult_facts": gen_mult_facts_2_5_10,
        "halves_quarters": gen_halves_quarters,
    },
    3: {
        "place_value": gen_place_value_3digit,
        "addition": gen_add_within_1000,
        "subtraction": gen_sub_within_1000,
        "mult_facts": gen_mult_facts_3_4_5_10,
        "unit_fractions": _gen_unit_fractions,
        "fraction_of_whole": _gen_fraction_as_part_of_whole,
    },
    4: {
        "place_value": gen_place_value_4digit,
        "mult_facts": gen_mult_facts_to_10x10,
        "division_facts": gen_division_facts,
        "sharing_division": _gen_whole_number_division,
        "equivalent_fractions": _gen_equivalent_fractions,
        "adding_fractions": _gen_adding_equal_denom,
    },
    5: {
        "decimal_place_value": gen_decimal_place_value,
        "add_sub_decimals": gen_add_sub_decimals,
        "mult_fraction_whole": gen_mult_fraction_whole,
        "percentage_of_quantity": gen_percentage_of_quantity,
        "negative_numbers": gen_negative_numbers,
        "division_remainder_fraction": gen_division_remainder_as_fraction,
        "division_remainder_decimal": gen_division_remainder_as_decimal,
    },
    6: {
        "order_of_operations": gen_order_of_operations,
        "mult_decimals": gen_mult_decimals,
        "div_decimals": gen_div_decimals,
        "area_perimeter": gen_area_perimeter,
        "fraction_decimal_equiv": gen_fraction_decimal_equiv,
    },
    7: {
        "integers_add_sub": gen_integers_add_sub,
        "order_of_ops_negatives": gen_order_of_ops_negatives,
        "unlike_denom_fractions": gen_unlike_denom_fractions,
        "one_step_equations": gen_one_step_equations,
        "mult_decimal_by_decimal": gen_mult_decimal_by_decimal,
    },
    8: {
        "two_step_equations": gen_two_step_equations,
        "squares": gen_squares,
        "negative_multiplication": gen_negative_multiplication,
        "percentage_change": gen_percentage_change,
        "div_decimal_by_decimal": gen_div_decimal_by_decimal,
    },
}

# pack key -> [(node-id prefix, level display name, stage), ...].
#
# Level->stage mapping is deliberately CONSERVATIVE and approximate: these packs
# claim no alignment, so a stage is "roughly this difficulty," never "this is
# what <country> teaches in <year>". Real systems differ in pacing (Singapore
# primary maths is widely regarded as running ahead of most), which is exactly
# why claimed alignment would need the licence clearance none of these have.
# India Class 3 is absent here: it shipped earlier with its own un-prefixed node
# ids (in_generic_items.py) and keeps them — renaming would orphan live mastery
# rows for no benefit.
PACK_LEVELS: dict[str, list[tuple[str, str, int]]] = {
    "SG_GENERIC": [
        ("sg_p2", "Primary 2", 2),
        ("sg_p3", "Primary 3", 3),
        ("sg_p4", "Primary 4", 4),
        ("sg_p5", "Primary 5", 5),
        ("sg_p6", "Primary 6", 6),
        ("sg_s1", "Secondary 1", 7),
        ("sg_s2", "Secondary 2", 8),
    ],
    "US_GENERIC": [
        ("us_g2", "Grade 2", 2),
        ("us_g3", "Grade 3", 3),
        ("us_g4", "Grade 4", 4),
        ("us_g5", "Grade 5", 5),
        ("us_g6", "Grade 6", 6),
        ("us_g7", "Grade 7", 7),
        ("us_g8", "Grade 8", 8),
    ],
    "IN_GENERIC": [
        ("in_c2", "Class 2", 2),
        ("in_c4", "Class 4", 4),
        ("in_c5", "Class 5", 5),
        ("in_c6", "Class 6", 6),
        ("in_c7", "Class 7", 7),
        ("in_c8", "Class 8", 8),
    ],
}


def build_generators(prefix: str, stage: int) -> dict[str, GenFn]:
    """One pack-level's node_id -> generator map, e.g. build_generators("sg_p3", 3)
    -> {"sg_p3_place_value": gen_place_value_3digit, ...}."""
    if stage not in STAGE_CONCEPTS:
        raise KeyError(f"no concept set for stage {stage!r} (have {sorted(STAGE_CONCEPTS)})")
    return {f"{prefix}_{slug}": fn for slug, fn in STAGE_CONCEPTS[stage].items()}


# item_source name -> generators, for every generic pack level. The item_source
# name a template carries is "<prefix>_maths" (e.g. "sg_p3_maths").
GENERIC_ITEM_SOURCES: dict[str, dict[str, GenFn]] = {
    f"{prefix}_maths": build_generators(prefix, stage)
    for levels in PACK_LEVELS.values()
    for prefix, _level_name, stage in levels
}
