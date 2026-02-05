"""MCP Client wrapper for calling MCP server tools.

This module provides a client interface to the MCP server,
allowing the agent service to discover and execute tools.
"""

import asyncio
import json
import logging
from typing import Optional

from app.mcp import call_tool as mcp_call_tool, list_available_tools

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for interacting with the MCP server.

    Provides tool discovery and execution capabilities.
    """

    # Timeout for tool execution (increased to 30 seconds for DB operations)
    TOOL_TIMEOUT = 30.0

    def __init__(self):
        """Initialize the MCP client."""
        self._tools_cache: Optional[list[dict]] = None
        logger.info("MCP Client initialized")

    async def discover_tools(self) -> list[dict]:
        """Discover available tools from the MCP server.

        Returns:
            List of tool definitions with name, description, and parameters
        """
        if self._tools_cache is None:
            self._tools_cache = await list_available_tools()
            logger.info(f"Discovered {len(self._tools_cache)} MCP tools")
        return self._tools_cache

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Execute a tool on the MCP server.

        Args:
            tool_name: Name of the tool to execute
            arguments: Dictionary of tool arguments

        Returns:
            Tool result as a dictionary
        """
        logger.info(f"MCP Client calling tool: {tool_name} with args: {arguments}")

        try:
            # Call the MCP tool with timeout enforcement
            result_json = await asyncio.wait_for(
                mcp_call_tool(tool_name, arguments),
                timeout=self.TOOL_TIMEOUT
            )

            # Parse result
            result = json.loads(result_json)
            logger.info(f"MCP tool {tool_name} result: success={result.get('success')}")
            return result

        except asyncio.TimeoutError:
            logger.error(f"MCP tool {tool_name} timed out after {self.TOOL_TIMEOUT}s")
            return {"success": False, "error": f"Tool execution timed out after {self.TOOL_TIMEOUT} seconds"}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP tool result: {e}")
            return {"success": False, "error": f"Invalid tool response: {e}"}
        except Exception as e:
            logger.error(f"MCP tool execution failed: {e}")
            return {"success": False, "error": str(e)}

    def get_tool_names(self) -> list[str]:
        """Get list of available tool names.

        Returns:
            List of tool name strings
        """
        return [
            "add_task",
            "list_tasks",
            "update_task",
            "complete_task_toggle",
            "delete_task",
        ]

    def format_tool_result_for_context(self, tool_name: str, result: dict) -> str:
        """Format a tool result for inclusion in AI context.

        Args:
            tool_name: Name of the tool that was executed
            result: Tool result dictionary

        Returns:
            Formatted string describing the tool result
        """
        if not result.get("success"):
            error = result.get("error", "Unknown error")
            return f"Tool {tool_name} failed: {error}"

        if tool_name == "add_task":
            task = result.get("task", {})
            return f"Created task: '{task.get('title')}' (ID: {task.get('id')})"

        elif tool_name == "list_tasks":
            tasks = result.get("tasks", [])
            count = result.get("count", len(tasks))
            if count == 0:
                return "No tasks found."
            task_lines = []
            for t in tasks[:10]:  # Limit to 10 for context
                status = "[x]" if t.get("completed") else "[ ]"
                task_lines.append(f"  {status} {t.get('title')}")
            return f"Found {count} tasks:\n" + "\n".join(task_lines)

        elif tool_name == "update_task":
            task = result.get("task", {})
            return f"Updated task: '{task.get('title')}'"

        elif tool_name == "complete_task_toggle":
            task = result.get("task", {})
            message = result.get("message", "")
            return message or f"Toggled task: '{task.get('title')}' (completed: {task.get('completed')})"

        elif tool_name == "delete_task":
            return result.get("message", "Task deleted.")

        return json.dumps(result)


# Module-level singleton
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create the MCP client singleton."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
