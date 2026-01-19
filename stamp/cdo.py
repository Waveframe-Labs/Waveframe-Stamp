"""
Stamp — Canonical Diagnostic Object (CDO) translation layer.

This module is schema-agnostic. It translates raw jsonschema.ValidationError
objects into Stamp CDO dictionaries that conform to cdo-v1.schema.json.

Key invariants:
- Deterministic output (stable templates, stable ordering).
- No policy interpretation.
- No mutation of source artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from jsonschema import ValidationError


# ----------------------------
# Public API
# ----------------------------

def translate_validation_errors_to_cdos(
    errors: Sequence[ValidationError],
    *,
    stamp_version: str,
    schema_version: Optional[str] = None,
    validator_engine: str = "stamp-core",
) -> List[Dict[str, Any]]:
    """
    Translate a list of jsonschema.ValidationError into a list of CDO dictionaries.

    Notes:
    - This function assumes traversal has already "leaf-unwrapped" errors as needed.
      If the upstream validator yields higher-level errors (e.g., allOf/if/then),
      the caller should unwrap them before passing to this translator, or provide
      errors that already point at leaf constraints.
    - Output ordering is guaranteed: instance_path -> schema_keyword -> id.
    """
    cdos: List[Dict[str, Any]] = [ _error_to_cdo(e, stamp_version, schema_version, validator_engine) for e in errors ]
    cdos.sort(key=_cdo_sort_key)
    return cdos


# ----------------------------
# Internal helpers
# ----------------------------

def _cdo_sort_key(cdo: Dict[str, Any]) -> Tuple[str, str, str]:
    return (
        cdo.get("instance_path", ""),
        cdo.get("schema_keyword", ""),
        cdo.get("id", ""),
    )


def _now_rfc3339() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _json_pointer_from_path(path_parts: Sequence[Any]) -> str:
    """
    Convert jsonschema's path parts (deque/list) into RFC6901 JSON Pointer.
    """
    if not path_parts:
        return ""
    def escape(part: Any) -> str:
        s = str(part)
        return s.replace("~", "~0").replace("/", "~1")
    return "/" + "/".join(escape(p) for p in path_parts)


def _schema_pointer_from_absolute_path(abs_parts: Sequence[Any]) -> str:
    """
    jsonschema's ValidationError.absolute_schema_path gives a deque of schema navigation parts.
    We convert to RFC6901 pointer.
    """
    if not abs_parts:
        return ""
    def escape(part: Any) -> str:
        s = str(part)
        return s.replace("~", "~0").replace("/", "~1")
    return "/" + "/".join(escape(p) for p in abs_parts)


def _type_name(value: Any) -> str:
    """
    Deterministic mapping for expected fixture strings.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "number"  # JSON Schema uses "number" broadly; integer is a subcase.
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _error_to_cdo(
    err: ValidationError,
    stamp_version: str,
    schema_version: Optional[str],
    validator_engine: str,
) -> Dict[str, Any]:
    schema_keyword = str(err.validator) if err.validator is not None else "unknown"
    instance_path = _json_pointer_from_path(list(err.absolute_path))
    schema_path = _schema_pointer_from_absolute_path(list(err.absolute_schema_path))

    # Map keyword -> canonical id/message/details/fix
    if schema_keyword == "required":
        # jsonschema sets err.message like "'license' is a required property"
        missing = None
        if isinstance(err.message, str) and "is a required property" in err.message:
            # Extract between quotes if present
            # Example: "'license' is a required property"
            parts = err.message.split("'")
            if len(parts) >= 2:
                missing = parts[1]
        # Fallback: try err.validator_value (list of required keys) and err.instance (object)
        if missing is None and isinstance(err.validator_value, list) and isinstance(err.instance, dict):
            for k in err.validator_value:
                if k not in err.instance:
                    missing = str(k)
                    break
        missing = missing or "unknown"

        cdo = {
            "id": "required.missing",
            "severity": "error",
            "schema_keyword": "required",
            "instance_path": instance_path,
            "schema_path": schema_path or "/required",
            "message": f"Required property '{missing}' is missing.",
            "details": {"missing_property": missing},
            "fix": None,
        }

    elif schema_keyword == "additionalProperties":
        # jsonschema message often: "Additional properties are not allowed ('internal_id' was unexpected)"
        prop = None
        if isinstance(err.message, str) and "was unexpected" in err.message:
            # Try to extract within parentheses and quotes
            # ... ("internal_id" was unexpected)
            if "(" in err.message and ")" in err.message:
                inner = err.message.split("(", 1)[1].rsplit(")", 1)[0]
                # inner may contain "'internal_id' was unexpected" or "\"internal_id\" was unexpected"
                for quote in ("'", '"'):
                    if quote in inner:
                        parts = inner.split(quote)
                        if len(parts) >= 2:
                            prop = parts[1]
                            break
        # Better: jsonschema provides err.params with "additionalProperties": ["internal_id"] in some versions
        if prop is None and isinstance(getattr(err, "params", None), dict):
            ap = err.params.get("additionalProperties")
            if isinstance(ap, list) and ap:
                prop = str(ap[0])
            elif isinstance(ap, str):
                prop = ap
        prop = prop or (str(err.details) if hasattr(err, "details") else "unknown")

        cdo = {
            "id": "object.no_additional_properties",
            "severity": "error",
            "schema_keyword": "additionalProperties",
            "instance_path": instance_path,
            "schema_path": schema_path or "/additionalProperties",
            "message": f"Property '{prop}' is not allowed.",
            "details": {"property": prop},
            "fix": {
                "fixable": True,
                "strategy": "prune",
                "parameters": {"key": prop},
            },
        }

    elif schema_keyword == "enum":
        allowed = []
        if isinstance(err.validator_value, list):
            allowed = err.validator_value
        value = err.instance
        cdo = {
            "id": "enum.invalid",
            "severity": "error",
            "schema_keyword": "enum",
            "instance_path": instance_path,
            "schema_path": schema_path,
            "message": "Value is not allowed.",
            "details": {"allowed_values": allowed, "value": value},
            "fix": None,
        }

    elif schema_keyword == "type":
        expected = err.validator_value
        # Normalize expected to JSON Schema style string(s)
        expected_type = ""
        if isinstance(expected, list):
            # choose first for reporting in v1 (fixtures use a single string)
            expected_type = str(expected[0]) if expected else "unknown"
        else:
            expected_type = str(expected) if expected is not None else "unknown"

        actual_type = _type_name(err.instance)

        cdo = {
            "id": "type.mismatch",
            "severity": "error",
            "schema_keyword": "type",
            "instance_path": instance_path,
            "schema_path": schema_path,
            "message": "Value does not match the expected type.",
            "details": {
                "expected_type": expected_type,
                "actual_type": actual_type,
                "value": err.instance,
            },
            "fix": None,
        }

    elif schema_keyword == "pattern":
        pattern = err.validator_value
        cdo = {
            "id": "string.pattern_mismatch",
            "severity": "error",
            "schema_keyword": "pattern",
            "instance_path": instance_path,
            "schema_path": schema_path,
            "message": "Value does not match required pattern.",
            "details": {"pattern": pattern, "value": err.instance},
            "fix": None,
        }

    elif schema_keyword == "format":
        fmt = err.validator_value
        cdo = {
            "id": "format.invalid",
            "severity": "error",
            "schema_keyword": "format",
            "instance_path": instance_path,
            "schema_path": schema_path,
            "message": f"Value does not match required format '{fmt}'.",
            "details": {"format": fmt, "value": err.instance},
            "fix": None,
        }

    elif schema_keyword == "const":
        cdo = {
            "id": "const.mismatch",
            "severity": "error",
            "schema_keyword": "const",
            "instance_path": instance_path,
            "schema_path": schema_path,
            "message": "Value does not match required constant.",
            "details": {"allowed_value": err.validator_value, "value": err.instance},
            "fix": None,
        }

    elif schema_keyword in ("minLength", "maxLength"):
        comparator = "min" if schema_keyword == "minLength" else "max"
        limit = err.validator_value
        actual_len = len(err.instance) if isinstance(err.instance, str) else 0
        cdo = {
            "id": "string.length_invalid",
            "severity": "error",
            "schema_keyword": schema_keyword,
            "instance_path": instance_path,
            "schema_path": schema_path,
            "message": "String length is invalid.",
            "details": {"limit": limit, "actual_length": actual_len, "comparator": comparator},
            "fix": None,
        }

    else:
        # Fallback: keep it deterministic but generic.
        cdo = {
            "id": "validation.failed",
            "severity": "error",
            "schema_keyword": schema_keyword,
            "instance_path": instance_path,
            "schema_path": schema_path,
            "message": err.message if isinstance(err.message, str) else "Validation failed.",
            "details": {
                "validator_value": err.validator_value,
                "value": err.instance,
            },
            "fix": None,
        }

    # Add provenance (required by CDO schema)
    cdo["provenance"] = {
        "timestamp": _now_rfc3339(),
        "stamp_version": stamp_version,
        "schema_version": schema_version or "",
        "validator_engine": validator_engine,
    }

    return cdo
