---
type: Mentar Curriculum Template
title: "English — Year 3 (AU)"
tags: [AU, english, "Year 3"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 3 English (Language/Literacy strands)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR3_GENERATORS), so the deterministic verifier scores every answer.
# Fills the Y3 English gap the 2026-08 audit flagged (only Y2/Y5/Y6 existed).

template_id: au-year3-english
country: AU
year_level: "Year 3"
subject: english
curriculum_standard: "ACARA v9 (AC9E3A Language)"
schema_version: "0.1"
label: "English — Year 3 🇦🇺"                        # R3.1: web picker catalog fields
icon: "📖"
description: "Antonyms, prefixes, homophones and comparative adjectives (Australian Year 3)."
item_source: au_english_year3

language_register:
  reading_level: "~Year 3 / ages 8-9"
  vocabulary_note: "Short sentences. Plain everyday words."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain) —
# same shape as year2_english.md. All mc4 via mc_which_is over a curated,
# hand-verified pairwise-disjoint word table per node.
concepts:

  - id: aue3_antonyms
    label: "Antonyms (opposite words)"                    # AC9E3A alignment
    strand: "Vocabulary"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the OPPOSITE of 'hot'? A) cold  B) big  C) run  D) happy. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue3_prefixes
    label: "Word prefixes (un-, re-, dis-)"                # AC9E3A alignment
    strand: "Vocabulary"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these words begins with the prefix un- (not / opposite)? A) unhappy  B) replay  C) dislike  D) return. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue3_homophones
    label: "Homophones (their/there, to/too)"              # AC9E3A alignment
    strand: "Vocabulary"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means 'in this place'? A) here  B) hear  C) there  D) too. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue3_adjectives_comparative
    label: "Comparative and superlative adjectives"        # AC9E3A alignment
    strand: "Grammar"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a comparative adjective (comparing TWO things)? A) bigger  B) biggest  C) big  D) run. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 3 English (Language, Literacy)

ACARA v9 English (Language strand), Year 3 — sibling of `year2_english.md`/`year5_english.md`
in the per-country/per-year pattern (SPEC §6), closing the Y3 gap the 2026-08 explain-method
audit flagged. Every node reuses `engine/itemgen.py`'s shared `mc_which_is` helper over a
NEW, grade-differentiated, hand-verified pairwise-disjoint word table.

**Alignment note:** the AC9E3A codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and word tables are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
