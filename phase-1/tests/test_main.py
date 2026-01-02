"""Tests for the in-memory TODO CLI application."""

import pytest
from src.database import storage, TodoStorage
from src.models import TodoItem


@pytest.fixture(autouse=True)
def cleanup_storage():
    """Fixture to ensure clean storage for each test."""
    storage.clear()
    yield
    storage.clear()


class TestTodoStorage:
    """Tests for the TodoStorage class."""

    def test_singleton_pattern(self):
        """Test that TodoStorage follows singleton pattern."""
        storage1 = TodoStorage()
        storage2 = TodoStorage()
        assert storage1 is storage2

    def test_get_all_empty(self):
        """Test getting all todos when storage is empty."""
        todos = storage.get_all()
        assert todos == []

    def test_add_todo(self):
        """Test adding a new todo item."""
        todo = TodoItem(id=1, description="Test task", status="Remaining")
        storage.add(todo)

        todos = storage.get_all()
        assert len(todos) == 1
        assert todos[0].description == "Test task"
        assert todos[0].status == "Remaining"

    def test_get_next_id_empty(self):
        """Test getting next ID when storage is empty."""
        assert storage.get_next_id() == 1

    def test_get_next_id_with_items(self):
        """Test getting next ID with existing items."""
        storage.add(TodoItem(id=1, description="Task 1"))
        storage.add(TodoItem(id=5, description="Task 2"))
        assert storage.get_next_id() == 6

    def test_find_by_id_exists(self):
        """Test finding a todo by ID when it exists."""
        todo = TodoItem(id=1, description="Test task")
        storage.add(todo)

        found = storage.find_by_id(1)
        assert found is not None
        assert found.description == "Test task"

    def test_find_by_id_not_exists(self):
        """Test finding a todo by ID when it doesn't exist."""
        storage.add(TodoItem(id=1, description="Test task"))
        assert storage.find_by_id(999) is None


class TestUpdateTask:
    """Tests for updating tasks."""

    def test_update_task_description(self):
        """Test that update changes a task's description."""
        storage.add(TodoItem(id=1, description="Buy milk"))

        result = storage.update(1, "Buy almond milk")

        assert result is True
        todo = storage.find_by_id(1)
        assert todo.description == "Buy almond milk"

    def test_update_nonexistent_task(self):
        """Test that updating a non-existent task returns False."""
        storage.add(TodoItem(id=1, description="Existing task"))

        result = storage.update(999, "New description")

        assert result is False


class TestToggleTask:
    """Tests for toggling task status."""

    def test_toggle_status_to_completed(self):
        """Test toggling a 'Remaining' task to 'Completed'."""
        storage.add(TodoItem(id=1, description="Walk the dog", status="Remaining"))

        todo = storage.toggle(1)

        assert todo is not None
        assert todo.status == "Completed"

    def test_toggle_status_to_remaining(self):
        """Test toggling a 'Completed' task to 'Remaining'."""
        storage.add(TodoItem(id=1, description="Walk the dog", status="Completed"))

        todo = storage.toggle(1)

        assert todo is not None
        assert todo.status == "Remaining"

    def test_toggle_nonexistent_task(self):
        """Test that toggling a non-existent task returns None."""
        storage.add(TodoItem(id=1, description="Existing task"))

        result = storage.toggle(999)

        assert result is None


class TestDeleteTask:
    """Tests for deleting tasks."""

    def test_delete_task(self):
        """Test that delete removes a task from storage."""
        storage.add(TodoItem(id=1, description="Task to keep"))
        storage.add(TodoItem(id=2, description="Task to delete"))
        storage.add(TodoItem(id=3, description="Another task to keep"))

        result = storage.delete(2)

        assert result is True
        todos = storage.get_all()
        assert len(todos) == 2
        assert all(todo.id != 2 for todo in todos)

    def test_delete_nonexistent_task(self):
        """Test that deleting a non-existent task returns False."""
        storage.add(TodoItem(id=1, description="Existing task"))

        result = storage.delete(999)

        assert result is False


class TestTodoItem:
    """Tests for the TodoItem model."""

    def test_default_status(self):
        """Test that default status is 'Remaining'."""
        todo = TodoItem(id=1, description="Test task")
        assert todo.status == "Remaining"

    def test_description_required(self):
        """Test that description cannot be empty."""
        with pytest.raises(ValueError):
            TodoItem(id=1, description="")

    def test_valid_statuses(self):
        """Test valid status values."""
        remaining = TodoItem(id=1, description="Task", status="Remaining")
        completed = TodoItem(id=2, description="Task", status="Completed")

        assert remaining.status == "Remaining"
        assert completed.status == "Completed"
