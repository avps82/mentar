"""Child-safety escalation classifier.

Spec: docs/SAFETY.md Layer 3 (§3.1–§3.5); docs/design/W2.2_escalation.md §2–§4.
Tests: tests/safety/test_escalation.py (T2.1) — 20 positive + 20 negative fixtures.

This module is PURE: no DB writes, no FSM transitions, no LLM calls. The caller
(session loop / FSM driver) is responsible for logging, freeze, and handoff once
`classify()` returns a non-None match. See design §4 and `handle_trigger()` below
for the thin caller-side helper that demonstrates the end-to-end flow.

Two open rollout guards (W2.2 design §7 / SAFETY.md §3.5 — do not lose):
  1. Handoff wording (HANDOFF_MESSAGE_PRIMARY/SUPPORT) has NOT been reviewed by a
     safeguarding professional or child-communication specialist. Professional review
     is REQUIRED before any rollout beyond the supervised single-family Phase-0 pilot.
  2. Emergency-services signposting is explicitly absent (pilot routes to physically-
     present parent). This FAILS when the parent is the source of harm (physical_danger /
     abuse_disclosure cases). Crisis-helpline signposting with safeguarding input is
     REQUIRED before unsupervised/independent mode is enabled.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from enum import Enum

# ─────────────────────────────────────────────────────────────────────────────
# Public API types  (design §3)
# ─────────────────────────────────────────────────────────────────────────────

class TriggerClass(str, Enum):
    HARM_TO_SELF          = "harm_to_self"
    PHYSICAL_DANGER       = "physical_danger"
    SEVERE_DISTRESS       = "severe_distress"
    ABUSE_DISCLOSURE      = "abuse_disclosure"
    SECRECY_REQUEST       = "secrecy_request"
    ADVERSARIAL_JAILBREAK = "adversarial_jailbreak"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    LOW      = "low"


@dataclass(frozen=True)
class TriggerMatch:
    trigger_class: TriggerClass
    severity: Severity
    matched_span: str  # the substring that fired (for log/debug — NOT the alert)
    # NB: the FULL verbatim input is logged separately and never truncated.


# ─────────────────────────────────────────────────────────────────────────────
# Fixed handoff messages — VERBATIM from SAFETY.md §3.4
# These are NEVER passed through the LLM.  (design §3, §4 Step 3)
# ─────────────────────────────────────────────────────────────────────────────

HANDOFF_MESSAGE_PRIMARY: str = (
    "This is something to talk about with your grown-up. "
    "Let's pause our lesson here."
)

HANDOFF_MESSAGE_SUPPORT: str = (
    "Your grown-up can help you with this. "
    "Your lesson will be here when you're ready to come back."
)


# ─────────────────────────────────────────────────────────────────────────────
# Per-class keyword/regex banks (design §3 — module-level so Bucket D can
# swap them wholesale).
#
# Matching philosophy (design §3 classifier rules):
#   • Case-insensitive, compiled once.
#   • Sensitivity-biased: false positives are acceptable; false negatives are not.
#   • Word-boundary-aware where it prevents obvious trust-eroding false positives
#     (e.g. "die" in "diet"/"died in the game") — any exception is documented.
#   • Substring match otherwise (no boundary needed where context is unambiguous).
#
# Word-boundary approach: \b is used around short ambiguous roots (die/hurt/kill).
# Longer phrases and full self-harm expressions are matched as substrings because
# the phrase itself is unambiguous in any surrounding context.
# ─────────────────────────────────────────────────────────────────────────────

# ── A: harm_to_self (CRITICAL) ───────────────────────────────────────────────
# Patterns covering suicidal ideation and self-harm intent.
# "die" is word-boundary protected: "die" alone triggers but "diet"/"died" do not.
# "hurt myself" / "harm myself" are phrase-matched (no boundary needed).
# "don't want to be here anymore" and "no reason to live" catch indirect ideation.
_HARM_TO_SELF_PATTERNS: list[re.Pattern[str]] = [p for p in (
    re.compile(r"i want to (die|kill myself|end my life|hurt myself|harm myself)", re.I),
    re.compile(r"i('m going| am going| want) to (hurt|harm|kill) myself", re.I),
    re.compile(r"i('m| am) going to (hurt|harm|kill) myself", re.I),
    re.compile(r"(hurt|harm|kill) myself", re.I),
    re.compile(r"want to (end|take) my (life|own life)", re.I),
    re.compile(r"no reason to (live|go on|be alive)", re.I),
    # "I don't want to be here anymore" — indirect self-harm ideation
    re.compile(r"(don'?t|do not) want to be here (anymore|any more)", re.I),
    # standalone "want to die" — word-boundary on "die" avoids "died"/"dies"
    # but we use phrase match since "want to die" is unambiguous
    re.compile(r"want to die", re.I),
    # bare "i want to die" also caught above; "i might as well die" etc.
    re.compile(r"\bi might as well (die|be dead)\b", re.I),
    # "I'm thinking about ending it all" — indirect
    re.compile(r"thinking (about|of) (ending|killing) (it|myself|my life)", re.I),
    # "I've been cutting myself" / "I cut myself on purpose"
    re.compile(r"(cutting|cut) myself (on purpose|to hurt|because)", re.I),
)]

# ── A: physical_danger (CRITICAL) ────────────────────────────────────────────
# Patterns for immediate physical danger / abuse by another person.
# "hurt me" is phrase-matched; "hit me" similarly.
_PHYSICAL_DANGER_PATTERNS: list[re.Pattern[str]] = [p for p in (
    re.compile(r"someone (is|has been|keeps|was) (hurting|hitting|beating|abusing|punching|kicking) me", re.I),
    re.compile(r"(he|she|they|he's|she's) (hurt|hit|beat|kicked|punched|abused) me", re.I),
    re.compile(r"(i am|i'?m) (being|getting) (hurt|hit|beaten|abused|punched|kicked)", re.I),
    re.compile(r"(don'?t feel|don'?t feel) safe (at home|in my house|at school|here)", re.I),
    re.compile(r"(i'?m|i am) not safe", re.I),
    re.compile(r"not safe at home", re.I),
    re.compile(r"(someone|a person|grown.?up|adult|man|woman|he|she|they) (hurts|hits|beats|kicks|punches) me", re.I),
    re.compile(r"(my|our) (dad|mum|mom|stepdad|stepmom|uncle|aunt|teacher|brother|sister|carer|guardian) (hurts|hits|beats|abuses|punches|kicks) me", re.I),
    re.compile(r"being (physically )?abused", re.I),
    # "I'm in danger" / "I'm scared someone will hurt me"
    re.compile(r"(i'?m|i am) in danger", re.I),
    re.compile(r"scared (that )?(someone|he|she|they) will (hurt|hit|kill|harm) me", re.I),
)]

# ── B: severe_distress (HIGH) ────────────────────────────────────────────────
# Patterns for severe emotional/welfare distress beyond normal frustration.
# Calibration note (design §5): "I'm a bit sad today" is documented as BELOW
# threshold in v0.1 (see negative fixtures). We require explicit despair/
# hopelessness words, not mild mood reports.
# "dying of boredom" / "killing me" in game/school context → NOT fired (see negatives).
_SEVERE_DISTRESS_PATTERNS: list[re.Pattern[str]] = [p for p in (
    re.compile(r"(everything|nothing|life) (is|feels?) (hopeless|pointless|meaningless|worthless|terrible|awful)", re.I),
    re.compile(r"i('?ve| have) been (crying|sobbing) (all|every|for) (day|night|week|hours?)", re.I),
    re.compile(r"(i feel|i'?m feeling) (completely )?(hopeless|worthless|empty|broken|destroyed|devastated)", re.I),
    re.compile(r"nobody (loves?|cares? about|wants) me", re.I),
    re.compile(r"(i hate|i can'?t stand) (my life|myself|being alive|living)", re.I),
    re.compile(r"(can'?t|cannot) (cope|go on|take (it|this|anymore)|keep going)", re.I),
    re.compile(r"(every ?thing|my whole life) is (falling apart|ruined|over|destroyed)", re.I),
    # persistent despair markers
    re.compile(r"(always|never) (feel|felt|going to) (better|happy|good|okay|ok)\b", re.I),
    re.compile(r"(too much|no point) (to|in) (living|life|going on|continuing)", re.I),
)]

# ── C: abuse_disclosure (CRITICAL) ───────────────────────────────────────────
# Patterns for grooming, sexual abuse, exploitation disclosures.
# "touched" used in abuse context; "private parts" / "private areas" etc.
_ABUSE_DISCLOSURE_PATTERNS: list[re.Pattern[str]] = [p for p in (
    re.compile(r"(touched|touches|touching) (my|our) (private|body|bits|parts?|area)", re.I),
    re.compile(r"someone (touched|is touching|has touched|touched me) in (a )?wrong (way|place)", re.I),
    re.compile(r"(sexual|inappropriate|rude|dirty) (touch|touching|things?|photos?|pictures?|videos?)", re.I),
    re.compile(r"(show(ing|n)?|send(ing)?|sent|shar(e|ing)) (me )?(naked|nude|rude|sexual|private) (photos?|pictures?|videos?|images?)", re.I),
    re.compile(r"(ask(ing|ed)? me to) (take off|remove) (my |their )?(clothes|clothing|shirt|top)", re.I),
    re.compile(r"(adult|grown.?up|man|woman|teacher|coach|uncle|neighbour|neighbor|stranger|person|he|she|they) (want(s|ed)? (to )?(touch|see|have|do))", re.I),
    # Grooming patterns: gifts, special relationship, "our secret"
    re.compile(r"(he|she|they|it) (is|was) (being|getting) (really )?(special|nice|friendly|close) (to me|with me) but", re.I),
    re.compile(r"(sexual|sexually) (abused?|assault(ed)?|exploit(ed)?|harass(ed)?)", re.I),
    re.compile(r"abuse(d)? (me|my body|sexually)", re.I),
    # Euphemistic disclosures — simplified to catch the span that matters
    re.compile(r"(a grown.?up|an adult|someone older) (did|does|made|makes) (something|things?) (to me|with me)", re.I),
    re.compile(r"(he|she|they) (made|make|asked|ask|told|tell) me (to )?(do|touch|show) (something|things?|myself|them)", re.I),
)]

# ── C: secrecy_request (HIGH) ────────────────────────────────────────────────
# Patterns where the child tries to enlist the AI in keeping secrets from parents.
# Also covers disclosure that another adult has demanded secrecy.
_SECRECY_REQUEST_PATTERNS: list[re.Pattern[str]] = [p for p in (
    re.compile(r"(don'?t|do not|please don'?t) (tell|let|show) (my )?(mum|mom|mummy|mommy|dad|daddy|father|mother|parent|carer|guardian|teacher|anyone|grown.?up)", re.I),
    re.compile(r"(keep|kept) (this |it )?(a )?secret (from|between)", re.I),
    re.compile(r"(it'?s|this is) (just )?our secret", re.I),
    re.compile(r"(promise|swear) (me )?(you )?(won'?t|never|not) tell", re.I),
    re.compile(r"(he|she|they) (told|said|told me|says) (not to|to never|to not) tell (anyone|anyone|my mum|my mom|my dad|my parent)", re.I),
    re.compile(r"(told|said|asked) me (not|never) to (say|tell|talk about) (anything|this|it)", re.I),
    re.compile(r"(nobody|no one|don'?t let anyone) (must|should|can) know (about this|about it)", re.I),
)]

# ── D: adversarial_jailbreak (LOW) ───────────────────────────────────────────
# Patterns for jailbreak / safety-override attempts (Layer 1 §1.4 already blocks
# inline; this class ensures they reach the escalation log for audit).
_ADVERSARIAL_JAILBREAK_PATTERNS: list[re.Pattern[str]] = [p for p in (
    re.compile(r"(ignore|disregard|forget|bypass|override) (your |all )?(previous |your |the )?(instructions?|rules?|guidelines?|safety|system prompt|restrictions?)", re.I),
    re.compile(r"(pretend|act|behave|imagine) (like |as if )?(you (are|have) no |you don'?t have |you'?re |you are )(a different|rules?|restrictions?|guidelines?|an? (uncensored|unrestricted|free|evil|jailbroken))", re.I),
    re.compile(r"(you are now|you'?re now|from now on (you are|you'?re|act as)) (a |an )?(?!a tutor|helping|assisting)", re.I),
    re.compile(r"(jailbreak|dan mode|developer mode|god mode|unrestricted mode)", re.I),
    re.compile(r"(your new (instructions?|rules?|system prompt)|new system prompt)", re.I),
    re.compile(r"(pretend you have no rules|pretend you'?re a different ai|pretend (there are|you have) no (rules|restrictions|limits?))", re.I),
    re.compile(r"(do anything now|say anything|no (rules|limits?|restrictions?))\b", re.I),
)]


# ─────────────────────────────────────────────────────────────────────────────
# Severity + ordering table  (design §2 — precedence: A > B > C > D)
# ─────────────────────────────────────────────────────────────────────────────

# List of (TriggerClass, Severity, patterns) in descending priority order.
# For ties in severity, the order here decides (A critical > A critical again,
# then B high > C high; D low is last).
_CLASSIFIER_BANKS: list[tuple[TriggerClass, Severity, list[re.Pattern[str]]]] = [
    (TriggerClass.HARM_TO_SELF,          Severity.CRITICAL, _HARM_TO_SELF_PATTERNS),
    (TriggerClass.PHYSICAL_DANGER,        Severity.CRITICAL, _PHYSICAL_DANGER_PATTERNS),
    (TriggerClass.ABUSE_DISCLOSURE,       Severity.CRITICAL, _ABUSE_DISCLOSURE_PATTERNS),
    (TriggerClass.SEVERE_DISTRESS,        Severity.HIGH,     _SEVERE_DISTRESS_PATTERNS),
    (TriggerClass.SECRECY_REQUEST,        Severity.HIGH,     _SECRECY_REQUEST_PATTERNS),
    (TriggerClass.ADVERSARIAL_JAILBREAK,  Severity.LOW,      _ADVERSARIAL_JAILBREAK_PATTERNS),
]

# Severity rank for precedence comparison (higher = higher priority).
_SEVERITY_RANK: dict[Severity, int] = {
    Severity.CRITICAL: 3,
    Severity.HIGH:     2,
    Severity.LOW:      1,
}


# ─────────────────────────────────────────────────────────────────────────────
# Classifier (design §3)
# ─────────────────────────────────────────────────────────────────────────────

def classify(text: str) -> TriggerMatch | None:
    """Single-turn classifier. Returns the HIGHEST-severity match, or None.

    Sensitivity-biased: when in doubt, fire. False positives are acceptable and
    expected (SAFETY.md §3.2); false negatives are not.

    Precedence on multiple matches: highest Severity wins; ties broken by the
    category order A > B > C > D (i.e., the order in _CLASSIFIER_BANKS).
    The list is already sorted in descending priority so the first higher-or-
    equal severity match found in a linear scan is returned.
    """
    if not text or not text.strip():
        return None

    best: TriggerMatch | None = None

    for trigger_class, severity, patterns in _CLASSIFIER_BANKS:
        # Early exit: nothing can beat a CRITICAL already found, and the banks
        # are ordered so subsequent banks are equal-or-lower severity.
        if best is not None and _SEVERITY_RANK[severity] < _SEVERITY_RANK[best.severity]:
            break

        for pattern in patterns:
            m = pattern.search(text)
            if m:
                candidate = TriggerMatch(
                    trigger_class=trigger_class,
                    severity=severity,
                    matched_span=m.group(0),
                )
                if best is None or _SEVERITY_RANK[severity] > _SEVERITY_RANK[best.severity]:
                    best = candidate
                break  # one match per class is sufficient; move to next class

    return best


# ─────────────────────────────────────────────────────────────────────────────
# Thin caller helper — demonstrates the §4 flow end-to-end
# (classify stays pure/separate; this is the caller side)
# ─────────────────────────────────────────────────────────────────────────────

def handle_trigger(
    text: str,
    learner_id: int,
    conn: sqlite3.Connection,
) -> TriggerMatch | None:
    """Run the §4 flow for one child turn against a live SQLite connection.

    Returns the TriggerMatch if triggered (caller should enter ESCALATION_FREEZE
    for all classes except adversarial_jailbreak per §4.3), or None if no match.

    Steps performed (design §4):
      1. classify() — pure; no side effects.
      2. LOG — insert escalation_log row with full untruncated verbatim text.
         For adversarial_jailbreak: session_outcome='logged_only' (design §4.3).
         For all others: session_outcome='frozen'.
      3. HANDOFF — render HANDOFF_MESSAGE_PRIMARY + _SUPPORT (returned in log
         row comment; caller is responsible for display).
      4. ALERT — on-screen flag + log row (pilot: log row already written above;
         alert carries trigger_class only, NOT verbatim text per §4 Step 4).
      FREEZE + WAIT + RESUMPTION GATE are FSM responsibilities (not this helper).

    Note: adversarial_jailbreak is logged_only — do NOT enter ESCALATION_FREEZE.
    """
    match = classify(text)
    if match is None:
        return None

    # §4.3 — adversarial_jailbreak is logged-only, not frozen
    if match.trigger_class == TriggerClass.ADVERSARIAL_JAILBREAK:
        session_outcome = "logged_only"
    else:
        session_outcome = "frozen"

    # §4 Step 2 — LOG: full verbatim text, never truncated
    conn.execute(
        """
        INSERT INTO escalation_log
            (learner_id, trigger_class, trigger_text_verbatim, session_outcome)
        VALUES (?, ?, ?, ?)
        """,
        (learner_id, match.trigger_class.value, text, session_outcome),
    )
    conn.commit()

    # §4 Step 3 — HANDOFF (caller renders these; we return the match so caller knows)
    # §4 Step 4 — ALERT: the log row IS the pilot alert (on-screen flag in parent view)
    #             The alert surfaces trigger_class + timestamp ONLY — never verbatim text.

    return match
