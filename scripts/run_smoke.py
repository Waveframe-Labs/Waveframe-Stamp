from pathlib import Path

from stamp.validate import validate_artifact
from stamp.extract import ExtractedMetadata
from stamp.schema import ResolvedSchema


def run() -> None:
    print("🔥 Running Stamp smoke test...\n")

    artifact = {
        "title": "Example",
        "internal_id": 123,
    }

    schema = {
        "$id": "https://example.org/schema",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"type": "string"}
        }
    }

    extracted = ExtractedMetadata(
        artifact_path=Path("example.json"),
        metadata=artifact,
        raw_block=None,
        error=None,
    )

    resolved_schema = ResolvedSchema(
        identifier=schema["$id"],
        schema=schema,
        source="inline",
        uri=schema["$id"],
    )

    result = validate_artifact(
        extracted=extracted,
        resolved_schema=resolved_schema,
    )

    diagnostics = result.diagnostics

    print("Diagnostics emitted:\n")
    for d in diagnostics:
        print(d)

    # --- ABI ASSERTIONS (LOCKED) --------------------------------------

    assert len(diagnostics) == 1, "Expected exactly one diagnostic"

    diag = diagnostics[0]

    # Canonical ID (semantic, not jsonschema-derived)
    assert diag["id"] == "object.no_additional_properties"

    # Keyword preserved
    assert diag["schema_keyword"] == "additionalProperties"

    # Path formatting
    assert diag["instance_path"] == ""
    assert diag["schema_path"] == "/additionalProperties"

    # Fix contract
    assert diag["fix"] is not None
    assert diag["fix"]["fixable"] is True
    assert diag["fix"]["strategy"] == "prune"
    assert diag["fix"]["parameters"]["key"] == "internal_id"

    print("\n✅ Smoke test passed and ABI locked.")


if __name__ == "__main__":
    run()
