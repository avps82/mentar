---
title: "Grounding / ZIM-Reader — Design & References (Hermit-AI + OpenZIM MCP)"
version: v0.2 (hands-on)
status: "Recommendation: ADOPT OpenZIM MCP (MIT) for ZIM reading; BUILD the scope/safety wrapper (Hermit ideas, clean-room)."
last-updated: 2026-06-15
owner: Opus
sources: "github.com/0nspaceshipearth/Hermit-AI (AGPL-3.0); SPEC §15 (pedagogical guardrails / RAG), §18 (sources); SAFETY §1.5 (grounding-as-data); curriculum templates `grounding:` anchors"
---

# Grounding / ZIM-Reader — Reference Scan: Hermit-AI

Pradeep flagged **Hermit-AI** as an *idea jump-board* for Mentar's ZIM-reader / grounding
component (the layer that reads vetted offline sources — Vikidia, Simple English Wikipedia —
as RAG grounding for tutoring; SAFETY §1.5, SPEC §15). I cloned and inspected it hands-on.

> ⚠️ **Licence: AGPL-3.0.** Hermit is **reference-only / clean-room** for us — we may borrow
> *ideas*, not *code*. Copying Hermit source would make Mentar AGPL (infectious copyleft) and
> pre-empt the open W4.2 licence decision. Any reimplementation must be independent. This is
> a hard line, not a preference.

## What Hermit is

A 100%-offline chatbot that answers questions from **`.zim` archives** (Kiwix Wikipedia,
Gutenberg, Stack Overflow, etc.). Stack: **`libzim`** (ZIM reading), **`llama-cpp-python`**
(local inference — independently validates the llama.cpp backend decision, SPEC §20.1),
plus `sentence-transformers` + `faiss-cpu` + `rank-bm25` for hybrid retrieval. Same thesis
as Mentar: *local LLMs hallucinate; naive RAG retrieves garbage; verify retrieval in stages.*

## The idea worth borrowing: title-prediction over ZIM (not vector search)

Hermit's "multi-joint" pipeline: **entity extraction → title generation → article scoring →
fact refinement → multi-hop → final generation.** The standout for us is **step 2**: instead
of embedding/vector search, it asks the LLM to **predict likely article titles**, then looks
them up **directly in the ZIM index** — no FAISS index to build, no embedding model to load.
For a bounded, well-known corpus (Vikidia / Simple Wikipedia) this is lighter and often more
accurate than vector similarity for factual lookups, and it fits the **lightweight,
broad-hardware** posture (pairs naturally with the llama.cpp default).

## What to take vs leave (clean-room)

**Take (as design ideas, reimplemented independently):**
- **`libzim` for direct ZIM reading** — the practical way to serve Kiwix sources offline.
- **Title-prediction → direct ZIM lookup** as the primary retrieval path; keep BM25 as a
  cheap fallback. Defer embeddings/FAISS unless measured to help (lighter = better for us).
- **Staged retrieval with a relevance-scoring gate + fact refinement** — extract only the
  sentences that matter, not whole articles. This directly serves our anti-hallucination bar
  and keeps context small for small local models.

**Leave / adapt for Mentar's differentiators:**
- **Scope & vetting:** Hermit ingests ~300GB of arbitrary ZIMs. Mentar grounds **only in
  vetted, curriculum-scoped sources** (Vikidia, Simple English Wikipedia — `CONTENT_LICENSES.md`);
  retrieval must stay inside the active concept's `grounding:` anchor, not roam.
- **Child-safety wrapper:** anything retrieved is **untrusted DATA, never instructions**
  (SAFETY §1.5 grounding-as-data; our `system_prompt.md` already wraps it). Hermit has no
  child-safety layer — we add it.
- **STEM correctness:** Mentar pairs grounding with the **deterministic verifier** for
  checkable answers (SPEC §15) — Hermit relies on the LLM chain alone.
- **Cost control:** Hermit's 6-joint pipeline = many model calls per query. For a small local
  model on modest hardware we should keep the chain short (predict → lookup → score → refine)
  and cache, not run a heavy orchestration per turn.

## ZIM reading: ADOPT OpenZIM MCP (MIT) — don't build the reader

Pradeep flagged the **ZIM MCP** option (mcpmarket.com/server/zim-1) = **OpenZIM MCP**
(`github.com/cameronrye/openzim-mcp`). Verified via GitHub API: **MIT licence**, Python,
**actively maintained** (pushed 2026-06-14), libzim-based, fully **offline** (<50MB RAM),
sub-second full-text search, 8 clean tools (`zim_search`, `zim_query`, `zim_get`,
`zim_get_section`, `zim_browse`, `zim_links`, `zim_metadata`, `zim_health`).

**This changes the build-vs-adopt for the reader.** Unlike Hermit (AGPL → ideas only),
OpenZIM MCP is **MIT → we can actually use it.** Recommendation:

- **ADOPT OpenZIM MCP for the ZIM-reading layer** instead of building a libzim reader from
  scratch. It already solves indexing + full-text search + article/section retrieval offline.
- **Use it DETERMINISTICALLY in the pilot, not as model-driven tools.** MCP's default pattern
  has the *LLM* decide when to call tools — unreliable on small local models (llama.cpp 7–9B)
  and low-control, which is wrong when hallucination = a safety failure. Instead, **our
  controller calls its tools programmatically** (host the server / call its functions): pick
  the article from the active concept's `grounding:` anchor (+ Hermit's title-prediction
  idea), call `zim_search`/`zim_get`, then wrap the result as **untrusted DATA**
  (`system_prompt.md`). We drive retrieval; the model never free-roams a search tool.
- **Model-driven MCP tool-calling = a Phase-2 / capable-GPU-tier option**, not the pilot.
- **What we still build (thin):** the scope/safety wrapper — restrict to vetted curriculum
  sources, stay inside the concept anchor, data-wrap, and pair with the deterministic verifier
  for STEM. That's Mentar's differentiator and stays ours.

> Licence note: OpenZIM MCP **MIT** is compatible with any W4.2 choice (unlike Hermit AGPL).
> Confirm exact version/SBOM before pinning as a dependency.

## Where this lands in Mentar

Implies a **new grounding/retrieval component** (none exists yet) — suggest
`src/mentar/grounding/` (or `retrieval/`): `read ZIM (libzim) → resolve passage for the
active concept's grounding anchor → return it wrapped as data` to the dialogue controller /
prompt templates. This is the RAG half of SPEC §15 and is currently unbuilt; it deserves its
own W-task. The Help-modality + system prompts (W6.2) already expect a `{{grounding_passage}}`.

## Next steps (not built here)
1. Add a **grounding/retrieval W-task**: **adopt OpenZIM MCP (MIT)** as the ZIM reader,
   called **deterministically** by our controller; **build** the thin scope/safety wrapper +
   article-selection (concept anchor + Hermit's title-prediction idea, clean-room) +
   passage→data wrapping. (Spike it hands-on — sandbox has pip/net.)
2. Acquire the pilot ZIMs (Vikidia / Simple English Wikipedia) via Kiwix for local grounding.
3. Keep the chain minimal for small-model/CPU budgets; measure before adding embeddings.
4. Licence: OpenZIM MCP MIT is fine for any W4.2 choice; keep Hermit (AGPL) as ideas-only.
