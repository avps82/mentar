---
type: Mentar Curriculum Template
title: "English — Year 12 (AU)"
tags: [AU, english, "Year 12"]
timestamp: "2026-08-14T00:00:00Z"
# Mentar curriculum template — Australia, Year 12 English.
# NO claimed alignment: senior English is set by state certificate authorities,
# not by a single national content-description set (docs/CONTENT_LICENSES.md).
# Senior English is state-certificate territory (VCE/HSC/QCE/SACE...), which is
# why curriculum_standard is null here: these nodes are universally-taught
# technique and argument naming, NOT a claimed alignment to any state's units.
# All items come from parametric generators (engine/au_english_items.py
# AU_ENGLISH_YEAR12_GENERATORS), so the deterministic verifier scores every answer.
#
# 2026-08-14: this pack closes the breadth asymmetry AU maths never had — maths
# ran to Year 12 while english stopped at Year 8, a gap nobody had ratified.

template_id: au-year12-english
country: AU
year_level: "Year 12"
subject: english
curriculum_standard: null
schema_version: "0.1"
label: "English — Year 12 🇦🇺"
icon: "1️⃣2️⃣"
description: "Bias, allusion, syntax for effect and language change (senior English)."
item_source: au_english_year12

language_register:
  reading_level: "~Year 12 / ages 17-18"
  vocabulary_note: "Clear sentences. Senior-secondary vocabulary."

# 4 independent nodes (separate strands, no natural prereq chain) — same shape
# as every other AU english template. Seeds below are REAL draws from the
# generators, not paraphrases of them.
concepts:

  - id: aue12_bias
    label: "Biased and balanced wording"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is BALANCED wording (it reports the same event neutrally)? A) The cost was met from public funds.  B) A mob of protesters swarmed the square.  C) The so-called expert made yet another excuse.  D) Taxpayers were forced to foot the bill again.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue12_allusion
    label: "Allusion"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a plain description (no reference)? A) The plan had one serious weakness.  B) He met his Waterloo in the final round.  C) She opened a Pandora's box of paperwork.  D) The plan was his Achilles heel.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue12_syntax_for_effect
    label: "Syntax chosen for effect"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a long, accumulating sentence used to build detail? A) Across the valley, past the fence line and the dry creek, the smoke was already rising.  B) It failed.  C) Nobody moved.  D) That was the end.. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: aue12_language_change
    label: "How English changes over time"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a word COINED for new technology? A) bungalow  B) typhoon  C) kindergarten  D) podcast. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# Australia — Year 12 English

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught technique and argument naming at roughly this level.

The deterministic verifier scores every answer; the model never decides
correctness (SPEC §14).
