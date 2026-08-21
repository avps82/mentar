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

from mentar.engine.locale_text import to_american

# explain-mode (2026-08-13, Phase 3a — docs/design/explain_mode_design.md Tier 1
# science visuals): the FIRST fenced ``` block in a scaffold body, verbatim.
_FIRST_FENCE_RE = re.compile(r"```[^\n]*\n(.*?)\n```", re.S)

# The fence's INFO STRING, so a scaffold can declare what kind of diagram it is.
# ```key  -> a generic reference key/scale/legend: safe to show a child beside any
#            question, because it illustrates the concept rather than answering a
#            different instance of it.
# (blank) -> unmarked. Treated as a worked EXAMPLE, which must not be folded into
#            a computed card when it carries numbers -- those are a different
#            question's numbers (maintainer, 2026-08-16: "WHERE did 352 come
#            from??" on a place-value table reading 3|5|2 under a question about
#            463). Declared per file rather than guessed: a first cut inferred it
#            from "does the diagram contain a digit", which was about half wrong
#            -- it suppressed the BODMAS step list, the probability 0-1 scale and
#            every chemistry key, whose digits are step numbers, axis labels and
#            chemical formulas.
_FIRST_FENCE_INFO_RE = re.compile(r"```([^\n]*)\n.*?\n```", re.S)


def first_diagram_is_reference_key(scaffold_body: str) -> bool:
    """True when the first fenced block declares itself a generic reference key
    (```key), i.e. safe to show alongside any question on the concept."""
    m = _FIRST_FENCE_INFO_RE.search(scaffold_body or "")
    return bool(m) and m.group(1).strip().lower() == "key"

# Template `subject:` front-matter values -> visual_scaffolds/ subdirectory name.
# Subjects with no scaffold directory yet (e.g. "science") simply find no files
# and _load_visual_scaffold falls back to "".
_SUBJECT_TO_SCAFFOLD_DIR = {
    "mathematics": "maths",
    "maths": "maths",
    "english": "english",
    "science": "science",
    # Senior science splits into three certificate subjects (2026-08-15,
    # engine/senior_science_items.py) but they are still science: one scaffold
    # directory, so a senior physics node can reuse a junior forces scaffold
    # rather than duplicating it under a fourth directory.
    "physics": "science",
    "chemistry": "science",
    "biology": "science",
    "earth_environmental": "science",
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


@lru_cache(maxsize=2048)
def _kw_pattern(keyword: str) -> re.Pattern[str]:
    """A keyword matches on WORD boundaries, tolerating a plural suffix.

    2026-08-15: plain substring matching routed three senior-science nodes to the
    acids-and-bases scaffold, because the keyword "ph" is inside "phenotype",
    "photosynthesis" AND "trophic" -- and sent the electromagnetic spectrum to the
    magnetism scaffold via "magnet" inside "electromagnetic". Every one of those
    would have shown a child the wrong diagram in explain mode.

    Substring matching existed so "fraction" would match "fractions" and
    "multiply" would reach "Multiplying whole numbers", so the fix keeps that:
    bounded on both sides, with a short list of common inflections. Keywords
    that are themselves phrases or contain punctuation still work -- the bound is
    only applied where the keyword's own edge is a word character.
    """
    left = r"(?<![a-z0-9])" if keyword[:1].isalnum() else ""
    # Common inflections only -- NOT an arbitrary suffix, which is what let "ph"
    # match "phenotype". "multiply" must still reach "Multiplying whole numbers".
    right = r"(?:e?s|ing|ed)?(?![a-z0-9])" if keyword[-1:].isalnum() else ""
    return re.compile(left + re.escape(keyword) + right)


def _kw_matches(keyword: str, label_lower: str) -> bool:
    """Match a scaffold keyword against a node label, IGNORING British/American
    spelling on both sides.

    Scaffolds are shared across every country pack, but labels are not: the US
    packs use American spelling (engine/locale_text.py). Renaming one US label
    "Disease and defence" -> "Disease and defense" silently unrouted that node,
    because the scaffold claims the keyword `defence` -- caught by
    test_every_concept_node_has_a_scaffold, 2026-08-21.

    Normalising BOTH sides to one spelling fixes the class rather than that node:
    a US label reaches a British-keyworded scaffold and vice versa, so a scaffold
    never has to list both spellings and a future locale change cannot quietly
    take a picture away from a child.
    """
    if _kw_pattern(keyword).search(label_lower):
        return True
    normalised = to_american(keyword)
    if normalised == keyword:
        return False
    return bool(_kw_pattern(normalised).search(to_american(label_lower)))


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
    because 'a' sorts before 'f'). Equal counts break on CONTAINMENT, and only then on
    alphabetical order (2026-08-21). Counting alone was not enough: "Counting by
    2s" matched year1_counting.md on 'counting' and year1_skip_counting.md on
    'counting by 2s' -- one hit each, so the alphabetical tie-break handed a
    skip-counting question the count-by-ones diagram, a picture teaching the
    wrong method for the question on screen.

    The tie-break is containment, NOT keyword length. Length was tried first and
    is wrong: 'vocabulary' is LONGER than 'synonym' but far more generic, and
    ranking by length sent "Vocabulary -- synonym pairs" to the generic Frayer
    box instead of the synonyms/antonyms diagram. A keyword that strictly
    CONTAINS a rival's keyword is a refinement of it ('counting by 2s' refines
    'counting'), so the file claiming the refinement wins. Where neither
    contains the other the two are merely different, and alphabetical order
    stands exactly as before."""
    subdir = _SUBJECT_TO_SCAFFOLD_DIR.get(subject)
    if subdir is None:
        return ""
    label_lower = label.lower()
    scaffold_dir = str(Path(scaffold_root) / subdir)
    scored = []
    for keywords, body in _scan_scaffold_dir(scaffold_dir):
        matched = [kw for kw in keywords if _kw_matches(kw, label_lower)]
        if matched:
            scored.append((len(matched), matched, body))
    if not scored:
        return ""
    best = max(s[0] for s in scored)
    tied = [s for s in scored if s[0] == best]
    for _count, matched, body in tied:
        others = [kw for c, m, b in tied if b is not body for kw in m]
        if others and all(
            any(other != kw and other in kw for kw in matched) for other in others
        ):
            return body
    return tied[0][2]


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
