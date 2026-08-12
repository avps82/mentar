"""Visual scaffold loader — keyword-routes a concept label to a short OKF
scaffold snippet (curriculum/visual_scaffolds/), so the question/help prompt
gets a compact, topic-specific visual hint instead of the whole bundle.

Lives in engine/ alongside curriculum.py (same no-Flask-dependency reason).
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

# explain-mode (2026-08-13, Phase 3a — docs/design/explain_mode_design.md Tier 1
# science visuals): the FIRST fenced ``` block in a scaffold body, verbatim.
_FIRST_FENCE_RE = re.compile(r"```[^\n]*\n(.*?)\n```", re.S)

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


def first_diagram(scaffold_body: str) -> str | None:
    """The FIRST fenced ``` block in a scaffold body, verbatim, or None.

    Scaffold bodies are authored FOR AN LLM to choose from and weave into
    prose -- "use ONE of these visual structures", multiple alternative
    diagrams, a trailing "Guidelines for the question text" section aimed at
    the model, not a child. None of that is fit to show a child directly.

    Explain-mode's bare-card path (2026-08-13, Phase 3a) needs the opposite:
    deterministic, LLM-free, child-facing text -- so this extracts just the
    diagram, dropping every instruction and every alternative after the
    first. Spot-checked across the full science scaffold set: the first
    fenced block is consistently the strongest, most self-contained diagram
    in every file (the author's own natural lead choice), so "first" is not
    an arbitrary pick -- it is not, however, a substitute for a maintainer's
    eyes on the actual rendered result (same render-verification discipline
    §3's SVG rules state for Tier 2 -- ASCII in a `<pre>` has no layout
    engine to introduce NEW defects the source can't already show, but a
    diagram nobody has looked at rendered is still not verified praise)."""
    m = _FIRST_FENCE_RE.search(scaffold_body)
    return m.group(1) if m else None
