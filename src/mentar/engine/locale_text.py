"""British/Australian → American spelling, for the US country packs.

Why this exists: `generic_items.py` and its English/Science siblings build every
country pack from ONE stage table and REUSE the AU generators verbatim -- "adds
zero new item logic" is the discipline that keeps the packs from drifting apart.
The cost is that AU wording rides along, so a US sixth-grader was asked for an
area "in square centimetres" and a US chemistry item measured "moles per litre"
(found 2026-08-21; the maintainer's call: "use local std for the country pack as
it makes sense").

The alternative was forking the generators per country, which would have
reintroduced exactly the drift that file exists to prevent. One transform at the
one seam where pack identity is known keeps a single source of item logic.

DELIBERATELY AN EXPLICIT WORD LIST, not suffix rules. "-re -> -er" would rewrite
`genre`, `acre` and `are`; "-ise -> -ize" would rewrite `wise` and `promise`. A
list is boring, greppable, and cannot surprise a child mid-question. Words are
added when a pack actually needs one -- the locale test names the list, so an
unlisted word fails loudly rather than shipping silently.
"""

from __future__ import annotations

import re

# British/Australian -> American. Inflections are listed, not derived.
BRITISH_TO_AMERICAN: dict[str, str] = {
    # units — the ones school maths and science actually use
    "metre": "meter", "metres": "meters",
    "centimetre": "centimeter", "centimetres": "centimeters",
    "millimetre": "millimeter", "millimetres": "millimeters",
    "kilometre": "kilometer", "kilometres": "kilometers",
    "litre": "liter", "litres": "liters",
    "millilitre": "milliliter", "millilitres": "milliliters",
    # elements and materials
    "aluminium": "aluminum", "sulphur": "sulfur", "sulphate": "sulfate",
    "sulphide": "sulfide", "sulphuric": "sulfuric",
    # -our
    "colour": "color", "colours": "colors", "coloured": "colored",
    "colourless": "colorless", "behaviour": "behavior", "behaviours": "behaviors",
    "favourite": "favorite", "favourites": "favorites",
    "neighbour": "neighbor", "neighbours": "neighbors",
    "vapour": "vapor", "vapours": "vapors", "odour": "odor", "odours": "odors",
    "flavour": "flavor", "flavours": "flavors", "harbour": "harbor",
    # -re
    "centre": "center", "centres": "centers", "centred": "centered",
    "fibre": "fibre", "fibres": "fibers", "theatre": "theater",
    # -ise / -yse
    "realise": "realize", "realised": "realized", "organise": "organize",
    "organised": "organized", "recognise": "recognize", "recognised": "recognized",
    "summarise": "summarize", "summarised": "summarized",
    "categorise": "categorize", "categorised": "categorized",
    "analyse": "analyze", "analysed": "analyzed", "analysing": "analyzing",
    "fertiliser": "fertilizer", "fertilisers": "fertilizers",
    # other
    "defence": "defense", "offence": "offense", "practise": "practice",
    "grey": "gray", "jewellery": "jewelry", "modelling": "modeling",
    "labelled": "labeled", "labelling": "labeling", "travelled": "traveled",
}
# "fibre" -> "fiber" (the dict above must not map a word to itself)
BRITISH_TO_AMERICAN["fibre"] = "fiber"

_WORD_RE = re.compile(r"\b(" + "|".join(sorted(BRITISH_TO_AMERICAN, key=len, reverse=True)) + r")\b",
                      re.IGNORECASE)


def _match_case(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source[:1].isupper():
        return replacement.capitalize()
    return replacement


def to_american(text: str) -> str:
    """Rewrite British/Australian spellings in *text*, preserving case."""
    return _WORD_RE.sub(lambda m: _match_case(m.group(0),
                                              BRITISH_TO_AMERICAN[m.group(0).lower()]), text)


def _american_item(result: tuple) -> tuple:
    """Rewrite every human-readable field of a generator's tuple.

    Slots 0 and 1 are `answer_type` and `checker` -- identifiers the engine
    dispatches on, never shown to anyone -- so they are left exactly alone.
    Everything from slot 2 on is text a child reads, INCLUDING the answer: if
    the question says "aluminum" then the expected answer has to say "aluminum"
    too, or a US child typing what they were shown is marked wrong. Numbers and
    choice letters contain no British spellings, so they pass through untouched.
    """
    out = list(result)
    for i in range(2, len(out)):
        value = out[i]
        if isinstance(value, str):
            out[i] = to_american(value)
        elif isinstance(value, (list, tuple)):
            out[i] = type(value)(to_american(v) if isinstance(v, str) else v for v in value)
    return tuple(out)


def localise(fn, prefix: str):
    """Wrap *fn* so a US pack's items read in American English.

    Every other pack is returned unchanged and unwrapped -- AU, SG and IN all
    use British/Australian spelling, so for them this is a no-op with no cost.
    """
    if not prefix.startswith("us_"):
        return fn

    def american(rng):
        return _american_item(fn(rng))

    american.__name__ = getattr(fn, "__name__", "generator")
    american.__doc__ = getattr(fn, "__doc__", None)
    return american
