from __future__ import annotations

import json
from pathlib import Path

import typer

from stamp.extract import extract_metadata
from stamp.schema import load_schema
from stamp.validate import validate_artifact
from stamp.fix import build_fix_proposals

app = typer.Typer(
    add_completion=False,
    help="Validate artifacts against schemas.",
)


@app.command("run")
def run(
    artifact: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Path to artifact file (e.g., Markdown).",
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
        help="json | pretty",
    ),
    summary: bool = typer.Option(
        False,
        "--summary",
        help="Emit structured summary instead of raw diagnostics.",
    ),
    fix_proposals: bool = typer.Option(
        False,
        "--fix-proposals",
        help="Emit fix proposals derived from diagnostics (no changes applied).",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        help="Suppress success output when no violations are found.",
    ),
) -> None:
    """
    Validate an artifact against a JSON Schema and emit Canonical Diagnostic Objects (CDOs).

    Exit codes:
      - 0: no diagnostics
      - 1: diagnostics present

    Notes:
      - This command never mutates artifacts.
      - Fix proposals are descriptive only.
    """

    extracted = extract_metadata(artifact)
    resolved_schema = load_schema(schema)

    # IMPORTANT: keyword-only call (validate_artifact enforces this)
    result = validate_artifact(
        extracted=extracted,
        resolved_schema=resolved_schema,
    )

    diagnostics = result.diagnostics
    passed = len(diagnostics) == 0

    # --- Fix proposal mode ---
    if fix_proposals:
        proposals = build_fix_proposals(
            diagnostics=diagnostics,
            artifact=artifact,
            schema=schema,
        )
        typer.echo(json.dumps(proposals, indent=2))
        raise typer.Exit(code=0 if passed else 1)

    # --- Summary mode ---
    if summary:
        typer.echo(
            json.dumps(
                {
                    "artifact": str(artifact),
                    "schema": str(schema),
                    "passed": passed,
                    "diagnostic_count": len(diagnostics),
                },
                indent=2,
            )
        )
        raise typer.Exit(code=0 if passed else 1)

    # --- Default diagnostic output ---
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
