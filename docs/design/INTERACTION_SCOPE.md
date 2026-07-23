---
type: Mentar Design Doc
title: Interaction Scope — Child-Input Intents
description: Gap analysis + proposal for what child input the system recognizes and how it routes it, surfaced during product testing (2026-06-29).
tags: [design, fsm, safety, pedagogy]
timestamp: "2026-06-29T00:00:00Z"
---

# Interaction Scope — child-input intents (gap analysis + proposal)

**Status:** draft for maintainer ratification (2026-06-29). Surfaced during product testing.
**Why now:** UI is deferred, but the *interaction scope* — what child input the system
recognizes and how it routes it — is foundational. It shapes the FSM, safety, pedagogy, and
the BKT signal. Getting it wrong silently corrupts mastery and feels broken to a child.

**v0 slice shipped (A21, ratified 2026-07-04, built 2026-07-05):** a narrow, deterministic
carve-out for **don't-know** and **clarify/vocabulary** (the two intents flagged Essential in
§2) — `_is_dont_know_or_question()` in `dialogue/controller.py` matches a fixed don't-know
phrase set ("i don't know", "idk", "no idea", "dunno", "i dont know") OR a question-shaped
input (starts with what/how/why/when/where/who/can/is/does, or ends in `?`), and routes it
into the Help loop unscored — same wiring as `_is_help_request` (same guarded states, same
target, sets `help_by_node` too). **Frustration/mild-affect, off-topic, and meta/navigation
intents (§2) remain unbuilt** — the full taxonomy proposal below (§3–§6) is still deferred and
needs maintainer ratification beyond this narrow slice.

---

## 1. Current scope (what the system actually recognizes)

Child input is classified into exactly **four** intents, in this precedence:

| # | Intent | Trigger | Routing |
|---|--------|---------|---------|
| 1 | **Safety escalation** | deterministic regex (`safety/escalation.py`): harm_to_self, physical_danger, severe_distress, abuse_disclosure, secrecy_request, adversarial_jailbreak | freeze → handoff (parent) |
| 2 | **Help** | `?` / `help` / `h` | Help loop (explain + re-check) |
| 3 | **Stop** | `stop` / `quit` / `bye` / `exit` | end session |
| 4 | **Answer** | anything else | deterministic verifier scores it (right / wrong / unreadable) |

**The gap:** intent #4 is a catch-all. Any utterance that isn't a bare answer, a help/stop
keyword, or a safety trigger is **scored as an answer**. There is no recognition of the large
class of natural child inputs that are *neither* an answer *nor* a crisis.

---

## 2. The missing intents (force-scored today → essential to handle)

| Intent | Examples | Today | Problem | Priority |
|--------|----------|-------|---------|----------|
| **don't-know** | "I don't know", "dunno", "not sure", "no idea" | scored WRONG / unreadable | penalises honesty; corrupts BKT; should scaffold | **Essential** |
| **frustration / mild affect** | "this is hard", "I'm tired", "I'm bored", "I can't do this" | scored as an answer (below escalation threshold) | feels cold/broken; a wrong "answer"; misses a teachable/affective moment | **Essential** |
| **clarify / vocabulary** | "what does denominator mean?", "what's a half?" | scored WRONG | child asking to learn is marked wrong | **Essential** |
| **off-topic / chit-chat** | "do you like games?", "what's your name?" | scored as an answer | the system-prompt redirect rule never fires (input never reaches the LLM in the answer state) | **Important** |
| **meta / navigation** | "repeat", "what was the question?", "skip", "an easier one", "a different question" | scored as an answer | no agency; natural requests fail | Nice-to-have |

The first three are the ones that actively **break the learning signal** (a "don't know" or a
question logged as a wrong answer pushes mastery down for the wrong reason) — so they're
correctness bugs, not polish.

---

## 3. Design principle — bounded intents, NOT free chat

Expanding interaction scope must **not** become open-ended LLM conversation (that bypasses the
safety envelope — see SAFETY.md, and the no-free-chat rule). The proposal is:

- **A fixed, enumerated intent set** classified *before* scoring. Each intent routes
  deterministically to an existing or new bounded state.
- **Safety classifier stays first and deterministic** — it always pre-empts. No soft-intent
  routing can swallow a safety trigger.
- **The LLM is still only invoked inside bounded states** (present / help-explain / re-check).
  Soft intents route to those same bounded states, never to open dialogue.

So the scope grows in **recognised categories**, not in conversational freedom.

---

## 4. Proposed routing (within the safety envelope)

- **don't-know** → enter the Help loop (scaffold), exactly like a wrong unaided answer now does;
  do **not** log a scored wrong attempt (it's an honest "not yet", not an error).
- **frustration / mild affect** → one warm acknowledgement + offer help / an easier item;
  **not** scored. ⚠️ Boundary with `severe_distress` is safety-critical: the deterministic
  safety classifier runs first, so only *sub-threshold* affect reaches this path. Erring toward
  escalation is safe; erring toward "just frustration" on real distress is not — keep this
  pattern set conservative and reviewed.
- **clarify / vocabulary** → a bounded, grounded definition (Help-style, from the ZIM/glossary),
  then re-ask the same question; not scored.
- **off-topic** → the single gentle redirect already specified in the system prompt, but
  enforced at the FSM level so it fires from the answer state too; not scored.
- **meta / navigation** → deterministic: repeat = re-show `current_question`; skip/easier =
  present another item (possibly easier); not scored.

---

## 5. Open decisions for the maintainer

1. **Which soft intents are in-scope now** vs later (recommend: don't-know + frustration +
   clarify first — they're the BKT-corrupting ones).
2. **Classification mechanism — GUIDANCE (maintainer asked, 2026-06-29):**
   Safety classification is **deterministic + first**, always (settled; an LLM must never make a
   safeguarding call). The choice below is only for the *soft, non-safety* intents.
   - **A. Deterministic keywords** (like stop/help): auditable, instant, no LLM; brittle to
     paraphrase/typos.
   - **B. LLM intent-classifier**: robust to phrasing; an LLM call per turn; can mislabel a real
     answer.
   - **C. Hybrid (fallback)**: keywords catch common forms; an LLM classifier is consulted **only**
     when input matches no keyword *and* fails to verify as an answer (the genuinely ambiguous set)
     — keeps the LLM off the common path.

   **Recommendation: start A, architect for C.** Ship deterministic keywords first (safe, covers
   the bulk), and shape the input handler so a fallback classifier can slot in for
   no-keyword-and-unverifiable inputs later. **Why the stakes are low:** a wrong answer now
   auto-routes to Help, so a *missed* "I don't know" still gets scaffolded — the only harm of a
   miss is a spurious BKT penalty, not a broken experience. So "good enough to stop honest
   don't-knows dinging mastery" is the bar, not perfection.

   **Invariant for any approach:** the classifier emits a **label** (routing only), never content
   or correctness; the verifier still scores answers; on uncertainty the system **defaults to
   "treat as an answer"** (which auto-helps if wrong). Misrouting cost stays bounded.
3. **frustration vs severe_distress boundary** — needs the same safeguarding review as W2.2.
4. **don't-know penalty** — confirm it should NOT count against mastery (recommended).

---

## 6. Relationship to existing work

- Builds on the existing intent precedence in `dialogue/controller.py::_step_core` (safety →
  help → stop → answer). New soft intents slot in **after safety/help/stop, before scoring**.
- `frustration`/`severe_distress` boundary ties to `docs/design/W2.2_escalation.md`.
- Not UI: UI/rendering issues are tracked separately (TESTING_NOTES + the web-display backlog).
