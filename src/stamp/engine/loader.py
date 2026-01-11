# File: src/stamp/engine/loader.py

class Loader:
    """
    Minimal Loader Implementation
    -----------------------------
    Loads text files from disk and returns the content as-is.
    No validation or filtering implemented yet.
    """

    def load_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
