---
type: Mentar Curriculum Template
title: "English — Year 5 (AU)"
tags: [AU, english, "Year 5"]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — Australia, Year 5 English (Language/Literacy strands)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR5_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year5-english
country: AU
year_level: "Year 5"
subject: english
curriculum_standard: "ACARA v9 (AC9E5A Language)"
schema_version: "0.1"
label: "English — Year 5 🇦🇺"                        # R3.1: web picker catalog fields
icon: "📖"
description: "Richer synonyms and antonyms, adverbs/pronouns and compound words (Australian Year 5)."
item_source: au_english_year5

language_register:
  reading_level: "~Year 5 / ages 10-11"
  vocabulary_note: "Clear sentences. Richer vocabulary than Year 2."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via mc_which_is over new, harder curated tables than year2_english.md.
concepts:

  - id: aue5_synonyms_advanced
    label: "Synonyms (richer vocabulary)"                 # AC9E5A alignment
    strand: "Vocabulary"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the SAME as 'exhausted'? A) odd  B) thrilled  C) enraged  D) tired. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue5_antonyms_advanced
    label: "Antonyms (richer vocabulary)"                 # AC9E5A alignment
    strand: "Vocabulary"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the OPPOSITE of 'ancient'? A) scarce  B) stingy  C) modern  D) fake. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue5_word_classes_advanced
    label: "Adverbs, pronouns and verbs"                  # AC9E5A alignment
    strand: "Grammar"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a verb? A) walk  B) she  C) quietly  D) it. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue5_compound_words
    label: "Compound words"                               # AC9E5A alignment
    strand: "Spelling"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these IS a real compound word? A) sunflower  B) moonbrush  C) chairwater  D) tablesong. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue5_persuasive_starters
    label: "Persuasive writing moves"
    strand: "Persuasive writing"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an INFORMATIVE (not persuasive) line? A) “furthermore”, linking one argument to the next  B) “The school has 400 students and 12 classrooms.”  C) “on the other hand”, admitting the other side before answering it  D) “Every student deserves a safe ride to school — here is why.”. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue5_commas
    label: "Commas"
    strand: "Punctuation"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a comma used CORRECTLY after an opener? A) We packed hats snacks water and a map.  B) After the storm, the street was covered in leaves.  C) The stall sold apples, pears, plums and grapes.  D) We packed hats, snacks, water and a map.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: aue5_skimming_scanning
    label: "Ways of reading"
    strand: "Reading"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is SKIMMING a text? A) running your eyes over headings to get the gist  B) reading every sentence carefully to study the meaning  C) running a finger down a timetable for the 3 o'clock bus  D) hunting for one date or name without reading everything. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 5 English (Language, Literacy)

ACARA v9 English (Language strand), Year 5 — sibling of `year2_english.md` and
`year2_maths.md`/`year5_maths.md` in the per-country/per-year pattern (SPEC §6). Every node
reuses `engine/itemgen.py`'s shared `mc_which_is` helper over a NEW, genuinely
grade-differentiated word table (nuanced vocabulary and grammar categories a Year 2 child
wouldn't yet know), hand-verified pairwise-disjoint before shipping.

**Alignment note:** the AC9E5A codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and word tables are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template. The
National Literacy Learning Progressions (a separate ACARA document, CC BY-NC 4.0) are NOT
used as a source here.
