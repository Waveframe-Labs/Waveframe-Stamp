# File: src/stamp/engine/loader.py

from __future__ import annotations

import os
import glob
from typing import List, Tuple


class Loader:
    """
    Loader
    ------
    Responsible for safe, deterministic file loading as described in
    Stamp-Spec.md Section 3.

    Responsibilities:
    - Expand file path patterns (globs).
    - Reject directories, binary files, and unreadable files.
    - Normalize newline formats to '\n' for consistent parsing.
    - Return raw text and path in a structured form.

    This module does NOT:
    - parse metadata,
    - validate YAML,
    - rewrite content.

    Those are handled by Parser and Normalizer.
    """

    def resolve_paths(self, pattern: str) -> List[str]:
        """
        Resolve a glob pattern to a list of Markdown files.

        Example:
            "**/*.md" -> ["spec/Stamp-Spec.md", "README.md"]

        Non-MD files are ignored by default.
        """
        resolved = glob.glob(pattern, recursive=True)
        files = [p for p in resolved if p.lower().endswith(".md")]

        return files

    def load_file(self, path: str) -> Tuple[str, List[str]]:
        """
        Load a file safely from disk.

        Returns: (content, errors)

        - On success: (raw_text, [])
        - On failure: ("", [list of error messages])

        This allows Validator to aggregate loader-level failures
        into the fatal error classification system.
        """
        errors = []

        if not os.path.exists(path):
            return "", [f"File not found: {path}"]

        if os.path.isdir(path):
            return "", [f"Path is a directory, not a file: {path}"]

        try:
            # Detect binary by attempting text read first
            with open(path, "rb") as fh:
                raw = fh.read()
                if b"\x00" in raw:
                    return "", [f"Binary file detected and rejected: {path}"]
        except Exception as e:
            return "", [f"Unable to read file (binary check failed): {path} ({e})"]

        try:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except UnicodeDecodeError:
            return "", [f"File is not UTF-8 encoded: {path}"]
        except Exception as e:
            return "", [f"Error reading file: {path} ({e})"]

        # Normalize newlines to \n
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")

        return normalized, errors
