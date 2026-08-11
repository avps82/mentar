---
type: Mentar Visual Scaffold
title: Order of Operations — BODMAS / BIDMAS
description: Visual scaffold hints for order of operations (brackets, indices, division/multiplication, addition/subtraction).
tags: [mathematics, order-of-operations, BODMAS, BIDMAS, visual-scaffold]
subject: mathematics
topic_keywords: [order of operations, bodmas, bidmas, brackets, indices, powers, order, evaluate, simplify expression, order of operations with negative, negatives]
timestamp: "2026-07-22T00:00:00Z"
---

When writing or explaining this question, use ONE of these visual structures:

**Staircase / priority ladder** — work top-down:
```
Step 1  B — Brackets          ( )  first
Step 2  O — Orders/Indices    x²   second
Step 3  D — Division          ÷    left-to-right
Step 4  M — Multiplication    ×    left-to-right
Step 5  A — Addition          +    left-to-right
Step 6  S — Subtraction       −    left-to-right
```

**Worked annotation** — underline the operation to do next, one step per line:
```
  3 + 4 × 2
= 3 + (4 × 2)     ← multiply first
= 3 + 8
= 11
```

**Brackets-change-everything contrast**:
```
Without brackets:  3 + 4 × 2 = 11   (multiply first)
With brackets:    (3 + 4) × 2 = 14  (add first)
```

**Guidelines for the question text:**
- Always show the full expression before any steps.
- Annotate which rule is applied at each step (e.g. "× before +").
- For Year 6: BODMAS without indices. Year 7+: include powers and roots.
- Negative numbers: use brackets to make signs unambiguous: (−3) + 5.

**Negative leading term** — the sign belongs to the number, not to the next operation
(use for `order_of_ops_negatives` nodes, e.g. "What is -13 + 6 × 6?"):
```
-13 + 6 × 6
       ↑ do this FIRST (multiplication outranks addition)
-13 + 36
    ↑ now add -- adding a positive to a negative moves RIGHT along the number line
= 23
```
A common wrong turn is reading it left-to-right as (-13 + 6) × 6. The leading minus does
not change the priority order; it only makes the first term negative.
