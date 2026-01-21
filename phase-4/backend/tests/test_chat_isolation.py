"""Chat endpoint isolation tests - verify User_A cannot access User_B's chat.

These tests verify that the chat endpoints enforce user isolation:
- User_A cannot send messages to /{user_b_id}/chat
- User_A cannot access /{user_b_id}/chat/history
- user_id in URL MUST match authenticated user
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
# T056: Chat Endpoint Isolation Tests
# =============================================================================

class TestChatSendMessageIsolation:
    """Test that POST /{user_id}/chat returns 403 for user_id mismatch."""

    @pytest.mark.asyncio
    async def test_user_a_cannot_send_message_to_user_b_chat(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_id: str,
    ):
        """User A cannot access /{user_b_id}/chat - returns 403."""
        response = await async_client.post(
            f"/{user_b_id}/chat",
            json={"message": "Hello from User A trying to chat as User B"},
            headers=user_a_headers,
        )

        assert response.status_code == 403, (
            f"Expected 403 Forbidden, got {response.status_code}. "
            "User A should not be able to send messages to User B's chat endpoint."
        )

    @pytest.mark.asyncio
    async def test_user_can_send_message_to_own_chat(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_a_id: str,
    ):
        """User A can send messages to their own chat endpoint."""
        response = await async_client.post(
            f"/{user_a_id}/chat",
            json={"message": "Hello, this is my own chat"},
            headers=user_a_headers,
        )

        # Should succeed (200) or service unavailable (503) if AI is not configured
        # But definitely NOT 403
        assert response.status_code != 403, "User should be able to access their own chat"
        assert response.status_code in [200, 500, 503], f"Unexpected status: {response.status_code}"


class TestChatHistoryIsolation:
    """Test that GET /{user_id}/chat/history returns 403 for user_id mismatch."""

    @pytest.mark.asyncio
    async def test_user_a_cannot_access_user_b_history(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_id: str,
    ):
        """User A cannot access /{user_b_id}/chat/history - returns 403."""
        response = await async_client.get(
            f"/{user_b_id}/chat/history",
            headers=user_a_headers,
        )

        assert response.status_code == 403, (
            f"Expected 403 Forbidden, got {response.status_code}. "
            "User A should not be able to access User B's chat history."
        )

    @pytest.mark.asyncio
    async def test_user_can_access_own_history(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_a_id: str,
    ):
        """User A can access their own chat history."""
        response = await async_client.get(
            f"/{user_a_id}/chat/history",
            headers=user_a_headers,
        )

        # Should succeed - NOT 403
        assert response.status_code != 403, "User should be able to access their own history"
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"


class TestChatUserIdUrlValidation:
    """Test that user_id in URL MUST match authenticated user."""

    @pytest.mark.asyncio
    async def test_user_id_url_must_match_jwt_for_chat(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_a_id: str,
        user_b_id: str,
    ):
        """Verify user_id in URL MUST match authenticated user for chat."""
        # Try to access User B's chat with User A's token
        response_wrong = await async_client.post(
            f"/{user_b_id}/chat",
            json={"message": "Test"},
            headers=user_a_headers,
        )
        assert response_wrong.status_code == 403

        # Access own chat with own token - should work
        response_correct = await async_client.post(
            f"/{user_a_id}/chat",
            json={"message": "Test"},
            headers=user_a_headers,
        )
        # Should not be 403 (could be 200, 500, or 503 depending on AI service)
        assert response_correct.status_code != 403

    @pytest.mark.asyncio
    async def test_user_id_url_must_match_jwt_for_history(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_a_id: str,
        user_b_id: str,
    ):
        """Verify user_id in URL MUST match authenticated user for history."""
        # Try to access User B's history with User A's token
        response_wrong = await async_client.get(
            f"/{user_b_id}/chat/history",
            headers=user_a_headers,
        )
        assert response_wrong.status_code == 403

        # Access own history with own token - should work
        response_correct = await async_client.get(
            f"/{user_a_id}/chat/history",
            headers=user_a_headers,
        )
        assert response_correct.status_code == 200

    @pytest.mark.asyncio
    async def test_403_response_has_appropriate_message(
        self,
        async_client: AsyncClient,
        user_a_headers: dict,
        user_b_id: str,
    ):
        """Verify 403 response includes appropriate error message."""
        response = await async_client.post(
            f"/{user_b_id}/chat",
            json={"message": "Test"},
            headers=user_a_headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        # Should mention user ID mismatch
        assert "user" in data["detail"].lower() or "match" in data["detail"].lower()


class TestChatWithoutAuth:
    """Test that chat endpoints require authentication."""

    @pytest.mark.asyncio
    async def test_chat_without_auth_returns_401(
        self,
        async_client: AsyncClient,
        user_a_id: str,
    ):
        """Chat endpoint without auth returns 401."""
        response = await async_client.post(
            f"/{user_a_id}/chat",
            json={"message": "Hello"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_history_without_auth_returns_401(
        self,
        async_client: AsyncClient,
        user_a_id: str,
    ):
        """History endpoint without auth returns 401."""
        response = await async_client.get(f"/{user_a_id}/chat/history")
        assert response.status_code == 401
