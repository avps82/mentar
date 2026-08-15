"""Docs must not state a CURRENT-STATE fact that the code contradicts.

Docs drift silently: nothing fails when a README says "71 templates" and the repo
ships 142. The 2026-08-15 doc pass found three such claims (README's pack table
and totals, PHASE0_STATUS's live test-suite section, explain_mode_design's problem
statement asserting 0 of 319 nodes have a worked example when 423 now carry cards).

The hard part is that most numbers in these docs are RECORDS, not claims: a
changelog row saying "708 tests green" on 2026-08-11 is correct for that date, and
an "Accept: 568 tests pass" line is evidence for a completed work item. Rewriting
those would falsify the history. So this gate checks only counts that read as
statements about NOW, and treats anything carrying a date, an acceptance verb, or
a hedge as a record.

Test counts are deliberately NOT gated: "N tests pass" is inherently a
point-in-time statement, and a self-referential assertion about the suite's own
size would fight every commit.

    python3 tests/tools/test_doc_current_claims.py
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

_DOCS = [
    p for p in sorted(
        list((REPO_ROOT / "docs").rglob("*.md"))
        + [REPO_ROOT / "README.md", REPO_ROOT / "AGENTS.md", REPO_ROOT / "CLAUDE.md"]
    ) if p.exists()
]

# A number is a RECORD, not a live claim, when its line carries any of these.
_RECORD_MARKERS = (
    "accept", "verified", "superseded", "at time of", "as of", "(was ",
    "originally", "grown to", "then ", "record",
)


def _is_record(line: str) -> bool:
    low = line.lower()
    if re.search(r"20\d\d-\d\d-\d\d", line) or line.lstrip().startswith("| 20"):
        return True
    if any(marker in low for marker in _RECORD_MARKERS):
        return True
    # hedged or partial counts ("~8-10 nodes", "6 of 13", "10 templates + 10 generator sets")
    return bool(re.search(r"~|\bof\b|–|\+", line))


def _truth() -> dict[str, int]:
    """Counts straight from the shipped templates, with every pack enabled."""
    import importlib

    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "docclaims.db")
    os.environ.pop("MENTAR_PACK_STATE", None)
    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)
    state = pathlib.Path(tempfile.mkdtemp()) / "pack_state.json"
    state.write_text(
        json.dumps({"enabled": [p["key"] for p in app_mod._all_packs_with_state()]}),
        encoding="utf-8",
    )
    os.environ["MENTAR_PACK_STATE"] = str(state)
    app_mod = importlib.reload(app_mod)
    return {
        "templates": len(app_mod._all_packs_with_state()),
        "nodes": sum(len(c) for c in app_mod._SUBJECT_CURRICULA.values()),
    }


def test_docs_do_not_state_a_stale_template_or_node_count():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    truth = _truth()
    stale = []
    for doc in _DOCS:
        for i, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            if _is_record(line):
                continue
            for m in re.finditer(r"(\d{2,4})\s+(templates|concept nodes|curriculum nodes)", line):
                count = int(m.group(1))
                want = truth["templates"] if m.group(2) == "templates" else truth["nodes"]
                if count != want:
                    stale.append(
                        f"{doc.relative_to(REPO_ROOT)}:{i} says '{m.group(0)}', "
                        f"the repo ships {want}"
                    )
    assert not stale, (
        "docs state counts the code contradicts (update the doc, or mark the line as a "
        "record with a date / 'as of' / 'Accept'):\n" + "\n".join(f"  {s}" for s in stale)
    )


if __name__ == "__main__":
    test_docs_do_not_state_a_stale_template_or_node_count()
    print("  ✓ test_docs_do_not_state_a_stale_template_or_node_count")
