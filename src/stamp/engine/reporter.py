# File: src/stamp/engine/reporter.py

import time

class Reporter:
    """
    Minimal Reporter Implementation
    --------------------------------
    Generates a basic report structure using placeholder values.
    """

    def build_report(self, path: str, original_hash: str,
                     rewritten_hash: str, results: dict) -> dict:
        return {
            "file": path,
            "status": self._status_from_results(results),
            "fatal_errors": results.get("fatal_errors", []),
            "repairable_errors": results.get("repairable_errors", []),
            "warnings": results.get("warnings", []),
            "original_hash": original_hash,
            "rewritten_hash": rewritten_hash,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def _status_from_results(self, results: dict) -> str:
        if results.get("fatal_errors"):
            return "fail"
        if results.get("repairable_errors"):
            return "repairable"
        return "pass"
