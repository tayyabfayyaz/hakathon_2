# Data Model: To-Do CLI Application

**Date**: 2025-12-23
**Feature**: [CLI To-Do List](spec.md)

This document defines the data model for the To-Do CLI application.

## Entity: To-Do Item

Represents a single task in the to-do list.

### Fields

| Field         | Type   | Description                                     | Constraints      |
|---------------|--------|-------------------------------------------------|------------------|
| `id`          | `int`  | A unique integer identifying the task.          | Required, unique |
| `description` | `str`  | The text of the task.                           | Required, non-empty |
| `status`      | `str`  | The current state of the task ("Remaining" or "Completed"). | Required         |

### Example (Pydantic Model)

```python
from pydantic import BaseModel, Field
from typing import Literal

class TodoItem(BaseModel):
    id: int
    description: str = Field(..., min_length=1)
    status: Literal["Remaining", "Completed"] = "Remaining"
```

### State Transitions

- A `TodoItem` is created with a `status` of "Remaining".
- The `status` can be toggled between "Remaining" and "Completed".
