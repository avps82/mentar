"""Output-side safety gate — screen LLM output before it reaches the child.

Spec: docs/SAFETY.md Layer 2 (§2.1 hard content blocks, §2.2 curriculum scope).
Tests: tests/safety/test_output_guard.py

This module is PURE: no DB writes, no FSM transitions. The caller
(`SessionController._make_safe_llm`) is responsible for discarding blocked output,
writing the incident, and serving a neutral redirect — see `screen_output()` below.

v0 scope (deliberately minimal — Bucket E replaces this with a stronger
classifier post-pilot, see SAFETY §2.1/§2.2):
  - Hard content blocks: sexual content involving minors, violent/self-harm
    instructions, adult/drug content. These are absolute (SAFETY §2.1) — the
    highest-priority check, run first.
  - Curriculum scope: a light keyword heuristic flagging output that talks
    about something other than the active subject when it also contains a
    clearly off-topic-for-a-child-tutor marker (e.g. politics, alcohol/drugs
    framed as a topic, dating/relationship advice). This is NOT a full topic
    classifier — see the ceiling note on `_OFF_TOPIC_PATTERNS` below.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class BlockClass(str, Enum):
    SEXUAL_CONTENT_MINORS = "sexual_content_minors"
    VIOLENT_OR_HARMFUL    = "violent_or_harmful"
    ADULT_CONTENT         = "adult_content"
    OFF_SCOPE             = "off_scope"


# Hard blocks (§2.1) are the highest-severity audit rows; scope drift (§2.2) is data-only.
SEVERITY_BY_CLASS: dict[BlockClass, str] = {
    BlockClass.SEXUAL_CONTENT_MINORS: "critical",
    BlockClass.VIOLENT_OR_HARMFUL: "critical",
    BlockClass.ADULT_CONTENT: "critical",
    BlockClass.OFF_SCOPE: "low",
}

# Fixed string shown to the child in place of any discarded output — no LLM
# generation involved, mirrors the escalation HANDOFF_MESSAGE pattern (SAFETY §2.1).
NEUTRAL_REDIRECT = "Let's try that a different way — here's your question again."


@dataclass(frozen=True)
class OutputIncident:
    block_class: BlockClass
    matched_span: str  # first ~80 chars of the matching text, for audit — not full output


# ─────────────────────────────────────────────────────────────────────────────
# §2.1 — Hard content blocks (absolute, no exceptions)
# ─────────────────────────────────────────────────────────────────────────────

_SEXUAL_CONTENT_MINORS_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bchild(ren)?\b.{0,30}\b(sex|sexual|naked|nude)\b", re.IGNORECASE),
    re.compile(r"\b(sex|sexual)\b.{0,30}\b(minor|child|kid)s?\b", re.IGNORECASE),
]

_VIOLENT_OR_HARMFUL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"how to (make|build) a (bomb|weapon|explosive)", re.IGNORECASE),
    re.compile(r"how to (kill|hurt|harm) (yourself|myself|someone)", re.IGNORECASE),
    re.compile(r"\b(cut|cutting) yourself\b", re.IGNORECASE),
    re.compile(r"step[s]? to (suicide|self-harm)", re.IGNORECASE),
    # Added 2026-08-12. Every pattern above required a specific FRAME -- "how
    # to ...", "steps to ..." -- so a bare imperative went straight through:
    # "You should kill yourself." was NOT blocked. That is a false negative in
    # the class this module calls absolute and highest-priority, so the frame
    # requirement is dropped for self-directed harm.
    #
    # Deliberately over-blocking: a children's maths tutor has no legitimate
    # reason to emit these strings in ANY framing, including a well-meant
    # "don't hurt yourself". The consequence of a block is a neutral redirect,
    # which is always a safe thing to say; the consequence of a miss is not.
    re.compile(r"\b(kill|harm|hurt)\s+(yourself|yourselves)\b", re.IGNORECASE),
    re.compile(r"\bend (your|ur) (own )?life\b", re.IGNORECASE),
    re.compile(r"\btake your own life\b", re.IGNORECASE),
    re.compile(r"\bkill (him|her|them|someone)\b", re.IGNORECASE),
]

_ADULT_CONTENT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(explicit|graphic) sex(ual)? (content|scene|act)\b", re.IGNORECASE),
    re.compile(r"how to (get|buy|use) (cocaine|heroin|meth|drugs)\b", re.IGNORECASE),
]

_HARD_BLOCKS: list[tuple[BlockClass, list[re.Pattern[str]]]] = [
    (BlockClass.SEXUAL_CONTENT_MINORS, _SEXUAL_CONTENT_MINORS_PATTERNS),
    (BlockClass.VIOLENT_OR_HARMFUL, _VIOLENT_OR_HARMFUL_PATTERNS),
    (BlockClass.ADULT_CONTENT, _ADULT_CONTENT_PATTERNS),
]

# ─────────────────────────────────────────────────────────────────────────────
# §2.2 — Curriculum scope heuristic
#
# ponytail: this is a keyword deny-list, not a topic classifier — it catches
# obviously off-scope content (the response has drifted to an adult/unrelated
# subject entirely), not subtle off-topic drift within a plausible-sounding
# educational register. Upgrade to an LLM-judge or embedding-similarity check
# if false negatives show up in eval (Bucket E).
# ─────────────────────────────────────────────────────────────────────────────

_OFF_TOPIC_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(election|politic(s|ian)?|vote for)\b", re.IGNORECASE),
    re.compile(r"\b(dating|boyfriend|girlfriend) advice\b", re.IGNORECASE),
    re.compile(r"\b(alcohol|beer|wine|cigarette|vaping)\b", re.IGNORECASE),
]


def screen_output(
    text: str, subject_scope: str | None = None
) -> tuple[str | None, OutputIncident | None]:
    """Screen one piece of LLM output before it reaches the child.

    Returns (text, None) unchanged when clean (byte-identical — the common case).
    Returns (None, incident) when blocked — caller discards the text, logs the
    incident, and serves a neutral redirect instead.

    subject_scope is reserved for a future per-subject allow-list; v0's scope
    check is a fixed off-topic deny-list regardless of subject.
    """
    if not text:
        return text, None

    for block_class, patterns in _HARD_BLOCKS:
        for pattern in patterns:
            m = pattern.search(text)
            if m:
                return None, OutputIncident(block_class=block_class, matched_span=m.group(0)[:80])

    for pattern in _OFF_TOPIC_PATTERNS:
        m = pattern.search(text)
        if m:
            return None, OutputIncident(block_class=BlockClass.OFF_SCOPE, matched_span=m.group(0)[:80])

    return text, None
