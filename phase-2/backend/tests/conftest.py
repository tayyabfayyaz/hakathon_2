"""Test fixtures for backend API tests."""
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from main import app
from src.api.deps import get_db
from src.core.security import create_access_token, hash_password
from src.models.user import User
from src.models.todo import Todo


# Use SQLite for testing (in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_factory = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override."""

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(async_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash=hash_password("password123"),
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def another_user(async_session: AsyncSession) -> User:
    """Create another test user for ownership tests."""
    user = User(
        id=uuid4(),
        email="another@example.com",
        password_hash=hash_password("password456"),
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    """Create an auth token for the test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest_asyncio.fixture
async def auth_headers(auth_token: str) -> dict:
    """Create auth headers for authenticated requests."""
    return {"Cookie": f"access_token={auth_token}"}


@pytest_asyncio.fixture
async def test_todo(async_session: AsyncSession, test_user: User) -> Todo:
    """Create a test todo item."""
    todo = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="Test Todo",
        description="Test description",
        is_completed=False,
    )
    async_session.add(todo)
    await async_session.commit()
    await async_session.refresh(todo)
    return todo


@pytest_asyncio.fixture
async def completed_todo(async_session: AsyncSession, test_user: User) -> Todo:
    """Create a completed test todo item."""
    todo = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="Completed Todo",
        description="A completed task",
        is_completed=True,
    )
    async_session.add(todo)
    await async_session.commit()
    await async_session.refresh(todo)
    return todo


@pytest_asyncio.fixture
async def another_users_todo(async_session: AsyncSession, another_user: User) -> Todo:
    """Create a todo owned by another user for ownership tests."""
    todo = Todo(
        id=uuid4(),
        user_id=another_user.id,
        title="Another User's Todo",
        description="Should not be accessible",
        is_completed=False,
    )
    async_session.add(todo)
    await async_session.commit()
    await async_session.refresh(todo)
    return todo
