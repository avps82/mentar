---
type: Mentar Curriculum Template
title: "English — Class 11 (India, general)"
tags: [IN, english, "Class 11", generic, senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 11 English (GENERIC pack).
# Deliberately board-agnostic: NO claimed alignment to any syllabus, no authority
# codes, no reproduced syllabus text — NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack
# (docs/CONTENT_LICENSES.md §2b). Content is universally-taught senior english at
# roughly this difficulty, 100% Mentar-authored/reused-generic; the level name is a
# display label, not a claim about what India teaches at Class 11.
#
# 2026-08-15: the generic packs stopped at stage 8 while AU ran to Year 12, so
# India, Singapore and the US had no senior maths or English at all. The senior
# stages are DERIVED from AU's own Year 9-12 generator dicts (engine/generic_items.py
# and generic_english_items.py), so a generic senior level cannot drift from its AU
# counterpart. Science at this level is a SPLIT subject and lives in
# engine/senior_science_items.py, not here.

template_id: in-c11-english
country: IN
year_level: "Class 11"
subject: english
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "English — Class 11 🇮🇳 (general)"
icon: "1️⃣1️⃣"
description: "Naming techniques in a quotation, argument structure and register — general senior english at roughly Class 11 level."
item_source: in_c11_english

language_register:
  reading_level: "~ages 16-17"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# Independent nodes (separate strands, no natural prereq chain), from the shared
# senior stage table. Seeds are REAL draws from the generators, not paraphrases.
concepts:

  - id: in_c11_textual_analysis
    label: "Naming the technique in a quotation"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a metaphor (says one thing IS another)? A) Her voice was a warm blanket.  B) The old house sighed in the heat.  C) The clock scolded us from the wall.  D) The wind argued with the shutters.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_argument_structure
    label: "Claim, evidence and rebuttal"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a REBUTTAL (answering the opposing view)? A) Public transport should be free at peak times.  B) Opponents call it a luxury, yet the demand is measurable.  C) Sleep studies show teenagers need nine hours.  D) Local libraries deserve more funding.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_register_shift
    label: "Matching register to audience"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is FORMAL register (suited to an academic essay)? A) So there are three ways people explain it.  B) Looks like it got a bit better.  C) This paper examines three competing explanations.  D) Yeah, that didn't go how we thought.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# India — Class 11 English (generic, senior)

A board-agnostic senior pack: universally-taught topics at roughly Class 11 difficulty,
with **no claimed alignment** to any curriculum authority. NCERT/CBSE/ICSE licences do not permit a claimed-alignment pack.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
