---
type: Mentar Curriculum Template
title: "English — Year 10 (AU)"
tags: [AU, english, "Year 10"]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — Australia, Year 10 English.
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes are
# alignment REFERENCES and PROVISIONAL for this year level; all labels and
# questions are Mentar-authored — see docs/CONTENT_LICENSES.md; ACARA core
# content is CC BY 4.0).
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR10_GENERATORS), so the deterministic verifier scores every answer.
#
# 2026-08-14: this pack closes the breadth asymmetry AU maths never had — maths
# ran to Year 12 while english stopped at Year 8, a gap nobody had ratified.

template_id: au-year10-english
country: AU
year_level: "Year 10"
subject: english
curriculum_standard: "ACARA v9 (AC9E10A Language, provisional)"
schema_version: "0.1"
label: "English — Year 10 🇦🇺"
icon: "🔟"
description: "Tone, irony and satire, evaluative language and cohesion (Australian Year 10)."
item_source: au_english_year10

language_register:
  reading_level: "~Year 10 / ages 15-16"
  vocabulary_note: "Clear sentences. Senior-secondary vocabulary."

# 4 independent nodes (separate strands, no natural prereq chain) — same shape
# as every other AU english template. Seeds below are REAL draws from the
# generators, not paraphrases of them.
concepts:

  - id: aue10_tone
    label: "Identifying tone"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these takes a NEUTRAL, factual tone? A) The early results are genuinely encouraging.  B) There is every reason to expect a better year.  C) Rainfall was 12 mm below the monthly average.  D) The plan was careless and poorly argued.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue10_irony_satire
    label: "Irony and satire"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a literal statement (means exactly what it says)? A) Brilliant timing, she muttered as the bus pulled away.  B) What a perfect day for a picnic, he said in the pouring rain.  C) A mock award for the town's least useful new law.  D) The bus arrived four minutes late.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue10_evaluative_language
    label: "Evaluative and neutral language"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is NEUTRAL language (it reports)? A) a masterful reply  B) a reckless proposal  C) a disgraceful decision  D) a unanimous decision. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue10_cohesion
    label: "Cohesive devices between sentences"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a sequencing connective? A) subsequently  B) on the other hand  C) therefore  D) however. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# Australia — Year 10 English

Aligned to ACARA v9 content descriptions as REFERENCES only — every label and
question is Mentar-authored, and the codes are **provisional** for Year 10.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
