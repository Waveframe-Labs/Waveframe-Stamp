---
title: "Stamp — Runner Directory"
filetype: "documentation"
type: "specification"
domain: "tooling"
version: "0.1.0"
doi: "TBD-0.1.0"
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
ai_assistance_details: "AI-assisted drafting of documentation structure and clarity, with human review and final approval."

dependencies: []

anchors:
  - STAMP-RUNNER-DIR-v0.1.0
---

# runner/

This directory contains **deterministic execution scripts** used to run Stamp’s internal verification suites.

These scripts are **not part of the public CLI surface**. They exist to:

- Execute fixture suites in a controlled, repeatable way
- Validate frozen contracts (CDO, NPO) against reference data
- Provide smoke-level confidence that core behaviors have not regressed

They are intended for **developers, reviewers, and CI environments**, not end users.

---

## Files

### `run_fixtures.py`

Executes the **Canonical Diagnostic Object (CDO) fixture suite**.

Purpose:
- Validates deterministic normalization of schema violations
- Ensures diagnostic IDs, severities, and paths remain stable
- Detects accidental semantic drift in validation logic

This script is relied upon to protect the **CDO v1 contract**.

---

### `run_npo_fixtures.py`

Executes the **Normalization Proposal Object (NPO) fixture suite**.

Purpose:
- Verifies deterministic diagnostic → proposal mappings
- Ensures proposal IDs and classifications remain stable
- Confirms separation between fact emission and claim emission

This script protects the **NPO v1 contract**.

---

### `run_smoke.py`

Runs a **lightweight smoke test** across representative artifacts.

Purpose:
- Sanity-checks end-to-end wiring
- Confirms discovery, extraction, validation, and reporting work together
- Detects obvious breakage without exhaustive fixture execution

Smoke tests are intentionally minimal and fast.

---

## Design Notes

- Runner scripts are **pure execution drivers**
- No business logic lives here
- All semantics are defined in core modules under `stamp/`
- Output is deterministic and suitable for CI inspection

If a fixture or runner fails, the issue is **always upstream** in core logic.

---

## Usage

These scripts are typically run via:

```bash
python runner/run_fixtures.py
python runner/run_npo_fixtures.py
python runner/run_smoke.py
```

They may be wrapped by CI pipelines or invoked manually during development.

---

<div align="center">
  <sub>© 2026 Waveframe Labs</sub>
</div>
