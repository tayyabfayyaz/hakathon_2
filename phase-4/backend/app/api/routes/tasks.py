"""Task CRUD endpoints."""

from datetime import datetime
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
)

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
    """
    task = Task(
        text=task_data.text,
        user_id=current_user.id,
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
