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

import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from mentar.engine.bkt import BktParams, P_L0, bkt_update, params_for
from mentar.engine.fringe import DEFAULT_MASTERY_THRESHOLD, outer_fringe
from mentar.engine.probe_classify import ProbeClass, classify_probe
from mentar.eval.verify_numeric import CheckResult, check
from mentar.grounding import resolve_grounding
from mentar.safety.escalation import (
    HANDOFF_MESSAGE_PRIMARY,
    TriggerClass,
    classify,
)

logger = logging.getLogger(__name__)

HELP_MODALITIES = ["visual", "concrete", "analogy", "story", "formal"]
HELP_RETRY_CAP = 3
PROBE_EVERY_N = 5  # W5.3 pilot default


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
    current_node_id: Optional[str] = None
    current_pattern: Optional[str] = None
    current_question: Optional[str] = None           # rendered question text
    current_answer: Optional[str] = None             # child's latest answer
    last_scored_correct: Optional[bool] = None
    items_since_probe: int = 0
    # Help loop
    help_n: int = 0                                  # retry counter (1-indexed)
    help_modalities_used: list = field(default_factory=list)
    help_answer: Optional[str] = None
    help_scored_correct: Optional[bool] = None
    # Probe loop
    probe_variant: int = 0                           # 0 = first, 1 = retry
    probe_first_correct: Optional[bool] = None
    probe_answer: Optional[str] = None
    probe_scored_correct: Optional[bool] = None


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
    ) -> None:
        self._llm = llm_call
        self._prompt_dir = Path(prompt_dir)
        self._grounding_cfg = grounding_cfg
        self._curriculum = curriculum          # node_id -> {concept, answer_type, checker, expected_answer, grounding, prerequisites, bkt_priors?}
        self._store = db_store
        self._learner_id = learner_id
        self._templates: dict[str, str] = {}  # loaded lazily
        self._ctx = _SessionCtx()

    # ── Public API ────────────────────────────────────────────────────────────

    def step(self, learner_input: str | None) -> TurnResult:
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
                output_text = text
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

    # ── FSM tick dispatch ─────────────────────────────────────────────────────

    def _tick(self, state: FSMState, inp: str | None) -> tuple[str, bool]:
        """Process one FSM state.  Returns (text_output, should_advance_immediately)."""
        ctx = self._ctx
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
                ctx.mastery[node_id] = row["p_mastery"] if row else P_L0
            except Exception:
                ctx.mastery[node_id] = P_L0
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
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["concept"], passage)
        pattern_text = self._render_template(ctx.current_pattern, node, passage)
        question = self._llm([
            {"role": "system", "content": system_text},
            {"role": "user", "content": pattern_text},
        ])
        ctx.current_question = question
        ctx.state = FSMState.AWAIT_ANSWER
        return (question, False)

    def _do_await_answer(self, inp: str | None) -> tuple[str, bool]:
        ctx = self._ctx
        if inp is None:
            return ("", False)
        stripped = inp.strip()
        # Learner requests help
        if stripped in ("?", "help", "Help", "HELP", "h"):
            ctx.help_n = 1
            ctx.help_modalities_used = []
            ctx.state = FSMState.HELP_MODALITY_SELECT
            return ("", True)
        # Learner wants to stop
        if stripped.lower() in ("stop", "quit", "bye", "exit"):
            ctx.state = FSMState.SESSION_END_BY_LEARNER
            return ("OK, see you next time!", False)
        ctx.current_answer = stripped
        ctx.state = FSMState.SCORE
        return ("", True)

    def _do_score(self) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        outcome = check(
            answer_type=node.get("answer_type", "free_text"),
            checker=node.get("checker", "none"),
            llm_output=ctx.current_answer or "",
            ground_truth=node.get("expected_answer", ""),
        )
        if outcome.result is CheckResult.SAFE_REJECT:
            # Regenerate — do not penalise
            ctx.state = FSMState.PRESENT
            return ("", True)
        ctx.last_scored_correct = (outcome.result is CheckResult.PASS)
        ctx.state = FSMState.BKT_UPDATE
        return ("", True)

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

    def _do_help_explain(self) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["concept"], passage)
        help_text = self._render_template(ctx.current_pattern, node, passage)
        explanation = self._llm([
            {"role": "system", "content": system_text},
            {"role": "user", "content": help_text},
        ])
        ctx.state = FSMState.HELP_RECHECK_PRESENT
        return (explanation, True)

    def _do_help_recheck_present(self) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["concept"], passage)
        transfer_text = self._render_template("transfer_question_gen", node, passage)
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
        if not stripped:
            # Skip attempt rejected — stay in state
            return ("Please give it a try — even a guess is OK!", False)
        ctx.help_answer = stripped
        ctx.state = FSMState.HELP_RECHECK_SCORE
        return ("", True)

    def _do_help_recheck_score(self) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        outcome = check(
            answer_type=node.get("answer_type", "free_text"),
            checker=node.get("checker", "none"),
            llm_output=ctx.help_answer or "",
            ground_truth=node.get("expected_answer", ""),
        )
        ctx.help_scored_correct = (outcome.result is CheckResult.PASS)
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
        node = self._curriculum[ctx.current_node_id]
        passage = resolve_grounding(node.get("grounding", {}), self._grounding_cfg)
        system_text = self._render_system_prompt(node["concept"], passage)
        transfer_text = self._render_template("transfer_question_gen", node, passage)
        probe_q = self._llm([
            {"role": "system", "content": system_text},
            {"role": "user", "content": transfer_text},
        ])
        ctx.current_question = probe_q
        ctx.state = FSMState.PROBE_AWAIT_ANSWER
        return (probe_q, False)

    def _do_probe_await_answer(self, inp: str | None) -> tuple[str, bool]:
        ctx = self._ctx
        if inp is None:
            return ("", False)
        stripped = inp.strip()
        if not stripped:
            return ("Give it a go — what do you think?", False)
        ctx.probe_answer = stripped
        ctx.state = FSMState.PROBE_SCORE
        return ("", True)

    def _do_probe_score(self) -> tuple[str, bool]:
        ctx = self._ctx
        node = self._curriculum[ctx.current_node_id]
        outcome = check(
            answer_type=node.get("answer_type", "free_text"),
            checker=node.get("checker", "none"),
            llm_output=ctx.probe_answer or "",
            ground_truth=node.get("expected_answer", ""),
        )
        ctx.probe_scored_correct = (outcome.result is CheckResult.PASS)
        if ctx.probe_variant == 0:
            ctx.probe_first_correct = ctx.probe_scored_correct
        ctx.state = FSMState.PROBE_CLASSIFY
        return ("", True)

    def _do_probe_classify(self) -> tuple[str, bool]:
        ctx = self._ctx
        mastery = ctx.mastery.get(ctx.current_node_id, 0.0)
        stale = False  # TODO: wire updated_at from skill_state for forgetting detection
        probe_class = classify_probe(
            first_correct=ctx.probe_first_correct or False,
            retry_correct=ctx.probe_scored_correct if ctx.probe_variant > 0 else None,
            p_mastery=mastery,
            help_used=len(ctx.help_modalities_used) > 0,
            stale_mastery=stale,
        )
        if probe_class is ProbeClass.CLEAN_PASS:
            ctx.state = FSMState.BRANCH_DECISION
            return ("", True)
        if probe_class is ProbeClass.SLIP_SUSPECT and ctx.probe_variant == 0:
            # One retry allowed before classifying
            ctx.probe_variant = 1
            ctx.state = FSMState.PROBE_PRESENT
            return ("", True)
        # false_confidence / forgetting_suspect / slip after retry -> advance
        ctx.state = FSMState.BRANCH_DECISION
        return ("", True)

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

    def _render_template(self, name: str, node: dict, passage: str) -> str:
        tmpl = self._load_template(name)
        return (
            tmpl
            .replace("{{concept}}", node.get("concept", "fractions"))
            .replace("{{answer_type}}", node.get("answer_type", "fraction"))
            .replace("{{grounding_passage}}", passage)
        )

    def _render_system_prompt(self, concept: str, passage: str) -> str:
        tmpl = self._load_template("system_prompt")
        return (
            tmpl
            .replace("{{concept}}", concept)
            .replace("{{grounding_passage}}", passage)
        )
