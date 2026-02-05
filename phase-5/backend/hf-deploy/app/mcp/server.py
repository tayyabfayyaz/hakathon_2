"""MCP Server implementation using Official MCP SDK.

This module implements a Model Context Protocol (MCP) server that exposes
todo task management tools. Uses FastMCP for simplified tool registration.

Tools exposed:
- add_task: Create a new task
- list_tasks: List user's tasks
- update_task: Modify a task's title/description
- complete_task_toggle: Toggle task completion status
- delete_task: Remove a task
"""

import json
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import select

from app.config import get_settings
from app.models import Task

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="todo-mcp-server")

# Database session factory - will be initialized on startup
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        settings = get_settings()
        engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,  # Recycle connections after 30 minutes
        )
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("MCP database session factory initialized")
    return _async_session_factory


@asynccontextmanager
async def get_db_session():
    """Get a database session for tool operations."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def _find_task_by_title(
    session: AsyncSession,
    user_id: str,
    task_title: str
) -> list[Task]:
    """Find tasks matching a title (case-insensitive partial match).

    Tries multiple matching strategies:
    1. Exact substring match
    2. Word-based match (any word in the search term)
    """
    # First, try direct substring match
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.text.ilike(f"%{task_title}%"))
    )
    result = await session.execute(statement)
    matches = list(result.scalars().all())

    if matches:
        return matches

    # If no direct match, try matching individual words (min 3 chars)
    words = [w.strip() for w in task_title.split() if len(w.strip()) >= 3]

    if words:
        # Try each word individually
        for word in words:
            statement = (
                select(Task)
                .where(Task.user_id == user_id)
                .where(Task.text.ilike(f"%{word}%"))
            )
            result = await session.execute(statement)
            word_matches = list(result.scalars().all())
            if word_matches:
                return word_matches

    return []


# =============================================================================
# MCP Tools Implementation using @mcp.tool() decorator
# =============================================================================


@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> str:
    """Add a new task for the user.

    Use this when the user wants to create a new todo item.

    Args:
        user_id: The user's ID (required for ownership)
        title: The title or main text of the task
        description: Optional detailed description of the task

    Returns:
        JSON string with success status and created task details
    """
    logger.info(f"MCP add_task called: user_id={user_id}, title={title}")

    async with get_db_session() as session:
        task = Task(
            user_id=user_id,
            text=title,
            description=description
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        result = {
            "success": True,
            "task": {
                "id": str(task.id),
                "title": task.text,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
        }
        return json.dumps(result)


@mcp.tool()
async def list_tasks(
    user_id: str,
    include_completed: bool = True,
    limit: int = 50
) -> str:
    """List the user's tasks.

    Use this when the user wants to see their todos.

    Args:
        user_id: The user's ID (required for ownership)
        include_completed: Whether to include completed tasks (default: True)
        limit: Maximum number of tasks to return (default: 50)

    Returns:
        JSON string with success status, tasks array, and count
    """
    logger.info(f"MCP list_tasks called: user_id={user_id}, include_completed={include_completed}")

    async with get_db_session() as session:
        statement = select(Task).where(Task.user_id == user_id)

        if not include_completed:
            statement = statement.where(Task.completed == False)

        statement = statement.order_by(Task.created_at.desc()).limit(limit)

        result = await session.execute(statement)
        tasks = result.scalars().all()

        result_data = {
            "success": True,
            "tasks": [
                {
                    "id": str(task.id),
                    "title": task.text,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                }
                for task in tasks
            ],
            "count": len(tasks)
        }
        return json.dumps(result_data)


@mcp.tool()
async def update_task(
    user_id: str,
    task_id: Optional[str] = None,
    task_title: Optional[str] = None,
    new_title: Optional[str] = None,
    new_description: Optional[str] = None
) -> str:
    """Update an existing task's title or description.

    Use this when the user wants to modify a task.

    Args:
        user_id: The user's ID (required for ownership)
        task_id: The UUID of the task to update (if known)
        task_title: The current title of the task to update (for matching)
        new_title: The new title for the task
        new_description: The new description for the task

    Returns:
        JSON string with success status and updated task details
    """
    logger.info(f"MCP update_task called: user_id={user_id}, task_id={task_id}, task_title={task_title}")

    async with get_db_session() as session:
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
                return json.dumps({"success": False, "error": "Invalid task ID format"})

        elif task_title:
            matches = await _find_task_by_title(session, user_id, task_title)

            if len(matches) == 0:
                return json.dumps({"success": False, "error": f"No task found matching '{task_title}'"})
            elif len(matches) > 1:
                return json.dumps({
                    "success": False,
                    "error": "Multiple tasks match that title",
                    "matches": [{"id": str(t.id), "title": t.text} for t in matches]
                })
            task = matches[0]

        if task is None:
            return json.dumps({"success": False, "error": "Task not found. Please provide task_id or task_title."})

        if new_title:
            task.text = new_title
        if new_description is not None:
            task.description = new_description

        task.updated_at = datetime.utcnow()
        await session.commit()

        result = {
            "success": True,
            "task": {
                "id": str(task.id),
                "title": task.text,
                "description": task.description,
                "completed": task.completed
            }
        }
        return json.dumps(result)


@mcp.tool()
async def complete_task_toggle(
    user_id: str,
    task_id: Optional[str] = None,
    task_title: Optional[str] = None
) -> str:
    """Toggle a task's completion status.

    Use this when the user says they finished a task or wants to unmark a completed task.

    Args:
        user_id: The user's ID (required for ownership)
        task_id: The UUID of the task to toggle (if known)
        task_title: The title of the task to toggle (for fuzzy matching)

    Returns:
        JSON string with success status and task with toggled completion state
    """
    logger.info(f"MCP complete_task_toggle called: user_id={user_id}, task_id={task_id}, task_title={task_title}")

    async with get_db_session() as session:
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
                return json.dumps({"success": False, "error": "Invalid task ID format"})

        elif task_title:
            matches = await _find_task_by_title(session, user_id, task_title)

            if len(matches) == 0:
                return json.dumps({"success": False, "error": f"No task found matching '{task_title}'"})
            elif len(matches) > 1:
                return json.dumps({
                    "success": False,
                    "error": "Multiple tasks match that title",
                    "matches": [{"id": str(t.id), "title": t.text} for t in matches]
                })
            task = matches[0]

        if task is None:
            return json.dumps({"success": False, "error": "Task not found. Please provide task_id or task_title."})

        # Toggle completion status
        was_completed = task.completed
        task.completed = not task.completed

        if task.completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None

        task.updated_at = datetime.utcnow()
        await session.commit()

        action = "completed" if task.completed else "unmarked"
        result = {
            "success": True,
            "message": f"Task '{task.text}' has been {action}.",
            "task": {
                "id": str(task.id),
                "title": task.text,
                "completed": task.completed,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
        }
        return json.dumps(result)


@mcp.tool()
async def delete_task(
    user_id: str,
    task_id: Optional[str] = None,
    task_title: Optional[str] = None
) -> str:
    """Delete a task.

    Use this when the user wants to remove a task from their list.

    Args:
        user_id: The user's ID (required for ownership)
        task_id: The UUID of the task to delete (if known)
        task_title: The title of the task to delete (for matching)

    Returns:
        JSON string with success status and deleted task message
    """
    logger.info(f"MCP delete_task called: user_id={user_id}, task_id={task_id}, task_title={task_title}")

    async with get_db_session() as session:
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
                return json.dumps({"success": False, "error": "Invalid task ID format"})

        elif task_title:
            matches = await _find_task_by_title(session, user_id, task_title)

            if len(matches) == 0:
                return json.dumps({"success": False, "error": f"No task found matching '{task_title}'"})
            elif len(matches) > 1:
                return json.dumps({
                    "success": False,
                    "error": "Multiple tasks match that title",
                    "matches": [{"id": str(t.id), "title": t.text} for t in matches]
                })
            task = matches[0]

        if task is None:
            return json.dumps({"success": False, "error": "Task not found. Please provide task_id or task_title."})

        task_title_deleted = task.text
        await session.delete(task)
        await session.commit()

        result = {
            "success": True,
            "message": f"Task '{task_title_deleted}' has been deleted."
        }
        return json.dumps(result)


# =============================================================================
# MCP Server Access Functions
# =============================================================================


def get_mcp_server() -> FastMCP:
    """Get the MCP server instance."""
    return mcp


async def list_available_tools() -> list[dict]:
    """List all available tools from the MCP server.

    Returns:
        List of tool definitions with name, description, and parameters
    """
    return [
        {
            "name": "add_task",
            "description": "Add a new task for the user",
            "parameters": ["user_id", "title", "description"]
        },
        {
            "name": "list_tasks",
            "description": "List the user's tasks",
            "parameters": ["user_id", "include_completed", "limit"]
        },
        {
            "name": "update_task",
            "description": "Update an existing task's title or description",
            "parameters": ["user_id", "task_id", "task_title", "new_title", "new_description"]
        },
        {
            "name": "complete_task_toggle",
            "description": "Toggle a task's completion status",
            "parameters": ["user_id", "task_id", "task_title"]
        },
        {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": ["user_id", "task_id", "task_title"]
        }
    ]


async def call_tool(tool_name: str, arguments: dict) -> str:
    """Call an MCP tool directly.

    This is used by the agent service to execute tools.

    Args:
        tool_name: Name of the tool to call
        arguments: Dictionary of tool arguments

    Returns:
        JSON string result from the tool
    """
    logger.info(f"Calling MCP tool: {tool_name} with args: {arguments}")

    tool_map = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "update_task": update_task,
        "complete_task_toggle": complete_task_toggle,
        "delete_task": delete_task,
    }

    if tool_name not in tool_map:
        return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"})

    try:
        tool_func = tool_map[tool_name]
        result = await tool_func(**arguments)
        return result
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return json.dumps({"success": False, "error": str(e)})
