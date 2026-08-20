---
type: Mentar Curriculum Template
title: "Chemistry — Grade 10 (the United States, senior)"
tags: [US, chemistry, "Grade 10", senior]
timestamp: "2026-08-15T00:00:00Z"
# Mentar curriculum template — the United States, Grade 10 Chemistry.
# SENIOR SCIENCE IS A SPLIT SUBJECT, and in the US it is also SEQUENCED. Junior
# grades ship one combined "Science" pack because that is what a student studies.
# High school does not: the common US pattern is a whole year on Biology (Grade
# 9), then Chemistry (Grade 10), then Physics (Grade 11) -- one subject at a
# time, rather than the three in parallel that Australia, India and Singapore
# run. So this pack is a FULL YEAR of chemistry: both senior stages of it,
# six nodes, where a parallel-country senior pack carries three.
# Grade 12 is deliberately not shipped -- it is electives (AP, anatomy,
# environmental science, or none), which has no single shape to model.
# NO claimed alignment: senior science is set by state boards and district frameworks,
# not by one national content-description set (docs/CONTENT_LICENSES.md §2b).
# Content is universally-taught senior chemistry, 100% Mentar-authored.
# Items come from shared parametric generators (engine/senior_science_items.py),
# so the deterministic verifier scores every answer.

template_id: us-g10-chemistry
country: US
year_level: "Grade 10"
subject: chemistry
curriculum_standard: null                            # none claimed — see comment above
schema_version: "0.1"
label: "Chemistry — Grade 10 🇺🇸"
icon: "🧪"
description: "Bonding, the periodic table and the mole, then acids and bases, redox and reaction rates — senior chemistry at roughly Grade 10 level."
item_source: us_g10_chemistry

language_register:
  reading_level: "~ages 14-18"
  vocabulary_note: "Precise subject vocabulary. One idea per question."

# 6 independent nodes (separate strands, no natural prereq chain). All mc4 via
# engine/itemgen.py's shared mc_which_is helper; every generator passes glosses,
# so every node also carries an explain-mode method card
# (docs/design/explain_mode_design.md Type 4). Seeds are REAL draws.
concepts:

  - id: us_g10_bonding_types
    label: "Ionic, covalent and metallic bonding"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an IONIC compound (a metal with a non-metal, electrons transferred)? A) sodium chloride  B) iron  C) aluminium  D) copper. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g10_periodic_groups
    label: "Groups of the periodic table"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a Group 1 alkali metal (very reactive, one outer electron)? A) lithium  B) neon  C) argon  D) helium. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g10_mole_concept
    label: "The mole and amount of substance"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a measure of the AMOUNT of substance? A) the mole  B) moles per litre  C) molarity  D) mol/L. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g10_acids_bases
    label: "Strong acids, weak acids and bases"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a STRONG acid (fully ionised in water)? A) hydrochloric acid  B) ammonia solution  C) calcium hydroxide  D) sodium hydroxide. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g10_redox
    label: "Oxidation and reduction"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is OXIDATION (loses electrons, oxidation number rises)? A) iron rusting in damp air  B) copper ions plating onto an electrode  C) iron oxide turning to iron in a blast furnace  D) a non-metal atom becoming a negative ion. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: us_g10_reaction_rates
    label: "What changes the rate of a reaction"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these changes speeds a reaction up? A) raising the temperature  B) cooling the mixture  C) diluting the solution  D) using one large lump instead of powder. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g10_atomic_structure
    label: "Atomic structure"
    strand: "Atomic structure"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which statement is true of ELECTRONS? A) they occupy shells around the nucleus and set the chemistry  B) positively charged particles in the nucleus  C) their count defines which element the atom is  D) uncharged particles that add mass to the nucleus. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g10_gas_laws
    label: "Gas laws"
    strand: "Gas laws"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is what happens when a gas is HEATED at fixed volume? A) a balloon in the sun swelling up  B) it expands, taking up more volume  C) its pressure rises as particles hit the walls harder and more often  D) its pressure rises because the same particles hit the walls more often. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g10_reaction_kinds
    label: "Kinds of chemical reaction"
    strand: "Chemical reactions"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a DECOMPOSITION reaction? A) hydrogen peroxide breaking down into water and oxygen  B) methane burning in oxygen to give carbon dioxide and water  C) silver nitrate and salt solution giving a white solid  D) two clear solutions mixed and an insoluble solid forming. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g10_organic_basics
    label: "Organic families"
    strand: "Organic basics"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is an ALKENE (contains a C=C double bond)? A) propene  B) propane  C) methane  D) ethanol. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g10_equilibrium
    label: "Chemical equilibrium"
    strand: "Equilibrium"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a change that SHIFTS an equilibrium? A) raising the temperature of the mixture  B) the amounts of reactants and products stay constant, though both reactions continue  C) the yield the reaction eventually settles at  D) the forward and reverse reactions run at equal rates. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g10_electrochemistry
    label: "Electrochemical cells"
    strand: "Electrochemistry"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is true of an ELECTROLYTIC cell? A) an external power supply forces a non-spontaneous reaction  B) chemical energy is converted into electrical energy  C) oxidation happens at the anode  D) a spontaneous reaction generates an electric current. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }
  - id: us_g10_organic_synthesis
    label: "Organic reaction types"
    strand: "Organic synthesis"
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a SUBSTITUTION reaction? A) bromine adding across a C=C double bond, decolourising  B) the reaction that makes an ester plus water  C) one hydrogen on an alkane swapped for a chlorine atom  D) ethene + hydrogen becoming ethane across the double bond. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# the United States — Grade 10 Chemistry (senior)

**No claimed alignment** to any certificate authority's units — these nodes are
universally-taught senior chemistry at roughly this level.

Node ids are prefixed `us_g10_`; the generators are shared across all three
countries' senior packs (`engine/senior_science_items.py` — one progression, keyed
by senior stage). The deterministic verifier scores every answer; the model never
decides correctness (SPEC §14).
