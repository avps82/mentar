"""Generic (board-agnostic) Science generators, shared across country packs.

Third subject to follow the pattern `generic_items.py` (maths) set and
`generic_english_items.py` mirrored: SG_GENERIC/US_GENERIC/IN_GENERIC all teach
the same universally-taught primary/lower-secondary science progression — living
things and life cycles, materials and changes of state, forces, energy, cells —
at roughly equivalent ages, so the progression lives ONCE here keyed by
difficulty STAGE (2-8) and reuses PACK_LEVELS from generic_items.py for the level
names/prefixes/stage mapping. Before this (2026-08-14) the three generic packs
shipped maths and English only: science existed for AU alone.

Every generator is REUSED from `science_items.py` (already tested, already
shipped as AU content) — this file adds zero new item logic, and the stage table
is DERIVED from that module's per-year dicts rather than re-listing them, so a
generic level and its AU counterpart cannot drift apart. The "au<n>_science_"
prefix in those keys records where the content was first authored, not an
AU-specific claim; `tests/engine/test_generic_pack_coverage.py` pins each generic
level's node labels to the AU template of the same stage.

item_source name is "<prefix>_science" (e.g. "sg_p3_science"), and node ids are
"<prefix>_<slug>" with the au<n>_science_ prefix stripped (e.g. "sg_p3_habitats")
— distinct from the maths and English slugs under the same level prefix, so
nothing collides (enforced by
tests/engine/test_template_catalog.py::test_no_skill_id_collides_across_any_shipped_template).
"""

from __future__ import annotations

import re

from mentar.engine.generic_items import PACK_LEVELS
from mentar.engine.itemgen import GenFn
from mentar.engine.science_items import (
    AU_SCIENCE_YEAR3_GENERATORS,
    AU_SCIENCE_YEAR4_GENERATORS,
    AU_SCIENCE_YEAR5_GENERATORS,
    AU_SCIENCE_YEAR6_GENERATORS,
    AU_SCIENCE_YEAR7_GENERATORS,
    AU_SCIENCE_YEAR8_GENERATORS,
    SCIENCE_GENERATORS,
)

_AU_PREFIX = re.compile(r"^au\d+_science_")


def _slugs(generators: dict[str, GenFn]) -> dict[str, GenFn]:
    """Re-key an AU year's dict to bare concept slugs, e.g.
    au4_science_food_chain_roles -> food_chain_roles. Derived, not re-listed:
    the AU dict stays the single source of what a stage teaches."""
    return {_AU_PREFIX.sub("", key): fn for key, fn in generators.items()}


# Stage 2 has no AU_SCIENCE_YEAR2_GENERATORS dict of its own -- AU Year 2's
# template draws from the whole SCIENCE_GENERATORS pool -- so its three concepts
# are named here explicitly, from that pool.
_STAGE_2_KEYS = ("au2_science_sound", "au2_science_solar_system", "au2_science_materials")

# Difficulty STAGE -> {concept slug: generator}. Same stability rule as the maths
# and English tables: a renamed slug orphans that skill's mastery rows in the DB.
STAGE_CONCEPTS: dict[int, dict[str, GenFn]] = {
    2: _slugs({k: SCIENCE_GENERATORS[k] for k in _STAGE_2_KEYS}),
    3: _slugs(AU_SCIENCE_YEAR3_GENERATORS),
    4: _slugs(AU_SCIENCE_YEAR4_GENERATORS),
    5: _slugs(AU_SCIENCE_YEAR5_GENERATORS),
    6: _slugs(AU_SCIENCE_YEAR6_GENERATORS),
    7: _slugs(AU_SCIENCE_YEAR7_GENERATORS),
    8: _slugs(AU_SCIENCE_YEAR8_GENERATORS),
}


def build_generators(prefix: str, stage: int) -> dict[str, GenFn]:
    """One pack-level's node_id -> generator map, e.g. build_generators("sg_p3", 3)
    -> {"sg_p3_life_cycle": ..., "sg_p3_heat_sources": ..., ...}."""
    if stage not in STAGE_CONCEPTS:
        raise KeyError(f"no concept set for stage {stage!r} (have {sorted(STAGE_CONCEPTS)})")
    return {f"{prefix}_{slug}": fn for slug, fn in STAGE_CONCEPTS[stage].items()}


# item_source name -> generators, for every generic pack level.
GENERIC_SCIENCE_ITEM_SOURCES: dict[str, dict[str, GenFn]] = {
    f"{prefix}_science": build_generators(prefix, stage)
    for levels in PACK_LEVELS.values()
    for prefix, _level_name, stage in levels
}
