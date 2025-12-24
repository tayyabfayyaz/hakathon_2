"""TODO CLI - A command-line to-do list application.

This module provides the CLI interface for managing to-do items.
Available commands: add, list, update, toggle, delete.

Usage:
    python -m src.main add "Task description"
    python -m src.main list
    python -m src.main update 1 "New description"
    python -m src.main toggle 1
    python -m src.main delete 1
"""

import typer

from src.database import get_all_todos, save_all_todos
from src.models import TodoItem

app = typer.Typer(help="A simple command-line to-do list application.")


@app.command()
def add(description: str):
    """Add a new to-do item."""
    todos = get_all_todos()
    # Find the maximum existing ID and add 1, or start at 1 if no todos exist
    new_id = max([todo.id for todo in todos] or [0]) + 1
    new_todo = TodoItem(id=new_id, description=description)
    todos.append(new_todo)
    save_all_todos(todos)
    print(f"Task '{description}' has been added.")


@app.command(name="list")
def list_todos():
    """List all to-do items."""
    todos = get_all_todos()
    if not todos:
        print("No to-do items yet.")
        return

    print("ID | Description | Status")
    print("-- | --- | ---")
    for todo in todos:
        print(f"{todo.id} | {todo.description} | {todo.status}")


def _find_todo_by_id(todos: list[TodoItem], task_id: int) -> TodoItem | None:
    """Find a todo item by its ID. Returns None if not found."""
    for todo in todos:
        if todo.id == task_id:
            return todo
    return None


@app.command()
def update(task_id: int, description: str):
    """Update the description of an existing to-do item."""
    todos = get_all_todos()
    todo = _find_todo_by_id(todos, task_id)

    if todo is None:
        print(f"Error: Task with ID {task_id} not found.")
        raise typer.Exit(code=1)

    todo.description = description
    save_all_todos(todos)
    print(f"Task {task_id} has been updated.")


@app.command()
def toggle(task_id: int):
    """Toggle the status of a to-do item between 'Remaining' and 'Completed'."""
    todos = get_all_todos()
    todo = _find_todo_by_id(todos, task_id)

    if todo is None:
        print(f"Error: Task with ID {task_id} not found.")
        raise typer.Exit(code=1)

    # Toggle the status
    if todo.status == "Remaining":
        todo.status = "Completed"
    else:
        todo.status = "Remaining"

    save_all_todos(todos)
    print(f"Task {task_id} status changed to '{todo.status}'.")


@app.command()
def delete(task_id: int):
    """Delete a to-do item by its ID."""
    todos = get_all_todos()
    todo = _find_todo_by_id(todos, task_id)

    if todo is None:
        print(f"Error: Task with ID {task_id} not found.")
        raise typer.Exit(code=1)

    todos.remove(todo)
    save_all_todos(todos)
    print(f"Task {task_id} has been deleted.")


if __name__ == "__main__":
    app()
