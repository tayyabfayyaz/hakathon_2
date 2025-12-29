from typing import Annotated, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Cookie, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from src.core.database import get_session
from src.core.security import decode_access_token, hash_password
from src.models.user import User
from src.services.user_service import get_user_by_id, get_user_by_email
import secrets


async def get_db() -> AsyncSession:
    """Database session dependency."""
    async for session in get_session():
        yield session


async def validate_better_auth_session(session_token: str) -> Optional[dict]:
    """Validate a Better Auth session by calling the frontend's auth endpoint.

    Better Auth uses database sessions, not JWTs. We need to call the auth
    endpoint to validate the session and get user info.

    Args:
        session_token: The session token from the cookie

    Returns:
        User info dict with 'email' key if valid, None otherwise
    """
    try:
        async with httpx.AsyncClient() as client:
            # Call the Better Auth get-session endpoint
            response = await client.get(
                "http://localhost:3000/api/auth/get-session",
                cookies={"better-auth.session_token": session_token},
                timeout=5.0,
            )

            if response.status_code == 200:
                data = response.json()
                # Better Auth returns { session: {...}, user: {...} }
                if data and data.get("user"):
                    return {
                        "email": data["user"].get("email"),
                        "id": data["user"].get("id"),
                        "name": data["user"].get("name"),
                    }
            return None
    except Exception:
        return None


async def get_current_user(
    request: Request,
    access_token: Annotated[Optional[str], Cookie()] = None,
    better_auth_session_token: Annotated[Optional[str], Cookie(alias="better-auth.session_token")] = None,
    authorization: Annotated[Optional[str], Header()] = None,
    session: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT cookie or Better Auth session.

    Supports multiple authentication methods:
    1. Better Auth session token (cookie: better-auth.session_token) - validated via API
    2. Legacy access token (cookie: access_token) - validated via JWT decode
    3. Authorization header (Bearer token) - validated via JWT decode
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error_code": "UNAUTHORIZED",
            "message": "Not authenticated",
        },
    )

    user_info = None
    is_better_auth = False

    # Priority 1: Better Auth session token - validate via API call
    if better_auth_session_token:
        user_info = await validate_better_auth_session(better_auth_session_token)
        is_better_auth = True
        if user_info is None:
            raise credentials_exception
    # Priority 2: Authorization header (Bearer token) - legacy JWT
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        user_info = {"email": payload.get("sub"), "id": payload.get("sub")}
    # Priority 3: Legacy access token cookie - legacy JWT
    elif access_token:
        payload = decode_access_token(access_token)
        if payload is None:
            raise credentials_exception
        user_info = {"email": payload.get("sub"), "id": payload.get("sub")}
    else:
        raise credentials_exception

    if user_info is None:
        raise credentials_exception

    # Try to find user by email
    user = None
    user_email = user_info.get("email")
    user_id_str = user_info.get("id")

    # Try by email first
    if user_email:
        user = await get_user_by_email(session, user_email)

    # If not found by email, try by ID (for legacy tokens)
    if user is None and user_id_str:
        try:
            user_id = UUID(user_id_str)
            user = await get_user_by_id(session, user_id)
        except ValueError:
            pass

    # Auto-create user from Better Auth if they don't exist in backend database
    if user is None and is_better_auth and user_email and "@" in user_email:
        # The user exists in Better Auth but not in our database
        # Create them with a random password (they'll use Better Auth for login)
        user = User(
            email=user_email,
            password_hash=hash_password(secrets.token_urlsafe(32)),  # Random password
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    if user is None:
        raise credentials_exception

    return user


# Type aliases for cleaner dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
