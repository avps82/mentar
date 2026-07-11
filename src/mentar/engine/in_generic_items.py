"""Generic, board-agnostic India "Class 3 maths" pack -- universally-taught
topics only (place value/addition/subtraction, times tables, basic
fractions). Deliberately reuses existing, already-tested generic generator
functions rather than writing new ones, and carries NO NCERT/CBSE branding,
codes, or claimed curriculum alignment -- NCERT's e-content licence was
found to prohibit adaptation/derivation (see docs/CONTENT_LICENSES.md §2b),
so this pack is careful to stay 100% Mentar-authored/reused-generic
content, never anything derived from NCERT's specific materials.
"""

from __future__ import annotations

from mentar.engine.itemgen import GenFn, _gen_addition, _gen_subtraction, _gen_unit_fractions
from mentar.engine.practice_items import _gen_times_tables

IN_GENERIC_MATHS_GENERATORS: dict[str, GenFn] = {
    "in_generic_addition": _gen_addition,
    "in_generic_subtraction": _gen_subtraction,
    "in_generic_times_tables": _gen_times_tables,
    "in_generic_unit_fractions": _gen_unit_fractions,
}
