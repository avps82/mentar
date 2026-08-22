---
type: Mentar Visual Scaffold
title: "Two-Stage Probability — Tree Diagram"
description: "Visual scaffold for two-stage probability: branches, multiplying along a path, adding across paths."
tags: [mathematics, senior, probability, visual-scaffold]
subject: mathematics
timestamp: "2026-08-22T00:00:00Z"
topic_keywords: [two-stage probability, two-stage, two coins, probability with two coins]
---

When writing or explaining this question, use this visual structure:

```key
          stage 1        stage 2      path
                      /-- H          H then H
             /-- H --<
            |         \-- T          H then T
   start --<
            |         /-- H          T then H
             \-- T --<
                      \-- T          T then T
along a path: MULTIPLY     across paths: ADD
```

**Guidelines for the question text:**
- Say what the two stages ARE ("flip, then flip again"), so the child knows
  which branch set is which.
- Split out of `probability.md` on 2026-08-22: that file's first diagram is the
  0-to-1 likelihood SCALE, and a scale was being served to every two-stage
  question -- including the ones its own guidelines said to draw as trees. A
  scale cannot show a path, so it answered a question nobody had asked.
- State whether order matters. "One head and one tail" is two paths; "head then
  tail" is one.
