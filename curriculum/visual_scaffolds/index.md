---
okf_version: "0.2"
---

# Mentar Visual Scaffolds

Per-topic visual scaffold hints injected into question-generation prompts. Keeps small-model context minimal — only the matched topic file is loaded, not this whole bundle. Each file is a `Mentar Visual Scaffold` concept. At question-generation time the engine keyword-matches the active concept node's label against each scaffold's `topic_keywords` list and injects only the matching file's body into the prompt.

Routing: `topic_keywords` match is substring, case-insensitive, first-match wins. Falls back to no scaffold (plain generation) if no match.

## Subdirectories

* [maths](maths/index.md) — Mathematics visual scaffolds
* [english](english/index.md) — English visual scaffolds
* [science](science/index.md) — Science visual scaffolds
