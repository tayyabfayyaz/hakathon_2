"""Task CRUD endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
import logging

from app.api.deps import CurrentUserDep, SessionDep
from app.models.task import Task
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskPatch,
    TaskResponse,
    TaskListResponse,
)
from app.services.kafka_service import kafka_service

logger = logging.getLogger(__name__)


# Additional schemas for deadline operations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeadlineRequest(BaseModel):
    deadline: Optional[datetime]


class DeadlineResponse(BaseModel):
    task_id: str
    deadline: Optional[datetime]
    message: str

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
    - **deadline**: Optional deadline for the task
    """
    task = Task(
        text=task_data.text,
        description=task_data.description,
        deadline=task_data.deadline,
        user_id=current_user.id,
        completed=False,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Publish event to Kafka for notification system
    try:
        kafka_service.publish_todo_created(
            todo_id=str(task.id),
            user_id=task.user_id,
            title=task.text,
            description=task.description,
            deadline=task.deadline
        )
    except Exception as e:
        logger.error(f"Failed to publish todo created event: {e}")

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
    - **deadline**: Optional new deadline for the task
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
    task.description = task_data.description
    task.deadline = task_data.deadline
    task.updated_at = datetime.utcnow()

    # Handle completion status change
    if task_data.completed != task.completed:
        task.completed = task_data.completed
        task.completed_at = datetime.utcnow() if task_data.completed else None

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Publish event to Kafka for notification system
    try:
        kafka_service.publish_todo_updated(
            todo_id=str(task.id),
            user_id=task.user_id,
            title=task.text,
            description=task.description,
            deadline=task.deadline
        )
    except Exception as e:
        logger.error(f"Failed to publish todo updated event: {e}")

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

    # Store original values for comparison
    original_text = task.text
    original_description = task.description
    original_deadline = task.deadline
    original_completed = task.completed

    # Update only provided fields
    if task_data.text is not None:
        task.text = task_data.text

    if task_data.description is not None:
        task.description = task_data.description

    if task_data.deadline is not None:
        task.deadline = task_data.deadline

    if task_data.completed is not None and task_data.completed != task.completed:
        task.completed = task_data.completed
        task.completed_at = datetime.utcnow() if task_data.completed else None

    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Publish event to Kafka for notification system if relevant fields changed
    if (task.text != original_text or
        task.description != original_description or
        task.deadline != original_deadline or
        task.completed != original_completed):
        try:
            kafka_service.publish_todo_updated(
                todo_id=str(task.id),
                user_id=task.user_id,
                title=task.text,
                description=task.description,
                deadline=task.deadline
            )
        except Exception as e:
            logger.error(f"Failed to publish todo updated event: {e}")

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

    # Store task info before deletion for Kafka event
    task_id_str = str(task.id)
    user_id = task.user_id

    await session.delete(task)
    await session.commit()

    # Publish event to Kafka for notification system
    try:
        kafka_service.publish_todo_deleted(
            todo_id=task_id_str,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Failed to publish todo deleted event: {e}")


@router.put("/{task_id}/deadline", response_model=DeadlineResponse)
async def set_task_deadline(
    task_id: UUID,
    deadline_data: DeadlineRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> DeadlineResponse:
    """
    Set a deadline for a task.

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

    # Store original values for comparison
    original_text = task.text
    original_description = task.description
    original_deadline = task.deadline
    original_completed = task.completed

    # Update the deadline
    task.deadline = deadline_data.deadline
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Publish event to Kafka for notification system
    try:
        kafka_service.publish_todo_updated(
            todo_id=str(task.id),
            user_id=task.user_id,
            title=task.text,
            description=task.description,
            deadline=task.deadline
        )
    except Exception as e:
        logger.error(f"Failed to publish todo updated event: {e}")

    return DeadlineResponse(
        task_id=str(task.id),
        deadline=task.deadline,
        message="Deadline updated successfully"
    )


@router.delete("/{task_id}/deadline", response_model=DeadlineResponse)
async def remove_task_deadline(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> DeadlineResponse:
    """
    Remove a deadline from a task.

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

    # Store original values for comparison
    original_text = task.text
    original_description = task.description
    original_deadline = task.deadline
    original_completed = task.completed

    # Remove the deadline
    task.deadline = None
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Publish event to Kafka for notification system
    try:
        kafka_service.publish_todo_updated(
            todo_id=str(task.id),
            user_id=task.user_id,
            title=task.text,
            description=task.description,
            deadline=task.deadline
        )
    except Exception as e:
        logger.error(f"Failed to publish todo updated event: {e}")

    return DeadlineResponse(
        task_id=str(task.id),
        deadline=task.deadline,
        message="Deadline removed successfully"
    )
