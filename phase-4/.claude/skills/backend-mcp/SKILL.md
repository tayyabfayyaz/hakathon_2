---
name: backend-mcp
description: Create MCP (Model Context Protocol) tools for AI agent integration. Use when building AI-powered features, tool calling, or LLM function calling.
argument-hint: "[tool-name]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# MCP Tool Development

Create AI tools using the Model Context Protocol (MCP) for LLM integration.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Gemini    │────▶│  MCP Server  │────▶│  Database   │
│   (LLM)     │     │  (Tools)     │     │  (Actions)  │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │
       │ Tool Call         │ Tool Result
       ▼                   ▼
  User Intent ──────▶ Structured Action
```

## MCP Server Setup

```python
# app/mcp/server.py
from fastmcp import FastMCP
from app.mcp.tools import (
    add_task,
    list_tasks,
    update_task,
    complete_task_toggle,
    delete_task,
)

# Create MCP server
mcp = FastMCP("TodoList Task Manager")

# Register tools
mcp.tool(add_task)
mcp.tool(list_tasks)
mcp.tool(update_task)
mcp.tool(complete_task_toggle)
mcp.tool(delete_task)


def get_mcp_server() -> FastMCP:
    """Get the MCP server instance."""
    return mcp
```

## Tool Implementation

```python
# app/mcp/tools.py
from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import async_session_factory
from app.models.task import Task


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> dict:
    """
    Add a new task for the user.

    Args:
        user_id: The user's ID
        title: Task title (required)
        description: Optional task description

    Returns:
        Created task details with task_number
    """
    async with async_session_factory() as session:
        # Generate unique task number
        result = await session.exec(
            select(Task.task_number)
            .where(Task.user_id == user_id)
            .order_by(Task.task_number.desc())
            .limit(1)
        )
        last_number = result.first()
        task_number = (last_number or 999) + 1

        # Create task
        task = Task(
            user_id=user_id,
            task_number=task_number,
            text=title,
            description=description,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task_number": task.task_number,
            "task_id": str(task.id),
            "title": task.text,
            "message": f"Created task #{task.task_number}: {title}"
        }


async def list_tasks(
    user_id: str,
    include_completed: bool = False,
    limit: int = 10
) -> dict:
    """
    List user's tasks.

    Args:
        user_id: The user's ID
        include_completed: Whether to include completed tasks
        limit: Maximum number of tasks to return

    Returns:
        List of tasks with their details
    """
    async with async_session_factory() as session:
        query = select(Task).where(Task.user_id == user_id)

        if not include_completed:
            query = query.where(Task.completed == False)

        query = query.order_by(Task.created_at.desc()).limit(limit)
        result = await session.exec(query)
        tasks = result.all()

        return {
            "success": True,
            "count": len(tasks),
            "tasks": [
                {
                    "task_number": t.task_number,
                    "title": t.text,
                    "completed": t.completed,
                    "deadline": t.deadline.isoformat() if t.deadline else None,
                }
                for t in tasks
            ]
        }


async def update_task(
    user_id: str,
    task_identifier: str,
    new_title: Optional[str] = None,
    new_description: Optional[str] = None
) -> dict:
    """
    Update an existing task.

    Args:
        user_id: The user's ID
        task_identifier: Task number, UUID, or title to find
        new_title: New title for the task
        new_description: New description for the task

    Returns:
        Updated task details
    """
    async with async_session_factory() as session:
        task = await _find_task(session, user_id, task_identifier)

        if not task:
            return {
                "success": False,
                "error": f"Task not found: {task_identifier}"
            }

        if new_title:
            task.text = new_title
        if new_description is not None:
            task.description = new_description

        await session.commit()

        return {
            "success": True,
            "task_number": task.task_number,
            "title": task.text,
            "message": f"Updated task #{task.task_number}"
        }


async def complete_task_toggle(
    user_id: str,
    task_identifier: str
) -> dict:
    """
    Toggle task completion status.

    Args:
        user_id: The user's ID
        task_identifier: Task number, UUID, or title to find

    Returns:
        Updated task status
    """
    async with async_session_factory() as session:
        task = await _find_task(session, user_id, task_identifier)

        if not task:
            return {
                "success": False,
                "error": f"Task not found: {task_identifier}"
            }

        task.completed = not task.completed
        task.completed_at = datetime.now(timezone.utc) if task.completed else None

        await session.commit()

        status = "completed" if task.completed else "reopened"
        return {
            "success": True,
            "task_number": task.task_number,
            "completed": task.completed,
            "message": f"Task #{task.task_number} {status}"
        }


async def delete_task(
    user_id: str,
    task_identifier: str
) -> dict:
    """
    Delete a task.

    Args:
        user_id: The user's ID
        task_identifier: Task number, UUID, or title to find

    Returns:
        Deletion confirmation
    """
    async with async_session_factory() as session:
        task = await _find_task(session, user_id, task_identifier)

        if not task:
            return {
                "success": False,
                "error": f"Task not found: {task_identifier}"
            }

        task_number = task.task_number
        title = task.text

        await session.delete(task)
        await session.commit()

        return {
            "success": True,
            "message": f"Deleted task #{task_number}: {title}"
        }


async def _find_task(
    session: AsyncSession,
    user_id: str,
    identifier: str
) -> Optional[Task]:
    """
    Find task by number, UUID, or title.

    Priority: task_number > UUID > title match
    """
    # Try as task number
    if identifier.isdigit():
        result = await session.exec(
            select(Task)
            .where(Task.user_id == user_id)
            .where(Task.task_number == int(identifier))
        )
        task = result.first()
        if task:
            return task

    # Try as UUID
    try:
        task_uuid = UUID(identifier)
        task = await session.get(Task, task_uuid)
        if task and task.user_id == user_id:
            return task
    except ValueError:
        pass

    # Try as title (partial match)
    result = await session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.text.ilike(f"%{identifier}%"))
        .limit(1)
    )
    return result.first()
```

## AI Agent Integration

```python
# app/services/agent.py
import logging
from openai import AsyncOpenAI

from app.config import get_settings
from app.mcp.server import get_mcp_server

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Gemini via OpenAI-compatible API
client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SYSTEM_PROMPT = """You are a friendly AI assistant for TodoList Pro.
You help users manage their tasks through natural conversation.

You can:
- Add new tasks
- List existing tasks
- Update task titles and descriptions
- Mark tasks as complete/incomplete
- Delete tasks

Be conversational and helpful. Support both English and Hinglish.
When the user asks to do something with a task, use the appropriate tool.
"""


async def process_chat_message(
    user_id: str,
    message: str,
    conversation_history: list[dict]
) -> dict:
    """
    Process a chat message and execute any required tool calls.
    """
    mcp = get_mcp_server()

    # Build messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_history,
        {"role": "user", "content": message}
    ]

    # Get tool definitions from MCP
    tools = mcp.get_tool_definitions()

    # Call LLM
    response = await client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # Handle tool calls
    if assistant_message.tool_calls:
        tool_results = []

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Add user_id to all tool calls
            tool_args["user_id"] = user_id

            # Execute tool
            result = await mcp.call_tool(tool_name, tool_args)
            tool_results.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })

        # Get final response with tool results
        messages.append(assistant_message.model_dump())
        for result in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": result["tool_call_id"],
                "content": result["output"]
            })

        final_response = await client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=messages
        )

        return {
            "content": final_response.choices[0].message.content,
            "tool_calls": [tc.function.name for tc in assistant_message.tool_calls]
        }

    return {
        "content": assistant_message.content,
        "tool_calls": []
    }
```

## Tool Definition Format

```python
# MCP tool definitions (auto-generated from function signatures)
{
    "type": "function",
    "function": {
        "name": "add_task",
        "description": "Add a new task for the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user's ID"
                },
                "title": {
                    "type": "string",
                    "description": "Task title (required)"
                },
                "description": {
                    "type": "string",
                    "description": "Optional task description"
                }
            },
            "required": ["user_id", "title"]
        }
    }
}
```

## Adding New Tools

```python
# app/mcp/tools.py

async def set_task_deadline(
    user_id: str,
    task_identifier: str,
    deadline: str
) -> dict:
    """
    Set a deadline for a task.

    Args:
        user_id: The user's ID
        task_identifier: Task number, UUID, or title
        deadline: ISO format datetime string

    Returns:
        Updated task with deadline
    """
    async with async_session_factory() as session:
        task = await _find_task(session, user_id, task_identifier)

        if not task:
            return {"success": False, "error": "Task not found"}

        task.deadline = datetime.fromisoformat(deadline)
        await session.commit()

        return {
            "success": True,
            "task_number": task.task_number,
            "deadline": task.deadline.isoformat(),
            "message": f"Set deadline for task #{task.task_number}"
        }


# Register in server.py
mcp.tool(set_task_deadline)
```

## Best Practices

1. **User ID injection**: Always add `user_id` from auth context
2. **Multiple lookup strategies**: Support number, UUID, and title
3. **Structured responses**: Return `success`, `error`, and data
4. **Docstrings**: LLM uses them for tool descriptions
5. **Type hints**: Define clear parameter types
6. **Error handling**: Return friendly error messages
7. **Stateless tools**: Each call is independent
