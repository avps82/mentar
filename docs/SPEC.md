---
type: Mentar Spec
title: "Mentar — Project Specification"
description: The full product specification — the authoritative source of truth. Merges project-memory decisions with the pedagogical engine design (concept graph, mastery tracking, Help loop).
tags: [spec, product, authoritative]
timestamp: "2026-07-22T00:00:00Z"
---

# Mentar — Project Specification

**Project:** Mentar — OSS-first, local-first AI tutor for children  
**Version:** 0.3 — Integrated (project memory + design session + decisions 2026-06-11)  
**Status:** Pilot in progress (single-family supervised pilot)  
**Last Updated:** 2026-07-22

> **Provenance note.** This version merges two sources:  
> **(A) Project memory** — decisions, principles, research and blockers recorded in earlier Mentar sessions (dated 2026-06). These define product identity, safety, regulatory posture, business model.  
> **(B) Design session (this thread)** — the pedagogical engine: concept graph, mastery tracking, the Help loop, measurement strategy, OSS stack specifics.  
> Each major section notes its source. Legal/regulatory content originates from project research notes and carries the original "verify before launch" caveats. [⚠️ Verify regulatory specifics independently before any launch decision.]

---

## Table of Contents

1. [Project Identity & Positioning](#1-project-identity--positioning) · *(memory)*
2. [Problem Statement](#2-problem-statement)
3. [Vision & Goals](#3-vision--goals)
4. [Differentiator & Competitive Position](#4-differentiator--competitive-position) · *(memory)*
5. [Editions & Business Model](#5-editions--business-model) · *(memory)*
6. [Users, Roles & Age/Supervision Model](#6-users-roles--agesupervision-model) · *(memory + session)*
7. [Design Philosophy](#7-design-philosophy)
8. [System Architecture (Unified)](#8-system-architecture-unified)
9. [Curriculum Templating](#9-curriculum-templating) · *(memory)*
10. [Learning Framework — Concept Graph (KST)](#10-learning-framework--concept-graph-kst) · *(session)*
11. [Mastery Signal — Bayesian Knowledge Tracing](#11-mastery-signal--bayesian-knowledge-tracing) · *(session)*
12. [Interaction Patterns](#12-interaction-patterns) · *(session)*
13. [The Help Loop](#13-the-help-loop) · *(session)*
14. [Measurement Strategy](#14-measurement-strategy) · *(session)*
15. [Pedagogical Quality Guardrails](#15-pedagogical-quality-guardrails) · *(session)*
16. [Child Safety & Protection](#16-child-safety--protection) · *(memory)*
17. [Regulatory & Compliance Posture](#17-regulatory--compliance-posture) · *(memory)*
18. [Source Material Catalog](#18-source-material-catalog) · *(session)*
19. [OSS Foundation & Technical Stack](#19-oss-foundation--technical-stack) · *(memory + session)*
20. [Local LLM Strategy](#20-local-llm-strategy) · *(memory)*
21. [Parent Configuration](#21-parent-configuration)
22. [Development Environment](#22-development-environment) · *(session)*
23. [Pilot Plan](#23-pilot-plan) · *(session)*
24. [Open Problems, Blockers & TODOs](#24-open-problems-blockers--todos)
25. [Roadmap & Sequencing](#25-roadmap--sequencing)
26. [Appendix A — Key Definitions](#appendix-a--key-definitions)
27. [Appendix B — Research Artifacts](#appendix-b--research-artifacts)

---

## 1. Project Identity & Positioning
*Source: project memory (decision, 2026-06)*

**Mentar** is an **OSS-first, local-first AI tutor for children that supplements — not replaces — school education.**

- **Curriculum-templated** by country + year/grade level
- **Local LLM hosting** chosen for a dual benefit: **privacy** (a child's data stays on the device) and **cost** (no per-seat API fees)
- **OSS core** = template engine + dialogue framework + safety layer
- **Paid hosted-inference tier** for non-technical parents is a *later bridge*, modelled on the dbt/Airbyte open-core playbook
- **Origin:** emerged as a tangent from the maintainer's data-engineering ideation; the founding personal thesis was *"to change the way you think (with AI), you must change the way you read"* — which evolved into a tool that makes children actively engage with concepts rather than passively consume them

One-line: *An open-source, private, offline-capable tutor that helps kids genuinely understand their school curriculum through active questioning — with child safety built in from the first line, not bolted on.*

**Name:** "Mentar" — a riff on "mentor"; short, brandable, works as a repo / CLI / package name. **CONFIRMED (2026-06-11):** name is clear on GitHub, npm, and PyPI — no blocking collision (a dormant `github.com/mentar` org stub + one inactive 2017 fork exist, neither a conflict). Shortlist re-checked and rejected: Curio (taken on npm — dormant template engine + variants), Gradus (npm graveyard entry, v0.0.0 discontinued), Paideia (active GitHub org + heavy ed-brand overload), Tutela (less brandable), Hearth (generic). **Decision: keep Mentar.**
⚠️ Namespace not yet *reserved* — see name-reservation task (W4.1, 26): publish placeholder package to npm + PyPI to claim the name before any public repo.

---

## 2. Problem Statement

Two failure modes Mentar attacks:

### 2.1 Passive Consumption *(session)*
A book, video, or AI summary can be consumed and forgotten. The surface feels complete; the core concepts never land. The *illusion* of learning replaces actual understanding.

### 2.2 False Confidence — the Harder Enemy *(session)*
A learner believes they understand when they do not. No distress signal is raised, no help sought — because the learner does not know they are confused. This is the most dangerous failure mode and the hardest to detect. Existing tools are blind to it; Mentar targets it directly.

### 2.3 Why Current Tools Fall Short
- Textbooks and AI summaries enable passive consumption; AI summaries actively worsen false confidence.
- Fixed-path LMS platforms move learners along regardless of understanding.
- Existing OSS tutors (OATutor, Open TutorAI) are general/research-oriented — **not curriculum-aligned across countries and not local-first** (see 4).

---

## 3. Vision & Goals

### 3.1 Primary Goal
An AI tutor that ensures children genuinely grasp their curriculum — not surface recall — through active questioning, multi-representation explanation, and adaptive difficulty, while meeting a non-negotiable child-safety bar.

### 3.2 Confirmed Aims
1. **Change how kids learn** — systematic active engagement with complexity via questions and problem-solving, not passive reading. *(session)*
2. **Adaptive to the individual** — no fixed path; the system fits the gap between the learner's current state and the curriculum scope. *(session)*
3. **Supplement, not replace, school** — human-in-the-loop, curriculum-aligned, parent-overseen. *(memory)*
4. **Safety and UX as the bar to clear** — kid-safe content and age-appropriate behaviour are built in from the start. *(memory)*
5. **OSS + local-first** — privacy by architecture, cost-free at the core, community-extensible. *(memory)*

### 3.3 Measurable Outcomes *(session)*
- Demonstrated **transfer** (apply to a new surface), not **echo** (repeat what was shown).
- Mastery (BKT-tracked) consistent across the concept graph, not just on a prompted item.
- Help loop closes reliably: re-explain → transfer test → mastery update.
- False-confidence events detected via proactive probing.
- Curriculum coverage and parent-set completion criteria verifiable.

---

## 4. Differentiator & Competitive Position
*Source: project memory (learning + principle, 2026-06)*

### 4.1 The Differentiator
*Updated 2026-06-11 (decision): UX removed from the Phase 0 moat claim — see note below.*

> Core thesis: even with competition, Mentar is valuable **if the kid-safety guardrails and the pedagogy engine are done right.** Kid-safe content blocks and age-appropriate responses are non-negotiable and built-in from the start. This is the bar the product must clear to justify existing.

The *integration* is the moat: **curriculum-templated tutoring + built-in kid safety + local LLM hosting**, plus the adaptive questioning engine (10–14) that makes the teaching effective.

**On UX (decision, 2026-06-11):** the earlier framing treated "visual/UX done right" as a co-equal moat pillar. For a solo build this overcommitted — UX had a claimed moat but zero workstream. **Repositioned:** for **Phase 0/1 the differentiator bar = safety + pedagogy + local-first**, with UX deferred to **Phase 1 as an iteration surface, not a Phase 0 moat.** Bones first (the engine + safety must work); the UX skin is layered on and refined through iteration later. This closes the W5.1 "decide-or-rewrite" task in 26 (Option B chosen).

### 4.2 Competitive Landscape (as of 2026-06)
- **OSS adaptive tutoring exists** — OATutor (full ITS), Open TutorAI (LLM + RAG) — but both are general/research-oriented, **not** curriculum-aligned across countries and **not** local-first.
- **Safety tooling exists separately** — Guardrails AI, NVIDIA NeMo Guardrails, Stanford educational-guardrail work — but is not integrated into a kids' tutor.
- **Paid market** spans ~$4/mo (Khanmigo) to ~$500/mo (premium reading apps); most AI tutoring sits at **$10–40/mo** → demand is proven.

### 4.3 The Validated Gap
Nobody has integrated **curriculum-templated tutoring + built-in kid safety + local LLM hosting** for young learners. The pieces exist independently; the integrated OSS local-first product does not. That gap is Mentar's reason to exist.

---

## 5. Editions & Business Model
*Source: project memory (decision, 2026-06)*

| Edition | Who | Data posture | Compliance burden |
|---------|-----|--------------|-------------------|
| **OSS Local Edition** | Technical parents / devs; community | Data-light by design; runs fully local; no operator collects child data | Low — most COPPA/GDPR-K obligations don't attach (see 17) |
| **Paid Hosted Tier** *(later bridge)* | Non-technical parents | Hosted inference; collects data | High — full COPPA/GDPR-K/AI-Act machinery applies |

- **OSS core** = curriculum template engine + dialogue framework + safety layer (free, community-extensible).
- **Hosted tier** = managed inference + onboarding for parents who can't self-host. Open-core playbook (dbt/Airbyte): give away the engine, monetise the hosting/convenience layer.
- **Strategic rule:** keep the OSS local edition deliberately data-light; concentrate all heavy compliance machinery in the hosted tier (see 17).

---

## 6. Users, Roles & Age/Supervision Model
*Source: project memory (safety/age) + session (roles)*

### 6.1 Roles
| Role | Who | Responsibility |
|------|-----|----------------|
| **Learner** | Children | Engages with questions, presses Help, answers re-checks |
| **Configurer / Supervisor** | Parents (or teachers) | Sets mode, curriculum template, safeguards, completion criteria; stays in the loop |
| **Builder / Maintainer** | The maintainer + OSS community | Template engine, dialogue framework, safety layer, content, model abstraction |

### 6.2 Age & Supervision Model
- **Not locked to a single age band** — deliberately broader than the original "5–7 year old" framing; spans year/grade-level templates.
- **Under-13:** parent-mediated mode — **never child-alone-with-AI**. Younger year-level templates are supervised by default.
- **13+:** independent use with parental oversight.
- **Configurable** to member-state digital-consent ages (13–16) — see 17.
- **Age 13** is the recurring legal/guidance threshold (COPPA, UNESCO, ChatGPT all land there).

**Mechanism (decision, 2026-06-11 — closes W2.6):** "Never child-alone-with-AI" is now backed by a concrete mechanism, phased:
- **Phase 0 (pilot):** honor system + full transcript logging + parent review. Parent is physically present during pilot sessions; all turns logged and reviewable. Lowest friction so build focus stays on the engine.
- **Phase 1:** add a **parent PIN gate** to start/resume a session (child cannot access without the parent entering a code). The same PIN gates escalation acknowledgment (16.3).
- Rationale: get the bones (pedagogy + safety engine) working under the lighter mechanism first; harden the enforcement mechanism when scaling to non-technical parents who need it. Recorded in SAFETY.md Layer 5.

---

## 7. Design Philosophy

1. **Active over passive** — questions and problem-solving, never summaries. *(session)*
2. **Transfer over echo** — re-checks test a *new surface*, not a repeat of what was shown. *(session)*
3. **No fixed path** — learning varies; the curriculum template scopes *what*, the traversal personalises *how/when*. *(session)*
4. **Supplement, not replace** — human-in-the-loop is a load-bearing design + legal commitment, not a slogan. *(memory)*
5. **Safety by design** — kid-safety is built in from the start; "best interests of the child" (UNCRC) is the primary design lens. *(memory)*
6. **Local-first, data-light** — privacy and low cost are architectural, not features. *(memory)*
7. **Community-extensible** — curriculum templates and compliance coverage are contributor-fillable. *(memory)*
8. **Tool, not a friend** — Mentar must not foster parasocial attachment, emotional dependence, or over-reliance. It is a learning tool that supplements human connection — never a companion or substitute for parents, teachers, or peers. Design against engagement-for-its-own-sake. Ties to Bucket G research (chatbot attachment / parasocial risk). *(memory)*

**What Mentar is NOT:** a textbook · an AI summary engine · a fixed-curriculum platform · a replacement for teachers · a data-harvesting product · a gamified attention trap · a companion or friend substitute.

---

## 8. System Architecture (Unified)

The product is four layers. The first is the OSS core's *scope*; the rest are the adaptive *engine*.

```
┌─────────────────────────────────────────────────────────────┐
│ SAFETY LAYER  (wraps everything — content/age/escalation 16) │
├─────────────────────────────────────────────────────────────┤
│ 1. CURRICULUM TEMPLATE   country + grade MD files  → SCOPE    │  (memory, OSS core)
│       defines WHICH concepts are in play for this learner     │
├─────────────────────────────────────────────────────────────┤
│ 2. CONCEPT GRAPH (KST)   prerequisite ordering     → ORDER    │  (session)
│       defines WHAT depends on WHAT; computes the "fringe"     │
├─────────────────────────────────────────────────────────────┤
│ 3. MASTERY SIGNAL (BKT)  per-skill estimate        → STATE    │  (session)
│       tracks WHERE the learner is; drives adaptive toggle     │
├─────────────────────────────────────────────────────────────┤
│ 4. DIALOGUE FRAMEWORK    interaction patterns + Help loop     │  (memory core + session)
│       delivers questioning, re-explanation, measurement       │
├─────────────────────────────────────────────────────────────┤
│ LOCAL LLM  (privacy + cost; swappable; low-hallucination 20) │  (memory)
└─────────────────────────────────────────────────────────────┘
```

**Reconciliation note:** the curriculum template (memory's "OSS core") provides the *node set* and grade alignment; the KST concept graph (this session) adds *prerequisite ordering* on top. They are complementary, not competing. The "no fixed path" principle holds: the template scopes, the graph orders, the traversal personalises.

---

## 9. Curriculum Templating
*Source: project memory (decision, 2026-06)*

- Curriculum is defined **per country + year/grade level** as **simple Markdown files** (e.g., year 2, year 5, year 12), used as **learning guidelines**.
- Deliberately **not locked to a single age band**.
- **Community can add and extend templates** — this is a core OSS contribution surface.
- The **template engine + dialogue framework is the OSS core** of the product.

**Integration with the concept graph (10):** a curriculum template supplies the in-scope concepts for a learner's grade; the KST graph imposes prerequisite ordering on that set; the dialogue framework delivers it. Templates are guidelines (loose, grade-aligned); the graph is the rigorous dependency structure.

---

## 10. Learning Framework — Concept Graph (KST)
*Source: design session*

The in-scope curriculum is modelled as a **prerequisite graph** — not a linear syllabus.

- **Nodes:** individual concepts (e.g., "adding fractions with equal denominators")
- **Edges:** prerequisite relationships (e.g., whole-number division precedes fractions)
- **Knowledge state:** the set of currently-mastered concepts
- **Outer fringe:** concepts whose prerequisites are *all* satisfied — i.e., what the learner is ready to learn *right now*. This is the core adaptive next-step signal.

**Graph construction:** small hand-built graphs per subject for the pilot (fractions, ~8–10 nodes); longer term, `DAKS` (R) can infer prerequisite implications from response data so the graph improves from usage. ⚠️ **Flywheel caveat:** DAKS inference needs *aggregated multi-learner* response data, which the data-light local-first edition deliberately never collects — see 24 #16 (data-flywheel posture, decision pending W5.7).

**Traversal:** the AI selects entry point, depth, next node (from the fringe), and interaction pattern — fully adaptive. Benefits: coverage tracking (touched vs. skipped) and a real "done" definition (mastered across the graph).

**Commercial validation:** ALEKS (not OSS) is built on KST and deployed at scale.

---

## 11. Mastery Signal — Bayesian Knowledge Tracing
*Source: design session*

- **Library:** `pyBKT` (Python, `pip install pyBKT`, UC Berkeley CAHL lab — same lab as OATutor).
- Estimates per-skill mastery probability from problem-solving response sequences.
- Parameters per concept: `learns`, `forgets`, `guess`, `slip`.
- **Hinted-win discount:** a correct answer *after* Help counts as weaker evidence than a cold-correct one. **Corrected (2026-06-12, was an overclaim):** standard BKT has **no native hint handling**. **Mechanism chosen (W3.3, 2026-06-14):** implemented as an **elevated-guess observation class** in Mentar's own deterministic update wrapper (`src/mentar/engine/bkt.py`) — a hinted-correct uses `guess_hinted = guess + (1−guess)·0.5`, raising mastery strictly less than a cold correct. pyBKT is **not** in the per-turn hot path (it cannot fit a single learner's cold-start); it is reserved for **offline parameter fitting post-pilot** (N≥100 scored responses/skill → `prior_mode→0`). Cold-start priors are hand-set by node class. Full design: `docs/design/W3.3_bkt.md`. Tested: T3.3 invariants (verified numerically 2026-06-14).
- **Deviation from classic BKT — Option B (A20, ratified 2026-07-05):** classic BKT applies the learning transition `P(L') = P(L|obs) + (1−P(L|obs))·learns` after *every* observation. Mentar gates this: a **wrong** observation — hinted or unaided — only conditions the posterior (step a); no `learns` credit (step b) is added. Without this, a low-prior wrong-answer streak could still nudge mastery upward turn-over-turn (a symptom of the well-documented "model degeneracy" critique of vanilla BKT — see `docs/design/W3.3_bkt.md` §3.2 for the literature reference and full rationale). Correct observations, hinted or not, are unaffected (a hinted correct still earns strictly less than a cold correct, via the elevated guess).
  **Corrected 2026-08-16:** this read "a **bare-wrong** (unaided incorrect) observation", which contradicted A20's own acceptance criterion (*"a wrong-answer streak from cold start never raises mastery above the prior — was: rises then plateaus ~22%"*). The implementation matched the narrower wording, so the 22% survived on the HINTED path: a child answering wrong every turn and pressing Help every turn drove mastery 0.10 → 0.2231, measured end-to-end. That is the common path, not a corner — `FLOW.md` routes `HELP_RECHECK_SCORE → BKT_UPDATE (hinted)`, so a struggling child's wrong answers are usually hinted. Resolved in favour of the acceptance criterion.
- Drives the adaptive toggle: deepen, branch, advance, or change interaction pattern.

**Limitation:** BKT needs scored (right/wrong) responses → works for STEM/checkable answers. Open-ended critical thinking has no clean 0/1 signal and requires an **LLM-as-judge** layer (open problem, 24). This dovetails with the project's low-hallucination model requirement (20).

---

## 12. Interaction Patterns
*Source: design session*

| Pattern | Description | Best for |
|---------|-------------|----------|
| **Read-then-question** | Read a passage → system asks questions | Concept intro, comprehension |
| **Problem-first** | Given a problem → system probes reasoning | STEM, application |
| **State-and-challenge** | State what was learned → system challenges assumptions | Critical thinking, synthesis |

- **Default mix:** parent-configurable.
- **Adaptive toggle:** live mix adjustment based on performance (and never via emotion recognition — prohibited, see 16).
- No single pattern is locked; the system weights toward what works for this learner on this concept.

---

## 13. The Help Loop
*Source: design session*

The primary mechanism for closing the confusion → understanding cycle.

### 13.1 Flow
```
Learner presses Help (declared-confusion signal)
  → Pop-up: re-explanation of the concept ("the why"),
            in a DIFFERENT representation type
  → [still unclear] Retry: generate a DIFFERENT variant
            (cap retries — suggested N=3)
  → Learner MUST answer the re-check question (cannot skip)
            — question tests TRANSFER, not ECHO
  → [still unsure] Link back to the source concept
            (grounded reference; flag as sticking point; optional parent alert)
```

### 13.2 Non-Negotiable Constraints
1. **Vary the representation type, not the wording** — visual → concrete → analogy → story → formal.

   | Modality | "1/2 + 1/2 = 1" |
   |----------|-----------------|
   | Visual | Square cut into two triangles; together = one whole square |
   | Concrete | Two half-glasses poured together = one full glass |
   | Analogy | Two half-days = one full day |
   | Story | Half a pizza at lunch + half at dinner = a whole pizza |
   | Formal | 1/2 + 1/2 = 2/2 = 1 |

2. **Cap retries** — after N variants, link back to source, flag the concept, optionally alert parent.
3. **Re-check tests TRANSFER, not ECHO** — if Help showed "1/2 + 1/2", re-check with "1/3 + 1/3 + 1/3" or "you eat 2 of 4 pizza slices — what's left?". Echo measures mimicry; transfer measures grasp.
4. **Hinted-win discount** applies to the re-check (11).
5. **Link-back is grounded reference**, not a new explanation cycle — points to vetted source material.

### 13.3 What Help Misses
Help is reactive — it catches *declared* confusion only. It is blind to **silent misunderstanding / false confidence**, which requires proactive probing (14).

---

## 14. Measurement Strategy
*Source: design session*

### 14.1 Confusion ≠ Understanding (asymmetric)
```
Press Help          → does not understand        (reliable)
Does NOT press Help → AMBIGUOUS:
                        (a) understands           ← genuine mastery
                        (b) false confidence      ← the dangerous case
```
**Do not read silence as understanding.** Only an active probe disambiguates it.

### 14.2 Proactive Probing
Unprompted questions (not Help-triggered, not skippable), inserted after N items or when BKT mastery is high but Help use is suspiciously low. Each probe uses a transfer framing. This is what makes the mastery signal trustworthy for non-Help-pressing learners.

### 14.3 What Cannot Yet Be Measured
Open-ended critical thinking and grasp in non-checkable domains require an **LLM-as-judge** rubric layer — not yet designed (24).

### 14.4 Probe Outcome Classification (False-Confidence Decision Table)
*Source: W3.4 — review finding*

A probe outcome must be disambiguated before it is trusted as a false-confidence signal:
a single wrong answer can be a slip, and a previously-mastered skill can simply have gone
stale. The FSM runs **exactly one** retry variant on a first failure (SESSION_FSM §P3),
then classifies into one of four classes (persisted to `probe_event.class`):

| First probe | Retry variant | Other conditions | Class |
|-------------|---------------|------------------|-------|
| correct | — (not run) | — | `clean_pass` |
| wrong | correct | — | `slip_suspect` *(single failure, recovered)* |
| wrong | wrong | mastery stale (decayed-mastery window) | `forgetting_suspect` |
| wrong | wrong | mastery ≥ threshold **and** no Help pressed on concept | **`false_confidence`** |
| wrong | wrong | otherwise (mastery never high, or Help was pressed) | `slip_suspect` *(expected miss; v0 — revisit post-pilot)* |

**`false_confidence` is the dangerous case** and is asserted only when slip is ruled out
(both variants failed), mastery claims competence (≥ threshold), and the learner never
declared confusion (no Help). `forgetting_suspect` is checked first so a decayed skill is
not mislabelled. Implementation: `src/mentar/engine/probe_classify.py` (stub, W3.4). The
stale-mastery window is derived by the caller from `skill_state.updated_at`. All three
non-clean classes are logged distinctly for review.

---

## 15. Pedagogical Quality Guardrails
*Source: design session — distinct from child-safety guardrails in 16*

**Risk:** every AI-generated re-explanation must be correct and clarifying. A wrong explanation creates confident misunderstanding. **Hallucination = a safety failure** (per project principle, 16). Goal: *tighten, not eliminate.*

**Layered (strongest first):**
1. **Ground in vetted source (RAG, not recall)** — re-represent a retrieved correct passage; do not free-invent facts. Biggest single risk drop. *Implemented by* `src/mentar/grounding/` (**W7**) — a thin owned `libzim` reader that resolves each node's `grounding.anchor` to a passage for the system prompt's `{{grounding_passage}}` slot. Pilot scope = deterministic anchor-resolution (no LLM/BM25/embeddings); open retrieval deferred to W7.5. Contract: `docs/design/W7_grounding_reader.md`.
2. **Deterministic check (STEM)** — verify any numeric/worked step computationally before serving.
3. **Vetted variant bank** — builder/parent-approved alternative explanations for high-traffic concepts; live generation only for the long tail; approved variants accumulate (quality flywheel). ⚠️ **Flywheel caveat:** cross-household accumulation requires data the local-first edition doesn't collect; per-household banks work locally, but the *shared* flywheel is a hosted-tier or opt-in-contribution feature — see 24 #16 / W5.7.
4. **Backstop** — the transfer-test re-check catches a bad variant after the fact (lagging, but caught and flagged).

**Honest limit:** a confident-wrong explanation producing a confident-wrong answer can pass undetected. Human review + parent oversight remain inputs. When uncertain, the model should defer: *"let's check with your teacher."*

---

## 16. Child Safety & Protection
*Source: project memory (principles, 2026-06). This is the differentiator bar (4) — built in, never bolted on.*

### 16.0 SAFETY.md Architecture *(Decision, 2026-06)*
The kid-safety spec is organized as **6 layers**, to be documented in `SAFETY.md` (intended repo path: `docs/SAFETY.md`). All requirements in 16.1–16.3 map onto these layers.

| Layer | Name | What it covers |
|-------|------|---------------|
| 1 | **Input safety** | What comes *from* the child: distress-signal detection, off-topic redirect, harmful-input blocks |
| 2 | **Output safety** | What the tutor sends *back*: age-appropriate, on-scope, non-shaming, non-manipulative |
| 3 | **Boundary & escalation** | Edge cases — the hardest layer: distress disclosures, off-rail conversations, handoff to trusted adults |
| 4 | **Data & privacy** | What is collected, stored, retained, shared — and what is not |
| 5 | **Parental oversight & transparency** | Logs, transcripts, controls — the trust anchor |
| 6 | **Pedagogical safety** | Hallucination control — wrong explanations to a child are treated as safety failures |

> Layer 6 (pedagogical safety) is detailed in 15. Layers 1–5 map onto the three requirements below.

### 16.1 Privacy & Age (Requirement 1/3)
- **Privacy/data:** parental consent before any child-data processing; data minimisation + purpose limitation + retention limits; privacy by default and by design; voice/biometric/device IDs treated as personal info; a written security program for any data-processing tier.
- **Age/supervision:** under-13 = parent-mediated (never child-alone-with-AI); 13+ = independent with oversight; younger templates supervised by default; configurable to member-state consent ages (13–16).

### 16.2 Interaction & Content (Requirement 2/3)
- **Interaction:** NO dark patterns / compulsive gamification (an **EU Art. 5 legal line**, not just ethics); no profiling / targeted ads / detrimental use; **human-in-the-loop always**; **no emotion recognition** (EU education prohibition — so the adaptive toggle must use performance signals, not inferred mood).
- **Content:** **HARD BLOCK — never generate sexual content involving minors**; age-appropriate output only (no violent/adult/frightening material); stay within curriculum scope; validate for pedagogical appropriateness; **hallucination = safety failure** → fall back to *"let's check with your teacher."*

### 16.3 Transparency, Oversight & Escalation (Requirement 3/3)
- **Transparency:** privacy info in child-friendly language; the child always knows they're talking to an AI; parental logs/transcripts reviewable. Primary lens = **best interests of the child** (UNCRC).
- **Escalation** *(detail pending research Bucket D):* distress disclosures (harm/abuse/danger) **must route to a trusted adult** — never handled by AI alone, never silently dropped. **Never facilitate secrecy or isolate a child from trusted adults.**

---

## 17. Regulatory & Compliance Posture
*Source: project memory (research Buckets A & B, blocker, decision — all as of 2026-06).*  
[⚠️ Verify — general information from prior project research, NOT legal advice. Confirm independently before any launch.]

### 17.1 BLOCKER — EU AI Act high-risk classification
EU AI Act **Annex III classifies education AI as HIGH-RISK** → heavy obligations (risk-management system, technical documentation, human oversight, logging, accuracy/robustness, conformity assessment). For a solo OSS project this is a significant work tier.

**Unresolved (to verify):** the high-risk category centres on **consequential decisions** (admissions, grading, exam monitoring). A *supplementary* home tutor that doesn't gate access or assign formal grades **may fall outside** the strictest sub-categories. Also unresolved: how OSS distribution is treated (provider vs deployer obligations).

### 17.2 DECISION — Regulatory exposure of the OSS local edition
**Working position (the maintainer):** because the OSS edition is **local + parent-set-up + not a direct sale to children**, direct developer exposure is **low**.
- **Data protection (COPPA/GDPR-K):** strongest support — no operator collecting child data ⇒ no COPPA operator / GDPR controller role; GDPR household-activity exemption likely covers home use.
- **EU AI Act:** OSS status does *not* by itself dissolve obligations (the open-source exemption carves out Art. 5, Art. 6/Annex III, Art. 50). What keeps Mentar out of high-risk: (a) no consequential educational decisions; (b) purely-local non-commercial self-hosting may not be "placing on market." Both to verify. The Art. 5 manipulation ban travels regardless — but Mentar builds no manipulative mechanics.
- **Risk concentrates in the paid hosted tier** ⇒ full COPPA/GDPR-K/AI-Act machinery applies there.
- **Architecture confirmed:** OSS local edition data-light + self-hosted; heavy compliance lives in the hosted tier. *Safety spec matters regardless of legal exposure (parents, app stores, reputation, doing right by kids).*

### 17.3 Research Bucket A — child data-protection frameworks
- **COPPA (US, under-13):** 2025 amendments (full compliance 22 Apr 2026) add separate verifiable parental consent for 3rd-party/ad disclosure, retention limits, broader "personal information" (biometric + gov IDs), mandatory written info-security program. School-authorisation exception **not** codified.
- **GDPR-K (EU):** Art. 8 digital age of consent — under-16 needs parental consent; member states may lower to 13 (Germany 16; many at 13). Recital 38 carve-out for preventative/counselling services.
- **UK Age Appropriate Design Code:** 15 standards; applies to any service "likely to be accessed" by under-18s; a consumer product like Mentar **is** in scope.
- **California AADC:** partially in effect (9th Cir. mandate 3 Apr 2026); data-use + dark-patterns provisions enjoined; age-estimation remanded. Other states layering (Maryland, South Carolina).
- **Australia Online Safety Act:** under-16 social-media ban (Dec 2025) exempts education — Mentar likely outside it; other content codes still apply.
- **Through-lines:** verifiable parental consent; data minimisation/purpose limitation/retention; privacy by default & design; best-interests-of-child; no profiling/ads/dark patterns; age-appropriate transparency; written security program; treat voice/biometric/device data as personal.
- **Key strategic insight:** local-first architecture is a major compliance advantage — if data never leaves the device and no operator collects it, most heavy obligations don't attach.

### 17.4 Research Bucket B — AI-specific guidance for children
- **UNICEF Guidance on AI and Children v3.0 (2025):** UNCRC-grounded; 10-requirement design checklist; names AI-generated CSAM as a threat ⇒ absolute hard-block on sexual content involving minors.
- **EU AI Act:** Art. 5 (in force 2 Feb 2025) prohibits exploiting age vulnerabilities; July 2025 guidelines bring compulsive/gamified mechanics under it (fines up to €35M / 7%). Emotion recognition in education prohibited.
- **UNESCO Guidance for GenAI in Education (2023):** recommends age limit 13 for independent/unsupervised use; human-in-the-loop; validate for ethical *and* pedagogical appropriateness.
- **Implication:** age-13 is the recurring threshold; human-in-the-loop = the "supplement not replace" commitment; anti-manipulation is a hard requirement.

### 17.5 Safety Research Roadmap (8 Buckets)
*Tracked in memory. Living findings doc: `mentar-safety-research-findings.md` (intended repo: `docs/research/`). Append a new Part as each bucket closes. A & B findings subsume the earlier "map legal frameworks" TODO — README coverage doc still separately pending.*

| Bucket | Topic | Status |
|--------|-------|--------|
| A | Child data-protection & online-safety regulation | ✅ Done — 17.3 |
| B | AI-specific guidance for children (UNICEF, EU AI Act, UNESCO) | ✅ Done — 17.4 |
| C | Real-world AI-chatbot harm cases | ⏳ Pending |
| D | Safeguarding & disclosure handling | ⏳ Pending — feeds 16.3 escalation design |
| E | Age-appropriate content standards | ⏳ Pending |
| F | Guardrail tooling (local-first) | ⏳ Pending — feeds 19.3 safety tooling |
| G | Over-reliance & developmental risk (chatbot attachment / parasocial risk) | ⏳ Pending — feeds 7 principle 8 |
| H | Kid-safe product patterns | ⏳ Pending |

---

## 18. Source Material Catalog
*Source: design session. Distinct from curriculum templates (9): templates are grade-aligned guidelines; these are the concept/question content the AI reads.*

### 18.1 Two Source Roles
| Type | Role | Examples |
|------|------|---------|
| **Concept substrate** | AI reads → generates/grounds questions | Wikipedia, Vikidia, Wikibooks |
| **Question/problem bearing** | Predetermined Qs → AI tweaks | Khan/Kolibri, PhET, freeCodeCamp |
| **External question banks** | Predetermined Qs (parent-uploaded, not on Kiwix) | QuickGuide-style guides |

Both are used together; the system is not constrained to one. Question banks are an accelerator/quality enhancer, not a requirement — the system can run on concept substrate alone.

### 18.2 Kiwix ZIM Catalog (offline, self-hosted)
> Browse: https://library.kiwix.org · Download: `https://download.kiwix.org/zim/<dir>/<name>_<date>.zim`  
> ⚠️ Filenames carry rolling dates — verify exact filename/size before `wget`.

**Primary / K–6:** Vikidia (`zim/vikidia/`) · Simple English Wikipedia (`zim/wikipedia/wikipedia_en_simple_all_*`) · Khan Academy K–12 (Kolibri preferred) · African Storybook / StoryWeaver (`zim/other/`)

**Secondary / 7–12:** Wikipedia nopic (`zim/wikipedia/wikipedia_en_all_nopic_*`) · PhET (`zim/phet/`) · Khan Academy AP/SAT (Kolibri preferred) · Wikibooks (`zim/wikibooks/`) · TED-Ed (`zim/ted/`)

**Undergraduate:** MIT OCW (`zim/other/` ⚠️ intermittent) · Wikiversity (`zim/wikiversity/`) · freeCodeCamp (`zim/other/freecodecamp_*` ⚠️ verify dir) · DevDocs (`zim/devdocs/`) · Project Gutenberg (`zim/gutenberg/`) · TED (`zim/ted/`)

**Graduate / Research:** Wikipedia maxi (`zim/wikipedia/wikipedia_en_all_maxi_*`, ~100GB+) · Stack Exchange (`zim/stack_exchange/`) · Wikisource (`zim/wikisource/`) · Wiktionary (`zim/wiktionary/`)

### 18.3 External Question Banks
QuickGuide-style guides with predetermined questions per subject/level — parent-uploaded or sourced separately. Provide a syllabus-anchored question backbone the AI tweaks per learner. Not on Kiwix; separate ingestion path.

---

## 19. OSS Foundation & Technical Stack
*Source: memory (competitive/safety tooling) + session (pedagogical stack)*

### 19.1 Fit Assessment *(session)*
OSS is **borrowed plumbing, not the spine**. It covers ~40% (structured space, mastery, reference architecture); the differentiating ~60% (curriculum templating, integrated kid-safety, LLM questioning engine, critical-thinking measurement) is owned/novel. Fit is subject-dependent: strong for STEM, weak for open conceptual domains.

### 19.2 Pedagogical Engine
- **KST (concept graph):** `kst`, `kstMatrix`, `pks` (maintained, updated 03/2026), `DAKS` (infers graph from data) — R/CRAN; port fringe/path logic to Python.
- **BKT (mastery):** Mentar's own deterministic recurrence in `src/mentar/engine/bkt.py` for the per-turn hot path (W3.3). `pyBKT` (Python, UC Berkeley CAHL) is reserved for **offline parameter fitting** post-pilot (N ≥ 100 scored responses/skill).
- **Reference ITS:** OATutor (UC Berkeley CAHL, MIT, React, static/offline). Use as architectural reference for mastery→content wiring; **do not** adopt its authored OpenStax content model.
- **LLM-native (watch, research-stage):** Open TutorAI (modular, learner/educator/parent interfaces — closest to vision), CLASS (Rice/OpenStax), OATutor-GPT.
- **W3.5 verdict (2026-06-14): Open TutorAI = REFERENCE-ONLY** (do not fork) — borrow its learner/educator/parent module split as a reference, build our own surface. Desk assessment (confirm with a hands-on spike); full rationale in `docs/design/W3.5_build_vs_adopt.md`.

### 19.3 Safety Tooling *(memory)*
- **Guardrails AI**, **NVIDIA NeMo Guardrails**, **Stanford educational-guardrail work** — exist independently; candidates to integrate into Mentar's safety layer (16) rather than build from scratch.

---

## 20. Local LLM Strategy
*Source: project memory (decision + TODOs, 2026-06)*

**Decision:** local LLM hosting is the **default**, chosen for privacy (data stays local) + cost (no per-seat fees). It is also a compliance advantage (17).

### 20.1 Pluggable Backend Architecture *(decision, 2026-06-11)*
Mentar is **not tied to any single model or runtime.** As an OSS project, it ships a **model-abstraction layer** that exposes one interface and accepts multiple swappable backends. Local-first by default; cloud is *enabled, not imposed* — the parent decides.

```
generate(prompt, grounding_passages, constraints) → text
  ├─ Backend: llama.cpp (GGUF)                 ← PRIMARY local default (lightweight, broadest HW support)
  │     • Ollama is an optional convenience wrapper over the same engine
  ├─ Backend: parent's own vLLM cluster        ← capable-GPU / throughput tier, parent-operated
  ├─ Backend: Gemini API (opt-in)              ← parent supplies + owns the key
  └─ Backend: Claude / other API (opt-in)      ← parent supplies + owns the key
```

**Primary local backend = `llama.cpp` (decision, 2026-06-15, the maintainer).** Reasons: it is the
**lightest** runtime and gives the **broadest hardware support** (CPU-only, Apple Silicon
(Metal), modest GPUs, Win/macOS/Linux), running quantized **GGUF** weights — which is what
makes "runs on a parent's laptop/homelab" real, i.e. the local-first differentiator. vLLM is
the high-throughput **capable-GPU** tier (and the eval host, §20.3); Ollama is just a
convenience wrapper around llama.cpp. **Integration note:** `llama.cpp`'s `llama-server`
exposes an **OpenAI-compatible** API, so it uses the *same* provider path as vLLM (one
`base_url` swap) for both the inference layer and the NIAH retrieval eval — or it can run
in-process via `llama-cpp-python`. Either mode is config + env only (no code change).

- **Swappability = config + env var only** — no code change to switch backends (mirrors the 21 Markdown-config philosophy).
- **Cloud is the parent's choice and the parent's responsibility.** If a parent opts into a cloud backend, *they* supply and own the API key, and *they* assume the data-policy responsibility for traffic leaving the device. Mentar neither stores nor routes that data.
- **Compliance consequence:** when a parent chooses a cloud backend, **they become the operator/controller** for that data flow (COPPA/GDPR sense), not the Mentar project. This keeps the OSS local edition data-light regardless of which backend a parent selects (reinforces 17.2). [⚠️ Verify operator-attribution treatment before any launch framing.]
- **Why this matters:** it's an OSS tool — it *should* run everything. Prescribing one model/runtime would betray the architecture. The project gives the rails; the end user picks the engine.

### 20.2 Open work (re-homed to 26 W1)
1. **Evaluate OSS LLMs for tutoring** — identify smaller OSS models for educational dialogue with **low hallucination**; document by size/capability. *(Hallucination = a safety failure, 16.)* → W1.2–W1.3.
   - **Note on closed cloud models:** Gemini/GPT-class closed models cannot be self-hosted and so can't be the *default*; they're available only via the opt-in backend above. Their lower hallucination rate does not remove the need to eval OSS defaults — the pedagogical guardrails (15: RAG grounding, deterministic checks, vetted variant banks, transfer-test backstop) are what make a smaller local model safe, and must be proven on the OSS default.
2. **Minimum hardware requirements** — *backend-dependent* now: local Ollama → publish a min-spec RAM/CPU/GPU tier table; own vLLM cluster → parent's own sizing; cloud API → internet + key only. → W1.4.
3. **Model abstraction layer v0** — build + test the interface above against ≥2 backends. → W1.5.

### 20.3 Eval environment *(decision, 2026-06-11 — closes W1.1)*
Model evaluation runs on **a local AI test PC (10GB vRAM), serving models via vLLM**, already configured and reachable. The build host (2-core/16GB, no GPU) remains the build host and cannot run eval. **Connection details supplied 2026-06-15** — eval-host access is live (see `docs/MODEL.md`). 10GB vRAM is sufficient for the ≤14B-class candidates in scope.

**Note (session):** the chosen backend must also serve Help-loop re-explanations, transfer-question generation, and (Phase 2) the LLM-as-judge layer. Model quality directly gates pedagogical quality (15) and is the project's biggest infrastructure dependency.

### 20.4 Hardware horizon *(forward-looking watch — added 2026-06-11; tracked as W1.6)*
A new class of large-unified-memory "local AI" hardware is arriving fast, raising the ceiling on what models parents can run **locally** — strengthening the local-first default and the pluggable-backend bet. Snapshot [⚠️ Verify — fast-moving]:

| Vendor | Hardware | Tier | Local-AI relevance |
|--------|----------|------|--------------------|
| **NVIDIA** | **RTX Spark** (GB10-derived, 20-core Arm + Blackwell GPU ≈ RTX 5070, up to 128GB unified, 1 PFLOP) | **Consumer** — the relevant one | Runs ~120B models locally w/ ~1M-token context; **Windows-on-Arm**; in Surface Laptop Ultra + Asus/Dell/Lenovo/HP/MSI; **ships ~Q3/fall 2026, no pricing yet** |
| NVIDIA | DGX Spark / DGX Station (GB10 / GB300) | Developer (already out) | Reference only — dev/workstation tier, ~$4–5k; not the consumer target |
| **AMD** | Strix Halo / Ryzen AI Max+ 395 (128GB unified) → Ryzen AI Halo box (~Jun 2026) → Gorgon (2026) → Medusa Halo (2027) | Consumer/prosumer | 128GB unified at $1.5–3.3k; runs 70B locally; runs on standard Linux/Windows x86; Medusa ~2× bandwidth 2027 |
| **Apple** | Foundation Models framework + MLX (Apple Silicon) | Consumer | Open *in principle* (WWDC 2026) — but **integration cost is the open question**: on-device system model is **Swift-only**; the Python path is **MLX (`mlx-lm`) / OpenAI-compatible MLX server**, not Apple's system model directly. "Open" ≠ "drop-in for a Python stack." |

**Implication for Mentar:** the industry is converging on (a) big-unified-memory local boxes and (b) backend-abstraction patterns — both of which the 20.1 pluggable-backend layer already anticipates. **But "a backend exists" ≠ "Mentar can call it cheaply."** Two integration caveats now flagged for W1.6: (1) **RTX Spark is Windows-on-Arm** — confirm the Python local-inference stack (Ollama/llama.cpp/vLLM) runs *natively* on Win-on-Arm vs via x86 emulation (Prism), and at what latency cost. (2) **Apple is Swift-first** — targeting Apple's *system* on-device model needs Swift glue; the realistic Python route is MLX-served open weights behind an OpenAI-compatible endpoint. The W1.6 deliverable is a **per-backend integration-effort matrix** (drop-in / shim / native-code-needed), not just a hardware list. No purchase decision needed for the pilot (eval host sorted, 20.3). Living note: `docs/hardware-requirements.md`.

---

## 21. Parent Configuration

| Setting | Options | Default |
|---------|---------|---------|
| Learning mode | Passive / Critical | **Critical** |
| Supervision mode | Parent-mediated (under-13) / Independent-with-oversight (13+) | By age/template |
| Safeguards | Scholastic (on) / Broader (off) | Scholastic |
| Curriculum template | Country + year/grade | Parent-selected |
| Interaction-pattern mix | % of 3 patterns | **40/30/30** — pilot default (v0); revisable post-pilot (W5.3) |
| Adaptive toggle | On / Off (performance-based only; no emotion recognition) | On |
| Help retry cap | N | **3** — pilot default (v0); revisable post-pilot (W5.3) |
| Mastery threshold | 0–1 | **0.85** — pilot default (v0); consumed by `engine/fringe.py` (W5.3) |
| Probe cadence | trigger rule | **After every 5 items OR when (mastery ≥ 0.85 ∧ Help-rate < 1 per 10 items) — whichever first** — pilot default (v0) (W5.3; SPEC §14.2) |
| Completion criteria | Finish coursework / parent-defined question set | Parent-defined |
| **LLM backend** *(updated 2026-06-15)* | local **llama.cpp** (GGUF) / own vLLM cluster / Gemini API / Claude API (opt-in cloud; parent owns key); Ollama = optional wrapper | **local llama.cpp** (lightweight, broadest HW support — §20.1) |

Mode/curriculum configs are **Markdown composition files** swapped at runtime — no code change. Scholastic config = safe rules + filters on; Broader config = relaxed rules, wider scope. Curriculum templates (9) are the grade-aligned subset of these.

---

## 22. Development Environment
*Note: this is the project's BUILD/dev environment — distinct from the product's end-user deployment target (parents' local machines, 20). Specifics are generic by design; nothing here is required to use or develop Mentar.*

| Component | Role | Detail |
|-----------|------|--------|
| Build / dev host | code + tests | A low-resource Linux container, **no GPU** — runs the build, tests, and tooling; cannot serve models. |
| LLM eval host | W1.2–W1.3 model eval | A separate local AI test PC with a discrete GPU (~10GB vRAM), serving candidate models via **vLLM** behind an OpenAI-compatible endpoint. |
| Content | offline sources | Kiwix **ZIM** files served from local storage (the W7 grounding sources). |

Connection details are environment-specific and supplied at run time via env vars
(`MENTAR_VLLM_BASE_URL` / `MENTAR_VLLM_API_KEY`, etc.) — **never committed**. See `config/README.md`.

---

## 23. Pilot Plan
*Source: design session*

**Scope:** Fractions (STEM), ~8–10 concept nodes, scoped by a year-level math curriculum template.  
**Why fractions/STEM first:** clean prerequisites; checkable answers; deterministic verification works; isolates the LLM quality risk; recurring design example.

**Sample graph:**
```
Whole-number division
  └─ Fraction as part-of-whole
       └─ Equal vs. unequal parts
            └─ Unit fractions (1/n)
                 ├─ Comparing fractions (equal denominators)
                 └─ Adding fractions (equal denominators)  ← pilot target
                      └─ Subtracting fractions (equal denominators)
```

**Pilot goals:** prove adaptive traversal; prove the Help loop closes (transfer-tested, hinted-win discounted); stress-test the pedagogical guardrail; measure proactive-probe effectiveness and baseline false-confidence rate. Run with the safety layer active even in pilot — "active" is defined as the controls specified in **[SAFETY.md](SAFETY.md) v0.1** (W2.1), including the Layer 3 escalation path (W2.2). This resolves the apparent §24 "safety spec pending" gap: SAFETY.md v0.1 *is* the pilot's operative safety definition; the open Bucket-D items there are post-pilot refinements, not pilot blockers (note the §3.5 rollout guard bounds the pilot to a single supervised family).

**Pilot interface (W6.3, decided 2026-06-14):** minimal **local web app** (Flask/FastAPI bound to localhost), 4 plain views — learner question screen, Help pop-up, probe interrupt, parent log view (with escalation alert + acknowledge-to-resume). TUI rejected (weak for a child); fork rejected (W3.5 = reference-only). Full rationale: `docs/design/W6.3_pilot_interface.md`.

**Out of scope (v0):** humanities/open-ended reasoning; multi-subject graphs; full parent UI; LLM-as-judge; hosted tier; multiple learners.

---

## 24. Open Problems, Blockers & TODOs
*Merged: memory blockers/TODOs + session open problems*

| # | Item | Type | Source | Notes |
|---|------|------|--------|-------|
| 1 | EU AI Act high-risk classification | **Blocker — EU market entry / hosted tier ONLY; NOT the local pilot** | memory | Per §17.2: the supervised, non-grading, non-commercial **local** pilot does not "place on market" and makes no consequential decisions → high-risk likely does not attach; Art. 5 (manipulation ban) applies always but is satisfied by design. So this gates EU framing + the hosted tier, **not** Phase-0 or G0. Still verify Annex III / Art. 6 + OSS-distribution treatment before any EU launch. 17.1 |
| 2 | Evaluate OSS LLMs for tutoring (low hallucination) | TODO → **re-homed W1.2–W1.3** (26) | memory | 20 #1 — gates pedagogical quality; eval host decided (20.3) |
| 3 | Minimum local hardware requirements | TODO → **re-homed W1.4** (26) | memory | 20 #2 — now backend-dependent per 20.1 |
| 4 | LLM compatibility & swappability abstraction | TODO → **re-homed W1.5** (26) | memory | 20 #3 — pluggable-backend decision made (20.1); build pending |
| 5 | README compliance-coverage doc for OSS contributors | TODO | memory | Bucket A & B findings (17.3–17.4) cover the research; the README doc itself still needs to be written |
| 6 | Escalation design (distress disclosures) | **Pilot path live; Bucket D open** | memory | v0.1-interim trigger→freeze→alert path in SAFETY.md Layer 3 + `src/mentar/safety/escalation.py` (W2.2) — sufficient for the supervised pilot. Bucket D (validated trigger list, emergency signposting, handoff-wording review) refines post-pilot; §3.5 rollout guard bounds use until then. route-to-trusted-adult flow (16.3) |
| 7 | Subject flow & completion-criteria workflow | Open → **owned by W6.1** (26) | session | End-to-end session state machine; toggle-signal logic; tested by T3.7 |
| 8 | Silent-misunderstanding measurement (proactive probe design) | Open | session | Probe triggering + BKT integration |
| 9 | LLM explanation correctness | Partially mitigated | session | Guardrail layers in place; residual risk remains (15) |
| 10 | Open-ended critical-thinking measurement (LLM-as-judge) | Open | session | Rubric design, scoring calibration; Phase-2 dependency |
| 11 | Transfer-test question generation strategy | Open | session | Authored vs generated-and-verified vs grounded |
| 12 | Kolibri vs ZIM for Khan content | Verify | session | Format/integration path |
| 13 | GitHub / npm name availability for "Mentar" | ✅ **Resolved 2026-06-11** (W4.1b) | memory | Clear on GitHub/npm/PyPI; keep Mentar. ⏳ Namespace reservation (npm + PyPI placeholder publish) still pending — the maintainer to run |
| 14 | Cowork local filesystem setup | ✅ **Resolved** (2026-07-03 repo review confirmed this over-ran the finding) | memory | Files are written directly to the local working tree in every session since; the chat-download workaround is no longer needed. |
| 15 | Safety research Buckets C–H | TODO | memory | C: chatbot harm cases; D: safeguarding/disclosure; E: content standards; F: guardrail tooling; G: over-reliance/developmental; H: kid-safe patterns. Full roadmap 17.5 |
| 16 | **Data-flywheel tension** (local-first vs learning-from-usage) | **DECIDED 2026-06-15 → (c) per-child / per-household** | W5.7 (the maintainer) | OSS local edition learns **per child only**; no shared/aggregated flywheel. Cross-learner features (DAKS graph inference §10, shared vetted-variant bank §15) are NOT promised for the local edition — if ever pursued they live in the **hosted tier** (option (a) describes that later home). Keeps the OSS edition data-light; no reopening of the §17 compliance posture. Any "improves from usage" claim is per-household, not collective. §10/§15 caveats resolved to this. |
| 17 | Core design artifacts undrafted (session state machine, prompt set, pilot interface, repo sketch) | Open → **owned by W6** (26) | review 2026-06-12 | The dialogue 'pipeline/controller' that T4/T5 tests assume has no design doc; prompt templates must be versioned files (T7 gates on prompt changes); pilot UI surface undecided |
| 18 | **Khan Academy content licence (CC BY-NC-SA) vs paid hosted tier** | **Phase-3 blocker** | W4.1 2026-06-14; re-pointed B1 2026-07-05 | NC clause incompatible with a *paid* hosted tier; fine for non-commercial local/OSS use — this now includes the pilot itself, which re-pointed all grounding to Khan Academy (B1, no mounted Vikidia/Simple-WP ZIM was ever available). Do NOT bundle Khan content into any paid offering without a separate Khan licence. Vikidia/Simple English Wikipedia (CC BY-SA) remain cleared alternates, not currently mounted — see `docs/CONTENT_LICENSES.md` |

---

## 25. Roadmap & Sequencing

1. **Phase 0 — Pilot (now):** fractions/STEM, hand-built graph, OSS local, safety layer on. Prove the engine; isolate LLM-quality risk.
2. **Phase 1 — OSS Local Edition:** template engine + dialogue framework + safety layer; a few curriculum templates; local LLM with the low-hallucination model from TODO #2; **US / parental-consent-first** rollout (lighter than EU per 17).
3. **Phase 2 — Conceptual/open-ended:** add LLM-as-judge for non-checkable domains; expand interaction patterns; broaden curriculum templates with community.
4. **Phase 3 — Paid Hosted Tier:** managed inference for non-technical parents; full compliance machinery (COPPA/GDPR-K/AI-Act); EU entry only after the high-risk question (17.1) is resolved.

### 25.1 Kill Criteria (pre-committed)
*Source: W5.6 (review 2026-06-12). Pre-commit these now, while judgement is unclouded.*

| # | If this… | …then |
|---|----------|-------|
| (a) | No candidate model passes the T1.6 quality gates | Raise the size ceiling **once**; if still 0 pass → **pause** the project and revisit the local-first bar (SPEC §20). |
| (b) | EU AI Act verification (§24 #1) concludes high-risk applies **even to the OSS local edition** | **Halt EU framing**; US / parental-consent-first only; reassess at Phase 3. |
| (c) | The pilot learner shows genuine distress or withdraws assent | **DEFERRED to Bucket D (the maintainer, 2026-06-15) — revisit.** Interim: the **present parent's judgment** governs (parent-mediated pilot), and a per-input distress disclosure is handled by SAFETY Layer 3. **Must NOT halt on normal learning frustration** ("I hate fractions" ≠ distress — the escalation classifier already separates these). No automated tolerance-count or distress-signal *mechanism* exists yet, so no auto-stop rule is set; don't shut the pilot down early on ordinary struggle. |

> **On the (c) threshold — status & guidance.** Deferred per the maintainer: defining an auto-stop
> threshold makes little sense before a distress-signal *mechanism* exists, and a too-eager
> rule would halt the pilot on normal frustration. Until Bucket D closes, the present parent
> is the judge of genuine distress / loss of assent. When revisited, anchor on **continuous
> assent** (child agrees *and* can stop anytime) per **UNICEF ERIC** (Ethical Research
> Involving Children), standard **IRB/ethics child-assent** practice, and **NSPCC** guidance
> (Bucket D, SPEC §17.5). [⚠️ Verify against those sources before relying on it.]
| (d) | Phase-0 actuals exceed the W5.5 estimate by **>2×** | Invoke the scope-cut order (§25.2). |
| (e) | *(optional personal-runway line — ⏳ the maintainer to set)* solo time/€ budget exceeds **___** with G0 not reached | Invoke scope-cut order; if still blocked → pause. |

### 25.2 Scope-Cut Order (drop first → last)
When (d) triggers, cut in this order:
1. W1.6 hardware-horizon watch
2. W3.5 build-vs-adopt spike (verdict already reference-only — `docs/design/W3.5_build_vs_adopt.md`)
3. Multi-learner namespacing polish
4. Vetted variant bank (serve live-generation + post-session review only)
5. Probe-classifier granularity (keep the binary false-confidence classifier)

**NEVER cut (the differentiator bar, SPEC §4.1):** the safety layer · the transfer re-check
in the Help loop · the deterministic verifier. Cutting any of these fails the reason-to-exist
test and is itself a kill condition.

---

## Appendix A — Key Definitions

| Term | Definition |
|------|-----------|
| **Mentar** | OSS-first, local-first AI tutor for children that supplements school education. |
| **OSS core** | Curriculum template engine + dialogue framework + safety layer (free, community-extensible). |
| **Curriculum template** | Country + grade-level Markdown file defining in-scope concepts (learning guidelines). |
| **Concept graph (KST)** | Prerequisite graph imposing ordering on the in-scope concepts; computes the fringe. |
| **Fringe (outer)** | Concepts whose prerequisites are all met — what the learner is ready to learn now. |
| **BKT** | Bayesian Knowledge Tracing — per-skill mastery estimate from scored responses. Hot path: Mentar's own deterministic recurrence (`engine/bkt.py`). Offline fitting: `pyBKT` post-pilot. |
| **Hinted-win discount** | A correct answer after Help weighted as weaker mastery evidence than an unaided one. |
| **Transfer test** | Re-check using a new surface of the concept (tests grasp, not mimicry). |
| **Echo test** | Re-check repeating what was just shown (measures mimicry — to be avoided). |
| **False confidence** | A learner believes they understand when they don't; doesn't press Help. The primary enemy. |
| **Proactive probe** | Unprompted question to catch false confidence; not Help-triggered. |
| **Parent-mediated mode** | Under-13 mode where the child is never alone with the AI. |
| **Hallucination = safety failure** | A wrong answer to a child is treated as a safety incident; model defers ("check with your teacher"). |
| **Open-core playbook** | OSS engine free; monetise the hosted/convenience tier (dbt/Airbyte model). |
| **RAG (here)** | LLM re-explains from a retrieved vetted passage, not from free recall. |
| **Anti-over-reliance** | Design principle: Mentar must not foster parasocial attachment or emotional dependence. Tool, not a friend. |
| **SAFETY.md** | The 6-layer kid-safety specification document (16.0); intended repo path: `docs/SAFETY.md`. |

---

## Appendix B — Research Artifacts

| Artifact | Description | Intended Repo Location | Status |
|----------|-------------|----------------------|--------|
| `mentar-safety-research-findings.md` | Consolidated safety research: Buckets A+B findings, regulatory exposure analysis, design requirements, open questions, pending threads, sources. Living doc — append a Part as each Bucket C–H closes. | `docs/research/` | Created 2026-06; Buckets C–H pending |
| `SAFETY.md` | Kid-safety spec — 6-layer structure (16.0), drafted from 16 + findings doc | `docs/` | ✅ Written and shipped |
| README compliance-coverage doc | Maps major legal/compliance frameworks (COPPA, GDPR-K, EU AI Act, UK AADC); signals OSS contribution gaps | `compliance/README.md` | ✅ Written and shipped |

*Delivery note: files are written directly to the local working tree (TODO #14 resolved, 2026-07-05).*
