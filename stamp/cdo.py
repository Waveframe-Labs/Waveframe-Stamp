from __future__ import annotations

from typing import Any, Dict, List

from jsonschema.exceptions import ValidationError


def translate_validation_errors_to_cdos(
    *,
    errors: List[ValidationError],
    schema: Dict[str, Any],
    instance: Any,
) -> List[Dict[str, Any]]:
    """
    Translate jsonschema ValidationError objects into Canonical Diagnostic Objects (CDOs).

    This function is schema-agnostic and performs no policy interpretation.
    """
    diagnostics: List[Dict[str, Any]] = []

    for error in errors:
        diagnostic: Dict[str, Any] = {
            "id": _map_error_to_id(error),
            "severity": "error",
            "schema_keyword": error.validator,
            "instance_path": "/" + "/".join(str(p) for p in error.path),
            "schema_path": "/" + "/".join(str(p) for p in error.schema_path),
            "message": error.message,
            "details": _extract_details(error),
            "fix": _infer_fix_capability(error),
        }

        diagnostics.append(diagnostic)

    return diagnostics


def _map_error_to_id(error: ValidationError) -> str:
    """
    Map a jsonschema validator keyword to a stable diagnostic ID.
    """
    return f"{error.validator}.violation"


def _extract_details(error: ValidationError) -> Dict[str, Any]:
    """
    Extract structured details from a ValidationError where possible.
    """
    details: Dict[str, Any] = {}

    if error.validator == "required":
        details["missing_property"] = error.message.split("'")[1]

    if error.validator == "enum":
        details["allowed_values"] = error.validator_value
        details["value"] = error.instance

    if error.validator == "type":
        details["expected_type"] = error.validator_value
        details["actual_type"] = type(error.instance).__name__
        details["value"] = error.instance

    return details


def _infer_fix_capability(error: ValidationError) -> Any:
    """
    Determine whether a violation is mechanically fixable.
    This is intentionally conservative.
    """
    if error.validator == "additionalProperties":
        return {
            "fixable": True,
            "strategy": "prune",
            "parameters": {
                "key": error.message.split("'")[1]
            }
        }

    return None
