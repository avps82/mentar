# UK Age Appropriate Design Code (Children's Code)

**Jurisdiction:** United Kingdom  
**Administered by:** ICO (Information Commissioner's Office)  
**Scope:** Any service "likely to be accessed" by under-18s — including non-UK services accessible to UK children

---

## Key requirements (15 standards)

1. **Best interests of the child** as the primary design consideration — overrides commercial interests
2. **Data protection impact assessment** before deploying services likely accessed by children
3. **High privacy settings by default** — no nudging children to lower privacy protections
4. **Data minimisation** — only collect what's strictly necessary
5. **Data sharing** — do not share children's data unless strictly necessary
6. **Geolocation** off by default
7. **Parental controls** — do not use them to monitor children covertly
8. **Profiling** off by default — do not use children's data for profiling unless strictly necessary
9. **No nudge techniques** — do not use design techniques that encourage children to provide unnecessary data or weaken privacy settings
10. **Connected toys and devices** — apply the code to connected toys
11. **Online tools** — provide age-appropriate tools to support children's rights
12. **Transparency** — provide accessible and age-appropriate privacy information
13. **Detrimental use** — do not use children's data in ways detrimental to their wellbeing
14. **Nudge techniques for data** — no prompts to children to increase engagement in ways that are not in their best interests
15. **Targeted advertising** — do not serve targeted ads based on profiling to children

---

## Exemptions — Mentar context

Schools providing education are exempt from some provisions. However, **Mentar is a consumer product**, not a school service. It is in scope.

---

## Mentar OSS local edition — exposure assessment

**Exposure: LOW-MEDIUM**

- Local-first, no-collection architecture eliminates most data-related standards.
- However, "likely accessed by under-18s" is a low bar — Mentar is explicitly for children. The Code's principles apply to the **design** of the service, not just data handling.
- The best-interests-of-child standard and anti-dark-patterns standards apply as design principles regardless of data collection.

**Design implications (already captured in safety spec):**
- No dark patterns ✓
- No profiling ✓  
- No targeted advertising (ever) ✓
- High privacy by default ✓ (local-first)
- Best interests of child as primary lens ✓

---

## California AADC

California's Age-Appropriate Design Code (AADC) is modelled on the UK code. Status as of 2026-06:
- NetChoice litigation resulted in partial injunction
- 9th Circuit mandate issued 3 April 2026
- Data-use and dark-patterns provisions still enjoined; age-estimation remanded
- Other states layering similar codes: Maryland, South Carolina

**Practical implication:** The UK code's standards are effectively a superset. Designing to the UK code covers most California AADC intent. Monitor as litigation resolves.

---

*Not legal advice. Verify before commercial deployment.*
