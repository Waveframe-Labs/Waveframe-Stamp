from __future__ import annotations

import typer

from stamp.cli.validate import app as validate_app

cli = typer.Typer(
    name="stamp",
    help="Schema-agnostic structural diagnostics engine.",
    add_completion=False,
)

cli.add_typer(
    validate_app,
    name="validate",
    help="Validate an artifact against a schema and emit diagnostics.",
)


def main() -> None:
    cli()
