---
type: Mentar Curriculum Template
title: "Chemistry — Secondary 3 (Singapore, senior)"
tags: [SG, chemistry, "Secondary 3", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — Singapore, Secondary 3 Chemistry.
# SENIOR SCIENCE IS A SPLIT SUBJECT. Junior years ship one combined "Science"
# pack because that is what a student studies; at senior level they enrol in
# Physics, Chemistry or Biology separately, so shipping a merged pack here would
# misrepresent the curriculum (maintainer decision 2026-08-15: "senior science
# needs to split... let's follow the curriculum").
# NO claimed alignment: senior science is set by the Singapore-Cambridge examination syllabuses,
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior chemistry, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: sg-s3-chemistry
country: SG
year_level: "Secondary 3"
subject: chemistry
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Chemistry — Secondary 3"
icon: "🧪"
description: "Bonding types, groups of the periodic table, and the mole — senior chemistry at roughly Secondary 3 level."
item_source: sg_s3_chemistry

language_register:
  reading_level: "~ages 16-17"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 3 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: sg_s3_bonding_types
    label: "Ionic, covalent and metallic bonding"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an IONIC compound (a metal with a non-metal, electrons transferred)? A) sodium chloride  B) iron  C) aluminium  D) copper. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s3_periodic_groups
    label: "Groups of the periodic table"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a Group 1 alkali metal (very reactive, one outer electron)? A) lithium  B) neon  C) argon  D) helium. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: sg_s3_mole_concept
    label: "The mole and amount of substance"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a measure of the AMOUNT of substance? A) the mole  B) moles per litre  C) molarity  D) mol/L. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s3_atomic_structure
    label: "Atomic structure"
    strand: "Atomic structure"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which statement is true of PROTONS? A) they occupy shells around the nucleus and set the chemistry  B) the particles lost or gained when ions form  C) uncharged particles that add mass to the nucleus  D) positively charged particles in the nucleus. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s3_gas_laws
    label: "Gas laws"
    strand: "Gas laws"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is what happens when a gas is HEATED at fixed pressure? A) its pressure rises because the same particles are squeezed into a smaller space  B) it expands, taking up more volume  C) its volume falls while pressure × volume stays constant  D) its pressure rises as particles hit the walls harder and more often. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s3_reaction_kinds
    label: "Kinds of chemical reaction"
    strand: "Chemical reactions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a PRECIPITATION reaction? A) two clear solutions mixed and an insoluble solid forming  B) hydrogen peroxide breaking down into water and oxygen  C) a fuel reacting with oxygen and releasing heat  D) one compound breaking into simpler substances when heated. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: sg_s3_organic_basics
    label: "Organic families"
    strand: "Organic basics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an ALKENE (contains a C=C double bond)? A) propane  B) methanol  C) methane  D) ethene. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Singapore — Secondary 3 Chemistry (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior chemistry at roughly this level.

Node ids are prefixed `sg_s3_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
