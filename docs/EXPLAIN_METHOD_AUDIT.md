---
type: Mentar Status Doc
title: "Mentar — Explain-Method Audit (2026-07-25)"
description: Node-by-node audit of what "explain" actually produces for every curriculum concept — subject, category, and explain-output type (deterministic ASCII step-grid vs. LLM prose, with or without a visual-scaffold hint). Built by reading source directly (generator return statements, visual_scaffold.py matching logic), not by trusting prior session claims.
tags: [audit, explain, curriculum, visual-scaffold, arithmetic-steps]
timestamp: "2026-07-25T00:00:00Z"
---

# Explain-Method Audit — 2026-07-25

> ✅ **RE-AUDITED IN FULL 2026-08-11 — this document now covers all 319 nodes.**
> The original 2026-07-25 pass covered 76 nodes (the whole curriculum at the time); the
> curriculum has since grown to **319 nodes across 71 templates**. The re-run used the same
> method — sample real items from the real generator, push each through the real extractor
> and the real scaffold matcher, infer nothing from reading regexes — and is summarised in
> **§ Full re-audit (2026-08-11)** at the end. The per-node tables below are the ORIGINAL
> 76-node pass, kept as the historical record; where the two disagree, the re-audit wins.

**Why this exists.** The maintainer flagged that division's "show human working" output was wrong despite an earlier session reporting it as shipped/correct, and asked for a from-scratch audit of every curriculum concept's explain path — not a repeat of a prior "it's done" claim. This document was built by reading `arithmetic_steps.py`'s regexes, every generator's actual return statement, `visual_scaffold.py`'s matching logic, and every curriculum template's node list directly — not from memory of earlier sessions.

## How "explain" actually works (two layers)

1. **Initial Help** (5 modalities: visual / concrete / analogy / story / formal) — chosen when a child presses "Help". **Always LLM prose.** Only the `visual` modality (`prompts/help_visual.md`) injects a `{{visual_scaffold}}` hint; the other 4 modalities get no visual aid at all.
2. **"Explain more" (`HELP_ELABORATE`)** — a deeper follow-up. The controller tries a **deterministic ASCII step-grid** first (`engine/arithmetic_steps.py`, via `_build_steps_grid_if_eligible()`); if the node's problem text doesn't match one of the 4 arithmetic regexes, it falls back to LLM prose (`prompts/help_elaborate.md`, which also injects `{{visual_scaffold}}` if the node's label matches a scaffold file).

**This audit's "Explain type" column describes the `HELP_ELABORATE` outcome** (the deeper, most-informative explain path) since that's what "show human working" refers to. The initial Help's `visual` modality gets the same scaffold hint (or none) as shown here; the other 4 modalities are LLM prose regardless of this table.

## Eligibility rules (ground truth, read from source)

- **ASCII step-grid**: the node's *generated* problem text (not the template's static `transfer_seeds` — those aren't what's shown at runtime) must match one of `extract_addition_operands` / `extract_subtraction_operands` / `extract_multiplication_operands` / `extract_division_operands` in `engine/arithmetic_steps.py` — i.e. the literal shape `"What is {number} {op} {number}?"` with **plain non-negative integers or decimals**, never a fraction (`a/b`), a word problem, or a multi-term expression. Subtraction additionally requires a non-negative result; multiplication/addition require non-negative operands.
- **LLM prose + visual scaffold**: the node's **label** contains (case-insensitive substring) one of a scaffold file's `topic_keywords`, scanned alphabetically by filename, **first match wins** — this ordering is a real source of mismatches (see Findings).
- **LLM prose only**: neither of the above.

---

## Full node-by-node table

### Mathematics

| Template | Node | Category | Answer type | Explain type | Note |
|---|---|---|---|---|---|
| AU_ACARA/year2_maths | au2_place_value | Place value | mc4 | LLM prose + scaffold (**decimals** ⚠️) | Whole-number place value routed to the DECIMAL scaffold — see Finding 1 |
| AU_ACARA/year2_maths | au2_addition | Addition | int | **ASCII step-grid** | Reliable (bounds guarantee non-negative) |
| AU_ACARA/year2_maths | au2_subtraction | Subtraction | int | **ASCII step-grid** | Reliable |
| AU_ACARA/year2_maths | au2_mult_facts_2_5_10 | Multiplication | int | **ASCII step-grid** | Reliable |
| AU_ACARA/year2_maths | au2_halves_quarters | Fractions | fraction | LLM prose + scaffold (fractions) | Correct |
| AU_ACARA/year3_maths | au3_place_value | Place value | mc4 | LLM prose + scaffold (**decimals** ⚠️) | Same as au2 — Finding 1 |
| AU_ACARA/year3_maths | au3_addition | Addition | int | **ASCII step-grid** | Reliable |
| AU_ACARA/year3_maths | au3_subtraction | Subtraction | int | **ASCII step-grid** | Reliable |
| AU_ACARA/year3_maths | au3_mult_facts | Multiplication | int | **ASCII step-grid** | Reliable |
| AU_ACARA/year3_maths | au3_unit_fractions | Fractions | fraction | LLM prose + scaffold (fractions) | Correct |
| AU_ACARA/year3_maths | au3_fraction_of_whole | Fractions | fraction | LLM prose + scaffold (fractions) | Correct |
| AU_ACARA/year4_maths | au4_place_value | Place value | mc4 | LLM prose + scaffold (**decimals** ⚠️) | Same as au2/au3 — Finding 1 |
| AU_ACARA/year4_maths | au4_mult_facts | Multiplication | int | **ASCII step-grid** | Reliable |
| AU_ACARA/year4_maths | au4_division_facts | Division | int | **ASCII step-grid** | Reliable, exact by construction |
| AU_ACARA/year4_maths | au4_sharing_division | Division (word problem) | int | LLM prose + scaffold (division_word_problems) | Correct — word-problem phrasing never matches the regex, by design |
| AU_ACARA/year4_maths | au4_equivalent_fractions | Fractions | fraction | LLM prose + scaffold (fractions) | Correct |
| AU_ACARA/year4_maths | au4_adding_fractions | Fractions | fraction | LLM prose + scaffold (**addition_subtraction** ⚠️) | Should be "fractions" — see Finding 2 |
| AU_ACARA/year5_maths | au5_decimal_place_value | Decimal place value | mc4 | LLM prose + scaffold (decimals) | Correct (this one genuinely is decimal) |
| AU_ACARA/year5_maths | au5_add_sub_decimals | Add/sub decimals | decimal | **ASCII step-grid** | Reliable, exact by construction |
| AU_ACARA/year5_maths | au5_mult_fraction_whole | Fractions | fraction | LLM prose + scaffold (fractions) | Correct |
| AU_ACARA/year5_maths | au5_percentage_of_quantity | Percentages | int | LLM prose + scaffold (percentages) | Correct |
| AU_ACARA/year5_maths | au5_negative_numbers | Negative numbers | int | LLM prose + scaffold (negative_numbers) | Correct (word-problem phrasing, never regex-eligible) |
| AU_ACARA/year5_maths | au5_division_remainder_as_fraction | Division (remainder) | fraction | **ASCII step-grid** (`ending="fraction"`) | New 2026-07-24; reliable |
| AU_ACARA/year5_maths | au5_division_remainder_as_decimal | Division (remainder) | decimal | **ASCII step-grid** (`ending="decimal"`) | New 2026-07-24; reliable, divisor restricted to terminate |
| AU_ACARA/year6_maths | au6_order_of_operations | Order of operations | int | LLM prose + scaffold (order_of_operations) | Correct — multi-term expressions never match the 2-operand regex |
| AU_ACARA/year6_maths | au6_mult_decimals | Multiplication | decimal | **ASCII step-grid (13% of draws ⚠️)** | See Finding 5 — decimal × decimal/whole rarely passes the integer-only extraction gate |
| AU_ACARA/year6_maths | au6_div_decimals | Division | decimal | **ASCII step-grid** | Reliable, exact by construction |
| AU_ACARA/year6_maths | au6_area_perimeter | Area/perimeter | int | LLM prose + scaffold (area_perimeter) | Correct |
| AU_ACARA/year6_maths | au6_fraction_decimal_equiv | Fraction↔decimal | decimal | LLM prose + scaffold (decimals) | Debatable — see Finding 4 |
| AU_ACARA/year7_maths | au7_integers_add_sub | Add/sub integers | int | **ASCII step-grid (21% of draws ⚠️)** | Only when BOTH random operands land non-negative — see Finding 3 |
| AU_ACARA/year7_maths | au7_order_of_ops_negatives | Order of operations | int | LLM prose + scaffold (negative_numbers) | Correct |
| AU_ACARA/year7_maths | au7_unlike_denom_fractions | Fractions | fraction | LLM prose + scaffold (**addition_subtraction** ⚠️) | Should be "fractions" — Finding 2 |
| AU_ACARA/year7_maths | au7_one_step_equations | Algebra | int | LLM prose + scaffold (algebra_equations) | Correct |
| AU_ACARA/year7_maths | au7_mult_decimal_by_decimal | Multiplication | decimal | **ASCII step-grid (1% of draws ⚠️)** | See Finding 5 — effectively always LLM prose in practice |
| AU_ACARA/year8_maths | au8_two_step_equations | Algebra | int | LLM prose + scaffold (algebra_equations) | Correct |
| AU_ACARA/year8_maths | au8_squares | Squares | int | LLM prose + scaffold (squares_roots) | Correct |
| AU_ACARA/year8_maths | au8_negative_multiplication | Multiplication | int | **ASCII step-grid (23% of draws ⚠️)** | Only when BOTH random operands land non-negative — Finding 3 |
| AU_ACARA/year8_maths | au8_percentage_change | Percentages | int | LLM prose + scaffold (percentages) | Correct |
| AU_ACARA/year8_maths | au8_div_decimal_by_decimal | Division | decimal | **ASCII step-grid** | Reliable, exact by construction |
| IN_GENERIC/class3_maths | in_generic_addition | Addition | int | **ASCII step-grid** | Reliable |
| IN_GENERIC/class3_maths | in_generic_subtraction | Subtraction | int | **ASCII step-grid** | Reliable |
| IN_GENERIC/class3_maths | in_generic_times_tables | Multiplication | int | **ASCII step-grid** | Reliable |
| IN_GENERIC/class3_maths | in_generic_unit_fractions | Fractions | fraction | LLM prose + scaffold (fractions) | Correct |
| _pilot/arithmetic | addition | Addition | int | **ASCII step-grid** | Reliable |
| _pilot/arithmetic | subtraction | Subtraction | int | **ASCII step-grid** | Reliable |
| _pilot/arithmetic | multiplication | Multiplication | int | **ASCII step-grid** | Reliable |
| _pilot/fractions | whole_number_division | Division (word problem) | int | LLM prose + scaffold (division_word_problems) | Correct |
| _pilot/fractions | fraction_as_part_of_whole | Fractions | mc4 | LLM prose + scaffold (fractions) | Correct |
| _pilot/fractions | equal_vs_unequal_parts | Fractions | mc4 | LLM prose + scaffold (fractions) | Correct |
| _pilot/fractions | unit_fractions | Fractions | fraction | LLM prose + scaffold (fractions) | Correct |
| _pilot/fractions | equivalent_fractions | Fractions | fraction | LLM prose + scaffold (fractions) | Correct |
| _pilot/fractions | comparing_equal_denom | Fractions | mc4 | LLM prose + scaffold (fractions) | Correct |
| _pilot/fractions | adding_equal_denom | Fractions | fraction | LLM prose + scaffold (**addition_subtraction** ⚠️) | Should be "fractions" — Finding 2 |
| _pilot/fractions | subtracting_equal_denom | Fractions | fraction | LLM prose + scaffold (**addition_subtraction** ⚠️) | Should be "fractions" — Finding 2 |
| practice/maths | practice_times_tables | Multiplication | int | **ASCII step-grid** | Reliable |
| practice/maths | practice_skip_counting | Number patterns | int | LLM prose + scaffold (number_patterns) | Correct |
| practice/maths | practice_doubles_halves | Number patterns | int | LLM prose + scaffold (number_patterns) | Correct |

### English (all `mc4` — never step-grid eligible; the extraction regexes only match plain 2-operand arithmetic)

| Template | Node | Category | Explain type | Note |
|---|---|---|---|---|
| AU_ACARA/year2_english | aue2_word_classes | Parts of speech | LLM prose + scaffold (parts_of_speech) | Correct |
| AU_ACARA/year2_english | aue2_synonyms | Vocabulary | LLM prose + scaffold (vocabulary) | Correct |
| AU_ACARA/year2_english | aue2_plurals | Word forms | LLM prose + scaffold (word_forms) | Correct |
| AU_ACARA/year2_english | aue2_rhyming | Word forms | LLM prose + scaffold (word_forms) | Correct |
| AU_ACARA/year5_english | aue5_synonyms_advanced | Vocabulary | LLM prose + scaffold (vocabulary) | Correct |
| AU_ACARA/year5_english | aue5_antonyms_advanced | Vocabulary | LLM prose + scaffold (vocabulary) | Correct |
| AU_ACARA/year5_english | aue5_word_classes_advanced | Grammar | LLM prose + scaffold (grammar) | Correct |
| AU_ACARA/year5_english | aue5_compound_words | Word forms | LLM prose + scaffold (word_forms) | Correct |
| AU_ACARA/year6_english | aue6_figurative_language | Figurative language | LLM prose + scaffold (figurative_language) | Correct |
| AU_ACARA/year6_english | aue6_synonyms_nuanced | Vocabulary | LLM prose + scaffold (vocabulary) | Correct |
| AU_ACARA/year6_english | aue6_antonyms_nuanced | Vocabulary | LLM prose + scaffold (vocabulary) | Correct |
| AU_ACARA/year6_english | aue6_word_classes_conjunctions_prepositions | Grammar | LLM prose + scaffold (grammar) | Correct |
| practice/english | practice_synonyms_antonyms | Vocabulary | LLM prose + scaffold (vocabulary) | Correct |
| practice/english | practice_rhyming_words | Word forms | LLM prose + scaffold (word_forms) | Correct |
| practice/english | practice_odd_one_out | Classification | LLM prose + scaffold (odd_one_out) | Correct |
| practice/english | practice_plural_forms | Word forms | LLM prose + scaffold (word_forms) | Correct |

### Science (all `mc4` — never step-grid eligible)

| Template | Node | Category | Explain type | Note |
|---|---|---|---|---|
| _pilot/science | living_nonliving | Life science | LLM prose + scaffold (living_nonliving) | Correct |
| _pilot/science | classify_animals | Life science | LLM prose + scaffold (living_nonliving) | Correct |
| _pilot/science | states_of_matter | Physical science | LLM prose + scaffold (states_of_matter) | Correct |

**Totals:** 76 concept nodes audited (57 maths — AU_ACARA Y2–8 + IN_GENERIC + `_pilot` + `practice` combined, 16 english, 3 science), every eligibility number verified by running the real generator through the real extractor 200 times, not by reading regex text alone:
- **20 maths nodes: reliably (100%) ASCII step-grid-eligible.**
- **4 maths nodes: conditionally eligible** — `au7_integers_add_sub` (21%), `au8_negative_multiplication` (23%), `au6_mult_decimals` (13%), `au7_mult_decimal_by_decimal` (1%). In practice these read as "mostly LLM prose."
- **33 maths nodes: LLM prose, of which 4 have a real scaffold-routing bug** (Findings 1–2).
- **All 19 English/science nodes: LLM-prose-with-scaffold, correctly, by design** (mc4 questions never match the arithmetic regexes).

*(An earlier draft of this total miscounted maths at 39 by only tallying the AU_ACARA rows and forgetting IN_GENERIC + `_pilot` + `practice` — caught by recounting the table directly rather than trusting the prose summary. Corrected here.)*

---

## Findings — real issues, not just documentation

### Finding 1 — Whole-number place value wrongly routed to the decimals scaffold
`au2_place_value`, `au3_place_value`, `au4_place_value` (Years 2–4, **whole-number** place value: tens/hundreds/thousands) all match `visual_scaffolds/maths/decimals.md` because `"place value"` is literally one of that file's `topic_keywords` — but `decimals.md`'s actual content is a tenths/hundredths place-value chart, wrong for a whole-number concept. **No dedicated whole-number place-value scaffold file exists.** Only `au5_decimal_place_value` (genuinely about tenths) should match this file.
**Fix options:** (a) add a new `place_value.md` scaffold and make `decimals.md`'s keyword more specific (e.g. drop bare `"place value"`, keep `"decimal place value"`), or (b) narrow `decimals.md`'s `topic_keywords` to require "decimal" co-occurring. Not fixed in this pass — audit only, per the maintainer's request.

### Finding 2 — "Adding/Subtracting fractions..." nodes routed to the wrong scaffold
`au4_adding_fractions`, `au7_unlike_denom_fractions`, and pilot's `adding_equal_denom`/`subtracting_equal_denom` all have labels starting with "Adding"/"Subtracting" — which matches `addition_subtraction.md`'s keywords (`"adding"`, `"subtracting"`) **before** `fractions.md` ever gets checked, because `visual_scaffold.py` scans scaffold files **alphabetically by filename** and returns the **first** match (`addition_subtraction.md` sorts before `fractions.md`). A child on a fractions node gets a number-line addition hint instead of a fraction bar-model hint. **Root cause: keyword collision + alphabetical-first-match has no tie-break for "which scaffold is more specific to this subject area."** Not fixed in this pass.

### Finding 3 — Two integer/negative-number nodes have inconsistent (draw-dependent) step-grid eligibility
`au7_integers_add_sub` (`gen_integers_add_sub`, operands `randint(-15, 15)`) and `au8_negative_multiplication` (`gen_negative_multiplication`, operands randomly signed) can each produce a **negative operand**, which `extract_subtraction_operands`/`extract_multiplication_operands` correctly reject (by design — negative-operand arithmetic is number-line reasoning, not column carries). **Verified empirically** (200 real draws through the real generator + real extractor): `au7_integers_add_sub` is step-grid-eligible only **21%** of the time; `au8_negative_multiplication` only **23%**. The result: the **same concept node** shows the ASCII step-grid on some draws and LLM prose on others, purely by chance. Not a bug (the exclusion itself is correct and intentional), but a real inconsistency a child could notice. Logged, not fixed — would need either a distinct step-grid method for signed numbers, or accepting the inconsistency as out of scope for the current arithmetic_steps.py design (which explicitly limits itself to the early-years unsigned method).

### Finding 4 — `au6_fraction_decimal_equiv` scaffold choice is debatable
Routes to `decimals.md` (tenths/hundredths chart) via the `"decimal"` keyword. This is defensible (the node does involve decimals) but arguably a "fraction-decimal-equivalence" node would benefit more from a scaffold showing BOTH representations side by side — no such scaffold exists today. Lower priority than Findings 1–2 since the current match isn't actively wrong, just not ideal.

### Finding 5 — Decimal multiplication is almost NEVER step-grid-eligible, despite looking like a clean case on paper
`extract_multiplication_operands` deliberately scopes multiplication to **integer operands only** (per its own docstring — decimal multiplication needs its own place-value handling, deferred). This is documented in the code, but its PRACTICAL effect on two live curriculum nodes was not previously measured: **verified empirically** (200 real draws each):
- `au6_mult_decimals` (`gen_mult_decimals`, one-decimal-place × whole number): step-grid-eligible only when the decimal operand's random tenths value happens to be a multiple of 10 (e.g. "20" → "2.0", a whole number in disguise) — **13% of draws**.
- `au7_mult_decimal_by_decimal` (`gen_mult_decimal_by_decimal`, decimal × decimal): needs BOTH random decimal operands to independently land on whole values — **1% of draws**.

In practice, these two nodes are **effectively always LLM prose**, not the ASCII step-grid the template/generator naming would suggest. This was NOT caught by manual regex tracing (the text shape "What is {a} × {b}?" looks identical to the always-eligible integer multiplication cases) — only caught by actually running the generator + extractor together over many draws. **Lesson for future audits of this kind: eligibility claims for a generator with non-integer output must be verified by running real draws, not by reading the regex/text shape alone.**

### Confirmed correct (not a finding, stated for completeness)
- All word-problem-phrased division/sharing nodes (`au4_sharing_division`, pilot's `whole_number_division`) correctly fall to `division_word_problems.md` — word-problem text never matches the 2-operand regex, by design.
- All fraction-slash-operand nodes (`a/d + b/d` style) correctly never match the arithmetic step-grid — `_NUM` doesn't include `/`, so `extract_addition_operands` returns `None` for them even though the text superficially contains "What is ... + ...?".
- Multi-term expressions (`au6_order_of_operations`, `au7_order_of_ops_negatives`) correctly never match — the regex requires `?` immediately after the second operand, so a 3+-term expression like `"3 + 4 × 2?"` fails the addition regex (there's more text between the second operand and `?`).
- All English/science nodes are `mc4` and structurally cannot match any arithmetic regex (different question shape entirely) — routing to LLM-prose-with-scaffold is correct by design for every one of them.

## What this audit did NOT check
- Whether the LLM actually **draws a legible ASCII diagram** when a visual scaffold hint is injected (that depends on the model's own instruction-following — no automated check exists for this).
- The **initial Help modalities** (concrete/analogy/story/formal) — these are always LLM prose with no visual aid at all, unaffected by any finding here.
- Whether `docs/design/comprehensive_math_templates_reference.md` / `year1_12_*_templates_reference.md` (the maintainer's earlier logged-only template dumps for Y1-12 maths/English/science) have been built — **they have not**; those remain reference material only, unrelated to what's actually shipped and audited above.


---

## Full re-audit (2026-08-11) — all 319 nodes

> **Re-running this is now one command:** `python3 -m mentar.tools.audit_explain_paths`
> (promoted from a scratchpad script 2026-08-12, after it found real bugs twice). It reports;
> judging the output stays a human job. `tests/tools/test_audit_explain_paths.py` additionally
> locks the invariants worth gating: every node produces an item and resolves a scaffold, and
> the draw-dependent set does not grow.

Re-run because the curriculum grew 4x after the original pass and none of the new content
had ever been through it. Method identical to the original: **200 real draws per node**
through the real `ItemGenerator` (item bank loaded exactly as `web/app.py` does), each
problem pushed through the real `extract_*_operands` chain in the controller's own
add→sub→mult→div order, and each label through the real `load_visual_scaffold`.

### Coverage

| | Count |
|---|---|
| Nodes audited | **319** (was 76) |
| Templates | 71 |
| By subject | maths 183 · English 112 · science 24 |
| Get a visual scaffold | **319 / 319** |
| ASCII step-grid on *every* draw | 56 |
| LLM prose on every draw | 247 |
| **Draw-dependent (inconsistent)** | **16** |

English (112) and science (24) are 100% prose by construction — they are all `mc4`, and the
extraction regexes only match plain two-operand arithmetic. That is correct behaviour, not a
gap.

### Finding 6 — order-of-operations nodes were shown a thermometer, not a priority ladder ✅ FIXED

`au7_order_of_ops_negatives` and its three generic-pack twins generate
`"What is -13 + 6 × 6?"`. The skill under test is **precedence**. All four routed to
`negative_numbers.md`, whose three visual structures are a vertical thermometer, a horizontal
number line, and real-world anchors — precedence appeared only as a single guideline line.
`order_of_operations.md`, with its priority ladder / worked annotation / brackets-contrast
structures, is the right target and was losing 2–3.

The cause was deliberate, not accidental: `negative_numbers.md` had explicitly claimed the
keyword `order of operations with negative` — a keyword it could not back with a matching
visual structure. Same class as Findings 1+2 and the four routing bugs fixed during the
2026-08 breadth waves: **a scaffold claiming a topic its body does not actually teach.**

**Fixing it needed both sides, which a simulation caught before any edit.** Dropping the
keyword from `negative_numbers.md` alone leaves a 2–2 tie, and the tie-break is alphabetical
— `negative_numbers` < `order_of_operations` — so the wrong file would still have won. Adding
the keyword to `order_of_operations.md` alone produces a 3–3 tie with the same outcome. Only
doing both flips it (3–2). `order_of_operations.md` also gained a worked
`-13 + 6 × 6` example so it genuinely serves the nodes now routed to it, rather than
repeating the claim-without-content mistake being fixed. Locked by
`tests/engine/test_scaffold_coverage.py`, including a case asserting the plain negatives
nodes were *not* dragged along.

Verified by re-running the full audit: exactly **4 routing changes, 0 collateral changes**
across the other 315 nodes, and 0 step-grid changes.

### Finding 3+5 — draw-dependent eligibility: 4 → 16 → **4** ✅ mostly resolved 2026-08-12

The original found 4 nodes whose step-grid eligibility depends on the random draw. There are
now **16**, because the SG/US/IN generic packs reuse the same generators — one root cause,
replicated four times:

| Eligibility | Nodes |
|---|---|
| 1.5% | `*_mult_decimal_by_decimal` × 4 |
| 11.0% | `*_mult_decimals` × 4 |
| 20.5% | `*_integers_add_sub` × 4 |
| 25.5% | `*_negative_multiplication` × 4 |

A child on the same concept gets a step grid on one draw and prose on the next, purely by
chance. **This materially raises the priority of
`docs/design/step_grid_signed_and_decimal_mult_design.md`**, which was written when this was
a 4-node problem: Phase A (decimal multiplication) and Phase B (signed multiplication) are
both single fixes in `arithmetic_steps.py` that would resolve **8 nodes each**, not two.
Phase C remains gated on maintainer worked examples.

**Resolved 2026-08-12:** Phases A and B shipped, taking this from 16 nodes to **4**
(always-step-grid rose 56 → 68). The remaining 4 are the `*_integers_add_sub` family,
which is Phase C and still gated. Re-measured by re-running this audit, not asserted.

### Checked and clean

- **Every node resolves a scaffold** (319/319) and every one produces an item on every draw
  (0 failures in 63,800 draws).
- **Scaffold distribution is sane** — no single file is over-matching; the science scaffolds
  are 1:1 with their nodes, and the large maths/English buckets are the generic packs
  legitimately repeating the same concepts across countries.
- **Finding 4** (`fraction_decimal_equiv` → `decimals.md`, "debatable, not wrong") is
  unchanged and still judged not worth a dual-representation scaffold.

### Known gap, recorded not fixed

`division_word_problems.md` is titled *Division and Sharing Word Problems*, but also receives
plain-arithmetic nodes (`Division facts`, `Whole-number division`) whose generated text is a
bare `What is 24 ÷ 6?`. It is the only division scaffold, so this is "best available" rather
than wrong, and those nodes are 100% step-grid-eligible so Explain-more shows the real long
division anyway — only the Help→visual modality sees the mismatch. Splitting out a plain
division-algorithm scaffold is a content decision, not a bug fix.
