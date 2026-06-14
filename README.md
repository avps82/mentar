# Mentar

**OSS-first AI tutor for children that supplements — never replaces — school education.**

Local LLM hosting. Curriculum-templated by country and year level. Built-in kid safety from day one.

---

## What it is

Mentar is an open-source tutoring framework that lets parents run an AI tutor on their own hardware, with no data leaving the device and no per-seat API fees. The core is three components:

- **Template engine** — Markdown curriculum files per country + year/grade level, used as learning guidelines. Community-extensible.
- **Dialogue framework** — Scaffolds tutoring conversations within the bounds of the active curriculum template.
- **Safety layer** — Content guardrails and age-mode logic baked in, not bolted on. This is the non-negotiable bar the project must clear to justify existing.

---

## Why local-first

Two reasons:

1. **Privacy** — children's data never leaves the device. No operator collects it. This is also a major compliance advantage (see `compliance/`).
2. **Cost** — no per-seat API fees. A parent with a capable laptop or homelab machine pays nothing to run inference.

A paid hosted-inference tier (for non-technical parents) is a planned future bridge, but it carries its own heavier compliance obligations. The OSS local edition stays deliberately data-light by design.

---

## Architecture

```
mentar/
├── curriculum/          # Markdown templates per country + year level
│   ├── templates/
│   │   ├── au/          # Australia
│   │   ├── in/          # India
│   │   ├── uk/          # UK
│   │   └── us/          # US
│   └── _template.md     # Starter template for new curricula
├── safety/              # Safety spec, guardrails, age modes
├── compliance/          # Legal framework summaries (OSS local edition)
├── docs/                # Architecture, LLM compatibility, hardware requirements
└── src/
    ├── core/            # Template engine + dialogue framework
    ├── safety/          # Safety layer implementation
    └── inference/       # LLM abstraction layer (swappable backends)
```

---

## Curriculum templates

Templates are simple Markdown files that define what topics a child at a given country + year level should be learning. They are **guidelines**, not scripts — the dialogue framework uses them to keep sessions on-topic and age-appropriate.

Anyone can add a new country or year-level template. See `curriculum/_template.md` for the format.

---

## Safety

Kid-safe content blocks and age-appropriate responses are non-negotiable and built in from the start. See `safety/` for the full spec.

Key commitments:
- No dark patterns, no compulsive gamification mechanics (legal line under EU AI Act Article 5)
- No emotion recognition or mood inference
- Under-13: parent-mediated mode (parent in the loop, child never alone with AI)
- 13+: more independent with parental oversight available
- Hard block: model must never produce sexual content involving minors

---

## Compliance

The OSS local edition is data-light by design, which removes most direct developer exposure under COPPA, GDPR-K, and similar frameworks. However, obligations are real and documented.

See `compliance/README.md` for coverage status — what's mapped, what's incomplete, and where contributors can help.

---

## LLMs

Mentar is designed to work with smaller OSS models suited to educational dialogue. Low hallucination is critical for a children's tutor. The inference layer is abstracted so users can swap models.

Current evaluation status: see `docs/llm-compatibility.md`.

Hardware requirements: see `docs/hardware-requirements.md`.

---

## Contributing

- Add or improve a curriculum template in `curriculum/templates/<country>/`
- Improve the safety spec in `safety/`
- Fill compliance gaps flagged in `compliance/README.md`
- Test and document model compatibility in `docs/llm-compatibility.md`

---

## Status

Early-stage. The architecture and safety decisions are established. Implementation is ongoing.
