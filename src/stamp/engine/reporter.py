# File: src/stamp/engine/reporter.py

from __future__ import annotations

import json
import hashlib
from typing import Dict, Any
from datetime import datetime

from .validator import ValidationResult


class Reporter:
    """
    Reporter
    --------
    Responsible for producing the machine-readable validation report required by
    Stamp-Spec.md §5.2. This report is consumed by:

        - The Stamp CLI (--json flag)
        - GitHub Actions output artifacts
        - CRI-CORE enforcement modules
        - Third-party CI/CD tools

    Responsibilities:
        - Generate SHA-256 hashes for input & output content
        - Assemble metadata validation results
        - Wrap fatal/repairable/warning lists
        - Include timestamps
        - Include corrections applied (from Normalizer)
        - Preserve deterministic ordering of fields for reproducibility
    """

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate_report(
        self,
        path: str,
        original_content: str,
        rewritten_content: str | None,
        validation: ValidationResult,
        corrections: list[str] | None,
    ) -> Dict[str, Any]:
        """
        Produce the full machine-readable report as a structured dict.
        """

        original_hash = self._hash_content(original_content)
        rewritten_hash = (
            self._hash_content(rewritten_content) if rewritten_content is not None else None
        )

        report = {
            "file": path,
            "status": validation.status,
            "fatal_errors": validation.fatal_errors,
            "repairable_errors": validation.repairable_errors,
            "warnings": validation.warnings,
            "corrections_applied": corrections or [],
            "original_hash": original_hash,
            "rewritten_hash": rewritten_hash,
            "timestamp": self._timestamp(),
        }

        return report

    # ------------------------------------------------------------------

    def to_json(self, report: Dict[str, Any]) -> str:
        """
        Convert report dict to a formatted JSON string.
        """
        return json.dumps(report, indent=2, sort_keys=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _hash_content(self, content: str) -> str:
        """
        Return a deterministic SHA-256 hash of the content.
        This ensures reproducibility and traceability for provenance.
        """
        hasher = hashlib.sha256()
        hasher.update(content.encode("utf-8"))
        return hasher.hexdigest()

    # ------------------------------------------------------------------

    def _timestamp(self) -> str:
        """
        Return an ISO-8601 UTC timestamp for audit trails.
        """
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
