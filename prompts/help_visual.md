---
template_id: help_visual
purpose: Help re-explanation in the VISUAL representation (shapes/pictures), then a transfer re-check. Triggered when the child presses Help (SPEC §13.2).
fsm_state: HELP_REEXPLAIN (modality = visual)
version: 721efd007401
---
The child pressed Help on: {{concept}}. They are confused; be reassuring.

Re-explain {{concept}} using a VISUAL picture in words: describe shapes the child can
imagine or draw — a rectangle split into equal parts, a circle cut into slices, a bar
divided into pieces. Shade or count the parts to make the idea visible. Use the worked
example {{worked_example}} as the picture if it fits. Keep it to a few short sentences.

Do not repeat your earlier wording; change the REPRESENTATION, not just the words. Do NOT merely restate, reword, or re-ask the question — restating is not help. First give the child a concrete next step they can act on: name the very first thing to do, and show that step worked through on the example so they see HOW to begin, not just what to find.

Then ask ONE re-check question that tests TRANSFER, not memory: use DIFFERENT numbers or a
DIFFERENT shape from the picture you just drew, with a single checkable answer of type
{{answer_type}} (int, fraction, or mc4). Output only the visual explanation and the
re-check question.
