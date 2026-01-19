from pathlib import Path
from dataclasses import dataclass
from typing import Iterable, List, Union


EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    "archive",
}


@dataclass(frozen=True)
class DiscoveredArtifact:
    path: Path
    size_bytes: int


def discover_artifacts(
    roots: Iterable[Union[str, Path]]
) -> List[DiscoveredArtifact]:
    """
    Recursively discover candidate artifacts starting from given root paths.

    This function performs filesystem traversal only.
    It does not parse files, inspect contents, or apply schemas.
    """
    artifacts: List[DiscoveredArtifact] = []

    for root in roots:
        root_path = Path(root).resolve()

        if root_path.is_file():
            artifacts.append(
                DiscoveredArtifact(
                    path=root_path,
                    size_bytes=root_path.stat().st_size,
                )
            )
            continue

        if not root_path.is_dir():
            continue

        for path in root_path.rglob("*"):
            if not path.is_file():
                continue

            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue

            try:
                size = path.stat().st_size
            except OSError:
                continue

            artifacts.append(
                DiscoveredArtifact(
                    path=path,
                    size_bytes=size,
                )
            )

    return artifacts
