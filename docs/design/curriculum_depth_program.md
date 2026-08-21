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
| W5 | F–10 depth, maths | ✅ shipped 2026-08-21: Year 1 (6 topics) + 30 strand-fill topics Y2–10 — every year COMPLETE vs reference |
| W6 | F–10 depth, science + English | ✅ shipped 2026-08-21: Year 1 both + 25 science + 24 English strand-fill topics — every year COMPLETE vs reference |
| W7 | Retro-tag all existing F–10 topics with `strand:` | ✅ shipped 2026-08-21 — 110 concepts tagged across 27 templates; auditor now reports real gaps instead of 'untagged' |
| W8 | Mirror the depth into IN/SG/US generic packs (their own reference lists needed first) | 🔭 |

### SG reference lists — RECEIVED, not wired (2026-08-21)

`docs/design/country_references/sg_{maths,science,english}_reference.md`
hold the maintainer-supplied full SG reference (Years 1-12/Primary-to-Pre-U),
saved verbatim on request ("Note it for now") — **content authoring has not
started.** Structural notes that change how W8 must be scoped for SG, not
generic mirroring of AU:

- SG science starts at Year 3 (Primary 3), not Year 1/2 — a real structural
  absence, not a gap. Do not add SG Year 1/2 science pages.
- SG maths' "Year 10 (Secondary 10)" heading in the source is almost
  certainly "Secondary 4" — flagged in the saved file, not silently corrected.
- SG science splits Physics/Chemistry/Biology at Secondary 3 (Year 9), one
  stage earlier than AU's Year 11 split — `senior_science_items.py`'s
  `SENIOR_LEVELS["SG_GENERIC"]` already encodes exactly this (Sec 3/4 = stages
  1/2), so the shared depth generators should slot in without a new mapping.
- SG English's Year 9-10 secondary content was supplied as ONE combined
  block (not split by year) and its Pre-U years are GP/KI, not an
  English-course-split analogous to AU's Essential/Mainstream/Literature —
  mapping GP/KI onto that shape would misrepresent the subject.
- No Earth & Environmental Science named for SG at any level — recorded, not
  assumed as absent-by-decision the way US Grade 12 science is.

**IN reference set COMPLETE** (`in_{english,maths,science}_reference.md`):
CBSE Classes 1-12, NCERT-guided.
- English: no Y11/12 course split (unlike AU/SG) — one continuous English
  Core through senior secondary; do not invent a split.
- Maths: senior secondary (11-12) splits Mathematics (041, science/eng track)
  vs Applied Mathematics (241, commerce/social science track) — only 041 was
  supplied; do not infer 241 from it.
- Science: Classes 1-2 have NO dedicated science subject at all (folded into
  language/maths) — a real structural absence, do not add IN Class 1/2
  science pages. Classes 3-5 teach it as combined Environmental Studies
  (EVS), not separable into pure-science strands. Classes 6-10 unified
  (Physics+Chemistry+Biology integrated, no split). Senior secondary splits
  medical (PCB) vs non-medical (PCM) — Physics+Chemistry common to both,
  Biology is PCB-only, Maths(non-medical) is already in the maths reference.
  No Earth & Environmental Science named at any IN level.

**US reference set also COMPLETE** (`us_{english,maths,science}_reference.md`):
CCSS (English + maths) / NGSS (science).
- English: high school is TWO BANDS (9-10, 11-12), not four grades — CCSS
  itself doesn't split further; don't invent a per-grade split.
- Maths: high school uses named COURSES (Algebra 1/Geometry/Algebra 2/
  Pre-Calc-Calc), "typically Grade N" is a mapping convenience only — some
  US schools use an Integrated Pathway (Math 1/2/3) instead, not covered
  here.
- Science: middle school (6-8) supplied as ONE combined block of NGSS
  mastery targets "by end of Grade 8", not per-grade; matches the existing
  Integrated Science model some US schools use.
- **Grade 12 flag INVESTIGATED, 2026-08-21 (WebSearch: NGSS grade bands,
  CCSS math pathways, NCES/PACE enrollment data).** Verdict: `NO_SCIENCE_LEVELS
  = {"us_g12"}` is well-founded, not contradicted. Real enrollment data shows
  G12 maths has the SAME "no dominant course" shape as G12 science — only
  ~40% of grads complete precalculus, calculus enrollment is lower and
  declining, AP Statistics ~8% and rising (PACE/NCES). No single Grade 12
  maths course has a majority either.
  The actual finding is an ASYMMETRY ALREADY IN SHIPPED CODE, not a new
  contradiction: `US_GENERIC/g12_maths.md` (and IN Class 12 / SG Sec 4,
  same pattern) ships generic quadratic-algebra content derived from AU's
  retired Year 12 dict — content that predates and is unrelated to any of
  Grade 12's real elective menu, and the template's own header already
  disclaims it as "a display label, not a claim about what the United
  States teaches at Grade 12." So maths ships SOMETHING generic and
  non-claiming; science ships NOTHING. Both postures are internally
  consistent (neither claims curriculum accuracy for G12), so this is a
  maintainer PREFERENCE call — align them or leave as-is — not a bug to
  silently fix. NGSS/CCSS content in the saved references verified accurate
  against nextgenscience.org's own topic arrangement and CCSS pathway
  descriptions — not fabricated.

**All three country reference sets (SG, IN, US) are now complete.** W8 can
be scoped as a whole; go/no-go and ordering (which country's content work
starts first) is the maintainer's call, not decided here.

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
