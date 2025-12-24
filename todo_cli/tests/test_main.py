import pytest
from typer.testing import CliRunner
import json

from src.main import app 
from src.database import DB_PATH, get_all_todos, save_all_todos
from src.models import TodoItem

runner = CliRunner()

@pytest.fixture(autouse=True)
def cleanup_database():
    """Fixture to ensure a clean database for each test."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    yield
    if DB_PATH.exists():
        DB_PATH.unlink()

def test_add_creates_task():
    """T006: Test that `add` command creates a new task in the database."""
    result = runner.invoke(app, ["add", "Test task 1"])
    assert result.exit_code == 0
    
    todos = get_all_todos()
    assert len(todos) == 1
    assert todos[0].description == "Test task 1"
    assert todos[0].status == "Remaining"
    assert "Task 'Test task 1' has been added." in result.stdout

def test_list_empty():
    """T008: Test that `list` command shows a message when there are no tasks."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No to-do items yet." in result.stdout

def test_list_shows_all_tasks():
    """T007: Test that `list` command shows all tasks correctly."""
    # Given: A database with multiple items
    todos = [
        TodoItem(id=1, description="First task", status="Remaining"),
        TodoItem(id=2, description="Second task", status="Completed")
    ]
    save_all_todos(todos)
    
    # When: The list command is run
    result = runner.invoke(app, ["list"])
    
    # Then: The output should contain the details of all tasks
    assert result.exit_code == 0
    assert "First task" in result.stdout
    assert "Remaining" in result.stdout
    assert "Second task" in result.stdout
    assert "Completed" in result.stdout


# Phase 4: User Story 3 - Update Task Tests

def test_update_task_description():
    """T011: Test that `update` command changes a task's description."""
    # Given: A task exists in the database
    todos = [TodoItem(id=1, description="Buy milk", status="Remaining")]
    save_all_todos(todos)

    # When: The update command is run with a new description
    result = runner.invoke(app, ["update", "1", "Buy almond milk"])

    # Then: The task description should be updated
    assert result.exit_code == 0
    updated_todos = get_all_todos()
    assert len(updated_todos) == 1
    assert updated_todos[0].description == "Buy almond milk"
    assert "updated" in result.stdout.lower()


def test_update_nonexistent_task():
    """T012: Test that updating a non-existent task shows an error."""
    # Given: The database is empty or task doesn't exist
    todos = [TodoItem(id=1, description="Existing task", status="Remaining")]
    save_all_todos(todos)

    # When: The update command is run with a non-existent ID
    result = runner.invoke(app, ["update", "999", "New description"])

    # Then: An error message should be shown
    assert result.exit_code != 0 or "not found" in result.stdout.lower() or "error" in result.stdout.lower()


# Phase 5: User Story 4 - Toggle Task Tests

def test_toggle_status_to_completed():
    """T014: Test that toggling a 'Remaining' task changes it to 'Completed'."""
    # Given: A task with status "Remaining"
    todos = [TodoItem(id=1, description="Walk the dog", status="Remaining")]
    save_all_todos(todos)

    # When: The toggle command is run
    result = runner.invoke(app, ["toggle", "1"])

    # Then: The status should be "Completed"
    assert result.exit_code == 0
    updated_todos = get_all_todos()
    assert updated_todos[0].status == "Completed"


def test_toggle_status_to_remaining():
    """T015: Test that toggling a 'Completed' task changes it to 'Remaining'."""
    # Given: A task with status "Completed"
    todos = [TodoItem(id=1, description="Walk the dog", status="Completed")]
    save_all_todos(todos)

    # When: The toggle command is run
    result = runner.invoke(app, ["toggle", "1"])

    # Then: The status should be "Remaining"
    assert result.exit_code == 0
    updated_todos = get_all_todos()
    assert updated_todos[0].status == "Remaining"


def test_toggle_nonexistent_task():
    """T016: Test that toggling a non-existent task shows an error."""
    # Given: A database with one task
    todos = [TodoItem(id=1, description="Existing task", status="Remaining")]
    save_all_todos(todos)

    # When: The toggle command is run with a non-existent ID
    result = runner.invoke(app, ["toggle", "999"])

    # Then: An error message should be shown
    assert result.exit_code != 0 or "not found" in result.stdout.lower() or "error" in result.stdout.lower()


# Phase 6: User Story 5 - Delete Task Tests

def test_delete_task():
    """T018: Test that `delete` command removes a task from the database."""
    # Given: A database with multiple tasks
    todos = [
        TodoItem(id=1, description="Task to keep", status="Remaining"),
        TodoItem(id=2, description="Task to delete", status="Remaining"),
        TodoItem(id=3, description="Another task to keep", status="Completed")
    ]
    save_all_todos(todos)

    # When: The delete command is run
    result = runner.invoke(app, ["delete", "2"])

    # Then: The task should be removed
    assert result.exit_code == 0
    remaining_todos = get_all_todos()
    assert len(remaining_todos) == 2
    assert all(todo.id != 2 for todo in remaining_todos)
    assert "deleted" in result.stdout.lower()


def test_delete_nonexistent_task():
    """T019: Test that deleting a non-existent task shows an error."""
    # Given: A database with one task
    todos = [TodoItem(id=1, description="Existing task", status="Remaining")]
    save_all_todos(todos)

    # When: The delete command is run with a non-existent ID
    result = runner.invoke(app, ["delete", "999"])

    # Then: An error message should be shown
    assert result.exit_code != 0 or "not found" in result.stdout.lower() or "error" in result.stdout.lower()