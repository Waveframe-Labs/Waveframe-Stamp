from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from stamp.extract import extract_metadata
from stamp.schema import load_schema
from stamp.validate import validate_artifact

app = typer.Typer(
    add_completion=False,
    help="Validate artifacts against schemas."
)


@app.command("run")
def run(
    artifact: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Path to artifact file (e.g., Markdown with front matter).",
    ),
    schema: Optional[Path] = typer.Option(
        None,
        "--schema",
        exists=True,
        readable=True,
        help="Path to local JSON Schema file.",
    ),
    schema_url: Optional[str] = typer.Option(
        None,
        "--schema-url",
        help="URL to remote JSON Schema.",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        help="Output format: json | pretty",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        help="Suppress success message when no violations are found.",
    ),
) -> None:
    """
    Validate an artifact against a JSON Schema and emit Canonical Diagnostic Objects (CDOs).

    Exit codes:
      - 0: no violations
      - 1: violations found
      - 2: invalid CLI usage
    """

    # Enforce mutual exclusivity for schema source
    if (schema is None and schema_url is None) or (schema and schema_url):
        typer.echo("❌ Exactly one of --schema or --schema-url must be provided.")
        raise typer.Exit(code=2)

    extracted = extract_metadata(artifact)

    resolved_schema = load_schema(schema if schema else schema_url)

    result = validate_artifact(
        extracted=extracted,
        resolved_schema=resolved_schema,
    )

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
