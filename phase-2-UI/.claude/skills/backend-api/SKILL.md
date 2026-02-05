---
name: backend-api
description: Create FastAPI endpoints with proper validation, authentication, and error handling. Use when building REST APIs, adding routes, or handling HTTP requests.
argument-hint: "[endpoint-name]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# FastAPI Endpoint Creation

Create API endpoints following the TodoList Pro patterns.

## Route Template

```python
# app/api/routes/{resource}.py
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from typing import Annotated

from app.api.deps import CurrentUserDep, SessionDep
from app.models.{resource} import {Resource}
from app.schemas.{resource} import {Resource}Create, {Resource}Response, {Resource}Update

router = APIRouter(prefix="/{resources}", tags=["{resources}"])


@router.get("", response_model=list[{Resource}Response])
async def list_{resources}(
    current_user: CurrentUserDep,
    session: SessionDep,
) -> list[{Resource}Response]:
    """List all {resources} for the current user."""
    result = await session.exec(
        select({Resource})
        .where({Resource}.user_id == current_user.id)
        .order_by({Resource}.created_at.desc())
    )
    return result.all()


@router.get("/{{{resource}_id}}", response_model={Resource}Response)
async def get_{resource}(
    {resource}_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> {Resource}Response:
    """Get a specific {resource} by ID."""
    {resource} = await session.get({Resource}, {resource}_id)

    if not {resource}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Resource} not found"
        )

    if {resource}.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return {resource}


@router.post("", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_{resource}(
    data: {Resource}Create,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> {Resource}Response:
    """Create a new {resource}."""
    {resource} = {Resource}(
        user_id=current_user.id,
        **data.model_dump()
    )
    session.add({resource})
    await session.commit()
    await session.refresh({resource})
    return {resource}


@router.put("/{{{resource}_id}}", response_model={Resource}Response)
async def update_{resource}(
    {resource}_id: UUID,
    data: {Resource}Update,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> {Resource}Response:
    """Update a {resource}."""
    {resource} = await session.get({Resource}, {resource}_id)

    if not {resource}:
        raise HTTPException(status_code=404, detail="{Resource} not found")

    if {resource}.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr({resource}, key, value)

    {resource}.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh({resource})
    return {resource}


@router.delete("/{{{resource}_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{resource}(
    {resource}_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> None:
    """Delete a {resource}."""
    {resource} = await session.get({Resource}, {resource}_id)

    if not {resource}:
        raise HTTPException(status_code=404, detail="{Resource} not found")

    if {resource}.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    await session.delete({resource})
    await session.commit()
```

## Register Router

```python
# app/main.py
from app.api.routes.{resource} import router as {resource}_router

app.include_router({resource}_router)
```

## Dependency Injection

```python
# app/api/deps.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
import jwt

from app.config import get_settings
from app.database import get_session

security = HTTPBearer(auto_error=False)
settings = get_settings()


class CurrentUser:
    def __init__(self, id: str, email: str, name: str):
        self.id = id
        self.email = email
        self.name = name


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )
        return CurrentUser(
            id=payload["sub"],
            email=payload.get("email", ""),
            name=payload.get("name", "")
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# Type aliases for dependency injection
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
```

## Response Schemas

```python
# app/schemas/{resource}.py
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class {Resource}Base(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class {Resource}Create({Resource}Base):
    pass


class {Resource}Update(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class {Resource}Response({Resource}Base):
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

## Error Handling

```python
# Standard HTTP exceptions
from fastapi import HTTPException, status

# 400 Bad Request
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid input data"
)

# 401 Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required"
)

# 403 Forbidden
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Access denied"
)

# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)

# 422 Validation Error (automatic from Pydantic)
```

## Query Parameters

```python
@router.get("")
async def list_items(
    current_user: CurrentUserDep,
    session: SessionDep,
    skip: int = 0,
    limit: int = Query(default=50, le=100),
    include_completed: bool = True,
    search: str | None = None,
) -> list[ItemResponse]:
    query = select(Item).where(Item.user_id == current_user.id)

    if not include_completed:
        query = query.where(Item.completed == False)

    if search:
        query = query.where(Item.title.ilike(f"%{search}%"))

    query = query.offset(skip).limit(limit)
    result = await session.exec(query)
    return result.all()
```

## File Locations

- Routes: `backend/app/api/routes/`
- Dependencies: `backend/app/api/deps.py`
- Schemas: `backend/app/schemas/`
- Models: `backend/app/models/`
