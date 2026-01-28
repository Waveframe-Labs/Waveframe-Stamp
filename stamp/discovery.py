"""
<!--
title: "Stamp — Artifact Discovery Module"
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
ai_assistance_details: "AI-assisted drafting of discovery semantics and documentation; human-owned design decisions and final validation."
dependencies: []
anchors:
  - stamp-discovery-v0.0.1
-->
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Union


EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    "archive",
}


@dataclass(frozen=True)
class DiscoveredArtifact:
    """
    Represents a filesystem-discovered artifact candidate.

    Discovery is purely structural:
    - no parsing
    - no validation
    - no schema awareness
    """
    path: Path
    size_bytes: int


def discover_artifacts(
    roots: Iterable[Union[str, Path]]
) -> List[DiscoveredArtifact]:
    """
    Recursively discover candidate artifacts starting from given root paths.

    This function performs filesystem traversal only.
    It does not parse files, inspect contents, or apply schemas.

    Exclusion rules are directory-based and deterministic.
    """
    artifacts: List[DiscoveredArtifact] = []

    for root in roots:
        root_path = Path(root).resolve()

        # Single file root
        if root_path.is_file():
            try:
                artifacts.append(
                    DiscoveredArtifact(
                        path=root_path,
                        size_bytes=root_path.stat().st_size,
                    )
                )
            except OSError:
                continue
            continue

        # Non-directory root
        if not root_path.is_dir():
            continue

        # Directory traversal
        for path in root_path.rglob("*"):
            if not path.is_file():
                continue

            # Skip excluded directories
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue

            try:
                size = path.stat().st_size
            except OSError:
                continue

            artifacts.append(
                DiscoveredArtifact(
                    path=path,
                    size_bytes=size,
                )
            )

    return artifacts
