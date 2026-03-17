"""
main.py - Command-line interface for the simple database engine.

Usage
-----
    python main.py                  # uses default file db.json
    python main.py mydata.json      # uses a custom file

Session commands
----------------
    insert <key> <value>    Add or overwrite a key.
    get    <key>            Print the value for a key.
    delete <key>            Remove a key.
    save                    Persist current state to disk.
    load                    Reload state from disk (discards unsaved changes).
    keys                    List all keys.
    help                    Show this help text.
    exit | quit             Save and exit.
"""

import sys

from database import Database
from parser import ParseError, parse

HELP_TEXT = """
Commands:
  insert <key> <value>   Add or overwrite a key-value pair
  get    <key>           Retrieve the value for a key
  delete <key>           Remove a key
  save                   Save the database to disk
  load                   Load the database from disk
  keys                   List all stored keys
  help                   Show this message
  exit / quit            Save and exit
""".strip()


def run(db: Database) -> None:
    """Main REPL loop."""
    print(f"SimpleDB — file: '{db.filepath}'  ({len(db)} key(s) loaded)")
    print("Type 'help' for a list of commands.\n")

    while True:
        try:
            line = input("db> ")
        except (EOFError, KeyboardInterrupt):
            # Ctrl-D or Ctrl-C — treat as a clean exit.
            print("\nInterrupted. Saving and exiting...")
            db.save()
            break

        # ---- Parse -------------------------------------------------------
        try:
            action, args = parse(line)
        except ParseError as e:
            print(f"[error] {e}")
            continue

        # ---- Dispatch ----------------------------------------------------
        try:
            if action == "insert":
                key, value = args
                db.insert(key, value)
                print(f"Inserted '{key}'.")

            elif action == "get":
                value = db.get(args[0])
                print(f"{args[0]} = {value!r}")

            elif action == "delete":
                db.delete(args[0])
                print(f"Deleted '{args[0]}'.")

            elif action == "save":
                db.save()
                print(f"Saved {len(db)} key(s) to '{db.filepath}'.")

            elif action == "load":
                db.load()
                print(f"Loaded {len(db)} key(s) from '{db.filepath}'.")

            elif action == "keys":
                all_keys = db.keys()
                if all_keys:
                    print(f"{len(all_keys)} key(s): " + ", ".join(all_keys))
                else:
                    print("No keys stored yet.")

            elif action == "help":
                print(HELP_TEXT)

            elif action in ("exit", "quit"):
                db.save()
                print(f"Saved and exited. Goodbye!")
                break

        except (KeyError, ValueError, TypeError, OSError) as e:
            print(f"[error] {e}")


def main() -> None:
    filepath = sys.argv[1] if len(sys.argv) > 1 else "db.json"
    db = Database(filepath)

    # Load existing data if the file is already there.
    try:
        db.load()
    except (ValueError, OSError) as e:
        print(f"[warning] Could not load '{filepath}': {e}")
        print("Starting with an empty database.\n")

    run(db)


if __name__ == "__main__":
    main()
