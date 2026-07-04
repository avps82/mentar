"""LearnerStore — minimal SQLite wrapper for Mentar learner data.

Spec: docs/PHASE0.md W3.6
Safety: docs/SAFETY.md Layer 4 (data/privacy), Layer 5 (parental oversight)
Tests: tests/db/test_datamodel.py (T3.6)

Design notes:
- Stdlib sqlite3 only; no ORM.
- Row factory = sqlite3.Row (dict-like access by column name).
- All queries are parameterised; no string interpolation.
- Schema applied from schema.sql on first open (user_version == 0).
- user_version == 1 after schema applied; future migrations bump this.
- Transcript immutability is enforced by DB triggers; this layer does not
  add a second guard — the trigger is the authority.
- Multi-learner namespacing: every write method accepts learner_id and
  every read method filters by learner_id.  Never query without it.
- export/backup = file copy at OS level; call close() first so WAL is
  checkpointed (see export note below).
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

# Path to the schema DDL file alongside this module.
_SCHEMA_PATH = Path(__file__).parent / "schema.sql"

_EXPECTED_VERSION = 2

# v1 -> v2 (A3, 2026-07-04): escalation_log gained severity/session_id/turn_index so
# SAFETY §3.3/§3.5's claim that every escalation row carries these is actually true.
_MIGRATIONS: dict[int, list[str]] = {
    1: [
        "ALTER TABLE escalation_log ADD COLUMN severity TEXT "
        "CHECK (severity IN ('low', 'high', 'critical'));",
        "ALTER TABLE escalation_log ADD COLUMN session_id TEXT;",
        "ALTER TABLE escalation_log ADD COLUMN turn_index INTEGER;",
    ],
}


class LearnerStore:
    """Local SQLite store for one Mentar installation (one .db file per device).

    Multi-learner support is achieved via the learner_id column present on
    every table — each method scopes queries to a single learner.

    Thread safety: the Flask dev server (`mentar serve`) handles requests on
    multiple worker threads. A single sqlite3.Connection cannot be shared
    across threads (raises "SQLite objects created in a thread can only be used
    in that same thread"), and even with check_same_thread=False a shared
    connection is unsafe under simultaneous use. So each thread gets its OWN
    connection (lazily, via the `_conn` property), all pointing at the same
    file. The DB is in WAL mode with a busy timeout, which makes concurrent
    multi-connection reads/writes safe (writers serialise + wait, not error).
    """

    def __init__(self, db_path: str | Path) -> None:
        """Open (or create) the SQLite database at *db_path*.

        If the database is new (user_version == 0), the schema DDL in
        schema.sql is applied and user_version is set to 1.
        """
        self._path = Path(db_path)
        self._local = threading.local()  # per-thread connection store
        # Open this thread's connection and apply the schema if the DB is new.
        self._apply_schema_if_needed()

    def _new_conn(self) -> sqlite3.Connection:
        """Open a fresh connection for the current thread with our pragmas."""
        conn = sqlite3.connect(str(self._path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Per-connection pragmas (FK enforcement + busy timeout are not shared
        # across connections; WAL is DB-level but cheap+idempotent to re-set).
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        return conn

    @property
    def _conn(self) -> sqlite3.Connection:
        """The current thread's connection, opened on first use in that thread."""
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = self._new_conn()
            self._local.conn = conn
        return conn

    # ── Schema management ────────────────────────────────────────────────────

    def _apply_schema_if_needed(self) -> None:
        """Apply schema.sql if the DB is uninitialised (user_version == 0)."""
        version = self._user_version()
        if version == 0:
            ddl = _SCHEMA_PATH.read_text(encoding="utf-8")
            self._conn.executescript(ddl)
            self._conn.commit()
        elif version < _EXPECTED_VERSION:
            # Run each incremental migration in order, then bump user_version.
            # A version with no registered migration (i.e. older than any key in
            # _MIGRATIONS) is a genuinely stale DB we don't know how to upgrade —
            # that stays a loud RuntimeError (T3.6(d): no silent corruption).
            for v in range(version, _EXPECTED_VERSION):
                statements = _MIGRATIONS.get(v)
                if statements is None:
                    raise RuntimeError(
                        f"Database schema version {version} is older than expected "
                        f"{_EXPECTED_VERSION} and has no migration path from v{v}. "
                        "Run the migration script."
                    )
                for stmt in statements:
                    self._conn.execute(stmt)
            self._conn.execute(f"PRAGMA user_version = {_EXPECTED_VERSION};")
            self._conn.commit()
        # version == _EXPECTED_VERSION: nothing to do.

    def _user_version(self) -> int:
        row = self._conn.execute("PRAGMA user_version;").fetchone()
        return int(row[0])

    def schema_version(self) -> int:
        """Return the current PRAGMA user_version of the database."""
        return self._user_version()

    # ── Learner profile ──────────────────────────────────────────────────────

    def create_learner(
        self,
        name: str,
        year_level: str,
        country: str,
        age_mode: str,
    ) -> int:
        """Insert a learner profile row and return the new learner_id (int)."""
        cur = self._conn.execute(
            """
            INSERT INTO learner_profile (name, year_level, country, age_mode)
            VALUES (?, ?, ?, ?)
            """,
            (name, year_level, country, age_mode),
        )
        self._conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    def get_learner(self, learner_id: int) -> sqlite3.Row | None:
        """Return the learner_profile row for *learner_id*, or None."""
        return self._conn.execute(
            "SELECT * FROM learner_profile WHERE id = ?;",
            (learner_id,),
        ).fetchone()

    # ── Session ──────────────────────────────────────────────────────────────

    def create_session(self, learner_id: int, session_id: str) -> None:
        """Insert a session row.  session_id is caller-supplied (e.g. UUID)."""
        self._conn.execute(
            "INSERT INTO session (id, learner_id) VALUES (?, ?);",
            (session_id, learner_id),
        )
        self._conn.commit()

    def end_session(self, learner_id: int, session_id: str, ended_reason: str) -> None:
        """Mark a session as ended."""
        self._conn.execute(
            """
            UPDATE session
               SET ended_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
                   ended_reason = ?
             WHERE id = ? AND learner_id = ?;
            """,
            (ended_reason, session_id, learner_id),
        )
        self._conn.commit()

    def get_session(self, learner_id: int, session_id: str) -> sqlite3.Row | None:
        """Return a session row, scoped to the given learner."""
        return self._conn.execute(
            "SELECT * FROM session WHERE id = ? AND learner_id = ?;",
            (session_id, learner_id),
        ).fetchone()

    # ── Skill state ──────────────────────────────────────────────────────────

    def update_skill_state(
        self,
        learner_id: int,
        skill_id: str,
        p_mastery: float,
        priors_used: bool,
    ) -> None:
        """Upsert the BKT mastery estimate for one skill.

        Only p_mastery and prior_mode are updated here because the BKT
        parameters (p_guess, p_slip, p_learns, p_forgets) are set once at
        cold-start from the priors table and not changed until the fitted
        model supersedes them (W3.3: N >= 100 scored responses per skill).
        """
        self._conn.execute(
            """
            INSERT INTO skill_state (learner_id, skill_id, p_mastery, prior_mode,
                                     updated_at)
            VALUES (?, ?, ?, ?,
                    strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            ON CONFLICT (learner_id, skill_id) DO UPDATE
               SET p_mastery  = excluded.p_mastery,
                   prior_mode = excluded.prior_mode,
                   updated_at = excluded.updated_at;
            """,
            (learner_id, skill_id, p_mastery, int(priors_used)),
        )
        self._conn.commit()

    def get_skill_state(self, learner_id: int, skill_id: str) -> sqlite3.Row | None:
        """Return the skill_state row for one (learner, skill) pair."""
        return self._conn.execute(
            "SELECT * FROM skill_state WHERE learner_id = ? AND skill_id = ?;",
            (learner_id, skill_id),
        ).fetchone()

    def all_skill_states(self, learner_id: int) -> list[sqlite3.Row]:
        """Return all skill_state rows for a learner."""
        return self._conn.execute(
            "SELECT * FROM skill_state WHERE learner_id = ? ORDER BY skill_id;",
            (learner_id,),
        ).fetchall()

    # ── Response log ─────────────────────────────────────────────────────────

    def write_response(
        self,
        learner_id: int,
        session_id: str,
        skill_id: str,
        prompt_ref: str,
        answer: str,
        scored: int,
        hinted: int,
        check_result: str | None = None,
    ) -> int:
        """Insert a response_log row and return the new response id."""
        cur = self._conn.execute(
            """
            INSERT INTO response_log
                (learner_id, session_id, skill_id, prompt_ref, answer,
                 scored, hinted, check_result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (learner_id, session_id, skill_id, prompt_ref, answer,
             scored, hinted, check_result),
        )
        self._conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    def session_responses(self, learner_id: int, session_id: str) -> list[dict]:
        """Return all response_log rows for one (learner, session) pair as dicts."""
        rows = self._conn.execute(
            """
            SELECT * FROM response_log
             WHERE learner_id = ? AND session_id = ?
             ORDER BY id;
            """,
            (learner_id, session_id),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Help events ──────────────────────────────────────────────────────────

    def write_help_event(
        self,
        learner_id: int,
        session_id: str,
        skill_id: str,
        modality: str,
        response_log_id: int,
    ) -> int:
        """Insert a help_event row and return the new id."""
        cur = self._conn.execute(
            """
            INSERT INTO help_event
                (learner_id, session_id, skill_id, modality, response_log_id)
            VALUES (?, ?, ?, ?, ?);
            """,
            (learner_id, session_id, skill_id, modality, response_log_id),
        )
        self._conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    def session_help_events(self, learner_id: int, session_id: str) -> list[dict]:
        """Return all help_event rows for one (learner, session) pair as dicts."""
        rows = self._conn.execute(
            """
            SELECT * FROM help_event
             WHERE learner_id = ? AND session_id = ?
             ORDER BY id;
            """,
            (learner_id, session_id),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Probe events ─────────────────────────────────────────────────────────

    def write_probe_event(
        self,
        learner_id: int,
        session_id: str,
        skill_id: str,
        response_log_id: int,
        retry_response_log_id: int | None,
        class_: str,
    ) -> int:
        """Insert a probe_event row and return the new id."""
        cur = self._conn.execute(
            """
            INSERT INTO probe_event
                (learner_id, session_id, skill_id, response_log_id,
                 retry_response_log_id, class)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (learner_id, session_id, skill_id, response_log_id,
             retry_response_log_id, class_),
        )
        self._conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    def session_probe_events(self, learner_id: int, session_id: str) -> list[dict]:
        """Return all probe_event rows for one (learner, session) pair as dicts."""
        rows = self._conn.execute(
            """
            SELECT * FROM probe_event
             WHERE learner_id = ? AND session_id = ?
             ORDER BY id;
            """,
            (learner_id, session_id),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Escalation log ───────────────────────────────────────────────────────

    def write_escalation(
        self,
        learner_id: int,
        trigger_class: str,
        trigger_text_verbatim: str,
        severity: str | None = None,
        session_id: str | None = None,
        turn_index: int | None = None,
        session_outcome: str | None = None,
    ) -> int:
        """Insert an escalation_log row and return the new id.

        trigger_text_verbatim is stored exactly as received — never truncated
        (SAFETY.md §3.3 Step 2: "never silently dropped"). severity/session_id/
        turn_index are optional (nullable) so older callers keep working, but the
        controller (the only production caller) always supplies all three (A3).
        session_outcome defaults to the table's DEFAULT ('frozen') when omitted.
        """
        if session_outcome is None:
            cur = self._conn.execute(
                """
                INSERT INTO escalation_log
                    (learner_id, trigger_class, trigger_text_verbatim,
                     severity, session_id, turn_index)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (learner_id, trigger_class, trigger_text_verbatim,
                 severity, session_id, turn_index),
            )
        else:
            cur = self._conn.execute(
                """
                INSERT INTO escalation_log
                    (learner_id, trigger_class, trigger_text_verbatim,
                     severity, session_id, turn_index, session_outcome)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (learner_id, trigger_class, trigger_text_verbatim,
                 severity, session_id, turn_index, session_outcome),
            )
        self._conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    def parent_ack_escalation(self, esc_id: int) -> None:
        """Record the parent's acknowledgment of an escalation event."""
        self._conn.execute(
            """
            UPDATE escalation_log
               SET parent_ack_at    = strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
                   session_outcome  = 'acknowledged'
             WHERE id = ?;
            """,
            (esc_id,),
        )
        self._conn.commit()

    def get_escalation(self, learner_id: int, esc_id: int) -> sqlite3.Row | None:
        """Return one escalation_log row, scoped to learner."""
        return self._conn.execute(
            "SELECT * FROM escalation_log WHERE id = ? AND learner_id = ?;",
            (esc_id, learner_id),
        ).fetchone()

    def learner_escalations(self, learner_id: int) -> list[dict]:
        """Return all escalation_log rows for a learner as dicts."""
        rows = self._conn.execute(
            "SELECT * FROM escalation_log WHERE learner_id = ? ORDER BY id;",
            (learner_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Transcript ───────────────────────────────────────────────────────────

    def write_transcript(
        self,
        learner_id: int,
        session_id: str,
        turn_index: int,
        role: str,
        text: str,
    ) -> int:
        """Append one turn to the immutable transcript and return the new id.

        Immutability is enforced by DB triggers (trg_transcript_no_update and
        trg_transcript_no_delete in schema.sql) — attempts to UPDATE or DELETE
        a transcript row raise sqlite3.OperationalError.
        """
        cur = self._conn.execute(
            """
            INSERT INTO transcript
                (learner_id, session_id, turn_index, role, text)
            VALUES (?, ?, ?, ?, ?);
            """,
            (learner_id, session_id, turn_index, role, text),
        )
        self._conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    def transcript_for_session(
        self, learner_id: int, session_id: str
    ) -> list[dict]:
        """Return all transcript rows for one (learner, session) pair as dicts.

        Ordered by turn_index ascending — safe for deterministic replay.
        """
        rows = self._conn.execute(
            """
            SELECT * FROM transcript
             WHERE learner_id = ? AND session_id = ?
             ORDER BY turn_index ASC;
            """,
            (learner_id, session_id),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Connection lifecycle ─────────────────────────────────────────────────

    def checkpoint(self) -> None:
        """Checkpoint the WAL so an OS file-copy produces a consistent snapshot.

        Call this before shutil.copy2() / any file-level export.
        PRAGMA wal_checkpoint(TRUNCATE) flushes and truncates the WAL file.
        """
        self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")

    def close(self) -> None:
        """Checkpoint and close the connection.

        After close() the .db file is safe to copy (export = file copy per W3.6).
        Checkpoint is best-effort: a locked WAL (e.g. failed trigger in tests) is
        tolerated — the connection still closes cleanly.
        """
        conn = getattr(self._local, "conn", None)
        if conn is None:
            return
        try:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        except Exception:
            pass
        conn.close()
        # Drop the ref so a later access in this thread reopens a live connection.
        self._local.conn = None

    # ── Context manager support ──────────────────────────────────────────────

    def __enter__(self) -> LearnerStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
