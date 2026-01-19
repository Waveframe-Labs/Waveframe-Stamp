from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import json

try:
    import yaml
except ImportError:  # yaml is optional but strongly recommended
    yaml = None


@dataclass(frozen=True)
class ExtractedMetadata:
    artifact_path: Path
    metadata: Optional[dict]
    raw_block: Optional[str]
    error: Optional[str]


def extract_metadata(artifact_path: Path) -> ExtractedMetadata:
    """
    Extract a metadata block from a file.

    Supports:
    - Markdown with YAML front-matter
    - JSON files where the root object is metadata

    This function does not validate content or apply schemas.
    """
    try:
        text = artifact_path.read_text(encoding="utf-8")
    except Exception as e:
        return ExtractedMetadata(
            artifact_path=artifact_path,
            metadata=None,
            raw_block=None,
            error=f"Failed to read file: {e}",
        )

    # Markdown front-matter
    stripped = text.lstrip()
    if stripped.startswith("---"):
        parts = stripped.split("---", 2)
        if len(parts) >= 3:
            raw_block = parts[1].strip()
            if yaml is None:
                return ExtractedMetadata(
                    artifact_path=artifact_path,
                    metadata=None,
                    raw_block=raw_block,
                    error="PyYAML not installed",
                )
            try:
                data = yaml.safe_load(raw_block)
                if isinstance(data, dict):
                    return ExtractedMetadata(
                        artifact_path=artifact_path,
                        metadata=data,
                        raw_block=raw_block,
                        error=None,
                    )
                return ExtractedMetadata(
                    artifact_path=artifact_path,
                    metadata=None,
                    raw_block=raw_block,
                    error="Metadata block is not a mapping",
                )
            except Exception as e:
                return ExtractedMetadata(
                    artifact_path=artifact_path,
                    metadata=None,
                    raw_block=raw_block,
                    error=f"YAML parse error: {e}",
                )

    # JSON file
    if artifact_path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return ExtractedMetadata(
                    artifact_path=artifact_path,
                    metadata=data,
                    raw_block=text,
                    error=None,
                )
            return ExtractedMetadata(
                artifact_path=artifact_path,
                metadata=None,
                raw_block=text,
                error="JSON root is not an object",
            )
        except Exception as e:
            return ExtractedMetadata(
                artifact_path=artifact_path,
                metadata=None,
                raw_block=text,
                error=f"JSON parse error: {e}",
            )

    # No metadata detected
    return ExtractedMetadata(
        artifact_path=artifact_path,
        metadata=None,
        raw_block=None,
        error=None,
    )
