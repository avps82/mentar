"""A drawn count of 1 must not sit beside a hardcoded plural noun.

Maintainer, 2026-08-23, reading live output: "Blue got 1 votes". The pattern is
easy to miss in review because the source looks fine --
`rng.choice([1, 2, 3])` beside the literal string "votes" -- and it is only
wrong on the roll nobody pictures. It was live at 20% of draws in one Year 1
generator and 33% in another.

Worst case found: gen_decimal_place_value built all FOUR mc4 choices from a
digit that can roll 1, so a child read "1 ones / 1 tenths / 1 hundredths /
1 tens" together, in four country packs.

This is a reading app for six-year-olds. Broken agreement in the text a child is
asked to read is a content defect, not a cosmetic one.

    python3 -m pytest tests/engine/test_count_noun_agreement.py
"""
from __future__ import annotations

import importlib
import json
import os
import pathlib
import random
import re
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

# "1 <word>" where <word> is genuinely a plural NOUN. Verified by hand against
# every hit this test produced on 2026-08-23 -- each of these is correct English
# that inflect's singular_noun() misreads:
#   "the digit 1 sits in the tens place"      -- verb
#   "1 lies ON the positive real axis"        -- verb
#   "−1 points along the negative real axis"  -- verb
#   "a spanning tree ... has n − 1 edges"     -- a formula, not a count
#   "cos 0° = 1    cos 60° = 1/2"             -- column alignment in a table
_NOT_A_COUNTED_NOUN = {"sits", "lies", "points", "cos", "sin", "tan", "edges",
                       "is", "was", "has", "its", "this", "less", "plus",
                       "minus", "times", "as"}
_COUNT_ONE = re.compile(r"\b1\s+([A-Za-z][a-z]+)\b")


def _all_generators():
    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "agree.db")
    # isolation: the root conftest already points MENTAR_PACK_STATE at a
    # scratch path. Popping it did the OPPOSITE -- see conftest.py.
    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)
    state = pathlib.Path(tempfile.mkdtemp()) / "pack_state.json"
    state.write_text(
        json.dumps({"enabled": [p["key"] for p in app_mod._all_packs_with_state()]}),
        encoding="utf-8")
    os.environ["MENTAR_PACK_STATE"] = str(state)
    app_mod = importlib.reload(app_mod)
    for skey, subject in app_mod.SUBJECTS.items():
        for node, gen in (subject.get("generators") or {}).items():
            yield skey, node, gen


def test_no_item_says_one_of_a_plural_noun():
    try:
        import flask  # noqa: F401
        import inflect
    except ImportError:
        import pytest
        pytest.skip("flask/inflect not installed")

    from mentar.engine.itemgen import ItemGenerator

    engine = inflect.engine()
    offenders = set()
    for _subject, node, gen in _all_generators():
        for seed in range(25):
            try:
                item = ItemGenerator({node: gen}, rng=random.Random(seed))._make(node)
            except Exception:
                continue
            if item is None:
                continue
            text = " ".join(filter(None, [
                item.problem, item.stem, item.format_hint,
                " ".join(item.choices or ()), " ".join(item.method_steps or ()),
            ]))
            for match in _COUNT_ONE.finditer(text):
                word = match.group(1)
                if word.lower() in _NOT_A_COUNTED_NOUN:
                    continue
                if engine.singular_noun(word):
                    offenders.add(f"{node} seed={seed}: {match.group(0)!r}")
    assert not offenders, (
        "items read '1 <plural>'. Use engine/wording.py's count_noun(n, singular) "
        "rather than hardcoding the plural beside a drawn number:\n"
        + "\n".join(f"  {o}" for o in sorted(offenders)[:15])
    )


_ARTICLE = re.compile(r"\b(a|an)\s+([A-Za-z][A-Za-z-]+)\b")


def test_no_item_uses_the_wrong_indefinite_article():
    """"Which of these is a insect?" -- 25% of animal-classification draws
    (2026-08-23). mc_which_is's template hardcoded "a" and the fact table
    contains a vowel-initial label.

    The rule is asked of inflect rather than of the first letter, because the
    real rule is about SOUND: "an hour", "a use", "a one-way street" are all
    correct and all break a vowel-letter test. Anything inflect itself would
    write differently is the only thing flagged, so this cannot fire on the
    English content that legitimately says "a use".
    """
    try:
        import flask  # noqa: F401
        import inflect
    except ImportError:
        import pytest
        pytest.skip("flask/inflect not installed")

    from mentar.engine.itemgen import ItemGenerator

    engine = inflect.engine()
    offenders = set()
    for _subject, node, gen in _all_generators():
        for seed in range(12):
            try:
                item = ItemGenerator({node: gen}, rng=random.Random(seed))._make(node)
            except Exception:
                continue
            if item is None:
                continue
            text = " ".join(filter(None, [
                item.problem, item.stem, " ".join(item.choices or ()),
            ]))
            for match in _ARTICLE.finditer(text):
                written, noun = match.group(1), match.group(2)
                # Ask about the LOWERCASED word. This content uses capitals for
                # emphasis ("a STRUCTURAL adaptation", "an UNSUPPORTED claim"),
                # and inflect reads an all-caps word as an initialism to be
                # spelled out -- so it wanted "an STRUCTURAL". Genuine short
                # initialisms (DNA, LED) are skipped rather than guessed at.
                if noun.isupper() and len(noun) <= 4:
                    continue
                correct = engine.a(noun.lower()).split()[0]
                if correct.lower() != written.lower():
                    offenders.add(
                        f"{node} seed={seed}: {match.group(0)!r} -> {correct} {noun}")
    assert not offenders, (
        "items use the wrong indefinite article. mc_which_is offers {a_label}, "
        "which carries the article; engine/wording.py::article() for anything "
        "else:\n" + "\n".join(f"  {o}" for o in sorted(offenders)[:15])
    )
