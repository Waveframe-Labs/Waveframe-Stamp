<!--
title: "Stamp Metadata Extraction Module"
filetype: "operational"
type: "specification"
domain: "enforcement"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Draft"
created: "2026-01-25"
updated: "2026-01-25"

author:
  name: "Waveframe Labs"
  email: "contact@waveframelabs.org"
  orcid: "https://orcid.org/0009-0006-6043-9295"

maintainer:
  name: "Waveframe Labs"
  url: "https://waveframelabs.org"

ai_assisted: "partial"
ai_assistance_details: >
  AI assistance was used to help draft and refine the metadata extraction
  logic and documentation structure. All architectural decisions,
  validation behavior, and acceptance criteria were human-directed
  and reviewed.

dependencies: []
anchors: []
-->

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

    Supported (in priority order):
    1. Markdown YAML frontmatter
    2. HTML comment–embedded YAML metadata (any file type)

    Returns metadata=None if no valid metadata block is present.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return ExtractedMetadata(
            artifact_path=path,
            metadata=None,
            raw_block=None,
            error=str(e),
        )

    # 1) Markdown frontmatter always wins
    if path.suffix.lower() == ".md":
        md_result = _extract_markdown_frontmatter_from_text(path, text)
        if md_result.metadata is not None or md_result.error:
            return md_result

    # 2) HTML comment metadata fallback
    html_result = _extract_html_comment_metadata(path, text)
    if html_result:
        return html_result

    # No metadata found
    return ExtractedMetadata(
        artifact_path=path,
        metadata=None,
        raw_block=None,
        error=None,
    )


def _extract_markdown_frontmatter_from_text(
    path: Path,
    text: str,
) -> ExtractedMetadata:
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        return ExtractedMetadata(
            artifact_path=path,
            metadata=None,
            raw_block=None,
            error=None,
        )

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

    return ExtractedMetadata(
        artifact_path=path,
        metadata=None,
        raw_block=None,
        error="Unterminated YAML frontmatter block",
    )


def _extract_html_comment_metadata(
    path: Path,
    text: str,
) -> Optional[ExtractedMetadata]:
    """
    Extract YAML metadata embedded in a top-of-file HTML comment.

    Only the first HTML comment is considered.
    """
    stripped = text.lstrip()

    if not stripped.startswith("<!--"):
        return None

    start = stripped.find("<!--")
    end = stripped.find("-->")

    if start != 0 or end == -1:
        return None

    raw_block = stripped[4:end].strip()

    if not raw_block:
        return None

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
