"""recompute-mastery: replaying a learner's history must reproduce the engine.

A20's `learns` gate was corrected on 2026-08-16 so a WRONG answer earns no
learning credit, hinted or not. That fixed future updates; every skill_state row
already written still carried an inflated value. This tool replays the stored
response history so those rows agree with the current rule.

The load-bearing property is FIDELITY: replaying a fresh session must land on
exactly what the live FSM computed. Anything less and the tool is rewriting a
child's records with a guess. The first version failed this by reading
skill_state's p_guess/p_slip columns -- which are never written, so they hold
the schema defaults -- and that is how the column bug was found.

    python3 -m pytest tests/tools/test_recompute_mastery.py
"""

from __future__ import annotations

import os
import pathlib
import sqlite3
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "tests" / "web"))

from mentar.tools.recompute_mastery import recompute_mastery  # noqa: E402


def _session(answers):
    """Drive a real session through the web path; return (db_path, app_module)."""
    try:
        import flask  # noqa: F401
    except ImportError:
        pytest.skip("flask not installed (web extra)")
    from test_progress import _client

    app_mod, client = _client()
    headers = {"HX-Request": "true"}
    client.post("/choose", data={"subject": "fractions"})
    client.get("/learn")
    for a in answers:
        client.post("/answer", data={"answer": a}, headers=headers)
    return os.environ["MENTAR_DB_PATH"], app_mod


def _stored(db):
    con = sqlite3.connect(db)
    try:
        return {r[0]: r[1] for r in con.execute("SELECT skill_id, p_mastery FROM skill_state")}
    finally:
        con.close()


def test_replaying_a_fresh_session_reproduces_the_engine_exactly():
    """The whole tool rests on this. A mix of wrong, Help, hinted and correct
    answers, so the replay has to get the hinted flag and the ordering right."""
    db, _ = _session(["999999", "help", "999999", "4", "999999", "help", "4", "4"])
    assert _stored(db), "precondition: the session wrote a skill_state row"
    assert recompute_mastery(db) == [], (
        "replay disagreed with the live engine -- the tool would rewrite correct rows"
    )


def test_an_inflated_old_rule_row_is_corrected():
    """The reason the tool exists: a value the OLD rule produced is pulled back
    to what the child's own history actually supports."""
    db, _ = _session(["999999", "help", "999999"])
    skill = next(iter(_stored(db)))
    con = sqlite3.connect(db)
    con.execute("UPDATE skill_state SET p_mastery = 0.2231 WHERE skill_id = ?", (skill,))
    con.commit()
    con.close()

    changes = recompute_mastery(db)
    assert len(changes) == 1, changes
    assert changes[0].stored == pytest.approx(0.2231)
    assert changes[0].replayed < 0.2231, "a wrong-answer history must not support 0.22"
    assert changes[0].observations > 0


def test_a_dry_run_writes_nothing_and_apply_writes():
    db, _ = _session(["999999", "help", "999999"])
    skill = next(iter(_stored(db)))
    con = sqlite3.connect(db)
    con.execute("UPDATE skill_state SET p_mastery = 0.9 WHERE skill_id = ?", (skill,))
    con.commit()
    con.close()

    changes = recompute_mastery(db)                    # dry run
    assert changes and _stored(db)[skill] == pytest.approx(0.9), "dry run must not write"

    applied = recompute_mastery(db, apply=True)
    assert applied
    assert _stored(db)[skill] == pytest.approx(applied[0].replayed)
    assert recompute_mastery(db) == [], "a second run must find nothing left to do"


def test_a_skill_with_no_response_history_is_left_alone():
    """Seeded some other way (a resumed session's in-memory default). Replaying
    it would invent history rather than recompute it."""
    db, _ = _session(["4"])
    con = sqlite3.connect(db)
    learner = con.execute("SELECT id FROM learner_profile LIMIT 1").fetchone()[0]
    con.execute(
        "INSERT INTO skill_state (learner_id, skill_id, p_mastery) VALUES (?, 'ghost_node', 0.5)",
        (learner,),
    )
    con.commit()
    con.close()
    assert all(c.skill_id != "ghost_node" for c in recompute_mastery(db))
    assert _stored(db)["ghost_node"] == pytest.approx(0.5)


def test_the_store_persists_the_params_the_engine_actually_used():
    """W3.3 §6 B1 (2026-09-02): until this fix `update_skill_state` never wrote
    p_guess/p_slip/p_learns/p_forgets, so every row held the schema defaults
    (0.2/0.1/0.2/0 -- the mc4 class) whatever the node's real class. The pilot
    fractions nodes are numeric-class (guess 0.05), so a row still carrying the
    default fails this."""
    from mentar.tools.recompute_mastery import _params_by_node

    db, _ = _session(["999999"])
    con = sqlite3.connect(db)
    try:
        rows = con.execute(
            "SELECT skill_id, p_guess, p_slip, p_learns, p_forgets FROM skill_state"
        ).fetchall()
    finally:
        con.close()
    assert rows, "precondition: the session wrote a skill_state row"
    by_node = _params_by_node()
    for skill, g, s, learns, f in rows:
        p = by_node[skill]
        assert (g, s, learns, f) == pytest.approx((p.guess, p.slip, p.learns, p.forgets)), skill
    assert any(g != pytest.approx(0.2) for _, g, *_ in rows), (
        "every row still holds the schema-default guess -- the params were not written"
    )


def test_replay_adjacency_does_not_cross_a_session_boundary(tmp_path):
    """The item bank's no-repeat is per session, so the same bank item can be
    the last item of one session and the first of the next. The controller's
    item_observed flag resets at every PRESENT, so that second session's first
    hinted wrong IS an observation -- the replay must agree, or two sessions
    that happen to share an item id would replay one observation short."""
    from mentar.db.store import LearnerStore
    from mentar.engine.bkt import P_L0, bkt_update, params_for
    from mentar.tools.recompute_mastery import _replay_one

    store = LearnerStore(tmp_path / "t.db")
    lid = store.create_learner("kid", "Year 4", "AU", "parent_mediated")
    store.create_session(lid, "s1")
    store.create_session(lid, "s2")
    store.write_response(lid, "s1", "unit_fractions", "item:X", "2/3", 0, 0, None)  # s1: cold wrong
    store.write_response(lid, "s2", "unit_fractions", "item:X", "2/3", 0, 1, None)  # s2: first attempt, hinted wrong
    store.write_response(lid, "s2", "unit_fractions", "item:X", "2/3", 0, 1, None)  # s2: correlated, skipped
    params = params_for("fraction")
    p, seen = _replay_one(store._conn, lid, "unit_fractions", params)
    assert seen == 2, "the new session's first attempt must count even on the same item id"
    assert p == pytest.approx(bkt_update(bkt_update(P_L0, False, False, params), False, True, params))
