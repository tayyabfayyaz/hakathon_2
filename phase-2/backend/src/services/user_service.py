from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User, UserCreate
from src.core.security import hash_password, verify_password


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email address."""
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get a user by ID."""
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user with hashed password."""
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = await get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None

    # Update last login time
    user.last_login_at = datetime.utcnow()
    session.add(user)
    await session.commit()

    return user
