# File: src/stamp/engine/controller.py

from __future__ import annotations

import os
from typing import Dict, Any, List, Optional, Tuple

from .loader import Loader
from .parser import Parser
from .validator import Validator
from .normalizer import Normalizer
from .reporter import Reporter


class Controller:
    """
    Controller
    ----------
    The central orchestration layer for Stamp.

    Implements the full workflow as defined in Stamp-Spec.md §3, §4, §5:

        Loader → Parser → Validator → Normalizer → Reporter

    Responsibilities:
        - Resolve paths from CLI
        - Load file contents
        - Parse metadata block
        - Validate metadata + classify errors
        - Apply normalization when allowed
        - Rewrite file if repairable
        - Generate machine-readable report
        - Return exit codes and validation statuses

    This module is intentionally stateless and deterministic.
    """

    def __init__(self, schema: Dict[str, Any]):
        self.loader = Loader()
        self.parser = Parser()
        self.validator = Validator(schema)
        self.normalizer = Normalizer()
        self.reporter = Reporter()

    # ----------------------------------------------------------------------
    # PUBLIC ENTRYPOINTS
    # ----------------------------------------------------------------------

    def process_file(
        self,
        path: str,
        fix: bool = False,
        output_dir: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], int]:
        """
        Process a single file.

        Arguments:
            path — filesystem path to Markdown file
            fix — whether Stamp is allowed to auto-correct
            output_dir — alternate write location for normalized output

        Returns:
            (report_dict, exit_code)
        """

        # ----------------------------------------------------------
        # 1. Load file
        # ----------------------------------------------------------
        original_content, loader_errors = self.loader.load_file(path)

        # If loader errors → fatal
        if loader_errors:
            validation = self.validator.validate(
                metadata={},
                body=original_content,
                had_metadata=False,
                loader_errors=loader_errors,
            )
            report = self.reporter.generate_report(
                path=path,
                original_content=original_content,
                rewritten_content=None,
                validation=validation,
                corrections=None,
            )
            return report, 2

        # ----------------------------------------------------------
        # 2. Parse YAML frontmatter
        # ----------------------------------------------------------
        metadata, body, had_metadata = self.parser.extract_metadata_block(
            original_content
        )

        # ----------------------------------------------------------
        # 3. Validate metadata
        # ----------------------------------------------------------
        validation = self.validator.validate(
            metadata,
            body,
            had_metadata,
            loader_errors,
        )

        # Exit code logic based on Stamp-Spec.md §5.3
        if validation.fatal_errors:
            # Fatal → do not rewrite
            report = self.reporter.generate_report(
                path=path,
                original_content=original_content,
                rewritten_content=None,
                validation=validation,
                corrections=None,
            )
            return report, 2

        if validation.repairable_errors and not fix:
            # Repairable but in CHECK mode → do not rewrite, return repairable exit code
            report = self.reporter.generate_report(
                path=path,
                original_content=original_content,
                rewritten_content=None,
                validation=validation,
                corrections=validation.repairable_errors,
            )
            return report, 1

        # ----------------------------------------------------------
        # 4. Apply normalization (only if fix=True)
        # ----------------------------------------------------------
        if validation.repairable_errors and fix:
            normalized_yaml, body_out, corrections = self.normalizer.normalize(
                validation.metadata,
                validation.body,
            )
            rewritten = self._rebuild_document(normalized_yaml, body_out)
        else:
            # No modifications required
            rewritten = original_content
            corrections = []

        # ----------------------------------------------------------
        # 5. Write output if fix=True or if output_dir provided
        # ----------------------------------------------------------
        rewritten_path = None

        if (fix and validation.repairable_errors) or output_dir:
            rewritten_path = self._write_output(
                path=path,
                content=rewritten,
                output_dir=output_dir,
            )

        # ----------------------------------------------------------
        # 6. Create final report
        # ----------------------------------------------------------
        report = self.reporter.generate_report(
            path=rewritten_path or path,
            original_content=original_content,
            rewritten_content=rewritten if rewritten != original_content else None,
            validation=validation,
            corrections=corrections,
        )

        # Exit code:
        # - 0 = pass/no repairs needed
        # - 1 = repairs applied
        # - 2 = fatal errors
        exit_code = 1 if corrections else 0

        return report, exit_code

    # ----------------------------------------------------------------------
    # INTERNAL HELPERS
    # ----------------------------------------------------------------------

    def _rebuild_document(self, yaml_text: str, body: str) -> str:
        """
        Reconstruct the document after normalization:

            ---
            <yaml_text>
            ---
            <body>

        Body is left unchanged.
        """
        return f"---\n{yaml_text}---\n{body}"

    # ----------------------------------------------------------------------

    def _write_output(self, path: str, content: str, output_dir: Optional[str]) -> str:
        """
        Write normalized content either in-place or into a designated output directory.
        Returns the path written to.
        """
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, os.path.basename(path))
        else:
            out_path = path

        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(content)

        return out_path
