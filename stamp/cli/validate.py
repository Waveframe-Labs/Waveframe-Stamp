from __future__ import annotations

import json
from pathlib import Path
from typing import List

import typer

from stamp.extract import extract_metadata
from stamp.schema import load_schema
from stamp.validate import validate_artifact

from stamp.trace import (
    AppliedFix,
    build_trace,
    trace_path_for_artifact,
    write_trace,
)

app = typer.Typer(add_completion=False, help="Validate artifacts against schemas.")


@app.command("run")
def run(
    artifact: Path = typer.Argument(..., exists=True, readable=True, help="Path to artifact file (e.g., .md)."),
    schema: Path = typer.Option(..., "--schema", exists=True, readable=True, help="Path to JSON Schema (.json)."),
    format: str = typer.Option("json", "--format", help="json | pretty"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success output when no violations are found."),
) -> None:
    extracted = extract_metadata(artifact)
    resolved_schema = load_schema(schema)

    result = validate_artifact(extracted, resolved_schema)
    diagnostics = result.diagnostics

    exit_code = 1 if diagnostics else 0

    # ---- emit trace (always) ----
    trace = build_trace(
        artifact_path=artifact,
        schema_id=resolved_schema.identifier,
        schema_source=resolved_schema.source,
        schema_uri=resolved_schema.uri,
        exit_code=exit_code,
        diagnostics_count=len(diagnostics),
        applied_fixes=[],  # fixer not implemented yet
        tool_version="0.0.1",
        mode="validate",
    )

    trace_path = trace_path_for_artifact(artifact)
    write_trace(trace, path=trace_path)

    # ---- output diagnostics ----
    if diagnostics:
        if format == "pretty":
            for d in diagnostics:
                typer.echo(json.dumps(d, indent=2))
        else:
            typer.echo(json.dumps(diagnostics))
        raise typer.Exit(code=1)

    if not quiet:
        typer.echo("✅ Validation passed — no violations found.")
    raise typer.Exit(code=0)
