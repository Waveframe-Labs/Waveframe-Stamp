from __future__ import annotations

import json
from pathlib import Path

import typer

from stamp.extract import extract_metadata
from stamp.schema import load_schema
from stamp.validate import validate_artifact

app = typer.Typer(add_completion=False, help="Validate artifacts against schemas.")


@app.command("run")
def run(
    artifact: Path = typer.Argument(..., exists=True, readable=True, help="Path to artifact file (e.g., .md)."),
    schema: Path = typer.Option(..., "--schema", exists=True, readable=True, help="Path to JSON Schema (.json)."),
    format: str = typer.Option("json", "--format", help="json | pretty"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success output when no violations are found."),
) -> None:
    """
    Validate an artifact against a JSON Schema and emit Canonical Diagnostic Objects (CDOs).

    Exit codes:
      - 0: no diagnostics
      - 1: diagnostics present
    """
    extracted = extract_metadata(artifact)
    resolved_schema = load_schema(schema)

    result = validate_artifact(extracted, resolved_schema)
    diagnostics = result.diagnostics

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
