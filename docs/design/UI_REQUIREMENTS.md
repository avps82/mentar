---
title: "UI Rebuild — Requirements"
version: v0.1
status: "Requirements ratified 2026-07-10; design + per-screen specs = next phase (not started)"
last-updated: 2026-07-10
owner: maintainer (ratified) / Opus (drafted)
sources: "docs/design/W6.3_pilot_interface.md (supersedes its 4-view minimalism for look-and-feel only); SESSION_FSM.md; SAFETY.md L2/L5; AGENTS.md RULES; PHASE0_STATUS backlog (web display row)"
---

# UI Rebuild — Requirements

Requirements only — no visual design, no implementation in this doc. The next phase
(mockups + per-screen tight specs for gemma4:12b, one spec per screen tracing to the U-IDs
below) starts only after the open decisions in §7 are made.

**Why.** The current web UI is six minimal Jinja templates (~230 lines, inline CSS). It
works, but looks like a scaffold: nothing on screen says what Mentar *is* — local, private,
safety-first, real mastery model. Before the repo goes public the UI must act as the lure:
a parent who opens it should instantly read "trustworthy + substantial", and README
screenshots should look like a real product to OSS visitors.

**Ratified framing (maintainer, 2026-07-10):** audiences = parents evaluating + OSS
visitors; NO separate landing/about page — the polished flows themselves carry the story;
tech envelope = §5 recommendation.

---

## 1. Purpose & success criteria

- **U-1** The UI must communicate, on every screen, without reading docs: *local & private*
  ("runs 100% on this device — no cloud, no accounts"), *safe by design* (parent in control),
  and *substantial* (a real mastery model, not a chat wrapper).
- **U-2** Three screens must be screenshot-worthy for the README/repo page: the lesson
  screen, the progress/mastery map, and the parent dashboard. "Screenshot-worthy" = a
  stranger seeing the image understands the product and wants to try it.
- **U-2a** Actual README screenshots ARE a required deliverable of the UI work — but they
  are taken and committed **only after the maintainer has reviewed and approved the built
  front end**, never from an unreviewed build. (Sequence: build → maintainer review →
  screenshots → README.)
- **U-3** A parent's first 60 seconds (open app → choose subject → see one question → glance
  at parent view) must surface all three U-1 messages without any instructional text walls.

## 2. Scope

In scope: restyling + restructuring of the six existing flows — subject choose, learner
lesson, child progress, parent dashboard, frozen (escalation), done — as a **presentation
layer only**. Out of scope: any change to FSM/controller behaviour, routes/form contracts,
safety logic, DB, or new product features (see §6).

## 3. Functional requirements

### Global (all screens)
- **U-10** One consistent visual identity: named palette, one display + one text typeface
  (locally bundled, licence-cleared), a simple Mentar wordmark/mark. No per-template ad-hoc
  styles; one shared stylesheet.
- **U-11** A persistent, quiet trust strip (header or footer): "Runs entirely on this
  device · no cloud · no accounts" — present on child AND parent screens.
- **U-12** Responsive from ~360 px (phone) through tablet to desktop; tablet is the likely
  child device. Touch targets ≥ 44 px on child screens.
- **U-13** Child-facing text: large type (≥ 1.2 rem body on lesson screens), high contrast
  (WCAG AA), reading level suitable for age 8–10, never rely on colour alone for meaning.
- **U-14** All existing routes and form contracts unchanged (`GET /`, `POST /answer`,
  `POST /choose`, `GET /progress`, `GET /parent`, `POST /parent/ack`, frozen redirect
  behaviour) so `tests/web/` churn is minimal and the controller is untouched.

### Subject choose
- **U-20** Subject cards with icon, label, one-line kid-friendly description, and a small
  per-subject progress cue (e.g. "3 of 8 skills mastered") when history exists.
- **U-21** Carries the product one-liner ("Your private learning helper — everything stays
  on this computer") — this is the closest thing to a landing moment, per the no-landing
  decision.

### Learner (lesson)
- **U-30** The current pending question renders in its own **stable block** that never
  disappears when a turn returns feedback/hint only (root-fixes the known question-vanish
  issue at the view layer instead of the controller re-append workaround).
- **U-31** Transient content (feedback, praise, hints) renders in a visually distinct area,
  separate from the question; correct/incorrect feedback visibly distinct (icon + colour).
- **U-32** Model output renders safely: HTML-escape everything first, then a minimal owned
  markdown subset (bold, italics, bullets) — nothing else interpreted. A
  `<script>` in model output must render inert; this is a hard acceptance test.
- **U-33** Help and Stop are visible child-sized buttons (not only typed `?`/`stop`);
  pressing them submits exactly the strings the controller already recognises — no new
  intents. The typed forms keep working.
- **U-34** Per-skill progress cue visible during the lesson (e.g. small mastery bar for the
  current skill) — makes the mastery model tangible mid-lesson (U-1 "substantial").
- **U-35** The first-turn assent + transparency lines ("you can stop anytime…", "I'm Mentar,
  a computer learning helper — not a person") get deliberate visual treatment, not lost in
  message flow — they are a feature, not boilerplate.
- **U-36** Emoji already emitted by itemgen render at a friendly size; input keeps
  autofocus; Enter submits.

### Child progress
- **U-40** The concept graph becomes the centrepiece: the pilot's 8-node fractions DAG shown
  as a map (nodes + prerequisite edges) with per-node mastery states (not started / learning
  / mastered) in child-readable form. This is the flagship screenshot (U-2) — it is what
  visibly differentiates Mentar from a chat wrapper.
- **U-41** Rendered with owned SVG/canvas generated from the loaded curriculum template —
  works for any template (node count/edges not hardcoded), no graph library dependency.
- **U-42** Encouraging, non-judgemental framing (no red "failed" states child-side).

### Parent dashboard
- **U-50** Restructure into scannable sections in this priority order: safety alerts (if
  any) → session summary → mastery per skill → answers → full transcript (collapsed by
  default). A parent glancing for 10 seconds sees "is my child OK, what did they do, what
  did they learn".
- **U-51** All existing safety behaviours preserved exactly: escalation alert with verbatim
  trigger text (parent-side only), typed confirm-word `RESUME` gate, end-session action,
  degraded-logging banner when `escalation_fallback.log` is non-empty. Styling may change;
  semantics, wording of handoff messages, and the confirm mechanism may not.
- **U-52** Mastery visualisation consistent with the child progress map (same colour
  language), plus the numeric % parents were promised.

### Frozen (escalation) — child side
- **U-60** Calm, low-stimulus design; shows ONLY the two fixed handoff messages (invariant
  unchanged); no navigation to parent view, no trigger text, no controls. Tone: reassuring,
  not alarming.

### Done
- **U-70** Celebration + simple session recap (questions tried, skills touched), pointer to
  progress map. Child-appropriate; no dark-pattern "keep playing" pressure.

## 4. Non-functional requirements (the hard constraints)

- **U-80 Offline-absolute:** zero non-localhost requests. No CDN fonts, JS, CSS, analytics,
  favicons. Every asset ships in the repo, licence-logged (same discipline as
  CONTENT_LICENSES.md / LICENSE_AUDIT.md; assets must be AGPL-compatible).
- **U-81 Auditable JS:** total third-party runtime JS is either zero or a single vetted,
  vendored, pinned micro-library (see §5). Every shipped JS line reviewable in one sitting —
  this is a kids'-safety product; the webview is a trust boundary.
- **U-82 Safety invariants untouched:** child input never reaches the LLM (AGENTS.md RULES);
  frozen-state rendering rules; parent-ack gating; no trigger text child-side. UI work is
  presentation-only — any requirement here that seems to need a controller change goes back
  to the maintainer instead.
- **U-83 Low-end friendly:** no heavy animation/transitions; usable on the modest-hardware
  deployment envelope (same machines that run the local LLM); lesson page payload budget
  ≤ ~100 kB total (excluding fonts).
- **U-84 Keyboard + screen-reader basics:** logical tab order, labelled inputs, semantic
  headings/landmarks; not full WCAG certification, but nothing actively hostile.
- **U-85 Testable:** existing `tests/web/` assertions on content (handoff text present,
  trigger text absent, confirm-word no-op, banner presence) keep passing; new requirements
  above marked "hard acceptance test" (U-32) get tests.

## 5. Tech envelope — recommendation (the "why not full JS" question)

**Recommendation: server-rendered Flask/Jinja + one shared owned stylesheet + small owned
vanilla JS, optionally ONE vendored micro-library (htmx, MIT, ~14 kB) for no-reload turn
submission. No SPA framework for this rebuild.**

Why a full framework (React/Vue/Svelte) is the wrong shape *here*, not a generic objection:

1. **The app is a form-post loop.** The FSM lives server-side in `SessionController`; every
   turn is POST → new state → render. A SPA duplicates that state client-side and forces a
   JSON API layer that doesn't exist today — new surface, new bugs, for the same screens.
2. **Audit surface & supply chain.** A React build ships hundreds of transitive npm
   packages into a child-facing webview of a safety-first product. U-81 becomes
   unenforceable; today's promise ("every line auditable") is a real differentiator in the
   README, not a limitation.
3. **Offline & longevity.** No build step means a parent (or contributor) can read the
   repo and see exactly what the browser gets; nothing bit-rots with node/toolchain drift.
   This matches the project's local-first, boring-over-clever posture
   (dependency-philosophy: own the thin glue).
4. **"Modern-looking" is a CSS problem, not a framework problem.** Everything in §1–§3 —
   cards, progress map, animated mastery bars, distinct feedback states — is achievable
   with modern CSS + small vanilla JS/SVG. The one place frameworks genuinely help
   (rich interactive widgets) is the W6.5 manipulatives work, which is explicitly
   post-pilot — and even that was scoped as small owned widgets.
5. **The escape hatch stays open.** If Phase-1 manipulatives outgrow vanilla JS, a
   framework can be adopted *then*, for that widget layer, with this rebuild's clean
   template/CSS structure intact. Nothing in this rebuild forecloses it.

Where the "backend-only won't be enough" instinct is right: full-page reloads on every
answer feel dated, and a static page can't do satisfying feedback moments. That's what the
ONE micro-library (htmx: swap the question/feedback fragments over the existing POST, no
reload) plus CSS transitions solve — the modern feel, ~14 kB of auditable vendored JS, zero
build step. If even that is unwanted, vanilla `fetch` + fragment swap (~30 lines owned JS)
does the same.

## 6. Out of scope (recorded so they're not silently expected)

- Landing/about page (maintainer decision: flows only), manipulatives (W6.5), ZIM media
  (W7.6), i18n, PIN gate (Phase 1), any new child intents or FSM states, markdown beyond
  the U-32 subset, accounts/multi-learner UI (single-learner pilot), dark mode.

## 7. Open decisions for the maintainer (block the *design* phase, not this doc)

- **U-90** htmx (vendored) vs zero-dep owned JS snippet (§5). Both satisfy U-80/U-81; htmx
  is less code to own, the snippet is zero third-party.
- **U-91** Brand direction: keep 🍕-style playful emoji identity vs a drawn mascot/wordmark
  (a mascot needs an artist or generated asset + licence decision).
- **U-92** Palette preference (current warm cream/green vs something else) — pure taste,
  cheap to decide now, expensive to churn later.

## Changelog

| Date | Change |
|------|--------|
| 2026-07-10 | v0.1 — requirements drafted + ratified by the maintainer (audiences, no-landing, U-2a screenshot gate). Design phase not started. |
