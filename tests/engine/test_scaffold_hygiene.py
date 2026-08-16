"""Structural rules for the visual-scaffold library.

Routing picks the scaffold whose `topic_keywords` match a node's label MOST
often, then shows the child that file's FIRST fenced diagram. Two properties
have to hold for that to land on the right picture, and both have been broken in
production:

  1. ONE TOPIC PER FILE. A file holding several diagrams serves its first one to
     every label it wins, so the other topics get the wrong picture. This shape
     has now been found four separate times (English figurative language,
     English grammar, science circuits/waves, maths algebra), including files
     whose own prose says "(use for voice questions)" -- the author knew, but
     first_diagram() cannot read instructions.
  2. UNIQUE KEYWORD OWNERSHIP. When two files claim the same keyword, the tie is
     broken by FILENAME ORDER, so routing silently depends on alphabetics. 44
     such claims existed before this test.

Neither is checkable by reading one file at a time, which is why they kept
coming back. Per-label routing is pinned separately in test_scaffold_coverage.py;
this file guards the structure that makes those pins stable.

    python3 tests/engine/test_scaffold_hygiene.py
"""

from __future__ import annotations

import collections
import pathlib
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

SCAFFOLDS = REPO_ROOT / "curriculum" / "visual_scaffolds"
_SUBJECT_OF_DIR = {"english": "english", "maths": "mathematics", "science": "science"}


def _scaffolds():
    for subdir, subject in _SUBJECT_OF_DIR.items():
        for path in sorted((SCAFFOLDS / subdir).glob("*.md")):
            if path.name == "index.md":
                continue
            raw, body = path.read_text(encoding="utf-8").split("\n---\n", 1)
            yield subdir, subject, path, yaml.safe_load(raw.removeprefix("---\n")), body


def test_every_scaffold_is_usable():
    """Front matter a router can act on, and a diagram a child can be shown."""
    problems = []
    seen = 0
    for subdir, subject, path, meta, body in _scaffolds():
        seen += 1
        where = f"{subdir}/{path.name}"
        if not (meta.get("topic_keywords") or []):
            problems.append(f"{where}: no topic_keywords, so nothing can route to it")
        if meta.get("subject") != subject:
            problems.append(f"{where}: subject={meta.get('subject')!r}, expected {subject!r}")
        if "```" not in body:
            problems.append(f"{where}: no fenced diagram, so first_diagram() returns nothing")
        if not meta.get("description"):
            problems.append(f"{where}: no description (the index is built from it)")
    assert seen >= 90, f"expected the scaffold library, saw {seen} files"
    assert not problems, "\n".join(problems)


def test_no_keyword_is_claimed_by_two_scaffolds():
    """A shared keyword makes routing depend on filename order, not on meaning."""
    clashes = []
    for subdir in _SUBJECT_OF_DIR:
        owners = collections.defaultdict(list)
        for sub, _subject, path, meta, _body in _scaffolds():
            if sub != subdir:
                continue
            for keyword in meta.get("topic_keywords") or []:
                owners[str(keyword).strip().lower()].append(path.name)
        for keyword, files in sorted(owners.items()):
            if len(files) > 1:
                clashes.append(f"{subdir}: {keyword!r} claimed by {files}")
    assert not clashes, (
        "these keywords are claimed twice, so the winner is decided by filename:\n"
        + "\n".join(f"  {c}" for c in clashes)
    )


def test_each_index_lists_every_scaffold_beside_it():
    """The index is how a human finds an existing scaffold instead of writing a
    duplicate -- a file missing from it is effectively invisible."""
    missing = []
    for subdir in _SUBJECT_OF_DIR:
        index = (SCAFFOLDS / subdir / "index.md").read_text(encoding="utf-8")
        for path in sorted((SCAFFOLDS / subdir).glob("*.md")):
            if path.name == "index.md":
                continue
            if f"({path.name})" not in index:
                missing.append(f"{subdir}/index.md does not list {path.name}")
    assert not missing, "\n".join(missing)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} scaffold-hygiene tests passed.")


# ── which diagrams may be folded into a COMPUTED card (2026-08-16) ───────────
# Phase 3a folded a scaffold's first fenced block into the explain-mode card. It
# was spot-checked on SCIENCE, where diagrams are generic, then applied to every
# subject -- so a child asked "In the number 463, what is the value of the digit
# 6?" was shown a place-value table reading 3|5|2, the placeholder numbers from
# curriculum/visual_scaffolds/maths/place_value.md ("WHERE did 352 come from??").
#
# A scaffold is an authoring instruction for the LLM ("use ONE of these visual
# structures"), so its numbers can never match the drawn item. The rule: a
# diagram may be shown beside a computed card only if it is a generic reference
# KEY (declared ```key) or carries no numbers at all.

import re  # noqa: E402

from mentar.engine.visual_scaffold import (  # noqa: E402
    first_diagram,
    first_diagram_is_reference_key,
)


def _may_be_shown(body: str) -> bool:
    d = first_diagram(body)
    return bool(d) and (first_diagram_is_reference_key(body) or not re.search(r"[0-9]", d))


def test_a_worked_example_with_foreign_numbers_is_never_shown():
    """place_value.md's table has 3|5|2 baked in -- a different number from
    whatever the item drew. The card now computes its own table instead
    (au_items._place_value_table)."""
    body = (SCAFFOLDS / "maths" / "place_value.md").read_text(encoding="utf-8")
    assert "Hundreds | Tens | Ones" in first_diagram(body), "precondition: still the table"
    assert not _may_be_shown(body), "a foreign worked example reached a child's card"


def test_a_declared_reference_key_is_shown_even_though_it_has_digits():
    """The first cut inferred this from "does it contain a digit", which was
    about half wrong: it suppressed the BODMAS step list, the probability 0-1
    scale and the chemistry keys, whose digits are step numbers, axis labels and
    chemical formulas. Declared per file instead of guessed."""
    for rel in ("maths/order_of_operations.md", "maths/probability.md",
                "science/bonding_types.md", "english/homophones.md"):
        body = (SCAFFOLDS / rel).read_text(encoding="utf-8")
        assert first_diagram_is_reference_key(body), f"{rel} lost its ```key marker"
        assert _may_be_shown(body), f"{rel} is a reference key and must still be shown"


def test_every_key_marked_scaffold_really_has_a_first_fence():
    """A ```key marker on a file whose first fence moved would silently promote
    the wrong block."""
    for f in sorted(SCAFFOLDS.rglob("*.md")):
        body = f.read_text(encoding="utf-8", errors="replace")
        if first_diagram_is_reference_key(body):
            assert first_diagram(body), f"{f.name}: ```key but no extractable diagram"
