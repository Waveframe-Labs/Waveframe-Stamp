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
from typing import List, Optional

import typer

from stamp.extract import extract_metadata
from stamp.schema import load_schema
from stamp.validate import validate_artifact, ValidationResult
from stamp.fix import build_fix_proposals
from stamp.remediation import build_remediation_summary
from stamp.discovery import discover_artifacts
from stamp.trace import (
    ExecutionTrace,
    ArtifactTrace,
    now_utc,
)
from stamp.trace_schema import validate_trace  # ← NEW

app = typer.Typer()


def _is_passed(result: ValidationResult) -> bool:
    """
    A validation passes iff there are no error-severity diagnostics.
    """
    return not any(d.get("severity") == "error" for d in result.diagnostics)


def _write_validated_trace(trace: ExecutionTrace, path: Path) -> None:
    """
    Validate a trace artifact against the trace schema before writing.
    """
    errors = validate_trace(trace.to_dict())
    if errors:
        typer.secho(
            "Trace validation failed; trace artifact was not written.",
            fg=typer.colors.RED,
            err=True,
        )
        for e in errors:
            typer.secho(
                f"- {e['message']} (at {e['instance_path']})",
                fg=typer.colors.RED,
                err=True,
            )
        raise typer.Exit(code=2)

    trace.write_json(path)


@app.command("run")
def run(
    artifact: Path,
    schema: Path = typer.Option(..., "--schema"),
    summary: bool = typer.Option(False, "--summary"),
    remediation: bool = typer.Option(False, "--remediation"),
    fix_proposals: bool = typer.Option(False, "--fix-proposals"),
    trace_out: Optional[Path] = typer.Option(None, "--trace-out"),
):
    """
    Validate a single artifact.
    """
    started_at = now_utc()

    extracted = extract_metadata(artifact)
    resolved_schema = load_schema(schema)

    result = validate_artifact(
        extracted=extracted,
        resolved_schema=resolved_schema,
    )

    passed = _is_passed(result)
    exit_code = 0 if passed else 1

    if fix_proposals:
        proposals = build_fix_proposals(result)
        typer.echo(proposals)

    elif remediation:
        report = build_remediation_summary(result)
        typer.echo(report)

    elif summary:
        typer.echo(
            {
                "artifact": str(artifact),
                "schema": str(schema),
                "passed": passed,
                "diagnostic_count": len(result.diagnostics),
            }
        )

    else:
        typer.echo(result.diagnostics)

    finished_at = now_utc()

    if trace_out is not None:
        trace = ExecutionTrace(
            trace_version="0.0.1",
            tool="stamp",
            tool_version="0.0.1",
            command="validate run",
            schema=str(schema),
            started_at=started_at,
            finished_at=finished_at,
            exit_code=exit_code,
            artifacts=[
                ArtifactTrace(
                    artifact=str(artifact),
                    passed=passed,
                    diagnostic_count=len(result.diagnostics),
                )
            ],
        )
        _write_validated_trace(trace, trace_out)

    raise typer.Exit(code=exit_code)


@app.command("repo")
def repo(
    root: Path,
    schema: Path = typer.Option(..., "--schema"),
    trace_out: Optional[Path] = typer.Option(None, "--trace-out"),
):
    """
    Validate all discovered artifacts under a root path.
    """
    started_at = now_utc()

    resolved_schema = load_schema(schema)
    artifacts = discover_artifacts([root])

    artifact_traces: List[ArtifactTrace] = []

    passed_count = 0
    failed_count = 0

    for artifact in artifacts:
        extracted = extract_metadata(artifact.path)
        result = validate_artifact(
            extracted=extracted,
            resolved_schema=resolved_schema,
        )

        passed = _is_passed(result)

        artifact_traces.append(
            ArtifactTrace(
                artifact=str(artifact.path),
                passed=passed,
                diagnostic_count=len(result.diagnostics),
            )
        )

        if passed:
            passed_count += 1
        else:
            failed_count += 1

    typer.echo(
        {
            "root": str(root),
            "total_artifacts": len(artifact_traces),
            "passed": passed_count,
            "failed": failed_count,
        }
    )

    finished_at = now_utc()
    exit_code = 0 if failed_count == 0 else 1

    if trace_out is not None:
        trace = ExecutionTrace(
            trace_version="0.0.1",
            tool="stamp",
            tool_version="0.0.1",
            command="validate repo",
            schema=str(schema),
            started_at=started_at,
            finished_at=finished_at,
            exit_code=exit_code,
            artifacts=artifact_traces,
        )
        _write_validated_trace(trace, trace_out)

    raise typer.Exit(code=exit_code)
