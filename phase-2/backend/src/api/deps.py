from typing import Annotated, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security import decode_access_token
from src.models.user import User
from src.services.user_service import get_user_by_id


async def get_db() -> AsyncSession:
    """Database session dependency."""
    async for session in get_session():
        yield session


async def get_current_user(
    access_token: Annotated[Optional[str], Cookie()] = None,
    session: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT cookie."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error_code": "UNAUTHORIZED",
            "message": "Not authenticated",
        },
    )

    if not access_token:
        raise credentials_exception

    payload = decode_access_token(access_token)
    if payload is None:
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = await get_user_by_id(session, user_id)
    if user is None:
        raise credentials_exception

    return user


# Type aliases for cleaner dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
