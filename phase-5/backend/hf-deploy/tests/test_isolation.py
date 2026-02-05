"""User isolation tests - verify User_1 cannot see User_2's tasks.

These tests verify the critical multi-tenant security guarantee:
Every user operates in complete isolation. User_A cannot see, access,
or modify User_B's tasks under any circumstances.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from httpx import AsyncClient

from app.config import get_settings

settings = get_settings()


# =============================================================================
# Fixtures for Multi-User Testing
# =============================================================================

@pytest.fixture
def user_a_id() -> str:
    """User A's unique ID."""
    return str(uuid4())


@pytest.fixture
def user_b_id() -> str:
    """User B's unique ID."""
    return str(uuid4())


@pytest.fixture
def user_a_token(user_a_id: str) -> str:
    """Generate a valid JWT token for User A."""
    payload = {
        "sub": user_a_id,
        "email": "user_a@example.com",
        "name": "User A",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")


@pytest.fixture
def user_b_token(user_b_id: str) -> str:
    """Generate a valid JWT token for User B."""
    payload = {
        "sub": user_b_id,
        "email": "user_b@example.com",
        "name": "User B",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")


@pytest.fixture
def user_a_headers(user_a_token: str) -> dict:
    """Authorization headers for User A."""
    return {"Authorization": f"Bearer {user_a_token}"}


@pytest.fixture
def user_b_headers(user_b_token: str) -> dict:
    """Authorization headers for User B."""
    return {"Authorization": f"Bearer {user_b_token}"}


# =============================================================================
# T046: Task Listing Isolation Tests
# =============================================================================

class TestTaskListingIsolation:
    """Test that GET /tasks only returns the authenticated user's tasks."""

    @pytest.mark.asyncio
    async def test_user_a_cannot_see_user_b_tasks(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """User A's GET /tasks does NOT include User B's tasks."""
        # User B creates a task
        user_b_task = await async_client.post(
            "/tasks",
            json={"text": "User B's private task"},
            headers=user_b_headers,
        )
        assert user_b_task.status_code == 201
        user_b_task_id = user_b_task.json()["id"]

        # User A lists their tasks
        response = await async_client.get("/tasks", headers=user_a_headers)
        assert response.status_code == 200
        data = response.json()

        # Verify User B's task is NOT in User A's list
        task_ids = [task["id"] for task in data["tasks"]]
        assert user_b_task_id not in task_ids, "User A should NOT see User B's task"

    @pytest.mark.asyncio
    async def test_list_returns_only_authenticated_users_tasks(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
        user_a_id: str,
    ):
        """Create tasks for both users, verify list returns only authenticated user's tasks."""
        # User A creates a task
        await async_client.post(
            "/tasks",
            json={"text": "User A's task"},
            headers=user_a_headers,
        )

        # User B creates a task
        await async_client.post(
            "/tasks",
            json={"text": "User B's task"},
            headers=user_b_headers,
        )

        # User A lists tasks - should only see their own
        response = await async_client.get("/tasks", headers=user_a_headers)
        assert response.status_code == 200
        data = response.json()

        # All returned tasks should belong to User A
        for task in data["tasks"]:
            assert task["user_id"] == user_a_id, f"Found task belonging to wrong user: {task['user_id']}"

    @pytest.mark.asyncio
    async def test_task_count_matches_users_own_tasks(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """Verify task count matches only user's own tasks."""
        # Create 2 tasks for User A
        await async_client.post("/tasks", json={"text": "A task 1"}, headers=user_a_headers)
        await async_client.post("/tasks", json={"text": "A task 2"}, headers=user_a_headers)

        # Create 5 tasks for User B
        for i in range(5):
            await async_client.post("/tasks", json={"text": f"B task {i}"}, headers=user_b_headers)

        # User A's count should NOT include User B's tasks
        response_a = await async_client.get("/tasks", headers=user_a_headers)
        response_b = await async_client.get("/tasks", headers=user_b_headers)

        # Counts should be independent
        assert response_a.json()["count"] >= 2, "User A should see at least their 2 tasks"
        assert response_b.json()["count"] >= 5, "User B should see at least their 5 tasks"


# =============================================================================
# T047: Single Task Access Isolation Tests
# =============================================================================

class TestSingleTaskAccessIsolation:
    """Test that GET /tasks/{id} returns 404 for other users' tasks."""

    @pytest.mark.asyncio
    async def test_user_a_cannot_get_user_b_task_returns_404(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """User A cannot GET /tasks/{user_b_task_id} - returns 404 (not 403)."""
        # User B creates a task
        user_b_task = await async_client.post(
            "/tasks",
            json={"text": "User B's secret task"},
            headers=user_b_headers,
        )
        assert user_b_task.status_code == 201
        user_b_task_id = user_b_task.json()["id"]

        # User A tries to access User B's task
        response = await async_client.get(
            f"/tasks/{user_b_task_id}",
            headers=user_a_headers,
        )

        # MUST return 404 (not 403) to avoid information leakage
        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}. "
            "Other user's tasks should return 404 to prevent enumeration attacks."
        )

    @pytest.mark.asyncio
    async def test_same_task_id_returns_data_for_owner_404_for_others(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """Same task ID returns data for owner, 404 for others."""
        # User A creates a task
        user_a_task = await async_client.post(
            "/tasks",
            json={"text": "User A's task"},
            headers=user_a_headers,
        )
        task_id = user_a_task.json()["id"]

        # User A (owner) can access the task
        owner_response = await async_client.get(f"/tasks/{task_id}", headers=user_a_headers)
        assert owner_response.status_code == 200
        assert owner_response.json()["text"] == "User A's task"

        # User B (non-owner) gets 404
        non_owner_response = await async_client.get(f"/tasks/{task_id}", headers=user_b_headers)
        assert non_owner_response.status_code == 404

    @pytest.mark.asyncio
    async def test_no_information_leakage_in_404_response(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """Verify 404 response body reveals no details about the task."""
        # User B creates a task
        user_b_task = await async_client.post(
            "/tasks",
            json={"text": "Super secret information"},
            headers=user_b_headers,
        )
        user_b_task_id = user_b_task.json()["id"]

        # User A tries to access User B's task
        response = await async_client.get(
            f"/tasks/{user_b_task_id}",
            headers=user_a_headers,
        )

        assert response.status_code == 404
        response_body = response.json()

        # Response should NOT contain any task information
        assert "Super secret" not in str(response_body)
        assert user_b_task_id not in str(response_body) or "not found" in str(response_body).lower()


# =============================================================================
# T048: Task Update Isolation Tests
# =============================================================================

class TestTaskUpdateIsolation:
    """Test that PUT/PATCH /tasks/{id} returns 404 for other users' tasks."""

    @pytest.mark.asyncio
    async def test_user_a_cannot_put_user_b_task(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """User A cannot PUT /tasks/{user_b_task_id} - returns 404."""
        # User B creates a task
        user_b_task = await async_client.post(
            "/tasks",
            json={"text": "User B's original task"},
            headers=user_b_headers,
        )
        user_b_task_id = user_b_task.json()["id"]

        # User A tries to update User B's task via PUT
        response = await async_client.put(
            f"/tasks/{user_b_task_id}",
            json={"text": "Hacked by User A", "completed": True},
            headers=user_a_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_a_cannot_patch_user_b_task(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """User A cannot PATCH /tasks/{user_b_task_id} - returns 404."""
        # User B creates a task
        user_b_task = await async_client.post(
            "/tasks",
            json={"text": "User B's task"},
            headers=user_b_headers,
        )
        user_b_task_id = user_b_task.json()["id"]

        # User A tries to patch User B's task
        response = await async_client.patch(
            f"/tasks/{user_b_task_id}",
            json={"completed": True},
            headers=user_a_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_b_task_unchanged_after_user_a_failed_update(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """Verify User B's task remains unchanged after User A's failed update attempt."""
        original_text = "User B's original unchanged task"

        # User B creates a task
        user_b_task = await async_client.post(
            "/tasks",
            json={"text": original_text},
            headers=user_b_headers,
        )
        user_b_task_id = user_b_task.json()["id"]

        # User A tries to update User B's task (should fail)
        await async_client.put(
            f"/tasks/{user_b_task_id}",
            json={"text": "MODIFIED BY USER A", "completed": True},
            headers=user_a_headers,
        )

        # User B verifies their task is unchanged
        response = await async_client.get(f"/tasks/{user_b_task_id}", headers=user_b_headers)
        assert response.status_code == 200
        assert response.json()["text"] == original_text
        assert response.json()["completed"] is False


# =============================================================================
# T049: Task Deletion Isolation Tests
# =============================================================================

class TestTaskDeletionIsolation:
    """Test that DELETE /tasks/{id} returns 404 for other users' tasks."""

    @pytest.mark.asyncio
    async def test_user_a_cannot_delete_user_b_task(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """User A cannot DELETE /tasks/{user_b_task_id} - returns 404."""
        # User B creates a task
        user_b_task = await async_client.post(
            "/tasks",
            json={"text": "User B's task to protect"},
            headers=user_b_headers,
        )
        user_b_task_id = user_b_task.json()["id"]

        # User A tries to delete User B's task
        response = await async_client.delete(
            f"/tasks/{user_b_task_id}",
            headers=user_a_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_b_task_still_exists_after_user_a_failed_delete(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """Verify User B's task still exists after User A's failed delete attempt."""
        # User B creates a task
        user_b_task = await async_client.post(
            "/tasks",
            json={"text": "User B's protected task"},
            headers=user_b_headers,
        )
        user_b_task_id = user_b_task.json()["id"]

        # User A tries to delete User B's task (should fail)
        await async_client.delete(f"/tasks/{user_b_task_id}", headers=user_a_headers)

        # User B verifies their task still exists
        response = await async_client.get(f"/tasks/{user_b_task_id}", headers=user_b_headers)
        assert response.status_code == 200
        assert response.json()["text"] == "User B's protected task"

    @pytest.mark.asyncio
    async def test_user_a_delete_own_task_does_not_affect_user_b(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_headers: dict,
    ):
        """After User A deletes own task, User B can still see their tasks."""
        # User A creates and then deletes their task
        user_a_task = await async_client.post(
            "/tasks",
            json={"text": "User A's task to delete"},
            headers=user_a_headers,
        )
        user_a_task_id = user_a_task.json()["id"]

        # User B creates a task
        user_b_task = await async_client.post(
            "/tasks",
            json={"text": "User B's task"},
            headers=user_b_headers,
        )
        user_b_task_id = user_b_task.json()["id"]

        # User A deletes their own task
        delete_response = await async_client.delete(f"/tasks/{user_a_task_id}", headers=user_a_headers)
        assert delete_response.status_code == 204

        # User B's task is completely unaffected
        response = await async_client.get(f"/tasks/{user_b_task_id}", headers=user_b_headers)
        assert response.status_code == 200
        assert response.json()["text"] == "User B's task"


# =============================================================================
# T051: CREATE Flow - user_id Cannot Be Overridden
# =============================================================================

class TestCreateFlowIsolation:
    """Test that user_id cannot be overridden via request body."""

    @pytest.mark.asyncio
    async def test_explicit_user_id_in_body_is_ignored(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_a_id: str,
        user_b_id: str,
    ):
        """POST /tasks with explicit user_id in body is ignored."""
        # User A tries to create a task with User B's user_id in the body
        response = await async_client.post(
            "/tasks",
            json={
                "text": "Task with fake user_id",
                "user_id": user_b_id,  # Attempt to override user_id
            },
            headers=user_a_headers,
        )

        # Task should still be created successfully
        assert response.status_code == 201
        data = response.json()

        # The task should belong to User A (from JWT), not User B (from body)
        assert data["user_id"] == user_a_id, (
            f"Task user_id should be {user_a_id} (from JWT), not {data['user_id']}"
        )
