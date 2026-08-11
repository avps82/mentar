---
type: Mentar Curriculum Template
title: "Science — Year 5 (AU)"
tags: [AU, science, "Year 5"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 5 Science (Science Understanding strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# Codes and content-description mapping identified via general curriculum knowledge, not
# fetched verbatim from the primary ACARA site (blocked to automated fetch) -- treat as
# PROVISIONAL pending a direct-source check before wider release, same caveat
# year2_science.md/year3_science.md/year4_science.md already carry for their own codes.
# All items come from parametric generators (engine/science_items.py
# AU_SCIENCE_YEAR5_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year5-science
country: AU
year_level: "Year 5"
subject: science
curriculum_standard: "ACARA v9 (AC9S5 Science Understanding)"
schema_version: "0.1"
label: "Science — Year 5 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔬"
description: "Animal adaptations, dissolving in water, and transparent vs. opaque materials (Australian Year 5 Science)."
item_source: au_science_year5

language_register:
  reading_level: "~Year 5 / ages 10-11"
  vocabulary_note: "Clear sentences. Everyday examples. Multiple-choice, answer with a letter."

# 3 nodes: adaptations, dissolving, light materials -- all independent roots, same shape
# as year2_science.md through year4_science.md.
concepts:

  - id: au5_science_adaptations
    label: "Body features that help survival (adaptations)"          # AC9S5U01 (provisional)
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a body feature that helps an animal survive in its habitat? A) a polar bear's thick fur  B) a dog's collar  C) a horse's saddle  D) a fish tank. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au5_science_dissolving
    label: "What dissolves in water"                                 # AC9S5U02 (provisional)
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these dissolves in water? A) salt  B) sand  C) oil  D) small stones. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au5_science_light_materials
    label: "Transparent and opaque materials"                        # AC9S5U03 (provisional)
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is transparent (lets light pass through clearly)? A) clear glass  B) a brick wall  C) a wooden door  D) a thick book. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 5 Science

Extends `year2_science.md` through `year4_science.md`'s proven 3-node shape one year
further: body-feature adaptations (Biological sciences), dissolving (Chemical sciences),
and transparent/opaque materials (Physical sciences — light). Every node reuses
`engine/itemgen.py`'s shared `mc_which_is` helper over a NEW, hand-verified pairwise-disjoint
fact table — the LLM never decides correctness (SPEC §14).

**Alignment note:** the AC9S5U0x codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability, identified via general curriculum
knowledge (not fetched verbatim from the primary ACARA site, which is blocked to automated
fetch) — marked **provisional** pending a direct-source check, the same caveat
`year2_science.md`–`year4_science.md` already carry for their own codes. Question text,
labels and fact tables are Mentar-authored. ACARA core curriculum content is CC BY 4.0
(verified 2026-07-10 — `docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced
in this template.
