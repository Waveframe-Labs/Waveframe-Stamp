# Stamp Implementation Architecture
version: 0.0.1
status: Draft
type: architecture-design
domain: methodology

---

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

## 5

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

## 7. GitHub Action Wrapper

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

## 8. Schema Vendoring Strategy

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

## 9. Repository-Mode vs Single-File Mode

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

## 10. Future API Wrapper Pathway

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

## 11. Test Strategy

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

## 12. Implementation Roadmap

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

