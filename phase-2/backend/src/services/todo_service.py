from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID
from sqlmodel import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.todo import Todo, TodoCreate, TodoUpdate


async def create_todo(
    session: AsyncSession, user_id: UUID, todo_data: TodoCreate
) -> Todo:
    """Create a new todo for a user."""
    todo = Todo(
        user_id=user_id,
        title=todo_data.title.strip(),
        description=todo_data.description.strip() if todo_data.description else None,
    )
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


async def get_todo_by_id(
    session: AsyncSession, todo_id: UUID, user_id: UUID
) -> Optional[Todo]:
    """Get a todo by ID, ensuring it belongs to the user and is not deleted."""
    statement = select(Todo).where(
        and_(
            Todo.id == todo_id,
            Todo.user_id == user_id,
            Todo.deleted_at.is_(None),
        )
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def list_todos(
    session: AsyncSession,
    user_id: UUID,
    search: Optional[str] = None,
    status: Optional[str] = None,
    cursor: Optional[datetime] = None,
    limit: int = 20,
) -> Tuple[List[Todo], int, Optional[str]]:
    """List todos for a user with optional search, filter, and pagination."""
    # Base query - exclude deleted
    base_conditions = [
        Todo.user_id == user_id,
        Todo.deleted_at.is_(None),
    ]

    # Add search condition
    if search:
        search_term = f"%{search}%"
        base_conditions.append(
            or_(
                Todo.title.ilike(search_term),
                Todo.description.ilike(search_term),
            )
        )

    # Add status filter
    if status == "completed":
        base_conditions.append(Todo.is_completed == True)
    elif status == "remaining":
        base_conditions.append(Todo.is_completed == False)

    # Count total
    count_statement = select(func.count()).select_from(Todo).where(and_(*base_conditions))
    count_result = await session.execute(count_statement)
    total_count = count_result.scalar_one()

    # Add cursor for pagination
    if cursor:
        base_conditions.append(Todo.created_at < cursor)

    # Fetch items
    statement = (
        select(Todo)
        .where(and_(*base_conditions))
        .order_by(Todo.created_at.desc())
        .limit(limit + 1)  # Fetch one extra to check for next page
    )
    result = await session.execute(statement)
    todos = list(result.scalars().all())

    # Determine next cursor
    next_cursor = None
    if len(todos) > limit:
        todos = todos[:limit]  # Remove the extra item
        next_cursor = todos[-1].created_at.isoformat()

    return todos, total_count, next_cursor


async def update_todo(
    session: AsyncSession, todo: Todo, update_data: TodoUpdate
) -> Todo:
    """Update a todo with the provided data."""
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        if value is not None:
            setattr(todo, key, value.strip() if isinstance(value, str) else value)

    todo.updated_at = datetime.utcnow()
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


async def soft_delete_todo(session: AsyncSession, todo: Todo) -> None:
    """Soft delete a todo by setting deleted_at."""
    todo.deleted_at = datetime.utcnow()
    session.add(todo)
    await session.commit()


async def toggle_todo_status(session: AsyncSession, todo: Todo) -> Todo:
    """Toggle the completion status of a todo."""
    todo.is_completed = not todo.is_completed
    todo.updated_at = datetime.utcnow()
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo
