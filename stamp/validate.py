from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator

from stamp.extract import ExtractedMetadata
from stamp.schema import ResolvedSchema

# Import your existing CDO translation function(s).
# Adjust the import to match what you actually named the module/function.
from stamp.cdo import translate_validation_errors_to_cdos  # type: ignore


@dataclass(frozen=True)
class ValidationResult:
    artifact_path: Path
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
    extracted: ExtractedMetadata,
    resolved_schema: ResolvedSchema,
) -> ValidationResult:
    """
    Validate extracted metadata against a resolved schema and emit CDO diagnostics.
    """
    # If there is no metadata block, validation still happens against `None`.
    # The schema decides whether that's invalid (e.g., "type": "object").
    instance = extracted.metadata

    raw_errors = _validate_instance(instance, resolved_schema.schema)

    diagnostics = translate_validation_errors_to_cdos(
        errors=raw_errors,
        schema=resolved_schema.schema,
        instance=instance,
    )

    return ValidationResult(
        artifact_path=extracted.artifact_path,
        schema_id=resolved_schema.identifier,
        diagnostics=diagnostics,
    )
