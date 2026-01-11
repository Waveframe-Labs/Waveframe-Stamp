#!/usr/bin/env python3

"""
Stamp CLI
---------
Primary command-line entrypoint for the Stamp metadata validation tool.

Implements the CLI contract defined in Stamp-Spec.md Section 5.8.
Routes files into the loader → parser → validator → normalizer → reporter pipeline.

This is a scaffold file — logic is not implemented yet.
"""

import argparse
import sys
import glob
import os
from typing import List

# Engine stubs (to be implemented later)
from stamp.engine.loader import Loader
from stamp.engine.parser import Parser
from stamp.engine.validator import Validator
from stamp.engine.normalizer import Normalizer
from stamp.engine.reporter import Reporter


def expand_file_list(paths: List[str]) -> List[str]:
    """
    Expand file patterns and return a unique list of .md files.

    Safety Guard:
    - Defaults to matching only .md files to avoid modifying LICENSE,
      CSV files, binary assets, or other non-governed files.
    """
    expanded = []
    for p in paths:
        for match in glob.glob(p, recursive=True):
            if match.endswith(".md") and os.path.isfile(match):
                expanded.append(match)
    return list(set(expanded))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Stamp — Metadata Validator and Normalizer"
    )

    parser.add_argument(
        "paths",
        nargs="+",
        help="Files or glob patterns to process (e.g., '*.md').",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate only. Do not modify files."
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Validate and apply deterministic fixes in-place."
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Write normalized files to this directory instead of overwriting source."
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable report to stdout."
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.check and args.fix:
        print("ERROR: --check and --fix cannot be used together.", file=sys.stderr)
        sys.exit(2)

    files = expand_file_list(args.paths)

    if not files:
        print("No markdown files found matching input patterns.", file=sys.stderr)
        sys.exit(2)

    loader = Loader()
    parser = Parser()
    validator = Validator(schema={})   # schema vendoring applied later
    normalizer = Normalizer()
    reporter = Reporter()

    highest_exit_code = 0

    for path in files:
        # TODO: Actual engine logic not implemented yet
        try:
            content = loader.load_file(path)
            metadata, body, had_meta = parser.extract_metadata_block(content)
            results = validator.validate(metadata)

            fatal = len(results.get("fatal_errors", [])) > 0
            repairable = len(results.get("repairable_errors", [])) > 0

            # Determine action
            if fatal:
                highest_exit_code = max(highest_exit_code, 2)

            elif repairable:
                if args.fix:
                    # TODO: apply normalization
                    # TODO: reassemble file
                    # TODO: write in-place or to output_dir
                    highest_exit_code = max(highest_exit_code, 1)
                else:
                    # check-only mode sees repairable errors as exit 1
                    highest_exit_code = max(highest_exit_code, 1)

            else:
                # clean pass
                highest_exit_code = max(highest_exit_code, 0)

            # TODO: compute hashes
            original_hash = "TODO"
            rewritten_hash = None

            report = reporter.build_report(
                path=path,
                original_hash=original_hash,
                rewritten_hash=rewritten_hash,
                results=results
            )

            if args.json:
                import json
                print(json.dumps(report, indent=2))

        except Exception as e:
            print(f"Unexpected error processing {path}: {e}", file=sys.stderr)
            highest_exit_code = max(highest_exit_code, 2)

    sys.exit(highest_exit_code)


if __name__ == "__main__":
    main()
