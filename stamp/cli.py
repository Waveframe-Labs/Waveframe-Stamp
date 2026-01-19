from __future__ import annotations

import typer

from stamp.cli.validate import app as validate_app

cli = typer.Typer(add_completion=False)
cli.add_typer(validate_app)


if __name__ == "__main__":
    cli()
