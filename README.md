# SimpleDB

A lightweight key-value database engine built in Python. Supports inserting, retrieving, and deleting string-keyed records, with JSON-based persistence to disk. Built as a computer science project to demonstrate clean separation of concerns across a multi-module Python codebase.

---

## Project Structure

```
simpledb/
├── main.py        # CLI interface and REPL loop
├── database.py    # Core database logic
├── parser.py      # Command parser
├── storage.py     # File saving and loading
└── db.json        # Auto-created on first save
```

Each file has a single responsibility and depends only on the layer below it:

```
main.py  →  database.py  →  storage.py
              ↑
           parser.py
```

---

## Requirements

- Python 3.10 or higher (uses the `tuple[str, list]` type hint syntax)
- No third-party dependencies — only the Python standard library

---

## Getting Started

Clone or download the project, then run:

```bash
python main.py
```

By default, the database saves to `db.json` in the current directory. To use a custom file:

```bash
python main.py mydata.json
```

---

## Commands

| Command | Description |
|---|---|
| `insert <key> <value>` | Add or overwrite a key. Value may contain spaces. |
| `get <key>` | Print the value stored at key. |
| `delete <key>` | Remove a key from the database. |
| `save` | Write the current state to disk. |
| `load` | Reload state from disk (discards unsaved changes). |
| `keys` | List all stored keys in alphabetical order. |
| `help` | Show the command reference. |
| `exit` / `quit` | Save and exit. |

---

## Example Session

```
$ python main.py

SimpleDB — file: 'db.json'  (0 key(s) loaded)
Type 'help' for a list of commands.

db> insert name Alice
Inserted 'name'.

db> insert city New York
Inserted 'city'.

db> get name
name = 'Alice'

db> keys
2 key(s): city, name

db> save
Saved 2 key(s) to 'db.json'.

db> delete city
Deleted 'city'.

db> exit
Saved and exited. Goodbye!
```

---

## File Overview

### `storage.py`
Handles all disk I/O. Uses an atomic write strategy (write to a temp file, then rename) to ensure the database file is never left in a corrupt state if the process is interrupted mid-save. Data is stored as human-readable JSON.

### `database.py`
The `Database` class holds data in a plain Python dictionary and exposes `insert`, `get`, `delete`, `save`, `load`, and `keys` methods. It also supports use as a context manager, which auto-loads on entry and auto-saves on clean exit:

```python
from database import Database

with Database("mydata.json") as db:
    db.insert("language", "Python")
    print(db.get("language"))   # Python
# File is saved automatically here
```

### `parser.py`
Tokenizes a raw input string into an `(action, args)` tuple. Validates argument counts for each command and raises a `ParseError` with a descriptive message on bad input. Multi-word values work correctly — everything after the key is treated as the value:

```
insert motto Never give up
→ ("insert", ["motto", "Never give up"])
```

### `main.py`
The entry point. Runs a REPL (read-eval-print loop) that reads commands, dispatches them to the database, and prints results. Handles `Ctrl-C` and `Ctrl-D` gracefully by saving before exit.

---

## Error Handling

The engine surfaces errors without crashing the session:

```
db> get missing_key
[error] Key 'missing_key' not found.

db> insert
[error] Usage: insert <key> <value>

db> badcommand
[error] Unknown command 'badcommand'. Type 'help' to see available commands.
```

---

## Persistence Format

Data is stored as a plain JSON object in the database file:

```json
{
  "name": "Alice",
  "city": "New York"
}
```

The file can be inspected or edited manually with any text editor.

---

## Limitations

- Values are stored as strings only (no typed values like integers or lists via the CLI).
- No support for concurrent access — the database is designed for single-process use.
- No transaction or rollback support; unsaved changes are lost if the process exits unexpectedly.
- Keys are case-sensitive (`Name` and `name` are different keys).
