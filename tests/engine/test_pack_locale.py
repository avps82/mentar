"""Country packs must use their own country's spelling.

Maintainer, 2026-08-21, on being shown "centimetres" in an AU node: *"This
spelling is centimeters .. typo... Do we need to do a spell check on the repo?"*
It was not a typo -- that node is ACARA, and "centimetres" is correct Australian
-- but the question found a real bug pointing the other way. `generic_items.py`
and its siblings REUSE the AU generators verbatim, so a US sixth-grader was
asked for an area "in square centimetres", a US chemistry item measured "moles
per litre", and US physics said "aluminium".

This tests the GENERATED ITEMS, not the template text: the templates were the
symptom, the shared generators were the cause, and a template-only check would
have gone green while the pipeline kept emitting British spelling.

Deliberately ONE-DIRECTIONAL. British forms ("centimetre", "aluminium") are
unambiguous, so flagging them in a US pack is safe. The reverse is not: "meter"
is correct British for a gas meter and for poetic meter, so asserting AU/SG/IN
carry no American spelling would fail on legitimate content. That direction is
left unguarded ON PURPOSE rather than shipped as a flaky test -- and the sweep
that found this measured it as clean at 0.
"""
from __future__ import annotations

import pathlib
import random
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.engine.generic_english_items import GENERIC_ENGLISH_ITEM_SOURCES  # noqa: E402
from mentar.engine.generic_items import GENERIC_ITEM_SOURCES  # noqa: E402
from mentar.engine.generic_science_items import GENERIC_SCIENCE_ITEM_SOURCES  # noqa: E402
from mentar.engine.itemgen import ItemGenerator  # noqa: E402
from mentar.engine.locale_text import BRITISH_TO_AMERICAN  # noqa: E402
from mentar.engine.senior_science_items import SENIOR_SCIENCE_ITEM_SOURCES  # noqa: E402

_BRITISH = re.compile(r"\b(" + "|".join(sorted(BRITISH_TO_AMERICAN, key=len, reverse=True)) + r")\b",
                      re.IGNORECASE)


def _us_packs():
    for sources in (GENERIC_ITEM_SOURCES, GENERIC_ENGLISH_ITEM_SOURCES,
                    GENERIC_SCIENCE_ITEM_SOURCES, SENIOR_SCIENCE_ITEM_SOURCES):
        for pack, generators in sources.items():
            if pack.startswith("us_"):
                yield pack, generators


def test_us_packs_never_show_a_child_british_spelling():
    offenders = []
    for pack, generators in _us_packs():
        for node, gen in generators.items():
            for seed in range(3):
                item = ItemGenerator({node: gen}, rng=random.Random(seed))._make(node)
                if item is None:
                    continue
                text = " ".join(filter(None, [
                    item.problem, item.stem, item.answer, item.format_hint,
                    " ".join(item.choices or ()),
                    " ".join(item.method_steps or ()),
                    " ".join(item.visual or ()),
                ]))
                for word in set(m.group(0).lower() for m in _BRITISH.finditer(text)):
                    offenders.append(f"{pack}/{node} seed={seed}: {word!r} -> "
                                     f"{BRITISH_TO_AMERICAN[word]!r}")
    assert not offenders, (
        "US packs are showing British/Australian spelling. These come from the AU "
        "generators the generic packs reuse -- fix by adding the word to "
        "engine/locale_text.py, never by forking the generator:\n"
        + "\n".join(f"  {o}" for o in sorted(set(offenders))[:20])
    )


def test_the_other_packs_keep_their_own_spelling():
    """The transform must be a no-op everywhere except the US packs -- AU, SG and
    IN all use British/Australian spelling, and 'correcting' them would be the
    original complaint made real."""
    from mentar.engine.locale_text import localise

    def gen(_rng):
        return ("int", "int_exact", "area in square centimetres", "4", None, None, None)

    for prefix in ("au11g", "sg_p6", "in_c8"):
        assert localise(gen, prefix) is gen, f"{prefix} must not be rewritten"
    assert localise(gen, "us_g6") is not gen
    assert "centimeters" in localise(gen, "us_g6")(None)[2]
