---
type: Mentar Design Doc
title: "Curriculum depth program — closing the gap the auditor names"
description: "Phased build to bring every AU year/subject up to the maintainer-supplied reference strand structure (curriculum_reference_au.json). Wave 1 (senior maths Essential+General) SHIPPED 2026-08-20; the auditor's report is the single source of coverage truth."
tags: [design, curriculum, program, in-progress]
timestamp: "2026-08-20T00:00:00Z"
---

# Curriculum depth program

**Why this exists, in the maintainer's words:** *"You guaranteed me that all is
in and I thought it was done. I tested it and found it missing."* The README's
year-range table and the changelog's "breadth COMPLETE" were technically true —
every year existed — and materially misleading: Year 11 maths held 4 topics
from one strand. This program replaces asserted coverage with **audited**
coverage.

## The instruments

- **Reference:** `curriculum_reference_au.json` — the maintainer-supplied
  strand structure for AU maths/science/English, Years 1–10 plus the full
  senior splits (4 maths courses, 4 science subjects incl. Earth &
  Environmental, 3 English courses). The audit vocabulary, not a licence claim.
- **Auditor:** `python3 -m mentar.tools.audit_curriculum_coverage` — per
  year/subject: topic count, strands present, strands MISSING, untagged
  topics, and reference years with NO template. **This report IS the coverage
  claim; cite nothing stronger.**
- **`strand:`** — per-concept grouping field (maintainer: "split the topics
  and subtopics"). Display/audit metadata; the engine stays per-concept.

## Phases

| Phase | Scope | Status |
|---|---|---|
| W1 | Senior maths: **Essential + General**, Y11+Y12 — 40 topics, formula-first cards, strands | ✅ shipped 2026-08-20 (gaps the auditor still names are wave-2 targets: Essential algebra/matrices/bivariate/spherical; General consumer/non-linear/trig/time-series/annuities) |
| W2 | Senior maths: **Methods + Specialist**, Y11+Y12 (~40 topics; calculus, functions, vectors, complex, combinatorics). Absorb the old merged year11/12_maths quadratic nodes into Methods (same node ids — mastery survives) and retire the merged subjects | 🔭 next |
| W3 | Senior science depth: physics/chemistry/biology to the reference strands (now 3 topics each vs 4–7 expected) + **Earth & Environmental Science** (new subject, Y11+Y12) | 🔭 |
| W4 | Senior English split: **Essential English / English / Literature** (current single senior English retires into the mainstream course) | 🔭 |
| W5 | F–10 depth, maths: every year to its reference strands (Year 1 template MISSING entirely; Y2–10 hold 4–7 untagged topics vs 5–6 strands) | 🔭 |
| W6 | F–10 depth, science + English: same treatment; Year 1 both MISSING | 🔭 |
| W7 | Retro-tag all existing F–10 topics with `strand:` so "untagged" stops masking real coverage; consider promoting the auditor to a CI gate once waves land | 🔭 |
| W8 | Mirror the depth into IN/SG/US generic packs (their own reference lists needed first) | 🔭 |

## Rules learned building W1 (bake into every wave)

- Cards must never show approximations as equalities — the claim-checker sweep
  caught "16 ÷ 3 = 5.33" and "5250 ÷ 100 = 52"; construct numbers exact.
- Never search for valid numbers in a `while` loop — construct them
  (`gen_relative_frequency` hung the whole build on an unsatisfiable retry).
- Sweep every generator with the standing oracle (self-verify, Answer-line,
  mc4 shape, claim-check ~60 draws) BEFORE wiring templates.
- Seeds are real draws; strand tags describe what the content IS, the
  reference describes what SHOULD exist — a mismatch is an honest gap, never
  a naming exercise.
