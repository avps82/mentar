-- Mentar learner-data schema
-- Spec: docs/PHASE0.md W3.6; docs/SPEC.md §6.2, §11, §13–14, §16 layer 4–5
-- Safety: docs/SAFETY.md Layer 4 (data/privacy) and Layer 5 (parental oversight)
--
-- Design decisions (defensible defaults):
--   * PRAGMA user_version = 1 — migration tracker per W3.6; bump on every schema change.
--   * All timestamps stored as ISO-8601 TEXT (UTC).  SQLite has no native DATETIME type;
--     TEXT with CHECK ensures ISO-8601 pattern; comparisons work lexicographically.
--   * transcript rows are immutable: AFTER UPDATE / AFTER DELETE triggers RAISE(ABORT, …).
--   * Multi-learner namespacing: every table carries learner_id FK to learner_profile.id;
--     no cross-learner data accessible without an explicit WHERE learner_id = ?.
--   * export/backup = OS-level file copy (single .db file; no WAL epoch to worry about
--     for cold copy because store.close() calls wal_checkpoint(TRUNCATE) before copy).
--   * Retention policy (90-day default, SAFETY.md §4.6) is enforced at the application
--     layer (LearnerStore), not in SQL, so the parent can reconfigure the window without
--     a schema migration.
--   * session_outcome in escalation_log stores the session's final state string rather
--     than a FK to session, because the session may be ended/deleted independently of
--     the escalation record (escalation_log is intentionally harder to purge).

PRAGMA user_version = 3;
PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1.  learner_profile
--     One row per child.  age_mode encodes the SPEC §6.2 supervision mode.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS learner_profile (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL CHECK (length(trim(name)) > 0),
    year_level  TEXT    NOT NULL CHECK (length(trim(year_level)) > 0),  -- "Year 4", "Grade 3", "pilot", etc. — matches curriculum template format
    country     TEXT    NOT NULL CHECK (length(trim(country)) > 0),
    age_mode    TEXT    NOT NULL CHECK (age_mode IN ('parent_mediated', 'independent')),
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.  session
--     Groups response_log, help_event, probe_event, transcript rows into one
--     tutoring session.  session_id is a UUID/opaque string owned by the caller.
--     rng_seed (v3, A19): the seed SessionController's internal RNG was constructed
--     with, so a session's non-deterministic choices (pattern/modality/praise-variant
--     selection) can be replayed exactly given the same seed.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS session (
    id           TEXT    PRIMARY KEY,          -- caller-supplied UUID or slug
    learner_id   INTEGER NOT NULL REFERENCES learner_profile(id) ON DELETE CASCADE,
    started_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    ended_at     TEXT,                         -- NULL while session is live
    ended_reason TEXT,                         -- 'completed'|'abandoned'|'escalation_freeze'|…
    rng_seed     INTEGER
);

CREATE INDEX IF NOT EXISTS idx_session_learner ON session(learner_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.  skill_state
--     Per-learner, per-skill BKT parameters + current mastery estimate.
--     prior_mode = 1 while N < 100 scored responses (W3.3 cold-start policy).
--     updated_at lets the forgetting_suspect window query work (W3.4).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS skill_state (
    learner_id   INTEGER NOT NULL REFERENCES learner_profile(id) ON DELETE CASCADE,
    skill_id     TEXT    NOT NULL CHECK (length(trim(skill_id)) > 0),
    p_mastery    REAL    NOT NULL DEFAULT 0.0 CHECK (p_mastery BETWEEN 0.0 AND 1.0),
    p_guess      REAL    NOT NULL DEFAULT 0.2 CHECK (p_guess   BETWEEN 0.0 AND 1.0),
    p_slip       REAL    NOT NULL DEFAULT 0.1 CHECK (p_slip    BETWEEN 0.0 AND 1.0),
    p_learns     REAL    NOT NULL DEFAULT 0.2 CHECK (p_learns  BETWEEN 0.0 AND 1.0),
    p_forgets    REAL    NOT NULL DEFAULT 0.0 CHECK (p_forgets BETWEEN 0.0 AND 1.0),
    prior_mode   INTEGER NOT NULL DEFAULT 1   CHECK (prior_mode IN (0, 1)),  -- bool
    updated_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    PRIMARY KEY (learner_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_skill_state_learner ON skill_state(learner_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.  response_log
--     Every scored interaction.  hinted = 1 triggers the hinted-win discount
--     in the BKT update wrapper (SPEC §11, W3.3).  check_result stores the
--     deterministic verifier output (SPEC §15 layer 2) as a TEXT blob.
--     prompt_ref is a template-id+hash pair (W6.2 prompt versioning, T4.6).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS response_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id      INTEGER NOT NULL REFERENCES learner_profile(id) ON DELETE CASCADE,
    session_id      TEXT    NOT NULL REFERENCES session(id)         ON DELETE CASCADE,
    skill_id        TEXT    NOT NULL CHECK (length(trim(skill_id)) > 0),
    prompt_ref      TEXT    NOT NULL,   -- "{template_id}:{sha256_prefix}" per W6.2
    answer          TEXT    NOT NULL,
    scored          INTEGER NOT NULL CHECK (scored  IN (0, 1)),  -- 0=wrong, 1=correct
    hinted          INTEGER NOT NULL CHECK (hinted  IN (0, 1)),  -- 0=unaided, 1=after Help
    check_result    TEXT,               -- verifier JSON blob; NULL for non-checkable items
    timestamp       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_response_log_learner ON response_log(learner_id);
CREATE INDEX IF NOT EXISTS idx_response_log_session ON response_log(learner_id, session_id);
CREATE INDEX IF NOT EXISTS idx_response_log_skill   ON response_log(learner_id, skill_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.  help_event
--     Logged each time a learner presses Help (SPEC §13).
--     modality = one of {visual, concrete, analogy, story, formal} (SPEC §13.2).
--     response_log_id references the response that triggered Help.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS help_event (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id       INTEGER NOT NULL REFERENCES learner_profile(id) ON DELETE CASCADE,
    session_id       TEXT    NOT NULL REFERENCES session(id)         ON DELETE CASCADE,
    skill_id         TEXT    NOT NULL CHECK (length(trim(skill_id)) > 0),
    modality         TEXT    NOT NULL CHECK (
                         modality IN ('visual', 'concrete', 'analogy', 'story', 'formal')
                     ),
    response_log_id  INTEGER NOT NULL REFERENCES response_log(id)   ON DELETE CASCADE,
    timestamp        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_help_event_learner ON help_event(learner_id);
CREATE INDEX IF NOT EXISTS idx_help_event_session ON help_event(learner_id, session_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.  probe_event
--     Proactive probes (SPEC §14.2).  class_ mirrors the W3.4 decision table.
--     retry_response_log_id is NULL when no retry was required (clean_pass or
--     slip_suspect from a single failure).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS probe_event (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id              INTEGER NOT NULL REFERENCES learner_profile(id) ON DELETE CASCADE,
    session_id              TEXT    NOT NULL REFERENCES session(id)         ON DELETE CASCADE,
    skill_id                TEXT    NOT NULL CHECK (length(trim(skill_id)) > 0),
    response_log_id         INTEGER NOT NULL REFERENCES response_log(id)   ON DELETE CASCADE,
    retry_response_log_id   INTEGER          REFERENCES response_log(id),  -- nullable
    class                   TEXT    NOT NULL CHECK (
                                class IN (
                                    'false_confidence',
                                    'slip_suspect',
                                    'forgetting_suspect',
                                    'clean_pass'
                                )
                            ),
    timestamp               TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_probe_event_learner ON probe_event(learner_id);
CREATE INDEX IF NOT EXISTS idx_probe_event_session ON probe_event(learner_id, session_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.  escalation_log
--     Immutable audit of distress/disclosure events (SAFETY.md Layer 3, §3.3).
--     trigger_text_verbatim MUST be stored exactly as received (never truncated).
--     parent_ack_at is NULL until the parent acknowledges (Layer 3 §3.3 Step 6).
--     This table is intentionally NOT subject to the 90-day rolling purge;
--     purge requires explicit multi-step parent action (SAFETY.md §4.6).
--     session_outcome records the state of the session when it was frozen
--     (e.g. 'frozen', 'ended_by_parent', 'resumed').
--     Special value 'logged_only' is used for adversarial_jailbreak class (design §4.3):
--     the trigger is logged for audit but the session is NOT frozen — Layer 1 §1.4 already
--     blocks the input inline. All other trigger classes use 'frozen' as the initial value.
--     v2 (A3, 2026-07-04): added severity/session_id/turn_index so SAFETY §3.3/§3.5's claim
--     that every escalation row carries these is actually true. session_id/turn_index are
--     TEXT/INTEGER (not FKs) — an escalation row must survive session deletion (see above).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS escalation_log (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id              INTEGER NOT NULL REFERENCES learner_profile(id) ON DELETE CASCADE,
    trigger_class           TEXT    NOT NULL,   -- e.g. 'harm_to_self', 'abuse_disclosure'
    trigger_text_verbatim   TEXT    NOT NULL,   -- exact child input; never truncated
    severity                TEXT    CHECK (severity IN ('low', 'high', 'critical')),
    session_id              TEXT,               -- the tutoring session the trigger fired in
    turn_index              INTEGER,            -- 0-based turn within that session
    freeze_started_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    parent_ack_at           TEXT,               -- NULL until acknowledged
    session_outcome         TEXT    NOT NULL DEFAULT 'frozen'
);

CREATE INDEX IF NOT EXISTS idx_escalation_log_learner ON escalation_log(learner_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 8.  transcript
--     Immutable turn-by-turn record (SAFETY.md Layer 5, §5.4; SPEC §6.2).
--     role must be one of {learner, tutor, system}.
--     Immutability enforced by AFTER UPDATE and AFTER DELETE triggers below.
--     turn_index is 0-based within a session.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transcript (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id  INTEGER NOT NULL REFERENCES learner_profile(id) ON DELETE CASCADE,
    session_id  TEXT    NOT NULL REFERENCES session(id)         ON DELETE CASCADE,
    turn_index  INTEGER NOT NULL CHECK (turn_index >= 0),
    role        TEXT    NOT NULL CHECK (role IN ('learner', 'tutor', 'system')),
    text        TEXT    NOT NULL,
    timestamp   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (learner_id, session_id, turn_index)
);

CREATE INDEX IF NOT EXISTS idx_transcript_learner ON transcript(learner_id);
CREATE INDEX IF NOT EXISTS idx_transcript_session ON transcript(learner_id, session_id);

-- ─── Immutability triggers ────────────────────────────────────────────────────
-- These ensure the transcript is an immutable audit log (SPEC §6.2, SAFETY.md §4.3).
-- RAISE(ABORT, …) rolls back the offending statement and raises OperationalError in sqlite3.

CREATE TRIGGER IF NOT EXISTS trg_transcript_no_update
AFTER UPDATE ON transcript
BEGIN
    SELECT RAISE(ABORT, 'transcript rows are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_transcript_no_delete
AFTER DELETE ON transcript
BEGIN
    SELECT RAISE(ABORT, 'transcript rows are immutable');
END;
