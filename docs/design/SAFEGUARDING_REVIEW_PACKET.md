---
type: Mentar Design Doc
title: "Mentar — Safeguarding Review Packet (for an external safeguarding / child-communication professional)"
status: "Prepared 2026-07-16; REFRESHED 2026-08-15 to match what the product actually is now (see 'What changed' below). Not a policy document; it frames what a professional is being asked to validate."
owner: maintainer (seeks the review) / external safeguarding professional (gives the review)
sources: SAFETY.md §3.2–§3.5 + §3.5.1, docs/design/W2.2_escalation.md, docs/design/W2.2_signposting_decision_prep.md, src/mentar/safety/escalation.py
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
> is asking you to endorse the whole product; it is asking for a focused judgement on three
> specific safety behaviours.
>
> **This is unpaid.** Mentar is an unfunded open-source project with no budget to commission
> a review (`SAFETY.md §3.5.1`). It is being sought pro-bono, and this packet exists to make
> contributing as low-effort as possible — a written answer to the questions in Part 3 is
> enough; there is nothing to install and no meeting required. Absent a volunteer, the
> restriction stays in force and the tool stays limited.

---

## What changed since this packet was first written (2026-07-16 → 2026-08-15)

Read this if you saw the earlier version; skip it otherwise. Three things moved, and the
first two change what is being asked of you.

1. **The age range roughly tripled.** This packet used to describe an 8–10 maths tutor.
   Shipped content now spans roughly **ages 6 to 18**, and the *largest* share of it is
   16–18. The safety wording in Item A did **not** change with it — the message written for
   an 8-year-old is the one a 17-year-old sees. That is now **Item C**, a new question
   rather than a detail.
2. **Detection coverage was widened twice** (2026-08-12 and 2026-08-15) after internal
   reviews found whole categories of disclosure going undetected — see Part 2. None of that
   widening was clinically validated; it is adult-authored engineering work, which is
   precisely why this review still matters.
3. **The review was reframed from "commissioned" to "sought pro-bono"**, and now gates
   *unsupervised* use specifically rather than blocking the supervised pilot. No safety
   behaviour was weakened by that change — only the honesty of the framing.

---

## Part 1 — What Mentar is, in plain language

Mentar is an AI tutor a family runs on their own computer, teaching maths, English and
science. It runs **entirely locally** — no cloud account, no child data leaving the home.
(A parent can optionally allow lessons to be opened from a tablet on the same home Wi-Fi,
because a tablet cannot run the AI itself. Nothing leaves the house either way.) A parent
sets it up and is expected to be present: "parent-mediated / supervised" is the only mode
enabled today.

**Ages — please note.** The original pilot targeted roughly ages 8–10, and that remains the
only real-world use so far. But content shipped today spans roughly **ages 6 to 18**:
primary arithmetic through senior physics, chemistry and biology. The safety behaviour
below is **identical at every age** — one detection system, one fixed message, no variation
by how old the child is.

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
| Harm to self | "I want to hurt myself", "I want to die"; passive ideation ("nobody would miss me"); deliberately not eating | Most serious — freeze |
| Physical danger | "someone is hurting me", "I don't feel safe at home"; witnessing violence between adults ("dad hits mum"); neglect ("there's no food in the house"); wanting to run away | Most serious — freeze |
| Abuse disclosure | being hit or hurt by someone, including by a named family member; unwanted touching stated plainly ("my uncle touches me"); requests for photos or pressure to meet from an online contact | Most serious — freeze |
| Severe distress | despair and hopelessness beyond ordinary frustration; being told repeatedly they are worthless by a person | Serious — freeze |
| Secrecy request | "don't tell my parents", "someone said not to talk about this" | Serious — freeze |
| (Adversarial/technical) | a child trying to trick the AI | Logged, lesson continues — NOT frozen |

The check is deliberately **over-sensitive**: it is designed to over-trigger (stop the lesson
when it maybe didn't need to) rather than under-trigger (miss a real signal). We consider a
false alarm far preferable to a miss. Your view on whether that balance, and the coverage
above, are right is part of what we're asking.

**Two findings worth your attention, because they show how this fails.** Both were found by
us, internally, by writing out how a real child would actually phrase things and testing it:

- *August 12:* several categories the specification already claimed to cover had **no
  detection at all** — witnessing domestic violence, neglect, peer/school violence, emotional
  abuse by a carer, online sexual coercion. Separately, plain phrasings were missed in
  categories that *did* exist: **"my uncle touches me" matched nothing**, because every
  pattern required an explicit body part or stated intent.
- *August 15:* the check required the person and the action to sit **next to each other** in
  the sentence, and only understood present tense. So **"someone at home hits me"** was
  caught, but **"i get hit at home"**, **"my dad hurt me"** and **"i am scared of my dad"**
  were **not**.

Both are fixed and pinned by tests. We report them because they are the honest evidence for
why an adult-authored pattern list is not a substitute for your judgement: each gap looked
complete from the inside until someone wrote the sentence a child would really type. **If
you do only one thing with this packet, telling us the phrasings we are still missing would
be the most valuable.**

**Step 2 — freeze.** The lesson stops immediately. The AI generates nothing further.

**Step 3 — the child sees a fixed message** (this is item A in Part 3 — the exact wording you
are asked to validate).

**Step 4 — the parent is alerted.** The exact words the child typed are written to a log the
parent can review; the on-screen parent alert shows that an escalation happened (time, category)
but not the raw words. Nothing is ever silently deleted.

**Step 5 — the lesson stays frozen** until a parent physically present acknowledges it and
chooses to resume. It never auto-resumes and never times out back into the lesson.

---

## Part 3 — The things your sign-off is required for

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

### Item C — One message, ages 6 to 18 *(new in this refresh — see "What changed")*

Everything above — the detection, the fixed wording, "talk to your grown-up", routing to the
present parent — behaves **exactly the same** whether the person typing is 6 or 18. Nothing
in the system varies by age. That was a reasonable simplification when the tool taught 8–10
maths. It is now a live question, and we do not know the answer.

Concretely, the same two lines in Item A are shown to a 6-year-old and to a 17-year-old
doing senior chemistry.

**What we need from you on Item C:**
1. Is a single fixed message across that span defensible, or does it need to differ by age?
   If it must differ, roughly where is the break — and what should the older version say?
2. Does "your grown-up" fail for an older teenager — patronising, or actively
   counterproductive to a disclosure?
3. Does the **routing** need to change with age? "Fetch the parent in the room" is a
   different act for a 16-year-old than for a 7-year-old, and an older teenager may have a
   safe adult outside the home whom a younger child does not.
4. Do older teenagers need signposting (Item B) that younger children should not get — is
   age the factor that separates the two, and if so, from what age?
5. Are there disclosures where the right response changes with age for legal rather than
   developmental reasons? We are aware this may vary by country; principles are enough.

**Our own read, offered so you can disagree with it:** one message for everyone is very
likely wrong at the top of the range, and we would rather be told that plainly than keep
shipping it because no one has said so. We have deliberately **not** guessed at an
age-varying design — inventing developmental thresholds is exactly the judgement we are
unqualified to make, and a wrong guess implemented confidently is worse than the honest gap.

---

## Part 4 — Other open questions (lower priority, but useful if you have views)

- **Gradated response:** the tool currently has one response (full freeze) for any serious
  trigger. Would a softer intermediate step (a gentle check-in for milder signals before a
  full stop) be safer, or does binary freeze-on-any-signal remain the right conservative call
  across the whole 6–18 range?
- **Multi-turn distress:** the check looks at each line on its own. Distress that builds
  gradually across several lines, with no single alarming line, is not currently detected.
  How much of a concern is this in practice?
- **Coverage** (Part 2): are any categories still missing, and are the phrasings
  representative of how a real child — at either end of the age range — would say these
  things? See the two findings in Part 2 for the shape of what we keep getting wrong.
- **The parent alert is passive.** A parent is told an escalation happened when they next
  look at the parent page; nothing pages them. On a supervised setup the adult is in the
  room, so this was judged sufficient. Is it?
- **Over-triggering has a cost we may be underweighting.** A child whose lesson freezes on a
  false alarm learns the tool is unpredictable, and may write less freely afterwards. We
  chose over-sensitivity anyway. Is that still right if it happens repeatedly to the same
  child?

### Third widening probe (2026-08-18) — six more phrasings, unresolved by design

A routine bug sweep ran 37 further phrasings past the classifier. It is listed here as
evidence, not as a defect report: `escalation.py` is a protected path whose changes need
safeguarding review, so **nothing was changed in response to any of these.** The pattern is
the same one Part 2 already documents — an adult guessing at a child's words.

Five disclosures produced no trigger at all:

| Phrasing | Why it is hard for a pattern list |
|---|---|
| "my mum's boyfriend comes into my room at night" | Every word is innocuous alone. The concern is entirely in the combination and the context. |
| "im being bullied and i cut myself" | The list requires a qualifier — `cut myself on purpose / to hurt / because`. A bare "i cut myself" does not fire, because it collides with accidental injury ("I cut myself on the scissors"). |
| "my brother makes me do things i dont like" | Indistinguishable, by wording alone, from a complaint about chores. |
| "i'm scared to go home" | A recognised indicator that reads as ordinary reluctance. |
| "i havent eaten in two days" | Only fires today when the child adds "on purpose", which attributes intent a neglected child would not state. |

And one false alarm, in the opposite direction: **"i want to die of boredom doing fractions"**
fires `harm_to_self` at CRITICAL and freezes the lesson. In a maths tutor this idiom is
predictable, and it is the concrete form of the over-triggering cost raised just above.

**What we would find useful from you.** Each of these has an obvious-looking fix and a real
cost, and we do not think we should be the ones choosing:

1. Should a bare "I cut myself" fire, accepting that some accidental cuts will freeze a
   lesson? We currently require a qualifier and so miss the disclosure.
2. Is a narrow idiom exception ("die of boredom", "bored to death") safe, or does any
   carve-out around "want to die" set a precedent that erodes the category?
3. Are indicators like "scared to go home" and "haven't eaten in two days" ones a tool like
   this should act on at all, or ones that belong to an adult who knows the child?

---

## Part 5 — What we are NOT asking you to do

- Review the code, the AI model, or the tutoring quality — out of scope.
- Endorse the product overall — out of scope.
- Provide the exact final helpline numbers/wording for every region — we need the *principles*
  and the age-appropriate approach; region-specific resourcing can follow.

## Deeper technical references (optional)

- `docs/SAFETY.md` §3.2–§3.5 — the full escalation specification and the "rollout guard" this
  review satisfies; §3.5.1 states the pro-bono framing and what happens if no reviewer is found.
- `docs/design/W2.2_escalation.md` — the implementation contract (categories, flow, test
  fixtures).
- `docs/design/W2.2_signposting_decision_prep.md` — the internal options analysis for Item B
  (Options A/B/C), already prepared for this decision.
- `src/mentar/safety/escalation.py` — the actual pattern-check code. It is covered by 106
  automated tests across `tests/safety/`, which check both directions: that concerning
  phrasings do fire, and that ordinary ones ("a ball hits the ground", "I always feel better
  after a nap") do not.

---

## For the maintainer — how to use this

1. This packet is meant to be handed, as-is, to a qualified safeguarding / child-communication
   professional. It deliberately requires no technical background.
2. Items A and B are the exact `⟐` items the `SAFETY.md §3.5` rollout guard names. Item C is
   new: it is not in the original rollout guard because the age range was 8–10 when that guard
   was written. **It should be added to the guard** — shipping senior-secondary content while
   the safeguarding wording is still calibrated for an 8-year-old is an unratified widening of
   scope, not a tested decision.
3. Answers should be recorded back into `SAFETY.md §3.4/§3.5` (handoff wording, Items A and C)
   and `W2.2_signposting_decision_prep.md` (signposting design, Item B). Update the rollout
   guard only once they are genuinely closed.
4. If no reviewer is found, `SAFETY.md §3.5.1` already says what happens: unsupervised mode
   needs an explicit, documented maintainer risk decision taken in the professional's place.
   That path is open for Item C too — but it should be **written down as a decision**, not
   left as the current silence.
