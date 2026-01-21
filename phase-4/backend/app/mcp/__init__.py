"""MCP (Model Context Protocol) module for AI agent task operations.

This module provides:
- MCP server with Official SDK implementation (server.py)
- Conversation persistence functions (tools.py)
- Tool result types (types.py)
"""

# Conversation persistence functions (from existing tools.py)
from app.mcp.tools import (
    get_or_create_conversation,
    add_message,
    get_conversation_history,
)

# MCP Server and tools (Official SDK)
from app.mcp.server import (
    get_mcp_server,
    list_available_tools,
    call_tool,
    add_task,
    list_tasks,
    update_task,
    complete_task_toggle,
    delete_task,
)

__all__ = [
    # Conversation persistence
    "get_or_create_conversation",
    "add_message",
    "get_conversation_history",
    # MCP Server
    "get_mcp_server",
    "list_available_tools",
    "call_tool",
    # MCP Tools
    "add_task",
    "list_tasks",
    "update_task",
    "complete_task_toggle",
    "delete_task",
]
