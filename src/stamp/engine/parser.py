# File: src/stamp/engine/parser.py

from __future__ import annotations

from typing import Dict, Tuple

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError


class Parser:
    """
    Parser
    ------
    Responsible for detecting and extracting the top-of-file YAML metadata
    block used by ARI-governed Markdown documents.

    This implementation:

    - Looks for a leading `---` fence at the very start of the file.
    - Extracts everything between the first and second `---` as YAML.
    - Parses the YAML using ruamel.yaml in round-trip mode to preserve
      ordering, comments, and formatting for future normalization steps.
    - Returns the remaining content as the Markdown body unchanged.

    It does NOT perform any schema validation. That is the responsibility of
    the Validator component.
    """

    def __init__(self) -> None:
        # Round-trip mode preserves comments, ordering, and formatting so that
        # normalization can rewrite metadata without destroying structure.
        self._yaml = YAML(typ="rt")
        self._yaml.preserve_quotes = True

    def extract_metadata_block(self, content: str) -> Tuple[Dict, str, bool]:
        """
        Extract the YAML metadata block from the top of a Markdown file.

        Returns a tuple: (metadata_dict, body_str, had_metadata)

        - metadata_dict: a mapping parsed from the YAML frontmatter, or {} if
          no valid metadata block was found or the YAML could not be parsed.
        - body_str: the remainder of the document after the metadata fences.
        - had_metadata: True if a metadata fence was detected at the top of
          the file, False otherwise.

        Design choices:

        - If there is no leading `---` fence, the entire file is treated as
          body content (no metadata).
        - If a fence is opened but never closed, the function treats the file
          as having no usable metadata and returns the original content as
          body. The Validator layer will later classify this as a fatal error.
        - If YAML parsing fails, we return an empty metadata dict but keep
          had_metadata=True so the Validator can distinguish “present but
          invalid” from “not present”.
        """
        if not content:
            return {}, "", False

        lines = content.splitlines(keepends=True)
        if not lines:
            return {}, content, False

        # ARI-governed files are expected to begin with a YAML frontmatter
        # block. We only treat it as such if the very first line is `---`.
        first_line = lines[0].strip()
        if first_line != "---":
            # No leading metadata fence; treat entire file as body.
            return {}, content, False

        # Find closing fence.
        closing_index = None
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                closing_index = idx
                break

        if closing_index is None:
            # Unterminated fence: for now, treat as no usable metadata and
            # pass the content through unchanged. Validator will later be
            # responsible for flagging this as a fatal structural error.
            return {}, content, False

        # Extract raw YAML between the fences and the body after them.
        yaml_block = "".join(lines[1:closing_index])
        body = "".join(lines[closing_index + 1 :])

        if not yaml_block.strip():
            # Empty metadata block: considered metadata-present but empty.
            return {}, body, True

        try:
            parsed = self._yaml.load(yaml_block)
        except YAMLError:
            # Malformed YAML. We signal that a metadata fence was present
            # (had_metadata=True) but return an empty dict for now.
            return {}, body, True

        if parsed is None:
            metadata = {}
        elif isinstance(parsed, dict):
            # ruamel.yaml returns an order-preserving CommentedMap; leaving this
            # intact allows the Normalizer to operate without losing structure.
            metadata = parsed
        else:
            # Non-mapping YAML at the top is considered invalid metadata.
            metadata = {}

        return metadata, body, True
