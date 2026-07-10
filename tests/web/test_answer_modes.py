"""Pure tests for web/answer_modes.py (R2.3 — answer-mode registry).

    python3 tests/web/test_answer_modes.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mentar.web.answer_modes import ANSWER_MODES, DEFAULT_MODE, mode_for  # noqa: E402


def test_mode_for_known_types():
    assert mode_for("mc4").widget == "radio"
    assert mode_for("mc4").show_format_hint is False
    assert mode_for("fraction").widget == "fraction"
    assert mode_for("fraction").show_format_hint is True
    assert mode_for("int").widget == "number"
    assert mode_for("free_text").widget == "text"


def test_mode_for_unknown_or_none_falls_back_to_default():
    assert mode_for("something_new") is DEFAULT_MODE
    assert mode_for(None) is DEFAULT_MODE
    assert mode_for("") is DEFAULT_MODE
    assert DEFAULT_MODE.widget == "text"


def test_compose_default_reads_answer_field():
    mode = ANSWER_MODES["int"]
    assert mode.compose({"answer": "  42  "}) == "42"
    assert mode.compose({}) == ""


def test_compose_fraction_prefers_direct_answer_then_num_den():
    mode = ANSWER_MODES["fraction"]
    # A direct "answer" field (e.g. typed "3/4") wins over num/den.
    assert mode.compose({"answer": "1/2", "answer_num": "3", "answer_den": "4"}) == "1/2"
    # No direct answer -> compose from num/den.
    assert mode.compose({"answer_num": "3", "answer_den": "4"}) == "3/4"
    # Missing either half -> empty (SAFE_REJECT territory, not a crash).
    assert mode.compose({"answer_num": "3"}) == ""
    assert mode.compose({}) == ""


def test_compose_radio_reads_the_letter_from_answer_field():
    mode = ANSWER_MODES["mc4"]
    assert mode.compose({"answer": "B"}) == "B"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} answer-mode tests passed.")
