"""
<!--
title: "Stamp — Validation Command Interface"
filetype: "operational"
type: "specification"
domain: "enforcement"
version: "0.0.1"
doi: "TBD-0.0.1"
status: "Draft"
created: "2026-01-16"
updated: "2026-01-27"
author:
  name: "Waveframe Labs"
  email: "test@waveframelabs.org"
  orcid: "https://orcid.org/0009-0006-6043-9295"
maintainer:
  name: "Waveframe Labs"
  url: "https://waveframelabs.org"
license: "Apache-2.0"
copyright:
  holder: "Waveframe Labs"
  year: "2026"
ai_assisted: "partial"
ai_assistance_details: "AI-assisted drafting of CLI orchestration logic under direct human design control and final validation."
dependencies: []
anchors:
  - stamp-validate-cli-v0.0.1
-->
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import typer

from stamp.extract import extract_metadata
from stamp.schema import load_schema
from stamp.validate import validate_artifact
from stamp.fix import build_fix_proposals
from stamp.remediation import build_remediation_summary
from stamp.discovery import discover_artifacts

app = typer.Typer()


@app.command("run")
def run(
    artifact: Path,
    schema: Path = typer.Option(..., "--schema"),
    summary: bool = typer.Option(False, "--summary"),
    remediation: bool = typer.Option(False, "--remediation"),
    fix_proposals: bool = typer.Option(False, "--fix-proposals"),
):
    """
    Validate a single artifact.
    """
    extracted = extract_metadata(artifact)
    resolved_schema = load_schema(schema)

    result = validate_artifact(
        extracted=extracted,
        resolved_schema=resolved_schema,
    )

    if fix_proposals:
        proposals = build_fix_proposals(result)
        typer.echo(proposals)
        raise typer.Exit(code=1 if not result.passed else 0)

    if remediation:
        report = build_remediation_summary(result)
        typer.echo(report)
        raise typer.Exit(code=1 if not result.passed else 0)

    if summary:
        typer.echo(
            {
                "artifact": str(artifact),
                "schema": str(schema),
                "passed": result.passed,
                "diagnostic_count": len(result.diagnostics),
            }
        )
        raise typer.Exit(code=1 if not result.passed else 0)

    typer.echo(result.diagnostics)
    raise typer.Exit(code=1 if not result.passed else 0)


@app.command("repo")
def repo(
    root: Path,
    schema: Path = typer.Option(..., "--schema"),
):
    """
    Validate all discovered artifacts under a root path.
    """
    resolved_schema = load_schema(schema)
    artifacts = discover_artifacts([root])

    results: List[dict] = []

    passed_count = 0
    failed_count = 0

    for artifact in artifacts:
        extracted = extract_metadata(artifact.path)
        result = validate_artifact(
            extracted=extracted,
            resolved_schema=resolved_schema,
        )

        results.append(
            {
                "artifact": str(artifact.path),
                "passed": result.passed,
                "diagnostic_count": len(result.diagnostics),
            }
        )

        if result.passed:
            passed_count += 1
        else:
            failed_count += 1

    typer.echo(
        {
            "root": str(root),
            "total_artifacts": len(results),
            "passed": passed_count,
            "failed": failed_count,
            "results": results,
        }
    )

    raise typer.Exit(code=1 if failed_count > 0 else 0)
