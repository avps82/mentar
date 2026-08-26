---
type: Mentar Design Doc
title: "Launch posts — drafts for HN / Reddit (maintainer edits + fires)"
description: Ready-to-edit drafts for the public launch. The maintainer posts these personally — never automated, one community at a time, HN first.
tags: [launch, promotion, drafts]
timestamp: "2026-08-27T00:00:00Z"
---

# Launch posts — drafts

Rules of engagement (agreed 2026-08-27):

- **HN first.** If it lands, other posts follow with that credibility; if it doesn't, revise before spending the next community.
- **One community at a time.** Never simultaneous — each post gets full attention for ~3 hours after firing.
- **The honesty note leads.** Never bury "AI-built, supervised-only, not independently audited" — it is the differentiator, and this audience checks.
- **Engineers first, parents later.** No homeschool/parenting communities until the pilot has results and the pro-bono safeguarding review lands.

---

## 1. Show HN

**Title (pick one, ≤80 chars):**

> Show HN: Mentar – local-first AI tutor for kids where the LLM never grades
>
> Show HN: An AI tutor that runs on your own machine and can't mark wrong answers right

**URL:** https://github.com/avps82/mentar

**First comment (post immediately after submitting — this is the real pitch):**

Hi HN — I built Mentar because I wanted my kids to have an AI tutor without an
account, a subscription, or their questions leaving the house.

The architecture decision I'd most like feedback on: **the LLM never decides
correctness.** Every question comes from hand-authored parametric generators
(934 curriculum topics, Years 1–12, AU/IN/SG/US), and answers are scored by a
deterministic verifier. The model's only job is *explaining* — analogies, worked
examples, gentle retries. If the model hallucinates, a child gets a bad
explanation, never a wrong grade.

Runs fully local (Ollama / llama.cpp; a base M1 with 16 GB works — that's my
test machine). AGPL on purpose: the network clause means nobody can offer kids
a modified version whose safety changes can't be inspected.

Honesty, because it matters here: the code is **largely AI-written under my
direction and review** — the README says so prominently. It's a research
preview, **supervised use only**. The safety layer is spec'd and tested but has
NOT had a professional safeguarding audit — I'm an unfunded OSS project seeking
that review pro-bono, and the repo carries a ready-made review packet for any
professional willing to look. I would genuinely value scrutiny from this crowd
on the safety design (docs/SAFETY.md) as much as stars.

Stack: Python, Flask + htmx (no build step), SQLite, BKT for mastery tracking,
Ollama/llama.cpp/any OpenAI-compatible endpoint for inference.

**Prepared answers for predictable questions:**

- *"AI + children, seriously?"* → Supervised-only is a hard line in the README,
  the warning block, and SAFETY.md §3.5.1. The safety case for unsupervised use
  needs professionally-validated pieces we don't have yet, so it is out of
  bounds — stated, not hedged.
- *"Why not just use ChatGPT?"* → Privacy (nothing leaves the device), cost
  (zero marginal), and the verifier: a chat window will happily mark a wrong
  answer right. Mentar structurally cannot.
- *"AI-written code, so is it slop?"* → 1247 tests, a release gate that runs
  the full suite + browser checks + gitleaks before any push, and every claim
  in the README is machine-checked against the tree (stale counts fail CI).
  Judge the code, not the author.
- *"AGPL will kill adoption"* → For a children's-safety project the network
  clause IS the feature. Commercial licences exist for anyone who needs them.

## 2. r/LocalLLaMA

**Title:**

> Mentar: open-source kids' tutor that runs on Ollama — and what shipping it taught me about local model quirks

**Body sketch:**

The project: local-first AI tutor, LLM explains but never grades (deterministic
verifier), 934 topics Y1–12, AGPL. Runs on a base M1/16 GB.

The content this sub might actually enjoy — things that only surfaced when
testing on real low-end hardware:

- Ollama's OpenAI-compatible `/v1` **ignores** `think:false` for reasoning
  models (gemma3-class): the whole token budget goes to hidden reasoning in a
  non-standard `reasoning` field and `content` comes back empty. Curl both
  values yourself — byte-identical behaviour. Our fix: detect it, name it, and
  recommend a non-reasoning model.
- Memory bandwidth is the whole game: a 12B at ~8 GB on a base M1 = ~7 t/s and
  that's the *hardware ceiling* with Metal working (`ollama ps` says 100% GPU).
  tokens/sec ≈ bandwidth ÷ model size predicts it within 10%.
- A flat request timeout is a remote-API assumption — on slow local hardware
  the budget you allow must fit inside the timeout you set, or every
  full-length reply dies. Scale the timeout with max_tokens.
- Retrying a timeout on a local backend buys the same failure twice more.

Model pick after eval: gemma2:9b (maths 31/31 on our suite, safety-graded)
over bigger reasoning models. `docs/MODEL.md` has the full reasoning.

## 3. r/selfhosted

**Title:**

> Self-hosted AI tutor for kids — no cloud, no accounts, nothing leaves your network

**Body sketch:**

Angle: the *data* story, not the AI story. Children's tutoring data is exactly
the category you don't want in anyone's cloud. Everything — questions, answers,
mastery tracking, safety logs — lives in a local SQLite file the parent owns.
LAN mode serves a tablet in the same house; parent views are admin-gated.
Setup is `./mentar setup` (auto-detects Ollama) → `./mentar serve`. AGPL.
Honest limits in the README: research preview, supervised use only.

---

*Post-launch: keep a running list here of questions we couldn't answer well —
each becomes a README/docs fix.*
