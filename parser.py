"""
parser.py - Parses raw text commands into structured (action, args) tuples.

Supported commands
------------------
  insert <key> <value>   – value may contain spaces
  get    <key>
  delete <key>
  save
  load
  keys
  help
  exit  /  quit
"""

# All recognised command names, normalised to lowercase.
COMMANDS = {"insert", "get", "delete", "save", "load", "keys", "help", "exit", "quit"}


class ParseError(ValueError):
    """Raised when a command cannot be understood."""


def parse(line: str) -> tuple[str, list[str]]:
    """
    Parse a single line of user input into an (action, args) tuple.

    The action is always lowercase.  For `insert`, the value is returned
    as a single string (joining everything after the key), so values that
    contain spaces work correctly:

        insert greeting  Hello, world!
        → ("insert", ["greeting", "Hello, world!"])

    Args:
        line: Raw input string from the user.

    Returns:
        A (action, args) tuple where args is a list of strings.

    Raises:
        ParseError: If the line is empty, the command is unknown, or
                    required arguments are missing.
    """
    stripped = line.strip()
    if not stripped:
        raise ParseError("Empty input — type 'help' to see available commands.")

    tokens = stripped.split()
    action = tokens[0].lower()

    if action not in COMMANDS:
        raise ParseError(
            f"Unknown command '{action}'. Type 'help' to see available commands."
        )

    args = tokens[1:]

    # Per-command argument validation
    if action == "insert":
        if len(args) < 2:
            raise ParseError("Usage: insert <key> <value>")
        # Re-join everything after the key so values can contain spaces.
        key = args[0]
        value = " ".join(args[1:])
        return action, [key, value]

    if action in ("get", "delete"):
        if len(args) != 1:
            raise ParseError(f"Usage: {action} <key>")
        return action, args

    if action in ("save", "load", "keys", "help", "exit", "quit"):
        if args:
            raise ParseError(f"'{action}' takes no arguments.")
        return action, []

    # Should be unreachable, but keeps the linter happy.
    return action, args
