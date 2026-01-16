# File: src/stamp/engine/controller.py

from __future__ import annotations

from typing import Dict, List, Optional

from .loader import Loader
from .parser import MetadataParser
from .validator import Validator
from .normalizer import Normalizer
from .reporter import Reporter
from .dependency_graph import DependencyGraph


class StampController:
    """
    StampController
    ----------------
    Orchestrates the entire Stamp validation/normalization workflow.

    Pipeline (per Stamp-Spec.md):
        1. Load file contents
        2. Parse metadata
        3. Validate metadata (structural & semantic)
        4. Add dependencies to global graph
        5. After all files are processed, detect cycles
        6. Normalize metadata (if repairable issues exist)
        7. Generate machine-readable report
    """

    def __init__(self):
        self.loader = Loader()
        self.parser = MetadataParser()
        self.validator = Validator()
        self.normalizer = Normalizer()
        self.reporter = Reporter()
        self.graph = DependencyGraph()

        # storage for accumulated dependency information
        self._file_metadata: Dict[str, Dict] = {}
        self._file_results: Dict[str, Dict] = {}

    # ----------------------------------------------------------------------
    # MAIN ENTRY POINT
    # ----------------------------------------------------------------------

    def process_files(
        self,
        file_paths: List[str],
        mode: str = "check",
        output_dir: Optional[str] = None
    ) -> Dict[str, Dict]:
        """
        Processes multiple files and returns their reports.

        Steps:
            - Load and parse each file
            - Validate metadata
            - Add deps to dependency graph
            - After all parsed: detect cycles
            - Normalize if required
            - Write outputs (if fix mode)
            - Return structured results
        """

        # Phase 1 — Parse & Validate Each File
        for path in file_paths:
            try:
                self._process_single_file(path)
            except Exception as exc:
                # catastrophic failure for a single file
                self._file_results[path] = self.reporter.fatal(
                    path,
                    [f"Internal error while processing: {exc}"]
                )

        # Phase 2 — Dependency Graph Cycle Detection (Spec §4.1)
        cycles = self.graph.detect_cycles()
        if cycles:
            # fatal errors for ALL files if cycles exist
            cycle = cycles[0]  # report first cycle found
            err_msg = f"Circular dependency detected: {' -> '.join(cycle)}"

            for path in file_paths:
                self._file_results[path] = self.reporter.fatal(
                    path,
                    [err_msg]
                )

            return self._file_results

        # Phase 3 — Apply Fixes or Output Behavior
        if mode == "fix":
            for path, result in self._file_results.items():
                if result.get("status") == "repairable":
                    self._apply_normalization(path, result, output_dir)

        return self._file_results

    # ----------------------------------------------------------------------

    def _process_single_file(self, path: str):
        """
        Process a single file:
            - load
            - parse metadata
            - validate structure
            - push deps to global graph
            - store intermediate results
        """

        raw = self.loader.load_file(path)
        parsed = self.parser.parse(raw)
        metadata = parsed["metadata"]
        body = parsed["body"]

        validation = self.validator.validate(metadata)

        # Add dependency edges (spec: this must occur before graph scan)
        deps = metadata.get("dependencies", [])
        self.graph.add_dependencies(path, deps)

        # store for normalization or reporting
        self._file_metadata[path] = {
            "raw": raw,
            "metadata": metadata,
            "body": body,
            "validation": validation
        }

        # build initial structured result
        if validation["fatal_errors"]:
            self._file_results[path] = self.reporter.fatal(
                path, validation["fatal_errors"]
            )
        elif validation["repairable_errors"]:
            self._file_results[path] = self.reporter.repairable(
                path,
                validation["repairable_errors"],
                validation["warnings"]
            )
        else:
            self._file_results[path] = self.reporter.clean(
                path,
                validation["warnings"]
            )

    # ----------------------------------------------------------------------

    def _apply_normalization(self, path: str, result: Dict, output_dir: Optional[str]):
        """
        Applies deterministic normalization to metadata and writes updated file
        to disk or output directory.
        """
        file_data = self._file_metadata[path]
        metadata = file_data["metadata"]
        body = file_data["body"]

        new_raw = self.normalizer.rewrite(metadata, body)
        self.loader.write_file(
            path=path,
            content=new_raw,
            output_dir=output_dir
        )

        # update report hash and status
        result["rewritten"] = True

