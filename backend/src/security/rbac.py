import json
from pathlib import Path

PERMISSIONS_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "doc_permissions.json"


def load_permissions() -> dict:
    with open(PERMISSIONS_FILE, "r") as f:
        return json.load(f)


def get_allowed_roles(filename: str, permissions: dict = None) -> list:
    """Return the list of roles allowed to access a given document."""
    if permissions is None:
        permissions = load_permissions()
    return permissions.get(filename, permissions.get("default", ["employee"]))


def is_allowed(filename: str, user_role: str, permissions: dict = None) -> bool:
    """Check if a user role can access a given document."""
    allowed_roles = get_allowed_roles(filename, permissions)
    return user_role in allowed_roles


def filter_chunks_by_role(chunks: list, user_role: str) -> list:
    """
    Filter a list of retrieved chunk dicts (each with a 'source' key)
    down to only those the user's role is permitted to see.
    """
    permissions = load_permissions()
    return [
        chunk for chunk in chunks
        if is_allowed(chunk["source"], user_role, permissions)
    ]


VALID_ROLES = ["employee", "hr", "leadership"]