---
type: Mentar Visual Scaffold
title: Algebra — Solving One-Step and Two-Step Equations
description: Visual scaffold hints for solving linear equations using balance and inverse operations.
tags: [mathematics, algebra, equations, visual-scaffold, balance, inverse-operations]
subject: mathematics
topic_keywords: [equation, solve, unknown, variable, one-step, two-step, balance, inverse, algebra, find x, what is x, linear equation]
timestamp: "2026-07-22T00:00:00Z"
---

When writing or explaining this question, use the balance layout below. Rules:
- NO square brackets [ ] around expressions
- Always show the explicit middle step (operation applied to both sides)
- Keep ⚖️ and other emoji OUTSIDE the equation block — before or after, never on a row
- **Column alignment:** find the LONGEST left-hand expression in the block, then pad EVERY left-hand expression with spaces to that same width — this keeps ALL `=` signs in a single vertical column
- **Arrow alignment:** use EXACTLY 4 spaces before every `←` arrow — no more, no fewer

**One-step balance** — three rows. `x + 5 - 5` is the longest LHS (9 chars), so every LHS is padded to 9:
```
  x + 5        = 12
  x + 5 - 5    = 12 - 5    ← subtract 5 from both sides
  x            = 7
```

**Two-step balance** — five rows. `2x + 3 - 3` is the longest LHS (10 chars), padded to 14. EXACTLY 4 spaces before every `←` — count them:
```
  2x + 3        = 11
  2x + 3 - 3    = 11 - 3    ← subtract 3 from both sides
  2x            = 8
  2x ÷ 2        = 8 ÷ 2     ← divide both sides by 2
  x             = 4

  Check: 2 × 4 + 3 = 8 + 3 = 11 ✓
```
Count the spaces above: `11 - 3    ←` has 4 spaces; `8 ÷ 2     ←` has 5 spaces (one extra because `8 ÷ 2` is 1 char shorter than `11 - 3`). The rule is: pad the shorter expression first so both reach the same width, THEN add 4 spaces. If both expressions are the same length, both get exactly 4 spaces.

The ⚖️ may appear as a standalone line before the block (e.g. "Let's keep both sides balanced ⚖️") or after — never inside a row.

**Guidelines:**
- Never skip the middle row.
- Use a single letter (x) consistently; do not switch variables.
- Year 7 (one-step): one inverse operation only.
- Year 8 (two-step): always show BOTH steps and the check.
- Word-problem framing: "A number is multiplied by 3 and then 5 is added, giving 17. Find the number."
