"""Named item-source registry (R3.1).

Curriculum templates are self-describing data (front matter: label, icon,
description, year_level, subject...), but the parametric item GENERATORS are
code -- a template can't carry Python functions in YAML. So a template names
its item source by a short string (the `item_source:` front-matter key) and
this registry resolves that name to the actual generators + optional item
bank.

Adding a new template that reuses existing generators: reference an existing
name below in the template's `item_source:` field, nothing to add here.
Adding a template with NEW generators: write the generator module (see
engine/itemgen.py / engine/science_items.py / engine/au_items.py for the
GenFn contract), then add one entry here naming it. web/app.py fails loudly
at startup if a template names an item_source not in this dict.
"""

from __future__ import annotations

from pathlib import Path

from mentar.engine.au_english_items import (
    AU_ENGLISH_YEAR2_GENERATORS,
    AU_ENGLISH_YEAR3_GENERATORS,
    AU_ENGLISH_YEAR4_GENERATORS,
    AU_ENGLISH_YEAR5_GENERATORS,
    AU_ENGLISH_YEAR6_GENERATORS,
    AU_ENGLISH_YEAR7_GENERATORS,
    AU_ENGLISH_YEAR8_GENERATORS,
    AU_ENGLISH_YEAR9_GENERATORS,
    AU_ENGLISH_YEAR10_GENERATORS,
)
from mentar.engine.au_items import (
    AU_YEAR2_GENERATORS,
    AU_YEAR3_GENERATORS,
    AU_YEAR4_GENERATORS,
    AU_YEAR5_GENERATORS,
    AU_YEAR6_GENERATORS,
    AU_YEAR7_GENERATORS,
    AU_YEAR8_GENERATORS,
    AU_YEAR9_GENERATORS,
    AU_YEAR10_GENERATORS,
)
from mentar.engine.au_senior_english_items import (
    AU_ESSENTIAL_ENGLISH_Y11_GENERATORS,
    AU_ESSENTIAL_ENGLISH_Y12_GENERATORS,
    AU_LITERATURE_Y11_GENERATORS,
    AU_LITERATURE_Y12_GENERATORS,
    AU_MAINSTREAM_ENGLISH_Y11_GENERATORS,
    AU_MAINSTREAM_ENGLISH_Y12_GENERATORS,
)
from mentar.engine.au_senior_maths_items import (
    AU_ESSENTIAL_Y11_GENERATORS,
    AU_ESSENTIAL_Y12_GENERATORS,
    AU_GENERAL_Y11_GENERATORS,
    AU_GENERAL_Y12_GENERATORS,
)
from mentar.engine.au_senior_maths_ms_items import (
    AU_METHODS_Y11_GENERATORS,
    AU_METHODS_Y12_GENERATORS,
    AU_SPECIALIST_Y11_GENERATORS,
    AU_SPECIALIST_Y12_GENERATORS,
)
from mentar.engine.generic_english_items import GENERIC_ENGLISH_ITEM_SOURCES
from mentar.engine.generic_items import GENERIC_ITEM_SOURCES
from mentar.engine.generic_science_items import GENERIC_SCIENCE_ITEM_SOURCES
from mentar.engine.in_generic_items import IN_GENERIC_MATHS_GENERATORS
from mentar.engine.itemgen import ARITHMETIC_GENERATORS, DEFAULT_GENERATORS
from mentar.engine.practice_items import ENGLISH_PRACTICE_GENERATORS, MATHS_PRACTICE_GENERATORS
from mentar.engine.science_items import (
    AU_SCIENCE_YEAR3_GENERATORS,
    AU_SCIENCE_YEAR4_GENERATORS,
    AU_SCIENCE_YEAR5_GENERATORS,
    AU_SCIENCE_YEAR6_GENERATORS,
    AU_SCIENCE_YEAR7_GENERATORS,
    AU_SCIENCE_YEAR8_GENERATORS,
    AU_SCIENCE_YEAR9_GENERATORS,
    AU_SCIENCE_YEAR10_GENERATORS,
    SCIENCE_GENERATORS,
)
from mentar.engine.senior_science_items import SENIOR_SCIENCE_ITEM_SOURCES


def build_registry(pilot_itembank_path: Path) -> dict[str, dict]:
    """The pilot fractions item bank's path is env-overridable (MENTAR_ITEMBANK
    in web/app.py) -- built as a function, not a module-level constant, so the
    registry always reflects the resolved path at call time."""
    return {
        "pilot_fractions": {"generators": DEFAULT_GENERATORS, "itembank": pilot_itembank_path},
        "arithmetic": {"generators": ARITHMETIC_GENERATORS, "itembank": None},
        "science": {"generators": SCIENCE_GENERATORS, "itembank": None},
        "au_science_year2": {"generators": SCIENCE_GENERATORS, "itembank": None},
        "au_science_year3": {"generators": AU_SCIENCE_YEAR3_GENERATORS, "itembank": None},
        "au_science_year4": {"generators": AU_SCIENCE_YEAR4_GENERATORS, "itembank": None},
        "au_science_year5": {"generators": AU_SCIENCE_YEAR5_GENERATORS, "itembank": None},
        "au_science_year6": {"generators": AU_SCIENCE_YEAR6_GENERATORS, "itembank": None},
        "au_science_year7": {"generators": AU_SCIENCE_YEAR7_GENERATORS, "itembank": None},
        "au_science_year8": {"generators": AU_SCIENCE_YEAR8_GENERATORS, "itembank": None},
        # 2026-08-14: AU science reached Year 8 while AU maths reached Year 12.
        # Years 9-10 are still a single "Science" subject in the AU curriculum;
        # Years 11-12 stop deliberately (senior science splits into Physics /
        # Chemistry / Biology -- see science_items.py's note).
        "au_science_year9": {"generators": AU_SCIENCE_YEAR9_GENERATORS, "itembank": None},
        "au_science_year10": {"generators": AU_SCIENCE_YEAR10_GENERATORS, "itembank": None},
        # Senior maths, split by course (maintainer 2026-08-20) -- the
        # senior-science precedent applied to maths. See au_senior_maths_items.
        "au11_essential": {"generators": AU_ESSENTIAL_Y11_GENERATORS, "itembank": None},
        "au12_essential": {"generators": AU_ESSENTIAL_Y12_GENERATORS, "itembank": None},
        "au11_general": {"generators": AU_GENERAL_Y11_GENERATORS, "itembank": None},
        "au12_general": {"generators": AU_GENERAL_Y12_GENERATORS, "itembank": None},
        "au_year2": {"generators": AU_YEAR2_GENERATORS, "itembank": None},
        "au_year3": {"generators": AU_YEAR3_GENERATORS, "itembank": None},
        "au_year4": {"generators": AU_YEAR4_GENERATORS, "itembank": None},
        "au_year5": {"generators": AU_YEAR5_GENERATORS, "itembank": None},
        "au_year6": {"generators": AU_YEAR6_GENERATORS, "itembank": None},
        "au_year7": {"generators": AU_YEAR7_GENERATORS, "itembank": None},
        "au_year8": {"generators": AU_YEAR8_GENERATORS, "itembank": None},
        "au_year9": {"generators": AU_YEAR9_GENERATORS, "itembank": None},
        "au_year10": {"generators": AU_YEAR10_GENERATORS, "itembank": None},
        "au11_methods": {"generators": AU_METHODS_Y11_GENERATORS, "itembank": None},
        "au12_methods": {"generators": AU_METHODS_Y12_GENERATORS, "itembank": None},
        "au11_specialist": {"generators": AU_SPECIALIST_Y11_GENERATORS, "itembank": None},
        "au12_specialist": {"generators": AU_SPECIALIST_Y12_GENERATORS, "itembank": None},
        "au_english_year2": {"generators": AU_ENGLISH_YEAR2_GENERATORS, "itembank": None},
        "au_english_year3": {"generators": AU_ENGLISH_YEAR3_GENERATORS, "itembank": None},
        "au_english_year4": {"generators": AU_ENGLISH_YEAR4_GENERATORS, "itembank": None},
        "au_english_year5": {"generators": AU_ENGLISH_YEAR5_GENERATORS, "itembank": None},
        "au_english_year6": {"generators": AU_ENGLISH_YEAR6_GENERATORS, "itembank": None},
        "au_english_year7": {"generators": AU_ENGLISH_YEAR7_GENERATORS, "itembank": None},
        "au_english_year8": {"generators": AU_ENGLISH_YEAR8_GENERATORS, "itembank": None},
        # 2026-08-14: AU English reached Year 8 while AU maths reached Year 12.
        # English stays one subject through Year 12, so it extends cleanly.
        "au_english_year9": {"generators": AU_ENGLISH_YEAR9_GENERATORS, "itembank": None},
        "au_english_year10": {"generators": AU_ENGLISH_YEAR10_GENERATORS, "itembank": None},
        "au11_essential_english": {"generators": AU_ESSENTIAL_ENGLISH_Y11_GENERATORS, "itembank": None},
        "au12_essential_english": {"generators": AU_ESSENTIAL_ENGLISH_Y12_GENERATORS, "itembank": None},
        "au11_mainstream_english": {"generators": AU_MAINSTREAM_ENGLISH_Y11_GENERATORS, "itembank": None},
        "au12_mainstream_english": {"generators": AU_MAINSTREAM_ENGLISH_Y12_GENERATORS, "itembank": None},
        "au11_literature": {"generators": AU_LITERATURE_Y11_GENERATORS, "itembank": None},
        "au12_literature": {"generators": AU_LITERATURE_Y12_GENERATORS, "itembank": None},
        "maths_practice": {"generators": MATHS_PRACTICE_GENERATORS, "itembank": None},
        "english_practice": {"generators": ENGLISH_PRACTICE_GENERATORS, "itembank": None},
        # IN_GENERIC ships in-repo under curriculum/templates/ like every other
        # pack (R10 -- a family toggles it on/off from Settings, no download).
        "in_generic_maths": {"generators": IN_GENERIC_MATHS_GENERATORS, "itembank": None},
        # Generic (board-agnostic) packs — SG/US/IN levels built from ONE shared
        # concept-progression table (engine/generic_items.py). Spread rather than
        # listed one-by-one: 20 entries whose contents are already defined there,
        # so hand-listing them here would be a second place to drift.
        **{
            name: {"generators": gens, "itembank": None}
            for name, gens in GENERIC_ITEM_SOURCES.items()
        },
        # Generic English packs — same reuse discipline, mirrored from AU English
        # generators (engine/generic_english_items.py) instead of AU maths.
        **{
            name: {"generators": gens, "itembank": None}
            for name, gens in GENERIC_ENGLISH_ITEM_SOURCES.items()
        },
        # Senior science (2026-08-15): Physics / Chemistry / Biology as SEPARATE
        # subjects at senior level, for AU, India and Singapore. Junior years stay
        # combined; senior years do not, because that is what a student enrols in.
        **{
            name: {"generators": gens, "itembank": None}
            for name, gens in SENIOR_SCIENCE_ITEM_SOURCES.items()
        },
        # Generic Science packs (2026-08-14) — third subject on the same shared
        # stage table, reusing engine/science_items.py's already-shipped AU
        # generators. Before this, science existed for AU only.
        **{
            name: {"generators": gens, "itembank": None}
            for name, gens in GENERIC_SCIENCE_ITEM_SOURCES.items()
        },
    }
