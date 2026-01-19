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
# Helpers
# ----------------------------

def instance_matches_schema(schema: dict, instance: dict) -> bool:
    try:
        jsonschema.validate(instance=instance, schema=schema)
        return True
    except jsonschema.ValidationError:
        return False


# ----------------------------
# Stamp Core
# ----------------------------

def stamp_validate(schema: dict, instance: dict) -> list[dict]:
    diagnostics = []

    # -------------------------------------------------
    # if / then traversal (root level, leaf-preserving)
    # -------------------------------------------------
    if "if" in schema and "then" in schema:
        if_schema = schema["if"]
        then_schema = schema["then"]

        if instance_matches_schema(if_schema, instance):
            # Validate ONLY against `then` schema
            overlay_schema = {
                "type": schema.get("type", "object"),
                **then_schema
            }
            diagnostics.extend(stamp_validate(overlay_schema, instance))
            return diagnostics

    # ----------------------------
    # required (root level only)
    # ----------------------------
    required_fields = schema.get("required", [])
    if isinstance(required_fields, list):
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

    # ---------------------------------------
    # additionalProperties (root level only)
    # ---------------------------------------
    if (
        schema.get("type") == "object"
        and schema.get("additionalProperties") is False
        and isinstance(instance, dict)
    ):
        allowed_keys = set(schema.get("properties", {}).keys())

        for key in instance.keys():
            if key not in allowed_keys:
                diagnostics.append({
                    "id": "object.no_additional_properties",
                    "severity": "error",
                    "schema_keyword": "additionalProperties",
                    "instance_path": "",
                    "schema_path": "/additionalProperties",
                    "message": f"Property '{key}' is not allowed.",
                    "details": {
                        "property": key
                    },
                    "fix": {
                        "fixable": True,
                        "strategy": "prune",
                        "parameters": {
                            "key": key
                        }
                    },
                    "provenance": {
                        "timestamp": "2026-01-01T00:00:00Z",
                        "stamp_version": "0.1.0-dev",
                        "schema_version": "draft-2020-12",
                        "validator_engine": "stamp-core"
                    }
                })

    # ----------------------------
    # enum (root level properties)
    # ----------------------------
    if (
        schema.get("type") == "object"
        and isinstance(schema.get("properties"), dict)
        and isinstance(instance, dict)
    ):
        for prop, prop_schema in schema["properties"].items():
            if (
                prop in instance
                and isinstance(prop_schema, dict)
                and "enum" in prop_schema
            ):
                allowed = prop_schema["enum"]
                value = instance[prop]

                if value not in allowed:
                    diagnostics.append({
                        "id": "enum.mismatch",
                        "severity": "error",
                        "schema_keyword": "enum",
                        "instance_path": f"/{prop}",
                        "schema_path": f"/properties/{prop}/enum",
                        "message": "Value is not one of the allowed enum values.",
                        "details": {
                            "allowed_values": allowed,
                            "value": value
                        },
                        "fix": None,
                        "provenance": {
                            "timestamp": "2026-01-01T00:00:00Z",
                            "stamp_version": "0.1.0-dev",
                            "schema_version": "draft-2020-12",
                            "validator_engine": "stamp-core"
                        }
                    })

    # ----------------------------
    # type (root level properties)
    # ----------------------------
    python_type_to_schema = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        dict: "object",
        list: "array",
    }

    if (
        schema.get("type") == "object"
        and isinstance(schema.get("properties"), dict)
        and isinstance(instance, dict)
    ):
        for prop, prop_schema in schema["properties"].items():
            if (
                prop in instance
                and isinstance(prop_schema, dict)
                and "type" in prop_schema
            ):
                expected = prop_schema["type"]
                value = instance[prop]

                type_ok = False
                if expected == "string":
                    type_ok = isinstance(value, str)
                elif expected == "number":
                    type_ok = isinstance(value, (int, float)) and not isinstance(value, bool)
                elif expected == "integer":
                    type_ok = isinstance(value, int) and not isinstance(value, bool)
                elif expected == "boolean":
                    type_ok = isinstance(value, bool)
                elif expected == "object":
                    type_ok = isinstance(value, dict)
                elif expected == "array":
                    type_ok = isinstance(value, list)

                if not type_ok:
                    diagnostics.append({
                        "id": "type.mismatch",
                        "severity": "error",
                        "schema_keyword": "type",
                        "instance_path": f"/{prop}",
                        "schema_path": f"/properties/{prop}/type",
                        "message": "Value does not match the expected type.",
                        "details": {
                            "expected_type": expected,
                            "actual_type": python_type_to_schema.get(type(value), type(value).__name__),
                            "value": value
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
# Runner utilities
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

        actual = stamp_validate(schema, instance)

        validate_cdo_schema(actual, cdo_schema)

        actual_cmp = strip_provenance(actual)
        expected_cmp = strip_provenance(expected)

        actual_cmp = sort_diagnostics(actual_cmp)
        expected_cmp = sort_diagnostics(expected_cmp)

        assert_equal(actual_cmp, expected_cmp, case_id)

        print(f"✓ Passed: {case_id}")

    print("\n✅ All fixture cases passed.")


if __name__ == "__main__":
    run()
