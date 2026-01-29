---
title: "Stamp"
filetype: "documentation"
type: "specification"
domain: "methodology"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Active"
created: "2026-01-16"
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
ai_assistance_details: "AI-assisted drafting and structural refinement under direct human authorship, review, and final approval."

dependencies: []

anchors: []
---

<p align="center">
  <img src="/figures/STAMP_BANNER.png" alt="Waveframe Stamp Banner" width="650">
</p> 

# Stamp

<p align="center">
  <a href="https://waveframelabs.org">
    <img src="https://img.shields.io/badge/WAVEFRAME%20LABS-Institutional%20Repository-FF6A00?style=flat" />
  </a>
  <img src="https://img.shields.io/badge/version-0.1.0-blue?style=flat" />
  <a href="https://orcid.org/0009-0006-6043-9295">
    <img src="https://img.shields.io/badge/ORCID-0009--0006--6043--9295-A6CE39?logo=orcid&logoColor=white&style=flat" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey?style=flat" />
  </a>
</p>

**Stamp** is a deterministic metadata validation and remediation tool for governed research artifacts.

It validates artifact metadata against a formal schema (e.g. ARI metadata), emits **structured diagnostics**, proposes **safe mechanical fixes**, and produces **human-action remediation summaries** when automation ends.

Stamp is designed to be:

* schema-agnostic
* policy-neutral
* reproducible
* machine- and human-readable

It is a **front door** to governed research workflows — not an enforcement engine.

Stamp does not embed or assume any specific governance policy. All schemas are supplied explicitly at runtime.

---

## What Stamp Is (and Is Not)

### Stamp **is**

* A metadata extractor
* A schema validator
* A diagnostic normalizer (Canonical Diagnostic Objects / CDOs)
* A safe auto-fix engine (conservative by design)
* A human-action explainer (remediation summaries)

### Stamp **is not**

* A policy engine
* A governance authority
* A content validator
* An opinionated formatter
* An enforcement mechanism (that’s CRI-CORE)

Stamp explains **what is wrong**, **what can be fixed automatically**, and **what requires human judgment** — nothing more, nothing less.

---

## High-Level Architecture

Stamp is intentionally layered:

```
Artifact
  ↓
[ Extraction ]
  ↓
[ Schema Resolution ]
  ↓
[ Validation ]
  ↓
[ Diagnostics (CDOs) ]
  ↓
┌───────────────┬───────────────────┐
│ Auto Fix      │ Human Remediation │
│ (safe only)   │ Summary           │
└───────────────┴───────────────────┘
```

Each layer is deterministic and independently testable.

---

## Supported Artifact Types (Current)

* Markdown files with YAML frontmatter
* Code files with ARI metadata embedded in HTML comments

> Stamp does **not** assume a specific file type — only that metadata can be deterministically extracted.

---

## Core Concepts

### Canonical Diagnostic Objects (CDOs)

All validation errors are normalized into **stable, structured diagnostics**.

Each diagnostic includes:

* semantic ID (stable ABI)
* severity
* schema keyword
* instance path
* schema path
* human-readable message
* structured details (when available)
* optional fix capability

This makes diagnostics:

* diffable
* loggable
* machine-actionable
* UI-friendly

---

### Fix Proposals vs Fix Application

Stamp separates **suggestion** from **mutation**.

* `--fix-proposals`
  → describes *possible* fixes (no changes applied)

* `fix apply`
  → applies **only** safe, mechanical fixes  
  → never guesses  
  → never invents data

Example of auto-fixable issue:

* Removing unexpected metadata keys (`additionalProperties`)

Everything else remains human-owned.

---

### Remediation Summaries

When automation stops, Stamp produces a **human-action remediation summary** that classifies:

* what remains broken
* why it’s broken
* who must decide
* what type of decision is required

Action types include:

* `author_decision`
* `governance_decision`
* `disclosure_decision`
* `auto_fixable`

This is designed for:

* researchers
* reviewers
* compliance tooling
* UI presentation

---

## CLI Usage

### Validate an artifact

```bash
python -m stamp.cli.main validate run artifact.md \
  --schema ari-metadata.schema.v3.0.2.json
```

### Get a validation summary

```bash
python -m stamp.cli.main validate run artifact.md \
  --schema ari-metadata.schema.v3.0.2.json \
  --summary
```

### See fix proposals

```bash
python -m stamp.cli.main validate run artifact.md \
  --schema ari-metadata.schema.v3.0.2.json \
  --fix-proposals
```

### Apply safe fixes

```bash
python -m stamp.cli.main fix apply artifact.md \
  --schema ari-metadata.schema.v3.0.2.json \
  --out artifact.fixed.md
```

### Human remediation summary

```bash
python -m stamp.cli.main validate run artifact.md \
  --schema ari-metadata.schema.v3.0.2.json \
  --remediation
```

### Validate a repository or directory

```bash
python -m stamp.cli.main validate repo path/to/repo \
  --schema ari-metadata.schema.v3.0.2.json
```

Only artifacts that explicitly declare metadata are considered governed and validated.  
Files without metadata are discovered but intentionally ignored.

Execution traces created via `--trace-out` are immutable execution evidence and are intentionally excluded from metadata governance and validation.

> **Windows note:** On PowerShell, JSON output can be piped through  
> `ConvertFrom-Json | ConvertTo-Json -Depth 10` instead of `jq`.

---

## Design Principles

* **Determinism over convenience**
* **Traceability over magic**
* **No self-approval**
* **Separation of validation, fixing, and judgment**
* **Format-agnostic governance**

Stamp should always be boring, predictable, and explainable.

---

## Roadmap (Near-Term)

* HTML-comment metadata extraction for additional code file types
* Minimal Streamlit UI (paste → validate → explain)
* Public v0.1.x hardening (UX polish, docs, edge cases)
* CRI-CORE integration (enforcement layer)

---

## Status

> Actively developed  
> Internal coherence phase  
> Architecture stable, contracts stabilizing

---

## Citation

If you use **Stamp** in academic work, tooling research, or technical documentation, please cite it as follows.

### BibTeX

```bibtex
@software{stamp_2026,
  title        = {Stamp: A Schema-Agnostic Structural Diagnostics Engine},
  author       = {Wright, Shawn C.},
  year         = {2026},
  version      = {0.1.0},
  publisher    = {Waveframe Labs},
  url          = {https://github.com/waveframelabs/stamp},
  doi          = {TBD}
}
```

**Stamp is developed and maintained by Waveframe Labs under internal governance standards.**  

---  

<div align="center">
  <sub>© 2026 Waveframe Labs</sub>
</div>
