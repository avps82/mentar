---
type: Mentar Design Doc
title: "htmx 4 Migration Plan (future, not urgent)"
version: v0.1
status: "MONITORING — htmx 4 is in beta (4.0.0-beta6 as of 2026-07-26), target stable release 'Summer '26' per htmx.org, explicitly not recommended for production by the htmx team itself. No migration work started. Revisit when a stable 4.0.0 ships."
last-updated: 2026-07-26
owner: maintainer (ask) / Opus+Sonnet (research)
sources: "Live-checked 2026-07-26: github.com/bigskysoftware/htmx/releases, htmx.org, four.htmx.org/docs (the official v4 info hub) -- not written from memory/assumption. docs/LICENSE_AUDIT.md (current pin: htmx 2.0.9). curriculum/../src/mentar/web/templates + static/*.js (Mentar's actual usage, checked directly)."
---

# htmx 4 Migration Plan

**Why this exists.** The maintainer asked to plan ahead for htmx 4 while noting it's currently in
beta. This document records what was actually verified (not guessed) about htmx 4's status and
which of its breaking changes genuinely affect Mentar's current usage — most don't.

## Current state (verified)

- Mentar vendors **htmx 2.0.9** (`src/mentar/web/static/htmx.min.js`, sha256-pinned per
  `docs/LICENSE_AUDIT.md`), loaded via `<script src="/static/htmx.min.js" defer>` in `learner.html`.
- Live-confirmed usage (this session): `hx-post="/answer" hx-target="#turn-area"
  hx-swap="innerHTML"` in `learner.html` and `_turn.html` — the core mechanism that swaps in the
  next question/feedback without a full page reload (`UI_REQUIREMENTS.md`'s U-90 requirement).
  Not decorative — load-bearing for the main tutoring loop.

## htmx 4 status (checked live, 2026-07-26 — do not trust this section without re-verifying if read much later)

- **Beta**, latest tag `4.0.0-beta6`. Target stable release: **"Summer '26"** per the official
  htmx.org homepage. The htmx team's own guidance: *"Not yet recommended for production
  deployment."*
- Official v4 info hub: `four.htmx.org` (`/docs`, `/reference`).
- An automated migration scanner exists for when the time comes:
  `npx htmx.org@4.0.0-beta6 upgrade-check -- ./path/to/project/root`
- A compatibility extension (`htmx-2-compat`) exists to restore v2 behavior temporarily during a
  gradual migration, if that path is preferred over a clean cutover.

## What actually changes in v4, and whether it affects Mentar (checked, not assumed)

| v4 change | Affects Mentar today? | Detail |
|---|---|---|
| **Event names go camelCase → colon-separated** (`htmx:afterSwap` → `htmx:after:swap`) | **YES — one confirmed required change.** | `src/mentar/web/static/tts.js:88` listens for `htmx:afterSwap` (the read-aloud-after-swap hook). This listener would silently stop firing on a v4 upgrade unless renamed. The smallest, most concrete action item in this whole plan. |
| **4xx/5xx responses swap into the target by default** (v2 suppressed them; only 204/304 don't swap in v4) | **No — checked, not currently a risk.** | The only htmx-wired route is `/answer` (`hx-target="#turn-area"`), and it only ever returns `200` (with an `HX-Redirect` header for the escalation-freeze/frozen-page special cases) — confirmed by reading `web/app.py`'s `/answer` handler directly. The routes that DO return 4xx/5xx (curriculum pack install/settings JSON APIs) are NOT wired via `hx-post`/`hx-target` — they're plain JSON endpoints, unaffected. **Re-check this row if any NEW route ever gets both an `hx-*` wiring AND a non-2xx response path — the assumption would need re-verifying, not just re-copying.** |
| **Attribute inheritance becomes explicit** (an `hx-target` set on a parent no longer implicitly applies to children; needs an explicit `:inherited` modifier) | **No — checked.** | Every `hx-post`/`hx-target`/`hx-swap` in Mentar's templates is set directly on the element that uses it (the `<form>` itself), not inherited from an ancestor. No implicit-inheritance reliance found. |
| **Out-of-band (`hx-swap-oob`) swap ordering reversed** | **No — not used at all.** | Zero matches for `hx-swap-oob` anywhere in `src/mentar/web/templates/`. |
| **Native `fetch()` instead of `XMLHttpRequest`** | **No — transparent.** | No Mentar code hooks into htmx's internal XHR objects or assumes XHR-specific behavior. |
| **Native HTML5 form validation** (custom validation needs `hx-validate="true"`) | **Needs a quick check at migration time, not verified false here.** | Mentar's answer forms use plain `<input>` widgets (`web/answer_modes.py`) without custom JS validation logic today, so this is *likely* a non-issue, but wasn't exhaustively checked against every widget type — flag for the actual migration pass, don't assume clear from this document alone. |

## Recommendation

**Do nothing yet.** htmx 4 is explicitly pre-production per its own maintainers, with no stable
release date beyond "Summer '26." Revisit this document once a **stable 4.0.0** ships (not another
beta) — at that point:

1. Run `npx htmx.org@4.0.0-beta6 upgrade-check -- .` (or whatever the stable release's equivalent
   command is) for an automated, current scan — don't rely solely on this document's table, which
   is a snapshot.
2. Rename `tts.js`'s `htmx:afterSwap` listener to the v4 event name (confirm the exact final name
   against the stable release's docs — beta6's naming isn't guaranteed to be the shipped name).
3. Re-verify the "no htmx route returns non-2xx" assumption against whatever routes exist by then.
4. Re-pin `docs/LICENSE_AUDIT.md`'s htmx entry (currently 2.0.9) and re-verify the sha256/license
   text, following the same vendoring convention already established for 2.0.9.
5. Decide cutover vs. gradual (`htmx-2-compat`) based on how much else has changed in Mentar's
   templates by then.

**Not scoped or estimated as an active task** — this is a monitored future item, logged so it
doesn't need re-researching from scratch when it becomes relevant.
