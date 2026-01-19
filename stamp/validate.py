from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator

# Canonical CDO translation
from stamp.cdo import translate_validation_errors_to_cdos  # type: ignore


@dataclass(frozen=True)
class ValidationResult:
    artifact_path: Optional[Path]
    schema_id: str
    diagnostics: List[Dict[str, Any]]


def _validate_instance(instance: Any, schema: Dict[str, Any]) -> List[Any]:
    """
    Run Draft 2020-12 validation and collect ALL errors.
    Returns raw jsonschema error objects.
    """
    validator = Draft202012Validator(schema)
    return list(validator.iter_errors(instance))


def validate_artifact(
    *,
    artifact: Any,
    schema: Dict[str, Any],
    schema_id: str,
    artifact_path: Optional[Path] = None,
) -> ValidationResult:
    """
    Validate an artifact against a JSON Schema and emit Canonical Diagnostic Objects (CDOs).

    This is the primary public validation entrypoint for Stamp.
    Extraction, schema resolution, and enforcement are handled elsewhere.
    """
    raw_errors = _validate_instance(artifact, schema)

    diagnostics = translate_validation_errors_to_cdos(
        errors=raw_errors,
        schema=schema,
        instance=artifact,
    )

    return ValidationResult(
        artifact_path=artifact_path,
        schema_id=schema_id,
        diagnostics=diagnostics,
    )
