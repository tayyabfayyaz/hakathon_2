"""Database module for the TODO CLI application.

This module handles all file-based persistence for to-do items,
including atomic writes to prevent data corruption.
"""

import json
import os
import pathlib
import tempfile
from typing import List

from src.models import TodoItem

# Define the path to the database file
DB_PATH = pathlib.Path("todo_database.json")


def init_database():
    """Initialize the database file if it doesn't exist.

    Creates an empty JSON array file at DB_PATH if no file exists.
    """
    if not DB_PATH.exists():
        DB_PATH.write_text("[]")


def get_all_todos() -> List[TodoItem]:
    """Read all to-do items from the database.

    Returns:
        List of TodoItem objects. Returns empty list if database
        is empty or contains invalid JSON.
    """
    init_database()  # Ensure DB exists before reading
    with open(DB_PATH, "r") as f:
        try:
            data = json.load(f)
            return [TodoItem(**item) for item in data]
        except json.JSONDecodeError:
            return []


def save_all_todos(todos: List[TodoItem]):
    """Save all to-do items to the database with atomic write.

    Uses a temporary file and atomic replace to prevent data
    corruption in case of interruption.

    Args:
        todos: List of TodoItem objects to persist.

    Raises:
        Exception: If writing fails, the exception is re-raised
        after cleaning up the temporary file.
    """
    # Use a temporary file to write the new data
    temp_fd, temp_path_str = tempfile.mkstemp(dir=DB_PATH.parent)
    temp_path = pathlib.Path(temp_path_str)

    try:
        with os.fdopen(temp_fd, 'w') as temp_file:
            # Serialize the list of TodoItem models to a list of dicts
            json_data = [item.model_dump() for item in todos]
            json.dump(json_data, temp_file, indent=4)

        # Atomically replace the old database file with the new one
        os.replace(temp_path, DB_PATH)
    except Exception as e:
        # If something goes wrong, clean up the temporary file
        temp_path.unlink()
        raise e
