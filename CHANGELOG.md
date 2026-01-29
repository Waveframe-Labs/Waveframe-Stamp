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

anchors:
  - STAMP-CHANGELOG-v0.1.0
---

# Stamp — Change Log

This document records **material design decisions, contract freezes, and layer-level milestones** for the Stamp project.

It is **not a release log** and does **not imply end-user readiness**.

Its purpose is to provide an auditable history of how the Stamp layer reached its current form, such that downstream systems (notably **CRI-CORE**) may rely on its guarantees without re-interpreting intent.

---

## [Unreleased] — Stamp Core Layer (v0.1.x)

> Core architecture complete. Contracts stabilizing. UX hardening in progress.

### Added

#### Core Validation & Diagnostics

- Canonical Diagnostic Object (CDO) v1 schema
- Deterministic normalization of all `jsonschema` errors into CDOs
- Stable diagnostic IDs suitable for ABI-level reliance
- Full preservation of:
  - schema keyword
  - instance path
  - schema path
  - semantic error meaning

#### Fix & Remediation Model

- Normalization Proposal Object (NPO) v1 schema
- Deterministic diagnostic → proposal mapping
- Explicit separation between:
  - **fact emission** (validation)
  - **claim emission** (fix proposals)
  - **judgment** (human remediation)

#### CLI & Execution Semantics

- `validate run` — single-artifact validation
- `validate repo` — governed-repository validation
- Governance gate: only artifacts that **explicitly declare metadata** are validated
- Structured JSON output for:
  - diagnostics
  - summaries
  - fix proposals
  - remediation summaries
- Pipeable, deterministic CLI output suitable for tooling (`jq`, PowerShell, CI)

#### Execution Trace Artifacts

- Deterministic execution trace artifact format (`ExecutionTrace`)
- Machine-validated trace schema
- Trace artifacts treated as **immutable execution evidence**
- Explicit exclusion of trace artifacts from metadata governance
- Support for committing traces under `traces/` as audit records

#### Discovery & Extraction

- Deterministic artifact discovery with exclusion rules
- Explicit metadata extraction precedence:
  1. Markdown YAML frontmatter
  2. HTML-comment metadata
  3. Ungoverned (ignored)
- No heuristic guessing or fallback inference

---

### Frozen (Normative Contracts)

The following behaviors are now **contractually frozen** for Stamp v1:

#### Diagnostic Contract (CDO)

- Diagnostics represent **facts only**
- No inferred intent
- No policy interpretation
- No mutation logic

#### Fix Proposal Contract (NPO)

- Proposals represent **claims**, not actions
- Proposal IDs are deterministic and hash-derived
- Flat proposal lists (no ordering, no execution semantics)

#### Governance Boundaries

- Validation, fixing, and enforcement are strictly decoupled
- Stamp never:
  - applies fixes implicitly
  - approves changes
  - enforces policy
  - mutates artifacts without explicit user command

These guarantees are relied upon by downstream enforcement layers.

---

### Explicit Non-Goals (Reaffirmed)

Stamp **will not**:

- Validate artifact *content*
- Interpret policy or governance intent
- Enforce compliance decisions
- Manage approvals, workflows, or signatures
- Integrate enforcement logic (delegated to CRI-CORE)

Stamp stops **exactly** where human or institutional judgment begins.

---  

## [2026-01-29] — Packaging, CLI Identity, and Documentation Hardening

### Added

- Formalized Python packaging via `pyproject.toml`
  - Declared canonical project metadata
  - Defined console script entrypoint (`stamp`)
  - Enabled `pip install -e .` and PATH-based CLI usage
- Established **JSON-first CLI output contract**
  - All structured CLI output (diagnostics, summaries, remediation, proposals) now emits explicit JSON
  - Output is deterministic, pipeable, and shell-agnostic
- Added execution trace governance semantics
  - Trace artifacts defined as immutable execution evidence
  - Explicit exclusion of trace artifacts from metadata governance
  - Standardized trace storage under `traces/`

### Changed

- Renamed project identity to **`waveframe-stamp`** to avoid namespace collision with an existing PyPI package
- Standardized tool identity and version reporting across:
  - CLI output
  - Execution traces
  - Internal constants
- Updated README to serve as the **authoritative entry point** for:
  - Purpose and scope
  - Governance boundaries
  - CLI usage
  - Shell compatibility
  - Installation and quick start guidance

### Clarified

- Distinguished between:
  - **Repository cloning** vs **package installation**
  - **Validation tooling** vs **enforcement layers**
- Documented shell compatibility explicitly:
  - Bash / zsh (`jq`)
  - PowerShell (`ConvertFrom-Json`)
  - CI and automation environments
- Confirmed that Stamp is a **front-door validation layer**, not a policy authority or enforcement engine

### Deferred

- Public PyPI publication (pending final naming, license confirmation, and release tagging)
- DOI finalization (to be updated post-release)
- Formal release tagging (blocked on documentation and integration readiness)

This entry reflects a transition from internal prototyping to a
**stable, externally-consumable CLI tool with frozen core contracts**.

---

## [2026-01-29] — Core Architecture Lock-In

### Milestones

- Completed end-to-end repository validation with governed-only semantics
- Confirmed deterministic behavior across:
  - discovery
  - extraction
  - validation
  - diagnostics
  - trace generation
- Standardized tool identity and version reporting
- Normalized all CLI structured output to JSON
- Finalized README as authoritative architectural explanation

### Outcome

Stamp is now a **stable, boring, explainable front door** to governed research workflows.

---

## [2026-01-18] — Architecture & Contract Finalization (Initial)

- Completed stress-testing of mechanical, inferred, ambiguous, and prohibited normalization scenarios
- Formalized epistemic classifications for normalization proposals
- Locked governance boundary between:
  - Facts (CDO)
  - Claims (NPO)
- Declared readiness to serve as an upstream dependency for CRI-CORE

---

## Status

- **Layer completeness:** Achieved
- **Core contracts:** Frozen (v1)
- **Execution semantics:** Stable
- **Trace artifacts:** Enabled
- **Documentation:** Complete
- **Release tag:** Pending (post-integration)

Stamp is no longer exploratory. Remaining work is polish, UX, and integration.

---

<div align="center">
  <sub>© 2026 Waveframe Labs — Governed under the Aurora Research Initiative (ARI)</sub>
</div>
