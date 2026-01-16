# File: src/stamp/engine/dependency_graph.py

from __future__ import annotations

import os
from typing import Dict, List, Set, Tuple


class DependencyGraph:
    """
    DependencyGraph
    ----------------
    Builds and analyzes a directed graph of Markdown file dependencies as
    described in Stamp-Spec.md §4.1 (Fatal Errors).

    Responsibilities:
        - Add edges between files and their metadata-declared dependencies.
        - Resolve relative paths deterministically.
        - Detect circular dependency cycles.
        - Surface cycle paths for fatal error classification.

    Important Design Notes:
        - The controller will call `add_dependencies()` for each file.
        - After all files are processed, call `detect_cycles()`.
        - Cycles are always treated as fatal errors.
    """

    def __init__(self):
        # adjacency list: { file -> [dependencies] }
        self.graph: Dict[str, List[str]] = {}

    # ----------------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------------

    def add_dependencies(self, file_path: str, dependencies: List[str]) -> None:
        """
        Add dependency edges from file_path → dependencies.
        Only resolves and stores valid Markdown paths.
        """
        resolved_deps = []
        base_dir = os.path.dirname(file_path)

        for dep in dependencies:
            resolved = self._resolve_relative_path(base_dir, dep)

            # Only track .md files
            if resolved.lower().endswith(".md"):
                resolved_deps.append(resolved)

        self.graph[file_path] = resolved_deps

    # ----------------------------------------------------------------------

    def detect_cycles(self) -> List[List[str]]:
        """
        Perform cycle detection using DFS.

        Returns:
            A list of cycles, where each cycle is a list of file paths in order.

        Example:
            [["a.md", "b.md", "c.md", "a.md"]]
        """
        visited: Set[str] = set()
        stack: Set[str] = set()
        cycles: List[List[str]] = []

        for node in self.graph:
            if node not in visited:
                self._dfs(node, visited, stack, cycles, path=[])

        return cycles

    # ----------------------------------------------------------------------
    # INTERNAL HELPERS
    # ----------------------------------------------------------------------

    def _dfs(
        self,
        node: str,
        visited: Set[str],
        stack: Set[str],
        cycles: List[List[str]],
        path: List[str],
    ):
        """
        Depth-first search for cycle detection.

        - visited: tracks nodes fully processed
        - stack: tracks nodes in the current DFS recursion stack
        - path: tracks the traversal path for cycle reconstruction
        """
        visited.add(node)
        stack.add(node)
        path.append(node)

        for neighbor in self.graph.get(node, []):
            if neighbor not in visited:
                self._dfs(neighbor, visited, stack, cycles, path)
            elif neighbor in stack:
                # Found a cycle; extract path slice from neighbor to current
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        stack.remove(node)
        path.pop()

    # ----------------------------------------------------------------------

    def _resolve_relative_path(self, base_dir: str, dep: str) -> str:
        """
        Resolve a relative dependency path deterministically.

        Example:
            base: spec/
            dep: ../docs/file.md
            -> docs/file.md

        Normalizes paths to avoid OS inconsistencies.
        """
        joined = os.path.join(base_dir, dep)
        normalized = os.path.normpath(joined)
        return normalized
