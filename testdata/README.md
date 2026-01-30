---
title: "Stamp — Test Data"
filetype: "documentation"
type: "reference"
domain: "testing"
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

ai_assisted: "none"

dependencies: []

anchors: []
---

# testdata/

This directory contains **minimal, non-normative test inputs** used for local testing, debugging, and development sanity checks.

These files are intentionally simple and are **not** part of Stamp’s formal fixture or contract validation system.

---

## Contents

### `artifact.json`

A minimal JSON artifact used to test:

- basic metadata extraction paths
- error handling for missing or malformed fields
- local validation workflows during development

This file is not schema-complete and is **not intended to pass validation**.

---

### `schema.json`

A minimal JSON Schema used to test:

- schema loading and resolution
- validation plumbing
- error propagation and diagnostics formatting

This schema is intentionally incomplete and **not a normative schema**.

---

## Important Distinction

This directory is **not** a fixture suite.

- **Fixtures** (`fixtures/`) are contract-level, versioned, and relied upon for correctness guarantees.
- **Test data** (`testdata/`) is ad hoc, mutable, and intended only for development convenience.

Downstream tooling **must not** rely on files in this directory for correctness or compatibility guarantees.

---

<div align="center">
  <sub>© 2026 Waveframe Labs</sub>
</div>
