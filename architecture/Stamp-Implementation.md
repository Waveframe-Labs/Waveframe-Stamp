---
title: "Stamp Implementation Architecture"
filetype: "documentation"
type: "specification"
domain: "methodology"
version: "0.0.1"
doi: "TBD-0.0.1"
status: "Draft"
created: "2026-01-16"
updated: "2026-01-16"

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
ai_assistance_details: "AI-assisted drafting and structural refinement under direct human authorship and final approval."

dependencies: []

anchors:
  - "STAMP-IMPLEMENTATION-ARCH-v0.0.1"
---

# Stamp Implementation Architecture

## 1. Overview

Stamp is a deterministic metadata validation and normalization engine designed to apply the rules defined in the ARI Metadata Policy and Schema. This document defines the internal architecture, module structure, execution pipeline, and integration points for a hybrid implementation that supports:

1. a Python-based CLI tool,
2. a GitHub Action wrapper for CI workflows,
3. future expansion into an importable API for programmatic usage.

This architecture ensures that Stamp is modular, testable, and maintainable while supporting multiple deployment patterns.

---

## 2. High-Level Architecture

Stamp’s internal architecture is composed of four layers:

1. **Input Layer**
   - File loading
   - Mode selection (`check` vs `fix`)
   - Optional output directory routing

2. **Validation Layer**
   - Metadata extraction
   - YAML parsing
   - Schema validation (using vendored ARI schema)
   - Error classification (Fatal, Repairable, Warning)

3. **Normalization Layer**
   - Canonical field ordering
   - Structural cleanup
   - Placeholder insertion
   - Timestamp update (only when substantive repairs were made)

4. **Output Layer**
   - Rewritten file (if repairing)
   - Machine-readable report (JSON)
   - Exit code signaling

Each layer operates deterministically and produces no hidden state.

---

## 3. Execution Pipeline

The execution pipeline follows this fixed sequence:

1. **Load file**
2. **Extract metadata block**
3. **Parse YAML**
4. **Validate against ARI Metadata Schema**
5. **Classify errors**
6. **If fatal → stop**
7. **If repairable → normalize**
8. **Reassemble file**
9. **Compute full-file hashes**
10. **Write output (in-place or to output directory)**
11. **Generate JSON validation report**
12. **Return exit code**

All steps MUST be deterministic, reproducible, and side-effect free.

---

## 4. Module Structure

The recommended Python package layout is:

```
src/stamp/
engine/
loader.py
parser.py
validator.py
normalizer.py
reporter.py
dependency_graph.py
cli/
main.py
util/
hashing.py
date.py
filefilters.py
```

### 4.1 engine.loader
- Reads file from disk
- Ensures file is valid text
- Rejects binary or non-text inputs

### 4.2 engine.parser
- Detects YAML frontmatter
- Extracts metadata block
- Parses YAML
- Handles missing metadata block creation

### 4.3 engine.validator
- Validates against ARI Metadata Schema
- Applies error classification logic
- Ensures deterministic validation results

### 4.4 engine.normalizer
- Canonicalizes field order
- Fixes indentation, quoting, list formats
- Inserts placeholders when required
- Updates `updated` timestamp only if repairs occur

### 4.5 engine.dependency_graph
- Only active in repository-mode
- Loads and resolves all dependencies
- Detects circular references

### 4.6 engine.reporter
- Generates JSON output
- Includes full-file hashes
- Logs corrections and validation results

---

## 5. Stamp Error Object Contract (Normative)

Stamp’s primary output is a structured set of diagnostic objects (“errors”) emitted during validation and normalization. This section defines the **canonical error object contract**. This contract is normative and MUST remain stable across validator implementations.

All engine modules that emit diagnostics (schema validation, custom rules, normalization, fixing) MUST produce errors conforming to this contract.

### 5.1 Error Object Purpose

The error object is the sole interface between Stamp and downstream systems (including CRI-CORE). It encodes structural validity, repair semantics, and provenance impact without embedding governance interpretation.

### 5.2 Required Error Fields

Each error MUST include the following fields:

**Identity**
- `code` — Stable, machine-readable error identifier (e.g. `ARI_SCHEMA_REQUIRED_FIELD_MISSING`)
- `message` — Short human-readable summary

**Classification**
- `category` — One of:
  - `STRUCTURAL`
  - `SCHEMA`
  - `PROVENANCE`
  - `GOVERNANCE`
- `severity` — One of:
  - `INFO`
  - `WARNING`
  - `ERROR`
  - `FATAL`

**Repair Semantics**
- `repairable` — boolean
- `auto_fixable` — boolean
- `requires_human_approval` — boolean

**Scope**
- `file_path` — Path of the affected artifact
- `field_path` — JSON Pointer or dotted path to the affected field (nullable)
- `schema_id` — `$id` of the schema used for validation

**Provenance Impact**
- `invalidates_artifact` — boolean
- `invalidates_claim_state` — boolean

**Traceability**
- `source` — One of:
  - `schema`
  - `custom_rule`
  - `normalizer`
  - `fixer`
- `stamp_version` — Stamp version emitting the error
- `timestamp` — ISO-8601 timestamp of detection

### 5.3 Stability Guarantees

- Error object field names and meanings are **ABI-stable**
- New optional fields MAY be added in MINOR versions
- Required fields MUST NOT be removed or redefined without a MAJOR version bump
- Error `code` values MUST remain stable once introduced

### 5.4 Validator Responsibilities

- JSON Schema validators MUST translate raw schema violations into canonical error objects
- Validators MUST NOT invent governance semantics
- Multiple raw validation failures MAY map to multiple error objects

### 5.5 CRI-CORE Consumption

CRI-CORE MUST treat Stamp error objects as authoritative structural diagnostics. CRI-CORE is responsible for all enforcement decisions, claim state transitions, and lifecycle semantics.

Stamp MUST NOT perform enforcement actions beyond emitting errors conforming to this contract.

---

## 6. CLI Architecture

The CLI will route user commands through a single entrypoint:

```
stamp [--check | --fix] [--json] [--output-dir PATH] FILE...
```

### CLI execution flow:

1. Parse arguments
2. Expand file list (respect file masks; default to `*.md`)
3. For each file:
   - Run validation pipeline
   - Apply fixes if `--fix`
   - Print logs or JSON depending on flags
4. Aggregate exit codes
5. Return highest-severity code

The CLI MUST NOT perform any semantic logic not already defined in the engine modules.

---

## 7. Schema Validation and Error Translation

Stamp performs metadata validation by applying the ARI Metadata Schema (JSON Schema, draft 2020-12) as the sole authoritative definition of structural correctness. All validation failures emitted by the JSON Schema engine MUST be translated into Stamp’s canonical error object format before any downstream processing occurs.

Stamp MUST NOT expose raw JSON Schema error output directly to users or downstream systems.

### 7.1 Validation Phases

Schema-based validation occurs in two strictly ordered phases:

1. **Schema Evaluation Phase**
   - The extracted metadata block is validated against the selected ARI Metadata Schema version.
   - Validation enforces:
     - required fields
     - enums
     - regex patterns
     - formats (e.g., date, email, URI)
     - conditional logic (`if` / `then` / `allOf`)
     - `additionalProperties = false`
   - This phase is purely declarative and performs no mutation.

2. **Error Translation Phase**
   - All schema validation failures are translated into Stamp error objects.
   - Translation is deterministic and rule-based.
   - No semantic inference or policy interpretation is performed.

Only translated Stamp error objects may propagate beyond the validation layer.

---

### 7.2 Canonical Error Classification Rules

Each JSON Schema validation failure MUST be mapped to exactly one Stamp error object with the following classification dimensions:

#### Severity Mapping

| Schema Failure Type                                | Stamp Severity |
|---------------------------------------------------|----------------|
| Unknown or additional property                    | FATAL          |
| Invalid enum value                                | FATAL          |
| Invalid regex or format                           | FATAL          |
| Missing required field                            | ERROR          |
| Conditional requirement violation                 | ERROR          |
| Forbidden field present                           | ERROR          |

Severity indicates whether validation may continue and whether the artifact may be considered structurally valid.

---

#### Repairability Mapping

Stamp MUST classify repairability conservatively:

| Condition                                           | Repairable |
|----------------------------------------------------|------------|
| Missing deterministically defaultable fields        | true       |
| Formatting or ordering violations                   | true       |
| Forbidden field that can be safely removed          | true       |
| Missing semantically meaningful content             | false      |
| Enum or pattern violations                          | false      |
| Invalid identifiers (DOI, ORCID, version)           | false      |

Stamp MUST NOT fabricate semantic data under any circumstance.

---

### 7.3 Provenance and Enforcement Semantics

Each translated error MUST explicitly declare its provenance and enforcement implications:

- `source`: always `"schema"` for this phase
- `invalidates_artifact`: true for FATAL errors
- `invalidates_claim_state`: true for FATAL errors
- `requires_human_approval`: true for all non-repairable errors

CRI-CORE MUST be able to determine enforcement actions solely from the translated error objects without re-evaluating the schema.

---

### 7.4 Aggregation and Priority Rules

When multiple schema validation failures occur:

1. All failures MUST be collected and translated.
2. The highest-severity error determines the overall validation outcome.
3. No normalization or fixing MAY occur if any FATAL errors exist.
4. Repairable errors MAY be normalized only after explicit user approval.

Error ordering in reports MUST be stable and deterministic.

---

### 7.5 Stability and Contract Guarantees

The schema-to-error translation rules defined in this section constitute a stable contract.

- Implementations MAY change internal validation libraries.
- Implementations MUST NOT change error classification semantics without a MAJOR version increment.
- CRI-CORE and other downstream systems may rely on this contract as an ABI-level interface.

This guarantees long-term interoperability across tooling layers.

---

## 8. GitHub Action Wrapper

The GitHub Action will:

- bundle a specific Stamp version
- provide standard inputs:
  - `mode` (check/fix)
  - `path` (glob)
  - `output_dir`
  - `json_output`
- call the CLI internally
- expose validation results as:
  - step logs
  - JSON artifacts
  - exit codes for gating

This ensures seamless integration into CI workflows while reusing the same engine as the CLI.

---

## 9. Schema Vendoring Strategy

Stamp MUST:

1. Pin itself to a specific ARI Metadata Schema version (e.g., v3.0.2)
2. Vendor (copy) the schema into the build package under:

```
src/stamp/schema/ari-metadata-3.0.2.json
```

3. NEVER modify this file internally
4. Only update via MINOR or MAJOR version increments

Vendoring ensures:

- offline usage
- deterministic validation
- freedom from network failures
- protection from upstream schema changes

---

## 10. Repository-Mode vs Single-File Mode

### Single-file mode (default)
- Validates structure
- Ensures fields exist
- Ensures fields are valid
- Checks dependency path syntax
- Does NOT detect circular dependencies

### Repository-mode (optional)
- Loads all referenced dependencies
- Builds dependency graph
- Detects circular dependency cycles
- Enforces repository-wide constraints

This dual-mode design prevents false circular detection when Stamp is only given a single file.

---

## 11. Future API Wrapper Pathway

While v0.0.1 does not implement an API wrapper, the architecture supports future expansion:

```
from stamp import validate, normalize
```

Future releases may include:

- direct Python API calls
- metadata manipulation utilities
- integration points for CRI-CORE engine

This ensures long-term extensibility without locking the architecture prematurely.

---

## 12. Test Strategy

Tests MUST verify:

- deterministic normalization
- correct error classification
- accurate schema validation
- stable hash output
- cross-platform consistency
- CLI flag interactions
- GitHub Action wrapper behavior

Test fixtures will include:

- valid metadata samples
- invalid samples
- missing metadata
- circular dependency structures (repo-mode)

---

## 13. Implementation Roadmap

### v0.0.1
- Core engine
- CLI
- GitHub Action wrapper
- Schema vendoring
- Validation + normalization
- Deterministic output

### v0.1.x (MINOR)
- Performance improvements
- Additional warnings
- Optional extended diagnostics

### v1.0.0 (MAJOR)
- Stable API wrapper
- Repository-mode enabled by default
- Optional enterprise features

---

# End of Implementation Architecture  

<div align="center">
  <sub>© 2026 Waveframe Labs — Governed under the Aurora Research Initiative (ARI)</sub>
</div>  

