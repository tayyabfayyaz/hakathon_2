"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient

from src.models.user import User


class TestRegister:
    """Tests for POST /api/v1/auth/register."""

    @pytest.mark.asyncio
    async def test_register_with_valid_data(self, client: AsyncClient):
        """Test successful registration with valid email and password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "validpassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Registration successful"
        assert data["user"]["email"] == "newuser@example.com"
        assert "id" in data["user"]
        # Check that auth cookie is set
        assert "access_token" in response.cookies

    @pytest.mark.asyncio
    async def test_register_with_invalid_email(self, client: AsyncClient):
        """Test registration fails with invalid email format."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "validpassword123",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_register_with_short_password(self, client: AsyncClient):
        """Test registration fails with password less than 8 characters."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "short",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_register_with_duplicate_email(
        self, client: AsyncClient, test_user: User
    ):
        """Test registration fails with already registered email (409 conflict)."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "validpassword123",
            },
        )
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error_code"] == "EMAIL_EXISTS"
        assert "already registered" in data["detail"]["message"].lower()


class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    @pytest.mark.asyncio
    async def test_login_with_correct_credentials(
        self, client: AsyncClient, test_user: User
    ):
        """Test successful login with correct email and password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "password123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["user"]["email"] == test_user.email
        # Check that auth cookie is set
        assert "access_token" in response.cookies

    @pytest.mark.asyncio
    async def test_login_with_wrong_password(
        self, client: AsyncClient, test_user: User
    ):
        """Test login fails with incorrect password (401)."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error_code"] == "INVALID_CREDENTIALS"
        assert "invalid email or password" in data["detail"]["message"].lower()

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email(self, client: AsyncClient):
        """Test login fails with non-existent email (401)."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword",
            },
        )
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error_code"] == "INVALID_CREDENTIALS"


class TestLogout:
    """Tests for POST /api/v1/auth/logout."""

    @pytest.mark.asyncio
    async def test_logout_clears_cookie(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test logout clears the auth cookie."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"


class TestGetMe:
    """Tests for GET /api/v1/auth/me."""

    @pytest.mark.asyncio
    async def test_get_me_authenticated(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test getting current user info with valid auth."""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert str(data["id"]) == str(test_user.id)

    @pytest.mark.asyncio
    async def test_get_me_without_auth(self, client: AsyncClient):
        """Test /auth/me without auth token returns 401."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error_code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_get_me_with_invalid_token(self, client: AsyncClient):
        """Test /auth/me with invalid token returns 401."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Cookie": "access_token=invalid_token_here"},
        )
        assert response.status_code == 401
