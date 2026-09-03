---
type: Mentar Curriculum Template
title: "English — Class 10 (India, general)"
tags: [IN, english, "Class 10", generic, senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 10 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught senior english at
# roughly this difficulty, 100% Mentar-authored/reused-generic; the level name is a
# display label, not a claim about what India teaches at Class 10.
#
# 2026-08-15: the generic packs stopped at stage 8 while AU ran to Year 12, so
# India, Singapore and the US had no senior maths or English at all. The senior
# stages are DERIVED from AU's own Year 9-12 generator dicts (engine/generic_items.py
# and generic_english_items.py), so a generic senior level cannot drift from its AU
# counterpart. Science at this level is a SPLIT subject and lives in
# engine/senior_science_items.py, not here.

template_id: in-c10-english
country: IN
year_level: "Class 10"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Class 10 (general)"
icon: "📖"
description: "Tone, irony and satire, evaluative language and cohesion — general senior english at roughly Class 10 level."
item_source: in_c10_english

language_register:
  reading_level: "~ages 15-16"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# Independent nodes (separate strands, no natural prereq chain), from the shared
# senior stage table. Seeds are REAL draws from the generators, not paraphrases.
concepts:

  - id: in_c10_tone
    label: "Identifying tone"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these takes a CRITICAL tone? A) The plan was careless and poorly argued.  B) Rainfall was 12 mm below the monthly average.  C) The report was published in March.  D) The council met on Tuesday to review the plan.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c10_irony_satire
    label: "Irony and satire"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a literal statement (means exactly what it says)? A) A cartoon showing the minister asleep at a fire drill.  B) A mock award for the town's least useful new law.  C) What a perfect day for a picnic, he said in the pouring rain.  D) The bus arrived four minutes late.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c10_evaluative_language
    label: "Evaluative and neutral language"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is EVALUATIVE language (it judges)? A) a masterful reply  B) a unanimous decision  C) a same-day reply  D) a two-hour performance. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c10_cohesion
    label: "Cohesive devices between sentences"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a sequencing connective? A) whereas  B) however  C) on the other hand  D) firstly. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c10_reviewing_refining
    label: "Reviewing and refining"
    strand: "Reviewing and refining"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a REFINEMENT at sentence level? A) “your evidence is strong but I lost your thread in paragraph three”  B) replacing a vague 'very good' with a precise word  C) moving the strongest point from the middle to the front  D) cutting a paragraph that repeats an earlier one. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 10 English (generic, senior)

A board-agnostic senior pack: universally-taught topics at roughly Class 10 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
