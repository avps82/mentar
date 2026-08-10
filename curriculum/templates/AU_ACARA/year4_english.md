---
type: Mentar Curriculum Template
title: "English — Year 4 (AU)"
tags: [AU, english, "Year 4"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 4 English (Language/Literacy strands)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR4_GENERATORS), so the deterministic verifier scores every answer.
# Fills the Y4 English gap the 2026-08 audit flagged (only Y2/Y5/Y6 existed).

template_id: au-year4-english
country: AU
year_level: "Year 4"
subject: english
curriculum_standard: "ACARA v9 (AC9E4A Language)"
schema_version: "0.1"
label: "English — Year 4 🇦🇺"                        # R3.1: web picker catalog fields
icon: "4️⃣"
description: "Suffixes, contractions, common/proper nouns and similes (Australian Year 4)."
item_source: au_english_year4

language_register:
  reading_level: "~Year 4 / ages 9-10"
  vocabulary_note: "Short sentences. Plain everyday words."

# 4 independent nodes — same shape as year2_english.md/year3_english.md.
# All mc4 via mc_which_is over a curated, hand-verified pairwise-disjoint word
# table per node.
concepts:

  - id: aue4_suffixes
    label: "Word suffixes (-ful, -less, -ness)"           # AC9E4A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these words ends with the suffix -ness (a state of being)? A) happiness  B) careful  C) careless  D) joyful. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue4_contractions
    label: "Contractions (don't, can't, it's)"             # AC9E4A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which is the SHORT form (contraction) of 'do not'? A) don't  B) can't  C) it's  D) won't. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue4_common_proper_nouns
    label: "Common and proper nouns"                       # AC9E4A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a proper noun (needs a capital letter)? A) Australia  B) city  C) river  D) school. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue4_similes
    label: "Similes (using 'like' or 'as')"                # AC9E4A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a simile (uses 'like' or 'as' to compare)? A) ran like the wind  B) the dog ran fast  C) she sang a song  D) he was very brave. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 4 English (Language, Literacy)

ACARA v9 English (Language strand), Year 4 — sibling of `year2_english.md`/`year3_english.md`
in the per-country/per-year pattern (SPEC §6), closing the Y4 gap the 2026-08 explain-method
audit flagged. `aue4_similes` deliberately introduces simile RECOGNITION alone, one year
before `year6_english.md`'s `aue6_figurative_language` asks the child to distinguish a
simile from a metaphor.

**Alignment note:** the AC9E4A codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and word tables are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template.
