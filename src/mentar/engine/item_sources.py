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

from mentar.engine.au_items import AU_YEAR3_GENERATORS, AU_YEAR4_GENERATORS
from mentar.engine.itemgen import ARITHMETIC_GENERATORS, DEFAULT_GENERATORS
from mentar.engine.science_items import SCIENCE_GENERATORS


def build_registry(pilot_itembank_path: Path) -> dict[str, dict]:
    """The pilot fractions item bank's path is env-overridable (MENTAR_ITEMBANK
    in web/app.py) -- built as a function, not a module-level constant, so the
    registry always reflects the resolved path at call time."""
    return {
        "pilot_fractions": {"generators": DEFAULT_GENERATORS, "itembank": pilot_itembank_path},
        "arithmetic": {"generators": ARITHMETIC_GENERATORS, "itembank": None},
        "science": {"generators": SCIENCE_GENERATORS, "itembank": None},
        "au_year3": {"generators": AU_YEAR3_GENERATORS, "itembank": None},
        "au_year4": {"generators": AU_YEAR4_GENERATORS, "itembank": None},
    }
