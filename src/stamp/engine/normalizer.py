# File: src/stamp/engine/normalizer.py

class Normalizer:
    """
    Minimal Normalizer Implementation
    ---------------------------------
    Returns metadata unchanged, without applying canonical ordering
    or formatting adjustments. Placeholder behavior only.
    """

    def normalize(self, metadata: dict, repairs: list) -> dict:
        return metadata
