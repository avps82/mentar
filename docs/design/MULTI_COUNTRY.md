---
title: "Multi-Country Curriculum Platform — Design"
version: v0.3
status: "Design draft — NOT ratified. No code changes implied by this doc until maintainer sign-off."
last-updated: 2026-07-11
owner: Opus (drafted) / maintainer (ratification pending)
sources: "PHASE0_STATUS.md backlog row (2026-07-11, ratified strategic goal); curriculum/templates/AU/*.md; engine/curriculum.py; engine/item_sources.py; docs/CONTENT_LICENSES.md; REMAINDER_PLAN.md R6.2"
---

# Multi-Country Curriculum Platform — Design

**Scope of this doc.** Design only — no implementation. Maintainer ratified the *goal*
("always the goal... big, yes, but the goal") but asked for a dedicated pass before any
spec. This is that pass. Decisions taken via AskUserQuestion (2026-07-11): content-download
is designed here but not built; R6.2 (skill display-name unification) is resolved here (§5)
and built this same wave as the mechanical outcome, since naming IS a piece of curriculum
data-shape design, not a separate concern.

---

## 1. What already generalizes vs what's AU-specific

The AU templates (`curriculum/templates/AU/year3_maths.md`, `year4_maths.md`) were authored
without a multi-country abstraction in mind, but the shape that exists today turns out to
mostly hold up:

**Already country-agnostic (built for R3.1, reused as-is):**
- `curriculum/templates/<DIR>/*.md` directory-as-namespace convention
  (`engine/curriculum.py::derive_subject_key`) — any directory auto-prefixes its templates'
  session keys. `_pilot/` is the one deliberate exception (legacy, unprefixed). §2/§2b refine
  this to `country_authority` naming plus a year sub-folder for content versioning.
- Front-matter catalog fields (`label`, `icon`, `description`, `year_level`, `subject`) — the
  web picker already renders off these, generically, for every template regardless of country.
- `item_source:` naming + `engine/item_sources.py`'s registry — a template names its item
  generator by string; the registry resolves it. Adding a country's templates never touches
  this file unless it also ships new parametric generators.
- The node schema itself: `id`, `label`, `prereqs`, `grounding`, `transfer_seeds`, `verifier`,
  `bkt_priors` — nothing here is AU-shaped. It's a generic mastery-graph node.

**Currently AU-specific, hardcoded, or implicit (the parts a second country will hit):**
- `curriculum_standard: "ACARA v9 (AC9M3 Number)"` — free-text today, which is actually
  fine (see §2), but nothing validates its shape, and no code reads it structurally yet.
- Content-description codes (`AC9M3N01`) live only as trailing YAML comments on each node
  (`year3_maths.md:29`) — not a structured field. This is good practice already: they're
  human-alignment references, not something code depends on. Worth keeping this way rather
  than promoting to a real field — see §2's "codes are optional metadata" rule.
- `country: AU` front-matter field exists but nothing reads it programmatically yet (not the
  picker, not the registry) — it's documentation-only today. A second country doesn't need
  it to become functional; it only needs to *not lie*.
- Licence clearance: `docs/CONTENT_LICENSES.md` §2b covers ACARA specifically, authored as a
  one-off table row, not a template other countries automatically inherit protection from.
  This is the sharpest gap — see §3.
- `AU_YEAR3_GENERATORS`/`AU_YEAR4_GENERATORS` in `engine/au_items.py` are AU-numbered
  (fact tables, number ranges) but structurally identical in *shape* to
  `ARITHMETIC_GENERATORS`/`SCIENCE_GENERATORS` in `engine/itemgen.py` — the `GenFn` contract
  itself is already country-agnostic; only the fact data inside AU's generators is AU-tuned.

**Verdict:** the schema doesn't need a redesign. It needs three additions (codes-optional
validation, a licence-checklist *process*, and the naming fix in §5) plus discipline to keep
future country-specific numbering/coding out of code and in template data.

---

## 2. Paper validation — stress-testing the schema against four other systems

No content is authored for any of these. This is a dry run: does the existing node/front-matter
shape survive contact, or does something break?

| System | Level naming | Code scheme | How it maps onto the existing schema | Where it bends the abstraction |
|---|---|---|---|---|
| **US Common Core** | "Grade 3", "Grade 4"... | Highly structured: `CCSS.MATH.CONTENT.3.NBT.A.1` | `year_level: "Grade 3"` (free text, already works); code goes in the same trailing-comment position ACARA codes use today | None — best-case fit. Codes are the most code-shaped of any system here, so if this doesn't force a change, nothing will. |
| **UK National Curriculum** | "Key Stage 2, Year 4" — a two-level hierarchy, not a flat year number | DfE reference codes exist but are less universally quoted than CCSS/ACARA | `year_level: "Key Stage 2, Year 4"` — free text absorbs the two-level naming fine, since nothing parses `year_level` structurally today (it's a display string) | **Confirms** `year_level` must stay a free-text display field forever, never parsed into an integer or split into (stage, year) — some countries genuinely have compound level names. |
| **Singapore MOE** | "Primary 3" | No public standards-code scheme comparable to CCSS/ACARA — syllabus documents are prose, not enumerated codes | `curriculum_standard: "MOE Mathematics Syllabus (Primary)"` (free text); simply omit the per-node code comment | **Confirms** the content-description code must be OPTIONAL per node, not a required field with a fallback placeholder — some countries structurally don't have one, and inventing a fake code would be worse than having none. |
| **India NCERT/CBSE/ICSE/state boards** | "Class 3" (NCERT) — but ICSE, CBSE, and each state board can diverge on pacing/scope for the same class number | NCERT has learning outcome codes; CBSE/ICSE reference NCERT but aren't identical; state boards vary further | `country: IN`, but this is the case that breaks a hidden assumption | **Confirms** "one curriculum authority per country" cannot be assumed — and India needs a THIRD level for state boards specifically (a category of authority with per-state variants, not a single national body). Confirmed authority list (maintainer, 2026-07-11): `IN_NCERT`, `IN_CBSE`, `IN_ICSE`, and `IN_STATE_BRD_<XX>` per state using its two-letter code (e.g. `IN_STATE_BRD_TN` for Tamil Nadu, `IN_STATE_BRD_KA` for Karnataka) — each a sibling directory, same mechanism `_pilot`/`AU` already use. This is a naming-convention decision, not a schema change: the existing `<DIR>/*.md` mechanism already supports arbitrary directory names: no code change needed, just don't assume `country` alone is a unique key when picking a directory name. |

**Net result of the stress test:** the node schema requires **zero changes**. Two working
conventions get *confirmed* (not invented): (a) `year_level` and `curriculum_standard` are
always free-text display strings, never parsed; (b) per-node codes are optional, absent
entirely for Singapore-shaped systems. Two conventions get *added*: (c) the directory
namespace key is `country_authority` (e.g. `AU_ACARA`, `IN_NCERT`, `IN_CBSE`), not country
alone — clean even for single-authority countries, groups by country in a directory
listing, and a country with multiple curriculum bodies gets multiple sibling directories
the same way `_pilot` and `AU` already coexist; (d) each authority directory gets a
publication-**year sub-folder** (§2b) so a curriculum revision never disrupts a family
already partway through the previous version.

---

## 2b. Curriculum-year versioning — a sub-folder per publication year (maintainer ask, 2026-07-11)

Curriculum authorities revise their content periodically (ACARA v9 today, a v10 someday;
Common Core has had multiple revisions; NCERT/CBSE syllabi get periodic refreshes). The
platform should always serve the **latest** version by default, without either (a) silently
mutating an in-progress child's session onto different content mid-year, or (b) requiring a
manual code change every time an authority publishes an update.

**Layout:** `curriculum/templates/<country_authority>/<year>/*.md` — e.g.
`curriculum/templates/AU_ACARA/2023/year3_maths.md`. The year is the CURRICULUM
**publication** year (when this revision of the standard was issued), not a school year and
not the content-authoring date — same idea as `khanacademy_en_all_2023-03.zim`'s naming.

**"Latest" resolution — an explicit pointer file, not a symlink or auto-detected max().**
`curriculum/templates/AU_ACARA/LATEST` contains a single line, the year to serve by default
(e.g. `2023`). Rejected alternatives and why:
- A symlink (`latest -> 2023/`) is simplest on paper but is genuine cross-platform friction
  for an app that runs on a parent's own Windows/Mac/Linux machine, and this project already
  avoids symlinks elsewhere for exactly that reason.
- Auto-detecting the highest-numbered year folder present means a half-authored future-year
  folder gets served the instant it's added to the repo, before anyone's reviewed it — risky
  for kid-facing content, and silent (no diff shows the behaviour change).
The pointer file is a one-line, diff-reviewable PR when an authority publishes an update
("bump AU/ACARA to 2025") — same diff-reviewable spirit as the rest of this schema (W3.1).

**Critical: the year must NOT leak into the skill_id/session-key namespace.**
`derive_subject_key()` today prefixes by the *immediate parent directory* of the `.md` file
— if the year folder becomes that immediate parent, keys would become `2023_place_value`
instead of `AU_ACARA_place_value`, and worse, if the year DID leak through, bumping the
`LATEST` pointer would silently orphan every child's `skill_state` mastery history for that
country (rows key on `skill_id`, which would now be pointing at a different, dated prefix).
`derive_subject_key()` needs a small rework to resolve the **authority** directory (one level
above the year folder), not simply `path.parent.name`, so the year folder stays a pure
authoring/versioning device — invisible to everything at runtime. A genuinely restructured
curriculum (not just a refreshed edition of the same standard) is a different, deliberate
content decision that SHOULD get new node ids on purpose — that's an authoring choice, not
something a year-folder bump should trigger by accident.

**Resolved (maintainer, 2026-07-11): auto-follow by default, gated at a parent checkpoint,
never mid-session.** A `LATEST` bump is only ever checked at a NEW session's start, never
applied mid-session. If it changed since the learner's last session on that subject, a
one-time notice appears on the **parent** dashboard (never the child's screen) —
"ACARA updated this curriculum (2023 → 2025)" — with an accept-now / stay-on-2023-for-now
choice, reusing the EXISTING `SessionController.parent_acknowledge()` control-plane already
built for the escalation-freeze resume flow (no new mechanism). If the parent doesn't act,
the child just keeps progressing on their current version — nothing silently drifts, but
nothing is blocked either. Rationale for defaulting to auto-follow rather than requiring
opt-in: a mid-revision curriculum swap is rare enough ("far and apart") that the checkpoint
notice is sufficient safety margin without adding friction to the common case.

**Migration mapping — deliberately NOT a general mechanism.** The common case (a
wording/exercise refresh, no conceptual restructure) needs zero mapping: node ids stay the
same, mastery carries forward for free. The rare case (an authority genuinely merges/
splits/renames concepts) is exactly the case flagged above as deserving new ids on purpose —
rare and manual enough that whoever authors the update can drop in a small OPTIONAL mapping
file (old_id → new_id) at that moment, only for the ids that actually changed. Anything
unmapped simply goes dormant in `skill_state`, never deleted — same preserve-on-delete
default as §4's content-download semantics. No runtime migration engine needed.

---

## 3. Licence discipline — a per-country/per-source checklist

`docs/CONTENT_LICENSES.md` §2b currently has exactly one row (ACARA). The manual process that
produced it (verify the licence live on the authority's own site, record clause + version,
flag any restrictive sub-scopes) worked, but existed only as narrative — not a checklist
future country onboarding is forced to repeat.

**Add to `docs/CONTENT_LICENSES.md`, before any second country's templates are authored:**
a short "Onboarding a new curriculum-alignment source" checklist, modeled directly on how
§2b's ACARA row and Khan Academy's grounding clearance were actually done:
1. Find the authority's own stated licence (not a secondary summary) — record source URL +
   date checked, same as §2b's "verified against the site's copyright/terms page 2026-07-10".
2. Identify what's covered vs excluded — ACARA's row already models this (core content CC BY
   4.0, but Literacy Progressions carved out as CC BY-NC 4.0, "Excluded Materials" flagged
   view-only). Every new authority needs the same excluded-subset check, not a blanket
   assumption that "the curriculum" means uniformly one licence.
3. Record whether alignment is code-only (no descriptor text reproduced — the pattern ACARA
   and this doc's §2 both rely on) or whether any descriptor/outcome text will be quoted
   verbatim (triggers attribution/share-alike obligations per source licence).
4. **No shortcut rule, stated explicitly and permanently:** "this is a government/public
   curriculum" is never sufficient justification on its own — CC BY 4.0 (ACARA) and
   CC BY-NC 4.0 (ACARA's own Literacy Progressions, a sibling document from the *same*
   authority) prove licence terms vary even within one authority's own publications.

This checklist is the entire deliverable of §3 — it's process, not code, and it's cheap to
add to CONTENT_LICENSES.md directly whenever the maintainer ratifies this doc.

---

## 4. Content-download — design only, not built this wave

**Why this exists at all:** R3.1 already solved "add a template" (drop a `.md` file into
`curriculum/templates/`, auto-discovered). Content-download solves a different problem: a
parent who has never touched a filesystem needs to *get* that file onto their machine, from
inside the app. It is the one place multi-country necessarily touches U-80 (offline-only,
zero non-localhost requests) — the single sanctioned exception, not a general relaxation.

**Source & hosting.** Recommend a static manifest + package files hosted from the Mentar
project's own GitHub releases (or GitHub Pages) — no new backend service to build/operate,
consistent with the project's "OSS repo, no hosted infra" posture elsewhere in the docs. A
manifest JSON lists available packs (country, authority, year/grade, subject, licence tag,
download URL, checksum); the app fetches the manifest, then a chosen pack, verifies the
checksum, and unpacks into `curriculum/templates/<DIR>/`.

**Package format.** A pack = one directory's worth of `.md` templates (matching what
already lives in `curriculum/templates/<DIR>/` today) plus a `manifest.json` entry recording
licence metadata (feeds directly into the §3 checklist — a pack literally cannot ship
without its licence row filled in). Reuses the existing template format exactly — no new
schema, no new loader code, `engine/curriculum.py` doesn't change at all for this feature.

**Fetch-path security (the actual new risk surface).** This is the one place external
network content enters an otherwise fully local app, so it needs its own review before
building, not folded into a general feature review:
- HTTPS-only, pinned to the Mentar project's own release host — never an arbitrary
  user-supplied URL.
- Checksum (sha256) verification against the signed manifest before any file is written to
  disk; reject on mismatch, never partially install.
- Downloaded content is data (Markdown + YAML front matter), not code — no `eval`, no
  executable payload, consistent with how templates are already just parsed by
  `yaml.safe_load` today. This materially limits blast radius even if the manifest were
  somehow compromised: worst case is bad/wrong curriculum content, not code execution.
- Explicit user-initiated action only (a button press), never a background auto-fetch — U-80
  stays true for every OTHER code path in the app; this is the one opt-in exception, not a
  precedent for loosening it elsewhere.
- Recommend: log/display the pack's licence + source to the parent before confirming
  install (surfaces the §3 checklist data at the point of consequence, not just in a repo doc
  no parent will ever open).

**Delete/uninstall semantics.** Recommend: deleting a pack removes its `.md` templates
(so it stops appearing in the picker) but **preserves** the child's existing `skill_state`
mastery rows for that pack's node ids — same reasoning as any other data-retention default
in this app (mastery history is the valuable, hard-to-regenerate artifact; content files are
cheaply re-downloadable). A "permanently erase this child's history for this pack too"
option can be a separate, explicit, harder-to-reach action — not the default single click.

**Explicitly not designed here (next pass, if this gets built):** manifest signing/rotation
mechanics, version-upgrade handling for an already-installed pack, and UI copy/flow —
deferred because none of it is needed to evaluate whether the download mechanism itself is
soundly shaped, which is this section's only job.

---

## 5. R6.2 resolution — one naming convention, decided here, built this wave

**The bug this fixes:** `curriculum[node_id]["concept"]` is the one correct display-name
source (`engine/curriculum.py:85`, populated from each node's YAML `label:` field), but three
of four rendering sites never use it — `progress.html`'s star-cards and `learner.html`'s
mastery bar do `skill_id | replace("_"," ") | title` (produces "Au3 Place Value" — the `au3_`
namespace prefix, added purely for cross-curriculum collision-safety in R3.1, leaks straight
into what a child/parent reads); `parent.html` shows the raw `skill_id` with no transform at
all; `done.html` repeats the naive replace+title. This is exactly a multi-country problem in
miniature: every new country's namespace prefix (`us_`, `uk_`, `sg_`, `in-ncert_`...) would
independently reproduce the same "Au3 Place Value"-shaped bug at every one of these three
sites, forever, unless the id→name lookup is unified once.

**Decisions (answering REMAINDER_PLAN.md R6.2's four open questions):**

(a) **Rename `"concept"` → `"label"`** in the dict `load_curriculum` returns
(`engine/curriculum.py:85`) — matches the YAML source field name exactly (`node.get("label",
nid)`), removing the one internal naming mismatch that existed before any of this. Internal
rename only; no schema/migration note needed in `docs/PHASE0.md` W3.1 beyond noting the dict
key match now (nothing persisted to disk changes — `skill_state` rows still key on
`skill_id`, never on the label).

(b) **Routes attach `display_name`, templates never derive names from ids.** Every
skill/answer dict a Flask route in `web/app.py` builds for a template gets a `display_name`
key set from `curriculum[skill_id]["label"]` (falling back to the raw id only if a skill_id
somehow isn't in the loaded curriculum — should not happen in practice, but a KeyError here
is worse than a rare literal-id fallback). This is a small inline addition at each of the
handful of call sites building those dicts today, not a new module — one helper function
(e.g. `_display_name(curriculum, skill_id)`) is enough; no new abstraction layer, no
registry. Templates (`progress.html`, `learner.html`, `parent.html`, `done.html`) then render
`{{ item.display_name }}` uniformly and stop doing any id-transformation of their own.

(c) **Scope: templates only, this pass.** No CLI output or audit surface currently renders
skill ids to a human today (confirmed by the grep the R6.2 spec already did) — nothing else
needs fixing in this wave. If a future CLI/audit surface is added, it should call the same
`_display_name` helper rather than reinvent a fifth strategy — noted here so it's discoverable,
not built speculatively now.

(d) **The convention, stated once:** *"skill_id is a machine key, never shown to a human;
every human-facing surface renders `display_name`, sourced once from the template's `label:`
field, computed by the route, never re-derived in a template."* This sentence is the
convention worth writing down — added as a one-line comment at `engine/curriculum.py`'s
`load_curriculum` and referenced from any future curriculum-authoring guidance
(`curriculum/README.md`), so a new country's templates don't reintroduce the drift this
section just closed out.

**What Phase C (build) does with this:** rename the dict key, add the one small
`_display_name` helper + its call sites in `web/app.py`, fix the 3 wrong template sites to
render `display_name` only. Tests assert every rendered name for the AU Year 3 template
equals the YAML label ("Place value to 999") — never "Au3 Place Value", never raw
`au3_place_value` — across all four surfaces.

---

## 6. Summary / what's decided vs what's still open

**Decided by this doc (ready to build/act on once ratified):**
- Schema needs no changes; `year_level`/`curriculum_standard` stay free-text forever, codes
  stay optional per-node comments.
- Directory namespace = `country_authority` (e.g. `AU_ACARA`, `IN_NCERT`, `IN_CBSE`) — clean
  even for single-authority countries, groups by country, multi-authority countries (India)
  get sibling directories, same mechanism `_pilot`/`AU` already use.
- A publication-year sub-folder per authority (§2b), resolved via an explicit `LATEST`
  pointer file (not a symlink, not auto-max-detection) — a curriculum revision becomes a
  one-line reviewable PR, never an implicit behaviour change. The year must stay OUT of the
  skill_id/session-key namespace (`derive_subject_key()` needs a small rework to resolve the
  authority directory, not the immediate parent) so a revision bump can never silently orphan
  a child's mastery history.
- A licence-onboarding checklist to add to `CONTENT_LICENSES.md` before any second country's
  content is authored.
- Content-download's shape (manifest + static release hosting + pack-is-data-not-code +
  explicit user action + preserve-mastery-on-delete) — design only, not built.
- R6.2's naming convention (§5) — this one ships as code this same wave.
- India's confirmed authority list: `IN_NCERT`, `IN_CBSE`, `IN_ICSE`,
  `IN_STATE_BRD_<XX>` per state (two-letter code, e.g. `IN_STATE_BRD_TN` for Tamil Nadu) —
  each a sibling directory, no schema change needed.
- `LATEST`-bump handling (§2b): auto-follow by default, gated at a parent-dashboard
  checkpoint (reusing `parent_acknowledge()`), never mid-session. No general migration
  engine — an optional, sparse old_id→new_id mapping file only for the rare genuine
  restructure case.
- **Second country to build: India** (maintainer, 2026-07-11) — deliberately picked as the
  harder case (multi-authority + state boards) over Singapore, to stress-test the naming
  convention early rather than defer its hardest edge to later.

**Left open for the maintainer to ratify or push back on:**
- Whether content-download is worth building at all in the near term, or whether "clone the
  repo / drop a file in" remains an acceptable distribution story for longer (it's exactly
  as functional today, just less parent-friendly).
