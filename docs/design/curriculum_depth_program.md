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
| W2 | Senior maths: **Methods + Specialist**, Y11+Y12 — 40 new topics; the retired merged year11/12_maths quadratics absorbed into Methods VERBATIM (same node ids, mastery survives) under an 'Algebra foundations' strand | ✅ shipped 2026-08-21, auditor reads all four course-years COMPLETE vs reference; the W1 Essential/General strand gaps are W2b, next |
| W3 | Senior science depth: physics/chemistry/biology to the reference strands + **Earth & Environmental Science** (new subject, AU-only until other countries' shapes are verified). 20 shared depth generators land in `STAGE_CONCEPTS`, so IN/SG/US packs can draw them — their template extensions are W8 | ✅ shipped 2026-08-22: all 8 AU senior science subject-years COMPLETE vs reference |
| W4 | Senior English split: **Essential English / English / Literature** — 20 new fact-table topics; the merged year11/12_english retires with its 7 nodes absorbed VERBATIM into mainstream English ('Language and analysis' strand, mastery survives). Auditor course keys are subject-relative now (essential → 'Essential English' under english) | ✅ shipped 2026-08-23: all 6 senior English course-years COMPLETE vs reference |
| W5 | F–10 depth, maths: Year 1 SHIPPED (6 topics, all strands); Y2–10 strand fill in progress — the auditor now names TRUE gaps (post-W7 tagging): ~30 missing strands | 🔨 Year 1 done 2026-08-21; Y2–10 fill next |
| W6 | F–10 depth, science + English: Year 1 SHIPPED both (5 topics each, all strands); Y2–10 fill next (~25 science + ~25 English strands) | 🔨 Year 1 done 2026-08-21 |
| W7 | Retro-tag all existing F–10 topics with `strand:` | ✅ shipped 2026-08-21 — 110 concepts tagged across 27 templates; auditor now reports real gaps instead of 'untagged' |
| W8 | Mirror the depth into IN/SG/US generic packs (their own reference lists needed first) | 🔭 |

## AU is the benchmark for every other country (maintainer, 2026-08-20)

The generic IN/SG/US packs were built by mirroring AU's then-thin structure, so
they inherit its gaps at best. Rule: the auditor's CROSS-COUNTRY BENCHMARK
section compares each country's per-subject topic totals against AU. A country
showing FEWER topics than AU is either a genuinely lighter national curriculum
or a coverage miss — the report cannot tell which, so every "BELOW — verify"
row needs a human check against that country's own syllabus before it is
accepted as legitimately smaller. Stage-structure differences are real
(SG has fewer year levels; US ships no Grade 12 science by decision), which is
why template counts print beside topic counts — normalise before concluding.

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
