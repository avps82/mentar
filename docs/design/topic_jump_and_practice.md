---
type: Mentar Design Doc
title: "Jump to a topic — child/parent-chosen practice of a specific concept"
description: "SHIPPED 2026-08-18, same day as the plan. A visible 'Jump to a topic' affordance on each subject card, leading to a clickable topic list that pins one concept and serves items from it, bypassing fringe selection."
tags: [design, ui, curriculum, practice, shipped]
timestamp: "2026-08-18T00:00:00Z"
---

# Jump to a topic

**Status: SHIPPED 2026-08-18** — built to the plan below, same day it was ratified.
Delivered exactly the planned diff: controller pin (param + one NODE_SELECT branch +
checkpoint field), `/choose` `topic` field + `/topics` route, the card's sibling
"🎯 Jump to a topic" link, `topics.html`. One departure the plan missed, found while
writing the tests: `/choose` needed an ESCALATION_FREEZE guard — without it, re-choosing
with a topic pin would have replaced a FROZEN controller with a fresh one, letting a
child thaw an escalation freeze by tapping a topic. Guarded and pinned by
`test_disclosure_freezes_a_pinned_session_and_a_pin_cannot_thaw_it`.

**Post-ship sweep, same day:** the first re-jump after a COMPLETED session exposed a
second gap — the pin hadn't changed, so `/choose` kept the terminal controller and
`/learn` bounced to `/done`; tapping the topic again did nothing, which broke the
repetition goal for exactly the topic just finished. Fixed by popping the controller on
any explicit choose when the live one `is_terminal` — unified with the GUIDED case,
where tapping the subject card after `/done` had the same dead-end (previously escaped
only via the done page's Start-again button). A LIVE session re-chosen unchanged is
still a no-op (double-tap/refresh must not reset progress). All three behaviours are
mutation-proved tests in `tests/web/test_topics.py`.

## The need

The tool guides. Given a subject it picks what to teach next, from prerequisites and
mastery, and that is right for a young child building from foundations. It is wrong for
the other case the maintainer described: a learner who **already knows what they need**.

> "if a child comes in and needs to start from, instead of subtraction, they need to go
> straight to division, for instance, because they know subtraction"

> "they want to jump to those topics because they're not sure. This tool can help in
> those parts."

Two variants of one need — skip what is already known, and go straight to the thing that
is actually troubling them. Also, explicitly, **repetition**: today a topic is taught once
and then disappears from selection, and the maintainer wants a learner to be able to come
back and redo it "to get the memorization parts, the structure set in nicely".

This is an assist tool for a parent as much as the child: *"okay, move to the next topic,
you are good with this, it's wasting your time."*

## Why it is not possible today

`engine/fringe.py` `outer_fringe()` offers a concept only when **every** prereq is
mastered, and skips any concept already mastered. Two consequences:

* A topic further along the graph is **unreachable** until everything before it is
  mastered — so there is no way to start at division, or at a specific senior topic.
* A topic already mastered is **unreachable again** until it goes stale, which is
  `STALE_MASTERY_DAYS = 14` (`dialogue/controller.py`), after which spaced review injects
  it every `REVIEW_EVERY_N = 4` items. Revisiting exists, but it is engine-driven and two
  weeks away — the "do once, forget later" the maintainer described.

The existing practice packs (`curriculum/templates/practice/`) are NOT this. They are two
separate evergreen subjects with three drill concepts each (times tables, skip counting,
doubles/halves). They cannot express "practise Year 5 fractions again".

## The proposed flow (maintainer's own wording)

1. Subject card on the front page → straight into questions. *(exists — `POST /choose`)*
2. A visible **"Jump to a topic"** affordance on that card, so the option is discoverable
   rather than hidden behind the progress page.
3. The topic list shows the subject's concepts.
4. Click a concept → practise **that** concept.

Discoverability is a requirement, not a nicety: a learner who does not know jumping is
possible will sit through the guided path and conclude the tool wastes their time.

## What has to change

**One branch, one route, one click target.**

* `_do_node_select()` (`dialogue/controller.py`) is the ONLY place a node is chosen. A
  pinned-topic session uses the chosen node instead of calling `select_next()`. Everything
  downstream — item generation, verifying, help, worked examples, explain cards — is
  already per-node and does not care how the node was chosen. That is what makes this
  small.
* A route to enter a pinned session for `(subject, node_id)`.
* A click target on the topic list.

### Constraint: it MUST go through the normal controller turn

Not a side path that draws an item and checks the answer directly. Child input has to keep
passing the escalation classifier and the output guard. A lightweight "just serve some
questions" route is the one way this modest feature could go badly wrong, and it is an
easy mistake to make when the goal is only to show questions.

### Markup constraint on the subject card

`web/templates/subjects.html` renders each card as a `<button type="submit">` inside a
`<form method="POST" action="/choose">`. The whole card is the button, so a "Jump to a
topic" link **cannot be nested inside it** — interactive content inside a button is
invalid and behaves unpredictably. It has to be a sibling element within the card wrapper,
which means the card markup changes shape slightly.

### Which topics are clickable — a real choice, not a detail

`/progress` renders two things covering **different sets**:

* the **graph** is built from the whole curriculum, so every concept appears, including
  never-attempted ones;
* the **star cards** are built only from concepts that already have a `skill_state` row,
  so a concept never attempted has no card at all (hence "No topics yet" for a new
  learner).

If the click target is the star cards, a learner can only re-practise what they have
already touched — which cannot serve "jump ahead to the thing I'm stuck on". So either the
graph nodes are the target, or the card list must render every curriculum concept rather
than only attempted ones. Choose deliberately.

If graph nodes become the target: they are small SVG circles, a tight tap target for a
younger child on a tablet.

## Open decisions

1. **Does a practice win feed mastery?** Simplest is no — the learner model then stays
   strictly "what the guided path demonstrated". The maintainer's position is that the
   mastery flag is not the point here ("If mastery flag is not touched or it's not
   succeeded, that is fine"), which favours not writing it.
2. **What happens after the pinned topic?** Keep serving items from it until the learner
   leaves (favours the repetition goal), or hand back to normal selection (which would
   throw a senior learner back to foundational nodes — jarring).
3. **Is `STALE_MASTERY_DAYS = 14` too long for the guided path anyway?** Independent of
   this feature, and a one-constant change if so.

## Build plan (2026-08-18) — executed as written

**Principle: pinning changes WHICH node feeds the loop, never the loop.** The product's
determined learning experience — question → answer → deterministic verify → help → worked
example → recheck → probe — is already the "exam that then shows you how" shape the
maintainer described. A pinned-topic session is that same FSM with node selection held
constant. No practice mode, no quiz UI, no second answer path.

Two things fall out of the existing code for free, verified against it:

* **The exam shape needs no code.** `_do_branch_decision` already ends every session
  warmly at `max_items` (`MENTAR_SESSION_ITEMS`, default 10). A pinned session inherits
  it: pick a topic → ~10 questions on it → "That's a great session". Re-entering the
  topic later IS the repetition ask. This resolves open decision 2.
* **Probes survive pinning.** `probe_due` fires from `_do_branch_decision`
  (`items_since_probe` / mastery threshold), NOT from node selection — so a pinned
  session keeps understanding-checks. Only interleave and spaced-review injection are
  bypassed, which is exactly what "stay on this topic" means.

### Decision on mastery (open decision 1): let it write, unchanged

A pinned session runs the real verifier on real answers — that is genuine evidence, not
practice noise. Letting `_do_bkt_update` run untouched is BOTH the smallest diff (zero
branches in the BKT path) and philosophically sound. The maintainer has said either way
is fine. Consequence to accept knowingly: mastering a jumped-to node does NOT unlock its
neighbours for guided selection until its prereqs are also mastered — correct behaviour,
worth a line in the topic page's UI copy ("guided lessons still build up to this").

### Changes, smallest-diff order

**1. `dialogue/controller.py` — one param, one branch, one checkpoint field (~15 lines)**

* `SessionController.__init__` gains `pinned_node: str | None = None`. Validate it is in
  `self._curriculum` at construction and raise `ValueError` otherwise — fail loud at the
  seam, not silently mid-session (same posture as the A9 coverage check).
* `_do_node_select`: if `self._pinned_node` and it is not yet at the session cap, set
  `next_node = self._pinned_node` instead of calling `select_next()`. Every re-entry to
  NODE_SELECT (post-probe, post-help) passes through this one function, so one branch
  covers all paths.
* Checkpoint: add `"pinned_node"` to the dict written by `update_session_checkpoint` and
  read it back in `_do_session_start` via `cp.get("pinned_node")` — additive, old
  checkpoints read as un-pinned. Without this a server restart silently converts a
  pinned session into a guided one.

**2. `web/app.py` — extend `/choose`, add `/topics` (~35 lines)**

* `POST /choose` accepts an optional `topic` form field. If present and in
  `_SUBJECT_CURRICULA[subject]`, store it in `session["pinned_node"]` AND pop the
  existing controller (a pinned session is always a fresh session); if absent, clear
  `session["pinned_node"]`. Invalid topic → ignore, fall through to normal choose (a
  stale link degrades to a guided session, never a 500).
* `_get_or_create_controller` passes `session.get("pinned_node")` through to the
  constructor. It already pops the controller on subject switch; the pop-on-pin above
  reuses the same idiom.
* `GET /topics?subject=<key>`: renders every concept of that subject from
  `_SUBJECT_CURRICULA` (which covers never-attempted nodes — the star-card gap named
  above), in the graph's topological order, each as a one-tap POST form to `/choose`
  with `subject` + `topic`. Show existing mastery as the star rating where a
  `skill_state` row exists. Child-facing page: same visual language as the picker,
  NO `_GROWN_UP_PREFIXES` entry (see "does not need delineation" above).

**3. `web/templates/subjects.html` — the visible affordance (~8 lines)**

The card is a `<button type="submit">` wrapping the whole tile, so the link must be a
SIBLING: wrap card+link in a `div`, button unchanged, and under it one link —
**“🎯 Jump to a topic”** → `/topics?subject=<key>`. Maintainer requirement: this must be
plainly visible on the front-page card, not discoverable-only-via-progress.

`/progress` footer gains the same link for the current subject (cheap, consistent), but
the CANONICAL entry is the front-page card.

**4. New `web/templates/topics.html`** — list page per subject. Reuses `.subject-card`
styling; no new JS; no htmx needed (full-page nav is fine here, same rationale as the
progress switcher).

### What is deliberately NOT touched

`engine/fringe.py`, `engine/bkt.py`, `eval/verify_numeric.py`, all of `safety/`,
`answer_modes.py`, `_turn.html`, `/answer`. The escalation classifier and output guard
sit inside the turn path the pinned session reuses — the tests below prove that rather
than assert it.

### Tests (all through the real request path — "code reads correct" is not evidence)

* **Controller:** pinned session serves ONLY the pinned node across N items; probe still
  fires at `PROBE_EVERY_N`; cap ends the session warmly; checkpoint round-trips
  `pinned_node` (simulated restart resumes still-pinned); unknown `pinned_node` raises
  at construction.
* **Web:** `/topics` lists every curriculum node including never-attempted ones;
  `POST /choose` with `topic` → `/learn` serves a question drawn from that node
  (assert via the item's node id, not page text); invalid/stale topic falls back to a
  guided session with no error; switching subject clears the pin.
* **Safety (the load-bearing one):** mid-pinned-session, a disclosure phrase →
  ESCALATION_FREEZE, exactly as in a guided session. If this test cannot be written, the
  implementation took the forbidden shortcut.
* **Browser (1 case):** the card shows the Jump link; tapping through lands on a
  question. Geometry-level tap-target check on the topic list.

### Rollout

One PR, additive throughout; no schema change (checkpoint is JSON), no config, no new
dependency. If the senior-depth work (§ Related) lands later, this page gets richer with
zero further changes — the list renders whatever the template declares.

## What this feature does NOT need

Earlier discussion treated parent/child delineation as a prerequisite, on the grounds that
a child would abuse a skip control. That reasoning does not hold: **skipping to work you
cannot do is self-punishing**, not a shortcut — there is no reward to chase, and the
learner meets harder material immediately. Delineation remains a real and separate topic
(see § Related) but does not gate this.

Seeding prerequisite mastery to unlock a topic was also considered and is NOT proposed
here — pinning the node sidesteps the fringe entirely, so no concept has to be falsely
recorded as mastered.

## Related

* Senior-year **content depth** limits how useful this is per year: AU maths has 4
  concepts at Year 9, 4 at Year 10, 4 at Year 11, 3 at Year 12, and no quadratic-equation
  solving anywhere. Jumping works identically at every year; there is simply less to jump
  to in the senior ones. See
  [`comprehensive_math_templates_reference.md`](comprehensive_math_templates_reference.md).
* Parent/child delineation: the grown-up-page guard is a **location** boundary, not an
  identity one, and is absent entirely outside `--lan` mode. Separate work; noted in
  [`../PHASE0_STATUS.md`](../PHASE0_STATUS.md).
