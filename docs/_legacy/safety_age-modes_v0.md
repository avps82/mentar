# Age Modes

Mentar operates in one of two modes depending on the child's age. The parent configures this during setup.

---

## Under-13 — Parent-mediated mode

A parent or guardian is **in the loop** for all sessions. The child does not have an unsupervised, ongoing conversation with the AI.

Design intent:
- Parent reviews or co-participates in sessions
- Session summaries (local only, not transmitted) are available to the parent
- The dialogue framework prompts for parental involvement at appropriate points
- The AI does not form an ongoing "relationship" with the child independent of parent awareness

Regulatory backing:
- COPPA (US) requires verifiable parental consent for under-13. Local-first + parent-setup removes most operator obligations, but the design still honours the intent.
- UNESCO guidance recommends against unsupervised GenAI conversations for under-13.
- UK Age Appropriate Design Code: best interests of child as primary design lens.

---

## 13+ — Independent with oversight

The child can engage more independently. Parental oversight is available but not mandatory for each session.

Design intent:
- Standard tutoring interaction
- Parent can review session history (local only)
- Safety guardrails still fully apply

---

## Year-level mapping

Curriculum templates are keyed to country + year/grade level, not age directly. The age-mode is set separately during parent setup. The system maps year level to an approximate age range as a guide, but the parent's explicit configuration takes precedence.

Example (approximate):
| Year level | Approx. age | Default mode |
|---|---|---|
| Foundation / Year 1 | 5–6 | Under-13 (parent-mediated) |
| Year 7 | 11–12 | Under-13 (parent-mediated) |
| Year 8 | 12–13 | Under-13 → transition |
| Year 9+ | 13+ | Independent with oversight |

These defaults can be overridden by the parent.

---

## Transition at 13

The age-13 threshold is deliberately chosen to align with:
- COPPA (US) under-13 consent requirement
- UNESCO guidance recommending age-13 minimum for independent GenAI conversations
- GDPR Article 8 digital age of consent (13 as the lowest member-state minimum)
- ChatGPT and most major AI platforms' minimum age

Parents can choose to keep a 13+ child in parent-mediated mode.
