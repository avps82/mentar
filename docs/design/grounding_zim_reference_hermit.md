---
title: "Grounding / ZIM-Reader — Reference Scan: Hermit-AI"
version: v0.1 (idea jump-board, hands-on)
status: "Reference-only (clean-room). Informs Mentar's grounding/retrieval component."
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

## Where this lands in Mentar

Implies a **new grounding/retrieval component** (none exists yet) — suggest
`src/mentar/grounding/` (or `retrieval/`): `read ZIM (libzim) → resolve passage for the
active concept's grounding anchor → return it wrapped as data` to the dialogue controller /
prompt templates. This is the RAG half of SPEC §15 and is currently unbuilt; it deserves its
own W-task. The Help-modality + system prompts (W6.2) already expect a `{{grounding_passage}}`.

## Next steps (not built here)
1. Add a **grounding/retrieval W-task**: libzim-based reader for Vikidia/Simple-Wiki ZIM,
   title-prediction + BM25 retrieval, passage→data wrapping. Clean-room (no Hermit code).
2. Acquire the pilot ZIMs (Vikidia / Simple English Wikipedia) via Kiwix for local grounding.
3. Keep the chain minimal for small-model/CPU budgets; measure before adding embeddings.
4. Revisit at W4.2: our licence choice must stay independent of Hermit's AGPL.
