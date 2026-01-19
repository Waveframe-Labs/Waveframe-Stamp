---
title: "Stamp Operating Model"
filetype: "documentation"
type: "normative"
domain: "documentation"
version: "0.0.1"
doi: "TBD-0.0.1"
status: "Draft"
created: "2026-01-18"
updated: "2026-01-18"

author:
  name: "Shawn C. Wright"
  email: "swright@waveframelabs.org"
  orcid: "https://orcid.org/0009-0006-6043-9295"

maintainer:
  name: "Waveframe Labs"
  url: "https://waveframelabs.org"

license: "NOASSERTION"

copyright:
  holder: "Waveframe Labs"
  year: "2026"

ai_assisted: "partial"
ai_assistance_details: "AI-assisted drafting under human architectural control; all architectural decisions validated and finalized by the author."

dependencies: []

anchors:
  - "STAMP-OPERATING-MODEL-v0.0.1"
---

# Stamp — Operating Model

## 1. Purpose

Stamp is a **schema-agnostic metadata engine** designed to **inspect, validate, and reason about metadata** in digital artifacts without enforcing or mutating them by default.

Stamp exists to produce **epistemically clean outputs**:

- **Facts** about compliance (Canonical Diagnostic Objects — CDOs)
- **Claims** about possible remediation (Normalization Proposal Objects — NPOs)

Stamp does **not** decide legitimacy, authority, or approval.
It produces structured information that downstream systems may act upon.

---

## 2. Non-Goals (Explicit)

Stamp is **not**:

- A formatter
- A linter that rewrites files silently
- A policy enforcement engine
- A governance authority
- A Waveframe-only tool

Any behavior implying enforcement, mutation, or approval **violates this model**.

---

## 3. Core Capabilities

Stamp MUST be able to:

1. Traverse repositories or directories
2. Discover candidate artifacts
3. Extract metadata from supported formats
4. Validate metadata against **user-supplied schemas**
5. Emit deterministic diagnostics (CDO)
6. Optionally emit normalization proposals (NPO)
7. Operate without mutating source artifacts

---

## 4. Execution Modes

Stamp exposes **explicit execution modes**. No mode implies another.

### 4.1 `validate` (Default)

**Behavior**
- Extract metadata
- Validate against schema
- Emit CDOs only

**Guarantees**
- Read-only
- Deterministic
- No prescriptions

---

### 4.2 `normalize` (Explicit Opt-In)

**Behavior**
- Perform everything in `validate`
- Generate NPOs based on CDOs and internal heuristics

**Guarantees**
- Still read-only
- No mutation
- No enforcement
- Proposals may require approval or be prohibited

---

### 4.3 `extract` (Internal / Supporting)

**Behavior**
- Extract canonical metadata view only

**Use Cases**
- Indexing
- Forge integration
- Downstream analysis

---

## 5. Inputs

Stamp accepts the following inputs:

- One or more filesystem paths
- One or more JSON Schemas (any domain)
- Optional execution flags (mode selection)

Stamp MUST NOT assume:
- A specific schema
- A specific institution
- A specific metadata policy

---

## 6. Outputs

Stamp emits **structured data**, never side effects.

### 6.1 Canonical Diagnostic Objects (CDO)

- Represent **facts**
- Deterministic
- Schema-validated
- Order-stable

### 6.2 Normalization Proposal Objects (NPO)

- Represent **claims**
- Optional
- Epistemically classified:
  - mechanical
  - inferred
  - ambiguous
  - prohibited
- Never applied automatically by Stamp

---

## 7. Determinism & Traceability

Stamp guarantees:

- Stable output ordering
- Deterministic identifiers
- Schema-validated outputs
- Clear separation of fact vs inference

These guarantees exist to support:
- CRI-CORE enforcement
- Auditability
- Trust without authority

---

## 8. Relationship to the Waveframe Labs Ecosystem

Stamp is **tool-agnostic but philosophy-aligned**.

- It can be used independently
- It embeds no institutional assumptions
- It is designed to integrate with:
  - ARI (governance)
  - NTD / NTS (AI traceability)
  - AWO (workflow orchestration)
  - CRI-CORE (enforcement)

Stamp does not require these systems — but they require Stamp-like guarantees.

---

## 9. Versioning & Evolution

This operating model is versioned independently of implementation.

Changes to this document MUST be logged and justified.
Breaking changes require explicit governance acknowledgment.

---

<div align="center">
  <sub>© 2026 Waveframe Labs — Governed under the Aurora Research Initiative (ARI)</sub>
</div>
