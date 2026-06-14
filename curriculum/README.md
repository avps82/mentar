# Curriculum Templates

Templates are Markdown files that define what a child at a given **country + year/grade level** should be learning. They are **guidelines**, not scripts. The dialogue framework uses them to:

- Keep sessions on-topic for the child's school level
- Calibrate language complexity
- Redirect off-topic or out-of-scope questions

---

## Structure

```
curriculum/templates/
├── au/          # Australia (Australian Curriculum)
├── in/          # India (CBSE / NCERT)
├── uk/          # England (National Curriculum)
└── us/          # US (Common Core / state standards)
```

Year-level files within each folder: `year-1.md`, `year-2.md`, ... `year-12.md` (or equivalent grade naming for the country).

---

## Adding a new curriculum

1. Copy `_template.md` to `templates/<country-code>/year-<N>.md`
2. Fill in the subjects, vocabulary guidance, and interaction notes
3. Open a PR

You can add a new country folder at any time. The system is deliberately open for community extension.

---

## Scope

Templates are intentionally lightweight. They capture:
- Core topics per subject at this year level
- Vocabulary / language complexity guidance
- What's out of scope (to redirect gracefully)

They do NOT try to be complete textbooks. The LLM fills in subject-matter knowledge; the template scopes and calibrates the dialogue.
