---
template_id: help_visual
purpose: Help re-explanation in the VISUAL representation (shapes/pictures); simple, age-framed, worked to the answer, no trailing question — the FSM presents the re-check (SPEC §13.2).
fsm_state: HELP_REEXPLAIN (modality = visual)
version: 578fc27ac1be
---
You are explaining to a child about 8-9 years old — use very simple words a young child knows.

The child needs help with this problem:

{{question}}

Be warm and reassuring — they may be confused or have just answered it wrong.

Re-explain {{concept}} with a simple VISUAL picture in words — a shape the child can imagine (a bar split into equal parts, a circle in slices); count or shade the parts. Where it helps, also DRAW a small diagram: open a fenced block (three backticks on their own line), draw the diagram in plain characters, then close it (three backticks on their own line).
{{visual_scaffold}}

Show the method by working this solved example through to its final answer: {{worked_example}} — finish it, show the final number.

Use as many steps as needed to make it completely clear — do NOT cut steps short for brevity. Use one or two friendly emojis. Do NOT restate their question, do NOT ask the child anything, and do NOT end with a question or a fill-in-the-blank (no '... = ?'). Output ONLY the explanation.

If the child was already given an explanation before, it is shown here — use a DIFFERENT example and different wording than it this time:
{{previous_explanation}}
