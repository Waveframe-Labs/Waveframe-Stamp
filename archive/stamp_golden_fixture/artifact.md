---
title: "Broken Artifact"
filetype: documentation
type: normative
domain: governance
version: "1"
doi: "10.5281/zenodo.1234567"
status: LIVE
created: "2026-13-01"
updated: "2026-01-01"

author:
  name: "Test User"
  email: "test@example.com"
  orcid: "0000-0000-0000-0000"

maintainer:
  name: "Waveframe Labs"
  url: "https://waveframelabs.org"

license: "Apache-2.0"

copyright:
  holder: "Waveframe Labs"
  year: "2026"

ai_assisted: partial

anchors:
  - TEST-DOC-v0.1.0

extra_field: "should not exist"
---

This document intentionally violates the ARI Metadata Schema v3.0.2.

It exists solely as a **golden fixture** for validating:

- JSON Schema → Stamp error translation
- Severity classification (FATAL vs ERROR)
- Repairability rules
- Deterministic ordering
- No-mutation behavior when FATAL errors exist
