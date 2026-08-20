"""Jump-to-topic web flow: /topics list -> POST /choose with a topic -> pinned /learn.

docs/design/topic_jump_and_practice.md. Everything here drives the REAL request
path (R12 lesson: "code reads correct" is not evidence).

    python3 -m pytest tests/web/test_topics.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "tests" / "web"))

from test_progress import _client

H = {"HX-Request": "true"}


def _pilot_nodes(app_mod):
    return list(app_mod._SUBJECT_CURRICULA["fractions"])


def _uuid(client):
    with client.session_transaction() as s:
        return s.get("learner_uuid", "")


def test_topics_page_lists_every_node_including_unattempted():
    """The list is built from the curriculum, NOT skill_state -- a fresh learner
    (no mastery rows at all) must still see every topic, marked 'new'."""
    app_mod, c = _client()
    nodes = _pilot_nodes(app_mod)
    body = c.get("/topics?subject=fractions").get_data(as_text=True)
    for nid in nodes:
        assert f'value="{nid}"' in body, f"topic {nid} missing from /topics"
    assert body.count("topic-new") == len(nodes), "a fresh learner's topics must all be 'new'"


def test_front_page_card_carries_the_jump_link():
    """Maintainer requirement: the affordance is visible on the card itself."""
    _, c = _client()
    body = c.get("/").get_data(as_text=True)
    assert "/topics?subject=" in body
    assert "Jump to a topic" in body


def test_choosing_a_topic_pins_the_session_to_it():
    """A node guided selection would NOT serve first (has prerequisites) is
    served immediately when chosen -- asserted on the controller's actual node,
    not on page text."""
    app_mod, c = _client()
    nodes = _pilot_nodes(app_mod)
    cur = app_mod._SUBJECT_CURRICULA["fractions"]
    target = next(n for n in nodes if cur[n].get("prerequisites"))
    c.post("/choose", data={"subject": "fractions", "topic": target})
    c.get("/learn")
    ctrl = app_mod._controllers[_uuid(c)]
    assert ctrl._pinned_node == target
    assert ctrl._ctx.current_node_id == target
    # ...and it STAYS there across answered items (wrong answer -> next turn).
    c.post("/answer", data={"answer": "999999"}, headers=H)
    assert ctrl._ctx.current_node_id == target


def test_invalid_topic_degrades_to_a_guided_session():
    """A stale/forged topic value must fall through to normal choose -- no 500,
    no pin."""
    app_mod, c = _client()
    r = c.post("/choose", data={"subject": "fractions", "topic": "no_such_node"})
    assert r.status_code == 302
    c.get("/learn")
    assert app_mod._controllers[_uuid(c)]._pinned_node is None


def test_switching_subject_clears_the_pin():
    app_mod, c = _client()
    nodes = _pilot_nodes(app_mod)
    c.post("/choose", data={"subject": "fractions", "topic": nodes[-1]})
    c.get("/learn")
    other = next(k for k in app_mod.SUBJECTS if k != "fractions")
    c.post("/choose", data={"subject": other})
    c.get("/learn")
    assert app_mod._controllers[_uuid(c)]._pinned_node is None


def test_disclosure_freezes_a_pinned_session_and_a_pin_cannot_thaw_it():
    """THE load-bearing test (design doc): the pinned session runs the same turn
    path, so a disclosure freezes it -- and re-choosing with a topic pin must
    NOT hand the child a fresh unfrozen session."""
    app_mod, c = _client()
    from mentar.dialogue.controller import FSMState
    nodes = _pilot_nodes(app_mod)
    c.post("/choose", data={"subject": "fractions", "topic": nodes[0]})
    c.get("/learn")
    c.post("/answer", data={"answer": "i want to kill myself"}, headers=H)
    ctrl = app_mod._controllers[_uuid(c)]
    assert ctrl.state == FSMState.ESCALATION_FREEZE.value

    # Attempted escape: choose the same subject again, pinned to another topic.
    c.post("/choose", data={"subject": "fractions", "topic": nodes[1]})
    assert app_mod._controllers[_uuid(c)] is ctrl, "pin replaced a FROZEN controller"
    assert app_mod._controllers[_uuid(c)].state == FSMState.ESCALATION_FREEZE.value


def test_topics_page_shows_mastery_where_it_exists():
    """After real answered items, the practised node's row shows a percentage
    instead of 'new'."""
    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")
    for _ in range(2):
        c.post("/answer", data={"answer": "1/3"}, headers=H)
        c.post("/answer", data={"answer": "999999"}, headers=H)
    body = c.get("/topics?subject=fractions").get_data(as_text=True)
    nodes = _pilot_nodes(app_mod)
    assert body.count("topic-new") < len(nodes), (
        "no topic row picked up a mastery percentage after real answers"
    )


def test_unknown_subject_redirects_to_the_picker():
    _, c = _client()
    r = c.get("/topics?subject=bogus")
    assert r.status_code == 302


def _drive_to_completion(app_mod, c, ctrl, tries=60):
    for _ in range(tries):
        item = getattr(ctrl._ctx, "current_item", None)
        c.post("/answer", data={"answer": str(item.answer) if item else "1/2"}, headers=H)
        if "END" in str(ctrl._ctx.state):
            return True
    return False


def test_rechoosing_the_same_topic_after_completion_starts_fresh():
    """Found 2026-08-18, first re-jump after a completed session: the pin had not
    changed, so /choose kept the TERMINAL controller and /learn bounced straight
    to /done -- tapping the topic again did nothing. "Practise it again" is the
    feature's whole point, so a topic tap on a terminal session must start over."""
    app_mod, c = _client()
    nodes = _pilot_nodes(app_mod)
    c.post("/choose", data={"subject": "fractions", "topic": nodes[0]})
    c.get("/learn")
    ctrl = app_mod._controllers[_uuid(c)]
    assert _drive_to_completion(app_mod, c, ctrl), "precondition: session must end"

    c.post("/choose", data={"subject": "fractions", "topic": nodes[0]})
    assert c.get("/learn").status_code == 200, "re-jump bounced to /done"
    fresh = app_mod._controllers[_uuid(c)]
    assert fresh is not ctrl
    assert fresh._pinned_node == nodes[0]


def test_retapping_the_same_topic_mid_session_does_not_reset_progress():
    """The other half of the same rule: a double-tap / back-button re-choose of
    the topic already LIVE must be a no-op, not a session reset."""
    app_mod, c = _client()
    nodes = _pilot_nodes(app_mod)
    c.post("/choose", data={"subject": "fractions", "topic": nodes[0]})
    c.get("/learn")
    ctrl = app_mod._controllers[_uuid(c)]
    c.post("/answer", data={"answer": "999999"}, headers=H)
    n = ctrl._ctx.items_completed

    c.post("/choose", data={"subject": "fractions", "topic": nodes[0]})
    c.get("/learn")
    assert app_mod._controllers[_uuid(c)] is ctrl, "a mid-session re-tap replaced the session"
    assert ctrl._ctx.items_completed == n


def test_guided_subject_card_tap_after_done_also_starts_fresh():
    """Same rule unified for GUIDED sessions: tapping the subject card after
    /done used to bounce back to /done (only the done page's Start-again button
    escaped it). A card tap is an explicit start intent either way."""
    app_mod, c = _client()
    c.post("/choose", data={"subject": "fractions"})
    c.get("/learn")
    ctrl = app_mod._controllers[_uuid(c)]
    assert _drive_to_completion(app_mod, c, ctrl), "precondition: session must end"

    c.post("/choose", data={"subject": "fractions"})
    assert c.get("/learn").status_code == 200, "card tap after done still bounced to /done"
    assert app_mod._controllers[_uuid(c)] is not ctrl


def test_topics_page_groups_by_strand_with_flat_fallback():
    """The strand grouping (maintainer, 2026-08-20: "split the topics and
    subtopics"): a strand-tagged subject renders its curriculum's own strand
    headings above the topic rows, in template order; a template WITHOUT
    strands (the pilot) still renders the old flat list — zero headings, all
    rows. Driven through the real request path."""
    try:
        import flask  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("flask not installed (web extra)")
    import re

    app_mod, c = _client()   # all packs on: AU year 3 maths is available
    body = c.get("/topics?subject=au_acara_year3_maths").get_data(as_text=True)
    headings = re.findall(r'strand-heading">([^<]+)<', body)
    assert headings[:2] == ["Number", "Fractions"], headings
    assert set(headings) >= {"Algebra", "Space", "Statistics"}, headings
    # every node still gets a row — grouping must never drop topics
    assert body.count('name="topic"') == len(app_mod._SUBJECT_CURRICULA["au_acara_year3_maths"])

    flat = c.get("/topics?subject=fractions").get_data(as_text=True)
    assert "strand-heading" not in flat
    assert flat.count('name="topic"') == len(_pilot_nodes(app_mod))
