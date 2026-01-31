---
title: "Stamp — Documentation Folder"
filetype: "documentation"
type: "specification"
domain: "methodology"
version: "0.1.0"
doi: "10.5281/zenodo.18436622"
status: "Active"
created: "2026-01-29"
updated: "2026-01-31"

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
ai_assistance_details: "AI-assisted drafting of folder-level documentation under direct human review and final approval."

dependencies: []
anchors: []
---

# docs/

This directory contains **conceptual and operational documentation** for the Stamp project.

It is intended to explain *how Stamp is meant to be understood and used* rather than to document internal APIs or code-level behavior.

Content in this folder is:
- human-readable
- stable once published
- referenced by the root README when conceptual grounding is required

---

## Contents

### `OPERATING_MODEL.md`

This document defines the **operating model** for Stamp.

It explains:
- the role Stamp plays within a governed research workflow
- the boundaries between validation, fixing, and enforcement
- how Stamp is intended to interact with downstream systems (e.g. CRI-CORE)
- what Stamp explicitly does *not* do

`OPERATING_MODEL.md` should be treated as:
- authoritative for intent and scope
- stable across minor releases
- required reading for reviewers, auditors, and integrators

It is **not** a tutorial and does not replace:
- the root README
- GETTING_STARTED.md
- CLI reference material

---

## Scope Clarification

The `docs/` folder intentionally avoids:
- duplicating README content
- embedding CLI usage examples
- documenting internal module structure

Those concerns live elsewhere in the repository.

---

<div align="center">
  <sub>© 2026 Waveframe Labs</sub>
</div>
