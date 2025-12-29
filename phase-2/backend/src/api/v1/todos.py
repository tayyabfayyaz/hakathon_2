from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query

from src.api.deps import DbSession, CurrentUser
from src.models.todo import TodoCreate, TodoUpdate, TodoRead, TodoListResponse
from src.services.todo_service import (
    create_todo,
    get_todo_by_id,
    list_todos,
    update_todo,
    soft_delete_todo,
    toggle_todo_status,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_new_todo(
    todo_data: TodoCreate,
    session: DbSession,
    current_user: CurrentUser,
):
    """Create a new todo item."""
    todo = await create_todo(session, current_user.id, todo_data)
    return TodoRead.model_validate(todo)


@router.get("", response_model=TodoListResponse)
async def get_todos(
    session: DbSession,
    current_user: CurrentUser,
    search: Optional[str] = Query(None, max_length=100),
    status: Optional[str] = Query(None, regex="^(all|completed|remaining)$"),
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """List all todos for the current user with optional search and filter."""
    # Parse cursor if provided
    cursor_dt = None
    if cursor:
        try:
            cursor_dt = datetime.fromisoformat(cursor)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_CURSOR",
                    "message": "Invalid cursor format",
                },
            )

    # Get filtered status (treat "all" as None)
    filter_status = status if status and status != "all" else None

    todos, total_count, next_cursor = await list_todos(
        session,
        current_user.id,
        search=search,
        status=filter_status,
        cursor=cursor_dt,
        limit=limit,
    )

    return TodoListResponse(
        items=[TodoRead.model_validate(t) for t in todos],
        next_cursor=next_cursor,
        total_count=total_count,
    )


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: UUID,
    session: DbSession,
    current_user: CurrentUser,
):
    """Get a specific todo by ID."""
    todo = await get_todo_by_id(session, todo_id, current_user.id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "NOT_FOUND",
                "message": "Todo not found",
            },
        )
    return TodoRead.model_validate(todo)


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_existing_todo(
    todo_id: UUID,
    update_data: TodoUpdate,
    session: DbSession,
    current_user: CurrentUser,
):
    """Update an existing todo."""
    todo = await get_todo_by_id(session, todo_id, current_user.id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "NOT_FOUND",
                "message": "Todo not found",
            },
        )

    updated_todo = await update_todo(session, todo, update_data)
    return TodoRead.model_validate(updated_todo)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: UUID,
    session: DbSession,
    current_user: CurrentUser,
):
    """Delete a todo (soft delete)."""
    todo = await get_todo_by_id(session, todo_id, current_user.id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "NOT_FOUND",
                "message": "Todo not found",
            },
        )

    await soft_delete_todo(session, todo)
    return None


@router.post("/{todo_id}/toggle", response_model=TodoRead)
async def toggle_todo(
    todo_id: UUID,
    session: DbSession,
    current_user: CurrentUser,
):
    """Toggle the completion status of a todo."""
    todo = await get_todo_by_id(session, todo_id, current_user.id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "NOT_FOUND",
                "message": "Todo not found",
            },
        )

    toggled_todo = await toggle_todo_status(session, todo)
    return TodoRead.model_validate(toggled_todo)
