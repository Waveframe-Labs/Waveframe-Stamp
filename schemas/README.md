---
title: "Stamp — Schemas Directory"
filetype: "documentation"
type: "specification"
domain: "methodology"
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

ai_assisted: "partial"
ai_assistance_details: "AI-assisted drafting of schema documentation under direct human authorship, review, and final approval."

dependencies: []

anchors: []
---

# schemas/

This directory contains the **normative JSON Schemas** that define Stamp’s core contracts.
These schemas are **authoritative**, versioned, and relied upon by downstream tooling.

Schemas in this directory define **what Stamp means**, not how it is executed.

---

## Contents

### `cdo-v1.schema.json`

**Canonical Diagnostic Object (CDO) — v1**

Defines the structure of all diagnostics emitted by Stamp during validation.

**Key guarantees:**
- Diagnostics represent **facts only**
- No inferred intent or policy judgment
- Stable semantic IDs suitable for ABI-level reliance
- Fully machine-readable and diffable

All validation errors are normalized into this format before any further processing.

---

### `npo-v1.schema.json`

**Normalization Proposal Object (NPO) — v1**

Defines the structure of fix proposals derived from diagnostics.

**Key guarantees:**
- Proposals represent **claims**, not actions
- Deterministic proposal IDs (hash-derived)
- Flat proposal lists (no ordering or execution semantics)
- Explicit separation from mutation or enforcement

NPOs explain *what could be fixed*, never *what must be fixed*.

---

## Contract Status

Both schemas in this directory are:

- **Normative**
- **Versioned**
- **Contractually frozen at v1**
- Safe for downstream reliance (e.g. CRI-CORE)

Any future changes will occur via:
- New schema files (e.g. `*-v2.schema.json`)
- Explicit changelog entries
- Non-breaking coexistence with v1

Existing v1 schemas will not be modified retroactively.

---

## Design Notes

- Schemas are intentionally **policy-neutral**
- Enforcement and approval semantics are **out of scope**
- These schemas define *structure*, not *authority*

Stamp treats schemas as **truth sources**, not suggestions.

---

<div align="center">
  <sub>© 2026 Waveframe Labs</sub>
</div>
