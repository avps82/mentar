---
type: Mentar Curriculum Template
title: "Chemistry — Class 11 (India, senior)"
tags: [IN, chemistry, "Class 11", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — India, Class 11 Chemistry.
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

template_id: in-c11-chemistry
country: IN
year_level: "Class 11"
subject: chemistry
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Chemistry — Class 11"
icon: "🧪"
description: "Bonding types, groups of the periodic table, and the mole — senior chemistry at roughly Class 11 level."
item_source: in_c11_chemistry

language_register:
  reading_level: "~ages 16-17"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: in_c11_bonding_types
    label: "Ionic, covalent and metallic bonding"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an IONIC compound (a metal with a non-metal, electrons transferred)? A) sodium chloride  B) iron  C) aluminium  D) copper. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_periodic_groups
    label: "Groups of the periodic table"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a Group 1 alkali metal (very reactive, one outer electron)? A) lithium  B) neon  C) argon  D) helium. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: in_c11_mole_concept
    label: "The mole and amount of substance"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a measure of the AMOUNT of substance? A) the mole  B) moles per litre  C) molarity  D) mol/L. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c11_atomic_structure
    label: "Atomic structure"
    strand: "Atomic structure"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which statement is true of NEUTRONS? A) their count defines which element the atom is  B) changing their count makes an isotope of the same element  C) they occupy shells around the nucleus and set the chemistry  D) the particles lost or gained when ions form. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c11_gas_laws
    label: "Gas laws"
    strand: "Gas laws"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is what happens when a gas is HEATED at fixed volume? A) its pressure rises as particles hit the walls harder and more often  B) its pressure rises because the same particles are squeezed into a smaller space  C) a balloon in the sun swelling up  D) its volume falls while pressure × volume stays constant. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c11_reaction_kinds
    label: "Kinds of chemical reaction"
    strand: "Chemical reactions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a COMBUSTION reaction? A) two clear solutions mixed and an insoluble solid forming  B) methane burning in oxygen to give carbon dioxide and water  C) one compound breaking into simpler substances when heated  D) hydrogen peroxide breaking down into water and oxygen. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: in_c11_organic_basics
    label: "Organic families"
    strand: "Organic basics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an ALCOHOL (contains an -OH group)? A) methane  B) ethene  C) propane  D) methanol. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# India — Class 11 Chemistry (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior chemistry at roughly this level.

Node ids are prefixed `in_c11_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
