"""Child-safety escalation classifier.

Spec: docs/SAFETY.md Layer 3 (§3.1–§3.5); docs/design/W2.2_escalation.md §2–§4.
Tests: tests/safety/test_escalation.py (T2.1) — 20 positive + 20 negative fixtures.

This module is PURE: no DB writes, no FSM transitions, no LLM calls. The caller
(session loop / FSM driver) is responsible for logging, freeze, and handoff once
`classify()` returns a non-None match. The real (only, since A3) caller is
`SessionController._step_core` in dialogue/controller.py, which logs via
`LearnerStore.write_escalation` — see design §4 for the flow: classify (here) ->
LOG (write_escalation, full untruncated verbatim text; adversarial_jailbreak =
'logged_only', all others = 'frozen') -> HANDOFF (HANDOFF_MESSAGE_PRIMARY/SUPPORT
below) -> FREEZE + WAIT + RESUMPTION GATE (FSM responsibilities, not this module).

Two open rollout guards (W2.2 design §7 / SAFETY.md §3.5 — do not lose):
  1. Handoff wording (HANDOFF_MESSAGE_PRIMARY/SUPPORT) has NOT been reviewed by a
     safeguarding professional. Such review is SOUGHT PRO-BONO (unfunded OSS; SAFETY.md
     §3.5.1) and gates UNSUPERVISED mode, not the supervised single-family pilot.
  2. Emergency-services signposting is explicitly absent (pilot routes to physically-
     present parent). This FAILS when the parent is the source of harm (physical_danger /
     abuse_disclosure cases). Crisis-helpline signposting with safeguarding input is
     REQUIRED before unsupervised/independent mode is enabled.
"""

from __future__ import annotations

import base64
import re
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
    # Passive ideation (added 2026-08-12). A probe of realistic phrasings found
    # these missed entirely, which contradicts this module's own sensitivity-biased
    # contract -- passive ideation is a recognised risk indicator, not a milder
    # version of the direct statements above. Deliberately narrow so the existing
    # negative fixture "I miss my friend, she moved to another school" stays silent:
    # the subject must be nobody/everyone, not "I".
    re.compile(r"\b(nobody|no ?one|not one person)\s+(would|will|'?d)\s+(miss|care about|notice|even notice)\s+me\b", re.I),
    re.compile(r"\b(everyone|everybody|they all|my family)\s+(would|will|'?d)\s+be\s+better\s+off\s+without\s+me\b", re.I),
    re.compile(r"\bi\s+wish\s+i\s+(wasn'?t|was not|weren'?t|had never been)\s+(alive|here|born)\b", re.I),
    # "I'm thinking about ending it all" — indirect
    re.compile(r"thinking (about|of) (ending|killing) (it|myself|my life)", re.I),
    # "I've been cutting myself" / "I cut myself on purpose"
    re.compile(r"(cutting|cut) myself (on purpose|to hurt|because)", re.I),
    # Deliberate eating-related self-harm (2026-08-12 safeguarding review). SAFETY §3.2 Cat A.
    re.compile(r"\bmake myself (sick|throw up|vomit)\b", re.I),
    re.compile(r"\bhaven'?t eaten (for|in) [^.?!]{0,20}\bon purpose\b", re.I),
    re.compile(r"\b(refuse|refusing) to eat\b[^.?!]{0,20}\bon purpose\b", re.I),
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
    # Dangerous situation / peer violence / witnessing DV / neglect / running away (2026-08-12 safeguarding review). SAFETY §3.2 Cat A stated scope; over-block by design.
    re.compile(r"\b(kids?|boys?|girls?|children|they|everyone) (at|in) (school|class)\b[^.?!]{0,40}\b(hit|hurt|beat|kick|punch)(s|ing|ed)? me\b", re.I),
    re.compile(r"\b(a |the )?(kid|boy|girl)\b[^.?!]{0,30}\bkeeps? (hitting|hurting|beating|kicking|punching) me\b", re.I),
    re.compile(r"\b(they|he|she) (said|says) (they|he|she)('| wi)ll (beat|hurt|hit|kill) me\b", re.I),
    re.compile(r"\bscared to go to school\b", re.I),
    re.compile(r"\b(dad|daddy|father|mum|mummy|mom|mother|step ?\w*|he|she|they)\b[^.?!]{0,25}\b(hits?|hitting|beats?|beating|pushed|pushes|hurts?|hurting|threw|throws)\b[^.?!]{0,25}\b(my |the )?(dad|daddy|father|mum|mummy|mom|mother|each other)\b", re.I),  # t7.3-exempt: regex alternation, not a prompt
    re.compile(r"\bmy parents (fight|are fighting|throw things|scream|hit each other)\b", re.I),
    re.compile(r"\bi hide\b[^.?!]{0,40}\b(shouts?|shouting|screams?|screaming|fights?|fighting|angry|drunk)\b", re.I),
    re.compile(r"\bno food (in the house|at home)\b", re.I),
    re.compile(r"\bhaven'?t eaten since (yesterday|this morning|last night)\b", re.I),
    re.compile(r"\b(nobody|no ?one)('s| has| is)? (been )?(home|here) (for|since|in) \w{1,8} (days?|nights?|weeks?)\b", re.I),
    re.compile(r"\b(look after|looking after|take care of)\b[^.?!]{0,30}\b(baby|little|younger)\b[^.?!]{0,30}\b(scared|frightened|alone|by myself|on my own)\b", re.I),
    re.compile(r"\bcan'?t wake (my |her |him |them )*(mum|mom|mummy|dad|daddy|mother|father)\b", re.I),
    re.compile(r"\bneedles? in (the|our|my) house\b", re.I),
    re.compile(r"\b(drinks|drunk|drinking) until (she|he|they) (falls?|fell|pass(es)?|passed) (asleep|out)\b", re.I),
    re.compile(r"\b(i'?m|i am) (going to|gonna) run away\b", re.I),
    re.compile(r"\bran away from home\b", re.I),
    re.compile(r"\bslept (rough|in the street|on a bench|in a doorway)\b", re.I),
    re.compile(r"\bslept outside\b(?![^.?!]{0,20}\b(tent|camping|camp|sleepover|garden|star)\b)[^.?!]{0,20}\b(because|couldn'?t|had to|scared|cold|alone)\b", re.I),
    re.compile(r"\bcouldn'?t go home\b", re.I),
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
    # "I never feel better" / "I'll never be happy" -- despair. Deliberately NOT
    # "always feel better" (a positive; a pre-2026-08-12 cut fired on "I always
    # feel better after a nap"). "always" only pairs with a NEGATIVE state word.
    re.compile(r"\bnever (feel|felt|going to feel|be|going to be) (better|happy|good|okay|ok|alright)\b", re.I),
    re.compile(r"\balways (feel|felt) (worse|sad|awful|terrible|empty|alone|like this)\b", re.I),
    re.compile(r"(too much|no point) (to|in) (living|life|going on|continuing)", re.I),
    # Emotional / psychological abuse BY someone (2026-08-12 safeguarding review). SAFETY §3.2 Cat B; repeated/severe element required so ordinary meanness stays below threshold.
    re.compile(r"\b(says?|tells? me|calls? me)\b[^.?!]{0,20}\b(worthless|useless|stupid|pathetic|a mistake)\b[^.?!]{0,20}\b(every ?day|all the time|always)\b", re.I),
    re.compile(r"\b(every ?day|all the time|always)\b[^.?!]{0,20}\b(says?|tells? me|calls? me)\b[^.?!]{0,20}\b(worthless|useless|stupid|pathetic)\b", re.I),
    re.compile(r"\bwish(es)? (i|you) (was|were|had) never born\b", re.I),
    re.compile(r"\block(s|ed)? me in (my room|the (house|basement|cupboard|closet))\b", re.I),
    re.compile(r"\bget called names at home\b", re.I),
    re.compile(r"\bnot allowed to (eat|leave|come out|see anyone)\b", re.I),
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
    # Added 2026-08-12 after a probe found the plainest disclosures missed:
    # "my uncle touches me" matched nothing, because every existing touch pattern
    # required a body-part word, "in a wrong way", or "wants to touch". A child
    # disclosing rarely qualifies the sentence. Requires a PERSON subject so that
    # emotional uses ("the story touched me") do not fire.
    # Matches "<person> touches ME" only -- never "touches MY <thing>". A first cut
    # allowed "me|my" and fired on "the man touches my stuff"; requiring the bare
    # object also makes it safe to include immediate family, who are statistically
    # the likeliest subjects of a real disclosure and were missing as a result.
    # "touches my private parts / body / area" is already covered above.
    re.compile(
        r"\b(my |a |an |the )?"  # t7.3-exempt: regex alternation, not a prompt
        r"(uncle|aunt|cousin|coach|teacher|neighbou?r|stranger|babysitter|"
        r"step-?\s?(dad|father|mum|mom|mother|brother|sister)|"
        r"dad|daddy|father|mum|mummy|mom|mother|brother|sister|grandad|grandpa|granddad|"
        r"man|woman|boy|girl|grown.?up|adult|someone|somebody|he|she|they)\s+"
        r"(touch(es|ed)?|is touching|keeps touching|kept touching)\s+me\b",
        re.I,
    ),
    # Grooming: a request for images. The existing pattern required an explicit
    # qualifier ("naked/rude photos"); a real disclosure is usually just "asked me
    # for photos". Parent-routed, so a false positive costs a parent conversation.
    re.compile(
        r"\b(ask(s|ed)?|want(s|ed)?|told|keeps asking)\s+me\s+"
        r"(to\s+send\s+|to\s+take\s+|for\s+)"
        r"(him|her|them)?\s*(a\s+|some\s+)?(photo|photos|picture|pictures|pic|pics|video|videos|selfie|selfies)\b",
        re.I,
    ),
    # Sextortion / online coercion (2026-08-12 safeguarding review). SAFETY §3.2 Cat C exploitation.
    re.compile(r"\b(share|post|send|show)\b[^.?!]{0,20}\b(my )?(photos?|pictures?|pics?|videos?)\b[^.?!]{0,25}\bif i don'?t\b", re.I),
    re.compile(r"\b(threatens?|threatened|threatening) (to )?(share|post|send|show|tell)\b", re.I),
    re.compile(r"\b(knows?|found out) (my school|where i live|my address)\b", re.I),
    re.compile(r"\bkeeps? (messaging|texting|contacting) me\b[^.?!]{0,30}\b(asked|told) (them|him|her) to stop\b", re.I),
    # Grooming: an online contact pressing to meet or move off-platform.
    re.compile(
        r"\b(someone|somebody|a man|a woman|a person|a boy|a girl|a stranger|he|she|they)\b"  # t7.3-exempt: regex alternation, not a prompt
        r"[^.?!]{0,60}\b(online|on the internet|in a game|on a game|in the chat)\b"
        r"[^.?!]{0,60}\b(want(s|ed)? to meet|asked to meet|wants my address|asked where i live)\b",
        re.I,
    ),
    re.compile(r"(he|she|they) (made|make|asked|ask|told|tell) me (to )?(do|touch|show) (something|things?|myself|them)", re.I),
)]

# ── C: secrecy_request (HIGH) ────────────────────────────────────────────────
# Patterns where the child tries to enlist the AI in keeping secrets from parents.
# Also covers disclosure that another adult has demanded secrecy.
_SECRECY_REQUEST_PATTERNS: list[re.Pattern[str]] = [p for p in (
    re.compile(r"(don'?t|do not|please don'?t) (tell|let|show) (my )?(mum|mom|mummy|mommy|dad|daddy|father|mother|parent|carer|guardian|teacher|anyone|grown.?up)", re.I),
    re.compile(r"(keep|kept) (this |it )?(a )?secret (from|between)", re.I),
    re.compile(r"(it'?s|this is) (just )?our secret", re.I),
    # "not to tell" is the natural child phrasing ("will you promise not to tell my mum?") —
    # found missing by the T2.5 pipeline run 2026-08-12.
    re.compile(r"(promise|swear) (me )?(you )?(won'?t|never|not to|not) tell", re.I),
    re.compile(r"(he|she|they) (told|said|told me|says) (not to|to never|to not) tell (anyone|anyone|my mum|my mom|my dad|my parent)", re.I),
    re.compile(r"(told|said|asked) me (not|never) to (say|tell|talk about) (anything|this|it)", re.I),
    re.compile(r"(nobody|no one|don'?t let anyone) (must|should|can) know (about this|about it)", re.I),
)]

# ── D: adversarial_jailbreak (LOW) ───────────────────────────────────────────
# Patterns for jailbreak / safety-override attempts (Layer 1 §1.4 already blocks
# inline; this class ensures they reach the escalation log for audit).
_ADVERSARIAL_JAILBREAK_PATTERNS: list[re.Pattern[str]] = [p for p in (
    re.compile(r"(ignore|disregard|forget|bypass|override) (?:your |all |previous |the |above ){0,2}(instructions?|rules?|guidelines?|safety|(?:system )?prompt\b|restrictions?)", re.I),
    re.compile(r"(pretend|act|behave|imagine) (like |as if )?(you (are|have) no |you don'?t have |you'?re |you are )(a different|rules?|restrictions?|guidelines?|an? (uncensored|unrestricted|free|evil|jailbroken))", re.I),
    # E2.5 (2026-08-10): the exemption lookahead must run BEFORE the optional article
    # is consumed — the old form `(a |an )?(?!a tutor|...)` greedily ate "a " first, so
    # the lookahead checked for the literal "a tutor" at a position where "a " was
    # already gone and never blocked; "you are now a tutor" fired as a jailbreak.
    re.compile(r"(you are now|you'?re now|from now on (you are|you'?re|act as)) (?!(?:a |an )?(?:tutor|helping|assisting|my tutor))((?:a |an )?)", re.I),
    re.compile(r"(jailbreak|dan mode|developer mode|god mode|unrestricted mode)", re.I),
    re.compile(r"(your new (instructions?|rules?|system prompt)|new system prompt)", re.I),
    re.compile(r"(pretend you have no rules|pretend you'?re a different ai|pretend (there are|you have) no (rules|restrictions|limits?))", re.I),
    re.compile(r"(do anything now|say anything|no (rules|limits?|restrictions?))\b", re.I),
    # System-prompt / instruction extraction (prompt-leak attempts).
    re.compile(r"(what('?s| is| are)|tell me|show me|give me) (your |the )?(system )?(prompt|instructions?|rules?|guidelines?)", re.I),
    re.compile(r"(print|show|reveal|repeat|output|display) (me )?(your |the )?(system )?(prompt|instructions?|rules?|guidelines?)", re.I),
    re.compile(r"(repeat|print|show|reveal|output) (the |all )?(text|words?|message|everything|content) (above|before|prior|earlier)", re.I),
    re.compile(r"what were you (told|instructed|programmed|asked|made) (not )?to", re.I),
)]

# De-obfuscation: catch jailbreaks hidden by leetspeak / spacing / base64. Applied
# ONLY as a fallback for the LOW-severity jailbreak class (never to the critical/high
# safety classes — aggressive normalisation there risks false escalations / misses).
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "8": "b"})
_JAILBREAK_DEOBFUSCATED = re.compile(
    r"(ignore|disregard|forget|bypass|override).{0,15}(instruction|rule|guideline|safety|systemprompt|restriction)"  # t7.3-exempt: de-obfuscation regex, not a prompt
    r"|jailbreak|danmode|developermode|godmode|unrestrictedmode"
    # E2.5: same benign-role exemption as the primary pattern, in despaced form --
    # without it the fallback re-fires on "you are now a tutor" after despacing.
    r"|youarenow(?!(?:a|an|my)?(?:tutor|helping|assisting))"
    r"|youhavenorules|pretend.{0,15}no.{0,5}(rule|restriction|limit)"
    r"|(whatis|tellme|showme|print|reveal|repeat).{0,15}(systemprompt|instruction|rule|guideline)",
    re.I,
)


def _deobfuscated_views(text: str) -> list[str]:
    """Normalised variants of *text* for catching obfuscated jailbreaks."""
    low = text.lower()
    leet = low.translate(_LEET)
    despaced = re.sub(r"[^a-z0-9]", "", leet)          # collapse spacing/punctuation
    views = [leet, despaced]
    for token in re.findall(r"[A-Za-z0-9+/]{8,}={0,2}", text):
        if len(token) % 4 == 0:
            try:
                dec = base64.b64decode(token, validate=True).decode("utf-8", "ignore")
            except Exception:
                continue
            if dec and dec.isprintable():
                views.append(dec.lower())
    return views


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

    # Fallback: catch jailbreaks obfuscated by leetspeak / spacing / base64. Only
    # when nothing else fired (so it can't override a real safety class), and only
    # for the LOW-severity jailbreak class.
    if best is None:
        for view in _deobfuscated_views(text):
            m = _JAILBREAK_DEOBFUSCATED.search(view)
            if m:
                return TriggerMatch(
                    trigger_class=TriggerClass.ADVERSARIAL_JAILBREAK,
                    severity=Severity.LOW,
                    matched_span=m.group(0)[:80],
                )

    return best
