from __future__ import annotations

import typer

from stamp.cli.validate import app as validate_app

# Root CLI application
app = typer.Typer(
    add_completion=False,
    help="Stamp — schema-agnostic structural diagnostics engine",
)

# Register subcommands
app.add_typer(
    validate_app,
    name="validate",
    help="Validate an artifact against a JSON Schema and emit diagnostics",
)


def cli() -> None:
    """
    Console entrypoint for the Stamp CLI.

    This function is referenced by the console script defined in pyproject.toml.
    """
    app()


if __name__ == "__main__":
    cli()
