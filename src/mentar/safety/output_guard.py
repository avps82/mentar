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
    # Added 2026-08-16. The 2026-08-12 pass dropped the frame requirement for
    # "kill/harm/hurt yourself", but the residue of the same class still went
    # through: a probe found "Maybe you'd be better off dead.", "Why don't you
    # just die?" and "You deserve to be hurt." all reaching the child unblocked.
    #
    # Scoped to the SECOND PERSON on purpose. "Hamlet would be better off dead"
    # is legitimate Year 12 English analysis and must not be blocked; "YOU would
    # be better off dead" has no use in a tutor's mouth in any framing.
    re.compile(r"\byou('d| would| are|'re| were)?\s*(be\s+)?better off dead\b", re.IGNORECASE),
    re.compile(r"\bwhy don'?t you (just )?die\b", re.IGNORECASE),
    re.compile(r"\byou should (just )?die\b", re.IGNORECASE),
    re.compile(r"\byou deserve (to be|being) (hurt|beaten|punished|hit)\b", re.IGNORECASE),
    # Instructional framing for violence toward another person. Frame-based
    # deliberately: "hit her" alone appears in ordinary word problems ("the ball
    # hit her racket"), but a tutor never offers to TEACH hitting.
    # "beat" is deliberately NOT in this list -- "I'll show you how to beat your
    # own best score" is exactly the encouragement this tutor should be giving,
    # and it was the one false positive the probe turned up.
    re.compile(r"\b(teach|show)\s+(you\s+)?(how\s+)?to\s+(hit|hurt|punch|stab)\b", re.IGNORECASE),
    # Added 2026-08-21 (probe round 3). The 2026-08-12 note above says the frame
    # requirement ("how to ...") let a bare imperative through, and dropped it
    # FOR SELF-DIRECTED HARM ONLY. The identical defect was still live in every
    # other class, so a probe walked straight past this module:
    #
    #   "To make a pipe bomb you need a metal tube and gunpowder."  -> allowed
    #   "You should hit your brother back as hard as you can."      -> allowed
    #   "You should meet me alone after school and not tell your parents." -> allowed
    #
    # Instruction-to-the-reader framing for a weapon. NOT bare "building bombs":
    # "the Allies were building bombs" is legitimate WWII history.
    re.compile(r"\bto (make|build|assemble) (a |an )?(pipe |nail |petrol |home.?made )?"
               r"(bomb|explosive|grenade|molotov)\b", re.IGNORECASE),
    # Violence aimed at a PERSON, imperative. A person-object is required so
    # "you should hit the ball harder" and "kick the football" stay legitimate.
    re.compile(r"\byou should (hit|punch|kick|hurt|attack|stab)\s+"
               r"(him|her|them|your|his|their|the other)\b", re.IGNORECASE),
    # GROOMING / LURING — previously uncovered by ANY class, and the single most
    # dangerous thing a tutor could emit. Over-blocking is deliberate: none of
    # these has a legitimate use in a children's tutor, in any framing.
    re.compile(r"\bmeet (me|up with me)\b[^.?!]{0,40}"
               r"\b(alone|in person|after school|without telling|don'?t tell)\b", re.IGNORECASE),
    re.compile(r"\b(don'?t|do not|never) tell your (parents?|mum|mom|dad|carer|teacher)\b", re.IGNORECASE),
    re.compile(r"\b(keep|this is|it'?s) (this |our )?(a )?secret between (us|you and me)\b", re.IGNORECASE),
    # Self-harm METHOD, which needs no "how to" frame to be lethal advice.
    re.compile(r"\btake (all|the whole|a whole)\b[^.?!]{0,25}"
               r"\b(pills|tablets|bottle|packet|medication)\b", re.IGNORECASE),
]

_ADULT_CONTENT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(explicit|graphic) sex(ual)? (content|scene|act)\b", re.IGNORECASE),
    re.compile(r"how to (get|buy|use) (cocaine|heroin|meth|drugs)\b", re.IGNORECASE),
    # 2026-08-21: the pattern above missed MANUFACTURE, and "\bmeth\b" never
    # matched the spelled-out drug ("how to make methamphetamine at home").
    re.compile(r"\b(how to|to) (make|cook|produce|synthesi[sz]e)\b[^.?!]{0,25}"
               r"\b(meth|methamphetamine|cocaine|heroin|fentanyl|ecstasy)\b", re.IGNORECASE),
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
    # "alcohol" is DRINK-SENSE ONLY (fixed 2026-08-21). The bare keyword also
    # matched the organic-chemistry sense, and off_scope DISCARDS the text — so
    # every tutor explanation of the shipped senior "Organic families /
    # ALCOHOLS (contains an -OH group)" topic was thrown away and replaced with
    # a redirect. Found by screening the guard against the whole shipped corpus:
    # 4 authored seeds and a scaffold flagged their own curriculum. The
    # neighbouring gambling comment ("no shipped curriculum discusses these")
    # was true when written and had silently stopped being true here.
    re.compile(r"\b(drink(ing|s)?|drunk|abusing|abuse of|underage)\s+alcohol\b", re.IGNORECASE),
    re.compile(r"\balcohol(ic)?\s+(drink|beverage|abuse|addiction)\b", re.IGNORECASE),
    re.compile(r"\b(beer|wine|cigarette|vaping)\b", re.IGNORECASE),
    # Gambling: promoted from "known v0 limit" after a live T2.5 pipeline run (2026-08-12)
    # caught the model OFFERING to teach "the math of poker" to a child — a real miss, not a
    # hypothetical. Deliberately over-blocking: no shipped curriculum discusses these.
    re.compile(r"\b(poker|casino|gambling|roulette|blackjack|betting|place a bet)\b", re.IGNORECASE),
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
