---
template_id: pattern_read_then_question
purpose: Interaction pattern — present a short grounded passage, then ask a checking question. Best for concept introduction / comprehension (SPEC §12).
fsm_state: PRESENT (pattern = read-then-question)
version: 1b5f70e4bb39
---
The child is learning: {{concept}}.
{{visual_scaffold}}

Step 1 — Present.
Using only the grounded reference text you were given, write a SHORT explanation of
{{concept}} for {{learner_register}}. Use at most 3–4 simple sentences. Use a concrete,
everyday example if it helps. Do not introduce ideas beyond {{concept}}.

Step 2 — Ask.
Then ask ONE question that checks whether the child understood the idea you just explained.
- The question must be answerable from the explanation.
- It must have a single checkable answer of type {{answer_type}} (one of: int, fraction, mc4).
- Do not ask the child to simply repeat your words back. Ask them to USE the idea.

Output only: the short explanation, then the question. Nothing else.
