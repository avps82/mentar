"""LearnerStore -> SessionController adapter.

Lives in db/ (not web/) so the CLI's headless `run-session` doesn't have to
import mentar.web.app (and its hard Flask dependency) just to wire a DB store
to a controller (A17 — layering hygiene; REVIEW §8.3).
"""

from __future__ import annotations

from mentar.db.store import LearnerStore


class _DbStoreAdapter:
    """Adapts LearnerStore (int learner_id) to the controller's expected interface."""

    def __init__(self, store: LearnerStore, db_id: int) -> None:
        self._store = store
        self._db_id = db_id

    @property
    def db_path(self):
        return self._store.db_path

    def get_skill_state(self, learner_id: str, node_id: str):
        return self._store.get_skill_state(self._db_id, node_id)

    def update_skill_state(self, learner_id: str, node_id: str, p: float) -> None:
        self._store.update_skill_state(
            learner_id=self._db_id,
            skill_id=node_id,
            p_mastery=p,
            priors_used=True,  # pilot uses cold-start priors (W3.3: fitted only at N>=100)
        )

    def write_escalation(
        self,
        learner_id: str,
        trigger_class: str,
        trigger_text_verbatim: str,
        severity: str | None = None,
        session_id: str | None = None,
        turn_index: int | None = None,
        session_outcome: str | None = None,
    ) -> int:
        # Verbatim text stored untruncated (SAFETY §3.3 Step 2).
        return self._store.write_escalation(
            learner_id=self._db_id,
            trigger_class=trigger_class,
            trigger_text_verbatim=trigger_text_verbatim,
            severity=severity,
            session_id=session_id,
            turn_index=turn_index,
            session_outcome=session_outcome,
        )

    # ── Durable session logging (controller calls these best-effort) ──────────

    def create_session(self, session_id: str, rng_seed: int | None = None) -> None:
        self._store.create_session(self._db_id, session_id, rng_seed=rng_seed)

    def end_session(self, session_id: str, ended_reason: str) -> None:
        self._store.end_session(self._db_id, session_id, ended_reason)

    def update_session_checkpoint(self, session_id: str, checkpoint_json: str) -> None:
        self._store.update_session_checkpoint(self._db_id, session_id, checkpoint_json)

    def write_transcript(self, session_id: str, turn_index: int, role: str, text: str) -> int:
        return self._store.write_transcript(self._db_id, session_id, turn_index, role, text)

    def write_response(
        self, session_id: str, skill_id: str, prompt_ref: str, answer: str,
        scored: int, hinted: int, check_result: str | None,
    ) -> int:
        return self._store.write_response(
            self._db_id, session_id, skill_id, prompt_ref, answer, scored, hinted, check_result,
        )

    def write_help_event(
        self, session_id: str, skill_id: str, modality: str, response_log_id: int,
    ) -> int:
        return self._store.write_help_event(
            self._db_id, session_id, skill_id, modality, response_log_id,
        )

    def write_probe_event(
        self, session_id: str, skill_id: str, response_log_id: int,
        retry_response_log_id: int | None, class_: str,
    ) -> int:
        return self._store.write_probe_event(
            self._db_id, session_id, skill_id, response_log_id, retry_response_log_id, class_,
        )
