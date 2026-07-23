---
type: Mentar Design Doc
title: "UI Rebuild — Requirements"
version: v1.0
status: "Requirements ratified + BUILT 2026-07-10 (all 6 flows). U-2a maintainer review completed 2026-07-10 (§9 build log). R4-R6 follow-ons built 2026-07-11."
last-updated: 2026-07-22
owner: maintainer (ratified) / Opus (drafted + built)
sources: "docs/design/W6.3_pilot_interface.md (supersedes its 4-view minimalism for look-and-feel only); SESSION_FSM.md; SAFETY.md L2/L5; AGENTS.md RULES; PHASE0_STATUS backlog (web display row)"
---

# UI Rebuild — Requirements

Originally scoped as requirements-only, with mockups + per-screen gemma specs as a later
phase. The maintainer directed a live, autonomous build the same session (once U-90/U-91/U-92
were decided) rather than the phased mockup→spec→gemma path — see §8 for exactly what shipped,
what deviated from the letter of a requirement and why, and what's still open.

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

- **U-90 RESOLVED 2026-07-10 — htmx vendored + wired, shipped.** First attempt: the
  harness's own permission classifier blocked fetching htmx from an external CDN on the
  maintainer's verbal say-so (a real-world instance of the U-81 "auditable JS" trust
  boundary — external-code fetches require a human-typed command, not chat authorization).
  Shipped a zero-dep owned-JS stopgap (`turn.js`) so plumbing wasn't blocked. Maintainer
  then typed the fetch command directly (`!` prefix), which cleared the boundary; htmx
  2.0.9 vendored at `src/mentar/web/static/htmx.min.js` (pinned latest-stable tag, sha256
  logged in `docs/LICENSE_AUDIT.md`). Maintainer explicitly asked for a **clean htmx
  adoption, not a hybrid** — `turn.js` deleted; `/answer` rewired to native htmx idioms
  (`HX-Request`/`HX-Redirect` headers) instead of the earlier custom JSON contract;
  `learner.html`'s form now uses `hx-post`/`hx-target`/`hx-swap` declaratively, zero owned
  JS. This required one small real architecture addition: completion (`done`) had no
  standalone URL (rendered inline from the `POST /answer` body), and `HX-Redirect` needs a
  real route to target — added `GET /done` (+ a small `_done_messages` per-learner dict,
  same pattern as `_turn_logs`/`_db_learner_ids`) and unified BOTH completion paths
  (`/` on first-turn-done, and `/answer` on later-turn-done) through it, removing the
  inline-render duplication. Fragment responses are HTML-escaped
  (`markupsafe.escape`, matching Jinja's existing `{{ question }}` autoescaping) since
  htmx swaps via `innerHTML` — pulled the U-32 escaping requirement forward as a live test
  rather than deferring it. Licence text for htmx is still pending verification (noted in
  LICENSE_AUDIT.md) — same external-fetch boundary, queued for whenever the maintainer is
  next at a terminal. Tests: `tests/web/test_app_smoke.py::test_answer_hx_request_returns_
  question_fragment`, `::test_answer_hx_fragment_escapes_html`, `::test_answer_hx_request_
  on_escalation_sends_hx_redirect`, `::test_done_route_shows_final_message_and_is_directly_
  navigable`. 469 tests green, ruff clean.
- **U-91 RESOLVED 2026-07-10** — kept the 🍕-style emoji identity (maintainer's explicit
  pick, the recommended option: zero new assets, zero licensing, buildable autonomously).
  No mascot work done or planned.
- **U-92 RESOLVED 2026-07-10** — maintainer wanted "something between" the Calm & Trustworthy
  (teal/amber) and Bright & Modern (indigo/pink) preview options, **plus a light/dark toggle**
  as a nice-to-have. Shipped as CSS custom properties in `static/style.css`: primary `#2F8F9D`
  (a blended teal — more saturated than the calm option, less purple than the bright one),
  accent `#FF7F50` (coral, between amber and pink-coral), background `#F9FAFC`. Dark variant
  under `[data-theme="dark"]` with contrast-adjusted equivalents (primary `#5FC9D6`, accent
  `#FF9776`, bg `#16202A`). Toggle: `static/theme.js` (~20 lines, owned, no deps) — reads
  `prefers-color-scheme` for the initial value, persists an explicit user choice in
  `localStorage`, flips a `data-theme` attribute on `<html>`.

## §8 — Build log (2026-07-10, all 6 flows, same session as requirements ratification)

Built directly against this doc's U-IDs once U-90/91/92 were decided; maintainer directed a
live autonomous build ("do the rest... until all is completed") rather than the phased
mockup→spec→gemma path originally scoped. Architecture: one shared `templates/_base.html`
(header/trust-strip/theme-toggle/footer blocks) all 6 page templates now `{% extends %}`,
one shared `static/style.css` (CSS custom properties, no per-template inline styles — U-10).
472 tests green (was 463 pre-session), ruff clean, end-to-end content-level verification run
against a live Flask test client for every screen (no rendered-pixel screenshot — see the gap
note below). Per-screen:

- **Subjects (U-20/U-21):** cards gained `icon`/`description` fields (added to the `SUBJECTS`
  dict in `web/app.py`, presentation metadata only) + a per-subject "N of M skills mastered"
  cue via new `_subjects_progress()` helper — only shown when a store already exists for that
  learner (never triggers a fresh DB connection just to render the picker). Product one-liner
  added per U-21.
- **Learner/lesson (U-30–U-36):** htmx fragment-swap (already shipped, U-90) now targets a
  `.question` block that also carries a `first-turn` class + distinct border when the
  assent/transparency lines are present (U-35) — detected via `is_first_turn` computed from
  `ctrl.state == SESSION_START` before calling `step()`, not string-matching the rendered
  text. Visible Help/Stop buttons added (U-33) as two small satellite forms hitting the same
  `/answer` route with the identical recognized strings (`"help"`/`"stop"`) — no new intents,
  typed input still works. Per-skill mastery bar (U-34) added via a new
  `SessionController.current_node_id` read-only property (small, additive, no FSM behaviour
  change) + `_current_node_mastery()` helper.
  **U-32 RESOLVED (fully, not just escaping):** the first htmx pass only escaped model/
  generator text; added `_render_markdown_lite()` after re-checking against the requirement
  text — escapes first (the security property, tested against a `<script>` payload), then
  substitutes ONLY 4 whitelisted tags (`<strong>`/`<em>`/`<ul>`/`<li>`) for `**bold**`,
  `*italic*`, and `* `/`- ` bullet lines; bold is substituted before italic so a bold span's
  stars are consumed first; bullet markers are stripped per-line before the italic regex runs
  so a leading `* ` is never misread as an emphasis delimiter. Wired into BOTH the htmx
  fragment path and the full-page path (`index()` now passes `question_html` through the same
  function, rendered via `{{ question_html | safe }}`) so they never visually disagree — this
  was checked explicitly with a live full-page-load test after the first fragment-only version
  shipped. Segment joining avoids inserting a raw `\n` next to `<ul>`/`<li>` tags (the
  `.question` block is `white-space:pre-wrap`, so a stray newline next to a block element would
  render as a visible gap) — caught by tracing the join logic by hand before shipping, not by
  a failing test. Tests: `test_markdown_lite_renders_bold_italic_and_bullets`.
  **U-31 RESOLVED 2026-07-10 (second pass, no controller data-contract change needed):**
  initially flagged as needing a `TurnResult` change; re-examined and solved at the view
  layer. The controller joins per-state outputs with `\n\n` and the pending question is the
  FINAL segment in every await state, so `_split_turn_text()` splits at the LAST occurrence
  of the (newly exposed, read-only) `SessionController.current_question` — everything before
  it renders in a distinct `.feedback` area, everything from it onward (question + format
  hint) in the stable `.question` block. Both areas render via the shared `_turn.html`
  partial, included on full-page loads AND returned bare as the htmx fragment
  (`hx-target="#turn-area"`), so the two paths cannot disagree. Graceful degradation: if the
  question isn't found in the text (or is at position 0, the Help `Q) …` shape), no split —
  the whole text renders in the question block, which is exactly the pre-U-31 behaviour.
  Tests: `test_turn_split_feedback_from_question` (pure splitter cases + live view + htmx
  fragment).
- **Progress/concept map (U-40–U-42):** new `_compute_graph_layout()` in `web/app.py` — a
  pure, owned layered-DAG layout (level = 1 + max(prereq levels), percentage coordinates, no
  graph library) rendered as an SVG in `progress.html`. Verified against the real 8-node
  pilot fractions curriculum: 8 nodes, 7 edges, correct branch shape. Works for any curriculum
  (arithmetic/science templates too — node count isn't hardcoded). The old star-card list
  stays underneath as a supplementary "how you're doing in detail" view (kept, not replaced —
  it was already tested and working; U-40 says the graph becomes the *centrepiece*, not the
  *only* view).
- **Parent dashboard (U-50–U-52):** reordered into safety-alerts → session-summary → mastery →
  answers → full transcript (U-50); every literal string the safety tests assert on (`"correct
  out of"`, `"Mastery progress"`, `"RESUME"`, confirm-word no-op, `"Durable logging degraded"`)
  preserved byte-for-byte — only wrapped in `.card` styling and reordered. Transcript now a
  `<details>` element, collapsed by default. Header block overridden to drop the theme-toggle/
  brand-emoji chrome (keeps the trust strip) for a more serious tone on this screen.
- **Frozen (U-60):** header/footer blocks emptied entirely — no brand link, no theme toggle,
  no nav of any kind, verified via a new test (`<a ` and `theme-toggle` both absent from the
  rendered HTML) in addition to the pre-existing trigger-text/confirm-word absence checks.
- **Done (U-70):** new recap (questions answered, correct count, help count, skills touched)
  sourced through the exact same `store.session_responses`/`session_help_events` calls already
  used by `/parent` — no new store methods. Added a "See my progress map" link alongside
  "Start again".
- **Verification gap (be explicit, per CLAUDE.md's UI-testing instruction):** no headless
  browser/screenshot tool is available in this sandbox (checked: no Playwright, no Chromium/
  Firefox binary, no wkhtmltoimage/cutycapt, no project run-skill for this app) and installing
  one would very likely hit the same external-fetch permission boundary documented under
  U-90. Verification here is therefore full content/structural assertions against a real
  Flask test client (every screen's HTML actually rendered and inspected, not just routes
  hit) — not a rendered-pixel check. This lines up with U-2a anyway: the maintainer reviews
  the actual running app before any screenshot is taken, which is the real visual QA step.

## §9 — Maintainer review round 1 (U-2a, 2026-07-10) — findings + resolutions

The maintainer reviewed the running rebuild (the U-2a gate). Findings and what shipped in
response, same session:

- **R1-1 (bug): feedback/question split broken in real use** — the Help flow's
  `Q) {question}` recap made the rfind-split land right after `Q)`: the feedback box showed
  a bare "Q)" ("there is a Q) box but it's empty, always") and the explanation landed
  bundled into the question block. **Fixed structurally, as the maintainer directed**
  ("have tags… so we can easily place it to the right spot"): `TurnResult` now carries
  `message` + `question` fields composed at the FSM-state source (the controller knows
  which part is which deterministically — no LLM tagging needed, and most turn text isn't
  LLM-generated anyway); `_split_turn_text` deleted; the `Q)` recap removed (the question
  stays visible in its own block). Verified live against the exact reported scenario.
- **R1-2: multiple-choice answers → radio buttons** — `Item` gained a structured
  `choices` tuple (mc generators return it; bank jsonl may carry a `choices` list); the
  answer widget in `_turn.html` renders a native radio group A–D (no JS needed) when
  choices are present. The widget lives inside the htmx swap target so it changes with
  each question.
- **R1-3: fraction answers (`_/_`) need a proper input** — fraction questions render
  numerator/denominator number inputs; `/answer` composes `n/d` server-side (verifier
  grammar unchanged, works with JS disabled). Other answer types keep the text input;
  "variations" (mixed numbers etc.) can extend the same widget switch later.
- **R1-4: more subjects/grades, Australian curriculum** — first two ACARA v9 templates
  shipped (`curriculum/templates/AU/year3_maths.md`, `year4_maths.md`, Number strand) +
  `engine/au_items.py` generators; ACARA core content verified CC BY 4.0 (codes referenced
  as alignment identifiers only — CONTENT_LICENSES.md §2b). The per-year pattern is now
  established; more year levels/strands extend it.
- **R1-5: text-to-audio for question + choices** — `static/tts.js` (owned, no deps): a 🔊
  button on the question block reads the question and choices via the browser's built-in
  `speechSynthesis` (local voices, no network — U-80/U-81 hold); hides itself where
  unsupported. ⚠️ Not verifiable in-sandbox (no browser/audio) — needs the maintainer's
  next hands-on look.

Still pending from U-2a: the maintainer's approval of the overall look → then README
screenshots.

### R3 — Year > Subject IA (2026-07-10 ask) — ✅ BOTH DONE 2026-07-11

Picker groups subjects by year ("Year 3 (AU)", "Year 4 (AU)", "Try-out topics" — derived
server-side from the R3.1 template-catalog scan, not hand-maintained); `/progress` gained
a year/subject switcher. Fixed a real defect found while speccing: the skill-card list
used to mix every subject's rows together — now filtered to the selected subject only.
Full detail: `docs/REMAINDER_PLAN.md` → "R3 — Year > Subject information architecture".

### R6 — bugs on AU Year 3's /progress: graph clipped + display names inconsistent
(2026-07-11, root-caused, NOT built)

R6.1 (small, isolated): the concept-graph's y-position formula and its SVG viewBox height
use two different uncoupled scales — R2.4 changed the height-per-level constant without
updating the y formula to match, so any curriculum with ≥3 levels clips its bottom row.
R6.2 (bigger, deliberately NOT patched — maintainer wants a ground-up pass): "Au3 Place
Value" exposed that skill_id → display-name logic is reimplemented FOUR different, mutually
inconsistent ways across `progress.html`/`learner.html`/`parent.html`/`done.html` — only
the concept-graph does it correctly today (joins to the curriculum's own authored label).
Full detail + the open design questions: `docs/REMAINDER_PLAN.md` → "R6".

### Review round 2 (2026-07-10, after round 1 shipped) — ✅ ALL FOUR (R2.1–R2.4) SHIPPED 2026-07-11

- **R2-1: MCQ options rendered three times** — inline in the question text ("A) a tree
  B) …"), again in the format hint ("answer with a letter: A, B, C or D"), again as
  radios; TTS reads the options twice. Fix direction (maintainer: "maybe this needs to be
  redone"): generators return the question STEM separately; one central composer builds
  the inline text for CLI/transcript surfaces; web shows stem + radios only, no hint.
- **R2-2: TTS restarts instead of pausing** — clicking 🔊 mid-read restarts the sentence.
  Fix direction (maintainer): three-state button — 🔊 idle → ⏸ speaking → ▶️ paused —
  via `speechSynthesis.pause()/resume()`, plus cancel-on-htmx-swap so a new question
  never plays over stale audio.

- **R2-3: configurable answer modes** — maintainer: "better to have config for different
  modes for answering things." The widget if/elif chain in `_turn.html` + the inline
  compose rule in `/answer` become a single owned registry
  (`web/answer_modes.py`: answer_type → widget / hint policy / form-compose fn) so new
  answering modes (mixed numbers, decimals-later, …) are one entry + one template branch.

- **R2-4 ✅ DONE 2026-07-11 (commit 83b9b1c): concept-map labels truncate mid-word** (/progress) — the SVG node labels were
  hard-cut at 14 chars ("Place value to", "Equivalent fra"), exposed by the longer AU
  labels. Fix direction: word-wrapped multi-line labels (`<tspan>` per line) computed in
  the pure layout function; never cut mid-word; full label stays as the hover tooltip.

- **R3 (new IA, not a bug): Year → Subject → parts** — maintainer direction for the
  picker and progress page, plus derive the year/subject catalog instead of hand-
  registering it. Decision: server-side front-matter scan of `curriculum/templates/`
  (templates are the source of truth; JS-disabled parity; no client fetch), with item
  sources referenced BY NAME via a registry (generators are code). Also fixes a real
  defect: /progress's star cards currently mix ALL subjects' skill rows into one list.

**Tight `[G]` specs live in `docs/REMAINDER_PLAN.md`** — "UI review round 2 (R2)" (four
tasks) and "R3 — Year > Subject information architecture" (two tasks). Execution order:
**R2.1 → R2.3 → R2.2, R2.4 anytime; then R3.1 → R3.2** (R2.3 folds R2.1's
hint-suppression into the registry; R2.2's audio depends on R2.1's stem; R2.4 is
independent; R3.2 renders what R3.1 discovers). R2.2 carries a manual hands-on checklist
since audio isn't verifiable in the build sandbox.

## Changelog

| Date | Change |
|------|--------|
| 2026-07-10 | v0.1 — requirements drafted + ratified by the maintainer (audiences, no-landing, U-2a screenshot gate). Design phase not started. |
| 2026-07-10 | U-90 resolved: htmx vendored + cleanly wired (no hybrid) after the maintainer typed the fetch command directly. New `GET /done` route; `X-Requested-With`/JSON contract replaced by native `HX-Request`/`HX-Redirect`; fragment responses HTML-escaped (U-32 pulled forward). 469 tests green. htmx `LICENSE` text still pending (same external-fetch boundary). |
| 2026-07-10 | U-91/U-92 resolved (kept emoji identity; blended teal/coral palette + light/dark toggle) and all 6 flows built same session per maintainer direction — see §8. U-32 completed properly (full markdown-lite render, not just escaping) after re-checking the requirement text against the first pass. 473 tests green, ruff clean. Known gap: U-31 (feedback/question visual split) needs a controller data-contract change, out of scope; flagged not silently dropped. No screenshot/pixel verification available in-sandbox — content-level Flask-test-client verification only, real visual QA is the maintainer's pending review (U-2a). |
| 2026-07-10 | **Maintainer review round 1 (U-2a) landed + all findings resolved same session — see §9.** Structured turn payload (TurnResult.message/.question) replaces the string-split entirely; mc4 radio buttons; fraction num/den inputs; TTS 🔊 (speechSynthesis, owned JS); ACARA Year 3 + Year 4 maths templates. 488 tests green. |
