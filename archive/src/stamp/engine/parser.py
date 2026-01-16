# File: src/stamp/engine/parser.py

from __future__ import annotations

import re
from typing import Dict, Tuple


class MetadataParser:
    """
    Extract YAML metadata block and document body.

    The metadata block must appear at the very top of the file and be delimited by '---'.

    Returns a dictionary:
        {
            "metadata": parsed_yaml_dict,
            "body": remaining_markdown_text
        }
    """

    def __init__(self, yaml_loader=None):
        # Defer import of ruamel.yaml until runtime to avoid slow CLI startup.
        if yaml_loader is None:
            from ruamel.yaml import YAML
            yaml_loader = YAML()
            yaml_loader.preserve_quotes = True
        self.yaml_loader = yaml_loader

    # ----------------------------------------------------------------------

    def parse(self, text: str) -> Dict[str, object]:
        """
        Extract metadata block and parse YAML.
        """
        metadata_text, body_text = self._extract_sections(text)
        metadata_obj = self._parse_yaml(metadata_text)

        return {
            "metadata": metadata_obj,
            "body": body_text,
        }

    # ----------------------------------------------------------------------

    def _extract_sections(self, text: str) -> Tuple[str, str]:
        """
        Finds the first YAML block delimited by '---'.
        """

        # Match:
        # ---
        # (yaml content)
        # ---
        pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.search(pattern, text, re.DOTALL)

        if not match:
            # No YAML block found — treat entire file as body with empty metadata
            return "", text

        metadata_text = match.group(1)
        body_text = text[match.end():]
        return metadata_text, body_text

    # ----------------------------------------------------------------------

    def _parse_yaml(self, yaml_text: str) -> Dict:
        """
        Parse YAML safely using ruamel.yaml.
        """
        if not yaml_text.strip():
            return {}

        try:
            return self.yaml_loader.load(yaml_text) or {}
        except Exception:
            # malformed YAML becomes fatal error later in validation
            return {}
