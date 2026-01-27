"""
<!--
title: "Stamp — Metadata Extraction Module"
filetype: "operational"
type: "specification"
domain: "enforcement"
version: "0.0.1"
doi: "TBD-0.0.1"
status: "Draft"
created: "2026-01-27"
updated: "2026-01-27"
author:
  name: "Waveframe Labs"
  email: "test@waveframelabs.org"
  orcid: "https://orcid.org/0009-0006-6043-9295"
maintainer:
  name: "Waveframe Labs"
  url: "https://waveframelabs.org"
license: "Apache-2.0"
copyright:
  holder: "Waveframe Labs"
  year: "2026"
ai_assisted: "partial"
ai_assistance_details: "AI-assisted drafting of module metadata and extraction contract notes; human-owned decisions and final validation."
dependencies: []
anchors:
  - stamp-extract-v0.0.1
-->
"""

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

    Priority order:
      1. Markdown YAML frontmatter (if present and valid)
      2. HTML comment metadata block
      3. No metadata
    """

    # 1. Markdown frontmatter has absolute priority
    if path.suffix.lower() == ".md":
        md_result = _extract_markdown_frontmatter(path)
        if md_result.metadata is not None:
            return md_result

    # 2. Fallback: HTML comment metadata (any file type)
    html_result = _extract_html_comment_metadata(path)
    if html_result.metadata is not None:
        return html_result

    # 3. No metadata found
    return ExtractedMetadata(
        artifact_path=path,
        metadata=None,
        raw_block=None,
        error=None,
    )


def _extract_markdown_frontmatter(path: Path) -> ExtractedMetadata:
    """
    Extract YAML frontmatter from a Markdown file.

    Frontmatter must be the first block in the file.
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


def _extract_html_comment_metadata(path: Path) -> ExtractedMetadata:
    """
    Extract ARI metadata from an HTML comment block at the top of a file.

    Expected format:

    <!--
    key: value
    ...
    -->
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

    stripped = text.lstrip()

    if not stripped.startswith("<!--"):
        return ExtractedMetadata(
            artifact_path=path,
            metadata=None,
            raw_block=None,
            error=None,
        )

    end_idx = stripped.find("-->")
    if end_idx == -1:
        return ExtractedMetadata(
            artifact_path=path,
            metadata=None,
            raw_block=None,
            error="Unterminated HTML comment metadata block",
        )

    raw_block = stripped[4:end_idx].strip()

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
