---
title: "Mentar — Content Licence Audit (Pilot Sources)"
version: v0.1
status: "Pilot sources cleared; hosted-tier conflicts logged"
last-updated: 2026-06-14
scope: "Phase-0 pilot grounding sources ONLY (W4.1). Not a full content-licensing policy."
sources: "PHASE0.md W4.1; SPEC §18 (content stack), §24 #12; curriculum/templates/_pilot/fractions.md grounding anchors"
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
Layer 6). The pilot template (`curriculum/templates/_pilot/fractions.md`) anchors to:

| Source | Licence | Local pilot use | Attribution / share-alike obligation |
|--------|---------|-----------------|--------------------------------------|
| **Vikidia** (en.vikidia.org) | CC BY-SA 3.0 | ✅ Compatible | Must credit Vikidia + authors; derivatives/adaptations must be shared under CC BY-SA (compatible). |
| **Simple English Wikipedia** | CC BY-SA 4.0 (text; also GFDL legacy) | ✅ Compatible | Must credit Wikipedia contributors + link licence; share-alike on derivatives. |

**Why these are fine for the pilot:**
- The pilot runs **local-only**, single supervised family — the content is read as grounding,
  not redistributed publicly. No commercial use.
- Both are CC BY-SA: no NonCommercial (NC) and no NoDerivatives (ND) clause → compatible
  with Mentar's local use and an eventual OSS edition (subject to honoring attribution +
  share-alike if any adapted text is redistributed).

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

- **Vikidia (en):** stated CC BY-SA 3.0. Some Vikidia language editions differ — the pilot
  uses the **English** edition; reconfirm if other-language editions are added.
- **Simple English Wikipedia:** Wikimedia text is CC BY-SA 4.0 (with GFDL dual-licence
  legacy). Images/media on a page may carry **different** licences — the pilot grounds on
  **text passages only**; do not pull page media without per-asset licence checks.

---

## 3. Hosted-tier / out-of-scope conflicts (logged, NOT resolved here)

| Source | Licence | Conflict | Disposition |
|--------|---------|----------|-------------|
| **Khan Academy** content | CC BY-NC-SA | **NC (NonCommercial) clause vs Mentar paid hosted tier** | **Phase-3 blocker.** The NC clause is incompatible with a *paid* hosted tier. Fine for non-commercial local/OSS use; must NOT be bundled into any paid offering without a separate Khan licence. Logged in SPEC §24. |

Khan content format/integration (ZIM vs Kolibri) is a separate open item — SPEC §24 #12.

---

## 4. Outcome

- **Pilot sources (Vikidia, Simple English Wikipedia): CLEARED** for local pilot use under
  CC BY-SA, with attribution + share-alike obligations noted above.
- **Khan Academy CC BY-NC-SA: hosted-tier conflict logged** as a Phase-3 blocker (SPEC §24).
- W4.1 acceptance met: licence table for pilot sources written; Khan NC conflict logged.
- Project-licence choice + trademark search remain in **W4.2** (G2, not G0).
