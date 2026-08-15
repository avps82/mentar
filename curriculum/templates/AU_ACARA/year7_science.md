---
type: Mentar Curriculum Template
title: "Science — Year 7 (AU)"
tags: [AU, science, "Year 7"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 7 Science (Science Understanding strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# Codes and content-description mapping identified via general curriculum knowledge, not
# fetched verbatim from the primary ACARA site (blocked to automated fetch) -- treat as
# PROVISIONAL pending a direct-source check before wider release, same caveat
# year2_science.md-year6_science.md already carry for their own codes.
# All items come from parametric generators (engine/science_items.py
# AU_SCIENCE_YEAR7_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year7-science
country: AU
year_level: "Year 7"
subject: science
curriculum_standard: "ACARA v9 (AC9S7 Science Understanding)"
schema_version: "0.1"
label: "Science — Year 7 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔬"
description: "Body systems, contact and non-contact forces, and pure substances vs. mixtures (Australian Year 7 Science)."
item_source: au_science_year7

language_register:
  reading_level: "~Year 7 / ages 12-13"
  vocabulary_note: "Clear sentences. Secondary-level vocabulary. Multiple-choice, answer with a letter."

# 3 nodes: body systems, forces, mixtures -- all independent roots, same shape as
# year2_science.md through year6_science.md.
concepts:

  - id: au7_science_body_systems
    label: "Digestive and circulatory systems"                       # AC9S7U01 (provisional)
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is part of the digestive system? A) the stomach  B) the heart  C) the veins  D) red blood cells. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au7_science_forces
    label: "Contact and non-contact forces"                          # AC9S7U02 (provisional)
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a non-contact force (acts at a distance)? A) gravity pulling an apple down  B) pushing a door  C) kicking a ball  D) pulling a rope. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au7_science_mixtures
    label: "Pure substances and mixtures"                            # AC9S7U03 (provisional)
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a mixture (more than one substance mixed together)? A) salt water  B) pure gold  C) oxygen gas  D) distilled water. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 7 Science

Extends `year2_science.md`–`year6_science.md`'s proven 3-node shape one year further:
digestive/circulatory body systems (Biological sciences), contact/non-contact forces
(Physical sciences), and pure substances vs. mixtures (Chemical sciences). Every node reuses
`engine/itemgen.py`'s shared `mc_which_is` helper over a NEW, hand-verified pairwise-disjoint
fact table — the LLM never decides correctness (SPEC §14).

**Alignment note:** the AC9S7U0x codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability, identified via general curriculum
knowledge (not fetched verbatim from the primary ACARA site, which is blocked to automated
fetch) — marked **provisional** pending a direct-source check, the same caveat
`year2_science.md`–`year6_science.md` already carry for their own codes. Question text,
labels and fact tables are Mentar-authored. ACARA core curriculum content is CC BY 4.0
(verified 2026-07-10 — `docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced
in this template.
