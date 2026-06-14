---
template_id: help_concrete
purpose: Help re-explanation in the CONCRETE representation (real objects/actions), then a transfer re-check (SPEC §13.2).
fsm_state: HELP_REEXPLAIN (modality = concrete)
version: bf2c82082cf1
---
The child pressed Help on: {{concept}}. They are confused; be reassuring.

Re-explain {{concept}} using CONCRETE, hands-on objects: pouring water between cups,
breaking a chocolate bar, sharing apples between friends, folding a strip of paper. Make it
something the child could actually do with their hands. Use {{worked_example}} as the
situation if it fits. A few short sentences.

Do not repeat your earlier wording; change the REPRESENTATION, not just the words.

Then ask ONE re-check question that tests TRANSFER, not memory: change the objects or the
numbers from the example you just used, with a single checkable answer of type
{{answer_type}} (int, fraction, or mc4). Output only the concrete explanation and the
re-check question.
