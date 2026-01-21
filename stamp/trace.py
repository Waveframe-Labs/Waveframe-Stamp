from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AppliedFix:
    id: str
    strategy: str
    parameters: Dict[str, Any]


@dataclass(frozen=True)
class StampTrace:
    tool: str
    version: str
    mode: str  # e.g., "validate", "normalize-preview", "apply"
    timestamp_utc: str

    artifact_path: str
    schema_id: str
    schema_source: str  # local | remote | inline
    schema_uri: Optional[str]

    exit_code: int
    diagnostics_count: int

    applied_fixes: List[AppliedFix]


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_trace(
    *,
    artifact_path: Path,
    schema_id: str,
    schema_source: str,
    schema_uri: Optional[str],
    exit_code: int,
    diagnostics_count: int,
    applied_fixes: List[AppliedFix],
    tool_version: str,
    mode: str,
) -> StampTrace:
    return StampTrace(
        tool="stamp-core",
        version=tool_version,
        mode=mode,
        timestamp_utc=_now_utc_iso(),
        artifact_path=str(artifact_path),
        schema_id=schema_id,
        schema_source=schema_source,
        schema_uri=schema_uri,
        exit_code=exit_code,
        diagnostics_count=diagnostics_count,
        applied_fixes=applied_fixes,
    )


def trace_path_for_artifact(artifact_path: Path) -> Path:
    # artifact.md -> artifact.md.stamp.json
    return artifact_path.with_name(artifact_path.name + ".stamp.json")


def write_trace(trace: StampTrace, *, path: Path) -> None:
    payload = asdict(trace)
    # dataclasses -> nested dicts; ensure AppliedFix list serializes cleanly
    payload["applied_fixes"] = [asdict(f) for f in trace.applied_fixes]

    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
