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

# Stamp Specification  
**Normative Specification**

## 1. Purpose

Stamp exists to deterministically validate, normalize, and generate YAML metadata blocks for all governed artifacts within the Aurora ecosystem. It ensures that documents meet the structural and semantic requirements of the ARI Metadata Policy, removing ambiguity and guaranteeing machine-readability. By producing standardized and complete metadata, Stamp allows downstream systems—particularly CRI-CORE and Forge—to operate without reinterpreting or repairing document structure. Stamp defines and applies the rules that govern metadata layout but does not itself perform compliance enforcement; it prepares artifacts for enforcement by ensuring correctness and reproducibility at the metadata level.

---  
## 2. Scope

Stamp applies to all governed artifacts within the Aurora ecosystem that rely on YAML metadata blocks for provenance, traceability, and compliance. Its scope includes Markdown files that contain ARI-governed frontmatter, documents requiring metadata generation or correction, and artifacts intended for downstream processing by CRI-CORE or Forge.

Stamp governs three domains of behavior:

1. **Validation** — ensuring metadata completeness, correctness, structure, and semantic alignment with the ARI Metadata Policy and associated schemas.
2. **Normalization** — rewriting metadata into canonical form without altering meaning, ensuring deterministic formatting and equivalence across repositories.
3. **Injection** — generating required fields, placeholders, and structural elements when missing, enabling artifacts to meet minimum compliance prerequisites.

Stamp does not define policy, determine compliance outcomes, enforce repository rules, or perform any substantive review of document content. Its function is strictly structural and preparatory: ensuring that metadata is machine-readable, complete, and ready for enforcement and publication workflows.

---

## 3. Functional Requirements

Stamp MUST implement three primary functional domains: metadata detection, metadata validation, and metadata normalization/injection. These domains collectively ensure that all governed artifacts meet ARI metadata requirements and are prepared for downstream enforcement and publication.

---

### 3.1 Metadata Detection

Stamp MUST:

- detect the presence of a YAML frontmatter block at the beginning of a Markdown file;
- correctly identify the boundaries of the metadata block (`---` fences);
- extract and parse the YAML content into a structured representation;
- gracefully handle missing, malformed, or partially corrupted metadata blocks;
- create a new metadata block when none is present.

Detection failures SHOULD be recoverable unless the file structure is invalid in a way that prevents safe parsing.

---

### 3.2 Metadata Validation

Stamp MUST validate all YAML metadata fields in accordance with the ARI Metadata Policy v3.0.1 and ARI Metadata Schema v3.0.2. Validation MUST include:

- **required fields** — verifying that all mandatory fields are present;
- **value domains** — ensuring fields use approved enums (filetype, type, domain, status);
- **regex constraints** — enforcing DOI, ORCID, and version formatting;
- **date formats** — ensuring ISO-8601 formatting for created/updated;
- **immutability rules** — preventing changes to the `created` field once set;
- **conditional rules** — verifying ai_assisted/ai_assistance_details relationships;
- **dependency resolution** — ensuring paths are relative and resolvable;
- **anchor format** — enforcing anchor naming and uniqueness.

Validation MUST produce a machine-readable report detailing errors, their severity, and whether they are repairable.

---

### 3.3 Metadata Normalization

Stamp MUST:

- reorder metadata fields into a canonical sequence;
- standardize quotation style and indentation;
- remove unrecognized or disallowed fields;
- enforce consistent list formatting for arrays;
- normalize date formatting while preserving `created` immutability;
- rewrite YAML in a way that preserves semantic equivalence.

Normalization MUST NOT alter the meaning or authority level of the document.

---

### 3.4 Metadata Injection

Stamp MUST:

- insert missing required fields using deterministic defaults;
- generate placeholder DOIs using the `TBD-X.Y.Z` format when appropriate;
- insert `ai_assistance_details` only when required by ai_assisted state;
- generate empty but valid arrays for dependencies and anchors when absent.

Stamp MUST NOT:

- fabricate authorship, ORCID identifiers, or false provenance;
- invent version values or override declared semantic versioning.

---

### 3.5 Deterministic Output

For any given input, Stamp MUST produce the same normalized output across:

- repeated runs,
- different environments,
- different execution contexts.

Determinism is a hard requirement because CRI-CORE and Forge depend on stable metadata structures.

---

### 3.6 Non-Goals

Stamp MUST NOT:

- enforce compliance outcomes (CRI-CORE responsibility);
- interpret or validate document body content;
- resolve external references beyond dependency paths;
- perform semantic analysis of text or logic.

Stamp’s responsibility ends once valid metadata is structurally and semantically complete.

---

## 4. Error Classification

Stamp MUST classify all metadata issues into three categories: Fatal Errors, Repairable Errors, and Warnings. This classification determines how Stamp processes the artifact, what corrections may be applied, and what status codes are returned to downstream systems such as CRI-CORE.

Error classification MUST be deterministic and based solely on structural and semantic metadata rules defined by the ARI Metadata Policy and Schema. Stamp MUST NOT infer user intent or alter content beyond what is necessary to repair or normalize metadata structure.

---

### 4.1 Fatal Errors

Fatal errors represent violations that prevent a document from being brought into compliance through automated correction. When a fatal error is encountered, Stamp MUST:

- halt processing,
- refrain from modifying the file,
- output a noncompliant status,
- return exit code `2`,
- include all fatal violations in the machine-readable report.

Fatal errors include:

- missing or invalid `author` object;
- invalid DOI that does not match Zenodo or placeholder patterns;
- invalid ORCID format;
- malformed YAML that cannot be parsed safely;
- circular dependencies in the dependency graph;
- invalid `type`, `domain`, `filetype`, or `status` values not in the allowed enumerations;
- missing required fields that cannot be safely defaulted.

Fatal errors MUST NOT be auto-corrected.

---

### 4.2 Repairable Errors

Repairable errors represent metadata issues that Stamp CAN correct deterministically without risking semantic misinterpretation or violating provenance rules. When repairable errors are detected, Stamp MUST:

- apply the appropriate correction,
- rewrite the metadata block,
- preserve semantic equivalence,
- return exit code `1`,
- report all corrections in the machine-readable summary.

Repairable errors include:

- missing fields that can be deterministically defaulted (e.g., missing `anchors`, empty dependency lists);
- incorrect field ordering;
- indentation inconsistencies;
- missing YAML fences;
- missing DOI placeholder when version is unreleased;
- missing `ai_assistance_details` when ai_assisted = partial/extensive;
- outdated `updated` date (may be auto-updated).

Stamp MUST ensure corrections do not fabricate authorship, provenance, or version data.

---

### 4.3 Warnings

Warnings represent situations where metadata is valid and compliant but may indicate unusual or potentially unintended patterns. When warnings occur, Stamp MUST:

- allow the file to pass unmodified,
- return exit code `0`,
- include warnings in the machine-readable report.

Warnings include:

- unusually large numbers of declared dependencies;
- unresolved anchors that do not correspond to known files (non-fatal);
- future-dated `updated` timestamps;
- empty or placeholder DOIs for older documents (allowed but suboptimal).

Warnings MUST NEVER cause Stamp to halt processing or rewrite the document.

---

### 4.4 Error Interaction Rules

Stamp MUST enforce the following rules when multiple error types are present:

- Any presence of a Fatal Error overrides all other classifications and halts processing.
- If no Fatal Errors exist but one or more Repairable Errors exist → Stamp MUST repair and continue.
- If only Warnings exist → Stamp MUST allow the document to pass without modification.

Stamp MUST apply error categories in the following priority order:

1. Fatal Error
2. Repairable Error
3. Warning

This ordering prevents partial correction of a document that is fundamentally invalid.

---

### 4.5 Reporting Requirements

For every run, Stamp MUST produce a machine-readable error report containing:

- error classification;
- list of individual issues grouped by category;
- whether auto-corrections were applied;
- final compliance status;
- exit code.

This report is used by CRI-CORE for enforcement and by Forge for publication preprocessing.

---

## 5. Output Requirements

Stamp MUST produce two primary outputs for every processed artifact: (1) a normalized version of the file when repairs are required, and (2) a machine-readable validation report that summarizes all detected issues, corrections applied, and the final compliance status. These outputs ensure that downstream systems—particularly CRI-CORE and Forge—can operate deterministically without interpreting or revalidating metadata structures.

No hidden state, temporary transformations, or non-reproducible modifications may influence output.

---

### 5.1 Normalized File Output

When repairable errors are present, Stamp MUST produce a rewritten file with the YAML metadata block normalized according to canonical formatting rules. The rewritten file MUST:

- preserve semantic equivalence with the original metadata,
- retain all user-authored content outside the metadata block,
- use the canonical field ordering as defined by ARI Metadata Policy,
- correct structural issues (indentation, quoting, list formats),
- inject required fields with deterministic placeholder values when appropriate.

Stamp MUST NOT alter the body content of the document. Only the metadata block may be modified.

If the input file is already compliant and no repairs are required, Stamp MUST NOT rewrite the file.

---

### 5.2 Validation Report (Machine-Readable)

For every run, Stamp MUST generate a machine-readable validation report in JSON format. The report MUST include:

- `status`: `"pass"`, `"repairable"`, or `"fail"`;
- `exit_code`: integer value corresponding to error class;
- `fatal_errors`: list of violations classified as fatal;
- `repairable_errors`: list of issues corrected by Stamp;
- `warnings`: list of non-fatal advisories;
- `corrections_applied`: list of transformations made to metadata;
- `original_hash`: SHA-256 hash of input file;
- `rewritten_hash` (if rewritten): SHA-256 hash of normalized output file;
- `timestamp`: ISO-8601 timestamp of validation run.

The report MUST be generated even if the document passes with no warnings.

---

### 5.3 Exit Codes

Stamp MUST return deterministic exit codes based on the highest-severity condition encountered:

- `0` — clean compliance (no errors, no warnings or warnings only)
- `1` — repairable issues were automatically corrected
- `2` — fatal errors encountered; document is noncompliant and cannot be processed

Exit codes MUST be the sole determinant of downstream gating behavior in CI/CD pipelines.

---

### 5.4 Output Directory Rules

Stamp MUST support two output modes:

1. **In-place mode**  
   - Rewrites the file directly when repairs are required.
   - Non-destructive, preserving original formatting in the body.

2. **Output directory mode**  
   - Writes the normalized file to a designated output directory.
   - Leaves original input untouched.

For CLI and GitHub Action usage, providing an explicit output directory MUST switch Stamp to non-destructive mode by default.

---

### 5.5 Log Output (Human-Readable)

Stamp SHOULD provide optional human-readable log output to stdout or stderr containing:

- summary of validation process,
- description of corrections applied,
- warnings and advisory messages.

Log output MUST NOT contain any information absent from the machine-readable report.

---

### 5.6 No Hidden State

Stamp MUST NOT:

- generate temporary files not reported in the validation summary,
- store or rely on local caches,
- behave differently across runs with identical inputs.

Determinism and reproduceability are mandatory so that CRI-CORE can depend on Stamp as a pre-validation contract.

---

### 5.7 Non-Modification Guarantee

If no repairable errors exist, Stamp MUST:

- leave the file unmodified,
- return exit code `0`,
- still generate a complete validation report,
- still produce a SHA-256 input hash.

This guarantees that Stamp can be safely used as a pre-commit or CI validation tool without rewriting compliant files.

---

## 6. Integration Points

Stamp serves as the metadata substrate generator and pre-validation layer for the Aurora ecosystem. Its output provides the structural guarantees required by downstream systems, enabling them to operate deterministically without duplicating metadata logic. This section defines the mandatory integration boundaries between Stamp and other Aurora components.

Stamp MUST NOT perform enforcement or publication functions. Its role is strictly preparatory and structural.

---

### 6.1 Integration with CRI-CORE

CRI-CORE is responsible for enforcement of compliance rules and validation of independence, provenance, reproducibility, and governance constraints. Stamp does not perform enforcement; it only prepares artifacts so CRI-CORE can do so reliably.

Stamp MUST:

- output machine-readable validation reports that CRI-CORE can consume directly;
- use deterministic exit codes (`0`, `1`, `2`) for CI gating;
- ensure that all metadata fields required by ARI Metadata Policy are present and structurally correct;
- guarantee that metadata formatting is canonical, preventing ambiguity during enforcement;
- guarantee that YAML structure is valid and machine-parseable.

Stamp MUST NOT:

- attempt to enforce independence rules,
- make judgment about compliance outcomes,
- modify or interpret the document body,
- override CRI-CORE enforcement decisions.

CRI-CORE MUST rely on Stamp to ensure metadata correctness before enforcement is attempted.

---

### 6.2 Integration with Forge

Forge is the publication engine responsible for generating scholar-grade PDFs and applying metadata to outputs. Forge expects fully validated, normalized metadata blocks and MUST NOT perform structural metadata repair.

Stamp MUST:

- guarantee that metadata is complete before Forge is invoked;
- normalize all fields to canonical order and formatting;
- ensure valid DOIs are present or placeholder DOIs inserted when allowed;
- enforce AI assistance disclosure requirements so Forge can include them in output formatting.

Stamp MUST NOT:

- generate publication artifacts,
- render or format document content,
- perform PDF transformations.

Forge MUST rely on Stamp to ensure schema-aligned metadata before rendering.

---

### 6.3 Integration with AWO Workflows

Stamp is a preprocessing step in AWO pipelines and MUST integrate without modifying workflow semantics. In AWO v2.0.0, metadata validation is required before workflow execution.

Stamp MUST:

- operate as a standalone CLI for integration into AWO-defined pipelines;
- support in-place and output-directory modes for flexible workflow design;
- provide deterministic exit codes for automated workflow gating;
- ensure YAML parsing behavior is consistent across environments.

Stamp MUST NOT:

- redefine workflow steps,
- create workflow logs,
- modify execution provenance outside metadata.

AWO workflows MUST treat Stamp as a required gate for structural metadata validity.

---

### 6.4 Integration with External Tools and CI/CD Pipelines

Stamp MUST support use in:

- GitHub Actions,
- local development workflows,
- pre-commit hooks,
- continuous integration pipelines,
- build pipelines for publication.

Stamp MUST:

- provide a CLI interface with predictable flags and behaviors;
- optionally output normalized files to a separate directory;
- provide JSON reports consumable by automation systems;
- exit with deterministic codes for CI gating;
- operate without external network calls or dependencies.

Stamp MUST NOT:

- introduce environmental variability,
- require persistent external services,
- rely on caching or non-reproducible state.

This ensures predictable integration in both open-source and enterprise contexts.

---

### 6.5 Integration Boundaries Summary

Stamp guarantees:

- **structural validity** of metadata,
- **semantic alignment** with ARI/NTS schemas,
- **deterministic normalization** across all runs,
- **machine-readable reports** for downstream tools.

CRI-CORE enforces compliance.  
Forge produces publication outputs.  
Stamp simply prepares the metadata substrate both systems depend on.

---

## 7. Versioning Rules

Stamp MUST follow semantic versioning (`MAJOR.MINOR.PATCH`) and apply version increments based on the nature of changes to the specification or implementation. Version increments MUST reflect the impact of changes on downstream tools, repository metadata, and reproducibility guarantees. Stamp MUST NOT change behavior in ways that violate earlier version contracts without a corresponding MAJOR version increase.

---

### 7.1 MAJOR Version Changes

A MAJOR version increment MUST occur when:

- breaking changes are introduced to metadata validation behavior;
- new required fields are added to ARI Metadata Policy or Schema;
- the canonical ordering of metadata fields changes;
- backward-incompatible rules are introduced for AI-assistance logic;
- error classification semantics change in ways that break prior tooling.

MAJOR increments represent contract-breaking changes.  
CRI-CORE and Forge MUST be updated accordingly before or alongside rollout.

---

### 7.2 MINOR Version Changes

A MINOR version increment MUST occur when:

- new non-breaking validation rules are added;
- new optional fields become recognized or normalized;
- additional warnings or advisory checks are implemented;
- new CLI features or modes are added without changing core behavior;
- performance improvements or internal optimizations are introduced;
- **default placeholder values are modified in a way that changes normalized output for previously-compliant files.**

MINOR changes MUST NOT:

- alter exit codes for pre-existing conditions,
- change required fields,
- change canonical ordering,
- break deterministic output for previously-compliant metadata.

MINOR increments represent additive expansion without breaking compatibility.

---

### 7.3 PATCH Version Changes

A PATCH version increment MUST occur when:

- implementation bugs are fixed;
- formatting inconsistencies are corrected;
- validation edge cases are resolved without changing semantics;
- **default placeholder values are updated in ways that do not alter the normalized output for previously-compliant files**;
- internal code refactors preserve identical external behavior.

PATCH changes MUST produce identical results to prior versions for all compliant inputs.

---

### 7.4 Version Pinning and Schema Alignment

Stamp MUST:

- reference a specific version of the ARI Metadata Schema;
- fail gracefully when invoked with documents requiring unsupported schema versions;
- clearly report schema-version mismatches as warnings or fatal errors depending on compatibility.

Stamp MUST NOT automatically upgrade or reinterpret metadata according to newer schema versions without explicit user request or configuration.

---

### 7.5 Deterministic Upgrade Path

Upgrading Stamp versions MUST NOT:

- change output formatting for already-normalized metadata (unless MAJOR version);
- introduce nondeterminism or environment-specific differences;
- require manual migration for compliant files.

If a future version introduces changes requiring migration, Stamp MUST provide:

- a deterministic migration mode,
- a report specifying required changes,
- a clear indication of which rules triggered migration.

---

### 7.6 Version Declaration in Metadata

Every governed file processed by Stamp MUST contain:

- `version`: the document’s own version  
- NOT the version of Stamp

Stamp MUST NOT insert or modify the document’s semantic version unless explicitly invoked with a version-bump mode.

Stamp MAY include its own version in the validation report, but MUST NOT alter the metadata of the document to reflect Stamp’s version.

---

### 7.7 Version-Behavior Locking

Stamp MUST guarantee:

- validation behavior is locked to the version of Stamp invoked;
- normalization output remains identical for all compliant inputs across all PATCH versions within a given MINOR branch;
- tests and reference outputs verify the behavior of each version against known baselines.

This ensures reproducibility across time and machines, supporting long-term provenance and auditability.

---

## 8. Compliance Guarantees

Stamp MUST guarantee deterministic, reproducible, and policy-aligned behavior for all metadata operations. These guarantees ensure that downstream systems—particularly CRI-CORE and Forge—can rely on Stamp as a stable preprocessing layer with no ambiguity or hidden state. All guarantees in this section are normative and binding.

---

### 8.1 Deterministic Behavior

Stamp MUST produce identical output for identical input across:

- repeated runs,
- different machines,
- different operating systems,
- different execution environments.

No randomness, environment-specific logic, or heuristics may influence Stamp’s results. Determinism is mandatory for reproducibility, auditability, and CRI-CORE integration.

---

### 8.2 Metadata Equivalence

Stamp MUST preserve metadata equivalence during normalization. This means:

- no change to the meaning of any field,
- no reinterpretation of user-provided content,
- no modification of authority-level or domain classification,
- no inferred provenance or authorship.

Normalization MUST only adjust formatting, ordering, and structural presentation—not semantics.

---

### 8.3 Structural Completeness

Stamp MUST ensure that every governed artifact contains all required fields defined by:

- ARI Metadata Policy v3.0.1,
- ARI Metadata Schema v3.0.2.

If a required field is missing and can be deterministically defaulted, Stamp MUST insert it. If a field cannot be deterministically created (e.g., author name), Stamp MUST classify the issue as a fatal error.

---

### 8.4 Schema Alignment

Stamp MUST validate all metadata fields against the ARI Metadata Schema and MUST NOT accept:

- unrecognized fields,
- incorrectly typed fields,
- values outside enumerated constraints,
- malformed or unparsable metadata.

Stamp MUST reject (fatal) any metadata block that cannot be parsed or validated safely.

---

### 8.5 Provenance Guarantees

Stamp MUST guarantee that:

- AI-assistance fields reflect policy requirements,
- placeholder DOIs follow the `TBD-X.Y.Z` pattern,
- `created` date is immutable once set,
- `updated` date reflects actual file modification timing.

Stamp MUST NOT fabricate information that implies false provenance, authorship, or historical revision.

---

### 8.6 Non-Modification of Body Content

Stamp MUST NOT alter:

- document text outside the metadata block,
- headings, paragraphs, or code blocks,
- semantic meaning or logical content.

Stamp’s operations are strictly confined to the metadata block and file-level structural validity.

---

### 8.7 Stability Across Versions

Stamp MUST guarantee:

- PATCH versions do not change behavior for valid inputs,
- MINOR versions do not break existing workflows,
- MAJOR versions only change behavior in documented, intentional ways.

These guarantees ensure backward compatibility unless explicitly broken by MAJOR version increments.

---

### 8.8 CI/CD Reliability

Stamp MUST behave predictably in automated pipelines. Specifically, Stamp MUST:

- return deterministic exit codes,
- produce machine-readable reports,
- operate without network dependencies,
- avoid side effects or non-local state.

This ensures uninterrupted operation in AWO, CRI-CORE, and Forge pipelines.

---

### 8.9 Reproducibility and Auditability

Stamp MUST provide all information required for third-party auditing, including:

- SHA-256 file hashes before and after normalization,
- timestamped validation reports,
- explicit lists of all corrections applied,
- clear classification of all detected issues.

No transformation or validation step may be omitted from the machine-readable report.

---

### 8.10 Guarantee of Non-Ambiguity

Stamp MUST eliminate any ambiguity that could result from:

- partially valid metadata,
- inconsistent formatting,
- undocumented correction rules,
- environment-specific behavior.

Any ambiguity MUST be treated as a repairable error or a fatal error, depending on severity.

---

### 8.11 Separation of Responsibilities

Stamp MUST guarantee that it does not perform:

- policy definition,
- compliance enforcement,
- content-level interpretation,
- governance decisions.

These responsibilities belong to ARI, CRI-CORE, and AWO, respectively. Stamp’s role is strictly structural and preparatory.

---

### 8.12 Guarantee of Forward Compatibility

Stamp MUST ensure that metadata generated or normalized under a given version:

- remains valid and parseable under future versions (unless MAJOR bump),
- contains no deprecated structures unless explicitly allowed,
- adheres to a stable, auditable formatting contract.

Forward compatibility ensures long-term viability of archived research artifacts.

---  

## Appendix A: Glossary

**Anchor**  
A unique, versioned identifier declaring the canonical reference label for a governed document. Must follow the format `<SYSTEM>-<DOCNAME>-vX.Y.Z`.

**ARI Metadata Policy**  
The authoritative policy defining required metadata fields, structural rules, and semantic constraints for governed artifacts in the Aurora ecosystem.

**ARI Metadata Schema**  
The JSON Schema representation of the ARI Metadata Policy. Used by Stamp to validate metadata fields, types, patterns, and conditional logic.

**Canonical Order**  
A predetermined sequence of metadata fields defined by ARI policy. Stamp MUST reorder fields into this exact sequence during normalization.

**Deterministic Output**  
Guarantee that given identical input, Stamp produces identical output across all systems, environments, and executions. Prohibits randomness or environment-dependent behavior.

**Dependency Path**  
A relative file path (beginning with `./` or `../`) indicating an upstream document required for interpretability. Must resolve to an existing file and must not form circular references.

**Fatal Error**  
An error that prevents safe or deterministic correction. Stamp MUST halt processing and declare noncompliance when a fatal error occurs.

**Metadata Equivalence**  
A guarantee that normalization preserves the meaning and authority of metadata fields while altering only formatting or structure.

**Normalization**  
Transforming metadata into a canonical format, including field ordering, indentation, quoting, and structural cleanup, without changing semantic meaning.

**Placeholder DOI**  
A temporary DOI represented as `TBD-X.Y.Z` used for unpublished or version-in-progress documents. Stamp may insert placeholder DOIs when missing and permitted.

**Repairable Error**  
A violation that Stamp can deterministically correct without guessing or altering meaning. Correction results in a rewritten metadata block and exit code `1`.

**Schema Alignment**  
The requirement that metadata fields must match the ARI Metadata Schema in type, pattern, and enumeration. Any deviation constitutes an error.

**Semantic Versioning**  
Versioning format `MAJOR.MINOR.PATCH` indicating breaking changes, additive non-breaking changes, or patches/bug fixes.

**Warning**  
A non-fatal condition that does not break compliance but may indicate an unusual or suboptimal pattern. Does not cause rewriting or failure.

---  

## 9. End of Specification

This specification defines the complete normative behavior of Stamp v0.0.1. All validation, normalization, injection, and output rules described herein are mandatory and binding for any compliant implementation. Downstream systems—including CRI-CORE, Forge, and AWO-governed workflows—MUST assume that Stamp adheres to the rules, guarantees, and integration boundaries detailed in this document.

Any implementation claiming conformance to Stamp v0.0.1 MUST:

1. implement all required behaviors defined in Sections 3 through 8;
2. adhere to the versioning rules in Section 7;
3. preserve deterministic output as defined in Section 8;
4. produce machine-readable validation reports conforming to Section 5;
5. maintain strict separation of responsibilities per Section 6.

Implementations MAY extend this specification with additional, non-breaking features, provided that:

- all normative behavior remains intact,
- deterministic output is preserved,
- no changes conflict with ARI, NTS, or AWO requirements,
- no extensions alter or override the rules defined herein.

Future revisions of this specification MUST increment the appropriate semantic version level in accordance with Section 7.

This document concludes the normative definition of Stamp v0.0.1.

---

<div align="center">
  <sub>© 2026 Waveframe Labs — Independent Open-Science Research Entity • Governed under the Aurora Research Initiative (ARI)</sub>
</div>

