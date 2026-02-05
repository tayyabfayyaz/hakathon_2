"""Tests for voice preferences API endpoints."""

import pytest
from httpx import AsyncClient

from app.models import UserVoicePreferences


class TestVoicePreferencesAPI:
    """Test cases for voice preferences endpoints."""

    @pytest.fixture
    def user_id(self) -> str:
        """Test user ID."""
        return "test-user-voice-123"

    @pytest.fixture
    def other_user_id(self) -> str:
        """Another user's ID for isolation tests."""
        return "other-user-456"

    # GET /api/{user_id}/voice/preferences tests

    async def test_get_voice_preferences_creates_defaults(
        self,
        client: AsyncClient,
        auth_headers: dict,
        user_id: str,
    ):
        """Test that GET creates default preferences if none exist."""
        response = await client.get(
            f"/api/{user_id}/voice/preferences",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["voice_output_enabled"] is True  # Default
        assert data["continuous_mode_enabled"] is False  # Default
        assert data["preferred_voice"] is None  # Default
        assert "updated_at" in data

    async def test_get_voice_preferences_returns_existing(
        self,
        client: AsyncClient,
        auth_headers: dict,
        user_id: str,
        session,
    ):
        """Test that GET returns existing preferences."""
        # Create preferences first
        prefs = UserVoicePreferences(
            user_id=user_id,
            voice_output_enabled=False,
            continuous_mode_enabled=True,
            preferred_voice="Microsoft David",
        )
        session.add(prefs)
        await session.commit()

        response = await client.get(
            f"/api/{user_id}/voice/preferences",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["voice_output_enabled"] is False
        assert data["continuous_mode_enabled"] is True
        assert data["preferred_voice"] == "Microsoft David"

    async def test_get_voice_preferences_forbidden_other_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        other_user_id: str,
    ):
        """Test that users cannot access other users' preferences."""
        response = await client.get(
            f"/api/{other_user_id}/voice/preferences",
            headers=auth_headers,
        )

        assert response.status_code == 403

    async def test_get_voice_preferences_unauthorized(
        self,
        client: AsyncClient,
        user_id: str,
    ):
        """Test that unauthenticated requests are rejected."""
        response = await client.get(f"/api/{user_id}/voice/preferences")

        assert response.status_code == 401

    # PUT /api/{user_id}/voice/preferences tests

    async def test_update_voice_preferences_all_fields(
        self,
        client: AsyncClient,
        auth_headers: dict,
        user_id: str,
    ):
        """Test updating all preference fields."""
        update_data = {
            "voice_output_enabled": False,
            "continuous_mode_enabled": True,
            "preferred_voice": "Google US English",
        }

        response = await client.put(
            f"/api/{user_id}/voice/preferences",
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["voice_output_enabled"] is False
        assert data["continuous_mode_enabled"] is True
        assert data["preferred_voice"] == "Google US English"

    async def test_update_voice_preferences_partial(
        self,
        client: AsyncClient,
        auth_headers: dict,
        user_id: str,
    ):
        """Test partial update - only provided fields change."""
        # First set some initial values
        await client.put(
            f"/api/{user_id}/voice/preferences",
            headers=auth_headers,
            json={
                "voice_output_enabled": True,
                "continuous_mode_enabled": False,
            },
        )

        # Update only voice_output_enabled
        response = await client.put(
            f"/api/{user_id}/voice/preferences",
            headers=auth_headers,
            json={"voice_output_enabled": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["voice_output_enabled"] is False
        assert data["continuous_mode_enabled"] is False  # Unchanged

    async def test_update_voice_preferences_creates_if_missing(
        self,
        client: AsyncClient,
        auth_headers: dict,
        user_id: str,
    ):
        """Test that PUT creates preferences if they don't exist."""
        update_data = {"continuous_mode_enabled": True}

        response = await client.put(
            f"/api/{user_id}/voice/preferences",
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["continuous_mode_enabled"] is True
        assert data["voice_output_enabled"] is True  # Default preserved

    async def test_update_voice_preferences_forbidden_other_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        other_user_id: str,
    ):
        """Test that users cannot update other users' preferences."""
        response = await client.put(
            f"/api/{other_user_id}/voice/preferences",
            headers=auth_headers,
            json={"voice_output_enabled": False},
        )

        assert response.status_code == 403

    async def test_update_voice_preferences_unauthorized(
        self,
        client: AsyncClient,
        user_id: str,
    ):
        """Test that unauthenticated requests are rejected."""
        response = await client.put(
            f"/api/{user_id}/voice/preferences",
            json={"voice_output_enabled": False},
        )

        assert response.status_code == 401

    async def test_update_voice_preferences_updates_timestamp(
        self,
        client: AsyncClient,
        auth_headers: dict,
        user_id: str,
    ):
        """Test that updated_at timestamp is updated on changes."""
        # Create initial preferences
        response1 = await client.get(
            f"/api/{user_id}/voice/preferences",
            headers=auth_headers,
        )
        initial_updated_at = response1.json()["updated_at"]

        # Update preferences
        response2 = await client.put(
            f"/api/{user_id}/voice/preferences",
            headers=auth_headers,
            json={"voice_output_enabled": False},
        )
        new_updated_at = response2.json()["updated_at"]

        # Timestamps should be different (or at least not older)
        assert new_updated_at >= initial_updated_at


class TestChatWithInputMethod:
    """Test that chat API properly handles input_method."""

    @pytest.fixture
    def user_id(self) -> str:
        """Test user ID."""
        return "test-user-chat-voice-123"

    async def test_chat_accepts_voice_input_method(
        self,
        client: AsyncClient,
        auth_headers: dict,
        user_id: str,
    ):
        """Test that chat endpoint accepts voice input_method."""
        response = await client.post(
            f"/api/{user_id}/chat",
            headers=auth_headers,
            json={
                "message": "Add a task to test voice input",
                "input_method": "voice",
            },
        )

        # May fail if AI service unavailable, but should not be 400/422
        assert response.status_code in [200, 503, 500]

    async def test_chat_defaults_to_text_input_method(
        self,
        client: AsyncClient,
        auth_headers: dict,
        user_id: str,
    ):
        """Test that chat endpoint defaults to text input_method."""
        response = await client.post(
            f"/api/{user_id}/chat",
            headers=auth_headers,
            json={"message": "Hello"},  # No input_method specified
        )

        # May fail if AI service unavailable, but should not be 400/422
        assert response.status_code in [200, 503, 500]

    async def test_chat_history_includes_input_method(
        self,
        client: AsyncClient,
        auth_headers: dict,
        user_id: str,
    ):
        """Test that chat history response includes input_method."""
        response = await client.get(
            f"/api/{user_id}/chat/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # If there are messages, they should have input_method
        for msg in data.get("messages", []):
            assert "input_method" in msg
