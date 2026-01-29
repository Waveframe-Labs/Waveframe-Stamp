---
title: "Stamp — Changelog"
filetype: "log"
type: "normative"
domain: "documentation"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Active"
created: "2026-01-18"
updated: "2026-01-29"

author:
  name: "Shawn C. Wright"
  email: "swright@waveframelabs.org"
  orcid: "https://orcid.org/0009-0006-6043-9295"

maintainer:
  name: "Waveframe Labs"
  url: "https://waveframelabs.org"

license: "Apache-2.0"

copyright:
  holder: "Waveframe Labs"
  year: "2026"

ai_assisted: "none"

dependencies: []

anchors: []
---

# Stamp — Change Log

This document records **material design decisions, contract freezes, and layer-level milestones** for the Stamp project.

It is **not a release log** and does **not imply end-user readiness**.

The purpose of this log is to provide an auditable history of how the Stamp layer reached its current form, so that downstream systems (notably CRI-CORE) may rely on its guarantees.

---

## [Unreleased] — Stamp Core Layer Completion

### Added

- Canonical Diagnostic Object (CDO) v1 schema
- Normalization Proposal Object (NPO) v1 schema
- Deterministic diagnostic-to-proposal mapping logic
- Canonical fixture suites proving:
  - Required field violations
  - Enum mismatches
  - Type mismatches
  - AdditionalProperties enforcement
  - Conditional (`if` / `then`) requirements
- Reference implementation:
  - `stamp.validate` — fact emission only
  - `stamp.normalize` — proposal emission only
- Execution runners for CDO and NPO fixtures

### Frozen

The following contracts and behaviors are **explicitly frozen** at v1:

- **CDO Contract**
  - Diagnostics represent *facts only*
  - No inferred intent
  - No mutation or correction logic
- **NPO Contract**
  - Proposals represent *claims*, not actions
  - Deterministic proposal IDs via hashing
  - Flat proposal lists (no nesting or execution order)
- **Separation of Concerns**
  - Validation and normalization are strictly decoupled
  - Stamp does not enforce, apply, or approve changes

### Explicit Non-Goals

Stamp **will not**:

- Mutate or rewrite artifacts
- Enforce policy decisions
- Apply fixes automatically
- Manage approvals or workflows
- Integrate directly with CRI-CORE at this layer

All enforcement and execution responsibilities are deferred to downstream systems.

---

## [2026-01-18] — Architecture & Contract Finalization

- Completed stress-testing of mechanical, inferred, ambiguous, and prohibited normalization scenarios
- Formalized epistemic classifications for normalization proposals
- Locked governance boundary between:
  - Facts (CDO)
  - Claims (NPO)
- Confirmed readiness to serve as an upstream dependency for CRI-CORE

---

## Status

- **Layer completeness:** Achieved
- **Contracts:** Frozen (v1)
- **Fixtures:** Passing
- **Documentation:** In progress (non-blocking)

No version tag has been applied. Tagging will occur only after downstream integration milestones are reached.

---

<div align="center">
  <sub>© 2026 Waveframe Labs — Governed under the Aurora Research Initiative (ARI)</sub>
</div>
