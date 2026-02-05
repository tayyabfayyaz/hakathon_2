"""MCP tool result types for task operations.

Provides structured response types for MCP tools.
"""

from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime


@dataclass
class TaskResult:
    """Result of a task operation."""
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ToolResult:
    """Generic MCP tool result."""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    task: Optional[TaskResult] = None
    tasks: Optional[list[TaskResult]] = None
    count: Optional[int] = None
    matches: Optional[list[dict]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {"success": self.success}

        if self.message:
            result["message"] = self.message
        if self.error:
            result["error"] = self.error
        if self.task:
            result["task"] = {
                "id": self.task.id,
                "title": self.task.title,
                "description": self.task.description,
                "completed": self.task.completed,
            }
            if self.task.created_at:
                result["task"]["created_at"] = self.task.created_at
            if self.task.completed_at:
                result["task"]["completed_at"] = self.task.completed_at
        if self.tasks is not None:
            result["tasks"] = [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed,
                    "created_at": t.created_at,
                }
                for t in self.tasks
            ]
        if self.count is not None:
            result["count"] = self.count
        if self.matches:
            result["matches"] = self.matches

        return result
