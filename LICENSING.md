# Licensing

SPDX-License-Identifier: AGPL-3.0-only
Copyright (C) 2026 Mentar maintainers

## The short version

- **Mentar is open source under the [GNU AGPL-3.0-only](LICENSE).** You can use it, study it,
  modify it, and redistribute it — including commercially — provided you honour the AGPL:
  any version you distribute, **or run as a network service for others**, must make its
  complete corresponding source available under the same licence.
- **The maintainer additionally offers commercial licences.** If the AGPL's terms don't work
  for your use (for example, you want to build a proprietary or closed hosted product on
  Mentar), a separate commercial licence can be negotiated with the copyright holder. Contact
  the maintainer.
- **Contributions require a Contributor License Agreement (CLA)** — see below for exactly
  why, stated honestly.

## Why AGPL

Mentar is a children's product whose entire trust model is openness: the code is largely
AI-authored under human direction (see the README's honesty note), it has not had a funded
professional audit, and its safety case therefore rests on *anyone being able to read,
run, and verify it*. A licence that kept the source closed to commercial users would spend
the very transparency the project depends on.

AGPL was chosen over a permissive licence for one reason: the network-services clause.
A permissive licence would allow anyone to run Mentar as a closed, modified, hosted service
for children — with safety changes nobody can inspect. Under AGPL, whoever offers Mentar
over a network must publish their modifications. For this project that clause is not
ideology; it is a child-safety property.

AGPL is a deliberate **choice**, not a dependency constraint: as of 2026-08-12 every core
dependency is permissive or weak-copyleft (`docs/LICENSE_AUDIT.md`). The one GPL dependency,
`libzim`, lives in the optional `[grounding]` extra — if you install that extra, GPL terms
apply to that combination, which the AGPL is compatible with.

## Commercial licensing (dual licensing)

The copyright holder retains all rights that the AGPL does not grant, and may license
Mentar under other terms. In practice:

- **Using Mentar commercially under the AGPL is fine and needs no permission** — a school,
  a tutoring service, or a company may run it, provided AGPL obligations are met (chiefly:
  source availability for any distributed or network-served modifications).
- **A commercial licence is for when you cannot or do not want to meet those obligations** —
  e.g. embedding Mentar in a proprietary product, or operating a closed hosted service.

This is the standard dual-licensing model. It works only while the copyright in the code
remains consolidated — which is what the CLA below protects.

## Contributor License Agreement (CLA)

Before a first external contribution is merged, the contributor must agree to the project's
CLA (grant of copyright licence to the maintainer, including the right to relicense).

**The honest reason:** dual licensing requires the maintainer to hold sufficient rights over
the whole codebase. Every external patch merged *without* a CLA would give its author a
permanent veto over any future commercial licence or licence change. The CLA keeps the
commercial-licensing door open; the AGPL guarantees the community always keeps the open
version regardless of what the maintainer does with those rights.

If you're uncomfortable signing rights over, that is a legitimate position — the honest
trade is stated here so nobody discovers it after contributing.

## Content licences

Curriculum content has its own per-source licensing, tracked in
[`docs/CONTENT_LICENSES.md`](docs/CONTENT_LICENSES.md). One is load-bearing for commercial
use: **Khan Academy grounding content is CC BY-NC-SA** — it clears the free local edition
but not any paid tier. The shipped curriculum packs are Mentar-authored and carry no such
restriction.

## Notes

- Version: **AGPL-3.0-only** (not "or-later") — a future licence version change is a
  maintainer decision, not automatic.
- The code is substantially AI-generated under human direction and review. The copyright
  status of AI-generated code is not fully settled law; the project claims copyright on the
  basis of human selection, direction, and revision, and states this openly rather than
  pretending otherwise.
- This document explains intent; the [LICENSE](LICENSE) file is the binding text.
