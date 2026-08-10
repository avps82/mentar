# Mentar — Prompt Template Registry

Versioned prompt templates loaded by the dialogue controller — **never** hardcoded
strings in `src/` (SPEC §12, §13.2; PHASE0 W6.2; ARCHITECTURE.md). The registry below
is the authoritative list; tests T4.6 (loads-and-versions) and T7.3 (regression-on-change)
gate on it.

## Hashing convention

Each template file has YAML front matter (`---` … `---`) followed by the prompt **body**.
The `version` is:

```
sha256( body_bytes_after_the_closing '---\n' ).hexdigest()[:12]
```

i.e. the hash covers ONLY the body, never the front matter (so the version line cannot
hash itself). The `prompt_ref` stored in `response_log` is `"{template_id}:{version}"`
(schema.sql). Regenerate/verify with `python tools or T4.6`; the same algorithm must
reproduce every hash below or the test FAILS (stale registry).

## Templates (10 files)

| File | template_id | Purpose | version (sha256[:12]) |
|------|-------------|---------|------------------------|
| `help_analogy.md` | `help_analogy` | Help re-explanation by ANALOGY (mapping the idea to something familiar), then a transfe… | `357bbd5127f9` |
| `help_concrete.md` | `help_concrete` | Help re-explanation in the CONCRETE representation (real objects/actions), then a trans… | `618b40f8d01b` |
| `help_elaborate.md` | `help_elaborate` | R12.5 "Explain more" — unpack the SAME explanation one level deeper at the child's requ… | `acb28cea1a3c` |
| `help_formal.md` | `help_formal` | Help re-explanation in the FORMAL representation (symbols/notation/steps), then a trans… | `936b9062ca4d` |
| `help_story.md` | `help_story` | Help re-explanation as a short STORY (narrative with characters), then a transfer re-ch… | `bdc8c67b16c1` |
| `help_visual.md` | `help_visual` | Help re-explanation in the VISUAL representation (shapes/pictures), then a transfer re-… | `578fc27ac1be` |
| `pattern_problem_first.md` | `pattern_problem_first` | Interaction pattern — pose a problem first, then probe the child's reasoning. Best for … | `b045d54ca85f` |
| `pattern_read_then_question.md` | `pattern_read_then_question` | Interaction pattern — present a short grounded passage, then ask a checking question. B… | `4743ea70953b` |
| `pattern_state_and_challenge.md` | `pattern_state_and_challenge` | Interaction pattern — child states what they learned, system gently challenges an assum… | `eb701d1f2cb0` |
| `system_prompt.md` | `system_prompt` | Global system prompt — safety framing, grounding-as-data wrapper, AI transparency, scop… | `ea938ac6c586` |
| `transfer_question_gen.md` | `transfer_question_gen` | Generate a NEW-surface transfer question (with answer + answer_type) from a concept and… | `d1ea720661c9` |

## Coverage (W6.2 acceptance)

- **Interaction patterns ×3** (SPEC §12): read-then-question, problem-first, state-and-challenge.
- **Help modalities ×5** (SPEC §13.2): visual, concrete, analogy, story, formal — each re-explains
  in its representation and ends with a TRANSFER re-check (not echo).
- **Transfer-question generation ×1** (SPEC §13.2, §14): new-surface question + answer + answer_type.
- **System prompt ×1**: safety framing + grounding-as-data wrapper (SAFETY §1.5 / W2.3),
  AI transparency, scope limits, honest deferral.

