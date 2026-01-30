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

def stamp_validate(schema: dict, instance: dict, schema_path_prefix: str = "") -> list[dict]:
    diagnostics = []

    def prefixed(path: str) -> str:
        return f"{schema_path_prefix}{path}"

    # -------------------------------------------------
    # if / then traversal (root level, leaf-preserving)
    # -------------------------------------------------
    if "if" in schema and "then" in schema:
        if_schema = schema["if"]
        then_schema = schema["then"]

        if instance_matches_schema(if_schema, instance):
            diagnostics.extend(
                stamp_validate(
                    then_schema,
                    instance,
                    schema_path_prefix=f"{schema_path_prefix}/then"
                )
            )
            return diagnostics

    # ----------------------------
    # required
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
                    "schema_path": prefixed("/required"),
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
    # additionalProperties
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
                    "schema_path": prefixed("/additionalProperties"),
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
    # enum
    # ----------------------------
    if (
        schema.get("type") == "object"
        and isinstance(schema.get("properties"), dict)
        and isinstance(instance, dict)
    ):
        for prop, prop_schema in schema["properties"].items():
            if "enum" in prop_schema and prop in instance:
                value = instance[prop]
                allowed = prop_schema["enum"]

                if value not in allowed:
                    diagnostics.append({
                        "id": "enum.mismatch",
                        "severity": "error",
                        "schema_keyword": "enum",
                        "instance_path": f"/{prop}",
                        "schema_path": prefixed(f"/properties/{prop}/enum"),
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
    # type
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
            if "type" in prop_schema and prop in instance:
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
                        "schema_path": prefixed(f"/properties/{prop}/type"),
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
# Runner (unchanged)
# ----------------------------

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_cdo_schema(diagnostics: list[dict], cdo_schema: dict):
    validator = jsonschema.Draft202012Validator(cdo_schema)
    for idx, diag in enumerate(diagnostics):
        errors = list(validator.iter_errors(diag))
        if errors:
            print(f"\n❌ CDO schema validation failed for diagnostic #{idx}")
            for err in errors:
                print(f"  - {err.message}")
            sys.exit(1)


def strip_provenance(diagnostics: list[dict]) -> list[dict]:
    return [{k: v for k, v in d.items() if k != "provenance"} for d in diagnostics]


def sort_diagnostics(diagnostics: list[dict]) -> list[dict]:
    return sorted(diagnostics, key=lambda d: (d["instance_path"], d["schema_keyword"], d["id"]))


def run():
    fixtures = load_json(FIXTURES_PATH)
    cdo_schema = load_json(CDO_SCHEMA_PATH)

    print(f"Running {len(fixtures['cases'])} fixture case(s)...")

    for case in fixtures["cases"]:
        print(f"→ Case: {case['id']}")

        actual = stamp_validate(case["schema"], case["instance"])
        validate_cdo_schema(actual, cdo_schema)

        actual_cmp = sort_diagnostics(strip_provenance(actual))
        expected_cmp = sort_diagnostics(strip_provenance(case["expected_diagnostics"]))

        if actual_cmp != expected_cmp:
            print("\n❌ Fixture mismatch in case:", case["id"])
            print("\nExpected:")
            print(json.dumps(expected_cmp, indent=2))
            print("\nActual:")
            print(json.dumps(actual_cmp, indent=2))
            sys.exit(1)

        print(f"✓ Passed: {case['id']}")

    print("\n✅ All fixture cases passed.")


if __name__ == "__main__":
    run()
