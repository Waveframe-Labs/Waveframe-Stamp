from __future__ import annotations

import typer
from pathlib import Path

from stamp.extract import extract_metadata
from stamp.schema import load_schema
from stamp.validate import validate_artifact
from stamp.fix import apply_fix_proposals

app = typer.Typer(add_completion=False, help="Apply safe fixes to artifacts.")


@app.command("apply")
def apply(
    artifact: Path = typer.Argument(..., exists=True, readable=True),
    schema: Path = typer.Option(..., "--schema", exists=True, readable=True),
    out: Path = typer.Option(..., "--out", help="Output path for fixed artifact."),
) -> None:
    """
    Apply safe fix proposals to an artifact.

    This command:
      - re-validates the artifact
      - applies ONLY fixable strategies
      - never mutates in place
    """

    extracted = extract_metadata(artifact)
    resolved_schema = load_schema(schema)

    result = validate_artifact(
        extracted=extracted,
        resolved_schema=resolved_schema,
    )

    apply_fix_proposals(
        artifact=artifact,
        diagnostics=result.diagnostics,
        out_path=out,
    )

    typer.echo(f"✔ Fixed artifact written to {out}")
