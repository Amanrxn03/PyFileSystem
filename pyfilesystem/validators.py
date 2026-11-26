import re

_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._ -]{0,63}$")

def validate_name(name: str) -> str:
    if not isinstance(name, str):
        raise ValueError("Name must be text.")
    name = name.strip()
    if not name or name in {".", ".."} or not _SAFE_NAME.fullmatch(name):
        raise ValueError("Use 1-64 letters, numbers, spaces, dots, underscores or hyphens; do not use . or ..")
    if name.startswith(".") and name in {".", ".."}:
        raise ValueError("Invalid name.")
    return name

def validate_size(size, maximum=10_000):
    try:
        value = int(size)
    except (TypeError, ValueError):
        raise ValueError("Size must be a whole number.")
    if value < 0 or value > maximum:
        raise ValueError(f"Size must be between 0 and {maximum} KB.")
    return value

def validate_record_position(position, record_count):
    try:
        pos = int(position)
    except (TypeError, ValueError):
        raise ValueError("Record position must be an integer.")
    if pos < 0 or pos >= record_count:
        raise IndexError(f"Record position must be between 0 and {max(0, record_count-1)}.")
    return pos
