from __future__ import annotations

from typing import Any, Dict, List

from jsonschema.exceptions import ValidationError


# --- Canonical Diagnostic ID Mapping (ABI) -----------------------------

_CANONICAL_ID_MAP: Dict[str, str] = {
    "additionalProperties": "object.no_additional_properties",
    "required": "required.missing",
    "enum": "enum.invalid",
    "type": "type.mismatch",
}


# --- Public API --------------------------------------------------------

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
            "instance_path": _format_path(error.path),
            "schema_path": _format_path(error.schema_path),
            "message": error.message,
            "details": _extract_details(error),
            "fix": _infer_fix_capability(error),
        }

        diagnostics.append(diagnostic)

    return diagnostics


# --- Internals ---------------------------------------------------------

def _map_error_to_id(error: ValidationError) -> str:
    """
    Map a jsonschema validator keyword to a stable, semantic diagnostic ID.
    """
    return _CANONICAL_ID_MAP.get(
        error.validator,
        f"{error.validator}.violation",
    )


def _format_path(path: Any) -> str:
    """
    Convert a jsonschema path iterator into a JSON Pointer–like string.
    """
    if not path:
        return ""
    return "/" + "/".join(str(p) for p in path)


def _extract_details(error: ValidationError) -> Dict[str, Any]:
    """
    Extract structured details from a ValidationError where possible.
    """
    details: Dict[str, Any] = {}

    if error.validator == "required":
        # Message format: "'field' is a required property"
        parts = error.message.split("'")
        if len(parts) >= 2:
            details["missing_property"] = parts[1]

    elif error.validator == "enum":
        details["allowed_values"] = error.validator_value
        details["value"] = error.instance

    elif error.validator == "type":
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
        # Message format: "Additional properties are not allowed ('foo' was unexpected)"
        parts = error.message.split("'")
        key = parts[1] if len(parts) >= 2 else None

        return {
            "fixable": True,
            "strategy": "prune",
            "parameters": {
                "key": key,
            },
        }

    return None
