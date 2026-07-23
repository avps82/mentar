---
type: Mentar Reference Material
title: Year 1-6 mathematics visual templates
description: Maintainer dump of 16 ASCII templates across 5 sections spanning the full Year 1-6 range, logged only.
tags: [design, reference, mathematics, visual-scaffold, logged-only]
timestamp: "2026-07-19T00:00:00Z"
---

# Year 1-6 mathematics visual templates (2026-07-19)

Maintainer dump, LOGGED ONLY (same pattern as the other two reference docs
logged the same session — no action requested). 16 ASCII templates across 5
sections, spanning the FULL Year 1-6 range. Companion to
`docs/design/comprehensive_math_templates_reference.md` (the earlier, less
grade-banded dump) — read that file's scope note too, it applies here
identically: none of this is a small extension of `engine/arithmetic_steps.py`
(shipped: add/sub/mult/div column/bus-stop grids only), each topic needs its
own design pass.

## Section 1: Place value & number operations

### Template 1 — master place value chart (millions to thousandths)

```text
  [M]     [H-Th]  [T-Th]   [Th]    [H]     [T]     [O]         [t]     [h]     [th]
 Millions  Hun-    Ten-   Thou-   Hun-    Tens    Ones    •   Tenths  Hun-    Thou-
          Thous   Thous   sands   dreds                  dec         dredths sandths
_____________________________________________________________________________________
 [   ]  | [   ]  | [   ]  | [   ]  | [   ]  | [   ]  | [   ]  | • | [   ]  | [   ]  | [   ]  |
________|________|________|________|________|________|________|___|________|________|________|
```

### Template 2 — vertical grid, addition/subtraction with decimals

```text
       [   ]   [   ]   [   ]        [   ]   [   ]   <-- Regrouping / Carrying Row
       [   ]   [   ]   [   ]    •   [   ]   [   ]
   ±   [   ]   [   ]   [   ]    •   [   ]   [   ]
   -----------------------------------------------
       [   ]   [   ]   [   ]    •   [   ]   [   ]
```

### Template 3 — long division layout, decimal-capable

```text
           [ ] [ ] . [ ]
       _________________
  [ ] )  [ ] [ ] [ ] . [ ]
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

## Section 2: Integers, fractions & percentages

### Template 4 — dual-direction number line (-8 to +8)

```text
 <---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|--->
    -8  -7  -6  -5  -4  -3  -2  -1   0  +1  +2  +3  +4  +5  +6  +7  +8
```

### Template 5 — fraction bar models (equivalence and comparison)

```text
  [========================= 1 Whole =========================]
  [============ 1/2 ============][============ 1/2 ============]
  [====== 1/4 ======][====== 1/4 ======][====== 1/4 ======][====== 1/4 ======]
  [== 1/8 ==][== 1/8 ==][== 1/8 ==][== 1/8 ==][== 1/8 ==][== 1/8 ==][== 1/8 ==][== 1/8 ==]
```

### Template 6 — fraction processing block, four operations

```text
    [   ]         [   ]         [   ] × [   ]         [   ]
   -------   ■   -------   =   ---------------   =   -------
    [   ]         [   ]         [   ] × [   ]         [   ]
```

### Template 7 — 100-square percentage grid

```text
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]  (Each block = 1% = 0.01 = 1/100)
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
  [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
```

## Section 3: Ratios, proportions & expressions

### Template 8 — ratio tape diagram

```text
  Quantity A: | [   ] | [   ] | [   ] |
  Quantity B: | [   ] | [   ] |
```

### Template 9 — "butterfly" proportion grid

```text
        ____         ____
       / [ ]\       /[ ] \
      (   --- ) = (  ---  )
       \___[ ]/     \[ ]_/
         \             /
          \___________/
```

### Template 10 — PEMDAS order-of-operations pathway

```text
  1. ( ) Parentheses ==>  ___________________________
  2. x²  Exponents   ==>  ___________________________
  3. ×/÷ Left-Right  ==>  ___________________________
  4. +/- Left-Right  ==>  ___________________________
```

## Section 4: Geometry & measurement (Year 5-6 extension)

### Template 11 — 2D shape dimensions (perimeter & area)

```text
         <----- [Length] ----->
      +-----------------------+  ^

      |                       |  |
      |                       | [Width]
      |                       |  |
      +-----------------------+  v
```

### Template 12 — 3D isometric prism (volume: L × W × H)

```text
          +---------+
         /         /|
        /         / |  [Height]
       +---------+  +    v

       |         | /
       |         |/   [Width]
       +---------+   /
      < [Length] >  v
```

### Template 13 — protractor & angle classifications

```text
          Acute       Right       Obtuse       Straight
          (<90°)     (90°)      (90°-180°)      (180°)
            /          |           \
           /           |            \
          /____        |____         \____      ________
```

## Section 5: Data, statistics & coordinate planes (Year 4-6)

### Template 14 — 4-quadrant coordinate grid

```text
                 +Y
                  |
             2    |    1
                  |
       -X --------+-------- +X
                  |
             3    |    4
                  |
                 -Y
```

### Template 15 — frequency & tally data chart

```text
  Category / Item    | Tally Marks    | Frequency (Total)
  -------------------|----------------|------------------
  [                ] | ||||           | [   ]
  [                ] | ||||-||||      | [   ]
  [                ] | ||               | [   ]
```

### Template 16 — mean, median, mode, and range toolkit

```text
  Data Set Ordered:  [   ], [   ], [   ], [   ], [   ]

  * Mean (Average):  (Sum of all items) ÷ (Total count of items)
  * Median (Middle): Central value in ordered list
  * Mode (Frequent): Most repeated value
  * Range (Spread):  Largest value - Smallest value
```

## Related files

- `docs/design/comprehensive_math_templates_reference.md` — the earlier,
  less grade-banded dump from the same session.
- `docs/design/year7_12_math_templates_reference.md` — the Year 7-12
  companion (algebra graphing, trig, calculus, matrices, financial math).
- `docs/design/show_human_working_layout_reference.md` — division-specific
  alignment reference (the one feature area from this whole inventory that's
  actually shipped, Phase 1-4).
- Memory: [[project_comprehensive_math_templates_idea]].
