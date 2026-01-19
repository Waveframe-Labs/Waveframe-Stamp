from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union
import json
import urllib.request


@dataclass(frozen=True)
class ResolvedSchema:
    source: str          # local | remote | inline
    identifier: str
    uri: Optional[str]
    schema: dict


def load_schema(source: Union[Path, str, dict]) -> ResolvedSchema:
    """
    Load a JSON Schema from a local file, remote URL, or inline dict.

    No validation, no ref resolution, no trust assumptions.
    """
    # Inline schema
    if isinstance(source, dict):
        identifier = source.get("$id", "inline-schema")
        return ResolvedSchema(
            source="inline",
            identifier=identifier,
            uri=source.get("$id"),
            schema=source,
        )

    # Local file
    if isinstance(source, Path):
        text = source.read_text(encoding="utf-8")
        data = json.loads(text)
        identifier = data.get("$id", source.name)
        return ResolvedSchema(
            source="local",
            identifier=identifier,
            uri=data.get("$id"),
            schema=data,
        )

    # Remote URL
    if isinstance(source, str) and source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source) as response:
            text = response.read().decode("utf-8")
        data = json.loads(text)
        identifier = data.get("$id", source)
        return ResolvedSchema(
            source="remote",
            identifier=identifier,
            uri=source,
            schema=data,
        )

    raise ValueError(f"Unsupported schema source: {source}")
