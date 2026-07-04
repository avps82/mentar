"""Session FSM controller — wires BKT, fringe, escalation, grounding, prompts.

Spec: docs/SESSION_FSM.md (W6.1); SPEC §12-14; tests: T3.7, T4.x, T5.x.

The controller drives the session state machine.  Call step() repeatedly:
  - pass None for the first call (SESSION_START)
  - pass the child's typed text for every subsequent call
  - inspect TurnResult.done to know when the session ends
  - inspect TurnResult.escalated for the safety-freeze path

Prompt templates are loaded once from prompt_dir; grounding is resolved per turn.
LLM calls are injected via llm_call so the caller controls the backend (llama.cpp /
vLLM / any OpenAI-compatible endpoint).  The controller itself has no network I/O.
"""

from __future__ import annotations

import json
import logging
import random
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from mentar.engine.bkt import P_L0, bkt_update, params_for
from mentar.engine.explain_check import has_verified_failure
from mentar.engine.fringe import DEFAULT_MASTERY_THRESHOLD, outer_fringe
from mentar.engine.probe_classify import ProbeClass, classify_probe
from mentar.eval.verify_numeric import CheckResult, check
from mentar.grounding import resolve_grounding
from mentar.safety.credential_guard import redact_credentials
from mentar.safety.escalation import (
    HANDOFF_MESSAGE_PRIMARY,
    Severity,
    classify,
)
from mentar.safety.output_guard import NEUTRAL_REDIRECT, SEVERITY_BY_CLASS, screen_output

logger = logging.getLogger(__name__)

HELP_MODALITIES = ["visual", "concrete", "analogy", "story", "formal"]
STOP_WORDS = {"stop", "quit", "bye", "exit"}  # learner-initiated session end
HELP_WORDS = {"?", "help", "h"}               # learner-initiated help request
STALE_MASTERY_DAYS = 14  # mastery older than this counts as "stale" for forgetting detection
# W5.6 continuous-assent: shown ONCE at the start so the child knows they can withdraw anytime.
# (A learner 'stop' = self-withdrawal; a parent 'end' via /parent/ack = parent-withdrawal —
# both recorded in session.ended_reason. See docs/design/W5.6_decision_prep.md.)
ASSENT_LINE = "Remember — you can stop anytime, just say 'stop'."

# Deterministic feedback phrasings — varied (not static) so the tutor doesn't sound robotic.
# Edit/extend these pools to retune the voice; one is chosen at random per turn.
PRAISE_VARIANTS = [
    "That's right — nice work!",
    "Correct! Well done.",
    "Yes, that's it — great job!",
    "Spot on — brilliant!",
    "You got it — awesome!",
]
WRONG_VARIANTS = [
    "Not quite — that's okay, mistakes help us learn. Let's work through it together.",
    "Good try! That's not quite it — let's figure it out together.",
    "Not this time — no worries, let's take a look together.",
    "Close! Let's work through it step by step.",
    "Hmm, not quite — let's sort it out together.",
]


def _is_stop(text: str) -> bool:
    return text.strip().lower() in STOP_WORDS


def _is_help_request(text: str) -> bool:
    return text.strip().lower() in HELP_WORDS


_DONT_KNOW_PHRASES = {"i don't know", "idk", "no idea", "dunno", "i dont know"}
_QUESTION_STARTERS = ("what", "how", "why", "when", "where", "who", "can", "is", "does")


def _is_dont_know_or_question(text: str) -> bool:
    """A21 — interaction-scope v0: deterministic carve-out for two common
    non-answer child inputs that were previously force-scored (corrupting BKT):
    a declared "don't know", and a question-shaped clarifying request (e.g.
    "what does numerator mean?"). Full taxonomy stays deferred
    (docs/design/INTERACTION_SCOPE.md); this is only the narrow ratified slice.
    """
    stripped = text.strip().lower()
    if stripped in _DONT_KNOW_PHRASES:
        return True
    if stripped.endswith("?"):
        return True
    return stripped.startswith(_QUESTION_STARTERS)


def _is_stale_mastery(updated_at: str | None, now: datetime | None = None) -> bool:
    """True if a skill's mastery timestamp is older than STALE_MASTERY_DAYS.

    Pure + null-safe: missing/unparseable timestamps are treated as not-stale (no false
    forgetting signal). ``updated_at`` is an ISO-8601 string (schema writes ...Z).
    """
    if not updated_at:
        return False
    try:
        ts = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return False
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    now = now or datetime.now(UTC)
    return (now - ts).days > STALE_MASTERY_DAYS


def _raise_on_uncovered_nodes(curriculum: dict, item_bank) -> None:
    """A9: a node with a real checker (checker != 'none') but no item-source
    coverage falls back to _do_present's LLM-generated-question path, which
    scores against node['expected_answer'] — but that field is a transfer-seed
    QUESTION string (see engine/curriculum.py), not a real answer. That's a
    guaranteed FAIL/SAFE_REJECT, silently. Refuse loudly at construction time
    instead (only checked when an item_bank is actually wired — a bare
    item_bank=None is the deliberate legacy/test fallback, not a misconfigured
    production subject)."""
    uncovered = [
        nid for nid, node in curriculum.items()
        if node.get("checker", "none") != "none" and not item_bank.has(nid)
    ]
    if uncovered:
        raise RuntimeError(
            f"Curriculum node(s) {uncovered} have a checker but no item-bank/generator "
            "coverage — scoring would silently fall back to expected_answer, which is "
            "a transfer-seed QUESTION, not a real answer. Add coverage or checker: none."
        )


HELP_RETRY_CAP = 3
UNREADABLE_STREAK_CAP = 3  # A9: consecutive SAFE_REJECT/EXTRACT_FAIL before routing to Help
PROBE_EVERY_N = 5  # W5.3 pilot default
# When a proactive probe shows mastery was overestimated (false_confidence /
# forgetting / slip-after-retry), demote mastery to this so the node returns to
# normal practice instead of being re-probed endlessly. Below DEFAULT_MASTERY_THRESHOLD.
PROBE_DEMOTE_MASTERY = 0.6


class FSMState(str, Enum):
    SESSION_START         = "SESSION_START"
    NODE_SELECT           = "NODE_SELECT"
    PATTERN_SELECT        = "PATTERN_SELECT"
    PRESENT               = "PRESENT"
    AWAIT_ANSWER          = "AWAIT_ANSWER"
    SCORE                 = "SCORE"
    BKT_UPDATE            = "BKT_UPDATE"
    BRANCH_DECISION       = "BRANCH_DECISION"
    HELP_MODALITY_SELECT  = "HELP_MODALITY_SELECT"
    HELP_EXPLAIN          = "HELP_EXPLAIN"
    HELP_RECHECK_PRESENT  = "HELP_RECHECK_PRESENT"
    HELP_RECHECK_AWAIT    = "HELP_RECHECK_AWAIT"
    HELP_RECHECK_SCORE    = "HELP_RECHECK_SCORE"
    HELP_RECHECK_BKT_UPDATE = "HELP_RECHECK_BKT_UPDATE"
    HELP_RETRY_DECISION   = "HELP_RETRY_DECISION"
    LINK_BACK             = "LINK_BACK"
    PROBE_PRESENT         = "PROBE_PRESENT"
    PROBE_AWAIT_ANSWER    = "PROBE_AWAIT_ANSWER"
    PROBE_SCORE           = "PROBE_SCORE"
    PROBE_CLASSIFY        = "PROBE_CLASSIFY"
    ESCALATION_FREEZE     = "ESCALATION_FREEZE"
    PARENT_ACK_WAIT       = "PARENT_ACK_WAIT"
    SESSION_END_COMPLETE  = "SESSION_END_COMPLETE"
    SESSION_END_BY_LEARNER = "SESSION_END_BY_LEARNER"
    SESSION_END_BY_PARENT = "SESSION_END_BY_PARENT"


_TERMINAL = {
    FSMState.SESSION_END_COMPLETE,
    FSMState.SESSION_END_BY_LEARNER,
    FSMState.SESSION_END_BY_PARENT,
}

_AWAIT = {
    FSMState.AWAIT_ANSWER,
    FSMState.HELP_RECHECK_AWAIT,
    FSMState.PROBE_AWAIT_ANSWER,
    FSMState.PARENT_ACK_WAIT,
    FSMState.ESCALATION_FREEZE,
}

# Terminal state -> session.ended_reason recorded when the session closes.
_END_REASON = {
    FSMState.SESSION_END_COMPLETE: "completed",
    FSMState.SESSION_END_BY_LEARNER: "ended_by_learner",
    FSMState.SESSION_END_BY_PARENT: "ended_by_parent",
}


@dataclass
class TurnResult:
    state: str
    text: str
    done: bool
    escalated: bool


@dataclass
class _SessionCtx:
    """Mutable FSM context — all transient state for one session."""
    state: FSMState = FSMState.SESSION_START
    mastery: dict = field(default_factory=dict)      # node_id -> float
    mastery_updated_at: dict = field(default_factory=dict)  # node_id -> ISO ts | None
    current_node_id: str | None = None
    current_pattern: str | None = None
    current_question: str | None = None           # rendered question text
    current_item: object | None = None            # current checkable Item (or None = LLM-gen)
    current_answer: str | None = None             # child's latest answer
    last_scored_correct: bool | None = None
    items_since_probe: int = 0
    unreadable_streak: int = 0     # A9: consecutive SAFE_REJECT/EXTRACT_FAIL on this question
    # Help loop
    help_n: int = 0                                  # retry counter (1-indexed)
    help_modalities_used: list = field(default_factory=list)
    help_answer: str | None = None
    help_scored_correct: bool | None = None
    # A5: per-node, CHILD-INITIATED help only (never the auto-help branch in
    # _do_bkt_update) — the false-confidence probe signal must not be polluted by
    # a previous node's help use or by the system's own auto-help scaffolding.
    help_by_node: dict = field(default_factory=dict)
    # Probe loop
    probe_variant: int = 0                           # 0 = first, 1 = retry
    probe_first_correct: bool | None = None
    probe_answer: str | None = None
    probe_scored_correct: bool | None = None
    probe_response_log_id: int | None = None         # FK target for probe_event linkage
    probe_retry_response_log_id: int | None = None
    # Durable logging
    turn_index: int = 0                              # next transcript turn index (0-based)


class SessionController:
    """Drives the Mentar session FSM.  One instance per learner session."""

    def __init__(
        self,
        llm_call: Callable[[list[dict]], str],
        prompt_dir: Path,
        grounding_cfg: dict,
        curriculum: dict,
        db_store,
        learner_id: str,
        item_bank=None,
        session_id: str | None = None,
        subject: str = "maths",
        scope_line: str | None = None,
    ) -> None:
        self._llm = self._make_safe_llm(llm_call)
        self._prompt_dir = Path(prompt_dir)
        self._grounding_cfg = grounding_cfg
        self._curriculum = curriculum          # node_id -> {concept, answer_type, checker, expected_answer, grounding, prerequisites, bkt_priors?}
        self._store = db_store
        self._learner_id = learner_id
        # A7: fills the system prompt's {{subject}}/{{scope_line}} slots — the active
        # curriculum template's `subject:` (e.g. "mathematics", "science"); scope_line
        # defaults to the same value (a short "stay within X" phrase). Without this the
        # prompt hardcoded "fractions" regardless of the active subject (REVIEW §2.1).
        self._subject = subject
        self._scope_line = scope_line or subject
        # One tutoring session per controller instance. A session row is created lazily
        # on the first step() and closed at a terminal state (both best-effort).
        self._session_id = session_id or uuid.uuid4().hex
        self._session_created = False
        self._session_ended = False
        # Optional ItemBank: when present, checkable questions are drawn from it (the
        # verifier scores against the item's ground truth).  When None, fall back to the
        # legacy LLM-generated question + node["expected_answer"] path.
        self._item_bank = item_bank
        if self._item_bank is not None:
            _raise_on_uncovered_nodes(self._curriculum, self._item_bank)
        self._templates: dict[str, str] = {}  # loaded lazily
        self._assent_shown = False             # W5.6: assent line shown once, first turn
        self._ctx = _SessionCtx()

    # ── Public API ────────────────────────────────────────────────────────────

    def step(self, learner_input: str | None) -> TurnResult:
        """Advance the FSM by one turn, persisting the transcript around it.

        Wraps the FSM core (:meth:`_step_core`) with best-effort durable logging:
        the child's input and the tutor's reply are appended to the immutable
        transcript, and the session row is created/closed at the boundaries.
        All persistence is best-effort — a DB failure must never block tutoring.
        """
        self._maybe_create_session()
        if (
            learner_input is not None
            and learner_input.strip()
            and self._ctx.state not in _TERMINAL
        ):
            self._log_transcript("learner", learner_input)
        result = self._step_core(learner_input)
        if result.text and not self._assent_shown:
            # W5.6: prepend the continuous-assent line to the very first child-facing turn.
            self._assent_shown = True
            result = TurnResult(
                state=result.state, text=f"{ASSENT_LINE}\n\n{result.text}",
                done=result.done, escalated=result.escalated,
            )
        if result.text:
            self._log_transcript("tutor", result.text)
        if result.done:
            self._maybe_end_session(self._ctx.state)
        return result

    def parent_acknowledge(self, action: str) -> TurnResult:
        """Parent control-plane action on a frozen/awaiting session: ``resume``/``end``.

        Separate from :meth:`step` on purpose — the escalation freeze stays *absorbing*
        for child input (a child can never unfreeze a session by typing), so only the
        parent UI (``/parent/ack``) drives the transition out of ESCALATION_FREEZE via
        this method. On resume the FSM is driven to present the next question.
        """
        ctx = self._ctx
        self._maybe_create_session()
        if ctx.state not in (FSMState.ESCALATION_FREEZE, FSMState.PARENT_ACK_WAIT):
            # Nothing to acknowledge; report current status with no side effects.
            return TurnResult(
                state=ctx.state.value, text="",
                done=ctx.state in _TERMINAL,
                escalated=ctx.state is FSMState.ESCALATION_FREEZE,
            )
        self._log_transcript("system", f"parent_ack:{action}")
        result = self._handle_parent_ack(action)
        # Resume leaves the FSM at NODE_SELECT (transient) — drive it to the next
        # question so the child has something to do.
        if not result.done and ctx.state not in _AWAIT and ctx.state not in _TERMINAL:
            driven = self._step_core(None)
            text = "\n\n".join(t for t in (result.text, driven.text) if t)
            result = TurnResult(
                state=ctx.state.value, text=text, done=driven.done, escalated=False,
            )
        if result.text:
            self._log_transcript("tutor", result.text)
        if result.done:
            self._maybe_end_session(ctx.state)
        return result

    def _step_core(self, learner_input: str | None) -> TurnResult:
        """Advance the FSM by one logical turn.

        Drive through transient states automatically; stop at any state that
        requires user input (AWAIT_*) or is terminal.  Returns the text to show
        the child and the new FSM state name.
        """
        ctx = self._ctx

        # Global pre-empt: escalation check on any non-None child input.
        if learner_input is not None and ctx.state not in _TERMINAL:
            if ctx.state is FSMState.ESCALATION_FREEZE:
                # Absorbing — ignore tutoring input, stay frozen.
                return TurnResult(
                    state=ctx.state.value, text="", done=False, escalated=True
                )
            if ctx.state is FSMState.PARENT_ACK_WAIT:
                return self._handle_parent_ack(learner_input)
            trigger = classify(learner_input)
            if trigger is not None:
                # Log every trigger for the parent (SAFETY §3.x): full UNTRUNCATED
                # text + class + severity/session/turn (A3). Best-effort — a DB
                # failure must never block handling.
                session_outcome = (
                    "logged_only" if trigger.severity is Severity.LOW else "frozen"
                )
                try:
                    self._store.write_escalation(
                        self._learner_id,
                        trigger.trigger_class.value,
                        learner_input,
                        severity=trigger.severity.value,
                        session_id=self._session_id,
                        turn_index=ctx.turn_index,
                        session_outcome=session_outcome,
                    )
                except Exception:
                    logger.warning("escalation: failed to persist escalation_log row", exc_info=True)
                    self._write_escalation_fallback(
                        trigger.trigger_class.value, trigger.severity.value, learner_input
                    )

                if trigger.severity is Severity.LOW:
                    # LOW (adversarial_jailbreak): logged-only, NOT frozen (design §4.3).
                    # A child poking the AI shouldn't trigger the distress handoff or end
                    # the lesson — gently redirect and carry on with the current question.
                    logger.info(
                        "jailbreak (logged, not frozen): span=%s", trigger.matched_span[:80]
                    )
                    redirect = "Let's keep going with our maths! 😊"
                    if ctx.current_question:
                        redirect = f"{redirect}\n\n{ctx.current_question}"
                    return TurnResult(
                        state=ctx.state.value, text=redirect, done=False, escalated=False
                    )

                # CRITICAL / HIGH: freeze + parent handoff.
                ctx.state = FSMState.ESCALATION_FREEZE
                logger.warning(
                    "escalation: span=%s class=%s", trigger.matched_span[:80], trigger.trigger_class
                )
                return TurnResult(
                    state=ctx.state.value,
                    text=HANDOFF_MESSAGE_PRIMARY,
                    done=False,
                    escalated=True,
                )

        # Drive transient states until we hit an await or terminal state.
        output_text = ""
        for _ in range(40):  # guard against infinite loops in tests
            state = ctx.state
            if state in _TERMINAL:
                return TurnResult(state=state.value, text=output_text, done=True, escalated=False)
            if state in _AWAIT and learner_input is None and state != FSMState.SESSION_START:
                # Already waiting; caller must supply input.
                return TurnResult(state=state.value, text=output_text, done=False, escalated=False)

            text, advance = self._tick(state, learner_input)
            if text:
                # Accumulate across ticks: a single turn can emit several messages
                # (e.g. a Help explanation THEN the re-check question). Overwriting would
                # drop the explanation and show only the last message.
                output_text = f"{output_text}\n\n{text}" if output_text else text
            learner_input = None  # consumed; subsequent ticks are transient
            if not advance:
                break  # reached a natural await/terminal

        return TurnResult(
            state=ctx.state.value,
            text=output_text,
            done=ctx.state in _TERMINAL,
            escalated=ctx.state is FSMState.ESCALATION_FREEZE,
        )

    @property
    def state(self) -> str:
        return self._ctx.state.value

    @property
    def session_id(self) -> str:
        """The id of this controller's tutoring session (for durable-log reads)."""
        return self._session_id

    # ── Durable logging (best-effort) ─────────────────────────────────────────

    def _safe_store(self, method: str, *args):
        """Call an optional store method; never let persistence break a turn.

        Returns the call result (e.g. a new row id) or None when the store does
        not implement *method* (lightweight test fakes) or the write fails. This
        mirrors the existing best-effort escalation/BKT persistence: a logging
        failure must never crash a tutoring turn.
        """
        fn = getattr(self._store, method, None)
        if fn is None:
            return None
        try:
            return fn(*args)
        except Exception:
            logger.warning("store.%s failed", method, exc_info=True)
            return None

    def _write_escalation_fallback(
        self, trigger_class: str, severity: str, trigger_text_verbatim: str
    ) -> None:
        """A3/A15 — durable escalation logging is safety-critical (SAFETY §3.1);
        `write_escalation` failing must never silently drop the disclosure. Append
        one JSON line to escalation_fallback.log next to the DB file, so a parent
        reading the log directly (or the parent view's degraded banner) can still
        recover it. Best-effort: if even this fails, we've done what we can.
        """
        db_path = getattr(self._store, "db_path", None)
        fallback_path = (
            Path(db_path).parent / "escalation_fallback.log" if db_path else None
        )
        if fallback_path is None:
            return
        line = json.dumps({
            "iso_ts": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "trigger_class": trigger_class,
            "severity": severity,
            "verbatim_text": trigger_text_verbatim,
        })
        try:
            with open(fallback_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            logger.error("escalation: fallback log write also failed", exc_info=True)

    def _maybe_create_session(self) -> None:
        if not self._session_created:
            self._session_created = True
            self._safe_store("create_session", self._session_id)

    def _maybe_end_session(self, state: FSMState) -> None:
        if not self._session_ended:
            self._session_ended = True
            self._safe_store("end_session", self._session_id, _END_REASON.get(state, "ended"))

    def _log_transcript(self, role: str, text: str) -> None:
        idx = self._ctx.turn_index
        self._ctx.turn_index += 1
        self._safe_store("write_transcript", self._session_id, idx, role, text)

    def _log_response(
        self, skill_id: str | None, answer: str | None, *,
        scored: bool, hinted: bool, outcome,
    ) -> int | None:
        """Persist one scored response; return its row id (for help/probe FKs)."""
        item = self._ctx.current_item
        prompt_ref = (
            f"item:{item.id}" if item is not None else f"pattern:{self._ctx.current_pattern}"
        )
        return self._safe_store(
            "write_response", self._session_id, skill_id, prompt_ref,
            answer or "", int(bool(scored)), int(bool(hinted)),
            outcome.result.value if outcome is not None else None,
        )

    def _log_probe_event(self, skill_id: str | None, probe_class: ProbeClass) -> None:
        rid = self._ctx.probe_response_log_id
        if rid is None:
            return  # response logging was skipped (e.g. a fake store) — nothing to link
        self._safe_store(
            "write_probe_event", self._session_id, skill_id, rid,
            self._ctx.probe_retry_response_log_id, probe_class.value,
        )

    # ── FSM tick dispatch ─────────────────────────────────────────────────────

    def _tick(self, state: FSMState, inp: str | None) -> tuple[str, bool]:
        """Process one FSM state.  Returns (text_output, should_advance_immediately)."""
        match state:
            case FSMState.SESSION_START:
                return self._do_session_start()
            case FSMState.NODE_SELECT:
                return self._do_node_select()
            case FSMState.PATTERN_SELECT:
                return self._do_pattern_select()
            case FSMState.PRESENT:
                return self._do_present()
            case FSMState.AWAIT_ANSWER:
                return self._do_await_answer(inp)
            case FSMState.SCORE:
                return self._do_score()
            case FSMState.BKT_UPDATE:
                return self._do_bkt_update(hinted=False)
            case FSMState.BRANCH_DECISION:
                return self._do_branch_decision()
            case FSMState.HELP_MODALITY_SELECT:
                return self._do_help_modality_select()
            case FSMState.HELP_EXPLAIN:
                return self._do_help_explain()
            case FSMState.HELP_RECHECK_PRESENT:
                return self._do_help_recheck_present()
            case FSMState.HELP_RECHECK_AWAIT:
                return self._do_help_recheck_await(inp)
            case FSMState.HELP_RECHECK_SCORE:
                return self._do_help_recheck_score()
            case FSMState.HELP_RECHECK_BKT_UPDATE:
                return self._do_bkt_update(hinted=True)
            case FSMState.HELP_RETRY_DECISION:
                return self._do_help_retry_decision()
            case FSMState.LINK_BACK:
                return self._do_link_back()
            case FSMState.PROBE_PRESENT:
                return self._do_probe_present()
            case FSMState.PROBE_AWAIT_ANSWER:
                return self._do_probe_await_answer(inp)
            case FSMState.PROBE_SCORE:
                return self._do_probe_score()
            case FSMState.PROBE_CLASSIFY:
                return self._do_probe_classify()
            case FSMState.SESSION_END_COMPLETE | FSMState.SESSION_END_BY_LEARNER | FSMState.SESSION_END_BY_PARENT:
                return ("", False)
            case _:
                logger.error("unknown FSM state: %s", state)
                return ("", False)

    # ── State handlers ────────────────────────────────────────────────────────

    def _do_session_start(self) -> tuple[str, bool]:
        ctx = self._ctx
        # Load persisted mastery from db_store; fall back to P_L0 priors.
        for node_id in self._curriculum:
            try:
                row = self._store.get_skill_state(self._learner_id, node_id)
                if row:
                    ctx.mastery[node_id] = row["p_mastery"]
                    ctx.mastery_updated_at[node_id] = (
                        row["updated_at"] if "updated_at" in row.keys() else None
                    )
                else:
                    ctx.mastery[node_id] = P_L0
                    ctx.mastery_updated_at[node_id] = None
            except Exception:
                ctx.mastery[node_id] = P_L0
                ctx.mastery_updated_at[node_id] = None
        ctx.state = FSMState.NODE_SELECT
        return ("", True)

    def _do_node_select(self) -> tuple[str, bool]:
        ctx = self._ctx
        graph = {nid: n.get("prerequisites", []) for nid, n in self._curriculum.items()}
        fringe = outer_fringe(graph, ctx.mastery)
        if not fringe:
            ctx.state = FSMState.SESSION_END_COMPLETE
            return ("Well done — you've mastered all the fractions concepts for today! Great work.", False)
        ctx.current_node_id = next(iter(sorted(fringe)))
        ctx.state = FSMState.PATTERN_SELECT
        return ("", True)

    def _do_pattern_select(self) -> tuple[str, bool]:
        ctx = self._ctx
        patterns = ["pattern_problem_first", "pattern_read_then_question", "pattern_state_and_challenge"]
        ctx.current_pattern = random.choice(patterns)
        ctx.state = FSMState.PRESENT
        return ("", True)

    def _do_present(self) -> tuple[str, bool]:
        ctx = self._ctx
        ctx.unreadable_streak = 0  # A9: fresh question, fresh streak
        node = self._curriculum[ctx.current_node_id]
        item = self._sample_item(ctx.current_node_id)
        if item is not None:
            # Checkable item: present the problem verbatim so it matches its ground truth.
            ctx.current_item = item
            ctx.current_question = item.problem
            ctx.state = FSMState.AWAIT_ANSWER
            hint = self._answer_format_hint(item.answer_type)
            return (f"{item.problem} {hint}".rstrip(), False)
        # Fallback: LLM-generated question (nodes without a bank / legacy callers).
        ctx.current_item = None
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["concept"], passage)
        pattern_text = self._render_template(ctx.current_pattern, node, passage)
        question = self._llm([
            {"role": "system", "content": system_text},
            {"role": "user", "content": pattern_text},
        ])
        ctx.current_question = question
        ctx.state = FSMState.AWAIT_ANSWER
        hint = self._answer_format_hint(node.get("answer_type", ""))
        return (f"{question} {hint}".rstrip(), False)

    # ── Item / answer-spec helpers ──────────────────────────────────────────────

    def _sample_item(self, node_id: str):
        """Draw a checkable item for *node_id*, or None when no bank covers it."""
        if self._item_bank is not None and self._item_bank.has(node_id):
            return self._item_bank.sample(node_id)
        return None

    def _answer_spec(self, node: dict) -> tuple[str, str, str]:
        """(answer_type, checker, ground_truth) — from the current item if set, else node."""
        item = self._ctx.current_item
        if item is not None:
            return item.answer_type, item.checker, item.answer
        return (
            node.get("answer_type", "free_text"),
            node.get("checker", "none"),
            node.get("expected_answer", ""),
        )

    def _do_await_answer(self, inp: str | None) -> tuple[str, bool]:
        ctx = self._ctx
        if inp is None:
            return ("", False)
        stripped = inp.strip()
        # Learner requests help (explicit, or A21: "I don't know" / a clarifying
        # question — a declared-confusion signal, not a wrong answer to score).
        if _is_help_request(stripped) or _is_dont_know_or_question(stripped):
            ctx.help_n = 1
            ctx.help_modalities_used = []
            ctx.help_by_node[ctx.current_node_id] = True
            ctx.state = FSMState.HELP_MODALITY_SELECT
            return ("", True)
        # Learner wants to stop
        if _is_stop(stripped):
            ctx.state = FSMState.SESSION_END_BY_LEARNER
            return ("OK, see you next time!", False)
        ctx.current_answer = stripped
        ctx.state = FSMState.SCORE
        return ("", True)

    def _do_score(self) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        answer_type, checker, ground_truth = self._answer_spec(node)
        outcome = check(
            answer_type=answer_type,
            checker=checker,
            llm_output=ctx.current_answer or "",
            ground_truth=ground_truth,
        )
        if outcome.result in (CheckResult.SAFE_REJECT, CheckResult.EXTRACT_FAIL):
            ctx.unreadable_streak += 1
            if ctx.unreadable_streak >= UNREADABLE_STREAK_CAP:
                # A9: 3 unreadable answers in a row on the SAME question has no exit
                # otherwise — a child who genuinely can't produce the expected shape
                # (keyboard trouble, misunderstanding "_/_") gets stuck nudging forever.
                # Route into the Help loop, unscored — nothing logged as scored (mirrors
                # the auto-help-on-wrong branch in _do_bkt_update; NOT child-initiated,
                # so help_by_node is deliberately NOT set here — A5).
                ctx.unreadable_streak = 0
                ctx.help_n = 1
                ctx.help_modalities_used = []
                ctx.state = FSMState.HELP_MODALITY_SELECT
                return ("", True)
            # Couldn't read a checkable answer (blank / gibberish / malformed). Don't
            # penalise or log — re-ask the SAME question with answer-type-aware guidance.
            # (A vague "couldn't read" + jumping to a NEW question confused testers; this
            # is neither correct nor wrong, so say what's needed and keep the question.)
            ctx.state = FSMState.AWAIT_ANSWER
            if answer_type == "mc4":
                nudge = "I didn't catch a letter there — please answer with A, B, C or D."
            else:
                nudge = "Hmm, I couldn't read a number there — give it another go."
            return (f"{nudge}\n\n{ctx.current_question}", False)
        ctx.last_scored_correct = (outcome.result is CheckResult.PASS)
        self._log_response(
            ctx.current_node_id, ctx.current_answer,
            scored=ctx.last_scored_correct, hinted=False, outcome=outcome,
        )
        ctx.state = FSMState.BKT_UPDATE
        # Deterministic correctness feedback — the child must be told right/wrong.
        # On a wrong answer we do NOT reveal the answer here: BKT_UPDATE routes a
        # wrong unaided answer into the Help loop to work through it (note 4b).
        return (self._answer_feedback(ctx.last_scored_correct), True)

    def _make_safe_llm(self, llm_call):
        """Wrap the injected LLM so a backend failure degrades to '' instead of
        crashing the turn (which 500s the web page). Callers handle empty output
        (item bank covers questions; Help has a deterministic fallback hint).

        Two safety stages run on every LLM output before it can reach the child:
        credential-leak redaction, then the output-side content/scope gate (A13).
        Both live here — the single chokepoint every LLM response passes through.
        """
        def _safe(messages):
            try:
                out = llm_call(messages)
                out = out if isinstance(out, str) else ""
            except Exception:
                logger.warning("llm_call failed; degrading to empty output", exc_info=True)
                return ""
            # Credential-leak guard: scrub any secret-shaped string from model output
            # before it can reach the child or the transcript/logs (defence-in-depth).
            redacted = redact_credentials(out)
            if redacted != out:
                logger.warning("credential guard: redacted secret-shaped text from LLM output")

            # Output-side safety gate (A13, SAFETY §2.1/§2.2): discard + log + redirect
            # on a hard content block or off-scope drift. Never lets flagged text through.
            screened, incident = screen_output(redacted)
            if incident is not None:
                logger.warning(
                    "output guard: blocked class=%s span=%s",
                    incident.block_class.value, incident.matched_span,
                )
                try:
                    self._store.write_escalation(
                        self._learner_id,
                        f"output_blocked:{incident.block_class.value}",
                        incident.matched_span,
                        severity=SEVERITY_BY_CLASS[incident.block_class],
                        session_id=self._session_id,
                        turn_index=self._ctx.turn_index,
                        session_outcome="output_blocked",
                    )
                except Exception:
                    logger.warning("output guard: failed to persist incident row", exc_info=True)
                return NEUTRAL_REDIRECT
            return screened
        return _safe

    def _fallback_hint(self, node_id: str) -> str:
        """Deterministic hint used when the LLM is unavailable/empty — Help must
        never come back with nothing.

        Prefers the grounding passage (real explanatory text from the ZIM) over a
        bare worked example, which is just a problem + its answer (not an
        explanation). This is a DEGRADED path — a live model gives the real
        modality-based explanation; if you see this, the backend isn't serving
        (run scripts/check_backend.py).
        """
        node = self._curriculum.get(node_id, {})
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        if passage and passage.strip():
            snippet = passage.strip()[:400]
            return (
                "Let's look at how this works:\n"
                f"{snippet}\n"
                "Now try your question using that idea."
            )
        example = self._worked_example_for(node_id)
        if example:
            return (
                "Let's take it one step at a time. Here's a similar question and its "
                f"answer to compare with:\n{example}\n"
                "Look at how the answer comes from the numbers, then try yours the same way."
            )
        return (
            "Let's take it one step at a time — read the question again and try just "
            "the first part. You can do this!"
        )

    @staticmethod
    def _answer_format_hint(answer_type: str) -> str:
        """A small, kid-friendly cue for the expected answer SHAPE, from the KNOWN
        answer type (deterministic — not LLM-guessed; it must match the verifier)."""
        return {
            "fraction": "(answer like _/_)",
            "mc4": "(answer with a letter: A, B, C or D)",
            "int": "(answer with a number)",
            "decimal": "(answer with a number)",
        }.get(answer_type, "")

    @staticmethod
    def _strip_trailing_questions(text: str) -> str:
        """Drop trailing question lines a model appends to a Help explanation.

        The FSM owns the single practice question; a tacked-on "… = ?" (often with a
        trailing emoji, so it doesn't even end in '?') makes it unclear which to
        answer. Remove trailing blank/question-bearing lines, keeping the prose +
        completed worked example.
        """
        lines = text.rstrip().split("\n")
        while lines and (not lines[-1].strip() or "?" in lines[-1]):
            lines.pop()
        return "\n".join(lines).rstrip()

    @staticmethod
    def _answer_feedback(correct: bool) -> str:
        """Short, warm, deterministic right/wrong feedback for a scored answer.

        On wrong we don't reveal the answer — the Help loop (entered from
        BKT_UPDATE) works through it instead.
        """
        if correct:
            return random.choice(PRAISE_VARIANTS)
        return random.choice(WRONG_VARIANTS)

    def _do_bkt_update(self, hinted: bool) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        correct = ctx.help_scored_correct if hinted else ctx.last_scored_correct
        p_prior = ctx.mastery.get(ctx.current_node_id, P_L0)
        bkt_params = params_for(
            node.get("answer_type", "numeric"),
            node.get("bkt_priors"),
        )
        p_new = bkt_update(p_prior, correct=correct or False, hinted=hinted, params=bkt_params)
        ctx.mastery[ctx.current_node_id] = p_new
        try:
            self._store.update_skill_state(
                self._learner_id, ctx.current_node_id, p_new
            )
        except Exception:
            logger.warning("bkt_update: db persist failed", exc_info=True)
        if hinted:
            ctx.state = FSMState.HELP_RETRY_DECISION
        elif not correct:
            # Auto-help on a WRONG unaided answer: scaffold (explain + re-check)
            # instead of revealing the answer and advancing. Start a fresh Help
            # cycle (HELP_MODALITY_SELECT self-limits via the retry cap / modality
            # exhaustion -> LINK_BACK). Testing note 4b.
            ctx.help_n = 1
            ctx.help_modalities_used = []
            ctx.state = FSMState.HELP_MODALITY_SELECT
        else:
            ctx.state = FSMState.BRANCH_DECISION
        return ("", True)

    def _do_branch_decision(self) -> tuple[str, bool]:
        ctx = self._ctx
        ctx.items_since_probe += 1
        mastery = ctx.mastery.get(ctx.current_node_id, 0.0)
        probe_due = (ctx.items_since_probe >= PROBE_EVERY_N) or (mastery >= DEFAULT_MASTERY_THRESHOLD)
        if probe_due:
            ctx.items_since_probe = 0
            ctx.probe_variant = 0
            ctx.probe_first_correct = None
            ctx.probe_response_log_id = None
            ctx.probe_retry_response_log_id = None
            ctx.state = FSMState.PROBE_PRESENT
        else:
            ctx.state = FSMState.NODE_SELECT
        return ("", True)

    # ── Help loop ─────────────────────────────────────────────────────────────

    def _do_help_modality_select(self) -> tuple[str, bool]:
        ctx = self._ctx
        available = [m for m in HELP_MODALITIES if m not in ctx.help_modalities_used]
        if not available:
            ctx.state = FSMState.LINK_BACK
            return ("", True)
        modality = random.choice(available)
        ctx.help_modalities_used.append(modality)
        ctx.current_pattern = f"help_{modality}"
        ctx.state = FSMState.HELP_EXPLAIN
        return ("", True)

    _MAX_EXPLAIN_ATTEMPTS = 2  # A14: bounded regeneration on a verified-wrong claim

    def _do_help_explain(self) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["concept"], passage)
        help_text = self._render_template(
            ctx.current_pattern, node, passage,
            worked_example=self._worked_example_for(ctx.current_node_id),
            question=ctx.current_question or "",
        )
        messages = [
            {"role": "system", "content": system_text},
            {"role": "user", "content": help_text},
        ]

        explanation = ""
        for attempt in range(self._MAX_EXPLAIN_ATTEMPTS):
            candidate = self._llm(messages)
            # Deterministic guard: small models tack a question onto the explanation
            # (e.g. "10 ÷ 5 = ? ⭐"), which collides with the FSM's single practice
            # question. Strip trailing question lines so only ONE question is live.
            candidate = self._strip_trailing_questions(candidate or "")
            if not (candidate and candidate.strip()):
                break  # empty/unavailable — no point retrying, go to fallback
            # A14 / SAFETY §6.2 Level 2: verify arithmetic claims in the explanation
            # before it can reach the child — discard + regenerate on a verified FAIL.
            # SAFE_REJECT/EXTRACT_FAIL (unparseable) is not a failure — prose passes.
            if has_verified_failure(candidate):
                logger.warning(
                    "help explanation: discarded a verified-wrong arithmetic claim (attempt %d)",
                    attempt + 1,
                )
                continue
            explanation = candidate
            break

        if not (explanation and explanation.strip()):
            # LLM unavailable/empty, or every attempt had a verified-wrong claim —
            # never leave the child with no hint, and never with a wrong one.
            explanation = self._fallback_hint(ctx.current_node_id)
        if ctx.current_question:
            # Show the question being explained first, labelled, for context.
            explanation = f"Q) {ctx.current_question}\n\n{explanation}"
        ctx.state = FSMState.HELP_RECHECK_PRESENT
        return (explanation, True)

    def _do_help_recheck_present(self) -> tuple[str, bool]:
        ctx = self._ctx
        # ONE question at a time: re-try the SAME question the child is on (it's
        # already shown as "Q) …" above), rather than posing a new, different one.
        # Show the expected answer SHAPE so the child knows how to reply.
        answer_type, _, _ = self._answer_spec(self._curriculum[ctx.current_node_id])
        prompt = f"Now you try it! ✏️ {self._answer_format_hint(answer_type)}".rstrip()
        if ctx.current_item is not None or ctx.current_question:
            ctx.state = FSMState.HELP_RECHECK_AWAIT
            return (prompt, False)
        ctx.current_item = None
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["concept"], passage)
        transfer_text = self._render_template(
            "transfer_question_gen", node, passage,
            worked_example=self._worked_example_for(ctx.current_node_id),
        )
        recheck_q = self._llm([
            {"role": "system", "content": system_text},
            {"role": "user", "content": transfer_text},
        ])
        ctx.current_question = recheck_q
        ctx.state = FSMState.HELP_RECHECK_AWAIT
        return (recheck_q, False)

    def _do_help_recheck_await(self, inp: str | None) -> tuple[str, bool]:
        ctx = self._ctx
        if inp is None:
            return ("", False)
        stripped = inp.strip()
        if _is_stop(stripped):
            ctx.state = FSMState.SESSION_END_BY_LEARNER
            return ("OK, see you next time!", False)
        # A help request at the re-check must NOT be scored as an answer — give
        # another Help round instead (HELP_MODALITY_SELECT self-limits once all
        # modalities are exhausted -> LINK_BACK). A21: "I don't know" / a
        # clarifying question are treated the same way.
        if _is_help_request(stripped) or _is_dont_know_or_question(stripped):
            ctx.help_by_node[ctx.current_node_id] = True
            ctx.state = FSMState.HELP_MODALITY_SELECT
            return ("", True)
        if not stripped:
            # Skip attempt rejected — keep the question on screen (web shows last msg).
            return (f"Please give it a try — even a guess is OK!\n\n{ctx.current_question}", False)
        ctx.help_answer = stripped
        ctx.state = FSMState.HELP_RECHECK_SCORE
        return ("", True)

    def _do_help_recheck_score(self) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        answer_type, checker, ground_truth = self._answer_spec(node)
        outcome = check(
            answer_type=answer_type,
            checker=checker,
            llm_output=ctx.help_answer or "",
            ground_truth=ground_truth,
        )
        ctx.help_scored_correct = (outcome.result is CheckResult.PASS)
        rid = self._log_response(
            ctx.current_node_id, ctx.help_answer,
            scored=ctx.help_scored_correct, hinted=True, outcome=outcome,
        )
        if rid is not None and ctx.help_modalities_used:
            # Link the Help round's modality to the response it produced.
            self._safe_store(
                "write_help_event", self._session_id, ctx.current_node_id,
                ctx.help_modalities_used[-1], rid,
            )
        ctx.state = FSMState.HELP_RECHECK_BKT_UPDATE
        return ("", True)

    def _do_help_retry_decision(self) -> tuple[str, bool]:
        ctx = self._ctx
        if ctx.help_scored_correct:
            ctx.state = FSMState.BRANCH_DECISION
            return ("Great job! Let's keep going.", True)
        if ctx.help_n >= HELP_RETRY_CAP:
            ctx.state = FSMState.LINK_BACK
            return ("", True)
        ctx.help_n += 1
        ctx.state = FSMState.HELP_MODALITY_SELECT
        return ("", True)

    def _do_link_back(self) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        snippet = passage[:300].strip() if passage else ""
        if snippet:
            text = (
                f"This is a tricky one. Here's something to look at with a grown-up:\n\n{snippet}\n\n"
                "Let's move on for now and come back to this one."
            )
        else:
            text = (
                "This one is tricky — let's move on and come back to it later. "
                "You might want to ask your teacher about it too."
            )
        ctx.state = FSMState.BRANCH_DECISION
        return (text, True)

    # ── Probe loop ────────────────────────────────────────────────────────────

    def _do_probe_present(self) -> tuple[str, bool]:
        ctx = self._ctx
        item = self._sample_item(ctx.current_node_id)
        if item is not None:
            ctx.current_item = item
            ctx.current_question = item.problem
            ctx.state = FSMState.PROBE_AWAIT_ANSWER
            hint = self._answer_format_hint(item.answer_type)
            return (f"{item.problem} {hint}".rstrip(), False)
        ctx.current_item = None
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["concept"], passage)
        transfer_text = self._render_template(
            "transfer_question_gen", node, passage,
            worked_example=self._worked_example_for(ctx.current_node_id),
        )
        probe_q = self._llm([
            {"role": "system", "content": system_text},
            {"role": "user", "content": transfer_text},
        ])
        ctx.current_question = probe_q
        ctx.state = FSMState.PROBE_AWAIT_ANSWER
        hint = self._answer_format_hint(node.get("answer_type", ""))
        return (f"{probe_q} {hint}".rstrip(), False)

    def _do_probe_await_answer(self, inp: str | None) -> tuple[str, bool]:
        ctx = self._ctx
        if inp is None:
            return ("", False)
        stripped = inp.strip()
        if _is_stop(stripped):
            ctx.state = FSMState.SESSION_END_BY_LEARNER
            return ("OK, see you next time!", False)
        # Child wants help on the probe — GIVE it (enter the Help loop) rather than
        # dead-ending with a re-prompt. The probe is abandoned, but a child needing
        # help is itself useful signal, and help must never be refused. A21: "I
        # don't know" / a clarifying question route the same way.
        if _is_help_request(stripped) or _is_dont_know_or_question(stripped):
            ctx.help_n = 1
            ctx.help_modalities_used = []
            ctx.help_by_node[ctx.current_node_id] = True
            ctx.state = FSMState.HELP_MODALITY_SELECT
            return ("", True)
        if not stripped:
            # Keep the question on screen (the web view shows the last message).
            return (f"Give it a go — what do you think?\n\n{ctx.current_question}", False)
        ctx.probe_answer = stripped
        ctx.state = FSMState.PROBE_SCORE
        return ("", True)

    def _do_probe_score(self) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        answer_type, checker, ground_truth = self._answer_spec(node)
        outcome = check(
            answer_type=answer_type,
            checker=checker,
            llm_output=ctx.probe_answer or "",
            ground_truth=ground_truth,
        )
        ctx.probe_scored_correct = (outcome.result is CheckResult.PASS)
        rid = self._log_response(
            ctx.current_node_id, ctx.probe_answer,
            scored=ctx.probe_scored_correct, hinted=False, outcome=outcome,
        )
        if ctx.probe_variant == 0:
            ctx.probe_first_correct = ctx.probe_scored_correct
            ctx.probe_response_log_id = rid
        else:
            ctx.probe_retry_response_log_id = rid
        ctx.state = FSMState.PROBE_CLASSIFY
        return ("", True)

    def _do_probe_classify(self) -> tuple[str, bool]:
        ctx = self._ctx
        mastery = ctx.mastery.get(ctx.current_node_id, 0.0)
        stale = _is_stale_mastery(ctx.mastery_updated_at.get(ctx.current_node_id))
        probe_class = classify_probe(
            first_correct=ctx.probe_first_correct or False,
            retry_correct=ctx.probe_scored_correct if ctx.probe_variant > 0 else None,
            mastery=mastery,
            # A5: child-initiated help on THIS node only — not stale from a
            # previous node, not polluted by the system's own auto-help.
            help_pressed=ctx.help_by_node.get(ctx.current_node_id, False),
            mastery_is_stale=stale,
        )
        if probe_class is ProbeClass.CLEAN_PASS:
            # Mastery confirmed -> ADVANCE (NODE_SELECT drops the mastered node from
            # the fringe). Must NOT return to BRANCH_DECISION: with mastery >= the
            # threshold, probe_due would re-fire forever (the endless-silent-probe bug).
            self._log_probe_event(ctx.current_node_id, probe_class)
            ctx.state = FSMState.NODE_SELECT
            return (random.choice(PRAISE_VARIANTS), True)
        if probe_class is ProbeClass.SLIP_SUSPECT and ctx.probe_variant == 0:
            # One retry allowed before classifying (event written after the retry)
            ctx.probe_variant = 1
            ctx.state = FSMState.PROBE_PRESENT
            return ("", True)
        # false_confidence / forgetting_suspect / slip after retry: the probe revealed
        # mastery was OVERESTIMATED. Demote below threshold so the node returns to
        # NORMAL practice (with feedback) instead of being re-probed endlessly, then
        # advance through NODE_SELECT.
        self._log_probe_event(ctx.current_node_id, probe_class)
        demoted = min(ctx.mastery.get(ctx.current_node_id, P_L0), PROBE_DEMOTE_MASTERY)
        ctx.mastery[ctx.current_node_id] = demoted
        try:
            self._store.update_skill_state(self._learner_id, ctx.current_node_id, demoted)
        except Exception:
            logger.warning("probe demote: db persist failed", exc_info=True)
        ctx.state = FSMState.NODE_SELECT
        return ("Let's practise that one a bit more.", True)

    # ── Parent ack ────────────────────────────────────────────────────────────

    def _handle_parent_ack(self, inp: str) -> TurnResult:
        ctx = self._ctx
        if inp.strip().lower() in ("end", "stop", "finish"):
            ctx.state = FSMState.SESSION_END_BY_PARENT
            return TurnResult(state=ctx.state.value, text="Session ended. Thank you.", done=True, escalated=False)
        # resume
        ctx.state = FSMState.NODE_SELECT
        return TurnResult(state=ctx.state.value, text="Welcome back. Let's continue.", done=False, escalated=False)

    # ── Template helpers ──────────────────────────────────────────────────────

    def _load_template(self, name: str) -> str:
        if name not in self._templates:
            path = self._prompt_dir / f"{name}.md"
            raw = path.read_text(encoding="utf-8")
            # Strip YAML front matter (--- ... ---\n)
            if raw.startswith("---"):
                end = raw.index("---", 3)
                raw = raw[end + 3:].lstrip("\n")
            self._templates[name] = raw
        return self._templates[name]

    def _render_template(
        self, name: str, node: dict, passage: str,
        worked_example: str = "", question: str = "",
    ) -> str:
        tmpl = self._load_template(name)
        return (
            tmpl
            .replace("{{concept}}", node.get("concept", "fractions"))
            .replace("{{answer_type}}", node.get("answer_type", "fraction"))
            .replace("{{grounding_passage}}", passage)
            .replace("{{worked_example}}", worked_example or "a simple example with small numbers")
            .replace("{{question}}", question or "the question they're working on")
        )

    def _worked_example_for(self, node_id: str) -> str:
        """A solved example string for the worked-example slot in Help/transfer prompts.

        Prefers a node-authored `worked_example`; else a solved item from the bank (excluding
        the live question so its answer isn't revealed); else "".
        """
        node = self._curriculum.get(node_id, {})
        if node.get("worked_example"):
            return str(node["worked_example"])
        if self._item_bank is not None:
            cur_id = getattr(self._ctx.current_item, "id", None)
            ex = self._item_bank.example(node_id, exclude_id=cur_id)
            if ex is not None:
                return f"{ex.problem} (Answer: {ex.answer})"
        return ""

    def _render_system_prompt(self, concept: str, passage: str) -> str:
        tmpl = self._load_template("system_prompt")
        return (
            tmpl
            .replace("{{concept}}", concept)
            .replace("{{grounding_passage}}", passage)
            .replace("{{subject}}", self._subject)
            .replace("{{scope_line}}", self._scope_line)
        )
