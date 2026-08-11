---
type: Mentar Curriculum Template
title: "Science — Year 6 (AU)"
tags: [AU, science, "Year 6"]
timestamp: "2026-08-11T00:00:00Z"
# Mentar curriculum template — Australia, Year 6 Science (Science Understanding strand)
# Aligned to ACARA Australian Curriculum v9 content descriptions (codes below are
# alignment REFERENCES; all labels/questions are Mentar-authored — see
# docs/CONTENT_LICENSES.md; ACARA core content is CC BY 4.0).
# Codes and content-description mapping identified via general curriculum knowledge, not
# fetched verbatim from the primary ACARA site (blocked to automated fetch) -- treat as
# PROVISIONAL pending a direct-source check before wider release, same caveat
# year2_science.md-year5_science.md already carry for their own codes.
# All items come from parametric generators (engine/science_items.py
# AU_SCIENCE_YEAR6_GENERATORS), so the deterministic verifier scores every answer.

template_id: au-year6-science
country: AU
year_level: "Year 6"
subject: science
curriculum_standard: "ACARA v9 (AC9S6 Science Understanding)"
schema_version: "0.1"
label: "Science — Year 6 🇦🇺"                          # R3.1: web picker catalog fields
icon: "🔬"
description: "Vertebrates and invertebrates, electrical conductors and insulators, and reversible/irreversible changes (Australian Year 6 Science)."
item_source: au_science_year6

language_register:
  reading_level: "~Year 6 / ages 11-12"
  vocabulary_note: "Clear sentences. Everyday examples. Multiple-choice, answer with a letter."

# 3 nodes: vertebrates, circuits, reversible change -- all independent roots, same shape
# as year2_science.md through year5_science.md.
concepts:

  - id: au6_science_vertebrates
    label: "Vertebrates and invertebrates"                           # AC9S6U01 (provisional)
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a vertebrate (has a backbone)? A) a dog  B) a worm  C) a spider  D) a snail. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au6_science_circuits
    label: "Electrical conductors and insulators"                    # AC9S6U02 (provisional)
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a good conductor of electricity? A) copper wire  B) a rubber band  C) a plastic ruler  D) a wooden spoon. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

  - id: au6_science_reversible_change
    label: "Reversible and irreversible changes"                     # AC9S6U03 (provisional)
    prereqs: []
    grounding: {}
    transfer_seeds:
      - "Which of these is a reversible change (can be undone)? A) melting chocolate  B) burning paper  C) baking a cake  D) rusting iron. Answer with the letter."
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors: { guess: 0.25, slip: 0.1, learns: 0.2, forgets: 0 }

---

# Australia — Year 6 Science

Extends `year2_science.md`–`year5_science.md`'s proven 3-node shape one year further:
vertebrate/invertebrate classification (Biological sciences), electrical conductors and
insulators (Physical sciences), and reversible vs. irreversible change (Chemical sciences —
the broader distinction `year4_science.md`'s state-change node sits inside: melting/freezing
are always reversible, this node adds chemical changes like burning/rusting/baking that are
not). Every node reuses `engine/itemgen.py`'s shared `mc_which_is` helper over a NEW,
hand-verified pairwise-disjoint fact table — the LLM never decides correctness (SPEC §14).

**Alignment note:** the AC9S6U0x codes in the node comments are references to ACARA v9
content descriptions for alignment/traceability, identified via general curriculum
knowledge (not fetched verbatim from the primary ACARA site, which is blocked to automated
fetch) — marked **provisional** pending a direct-source check, the same caveat
`year2_science.md`–`year5_science.md` already carry for their own codes. Question text,
labels and fact tables are Mentar-authored. ACARA core curriculum content is CC BY 4.0
(verified 2026-07-10 — `docs/CONTENT_LICENSES.md`); no ACARA descriptor text is reproduced
in this template.
