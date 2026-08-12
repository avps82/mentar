"""Handoff-wording validation harness (W2.2 §6.2; SAFETY.md §3.4).

Machine-checkable invariants for the fixed handoff messages (`HANDOFF_MESSAGE_*`
in :mod:`mentar.safety.escalation`). They encode the design-doc properties:

  * routes the child to the **physically-present adult** (the pilot escalation target),
  * **no emergency-services signposting** — the §6.1 interim decision routes to the
    parent, NOT to crisis numbers/helplines shown to the child,
  * non-alarming + no clinical jargon (age-appropriate),
  * no first-person AI promise to resolve a safety matter (the tutor hands off, it
    does not claim to fix it),
  * bounded length + literal text (never LLM-templated).

IMPORTANT — this harness does NOT replace human safeguarding sign-off. That
sign-off is SOUGHT PRO-BONO (an unfunded OSS project cannot commission it; see
SAFETY.md §3.5.1) and gates UNSUPERVISED mode, not the supervised single-family
pilot. Passing here is necessary, not sufficient (W2.2 §6.2; SAFETY.md §3.4).
"""

from __future__ import annotations

import re

MAX_LEN = 240  # child-appropriate brevity

_ADULT_TERMS = ("grown-up", "grown up", "grownup", "parent", "carer", "guardian")

# Emergency/crisis signposting the pilot must NOT surface to the child (design §6.1).
_EMERGENCY_TERMS = (
    "999", "911", "112", "emergency", "police", "ambulance", "hospital",
    "hotline", "helpline", "crisis line", "suicide", "self-harm", "self harm",
)

_ALARMING_TERMS = ("danger", "warning", "alert", "urgent", "scary")

_CLINICAL_TERMS = ("therap", "diagnos", "medication", "medicine", "clinical", "symptom")

# First-person AI promise to resolve the issue ("I'll/I will/I can ... help/fix/solve").
# The tutor must hand off to the adult, not promise to sort a safety matter itself.
_AI_PROMISE_RE = re.compile(r"\bi(?:'ll| will| can)\b[^.]*\b(help|fix|solve|sort)\b", re.IGNORECASE)


def validate_handoff_message(message: str) -> list[str]:
    """Return a list of criterion violations for *message* (empty list = passes)."""
    text = (message or "").strip()
    if not text:
        return ["empty message"]

    low = text.lower()
    failures: list[str] = []

    if len(text) > MAX_LEN:
        failures.append(f"too long ({len(text)} > {MAX_LEN} chars)")
    if "{{" in text or "}}" in text:
        failures.append("contains a template placeholder (must be literal text)")
    if not any(t in low for t in _ADULT_TERMS):
        failures.append("does not route the child to a present adult")
    failures += [
        f"contains emergency-signposting term '{t}' (pilot routes to the parent)"
        for t in _EMERGENCY_TERMS if t in low
    ]
    failures += [f"contains alarming term '{t}'" for t in _ALARMING_TERMS if t in low]
    failures += [f"contains clinical term '{t}'" for t in _CLINICAL_TERMS if t in low]
    if _AI_PROMISE_RE.search(text):
        failures.append("contains a first-person AI promise to resolve the issue")
    return failures


def validate_frozen_messages() -> dict[str, list[str]]:
    """Validate the live `HANDOFF_MESSAGE_*` constants; {name: violations}."""
    from mentar.safety.escalation import HANDOFF_MESSAGE_PRIMARY, HANDOFF_MESSAGE_SUPPORT

    return {
        "HANDOFF_MESSAGE_PRIMARY": validate_handoff_message(HANDOFF_MESSAGE_PRIMARY),
        "HANDOFF_MESSAGE_SUPPORT": validate_handoff_message(HANDOFF_MESSAGE_SUPPORT),
    }
