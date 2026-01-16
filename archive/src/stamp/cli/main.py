# File: src/stamp/cli/main.py

import click
import json
from pathlib import Path

from stamp.engine.controller import StampController
from stamp.engine.fixer import Fixer


@click.group()
@click.version_option(package_name="stamp")
def cli():
    """
    Stamp CLI Interface
    -------------------
    Validates and normalizes ARI-governed metadata.
    Provides:
        - metadata validation
        - normalized output
        - diff generation for proposed fixes
        - controlled fix application
    """
    pass


# ---------------------------------------------------------------------------
# CHECK COMMAND (DEFAULT MODE)
# ---------------------------------------------------------------------------

@cli.command("check")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--json", "json_output", is_flag=True, help="Emit JSON report.")
def check_cmd(paths, json_output):
    """
    Validate metadata without modifying files.
    """
    controller = StampController()
    results = []

    for path in paths:
        report = controller.validate_single(path)
        results.append(report)

        if not json_output:
            click.echo(f"[{path}] status={report['status']} exit={report['exit_code']}")

    if json_output:
        click.echo(json.dumps(results, indent=2))

    # exit based on highest severity
    exit(max(r["exit_code"] for r in results))


# ---------------------------------------------------------------------------
# FIX COMMAND (REPLACES OLD --fix)
# ---------------------------------------------------------------------------

@cli.command("fix")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--approve", is_flag=True, help="Approve modifications and apply them.")
@click.option("--output-dir", default=None, help="Write fixed files to directory.")
@click.option("--json", "json_output", is_flag=True, help="Emit JSON report.")
def fix_cmd(paths, approve, output_dir, json_output):
    """
    Validate and optionally apply mechanical fixes.
    Requires --approve to write changes.
    """
    controller = StampController()
    fixer = Fixer()
    results = []

    for path in paths:
        report = controller.validate_single(path)
        original_text = controller.loader.load_file(path)

        if report["exit_code"] == 2:
            click.echo(f"❌ FATAL errors in {path}. No fixes applied.")
            results.append(report)
            continue

        metadata, body = controller.parser.parse(original_text)

        # generate proposed fixes
        proposal = fixer.propose_fixes(original_text, metadata, body)

        report["proposed_diff"] = proposal["diff"]
        report["proposed_changed"] = proposal["changed"]

        if proposal["changed"]:
            click.echo(f"⚠️  Proposed fixes for: {path}")
            click.echo("\n".join(proposal["diff"].splitlines()[:30]) + "\n...")

            if approve:
                fixer.apply_fixes(path, proposal["normalized"], controller.loader, output_dir)
                click.echo(f"✅ Fixes applied to {path}")

        results.append(report)

    if json_output:
        click.echo(json.dumps(results, indent=2))

    exit(max(r["exit_code"] for r in results))


# ---------------------------------------------------------------------------
# PROPOSE-FIXES (no apply, just show diffs)
# ---------------------------------------------------------------------------

@cli.command("propose-fixes")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--json", "json_output", is_flag=True)
def propose_fixes_cmd(paths, json_output):
    """
    Show diffs for mechanical fixes without applying them.
    """
    controller = StampController()
    fixer = Fixer()

    reports = []

    for path in paths:
        raw = controller.loader.load_file(path)
        metadata, body = controller.parser.parse(raw)
        proposal = fixer.propose_fixes(raw, metadata, body)

        result = {
            "path": path,
            "changed": proposal["changed"],
            "diff": proposal["diff"],
        }
        reports.append(result)

        if not json_output:
            if proposal["changed"]:
                click.echo(f"⚠️ Changes proposed for {path}:\n")
                click.echo(proposal["diff"])
            else:
                click.echo(f"✔ No fixes needed for {path}")

    if json_output:
        click.echo(json.dumps(reports, indent=2))


# ---------------------------------------------------------------------------
# APPLY-FIXES (explicit-only apply mode)
# ---------------------------------------------------------------------------

@cli.command("apply-fixes")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--output-dir", default=None)
def apply_fixes_cmd(paths, output_dir):
    """
    Apply previously inspected fixes.
    Requires the user to explicitly confirm before writing.
    """
    controller = StampController()
    fixer = Fixer()

    for path in paths:
        raw = controller.loader.load_file(path)
        metadata, body = controller.parser.parse(raw)

        proposal = fixer.propose_fixes(raw, metadata, body)

        if not proposal["changed"]:
            click.echo(f"✔ Nothing to apply for {path}")
            continue

        click.echo(f"⚠️ Reviewing changes for: {path}\n")
        click.echo(proposal["diff"])

        # ask user for explicit confirmation
        if click.confirm(f"Apply these fixes to {path}?", default=False):
            fixer.apply_fixes(path, proposal["normalized"], controller.loader, output_dir)
            click.echo(f"✅ Fixes applied to {path}")
        else:
            click.echo(f"❌ Fixes skipped for {path}")


if __name__ == "__main__":
    cli()
