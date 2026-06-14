---
template_id: help_story
purpose: Help re-explanation as a short STORY (narrative with characters), then a transfer re-check (SPEC §13.2).
fsm_state: HELP_REEXPLAIN (modality = story)
version: f406474a04dd
---
The child pressed Help on: {{concept}}. They are confused; be reassuring.

Re-explain {{concept}} as a SHORT STORY: a couple of friendly characters run into a
situation where {{concept}} is the key to solving their everyday problem (sharing snacks at
a party, dividing a treasure, splitting jobs fairly). Keep the story tiny — three or four
sentences — and make the maths idea the turning point. Use {{worked_example}} as the story's
problem if it fits.

Do not repeat your earlier wording; change the REPRESENTATION, not just the words. Keep the
story calm and cheerful; nothing scary or sad.

Then ask ONE re-check question that tests TRANSFER, not memory: a new situation with
DIFFERENT numbers, single checkable answer of type {{answer_type}} (int, fraction, or mc4).
Output only the story and the re-check question.
