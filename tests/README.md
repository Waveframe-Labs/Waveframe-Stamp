---
title: "Stamp — Tests"
filetype: "documentation"
type: "specification"
domain: "methodology"
version: "0.1.0"
doi: "10.5281/zenodo.18436622"
status: "Active"
created: "2026-01-29"
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
ai_assistance_details: "AI-assisted drafting of test structure documentation with human review and approval."

dependencies: []
anchors: []
---

# Tests

This directory contains **formal unit and integration tests** for the Stamp codebase.

Tests in this folder are intended to be:

- Discoverable by standard Python tooling (`pytest`)
- Deterministic and reproducible
- Focused on **contract correctness**, not CLI behavior
- Safe to run in CI environments

## Scope

Tests in `tests/` SHOULD cover:

- Core validation logic (`validate`, `schema`, `cdo`)
- Deterministic normalization behavior
- Fix proposal generation rules
- Remediation classification logic
- Edge cases for schema conditionals and metadata extraction

Tests in `tests/` SHOULD NOT:

- Perform filesystem discovery across the repository
- Execute CLI commands end-to-end
- Rely on mutable external state

CLI-level smoke checks and developer utilities live in `scripts/`.

## Relationship to Other Folders

- `fixtures/` — Stable, versioned fixture data used by tests
- `schemas/` — Canonical schemas under test
- `examples/` — User-facing demo artifacts (not tests)
- `scripts/` — Manual runners and smoke utilities

## Status

The test suite is expected to grow incrementally as contracts evolve.
Absence of a test implies **non-frozen behavior**, not undefined behavior.

---

<div align="center">
  <sub>© 2026 Waveframe Labs</sub>
</div>
