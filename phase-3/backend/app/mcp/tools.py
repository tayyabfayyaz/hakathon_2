"""MCP tool implementations for task management operations.

All tools are stateless - they accept user_id explicitly and perform
database operations directly. Tools wrap existing DB logic without
modifying Phase-2 CRUD operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Task, Conversation, Message, MessageRole


# NOTE: OpenAI TOOL_DEFINITIONS removed - now using Official MCP SDK in server.py


async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str
) -> Conversation:
    """Get existing conversation for user or create new one.

    Each user has exactly one conversation (UNIQUE constraint on user_id).

    Args:
        session: Database session
        user_id: User ID from JWT token

    Returns:
        Conversation object
    """
    statement = select(Conversation).where(Conversation.user_id == user_id)
    result = await session.execute(statement)
    conversation = result.scalar_one_or_none()

    if conversation is None:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    return conversation


async def add_message(
    session: AsyncSession,
    user_id: str,
    conversation_id: UUID,
    role: str,
    content: str
) -> Message:
    """Store a message in the conversation.

    Args:
        session: Database session
        user_id: User ID from JWT token
        conversation_id: Parent conversation ID
        role: Message role string ('user' or 'assistant')
        content: Message content

    Returns:
        Created Message object
    """
    # Convert enum to string value if needed
    role_str = role.value if isinstance(role, MessageRole) else role
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role_str,
        content=content
    )
    session.add(message)

    # Update conversation timestamp
    statement = select(Conversation).where(Conversation.id == conversation_id)
    result = await session.execute(statement)
    conversation = result.scalar_one()
    conversation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(message)
    return message


async def get_conversation_history(
    session: AsyncSession,
    user_id: str,
    limit: int = 50
) -> list[Message]:
    """Get conversation history for a user.

    Args:
        session: Database session
        user_id: User ID from JWT token
        limit: Maximum number of messages to return

    Returns:
        List of Message objects ordered by creation time
    """
    statement = (
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    result = await session.execute(statement)
    return list(result.scalars().all())


async def add_task(
    session: AsyncSession,
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> dict:
    """Add a new task for the user.

    Wraps existing Task model without modifying Phase-2 CRUD logic.

    Args:
        session: Database session
        user_id: User ID from JWT token
        title: Task title
        description: Optional task description

    Returns:
        Dict with task details for AI response
    """
    task = Task(
        user_id=user_id,
        text=title,
        description=description
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {
        "success": True,
        "task": {
            "id": str(task.id),
            "title": task.text,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat()
        }
    }


async def list_tasks(
    session: AsyncSession,
    user_id: str,
    include_completed: bool = True,
    limit: int = 50
) -> dict:
    """List tasks for the user.

    Args:
        session: Database session
        user_id: User ID from JWT token
        include_completed: Whether to include completed tasks
        limit: Maximum number of tasks to return

    Returns:
        Dict with tasks list for AI response
    """
    statement = select(Task).where(Task.user_id == user_id)

    if not include_completed:
        statement = statement.where(Task.completed == False)

    statement = statement.order_by(Task.created_at.desc()).limit(limit)

    result = await session.execute(statement)
    tasks = result.scalars().all()

    return {
        "success": True,
        "tasks": [
            {
                "id": str(task.id),
                "title": task.text,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ],
        "count": len(tasks)
    }


async def _find_task_by_title(
    session: AsyncSession,
    user_id: str,
    task_title: str
) -> list[Task]:
    """Find tasks matching a title (case-insensitive partial match).

    Args:
        session: Database session
        user_id: User ID from JWT token
        task_title: Title to search for

    Returns:
        List of matching tasks
    """
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.text.ilike(f"%{task_title}%"))
    )
    result = await session.execute(statement)
    return list(result.scalars().all())


async def complete_task(
    session: AsyncSession,
    user_id: str,
    task_id: Optional[str] = None,
    task_title: Optional[str] = None
) -> dict:
    """Mark a task as completed.

    Can find task by ID or by title matching.

    Args:
        session: Database session
        user_id: User ID from JWT token
        task_id: Task UUID (if known)
        task_title: Task title for matching

    Returns:
        Dict with result for AI response
    """
    task = None

    if task_id:
        try:
            uuid = UUID(task_id)
            statement = select(Task).where(
                Task.id == uuid,
                Task.user_id == user_id
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()
        except ValueError:
            return {"success": False, "error": "Invalid task ID format"}

    elif task_title:
        matches = await _find_task_by_title(session, user_id, task_title)

        if len(matches) == 0:
            return {"success": False, "error": f"No task found matching '{task_title}'"}
        elif len(matches) > 1:
            return {
                "success": False,
                "error": "Multiple tasks match that title",
                "matches": [{"id": str(t.id), "title": t.text} for t in matches]
            }
        task = matches[0]

    if task is None:
        return {"success": False, "error": "Task not found. Please provide task_id or task_title."}

    if task.completed:
        return {"success": True, "message": f"Task '{task.text}' is already completed."}

    task.completed = True
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    await session.commit()

    return {
        "success": True,
        "task": {
            "id": str(task.id),
            "title": task.text,
            "completed": True,
            "completed_at": task.completed_at.isoformat()
        }
    }


async def update_task(
    session: AsyncSession,
    user_id: str,
    task_id: Optional[str] = None,
    task_title: Optional[str] = None,
    new_title: Optional[str] = None,
    new_description: Optional[str] = None
) -> dict:
    """Update a task's title or description.

    Args:
        session: Database session
        user_id: User ID from JWT token
        task_id: Task UUID (if known)
        task_title: Current task title for matching
        new_title: New title to set
        new_description: New description to set

    Returns:
        Dict with result for AI response
    """
    task = None

    if task_id:
        try:
            uuid = UUID(task_id)
            statement = select(Task).where(
                Task.id == uuid,
                Task.user_id == user_id
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()
        except ValueError:
            return {"success": False, "error": "Invalid task ID format"}

    elif task_title:
        matches = await _find_task_by_title(session, user_id, task_title)

        if len(matches) == 0:
            return {"success": False, "error": f"No task found matching '{task_title}'"}
        elif len(matches) > 1:
            return {
                "success": False,
                "error": "Multiple tasks match that title",
                "matches": [{"id": str(t.id), "title": t.text} for t in matches]
            }
        task = matches[0]

    if task is None:
        return {"success": False, "error": "Task not found. Please provide task_id or task_title."}

    if new_title:
        task.text = new_title
    if new_description is not None:
        task.description = new_description

    task.updated_at = datetime.utcnow()
    await session.commit()

    return {
        "success": True,
        "task": {
            "id": str(task.id),
            "title": task.text,
            "description": task.description,
            "completed": task.completed
        }
    }


async def delete_task(
    session: AsyncSession,
    user_id: str,
    task_id: Optional[str] = None,
    task_title: Optional[str] = None
) -> dict:
    """Delete a task.

    Args:
        session: Database session
        user_id: User ID from JWT token
        task_id: Task UUID (if known)
        task_title: Task title for matching

    Returns:
        Dict with result for AI response
    """
    task = None

    if task_id:
        try:
            uuid = UUID(task_id)
            statement = select(Task).where(
                Task.id == uuid,
                Task.user_id == user_id
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()
        except ValueError:
            return {"success": False, "error": "Invalid task ID format"}

    elif task_title:
        matches = await _find_task_by_title(session, user_id, task_title)

        if len(matches) == 0:
            return {"success": False, "error": f"No task found matching '{task_title}'"}
        elif len(matches) > 1:
            return {
                "success": False,
                "error": "Multiple tasks match that title",
                "matches": [{"id": str(t.id), "title": t.text} for t in matches]
            }
        task = matches[0]

    if task is None:
        return {"success": False, "error": "Task not found. Please provide task_id or task_title."}

    task_title_deleted = task.text
    await session.delete(task)
    await session.commit()

    return {
        "success": True,
        "message": f"Task '{task_title_deleted}' has been deleted."
    }
