"""
<!--
title: "Stamp — Execution Trace Artifact"
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
ai_assistance_details: "AI-assisted drafting of trace artifact structure; human-owned execution semantics and final validation."
dependencies: []
anchors:
  - stamp-trace-v0.0.1
-->
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import json
from pathlib import Path


@dataclass(frozen=True)
class ArtifactTrace:
    artifact: str
    passed: bool
    diagnostic_count: int


@dataclass(frozen=True)
class ExecutionTrace:
    tool: str
    tool_version: str
    command: str
    schema: str
    started_at: str
    finished_at: str
    exit_code: int
    artifacts: List[ArtifactTrace]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def write_json(self, path: Path) -> None:
        path.write_text(
            json.dumps(self.to_dict(), indent=2),
            encoding="utf-8",
        )


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()
