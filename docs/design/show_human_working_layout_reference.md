# "Show human working" — long-division layout reference (2026-07-19)

Maintainer feedback, LOGGED ONLY (explicitly "no action, just note down" — their
weekly session was ending). Supersedes nothing shipped; this is reference
material for the NEXT session's polish pass on `build_long_division_steps`
(`src/mentar/engine/arithmetic_steps.py`).

**Core ask: "needs to be aligned... I wanted clean and simple like this."** The
examples below are the maintainer's own reference for column alignment,
spacing, and labelling — treat as the target layout, not just inspiration.

## Worked examples (maintainer-supplied, verbatim)

### 1. Exact division, single-digit quotient (12 ÷ 3 = 4)

```
    4  <-- Quotient
  _____
3 ) 12  <-- Dividend
  - 12
  ____
     0  <-- Remainder
```

### 2. Division WITH a nonzero remainder (63 ÷ 5 = 12 remainder 3)

**Important scope note:** this is a case `build_long_division_steps` does NOT
currently support — the shipped builder only handles EXACT (terminating)
division and raises `ValueError` otherwise (see its docstring and
`extract_division_operands`). All three shipped division generators
(`gen_division_facts`, `gen_div_decimals`, `gen_div_decimal_by_decimal`)
construct their dividend FROM the quotient specifically to guarantee
exactness, so nothing shipped today actually needs remainder support — but
this example shows the maintainer may want it for a future generator/node
shape. Needs its own design pass (not scoped, not estimated) if picked up.

```
    12
  _____
5 ) 63
  - 5
  ____
    13
  - 10
  ____
     3  <-- Remainder
```

### 3. Fraction-bar notation (supplementary, not a layout ask)

```
  12
------ = 4
  3
```

### 4. Two-digit divisor, decimal dividend, decimal quotient (1345.0 ÷ 25 = 53.8)

```
      5 3 . 8
   ___________
25 ) 1 3 4 5 . 0
       - 1 2 5
   _______
       9 5
     - 7 5
     _____
       2 0   0
     - 2 0   0
     _________
             0
```

Note the precise column alignment here — this is a good self-check case for
the eventual alignment fix (2-digit divisor width, decimal point in both
dividend and quotient, multi-step subtraction blocks).

## Division sign reference

Maintainer linked: <https://www.alt-codes.net/division-sign-symbols> — for the
division bracket glyph (the current shipped `")"` character was separately
flagged as "looks weird" in the prior polish-notes round; this link is
presumably for finding a better one, or the right sign for other division
notations).

## Three explicit ASCII templates (maintainer-supplied, verbatim)

These look sourced from a worksheet/generator site (possibly the same one
behind the alt-codes.net link, or a companion resource) — `[ ]` marks a digit
placeholder. Treat as exact target layouts for 3-digit and 4-digit dividends,
plus an alternative "grid/pipe" visual style worth considering as a design
option (not necessarily a replacement for the current CSS Grid approach).

### Template 1 — 3-digit dividend, 2 subtraction steps

```
[ ] [ ] [ ]
     _____________
[ ] )  [ ] [ ] [ ]
     - [ ] [ ]
     _________
           [ ] [ ]
         - [ ] [ ]
         _________
               [ ]  <-- Remainder
```

### Template 2 — 4-digit dividend, up to 3 subtraction blocks

```
[ ] [ ] [ ] [ ]
       _________________
[ ] )  [ ] [ ] [ ] [ ] [ ]
     - [ ] [ ]
     ___________
           [ ] [ ]
         - [ ] [ ]
         _________
               [ ] [ ]
             - [ ] [ ]
             _________
                   [ ]  <-- Remainder
```

(Note: the maintainer's own template shows a 4-digit quotient header but a
5-`[ ]` dividend row — likely a typo in their source material, not a spec
detail to replicate literally; flag/confirm before building against it.)

### Template 3 — "Grid-style" pipe-separated columns (alternative visual direction)

```
      | [ ] | [ ] | [ ] |
   -----------------------
[ ] ) | [ ] | [ ] | [ ] |
    - | [ ] | [ ] |     |
   -----------------------

      |     | [ ] | [ ] |
    - |     | [ ] | [ ] |
   -----------------------

      |     |     | [ ] | <-- Remainder
```

This is visually a different approach from the other two (and from what's
currently shipped): explicit vertical pipe dividers between every place-value
column, giving a literal boxed-grid look. Worth considering as a distinct
style option in the eventual "two display types, switchable in Settings"
request already logged in
[[project_show_human_working_idea]] / `docs/PHASE0_STATUS.md`, rather than
assuming it replaces the current borderless CSS Grid style outright.

## How this relates to what's already logged

The four CSS-only polish notes from earlier the same session (carry/borrow
font size, "−" sign spacing, the `)` bracket glyph, general cleanliness) are
in `docs/PHASE0_STATUS.md`'s backlog row and [[project_show_human_working_idea]].
This file is the (much larger) follow-up reference material for the same
"needs alignment work" ask — read both before starting the next polish pass.
