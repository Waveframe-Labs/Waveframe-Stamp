from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


def apply_fix_proposals(
    *,
    artifact: Path,
    diagnostics: List[Dict[str, Any]],
    out_path: Path,
) -> None:
    """
    Apply safe, mechanical fix proposals to an artifact.

    Supported strategies (v0):
      - prune: remove a top-level metadata key

    This function NEVER guesses.
    """

    text = artifact.read_text(encoding="utf-8")

    if not text.lstrip().startswith("---"):
        raise ValueError("Artifact does not contain YAML frontmatter.")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Malformed YAML frontmatter.")

    frontmatter = yaml.safe_load(parts[1]) or {}
    body = parts[2]

    modified = False

    for d in diagnostics:
        fix = d.get("fix")
        if not fix:
            continue

        if not fix.get("fixable"):
            continue

        if fix.get("strategy") == "prune":
            key = fix.get("parameters", {}).get("key")
            if key and key in frontmatter:
                del frontmatter[key]
                modified = True

    if not modified:
        # Still write output for determinism
        out_path.write_text(text, encoding="utf-8")
        return

    new_frontmatter = yaml.safe_dump(
        frontmatter,
        sort_keys=False,
        allow_unicode=True,
    ).strip()

    rebuilt = f"---\n{new_frontmatter}\n---{body}"
    out_path.write_text(rebuilt, encoding="utf-8")
