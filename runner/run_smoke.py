import json
from pathlib import Path

from stamp.validate import validate_artifact


def run():
    print("🔥 Running Stamp smoke test...\n")

    # --- Minimal schema ---
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:smoke:schema",
        "type": "object",
        "required": ["title"],
        "properties": {
            "title": {"type": "string"}
        },
        "additionalProperties": False  
    }

    # --- Minimal artifact (intentionally invalid) ---
    artifact = {
        "unexpected": "boom"
    }

    diagnostics = validate_artifact(
        artifact=artifact,
        schema=schema,
        schema_id=schema["$id"]
    )

    # --- Assertions (manual, explicit) ---
    if not diagnostics:
        raise RuntimeError("Smoke test FAILED: No diagnostics returned")

    print("Diagnostics emitted:\n")
    for d in diagnostics:
        print(json.dumps(d, indent=2))

    print("\n✅ Smoke test PASSED")


if __name__ == "__main__":
    run()
