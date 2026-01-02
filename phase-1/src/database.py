"""In-memory storage module for the TODO CLI application.

This module provides in-memory storage for to-do items.
Data persists only during the application session.
"""

from typing import List

from src.models import TodoItem


class TodoStorage:
    """In-memory storage for todo items."""

    _instance = None
    _todos: List[TodoItem] = []

    def __new__(cls):
        """Singleton pattern to ensure single storage instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._todos = []
        return cls._instance

    def get_all(self) -> List[TodoItem]:
        """Get all to-do items from memory."""
        return self._todos.copy()

    def add(self, todo: TodoItem) -> None:
        """Add a new to-do item."""
        self._todos.append(todo)

    def get_next_id(self) -> int:
        """Get the next available ID."""
        if not self._todos:
            return 1
        return max(todo.id for todo in self._todos) + 1

    def find_by_id(self, task_id: int) -> TodoItem | None:
        """Find a todo item by its ID."""
        for todo in self._todos:
            if todo.id == task_id:
                return todo
        return None

    def update(self, task_id: int, description: str) -> bool:
        """Update a task's description. Returns True if found."""
        todo = self.find_by_id(task_id)
        if todo:
            todo.description = description
            return True
        return False

    def toggle(self, task_id: int) -> TodoItem | None:
        """Toggle a task's status. Returns the todo if found."""
        todo = self.find_by_id(task_id)
        if todo:
            todo.status = "Completed" if todo.status == "Remaining" else "Remaining"
            return todo
        return None

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID. Returns True if found and deleted."""
        todo = self.find_by_id(task_id)
        if todo:
            self._todos.remove(todo)
            return True
        return False

    def clear(self) -> None:
        """Clear all todos (useful for testing)."""
        self._todos = []


# Global storage instance
storage = TodoStorage()
