from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path


def build_fix_proposals(
    *,
    diagnostics: List[Dict[str, Any]],
    artifact: Path,
    schema: Path,
) -> Dict[str, Any]:
    """
    Build structured fix proposals derived from diagnostics.

    This function does NOT modify artifacts.
    It only describes possible mechanical fixes.
    """

    fixes: List[Dict[str, Any]] = []

    for d in diagnostics:
        fix = d.get("fix")
        if not fix or not fix.get("fixable"):
            continue

        fixes.append(
            {
                "id": d.get("id"),
                "strategy": fix.get("strategy"),
                "target": d.get("instance_path"),
                "parameters": fix.get("parameters", {}),
                "confidence": "high",
                "safe": True,
            }
        )

    return {
        "artifact": str(artifact),
        "schema": str(schema),
        "fixes_available": len(fixes) > 0,
        "fix_count": len(fixes),
        "fixes": fixes,
    }
