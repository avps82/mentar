"""Count-agreement for child-facing text: "1 apple", not "1 apples".

Why this exists: a generator that hardcodes a plural noun beside a drawn count
is ungrammatical whenever that count rolls 1, and the roll is usually silent --
`rng.choice([1, 2, 3])` reads fine in the source and produces "Blue got 1 votes"
a third of the time (maintainer, 2026-08-23). Found in three generators; the
decimal place-value one shipped all FOUR mc4 choices ungrammatical at once
("1 ones", "1 tenths", "1 hundredths", "1 tens") across four country packs.

This is a reading app for six-year-olds. Modelling broken agreement in the text
a child is asked to read is a content defect, not a cosmetic one.

Uses `inflect`, already a core dependency for exactly this
(docs: English plurals/articles/ordinals). Deliberately NOT a hand-rolled
"+ 's'": the project's standing rule is never to re-implement what an adopted
library covers, and the naive version is wrong on box/boxes, sheep and half.
"""

from __future__ import annotations

import inflect

# One engine for the process: inflect.engine() is not free to construct, and
# item generation calls this on every draw.
_ENGINE = inflect.engine()


def count_noun(count: int | float, noun: str) -> str:
    """"1 apple", "3 apples" -- the count and its noun, agreeing.

    `noun` is given in the SINGULAR; inflect decides the rest, so irregulars
    (box, sheep, half) come out right without a table here.
    """
    return f"{count} {_ENGINE.plural(noun, count)}"


def plural(noun: str, count: int | float) -> str:
    """Just the noun, agreeing with `count` -- for when the number is already
    written elsewhere in the sentence."""
    return _ENGINE.plural(noun, count)
