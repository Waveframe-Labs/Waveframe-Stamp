---
title: "Stamp Operating Model"
filetype: "documentation"
type: "specification"
domain: "documentation"
version: "0.1.0"
doi: "10.5281/zenodo.18436623"
status: "Active"
created: "2026-01-18"
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
ai_assistance_details: "AI-assisted drafting under human architectural control; all operating guarantees, non-goals, and release semantics reviewed and finalized by the author."

dependencies: []

anchors:
  - "STAMP-OPERATING-MODEL-v0.1.0"
---

# Stamp — Operating Model

## 1. Purpose

Stamp is a **schema-agnostic metadata validation and diagnostics engine**.

Its purpose is to **inspect, validate, and reason about metadata** embedded in digital artifacts, while maintaining strict separation between:

- **fact** (what is verifiably true),
- **inference** (what may be proposed),
- **action** (what must be decided elsewhere).

Stamp exists to produce **epistemically clean outputs** that downstream systems may rely on without inheriting hidden assumptions or authority.

---

## 2. Explicit Non-Goals

Stamp is **not**:

- A formatter
- A linter that silently rewrites files
- A policy engine
- A governance authority
- An enforcement mechanism
- A Waveframe-specific tool

Stamp **never** approves, rejects, or legitimizes artifacts.

Any behavior implying silent mutation, enforcement, or institutional authority **violates this operating model**.

---

## 3. Core Capabilities

Stamp MUST be able to:

1. Traverse directories or repositories
2. Discover candidate artifacts deterministically
3. Extract metadata from supported formats
4. Validate metadata against **user-supplied schemas**
5. Emit deterministic diagnostics
6. Propose **safe, mechanical fixes** when explicitly requested
7. Operate without mutating source artifacts by default

All capabilities are opt-in and explicitly invoked.

---

## 4. Execution Modes

Stamp exposes **explicit execution modes**.  
No mode implies another.

### 4.1 `validate` (Default)

**Behavior**
- Extract metadata
- Validate against a supplied schema
- Emit Canonical Diagnostic Objects (CDOs)

**Guarantees**
- Read-only
- Deterministic
- No prescriptions
- No mutation

---

### 4.2 `fix` (Explicit Opt-In)

**Behavior**
- Perform everything in `validate`
- Propose and optionally apply **safe, mechanical fixes only**
  (e.g. removal of disallowed fields)

**Guarantees**
- Never invents data
- Never guesses intent
- Never applies semantic or policy-level changes
- Writes results to a new artifact when applied

Stamp does not decide whether a fix *should* be applied — only whether it is mechanically safe.

---

### 4.3 `extract` (Internal / Supporting)

**Behavior**
- Extract a canonical metadata view only

**Use Cases**
- Indexing
- Analysis
- Integration with downstream tooling

---

## 5. Inputs

Stamp accepts:

- One or more filesystem paths
- One or more JSON Schemas
- Explicit execution flags

Stamp MUST NOT assume:

- A specific schema
- A specific institution
- A specific metadata policy
- A specific governance framework

---

## 6. Outputs

Stamp emits **structured data**, never side effects.

### 6.1 Canonical Diagnostic Objects (CDOs)

- Represent **facts**
- Deterministic
- Schema-validated
- Stable identifiers
- Order-stable

### 6.2 Fix Proposals

- Represent **mechanically safe suggestions**
- Explicitly classified
- Optional
- Never applied without opt-in

---

## 7. Determinism & Traceability

Stamp guarantees:

- Deterministic output ordering
- Stable diagnostic identifiers
- Clear separation of fact vs proposal
- Optional execution traces

These guarantees exist to support:

- Auditability
- Reproducibility
- Downstream enforcement or workflow tooling

---

## 8. Relationship to the Waveframe Labs Ecosystem

Stamp is **tool-agnostic but philosophy-aligned**.

It can be used independently, or as a component within larger systems, including:

- Governance frameworks
- Workflow orchestration tools
- Enforcement engines
- Compliance pipelines

Stamp embeds **no institutional authority**.  
It provides reliable signals that other systems may act upon.

---

## 9. Versioning & Evolution

This operating model is versioned independently of implementation details.

Changes to this document MUST be:

- Explicit
- Logged
- Justified

Breaking semantic changes require clear acknowledgment and version updates.

---

<div align="center">
  <sub>© 2026 Waveframe Labs</sub>
</div>
