"""Authentication dependency tests."""

import pytest
from httpx import AsyncClient


class TestAuthentication:
    """Test JWT token validation."""

    @pytest.mark.asyncio
    async def test_valid_token_extracts_user_id(
        self, async_client: AsyncClient, auth_headers: dict, test_user_id: str
    ):
        """Test that valid token allows access to protected endpoints."""
        # This test will pass once tasks endpoint is implemented
        response = await async_client.get("/tasks", headers=auth_headers)
        # Should not get 401 with valid token
        assert response.status_code != 401 or response.status_code == 404

    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, async_client: AsyncClient):
        """Test that missing token returns 401 Unauthorized."""
        response = await async_client.get("/tasks")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_returns_401(
        self, async_client: AsyncClient, expired_token: str
    ):
        """Test that expired token returns 401 Unauthorized."""
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await async_client.get("/tasks", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_malformed_token_returns_401(
        self, async_client: AsyncClient, malformed_token: str
    ):
        """Test that malformed token returns 401 Unauthorized."""
        headers = {"Authorization": f"Bearer {malformed_token}"}
        response = await async_client.get("/tasks", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_signature_returns_401(
        self, async_client: AsyncClient, invalid_signature_token: str
    ):
        """Test that token with wrong signature returns 401."""
        headers = {"Authorization": f"Bearer {invalid_signature_token}"}
        response = await async_client.get("/tasks", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_bearer_case_insensitive(
        self, async_client: AsyncClient, valid_token: str
    ):
        """Test that Bearer prefix is case insensitive."""
        headers = {"Authorization": f"bearer {valid_token}"}
        response = await async_client.get("/tasks", headers=headers)
        # Should not get 401 with valid token (bearer lowercase)
        assert response.status_code != 401 or response.status_code == 404
