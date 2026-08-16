# DESIGN.md — Mentar

Mentar's design system, written for an AI coding agent to follow. Everything here
is enforced by tests; where it is, the test is named. If this file and the code
disagree, the code and its tests win — and this file is the bug.

**Audience:** a child (ages ~6–18, largest share 16–18) and the parent beside them.
Calm, legible, unhurried. Nothing that rewards speed, nothing that gamifies being
wrong.

## Hard constraints (not preferences)

- **No npm, no build step, no CDN, no framework.** Flask + Jinja2 + htmx + vanilla
  JS. One stylesheet, one vendored `htmx.min.js`. There is no `package.json` and
  there should not be one.
- **U-80: offline-absolute — zero non-localhost requests.** This is a product
  requirement of a local-first child tutor, not a performance choice. It is why
  browser `SpeechRecognition` was rejected (it uploads audio) and why fonts are
  system stacks rather than downloads.
- **Themes may recolour. Themes may never move things.** `--radius`, `--font` and
  `--font-mono` are STRUCTURAL and defined once in `:root`. If a theme could
  resize or reflow, every future layout fix becomes N-themes wide.

## Colour tokens

20 thematic tokens. Every theme must define all 20 and no others; structural
tokens must appear only in `:root`. Gated by
`tests/web/test_theme_tokens.py::test_every_theme_defines_exactly_the_thematic_tokens`
and `::test_only_root_defines_structural_tokens`.

| Token | Light | Dark |
|---|---|---|
| `--accent` | `#FF7F50` | `#FF9776` |
| `--bg` | `#F6F8FB` | `#16202A` |
| `--border` | `#E4E7EB` | `#2D3946` |
| `--danger` | `#E53935` | `#FF6B6B` |
| `--danger-bg` | `#FDE8E8` | `#3A2323` |
| `--learning` | `#FFB300` | `#FFC857` |
| `--mastered` | `#2F8F9D` | `#5FC9D6` |
| `--not-started` | `#E3E6EA` | `#3A4550` |
| `--on-accent` | `#26303A` | `#16202A` |
| `--on-danger` | `#FFFFFF` | `#16202A` |
| `--on-primary` | `#FFFFFF` | `#16202A` |
| `--primary` | `#2F8F9D` | `#5FC9D6` |
| `--primary-strong` | `#21707C` | `#7FDBE6` |
| `--shadow` | `0 1px 2px rgba(30, 40, 50, 0.06), 0 6px 16p...` | `0 1px 2px rgba(0, 0, 0, 0.3), 0 6px 18px rg...` |
| `--shadow-hover` | `0 2px 4px rgba(30, 40, 50, 0.08), 0 12px 28...` | `0 2px 4px rgba(0, 0, 0, 0.35), 0 12px 30px ...` |
| `--surface` | `#FFFFFF` | `#1E2A36` |
| `--text` | `#26303A` | `#E8EDF0` |
| `--text-muted` | `#6B7580` | `#9AA7B2` |
| `--warn-bg` | `#FFF3CD` | `#3A3220` |
| `--warn-border` | `#E0A800` | `#C79A2E` |

**Six themes ship**, not two: `light` (`:root`), `dark`, and the named
child-facing themes `ocean`, `space`, `forest`, `sunshine`. Each is exactly one
`[data-theme]` block redefining all 20 thematic tokens — nothing else. The table
above shows light/dark; read `style.css` for the rest. Every palette was chosen by
running the contrast maths, not by eye, and `sunshine` had to be re-picked after a
LOOK caught two near-identical reds (accent vs danger, 0.051 luminance apart) that
the maths passed.

Structural, never themed: `--radius: 14px`, `--font` (system UI stack),
`--font-mono` (`ui-monospace, "SF Mono", …`).

**Never hardcode a colour.** Every value above is a `var(--token)` at the point of
use. Colour tokens must be plain six-digit hex
(`::test_colour_tokens_are_plain_six_digit_hex`).

## Contrast floors

Enforced per theme with real WCAG maths, whose implementation is itself checked
against known values (`::test_contrast_maths_matches_known_wcag_values`):

| Pair | Floor | Why |
|---|---|---|
| `--text` on `--bg` | 7.0:1 | body text on the page |
| `--text` on `--surface` | 7.0:1 | body text on cards |
| `--text-muted` on `--surface` | 4.5:1 | muted hints on cards |
| `--primary-strong` on `--surface` | 4.5:1 | links / progress text on cards |
| `--primary-strong` on `--bg` | 4.5:1 | links on the page |
| `--on-primary` on `--primary` | 3.0:1 | .btn label |
| `--on-accent` on `--accent` | 3.0:1 | .btn-accent label |
| `--on-danger` on `--danger` | 3.0:1 | .btn-danger label |
| `--primary` on `--bg` | 3.0:1 | brand wordmark + hover borders on the page |

Three separate label inks (`--on-primary`, `--on-accent`, `--on-danger`) exist
because one ink cannot pass on all three backgrounds within a theme: white
measured 2.50:1 on light `--accent`. Darkening the backgrounds instead was
measured and rejected — `--primary` doubles as the wordmark colour, and a
dark-mode value that fixes the button drops the wordmark to 2.77:1.

## Type and surfaces

- Body text `1rem`; the feedback bubble is `1.05rem`. If you add a second text
  block to a bubble, it must match — a card at `1rem` beside prose at `1.05rem`
  was a reported bug.
- **Monospace is a surface, not a font choice.** `.steps-pre` (computed step
  grids and method cards) and `.ascii-art` (fenced diagrams) share one
  "diagram box" look: `--font-mono`, `--surface` background, `--border`, `--radius`.
- Radius `--radius` everywhere. Shadows are layered (a tight contact shadow plus
  a soft ambient one), never a flat grey outline.

## The rendering split — computed content vs model prose

Two paths that must never merge:

- **Model prose** (Help explanations, feedback) goes through
  `_render_markdown_lite()`: HTML-escape first, then insert only
  `<strong> <em> <ul> <li> <pre>`. It exists because untrusted text is reaching a
  child's screen.
- **Computed content** (step grids, method cards, ASCII diagrams) renders as
  `<pre class="steps-pre">` and bypasses markdown-lite entirely — it was never
  model output.

Adding a new computed visual? Reuse the `steps-pre` line convention
(`{"text": ..., "is_annotation": bool}`). Do not invent a third path.

## Component conventions

- **Feedback bubble** (`.feedback`) is a flex row that wraps. `.msg-text` carries
  `flex: 1`, so anything meant to sit BELOW it needs `flex-basis: 100%` — that is
  why `.steps-pre` and `.msg-tail` set it. A second `.msg-text` without it lands
  beside the first.
- **Explain card order** is lead-in → worked-example card → "Now you try it! ✏️"
  → Explain more. The card is how it's solved, so the call to action follows it.
- **Every explain card ends by naming the answer** (`Answer: …`), before any
  appended picture. With sentence-shaped options, "the bit after the arrow" is not
  a readable answer. Gated by `tests/engine/test_card_answer_line.py`.
- **A picture beside a computed card must be computed too.** Authored scaffolds in
  `curriculum/visual_scaffolds/` are instructions to the model, so their numbers
  are placeholders — showing one verbatim put a place-value table reading 3|5|2
  under a question about 463. A scaffold diagram is shown only if it declares
  itself a generic reference key (` ```key `) or contains no numbers.

## Guardrails — each one shipped as a bug

1. `background-clip: text` + `color: transparent` on a container holding an emoji
   strips the emoji's colour layers in WebKit/Blink. Scope gradient text to a
   span around the TEXT ONLY (`.brand-text` vs `.brand-emoji`).
2. Never sort "looks numeric" strings lexicographically — `"Year 10" < "Year 2"`.
   Use `_grade_sort_key()`.
3. A GET route revisitable after a flow ended needs its own terminal-state guard,
   not just the transition that ended it.
4. A rendered visual is verified by RENDERING it. SVG `<marker>` scales with
   `stroke-width` (`markerUnits="userSpaceOnUse"`); a `--` inside an XML comment
   silently kills the parse. Geometry needs a real browser
   (`tests/web/test_browser_ui.py`, headless Chromium over CDP — no Playwright,
   no npm).
5. htmx and non-JS paths render the same template with the same data. `/answer`
   branches on `HX-Request` for HOW to respond, never WHAT to compute.

## Accessibility

- Respect `prefersReducedMotion`; the idle nudge pulses twice and stops.
- Every bubble and question carries a read-aloud control (`tts.js` reads
  `.msg-text` and `.steps-pre` inside `.feedback`).
- Answer inputs use the native widget for their type (`type="number"` for ints)
  as defence in depth — the real boundary stays server-side.
- Never rely on colour alone: mastery states pair `--mastered`/`--learning`/
  `--not-started` with text.
