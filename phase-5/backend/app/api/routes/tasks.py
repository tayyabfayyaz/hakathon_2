"""Task CRUD endpoints."""

import random
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.task import Task
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskPatch,
    TaskResponse,
    TaskListResponse,
    DeadlineRequest,
    DeadlineResponse,
)


async def generate_unique_task_number(session, user_id: str) -> int:
    """Generate a unique task number for a user (1000-9999).

    Ensures no collision with existing task numbers for the same user.
    """
    max_attempts = 100
    for _ in range(max_attempts):
        task_number = random.randint(1000, 9999)
        # Check if this number already exists for this user
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.task_number == task_number,
        )
        result = await session.exec(statement)
        if result.first() is None:
            return task_number
    # Fallback: use timestamp-based number if all attempts failed
    return random.randint(10000, 99999)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> Task:
    """
    Create a new task for the authenticated user.

    - **text**: Task description (1-500 characters)

    Returns task with a unique `task_number` (4-digit ID) for easy voice/chat reference.
    """
    # Generate unique task number for this user
    task_number = await generate_unique_task_number(session, current_user.id)

    task = Task(
        text=task_data.text,
        user_id=current_user.id,
        task_number=task_number,
        completed=False,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict:
    """
    List all tasks for the authenticated user.

    Returns tasks sorted by creation date (newest first).
    """
    statement = (
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
    )
    result = await session.exec(statement)
    tasks = result.all()
    return {"tasks": tasks, "count": len(tasks)}


@router.get("/by-number/{task_number}", response_model=TaskResponse)
async def get_task_by_number(
    task_number: int,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> Task:
    """
    Get a specific task by its short task_number (for voice/chat agents).

    - **task_number**: The 4-digit task ID (e.g., 4521)

    Returns 404 if task doesn't exist or belongs to another user.
    """
    statement = select(Task).where(
        Task.task_number == task_number,
        Task.user_id == current_user.id,
    )
    result = await session.exec(statement)
    task = result.first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task #{task_number} not found",
        )

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> Task:
    """
    Get a specific task by ID.

    Returns 404 if task doesn't exist or belongs to another user.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id,
    )
    result = await session.exec(statement)
    task = result.first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> Task:
    """
    Update a task (full replacement).

    - **text**: New task description
    - **completed**: New completion status
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id,
    )
    result = await session.exec(statement)
    task = result.first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update fields
    task.text = task_data.text
    task.updated_at = datetime.utcnow()

    # Handle completion status change
    if task_data.completed != task.completed:
        task.completed = task_data.completed
        task.completed_at = datetime.utcnow() if task_data.completed else None

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def patch_task(
    task_id: UUID,
    task_data: TaskPatch,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> Task:
    """
    Partially update a task.

    Only provided fields will be updated.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id,
    )
    result = await session.exec(statement)
    task = result.first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update only provided fields
    if task_data.text is not None:
        task.text = task_data.text

    if task_data.completed is not None and task_data.completed != task.completed:
        task.completed = task_data.completed
        task.completed_at = datetime.utcnow() if task_data.completed else None

    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> None:
    """
    Delete a task.

    Returns 404 if task doesn't exist or belongs to another user.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id,
    )
    result = await session.exec(statement)
    task = result.first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await session.delete(task)
    await session.commit()


@router.put("/{task_id}/deadline", response_model=DeadlineResponse)
async def set_deadline(
    task_id: UUID,
    deadline_data: DeadlineRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict:
    """
    Set or update a task's deadline.

    - **deadline**: The deadline datetime (must be in the future)

    Returns the updated deadline information.
    """
    # Get the task
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id,
    )
    result = await session.exec(statement)
    task = result.first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Validate deadline is in the future
    now_utc = datetime.now(timezone.utc)
    deadline_utc = deadline_data.deadline
    # If deadline is naive, assume UTC
    if deadline_utc.tzinfo is None:
        deadline_utc = deadline_utc.replace(tzinfo=timezone.utc)
    if deadline_utc <= now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deadline must be in the future",
        )

    # Update the deadline (convert to UTC naive datetime for database storage)
    # If timezone-aware, convert to UTC and strip timezone
    deadline_to_store = deadline_data.deadline
    if deadline_to_store.tzinfo is not None:
        # Convert to UTC and make naive
        deadline_to_store = deadline_to_store.astimezone(timezone.utc).replace(tzinfo=None)
    task.deadline = deadline_to_store
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {
        "task_id": task.id,
        "deadline": task.deadline,
        "message": "Deadline set successfully",
    }


@router.delete("/{task_id}/deadline", response_model=DeadlineResponse)
async def remove_deadline(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict:
    """
    Remove a task's deadline.

    Returns confirmation of deadline removal.
    """
    # Get the task
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id,
    )
    result = await session.exec(statement)
    task = result.first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Remove the deadline
    task.deadline = None
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {
        "task_id": task.id,
        "deadline": None,
        "message": "Deadline removed successfully",
    }
