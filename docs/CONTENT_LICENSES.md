---
title: "Mentar — Content Licence Audit (Pilot Sources)"
version: v0.4
status: "Pilot sources cleared; hosted-tier conflicts logged; NCERT (India) flagged no-derivatives"
last-updated: 2026-07-11
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
| **ACARA — Australian Curriculum v9** (australiancurriculum.edu.au) | **CC BY 4.0** for core curriculum content (verified against the site's copyright/terms page 2026-07-10) | `curriculum/templates/AU/*.md` reference **content-description CODES only** (e.g. AC9M3N01) as alignment identifiers; all node labels, question text and generator fact tables are **Mentar-authored** — no ACARA descriptor text is reproduced. | Attribution format if descriptor text is ever quoted: "© Australian Curriculum, Assessment and Reporting Authority (ACARA) 2010 to present" + download date + modification note. ⚠️ The **National Literacy Learning Progressions are CC BY-NC 4.0** (non-commercial) and "Excluded Materials" (photos/videos/teacher resources) are view-only — do NOT pull from either. |
| **NCERT (India) — e-content licence** (epathshala.nic.in) | ⚠️ **NO DERIVATIVES** — strictly stricter than ACARA. Two independent web searches (2026-07-11) converged on identical language: *"No person is permitted to adapt, translate, alter, summarize, or make any derivation of NCERT E-content... Any such act without the specific, written permission of NCERT will amount to infringement of copyright."* Free redistribution "as is" and non-commercial sharing are permitted; adaptation is not. **Not directly verified against the live page** — epathshala.nic.in was unreachable both from the sandbox and reported unreachable by the maintainer; treated as confirmed on the strength of two independently-converging search results, per this doc's own "no shortcut" rule (do not assume permissive just because unverifiable). | **Decision: do NOT author "NCERT-aligned" content.** `curriculum/templates/IN_GENERIC/` (not `IN_NCERT`) references NO NCERT codes, learning-outcome wording, or claimed curriculum alignment — universally-taught topics only (place value, addition, times tables, basic fractions), 100% Mentar-authored, same discipline as the evergreen `practice/` pack. | Re-verify directly against `epathshala.nic.in/pages.php?id=license&ln=en` if/when reachable, before ever attempting a real `IN_NCERT`/`IN_CBSE` pack. |

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
| 2026-07-10 | v0.2 — Khan Academy promoted from §3-only (Phase-3 blocker note) to §1 (live pilot grounding source, cleared for local use) following B1's 2026-07-05 re-point. Vikidia/Simple-WP re-labelled cleared alternates, not currently mounted. Added the "no attribution UI exists yet, for any source" honesty note (D1, post-release-wave gap sweep). |
| 2026-07-10 | v0.3 — new §2b: ACARA (Australian Curriculum v9) logged as a curriculum-ALIGNMENT source for the new `curriculum/templates/AU/` templates. Core content CC BY 4.0 (verified live against the site's copyright page); Mentar references codes only, reproduces no descriptor text; NC-licensed Literacy Progressions + view-only Excluded Materials flagged as off-limits. |
| 2026-07-11 | v0.4 — §2b: NCERT (India) e-content licence flagged NO-DERIVATIVES (adapt/summarize/derive all prohibited without written permission) — a materially stricter posture than ACARA's CC BY 4.0. Could not verify live (epathshala.nic.in unreachable both from the sandbox and by the maintainer); treated as confirmed on two independently-converging web searches, per this doc's own no-shortcut discipline. Decision: `curriculum/templates/IN_GENERIC/` ships universally-taught, 100% Mentar-authored content with NO NCERT/CBSE branding, codes, or claimed alignment — same posture as the evergreen `practice/` pack. Re-verify directly before ever attempting a real `IN_NCERT`/`IN_CBSE` pack. |
