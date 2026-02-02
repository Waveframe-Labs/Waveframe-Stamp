---
title: "Stamp — Getting Started"
filetype: "documentation"
type: "guidance"
domain: "methodology"
version: "0.1.1"
doi: "10.5281/zenodo.18436623"
status: "Active"
created: "2026-01-29"
updated: "2026-02-01"

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
ai_assistance_details: "AI-assisted drafting of onboarding structure and examples, with human-authored technical content, review, and final approval."

dependencies: []  

anchors: []
---

# Getting Started with Stamp

This guide walks you through using **Stamp** for the first time, from installation to validating your first artifact.

Stamp is a **deterministic metadata validation tool**. It checks that artifact metadata conforms to a schema you provide and produces structured, machine-readable results.

---

## Prerequisites

- Python **3.10+**
- A shell environment (PowerShell, Bash, zsh, etc.)
- No external tools required (JSON processors are optional)

---

## Installation

### Option A — Install from PyPI (recommended once released)

```bash
pip install waveframe-stamp
```

This installs the `stamp` CLI on your PATH.

Verify:

```bash
stamp --help
```

---

### Option B — Clone and run locally (current development workflow)

```bash
git clone https://github.com/Waveframe-Labs/Waveframe-Stamp.git
cd Waveframe-Stamp
pip install -e .
```

This installs Stamp in editable mode and exposes the `stamp` command locally.

---

## Your First Validation

### Validate a single artifact

The `--schema` argument must point to a local JSON Schema file path (relative or absolute).
Stamp does not download schemas automatically.

```bash
stamp validate run artifact.md   --schema ari-metadata.schema.v3.0.2.json
```

Output is **explicit JSON** describing validation diagnostics.

---

### Get a summary instead of full diagnostics

The summary output returns only pass/fail counts and artifact totals.

```bash
stamp validate run artifact.md   --schema ari-metadata.schema.v3.0.2.json   --summary
```

---

### Validate an entire repository

```bash
stamp validate repo .   --schema ari-metadata.schema.v3.0.2.json
```

Only artifacts that **explicitly declare metadata** are considered governed and validated.

---

## Understanding Output

All Stamp commands emit **JSON to stdout**.

This makes output:

- Scriptable
- Pipeable
- Deterministic
- CI-friendly

### PowerShell example

```powershell
stamp validate repo . --schema ari-metadata.schema.v3.0.2.json |
  ConvertFrom-Json |
  ConvertTo-Json -Depth 10
```

### Bash / macOS example (optional)

```bash
stamp validate repo . --schema schema.json | jq
```

> JSON processors like `jq` are optional. Stamp itself does not depend on them.

---

## Execution Traces

Stamp can emit **immutable execution trace artifacts** for audit and reproducibility.

The output directory must already exist.

```bash
stamp validate repo .   --schema schema.json   --trace-out stamp-validation-trace.json
```

Trace files:

- Are machine-validated
- Are excluded from metadata governance
- May be committed as audit evidence

---

## What Stamp Does *Not* Do

Stamp intentionally does **not**:

- Enforce policy
- Approve changes
- Modify artifacts without explicit command
- Guess missing data

Stamp stops where **human or institutional judgment** begins.

---

## Next Steps

- Read the main README for architectural details
- Explore `fixtures/` for example diagnostics
- Use `--fix-proposals` and `--remediation` to understand next actions
- See `RELEASING.md` if you are maintaining Stamp itself

---

© 2026 Waveframe Labs
