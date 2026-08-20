---
type: Mentar Curriculum Template
title: "English — Year 6 (AU)"
tags: [AU, english, "Year 6"]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — Australia, Year 6 English (Language/Literacy strands)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR6_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year6-english
country: AU
year_level: "Year 6"
subject: english
curriculum_standard: "ACARA v9 (AC9E6A Language)"
schema_version: "0.1"
label: "English — Year 6 🇦🇺"                        # R3.1: web picker catalog fields
icon: "📖"
description: "Similes and metaphors, nuanced synonyms/antonyms, conjunctions and prepositions (Australian Year 6)."
item_source: au_english_year6

language_register:
  reading_level: "~Year 6 / ages 11-12"
  vocabulary_note: "Clear sentences. Nuanced vocabulary and figurative language."

# 4 independent nodes (separate vocabulary/grammar/figurative-language strands, no
# natural prereq chain). All mc4 via mc_which_is over new, harder curated tables than
# year2_english.md/year5_english.md.
concepts:

  - id: aue6_figurative_language
    label: "Similes and metaphors"                        # AC9E6A alignment
    strand: "Text analysis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a simile (uses 'like' or 'as')? A) as brave as a lion  B) time is money  C) her heart is a stone  D) the world is a stage. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue6_synonyms_nuanced
    label: "Synonyms (nuanced vocabulary)"                # AC9E6A alignment
    strand: "Vocabulary"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the SAME as 'reluctant'? A) hesitant  B) eager  C) angry  D) calm. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue6_antonyms_nuanced
    label: "Antonyms (nuanced vocabulary)"                # AC9E6A alignment
    strand: "Vocabulary"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the OPPOSITE of 'transparent'? A) opaque  B) clear  C) bright  D) thin. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue6_word_classes_conjunctions_prepositions
    label: "Conjunctions and prepositions"                # AC9E6A alignment
    strand: "Grammar"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a conjunction (joins two ideas)? A) because  B) under  C) quickly  D) she. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 6 English (Language, Literacy)

ACARA v9 English (Language strand), Year 6 — sibling of `year2_english.md`/`year5_english.md`
and `year2_maths.md`–`year6_maths.md` in the per-country/per-year pattern (SPEC §6). Every
node reuses `engine/itemgen.py`'s shared `mc_which_is` helper over a NEW curated table —
figurative language and nuanced vocabulary/grammar categories that build on Year 2/5's
foundations without repeating them.

**Alignment note:** the AC9E6A codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and word tables are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template. The
National Literacy Learning Progressions (a separate ACARA document, CC BY-NC 4.0) are NOT
used as a source here.
