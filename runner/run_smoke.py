from pathlib import Path

from stamp.validate import validate_artifact
from stamp.extract import ExtractedMetadata
from stamp.schema import ResolvedSchema


def run() -> None:
    print("🔥 Running Stamp smoke test...\n")

    # Simulated artifact content
    artifact = {
        "title": "Example",
        "internal_id": 123
    }

    # Simulated schema
    schema = {
        "$id": "urn:example:schema",
        "type": "object",
        "properties": {
            "title": {"type": "string"}
        },
        "additionalProperties": False
    }

    # ---- Extraction layer (explicit, no shortcuts) ----
    extracted = ExtractedMetadata(
        artifact_path=Path("example.json"),
        metadata=artifact,
        raw_block=artifact,   # In real use, this would be the parsed metadata block
        error=None,           # Explicitly declare extraction succeeded
    )

    # ---- Schema resolution layer ----
    resolved_schema = ResolvedSchema(
        identifier=schema["$id"],
        schema=schema,
    )

    # ---- Validation orchestration ----
    result = validate_artifact(
        extracted=extracted,
        resolved_schema=resolved_schema,
    )

    print("Diagnostics emitted:\n")

    for d in result.diagnostics:
        print(d)

    print("\n✅ Smoke test passed.")


if __name__ == "__main__":
    run()
