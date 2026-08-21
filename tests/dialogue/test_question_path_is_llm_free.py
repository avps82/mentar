"""The question a child sees — and now its PICTURE — never comes from the model.

Maintainer, 2026-08-21: *"question part AI is not there. Hence testing is
important."* That is exactly right, and it is the reason this file exists.

`_do_present` samples a generated item and returns immediately; the LLM branch
below it is only a fallback for nodes with no generator. So for every visual
topic the picture is emitted by owned, deterministic code and shown to the child
VERBATIM. There is no model to paper over a malformed picture, and no per-question
human review. Whatever the generator emits is precisely what a seven-year-old
gets, which makes automated tests the only safety net the question path has.

This pins the property itself: presenting a visual question performs ZERO LLM
calls. Route the question through the model "just for phrasing" and it reddens.

    python3 -m pytest tests/dialogue/test_question_path_is_llm_free.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.dialogue.controller import SessionController  # noqa: E402
from mentar.engine.curriculum import load_curriculum  # noqa: E402
from mentar.engine.item_sources import build_registry  # noqa: E402
from mentar.engine.itembank import load_item_bank  # noqa: E402
from mentar.engine.itemgen import CompositeItemSource, ItemGenerator  # noqa: E402

PROMPTS = REPO_ROOT / "prompts"
_PILOT = REPO_ROOT / "curriculum" / "templates" / "_pilot" / "fractions.md"


class _CountingLLM:
    """Fails loudly rather than silently returning prose: if the question path
    ever reaches the model, the test should say so, not paper over it."""

    def __init__(self):
        self.calls: list[list[dict]] = []

    def __call__(self, messages):
        self.calls.append(messages)
        return "MODEL PROSE THAT MUST NEVER BECOME A QUESTION"


def _controller(llm):
    """Wired the way web/app.py wires it: WITH an item source.

    Passing item_bank=None is the documented legacy/test fallback, and a
    controller built that way sends every question to the model — which is
    exactly the behaviour under test, so omitting it would make this file
    assert the opposite of what it claims."""
    bank_path = REPO_ROOT / "curriculum" / "itembank" / "pilot_fractions.jsonl"
    subj = build_registry(bank_path)["pilot_fractions"]
    bank = load_item_bank(subj["itembank"]) if subj["itembank"] else None
    source = CompositeItemSource(ItemGenerator(generators=subj["generators"]), bank)
    return SessionController(
        llm_call=llm,
        prompt_dir=PROMPTS,
        grounding_cfg={},
        curriculum=load_curriculum(_PILOT),
        db_store=None,
        learner_id="visual-test-learner",
        item_bank=source,
    )


def test_presenting_a_visual_question_calls_no_llm():
    llm = _CountingLLM()
    ctrl = _controller(llm)
    ctrl.step(None)          # opening turn -> assent
    ctrl.step("yes")         # -> first question

    assert ctrl.current_question is not None, "no question was presented"
    assert llm.calls == [], (
        f"the question path called the model {len(llm.calls)} time(s) — the question "
        "and its picture must be deterministic, because nothing downstream reviews them"
    )


def test_a_presented_picture_is_exactly_what_the_generator_emitted():
    """No re-wrapping, no prose-massaging, no model in between: the lines the
    child sees are byte-identical to the generator's output.

    The node is pinned rather than walked to, so this asserts the property every
    run instead of skipping whenever the fringe picks a different node first."""
    llm = _CountingLLM()
    ctrl = _controller(llm)
    ctrl.step(None)
    ctrl.step("yes")

    ctrl._ctx.current_node_id = "unit_fractions"
    ctrl._do_present()

    assert ctrl.current_visual, "the pinned visual node presented no picture"
    assert ctrl.current_visual == list(ctrl._ctx.current_item.visual), (
        "picture was altered between the item and the view"
    )
    assert llm.calls == [], "a picture-bearing turn reached the model"


def test_the_picture_never_states_the_answer_on_the_question_path():
    """End-to-end version of the give-away guard: not "the renderer withholds its
    summary" but "what actually reached the child does not assert the answer"."""
    llm = _CountingLLM()
    ctrl = _controller(llm)
    ctrl.step(None)
    ctrl.step("yes")
    ctrl._ctx.current_node_id = "unit_fractions"
    for _ in range(15):
        ctrl._do_present()
        visual, item = ctrl.current_visual, ctrl._ctx.current_item
        if not visual:
            continue
        for line in visual:
            assert "=" not in line, f"picture asserts a result: {line!r}"
            assert line.strip() != str(item.answer), f"picture IS the answer: {line!r}"


def test_the_cli_transcript_carries_the_picture_too():
    """A constitutive question WITHOUT its picture is unanswerable, and the CLI
    and durable transcript read `TurnResult.text`, not `current_visual`.

    The web view pulls the picture from `current_visual` into its own <pre>, so
    every browser test passes whether or not `text` carries it — a refactor that
    tidied the picture out of `_compose_result` would leave the terminal asking
    "What fraction is ONE part?" with nothing to look at, and nothing would go
    red. Pinned here: the picture is in `text`, ABOVE the question, and exactly
    the generator's lines.
    """
    ctrl = _controller(_CountingLLM())
    ctrl.step(None)
    ctrl.step("yes")
    ctrl._ctx.current_node_id = "unit_fractions"
    ctrl._do_present()
    result = ctrl._compose_result("")

    picture = "\n".join(ctrl.current_visual)
    assert picture in result.text, (
        f"the picture never reached the CLI transcript:\n{result.text!r}"
    )
    assert result.question, "no question was presented"
    assert result.text.index(result.question) < result.text.index(picture), (
        "the question must come ABOVE the picture it belongs to -- instruction "
        "first, then the material (maintainer, 2026-08-21)"
    )
