from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass(frozen=True)
class FixProposal:
    """
    A single proposed fix derived from a validation diagnostic.

    This object is descriptive only. It does not perform mutation.
    """
    rule_id: str
    message: str
    path: str
    proposed_value: Optional[Any]
    severity: str
    auto_fixable: bool


def build_fix_proposals(
    *,
    diagnostics: List[Dict[str, Any]],
    artifact: Path,
    schema: Path,
) -> Dict[str, Any]:
    """
    Build fix proposals from validation diagnostics.

    This function is PURE:
      - No file I/O
      - No mutation
      - No schema assumptions

    Returns a structured proposal bundle suitable for CLI, UI, or CRI-CORE.
    """

    proposals: List[FixProposal] = []

    for d in diagnostics:
        proposals.append(
            FixProposal(
                rule_id=d.get("rule_id", "unknown"),
                message=d.get("message", "No message provided"),
                path=d.get("path", ""),
                proposed_value=d.get("suggested_fix"),
                severity=d.get("severity", "unknown"),
                auto_fixable=bool(d.get("auto_fixable", False)),
            )
        )

    return {
        "artifact": str(artifact),
        "schema": str(schema),
        "proposal_count": len(proposals),
        "proposals": [p.__dict__ for p in proposals],
    }


def apply_fix_proposals(
    *,
    artifact: Path,
    proposals: List[FixProposal],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Apply fix proposals to a Markdown artifact with YAML frontmatter.

    Rules:
      - Only auto_fixable proposals are applied
      - Only frontmatter is modified
      - Original file is preserved unless dry_run=False

    Returns an application report.
    """

    if not artifact.exists():
        raise FileNotFoundError(f"Artifact not found: {artifact}")

    raw_text = artifact.read_text(encoding="utf-8")

    if not raw_text.startswith("---"):
        raise ValueError("Artifact does not contain YAML frontmatter.")

    _, fm_text, body = raw_text.split("---", 2)

    frontmatter = yaml.safe_load(fm_text) or {}

    applied: List[str] = []
    skipped: List[str] = []

    for proposal in proposals:
        if not proposal.auto_fixable:
            skipped.append(proposal.rule_id)
            continue

        if not proposal.path:
            skipped.append(proposal.rule_id)
            continue

        # Apply simple top-level key fixes only (intentional constraint)
        key = proposal.path.split(".")[0]
        frontmatter[key] = proposal.proposed_value
        applied.append(proposal.rule_id)

    if not dry_run:
        new_fm = yaml.safe_dump(frontmatter, sort_keys=False).strip()
        new_text = f"---\n{new_fm}\n---{body}"
        artifact.write_text(new_text, encoding="utf-8")

    return {
        "artifact": str(artifact),
        "applied": applied,
        "skipped": skipped,
        "dry_run": dry_run,
    }
