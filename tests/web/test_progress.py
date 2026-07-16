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
    os.environ.pop("MENTAR_PACK_STATE", None)  # isolation: don't inherit a toggle test's state file
    import importlib

    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)
    app_mod._llm_call_cached = lambda messages: "stub tutor reply"  # no network in tests
    app_mod._SETUP_GATE_BYPASS = True  # R9: not testing setup/first-run here
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
    c.get("/learn")
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
    c.get("/learn")

    body = c.get("/progress").get_data(as_text=True)
    assert "<svg" in body
    assert body.count("<circle") == 8
    assert "graph-node" in body


def test_picker_groups_subjects_by_year():
    """R3.2: the picker reads Year -> Subject, grouped by SUBJECT_GROUPS
    (derived from the R3.1 template-catalog scan, not hand-maintained)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    _app_mod, c = _client()
    html = c.get("/choose").get_data(as_text=True)
    assert "Year 3 (AU)" in html and "Year 4 (AU)" in html and "Try-out topics" in html
    # AU subjects sit under their own year headings, pilot topics under try-out.
    year3_idx = html.find("Year 3 (AU)")
    tryout_idx = html.find("Try-out topics")
    assert year3_idx < html.find("au_year3_maths") < tryout_idx
    assert tryout_idx < html.find('value="fractions"')


def test_practice_pack_subjects_appear_under_tryout_topics():
    """The evergreen practice sampler (times tables/skip counting/doubles-halves,
    synonyms-antonyms/rhyming/odd-one-out/plurals) lives in its own
    curriculum/templates/practice/ directory (not _pilot/), auto-prefixed
    "practice_" -- but must still land in the SAME "Try-out topics" picker
    group as fractions/arithmetic/science (grouping is by year_level: pilot,
    not by directory name)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    _app_mod, c = _client()
    html = c.get("/choose").get_data(as_text=True)
    assert "Maths practice" in html
    assert "English practice" in html

    tryout_idx = html.find("Try-out topics")
    assert tryout_idx != -1
    assert tryout_idx < html.find('value="practice_maths"')
    assert tryout_idx < html.find('value="practice_english"')


def test_progress_switcher_filters_star_cards_to_selected_subject():
    """R3.2: fixes a real defect -- /progress used to mix ALL subjects' skill
    rows into one undifferentiated list. A learner with history in TWO
    subjects must see ONLY the selected subject's nodes on each switcher tab,
    never the other subject's."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    _app_mod, c = _client()

    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")
    c.post("/answer", data={"answer": "4"})

    c.post("/choose", data={"subject": "au_year3_maths"})
    c.get("/learn")
    c.post("/answer", data={"answer": "A"})

    au3 = c.get("/progress?subject=au_year3_maths").get_data(as_text=True)
    frac = c.get("/progress?subject=fractions").get_data(as_text=True)

    # R6.2: star-cards render the real curriculum label (display_name), never
    # the raw namespaced skill_id or a naive "au3_place_value" -> "Au3 Place
    # Value" transform. (AU3 has its OWN "Unit fractions (...)" node, so check
    # the fractions pilot's distinct full label "Unit fractions (1/n)", not
    # the shared substring both curricula's authors happened to use.)
    assert "Place value to 999" in au3
    assert "Whole-number division" not in au3 and "Unit fractions (1/n)" not in au3

    assert "Whole-number division" in frac
    assert "Place value to 999" not in frac

    # The active tab is highlighted; a per-subject mastered/total count shows.
    assert 'href="/progress?subject=au_year3_maths" class="switcher-link active"' in au3
    assert "(0/6)" in au3  # attempted once, not yet past the 0.85 mastery threshold

    # No query param -> defaults to the session's active subject (au3, chosen last).
    default = c.get("/progress").get_data(as_text=True)
    assert 'href="/progress?subject=au_year3_maths" class="switcher-link active"' in default


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
    c.get("/learn")

    body = c.get("/progress").get_data(as_text=True)
    assert "<tspan" in body
    assert "Equivalent fra<" not in body   # the old mid-word cut
    assert "fractions</tspan>" in body     # the dropped word now renders whole
    assert "Place value to" in body

    # Every node's full label is still available via the hover tooltip.
    curriculum = app_mod._SUBJECT_CURRICULA["au_year4_maths"]
    for node in curriculum.values():
        assert f"<title>{node['label']}" in body


def test_parent_mastery_table_appears_after_answer():
    """GET /parent includes the mastery table and session summary after one answer."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    _app_mod, c = _client()

    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")
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


def test_r6_2_display_name_unified_across_all_four_surfaces():
    """R6.2 regression: skill_id (machine key, namespaced e.g. "au3_place_value")
    and its human display name used to be conflated in 3 of 4 rendering sites
    (progress.html star-cards + learner.html mastery bar did a naive
    replace('_',' ')|title -- producing "Au3 Place Value"; parent.html showed
    the raw skill_id verbatim; done.html did the same naive transform).
    Only progress.html's concept-graph ever did it correctly. All four must
    now render the SAME curriculum-authored label, sourced once via
    app._display_name(), never re-derived per-template."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")

    app_mod, c = _client()
    c.post("/choose", data={"subject": "au_year3_maths"})
    r = c.get("/learn")
    learn_html = r.get_data(as_text=True)

    with c.session_transaction() as sess:
        learner_uuid = sess["learner_uuid"]
    ctrl = app_mod._controllers[learner_uuid]
    ctrl._ctx.current_node_id = "au3_place_value"

    # 1. learner.html's per-skill mastery bar.
    learn_html = c.get("/learn").get_data(as_text=True)
    assert "Place value to 999" in learn_html
    assert "Au3 Place Value" not in learn_html
    assert "au3_place_value" not in learn_html

    c.post("/answer", data={"answer": "A"})

    # 2. progress.html's star-card list (the concept-graph SVG was already
    # correct before R6.2 -- this covers the star-card list specifically).
    progress_html = c.get("/progress?subject=au_year3_maths").get_data(as_text=True)
    assert "Place value to 999" in progress_html
    assert "Au3 Place Value" not in progress_html

    # 3. parent.html's mastery table + answers table (previously the raw,
    # unmodified skill_id -- arguably the worst of the four).
    parent_html = c.get("/parent").get_data(as_text=True)
    assert "Place value to 999" in parent_html
    assert "au3_place_value" not in parent_html

    # 4. done.html's session recap.
    from mentar.dialogue.controller import TurnResult
    ctrl.step = lambda answer_text: TurnResult(
        state=ctrl.state, text="All done!", done=True, escalated=False
    )
    c.post("/answer", data={"answer": "A"})
    done_html = c.get("/done").get_data(as_text=True)
    assert "Place value to 999" in done_html
    assert "Au3 Place Value" not in done_html
    assert "au3_place_value" not in done_html


def test_graph_layout_au_year3_bottom_row_no_longer_clipped():
    """R6.1 regression: _compute_graph_layout's y-position scale and its
    returned viewBox height used to be two uncoupled scales. For the AU Year 3
    template (3 levels), the bug put the bottom row at y=83.3 while height
    was only 78 -- clipped off-screen. Reproduce the exact before/after."""
    from mentar.web.app import _SUBJECT_CURRICULA, _compute_graph_layout

    curriculum = _SUBJECT_CURRICULA["au_year3_maths"]
    graph = _compute_graph_layout(curriculum, {})

    # Old buggy formula for reference (must NOT match the new height).
    old_height = 78
    bottom_row_nodes = [n for n in graph["nodes"] if n["y"] == max(n2["y"] for n2 in graph["nodes"])]
    assert bottom_row_nodes, "expected at least one bottom-row node"
    for node in bottom_row_nodes:
        assert node["y"] < old_height, "bottom row must sit above the OLD (buggy) height too now"
    assert graph["height"] > old_height  # the new height has real padding, not the bare old value


def test_graph_layout_bottom_row_within_viewbox_for_all_templates():
    """R6.1: for every shipped template, the bottom-most node's y + circle
    radius (4, per progress.html's <circle r="4">) + full wrapped-label
    extent (up to 3 lines: 8 + (lines-1)*4, per progress.html's <text
    y="{{ n.y + 8 }}"> / <tspan dy="4">) must stay <= the returned height."""
    from mentar.web.app import _SUBJECT_CURRICULA, _compute_graph_layout

    RADIUS = 4
    for subject_key, curriculum in _SUBJECT_CURRICULA.items():
        graph = _compute_graph_layout(curriculum, {})
        for node in graph["nodes"]:
            label_extent = 8 + (len(node["label_lines"]) - 1) * 4
            bottom_edge = node["y"] + RADIUS + label_extent
            assert bottom_edge <= graph["height"], (
                f"{subject_key}: node {node['id']!r} bottom edge {bottom_edge} "
                f"exceeds viewBox height {graph['height']}"
            )
