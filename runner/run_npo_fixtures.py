import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

# Ensure repo root is on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stamp.normalize import StampNormalize


FIXTURES_PATH = ROOT / "fixtures" / "npo-fixtures-v1.json"
NPO_SCHEMA_PATH = ROOT / "schemas" / "npo-v1.schema.json"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def strip_nondeterministic(npo: dict) -> dict:
    npo = dict(npo)
    npo.pop("generated_at", None)
    return npo


def sort_proposals(npo: dict) -> dict:
    npo = dict(npo)
    npo["proposals"] = sorted(npo.get("proposals", []), key=lambda p: p["id"])
    return npo


def run():
    fixtures = load_json(FIXTURES_PATH)
    npo_schema = load_json(NPO_SCHEMA_PATH)

    normalizer = StampNormalize(stamp_version="0.1.0")

    print(f"Running {len(fixtures['cases'])} NPO fixture case(s)...")

    for case in fixtures["cases"]:
        print(f"→ Case: {case['id']}")

        result = normalizer.normalize(
            diagnostics=case["input"]["diagnostics"],
            source_artifact=case["input"]["source_artifact"],
            schema_context=case["input"]["schema_context"],
        )

        # Validate output schema
        try:
            validate(instance=result, schema=npo_schema)
        except ValidationError as e:
            print(f"\n❌ Schema validation failed in case: {case['id']}")
            print(e)
            sys.exit(1)

        expected = {
            "proposals": case["expected_proposals"],
            "summary": case["expected_summary"],
        }

        actual = strip_nondeterministic(result)
        actual = sort_proposals(actual)

        if actual["summary"] != expected["summary"] or actual["proposals"] != expected["proposals"]:
            print(f"\n❌ Fixture mismatch in case: {case['id']}\n")
            print("Expected summary:")
            print(json.dumps(expected["summary"], indent=2))
            print("\nActual summary:")
            print(json.dumps(actual["summary"], indent=2))

            print("\nExpected proposals:")
            print(json.dumps(expected["proposals"], indent=2))
            print("\nActual proposals:")
            print(json.dumps(actual["proposals"], indent=2))
            sys.exit(1)

        print(f"✓ Passed: {case['id']}")

    print("\n✅ All NPO fixture cases passed.")


if __name__ == "__main__":
    run()
