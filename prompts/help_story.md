---
template_id: help_story
purpose: Help re-explanation as a short STORY; simple, age-framed, worked to the answer, no trailing question — the FSM presents the re-check (SPEC §13.2).
fsm_state: HELP_REEXPLAIN (modality = story)
version: bdc8c67b16c1
---
You are explaining to a child about 8-9 years old — use very simple words a young child knows.

The child needs help with this problem:

{{question}}

Be warm and reassuring — they may be confused or have just answered it wrong.

Re-explain {{concept}} as a cheerful STORY (two friendly characters share something) — however long the story needs to be to make it clear, nothing scary.

Show the method by working this solved example through to its final answer: {{worked_example}} — finish it, show the final number.

Use as many steps as needed to make it completely clear — do NOT cut steps short for brevity. Use one or two friendly emojis. Do NOT restate their question, do NOT ask the child anything, and do NOT end with a question or a fill-in-the-blank (no '... = ?'). Output ONLY the explanation.

If the child was already given an explanation before, it is shown here — use a DIFFERENT example and different wording than it this time:
{{previous_explanation}}
