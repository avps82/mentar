---
okf_version: "0.2"
---

# Mentar Visual Scaffolds

Per-topic visual scaffold hints injected into question-generation prompts. Keeps small-model context minimal — only the matched topic file is loaded, not this whole bundle. Each file is a `Mentar Visual Scaffold` concept. At question-generation time the engine keyword-matches the active concept node's label against each scaffold's `topic_keywords` list and injects only the matching file's body into the prompt.

Routing (`engine/visual_scaffold.py`): a keyword matches the concept node's label on WORD
BOUNDARIES, case-insensitively, also accepting an -s/-es/-ing/-ed suffix on the keyword. That
suffix set is wider than it looks: `mean` matches 'meaning', `count` matches 'counted'. The
file matching the MOST keywords wins. Equal counts break on
CONTAINMENT (a keyword that strictly contains a rival's is a refinement of it, so 'counting by
2s' beats 'counting'), and only then on alphabetical filename order. Falls back to no scaffold
(plain generation) if nothing matches.

Keep keywords SPECIFIC. A short generic keyword silently steals unrelated labels: bare `3d`
sent Year 3 '3D shapes' to a senior 3D-vector-magnitude formula, and bare `moving` sent Year 5
'Moving on a grid' to a moving-average window (both found and fixed 2026-08-22). The coverage
test only asserts that SOME scaffold matches, so a mis-route stays green.

## Subdirectories

* [maths](maths/index.md) — Mathematics visual scaffolds
* [english](english/index.md) — English visual scaffolds
* [science](science/index.md) — Science visual scaffolds
