"""Answer-mode registry (R2.3, maintainer ask: "config for different modes for
answering things").

Single owned place mapping an answer_type -> (which widget the web view
renders, whether the "(answer like ...)" format hint is shown, how the posted
form composes into the ONE answer string SessionController.step() accepts).
Deliberately a code-level registry, not a YAML/JSON file: there is no
per-deployment reason to vary answer widgets at runtime, and a small reviewed
dict already IS the configuration surface -- a file would just add indirection
with nothing to configure differently per install.

The verifier's answer grammar (int / fraction / mc4 / free_text strings) is
UNCHANGED by this module -- modes only shape how the child's answer is
collected and packed into that same string.

Adding a new mode (e.g. mixed numbers "1 1/2"):
  1. Write a compose_<mode>(form) -> str function below.
  2. Add one AnswerMode(...) entry to ANSWER_MODES keyed by the verifier's
     answer_type string.
  3. Add one branch to _turn.html keyed on mode.widget.
That's the whole extension surface.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class AnswerMode:
    widget: str              # _turn.html branch key: "radio" | "fraction" | "number" | "decimal" | "text"
    show_format_hint: bool   # whether question_display's "(answer like ...)" hint is shown
    compose: Callable[[Mapping[str, str]], str]  # request.form -> the answer string for ctrl.step()


def _compose_default(form: Mapping[str, str]) -> str:
    return form.get("answer", "").strip()


def _compose_fraction(form: Mapping[str, str]) -> str:
    answer = _compose_default(form)
    if answer:
        return answer
    num = form.get("answer_num", "").strip()
    den = form.get("answer_den", "").strip()
    return f"{num}/{den}" if num and den else ""


ANSWER_MODES: dict[str, AnswerMode] = {
    "mc4": AnswerMode("radio", show_format_hint=False, compose=_compose_default),
    "fraction": AnswerMode("fraction", show_format_hint=True, compose=_compose_fraction),
    "int": AnswerMode("number", show_format_hint=True, compose=_compose_default),
    # R13: inputmode="decimal" (not "numeric") is deliberate -- "numeric" suppresses the
    # decimal-point key on some mobile keyboards, which would make a decimal question
    # unanswerable on a phone/tablet.
    "decimal": AnswerMode("decimal", show_format_hint=True, compose=_compose_default),
    "free_text": AnswerMode("text", show_format_hint=True, compose=_compose_default),
}
DEFAULT_MODE = ANSWER_MODES["free_text"]


def mode_for(answer_type: str | None) -> AnswerMode:
    """The AnswerMode for a verifier answer_type, or DEFAULT_MODE (plain text
    input) for an unknown/None type -- never raises, matches this app's
    graceful-degradation posture (an unrecognised type still gets a usable
    input, not a broken page)."""
    return ANSWER_MODES.get(answer_type or "", DEFAULT_MODE)
