# Comprehensive basic-mathematics reference templates (2026-07-19)

Maintainer dump, LOGGED ONLY ("Note it down for now" — no action requested).
16 ASCII templates across 7 topic areas, supplied verbatim as reference
material for POTENTIAL future "show human working"-style visual scaffolding.

**Scope note:** this is substantially BROADER than what's shipped. The shipped
"show human working" feature ([[project_show_human_working_idea]],
`docs/PHASE0_STATUS.md`) covers only the four arithmetic operations
(add/sub/mult/div) as column/bus-stop step grids. This dump adds templates for
topics that don't exist as step-grid content at all today: decimal place-value
charts, fraction operations (common-denominator add/sub, keep-change-flip
division, mixed-number borrowing), percentage/ratio visuals, geometry
perimeter/area, exponents/radicals, and a PEMDAS order-of-operations
checklist. Each would need its OWN design pass (own extraction logic against
real generator phrasings, own builder, own tests) — none of this is a small
extension of the existing `arithmetic_steps.py` module. Treat this file as a
long-range idea inventory, not a scoped backlog item.

## Section 1: Multi-digit & decimal long division

Two more division layout variants, on top of the ones already logged in
`docs/design/show_human_working_layout_reference.md` (which is the file to
check FIRST for anything division-related — this section is additional, not
a replacement).

### Template 1 — whole-number long division, 4-digit dividend

```text
         [ ] [ ] . [ ]
       _______________
  [ ] ) [ ] [ ] [ ] [ ]
     - [ ] [ ]
     ___________
           [ ] [ ]
         - [ ] [ ]
         _________
               [ ] [ ]
             - [ ] [ ]
             _________
                     0
```

### Template 2 — decimal long division

```text
         [ ] [ ] . [ ]
       _______________
  [ ] ) [ ] [ ] [ ] . [ ]
     - [ ] [ ]
     ___________
           [ ]
         - [ ]
         _________
               [ ] [ ]
             - [ ] [ ]
             _________
                     0
```

## Section 2: Decimal place values & grid operations

### Template 3 — decimal place-value alignment chart

```text
    [10,000s] [1,000s]  [100s]   [10s]    [1s]         [0.1s]   [0.01s]  [0.001s]
       Ten-    Thou-     Hun-                     •    Tenths    Hun-     Thou-
    Thousands  sands    dreds    Tens     Ones   dec            dredths  sandths
   _______________________________________________________________________________

  |   [   ]  |  [   ]  |  [   ]  |  [   ]  |  [   ]  | • |  [   ]  |  [   ]  |  [   ]  |
  |__________|_________|_________|_________|_________|___|_________|_________|_________|
```

### Template 4 — decimal addition grid (labelled place-value columns + carry row)

```text
       Hundreds  Tens   Ones         Tenths  Hundredths
        [   ]   [   ]  [   ]    •    [   ]    [   ]     <-- Carrying Row
        [   ]   [   ]  [   ]    •    [   ]    [   ]
   +    [   ]   [   ]  [   ]    •    [   ]    [   ]
   ---------------------------------------------------
        [   ]   [   ]  [   ]    •    [   ]    [   ]
```

Note: this is a labelled-column variant of what `build_addition_steps` already
does (unlabelled) — the addition/subtraction ALGORITHM is shipped; this
template's novelty is the explicit "Hundreds/Tens/Ones/Tenths/Hundredths"
header row, not new arithmetic.

### Template 5 — decimal subtraction grid (labelled place-value columns + borrow row)

```text
       Hundreds  Tens   Ones         Tenths  Hundredths
        [   ]   [   ]  [   ]    •    [   ]    [   ]     <-- Borrowing Row
        [   ]   [   ]  [   ]    •    [   ]    [   ]
   -    [   ]   [   ]  [   ]    •    [   ]    [   ]
   ---------------------------------------------------
        [   ]   [   ]  [   ]    •    [   ]    [   ]
```

Same note as Template 4 — labelled-column variant of the shipped
`build_subtraction_steps`.

## Section 3: Integers & negative numbers

### Template 6 — dual-direction horizontal number line

```text
 <---|---|---|---|---|---|---|---|---|---|---|--->
    -5  -4  -3  -2  -1   0   1   2   3   4   5
```

### Template 7 — vertical "elevator" guide

```text
   [ +3 ]
   [ +2 ]
   [ +1 ]
     0  <-- Ground Level
   [ -1 ]
   [ -2 ]
   [ -3 ]
   [ -4 ]
   [ -5 ]
```

Relevant to the negative-operand exclusion already documented in
`arithmetic_steps.py` (Y7's `gen_integers_add_sub`/`gen_negative_multiplication`
are explicitly NOT step-eligible for the column/bus-stop methods — "different
pedagogical case, number-line reasoning"). These two templates are exactly
that different pedagogical case's visual — worth reconsidering the negative-
operand exclusion in light of these once/if this area gets designed.

## Section 4: Fractions & mixed numbers

### Template 8 — adding/subtracting fractions (common denominator), 3-step

```text
  Step 1: Original Problem       Step 2: Multiply to Match       Step 3: Add / Subtract Tops
                        ×     [   ]          [   ]   [   ]     [   ]
    -------   ±   -------   ===>   --------------- = -------  ===>  ------- ± ------- = -------
                        ×     [   ]          [   ]   [   ]     [   ]

                                    ×     [   ]          (Keep the bottom the same!)
                                   --------------- = -------
                                    ×     [   ]
```

### Template 9 — dividing fractions ("keep, change, flip")

```text
    KEEP         CHANGE        FLIP
   [   ]                       [   ]              [   ]       × [   ]       [   ]
  -------          ÷          -------  ===>  ------- × -------  =  ---------------  =  -------
   [   ]                       [   ]              [   ]       × [   ]       [   ]
```

### Template 10 — subtracting mixed numbers with borrowing, 3-step

```text
  Step 1: Original Problem         Step 2: Borrow 1 from Whole       Step 3: Final Subtraction
         [ ]                                     [ ] + [ ]                           [ ]       [ ]
     [ ] -------                             [ ] ---------                       [ ] ------- - -------
         [ ]                                        [ ]                              [ ]       [ ]
-                                     -                                   -
         [ ]                                     [ ]                                           [ ]
     [ ] -------                             [ ] -------                                   = -------
         [ ]                                        [ ]                                        [ ]
```

## Section 5: Ratios, percentages, and proportions

### Template 11 — 100-block percentage grid (10×10)

```text
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
```

### Template 12 — ratio tape diagram

```text
  Category A | [   ] | [   ] | [   ] |
  Category B | [   ] | [   ] |
```

### Template 13 — "butterfly" proportion layout

```text
        ____         ____
       / [ ]\       /[ ] \
      (   --- ) = (  ---  )
       \___[ ]/     \[ ]_/
         \             /
          \___________/
```

## Section 6: Basic geometry (perimeter & area)

### Template 14 — geometric dimension block

```text
         <----- [ ] units ----->
      +-----------------------+  ^

      |                       |  |
      |                       | [ ] units
      |                       |  |
      +-----------------------+  v

  Formula Checklist:
  Perimeter = Side + Side + Side + Side
  Area      = Length × Width
```

## Section 7: Exponents, square roots, and order of operations

### Template 15 — exponents & radicals block

```text
   Exponent Form:     [Base]^[Exponent] = [Base] × [Base]...

   Square Root Form:  \/ [   ]  =  [   ]
```

### Template 16 — PEMDAS order-of-operations workflow checklist

```text
  [ ] Step 1: Parentheses ( )      ==>  ___________________________
  [ ] Step 2: Exponents x²         ==>  ___________________________
  [ ] Step 3: Multiply/Divide (L->R)==>  ___________________________
  [ ] Step 4: Add/Subtract (L->R)  ==>  ___________________________
```

Relevant to `gen_order_of_ops_negatives` (already shipped, Y7) — this
checklist template is a possible future visual for that node's Explain-more,
distinct from the column/bus-stop grids.

## Related files

- `docs/PHASE0_STATUS.md` — canonical backlog row for "show human working"
  (shipped Phase 1-4 status + the smaller polish-notes/layout-reference items).
- `docs/design/show_human_working_layout_reference.md` — the division-specific
  alignment reference logged earlier the same session.
- Memory: [[project_show_human_working_idea]].
