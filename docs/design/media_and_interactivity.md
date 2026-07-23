---
type: Mentar Design Doc
title: "Media & Interactivity in Mentar — grounding ≠ presentation (decision + scope)"
version: v1.0 (decision)
status: "DECIDED 2026-06-15. Grounding stays text-only (correct). Media/interactivity is a presentation-layer concern → two new post-pilot W-tasks: W6.5 (Mentar-owned manipulatives) + W7.6 (vetted ZIM media serving)."
last-updated: 2026-06-15
owner: Opus
refs: "docs/design/W7_grounding_reader.md, SPEC §15 (RAG), SAFETY §1.5 (grounding-as-data), docs/CONTENT_LICENSES.md (Khan NC), SPEC §24 #18, W6.3 pilot interface"
---

# Media & Interactivity — can Mentar handle video / audio / animation / interactive graphs?

The maintainer's question: ZIM archives can contain video, audio, animations, and even interactive
(JS) widgets — can we handle that? Short answer: the doubt dissolves once **grounding** and
**presentation** are kept separate. They are different layers and must not be conflated.

## The two layers

| Layer | What it is | Media? | Status |
|-------|-----------|--------|--------|
| **Grounding** (`src/mentar/grounding/`) | Feed correct *text* to the local LLM so it doesn't hallucinate (SPEC §15 layer-1 RAG) | **Text only — and that is the correct scope.** A local text LLM cannot consume video/audio. Multimodal grounding is neither needed nor in scope for the fractions pilot. The reader strips HTML to plain text by design. | ✅ built (W7), correct |
| **Presentation** (the pilot web app — W6.3 / Phase-1 UX) | What the **child sees** | This is the *only* place images / animation / interactive graphs belong | media not built |

The "can we handle media?" doubt is a **presentation** question, not a grounding one. Do **not**
make the grounding reader emit media — wrong layer.

## What ZIM can hold vs. what we do

ZIM is a general offline-web container: it can carry images (PNG/WebP/SVG), video (WebM),
audio (Ogg/MP3), animation (GIF/SVG/JS), and JavaScript; Kiwix renders all of it in a browser.
**Media-rich ZIMs exist** — e.g. PhET (interactive HTML5 physics/math sims), Khan Academy
(video), Wikipedia "maxi" (images). Our **pilot** ZIMs are the **`nopic`** (text-only) Vikidia
+ Simple-English-Wikipedia, so there is no media in them to begin with. `libzim` *can* return
any entry's bytes + mimetype, so serving ZIM media is technically feasible — but gated on safety
(below).

## Decisions

1. **Grounding stays text-only.** No change to W7. Correct for a text LLM and the pilot.
2. **Static media *from* a ZIM** (images, later video/audio) is a **presentation** feature →
   **W7.6 (vetted ZIM media serving)**. `libzim` can serve the bytes; the hard part is **child-
   safety vetting** — we must NOT render arbitrary ZIM media/HTML/JS to a child. Requires a
   curated/whitelisted path + a `grounding:`-schema extension for media assets. Post-pilot.
3. **Interactive / user-changeable graphs** (a draggable fraction bar, a pie the child splits)
   → **W6.5 (Mentar-owned manipulatives)**, NOT from ZIM. Two reasons:
   - **Safety:** running a ZIM's embedded JS in a child-facing webview is an unvetted-content /
     injection surface that directly conflicts with our grounding-as-data + child-safety stance.
   - **Pedagogy:** fraction manipulatives are far better as **owned widgets** we generate per
     concept (parameterized by the lesson), not retrieved content.
   PhET-style interactive sims (which *are* ZIM-embedded JS) would fall under W7.6's vetting bar
   if ever adopted — they are not a substitute for owned manipulatives.

## Licensing flag (acted on now)

The maintainer is downloading **Khan Academy** ZIMs. Khan Academy content is **CC BY-NC-SA** — the
**NC (non-commercial)** clause is already logged as a hosted-tier conflict in
`docs/CONTENT_LICENSES.md` / SPEC §24 #18. Fine for **personal/local** use and experimentation;
**not** redistributable in a commercial/hosted edition without permission. Keep Khan out of any
*shipped* content path until that clears. PhET sims are CC BY (more permissive) — better
candidate if interactive content is ever pulled from a ZIM.

## Bottom line

Nothing is boxed-in. Pilot (fractions) needs **text grounding only** — already done. Anything
visual/interactive is a cleanly-separable presentation concern: **W6.5** (owned manipulatives,
the pedagogically right answer) and **W7.6** (vetted ZIM media serving, if/when wanted). Both
post-pilot, neither G0-blocking.
