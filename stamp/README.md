---
title: "Stamp — Core Library"
filetype: "documentation"
type: "specification"
domain: "methodology"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Active"
created: "2026-01-29"
updated: "2026-01-30"

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
  - STAMP-CORE-LIBRARY-v0.1.0
---

This directory contains the **Stamp core library.**  

Files here implement deterministic, schema-agnostic logic for:
- metadata extraction
- validation
- diagnostic normalization (CDOs)
- fix proposal generation (NPOs)

These modules **do not perform I/O, CLI parsing, or enforcement.**  
They are designed to be imported by tooling, CI systems, and higher-level interfaces.