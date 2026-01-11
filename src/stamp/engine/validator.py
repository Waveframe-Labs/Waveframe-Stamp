# File: src/stamp/engine/validator.py

from __future__ import annotations

import json
from typing import Dict, List, Tuple, Any

from jsonschema import Draft202012Validator, ValidationError


class ValidationResult:
    """
    Structured result object returned by Validator.validate().

    Attributes:
        fatal_errors: list of fatal error strings
        repairable_errors: list of repairable error strings
        warnings: list of warning strings
        metadata: parsed metadata object (may be {} if invalid)
        body: markdown body text
        had_metadata: bool — whether a metadata fence was detected
    """

    def __init__(
        self,
        fatal_errors: List[str],
        repairable_errors: List[str],
        warnings: List[str],
        metadata: Dict[str, Any],
        body: str,
        had_metadata: bool,
    ):
        self.fatal_errors = fatal_errors
        self.repairable_errors = repairable_errors
        self.warnings = warnings
        self.metadata = metadata
        self.body = body
        self.had_metadata = had_metadata

    @property
    def status(self) -> str:
        """
        Returns pass / repairable / fail based on spec-required classification.
        """
        if self.fatal_errors:
            return "fail"
        if self.repairable_errors:
            return "repairable"
        return "pass"


class Validator:
    """
    Validator
    ---------
    Implements ARI-compliant error classification as defined in Stamp-Spec.md §4.

    Responsibilities:
        - Accept metadata + body from Parser and errors from Loader.
        - Classify loader failures as fatal errors.
        - Validate metadata against ARI Metadata Schema (jsonschema).
        - Identify repairable vs fatal errors per policy.
        - Surface warnings (non-fatal anomalies).
    """

    def __init__(self, schema: Dict[str, Any]):
        """
        schema: JSON schema dict loaded by engine initializer.
        """
        self.schema = schema
        self.json_validator = Draft202012Validator(schema)

    # -------------------------------------------------------------------------
    # PUBLIC VALIDATION INTERFACE
    # -------------------------------------------------------------------------

    def validate(
        self,
        metadata: Dict,
        body: str,
        had_metadata: bool,
        loader_errors: List[str],
    ) -> ValidationResult:
        """
        Main entrypoint for validation.

        Inputs:
            metadata: dict from Parser
            body: markdown body
            had_metadata: bool (Parser detected fence)
            loader_errors: errors returned by Loader

        Outputs:
            ValidationResult
        """

        fatal: List[str] = []
        repairable: List[str] = []
        warnings: List[str] = []

        # -------------------------------------------------------------
        # 1. Loader errors → always fatal
        # -------------------------------------------------------------
        if loader_errors:
            fatal.extend(loader_errors)

        # -------------------------------------------------------------
        # 2. No metadata block present → repairable (Stamp must inject)
        # -------------------------------------------------------------
        if not had_metadata:
            repairable.append("Missing metadata block (no top-of-file YAML found).")
            return ValidationResult(fatal, repairable, warnings, metadata, body, had_metadata)

        # -------------------------------------------------------------
        # 3. Empty metadata dict
        # -------------------------------------------------------------
        if metadata == {}:
            # Could be empty but valid YAML or malformed. Parser already handled that.
            repairable.append("Empty or unparseable metadata block detected.")
            return ValidationResult(fatal, repairable, warnings, metadata, body, had_metadata)

        # -------------------------------------------------------------
        # 4. JSON Schema validation
        # -------------------------------------------------------------
        schema_errors = list(self.json_validator.iter_errors(metadata))
        for err in schema_errors:
            self._classify_schema_error(err, fatal, repairable)

        # -------------------------------------------------------------
        # 5. Policy-level additional checks
        # -------------------------------------------------------------
        self._apply_policy_rules(metadata, fatal, repairable, warnings)

        return ValidationResult(
            fatal=fatal,
            repairable=repairable,
            warnings=warnings,
            metadata=metadata,
            body=body,
            had_metadata=had_metadata,
        )

    # -------------------------------------------------------------------------
    # INTERNAL HELPERS
    # -------------------------------------------------------------------------

    def _classify_schema_error(
        self,
        err: ValidationError,
        fatal: List[str],
        repairable: List[str],
    ) -> None:
        """
        Classify schema-level validation problems into fatal or repairable.

        Rules based on Stamp-Spec.md §4:
            - Missing required fields → fatal
            - Invalid enumerations → fatal
            - Type mismatches that can be deterministically corrected → repairable
        """
        path = ".".join([str(p) for p in err.path]) or "<root>"

        if err.validator == "required":
            fatal.append(f"Missing required field: {err.message}")
        elif err.validator == "enum":
            fatal.append(f"Invalid value for '{path}': {err.message}")
        elif err.validator == "type":
            repairable.append(f"Incorrect type for '{path}': {err.message}")
        else:
            # conservative: treat unknown schema errors as fatal
            fatal.append(f"Schema validation error at {path}: {err.message}")

    # -------------------------------------------------------------------------

    def _apply_policy_rules(
        self,
        metadata: Dict[str, Any],
        fatal: List[str],
        repairable: List[str],
        warnings: List[str],
    ) -> None:
        """
        Apply ARI Metadata Policy v3.0.1 beyond JSON Schema:

        - Domain & Type validity are enforced by schema (fatal).
        - ai_assisted logic must match ai_assistance_details requirement.
        - 'updated' must not precede 'created'.
        - anchors list must not be empty for governed artifacts.
        - dependency list issues classified as repairable.
        """

        # ai_assisted consistency
        ai_assisted = metadata.get("ai_assisted")
        details = metadata.get("ai_assistance_details")

        if ai_assisted in ("partial", "extensive") and not details:
            repairable.append("ai_assistance_details missing for AI-assisted document.")

        if ai_assisted == "none" and details:
            repairable.append("ai_assistance_details should not be present when ai_assisted='none'.")

        # date ordering
        created = metadata.get("created")
        updated = metadata.get("updated")

        if created and updated and updated < created:
            repairable.append("updated date precedes created date (repairable normalization).")

        # anchors validity
        anchors = metadata.get("anchors", [])
        if not isinstance(anchors, list):
            repairable.append("anchors field must be an array.")
        elif len(anchors) == 0:
            repairable.append("Missing anchors list (required by ARI Policy §8).")

        # dependencies shape
        dependencies = metadata.get("dependencies", [])
        if not isinstance(dependencies, list):
            repairable.append("dependencies field must be an array.")

        # future-dated updated timestamp → warning
        if updated and updated > "2030-01-01":
            warnings.append("Updated timestamp is suspiciously far in the future.")

