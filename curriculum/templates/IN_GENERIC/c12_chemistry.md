---
type: Mentar Curriculum Template
title: "Chemistry — Class 12 (India, senior)"
tags: [IN, chemistry, "Class 12", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 12 Chemistry.
# SENIOR SCIENCE IS A SPLIT SUBJECT. Junior years ship one combined "Science"
# pack because that is what a student studies; at senior level they enrol in
# Physics, Chemistry or Biology separately, so shipping a merged pack here would
# misrepresent the curriculum (maintainer decision 2026-08-15: "senior science
# needs to split... let's follow the curriculum").
# NO claimed alignment: senior science is set by the CBSE/ICSE and state boards,
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior chemistry, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: in-c12-chemistry
country: IN
year_level: "Class 12"
subject: chemistry
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Chemistry — Class 12 🇮🇳"
icon: "🧪"
description: "Acids and bases, oxidation and reduction, and reaction rates — senior chemistry at roughly Class 12 level."
item_source: in_c12_chemistry

language_register:
  reading_level: "~ages 17-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: in_c12_acids_bases
    label: "Strong acids, weak acids and bases"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a STRONG acid (fully ionised in water)? A) hydrochloric acid  B) ammonia solution  C) calcium hydroxide  D) sodium hydroxide. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c12_redox
    label: "Oxidation and reduction"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is OXIDATION (loses electrons, oxidation number rises)? A) iron rusting in damp air  B) copper ions plating onto an electrode  C) iron oxide turning to iron in a blast furnace  D) a non-metal atom becoming a negative ion. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c12_reaction_rates
    label: "What changes the rate of a reaction"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these changes speeds a reaction up? A) raising the temperature  B) cooling the mixture  C) diluting the solution  D) using one large lump instead of powder. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
---

# India — Class 12 Chemistry (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior chemistry at roughly this level.

Node ids are prefixed `in_c12_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
