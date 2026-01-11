# File: src/stamp/engine/parser.py

class Parser:
    """
    Minimal Parser Implementation
    -----------------------------
    Does NOT parse real YAML frontmatter yet.
    Returns empty metadata, full content as body, and had_meta=False.
    """

    def extract_metadata_block(self, content: str) -> tuple:
        metadata = {}
        body = content
        had_metadata = False
        return metadata, body, had_metadata
