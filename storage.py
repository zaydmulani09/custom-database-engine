"""
storage.py - Handles persistent file saving and loading for the database engine.

Uses JSON as the on-disk format: human-readable, easy to debug, and
supported natively by Python without third-party dependencies.
"""

import json
import os
import tempfile


def save(filepath: str, data: dict) -> None:
    """
    Persist the database dictionary to a JSON file.

    Uses a write-to-temp-then-rename strategy to avoid corrupting the
    existing file if the process is interrupted mid-write.

    Args:
        filepath: Destination file path (e.g. "mydb.json").
        data:     The dictionary to serialize.

    Raises:
        OSError:           If the file cannot be written.
        TypeError:         If `data` contains values that are not JSON-serializable.
    """
    dir_name = os.path.dirname(os.path.abspath(filepath))

    # Write to a temp file in the same directory so the final rename is atomic.
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())          # Flush kernel buffers to disk.
        os.replace(tmp_path, filepath)    # Atomic on POSIX; best-effort on Windows.
    except Exception:
        # Clean up the temp file if anything went wrong.
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def load(filepath: str) -> dict:
    """
    Load a previously saved JSON file and return its contents as a dictionary.

    Args:
        filepath: Path to the JSON file to load.

    Returns:
        The deserialized dictionary, or an empty dict if the file does not exist.

    Raises:
        ValueError:  If the file exists but contains malformed JSON.
        OSError:     If the file exists but cannot be read.
    """
    if not os.path.exists(filepath):
        return {}

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            contents = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Database file '{filepath}' is corrupted: {e}") from e

    if not isinstance(contents, dict):
        raise ValueError(
            f"Database file '{filepath}' must contain a JSON object, "
            f"got {type(contents).__name__} instead."
        )

    return contents
