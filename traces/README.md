---
title: "Stamp — Execution Traces"
filetype: "documentation"
type: "informational"
domain: "tooling"
version: "0.1.0"
doi: "10.5281/zenodo.18436622"
status: "Active"
created: "2026-01-29"
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
ai_assistance_details: "AI-assisted drafting of explanatory documentation, with human review and final approval."

dependencies: []

anchors:
  - STAMP-TRACES-README-v0.1.0
---

# Execution Traces

This directory contains **execution trace artifacts** produced by Stamp during validation runs.

Execution traces are **immutable, machine-validated records** of how Stamp was invoked, what artifacts were evaluated, and what outcomes were produced.

They serve as **audit evidence**, not as governed research artifacts.

---

## What Lives Here

Current contents:

- `stamp-validation-trace.json`  
  A recorded execution trace generated via the `--trace-out` flag during repository validation.

---

## What Execution Traces Are

Execution traces:

- Capture **tool identity and version**
- Record **timestamps and exit codes**
- Enumerate validated artifacts and outcomes
- Are validated against a dedicated trace schema
- Are safe to commit for audit and provenance purposes

They are designed to be:

- Deterministic
- Diffable
- Machine-consumable
- Suitable for long-term provenance records

---

## What Execution Traces Are *Not*

Execution traces are **not**:

- Subject to metadata governance
- Validated against ARI or other metadata schemas
- Required to contain frontmatter or embedded metadata
- Inputs to policy or enforcement logic

They are intentionally excluded from repository validation.

---

## Governance Note

Stamp explicitly excludes trace artifacts from validation during `validate repo` runs.

This prevents execution evidence from:

- Failing metadata validation
- Requiring artificial metadata
- Polluting governed artifact counts

This behavior is **by design** and contractually stable.

---

<div align="center">
  <sub>© 2026 Waveframe Labs</sub>
</div>
