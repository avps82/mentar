---
type: Mentar Design Doc
title: Explain-mode design — a method explanation for every concept type
description: Design for computed, LLM-free method explanations across all five concept types, so Explain-more never falls back to a bare answer.
---

# Explain-mode design — a proper method explanation for every concept type

**Status: PLAN ONLY (2026-08-12). Nothing in here is built.**
Maintainer-requested after the live report logged in `PHASE0_STATUS.md`'s backlog
("worked-example gap"): *"explain more doesn't really work. Needs more on how to solve this
properly.. There is huge gaps. We need to see if a type of math or english as a proper explain
mode for every part.. this is common for all countries."*

---

## 1. The problem, precisely

> **STATUS 2026-08-15 — this problem is largely solved; the diagnosis below is kept as the
> original statement of it.** Phases 0/1/3/3a shipped, and English cards followed on
> 2026-08-15. Measured with `tools/audit_explain_paths.py` over the corpus as of 2026-08-15 (561 nodes,
> 142 templates as of 2026-08-15): **72 always show a step grid, 423 always show a computed method card, 66 are
> still LLM prose only** — and those 66 are the quadratic-algebra generators deferred on
> 2026-08-13, replicated across the senior packs. The numbers in the diagnosis below are the
> corpus as it stood when this design was written, not today's.

**0 of 319 curriculum nodes have an authored `worked_example`.** When a child presses Help or
"Explain more" on any node outside the four step-grid arithmetic shapes, the prompt's
worked-example slot is filled by `controller.py::_worked_example_for`'s fallback: a random
solved sibling item formatted as `"{problem} (Answer: {answer})"`. The LLM is told to "build
on" it — but a bare question-and-answer contains no method, so the child gets:

> *"Here's a similar question and its answer to compare with: What is 50% of 64? (Answer: 32).
> Look at how the answer comes from the numbers, then try yours the same way."*

That is the live failure the maintainer screenshotted. "Look at how the answer comes from the
numbers" is asking an 8-year-old to reverse-engineer the method the tutor was supposed to teach.

The step-grid system (`engine/arithmetic_steps.py`) already solves this completely — but only
for column addition/subtraction/multiplication/division and their decimal/signed variants.
Everything else falls through: **percentages, fractions-of, equations, place value, order of
operations, area/perimeter, and ALL of English and science.**

### Inventory (scanned 2026-08-12, all 6 authority packs)

| Subject | Nodes | Answer types |
|---|---|---|
| mathematics | 183 | int 87 · fraction 35 · decimal 28 · expression 15 · mc4 18 |
| english | 112 | mc4 112 |
| science | 24 | mc4 24 |

~77 distinct generator functions produce every item. **Generators are shared across country
packs** (IN_GENERIC/SG_GENERIC/US_GENERIC reuse the same functions AU uses) — so an explainer
written per GENERATOR automatically covers every country. That is the maintainer's "this is
common for all countries" requirement, satisfied by construction rather than by translation.

---

## 2. The architectural principle (unchanged, extended)

Same posture as the step grids and every item generator: **the method explanation is computed,
never composed.** An LLM asked to "show the steps" is exactly the failure class A14
(`engine/explain_check.py`) exists to catch. The LLM's job stays warmth and re-phrasing; the
method itself must come from code that provably knows the answer.

**The key design fact this plan turns on:** every generator already holds, at draw time, the
exact parameters that make the answer right — `gen_percentage_of_quantity` draws `pct=50,
quantity=64` before it formats the question string. Today those parameters are discarded the
moment the `(answer_type, checker, problem, answer)` tuple is returned. The step-grid system
had to *re-parse* them out of the problem text with regexes (its extractors) because it was
retrofitted onto existing items. New explain-mode work should not repeat that: **the generator
attaches its explanation at draw time**, when the parameters are simply in scope. No parsing,
no ambiguity, no per-country phrasing drift to chase.

---

## 3. The explain-mode taxonomy

This is the heart of the maintainer's ask: different concept types need different SHAPES of
explanation, and what "explaining" even means is a genuinely THREE-way split (maintainer
correction 2026-08-12 — not maths-with-science-alongside vs English):

- **Maths** has a *derivation*: a rule chain any child can re-run to reach the answer.
- **English** has a *rule applied to an instance*: nothing to compute, but a reason the right
  option fits and each wrong one doesn't.
- **Science** (at this year band) has *neither*: recall of a curated fact, so the honest
  explanation is the fact's category context — trying to fake a "method" for "which of these
  is metal?" would be teaching a derivation that doesn't exist.

### Type 1 — Algorithmic column methods *(SHIPPED — the step grids)*

The school algorithm has a visual/positional layout: column addition with carries, long
division. Already covered by `arithmetic_steps.py` for +, −, ×, ÷ including decimal and signed
variants. Nothing to do here; this row exists so the taxonomy is complete.

### Type 2 — Procedural numeric: the "method card" *(maths — the big win)*

Most maths nodes are not column algorithms but short fixed **rule chains**. A percentage-of,
a fraction-of, a one-step equation — each has a 2–5 step method a child is taught, and every
step is computable from the draw parameters:

```
What is 50% of 64?
  1. "50%" means 50 out of every 100 — as a fraction that is 50/100 = 1/2.
  2. "of" means multiply: 1/2 × 64.
  3. Half of 64 is 64 ÷ 2 = 32.
  Answer: 32
```

Every line above is an f-string over `(pct, quantity)` plus arithmetic the generator already
did. Different `pct` values pick different wordings (10% → "divide by 10"; 25% → "a quarter —
divide by 4"; 75% → "three quarters — a quarter times 3") — a small dict of per-parameter
phrasings, exactly like the fact tables science items already use.

Real generator families this covers (names from `engine/au_items.py` / `itemgen.py` /
`practice_items.py`):

| Family | Generators (examples) | Method card shape |
|---|---|---|
| Percentages | `gen_percentage_of_quantity`, `gen_percentage_change` | percent → fraction → multiply |
| Fraction arithmetic | `gen_unlike_denom_fractions`, `gen_mult_fraction_whole`, `gen_halves_quarters` | common denominator / of-means-multiply chains |
| Place value | `gen_place_value_2digit/3digit/4digit`, `gen_decimal_place_value` | expand the number by columns, point at the asked digit |
| Equations | `gen_one_step_equations`, `gen_two_step_equations` | undo operations one at a time, show both sides |
| Order of operations | `gen_order_of_operations`, `gen_order_of_ops_negatives` | priority ladder, resolve one operation per step |
| Integers | `gen_integers_add_sub`, `gen_negative_numbers`, `gen_negative_multiplication` | sign rule stated, then the unsigned computation |
| Geometry-numeric | `gen_area_perimeter`, `gen_compound_shape_area`, `gen_combined_rectangles_perimeter` | formula stated → substitute → compute |
| Algebra expressions | `gen_word_to_expression`, `gen_combine_expressions`, `gen_distributive_word_to_expression`, quadratic variants | translate each phrase → combine like terms term-by-term |
| Conversions | `gen_fraction_decimal_equiv`, `gen_division_remainder_as_fraction`/`_decimal` | the equivalence rule, then the computation |

Rough coverage: **~130 of the 183 maths nodes** (int/fraction/decimal/expression answered);
the remaining maths mc4 nodes are Type 3/4 shaped.

**Two corrections found while building Phase 1, not caught when this table was first
written (2026-08-13):**

- **`gen_compound_shape_area`/`gen_combined_rectangles_perimeter` are Algebra expressions,
  not Geometry-numeric.** Their answer_type is `expression` (a simplified algebraic
  expression, e.g. `8*x + 12`), not a number — reading the actual generator bodies (not
  just their names) shows they belong with the Algebra family below, not Geometry.
  Geometry-numeric in practice is just `gen_area_perimeter` (Year 6, genuinely numeric).
- **`gen_division_remainder_as_fraction`/`_decimal` are ALREADY Type 1, not Type 2.** Their
  own docstrings say so — they exist specifically to feed `build_long_division_steps` on
  Explain-more (the "fraction"/"decimal" endings the division step-grid rebuild added).
  A method card on these generators would be dead code: the controller's preference ladder
  checks the step grid FIRST (§4b), so it would never be reached. Conversions in practice
  is just `gen_fraction_decimal_equiv` — genuinely uncovered, migrated in Phase 1.

### Type 3 — Rule application: rule + instance + why-the-others-are-wrong *(English)*

English is the second arm of the three-way split, and it IS different: there is no
derivation to show. But the generator still knows everything needed for a real explanation,
because mc4 items are drawn from **labelled word tables**:

- **the rule** — fixed per generator: "an adverb tells you HOW an action happens; it usually
  describes a verb";
- **the instance** — which word was drawn and its label: "in 'the thunder grumbled angrily',
  'angrily' tells you HOW it grumbled";
- **the distractor rationale** — the wrong options were drawn from OTHER labelled pools, so
  their true labels are known: "'thunder' is a noun (a thing), 'grumbled' is the verb itself".

```
Which word is the adverb? "The thunder grumbled angrily."
  Rule:    an adverb tells you HOW something happens — it describes the verb.
  Here:    the action is "grumbled". Which word tells you HOW it grumbled? → "angrily".
  Others:  "thunder" names a thing (noun) · "grumbled" is the action itself (verb).
```

All three parts are template text over data the generator already holds at draw time.
The distractor-rationale line is the piece the current system cannot produce at all, and for
mc4 it is most of what "explaining" means — a child who picked "grumbled" needs to hear why
that specific choice was wrong, not the rule restated.

Covers all **112 English nodes** (28 generators: word classes, synonyms/antonyms, homophones,
prefixes/suffixes, figurative language, active/passive, clauses, connotation, …). One nuance:
vocabulary generators (synonyms/antonyms) have per-WORD rationale, so their word tables gain a
one-line gloss per entry — a content-authoring cost, not a design problem (same shape as the
science fact tables).

### Type 4 — Fact in category: context around a recall item *(science + some English vocab)*

Science mc4 items are curated **fact-table lookups** ("Which of these is made of metal?").
There is no method and no rule — the honest explanation shape is the fact, its category
context, and the distractors' true categories, all already present in the fact table:

```
Which of these is made of metal? → a steel screw
  A steel screw is made of metal — metals feel cold, hard and shiny.
  The others: a rubber band is rubber (stretchy) · a glass jar is glass (see-through).
```

Covers the **24 science nodes** and the handful of English vocab generators whose tables
already carry category labels. Requires each fact table row to gain one "because" gloss —
again content authoring against an existing structure, reviewed once, deterministic forever.

**Science visuals — two tiers (RATIFIED 2026-08-12).** Words carry the concept, but for
phenomena like light scattering an image does what prose can't, and the maintainer asked for
a text-native answer:

- **Tier 1, now: authored ASCII/emoji scaffolds.** The pipeline already renders fenced blocks
  as monospace diagram boxes (A2 rendering contract) and `help_elaborate.md` already has a
  per-topic `{{visual_scaffold}}` slot — science concepts get an authored scaffold each, zero
  new infrastructure, ships with Phase 3.
- **Tier 2, the proper fix: authored SVG.** SVG **is text** — hand-authorable, diffable,
  PR-reviewable, versioned like any content, yet the browser renders a real, crisp image.
  No binary assets, no licensing, fully offline, and parametric where useful (a particle-
  spacing diagram for solid/liquid/gas can be generated by owned Python from the same fact
  table that generates the question). Sample the maintainer requested, to judge the look:
  `docs/design/samples/light_scattering.svg` (the "ALL the colours travelling together"
  concept). **SVG is ALWAYS authored or emitted by owned code — never LLM-generated at
  runtime.** The maintainer's read is correct and it is also the architectural one: small
  local models are hit-or-miss at SVG, and a runtime-generated image is an unreviewable one.
  ASCII scaffolds may reasonably come from LLM knowledge at AUTHORING time (then reviewed and
  frozen); SVG is authored, full stop.

**Two rules learned from the sample's first render (maintainer review, 2026-08-12):**

1. **Name the concept with its textbook term.** The diagram (and its method card) must SAY
   "this is called Rayleigh scattering" — not just describe the phenomenon. A child who
   learns the idea without the name can't find it again in a book, a class, or a search; the
   name is what connects Mentar's explanation to everything else they'll ever read.
   Applies to every Type 4 card and diagram, and to Type 2/3 where a method has a standard
   name ("the distributive law", "a simile").
2. **An SVG is verified by RENDERING it, never by reading its source.** The sample's first
   cut passed source-level review and rendered with two defects the maintainer's screenshot
   caught immediately: a rotated label colliding with another label, and grossly oversized
   arrowheads (SVG markers scale with stroke-width by default — fixed with
   `markerUnits="userSpaceOnUse"`). Both invisible in the markup, both obvious at a glance in
   the render. So the authoring loop is author → **rasterize and look** → correct → freeze; a
   diagram nobody has SEEN is not done. The maintainer's phrasing is the rule: "You need to
   observe/render the image to see the correctness of it." (Practical note: the agent sandbox
   currently has no rasterizer — rsvg/inkscape/cairo absent, installs blocked — so
   render-verification happens in the maintainer's browser or on the dev host; if SVG
   authoring scales up, adding `rsvg-convert` to the dev environment makes the loop
   self-serve.)

**Round 3 (same day) sharpened the rule into a two-layer discipline.** The corrected sample
shipped with `--` inside an XML comment — illegal in XML, so the browser stopped parsing the
file entirely ("Double hyphen within comment"); the maintainer's render caught it again. The
lesson splits verification into what belongs where:

- **Machine layer (CI, now built):** well-formedness is checkable without eyes —
  `tests/tools/test_svg_wellformed.py` XML-parses every repo SVG (which inherently rejects
  the double-hyphen class) and enforces self-containment (no scripts/external refs). An SVG
  that cannot parse must never reach a render review.
- **Eyes layer (render):** everything geometric — collisions, sizes, legibility — still
  needs the rasterize-and-look loop; no source-level check replaces it.

**Local-LLM authoring pipeline (maintainer-requested, spec written 2026-08-12):** the full
requirements prompt — a draft → lint → render → vision-review loop, every defect class from
all three rounds encoded as a machine check, plus the per-concept generation prompt and the
render-review checklist as embedded templates — lives in the infra repo at
`local-llm-infra/prompts/svg-pipeline-requirements.md`, ready to hand to the harness.

### Type 5 — Evidence pointing *(future: comprehension against a passage)*

Not shipped in any current node (no passage-comprehension generators exist yet), recorded so
the taxonomy doesn't silently exclude it: when comprehension items exist, the generator knows
WHICH sentence of the passage carries the answer, and the explanation is that quote plus one
linking line. Deterministic like everything above. No work now.

### The Maths vs English vs Science comparison, in one table

Three subjects, three distinct explanation shapes — science is NOT "maths but easier", and
English is NOT "science with words". Each column is its own case:

| | Maths (Types 1–2) | English (Type 3) | Science (Type 4) |
|---|---|---|---|
| What "explaining" means | show the derivation | state rule, apply to instance, dismiss distractors | give the fact its category context |
| What the child re-runs | the computation, step by step | the rule, on the next sentence they meet | nothing — recall anchored by context |
| Steps verifiable by arithmetic? | **yes — self-checking** | no — reviewed once at authoring | no — reviewed once at authoring |
| Source of truth | draw parameters + arithmetic | labelled word tables | curated fact table |
| New content needed | none (pure code) | one gloss per vocab row; rules per generator | one gloss per fact row |
| Risk if wrong | wrong maths taught — caught by self-check | wrong rationale — caught at table review | wrong fact — caught at table review |

(Science stops being pure recall at higher year bands — a Y7 "balance this equation" node
WOULD have a derivation and would belong in Type 2. The taxonomy is per concept type, not per
subject label; today's 24 science nodes all happen to be Type 4.)

---

## 4. Delivery mechanism

### 4a. Carry the explanation on the Item

`engine/itembank.py::Item` gains one optional field:

```python
method_steps: tuple[str, ...] | None = None   # computed method card, one line per step
```

Generators fill it at draw time (opt-in — an unmigrated generator returns items exactly as
today). The existing 4-tuple return convention stays; migrated generators return a 5th element
or the item-source layer attaches it, whichever proves cleaner at implementation time.

### 4b. Controller wiring (the preference ladder)

In `_do_help_explain` / `_worked_example_for`, the worked-example slot's source becomes:

1. **step grid** (Type 1) — unchanged, still skips the LLM entirely on Explain-more;
2. **`item.method_steps`** — rendered directly (Help) or given to `help_elaborate.md` as the
   worked example (so the LLM elaborates ON a real method instead of a bare answer);
3. node-authored `worked_example` — still wins if a template author writes one;
4. today's sibling-item fallback — becomes the last resort instead of the only behaviour.

**RATIFIED 2026-08-12 — LLM-narrated, card-constrained, bare card as the fallback.** The
maintainer prefers natural prose over raw computed output, and the architecture supports that
without giving up the correctness guarantee. The card is not (usually) what the child sees —
it is what the LLM is HELD TO:

1. the generator computes `method_steps` (ground truth);
2. the LLM receives the card and narrates it warmly — this is what the child reads;
3. `explain_check` verifies the prose against the card (the same machinery that already
   verifies arithmetic claims, extended to "the narration must contain the card's steps and
   numbers, and contradict none of them");
4. on a verification failure, an empty/unavailable LLM, or a low-end-hardware timeout, the
   bare card renders directly (same `<pre class="steps-pre">` convention as the step grids).

The child always gets a correct method; they usually get it in a warm voice. For science
(Type 4) the fact-gloss + authored diagram act as the grounding that constrains the known
fabricated-reasoning failure mode.

### 4c. Rendering

Reuse the existing steps-pre block (`_arithmetic_steps.html` + `.steps-pre` CSS): method cards
are line-oriented plain text, exactly what that pipeline renders, and it already bypasses the
U-32 markdown-lite whitelist for computed (non-LLM) content. No new UI surface.

---

## 5. Verification — the harness IS the feature

Same discipline that caught six real bugs during the step-grid builds:

- **Type 2 (maths): self-validating by construction.** A pytest fixture draws N items per
  migrated generator and asserts the method card's final line contains `item.answer` verbatim
  (and, where the card shows intermediate values, recomputes them). A card that can't produce
  its own item's answer fails CI. This is the same "computed ground truth" loop
  `test_multiplication_self_validates_against_real_verifier` runs today.
- **Types 3–4 (English/science): reviewed data, guarded shape.** Glosses live in the same
  tables as the content they explain (one review surface, no drift); a pytest asserts every
  drawn mc4 item's card mentions the correct choice text and every distractor exactly once —
  shape-checking what can't be arithmetic-checked. The content-marker spot-check practice
  (established during the science waves, 4/6 waves caught something) applies at authoring.
- **audit tooling:** `tools/audit_explain_paths.py` gains a per-node "explain source" column
  (grid / method card / authored / bare-sibling-fallback) so coverage is measurable and the
  remaining gap is always visible instead of anecdotal.

---

## 6. Phasing

| Phase | Scope | Size | Depends on | Status |
|---|---|---|---|---|
| **0 — infrastructure + pilot** | `Item.method_steps`, controller preference ladder, rendering reuse, self-check harness, **one family: percentages** (the maintainer's own failing example becomes the acceptance test) | small (R13-ish) | nothing | ✅ **SHIPPED 2026-08-13** |
| **1 — maths method cards** | remaining Type 2 families, roughly in the §3 table's order (each family is one function + one test, independent of the others) | medium, embarrassingly parallel | 0 | 🟡 **in progress** — place value (4) + integers (3) + equations (2) + order of ops (2) + fraction arithmetic (3) + geometry-numeric (1) + conversions (1) + algebra expressions (6 of 13 — Y9/Y10 linear forms; Y11/Y12 quadratic-heavy generators + the 2 miscategorized area/perimeter-expression generators still open, lower volume + higher error-risk, deliberately deferred) shipped 2026-08-13 |
| **2 — English rationale cards** | Type 3: 28 generators; rules per generator + glosses on vocab tables | medium; content-authoring heavy | 0 | 🔭 open |
| **3 — science context cards** | Type 4: glosses on fact tables, card assembler | small | 0 | ✅ **SHIPPED 2026-08-13** (all 24) |
| **3a — science ASCII scaffolds** | Tier 1 visuals: one authored diagram per science concept | small | 3 | ✅ **SHIPPED 2026-08-13** (all 24, see note) |
| **3b — science SVG diagrams** | Tier 2 visuals: authored/parametric SVG per concept where a diagram genuinely beats words (sample approved-pending-look: `samples/light_scattering.svg`); render partial + CSS | medium; authoring-heavy, per-concept | 3 | 🔭 open |
| **4 — comprehension** | Type 5 | n/a — no such nodes exist yet | new content first | n/a |

Phases 1–3 are independent of each other; any can ship alone once Phase 0 lands.

**Phase 0 + 3 delivery notes (2026-08-13):** `Item.method_steps: tuple[str, ...] | None`
(`itembank.py`); `ItemGenerator._make` reads an optional 6th tuple element (index 4 is
choices' slot, present-or-None even for non-mc4 generators that want a card, so the
position is always unambiguous). Controller preference ladder implemented per §4b exactly:
`_worked_example_for`'s sibling-draw fallback now renders the card's lines instead of the
bare `"(Answer: X)"` string when the sibling has one (feeds BOTH the first Help LLM prompt
and `help_elaborate.md`); a new `elaborate_method_card` ctx field/property mirrors
`elaborate_steps_grid` exactly and renders the LIVE item's card directly on Explain-more,
skipping the LLM (safe here specifically — the child has already answered, unlike the
sibling-draw path). `mc_which_is` (shared by science/English/practice) gained optional
`glosses`/`concept_name` kwargs, fully backward-compatible (English/practice call sites
pass neither; unaffected). Card format: `(CONCEPT_NAME, "question → answer", "  answer →
label (gloss)", "  The others: d1 → label1 · d2 → label2 · d3 → label3")`. All 24 science
fact tables gloss-authored (48 one-line glosses + 24 concept names), verified against the
real dict keys programmatically before insertion (no transcription drift). Two new test
files (`tests/engine/test_method_cards.py`, `tests/engine/test_science_method_cards.py`)
+ controller wiring tests (`tests/dialogue/test_explain_mode_cards.py`) — the reasoning-
verification design in §5 is real code now, not aspirational. **LLM-narration layer (the
other half of the ratified §7 Q1 decision) NOT built this pass** — Phase 0 shipped the
bare-card path only, per the design's own sequencing ("Phase 0 builds the bare-card path
FIRST anyway"); narration + `explain_check` extension is follow-up work.

**Phase 3a delivery notes (2026-08-13) — a stale-status correction, not a new build from
scratch.** Auditing what "the rest of the ASCII text option" actually needed found
`curriculum/visual_scaffolds/science/` **already existed with all 24 concepts covered**
(22 files; two pairs of prereq-linked concepts intentionally share one file each —
`living_nonliving.md` covers both living-vs-nonliving AND animal groups,
`states_of_matter.md` covers both the three states AND the heat-driven change between
them — verified by running the REAL routing function, `load_visual_scaffold`, against
every node's actual curriculum label, not by eyeballing filenames). This doc's own §6
table had marked 3a "🔭 open" earlier the same day — itself stale, exactly the class of
error prior staleness audits kept finding: verify a status claim against the running
code, never trust a marker.

The REAL gap, found by checking what the bare-card Explain-more path actually renders:
the scaffolds exist and are well-authored, but were written FOR AN LLM to choose from and
weave into prose ("use ONE of these visual structures", multiple alternative diagrams, a
trailing "Guidelines for the question text" section) — and Phase 0's bare-card path is
LLM-free by design, so it never read them at all. Fixed with one new function,
`visual_scaffold.first_diagram()`: deterministically extracts just the first fenced
```` ``` ```` block (spot-checked across the full science set — consistently the
strongest, most self-contained diagram, the author's own natural lead choice), dropping
every instruction and every alternative. Wired into `_do_help_explain`'s elaborate branch:
when a method card exists, the concept's scaffold is looked up (existing
`load_visual_scaffold`, keyed off the node's real label) and its first diagram folded
into the SAME bare-card display as extra lines, after a blank-line separator. Verified
end-to-end, not just at the extractor level:
`test_elaborate_on_science_node_folds_in_the_ascii_diagram` drives a real controller turn
on a real science node and asserts both that the diagram text is present AND that no
LLM-meta-instruction ("Guidelines for the question text", "use ONE of these") ever reaches
the rendered card. `tests/engine/test_scaffold_coverage.py` (pre-existing) already
CI-gates the "every node has a scaffold" invariant this all depends on. 895 tests green
(was 894), ruff clean, doc-path checker clean.

## 7. Open questions (maintainer input wanted, none blocking Phase 0)

1. ~~**LLM-free or LLM-wrapped?**~~ **RESOLVED 2026-08-12 (maintainer): LLM-narrated,
   card-constrained, bare card as the fallback** — see §4b. The maintainer's reasoning:
   prose "is a better explain than just results and feels natural"; the constraint chain
   (card → narration → explain_check → bare-card fallback) keeps the correctness guarantee
   that motivated the original "direct" recommendation. Phase 0 builds the bare-card path
   FIRST anyway (it is the fallback, so it must exist before the narration can fail onto it),
   then the narration layer on top.
2. **First Help press vs Explain-more only?** Step grids deliberately render only on
   Explain-more (the maintainer's original placement ask). Method cards could justify the same
   placement, or could replace the first Help explanation for mc4 items where the modality
   prose adds little. Phase 0 keeps the step-grid precedent (Explain-more only); revisit with
   real usage.
3. **Gloss authoring for English/science tables** is content work with the same review burden
   as the original tables — worth confirming the maintainer wants that before Phase 2/3 start
   (Phase 0/1 need no new content at all).
