---
type: Mentar Compliance Research
title: COPPA — Children's Online Privacy Protection Act (US)
description: US COPPA (2025 amendments) mapping for the OSS local edition. Not legal advice.
tags: [compliance, legal, coppa, us]
timestamp: "2026-07-23T00:00:00Z"
---

# COPPA — Children's Online Privacy Protection Act (US)

**Jurisdiction:** United States  
**Applies to:** Under-13  
**Current version:** 2025 amendments (full compliance deadline 22 April 2026)

---

## What COPPA requires (2025 amendments)

- **Verifiable parental consent** before collecting personal information from under-13, including for disclosure to third parties (2025 amendment adds separate consent requirement for ad/3rd-party disclosure)
- **Data minimisation** — collect only what's necessary for the service
- **Retention limits** — retain children's data only as long as necessary (2025 amendment adds explicit limits)
- **Broader definition of "personal information"** — now includes biometric data and government IDs (2025 amendment)
- **Written information security program** — required for operators collecting children's data
- **No school-authorization exception** codified — FTC did not codify this in 2025 amendments

---

## Mentar OSS local edition — exposure assessment

**Exposure: LOW**

- The local edition collects no personal information. Data stays on-device.
- No operator role: Mentar (as OSS developer) is not collecting, using, or disclosing children's personal information.
- No COPPA operator obligations attach when there is no data collection.

The parent sets up the system on their own hardware. Under COPPA, the household use is the parent's own activity, not an operator-child relationship with Mentar as operator.

**Risk concentrates in the hosted tier:** If Mentar ever runs inference in the cloud and collects session data, full COPPA operator machinery applies — consent, retention, security program, etc.

---

## Design implications

- OSS edition: deliberately no data collection. Maintain this.
- Any future analytics, telemetry, or optional cloud sync must trigger a full COPPA review before implementation.
- If the hosted tier ever serves US under-13 users, verifiable parental consent + separate ad-disclosure consent + written security program are mandatory.

---

*Not legal advice. Verify before commercial deployment.*
