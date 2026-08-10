---
type: Mentar Audit Doc
title: "Mentar — Content Licence Audit (Pilot Sources)"
version: v0.6
status: "Pilot sources cleared. Country strategy settled: AU=ACARA (CC BY), IN/SG/US = GENERIC packs (no claimed alignment) — US decided 2026-08-11"
last-updated: 2026-07-16
scope: "Phase-0 pilot grounding sources ONLY (W4.1). Not a full content-licensing policy."
sources: "PHASE0.md W4.1; SPEC §18 (content stack), §24 #12; curriculum/templates/_pilot/fractions.md grounding anchors; REMAINDER_PLAN.md B1 (2026-07-05 re-point to Khan Academy)"
---

# Content Licence Audit — Pilot Sources

Audits the licences of the grounding sources used by the Phase-0 fractions pilot, per
**W4.1**. Scope is the pilot only; broader/hosted-tier content licensing is out of scope
and tracked separately (see §3).

> **⚠️ Not legal advice.** Licence identifications below are from each project's stated
> licensing as of 2026-06-14. Verify per source before any non-local or commercial use.

---

## 1. Pilot grounding sources — cleared for local pilot use

The pilot grounds explanations in vetted reference passages (RAG, not recall — SAFETY.md
Layer 6). **As of B1 (2026-07-05), the live pilot template
(`curriculum/templates/_pilot/fractions.md`) anchors all 8 nodes to Khan Academy** — the
originally-intended Vikidia/Simple-WP ZIMs were never present on the real mount
(`/mnt/zim`); see `REMAINDER_PLAN.md` B1 for the full re-point story. Vikidia/Simple-WP stay
listed below as cleared, verified alternates (the reader supports either; a future re-point
back or to another mounted ZIM needs no new licence work):

| Source | Licence | Local pilot use | Attribution / share-alike obligation |
|--------|---------|-----------------|--------------------------------------|
| **Khan Academy** (khanacademy_en_all, ZIM) — **live pilot source** | CC BY-NC-SA (unspecified version on the ZIM; treat as 3.0/4.0-equivalent pending exact confirmation) | ✅ Cleared for the **non-commercial local pilot** — a single supervised family running the OSS edition locally does not trigger the NC clause. **Does NOT clear the Phase-3 paid hosted tier** — see §3, same source, different tier. | Must credit Khan Academy; ND is not asserted by CC BY-NC-SA but SA (share-alike) is — any redistributed adaptation of KA text/transcript inherits CC BY-NC-SA (which is itself NC, compounding the hosted-tier restriction, not removing it). |
| **Vikidia** (en.vikidia.org) — cleared alternate, not currently mounted | CC BY-SA 3.0 | ✅ Compatible | Must credit Vikidia + authors; derivatives/adaptations must be shared under CC BY-SA (compatible). |
| **Simple English Wikipedia** — cleared alternate, not currently mounted | CC BY-SA 4.0 (text; also GFDL legacy) | ✅ Compatible | Must credit Wikipedia contributors + link licence; share-alike on derivatives. |

**Why these are fine for the pilot:**
- The pilot runs **local-only**, single supervised family — the content is read as grounding,
  not redistributed publicly. No commercial use. This is exactly the condition that clears
  Khan Academy's NC clause for the pilot while still blocking it from the paid hosted tier.
- Vikidia/Simple-WP are CC BY-SA: no NonCommercial (NC) and no NoDerivatives (ND) clause →
  compatible with Mentar's local use and an eventual OSS edition (subject to honoring
  attribution + share-alike if any adapted text is redistributed). Khan Academy adds the NC
  clause on top, which is why it's pilot-only, not OSS-edition-general the way Vikidia/
  Simple-WP are — see §3.
- **No attribution UI exists for any source today** (Khan Academy or Vikidia/Simple-WP) — the
  reader surfaces grounding passages to the LLM's system prompt only, never with a
  learner/parent-visible source-credit string. The obligation below is tracked here + in each
  curriculum node's `grounding:` metadata (source + anchor), not yet built as a UI feature.

**Obligations to honour even in the pilot (cheap to do now):**
1. Keep the source + anchor URL with each grounded passage (already in template `grounding:`).
2. When any adapted/excerpted source text is surfaced to the learner, retain attribution
   metadata so a future redistribution can credit correctly.
3. CC BY-SA is **share-alike**: if Mentar ever redistributes adapted passages, that
   redistribution inherits CC BY-SA. Confirm compatibility with the chosen project licence
   in **W4.2** (e.g., code Apache/AGPL vs content CC BY-SA are separate licences — keep them
   separated; do not relicense source content).

---

## 2. Verification notes (per source)

- **Khan Academy:** stated CC BY-NC-SA site-wide (khanacademy.org footer/terms as of the
  earlier W4.1 pass, logged in §3 pre-B1). The exact version (3.0 vs 4.0) on the specific
  `khanacademy_en_all_2023-03.zim` mirror is unconfirmed — treat as the more restrictive
  reading until verified. The pilot grounds on the video's **English `.vtt` subtitle
  transcript** (plain narration text extracted by `ZimReader.get_video_narration`), never the
  video file itself or page images — same "text passages only, no media" discipline as
  Vikidia/Simple-WP below.
- **Vikidia (en):** stated CC BY-SA 3.0. Some Vikidia language editions differ — the pilot
  uses the **English** edition; reconfirm if other-language editions are added.
- **Simple English Wikipedia:** Wikimedia text is CC BY-SA 4.0 (with GFDL dual-licence
  legacy). Images/media on a page may carry **different** licences — the pilot grounds on
  **text passages only**; do not pull page media without per-asset licence checks.

---

## 2b. Curriculum-standard alignment sources (not grounding content)

| Source | Licence | Use in Mentar | Notes |
|--------|---------|---------------|-------|
| **ACARA — Australian Curriculum v9** (australiancurriculum.edu.au) | **CC BY 4.0** for core curriculum content (verified against the site's copyright/terms page 2026-07-10) | `curriculum/templates/AU_ACARA/*.md` (renamed from `AU/` 2026-07-19, R-MC — see MULTI_COUNTRY.md's `country_authority` directory convention) reference **content-description CODES only** (e.g. AC9M3N01) as alignment identifiers; all node labels, question text and generator fact tables are **Mentar-authored** — no ACARA descriptor text is reproduced. | Attribution format if descriptor text is ever quoted: "© Australian Curriculum, Assessment and Reporting Authority (ACARA) 2010 to present" + download date + modification note. ⚠️ The **National Literacy Learning Progressions are CC BY-NC 4.0** (non-commercial) and "Excluded Materials" (photos/videos/teacher resources) are view-only — do NOT pull from either. |
| **NCERT (India) — e-content licence** (epathshala.nic.in) | ⚠️ **NO DERIVATIVES** — strictly stricter than ACARA. Two independent web searches (2026-07-11) converged on identical language: *"No person is permitted to adapt, translate, alter, summarize, or make any derivation of NCERT E-content... Any such act without the specific, written permission of NCERT will amount to infringement of copyright."* Free redistribution "as is" and non-commercial sharing are permitted; adaptation is not. **Not directly verified against the live page** — epathshala.nic.in was unreachable both from the sandbox and reported unreachable by the maintainer (re-checked again 2026-07-13, still unreachable); treated as confirmed on the strength of two independently-converging search results, per this doc's own "no shortcut" rule (do not assume permissive just because unverifiable). | **Decision: do NOT author "NCERT-aligned" content.** `curriculum/templates/IN_GENERIC/` (not `IN_NCERT`) references NO NCERT codes, learning-outcome wording, or claimed curriculum alignment — universally-taught topics only (place value, addition, times tables, basic fractions), 100% Mentar-authored, same discipline as the evergreen `practice/` pack. | Re-verify directly against `epathshala.nic.in/pages.php?id=license&ln=en` if/when reachable, before ever attempting a real `IN_NCERT`/`IN_CBSE` pack. |
| **CBSE (India) — website/curriculum copyright** (cbse.gov.in / results.cbse.nic.in) | ⚠️ **Permission-required, not an open licence.** Web search (2026-07-13): *"Material featured on CBSE's site may be reproduced free of charge after taking proper permission from the Central Board of Secondary Education (CBSE)... subject to the material being reproduced accurately and not being used in a derogatory manner."* "Reproduced accurately" reads as the same no-derivation posture as NCERT (CBSE syllabi explicitly reference NCERT anyway). **Not directly verified against a live CBSE terms page** — same discipline as NCERT: don't assume permissive. | **No `IN_CBSE` pack** — same `IN_GENERIC` decision applies; CBSE gives no basis for a claimed-alignment pack either. | Re-verify directly if reachable, before ever attempting a real `IN_CBSE` pack. |
| **ICSE/CISCE (India) — syllabus copyright** (cisce.org) | ⚠️ **All rights reserved** — the most restrictive of the three. Web search (2026-07-13) found only a bare "© Council for the Indian School Certificate Examinations. All rights reserved" on official syllabus PDFs — no licence grant of any kind located (no reproduce-with-permission clause even). | **No `IN_ICSE` pack.** Same `IN_GENERIC` decision. | Re-verify directly if reachable, before ever attempting a real `IN_ICSE` pack. |
| **Net finding (2026-07-13):** none of India's three major national curriculum bodies (NCERT, CBSE, ICSE) offer a licence that would clear a claimed-alignment pack the way ACARA's CC BY 4.0 did for Australia. `IN_GENERIC` (board-agnostic, no claimed alignment) is confirmed as the right strategy for India generally, not just a workaround for NCERT specifically — a state board (untested) or written permission from one of the three national bodies are the only paths to a real `IN_<BOARD>` pack. | | | |
| **US Common Core (NGA Center / CCSSO)** (thecorestandards.org/public-license) | ⚠️ **Open-ish, but NOT clean CC BY — two catches.** Grants a "limited, non-exclusive, royalty-free license to copy, publish, distribute, and display the Common Core State Standards" WITH: (1) a **purpose restriction** — use must be *"in support of the Common Core State Standards Initiative"* (arguably a faithful tutor qualifies, but it's fuzzier than ACARA's unconditional CC BY 4.0); (2) **"Common Core" is a registered trademark** with separate branding guidelines governing use of the name. Attribution notice required: *"© Copyright 2010. National Governors Association Center for Best Practices and Council of Chief State School Officers. All rights reserved."* Web-search-sourced 2026-07-16; not a lawyer's reading. | **DECIDED 2026-08-11 (maintainer): option (b) — `US_GENERIC`.** Rationale: OSS-release safety — a public AGPL repo should not carry content under a purpose-restricted licence with trademark exposure, however defensible the code-referencing reading looked. No CCSS codes, no "Common Core" naming, board/state-agnostic content on the IN_GENERIC/SG_GENERIC pattern (free-text `year_level: "Grade 3"` etc.). The (a) analysis stays recorded above in case a cleaner-licensed angle ever appears. Previous state was: DEFERRED — maintainer decision needed. Referencing CCSS *codes* only (e.g. CCSS.MATH.CONTENT.3.NBT.A.1) as internal alignment identifiers, Mentar-authoring all text, is the same discipline that cleared ACARA — but the purpose clause + trademark make a "Common Core"-*branded/aligned* pack a judgement call this project's own "no shortcut" rule says not to assume away. A **generic** `US_GENERIC` pack (no branding/codes/alignment) would clear trivially but duplicates `IN_GENERIC` and adds ~nothing, since a US pack's whole value IS the Common Core alignment. | Maintainer to decide: (a) commission/accept a considered read of the "in support of the initiative" clause + trademark and ship a code-referencing `US_COMMONCORE` pack, or (b) skip US until a cleaner-licensed angle exists. Logged so the facts are ready when decided. |
| **Singapore MOE** (moe.gov.sg) | ⚠️ **All rights reserved — no open licence, derivatives prohibited.** Terms of Use (fetched directly 2026-08-11): *"The intellectual property rights in the materials are owned or licensed to us"*; *"Apart from any fair dealings for the purposes of private study, research, criticism or review, as permitted by law, no part of The Website may be reproduced or reused for any commercial purposes whatsoever without our prior written permission"*; *"The modification of the materials on The Website is prohibited."* No CC/open-data grant anywhere in the terms. Independently corroborated by a web search the same day (MOE copyright-guidelines pages assume permission-per-use). MULTI_COUNTRY.md §2 already noted MOE publishes prose syllabi with no public standards-code scheme — so there are also no codes to reference-only cite the way ACARA/CCSS allow. | **Same position as NCERT/CBSE/ICSE → same strategy: `SG_GENERIC`** (board-agnostic pack teaching the same concepts at the same levels — "Primary 3", "Secondary 1" as free-text `year_level` — without claimed alignment or any reproduced syllabus text). C1 gate ANSWERED; authoring can proceed on the IN_GENERIC pattern. | No MOE contact needed for SG_GENERIC (nothing reproduced, nothing claimed). A claimed-alignment `SG_MOE` pack would need written permission — not pursued. |

### 2c. Onboarding a new curriculum-alignment source — checklist

Added per `docs/design/MULTI_COUNTRY.md` §3 (ratified 2026-07-19), modeled directly on how
§2b's ACARA row and Khan Academy's grounding clearance were actually done. Run this BEFORE
authoring any new country/authority's templates (R14/R15):

1. **Find the authority's own stated licence** (not a secondary summary) — record source URL
   + date checked, e.g. "verified against the site's copyright/terms page 2026-07-10" (§2b's
   ACARA row).
2. **Identify what's covered vs excluded** — a blanket "the curriculum is licence X" is not
   enough. ACARA's own row is the model: core content CC BY 4.0, but its Literacy
   Progressions are CC BY-NC 4.0 (non-commercial) and "Excluded Materials" are view-only.
   Check every sibling document for a carve-out before assuming uniformity.
3. **Record whether alignment is code-only** (no descriptor/outcome text reproduced — the
   pattern every shipped pack uses) **or whether any text will be quoted verbatim**
   (triggers attribution/share-alike obligations under the source licence).
4. **No shortcut rule, stated permanently:** "this is a government/public curriculum" is
   NEVER sufficient justification on its own — CC BY 4.0 (ACARA) vs CC BY-NC 4.0 (ACARA's own
   Literacy Progressions, same authority) proves licence terms vary even within one
   authority's own publications. NCERT/CBSE/ICSE (§2b) all failed this check outright — no
   `IN_<BOARD>`-branded pack exists as a result.
5. **Log the row in §2b (cleared) or as a deferred row above (blocked/undecided)** before any
   template is authored — never author first and backfill the licence check.

---

## 3. Hosted-tier / out-of-scope conflicts (logged, NOT resolved here)

| Source | Licence | Conflict | Disposition |
|--------|---------|----------|-------------|
| **Khan Academy** content | CC BY-NC-SA | **NC (NonCommercial) clause vs Mentar paid hosted tier** | **Phase-3 blocker.** Same source as §1's live pilot anchor — the NC clause doesn't block the non-commercial local pilot (§1), only a *paid* hosted tier. Must NOT be bundled into any paid offering without a separate Khan licence. Logged in SPEC §24. |

Khan content format/integration (ZIM vs Kolibri) is a separate open item — SPEC §24 #12.

---

## 4. Outcome

- **Pilot sources: Khan Academy (live, since B1 2026-07-05) + Vikidia/Simple English
  Wikipedia (cleared alternates): CLEARED** for local pilot use — Khan under CC BY-NC-SA
  (NC clause doesn't trigger for a non-commercial local pilot), Vikidia/Simple-WP under
  CC BY-SA, with attribution + share-alike obligations noted in §1.
- **Khan Academy CC BY-NC-SA: hosted-tier conflict logged** as a Phase-3 blocker (SPEC §24) —
  unchanged by the pilot re-point, since the pilot itself was never the blocked use case.
- W4.1 acceptance met: licence table for pilot sources written; Khan NC conflict logged.
- Project-licence choice + trademark search remain in **W4.2** (G2, not G0).

## Changelog

| Date | Change |
|------|--------|
| 2026-08-11 | v0.8 — §2b: **US decided (maintainer): `US_GENERIC`**, not a code-referencing US_COMMONCORE pack — OSS-release safety (purpose clause + trademark stay out of a public AGPL repo). Same generic pattern as IN_GENERIC/SG_GENERIC. Also this date: Singapore MOE row added (all rights reserved → SG_GENERIC). |
| 2026-07-19 | v0.7 — R-MC: `curriculum/templates/AU/` renamed to `AU_ACARA/` (MULTI_COUNTRY.md's ratified `country_authority` directory convention, done now while zero external users exist); §2b's ACARA row path updated. New §2c: the licence-onboarding checklist from MULTI_COUNTRY.md §3, to run before any R14/R15 template is authored. |
| 2026-07-16 | v0.6 — §2b: US Common Core (NGA/CCSSO) logged as a candidate for a future US pack. NOT clean CC BY like ACARA — a "in support of the Initiative" purpose clause + "Common Core" trademark make a branded/aligned pack a maintainer judgement call, not an auto-clear. Code-referencing (CCSS codes as identifiers, Mentar-authored text) is the ACARA-cleared pattern but still needs a considered read of those two catches. Deliberately NOT actioned autonomously; flagged with facts ready for the maintainer to decide. |
| 2026-07-10 | v0.2 — Khan Academy promoted from §3-only (Phase-3 blocker note) to §1 (live pilot grounding source, cleared for local use) following B1's 2026-07-05 re-point. Vikidia/Simple-WP re-labelled cleared alternates, not currently mounted. Added the "no attribution UI exists yet, for any source" honesty note (D1, post-release-wave gap sweep). |
| 2026-07-10 | v0.3 — new §2b: ACARA (Australian Curriculum v9) logged as a curriculum-ALIGNMENT source for the new `curriculum/templates/AU/` templates. Core content CC BY 4.0 (verified live against the site's copyright page); Mentar references codes only, reproduces no descriptor text; NC-licensed Literacy Progressions + view-only Excluded Materials flagged as off-limits. |
| 2026-07-13 | v0.5 — §2b: checked CBSE and ICSE/CISCE (the other two India national boards), following up on NCERT's no-derivatives finding. Neither offers a clear open licence either — CBSE requires permission + "reproduced accurately" (same no-derivation spirit as NCERT); ICSE is bare all-rights-reserved. Net finding: `IN_GENERIC` (board-agnostic) is confirmed as the right India strategy generally, not a one-off NCERT workaround. |
| 2026-07-11 | v0.4 — §2b: NCERT (India) e-content licence flagged NO-DERIVATIVES (adapt/summarize/derive all prohibited without written permission) — a materially stricter posture than ACARA's CC BY 4.0. Could not verify live (epathshala.nic.in unreachable both from the sandbox and by the maintainer); treated as confirmed on two independently-converging web searches, per this doc's own no-shortcut discipline. Decision: `curriculum/templates/IN_GENERIC/` ships universally-taught, 100% Mentar-authored content with NO NCERT/CBSE branding, codes, or claimed alignment — same posture as the evergreen `practice/` pack. Re-verify directly before ever attempting a real `IN_NCERT`/`IN_CBSE` pack. |
