# File: src/stamp/engine/fixer.py

from __future__ import annotations

import difflib
from typing import Dict, Any, List

from .normalizer import Normalizer


class Fixer:
    """
    Fixer
    -----
    Responsible ONLY for mechanical, deterministic repairs:

        - field ordering
        - indentation normalization
        - missing fields that can be defaulted safely
        - type coercions (string/list alignment)
        - canonical formatting fixes

    Rules:
        1. No silent modifications.
        2. Fixes must be explicitly approved.
        3. All fixes must produce a unified diff.
        4. Fixer does NOT validate — Validator does.
        5. Fixer does NOT override semantics — only structure.
        6. CRI-CORE must re-validate after fixes.

    Workflow:
        propose_fix(metadata, body) -> (normalized_str, diff_str)
        apply_fix(path, new_content) -> writes file only when approved
    """

    def __init__(self):
        self.normalizer = Normalizer()

    # ------------------------------------------------------------------ #
    # PROPOSE FIXES                                                      #
    # ------------------------------------------------------------------ #

    def propose_fixes(
        self,
        original_text: str,
        metadata: Dict[str, Any],
        body: str,
    ) -> Dict[str, Any]:
        """
        Generates a proposed normalized version of a file but does NOT apply changes.

        Returns:
            {
                "normalized": <new full text>,
                "diff": <unified diff>,
                "changed": bool
            }
        """
        new_text = self.normalizer.rewrite(metadata, body)

        # No changes → no diff
        if new_text == original_text:
            return {
                "normalized": new_text,
                "diff": "",
                "changed": False,
            }

        diff = self._generate_diff(original_text, new_text)

        return {
            "normalized": new_text,
            "diff": diff,
            "changed": True,
        }

    # ------------------------------------------------------------------ #
    # APPLY FIXES                                                        #
    # ------------------------------------------------------------------ #

    def apply_fixes(
        self,
        path: str,
        proposed_text: str,
        loader,
        output_dir: str | None = None,
    ) -> None:
        """
        Writes the normalized file to disk ONLY when explicitly called.
        Integrates with Loader to ensure deterministic I/O.

        Note:
            This function NEVER decides on its own to apply changes.
            The caller must explicitly confirm the fix.
        """
        loader.write_file(
            path=path,
            content=proposed_text,
            output_dir=output_dir,
        )

    # ------------------------------------------------------------------ #
    # DIFF GENERATION                                                    #
    # ------------------------------------------------------------------ #

    def _generate_diff(self, original: str, new: str) -> str:
        """
        Produce a unified diff with context lines.

        This is critical for:
            - user approval
            - CRI-CORE inspection
            - audit logs
        """
        original_lines = original.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            new_lines,
            fromfile="original",
            tofile="normalized",
            lineterm=""
        )

        return "".join(diff)
