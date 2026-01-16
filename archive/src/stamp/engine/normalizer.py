# File: src/stamp/engine/normalizer.py

from __future__ import annotations

from typing import Dict, Any, Tuple, List
from datetime import datetime

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class Normalizer:
    """
    Normalizer
    ----------
    Implements deterministic rewriting of metadata according to:

    - ARI Metadata Policy v3.0.1
    - Stamp-Spec.md §5.1 (Normalized File Output)
    - Repairable error rules in Stamp-Spec.md §4.2

    Responsibilities:
        - Insert missing required fields that can be deterministically inferred.
        - Fix ordering of metadata keys.
        - Inject placeholder DOIs for unreleased versions.
        - Add ai_assistance_details when required.
        - Update `updated` timestamp only when other corrections occur.
        - Preserve YAML formatting using ruamel.yaml round-trip mode.
        - DO NOT modify the Markdown body.

    Inputs:
        metadata: dict (from Parser validated by Validator)
        body: str (original markdown body)

    Outputs:
        rewritten_yaml: str (normalized YAML frontmatter)
        body: str (unchanged)
        corrections: List[str] (list of applied changes)
    """

    # Canonical ordering required by ARI Metadata Policy
    CANONICAL_ORDER = [
        "title",
        "filetype",
        "type",
        "domain",
        "version",
        "doi",
        "status",
        "created",
        "updated",
        "author",
        "maintainer",
        "license",
        "copyright",
        "ai_assisted",
        "ai_assistance_details",
        "dependencies",
        "anchors",
    ]

    def __init__(self) -> None:
        self.yaml = YAML(typ="rt")
        self.yaml.preserve_quotes = True

    # -------------------------------------------------------------------------
    # PUBLIC INTERFACE
    # -------------------------------------------------------------------------

    def normalize(self, metadata: Dict[str, Any], body: str) -> Tuple[str, str, List[str]]:
        """
        Perform deterministic metadata normalization.

        Returns:
            (yaml_text, body_text, corrections_list)
        """
        corrections: List[str] = []

        # Copy metadata into a round-trip-safe structure
        cleaned = CommentedMap()
        for key, value in metadata.items():
            cleaned[key] = value

        # Apply ordering
        ordered = self._apply_canonical_order(cleaned, corrections)

        # Fill missing deterministically repairable fields
        self._apply_repairable_defaults(ordered, corrections)

        # Fix AI-assisted logic if needed
        self._fix_ai_assisted_rules(ordered, corrections)

        # Auto-update timestamp if other repairs occurred
        self._maybe_update_timestamp(ordered, corrections)

        # Dump to YAML string with preserved formatting
        yaml_text = self._dump_yaml(ordered)

        return yaml_text, body, corrections

    # -------------------------------------------------------------------------
    # INTERNAL HELPERS
    # -------------------------------------------------------------------------

    def _apply_canonical_order(
        self,
        metadata: CommentedMap,
        corrections: List[str],
    ) -> CommentedMap:
        """
        Reorder fields into canonical ARI ordering.

        Missing fields are preserved and appended later by defaults logic.
        """
        new_map = CommentedMap()

        # Keep track of original keys for ordering differences
        original_keys = list(metadata.keys())

        for key in self.CANONICAL_ORDER:
            if key in metadata:
                new_map[key] = metadata[key]

        # Copy additional unknown fields (should not happen under ARI Governance)
        for key in metadata:
            if key not in new_map:
                new_map[key] = metadata[key]

        if list(new_map.keys()) != original_keys:
            corrections.append("Reordered metadata fields into canonical ARI ordering.")

        return new_map

    # -------------------------------------------------------------------------

    def _apply_repairable_defaults(
        self,
        metadata: CommentedMap,
        corrections: List[str],
    ) -> None:
        """
        Add missing fields that can be deterministically filled without violating
        provenance rules (Spec §4.2).

        These include:
            - anchors: []
            - dependencies: []
            - ai_assistance_details when required
            - placeholder doi: "TBD-x.y.z"
        """

        # Default empty arrays
        if "anchors" in metadata and metadata["anchors"] in (None, ""):
            metadata["anchors"] = []
            corrections.append("Injected empty anchors list.")

        if "dependencies" in metadata and metadata["dependencies"] in (None, ""):
            metadata["dependencies"] = []
            corrections.append("Injected empty dependencies list.")

        # Unreleased version DOI fallback
        version = metadata.get("version")
        doi = metadata.get("doi")

        if version and (doi is None or doi.startswith("TBD")):
            placeholder = f"TBD-{version}"
            if doi != placeholder:
                metadata["doi"] = placeholder
                corrections.append(f"Added placeholder DOI: {placeholder}")

    # -------------------------------------------------------------------------

    def _fix_ai_assisted_rules(
        self,
        metadata: CommentedMap,
        corrections: List[str],
    ) -> None:
        """
        Enforce ai_assisted vs ai_assistance_details consistency rules.

        Must follow:
          - If ai_assisted=none → ai_assistance_details must be removed.
          - If ai_assisted=partial/extensive → ai_assistance_details must exist.
        """
        ai = metadata.get("ai_assisted")
        details = metadata.get("ai_assistance_details")

        if ai == "none" and details:
            metadata["ai_assistance_details"] = None
            corrections.append("Removed ai_assistance_details (ai_assisted='none').")

        if ai in ("partial", "extensive") and not details:
            metadata["ai_assistance_details"] = (
                "AI-assisted normalization performed by Stamp."
            )
            corrections.append("Inserted ai_assistance_details for AI-assisted document.")

    # -------------------------------------------------------------------------

    def _maybe_update_timestamp(
        self,
        metadata: CommentedMap,
        corrections: List[str],
    ) -> None:
        """
        Update `updated` only when other corrections occurred.

        Must follow:
            - Stamp MUST NOT update updated date if *only* updating updated itself.
            - Stamp MUST update updated date if any other repair took place.
        """
        if not corrections:
            return  # no changes → do nothing

        # Only update updated if something else changed (Spec Section B re: timestamp loop)
        now = datetime.utcnow().strftime("%Y-%m-%d")
        original = metadata.get("updated")

        if original != now:
            metadata["updated"] = now
            corrections.append(f"Updated 'updated' timestamp to {now} (due to repairs).")

    # -------------------------------------------------------------------------

    def _dump_yaml(self, metadata: CommentedMap) -> str:
        """
        Output the normalized YAML as a string with preserved formatting.
        """
        from io import StringIO

        buf = StringIO()
        self.yaml.dump(metadata, buf)
        return buf.getvalue()
