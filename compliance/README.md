# Mentar — Compliance Coverage Status

> ⚠️ **Not legal advice.** This is an engineering coverage map summarising the project's
> regulatory *posture* and where it is documented. It is general information drawn from
> prior project research (SPEC §17), **not** a legal opinion. Verify independently before
> any non-local or commercial deployment.

This doc tracks **what is mapped, what is incomplete, and where contributors can help**.
The authoritative analysis lives in [`docs/SPEC.md` §17](../docs/SPEC.md) (Regulatory &
Compliance Posture); data/privacy *controls* live in [`docs/SAFETY.md`](../docs/SAFETY.md)
Layer 4; content licensing in [`docs/CONTENT_LICENSES.md`](../docs/CONTENT_LICENSES.md).

---

## The core posture

Mentar ships in two editions with very different exposure:

- **OSS Local Edition (current focus):** runs entirely on the parent's device. No operator
  collects child data. This is an *architectural* compliance advantage — if data never
  leaves the device, most heavy obligations (COPPA operator duties, GDPR controller duties)
  do not attach to the project (SPEC §17.2; SAFETY §4.1).
- **Paid Hosted Tier (future):** managed inference for non-technical parents. **This is
  where the heavy compliance machinery concentrates** — full COPPA / GDPR-K / EU-AI-Act
  obligations apply. Out of scope for Phase 0.

**Safety is honoured regardless of legal exposure** — for the children, the parents, app
stores, and reputation, not merely to satisfy a regulator (SPEC §17.2).

---

## Coverage map

| Framework / area | Edition relevance | Status | Authoritative source |
|------------------|-------------------|--------|----------------------|
| **COPPA** (US, under-13) | Hosted tier (local edition: no operator) | 🟡 Mapped; 2025 amendments (full compliance **22 Apr 2026**) need a re-check | SPEC §17.3; verify task **W5.4** |
| **GDPR-K** (EU, Art. 8 age of consent) | Hosted tier; local likely household-exempt | 🟡 Mapped | SPEC §17.3 |
| **UK Age Appropriate Design Code** | In scope (consumer product likely accessed by minors) | 🟡 Mapped, controls partial | SPEC §17.3; SAFETY L4/L5 |
| **California / state AADCs** | Hosted tier | 🟡 Mapped (partially enjoined) | SPEC §17.3 |
| **EU AI Act — Art. 5 (manipulation ban)** | **Travels to all editions** | 🟢 Designed for: no dark patterns / compulsive mechanics; no emotion recognition | SAFETY L2 §2.3, §2.7; SPEC §17.4 |
| **EU AI Act — Annex III high-risk (education)** | **EU market entry / hosted tier** (NOT the local pilot) | 🟠 Open for EU launch — turns on "consequential decisions"; the supervised non-grading **local** edition likely falls outside and does not "place on market" (§17.2), so it is **not pilot/G0-blocking** | SPEC §17.1–17.2; §24 #1 |
| **Data minimisation / retention** | All editions | 🟢 Specified (local SQLite, rolling-90-day default, parent deletes) | SAFETY §4.3, §4.6 |
| **Parental consent** | All editions (pilot) | 🟢 Pilot consent note authored | SAFETY §4.2; `docs/PILOT_CONSENT.md` (W2.5) |
| **Content licensing** | All editions | 🟢 Pilot sources cleared (CC BY-SA); Khan NC = hosted-tier conflict | `docs/CONTENT_LICENSES.md` (W4.1) |
| **Safeguarding / escalation** | All editions | 🟡 v0.1-interim live; emergency-signposting + handoff review open | SAFETY Layer 3; `docs/design/W2.2_escalation.md` |

Legend: 🟢 covered for current scope · 🟡 mapped, controls partial/pending · 🔴 open blocker.

---

## Key open items (where contributors can help)

1. **EU AI Act high-risk question (§17.1 / §24 #1)** — confirm whether a non-grading,
   supplementary home tutor sits outside Annex III high-risk, and how OSS distribution is
   treated (provider vs deployer). **G2 / EU-entry blocker.**
2. **COPPA post-2026 re-check (W5.4)** — re-verify against the amendments effective 22 Apr 2026.
3. **OSS project licence + trademark (W4.2)** — permissive vs copyleft decision, deliberately.
4. **Safety research Buckets C–H (SPEC §17.5)** — chatbot-harm cases (C), safeguarding (D),
   content standards (E), guardrail tooling (F), over-reliance (G), kid-safe patterns (H).

---

## Relationship to other docs

This folder is a **status overlay**, not a second source of truth. It never restates legal
analysis — it points to it. When SPEC §17 or SAFETY Layer 4 change, update the table above.
Living research findings are tracked under [`docs/research/`](../docs/research/) (SPEC §17.5).
