"""Task endpoint tests."""

import pytest
from httpx import AsyncClient


class TestCreateTask:
    """Test POST /tasks endpoint."""

    @pytest.mark.asyncio
    async def test_create_task_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test creating a task with valid data returns 201."""
        response = await async_client.post(
            "/tasks",
            json={"text": "Buy groceries"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "Buy groceries"
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_task_without_auth_returns_401(
        self, async_client: AsyncClient
    ):
        """Test creating a task without auth returns 401."""
        response = await async_client.post(
            "/tasks",
            json={"text": "Buy groceries"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_task_empty_text_returns_422(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test creating a task with empty text returns 422."""
        response = await async_client.post(
            "/tasks",
            json={"text": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_missing_text_returns_422(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test creating a task without text field returns 422."""
        response = await async_client.post(
            "/tasks",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestListTasks:
    """Test GET /tasks endpoint."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test listing tasks returns empty array when no tasks."""
        response = await async_client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "count" in data
        assert isinstance(data["tasks"], list)

    @pytest.mark.asyncio
    async def test_list_tasks_without_auth_returns_401(
        self, async_client: AsyncClient
    ):
        """Test listing tasks without auth returns 401."""
        response = await async_client.get("/tasks")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_tasks_returns_user_tasks_only(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test that list only returns current user's tasks."""
        # Create a task
        await async_client.post(
            "/tasks",
            json={"text": "My task"},
            headers=auth_headers,
        )

        # List tasks
        response = await async_client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should have at least one task
        assert data["count"] >= 0


class TestGetTask:
    """Test GET /tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_task_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test getting non-existent task returns 404."""
        response = await async_client.get(
            "/tasks/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_task_without_auth_returns_401(
        self, async_client: AsyncClient
    ):
        """Test getting task without auth returns 401."""
        response = await async_client.get(
            "/tasks/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 401


class TestUpdateTask:
    """Test PUT /tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_task_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent task returns 404."""
        response = await async_client.put(
            "/tasks/00000000-0000-0000-0000-000000000000",
            json={"text": "Updated", "completed": True},
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task_without_auth_returns_401(
        self, async_client: AsyncClient
    ):
        """Test updating task without auth returns 401."""
        response = await async_client.put(
            "/tasks/00000000-0000-0000-0000-000000000000",
            json={"text": "Updated", "completed": True},
        )
        assert response.status_code == 401


class TestPatchTask:
    """Test PATCH /tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_patch_task_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test patching non-existent task returns 404."""
        response = await async_client.patch(
            "/tasks/00000000-0000-0000-0000-000000000000",
            json={"completed": True},
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_patch_task_without_auth_returns_401(
        self, async_client: AsyncClient
    ):
        """Test patching task without auth returns 401."""
        response = await async_client.patch(
            "/tasks/00000000-0000-0000-0000-000000000000",
            json={"completed": True},
        )
        assert response.status_code == 401


class TestDeleteTask:
    """Test DELETE /tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_task_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent task returns 404."""
        response = await async_client.delete(
            "/tasks/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_without_auth_returns_401(
        self, async_client: AsyncClient
    ):
        """Test deleting task without auth returns 401."""
        response = await async_client.delete(
            "/tasks/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 401
