# CLI Interface Contract

**Date**: 2025-12-23
**Feature**: [CLI To-Do List](spec.md)

This document defines the command-line interface for the To-Do CLI application. The main command will be `todo`.

## Commands

### `todo add`

Adds a new task to the to-do list.

-   **Usage**: `todo add <description>`
-   **Arguments**:
    -   `description` (string, required): The description of the task.
-   **Example**: `todo add "Buy groceries"`

### `todo list`

Lists all the tasks in the to-do list.

-   **Usage**: `todo list`
-   **Output**: A formatted table with columns for ID, Description, and Status.

### `todo update`

Updates the description of an existing task.

-   **Usage**: `todo update <id> <new_description>`
-   **Arguments**:
    -   `id` (integer, required): The ID of the task to update.
    -   `new_description` (string, required): The new description for the task.
-   **Example**: `todo update 1 "Buy almond milk"`

### `todo toggle`

Toggles the status of a task between "Remaining" and "Completed".

-   **Usage**: `todo toggle <id>`
-   **Arguments**:
    -   `id` (integer, required): The ID of the task to toggle.
-   **Example**: `todo toggle 1`

### `todo delete`

Deletes a task from the to-do list.

-   **Usage**: `todo delete <id>`
-   **Arguments**:
    -   `id` (integer, required): The ID of the task to delete.
-   **Example**: `todo delete 1`
