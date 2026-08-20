"""Machine expression syntax must never reach a child's screen.

Found 2026-08-18: the quadratic families' problem and card text carry Python
power syntax, so a Year 11 question rendered as "If a = 4x**2 + 6x ..." -- the
question path (markdown-lite) is not the card chokepoint, so the 2026-08-16 `*`
fix never covered it.

The display form is `^`, NOT the prettier superscript: the verifier accepts a
caret and SAFE_REJECTs "x²", and a child who copies the displayed answer back
must never be rejected (the 6764399 invariant).

    python3 -m pytest tests/web/test_expr_display.py
"""

from __future__ import annotations

import pathlib
import random
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "tests" / "web"))

from test_progress import _client

from mentar.engine.item_sources import build_registry  # noqa: E402
from mentar.engine.itemgen import ItemGenerator  # noqa: E402
from mentar.eval.verify_numeric import CheckResult, check  # noqa: E402

# `\w**`, `**\w` -- a `**` or `*` sitting between operands, i.e. machine syntax.
_MACHINE = re.compile(r"\w\*|\*\w")


def test_a_quadratic_question_renders_caret_not_python_power():
    """Through the real request path: pin a quadratic node, read the rendered
    question. This is the exact page a Year 11 child sees."""
    app_mod, c = _client()
    c.post("/choose", data={
        "subject": "au_acara_year11_maths_methods", "topic": "au11_combine_quadratic_linear",
    })
    body = c.get("/learn").get_data(as_text=True)
    q = re.search(r'class="question-text">(.*?)</div>', body, re.S).group(1)
    assert "**" not in q, f"Python power syntax on a child's screen: {q[:120]!r}"
    assert "^" in q, "the squared term should render with a caret"


def test_no_card_line_or_problem_shows_machine_syntax_after_display_transform():
    """Sweep every generator: problem text and card lines, passed through the
    one display chokepoint, must be free of `*`/`**` between operands."""
    app_mod, _ = _client()
    reg = build_registry(REPO_ROOT / "curriculum" / "itembank" / "fractions.jsonl")
    offenders = []
    for src, spec in sorted(reg.items()):
        for node, fn in sorted((spec["generators"] or {}).items()):
            gen = ItemGenerator({node: fn}, rng=random.Random(20260818))
            for _ in range(4):
                item = gen._make(node)
                if item is None:
                    break
                lines = [item.problem or ""] + [str(x) for x in (item.method_steps or ())]
                for line in lines:
                    out = app_mod._display_expr_text(line)
                    if _MACHINE.search(out):
                        offenders.append((src, node, out[:70]))
                        break
    assert not offenders, f"machine syntax survives display: {offenders[:6]}"


def test_the_displayed_answer_still_passes_the_verifier():
    """The 6764399 invariant, extended to the caret transform: for every
    expression item, the DISPLAYED form of its answer must PASS its own checker
    against the machine ground truth -- a child copying the screen is right."""
    app_mod, _ = _client()
    reg = build_registry(REPO_ROOT / "curriculum" / "itembank" / "fractions.jsonl")
    failures = []
    checked = 0
    for src, spec in sorted(reg.items()):
        for node, fn in sorted((spec["generators"] or {}).items()):
            gen = ItemGenerator({node: fn}, rng=random.Random(7))
            item = gen._make(node)
            if item is None or item.answer_type != "expression":
                continue
            checked += 1
            shown = app_mod._display_expr_text(str(item.answer))
            out = check("expression", "expression_equiv", shown, str(item.answer))
            if out.result is not CheckResult.PASS:
                failures.append((src, node, shown, out.result.name))
    assert checked > 20, f"sweep vacuous -- only {checked} expression items found"
    assert not failures, f"displayed answers the verifier rejects: {failures[:6]}"
