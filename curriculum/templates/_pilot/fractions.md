---
# Mentar pilot template — fractions (Phase 0)
# Spec: docs/SPEC.md §23 (sample graph); schema: docs/PHASE0.md W3.1; authoring: W3.2.

template_id: pilot-fractions
country: null                                       # cross-country pilot, not bound to a single curriculum
year_level: pilot                                   # roughly Year 3-4 / Grade 3-4, ages 8-9
subject: mathematics
curriculum_standard: null
schema_version: "0.1"

language_register:
  reading_level: "~Year 3-4 / ages 8-9"
  vocabulary_note: "Short sentences. Concrete examples (pizza, glasses, chocolate bars, walking distance). Avoid algebraic notation; prefer 'top number / bottom number' over 'numerator / denominator' until the vocabulary node introduces those terms."

# 8 concept nodes — DAG per SPEC §23 sample plus one inserted node (equivalent_fractions)
# to give the comparing/adding nodes a stronger prereq spine.
#
# Graph edges:
#   whole_number_division
#     └─ fraction_as_part_of_whole
#          └─ equal_vs_unequal_parts
#               └─ unit_fractions
#                    └─ equivalent_fractions
#                         ├─ comparing_equal_denom
#                         └─ adding_equal_denom  ← pilot target node (SPEC §23)
#                              └─ subtracting_equal_denom
concepts:

  - id: whole_number_division
    label: "Whole-number division"
    prereqs: []
    grounding:
      source: wikipedia_simple
      anchor: "https://simple.wikipedia.org/wiki/Division_(mathematics)"
      passage_hint: "Definition + 'sharing equally' framing"
    transfer_seeds:
      - "You have 12 pencils to share equally between 4 friends. How many does each get?"
      - "Six children share 18 strawberries fairly. How many strawberries each?"
    verifier:
      answer_type: int
      checker: int_exact
    bkt_priors:
      guess: 0.05
      slip: 0.1
      learns: 0.2
      forgets: 0

  - id: fraction_as_part_of_whole
    label: "Fraction as a part of a whole"
    prereqs: [whole_number_division]
    grounding:
      source: vikidia
      anchor: "https://en.vikidia.org/wiki/Fraction"
      passage_hint: "Opening section — fraction as part of something"
    transfer_seeds:
      - "Which picture shows a circle split into parts that ARE fractions of the whole?"
      - "A chocolate bar is broken into pieces. Which arrangement shows the bar split into fractions of the whole?"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors:
      guess: 0.2
      slip: 0.1
      learns: 0.2
      forgets: 0

  - id: equal_vs_unequal_parts
    label: "Equal vs. unequal parts"
    prereqs: [fraction_as_part_of_whole]
    grounding:
      source: vikidia
      anchor: "https://en.vikidia.org/wiki/Fraction"
      passage_hint: "Equal parts requirement — why fractions need equal-size pieces"
    transfer_seeds:
      - "Two pizzas are each cut into 4 slices. In one, the slices are the same size; in the other, slices are different sizes. Which one is cut into FRACTIONS?"
      - "A ribbon is cut into 3 pieces of different lengths. Are these pieces thirds? Yes or no?"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors:
      guess: 0.2
      slip: 0.1
      learns: 0.2
      forgets: 0

  - id: unit_fractions
    label: "Unit fractions (1/n)"
    prereqs: [equal_vs_unequal_parts]
    grounding:
      source: vikidia
      anchor: "https://en.vikidia.org/wiki/Fraction"
      passage_hint: "Definition — one part of n equal parts"
    transfer_seeds:
      - "A glass is full of juice. You pour ONE of FIVE equal cups from it. What fraction of the juice did you pour?"
      - "A garden is divided into 8 equal beds. One bed has tomatoes. What fraction of the garden is tomatoes?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors:
      guess: 0.05
      slip: 0.1
      learns: 0.2
      forgets: 0

  - id: equivalent_fractions
    label: "Equivalent fractions (1/2 = 2/4 = 3/6)"
    prereqs: [unit_fractions]
    grounding:
      source: vikidia
      anchor: "https://en.vikidia.org/wiki/Fraction"
      passage_hint: "Equivalent fractions — same amount, different names"
    transfer_seeds:
      - "Sam ate 2 of 4 slices of a pizza. Mira ate 1 of 2 slices of an identical pizza. Did they eat the same amount?"
      - "Which of these fractions is the same amount as 1/3? (2/6, 2/4, 1/4, 3/9 — multiple may be correct)"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors:
      guess: 0.05
      slip: 0.1
      learns: 0.2
      forgets: 0

  - id: comparing_equal_denom
    label: "Comparing fractions with equal denominators"
    prereqs: [equivalent_fractions]
    grounding:
      source: vikidia
      anchor: "https://en.vikidia.org/wiki/Fraction"
      passage_hint: "Comparing fractions with the same bottom number"
    transfer_seeds:
      - "Lia drank 3/7 of her water bottle. Theo drank 5/7 of his (same-size bottle). Who drank more?"
      - "Which is bigger: 2/9 of a chocolate bar, or 4/9 of the same chocolate bar?"
    verifier:
      answer_type: mc4
      checker: mc_choice
    bkt_priors:
      guess: 0.2
      slip: 0.1
      learns: 0.2
      forgets: 0

  - id: adding_equal_denom
    label: "Adding fractions with equal denominators"
    prereqs: [equivalent_fractions]
    grounding:
      source: vikidia
      anchor: "https://en.vikidia.org/wiki/Fraction"
      passage_hint: "Adding fractions with the same bottom number"
    transfer_seeds:
      - "You eat 2 of 8 slices of a pizza for lunch and 3 of 8 slices for dinner. What fraction of the pizza did you eat in total?"
      - "Mira walks 1/5 of a kilometre to the park, then 2/5 of a kilometre to the shop. How far has she walked?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors:
      guess: 0.05
      slip: 0.1
      learns: 0.2
      forgets: 0

  - id: subtracting_equal_denom
    label: "Subtracting fractions with equal denominators"
    prereqs: [adding_equal_denom]
    grounding:
      source: vikidia
      anchor: "https://en.vikidia.org/wiki/Fraction"
      passage_hint: "Subtracting fractions with the same bottom number"
    transfer_seeds:
      - "A jug holds 7/10 of a litre of milk. You pour out 2/10 of a litre. How much milk is left?"
      - "Theo had 5/6 of a chocolate bar. He gave 2/6 of the bar to his sister. What fraction does Theo have now?"
    verifier:
      answer_type: fraction
      checker: fraction_equiv
    bkt_priors:
      guess: 0.05
      slip: 0.1
      learns: 0.2
      forgets: 0
---

# Mathematics — Pilot fractions

## Overview

This is the **Phase 0 pilot template** (SPEC §23). It is deliberately narrow: a single subject (fractions),
a single learning chain, ~8 concept nodes — chosen because fractions have clean prerequisites, checkable
numeric answers, and a deterministic verifier that lets us isolate the LLM-quality risk from the pedagogy
engine. The pilot is not country-bound.

## Prerequisite rationale

The chain follows the standard primary-math progression:

1. **Whole-number division** — fair sharing of integers is the conceptual anchor for "part of a whole."
2. **Fraction as part of a whole** — once a learner can split a quantity equally, they can name one of those parts.
3. **Equal vs. unequal parts** — a quiet but critical gate: many learners call any cut piece a "fraction," missing the equal-size requirement.
4. **Unit fractions (1/n)** — name a single part of n equal parts; the smallest fraction primitive.
5. **Equivalent fractions** — a gate before any equal-denominator comparison or arithmetic: learners must internalise that 2/4 and 1/2 are the same amount before "same bottom number" arithmetic feels meaningful.
6. **Comparing equal denominators** — once equivalence is grasped, comparing under a fixed denominator is just comparing top numbers.
7. **Adding equal denominators** — the pilot target node (SPEC §23).
8. **Subtracting equal denominators** — symmetric counterpart to adding; useful for transfer testing.

The graph has one root (`whole_number_division`) and two leaves (`comparing_equal_denom`, `subtracting_equal_denom`).
The pilot's success criterion (SPEC §23 / 26.7 P1) is reaching ≥6 nodes via fringe selection only.

## Calibration notes

- Vocabulary: prefer "top number" and "bottom number" over "numerator" / "denominator" in re-explanations.
  The terminology appears in grounding passages but is not load-bearing for the pilot.
- Surfaces to vary across Help modalities (SPEC §13.2): pizza slices, glasses of juice, chocolate bars,
  garden beds, walking distance, ribbon lengths. Transfer seeds above deliberately use a wider surface
  set than a single Help re-explanation would.
- Common misconceptions to flag in Help:
  - "Any cut piece is a fraction" — see `equal_vs_unequal_parts`.
  - "Bigger denominator = bigger fraction" — see `comparing_equal_denom`.
  - "Add top AND bottom" (1/4 + 1/4 = 2/8) — see `adding_equal_denom`. This is the most common pilot bug to plan a transfer probe around.

## Out of scope

- **Different denominators** (e.g. 1/2 + 1/3) — Phase 1 or follow-up template.
- **Mixed numbers and improper fractions** — Phase 1.
- **Decimal / fraction conversion** — separate template.
- **Multiplying / dividing fractions** — Year 5+ templates.

If a learner asks a question that lands in the out-of-scope list, the dialogue framework
should defer ("That's something you'll meet a bit later — let's stay with these for now")
rather than attempt to teach it. See SPEC §15 (defer when uncertain) and §16.2 (stay in scope).

---

*Pilot template — version 0.1. Authored per [PHASE0.md](../../../docs/PHASE0.md) W3.2 and tested by [TESTS.md](../../../docs/TESTS.md) T3.1, T3.2.*
