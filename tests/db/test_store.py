"""LearnerStore schema migrations.

tests/db/test_datamodel.py owns the data-model conformance suite (T3.6); this
file is for migration round-trips, which need a REAL old-version database built
and then upgraded, rather than a fresh store.

    python3 -m pytest tests/db/test_store.py
"""

from __future__ import annotations


def test_v4_to_v5_migration_relaxes_severity_and_keeps_every_row(tmp_path):
    """v5 (2026-08-18): the severity CHECK gains 'concern'. SQLite cannot alter
    a CHECK, so the migration rebuilds escalation_log -- and a rebuild of the
    AUDIT table must provably never drop a row. Builds a REAL v4 database (the
    current schema with the old CHECK and version stamp), seeds it, migrates by
    simply opening it, then verifies old rows survived and 'concern' now
    inserts where it previously violated the constraint."""
    import sqlite3 as _sq

    from mentar.db.store import _SCHEMA_PATH, LearnerStore

    db = tmp_path / "v4.db"
    ddl = _SCHEMA_PATH.read_text(encoding="utf-8")
    ddl = ddl.replace("PRAGMA user_version = 5;", "PRAGMA user_version = 4;")
    ddl = ddl.replace("'low', 'concern', 'high', 'critical'", "'low', 'high', 'critical'")
    check_lines = [ln for ln in ddl.splitlines() if "CHECK (severity" in ln]
    assert check_lines and all("concern" not in ln for ln in check_lines), (
        "failed to reconstruct the v4 CHECK (comments may mention concern; the constraint must not)"
    )
    con = _sq.connect(db)
    con.executescript(ddl)
    con.execute(
        "INSERT INTO learner_profile (name, year_level, country, age_mode) "
        "VALUES ('kid', 'Year 4', 'AU', 'parent_mediated')"
    )
    con.execute(
        "INSERT INTO escalation_log (learner_id, trigger_class, trigger_text_verbatim, "
        "severity, session_outcome) VALUES (1, 'harm_to_self', 'verbatim text', "
        "'critical', 'frozen')"
    )
    # Precondition: v4 really does reject 'concern'.
    try:
        con.execute(
            "INSERT INTO escalation_log (learner_id, trigger_class, "
            "trigger_text_verbatim, severity) VALUES (1, 'welfare_concern', 'x', 'concern')"
        )
        raise AssertionError("v4 accepted 'concern' -- the migration would be pointless")
    except _sq.IntegrityError:
        pass
    con.commit()
    con.close()

    store = LearnerStore(str(db))          # opening runs the migration
    assert store.schema_version() == 5
    esc_id = store.write_escalation(
        1, "welfare_concern", "i'm scared to go home",
        severity="concern", session_outcome="logged_concern",
    )
    assert esc_id > 1
    rows = store.learner_escalations(1)
    assert len(rows) == 2, "the rebuild dropped audit rows"
    assert rows[0]["trigger_text_verbatim"] == "verbatim text"
    assert rows[0]["severity"] == "critical"
    assert rows[1]["severity"] == "concern"


def test_update_skill_state_persists_the_params_it_was_given(tmp_path):
    """W3.3 §6 B1 (2026-09-02). The method's docstring said the four BKT
    parameter columns were "set once at cold-start"; nothing ever wrote them,
    so every row carried the schema defaults (mc4: 0.2/0.1/0.2/0) whatever
    the node's class. Now: params given -> written; params omitted -> the
    columns are left exactly as they were."""
    from mentar.db.store import LearnerStore
    from mentar.engine.bkt import params_for

    store = LearnerStore(tmp_path / "t.db")
    lid = store.create_learner("kid", "Year 4", "AU", "parent_mediated")
    numeric = params_for("int")                       # guess 0.05 -- not the 0.2 default
    store.update_skill_state(lid, "au4_place_value", 0.42, priors_used=True, params=numeric)
    row = store.get_skill_state(lid, "au4_place_value")
    assert (row["p_guess"], row["p_slip"], row["p_learns"], row["p_forgets"]) == (
        numeric.guess, numeric.slip, numeric.learns, numeric.forgets,
    )
    assert row["p_mastery"] == 0.42

    # a legacy caller that knows only the mastery must not clobber the params
    store.update_skill_state(lid, "au4_place_value", 0.5, priors_used=True)
    row = store.get_skill_state(lid, "au4_place_value")
    assert row["p_mastery"] == 0.5
    assert row["p_guess"] == numeric.guess, "params=None must leave the columns untouched"
