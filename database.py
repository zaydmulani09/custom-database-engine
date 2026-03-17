"""
database.py - Core database logic.

Wraps an in-memory dictionary with insert / get / delete operations
and delegates all persistence to storage.py.
"""

from storage import load, save


class Database:
    def __init__(self, filepath: str = "db.json") -> None:
        """
        Create a Database instance tied to a file on disk.

        The file is NOT loaded automatically — call .load() explicitly,
        or use the Database as a context manager (with Database(...) as db).

        Args:
            filepath: Path to the JSON file used for persistence.
        """
        self.filepath = filepath
        self._data: dict = {}

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def insert(self, key: str, value) -> None:
        """
        Insert or overwrite a key-value pair.

        Args:
            key:   Non-empty string key.
            value: Any JSON-serializable value.

        Raises:
            TypeError:  If key is not a string.
            ValueError: If key is an empty string.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}.")
        if not key:
            raise ValueError("Key must not be empty.")
        self._data[key] = value

    def get(self, key: str):
        """
        Retrieve the value associated with key.

        Args:
            key: The key to look up.

        Returns:
            The stored value.

        Raises:
            KeyError: If the key does not exist.
        """
        if key not in self._data:
            raise KeyError(f"Key '{key}' not found.")
        return self._data[key]

    def delete(self, key: str) -> None:
        """
        Remove a key-value pair.

        Args:
            key: The key to remove.

        Raises:
            KeyError: If the key does not exist.
        """
        if key not in self._data:
            raise KeyError(f"Key '{key}' not found.")
        del self._data[key]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Write the current state to disk."""
        save(self.filepath, self._data)

    def load(self) -> None:
        """Replace the in-memory state with whatever is on disk."""
        self._data = load(self.filepath)

    # ------------------------------------------------------------------
    # Convenience / introspection
    # ------------------------------------------------------------------

    def keys(self) -> list:
        """Return a sorted list of all keys."""
        return sorted(self._data.keys())

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    # Context-manager support: `with Database("db.json") as db:`
    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:          # Only auto-save if no exception occurred.
            self.save()
        return False                  # Do not suppress exceptions.
