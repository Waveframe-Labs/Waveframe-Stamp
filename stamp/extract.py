from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import ruamel.yaml


@dataclass(frozen=True)
class ExtractedMetadata:
    artifact_path: Path
    metadata: Optional[Any]
    raw_block: Optional[str]
    error: Optional[str]


_yaml = ruamel.yaml.YAML(typ="safe")


def extract_metadata(path: Path) -> ExtractedMetadata:
    """
    Extract metadata from an artifact.

    Currently supported:
    - Markdown YAML frontmatter

    Returns metadata=None if no valid metadata block is present.
    """
    if path.suffix.lower() == ".md":
        return _extract_markdown_frontmatter(path)

    # Unsupported artifact types (for now)
    return ExtractedMetadata(
        artifact_path=path,
        metadata=None,
        raw_block=None,
        error=None,
    )


def _extract_markdown_frontmatter(path: Path) -> ExtractedMetadata:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return ExtractedMetadata(
            artifact_path=path,
            metadata=None,
            raw_block=None,
            error=str(e),
        )

    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        return ExtractedMetadata(
            artifact_path=path,
            metadata=None,
            raw_block=None,
            error=None,
        )

    # Find closing delimiter
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            raw_block = "\n".join(lines[1:i])
            try:
                data = _yaml.load(raw_block)
            except Exception as e:
                return ExtractedMetadata(
                    artifact_path=path,
                    metadata=None,
                    raw_block=raw_block,
                    error=str(e),
                )

            return ExtractedMetadata(
                artifact_path=path,
                metadata=data,
                raw_block=raw_block,
                error=None,
            )

    # Opening delimiter with no close
    return ExtractedMetadata(
        artifact_path=path,
        metadata=None,
        raw_block=None,
        error="Unterminated YAML frontmatter block",
    )
