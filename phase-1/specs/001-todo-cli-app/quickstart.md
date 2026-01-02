# Quickstart: To-Do CLI Application

**Date**: 2025-12-23
**Feature**: [CLI To-Do List](spec.md)

This guide provides instructions for setting up and running the To-Do CLI application.

## Prerequisites

-   Python 3.11 or higher
-   pip

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: The `requirements.txt` file will be created during the implementation phase.)*

## Usage

Once installed, the application can be run from the command line using the `todo` command.

### Add a task

```bash
todo add "My first task"
```

### List all tasks

```bash
todo list
```

### Update a task

```bash
todo update 1 "My updated task"
```

### Toggle a task's status

```bash
todo toggle 1
```

### Delete a task

```bash
todo delete 1
```
