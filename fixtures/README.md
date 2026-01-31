---
title: "Stamp — Fixtures"
filetype: "documentation"
type: "specification"
domain: "methodology"
version: "0.1.0"
doi: "10.5281/zenodo.18436622"
status: "Active"
created: "2026-01-18"
updated: "2026-01-31"

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
ai_assistance_details: "AI-assisted drafting of documentation structure with human-authored semantics, review, and final control."

dependencies: []
anchors: []
---

# Fixtures

This directory contains **normative test fixtures** used to verify Stamp’s core contracts.

Fixtures are not examples, demos, or sample inputs.  
They are **deliberately constructed artifacts** designed to assert and lock-in deterministic behavior.

---

## Contents

### `fixtures-v1.json`

Canonical validation fixtures for **Canonical Diagnostic Objects (CDOs)**.

These fixtures assert:

- Required field violations
- Enum mismatches
- Type mismatches
- `additionalProperties` enforcement
- Conditional schema logic (`if` / `then` / `else`)
- Deterministic diagnostic IDs and structures

They serve as a regression anchor for Stamp’s **fact emission layer**.

---

### `npo-fixtures-v1.json`

Canonical fixtures for **Normalization Proposal Objects (NPOs)**.

These fixtures assert:

- Deterministic diagnostic → proposal mapping
- Proposal ID stability
- Separation between facts (CDOs) and claims (NPOs)
- Absence of execution or mutation semantics

They lock the contract that **proposals describe possibilities, not actions**.

---

## Governance Notes

- Fixtures are **normative**, not illustrative
- Changes to fixtures imply **contract changes**
- Any modification requires:
  - Explicit changelog entry
  - Version bump (minor or major, depending on scope)
  - Downstream impact review (e.g., CRI-CORE)

Fixtures are intentionally boring, exhaustive, and precise.

---

## Validation Scope

Fixtures themselves are **not governed artifacts** and are excluded from metadata validation.  
They exist solely to validate Stamp’s internal behavior.

---

<div align="center">
  <sub>© 2026 Waveframe Labs</sub>
</div>
