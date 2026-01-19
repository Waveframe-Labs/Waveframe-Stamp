from stamp.validate import validate_artifact
from stamp.extract import ExtractedMetadata
from stamp.schema import ResolvedSchema

from pathlib import Path


def run() -> None:
    print("🔥 Running Stamp smoke test...\n")

    artifact = {
        "title": "Example",
        "internal_id": 123
    }

    schema = {
        "$id": "urn:example:schema",
        "type": "object",
        "properties": {
            "title": {"type": "string"}
        },
        "additionalProperties": False
    }

    extracted = ExtractedMetadata(
        artifact_path=Path("example.json"),
        metadata=artifact,
    )

    resolved_schema = ResolvedSchema(
        identifier=schema["$id"],
        schema=schema,
    )

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
