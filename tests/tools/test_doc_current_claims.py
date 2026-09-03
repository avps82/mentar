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

# Append-only REGISTERS: every number in them is point-in-time by construction --
# a dated status row, or an audit recording what some doc said when it was read.
# There is no current-state claim to be stale, so scanning them yields only noise
# (6 hits, all records, when the sentence-aware scan below was introduced).
# DOC_AUDIT.md is exempt from tools/check_doc_paths.py for the same reason.
_REGISTERS = {"DOC_AUDIT.md", "PHASE0_STATUS.md"}

_DOCS = [
    p for p in sorted(
        list((REPO_ROOT / "docs").rglob("*.md"))
        + [REPO_ROOT / "README.md", REPO_ROOT / "AGENTS.md", REPO_ROOT / "CLAUDE.md"]
    ) if p.exists() and p.name not in _REGISTERS
]

# A number is a RECORD, not a live claim, when its line carries any of these.
_RECORD_MARKERS = (
    "accept", "verified", "superseded", "at time of", "as of", "(was ",
    "originally", "grown to", "then ", "record",
    # A doc that says it describes something UNBUILT is not claiming current
    # state, whatever it counts. The paragraph-aware scan below surfaced
    # design/year1_12_english_templates_reference.md counting the 10 visual
    # templates in its own proposal -- a different noun from the 157 curriculum
    # templates the repo ships, in a block whose own words are "LOGGED ONLY ...
    # no action requested, no build".
    "logged only", "no action requested", "no build",
)


# ...UNLESS the line says, in the present tense, that this is what ships now. A
# date-stamp on such a line records when the claim was last checked, not that the
# claim is historical -- and reading it as a record is what let README's "**What
# actually ships today** (2026-08-11): **319 concept nodes across 71 curriculum
# templates**" sit there until 2026-08-22, by which point it was 934 across 157.
_CLAIM_MARKERS = (
    "actually ships", "ships today", "shipping today", "shipping now",
    "currently ships", "what ships", "today the repo", "at present",
)


def _is_claim(text: str) -> bool:
    """Says, in the present tense, that this is what ships NOW."""
    low = text.lower()
    return any(marker in low for marker in _CLAIM_MARKERS)


def _is_record(line: str) -> bool:
    low = line.lower()
    if _is_claim(line):
        return False
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
    # isolation: the root conftest already points MENTAR_PACK_STATE at a
    # scratch path. Popping it did the OPPOSITE -- see conftest.py.
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


def _sentences(text: str):
    """Split on sentence ends and markdown table-cell walls.

    A count and the words that qualify it ("as of", "ships today") have to be in
    the same breath to mean anything about each other.
    """
    return [s for s in re.split(r"(?<=[.!?])\s+|\s*\|\s*", text) if s.strip()]


def _paragraphs(text: str):
    """Yield (first-line-number, [lines]) for each blank-line-separated block."""
    block, start = [], 1
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip():
            if not block:
                start = i
            block.append(line)
        elif block:
            yield start, block
            block = []
    if block:
        yield start, block


def test_docs_do_not_state_a_stale_template_or_node_count():
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    truth = _truth()
    stale = []
    for doc in _DOCS:
        # Scan PARAGRAPHS, not lines. Markdown wraps prose, and "across 71
        # curriculum\ntemplates" is one claim split by a newline -- a line-by-line
        # scan sees "71 curriculum" and "templates" separately and matches neither.
        # That is the second reason README's stale count survived this gate.
        for start, block in _paragraphs(doc.read_text(encoding="utf-8")):
            # Classify the SENTENCE carrying each count, not the line and not
            # the whole block.
            #
            # Not the line: markdown wraps prose, so "across 71 curriculum\n
            # templates" is one claim split by a newline and a line scan matches
            # neither half. That is one of two reasons README's stale count
            # survived this gate for months.
            #
            # Not the block either: PHASE0_STATUS.md has single "paragraphs"
            # thousands of words long, where "ships today" in one sentence sat
            # nowhere near a log-only "(16 templates/7 topics)" proposal count in
            # another. Block-wide classification made each of them contaminate
            # the other, in both directions.
            i = start
            sentences = _sentences(" ".join(block))
            for idx, sentence in enumerate(sentences):
                # Precedence, and each clause is here because a real doc needed it:
                #   1. a claim in the count's OWN sentence always wins -- README's
                #      "**What actually ships today**" sits next to a date and a
                #      "+", both of which read as hedging;
                #   2. otherwise a record marker in that sentence, OR THE ONE
                #      BEFORE IT, exempts -- "LOGGED ONLY ... no build). 10
                #      templates across 4 sections" puts the marker and the count
                #      in different breaths, and that doc is a proposal, not a
                #      claim about the repo.
                if _is_claim(sentence):
                    pass
                elif _is_record(sentence) or (idx and _is_record(sentences[idx - 1])):
                    continue
                for m in re.finditer(
                    r"(\d{2,4})\s+(templates|concept nodes|curriculum nodes)", sentence
                ):
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


def _readme_tree() -> list[str]:
    """The fenced tree block under README's '## Architecture'."""
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    after = text.split("## Architecture", 1)[1]
    return after.split("```")[1].splitlines()


def test_the_readme_tree_lists_every_directory_the_repo_actually_has():
    """The architecture tree must not omit a directory that exists.

    check_doc_paths.py verifies that every path a doc NAMES resolves. It is
    structurally blind to the opposite failure, which is the one that happened:
    on 2026-08-22 the tree was missing config/, scripts/, packaging/,
    graphify-out/ and .github/workflows/ entirely, and described four curriculum
    packs with year ranges years out of date. Nothing named was missing, so
    nothing failed.

    This closes the half a test can close -- an omitted directory. The coverage
    DESCRIPTIONS beside each entry still need a human; no checker can read
    "maths Y2-8" and know the repo now ships Y1-12.
    """
    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    real_top = {p.split("/")[0] for p in tracked if "/" in p}
    real_pkgs = {
        p.split("/")[2] for p in tracked
        if p.startswith("src/mentar/") and len(p.split("/")) > 3
    }

    lines = _readme_tree()
    listed_top = {
        m.group(1).split("/")[0]
        for line in lines
        if (m := re.match(r"^[├└]──\s+(\S+?)/", line))
    }
    listed_pkgs = {
        m.group(1) for line in lines
        if (m := re.match(r"^│\s+[├└]──\s+(\w+)/", line))
    }

    missing_top = sorted(real_top - listed_top)
    assert not missing_top, (
        f"README's architecture tree omits top-level directories that exist: "
        f"{missing_top}. Add them, or the tree quietly stops being a map."
    )
    missing_pkgs = sorted(real_pkgs - listed_pkgs)
    assert not missing_pkgs, (
        f"README's tree omits src/mentar subpackages that exist: {missing_pkgs}"
    )
    # and the reverse: nothing listed that is gone
    ghost = sorted(listed_top - real_top - {"mentar"})
    assert not ghost, f"README's tree lists directories that do not exist: {ghost}"
