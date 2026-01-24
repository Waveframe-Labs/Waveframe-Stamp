from __future__ import annotations

import typer

from stamp.cli.validate import app as validate_app
from stamp.cli.fix import app as fix_app

cli = typer.Typer(add_completion=False, help="Stamp CLI — schema validation and remediation tools.")

cli.add_typer(validate_app, name="validate")
cli.add_typer(fix_app, name="fix")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
