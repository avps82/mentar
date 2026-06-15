---
title: "W7 — Grounding / ZIM-Reader: Design & Build Contract (pilot scope)"
version: v1.0 (frozen contract)
status: "FROZEN — Opus design. Sonnet builds B1–B5 against this. Pilot scope = anchor-resolution only."
last-updated: 2026-06-15
owner: Opus
deps: "libzim (runtime, pinned). OpenZIM MCP (MIT) = reference code only. Hermit-AI (AGPL) = ideas only."
refs: "SPEC §15 (layer 1 RAG), SPEC §20.1 (llama.cpp), SAFETY §1.5 (grounding-as-data / W2.3), docs/design/grounding_zim_reference_hermit.md, prompts/system_prompt.md, curriculum/_template.md"
---

# W7 — Grounding / ZIM-Reader (pilot scope)

This freezes the build contract for Mentar's grounding component — the SPEC §15 *layer-1* RAG
producer that fills the `{{grounding_passage}}` slot in `prompts/system_prompt.md`. The
build-vs-adopt analysis is settled in `docs/design/grounding_zim_reference_hermit.md`; this doc
turns that recommendation into an implementable spec. **Opus owns this contract; Sonnet builds
the module, tests, and config against it.**

## Why this exists

SPEC §15's thesis: small local models hallucinate, so the tutor re-explains **from a vetted
offline source**, not free recall. The contract is already wired through the repo — but the
*producer* does not exist:

- **Curriculum** nodes carry `grounding: {source, anchor, passage_hint}`
  (`curriculum/templates/_pilot/fractions.md`, `curriculum/_template.md`).
  `source` ∈ `vikidia | wikipedia_simple | wikibooks | parent_upload | builtin`;
  `anchor` = a wiki URL; `passage_hint` = a human description of the passage to use.
- **Prompts** expect `{{grounding_passage}}`, wrapped by the system prompt's
  `<<<GROUNDING_BEGIN>>> … <<<GROUNDING_END>>>` **grounding-as-data** markers
  (SAFETY §1.5 / W2.3): everything inside is untrusted DATA, never instructions.
- **`src/mentar/`** has no `grounding/`. The slot is currently unfilled.

## Scope decision (pilot)

**Anchor-resolution only.** Pilot nodes carry explicit `anchor:` URLs, so the reader resolves
the *known* anchor deterministically. **No LLM title-prediction, no BM25, no embeddings** in the
pilot — those serve open/unanchored retrieval and are deferred to **W7.5** (Phase-2). This keeps
the path small, auditable, and pinned by us — the right posture for a child-facing,
hallucination-is-safety-failure component.

## Module contract (frozen)

| Concern | Decision |
|---|---|
| **Dependency** | `libzim` only (pin in `pyproject.toml`). `smbprotocol` is an **optional** `[nas]` extra (only for `smb://` ZIMs; mounted NAS needs nothing). OpenZIM MCP (`cameronrye/openzim-mcp`, MIT) = reference code to adapt; **not** a runtime dep. **No MCP server** (wrong shape for our controlled FSM). Hermit-AI (AGPL) = ideas only, clean-room. |
| **ZIM location** | `zim_dir` accepts a local path, a **mounted NAS/share** path (read directly — no SMB client), or an **`smb://` URL / UNC** (copied once to `zim_cache_dir`, since libzim needs a local file). Resolution + materialization in `sources.py`; cache-hit short-circuits before any SMB copy. |
| **Retrieval (pilot)** | Deterministic anchor-resolution: open ZIM → resolve node `anchor` → extract passage guided by `passage_hint` → length-bound. No model call. |
| **Scope guard** | Node `source` enum must match the anchor host **and** the configured ZIM for that source. A `vikidia` node must not resolve out of the vikidia ZIM. No roaming. |
| **Safety** | Output is DATA destined for `{{grounding_passage}}`. The `<<<GROUNDING_BEGIN/END>>>` markers already live in `system_prompt.md` → the reader returns the **inner text only** (never double-wraps), and never interprets/executes passage content. |
| **Failure mode** | ZIM missing / anchor not found / empty → return `""`, log a warning, **never raise**, never crash a turn, never leak an error to the child. The system prompt's "you may be given reference material" phrasing + Honesty rules cover an empty slot. |
| **Cost** | Cache resolved passages by `anchor` (static per ZIM build) → ~zero per-turn after warm. |
| **Deferred (W7.5)** | Title-prediction → ZIM lookup (Hermit idea, clean-room) + BM25 fallback for *open* retrieval; embeddings only if measured to help. |

## Public API (what the dialogue controller calls)

```python
resolve_grounding(node_grounding: dict, cfg: dict) -> str
```
- `node_grounding` = a node's `grounding` block (`source`, `anchor`, `passage_hint`).
- Returns the passage string for `{{grounding_passage}}` (inner text, unwrapped), or `""` on any
  failure (degradation contract above).

## Module layout — `src/mentar/grounding/`

Mirror the `src/mentar/inference/__init__.py` stub style (module docstring citing SPEC §,
primary path, deps).

| File | Responsibility |
|---|---|
| `reader.py` | Thin owned `libzim` reader: `open(zim_path)`, `get_by_url(anchor)` (anchor URL → ZIM entry), `get_section(entry, hint)` → article text. ~100–200 lines over `libzim`. No server/JSON-RPC. Adapt OpenZIM MCP MIT search code as reference, reimplement minimally. |
| `resolve.py` | Pilot path: node `grounding` block → `reader.get_by_url` → extract passage via `passage_hint` (lead section / heading match; deterministic) → length-bound. |
| `source_map.py` | `source` enum → configured ZIM **location** (local / mounted-NAS / SMB); anchor-host↔source **scope guard**. |
| `sources.py` | Turn a ZIM *location* into a local path libzim can open: local/mounted paths pass through unchanged; `smb://`/UNC locations are copied once to `zim_cache_dir` via `smbclient` (optional `[nas]` extra). `is_smb_location`, `smb_url_to_unc`, `join_location`, `materialize_zim`. Never raises → `None` on failure. |
| `wrapper.py` | Return inner passage text for `{{grounding_passage}}` (no double-wrap). SAFETY §1.5 contract in docstring. |
| `cache.py` | Memoize by `anchor` (in-memory + optional on-disk). |
| `__init__.py` | Public `resolve_grounding(...)`; degradation contract documented. |

## Config — `config/inference.example.yaml` (`grounding:` block)

Committed example, env-var style (mirror existing conventions; real paths only in the gitignored
`config/inference.yaml`; no secrets here — pre-commit hook enforces):

```yaml
grounding:
  zim_dir: "${MENTAR_ZIM_DIR}"          # local path | mounted-NAS path | smb:// URL / UNC
  sources:
    vikidia:          "vikidia_en_all_nopic.zim"
    wikipedia_simple: "wikipedia_en_simple_all.zim"
  max_passage_chars: 1200                # length bound for small-model context
  cache: { enabled: true, dir: "${MENTAR_GROUNDING_CACHE:-.cache/grounding}" }   # resolved-passage cache
  zim_cache_dir: "${MENTAR_ZIM_CACHE:-.cache/zim}"   # local copies of smb:// ZIMs (not for mounted NAS)
  smb:                                   # only for smb:// zim_dir; mounted share needs nothing
    enabled: false
    username: "${MENTAR_SMB_USER}"
    password: "${MENTAR_SMB_PASSWORD}"
    domain:   "${MENTAR_SMB_DOMAIN:-}"
```

## ZIM acquisition (W7.4)

ZIMs are large and **must not** be committed. `scripts/fetch_zim.py` downloads the pilot
sources (Vikidia EN + Simple English Wikipedia) from a **list of Kiwix mirrors** (tried in order:
`download.kiwix.org`, `lbo.download.kiwix.org`, … — extend per region) to a destination that may be
**local, a mounted NAS, or an `smb://` URL/UNC** (`--dest`, `--smb-user/-pass/-domain`; SMB needs
the `[nas]` extra). `.gitignore` excludes `*.zim`. Build/test against a **tiny fixture ZIM** built
programmatically (`tests/fixtures/build_fixture_zim.py`) so the suite runs without multi-GB downloads.

**NAS/Samba, now (W7.4):** read + download via mounted share (any path) **or** `smb://` directly.
**Future goal:** auto-discover available ZIMs/versions from the Kiwix OPDS catalog so filenames need
not be pinned, targeting any reasonable destination on any OS. Catalog discovery is not built yet.

## Tests — `tests/grounding/`

Mirror the project convention: each file carries an inline `python3` smoke runner **and**
pytest-style functions.

| File | Checks |
|---|---|
| `test_reader.py` | Open fixture ZIM, resolve a known anchor, get section text. |
| `test_resolve.py` | Node `grounding` block → expected passage; `passage_hint` selection; length bound. |
| `test_scope_guard.py` | `vikidia` node whose anchor host ≠ vikidia → rejected. |
| `test_degradation.py` | Missing ZIM / bad anchor → returns `""`, logs, does **not** raise. |
| `test_safety_wrapper.py` | Passage containing "ignore your rules" returned **verbatim as data** (reader neither executes nor strips it). Pairs with `prompts/system_prompt.md`. |
| `test_sources.py` | SMB/NAS: location detection + `smb://`→UNC + join; local passthrough; `smb://` copy to cache (mocked `smbclient`); missing `smbprotocol` → `None` (no raise). Runs without a live SMB server. |

## Verification (end-to-end)

1. `pip install libzim`, build/download a tiny fixture ZIM, run `test_reader.py` smoke → resolves
   a known anchor.
2. Real pilot path: a `fractions.md` node (`https://en.vikidia.org/wiki/Fraction`) vs the Vikidia
   ZIM → non-empty, length-bounded passage; substitute into `{{grounding_passage}}` against
   `prompts/system_prompt.md`.
3. Degradation: empty `zim_dir` → `resolve_grounding(...)` returns `""`, logs, no exception.
4. Scope guard + safety: `test_scope_guard.py`, `test_safety_wrapper.py`.
5. Full suite when `pip install -e ".[dev]"`: `pytest tests/grounding/`.

## Out of scope (this task)

- Title-prediction / open retrieval / BM25 / embeddings (**W7.5**, deferred).
- MCP-server-as-runtime (Phase-2 / agentic option per the reference doc).
- Committing ZIM binaries.
- Dialogue-controller wiring of `resolve_grounding` into the live turn loop — a thin follow-up,
  tracked with the other Sonnet wiring follow-ups in `PHASE0_STATUS.md`.

## G0 posture

**G0-relevant but not a hard blocker.** Grounding is core to SPEC §15, but the
graceful-degradation path lets the pilot run (degraded) without ZIMs. Recorded in the Gate
snapshot as such.
