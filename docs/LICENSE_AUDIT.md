---
type: Mentar Audit Doc
title: License Audit (dependencies + bundled content)
description: Status input for the W4.2 OSS-license decision — dependency graph, vendored code, and content licences. Informs the choice, does not make it.
tags: [license, audit, compliance, oss]
timestamp: "2026-07-22T00:00:00Z"
---

# License Audit (dependencies + bundled content)

Status input for the **W4.2 OSS-license decision** — this audit *informs* the choice, it does
**not** make it. Generated 2026-06-26. Re-run when dependencies change.

## TL;DR — the dependency graph constrains the choice

> **⚠️ STALE FINDING — corrected 2026-08-12.** The TL;DR below dates from when `libzim` was a
> *core* dependency. It no longer is: `pyproject.toml` moved it to the optional `[grounding]`
> extra (imports are lazy; grounding degrades to "" without it). Verified against installed
> metadata 2026-08-12: every CORE dependency is permissive or weak-copyleft — pyyaml MIT,
> openai Apache-2.0, sympy BSD, pint BSD, inflect MIT, num2words **LGPL** (weak copyleft:
> fine to depend on as a library; does not force the project's licence). **Nothing in the
> core forces GPL/AGPL any more.** AGPL remains a *choice* (and a defensible one), not a
> constraint. A permissive or source-available licence is now viable, with the `[grounding]`
> extra remaining GPL-encumbered for whoever opts into it. Additional facts relevant to any
> relicensing decision, verified the same day: all 427 commits are the maintainer (no external
> contributors — no third-party copyright to clear), and the repo is still private (no one has
> yet received the code under AGPL, so a licence change today has zero downstream effect).

**`libzim` (python-libzim) is `GPL-3.0-or-later` and ~~a *core* dependency~~ (now the optional `[grounding]` extra — see the stale-finding note above).** This was the single
decisive fact:

- **AGPL-3.0 for Mentar → compatible** with the GPL libzim core. ✅
- **Permissive (MIT / Apache-2.0) for Mentar → NOT viable** for the *combined distribution* while
  libzim is a core dep — the GPL is copyleft, so the distributed whole would have to be GPL. To
  ship a permissive edition you'd have to make `libzim` an **optional** extra and provide a
  non-GPL grounding path.

This reinforces the earlier recommendation (**AGPL-3.0 + CLA**) — it's now partly *forced* by the
graph, not just a strategy preference.

## Dependencies

| Package | Scope | License | Distributed with Mentar? | Verdict |
|---|---|---|---|---|
| **libzim** | core | **GPL-3.0-or-later** | yes (import) | ⚠️ **copyleft — drives the license choice** (see TL;DR) |
| pyBKT | offline eval only (not in runtime hot path — see W3.3) | MIT | optional dev dependency | ✅ permissive |
| openai (client) | core | Apache-2.0 | yes | ✅ permissive |
| pyyaml | core (+ vendored) | MIT | yes | ✅ permissive; `.vendor/yaml` ships its LICENSE |
| flask | optional `web` | BSD-3-Clause | only if `web` installed | ✅ permissive |
| ollama | optional `inference-ollama` | MIT | optional | ✅ permissive |
| psutil | optional `setup` | BSD-3-Clause | optional | ✅ permissive |
| smbprotocol | optional `nas` | MIT | optional | ✅ permissive |
| pytest / pytest-cov / hypothesis / ruff | dev | MIT (et al.) | no (dev-only) | ✅ not distributed |

## Bundled / vendored code

- **`.vendor/yaml` = PyYAML 6.0.x (MIT)** — vendored *with* its `LICENSE`. Compliant. Removing it
  would *add* a dependency (wrong direction); keep.
- **`src/mentar/web/static/htmx.min.js` = htmx 2.0.9** (`bigskysoftware/htmx`), pinned to the
  latest stable non-beta tag (confirmed via GitHub's releases API 2026-07-10), fetched from
  `https://unpkg.com/htmx.org@2.0.9/dist/htmx.min.js`, sha256
  `57d9191515339922bd1356d7b2d80b1ee3b29f1b3a2c65a078bb8b2e8fd9ae5f`. Serves the web UI's
  progressive-enhancement fragment swap (`docs/design/UI_REQUIREMENTS.md` U-90) — Flask serves it
  as a plain static asset, not a Python import. ⚠️ **Licence text not yet verified/vendored** — the
  minified bundle carries no embedded banner; upstream `LICENSE` file pending fetch. Do not treat
  as compliant until that file is added alongside it (same pattern as `.vendor/yaml`).
- No AGPL or NC **code** is vendored (verified).

## Reference-only (NOT vendored — no license obligation in our tree)

| Source | License | How used |
|---|---|---|
| Hermit-AI | AGPL-3.0 | **ideas only**, clean-room — no code copied |
| MathTutorBench | CC BY-SA | **run-only**, never vendored |
| OpenZIM MCP | MIT | reference for the owned libzim reader |
| gguf-parser | MIT | OSS **binary**, downloaded at runtime (not bundled) |
| promptfoo | MIT | **run-only** via `npx` (eval/redteam) — not a dependency |
| AirLLM | Apache-2.0 | evaluated → **rejected** (latency/shape) — not used |

## Content licenses (grounding ZIMs)

| Source | License | Local pilot | Hosted / commercial |
|---|---|---|---|
| Vikidia | CC BY-SA 3.0 | ✅ with attribution + share-alike | share-alike applies |
| Simple English Wikipedia | CC BY-SA 4.0 | ✅ with attribution + share-alike | share-alike applies |
| Khan Academy | **CC BY-NC-SA** | ✅ local/personal only | ⛔ **NC blocks commercial/hosted** |

- **Only a synthetic fixture ZIM is committed** (`tests/fixtures/test_fixture.zim`); **no
  third-party content is vendored.** The reader consumes *user-supplied* ZIMs at runtime, so the
  NC restriction lands on the operator, not on Mentar's distribution — *provided* no NC content is
  ever shipped in the repo. Keep it that way.
- See `docs/CONTENT_LICENSES.md` for the full per-source notes.

## Recommendation (input, not decision)

Adopt **AGPL-3.0-only + a lightweight CLA** (preserves the option to dual-license later) — it is
the license compatible with the GPL `libzim` core and matches the earlier strategic analysis. If a
permissive edition is ever wanted, first make `libzim` optional and supply a non-GPL grounding
path. **Do not** ship Khan (NC) content in the repo under any license.
