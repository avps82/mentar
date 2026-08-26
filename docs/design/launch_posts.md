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

Hi HN. I wanted an AI tutor for my kids that didn't need an account, a
subscription, or their questions going to someone's cloud. Couldn't find one,
so I've been building it.

The design decision I care most about: the LLM never grades anything. All the
questions come from parametric generators I can actually read (934 topics,
years 1–12, AU/IN/SG/US), and a deterministic verifier checks the answers. The
model just explains — analogies, worked examples, "have another look at step 2"
style nudges. Worst case a hallucination gives my kid a clumsy explanation. It
can't tell her a wrong answer is right.

It runs fully local. My test hardware is what I had: a base M1 MacBook with
16GB and an old gaming rig with a 3080. The M1 is also why last week was mostly
me discovering that Ollama's /v1 endpoint silently ignores `think:false` — a
reasoning model burned its whole token budget on hidden chain-of-thought and
returned empty strings. Fun bug. It's gemma2:9b now.

Full disclosure, since it's going to come up anyway: most of this code is
AI-written, under my direction and review. The README says so in the first
screen. I'd rather you judge the 1247 tests and the safety design than take my
word for anything. Which is genuinely part of why I'm posting — it's a tutor
for children, and it has NOT had a professional safeguarding audit. I'm an
unfunded side project; I'm looking for that review pro-bono and there's a
ready-made packet in the repo for any professional willing to look. Until then
the README is blunt: supervised use only, adult in the room.

AGPL, on purpose. If someone offers kids a modified version, the safety changes
have to be inspectable. Commercial licences exist if that doesn't work for you.

Stack is boring by choice: Python, Flask + htmx, SQLite, BKT for mastery.
Happy to answer anything — especially pointed questions about the safety layer.

**Maintainer crib sheet — NOT for posting. Answers you'll want mid-thread:**

- *"AI + children, seriously?"* — supervised-only is a hard line in the README,
  the warning block, and SAFETY.md §3.5.1. Unsupervised needs professionally
  validated pieces we don't have; it's out of bounds, stated not hedged.
- *"Why not just ChatGPT?"* — privacy, zero marginal cost, and the verifier: a
  chat window will happily mark a wrong answer right; Mentar structurally can't.
- *"AI-written = slop?"* — 1247 tests, a release gate (full suite + browser
  checks + gitleaks) before any push, README counts machine-checked against the
  tree. Judge the code, not the author.
- *"AGPL kills adoption"* — for a children's-safety project the network clause
  IS the feature. Commercial licences available.

## 2. r/LocalLLaMA

**Title:**

> Mentar: open-source kids' tutor that runs on Ollama — and what shipping it taught me about local model quirks

**Body sketch:**

The project: local-first AI tutor for my kids — the LLM explains but never
grades (deterministic verifier), 934 topics Y1–12, AGPL. My hardware is a base
M1/16GB and an old gaming rig with a 3080 10GB, so if it doesn't run on those
it doesn't ship. (The 3080 fits gemma2:9b quantized with room to spare — you
don't need a 4090 for this.)

Things I only learned by testing on that hardware, which this sub might enjoy:

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
