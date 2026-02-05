"""Test fixtures and configuration."""

import os
from datetime import datetime, timedelta
from typing import AsyncGenerator
from uuid import uuid4

import jwt
import pytest
from httpx import AsyncClient, ASGITransport

# Set test environment variables before importing app
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-jwt-validation-min-32-chars"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

from app.main import app
from app.config import get_settings

settings = get_settings()


@pytest.fixture
def test_user_id() -> str:
    """Generate a test user ID."""
    return str(uuid4())


@pytest.fixture
def valid_token(test_user_id: str) -> str:
    """Generate a valid JWT token for testing."""
    payload = {
        "sub": test_user_id,
        "email": "test@example.com",
        "name": "Test User",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")


@pytest.fixture
def expired_token(test_user_id: str) -> str:
    """Generate an expired JWT token for testing."""
    payload = {
        "sub": test_user_id,
        "email": "test@example.com",
        "name": "Test User",
        "iat": datetime.utcnow() - timedelta(hours=2),
        "exp": datetime.utcnow() - timedelta(hours=1),
    }
    return jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")


@pytest.fixture
def malformed_token() -> str:
    """Generate a malformed token for testing."""
    return "not.a.valid.jwt.token"


@pytest.fixture
def invalid_signature_token(test_user_id: str) -> str:
    """Generate a token with invalid signature."""
    payload = {
        "sub": test_user_id,
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, "wrong-secret-key", algorithm="HS256")


@pytest.fixture
def auth_headers(valid_token: str) -> dict:
    """Generate authorization headers with valid token."""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
