# File: src/stamp/engine/validator.py

class Validator:
    """
    Minimal Validator Implementation
    --------------------------------
    Returns empty error sets regardless of input.
    This allows the CLI to operate while real validation is developed.
    """

    def __init__(self, schema: dict = None):
        self.schema = schema or {}

    def validate(self, metadata: dict) -> dict:
        return {
            "fatal_errors": [],
            "repairable_errors": [],
            "warnings": []
        }
