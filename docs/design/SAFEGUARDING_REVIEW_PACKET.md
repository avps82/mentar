---
title: "Mentar — Safeguarding Review Packet (for an external safeguarding / child-communication professional)"
status: "Prepared 2026-07-16 for the maintainer to hand to a qualified reviewer. Not a policy document; it frames what a professional is being asked to validate."
owner: maintainer (commissions review) / external safeguarding professional (gives the review)
sources: SAFETY.md §3.2–§3.5, docs/design/W2.2_escalation.md, docs/design/W2.2_signposting_decision_prep.md, src/mentar/safety/escalation.py
---

# Mentar — Safeguarding Review Packet

> **Who this is for.** A qualified safeguarding professional, child psychologist, or
> child-communication specialist being asked to review Mentar's safety-escalation
> behaviour. **You do not need to read any code or technical documents** — this packet
> is self-contained. Pointers to the deeper technical docs are at the end if you want them.
>
> **Why this review exists.** Mentar's own safety specification (`SAFETY.md §3.5`) contains
> a hard, self-imposed rule: the product **must not** be used beyond a single, supervised
> family — and must not enable any unsupervised/independent mode — until a professional has
> validated the two items in Part 3 of this packet. This review is that gate. Nothing here
> is asking you to endorse the whole product; it is asking for a focused judgement on two
> specific safety behaviours.

---

## Part 1 — What Mentar is, in plain language

Mentar is an offline AI tutor for a child (roughly ages 8–10), currently teaching primary
maths. It runs entirely on a family's own device — no cloud account, no child data leaving
the home. A parent sets it up and is expected to be present ("parent-mediated / supervised"
mode is the only mode enabled today).

Relevant to this review: while a child is doing a lesson, they type answers and can type
free text. If a child ever types something that suggests they are in distress or danger, the
tutoring must stop and the child must be pointed toward a safe adult — not "handled" by the
AI. That behaviour is what you are reviewing.

**One design principle worth knowing:** the AI model never decides what is or isn't a safety
concern, and never writes the safety message. A fixed, human-authored keyword/pattern check
runs on every line the child types; if it matches, a **fixed, pre-written message** is shown.
The AI is switched off for that moment entirely. This is deliberate — we do not want a
language model improvising in a safeguarding situation.

---

## Part 2 — Exactly what happens when a child types something concerning

**Step 1 — the check.** Every line the child types is checked against pattern banks grouped
into these categories (the category names are ours; the point is the *coverage*, which is one
thing your review should assess):

| Category | Covers (examples of what a child might type) | Treated as |
|---|---|---|
| Harm to self | "I want to hurt myself", "I want to die" | Most serious — freeze |
| Physical danger | "someone is hurting me", "I don't feel safe at home" | Most serious — freeze |
| Abuse disclosure | descriptions of being hit/hurt by someone | Most serious — freeze |
| Severe distress | despair, hopelessness beyond ordinary frustration | Serious — freeze |
| Secrecy request | "don't tell my parents", "someone said not to talk about this" | Serious — freeze |
| (Adversarial/technical) | a child trying to trick the AI | Logged, lesson continues — NOT frozen |

The check is deliberately **over-sensitive**: it is designed to over-trigger (stop the lesson
when it maybe didn't need to) rather than under-trigger (miss a real signal). We consider a
false alarm far preferable to a miss. Your view on whether that balance, and the categories
above, are right is part of what we're asking.

**Step 2 — freeze.** The lesson stops immediately. The AI generates nothing further.

**Step 3 — the child sees a fixed message** (this is item A in Part 3 — the exact wording you
are asked to validate).

**Step 4 — the parent is alerted.** The exact words the child typed are written to a log the
parent can review; the on-screen parent alert shows that an escalation happened (time, category)
but not the raw words. Nothing is ever silently deleted.

**Step 5 — the lesson stays frozen** until a parent physically present acknowledges it and
chooses to resume. It never auto-resumes and never times out back into the lesson.

---

## Part 3 — The two things your sign-off is required for

### Item A — The exact wording shown to the child

When the lesson freezes, the child sees these two lines, verbatim (nothing else, no AI text):

> **"This is something to talk about with your grown-up. Let's pause our lesson here."**
>
> **"Your grown-up can help you with this. Your lesson will be here when you're ready to come
> back."**

The wording was drafted by the (non-clinician) development team with these intentions: point
the child toward a trusted adult without alarming them; frame the pause as neutral, not a
punishment; express no judgement or urgency; and have the AI clearly step back rather than
offer to "help more."

**What we need from you on Item A:**
1. Is this wording safe and appropriate for a distressed child aged ~8–10?
2. Does "grown-up" work as an inclusive term, or is different phrasing safer?
3. Is there any circumstance where this message could make a distressed child feel worse,
   dismissed, or shut down?
4. If you'd change the wording, what exactly should it say?

### Item B — What happens when the safe adult *is* the problem

Today, a serious trigger routes the child to **the parent who is physically present**. In a
supervised single-family pilot, that adult is known and vetted, so this is considered
acceptable *for the pilot only*.

**The known hole, stated plainly:** "go to your grown-up" is the wrong instruction when the
grown-up is the source of harm — precisely the abuse-disclosure and physical-danger cases.
The current design does **not** show a child any external resource (e.g. a helpline or a
"find a different trusted adult" message). This is the single biggest reason the product is
locked to the supervised pilot.

**What we need from you on Item B:**
1. For a home-use tool where the parent is the intended safe adult, what should happen when
   a child discloses that the parent is the source of harm?
2. Should the child ever be shown an external resource (helpline / "tell another trusted
   adult like a teacher") — and if so, for which of the categories in Part 2, and in what
   exact, age-appropriate words?
3. Is showing a crisis number to an unsupervised child ever the right call, or does that
   create its own risks (a child alarmed by a "call 999" message)?
4. What is the minimum that must be true before this tool could safely be used **without** a
   parent present?

---

## Part 4 — Other open questions (lower priority, but useful if you have views)

- **Gradated response:** the tool currently has one response (full freeze) for any serious
  trigger. Would a softer intermediate step (a gentle check-in for milder signals before a
  full stop) be safer, or does binary freeze-on-any-signal remain the right conservative call
  for this age group?
- **Multi-turn distress:** the check looks at each line on its own. Distress that builds
  gradually across several lines, with no single alarming line, is not currently detected.
  How much of a concern is this in practice for this age group and use?
- **The trigger categories/coverage** in Part 2: are any categories missing, and are the
  example phrasings representative of how a real child of this age would express these things?

---

## Part 5 — What we are NOT asking you to do

- Review the code, the AI model, or the tutoring quality — out of scope.
- Endorse the product overall — out of scope.
- Provide the exact final helpline numbers/wording for every region — we need the *principles*
  and the age-appropriate approach; region-specific resourcing can follow.

## Deeper technical references (optional)

- `docs/SAFETY.md` §3.2–§3.5 — the full escalation specification and the "rollout guard" this
  review satisfies.
- `docs/design/W2.2_escalation.md` — the implementation contract (categories, flow, test
  fixtures).
- `docs/design/W2.2_signposting_decision_prep.md` — the internal options analysis for Item B
  (Options A/B/C), already prepared for this decision.
- `src/mentar/safety/escalation.py` — the actual pattern-check code (46 test cases in
  `tests/safety/test_escalation.py`).

---

## For the maintainer — how to use this

1. This packet is meant to be handed, as-is, to a qualified safeguarding / child-communication
   professional. It deliberately requires no technical background.
2. The two items in Part 3 are the load-bearing ones — they are the exact `⟐` items the
   `SAFETY.md §3.5` rollout guard names. Getting a documented professional judgement on both is
   what unlocks moving beyond the single-family pilot.
3. Their answers should be recorded back into `SAFETY.md §3.4/§3.5` (handoff wording) and
   `W2.2_signposting_decision_prep.md` (signposting design), and the rollout guard updated only
   once both are genuinely closed.
