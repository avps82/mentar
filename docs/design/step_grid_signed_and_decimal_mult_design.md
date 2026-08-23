---
type: Mentar Design Doc
title: "Step-grid design — signed arithmetic and decimal multiplication (E1 Findings 3+5)"
description: "Phases A+B SHIPPED 2026-08-12 (draw-dependent step-grid eligibility 16 nodes -> 4); Phase C still gated on maintainer worked examples. Answers docs/EXPLAIN_METHOD_AUDIT.md Findings 3 and 5."
tags: [design, reference, arithmetic, show-human-working, partially-shipped]
timestamp: "2026-08-11T00:00:00Z"
---

# Step-grid design — signed arithmetic and decimal multiplication

**Status: ALL THREE PHASES SHIPPED 2026-08-12. Draw-dependent step-grid eligibility is now ZERO.** A+B took draw-dependent eligibility from **16 nodes to 4**, and C closed the last 4 the
same day: **16 → 4 → 0**, with always-step-grid rising 56 → 72. See § Outcome at the end.

**Phase C was built as option 2 (the same-sign/different-sign rule), not option 1 (a number-line
rendering primitive), on the maintainer's "go do it".** §4 below asked for worked examples first
and recommended option 2 as the default absent a preference; that recommendation was taken. The
number line remains a live alternative — if it is preferred, `build_signed_addition_steps` is the
single function to replace, and the extractor, the controller wiring and the tests all stay.

Originally written in response to the maintainer's ask to turn `docs/EXPLAIN_METHOD_AUDIT.md`'s
Findings 3+5 — logged as "not a tonight-sized item; needs its own plan" — into an actual plan.
The plan text below is kept as written; the Outcome section records what shipped against it.

## 1. Restating the problem precisely

`engine/arithmetic_steps.py` renders the ASCII "show human working" step-grid for four
operations, but its extraction gate (`extract_addition_operands` /
`extract_subtraction_operands` / `extract_multiplication_operands`) silently returns `None`
— falling back to LLM prose — for two shapes it deliberately excludes:

| Node | Operation | Excluded shape | Eligible today |
|---|---|---|---|
| `au7_integers_add_sub` | add/sub | either operand negative | 21% (only when both operands land ≥0) |
| `au8_negative_multiplication` | multiplication | either operand negative | 23% (same reason) |
| `au6_mult_decimals` | multiplication | non-integer (decimal) operand | 13% (only when the decimal happens to be a whole number, e.g. "20.0") |
| `au7_mult_decimal_by_decimal` | multiplication | non-integer operand, both sides | 1% (needs BOTH decimals to independently land whole) |

These are **two unrelated problems that happen to share one symptom** (draw-dependent
eligibility on the same four nodes' concept), not one problem:

- **Signed operands** (add/sub AND multiplication) is a genuine pedagogical-shape gap: the
  shipped column-carry/borrow method is explicitly the *unsigned* early-years algorithm
  (see the module's own docstring). A negative operand isn't a harder version of the same
  method, it needs a *different* method — number-line reasoning for add/sub, a sign-rule
  step for multiplication.
- **Decimal multiplication** is not a new method at all — it is the *exact same*
  partial-products algorithm already shipped, applied to the operands' digit-strings with
  the decimal points stripped, then the point re-inserted in the result by counting total
  decimal places. `build_addition_steps`/`build_subtraction_steps` already do the
  equivalent scaling for decimals (see `_frac_digits`/`_layout`); multiplication just never
  got the same treatment because Phase 3's own docstring scoped it out explicitly
  ("decimal multiplication ... needs its own place-value handling ... and is deferred, not
  silently dropped").

Given that, this plan is **three independently shippable phases**, ordered smallest/lowest-risk
first, not one monolithic build:

- **Phase A — decimal multiplication** (fixes `au6_mult_decimals`, `au7_mult_decimal_by_decimal`)
- **Phase B — signed multiplication** (fixes `au8_negative_multiplication`)
- **Phase C — signed addition/subtraction** (fixes `au7_integers_add_sub`)

A and B are small, mechanical extensions of code that already exists in the file. C is the
genuinely new piece — a different visual shape, not a parameter extension — and per this
project's own standing lesson (`feedback_use_reference_examples_immediately`: *"ask for a
picture before building from-scratch when a named visual convention is referenced"*), C
should not be built from an invented ASCII convention. It needs the maintainer's own worked
example first, the same way `build_long_division_steps` was rebuilt against
`show_human_working_layout_reference.md`'s maintainer-supplied examples, not a
guessed layout.

---

## 2. Phase A — decimal multiplication (small, do first)

**Target nodes:** `au6_mult_decimals` (decimal × whole), `au7_mult_decimal_by_decimal`
(decimal × decimal).

**Algorithm** (standard school method — ignore the points, multiply as whole numbers,
count total decimal places, place the point that many digits from the right):

1. Compute `frac_digits = _frac_digits(a) + _frac_digits(b)` — **sum**, not `max` like
   add/sub (`extract_multiplication_operands`'s own docstring already flags this
   asymmetry).
2. Scale both operands to integers: `int_a = int(a * 10**_frac_digits(a))`,
   `int_b = int(b * 10**_frac_digits(b))`.
3. Run the **existing, unchanged** `build_multiplication_partial_products_steps(int_a, int_b)`
   to get a grid of the whole-number multiplication.
4. Re-insert a decimal point into the **result row only** (the operand rows keep their
   own point in their original position — this is the one place decimal multiplication's
   grid genuinely differs from add/sub's: the operand rows show the ORIGINAL decimal
   numbers as given, not the scaled integers, while the partial-product rows in between are
   the true intermediate INTEGER products with no point at all — that's how a child is
   actually taught the method, and is why this can't just reuse `_layout`/`_insert_point`
   unchanged for every row, only for the top operand rows and the final result row).

**Worked example** (`3.4 × 20 = 68.0`): strip points → `34 × 20`, run the existing
partial-products builder unchanged (`34 × 20 = 680`, shown via its normal carry-row/
partial-product-row layout), then re-insert the point 1 place from the right in the result
row only (`_frac_digits(3.4) + _frac_digits(20) = 1 + 0 = 1`) → `68.0`. The operand rows at
the top of the grid still show `3.4` and `20` as given (with `3.4`'s own point in place),
not the scaled integers — only the internal partial-product rows and the final result row
come from the integer-scaled arithmetic.

Unlike Phase C the ALGORITHM itself is not in question here (it's the standard taught
method, unambiguous) — only the exact ASCII row-labelling/spacing convention benefits from
a quick "does this look right" check against a real rendered example
(`3.4 × 20 = 68.0`, `2.4 × 3.6 = 8.64`) before shipping, not a blocking design gate.

**New code needed:**
- A new function `build_multiplication_decimal_steps(a: Decimal, b: Decimal) -> StepGrid`
  in `arithmetic_steps.py`, wrapping `build_multiplication_partial_products_steps` rather
  than duplicating its carry logic.
- `extract_multiplication_operands` currently hard-rejects non-integer operands
  (`a != a.to_integral_value()`). This gate needs a second extraction path — either widen
  the existing function to return a `(Decimal, Decimal, is_decimal: bool)` tuple, or add a
  sibling `extract_decimal_multiplication_operands`. Prefer the sibling function: keeps
  `extract_multiplication_operands`'s existing integer-only contract (and its callers)
  untouched, matches how `extract_division_operands`'s `ending` parameter is already kept
  out of the extraction function itself and decided by the caller
  (`_build_steps_grid_if_eligible`).
- Wire the new extractor + builder into `_build_steps_grid_if_eligible` as a fallback when
  `extract_multiplication_operands` returns `None` but the problem text still matches the
  multiplication shape with decimal operands.

**Estimated size:** ~1-2 hours including tests (300-draw self-validate style: run both
generators through the new path, spot-check a handful of grids by eye, add a regression
test file mirroring `tests/engine/test_arithmetic_steps.py`'s existing shape). No new Cell
kinds, no new rendering primitive — reuses everything.

---

## 3. Phase B — signed multiplication (small-medium)

**Target node:** `au8_negative_multiplication` (`a, b` each independently `±(2..12)`).

**Algorithm** (standard taught method — determine the sign FIRST as its own explicit step,
then multiply magnitudes with the ordinary method, then apply the sign):

1. Sign step: "same signs → positive, different signs → negative" — shown as its own
   labelled row/line, not folded into the digit grid (this is a genuine extra step in how
   the method is taught, distinct from the digit arithmetic itself).
2. Magnitude step: run the **existing, unchanged** `build_multiplication_partial_products_steps(abs(a), abs(b))`.
3. Result step: the magnitude result with the sign from step 1 applied, shown as the final
   answer line — e.g. `-8 × -3` → sign: "same signs → positive" → magnitude: `8 × 3 = 24`
   (full partial-products grid) → result: `-8 × -3 = 24`.

**New code needed:**
- A new function `build_signed_multiplication_steps(a: int, b: int) -> StepGrid` that
  prepends a sign-rule row/line to the existing partial-products grid and adjusts the final
  result row to show the signed values. Reuses `build_multiplication_partial_products_steps`
  as its core, does not reimplement carries.
- `extract_multiplication_operands` needs a sibling that permits negative integer operands
  (mirroring the decimal case in Phase A — keep the existing function's contract
  unchanged, add a signed-integer path). Note `au8_negative_multiplication`'s operands are
  always non-zero integers by construction (`rng.choice([-1,1]) * rng.randint(2,12)`), so
  no zero-sign edge case to handle for this specific node — but the new extractor/builder
  should still handle `a=0` or `b=0` defensively (result 0, sign line reads "n/a" or is
  omitted) since it's a general-purpose function, not tied to this one generator.
- Wire into `_build_steps_grid_if_eligible` alongside Phase A's new path.

**Open question for the maintainer** (small, not a blocker): does the sign-rule row belong
ABOVE the magnitude grid (as a preliminary/setup step) or as a labelled line appended
AFTER the magnitude result (as a final "now apply the sign" step)? Both are pedagogically
common; a one-line preference avoids building the wrong one. Recommend defaulting to
ABOVE (state the rule before doing the arithmetic, matching how the audit and this
project's other explanations generally front-load the reasoning) if no preference is
given, and note it as a two-line change to flip later either way — not worth blocking on.

**Estimated size:** ~1-2 hours including tests, similar scope to Phase A.

---

## 4. Phase C — signed addition/subtraction (the genuinely new piece)

**Target node:** `au7_integers_add_sub` (`a, b` each independently `±15`, add or subtract).

**Why this is different from A and B:** unlike multiplication, addition/subtraction of
signed numbers is not "the same method with a sign rule bolted on" — the actual taught
method is **number-line movement** (start at `a`, move right for `+`/adding a positive,
left for `-`/subtracting a positive or adding a negative), which is a different visual
shape entirely from a right-aligned digit grid. Forcing it into the existing `StepGrid`
(rows of `Cell`s in fixed columns) would misrepresent how the method is actually taught —
the same reasoning the module's own docstring already gives for excluding negatives from
the column method in the first place.

**This plan deliberately does NOT propose an ASCII number-line convention.** Per
`feedback_use_reference_examples_immediately` and the precedent already set by
`show_human_working_layout_reference.md` (long division was rebuilt against the
maintainer's own worked examples, not an invented layout), Phase C should start with a
short worked-example request, not a build. Concretely, before any code:

> Ask the maintainer for 2-3 worked examples of how they want signed addition/subtraction
> shown — e.g. a number-line ASCII sketch for `-8 + 3` and `5 - 12`, or an alternative
> convention they prefer (some curricula teach "same signs add and keep the sign, different
> signs subtract and keep the sign of the bigger one" as a text-rule method instead of a
> number line, which is much closer in shape to Phase B's sign-rule step and could reuse
> more of the existing rendering).

**Two candidate directions, for the maintainer to choose between** (not decided here):

1. **Number-line rendering.** Needs a genuinely new StepGrid-adjacent rendering primitive
   (a horizontal track with a marked start point, an arc/arrow showing the move, and an end
   point) — the biggest lift of the three phases, closer in size to a full
   "show human working" phase than a quick extension. Needs its own Cell-kind vocabulary
   (or a wholly separate rendering path outside `StepGrid` entirely, since the layout is
   fundamentally 1D-linear-with-an-arc, not a 2D column grid) and a CSS treatment on the
   web layer to match (the module docstring notes rendering goes through CSS Grid, not
   markdown — a number line likely needs its own CSS shape, not a reuse of the grid CSS).
2. **Same-sign/different-sign text-rule method.** Structurally close to Phase B's sign-rule
   step: "same signs → add the magnitudes, keep the sign" / "different signs → subtract the
   smaller magnitude from the larger, keep the sign of the bigger" — then reuse the
   **existing unsigned** `build_addition_steps`/`build_subtraction_steps` on the magnitudes
   for the actual digit arithmetic, exactly like Phase B reuses
   `build_multiplication_partial_products_steps`. This is dramatically smaller than option
   1 (no new rendering primitive) and consistent with how this project has approached
   every other signed-number case in this document, but it's a different taught method
   than "count on a number line" and may not match what the maintainer actually wants for
   this specific node/age group (Year 7 integers) — hence asking rather than assuming.

**Recommendation:** propose option 2 (text-rule + reuse of existing column grid) as the
default unless the maintainer specifically wants the number-line visual, since it ships in
roughly the same effort class as Phases A/B rather than opening a new rendering surface —
but this is explicitly a recommendation to confirm, not a decision made here.

**Estimated size:** option 2 ≈ 2-3 hours (similar shape to A/B plus the sign-rule
determination logic, which is slightly more branchy than multiplication's since it also
picks the OPERATOR shown in the reused grid — e.g. `-8 + 3` becomes "different signs →
subtract smaller from larger, keep sign of bigger" → reuses `build_subtraction_steps(8, 3)`
→ final sign applied). Option 1 (number line) is unscoped until worked examples exist —
plausibly a half-day-plus effort given it needs new rendering, not just new logic.

---

## 5. Suggested build order and gate

1. Phase A (decimal multiplication) — no open questions, ship first.
2. Phase B (signed multiplication) — one small open question (sign-row placement), ship
   with the recommended default if no reply, flip later if wrong.
3. Phase C (signed add/sub) — **gated on the maintainer's worked-example reply**; do not
   start building until that arrives, per the reference-examples-first lesson this project
   has already paid for once (long division) and should not re-pay.

Each phase, when built, should follow the same verification discipline every other wave in
this project has used: 200-300 draws through the real generator + real extractor to confirm
eligibility actually reaches ~100% (not just reading the code and assuming), a handful of
grids checked by eye against a known-correct worked example, and a regression test file
alongside the existing `tests/engine/test_arithmetic_steps.py`.


---

## Outcome (2026-08-12)

### Phases A + B — shipped

| | Before | After |
|---|---|---|
| Draw-dependent nodes | 16 | **4** |
| Always step-grid | 56 | **68** |

Phase A resolved 8 nodes (`*_mult_decimals` ×4, `*_mult_decimal_by_decimal` ×4), Phase B
resolved 4 (`*_negative_multiplication` ×4). Both landed as the plan specified: sibling
extractors rather than widening `extract_multiplication_operands` (its integer-only contract
and its caller stay untouched), and both builders **wrap the existing, unchanged**
`build_multiplication_partial_products_steps` rather than re-deriving its carry logic. The
three multiplication extractors provably partition the input space, so the controller's chain
order is not load-bearing — asserted by a test, since if that ever stops being true the chain
becomes silently order-dependent.

Phase B's sign row sits **above** the arithmetic (state the rule, then use it), the default the
plan recommended. Moving it below is a two-line change. Zero is handled explicitly rather than
by the sign rule — "same signs → positive" is false for `-7 × 0`, and no shipped generator
produces it, but the builder is general-purpose.

**Two real bugs caught while building, both by running rather than reading:**
1. Re-inserting the decimal point widens the grid by one cell, and padding a `LINE` row with a
   digit-kind cell punched a gap through the rule (`- ---` instead of `-----`). Padding now
   matches the row's own kind.
2. A first cut of the test asserted every `gen_negative_multiplication` draw is signed. It
   isn't — each operand's sign is drawn independently, so ~25% are both-positive and correctly
   take the plain integer path. **That is exactly the 25.5% eligibility the pre-fix audit
   measured**, i.e. the "bug" in the test was the audit's own number, confirming both.

A live round-trip through a real `SessionController` puts all three fixed node families at
**12/12** draws, and `au7_integers_add_sub` at 3/12 (Phase C, unchanged as expected). Note the
first cut of that round-trip reported 0/12 for a *working* node because it passed a single node
in isolation, whose prereqs the fringe could then never satisfy — a harness artifact, not a
product bug, and the same class of self-inflicted false signal seen twice before this session.

### Phase C — SHIPPED (option 2)

The remaining 4 nodes (`*_integers_add_sub`, e.g. `What is 5 - 12?`) need signed
addition/subtraction. This document's §4 asked for 2–3 worked examples before building, because
the two candidate conventions (number-line movement vs. the same-sign/different-sign text rule)
are genuinely different pedagogy, not an implementation detail. That request stands. Option 2
(text rule + reuse of the existing column grid) remains the recommendation if no preference is
given — it is structurally identical to Phase B, which is now shipped and proven — but it is a
teaching-method choice, and the project has already paid once for inventing a layout instead of
asking (`show_human_working_layout_reference.md`).
