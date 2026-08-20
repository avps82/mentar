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
import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from mentar.engine.arithmetic_steps import (
    StepGrid,
    build_addition_steps,
    build_long_division_steps,
    build_multiplication_decimal_steps,
    build_multiplication_partial_products_steps,
    build_signed_addition_steps,
    build_signed_multiplication_steps,
    build_subtraction_steps,
    extract_addition_operands,
    extract_decimal_multiplication_operands,
    extract_division_operands,
    extract_multiplication_operands,
    extract_signed_addition_operands,
    extract_signed_multiplication_operands,
    extract_subtraction_operands,
)
from mentar.engine.bkt import P_L0, bkt_update, params_for
from mentar.engine.explain_check import has_verified_failure, realign_algebra_blocks
from mentar.engine.fringe import DEFAULT_MASTERY_THRESHOLD, is_mastered, select_next
from mentar.engine.probe_classify import ProbeClass, classify_probe
from mentar.engine.visual_scaffold import (
    first_diagram,
    first_diagram_is_reference_key,
    load_visual_scaffold,
)
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
# A scaffold diagram carrying any digit is a DIFFERENT example from the card it
# would be appended to -- see the comment at the append site in _do_help_present.
_DIAGRAM_HAS_NUMBER_RE = re.compile(r"[0-9]")

# The call-to-action that closes a Help turn. A module constant because the web
# view SPLITS the turn's message on it, to place the worked-example card between
# "Let's see how it's solved!" and this line rather than after both (maintainer,
# 2026-08-16). Anchoring on a shared constant, not on the last "\n\n", so the
# layout cannot silently drift if either line is reworded.
RECHECK_PROMPT = "Now you try it! ✏️"

STALE_MASTERY_DAYS = 14  # mastery older than this counts as "stale" for forgetting detection
# W5.6 continuous-assent: shown ONCE at the start so the child knows they can withdraw anytime.
# (A learner 'stop' = self-withdrawal; a parent 'end' via /parent/ack = parent-withdrawal —
# both recorded in session.ended_reason. See docs/design/W5.6_decision_prep.md.)
ASSENT_LINE = "Remember — you can stop anytime, just say 'stop'."
# A4 / SAFETY.md §5.5: child-friendly AI transparency, shown ONCE alongside the assent line.
TRANSPARENCY_LINE = "I'm Mentar, a computer learning helper — not a person."

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


_SENTENCE_END = ".!?…:"
# A final line that is ONLY a list marker -- "2.", "A)", "iv.", "-", "*", "•" --
# is the start of an item the token cap swallowed, not content.
_STUMP_LINE_RE = re.compile(
    r"^\s*(?:\d{1,3}[.)]|[A-Za-z][.)]|[ivxIVX]{1,4}[.)]|[-*•])\s*$"
    # ...and a bare "Answer:" / "Final Answer:" heading with nothing after the
    # colon (2026-08-19 report: the model announced an answer it never wrote,
    # leaving the heading dangling above "Now you try it").
    r"|^\s*(?:final\s+)?answer\s*[:\-]?\s*$",
    re.IGNORECASE,
)


def _trim_truncated_tail(text: str) -> str:
    """Drop the stump an output-token cap leaves behind.

    Two stump shapes, applied repeatedly until the tail is clean (the second
    report's "…🏊\n\n2." needs both: the sentence-cut exposes the bare "2.",
    which the line rule then removes):

      * a MID-CLAUSE cut -- the text ends in a word character or comma/hyphen
        ("Because a") -> cut back to the last completed sentence;
      * a LIST-MARKER-ONLY final line ("2.", "A)", "-") -- the marker ends in
        "." so the sentence rule alone cannot see it -> drop the line.

    Clean endings (./!/?/:/quote/bracket/emoji) are left alone, so ordinary
    prose and card-style lines never change. If no earlier sentence boundary
    exists, the text is returned unchanged -- a stump is still better than
    nothing at all.
    """
    t = text.rstrip()
    for _ in range(6):                                   # bounded; each pass shrinks t
        lines = t.split("\n")
        if len(lines) > 1 and _STUMP_LINE_RE.match(lines[-1]):
            t = "\n".join(lines[:-1]).rstrip()
            continue
        if t and (t[-1].isalnum() or t[-1] in ",-"):
            cut = max(t.rfind(ch) for ch in _SENTENCE_END)
            if cut > 0:
                t = t[: cut + 1]
                continue
        break
    return t if t else text


# LaTeX the local models emit despite plain-text prompts. Narrow, additive list.
_LATEX_SUBS = [
    ("$\\rightarrow$", "→"), ("\\rightarrow", "→"),
    ("$\\times$", "×"), ("\\times", "×"),
    ("$\\div$", "÷"), ("\\div", "÷"),
    ("$\\cdot$", "·"), ("\\cdot", "·"),
]


def _normalise_llm_math(text: str) -> str:
    """Replace the LaTeX tokens models emit ("force $\\rightarrow$ a VECTOR")
    with the plain characters a child can read. Substring replacement on a
    fixed list -- never a LaTeX parser."""
    for src, dst in _LATEX_SUBS:
        if src in text:
            text = text.replace(src, dst)
    return text


# An explicit reveal formula: "Final Answer: A", "the answer is C", "Answer - 42".
_REVEAL_MC_RE = re.compile(
    r"\b(?:final\s+answer|the\s+answer\s+is|answer)\s*(?:[:\-–—]|\bis\b)\s*\(?([A-Da-d])\b(?![\w'])",
    re.IGNORECASE,
)


def _scrub_answer_reveal(text: str, answer_type: str, truth: str) -> str:
    """Cut an LLM Help explanation at the line that announces the final answer.

    The Help loop's contract is scaffold-then-recheck: the child attempts the
    question again after the explanation, so the explanation must not hand over
    the live answer (the deterministic card DOES -- but only via the explicit
    "Show me the working" press, which then hides itself). Everything before
    the reveal line is kept; if nothing substantial remains, "" is returned so
    the caller's existing retry/fallback path takes over.

    mc4 scrubs ANY explicit "answer: <letter>" formula -- a wrong letter handed
    over confidently is as bad as the right one. Other types scrub only a
    formula naming the LIVE ground truth, because bare numbers appear
    legitimately throughout worked arithmetic.
    """
    if not text:
        return text
    lines = text.splitlines()
    cut = None
    if answer_type == "mc4":
        for i, line in enumerate(lines):
            if _REVEAL_MC_RE.search(line):
                cut = i
                break
    elif truth:
        needle = re.compile(
            r"\b(?:final\s+answer|the\s+answer\s+is|answer)\s*(?:[:\-–—]|\bis\b)\s*"
            + re.escape(truth) + r"(?![\w])",
            re.IGNORECASE,
        )
        for i, line in enumerate(lines):
            if needle.search(line):
                cut = i
                break
    if cut is None:
        return text
    kept = "\n".join(lines[:cut]).rstrip()
    return kept if len(kept) >= 40 else ""


# "Final Answer:" / "Answer:" as a heading (start of line) in HELP PROSE.
_EXAMPLE_ANSWER_HEADING_RE = re.compile(
    r"(?m)^[ \t]*(?:final\s+answer|answer)\s*[:：]", re.IGNORECASE
)


def _names_a_live_choice(text: str, item) -> bool:
    """True when *text* mentions the live mc4 item's CORRECT choice string.

    The correct choice only, deliberately (maintainer, 2026-08-20): naming a
    DISTRACTOR is legitimate teaching -- an explanation of connectives that may
    not say "between" while "between" sits among the options would collapse
    every English help into the canned fallback. Naming the CORRECT text
    ("methane is covalent" under "which is covalent?") is answering, whether
    the model saw the options or merely picked the canonical example.

    Word-boundary, case-insensitive; skipped when shorter than 3 characters or
    already present in the STEM (the stem is deliberately given to the model,
    so a word it contains cannot be treated as a leak).
    """
    if item is None or getattr(item, "answer_type", "") != "mc4":
        return False
    choices = getattr(item, "choices", None) or ()
    letter = str(getattr(item, "answer", "")).strip().upper()
    idx = "ABCD".find(letter)
    if idx < 0 or idx >= len(choices):
        return False
    c = str(choices[idx]).strip().lower()
    stem = (getattr(item, "stem", None) or "").lower()
    if len(c) < 3 or c in stem:
        return False
    return re.search(r"(?<![\w])" + re.escape(c) + r"(?![\w])", text.lower()) is not None


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
# R12.5: child asks to unpack the SAME explanation further ("Explain more" button /
# typed). Bounded per Help chain — see ELABORATE_CAP.
ELABORATE_WORDS = {"more", "explain more", "tell me more"}
ELABORATE_CAP = 2
UNREADABLE_STREAK_CAP = 3  # A9: consecutive SAFE_REJECT/EXTRACT_FAIL before routing to Help
PROBE_EVERY_N = 5  # W5.3 pilot default
# CONCERN tier (2026-08-18, maintainer-authorised): a single welfare-concern
# match logs + surfaces to the parent and the lesson continues; this many in
# ONE session escalate to a freeze -- distress that builds across turns with no
# single alarming line was a documented gap (packet Part 4, "multi-turn
# distress").
CONCERN_FREEZE_THRESHOLD = 2
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
    HELP_ELABORATE        = "HELP_ELABORATE"
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
    FSMState.ESCALATION_FREEZE,
}

# States where a pending QUESTION is live on screen (TurnResult.question carries
# it, structurally — the display layer must never have to string-split it back
# out of the prose; that approach broke on the Help flow's "Q) …" recap).
_QUESTION_AWAIT = {
    FSMState.AWAIT_ANSWER,
    FSMState.HELP_RECHECK_AWAIT,
    FSMState.PROBE_AWAIT_ANSWER,
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
    text: str            # full child-facing text (message + question) — CLI/transcript compat
    done: bool
    escalated: bool
    # Structured display fields (U-31 proper fix, maintainer-requested 2026-07-10):
    # the web view places each part in its own area instead of string-splitting text.
    message: str = ""            # transient prose: feedback, praise, explanation, nudges
    question: str | None = None  # the pending question display (incl. format hint), if awaiting one


@dataclass
class _SessionCtx:
    """Mutable FSM context — all transient state for one session."""
    state: FSMState = FSMState.SESSION_START
    mastery: dict = field(default_factory=dict)      # node_id -> float
    mastery_updated_at: dict = field(default_factory=dict)  # node_id -> ISO ts | None
    current_node_id: str | None = None
    current_pattern: str | None = None
    current_question: str | None = None           # rendered question text (verbatim, for logging/templates)
    question_display: str | None = None           # child-facing question incl. format hint (TurnResult.question)
    current_item: object | None = None            # current checkable Item (or None = LLM-gen)
    current_answer: str | None = None             # child's latest answer
    last_scored_correct: bool | None = None
    items_since_probe: int = 0
    concern_hits: int = 0                            # CONCERN-tier matches this session
    items_completed: int = 0       # R11: completed item cycles (drives interleave/review/cap)
    unreadable_streak: int = 0     # A9: consecutive SAFE_REJECT/EXTRACT_FAIL on this question
    # Help loop
    help_n: int = 0                                  # retry counter (1-indexed)
    help_modalities_used: list = field(default_factory=list)
    help_answer: str | None = None
    help_scored_correct: bool | None = None
    last_explanation: str = ""     # R12.4/12.5: last help explanation shown (variety + elaborate)
    elaborate_count: int = 0       # R12.5: elaborations used this Help chain (cap = ELABORATE_CAP)
    elaborate_steps_grid: StepGrid | None = None  # "show human working", set on HELP_ELABORATE
    # explain-mode (2026-08-12): the SAME "render directly on Explain-more, skip
    # the LLM entirely" treatment as elaborate_steps_grid, for a node whose live
    # item carries a computed method_steps card (Type 2/4) instead of a step
    # grid (Type 1) -- mutually exclusive with elaborate_steps_grid per node.
    elaborate_method_card: tuple | None = None
    # Jump-to-answer honesty (maintainer, 2026-08-19): once the working -- which
    # ENDS IN THE ANSWER -- has been shown for this question, the button must not
    # be offered again for it. A plain "card is showing" check is not enough: a
    # fresh Help round (wrong answer again) clears the card, which would
    # resurrect the button for an already-revealed question. Per-question flag,
    # reset when a new question is presented.
    working_shown: bool = False
    # ...and WHICH item it was shown for. Inside one help loop the recheck draws
    # a NEW item, so the re-show can legitimately display a card the child has
    # not seen before -- the lead-in must not say "again" then (maintainer nit,
    # 2026-08-19: right card, wrong sentence).
    working_shown_item_id: str | None = None
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
        rng_seed: int | None = None,
        max_items: int | None = None,
        resume_checkpoint: dict | None = None,
        scaffold_dir: Path | None = None,
        pinned_node: str | None = None,
    ) -> None:
        self._llm = self._make_safe_llm(llm_call)
        self._prompt_dir = Path(prompt_dir)
        # Optional: curriculum/visual_scaffolds/ root -- fills {{visual_scaffold}} in
        # help/pattern templates with a short, topic-routed hint instead of the whole
        # bundle (keeps a small local model's context tight). None -> slot renders "".
        self._scaffold_dir = Path(scaffold_dir) if scaffold_dir is not None else None
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
        # R11 micro-session cap: end warmly after this many completed items (None = uncapped).
        self._max_items = max_items
        # R-RES: a checkpoint from a session a server-process restart interrupted --
        # {"current_node_id", "frozen", "items_completed", "items_since_probe"} or None
        # for a genuinely fresh session. Consumed once, in _do_session_start.
        self._resume_checkpoint = resume_checkpoint
        # One tutoring session per controller instance. A session row is created lazily
        # on the first step() and closed at a terminal state (both best-effort). A
        # resumed session reuses its ORIGINAL id (passed in by the caller) so durable
        # logging keeps accumulating under the same row.
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
        # A19: a per-instance seeded RNG (not the global `random` module) so a session's
        # non-deterministic choices (pattern/modality/praise-variant selection) can be
        # replayed exactly given the same seed. Default: a fresh random seed, logged.
        self._rng_seed = rng_seed if rng_seed is not None else random.SystemRandom().randrange(2**32)
        self._rng = random.Random(self._rng_seed)
        logger.info("session %s: rng_seed=%d", self._session_id, self._rng_seed)
        # Jump-to-topic (docs/design/topic_jump_and_practice.md): hold node selection
        # on ONE curriculum concept -- the learner/parent picked it explicitly. The
        # rest of the loop (verify, help, probes, escalation) is untouched; only
        # select_next() is bypassed. Fail loud at the seam, not silently mid-session
        # (same posture as _raise_on_uncovered_nodes above).
        if pinned_node is not None and pinned_node not in curriculum:
            raise ValueError(
                f"pinned_node {pinned_node!r} is not a concept of this subject's curriculum"
            )
        self._pinned_node = pinned_node
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
            # W5.6 assent + A4/SAFETY §5.5 AI-transparency: prepend both, once, to
            # the very first child-facing turn (message prose, not the question).
            self._assent_shown = True
            message = "\n\n".join(
                part for part in (ASSENT_LINE, TRANSPARENCY_LINE, result.message) if part
            )
            result = TurnResult(
                state=result.state,
                text="\n\n".join(part for part in (message, result.question) if part),
                done=result.done, escalated=result.escalated,
                message=message, question=result.question,
            )
        if result.text:
            self._log_transcript("tutor", result.text)
        if result.done:
            self._maybe_end_session(self._ctx.state)
        self._write_checkpoint()
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
        if ctx.state is not FSMState.ESCALATION_FREEZE:
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
            message = "\n\n".join(t for t in (result.message or result.text, driven.message) if t)
            text = "\n\n".join(t for t in (message, driven.question) if t)
            result = TurnResult(
                state=ctx.state.value, text=text, done=driven.done, escalated=False,
                message=message, question=driven.question,
            )
        if result.text:
            self._log_transcript("tutor", result.text)
        if result.done:
            self._maybe_end_session(ctx.state)
        self._write_checkpoint()
        return result

    def _write_checkpoint(self) -> None:
        """R-RES: best-effort per-turn checkpoint so a server-process restart can
        resume onto the same topic instead of losing all session context. Mirrors
        the existing best-effort persistence posture (_log_transcript etc.) — a DB
        failure here must never block or corrupt a tutoring turn."""
        ctx = self._ctx
        checkpoint = {
            "current_node_id": ctx.current_node_id,
            "frozen": ctx.state is FSMState.ESCALATION_FREEZE,
            "items_completed": ctx.items_completed,
            "items_since_probe": ctx.items_since_probe,
            "turn_index": ctx.turn_index,
            # Additive (old checkpoints read back as un-pinned): without this a
            # server restart silently converts a pinned session into a guided one.
            "pinned_node": self._pinned_node,
            # Same additive rule: without this, a restart resets the CONCERN
            # accumulation and the threshold quietly never fires.
            "concern_hits": ctx.concern_hits,
        }
        self._safe_store(
            "update_session_checkpoint", self._session_id, json.dumps(checkpoint),
        )

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
            trigger = classify(learner_input)
            if trigger is not None:
                # CONCERN accumulation: the hit count includes THIS one, so the
                # threshold-th concern freezes on the turn it arrives.
                concern_freezes = False
                if trigger.severity is Severity.CONCERN:
                    ctx.concern_hits += 1
                    concern_freezes = ctx.concern_hits >= CONCERN_FREEZE_THRESHOLD
                # Log every trigger for the parent (SAFETY §3.x): full UNTRUNCATED
                # text + class + severity/session/turn (A3). Best-effort — a DB
                # failure must never block handling.
                if trigger.severity is Severity.LOW:
                    session_outcome = "logged_only"
                elif trigger.severity is Severity.CONCERN and not concern_freezes:
                    session_outcome = "logged_concern"
                else:
                    session_outcome = "frozen"
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
                    return self._compose_result("Let's keep going with our maths! 😊")

                if trigger.severity is Severity.CONCERN and not concern_freezes:
                    # CONCERN: logged + surfaced on /parent, and the lesson
                    # simply CONTINUES -- no early return, so the child's input
                    # flows into normal turn handling and they see exactly what
                    # they would have seen anyway. The child is never shown that
                    # anything was noticed; the note is for the parent.
                    logger.warning(
                        "welfare concern (logged, not frozen; %d this session): span=%s",
                        ctx.concern_hits, trigger.matched_span[:80],
                    )
                else:
                    # CRITICAL / HIGH -- or the CONCERN threshold: freeze + parent handoff.
                    ctx.state = FSMState.ESCALATION_FREEZE
                    logger.warning(
                        "escalation: span=%s class=%s", trigger.matched_span[:80], trigger.trigger_class
                    )
                    return TurnResult(
                        state=ctx.state.value,
                        text=HANDOFF_MESSAGE_PRIMARY,
                        done=False,
                        escalated=True,
                        message=HANDOFF_MESSAGE_PRIMARY,
                    )

        # Drive transient states until we hit an await or terminal state.
        output_text = ""
        for _ in range(40):  # guard against infinite loops in tests
            state = ctx.state
            if state in _TERMINAL:
                return self._compose_result(output_text)
            if state in _AWAIT and learner_input is None and state != FSMState.SESSION_START:
                # Already waiting; caller must supply input.
                return self._compose_result(output_text)

            text, advance = self._tick(state, learner_input)
            if text:
                # Accumulate across ticks: a single turn can emit several messages
                # (e.g. a Help explanation THEN the re-check prompt). Overwriting would
                # drop the explanation and show only the last message.
                output_text = f"{output_text}\n\n{text}" if output_text else text
            learner_input = None  # consumed; subsequent ticks are transient
            if not advance:
                break  # reached a natural await/terminal

        return self._compose_result(output_text)

    def _compose_result(self, message: str) -> TurnResult:
        """Build a TurnResult from the accumulated MESSAGE prose + the pending
        question (structural — TurnResult.question, never embedded-and-re-split).
        `text` stays the full joined string for the CLI, the durable transcript,
        and backward compatibility."""
        ctx = self._ctx
        question = ctx.question_display if ctx.state in _QUESTION_AWAIT else None
        text = "\n\n".join(part for part in (message, question) if part)
        return TurnResult(
            state=ctx.state.value,
            text=text,
            done=ctx.state in _TERMINAL,
            escalated=ctx.state is FSMState.ESCALATION_FREEZE,
            message=message,
            question=question,
        )

    @property
    def state(self) -> str:
        return self._ctx.state.value

    @property
    def is_terminal(self) -> bool:
        """True once the session has ended (completed / learner-stopped /
        parent-ended) — a web GET landing here (browser back, a stale bookmark,
        a refresh) must redirect to the done screen rather than re-render the
        live-turn UI, which has no question to show and no input to accept."""
        return self._ctx.state in _TERMINAL

    @property
    def current_node_id(self) -> str | None:
        """The curriculum node the learner is currently on, or None before the
        first PRESENT (read-only display accessor -- e.g. a per-skill mastery
        cue in the web UI)."""
        return self._ctx.current_node_id

    @property
    def current_question(self) -> str | None:
        """The pending question text (verbatim, as used for logging/templates),
        or None before the first PRESENT."""
        return self._ctx.current_question

    @property
    def question_display(self) -> str | None:
        """The child-facing question display (question + answer-format hint) when a
        question is live on screen, else None (read-only — the web view's stable
        question block renders exactly this, matching TurnResult.question)."""
        if self._ctx.state in _QUESTION_AWAIT:
            return self._ctx.question_display
        return None

    @property
    def current_answer_type(self) -> str | None:
        """The live question's expected answer type (int/fraction/mc4/free_text),
        or None when no question is awaiting — drives the web input widget
        (radio buttons for mc4, numerator/denominator boxes for fraction)."""
        if self._ctx.state not in _QUESTION_AWAIT or self._ctx.current_node_id is None:
            return None
        answer_type, _, _ = self._answer_spec(self._curriculum[self._ctx.current_node_id])
        return answer_type

    @property
    def current_choices(self) -> list[str] | None:
        """Structured choice texts for the live mc4 question (parallel to A/B/C/D),
        or None for non-choice questions / items without structured choices."""
        if self._ctx.state not in _QUESTION_AWAIT:
            return None
        item = self._ctx.current_item
        choices = getattr(item, "choices", None)
        return list(choices) if choices else None

    @property
    def current_question_stem(self) -> str | None:
        """R2.1: the live mc4 question WITHOUT inline "A) ..." options, or None
        when no question is awaiting / the item has no structured stem. The web
        view shows this + current_choices as radios instead of the full inline
        text (which still exists on the item for CLI/transcript surfaces)."""
        if self._ctx.state not in _QUESTION_AWAIT:
            return None
        item = self._ctx.current_item
        return getattr(item, "stem", None)

    @property
    def session_progress(self) -> tuple[int, int] | None:
        """R12-fix2: (current question number, session length) for the web
        session-progress indicator — (items_completed + 1, max_items), or None
        when the session is uncapped (no stable denominator to show)."""
        if self._max_items is None:
            return None
        return (min(self._ctx.items_completed + 1, self._max_items), self._max_items)

    @property
    def can_elaborate(self) -> bool:
        """R12.5: True when an explanation is live and the child may ask to
        unpack it further — drives the web view's "💡 Explain more" button."""
        return (
            self._ctx.state is FSMState.HELP_RECHECK_AWAIT
            and bool(self._ctx.last_explanation)
            and self._ctx.elaborate_count < ELABORATE_CAP
            # The working ends in the ANSWER: once shown for this question, the
            # offer disappears until the next question (maintainer, 2026-08-19).
            and not self._ctx.working_shown
        )

    @property
    def elaborate_steps_grid(self) -> StepGrid | None:
        """"Show human working": the deterministic step grid for the current
        Explain-more press, or None when the live node isn't step-eligible
        (falls back to the LLM-prose explanation) or no elaborate press has
        happened yet this question."""
        return self._ctx.elaborate_steps_grid

    @property
    def elaborate_method_card(self) -> tuple | None:
        """Explain-mode (2026-08-12): the computed method card for the current
        Explain-more press, when the live item carries one (Type 2/4) and the
        node isn't step-grid-eligible. None otherwise -- same "no card yet /
        not this kind of node" collapse as elaborate_steps_grid."""
        return self._ctx.elaborate_method_card

    @property
    def session_id(self) -> str:
        """The id of this controller's tutoring session (for durable-log reads)."""
        return self._session_id

    @property
    def rng_seed(self) -> int:
        """A19: the seed this session's internal RNG was constructed with — pass
        this back into a new SessionController's rng_seed= to replay the same
        non-deterministic choices (pattern/modality/praise-variant selection)."""
        return self._rng_seed

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
            self._safe_store("create_session", self._session_id, self._rng_seed)

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
            case FSMState.HELP_ELABORATE:
                return self._do_help_explain(elaborate=True)
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
        # R-RES: where SESSION_START lands, given an optional resume checkpoint from a
        # session a server-process restart interrupted (self._resume_checkpoint). Kept
        # INLINE (not a helper) so T3.7's AST-based conformance test can see the literal
        # ctx.state = FSMState.X assignments -- it only walks _do_ handler bodies.
        #   - no checkpoint (the common case)                    -> NODE_SELECT
        #   - checkpoint says the session was frozen              -> ESCALATION_FREEZE,
        #     UNCONDITIONALLY (SAFETY §3.x: only the parent control plane may ever lift
        #     a freeze -- a restart must never silently resume one unfrozen).
        #   - checkpoint names a node still valid + unmastered in THIS curriculum
        #                                                          -> PATTERN_SELECT,
        #     seeded onto that SAME node (skips NODE_SELECT's own selection so R11's
        #     interleave policy -- which prefers switching AWAY from `current` -- can't
        #     override "resume onto the same topic"); a fresh item/question is
        #     presented, not the literal one that was on screen.
        #   - checkpoint names a node that's gone stale (template changed, already
        #     mastered since, or missing entirely)                 -> NODE_SELECT
        #     (safe degrade, not an error -- the checkpoint just wasn't trustworthy).
        cp = self._resume_checkpoint
        node_id = cp.get("current_node_id") if cp else None
        # Jump-to-topic: restore the pin across a server restart. Constructor wins
        # if it set one; a checkpointed pin naming a node this curriculum no longer
        # has is dropped (same safe-degrade as a stale current_node_id below).
        if self._pinned_node is None and cp and cp.get("pinned_node") in self._curriculum:
            self._pinned_node = cp["pinned_node"]
        if cp:
            # R-RES: restore turn_index so _log_transcript doesn't collide with
            # transcript rows already written by the previous server process.
            # If the checkpoint pre-dates turn_index saving, query the DB for
            # the actual max already written (handles old checkpoints gracefully).
            saved = cp.get("turn_index")
            if saved is not None:
                ctx.turn_index = int(saved)
            else:
                ctx.turn_index = self._store.max_turn_index_for_session(self._session_id) + 1
        if cp and cp.get("frozen"):
            ctx.state = FSMState.ESCALATION_FREEZE
        elif cp and node_id in self._curriculum and not is_mastered(ctx.mastery.get(node_id, 0.0)):
            ctx.current_node_id = node_id
            ctx.items_completed = int(cp.get("items_completed") or 0)
            ctx.items_since_probe = int(cp.get("items_since_probe") or 0)
            ctx.concern_hits = int(cp.get("concern_hits") or 0)
            ctx.state = FSMState.PATTERN_SELECT
        else:
            ctx.state = FSMState.NODE_SELECT
        return ("", True)

    def _do_node_select(self) -> tuple[str, bool]:
        ctx = self._ctx
        # Jump-to-topic: a pinned session always serves its one chosen concept --
        # repetition is the point, so an already-mastered pin is served again, not
        # skipped. Every re-entry to NODE_SELECT (post-probe, post-help) passes
        # through here, so this one branch covers all paths; the session still ends
        # via the max_items cap in _do_branch_decision (or the child's stop).
        if self._pinned_node is not None:
            ctx.current_node_id = self._pinned_node
            ctx.state = FSMState.PATTERN_SELECT
            return ("", True)
        graph = {nid: n.get("prerequisites", []) for nid, n in self._curriculum.items()}
        # R11 micro-learning: interleave among ready concepts + inject spaced review of
        # mastered-but-stale nodes (makes the FORGETTING_SUSPECT probe path reachable).
        stale_mastered = {
            nid for nid, p in ctx.mastery.items()
            if is_mastered(p) and _is_stale_mastery(ctx.mastery_updated_at.get(nid))
        }
        next_node = select_next(
            graph, ctx.mastery,
            stale_mastered=stale_mastered,
            current=ctx.current_node_id,
            items_completed=ctx.items_completed,
            rng=self._rng,
        )
        if next_node is None:
            ctx.state = FSMState.SESSION_END_COMPLETE
            # E2.1: subject-aware (was hardcoded "fractions" — same bug class A7 fixed
            # for the system prompt; a science session used to end on "fractions").
            return (f"Well done — you've mastered all the {self._subject} concepts for today! Great work.", False)
        ctx.current_node_id = next_node
        ctx.state = FSMState.PATTERN_SELECT
        return ("", True)

    def _do_pattern_select(self) -> tuple[str, bool]:
        ctx = self._ctx
        patterns = ["pattern_problem_first", "pattern_read_then_question", "pattern_state_and_challenge"]
        ctx.current_pattern = self._rng.choice(patterns)
        ctx.state = FSMState.PRESENT
        return ("", True)

    def _do_present(self) -> tuple[str, bool]:
        ctx = self._ctx
        ctx.unreadable_streak = 0  # A9: fresh question, fresh streak
        ctx.last_explanation = ""  # R12.4: fresh question — variety/elaborate context resets
        ctx.elaborate_count = 0
        ctx.elaborate_steps_grid = None  # "show human working": stale grid must not linger
        ctx.elaborate_method_card = None  # explain-mode: stale card must not linger either
        ctx.working_shown = False         # new question -- the working may be offered again
        ctx.working_shown_item_id = None
        node = self._curriculum[ctx.current_node_id]
        item = self._sample_item(ctx.current_node_id)
        if item is not None:
            # Checkable item: present the problem verbatim so it matches its ground truth.
            ctx.current_item = item
            ctx.current_question = item.problem
            ctx.state = FSMState.AWAIT_ANSWER
            hint = item.format_hint or self._answer_format_hint(item.answer_type)
            ctx.question_display = f"{item.problem} {hint}".rstrip()
            return ("", False)
        # Fallback: LLM-generated question (nodes without a bank / legacy callers).
        ctx.current_item = None
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["label"], passage)
        pattern_text = self._render_template(ctx.current_pattern, node, passage)
        question = self._llm([
            {"role": "system", "content": system_text},
            {"role": "user", "content": pattern_text},
        ])
        ctx.current_question = question
        ctx.state = FSMState.AWAIT_ANSWER
        hint = self._answer_format_hint(node.get("answer_type", ""))
        ctx.question_display = f"{question} {hint}".rstrip()
        return ("", False)

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

    def _handle_unreadable(self, answer_type: str) -> tuple[str, bool]:
        """A9/E2.4 shared: one unreadable (SAFE_REJECT/EXTRACT_FAIL) answer on the
        live question. Increments the per-question streak; at UNREADABLE_STREAK_CAP
        primes a fresh Help chain (NOT child-initiated — help_by_node deliberately
        not set, A5). Returns (nudge_text, cap_hit); the CALLER assigns ctx.state
        (T3.7's AST conformance test reads the literal FSMState assignments out of
        each _do_ handler body, so they must stay inline there)."""
        ctx = self._ctx
        ctx.unreadable_streak += 1
        if ctx.unreadable_streak >= UNREADABLE_STREAK_CAP:
            # 3 unreadable answers in a row on the SAME question has no exit
            # otherwise — a child who genuinely can't produce the expected shape
            # (keyboard trouble, misunderstanding "_/_") gets stuck nudging forever.
            ctx.unreadable_streak = 0
            ctx.help_n = 1
            ctx.help_modalities_used = []
            return ("", True)
        if answer_type == "mc4":
            return ("I didn't catch a letter there — please answer with A, B, C or D.", False)
        return ("Hmm, I couldn't read a number there — give it another go.", False)

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
            # Couldn't read a checkable answer (blank / gibberish / malformed). Don't
            # penalise or log — re-ask the SAME question with answer-type-aware guidance.
            # (The question itself stays live via TurnResult.question / question_display;
            # no need to re-embed it in the nudge prose.)
            nudge, cap_hit = self._handle_unreadable(answer_type)
            if cap_hit:
                ctx.state = FSMState.HELP_MODALITY_SELECT
                return ("", True)
            ctx.state = FSMState.AWAIT_ANSWER
            return (nudge, False)
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
            lines = example.splitlines()
            if len(lines) > 1:
                # A method card (multi-line, computed) -- render it in the CARD box,
                # not pasted into prose. 2026-08-14: two consecutive Explain-more
                # presses showed the SAME card two ways (proportional wrapped prose
                # here, monospace box on the next press). One shape, one look.
                self._ctx.elaborate_method_card = tuple(lines)
                return "Let's take it one step at a time. Here's a similar one worked through 👇"
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
            "expression": "(answer like 2x + 6)",
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

    def _answer_feedback(self, correct: bool) -> str:
        """Short, warm, deterministic right/wrong feedback for a scored answer.

        On wrong we don't reveal the answer — the Help loop (entered from
        BKT_UPDATE) works through it instead.
        """
        if correct:
            return self._rng.choice(PRAISE_VARIANTS)
        return self._rng.choice(WRONG_VARIANTS)

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
        # R11: refresh the in-session staleness clock — a just-reviewed node must not
        # keep being re-picked as "stale" every REVIEW_EVERY_N items.
        ctx.mastery_updated_at[ctx.current_node_id] = (
            datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
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
        ctx.items_completed += 1
        if self._max_items is not None and ctx.items_completed >= self._max_items:
            # R11 micro-session: bite-sized by design — end on a high note, not exhaustion.
            ctx.state = FSMState.SESSION_END_COMPLETE
            return ("That's a great session — see you next time!", False)
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
        modality = self._rng.choice(available)
        ctx.help_modalities_used.append(modality)
        ctx.current_pattern = f"help_{modality}"
        ctx.state = FSMState.HELP_EXPLAIN
        return ("", True)

    _MAX_EXPLAIN_ATTEMPTS = 2  # A14: bounded regeneration on a verified-wrong claim

    def _do_help_explain(self, elaborate: bool = False) -> tuple[str, bool]:
        """One Help explanation turn. With elaborate=True (R12.5, HELP_ELABORATE)
        the child asked to unpack the SAME explanation further — renders
        help_elaborate.md over the previous explanation instead of a fresh
        modality template; all the same safety guards apply.

        "Show human working" (2026-07-19): on an ELABORATE press specifically
        (never the initial Help modality explanations — maintainer's explicit
        placement ask), a step-eligible node (currently: plain non-negative
        column addition) skips the LLM entirely and renders a deterministic,
        provably-correct step grid instead — same reasoning as A14's
        verified-arithmetic guard below: an LLM asked to "show its steps" is
        exactly the failure class this project guards against, so the steps
        are computed, never composed. Non-eligible nodes fall through
        unchanged to the existing LLM-prose explanation."""
        ctx = self._ctx
        # Once the WORKING (which ends in the answer) has been shown for this
        # question, a further wrong answer must not start another LLM explain
        # loop -- the child has the answer in front of them, and a fresh prose
        # explanation buries it (maintainer, 2026-08-19: "it should rehighlight
        # that the answer again"). Re-show the same deterministic working with a
        # pointing lead-in instead. Falls through to the normal path only if the
        # working genuinely cannot be rebuilt (both branches below miss).
        if not elaborate and ctx.working_shown:
            elaborate = True
        if elaborate:
            ctx.elaborate_steps_grid = self._build_steps_grid_if_eligible()
            if ctx.elaborate_steps_grid is not None:
                live_id = getattr(ctx.current_item, "id", None)
                repeat = ctx.working_shown and ctx.working_shown_item_id == live_id
                ctx.working_shown = True
                ctx.working_shown_item_id = live_id
                explanation = ("Look again at the steps we worked through — the answer "
                               "is at the bottom. 👇") if repeat else "Let's see the steps! 👇"
                ctx.last_explanation = explanation
                ctx.state = FSMState.HELP_RECHECK_PRESENT
                return (explanation, True)
            # explain-mode (2026-08-12): same treatment, one tier down -- a node
            # without a step grid but whose LIVE item carries a computed method
            # card (Type 2 maths / Type 4 science) also skips the LLM on
            # Explain-more. Safe to use the LIVE item here specifically (unlike
            # _worked_example_for's deliberate sibling-draw below): the child has
            # already answered or is deep in the Help loop, so nothing is
            # leaked that isn't already resolved.
            ctx.elaborate_method_card = getattr(ctx.current_item, "method_steps", None)
            if ctx.elaborate_method_card is not None:
                # explain-mode Phase 3a (2026-08-13): fold in the concept's
                # authored ASCII diagram, when one exists, so the bare card
                # isn't text-only for topics where a picture genuinely helps
                # (science's whole reason for this tier -- docs/design/
                # explain_mode_design.md §3 Type 4). Deterministic, LLM-free
                # extraction (first_diagram) -- same "computed, not composed"
                # posture as the card itself. Split into individual lines to
                # match the one-tuple-element-per-line convention every other
                # card/grid line already follows.
                if self._scaffold_dir is not None:
                    node_for_scaffold = self._curriculum[ctx.current_node_id]
                    scaffold = load_visual_scaffold(
                        self._scaffold_dir, self._subject, node_for_scaffold.get("label", "")
                    )
                    diagram = first_diagram(scaffold) if scaffold else None
                    # Only a diagram with NO NUMBERS in it (2026-08-16, maintainer:
                    # "WHERE did 352 come from??").
                    #
                    # The card above is THIS item's worked example. A scaffold is a
                    # generic authoring instruction for the model -- its file says
                    # "When writing or explaining this question, use ONE of these
                    # visual structures" -- so its numbers are placeholders that can
                    # never match the drawn item. Stapling one to the card showed a
                    # child asked about 463 a place-value table reading 3|5|2, with
                    # no hint it was a different example. Every one of the 17 maths
                    # scaffolds carrying a diagram carries fixed numbers, so this was
                    # not an edge case: it was every maths node that had a scaffold.
                    #
                    # A digit-free diagram cannot contradict the card -- a labelled
                    # cell, a circuit, a story mountain -- and that is the case this
                    # tier was built for (explain_mode_design.md §3 Type 4, "science's
                    # whole reason"). 35 of science's 45 and 32 of english's 36 stay.
                    if diagram and (
                        first_diagram_is_reference_key(scaffold)
                        or not _DIAGRAM_HAS_NUMBER_RE.search(diagram)
                    ):
                        ctx.elaborate_method_card = (
                            *ctx.elaborate_method_card, "", *diagram.splitlines()
                        )
                live_id = getattr(ctx.current_item, "id", None)
                repeat = ctx.working_shown and ctx.working_shown_item_id == live_id
                ctx.working_shown = True
                ctx.working_shown_item_id = live_id
                explanation = ("Look again at how it's solved — the answer is on "
                               "the last line. 👇") if repeat else "Let's see how it's solved! 👇"
                ctx.last_explanation = explanation
                ctx.state = FSMState.HELP_RECHECK_PRESENT
                return (explanation, True)
        else:
            ctx.elaborate_steps_grid = None  # a fresh Help round -- clear any stale grid
            ctx.elaborate_method_card = None
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["label"], passage)
        template_name = "help_elaborate" if elaborate else ctx.current_pattern
        help_text = self._render_template(
            template_name, node, passage,
            worked_example=self._worked_example_for(ctx.current_node_id),
            # STEM ONLY for choice questions (2026-08-19, third leak report).
            # The full problem text carries "A) velocity B) mass ..." -- and a
            # model that can see the options will identify the right one in
            # unlimited phrasings no scrub can enumerate ("Velocity: ... It is
            # a Vector."). Withhold the options and that whole failure CLASS is
            # structurally impossible: the model teaches the concept and works
            # the sibling, but cannot point at a choice it has never seen.
            question=(
                getattr(ctx.current_item, "stem", None) or ctx.current_question or ""
            ),
            previous_explanation=ctx.last_explanation,
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
            candidate = realign_algebra_blocks(candidate)
            # A backend that hits its output-token cap returns prose cut mid-
            # sentence ("Because a") with no error signal -- the maintainer saw
            # exactly that reach a child (2026-08-19). Deterministic guard: when
            # the text ends mid-word/mid-clause, trim back to the last complete
            # sentence rather than displaying the stump.
            candidate = _trim_truncated_tail(candidate)
            candidate = _normalise_llm_math(candidate)
            # No-reveal contract (SPEC/pattern templates: "do NOT give the
            # answer" -- the child must attempt the re-check themselves). The
            # model sees the live question in {{question}} and, given budget,
            # will happily finish with "Final Answer: A" (maintainer report,
            # 2026-08-19; masked while max_tokens=400 cut it off). Deterministic
            # scrub, not prompt surgery -- prompts are A18-gated.
            candidate = _scrub_answer_reveal(
                candidate,
                self._ctx.current_item.answer_type if self._ctx.current_item else "",
                str(self._ctx.current_item.answer) if self._ctx.current_item else "",
            )
            # Choice-name guard (maintainer, CRITICAL, 2026-08-20): for a choice
            # question, prose that NAMES any live option is classifying it --
            # "methane is covalent" answers "which is covalent?" whether the
            # model saw the options or merely picked the canonical example.
            # Deterministic: WE know the live choices even though the model does
            # not. Reject and retry; the existing fallback hint catches
            # exhaustion. Only for mc4 -- numeric answers appear legitimately
            # throughout worked arithmetic.
            # Relabel (maintainer, 2026-08-20: "the answer says iron.. when it
            # is not... maybe example's answer is a better wording"): the model
            # works the SIBLING example to its answer, and a bare
            # "Final Answer:" / "Answer:" heading reads as the answer to the
            # child's own question. Deterministic rewording, prose path only --
            # the live item's own card keeps its true "Answer:" line.
            candidate = _EXAMPLE_ANSWER_HEADING_RE.sub("The example's answer:", candidate)
            if candidate and _names_a_live_choice(candidate, self._ctx.current_item):
                logger.warning(
                    "help explanation: discarded -- names a live answer choice (attempt %d)",
                    attempt + 1,
                )
                continue
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
        # R12.4/12.5: remember what was shown — the variety line in the help
        # templates and the elaborate flow both build on the previous explanation.
        ctx.last_explanation = explanation
        # (No "Q) {question}" recap prefix any more — the pending question is carried
        # structurally in TurnResult.question and stays visible in its own display
        # block; the recap prefix was what broke the old string-split display.)
        ctx.state = FSMState.HELP_RECHECK_PRESENT
        return (explanation, True)

    def _do_help_recheck_present(self) -> tuple[str, bool]:
        ctx = self._ctx
        # ONE question at a time: re-try the SAME question the child is on (kept
        # visible via TurnResult.question), rather than posing a new, different one.
        # Show the expected answer SHAPE so the child knows how to reply.
        answer_type, _, _ = self._answer_spec(self._curriculum[ctx.current_node_id])
        hint = self._answer_format_hint(answer_type)
        if ctx.current_item is not None or ctx.current_question:
            ctx.state = FSMState.HELP_RECHECK_AWAIT
            ctx.question_display = f"{ctx.current_question} {hint}".rstrip()
            return (RECHECK_PROMPT, False)
        ctx.current_item = None
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["label"], passage)
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
        ctx.question_display = f"{recheck_q} {hint}".rstrip()
        return (RECHECK_PROMPT, False)

    def _do_help_recheck_await(self, inp: str | None) -> tuple[str, bool]:
        ctx = self._ctx
        if inp is None:
            return ("", False)
        stripped = inp.strip()
        if _is_stop(stripped):
            ctx.state = FSMState.SESSION_END_BY_LEARNER
            return ("OK, see you next time!", False)
        # R12.5: "explain more" — unpack the SAME explanation one level deeper.
        # Only meaningful while an explanation is live; bounded per Help chain so
        # a child typing "more" forever still reaches the question.
        if stripped.lower() in ELABORATE_WORDS and ctx.last_explanation:
            if ctx.elaborate_count >= ELABORATE_CAP:
                return ("Let's give the question a try now — you can do it! ✏️", False)
            ctx.elaborate_count += 1
            ctx.state = FSMState.HELP_ELABORATE
            return ("", True)
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
            return ("Please give it a try — even a guess is OK!", False)
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
        if outcome.result in (CheckResult.SAFE_REJECT, CheckResult.EXTRACT_FAIL):
            # E2.4: an unreadable re-check answer must get the same "couldn't read
            # that" re-ask the first ask gets — previously it scored flatly WRONG
            # against mastery/retry-count (the only scoring site with that branch
            # was _do_score; recheck and probe silently lacked it).
            nudge, cap_hit = self._handle_unreadable(answer_type)
            if cap_hit:
                ctx.state = FSMState.HELP_MODALITY_SELECT
                return ("", True)
            ctx.state = FSMState.HELP_RECHECK_AWAIT
            return (nudge, False)
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
            hint = item.format_hint or self._answer_format_hint(item.answer_type)
            ctx.question_display = f"{item.problem} {hint}".rstrip()
            return ("", False)
        ctx.current_item = None
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["label"], passage)
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
        ctx.question_display = f"{probe_q} {hint}".rstrip()
        return ("", False)

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
            return ("Give it a go — what do you think?", False)
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
        if outcome.result in (CheckResult.SAFE_REJECT, CheckResult.EXTRACT_FAIL):
            # E2.4: same re-ask treatment as _do_score/_do_help_recheck_score — an
            # unreadable probe answer must not count as a failed probe (it would
            # feed the false-confidence classifier a phantom miss).
            nudge, cap_hit = self._handle_unreadable(answer_type)
            if cap_hit:
                ctx.state = FSMState.HELP_MODALITY_SELECT
                return ("", True)
            ctx.state = FSMState.PROBE_AWAIT_ANSWER
            return (nudge, False)
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
            return (self._rng.choice(PRAISE_VARIANTS), True)
        if ctx.probe_variant == 0:
            # SPEC §14: "The FSM runs EXACTLY ONE retry variant on a first
            # failure", and both false_confidence and forgetting_suspect are
            # asserted "only when slip is ruled out (BOTH variants failed)".
            # CLEAN_PASS returned above, so reaching here on variant 0 means the
            # first probe failed -- which is precisely when the retry is owed.
            #
            # This used to also require the provisional class to be SLIP_SUSPECT,
            # which inverted the intent (2026-08-16): the retry was given only
            # when the verdict was already benign, and SKIPPED for the two
            # serious ones. A child with mastery 0.95 and no Help who slipped
            # once was demoted 0.95 -> 0.60 and logged false_confidence on a
            # single wrong answer -- the exact "a single wrong answer can be a
            # slip" case the retry exists to disambiguate, and most likely in
            # high-mastery learners. It also corrupted the pilot's
            # false-confidence baseline (SPEC pilot goals).
            #
            # The probe_event is still written after the retry, as before.
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
        previous_explanation: str = "",
    ) -> str:
        tmpl = self._load_template(name)
        scaffold = ""
        if self._scaffold_dir is not None:
            scaffold = load_visual_scaffold(self._scaffold_dir, self._subject, node.get("label", ""))
        return (
            tmpl
            .replace("{{concept}}", node.get("label", "fractions"))
            .replace("{{answer_type}}", node.get("answer_type", "fraction"))
            .replace("{{grounding_passage}}", passage)
            .replace("{{worked_example}}", worked_example or "a simple example with small numbers")
            .replace("{{question}}", question or "the question they're working on")
            .replace("{{previous_explanation}}", previous_explanation or "(none yet — this is the first explanation)")
            .replace("{{visual_scaffold}}", scaffold)
        )

    def _build_steps_grid_if_eligible(self) -> StepGrid | None:
        """"Show human working": build a deterministic step grid for the
        current item's problem text, or None if the node's shape isn't
        step-eligible (plain non-negative addition/subtraction/integer
        multiplication/division so far -- Phase 1/2/3/4). Uses
        ctx.current_item.problem when a real item is live (the normal
        case), falling back to ctx.current_question for the legacy
        LLM-generated-question path (which never matches any extraction
        regex anyway, since that text isn't one of our own f-string
        phrasings -- returns None there, same as any other ineligible
        node).

        Division's `ending` is derived from the item's answer_type
        (2026-07-24 rebuild): "decimal" -> continue past the given
        precision into synthesized decimal places; "fraction" -> a mixed
        number remainder (only reachable for problems matching the
        division regex in the first place, so this never collides with
        the pilot's OWN plain fraction-arithmetic content, which has a
        different problem-text shape); anything else -> plain "R n"
        remainder notation. build_long_division_steps can still raise
        ValueError (a "decimal" ending that doesn't terminate within the
        synthesized-digit cap) -- caught here as "not eligible", same
        contract as every other ineligible shape."""
        ctx = self._ctx
        item = ctx.current_item
        problem = item.problem if item is not None else (ctx.current_question or "")
        add_operands = extract_addition_operands(problem)
        if add_operands is not None:
            return build_addition_steps(*add_operands)
        sub_operands = extract_subtraction_operands(problem)
        if sub_operands is not None:
            return build_subtraction_steps(*sub_operands)
        mult_operands = extract_multiplication_operands(problem)
        if mult_operands is not None:
            return build_multiplication_partial_products_steps(*mult_operands)
        # Phases A+B (2026-08-11): the two multiplication shapes the plain
        # integer extractor deliberately refuses. Each extractor rejects what
        # the others accept, so the order among these three is not load-bearing
        # -- they are listed after the integer case only for readability.
        dec_mult_operands = extract_decimal_multiplication_operands(problem)
        if dec_mult_operands is not None:
            return build_multiplication_decimal_steps(*dec_mult_operands)
        signed_mult_operands = extract_signed_multiplication_operands(problem)
        if signed_mult_operands is not None:
            return build_signed_multiplication_steps(*signed_mult_operands)
        # Phase C: signed add/sub -- either operand negative, or a subtraction
        # whose result goes negative. Runs after the plain add/sub extractors
        # above, which keep every case they already handle.
        signed_add_operands = extract_signed_addition_operands(problem)
        if signed_add_operands is not None:
            return build_signed_addition_steps(*signed_add_operands)
        div_operands = extract_division_operands(problem)
        if div_operands is not None:
            answer_type = item.answer_type if item is not None else "int"
            ending = "decimal" if answer_type == "decimal" else "fraction" if answer_type == "fraction" else "remainder"
            try:
                return build_long_division_steps(*div_operands, ending=ending)
            except ValueError:
                return None
        return None

    def _worked_example_for(self, node_id: str) -> str:
        """A solved example string for the worked-example slot in Help/transfer prompts.

        Prefers a node-authored `worked_example`; else a solved item from the bank (excluding
        the live question so its answer isn't revealed); else "".

        explain-mode (2026-08-12): when that sibling item carries a computed
        `method_steps` card (Type 2/4), its lines replace the bare "(Answer: X)"
        string -- the LLM is handed an actual method to narrate/build on instead
        of a fact with no derivation (docs/design/explain_mode_design.md §4a/b,
        the root cause of the maintainer-reported "not much explanation" gap).
        Deliberately still a SIBLING draw, never the live item -- this function
        feeds BOTH the first (non-elaborate) Help explanation and
        help_elaborate.md, and the live answer must never leak on the first
        Help press. The live item's OWN card is used only by the elaborate
        bare-card path in `_do_help_explain`, which runs after the child has
        already answered.
        """
        node = self._curriculum.get(node_id, {})
        if node.get("worked_example"):
            return str(node["worked_example"])
        if self._item_bank is not None:
            live = self._ctx.current_item
            cur_id = getattr(live, "id", None)
            live_text = (getattr(live, "stem", None) or getattr(live, "problem", "")) if live else ""
            # Exclusion by id is NOT enough (found 2026-08-19): generator-backed
            # sources mint a fresh id per draw, so on a small mc domain the
            # "sibling" is routinely the SAME question -- and the help templates
            # then work the child's own question "through to its final answer".
            # The leak was masked while max_tokens=400 truncated explanations
            # before the reveal. Retry for different CONTENT; a domain so small
            # that every draw collides gets NO worked example rather than a
            # solved copy of the live question.
            live_choices = {
                str(c).strip().lower() for c in (getattr(live, "choices", None) or ())
            }
            for _ in range(8):
                ex = self._item_bank.example(node_id, exclude_id=cur_id)
                if ex is None:
                    break
                ex_text = getattr(ex, "stem", None) or ex.problem
                if live_text and ex_text == live_text:
                    continue
                # A different QUESTION is not enough (maintainer, CRITICAL,
                # 2026-08-20): on a small mc domain the sibling's options
                # overlap the live ones, and a worked sibling that classifies
                # "methane -> COVALENT" has answered a live question whose
                # correct choice is methane. The sibling's choice set must be
                # DISJOINT from the live one; a pool too small to allow that
                # gets NO worked example rather than a keyed one.
                ex_choices = {
                    str(c).strip().lower() for c in (getattr(ex, "choices", None) or ())
                }
                if live_choices and ex_choices and (live_choices & ex_choices):
                    continue
                if getattr(ex, "method_steps", None):
                    return "\n".join(ex.method_steps)
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
