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
    artifact: Path = typer.Argument(..., exists=True, readable=True),
    schema: Path = typer.Option(..., "--schema", exists=True, readable=True),
    format: str = typer.Option("json", "--format", help="json | pretty"),
) -> None:
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

    if diagnostics:
        raise typer.Exit(code=1)
