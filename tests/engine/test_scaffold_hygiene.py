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
