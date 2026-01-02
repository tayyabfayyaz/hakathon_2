"""Health check endpoint tests."""

import pytest
from httpx import AsyncClient


class TestHealthCheck:
    """Test GET /health endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_returns_200(self, async_client: AsyncClient):
        """Test health check returns 200 OK."""
        response = await async_client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_check_response_structure(self, async_client: AsyncClient):
        """Test health check response has correct structure."""
        response = await async_client.get("/health")
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_check_no_auth_required(self, async_client: AsyncClient):
        """Test health check doesn't require authentication."""
        response = await async_client.get("/health")
        # Should not return 401
        assert response.status_code != 401

    @pytest.mark.asyncio
    async def test_health_check_status_values(self, async_client: AsyncClient):
        """Test health check returns valid status values."""
        response = await async_client.get("/health")
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert data["database"] in ["connected", "disconnected"]
