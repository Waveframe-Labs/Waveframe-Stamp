---
title: "Stamp Specification"
filetype: "specification"
type: "normative"
domain: "methodology"
version: "0.0.1"
doi: "TBD-0.0.1"
status: "Active"
created: "2026-01-11"
updated: "2026-01-11"

author:
  name: "Shawn C. Wright"
  email: "swright@waveframelabs.org"
  orcid: "https://orcid.org/0009-0006-6043-9295"

maintainer:
  name: "Waveframe Labs"
  url: "https://waveframelabs.org"

license: "TBD"

copyright:
  holder: "Waveframe Labs"
  year: "2026"

ai_assisted: "partial"
ai_assistance_details: "AI-assisted drafting under human direction; aligned with ARI Metadata Policy v3.0.1 and schema v3.0.2."

dependencies:
  - "../schemas/ari-metadata-3.0.2.json"

anchors:
  - "STAMP-SPEC-v0.0.1"
---

# Stamp Specification v0.0.1  
**Normative Specification**

## 1. Purpose
Stamp provides deterministic validation, normalization, and injection of YAML metadata blocks for Aurora-governed artifacts. This specification defines the mandatory behavior, validation logic, error-handling rules, and integration boundaries required for compliance with ARI Metadata Policy v3.0.1 and associated schemas.

## 2. Scope
Stamp applies to:

- Markdown documents containing ARI-governed YAML metadata
- metadata blocks requiring validation or correction
- documents that must be prepared for CRI-CORE enforcement
- artifacts destined for Forge (PDF generator)

This specification governs Stamp’s logic, not its implementation details.

---

## 3. Functional Requirements

### 3.1 Metadata Detection
Stamp MUST:
- detect the presence of a YAML frontmatter block
- extract it, parse it, and validate it
- generate a default block when missing

### 3.2 Metadata Validation
Stamp MUST validate all fields required by ARI Metadata Policy v3.0.1, including:
- field presence
- enum correctness
- regex matching
- date formatting
- conditional AI-assistance logic
- semantic versioning
- DOI structure
- ORCID structure

Validation MUST use schema `ari-metadata-3.0.2.json`.

### 3.3 Metadata Normalization
Stamp MUST:
- reorder fields into canonical form
- remove extraneous fields
- standardize quoting
- enforce indentation consistency
- ensure metadata equivalence (meaning unchanged)

### 3.4 Metadata Injection
Stamp MUST automatically:
- create missing fields with placeholder values
- insert DOI placeholders where allowed
- insert `ai_assistance_details` only when required
- generate a valid YAML structure when missing

Stamp MUST NOT:
- fabricate authorship
- fabricate ORCID values
- fabricate version tags

---

## 4. Error Classification

### 4.1 Fatal Errors
Fatal errors MUST cause Stamp to halt processing and return non-compliance:
- missing author object
- invalid DOI format
- invalid ORCID
- circular dependencies
- corrupted YAML

### 4.2 Repairable Errors
Stamp MUST auto-correct:
- missing fields with deterministic defaults
- incorrect field ordering
- indentation issues
- missing anchors
- empty dependency array

### 4.3 Warnings
Stamp MAY warn (but still pass):
- outdated `updated` timestamps compared to file diff
- unusually large dependency lists
- unresolved anchors (non-critical)

---

## 5. Output Requirements

### 5.1 Rewritten File
Stamp MUST output:
- a normalized Markdown file with corrected YAML block
- unchanged body content

### 5.2 Machine-Readable Report
Stamp MUST generate a JSON report containing:
- compliance status (“pass”, “fail”, “repairable”)
- list of violations
- list of corrections applied
- timestamps
- file hash before and after normalization

### 5.3 Exit Codes
Stamp MUST return:
- `0` for clean compliance
- `1` for repairable issues auto-corrected
- `2` for fatal errors and noncompliance

---

## 6. Integration Points

### 6.1 With CRI-CORE
Stamp prepares artifacts for enforcement by:
- guaranteeing metadata completeness
- guaranteeing schema alignment
- producing machine-readable output for downstream validators

Stamp MUST NOT perform enforcement itself.

### 6.2 With Forge
Forge relies on:
- validated metadata
- normalized YAML for PDF header generation

Stamp ensures the document is ready for Forge transformation.

---

## 7. Versioning Rules
Stamp versioning follows:
- **MAJOR**: breaking spec changes
- **MINOR**: new validations/fields
- **PATCH**: internal fixes

---

## 8. Compliance Guarantees
Stamp MUST guarantee:

- deterministic output given the same input
- metadata equivalence after normalization
- reproducible validation and correction steps

---

*End of Specification*

<div align="center">
  <sub>© 2025 Waveframe Labs — Independent Open-Science Research Entity • Governed under the Aurora Research Initiative (ARI)</sub>
</div>
