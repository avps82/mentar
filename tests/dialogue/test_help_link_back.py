"""dialogue/controller.py — the Help loop's terminal valve (LINK_BACK).

Closes a real coverage gap found on 2026-08-12: `LINK_BACK` is referenced in
five places in controller.py and had ZERO tests. It is the valve that stops the
Help loop generating variants forever — a child who keeps failing must
eventually be handed to a grown-up and moved on, not looped. That it was
untested meant nothing would have caught it silently breaking.

Covers the deterministic half of TESTS.md T4.1 (modality rotation) and T4.2
(retry cap → link-back, never an Nth variant). The LLM-judged halves of those
T-tasks (does the explanation *read* as a different representation) are eval
work and are not attempted here.

    python3 tests/dialogue/test_help_link_back.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from mentar.dialogue.controller import (  # noqa: E402
    HELP_MODALITIES,
    HELP_RETRY_CAP,
    FSMState,
    SessionController,
)

PROMPTS = REPO / "prompts"

_CURRICULUM = {
    "unit_fractions": {
        "label": "unit fractions",
        "answer_type": "fraction",
        "checker": "fraction_equiv",
        "expected_answer": "1/3",
        "grounding": {},
        "prerequisites": [],
    }
}


class _FakeStore:
    def __init__(self):
        self._m = {}

    def get_skill_state(self, learner_id, node_id):
        v = self._m.get(node_id)
        return {"p_mastery": v} if v is not None else None

    def update_skill_state(self, learner_id, node_id, p):
        self._m[node_id] = p


def _make(llm_fn=None, grounding_cfg=None):
    return SessionController(
        llm_call=llm_fn or (lambda msgs: "An explanation."),
        prompt_dir=PROMPTS,
        grounding_cfg=grounding_cfg if grounding_cfg is not None else {},
        curriculum=_CURRICULUM,
        db_store=_FakeStore(),
        learner_id="test-learner",
        rng_seed=11,
    )


# ── T4.1: modality rotation ──────────────────────────────────────────────────

def test_consecutive_help_presses_use_distinct_modalities():
    """T4.1(a): a Help chain must never reuse a representation it already tried."""
    ctrl = _make()
    ctrl.step(None)
    ctrl.step("?")
    used = list(ctrl._ctx.help_modalities_used)
    for _ in range(len(HELP_MODALITIES) - 1):
        ctrl.step("?")
        used = list(ctrl._ctx.help_modalities_used)
    assert len(used) == len(set(used)), f"a modality was reused: {used}"
    assert set(used) <= set(HELP_MODALITIES), used


def test_every_modality_is_reachable():
    """Guards against a rotation bug that silently starves one modality --
    all five must be used before the chain can exhaust."""
    ctrl = _make()
    ctrl.step(None)
    for _ in range(len(HELP_MODALITIES)):
        ctrl.step("?")
    assert set(ctrl._ctx.help_modalities_used) == set(HELP_MODALITIES)


# ── T4.2: the loop terminates, and terminates into LINK_BACK ─────────────────

def test_exhausting_every_modality_links_back_instead_of_a_new_variant():
    """T4.2: after the last modality there must be NO further generation."""
    ctrl = _make()
    ctrl.step(None)
    for _ in range(len(HELP_MODALITIES)):
        ctrl.step("?")
    # every modality now spent -- the next Help press must not invent a 6th
    ctrl._ctx.state = FSMState.HELP_MODALITY_SELECT
    text, _ = ctrl._do_help_modality_select()
    assert ctrl._ctx.state == FSMState.LINK_BACK, ctrl._ctx.state


def test_retry_cap_routes_to_link_back():
    """T4.2: help_n hitting HELP_RETRY_CAP ends the loop, whatever modalities remain.

    The cap lives in _do_help_retry_decision, not _do_help_recheck_score -- an
    earlier cut of this test drove the wrong handler and "failed" against
    correct code."""
    ctrl = _make()
    ctrl.step(None)
    ctrl.step("?")
    ctrl._ctx.help_scored_correct = False
    ctrl._ctx.help_n = HELP_RETRY_CAP
    ctrl._ctx.state = FSMState.HELP_RETRY_DECISION
    ctrl._do_help_retry_decision()
    assert ctrl._ctx.state == FSMState.LINK_BACK, ctrl._ctx.state


def test_below_the_cap_keeps_trying_another_modality():
    """The other side of the cap: it must not fire early and cut Help short."""
    ctrl = _make()
    ctrl.step(None)
    ctrl.step("?")
    ctrl._ctx.help_scored_correct = False
    ctrl._ctx.help_n = HELP_RETRY_CAP - 1
    ctrl._ctx.state = FSMState.HELP_RETRY_DECISION
    ctrl._do_help_retry_decision()
    assert ctrl._ctx.state == FSMState.HELP_MODALITY_SELECT, ctrl._ctx.state
    assert ctrl._ctx.help_n == HELP_RETRY_CAP


def test_a_correct_recheck_leaves_the_help_loop_without_linking_back():
    """A child who gets it right must not be handed off as a sticking point."""
    ctrl = _make()
    ctrl.step(None)
    ctrl.step("?")
    ctrl._ctx.help_scored_correct = True
    ctrl._ctx.help_n = HELP_RETRY_CAP
    ctrl._ctx.state = FSMState.HELP_RETRY_DECISION
    ctrl._do_help_retry_decision()
    assert ctrl._ctx.state == FSMState.BRANCH_DECISION, ctrl._ctx.state


def test_link_back_never_calls_the_llm():
    """T4.2's core requirement: the link-back is a VETTED SOURCE REFERENCE, not
    another generation. If this ever starts calling the model, the retry cap
    stops being a cap."""
    calls = []

    def _spy(msgs):
        calls.append(msgs)
        return "a generated explanation"

    ctrl = _make(llm_fn=_spy)
    ctrl.step(None)
    ctrl._ctx.state = FSMState.LINK_BACK
    before = len(calls)
    ctrl._do_link_back()
    assert len(calls) == before, "LINK_BACK generated a new explanation via the LLM"


def test_link_back_hands_off_and_moves_on():
    """The child must be pointed at a grown-up and the session must continue --
    not dead-end. Regression guard on both halves."""
    ctrl = _make()
    ctrl.step(None)
    ctrl._ctx.state = FSMState.LINK_BACK
    text, _ = ctrl._do_link_back()
    assert text.strip(), "LINK_BACK produced no message for the child"
    lowered = text.lower()
    assert any(w in lowered for w in ("grown-up", "teacher")), text
    assert ctrl._ctx.state == FSMState.BRANCH_DECISION, ctrl._ctx.state


def test_link_back_degrades_gracefully_without_grounding():
    """Grounding is wired to one pack only, so for almost every shipped node the
    passage is empty. The fallback must still be a real, warm message -- never a
    blank turn or a dangling 'here's something to look at:' with nothing after."""
    ctrl = _make(grounding_cfg={})
    ctrl.step(None)
    ctrl._ctx.state = FSMState.LINK_BACK
    text, _ = ctrl._do_link_back()
    assert text.strip()
    assert not text.rstrip().endswith(":"), f"dangling lead-in with no content: {text!r}"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
