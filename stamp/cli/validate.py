from __future__ import annotations

import json
from pathlib import Path

import typer

from stamp.extract import extract_metadata
from stamp.schema import load_schema
from stamp.validate import validate_artifact

app = typer.Typer(add_completion=False)


@app.command("validate")
def validate(
    artifact: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Artifact file to validate",
    ),
    schema: Path = typer.Option(
        ...,
        "--schema",
        exists=True,
        readable=True,
        help="JSON Schema file",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        help="Output format: json | pretty",
    ),
) -> None:
    """
    Validate an artifact against a JSON Schema and emit Canonical Diagnostic Objects.
    """
    if format not in {"json", "pretty"}:
        typer.echo("Invalid format. Use 'json' or 'pretty'.", err=True)
        raise typer.Exit(code=2)

    extracted = extract_metadata(artifact)
    resolved_schema = load_schema(schema)

    result = validate_artifact(
        extracted=extracted,
        resolved_schema=resolved_schema,
    )

    diagnostics = result.diagnostics

    if format == "pretty":
        for d in diagnostics:
            typer.echo(json.dumps(d, indent=2))
    else:
        typer.echo(json.dumps(diagnostics))

    # Non-zero exit if any diagnostics were emitted
    if diagnostics:
        raise typer.Exit(code=1)
