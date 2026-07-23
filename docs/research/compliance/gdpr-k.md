---
type: Mentar Compliance Research
title: GDPR-K — Children's Data Protection (EU)
description: EU GDPR-K mapping for the OSS local edition. Not legal advice.
tags: [compliance, legal, gdpr-k, eu]
timestamp: "2026-07-23T00:00:00Z"
---

# GDPR-K — Children's Data Protection (EU)

**Jurisdiction:** European Union (+ EEA)  
**Key provisions:** GDPR Article 8, Recital 38  
**Age threshold:** Under-16 (member states may lower to 13; Germany = 16, many others = 13)

---

## What GDPR-K requires

- **Article 8:** Processing personal data of a child for an online information society service requires parental consent if the child is under the age of digital consent in that member state (13–16, varies by country).
- **Recital 38 carve-out:** Parental consent is NOT required for preventative or counselling services offered directly to a child — intended to protect children's access to advice. Mentar is not a counselling service, so this carve-out likely does not apply.
- Standard GDPR principles apply to all children's data: lawfulness, fairness, transparency, purpose limitation, data minimisation, accuracy, storage limitation, security.

---

## Mentar OSS local edition — exposure assessment

**Exposure: LOW**

- No data leaves the device. No controller or processor role for Mentar as OSS developer.
- GDPR applies to processing of personal data. If there is no processing by an operator, controller obligations don't attach.
- A parent running Mentar at home for their own child is likely covered by the **household activity exemption** (GDPR Article 2(2)(c)) — processing by a natural person in the course of a purely personal or household activity is out of scope.

**Risk concentrates in the hosted tier:** Any cloud-hosted version that processes children's data (EU residents) becomes a data controller with full GDPR obligations — lawful basis, parental consent (under age of digital consent), DPA registration, data subject rights, DPO assessment, etc.

---

## Design implications

- OSS edition: maintain local-first, no-collection architecture.
- Hosted tier for EU users: legal basis (parental consent) + age verification are mandatory before processing any EU child's personal data.
- Do not implement emotion recognition or mood inference — legally fraught under EU AI Act (separate from GDPR-K but compounding).

---

## Member-state variation

Digital age of consent varies. If hosted tier targets EU, map by member state before launch:

| Country | Digital age of consent |
|---|---|
| Germany | 16 |
| France | 15 |
| Most others | 13 |

---

*Not legal advice. Verify before commercial deployment.*
