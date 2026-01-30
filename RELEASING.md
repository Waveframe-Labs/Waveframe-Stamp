---
title: "Stamp — Releasing Guide"
filetype: "documentation"
type: "procedure"
domain: "methodology"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Active"
created: "2026-01-29"
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

anchors: []  
---

# Releasing Stamp

This document defines the authoritative procedure for releasing **Stamp**.

It exists to ensure that every release is deterministic, auditable, reproducible,
and correctly versioned across Git, metadata, and package distribution.

This is not a marketing checklist.
It is an operational contract.

## Release Philosophy

Stamp follows a strict, layered release model:

1. Repository state is stabilized first
2. Git tag is authoritative
3. DOIs are minted from tagged artifacts
4. PyPI distribution follows the tag
5. No retroactive changes to released artifacts

Once a version is released, it is immutable.

## Pre-Release Checklist

Before tagging a release, confirm:

- All governed artifacts pass validation
- README.md is complete and accurate
- GETTING_STARTED.md exists and works as written
- CHANGELOG.md includes an entry for the release version
- RELEASING.md reflects current process
- Trace artifacts are committed under traces/
- No uncommitted changes exist

If any of the above is false, do not proceed.

## Step 1 — Version Lock

Decide the release version (e.g. v0.1.0).

Update all of the following to match:

- pyproject.toml
- Tool identity constants
- README version badge
- Metadata blocks declaring version

Commit these changes as a single atomic commit.

## Step 2 — Changelog Finalization

Update CHANGELOG.md:

- Move the relevant section from [Unreleased] to [vX.Y.Z]
- Confirm dates are correct
- Ensure wording reflects facts, not intent

Commit the changelog update separately.

## Step 3 — Git Tag

Create an annotated tag:

git tag -a vX.Y.Z -m "Stamp vX.Y.Z"
git push origin vX.Y.Z

From this point forward, the release is immutable.

## Step 4 — DOI Minting

After the tag exists:

1. Mint a version DOI from the tagged archive
2. Update README citation section
3. Update metadata blocks referencing the version DOI
4. Commit DOI updates

DOI updates must never modify released code.

## Step 5 — PyPI Distribution

Only after the tag exists:

python -m build
python -m twine upload dist/*

Rules:

- PyPI version must exactly match the Git tag
- No code changes between tag and upload
- PyPI is a distribution channel, not the source of truth

## Step 6 — Post-Release Verification

Verify:

- pip install waveframe-stamp works
- stamp --help reports correct version
- CLI commands behave as documented
- DOI resolves to the correct artifact

If verification fails, issue a new patch release.

## What Is Not Allowed

- Retagging an existing version
- Editing released artifacts
- Uploading to PyPI before tagging
- Minting DOIs before the tag exists
- Silent hotfixes

If a mistake is made, increment the version.

## Summary

Order matters:

1. Stabilize
2. Tag
3. Mint DOI
4. Distribute
5. Verify

Stamp releases are boring on purpose.

<div align="center">
  <sub>© 2026 Waveframe Labs — Independent Open-Science Research Entity</sub>
</div>
