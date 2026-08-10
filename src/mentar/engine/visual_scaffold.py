"""Visual scaffold loader — keyword-routes a concept label to a short OKF
scaffold snippet (curriculum/visual_scaffolds/), so the question/help prompt
gets a compact, topic-specific visual hint instead of the whole bundle.

Lives in engine/ alongside curriculum.py (same no-Flask-dependency reason).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

# Template `subject:` front-matter values -> visual_scaffolds/ subdirectory name.
# Subjects with no scaffold directory yet (e.g. "science") simply find no files
# and _load_visual_scaffold falls back to "".
_SUBJECT_TO_SCAFFOLD_DIR = {
    "mathematics": "maths",
    "maths": "maths",
    "english": "english",
    "science": "science",
}

_RESERVED_NAMES = {"index.md", "log.md"}


def _split_frontmatter(text: str) -> tuple[dict, str]:
    parts = text.split("\n---\n", maxsplit=1)
    if len(parts) != 2:
        return {}, text
    raw = yaml.safe_load(parts[0].removeprefix("---\n")) or {}
    return raw, parts[1].lstrip("\n")


@lru_cache(maxsize=8)
def _scan_scaffold_dir(scaffold_dir: str) -> tuple[tuple[tuple[str, ...], str], ...]:
    """Every (topic_keywords, body) pair found under one subject subdirectory,
    cached per directory so repeated turns don't re-read/re-parse disk."""
    d = Path(scaffold_dir)
    if not d.is_dir():
        return ()
    entries = []
    for path in sorted(d.glob("*.md")):
        if path.name in _RESERVED_NAMES:
            continue
        meta, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        keywords = tuple(str(k).lower() for k in meta.get("topic_keywords", []))
        if keywords:
            entries.append((keywords, body))
    return tuple(entries)


def load_visual_scaffold(scaffold_root: Path, subject: str, label: str) -> str:
    """Return the body of the scaffold file whose `topic_keywords` best match
    *label* (case-insensitive substring), or "" if none match / the subject
    has no scaffold directory yet.

    E1 Finding 2 fix (2026-08-10): MOST keywords matched wins, not first match
    in alphabetical filename order. "Adding fractions with the same denominator"
    matches addition_subtraction.md on 1 keyword ("adding") but fractions.md on
    3 ("fraction", "fractions", "denominator") — the more subject-specific
    scaffold matches more of the label, so counting is the tie-break the old
    first-match scan lacked (it always returned addition_subtraction.md purely
    because 'a' sorts before 'f'). Equal counts keep alphabetical order (stable,
    deterministic)."""
    subdir = _SUBJECT_TO_SCAFFOLD_DIR.get(subject)
    if subdir is None:
        return ""
    label_lower = label.lower()
    scaffold_dir = str(Path(scaffold_root) / subdir)
    best_body, best_count = "", 0
    for keywords, body in _scan_scaffold_dir(scaffold_dir):
        count = sum(1 for kw in keywords if kw in label_lower)
        if count > best_count:
            best_body, best_count = body, count
    return best_body
