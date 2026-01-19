import json
import sys
from pathlib import Path
from copy import deepcopy

import jsonschema


# ----------------------------
# Configuration
# ----------------------------

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_PATH = ROOT / "fixtures" / "fixtures-v1.json"
CDO_SCHEMA_PATH = ROOT / "schemas" / "cdo-v1.schema.json"


# ----------------------------
# Stamp Core (stub)
# ----------------------------

def stamp_validate(schema: dict, instance: dict) -> list[dict]:
    diagnostics = []

    # Handle only root-level "required" for now
    required_fields = schema.get("required", [])
    if not isinstance(required_fields, list):
        return diagnostics

    for field in required_fields:
        if field not in instance:
            diagnostics.append({
                "id": "required.missing",
                "severity": "error",
                "schema_keyword": "required",
                "instance_path": "",
                "schema_path": "/required",
                "message": f"Required property '{field}' is missing.",
                "details": {
                    "missing_property": field
                },
                "fix": None,
                "provenance": {
                    "timestamp": "2026-01-01T00:00:00Z",
                    "stamp_version": "0.1.0-dev",
                    "schema_version": "draft-2020-12",
                    "validator_engine": "stamp-core"
                }
            })

    return diagnostics


# ----------------------------
# Utility functions
# ----------------------------

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_cdo_schema(diagnostics: list[dict], cdo_schema: dict):
    validator = jsonschema.Draft202012Validator(cdo_schema)
    for idx, diag in enumerate(diagnostics):
        errors = sorted(validator.iter_errors(diag), key=lambda e: e.path)
        if errors:
            print(f"\n❌ CDO schema validation failed for diagnostic #{idx}")
            for err in errors:
                print(f"  - {err.message}")
            sys.exit(1)


def strip_provenance(diagnostics: list[dict]) -> list[dict]:
    stripped = []
    for diag in diagnostics:
        d = deepcopy(diag)
        d.pop("provenance", None)
        stripped.append(d)
    return stripped


def sort_diagnostics(diagnostics: list[dict]) -> list[dict]:
    return sorted(
        diagnostics,
        key=lambda d: (
            d.get("instance_path", ""),
            d.get("schema_keyword", ""),
            d.get("id", ""),
        ),
    )


def assert_equal(actual: list[dict], expected: list[dict], case_id: str):
    if actual != expected:
        print(f"\n❌ Fixture mismatch in case: {case_id}")
        print("\nExpected:")
        print(json.dumps(expected, indent=2))
        print("\nActual:")
        print(json.dumps(actual, indent=2))
        sys.exit(1)


# ----------------------------
# Runner
# ----------------------------

def run():
    fixtures = load_json(FIXTURES_PATH)
    cdo_schema = load_json(CDO_SCHEMA_PATH)

    cases = fixtures.get("cases", [])
    if not cases:
        print("⚠️ No fixture cases found.")
        return

    print(f"Running {len(cases)} fixture case(s)...")

    for case in cases:
        case_id = case["id"]
        schema = case["schema"]
        instance = case["instance"]
        expected = case["expected_diagnostics"]

        print(f"→ Case: {case_id}")

        # Run Stamp
        actual = stamp_validate(schema, instance)

        if not isinstance(actual, list):
            print(f"\n❌ stamp_validate must return a list (case: {case_id})")
            sys.exit(1)

        # Step 1: Validate CDO schema
        validate_cdo_schema(actual, cdo_schema)

        # Step 2: Strip provenance for comparison
        actual_cmp = strip_provenance(actual)
        expected_cmp = strip_provenance(expected)

        # Step 3: Deterministic ordering
        actual_cmp = sort_diagnostics(actual_cmp)
        expected_cmp = sort_diagnostics(expected_cmp)

        # Step 4: Deep equality
        assert_equal(actual_cmp, expected_cmp, case_id)

        print(f"✓ Passed: {case_id}")

    print("\n✅ All fixture cases passed.")


if __name__ == "__main__":
    run()
