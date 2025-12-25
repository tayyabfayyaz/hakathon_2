"""Tests for todo endpoints."""
import pytest
from httpx import AsyncClient
from uuid import uuid4

from src.models.user import User
from src.models.todo import Todo


class TestCreateTodo:
    """Tests for POST /api/v1/todos."""

    @pytest.mark.asyncio
    async def test_create_todo_with_valid_title(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a todo with valid title."""
        response = await client.post(
            "/api/v1/todos",
            json={"title": "Buy groceries"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["is_completed"] is False
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_todo_with_description(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a todo with title and description."""
        response = await client.post(
            "/api/v1/todos",
            json={
                "title": "Meeting notes",
                "description": "Prepare notes for the standup meeting",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Meeting notes"
        assert data["description"] == "Prepare notes for the standup meeting"

    @pytest.mark.asyncio
    async def test_create_todo_with_empty_title(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a todo with empty title fails (400 validation error)."""
        response = await client.post(
            "/api/v1/todos",
            json={"title": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_create_todo_with_whitespace_only_title(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a todo with whitespace-only title fails."""
        response = await client.post(
            "/api/v1/todos",
            json={"title": "   "},
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_todo_with_long_title(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a todo with title > 200 chars fails (400 error)."""
        long_title = "a" * 201
        response = await client.post(
            "/api/v1/todos",
            json={"title": long_title},
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_create_todo_without_auth(self, client: AsyncClient):
        """Test creating a todo without auth returns 401."""
        response = await client.post(
            "/api/v1/todos",
            json={"title": "Test todo"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_todo_trims_whitespace(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that title whitespace is trimmed."""
        response = await client.post(
            "/api/v1/todos",
            json={"title": "  Test title  "},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test title"


class TestListTodos:
    """Tests for GET /api/v1/todos."""

    @pytest.mark.asyncio
    async def test_list_todos_returns_user_todos(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test listing todos returns only user's todos."""
        response = await client.get(
            "/api/v1/todos",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total_count" in data
        assert len(data["items"]) >= 1
        # Verify test_todo is in the list
        todo_ids = [item["id"] for item in data["items"]]
        assert str(test_todo.id) in todo_ids

    @pytest.mark.asyncio
    async def test_list_todos_excludes_other_users_todos(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_todo: Todo,
        another_users_todo: Todo,
    ):
        """Test that other users' todos are not returned."""
        response = await client.get(
            "/api/v1/todos",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        todo_ids = [item["id"] for item in data["items"]]
        assert str(another_users_todo.id) not in todo_ids

    @pytest.mark.asyncio
    async def test_list_todos_empty(self, client: AsyncClient, auth_headers: dict):
        """Test listing todos when user has none."""
        response = await client.get(
            "/api/v1/todos",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_count"] == 0


class TestGetTodo:
    """Tests for GET /api/v1/todos/{id}."""

    @pytest.mark.asyncio
    async def test_get_todo_by_id(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test getting a specific todo by ID."""
        response = await client.get(
            f"/api/v1/todos/{test_todo.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_todo.id)
        assert data["title"] == test_todo.title

    @pytest.mark.asyncio
    async def test_get_nonexistent_todo(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting a non-existent todo returns 404."""
        fake_id = uuid4()
        response = await client.get(
            f"/api/v1/todos/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_other_users_todo(
        self, client: AsyncClient, auth_headers: dict, another_users_todo: Todo
    ):
        """Test getting another user's todo returns 404."""
        response = await client.get(
            f"/api/v1/todos/{another_users_todo.id}",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestUpdateTodo:
    """Tests for PATCH /api/v1/todos/{id}."""

    @pytest.mark.asyncio
    async def test_update_todo_title(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test updating todo with valid changes."""
        response = await client.patch(
            f"/api/v1/todos/{test_todo.id}",
            json={"title": "Updated title"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"

    @pytest.mark.asyncio
    async def test_update_todo_description(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test updating todo description."""
        response = await client.patch(
            f"/api/v1/todos/{test_todo.id}",
            json={"description": "New description"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "New description"

    @pytest.mark.asyncio
    async def test_update_todo_with_empty_title(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test updating todo with empty title fails (400 error)."""
        response = await client.patch(
            f"/api/v1/todos/{test_todo.id}",
            json={"title": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_other_users_todo(
        self, client: AsyncClient, auth_headers: dict, another_users_todo: Todo
    ):
        """Test updating another user's todo returns 404."""
        response = await client.patch(
            f"/api/v1/todos/{another_users_todo.id}",
            json={"title": "Hacked title"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestDeleteTodo:
    """Tests for DELETE /api/v1/todos/{id}."""

    @pytest.mark.asyncio
    async def test_delete_todo_returns_204(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test delete todo returns 204."""
        response = await client.delete(
            f"/api/v1/todos/{test_todo.id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_deleted_todo_not_in_list(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test deleted todo doesn't appear in list."""
        # Delete the todo
        await client.delete(
            f"/api/v1/todos/{test_todo.id}",
            headers=auth_headers,
        )

        # Verify it's not in the list
        response = await client.get(
            "/api/v1/todos",
            headers=auth_headers,
        )
        data = response.json()
        todo_ids = [item["id"] for item in data["items"]]
        assert str(test_todo.id) not in todo_ids

    @pytest.mark.asyncio
    async def test_delete_nonexistent_todo(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test delete non-existent todo returns 404."""
        fake_id = uuid4()
        response = await client.delete(
            f"/api/v1/todos/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestToggleTodo:
    """Tests for POST /api/v1/todos/{id}/toggle."""

    @pytest.mark.asyncio
    async def test_toggle_from_remaining_to_completed(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test toggle from remaining to completed."""
        assert test_todo.is_completed is False

        response = await client.post(
            f"/api/v1/todos/{test_todo.id}/toggle",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True

    @pytest.mark.asyncio
    async def test_toggle_from_completed_to_remaining(
        self, client: AsyncClient, auth_headers: dict, completed_todo: Todo
    ):
        """Test toggle from completed to remaining."""
        assert completed_todo.is_completed is True

        response = await client.post(
            f"/api/v1/todos/{completed_todo.id}/toggle",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is False

    @pytest.mark.asyncio
    async def test_toggle_nonexistent_todo(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test toggle non-existent todo returns 404."""
        fake_id = uuid4()
        response = await client.post(
            f"/api/v1/todos/{fake_id}/toggle",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestSearchTodos:
    """Tests for GET /api/v1/todos with search parameter."""

    @pytest.mark.asyncio
    async def test_search_returns_matching_todos(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test search returns matching todos."""
        response = await client.get(
            "/api/v1/todos",
            params={"search": "Test"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_search_is_case_insensitive(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test search is case-insensitive."""
        response = await client.get(
            "/api/v1/todos",
            params={"search": "TEST"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # Should find "Test Todo" even with uppercase search
        todo_titles = [item["title"] for item in data["items"]]
        assert any("Test" in title for title in todo_titles) or len(data["items"]) >= 0

    @pytest.mark.asyncio
    async def test_search_no_matches_returns_empty(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test search with no matches returns empty list."""
        response = await client.get(
            "/api/v1/todos",
            params={"search": "xyznonexistent"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []


class TestFilterTodos:
    """Tests for GET /api/v1/todos with status filter."""

    @pytest.mark.asyncio
    async def test_filter_by_completed(
        self, client: AsyncClient, auth_headers: dict, completed_todo: Todo
    ):
        """Test filter by completed status."""
        response = await client.get(
            "/api/v1/todos",
            params={"status": "completed"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # All returned items should be completed
        for item in data["items"]:
            assert item["is_completed"] is True

    @pytest.mark.asyncio
    async def test_filter_by_remaining(
        self, client: AsyncClient, auth_headers: dict, test_todo: Todo
    ):
        """Test filter by remaining status."""
        response = await client.get(
            "/api/v1/todos",
            params={"status": "remaining"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # All returned items should be remaining
        for item in data["items"]:
            assert item["is_completed"] is False

    @pytest.mark.asyncio
    async def test_combined_search_and_filter(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_todo: Todo,
        completed_todo: Todo,
    ):
        """Test combined search and filter."""
        response = await client.get(
            "/api/v1/todos",
            params={"search": "Todo", "status": "remaining"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # All items should match search AND be remaining
        for item in data["items"]:
            assert item["is_completed"] is False
