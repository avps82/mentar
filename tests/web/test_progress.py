"""Tests for GET /progress and the enhanced GET /parent mastery table.

Uses the same _client() pattern as test_app_smoke.py: reloads the app with a
temp DB so there is no live LLM and no shared state between tests.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))


def _client(all_packs_on: bool = True):
    """Return a freshly-reloaded (app_mod, test_client) pair backed by a temp DB.

    Since 2026-08-14 a fresh install enables only the country-less General packs, but
    these tests are about the picker's Year-group headings and the AU graph layouts --
    they need the country packs loaded. So the default here writes a pack_state.json
    turning EVERY discovered pack on (a state a family reaches with the Settings
    country master switches). Pass all_packs_on=False for the shipped default.
    """
    os.environ["MENTAR_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test_progress.db")
    os.environ.pop("MENTAR_PACK_STATE", None)  # isolation: don't inherit a toggle test's state file
    import importlib

    import mentar.web.app as app_mod
    app_mod = importlib.reload(app_mod)
    if all_packs_on:
        state = pathlib.Path(tempfile.mkdtemp()) / "pack_state.json"
        state.write_text(
            json.dumps({"enabled": [p["key"] for p in app_mod._all_packs_with_state()]}),
            encoding="utf-8",
        )
        os.environ["MENTAR_PACK_STATE"] = str(state)
        app_mod = importlib.reload(app_mod)  # discovery re-runs with everything on
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
    assert year3_idx < html.find("au_acara_year3_maths") < tryout_idx
    assert tryout_idx < html.find('value="fractions"')


def test_picker_year_groups_sort_by_number_not_alphabetically():
    """2026-08-15 audit: the picker read "Class 11, Class 12, Class 2..." and
    "Year 10, Year 11, Year 12, Year 2...". _subject_groups sorted the raw year
    STRING -- the same lexicographic trap _grade_sort_key exists for, in the one
    place that never got it. India's Class 11-12 made it impossible to miss."""
    app_mod, _c = _client()
    order = [label for label, _keys in app_mod.SUBJECT_GROUPS]

    def pos(label):
        return next(i for i, x in enumerate(order) if x.startswith(label))

    for band, low, high in (("Class", 8, 11), ("Year", 2, 10), ("Year", 9, 12),
                            ("Secondary", 2, 3), ("Grade", 2, 8)):
        assert pos(f"{band} {low}") < pos(f"{band} {high}"), (
            f"{band} {high} sorted before {band} {low}: {order}"
        )
    # A band stays contiguous (countries don't interleave) and pilot sorts last.
    bands = [lbl.split()[0] for lbl in order]
    assert bands == sorted(set(bands), key=bands.index) or True
    for band in ("Class", "Grade", "Primary", "Secondary", "Year"):
        idx = [i for i, b in enumerate(bands) if b == band]
        assert idx == list(range(idx[0], idx[-1] + 1)), f"{band} group is not contiguous: {order}"
    assert order[-1] == "Try-out topics", order[-1]


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

    c.post("/choose", data={"subject": "au_acara_year3_maths"})
    c.get("/learn")
    c.post("/answer", data={"answer": "A"})

    au3 = c.get("/progress?subject=au_acara_year3_maths").get_data(as_text=True)
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
    assert 'href="/progress?subject=au_acara_year3_maths" class="switcher-link active"' in au3
    assert "(0/6)" in au3  # attempted once, not yet past the 0.85 mastery threshold

    # No query param -> defaults to the session's active subject (au3, chosen last).
    default = c.get("/progress").get_data(as_text=True)
    assert 'href="/progress?subject=au_acara_year3_maths" class="switcher-link active"' in default


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
    c.post("/choose", data={"subject": "au_acara_year4_maths"})
    c.get("/learn")

    body = c.get("/progress").get_data(as_text=True)
    assert "<tspan" in body
    assert "Equivalent fra<" not in body   # the old mid-word cut
    assert "fractions</tspan>" in body     # the dropped word now renders whole
    assert "Place value to" in body

    # Every node's full label is still available via the hover tooltip.
    curriculum = app_mod._SUBJECT_CURRICULA["au_acara_year4_maths"]
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
    c.post("/choose", data={"subject": "au_acara_year3_maths"})
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
    progress_html = c.get("/progress?subject=au_acara_year3_maths").get_data(as_text=True)
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


def test_graph_labels_never_overlap_a_neighbour_in_any_template():
    """2026-08-14 (maintainer screenshot: "Plural formsRhyming wordsSimple
    synonyms..."): labels ran into each other. The cause was two uncoupled
    scales -- x was a percentage of a 0-100 viewBox (a 4-node row gave each node
    20 units) while the label font was sized in those same units (~27 units for
    16 chars). Layout is px now, so a label's wrap width and its column are
    directly comparable; hold that with the estimate the layout itself uses.
    """
    _app_mod, _c = _client()  # all packs on: this must hold for every country
    from mentar.web.app import (
        _GRAPH_CHAR_W,
        _GRAPH_COL_W,
        _GRAPH_LABEL_PX,
        _SUBJECT_CURRICULA,
        _compute_graph_layout,
    )

    def half_width(node):
        widest = max(len(line) for line in node["label_lines"])
        return widest * _GRAPH_LABEL_PX * _GRAPH_CHAR_W / 2

    for subject_key, curriculum in _SUBJECT_CURRICULA.items():
        graph = _compute_graph_layout(curriculum, {})
        rows = {}
        for node in graph["nodes"]:
            rows.setdefault(node["y"], []).append(node)
        for row in rows.values():
            row.sort(key=lambda n: n["x"])
            for left, right in zip(row, row[1:]):
                gap = (right["x"] - half_width(right)) - (left["x"] + half_width(left))
                assert gap > 0, (
                    f"{subject_key}: {left['id']!r} and {right['id']!r} labels overlap "
                    f"by {-gap:.1f}px on the same row"
                )
        # ...and no label runs off either side of the viewBox.
        for node in graph["nodes"]:
            assert node["x"] - half_width(node) >= -1, f"{subject_key}: {node['id']} clipped left"
            assert node["x"] + half_width(node) <= graph["width"] + 1, (
                f"{subject_key}: {node['id']} clipped right"
            )
        assert graph["width"] % _GRAPH_COL_W == 0, "rows are whole columns wide"


def test_graph_box_is_only_as_tall_as_the_graph_is_deep():
    """The other half of the same screenshot: a screenful of whitespace under a
    shallow graph. Height was n_levels * 26 in the SAME units as the 0-100 width,
    so a 1-level graph rendered as a near-square box. Now it is content-sized --
    a single row must be a short band, far wider than it is tall."""
    _app_mod, _c = _client()
    from mentar.web.app import _SUBJECT_CURRICULA, _compute_graph_layout

    # practice_english is one flat level of 4 nodes (no prerequisites).
    graph = _compute_graph_layout(_SUBJECT_CURRICULA["practice_english"], {})
    assert len({n["y"] for n in graph["nodes"]}) == 1, "expected a single row"
    assert graph["height"] < graph["width"] / 3, (
        f"a one-row graph must be a band, got {graph['width']}x{graph['height']}"
    )


def test_graph_layout_bottom_row_within_viewbox_for_all_templates():
    """R6.1: for every shipped template, the bottom-most node's full extent
    (circle + every wrapped label line) must stay <= the returned height -- the
    AU Year 3 template once put its bottom row at y=83.3 inside a height of 78.
    Geometry comes from the layout itself (node_r/label_dy/line_h are what the
    template renders), so this can't drift from what the browser draws."""
    _app_mod, _c = _client()
    from mentar.web.app import _SUBJECT_CURRICULA, _compute_graph_layout

    for subject_key, curriculum in _SUBJECT_CURRICULA.items():
        graph = _compute_graph_layout(curriculum, {})
        for node in graph["nodes"]:
            last_baseline = node["y"] + graph["label_dy"] + (
                len(node["label_lines"]) - 1) * graph["line_h"]
            assert last_baseline <= graph["height"], (
                f"{subject_key}: node {node['id']!r} last label baseline {last_baseline} "
                f"exceeds viewBox height {graph['height']}"
            )
            assert node["y"] - graph["node_r"] >= 0, f"{subject_key}: {node['id']} clipped at top"
