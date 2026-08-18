"""T3.6 — Learner data model tests.

Spec: docs/TESTS.md T3.6; docs/PHASE0.md W3.6
Safety: docs/SAFETY.md Layer 4 (data/privacy), Layer 5 (parental oversight)

Five test cases:
  1. test_full_session_roundtrip        — lossless write/read of a complete session
  2. test_two_learners_isolation        — zero cross-contamination across every table
  3. test_export_copy_opens_independently — file-copy export is independently readable
  4. test_schema_version_migration_stub — user_version == 3; v1->current migration verified
  5. test_transcript_immutability       — UPDATE/DELETE on transcript rows are rejected
"""

from __future__ import annotations

import shutil
import sqlite3

import pytest

from mentar.db.store import LearnerStore

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_store(tmp_path, name="test.db") -> LearnerStore:
    return LearnerStore(tmp_path / name)


def _populate_session(
    store: LearnerStore,
    learner_id: int,
    session_id: str,
    n_responses: int = 30,
    n_help: int = 2,
) -> dict:
    """Write a complete mock session and return the ids of written rows."""
    store.create_session(learner_id, session_id)

    # 30 responses across two skills
    skills = ["fractions/adding_equal_denom", "fractions/unit_fractions"]
    resp_ids = []
    for i in range(n_responses):
        skill = skills[i % len(skills)]
        rid = store.write_response(
            learner_id=learner_id,
            session_id=session_id,
            skill_id=skill,
            prompt_ref=f"tpl_read_q:{i:04x}",
            answer=str(i),
            scored=i % 2,           # alternate correct/wrong
            hinted=1 if i % 5 == 0 else 0,
            check_result='{"ok": true}' if i % 2 == 1 else None,
        )
        resp_ids.append(rid)

    # Skill states
    for skill in skills:
        store.update_skill_state(learner_id, skill, p_mastery=0.72, priors_used=True)

    # 2 help events
    help_ids = []
    modalities = ["visual", "concrete"]
    for j in range(n_help):
        hid = store.write_help_event(
            learner_id=learner_id,
            session_id=session_id,
            skill_id=skills[j % len(skills)],
            modality=modalities[j],
            response_log_id=resp_ids[j],
        )
        help_ids.append(hid)

    # 1 probe event (clean_pass, no retry needed)
    probe_id = store.write_probe_event(
        learner_id=learner_id,
        session_id=session_id,
        skill_id=skills[0],
        response_log_id=resp_ids[5],
        retry_response_log_id=None,
        class_="clean_pass",
    )

    # 1 escalation
    esc_id = store.write_escalation(
        learner_id=learner_id,
        trigger_class="harm_to_self",
        trigger_text_verbatim="I want to hurt myself",
    )

    # 10 transcript turns
    transcript_ids = []
    roles = ["learner", "tutor", "system"]
    for k in range(10):
        tid = store.write_transcript(
            learner_id=learner_id,
            session_id=session_id,
            turn_index=k,
            role=roles[k % 3],
            text=f"Turn {k}: some text for testing purposes.",
        )
        transcript_ids.append(tid)

    return {
        "resp_ids": resp_ids,
        "help_ids": help_ids,
        "probe_id": probe_id,
        "esc_id": esc_id,
        "transcript_ids": transcript_ids,
    }


# ─────────────────────────────────────────────────────────────────────────────
# T3.6 Case 1 — Full session round-trip (lossless)
# ─────────────────────────────────────────────────────────────────────────────

class TestFullSessionRoundtrip:
    """T3.6 (a): write ≥30 responses, 2 Help, 1 probe, 1 escalation, ≥10
    transcript rows; read back; assert lossless round-trip on all key fields."""

    def test_full_session_roundtrip(self, tmp_path):
        store = _make_store(tmp_path)
        sid = "session-001"
        learner_id = store.create_learner(
            name="Alice", year_level="Year 5", country="AU", age_mode="parent_mediated"
        )
        ids = _populate_session(store, learner_id, sid, n_responses=30, n_help=2)

        # ── Learner profile ──
        profile = store.get_learner(learner_id)
        assert profile is not None
        assert profile["name"] == "Alice"
        assert profile["year_level"] == "Year 5"
        assert profile["country"] == "AU"
        assert profile["age_mode"] == "parent_mediated"

        # ── Response log ──
        responses = store.session_responses(learner_id, sid)
        assert len(responses) == 30, f"expected 30 responses, got {len(responses)}"

        # Spot-check first response for lossless field storage
        r0 = responses[0]
        assert r0["learner_id"] == learner_id
        assert r0["session_id"] == sid
        assert r0["prompt_ref"] == "tpl_read_q:0000"
        assert r0["answer"] == "0"
        assert r0["scored"] == 0          # 0 % 2 == 0 → wrong
        assert r0["hinted"] == 1          # 0 % 5 == 0 → hinted
        assert r0["check_result"] is None # scored==0 rows have None

        # Spot-check a correct response
        r1 = responses[1]
        assert r1["scored"] == 1
        assert r1["check_result"] == '{"ok": true}'

        # Every response belongs to this learner
        for r in responses:
            assert r["learner_id"] == learner_id, "cross-learner contamination"

        # ── Help events ──
        help_evts = store.session_help_events(learner_id, sid)
        assert len(help_evts) == 2
        assert {h["modality"] for h in help_evts} == {"visual", "concrete"}
        for h in help_evts:
            assert h["learner_id"] == learner_id
            assert h["session_id"] == sid

        # ── Probe events ──
        probes = store.session_probe_events(learner_id, sid)
        assert len(probes) == 1
        p = probes[0]
        assert p["class"] == "clean_pass"
        assert p["retry_response_log_id"] is None
        assert p["learner_id"] == learner_id

        # ── Escalation log ──
        esc = store.get_escalation(learner_id, ids["esc_id"])
        assert esc is not None
        assert esc["trigger_class"] == "harm_to_self"
        assert esc["trigger_text_verbatim"] == "I want to hurt myself"
        assert esc["parent_ack_at"] is None  # not yet acknowledged

        # parent acknowledgment
        store.parent_ack_escalation(ids["esc_id"])
        esc2 = store.get_escalation(learner_id, ids["esc_id"])
        assert esc2["parent_ack_at"] is not None
        assert esc2["session_outcome"] == "acknowledged"

        # ── Transcript ──
        turns = store.transcript_for_session(learner_id, sid)
        assert len(turns) == 10, f"expected 10 transcript turns, got {len(turns)}"
        for i, t in enumerate(turns):
            assert t["turn_index"] == i          # ordered by turn_index
            assert t["learner_id"] == learner_id
            assert t["session_id"] == sid
            assert t["text"] == f"Turn {i}: some text for testing purposes."
            assert t["role"] in ("learner", "tutor", "system")

        # ── Skill states ──
        states = store.all_skill_states(learner_id)
        assert len(states) == 2
        for s in states:
            assert abs(s["p_mastery"] - 0.72) < 1e-9
            assert s["prior_mode"] == 1
            assert s["learner_id"] == learner_id

        store.close()


# ─────────────────────────────────────────────────────────────────────────────
# T3.6 Case 2 — Two-learner isolation
# ─────────────────────────────────────────────────────────────────────────────

class TestTwoLearnersIsolation:
    """T3.6 (b): interleaved writes for two learners; queries for learner A
    return zero rows belonging to learner B across every table."""

    def test_two_learners_isolation(self, tmp_path):
        store = _make_store(tmp_path)

        # Create two learners
        alice_id = store.create_learner("Alice", 5, "AU", "parent_mediated")
        bob_id   = store.create_learner("Bob",   7, "UK", "independent")

        # Interleaved session writes
        for sid, lid in [("sess-A", alice_id), ("sess-B", bob_id),
                          ("sess-A2", alice_id), ("sess-B2", bob_id)]:
            _populate_session(store, lid, sid, n_responses=10, n_help=1)

        # ── response_log isolation ──
        a_responses = store.session_responses(alice_id, "sess-A")
        a_responses += store.session_responses(alice_id, "sess-A2")
        for r in a_responses:
            assert r["learner_id"] == alice_id, (
                f"Alice's response_log contains Bob's row: {dict(r)}"
            )

        b_responses = store.session_responses(bob_id, "sess-B")
        b_responses += store.session_responses(bob_id, "sess-B2")
        for r in b_responses:
            assert r["learner_id"] == bob_id, (
                f"Bob's response_log contains Alice's row: {dict(r)}"
            )

        # Confirm zero overlap: Alice rows contain no Bob learner_id
        a_learner_ids_in_responses = {r["learner_id"] for r in a_responses}
        assert bob_id not in a_learner_ids_in_responses

        # ── help_event isolation ──
        a_help = store.session_help_events(alice_id, "sess-A")
        a_help += store.session_help_events(alice_id, "sess-A2")
        for h in a_help:
            assert h["learner_id"] == alice_id

        b_help = store.session_help_events(bob_id, "sess-B")
        b_help += store.session_help_events(bob_id, "sess-B2")
        for h in b_help:
            assert h["learner_id"] == bob_id

        # ── probe_event isolation ──
        a_probes = store.session_probe_events(alice_id, "sess-A")
        a_probes += store.session_probe_events(alice_id, "sess-A2")
        for p in a_probes:
            assert p["learner_id"] == alice_id

        b_probes = store.session_probe_events(bob_id, "sess-B")
        b_probes += store.session_probe_events(bob_id, "sess-B2")
        for p in b_probes:
            assert p["learner_id"] == bob_id

        # ── escalation_log isolation ──
        a_escs = store.learner_escalations(alice_id)
        for e in a_escs:
            assert e["learner_id"] == alice_id

        b_escs = store.learner_escalations(bob_id)
        for e in b_escs:
            assert e["learner_id"] == bob_id

        a_esc_learner_ids = {e["learner_id"] for e in a_escs}
        assert bob_id not in a_esc_learner_ids

        # ── transcript isolation ──
        a_turns = store.transcript_for_session(alice_id, "sess-A")
        a_turns += store.transcript_for_session(alice_id, "sess-A2")
        for t in a_turns:
            assert t["learner_id"] == alice_id

        b_turns = store.transcript_for_session(bob_id, "sess-B")
        b_turns += store.transcript_for_session(bob_id, "sess-B2")
        for t in b_turns:
            assert t["learner_id"] == bob_id

        a_turn_learner_ids = {t["learner_id"] for t in a_turns}
        assert bob_id not in a_turn_learner_ids

        # ── skill_state isolation ──
        a_states = store.all_skill_states(alice_id)
        for s in a_states:
            assert s["learner_id"] == alice_id

        b_states = store.all_skill_states(bob_id)
        for s in b_states:
            assert s["learner_id"] == bob_id

        # ── learner_profile isolation ──
        alice_profile = store.get_learner(alice_id)
        assert alice_profile["name"] == "Alice"
        bob_profile = store.get_learner(bob_id)
        assert bob_profile["name"] == "Bob"
        # Neither profile bleeds into the other's get
        assert store.get_learner(alice_id)["id"] != bob_id
        assert store.get_learner(bob_id)["id"]   != alice_id

        store.close()


# ─────────────────────────────────────────────────────────────────────────────
# T3.6 Case 3 — Export copy opens independently
# ─────────────────────────────────────────────────────────────────────────────

class TestExportCopyOpensIndependently:
    """T3.6 (c): write a session, shutil.copy2 the .db file, open the copy with
    a NEW LearnerStore, read back; matches the original."""

    def test_export_copy_opens_independently(self, tmp_path):
        original_path = tmp_path / "original.db"
        copy_path     = tmp_path / "exported.db"

        # Write a session in the original store
        with LearnerStore(original_path) as store:
            sid = "sess-export"
            learner_id = store.create_learner("Carol", 6, "US", "parent_mediated")
            store.create_session(learner_id, sid)
            r1 = store.write_response(
                learner_id=learner_id,
                session_id=sid,
                skill_id="fractions/unit_fractions",
                prompt_ref="tpl_problem_first:abcd",
                answer="1/3",
                scored=1,
                hinted=0,
                check_result='{"fraction": "1/3", "ok": true}',
            )
            store.write_transcript(learner_id, sid, 0, "tutor",
                                   "What is one third of twelve?")
            store.write_transcript(learner_id, sid, 1, "learner", "4")
            # checkpoint() is called inside close() via __exit__

        # File-copy export (the only export mechanism for the OSS local edition)
        shutil.copy2(original_path, copy_path)

        # Open the copy with a FRESH store instance — no shared state
        with LearnerStore(copy_path) as copy_store:
            # schema_version must still be valid
            assert copy_store.schema_version() == 5

            responses = copy_store.session_responses(learner_id, sid)
            assert len(responses) == 1
            r = responses[0]
            assert r["id"] == r1
            assert r["skill_id"] == "fractions/unit_fractions"
            assert r["answer"] == "1/3"
            assert r["scored"] == 1
            assert r["hinted"] == 0
            assert r["check_result"] == '{"fraction": "1/3", "ok": true}'

            turns = copy_store.transcript_for_session(learner_id, sid)
            assert len(turns) == 2
            assert turns[0]["role"] == "tutor"
            assert turns[1]["role"] == "learner"
            assert turns[1]["text"] == "4"

            profile = copy_store.get_learner(learner_id)
            assert profile["name"] == "Carol"
            assert profile["country"] == "US"


# ─────────────────────────────────────────────────────────────────────────────
# T3.6 Case 4 — Schema version / migration stub
# ─────────────────────────────────────────────────────────────────────────────

class TestSchemaVersionMigrationStub:
    """T3.6 (d): PRAGMA user_version == 5 after first open; re-open honours it
    (schema not applied twice); real v1->v2 (A3: escalation_log gains severity/
    session_id/turn_index), v2->v3 (A19: session gains rng_seed), and v3->v4
    (R-RES: session gains checkpoint_state) migrations run on an older DB; a
    version with no registered migration still raises RuntimeError (no silent
    corruption)."""

    def test_schema_version_is_current(self, tmp_path):
        store = _make_store(tmp_path)
        assert store.schema_version() == 5, (
            f"Expected user_version 5, got {store.schema_version()}"
        )
        store.close()

    def test_schema_not_applied_twice_on_reopen(self, tmp_path):
        """Reopening an existing DB must not re-run the DDL."""
        db_path = tmp_path / "reopen.db"

        # First open: schema applied
        with LearnerStore(db_path) as s1:
            lid = s1.create_learner("Dave", 3, "CA", "parent_mediated")
            assert s1.schema_version() == 5

        # Second open: schema already current; no error, no duplicate tables
        with LearnerStore(db_path) as s2:
            assert s2.schema_version() == 5
            profile = s2.get_learner(lid)
            assert profile is not None
            assert profile["name"] == "Dave"

    def test_v1_to_current_migration_adds_new_columns(self, tmp_path):
        """A real v1 DB (no A3/A19 columns at all) is migrated all the way to
        the current version in place on reopen, and the new columns are usable."""
        db_path = tmp_path / "v1.db"

        # Build a v1 DB by hand: recreate escalation_log and session exactly as
        # the pre-A3/pre-A19 schema defined them, then pin user_version to 1 —
        # a faithful stand-in for a real v1 DB.
        with LearnerStore(db_path) as s:
            lid = s.create_learner("Eve", "pilot", "GB", "parent_mediated")
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("DROP TABLE escalation_log")
        conn.execute("""
            CREATE TABLE escalation_log (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                learner_id              INTEGER NOT NULL REFERENCES learner_profile(id) ON DELETE CASCADE,
                trigger_class           TEXT    NOT NULL,
                trigger_text_verbatim   TEXT    NOT NULL,
                freeze_started_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                parent_ack_at           TEXT,
                session_outcome         TEXT    NOT NULL DEFAULT 'frozen'
            );
        """)
        conn.execute("DROP TABLE session")
        conn.execute("""
            CREATE TABLE session (
                id           TEXT    PRIMARY KEY,
                learner_id   INTEGER NOT NULL REFERENCES learner_profile(id) ON DELETE CASCADE,
                started_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                ended_at     TEXT,
                ended_reason TEXT
            );
        """)
        conn.execute("PRAGMA user_version = 1")
        conn.commit()
        conn.close()

        # Reopen: all three migrations run, columns exist, version bumps to current.
        with LearnerStore(db_path) as s2:
            assert s2.schema_version() == 5
            eid = s2.write_escalation(
                lid, "harm_to_self", "test", severity="critical",
                session_id="sess-1", turn_index=3,
            )
            row = s2.get_escalation(lid, eid)
            assert row["severity"] == "critical"
            assert row["session_id"] == "sess-1"
            assert row["turn_index"] == 3
            s2.create_session(lid, "sess-2", rng_seed=42)  # column usable post-migration
            s2.update_session_checkpoint(lid, "sess-2", '{"current_node_id": "x"}')
            assert s2.get_session(lid, "sess-2")["checkpoint_state"] == '{"current_node_id": "x"}'

    def test_no_migration_path_raises(self, tmp_path):
        """A version with no registered migration still raises RuntimeError —
        proves the guard (not just the registered v1->v3 path) is present."""
        db_path = tmp_path / "oldversion.db"

        with LearnerStore(db_path):
            pass

        import mentar.db.store as store_module
        original = store_module._EXPECTED_VERSION
        try:
            store_module._EXPECTED_VERSION = 6  # no migration registered for v5->v6
            with pytest.raises(RuntimeError, match="schema version"):
                LearnerStore(db_path)
        finally:
            store_module._EXPECTED_VERSION = original  # restore


# ─────────────────────────────────────────────────────────────────────────────
# A6 — get_learner_by_name (durable learner id across web-app restarts)
# ─────────────────────────────────────────────────────────────────────────────

class TestGetLearnerByName:
    def test_finds_existing_learner_by_exact_name(self, tmp_path):
        store = _make_store(tmp_path)
        lid = store.create_learner("pilot-abcd1234", "pilot", "GB", "parent_mediated")
        row = store.get_learner_by_name("pilot-abcd1234")
        assert row is not None
        assert row["id"] == lid

    def test_returns_none_for_unknown_name(self, tmp_path):
        store = _make_store(tmp_path)
        store.create_learner("pilot-abcd1234", "pilot", "GB", "parent_mediated")
        assert store.get_learner_by_name("pilot-nonexistent") is None

    def test_returns_oldest_on_duplicate_names(self, tmp_path):
        """name has no UNIQUE constraint — the lookup must be deterministic
        (oldest id) rather than whichever row SQLite happens to return."""
        store = _make_store(tmp_path)
        first_id = store.create_learner("dup-name", "pilot", "GB", "parent_mediated")
        store.create_learner("dup-name", "pilot", "GB", "parent_mediated")
        row = store.get_learner_by_name("dup-name")
        assert row["id"] == first_id


# ─────────────────────────────────────────────────────────────────────────────
# A19 — assert_parent_mediated (pilot scope guard) + rng_seed column
# ─────────────────────────────────────────────────────────────────────────────

class TestAssertParentMediated:
    def test_parent_mediated_learner_does_not_raise(self, tmp_path):
        store = _make_store(tmp_path)
        lid = store.create_learner("Amy", "pilot", "GB", "parent_mediated")
        store.assert_parent_mediated(lid)  # no raise

    def test_independent_learner_refuses_with_clear_message(self, tmp_path):
        store = _make_store(tmp_path)
        lid = store.create_learner("Ben", "pilot", "GB", "independent")
        with pytest.raises(RuntimeError, match="parent_mediated"):
            store.assert_parent_mediated(lid)


class TestSessionRngSeed:
    def test_create_session_stores_rng_seed(self, tmp_path):
        store = _make_store(tmp_path)
        lid = store.create_learner("Cal", "pilot", "GB", "parent_mediated")
        store.create_session(lid, "sess-1", rng_seed=12345)
        row = store._conn.execute(
            "SELECT rng_seed FROM session WHERE id = ?;", ("sess-1",)
        ).fetchone()
        assert row["rng_seed"] == 12345

    def test_create_session_without_seed_stores_null(self, tmp_path):
        store = _make_store(tmp_path)
        lid = store.create_learner("Cal", "pilot", "GB", "parent_mediated")
        store.create_session(lid, "sess-2")
        row = store._conn.execute(
            "SELECT rng_seed FROM session WHERE id = ?;", ("sess-2",)
        ).fetchone()
        assert row["rng_seed"] is None


# ─────────────────────────────────────────────────────────────────────────────
# T3.6 Case 5 — Transcript immutability
# ─────────────────────────────────────────────────────────────────────────────

class TestTranscriptImmutability:
    """T3.6 (e): transcript rows may be inserted but never updated or deleted.
    The DB-level triggers raise OperationalError (RAISE(ABORT, ...)) on any
    UPDATE or DELETE attempt.  INSERT must still succeed."""

    def _setup(self, tmp_path):
        store = _make_store(tmp_path)
        learner_id = store.create_learner("Eve", 8, "NZ", "independent")
        sid = "sess-immutable"
        store.create_session(learner_id, sid)
        tid = store.write_transcript(learner_id, sid, 0, "tutor",
                                     "What is half of six?")
        return store, learner_id, sid, tid

    def test_insert_succeeds(self, tmp_path):
        """Baseline: writing a transcript row must succeed."""
        store, learner_id, sid, tid = self._setup(tmp_path)
        turns = store.transcript_for_session(learner_id, sid)
        assert len(turns) == 1
        assert turns[0]["text"] == "What is half of six?"
        store.close()

    def test_update_transcript_is_rejected(self, tmp_path):
        """Attempting UPDATE on transcript must raise sqlite3.OperationalError
        with 'immutable' in the message."""
        store, learner_id, sid, tid = self._setup(tmp_path)
        with pytest.raises(
            (sqlite3.OperationalError, sqlite3.IntegrityError),
            match="immutable",
        ):
            store._conn.execute(
                "UPDATE transcript SET text = 'tampered' WHERE id = ?;",
                (tid,),
            )
        store.close()

    def test_cascade_delete_of_parents_is_blocked_too(self, tmp_path):
        """The triggers make transcript's own ON DELETE CASCADE unreachable.

        Verified 2026-08-16: with foreign_keys=ON a cascading delete fires
        trg_transcript_no_delete and aborts the WHOLE statement, so neither the
        session nor the learner can be deleted while a transcript row exists.
        The FK says "delete me with my parent", the trigger says "never", and
        the trigger wins -- which is the intended reading (an audit log you can
        erase via its parent row is not an audit log). The pilot's documented
        erasure path is deleting the .db file (SAFETY.md §4.6).

        Pinned because the CASCADE reads like it works, and whoever builds
        per-learner deletion for W3.6 multi-learner will otherwise trust it.
        """
        store, learner_id, sid, tid = self._setup(tmp_path)
        store._conn.execute("PRAGMA foreign_keys = ON;")
        for sql, args in (
            ("DELETE FROM session WHERE id = ?;", (sid,)),
            ("DELETE FROM learner_profile WHERE id = ?;", (learner_id,)),
        ):
            with pytest.raises(
                (sqlite3.OperationalError, sqlite3.IntegrityError),
                match="immutable",
            ):
                store._conn.execute(sql, args)
            store._conn.rollback()
        # the row, its session and its learner all survive the attempt
        assert len(store.transcript_for_session(learner_id, sid)) == 1
        store.close()

    def test_delete_transcript_is_rejected(self, tmp_path):
        """Attempting DELETE on transcript must raise sqlite3.OperationalError
        with 'immutable' in the message."""
        store, learner_id, sid, tid = self._setup(tmp_path)
        with pytest.raises(
            (sqlite3.OperationalError, sqlite3.IntegrityError),
            match="immutable",
        ):
            store._conn.execute(
                "DELETE FROM transcript WHERE id = ?;",
                (tid,),
            )
        store.close()

    def test_row_unchanged_after_failed_update(self, tmp_path):
        """The transcript row must be bit-identical after a rejected UPDATE."""
        store, learner_id, sid, tid = self._setup(tmp_path)
        try:
            store._conn.execute(
                "UPDATE transcript SET text = 'tampered' WHERE id = ?;", (tid,)
            )
        except (sqlite3.OperationalError, sqlite3.IntegrityError):
            pass  # expected
        turns = store.transcript_for_session(learner_id, sid)
        assert turns[0]["text"] == "What is half of six?", (
            "transcript text was modified despite the trigger"
        )
        store.close()

    def test_subsequent_inserts_still_work_after_rejected_update(self, tmp_path):
        """INSERT must still work after a rejected UPDATE (no stuck transaction)."""
        store, learner_id, sid, tid = self._setup(tmp_path)
        try:
            store._conn.execute(
                "UPDATE transcript SET text = 'tampered' WHERE id = ?;", (tid,)
            )
        except (sqlite3.OperationalError, sqlite3.IntegrityError):
            pass  # expected — connection should still be usable
        # A new insert must succeed
        tid2 = store.write_transcript(learner_id, sid, 1, "learner", "Three")
        turns = store.transcript_for_session(learner_id, sid)
        assert len(turns) == 2
        assert turns[1]["id"] == tid2
        store.close()
