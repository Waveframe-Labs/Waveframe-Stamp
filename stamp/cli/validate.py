from __future__ import annotations

import json
from pathlib import Path

import typer

from stamp.extract import extract_metadata
from stamp.schema import load_schema
from stamp.validate import validate_artifact

app = typer.Typer(
    add_completion=False,
    help="Validate artifacts against JSON Schemas."
)


@app.command("run")
def run(
    artifact: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Path to artifact file (e.g., Markdown with frontmatter).",
    ),
    schema: Path = typer.Option(
        ...,
        "--schema",
        exists=True,
        readable=True,
        help="Path to JSON Schema file.",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        help="Output format for diagnostics: json | pretty",
    ),
    summary: bool = typer.Option(
        False,
        "--summary",
        help="Emit a structured validation summary.",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        help="Suppress non-JSON success output.",
    ),
) -> None:
    """
    Validate an artifact against a JSON Schema and emit Canonical Diagnostic Objects (CDOs).

    Exit codes:
      - 0: validation passed (no diagnostics)
      - 1: validation failed (diagnostics present)
    """

    extracted = extract_metadata(artifact)
    resolved_schema = load_schema(schema)

    result = validate_artifact(extracted, resolved_schema)
    diagnostics = result.diagnostics

    passed = len(diagnostics) == 0

    if summary:
        summary_payload = {
            "artifact": str(artifact),
            "schema": {
                "identifier": resolved_schema.identifier,
                "uri": resolved_schema.uri,
                "source": resolved_schema.source,
            },
            "passed": passed,
            "diagnostic_count": len(diagnostics),
        }
        typer.echo(json.dumps(summary_payload, indent=2))
    else:
        if diagnostics:
            if format == "pretty":
                for d in diagnostics:
                    typer.echo(json.dumps(d, indent=2))
            else:
                typer.echo(json.dumps(diagnostics))
        else:
            if not quiet:
                typer.echo(json.dumps({
                    "passed": True,
                    "diagnostic_count": 0,
                    "message": "Validation passed — no violations found."
                }))

    raise typer.Exit(code=0 if passed else 1)
