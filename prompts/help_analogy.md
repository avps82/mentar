---
template_id: help_analogy
purpose: Help re-explanation by ANALOGY (mapping the idea to something familiar), then a transfer re-check (SPEC §13.2).
fsm_state: HELP_REEXPLAIN (modality = analogy)
version: edda40b1f122
---
The child pressed Help on: {{concept}}. They are confused; be reassuring.

Re-explain {{concept}} using an ANALOGY: map the idea onto something the child already
knows well (sharing a pizza, splitting a team, parts of an hour, slices of a day). Make the
mapping clear — say which part of the analogy matches which part of the maths. Use
{{worked_example}} to anchor the analogy if it fits. A few short sentences.

Do not repeat your earlier wording; change the REPRESENTATION, not just the words. Keep the
analogy simple and age-appropriate; do not stretch it past where it stays true.

Then ask ONE re-check question that tests TRANSFER, not memory: apply the same idea to a
DIFFERENT case with a single checkable answer of type {{answer_type}} (int, fraction, or
mc4). Output only the analogy explanation and the re-check question.
