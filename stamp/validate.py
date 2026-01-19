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
    extracted: ExtractedMetadata,
    resolved_schema: ResolvedSchema,
) -> ValidationResult:
    """
    Validate extracted metadata against a resolved schema and emit CDO diagnostics.
    """
    instance = extracted.metadata

    raw_errors = _validate_instance(instance, resolved_schema.schema)

    diagnostics = translate_validation_errors_to_cdos(
        errors=raw_errors,
        instance=instance,
    )

    return ValidationResult(
        artifact_path=extracted.artifact_path,
        schema_id=resolved_schema.identifier,
        diagnostics=diagnostics,
    )


    return ValidationResult(
        artifact_path=artifact_path,
        schema_id=schema_id,
        diagnostics=diagnostics,
    )
