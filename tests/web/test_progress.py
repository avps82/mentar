"""Tests for GET /progress and the enhanced GET /parent mastery table.

Uses the same _client() pattern as test_app_smoke.py: reloads the app with a
temp DB so there is no live LLM and no shared state between tests.
"""

from __future__ import annotations

import os
import pathlib
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))


def _client():
    """Return a freshly-reloaded (app_mod, test_client) pair backed by a temp DB."""
    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test_progress.db")
    import importlib

    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)
    app_mod._llm_call_cached = lambda messages: "stub tutor reply"  # no network in tests
    return app_mod, app_mod.app.test_client()


def test_progress_empty_session():
    """GET /progress works (200) when no session exists yet (no skills shown)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    _app_mod, c = _client()
    r = c.get("/progress")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "progress" in body.lower()


def test_progress_shows_skill_after_answer():
    """GET /progress shows a skill row after the learner has answered a question
    (the item-bank path scores deterministically, no LLM required)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    _app_mod, c = _client()

    # Kick off the session and submit one answer so a skill_state row is written.
    c.post("/choose", data={"subject": "fractions"})
    c.get("/")
    c.post("/answer", data={"answer": "4"})

    r = c.get("/progress")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    # At least one skill card should appear (skill_id rendered in some form).
    assert "⭐" in body, "Expected at least one star rating in the progress view"


def test_progress_shows_concept_graph_for_pilot_curriculum():
    """U-40/U-41: /progress renders an owned SVG concept-graph map with one
    node per curriculum node (8 for the pilot fractions template) -- built
    from _compute_graph_layout, no graph library."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    _app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/")

    body = c.get("/progress").get_data(as_text=True)
    assert "<svg" in body
    assert body.count("<circle") == 8
    assert "graph-node" in body


def test_wrap_label_never_cuts_a_word():
    """R2.4: greedy word-wrap for the concept-map labels -- the fix for the
    reported "Equivalent fra" / "Place value to" mid-word truncation."""
    from mentar.web.app import _wrap_label

    # Wraps on word boundaries only -- reflowed sensibly, never a partial word.
    assert _wrap_label("Equivalent fractions") == ["Equivalent", "fractions"]
    for line in _wrap_label("Place value to 9999"):
        assert all(w in "Place value to 9999".split() for w in line.rstrip("…").split())
    # A single word longer than max_chars is kept WHOLE on its own line, never split.
    long_word = "Supercalifragilisticexpialidocious"
    lines = _wrap_label(f"{long_word} extra")
    assert long_word in lines
    assert not any(long_word[:10] in line and long_word not in line for line in lines)
    # Truncation only when words are actually dropped, and only the LAST kept
    # line gets the ellipsis.
    truncated = _wrap_label("Sharing and grouping word problems for everyone", max_chars=10, max_lines=3)
    assert len(truncated) == 3
    assert truncated[-1].endswith("…")
    assert not any(line.endswith("…") for line in truncated[:-1])
    # Short label / edge cases.
    assert _wrap_label("Addition") == ["Addition"]
    assert _wrap_label("") == [""]
    assert _wrap_label("   ") == [""]


def test_progress_graph_labels_wrap_not_truncate_for_au_template():
    """The reported bug: AU labels ("Place value to 9999", "Equivalent
    fractions") were hard-cut at 14 chars with no ellipsis. Now they must wrap
    across <tspan> lines with every whole word intact, and the old cut string
    must never appear."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "au_year4_maths"})
    c.get("/")

    body = c.get("/progress").get_data(as_text=True)
    assert "<tspan" in body
    assert "Equivalent fra<" not in body   # the old mid-word cut
    assert "fractions</tspan>" in body     # the dropped word now renders whole
    assert "Place value to" in body

    # Every node's full label is still available via the hover tooltip.
    curriculum = app_mod._SUBJECT_CURRICULA["au_year4_maths"]
    for node in curriculum.values():
        assert f"<title>{node['concept']}" in body


def test_parent_mastery_table_appears_after_answer():
    """GET /parent includes the mastery table and session summary after one answer."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    _app_mod, c = _client()

    c.post("/choose", data={"subject": "fractions"})
    c.get("/")
    c.post("/answer", data={"answer": "4"})

    r = c.get("/parent")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    # Mastery table heading must be present.
    assert "Mastery progress" in body
    # Session summary line must be present.
    assert "Session summary" in body
    # At least one skill_id row inside the table (check for % sign from pct column).
    assert "%" in body
