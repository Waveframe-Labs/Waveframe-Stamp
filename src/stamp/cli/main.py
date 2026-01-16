# File: src/stamp/cli/main.py

from __future__ import annotations

import json
import glob
import sys
from pathlib import Path
from typing import List, Optional

import click

from stamp.engine.controller import StampController


@click.command()
@click.argument(
    "paths",
    nargs=-1,
    required=False,
)
@click.option(
    "--check",
    "mode",
    flag_value="check",
    default=True,
    help="Validate metadata without modifying files.",
)
@click.option(
    "--fix",
    "mode",
    flag_value="fix",
    help="Validate and normalize metadata, rewriting files or writing to output directory.",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    default=None,
    help="Write normalized files to this directory instead of modifying originals.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output machine-readable JSON report to STDOUT.",
)
def cli(paths: List[str], mode: str, output_dir: Optional[str], json_output: bool):
    """
    Stamp CLI
    ----------
    Validates, normalizes, and reports on metadata compliance for Markdown files
    according to the Aurora Metadata Policy & Schema.

    USAGE:

        stamp --check "**/*.md"
        stamp --fix docs/**/*.md --output-dir fixed/
        stamp --check file.md --json

    """

    controller = StampController()

    # Handle default path pattern
    if not paths:
        paths = ["**/*.md"]

    # Expand glob patterns into file list
    expanded: List[str] = []
    for pattern in paths:
        expanded.extend(glob.glob(pattern, recursive=True))

    if not expanded:
        click.echo("No matching files found.", err=True)
        sys.exit(0)

    # Process files through the controller
    results = controller.process_files(
        expanded,
        mode=mode,
        output_dir=output_dir,
    )

    # JSON output case
    if json_output:
        click.echo(json.dumps(results, indent=2))
        exit_code = _highest_exit_code(results)
        sys.exit(exit_code)

    # Human-readable output
    for path, report in results.items():
        status = report["status"]
        click.echo(f"{path}: {status.upper()}")

    exit_code = _highest_exit_code(results)
    sys.exit(exit_code)


def _highest_exit_code(results: dict) -> int:
    """
    Compute Stamp exit code from per-file results.
    Highest exit code always wins:

        2 = fatal error (fail)
        1 = repairable error
        0 = clean or warnings only
    """
    highest = 0
    for report in results.values():
        code = report.get("exit_code", 0)
        if code > highest:
            highest = code
    return highest


if __name__ == "__main__":
    cli()
