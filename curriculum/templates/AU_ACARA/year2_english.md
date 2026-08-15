---
type: Mentar Curriculum Template
title: "English — Year 2 (AU)"
tags: [AU, english, "Year 2"]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — Australia, Year 2 English (Language/Literacy strands)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR2_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year2-english
country: AU
year_level: "Year 2"
subject: english
curriculum_standard: "ACARA v9 (AC9E2A Language)"
schema_version: "0.1"
label: "English — Year 2 🇦🇺"                        # R3.1: web picker catalog fields
icon: "📖"
description: "Word classes, synonyms, plurals and rhyming words (Australian Year 2)."
item_source: au_english_year2

language_register:
  reading_level: "~Year 2 / ages 6-7"
  vocabulary_note: "Very short sentences. Everyday words only."

# 4 independent nodes (separate vocabulary/grammar strands, no natural prereq chain).
# All mc4 via engine/itemgen.py's shared mc_which_is helper over a curated,
# hand-verified pairwise-disjoint word table per node — same mechanism as the
# evergreen practice/english.md pack, but with grade-differentiated word choices
# and ACARA-code alignment for traceability.
concepts:

  - id: aue2_word_classes
    label: "Naming, doing and describing words"          # AC9E2A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a naming word (noun)? A) run  B) dog  C) happy  D) jump. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue2_synonyms
    label: "Simple synonyms"                              # AC9E2A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the SAME as 'happy'? A) glad  B) run  C) box  D) tree. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue2_plurals
    label: "Plural forms"                                 # AC9E2A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is the plural of 'child'? A) childs  B) children  C) childes  D) child. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue2_rhyming
    label: "Rhyming words"                                # AC9E2A alignment
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word rhymes with 'pig'? A) big  B) cat  C) run  D) sun. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 2 English (Language, Literacy)

ACARA v9 English (Language strand), Year 2 — sibling of `year2_maths.md` in the
per-country/per-year pattern (SPEC §6), and the first AU-specific English template
(`year3_maths.md`/`year4_maths.md` had no English counterpart before R14a). Every node
reuses `engine/itemgen.py`'s shared `mc_which_is` helper (the same mechanism the
evergreen `practice/english.md` pack uses) over a NEW, grade-differentiated, hand-verified
pairwise-disjoint word table — not a re-skin of the practice pack's tables.

**Alignment note:** the AC9E2A codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability. Question text, labels and word tables are
Mentar-authored. ACARA core curriculum content is CC BY 4.0 (verified 2026-07-10 —
`docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced in this template. The
National Literacy Learning Progressions (a separate ACARA document, CC BY-NC 4.0) are NOT
used as a source here.
