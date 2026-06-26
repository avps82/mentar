# License Audit (dependencies + bundled content)

Status input for the **W4.2 OSS-license decision** — this audit *informs* the choice, it does
**not** make it. Generated 2026-06-26. Re-run when dependencies change.

## TL;DR — the dependency graph constrains the choice

**`libzim` (python-libzim) is `GPL-3.0-or-later` and a *core* dependency.** This is the single
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
| pyBKT | core | MIT | yes | ✅ permissive |
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
