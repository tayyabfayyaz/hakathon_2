"""Data models for the TODO CLI application.

This module defines the Pydantic models used for data validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Literal


class TodoItem(BaseModel):
    """Represents a single to-do item.

    Attributes:
        id: Unique identifier for the task.
        description: The text description of the task.
        status: Current state - either 'Remaining' or 'Completed'.
    """

    id: int
    description: str = Field(..., min_length=1)
    status: Literal["Remaining", "Completed"] = "Remaining"
