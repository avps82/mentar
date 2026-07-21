---
type: Mentar Curriculum Template
title: "Practice — English"
tags: [practice, english]
timestamp: "2026-07-22T00:00:00Z"
# Mentar curriculum template — evergreen English practice sampler.
# Country-agnostic drill content (never expires, no curriculum authority owns it) --
# always available under the picker's "Try-out topics" group, separate from any
# country-curriculum templates. Multiple-choice only: the deterministic verifier
# (mc_choice) scores the child's letter against curated fact tables
# (engine/practice_items.py ENGLISH_PRACTICE_GENERATORS). The LLM never asserts
# the correct answer (SPEC §14 safety rule).

template_id: practice-english
country: null
year_level: pilot
subject: english
curriculum_standard: null
schema_version: "0.1"
label: "English practice 📖"                         # R3.1: web picker catalog fields
icon: "📖"
description: "Synonyms, rhymes, odd-one-out, and plurals -- quick vocabulary drills."
item_source: english_practice

language_register:
  reading_level: "~Year 3-5 / ages 8-10"
  vocabulary_note: "Short sentences. Multiple-choice, answer with a letter."

# 4 independent drill nodes -- no prerequisites, each a standalone practice skill.
concepts:

  - id: practice_synonyms_antonyms
    label: "Synonyms and antonyms"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word means the SAME as 'happy'? A) glad  B) sad  C) tiny  D) fast. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: practice_rhyming_words
    label: "Rhyming words"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which word rhymes with 'cat'? A) hat  B) dog  C) sun  D) tree. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: practice_odd_one_out
    label: "Odd one out"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which one does NOT belong with the others? A) apple  B) banana  C) carrot  D) grape. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: practice_plural_forms
    label: "Plural forms"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "What is the plural of 'child'? A) childs  B) children  C) childes  D) child. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# English practice (evergreen sampler)

A permanent "Try-out topics" fixture, separate from country-curriculum content --
quick, repeatable vocabulary drills (synonyms/antonyms, rhymes, odd-one-out,
irregular plurals) that stay relevant regardless of which country's curriculum a
family is following. Every item is generated from a small curated fact table (never
the LLM) and scored by the deterministic verifier.
