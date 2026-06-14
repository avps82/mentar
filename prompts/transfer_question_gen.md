---
template_id: transfer_question_gen
purpose: Generate a NEW-surface transfer question (with answer + answer_type) from a concept and a worked example. Used for re-checks and proactive probes (SPEC §13.2, §14).
fsm_state: HELP_RECHECK / PROBE_PRESENT (transfer-question generation)
version: d1ea720661c9
---
Concept: {{concept}}
Worked example already shown to the child: {{worked_example}}

Produce ONE new question that tests whether the child can TRANSFER the idea — not whether
they can repeat the worked example.

Rules:
- Change the SURFACE: use different numbers, a different everyday context, or a different
  shape/object from the worked example. The underlying idea must stay {{concept}}.
- Keep it Year-4 appropriate: small numbers, one step, no concept beyond {{concept}}.
- It must have a single, unambiguous, checkable answer.
- Do NOT reuse the same numbers or the same story as the worked example.

Return STRICT JSON only, no other text:
{"question": "<the question text>", "answer": "<the correct answer>", "answer_type": "<int|fraction|mc4>"}
For answer_type "mc4", include the four options inside the question text and make "answer"
the correct option's letter (A–D).
