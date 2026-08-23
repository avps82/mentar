"""Docs must not name a function that no longer exists.

`tools/check_doc_paths.py` is the same idea for FILE paths, and this is the gap
beside it: a doc can name `_split_turn_text()` forever and nothing notices, even
though the mechanism was replaced and the code that replaced it now says "never
string-split from prose" -- i.e. the doc described the one approach the code
forbids (found 2026-08-23).

Backticked `name(` is an unambiguous claim that a callable exists. Two classes
are deliberately NOT flagged, because both are honest writing:

  * REGISTERS -- dated changelogs and audit records. "handle_trigger() (the
    drifted duplicate) deleted" is a true sentence ABOUT a thing that is gone.
  * lines that say so. A plan offering an optional helper ("implementer's
    choice"), or a superseded paragraph carrying a correction note, is not
    claiming the symbol exists.

    python3 -m pytest tests/tools/test_doc_symbols.py
"""
from __future__ import annotations

import collections
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]

# Real callables that simply are not DEFINED in this repo: stdlib, Flask, sympy,
# and browser/JS APIs that docs legitimately name.
_NOT_DEFINED_HERE = {
    "url_for", "sorted", "open", "getattr", "redirect", "glob", "randint",
    "render_template", "rstrip", "fetch", "sympify", "simplify", "speak",
    "pause", "resume", "generate", "format", "strip", "split", "join",
    "print", "range", "enumerate", "setdefault",
}
# Dated changelogs and audit records: their whole job is describing what changed.
_REGISTERS = {"PHASE0_STATUS.md", "DOC_AUDIT.md", "REMAINDER_PLAN.md",
              "REVIEW_2026-07-03.md", "PHASE0.md"}
# A line that says the thing is gone, optional, or superseded is not a claim.
_DISCLAIMED = re.compile(
    r"superseded|deleted|removed|no longer|does not exist|never (?:created|built)|"
    r"implementer's choice|was replaced|resolved differently|stale",
    re.I)
_CALL = re.compile(r"`([a-z_][a-z0-9_]{3,})\(")


def _defined_symbols() -> set[str]:
    code = []
    for pattern in ("src/**/*.py", "tests/**/*.py", "scripts/*.py", "eval/**/*.py"):
        for path in REPO.glob(pattern):
            code.append(path.read_text(encoding="utf-8", errors="ignore"))
    joined = "\n".join(code)
    return (set(re.findall(r"^\s*def\s+(\w+)", joined, re.M))
            | set(re.findall(r"^\s*class\s+(\w+)", joined, re.M)))


def test_docs_do_not_name_a_function_that_no_longer_exists():
    known = _defined_symbols()
    missing = collections.defaultdict(list)
    for doc in sorted(list(REPO.glob("docs/**/*.md")) + list(REPO.glob("*.md"))):
        if doc.name in _REGISTERS:
            continue
        # Scope the disclaimer to the PARAGRAPH, not a fixed line window: a
        # correction note is appended to the end of the paragraph it corrects,
        # which in UI_REQUIREMENTS is nine lines below the mention.
        text = doc.read_text(encoding="utf-8")
        for block in text.split("\n\n"):
            # Collapse newlines first: markdown wraps prose, and W2.2's
            # "implementer's\nchoice" straddles a line break.
            if _DISCLAIMED.search(" ".join(block.split())):
                continue
            i = text[:text.index(block)].count("\n") if block in text else 0
            for match in _CALL.finditer(block):
                name = match.group(1)
                if name in known or name in _NOT_DEFINED_HERE:
                    continue
                missing[name].append(f"{doc.relative_to(REPO)}:~{i + 1}")
    assert not missing, (
        "docs name functions that do not exist. Either the doc is stale, or it is "
        "describing something removed and should say so:\n"
        + "\n".join(f"  {n}() — {w}" for n, w in sorted(missing.items()))
    )
