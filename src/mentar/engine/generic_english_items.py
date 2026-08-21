"""Generic (board-agnostic) English generators, shared across country packs.

Mirrors `engine/generic_items.py`'s maths pattern exactly: SG_GENERIC/US_GENERIC/
IN_GENERIC all teach the same universally-taught English progression (word
classes, synonyms/antonyms, word-building, figurative language, register) at
roughly equivalent ages, so the concept progression lives ONCE here keyed by
difficulty STAGE (2-8) and reuses PACK_LEVELS from generic_items.py for the
level names/prefixes/stage mapping — one source of truth for both subjects.

Every generator is REUSED from `au_english_items.py` (already tested, already
shipped as AU content) — this file adds zero new item logic. The "AU" in those
function names reflects where they were first authored, not AU-specific
content: same word-table generator shape `engine/au_items.py`'s maths
generators already get reused by in generic_items.py.

item_source name is "<prefix>_english" (e.g. "sg_p3_english"), distinct from
the maths pack's "<prefix>_maths" so both subjects can ship side by side under
the same level prefix without item_source collisions. Node ids use different
slugs per subject (word_classes/synonyms/... vs place_value/addition/...) so
no id collides either (enforced by
tests/engine/test_template_catalog.py::test_no_skill_id_collides_across_any_shipped_template).
"""

from __future__ import annotations

import re

from mentar.engine.au_english_items import (
    AU_ENGLISH_YEAR9_GENERATORS,
    AU_ENGLISH_YEAR10_GENERATORS,
    AU_ENGLISH_YEAR11_GENERATORS,
    AU_ENGLISH_YEAR12_GENERATORS,
    gen_active_passive_y7,
    gen_adjectives_comparative_y3,
    gen_adverbial_phrases_y8,
    gen_antonyms_advanced_y5,
    gen_antonyms_basic_y3,
    gen_antonyms_nuanced_y6,
    gen_clauses_y8,
    gen_common_proper_nouns_y4,
    gen_compound_words_y5,
    gen_connotation_y8,
    gen_contractions_y4,
    gen_figurative_language_y6,
    gen_formal_informal_y7,
    gen_homophones_y3,
    gen_idioms_y7,
    gen_onomatopoeia_y8,
    gen_personification_y7,
    gen_plurals_y2,
    gen_prefixes_y3,
    gen_rhyming_y2,
    gen_similes_basic_y4,
    gen_suffixes_y4,
    gen_synonyms_advanced_y5,
    gen_synonyms_nuanced_y6,
    gen_synonyms_y2,
    gen_word_classes_advanced_y5,
    gen_word_classes_conj_prep_y6,
    gen_word_classes_y2,
)
from mentar.engine.generic_items import PACK_LEVELS
from mentar.engine.itemgen import GenFn
from mentar.engine.locale_text import localise

# Difficulty STAGE -> {concept slug: generator}. Same stability rule as the
# maths table: a renamed slug orphans that skill's mastery rows in the DB.
STAGE_CONCEPTS: dict[int, dict[str, GenFn]] = {
    2: {
        "word_classes": gen_word_classes_y2,
        "synonyms": gen_synonyms_y2,
        "plurals": gen_plurals_y2,
        "rhyming": gen_rhyming_y2,
    },
    3: {
        "antonyms": gen_antonyms_basic_y3,
        "prefixes": gen_prefixes_y3,
        "homophones": gen_homophones_y3,
        "adjectives_comparative": gen_adjectives_comparative_y3,
    },
    4: {
        "suffixes": gen_suffixes_y4,
        "contractions": gen_contractions_y4,
        "proper_nouns": gen_common_proper_nouns_y4,
        "similes": gen_similes_basic_y4,
    },
    5: {
        "synonyms_advanced": gen_synonyms_advanced_y5,
        "antonyms_advanced": gen_antonyms_advanced_y5,
        "word_classes_advanced": gen_word_classes_advanced_y5,
        "compound_words": gen_compound_words_y5,
    },
    6: {
        "figurative_language": gen_figurative_language_y6,
        "synonyms_nuanced": gen_synonyms_nuanced_y6,
        "antonyms_nuanced": gen_antonyms_nuanced_y6,
        "conjunctions_prepositions": gen_word_classes_conj_prep_y6,
    },
    7: {
        "idioms": gen_idioms_y7,
        "formal_informal": gen_formal_informal_y7,
        "active_passive": gen_active_passive_y7,
        "personification": gen_personification_y7,
    },
    8: {
        "connotation": gen_connotation_y8,
        "clauses": gen_clauses_y8,
        "adverbial_phrases": gen_adverbial_phrases_y8,
        "onomatopoeia": gen_onomatopoeia_y8,
    },
}


# Senior stages 9-12 (2026-08-15), derived from AU English's own Year 9-12 dicts
# for the same reason the maths table derives its senior stages: one progression,
# no second copy to drift. AU English node ids are prefixed "aue<n>_".
_AUE_YEAR_PREFIX = re.compile(r"^aue\d+_")

STAGE_CONCEPTS.update({
    stage: {_AUE_YEAR_PREFIX.sub("", k): v for k, v in gens.items()}
    for stage, gens in (
        (9, AU_ENGLISH_YEAR9_GENERATORS),
        (10, AU_ENGLISH_YEAR10_GENERATORS),
        (11, AU_ENGLISH_YEAR11_GENERATORS),
        (12, AU_ENGLISH_YEAR12_GENERATORS),
    )
})


def build_generators(prefix: str, stage: int) -> dict[str, GenFn]:
    """One pack-level's node_id -> generator map, e.g. build_generators("sg_p3", 3)
    -> {"sg_p3_antonyms": gen_antonyms_basic_y3, ...}."""
    if stage not in STAGE_CONCEPTS:
        raise KeyError(f"no concept set for stage {stage!r} (have {sorted(STAGE_CONCEPTS)})")
    # US packs get American spelling (maintainer, 2026-08-21: "use local std
    # for the country pack"). localise() is a no-op for every other prefix.
    return {f"{prefix}_{slug}": localise(fn, prefix)
            for slug, fn in STAGE_CONCEPTS[stage].items()}


# item_source name -> generators, for every generic pack level. The item_source
# name a template carries is "<prefix>_english" (e.g. "sg_p3_english").
GENERIC_ENGLISH_ITEM_SOURCES: dict[str, dict[str, GenFn]] = {
    f"{prefix}_english": build_generators(prefix, stage)
    for levels in PACK_LEVELS.values()
    for prefix, _level_name, stage in levels
}
