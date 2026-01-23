from __future__ import annotations

import typer
from pathlib import Path

from stamp.extract import extract_metadata
from stamp.schema import load_schema
from stamp.validate import validate_artifact
from stamp.fix import build_fix_proposals, apply_fix_proposals

app = typer.Typer(add_completion=False, help="Apply fixes derived from schema validation.")


@app.command("apply")
def apply(
    artifact: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Path to artifact file (Markdown with YAML frontmatter).",
    ),
    schema: Path = typer.Option(
        ...,
        "--schema",
        exists=True,
        readable=True,
        help="Path to JSON Schema file.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview fixes without modifying the artifact.",
    ),
) -> None:
    """
    Validate an artifact and apply auto-fixable remediation proposals.

    This command:
      1. Runs validation
      2. Builds fix proposals from diagnostics
      3. Applies auto-fixable fixes (explicit opt-in)
    """

    extracted = extract_metadata(artifact)
    resolved_schema = load_schema(schema)

    result = validate_artifact(
        extracted=extracted,
        resolved_schema=resolved_schema,
    )

    diagnostics = result.diagnostics

    if not diagnostics:
        typer.echo("✅ No violations found — nothing to fix.")
        raise typer.Exit(code=0)

    proposal_bundle = build_fix_proposals(
        diagnostics=diagnostics,
        artifact=artifact,
        schema=schema,
    )

    proposals = proposal_bundle["proposals"]

    if not proposals:
        typer.echo("ℹ️ No fix proposals available.")
        raise typer.Exit(code=1)

    report = apply_fix_proposals(
        artifact=artifact,
        proposals=[
            # Rehydrate FixProposal objects
            type("FixProposalShim", (), p)() for p in proposals
        ],
        dry_run=dry_run,
    )

    if dry_run:
        typer.echo("🧪 Dry run complete — no changes written.")
    else:
        typer.echo("✏️ Fixes applied successfully.")

    typer.echo(report)

    # Re-validate after fixes (non-blocking for now)
    re_extracted = extract_metadata(artifact)
    re_result = validate_artifact(
        extracted=re_extracted,
        resolved_schema=resolved_schema,
    )

    if re_result.diagnostics:
        typer.echo("⚠️ Artifact still contains violations after fixes.")
        raise typer.Exit(code=1)

    typer.echo("✅ Artifact is schema-compliant after fixes.")
    raise typer.Exit(code=0)
